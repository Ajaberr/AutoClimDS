#!/usr/bin/env python3
"""
Test the trained CESM model on CESM variable descriptions to predict variable names
"""

import torch
import json
import pandas as pd
from transformers import AutoTokenizer, AutoModel
import torch.nn as nn
from collections import Counter
import random
import matplotlib.pyplot as plt
from difflib import SequenceMatcher
import os
from datetime import datetime

# Check device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"ÜÇ Using device: {device}")

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
    
    # Load label mappings
    try:
        label2id = torch.load('models/label2id.pth', weights_only=False)
        id2label = torch.load('models/id2label.pth')
        print(f" Loaded {len(label2id)} class mappings")
    except FileNotFoundError:
        print("¥î Could not find models/label2id.pth or models/id2label.pth")
        print("   Make sure you've trained the model first!")
        return None, None, None
    
    # Load tokenizer
    try:
        tokenizer = AutoTokenizer.from_pretrained('models/cesm_tokenizer')
        print(" Loaded tokenizer")
    except:
        print("¥î Could not load tokenizer from models/cesm_tokenizer/")
        print("   Falling back to original tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained("climatebert/distilroberta-base-climate-f")
    
    # Initialize and load model
    model = CESMBert(num_classes=len(label2id))
    try:
        model.load_state_dict(torch.load('models/cesm_model.pth', map_location=device))
        model.to(device)
        model.eval()
        print(" Loaded trained model")
    except FileNotFoundError:
        print("¥î Could not find cesm_model.pth")
        print("   Make sure you've trained the model first!")
        return None, None, None
    
    return model, tokenizer, id2label

def predict_cesm_variable(text, model, tokenizer, id2label, max_length=128):
    """Predict CESM variable for given text"""
    # Tokenize input
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
    
    # Get prediction
    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        probabilities = torch.softmax(outputs, dim=1)
        predicted_class = torch.argmax(probabilities, dim=1).item()
        confidence = probabilities[0, predicted_class].item()
    
    predicted_cesm = id2label[predicted_class]
    
    return predicted_cesm, confidence

def string_similarity(a, b):
    """Calculate string similarity between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_similar_variables(variable_name, all_variables, threshold=0.7):
    """Find variables with high string similarity"""
    similar = []
    for var in all_variables:
        if var != variable_name:
            similarity = string_similarity(variable_name, var)
            if similarity >= threshold:
                similar.append((var, similarity))
    return similar

def are_variables_in_same_group(var1, var2, all_variables, threshold=0.7):
    """Check if two variables are in the same similarity group (by variable name)"""
    if var1 == var2:
        return True
    
    # Check direct similarity
    if string_similarity(var1, var2) >= threshold:
        return True
    
    # Check if they share any similar variables (transitive similarity)
    var1_similar = set(var[0] for var in find_similar_variables(var1, all_variables, threshold))
    var2_similar = set(var[0] for var in find_similar_variables(var2, all_variables, threshold))
    
    # If var2 is similar to var1, or they share similar variables
    return var2 in var1_similar or var1 in var2_similar or bool(var1_similar & var2_similar)

def normalize_description(desc):
    """Normalize description for better comparison"""
    if not desc or desc.strip().lower() in ['unknown', '', 'nan']:
        return ""
    
    # Clean and normalize
    desc = desc.lower().strip()
    
    # Remove common prefixes that don't add semantic meaning
    prefixes_to_remove = ['atm ', 'lnd ', 'ocn ', 'ice ', 'component ']
    for prefix in prefixes_to_remove:
        if desc.startswith(prefix):
            desc = desc[len(prefix):]
    
    return desc

def are_descriptions_similar(desc1, desc2, threshold=0.8):
    """Check if two descriptions are similar enough to be considered same group"""
    if not desc1 or not desc2:
        return False
    
    desc1_norm = normalize_description(desc1)
    desc2_norm = normalize_description(desc2)
    
    if not desc1_norm or not desc2_norm:
        return False
    
    return string_similarity(desc1_norm, desc2_norm) >= threshold

def create_similarity_groups(cesm_df):
    """Create groups of similar CESM variables (desc_sim >= 0.7 OR name_sim >= 0.8)"""
    valid_vars = cesm_df.dropna(subset=['cesm_name', 'description'])
    valid_vars = valid_vars[~valid_vars['description'].str.lower().isin(['unknown', 'nan', ''])]
    
    variable_to_group = {}
    group_id = 0
    
    variables = [(row['cesm_name'].strip(), row['description'].strip()) for _, row in valid_vars.iterrows()]
    
    for i in range(len(variables)):
        for j in range(i + 1, len(variables)):
            name1, desc1 = variables[i]
            name2, desc2 = variables[j]
            
            # Check similarity conditions
            desc_sim = string_similarity(normalize_description(desc1), normalize_description(desc2))
            name_sim = string_similarity(name1, name2)
            
            if desc_sim >= 0.7 or name_sim >= 0.8:
                # Get existing groups
                group1 = variable_to_group.get(name1)
                group2 = variable_to_group.get(name2)
                
                if group1 is None and group2 is None:
                    # Create new group
                    group_id += 1
                    variable_to_group[name1] = group_id
                    variable_to_group[name2] = group_id
                elif group1 and not group2:
                    variable_to_group[name2] = group1
                elif group2 and not group1:
                    variable_to_group[name1] = group2
                elif group1 != group2:
                    # Merge groups
                    for var, grp in variable_to_group.items():
                        if grp == group2:
                            variable_to_group[var] = group1
    
    # Save similarity groups
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(script_dir, 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    groups_file = os.path.join(results_dir, f'similarity_groups_{timestamp}.json')
    
    # Convert to more readable format
    groups_info = {}
    for var, group_id in variable_to_group.items():
        if group_id not in groups_info:
            groups_info[group_id] = []
        groups_info[group_id].append(var)
    
    with open(groups_file, 'w') as f:
        json.dump(groups_info, f, indent=2)
    
    print(f" Similarity groups saved to: {groups_file}")
    
    return variable_to_group

def test_similarity_accuracy(cesm_df):
    """Test prediction accuracy with and without similarity grouping"""
    print(f" Testing prediction accuracy with similarity grouping")
    
    model, tokenizer, id2label = load_trained_model()
    if model is None:
        return None
    
    variable_to_group = create_similarity_groups(cesm_df)
    
    valid_rows = cesm_df.dropna(subset=['cesm_name', 'description'])
    valid_rows = valid_rows[~valid_rows['description'].str.lower().isin(['unknown', 'nan', ''])]
    
    exact_correct = 0
    group_correct = 0
    
    for _, row in valid_rows.iterrows():
        actual = row['cesm_name'].strip()
        description = row['description'].strip()
        
        try:
            predicted, confidence = predict_cesm_variable(description, model, tokenizer, id2label)
            
            # Exact match
            if predicted == actual:
                exact_correct += 1
                group_correct += 1
            # Same group match
            elif (variable_to_group.get(predicted) and 
                  variable_to_group.get(actual) and
                  variable_to_group[predicted] == variable_to_group[actual]):
                group_correct += 1
        except:
            continue
    
    total = len(valid_rows)
    exact_accuracy = (exact_correct / total * 100) if total > 0 else 0
    group_accuracy = (group_correct / total * 100) if total > 0 else 0
    
    print(f" Results: Exact {exact_accuracy:.1f}% | Group {group_accuracy:.1f}% | Improvement +{group_accuracy-exact_accuracy:.1f}%")
    
    # Save results
    results = {
        'exact_accuracy': exact_accuracy,
        'group_accuracy': group_accuracy,
        'improvement': group_accuracy - exact_accuracy,
        'exact_correct': exact_correct,
        'group_correct': group_correct,
        'total_tested': total,
        'timestamp': datetime.now().isoformat()
    }
    
    # Create results folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(script_dir, 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(results_dir, f'similarity_accuracy_{timestamp}.json')
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f" Results saved to: {results_file}")
    
    return results

def load_cesm_variables():
    """Load CESM variable descriptions"""
    print("è Loading CESM variables...")
    try:
        df = pd.read_csv('../NasaCMRData/cesm_variables/cesm_variables_raw.csv')
        print(f" Loaded {len(df)} CESM variables")
        return df
    except FileNotFoundError:
        print("¥î Could not find ../NasaCMRData/cesm_variables_raw.csv")
        return None

def test_cesm_predictions(similarity_threshold=0.7, grouping_type="name"):
    """Test model predictions on CESM variable descriptions with similarity grouping
    
    Args:
        similarity_threshold: Threshold for similarity matching
        grouping_type: "name" for variable name grouping, "description" for description grouping
    """
    # Load model
    model, tokenizer, id2label = load_trained_model()
    if model is None:
        return
    
    # Get all variable names for similarity checking
    all_variables = list(id2label.values())
    print(f"ï Loaded {len(all_variables)} CESM variables for similarity analysis")
    print(f" Using {grouping_type} grouping with {similarity_threshold} threshold")
    
    # Load CESM variables
    cesm_df = load_cesm_variables()
    if cesm_df is None:
        return
    
    # Create mapping of variable name to description (for description grouping)
    variable_descriptions = {}
    if grouping_type == "description":
        for _, row in cesm_df.iterrows():
            var_name = row.get('cesm_name', '').strip()
            description = row.get('description', '').strip()
            if var_name and description:
                variable_descriptions[var_name] = description
        print(f"ï Created description mapping for {len(variable_descriptions)} variables")
    
    # Filter out rows with missing descriptions or variable names
    valid_rows = cesm_df.dropna(subset=['cesm_name', 'description'])
    valid_rows = valid_rows[valid_rows['description'].str.strip() != '']
    valid_rows = valid_rows[valid_rows['cesm_name'].str.strip() != '']
    
    print(f"ê Found {len(valid_rows)} valid CESM variables with descriptions")
    
    # Test on ALL valid variables
    test_sample = valid_rows
    sample_size = len(test_sample)
    
    print(f" Testing on ALL {sample_size} variables")
    
    results = []
    correct_predictions = 0
    
    print("\nì Testing predictions...")
    
    for i, (idx, row) in enumerate(test_sample.iterrows()):
        actual_cesm = row['cesm_name'].strip()
        description = row['description'].strip()
        
        # Create input text (description + any other relevant info)
        input_texts = [
            description,  # Just description
            f"{description} {row.get('standard_type', '')}".strip(),  # Description + standard type
            f"{row.get('standard_type', '')} {description}".strip(),  # Standard type + description
        ]
        
        best_prediction = None
        best_confidence = 0
        best_input = None
        
        # Try different input formulations and take the one with highest confidence
        for input_text in input_texts:
            if input_text:
                try:
                    predicted_cesm, confidence = predict_cesm_variable(
                        input_text, model, tokenizer, id2label
                    )
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_prediction = predicted_cesm
                        best_input = input_text
                        
                except Exception as e:
                    print(f"¥î Error processing variable {i+1}: {e}")
                    continue
        
        if best_prediction is None:
            continue
            
        # Check if prediction is correct (exact match)
        is_exact_correct = (best_prediction == actual_cesm)
        
        # Check if prediction is in the same similarity group
        is_group_correct = are_variables_in_same_group(
            best_prediction, actual_cesm, all_variables, similarity_threshold
        )
        
        if is_exact_correct:
            correct_predictions += 1
        
        # Calculate similarity score for analysis
        similarity_score = string_similarity(best_prediction, actual_cesm)
        
        result = {
            'actual_cesm': actual_cesm,
            'predicted_cesm': best_prediction,
            'confidence': best_confidence,
            'is_exact_correct': is_exact_correct,
            'is_group_correct': is_group_correct,
            'similarity_score': similarity_score,
            'input_text': best_input,
            'description': description,
            'standard_type': row.get('standard_type', ''),
            'units': row.get('units', ''),
            'component': row.get('component', '')
        }
        results.append(result)
        
        # Print progress every 100 items to avoid overwhelming output
        if (i + 1) % 100 == 0 or (i + 1) <= 10:
            if is_exact_correct:
                status = ""
            elif is_group_correct:
                status = "ù"  # Similar group
            else:
                status = "¥î"
            
            print(f"[{i+1:4d}] {status} {actual_cesm} åÆ {best_prediction} ({best_confidence:.3f})")
            if not is_exact_correct and (i + 1) <= 10:
                print(f"       Description: {description[:60]}...")
                if is_group_correct:
                    print(f"       Note: Prediction is in same similarity group (sim: {similarity_score:.3f})")
    
    # Calculate and display results
    total_tested = len(results)
    exact_accuracy = (correct_predictions / total_tested * 100) if total_tested > 0 else 0
    
    # Calculate group accuracy (including similar variables)
    group_correct = sum(1 for r in results if r['is_group_correct'])
    group_accuracy = (group_correct / total_tested * 100) if total_tested > 0 else 0
    
    print(f"\nè RESULTS SUMMARY:")
    print(f"Total tested: {total_tested}")
    print(f"Exact matches: {correct_predictions} ({exact_accuracy:.2f}%)")
    print(f"Group matches (including similar): {group_correct} ({group_accuracy:.2f}%)")
    print(f"Improvement with similarity grouping: +{group_accuracy - exact_accuracy:.2f}%")
    
    # Save detailed results
    results_df = pd.DataFrame(results)
    results_df.to_csv('results/cesm_self_test_results.csv', index=False)
    print(f"Æ╛ Detailed results saved to results/cesm_self_test_results.csv")
    
    # Analyze results
    analyze_results(results, similarity_threshold)
    
    return results, exact_accuracy, group_accuracy

def analyze_results(results, similarity_threshold=0.7):
    """Analyze the test results with similarity grouping"""
    print(f"\nê DETAILED ANALYSIS:")
    
    if not results:
        return
    
    # Categorize results
    exact_correct = [r for r in results if r['is_exact_correct']]
    group_correct_not_exact = [r for r in results if r['is_group_correct'] and not r['is_exact_correct']]
    incorrect_results = [r for r in results if not r['is_group_correct']]
    
    # Confidence analysis
    if exact_correct:
        avg_exact_conf = sum(r['confidence'] for r in exact_correct) / len(exact_correct)
        print(f"Average confidence for exact matches: {avg_exact_conf:.3f}")
    
    if group_correct_not_exact:
        avg_group_conf = sum(r['confidence'] for r in group_correct_not_exact) / len(group_correct_not_exact)
        avg_similarity = sum(r['similarity_score'] for r in group_correct_not_exact) / len(group_correct_not_exact)
        print(f"Average confidence for group matches: {avg_group_conf:.3f}")
        print(f"Average similarity for group matches: {avg_similarity:.3f}")
    
    if incorrect_results:
        avg_incorrect_conf = sum(r['confidence'] for r in incorrect_results) / len(incorrect_results)
        print(f"Average confidence for incorrect predictions: {avg_incorrect_conf:.3f}")
    
    # Show examples of group matches (similar but not exact)
    if group_correct_not_exact:
        print(f"\nù Similar group matches (sample):")
        for r in group_correct_not_exact[:5]:
            print(f"  Expected: {r['actual_cesm']} | Got: {r['predicted_cesm']}")
            print(f"    Confidence: {r['confidence']:.3f} | Similarity: {r['similarity_score']:.3f}")
            print(f"    Description: {r['description'][:60]}...")
    
    # Most common incorrect predictions
    if incorrect_results:
        wrong_predictions = Counter([r['predicted_cesm'] for r in incorrect_results])
        print(f"\nMost common incorrect predictions:")
        for pred, count in wrong_predictions.most_common(5):
            print(f"  {pred}: {count} times")
    
    # Show some examples of correct high-confidence predictions
    high_conf_exact = [r for r in exact_correct if r['confidence'] > 0.8]
    if high_conf_exact:
        print(f"\n High-confidence exact matches (sample):")
        for r in high_conf_exact[:5]:
            print(f"  {r['actual_cesm']} ({r['confidence']:.3f})")
            print(f"    Description: {r['description'][:60]}...")
    
    # Component-wise analysis
    component_stats = {}
    for r in results:
        comp = r.get('component', 'unknown')
        if comp not in component_stats:
            component_stats[comp] = {'exact': 0, 'group': 0, 'total': 0}
        component_stats[comp]['total'] += 1
        if r['is_exact_correct']:
            component_stats[comp]['exact'] += 1
        if r['is_group_correct']:
            component_stats[comp]['group'] += 1
    
    print(f"\nAccuracy by component:")
    for comp, stats in component_stats.items():
        if stats['total'] > 0:
            exact_acc = stats['exact'] / stats['total'] * 100
            group_acc = stats['group'] / stats['total'] * 100
            print(f"  {comp}: Exact {exact_acc:.1f}% | Group {group_acc:.1f}% ({stats['exact']}/{stats['group']}/{stats['total']})")

def main():
    """Main function"""
    print(" CESM Self-Test: Predicting CESM Variables from Descriptions (with Similarity Grouping)")
    print("=" * 80)
    
    results, exact_accuracy, group_accuracy = test_cesm_predictions()
    
    print(f"\n FINAL RESULTS:")
    print(f"Exact Match Accuracy: {exact_accuracy:.2f}%")
    print(f"Group Match Accuracy: {group_accuracy:.2f}%")
    print(f"Improvement: +{group_accuracy - exact_accuracy:.2f}%")

if __name__ == "__main__":
    main()
