import pandas as pd
import numpy as np
import torch
from transformers import BartForConditionalGeneration, BartTokenizer
import csv
from tqdm import tqdm
import re

def paraphrase_with_bart(text, model, tokenizer, device, num_paraphrases=5):
    """
    Generate paraphrases using BART model
    """
    paraphrases = []
    
    # Clean and prepare the input text
    text = text.strip()
    if not text:
        return [text] * num_paraphrases
    
    # Generate paraphrases with different parameters for diversity
    for i in range(num_paraphrases):
        try:
            # Tokenize input
            batch = tokenizer(text, return_tensors='pt', max_length=512, truncation=True)
            batch = {k: v.to(device) for k, v in batch.items()}
            
            # Use different parameters for each paraphrase to increase diversity
            temperature = 0.7 + (i * 0.1)  # Vary temperature
            top_k = 40 + (i * 10)  # Vary top_k
            
            with torch.no_grad():
                generated_ids = model.generate(
                    batch['input_ids'],
                    attention_mask=batch['attention_mask'],
                    max_length=256,
                    num_return_sequences=1,
                    temperature=temperature,
                    top_k=min(top_k, 100),
                    top_p=0.9,
                    do_sample=True,
                    early_stopping=True,
                    pad_token_id=tokenizer.pad_token_id
                )
            
            paraphrase = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            # Clean up the paraphrase
            paraphrase = paraphrase.strip()
            if paraphrase and paraphrase != text and len(paraphrase) > 5:
                paraphrases.append(paraphrase)
            else:
                # If paraphrase is same or empty, create a simple variation
                paraphrases.append(create_simple_variation(text, i))
                
        except Exception as e:
            print(f"Error generating paraphrase {i+1} for '{text[:50]}...': {e}")
            paraphrases.append(create_simple_variation(text, i))
    
    return paraphrases

def create_simple_variation(text, variation_num):
    """
    Create simple variations when T5 fails to paraphrase
    """
    variations = [
        f"This represents {text.lower()}",
        f"Variable describing {text.lower()}",
        f"Parameter for {text.lower()}",
        f"Measurement of {text.lower()}",
        f"Data indicating {text.lower()}"
    ]
    
    if variation_num < len(variations):
        return variations[variation_num]
    else:
        return f"Climate variable: {text.lower()}"

def process_cesm_data():
    """
    Main function to process CESM data and create training set
    """
    print("Loading CESM variables data...")
    
    # Read the CSV file
    df = pd.read_csv('../NasaCMRData/cesm_variables/cesm_variables_raw.csv')
    
    print(f"Loaded {len(df)} variables")
    print("Columns:", df.columns.tolist())
    
    # Check if required columns exist
    if 'description' not in df.columns or 'cesm_name' not in df.columns:
        print("Error: Required columns 'description' or 'cesm_name' not found")
        return
    
    # Initialize BART model for paraphrasing
    print("Loading BART model for paraphrasing...")
    model_name = "eugenesiow/bart-paraphrase"
    tokenizer = BartTokenizer.from_pretrained(model_name)
    model = BartForConditionalGeneration.from_pretrained(model_name)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    print(f"Using device: {device}")
    
    # Prepare training data
    training_data = []
    
    print("Generating paraphrases...")
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing variables"):
        description = str(row['description'])
        cesm_name = str(row['cesm_name'])
        
        # Skip if description is empty or nan
        if pd.isna(description) or description.strip() == '' or description.lower() == 'nan':
            continue
        
        # Add original description
        training_data.append({
            'x': description,
            'y': cesm_name
        })
        
        # Generate 5 paraphrases
        try:
            paraphrases = paraphrase_with_bart(description, model, tokenizer, device, num_paraphrases=5)
            
            for paraphrase in paraphrases:
                training_data.append({
                    'x': paraphrase,
                    'y': cesm_name
                })
        except Exception as e:
            print(f"Error paraphrasing '{description}': {e}")
            # Add simple variations as fallback
            for i in range(5):
                simple_var = create_simple_variation(description, i)
                training_data.append({
                    'x': simple_var,
                    'y': cesm_name
                })
    
    # Create DataFrame and save
    training_df = pd.DataFrame(training_data)
    
    print(f"Generated {len(training_df)} training samples from {len(df)} original variables")
    
    # Save to CSV
    output_file = 'TrainingSet/cesm_training_set.csv'
    training_df.to_csv(output_file, index=False)
    
    print(f"Training set saved to {output_file}")
    
    # Print sample data
    print("\nSample training data:")
    print(training_df.head(10))
    
    # Print statistics
    print(f"\nStatistics:")
    print(f"Total training samples: {len(training_df)}")
    print(f"Unique CESM variables: {training_df['y'].nunique()}")
    print(f"Average samples per variable: {len(training_df) / training_df['y'].nunique():.1f}")

def create_simple_training_set():
    """
    Alternative simpler approach using basic text variations
    """
    print("Creating simple training set with basic variations...")
    
    # Read the CSV file
    df = pd.read_csv('../NasaCMRData/cesm_variables/cesm_variables_raw.csv')
    
    training_data = []
    
    for _, row in df.iterrows():
        description = str(row['description'])
        cesm_name = str(row['cesm_name'])
        
        if pd.isna(description) or description.strip() == '' or description.lower() == 'nan':
            continue
        
        # Original description
        training_data.append({'x': description, 'y': cesm_name})
        
        # Create 5 variations
        variations = [
            f"This variable represents {description.lower()}",
            f"Climate parameter: {description}",
            f"Atmospheric measurement of {description.lower()}",
            f"Variable describing {description.lower()}",
            f"Data for {description.lower()}"
        ]
        
        for var in variations:
            training_data.append({'x': var, 'y': cesm_name})
    
    # Save training set
    training_df = pd.DataFrame(training_data)
    output_file = 'TrainingSet/cesm_training_set_simple.csv'
    training_df.to_csv(output_file, index=False)
    
    print(f"Simple training set saved to {output_file}")
    print(f"Generated {len(training_df)} training samples")

if __name__ == "__main__":
    # Create TrainingSet directory if it doesn't exist
    import os
    if not os.path.exists('TrainingSet'):
        os.makedirs('TrainingSet')
    
    print("Choose processing method:")
    print("1. Advanced paraphrasing with T5 model (requires transformers library)")
    print("2. Simple text variations")
    
    try:
        # Try advanced method first
        process_cesm_data()
    except ImportError as e:
        print(f"Error importing required libraries: {e}")
        print("Falling back to simple method...")
        create_simple_training_set()
    except Exception as e:
        print(f"Error with advanced method: {e}")
        print("Falling back to simple method...")
        create_simple_training_set()
