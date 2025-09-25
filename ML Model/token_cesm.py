#!/usr/bin/env python3
"""
Token-based CESM variable matcher
Break down dataset summaries into tokens and find high-confidence matches
"""

import torch
import json
import pandas as pd
from transformers import AutoTokenizer, AutoModel
import torch.nn as nn
from collections import defaultdict
import re

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
    
    try:
        label2id = torch.load('models/label2id.pth')
        id2label = torch.load('models/id2label.pth')
        print(f" Loaded {len(label2id)} class mappings")
    except FileNotFoundError:
        print("¥î Could not find label mappings")
        return None, None, None
    
    try:
        tokenizer = AutoTokenizer.from_pretrained('models/cesm_tokenizer')
        print(" Loaded tokenizer")
    except:
        tokenizer = AutoTokenizer.from_pretrained("climatebert/distilroberta-base-climate-f")
    
    model = CESMBert(num_classes=len(label2id))
    try:
        model.load_state_dict(torch.load('models/cesm_model.pth', map_location=device))
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
        
        # Phrases of 2-6 words
        elif 2 <= len(words) <= 6:
            meaningful_tokens.append(token)
        
        # Break down longer phrases
        elif len(words) > 6:
            # Try to extract key phrases
            for i in range(len(words) - 1):
                phrase = ' '.join(words[i:i+2])
                meaningful_tokens.append(phrase)
                if i < len(words) - 2:
                    phrase3 = ' '.join(words[i:i+3])
                    meaningful_tokens.append(phrase3)
    
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

def analyze_dataset_with_tokens():
    """Analyze datasets by breaking them into tokens"""
    # Load model
    model, tokenizer, id2label = load_trained_model()
    if model is None:
        return
    
    # Load CMR data
    print("è Loading CMR data...")
    try:
        with open('../NasaCMRData/json_files/individual_cmr_data.json', 'r') as f:
            cmr_data = json.load(f)
        print(f" Loaded {len(cmr_data)} CMR entries")
    except FileNotFoundError:
        print("¥î Could not find ../NasaCMRData/json_files/individual_cmr_data.json")
        return
    
    results = []
    confidence_threshold = 0.5
    
    print(f"\nì Analyzing datasets with confidence threshold: {confidence_threshold}")
    
    for i, entry in enumerate(cmr_data[:10]):  # Analyze first 10 datasets
        dataset_title = entry.get('Dataset', {}).get('title', 'Unknown Dataset')
        print(f"\n[{i+1}] Dataset: {dataset_title[:60]}...")
        
        # Collect all text from the dataset
        all_text = []
        
        # Dataset title and summary
        if dataset_title:
            all_text.append(dataset_title)
        
        # Variables
        for var in entry.get('Variable', []):
            for field in ['name', 'long_name', 'description', 'standard_name']:
                text = var.get(field, '')
                if text and text.strip():
                    all_text.append(text.strip())
        
        # Combine all text
        combined_text = ' '.join(all_text)
        
        # Extract meaningful tokens
        tokens = extract_meaningful_tokens(combined_text)
        print(f"    Extracted {len(tokens)} tokens")
        
        # Test each token
        high_confidence_matches = []
        for token in tokens:
            try:
                predicted_cesm, confidence = predict_cesm_variable(
                    token, model, tokenizer, id2label
                )
                
                if confidence >= confidence_threshold:
                    high_confidence_matches.append({
                        'token': token,
                        'cesm_variable': predicted_cesm,
                        'confidence': confidence
                    })
                    print(f"     '{token}' åÆ {predicted_cesm} ({confidence:.3f})")
            except Exception as e:
                continue
        
        # Store results
        result = {
            'dataset': dataset_title,
            'total_tokens': len(tokens),
            'high_confidence_matches': high_confidence_matches,
            'matched_cesm_variables': [m['cesm_variable'] for m in high_confidence_matches]
        }
        results.append(result)
        
        if not high_confidence_matches:
            print(f"    ¥î No high-confidence matches found")
        else:
            print(f"    ê Found {len(high_confidence_matches)} high-confidence matches")
    
    # Summary analysis
    print(f"\nè SUMMARY ANALYSIS:")
    total_datasets = len(results)
    datasets_with_matches = sum(1 for r in results if r['high_confidence_matches'])
    total_matches = sum(len(r['high_confidence_matches']) for r in results)
    
    print(f"Datasets analyzed: {total_datasets}")
    print(f"Datasets with matches: {datasets_with_matches}/{total_datasets}")
    print(f"Total high-confidence matches: {total_matches}")
    print(f"Average matches per dataset: {total_matches/total_datasets:.1f}")
    
    # Most common CESM variables
    all_cesm_vars = []
    for r in results:
        all_cesm_vars.extend(r['matched_cesm_variables'])
    
    if all_cesm_vars:
        from collections import Counter
        cesm_counts = Counter(all_cesm_vars)
        print(f"\nMost commonly matched CESM variables:")
        for cesm, count in cesm_counts.most_common(10):
            print(f"  {cesm}: {count} times")
    
    # Save detailed results
    detailed_results = []
    for r in results:
        for match in r['high_confidence_matches']:
            detailed_results.append({
                'dataset': r['dataset'],
                'token': match['token'],
                'cesm_variable': match['cesm_variable'],
                'confidence': match['confidence']
            })
    
    if detailed_results:
        df = pd.DataFrame(detailed_results)
        df.to_csv('results/token_based_matches.csv', index=False)
        print(f"\nÆ╛ Saved {len(detailed_results)} detailed matches to results/token_based_matches.csv")
    
    return results

def interactive_token_test():
    """Interactive token testing"""
    model, tokenizer, id2label = load_trained_model()
    if model is None:
        return
    
    print("\n INTERACTIVE TOKEN TESTING")
    print("Enter text to break into meaningful tokens and test each one")
    print("Type 'quit' to exit\n")
    
    while True:
        try:
            text = input("Enter text: ").strip()
            if text.lower() in ['quit', 'exit', 'q']:
                break
            
            if not text:
                continue
            
            tokens = extract_meaningful_tokens(text)
            print(f"\nExtracted {len(tokens)} tokens:")
            
            for i, token in enumerate(tokens, 1):
                predicted_cesm, confidence = predict_cesm_variable(
                    token, model, tokenizer, id2label
                )
                
                status = "" if confidence > 0.5 else "Üá∩╕Å" if confidence > 0.3 else "¥î"
                print(f"  [{i}] '{token}' åÆ {predicted_cesm} ({confidence:.3f}) {status}")
            
            print()
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main function"""
    print(" Token-based CESM Matcher")
    print("=" * 50)
    
    while True:
        print("\nChoose an option:")
        print("1. Analyze CMR datasets with token matching")
        print("2. Interactive token testing")
        print("3. Quit")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == '1':
            analyze_dataset_with_tokens()
        elif choice == '2':
            interactive_token_test()
        elif choice == '3':
            print("æï Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
