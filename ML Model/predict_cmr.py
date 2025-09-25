#!/usr/bin/env python3
"""
Predict CESM variables for NASA CMR datasets using their full data summaries
Uses confidence threshold of 0.8 based on analysis
"""

import torch
import json
import pandas as pd
from transformers import AutoTokenizer, AutoModel
import torch.nn as nn
from collections import Counter, defaultdict
import re
import os

# Check device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"ÜÇ Using device: {device}")

# Get script directory for relative paths
script_dir = os.path.dirname(os.path.abspath(__file__))

# Initialize empty grouping variables (can be populated later if needed)
var_to_group = {}
group_info = {}

class CESMBert(nn.Module):
    def __init__(self, num_classes, model_name="climatebert/distilroberta-base-climate-f"):
        super(CESMBert, self).__init__()
        self.base_model = AutoModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(0.3)
        self.classifier = nn.Linear(self.base_model.config.hidden_size, num_classes)
   
    def forward(self, input_ids, attention_mask):
        outputs = self.base_model(input_ids=input_ids, attention_mask=attention_mask)
        
        # Use mean pooling over real tokens (ignore PADs)
        mask = attention_mask.unsqueeze(-1).type_as(outputs.last_hidden_state)
        summed = (outputs.last_hidden_state * mask).sum(dim=1)
        counts = mask.sum(dim=1).clamp(min=1e-9)
        pooled = summed / counts
        
        output = self.dropout(pooled)
        logits = self.classifier(output)
        return logits

def load_trained_model():
    """Load the trained model and mappings"""
    print(" Loading trained model...")
    
    try:
        label2id = torch.load(os.path.join(script_dir, 'models/label2id.pth'))
        id2label = torch.load(os.path.join(script_dir, 'models/id2label.pth'))
        print(f" Loaded {len(label2id)} class mappings")
    except FileNotFoundError:
        print("¥î Could not find label mappings in models/ directory")
        return None, None, None
    
    # Load custom tokenizer (required)
    try:
        tokenizer = AutoTokenizer.from_pretrained(os.path.join(script_dir, 'models/cesm_tokenizer'))
        print(" Loaded custom CESM tokenizer")
    except Exception as e:
        print(f"¥î Could not load custom tokenizer: {e}")
        print("   Make sure models/cesm_tokenizer/ directory exists!")
        return None, None, None
    
    model = CESMBert(num_classes=len(label2id))
    try:
        model.load_state_dict(torch.load(os.path.join(script_dir, 'models/cesm_model.pth'), map_location=device))
        model.to(device)
        model.eval()
        print(" Loaded trained model")
    except FileNotFoundError:
        print("¥î Could not find trained model")
        return None, None, None
    
    return model, tokenizer, id2label

def predict_cesm_variable(text, model, tokenizer, id2label, max_length=128):
    """Predict CESM variable for given text"""
    encoding = tokenizer(
        text,
        add_special_tokens=True,
        max_length=max_length,
        padding='max_length',
        truncation=True,
        return_attention_mask=True,
        return_tensors='pt'
    )
    
    input_ids = encoding['input_ids'].to(device)
    attention_mask = encoding['attention_mask'].to(device)
    
    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        probabilities = torch.softmax(outputs, dim=1)
        predicted_class = torch.argmax(probabilities, dim=1).item()
        confidence = probabilities[0, predicted_class].item()
    
    predicted_cesm = id2label[predicted_class]
    return predicted_cesm, confidence

def extract_meaningful_tokens(text):
    """Extract meaningful tokens from dataset text"""
    if not text:
        return []
    
    # Clean the text
    text = text.lower()
    
    # Split into potential phrases
    tokens = []
    
    # 1. Split by common separators
    for separator in [',', ';', '|', '\n', '. ']:
        if separator in text:
            tokens.extend([t.strip() for t in text.split(separator) if t.strip()])
            break
    else:
        tokens = [text.strip()]
    
    # 2. Extract meaningful phrases (2-4 words)
    meaningful_tokens = []
    for token in tokens:
        words = token.split()
        
        # Single meaningful words
        if len(words) == 1 and len(words[0]) > 3:
            meaningful_tokens.append(token)
        
        # Phrases of 2-9 words (optimized for CESM description lengths)
        elif 2 <= len(words) <= 9:
            meaningful_tokens.append(token)
        
        # Break down longer phrases (>9 words)
        elif len(words) > 9:
            # Try to extract key phrases of various lengths
            for i in range(len(words) - 1):
                # 2-word phrases
                if i < len(words) - 1:
                    phrase2 = ' '.join(words[i:i+2])
                    meaningful_tokens.append(phrase2)
                # 3-word phrases  
                if i < len(words) - 2:
                    phrase3 = ' '.join(words[i:i+3])
                    meaningful_tokens.append(phrase3)
                # 4-word phrases (most common CESM length)
                if i < len(words) - 3:
                    phrase4 = ' '.join(words[i:i+4])
                    meaningful_tokens.append(phrase4)
                # 6-word phrases (median CESM length)
                if i < len(words) - 5:
                    phrase6 = ' '.join(words[i:i+6])
                    meaningful_tokens.append(phrase6)
    
    # Remove duplicates and filter
    seen = set()
    filtered_tokens = []
    for token in meaningful_tokens:
        token = token.strip()
        if (token not in seen and 
            len(token) > 3 and 
            not token.isdigit() and
            token not in ['data', 'analysis', 'study', 'research', 'project']):
            seen.add(token)
            filtered_tokens.append(token)
    
    return filtered_tokens[:20]  # Limit to top 20 tokens

def extract_dataset_summary(cmr_entry):
    """Extract comprehensive text summary from CMR dataset entry"""
    summary_parts = []
    
    # Dataset information
    dataset = cmr_entry.get('Dataset', {})
    if dataset.get('title'):
        summary_parts.append(dataset['title'])
    if dataset.get('summary'):
        summary_parts.append(dataset['summary'])
    if dataset.get('abstract'):
        summary_parts.append(dataset['abstract'])
    
    # DataCategory summary - This is where most content is stored!
    data_category = cmr_entry.get('DataCategory', {})
    if data_category.get('summary'):
        summary_parts.append(data_category['summary'])
    
    # Variables information
    variables = cmr_entry.get('Variable', [])
    for var in variables:
        for field in ['name', 'long_name', 'description', 'standard_name']:
            if var.get(field):
                summary_parts.append(var[field])
    
    # Additional metadata
    if cmr_entry.get('Platform'):
        platforms = cmr_entry['Platform']
        if isinstance(platforms, list):
            for platform in platforms:
                if platform.get('short_name'):
                    summary_parts.append(f"Platform: {platform['short_name']}")
        elif platforms.get('short_name'):
            summary_parts.append(f"Platform: {platforms['short_name']}")
    
    if cmr_entry.get('Instrument'):
        instruments = cmr_entry['Instrument']
        if isinstance(instruments, list):
            for instrument in instruments:
                if instrument.get('short_name'):
                    summary_parts.append(f"Instrument: {instrument['short_name']}")
        elif instruments.get('short_name'):
            summary_parts.append(f"Instrument: {instruments['short_name']}")
    
    # Join all parts
    full_summary = ' '.join(summary_parts)
    return full_summary.strip()

def classify_prediction_quality(confidence):
    """Classify prediction quality based on confidence"""
    if confidence >= 0.8:
        return "HIGHLY_RELIABLE", ""
    elif confidence >= 0.6:
        return "RELIABLE", "í"
    elif confidence >= 0.5:
        return "MODERATE", "á"
    elif confidence >= 0.3:
        return "LOW_CONFIDENCE", "┤"
    else:
        return "REJECT", "¥î"


def deduplicate_datasets(cmr_data):
    """Remove duplicate datasets (same title, different IDs)"""
    print(" Deduplicating datasets...")
    
    seen_titles = {}
    deduplicated_data = []
    duplicates_removed = 0
    
    for i, entry in enumerate(cmr_data):
        title = entry.get('Dataset', {}).get('title', f'Dataset_{i+1}')
        
        if title not in seen_titles:
            # First occurrence - keep it
            seen_titles[title] = i
            deduplicated_data.append(entry)
        else:
            # Duplicate found - choose the better version
            current_version = entry.get('Dataset', {}).get('version_id', 'Not provided')
            
            # Find and compare with the original entry
            original_entry = None
            original_idx_in_dedup = None
            for j, stored_entry in enumerate(deduplicated_data):
                if stored_entry.get('Dataset', {}).get('title') == title:
                    original_entry = stored_entry
                    original_idx_in_dedup = j
                    break
            
            if original_entry:
                original_version = original_entry.get('Dataset', {}).get('version_id', 'Not provided')
                
                # If current has version and original doesn't, replace
                if current_version != 'Not provided' and original_version == 'Not provided':
                    deduplicated_data[original_idx_in_dedup] = entry
                duplicates_removed += 1
                print(f"   Replaced duplicate: {title[:60]}... (kept entry with version {current_version})")
            else:
                # Keep original, discard current
                duplicates_removed += 1
                print(f"   Removed duplicate: {title[:60]}... (kept original)")
    
    print(f" Removed {duplicates_removed} duplicate datasets")
    print(f" Deduplicated: {len(cmr_data)} åÆ {len(deduplicated_data)} datasets")
    
    return deduplicated_data

def predict_cmr_datasets(confidence_threshold=0.3):
    """Predict CESM variables for CMR datasets"""
    # Load model
    model, tokenizer, id2label = load_trained_model()
    if model is None:
        return
    
    # Load CMR data
    print("è Loading NASA CMR data...")
    try:
        print("   Loading large JSON file (634MB)...")
        cmr_data_path = os.path.join(os.path.dirname(script_dir), 'NasaCMRData/json_files/individual_cmr_data.json')
        with open(cmr_data_path, 'r', encoding='utf-8') as f:
            raw_cmr_data = json.load(f)
        print(f" Loaded {len(raw_cmr_data)} CMR datasets")
        
        # Deduplicate datasets
        cmr_data = deduplicate_datasets(raw_cmr_data)
        
    except FileNotFoundError:
        print(f"¥î Could not find {cmr_data_path}")
        return
    
    print(f" Using confidence threshold: {confidence_threshold}")
    print(f"ì Processing {len(cmr_data)} datasets...")
    
    results = []
    reliable_predictions = 0
    total_predictions = 0
    
    for i, cmr_entry in enumerate(cmr_data):
        # Extract dataset information
        dataset_title = cmr_entry.get('Dataset', {}).get('title', f'Dataset_{i+1}')
        dataset_id = cmr_entry.get('Dataset', {}).get('id', f'ID_{i+1}')
        
        # Create comprehensive summary
        full_summary = extract_dataset_summary(cmr_entry)
        
        if not full_summary.strip():
            print(f"[{i+1:4d}] Üá∩╕Å  Skipping dataset with no summary: {dataset_title[:50]}...")
            continue
        
        try:
            # Extract meaningful tokens from the dataset
            meaningful_tokens = extract_meaningful_tokens(full_summary)
            
            if not meaningful_tokens:
                print(f"[{i+1:4d}] Üá∩╕Å  No meaningful tokens after extraction: {dataset_title[:50]}...")
                continue
            
            # Test each token and collect all predictions
            all_predictions = []
            
            for token in meaningful_tokens:  # Test all extracted tokens
                try:
                    predicted_cesm, confidence = predict_cesm_variable(
                        token, model, tokenizer, id2label
                    )
                    
                    all_predictions.append({
                        'variable': predicted_cesm,
                        'confidence': confidence,
                        'token': token
                    })
                        
                except Exception as e:
                    continue
            
            if not all_predictions:
                continue
            
            # Group predictions by similarity groups FIRST
            predictions_by_group = defaultdict(list)
            
            for pred in all_predictions:
                variable = pred['variable']
                
                # Check if variable is in a similarity group
                if variable in var_to_group:
                    group_id = var_to_group[variable]['group_id']
                    predictions_by_group[f"group_{group_id}"].append(pred)
                else:
                    # Individual variable (not in any group)
                    predictions_by_group[f"individual_{variable}"].append(pred)
            
            # For EACH group, calculate aggregated confidence and check threshold
            group_candidates = []
            
            for group_key, predictions in predictions_by_group.items():
                # Sort by confidence (highest first)
                predictions.sort(key=lambda x: x['confidence'], reverse=True)
                
                individual_best = predictions[0]['confidence']
                
                # If individual prediction already meets threshold, use it directly
                if individual_best >= confidence_threshold:
                    aggregated_confidence = individual_best
                    use_individual = True
                else:
                    # Otherwise, try group aggregation with top 2 confidences
                    top_2_sum = sum(p['confidence'] for p in predictions[:2])
                    aggregated_confidence = top_2_sum
                    use_individual = False
                
                # Only consider groups that meet the confidence threshold
                if aggregated_confidence >= confidence_threshold:
                    # Get group info for display
                    group_members = []
                    if group_key.startswith("group_"):
                        group_id = int(group_key.split("_")[1])
                        if group_id in group_info:
                            group_members = group_info[group_id]['members']
                    else:
                        group_members = [predictions[0]['variable']]
                    
                    group_candidates.append({
                        'group_key': group_key,
                        'aggregated_confidence': aggregated_confidence,
                        'individual_confidence': individual_best,
                        'use_individual': use_individual,
                        'predictions': predictions,
                        'representative_variable': predictions[0]['variable'],
                        'group_members': group_members,
                        'tokens': [p['token'] for p in predictions[:2]]
                    })
            
            # If no groups meet the threshold, skip this dataset
            if not group_candidates:
                continue
            
            # Create results for ALL group candidates that meet the threshold
            for group_candidate in group_candidates:
                best_group = group_candidate['group_key']
                best_total_confidence = group_candidate['aggregated_confidence']
                best_individual_confidence = group_candidate['individual_confidence']
                best_prediction = group_candidate['representative_variable']
                best_group_members = group_candidate['group_members']
                best_tokens = group_candidate['tokens']
                used_individual = group_candidate.get('use_individual', False)
                
                total_predictions += 1
                quality, emoji = classify_prediction_quality(best_total_confidence)
                
                # Since we already filtered by threshold, all predictions meet the threshold
                meets_threshold = True
                reliable_predictions += 1
                
                result = {
                    'dataset_id': dataset_id,
                    'dataset_title': dataset_title,
                    'predicted_cesm_variable': best_prediction,
                    'individual_confidence': best_individual_confidence,
                    'aggregated_confidence': best_total_confidence,
                    'quality_rating': quality,
                    'meets_threshold': meets_threshold,
                    'best_matching_tokens': best_tokens[:2],
                    'group_type': best_group,
                    'group_members': best_group_members,
                    'used_individual_confidence': used_individual,
                    'total_tokens_processed': len(meaningful_tokens),
                    'input_summary': full_summary[:500] + "..." if len(full_summary) > 500 else full_summary,
                    'full_summary_length': len(full_summary)
                }
                results.append(result)
            
            # Print progress
            if (i + 1) % 50 == 0 or (i + 1) <= 10:
                print(f"[{i+1:4d}] è {dataset_title[:40]}... ({len(group_candidates)} predictions)")
                for j, candidate in enumerate(group_candidates):
                    quality, emoji = classify_prediction_quality(candidate['aggregated_confidence'])
                    confidence_type = "IND" if candidate.get('use_individual', False) else "AGG"
                    print(f"       [{j+1}] {emoji}  {candidate['representative_variable']} ({confidence_type}: {candidate['aggregated_confidence']:.3f}, ind: {candidate['individual_confidence']:.3f})")
                    
                    # Show group info
                    if candidate['group_key'].startswith("group_"):
                        group_type = "individual confidence" if candidate.get('use_individual', False) else f"{len(candidate['group_members'])} similar variables"
                        print(f"           Group: {group_type}")
                    else:
                        print(f"           Individual variable (no group)")
                
                print(f"       Processed {len(meaningful_tokens)} total tokens")
        
        except Exception as e:
            print(f"[{i+1:4d}] ¥î Error processing dataset: {e}")
            continue
    
    # Deduplicate predictions (same dataset + same CESM variable)
    print(f"\n Deduplicating predictions...")
    original_count = len(results)
    
    # Convert to DataFrame for easier deduplication
    results_df = pd.DataFrame(results)
    
    # Remove duplicates based on dataset_title + predicted_cesm_variable
    # Keep the one with highest aggregated confidence
    deduplicated_df = results_df.sort_values('aggregated_confidence', ascending=False).drop_duplicates(
        subset=['dataset_title', 'predicted_cesm_variable'], keep='first'
    )
    
    duplicates_removed = original_count - len(deduplicated_df)
    print(f" Removed {duplicates_removed} duplicate predictions (same dataset + same CESM variable)")
    print(f" Deduplicated predictions: {original_count} åÆ {len(deduplicated_df)}")
    
    # Save results
    output_path = os.path.join(script_dir, 'predictions/cmr_dataset_predictions.csv')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    deduplicated_df.to_csv(output_path, index=False)
    print(f"\nÆ╛ Saved {len(deduplicated_df)} predictions to {output_path}")
    
    # Update results for analysis
    results = deduplicated_df.to_dict('records')
    
    # Analysis
    analyze_cmr_predictions(results, confidence_threshold)
    
    return results

def analyze_cmr_predictions(results, confidence_threshold):
    """Analyze CMR prediction results"""
    print(f"\nè CMR PREDICTION ANALYSIS:")
    
    total = len(results)
    reliable = sum(1 for r in results if r['meets_threshold'])
    
    print(f"Total datasets processed: {total}")
    print(f"Reliable predictions (ëÑ{confidence_threshold}): {reliable} ({reliable/total*100:.1f}%)")
    
    # Confidence distribution (using aggregated confidence)
    confidence_ranges = {
        'HIGHLY_RELIABLE (ëÑ0.9)': sum(1 for r in results if r['aggregated_confidence'] >= 0.9),
        'RELIABLE (0.8-0.9)': sum(1 for r in results if 0.8 <= r['aggregated_confidence'] < 0.9),
        'MODERATE (0.7-0.8)': sum(1 for r in results if 0.7 <= r['aggregated_confidence'] < 0.8),
        'LOW (0.5-0.7)': sum(1 for r in results if 0.5 <= r['aggregated_confidence'] < 0.7),
        'VERY_LOW (<0.5)': sum(1 for r in results if r['aggregated_confidence'] < 0.5)
    }
    
    print(f"\nConfidence distribution:")
    for category, count in confidence_ranges.items():
        percentage = count/total*100 if total > 0 else 0
        print(f"  {category}: {count} ({percentage:.1f}%)")
    
    # Most common predictions
    predictions = [r['predicted_cesm_variable'] for r in results if r['meets_threshold']]
    if predictions:
        prediction_counts = Counter(predictions)
        print(f"\nTop 10 predicted CESM variables (reliable predictions only):")
        for cesm_var, count in prediction_counts.most_common(10):
            print(f"  {cesm_var}: {count} datasets")
    
    # Summary length analysis
    avg_summary_length = sum(r['full_summary_length'] for r in results) / len(results)
    print(f"\nAverage summary length: {avg_summary_length:.0f} characters")
    
    # Show some high-confidence examples
    high_conf_results = [r for r in results if r['aggregated_confidence'] >= 0.9]
    if high_conf_results:
        print(f"\n High-confidence predictions (sample):")
        for r in high_conf_results[:5]:
            print(f"  Dataset: {r['dataset_title'][:60]}...")
            print(f"    åÆ {r['predicted_cesm_variable']} (agg: {r['aggregated_confidence']:.3f}, ind: {r['individual_confidence']:.3f})")
            print()

def main():
    """Main function"""
    print("¢░∩╕Å  NASA CMR Dataset åÆ CESM Variable Predictor")
    print("=" * 60)
    
    # Run predictions with 0.3 confidence threshold (better coverage with optimized tokens)
    results = predict_cmr_datasets(confidence_threshold=0.3)
    
    if results:
        reliable_count = sum(1 for r in results if r['meets_threshold'])
        print(f"\n SUMMARY:")
        print(f"Processed {len(results)} datasets")
        print(f"Found {reliable_count} reliable CESM variable matches")
        print(f"Success rate: {reliable_count/len(results)*100:.1f}%")

if __name__ == "__main__":
    main()
