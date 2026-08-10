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

# Clear GPU memory and check device
if torch.cuda.is_available():
    try:
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
        # Test basic CUDA operation
        test_tensor = torch.tensor([1.0]).cuda()
        print(f"🔧 Cleared GPU cache and verified CUDA works")
        del test_tensor
    except Exception as e:
        print(f"⚠️  CUDA test failed: {e}")
        print("   Falling back to CPU")
        device = torch.device("cpu")
        exit()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"ÜÇ Using device: {device}")

if device.type == 'cuda':
    print(f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB total")
    print(f"   GPU Memory Available: {torch.cuda.memory_reserved(0) / 1e9:.1f} GB reserved")

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
    """Extract comprehensive text summary from dataset entry

    Handles multiple formats:
    - NASA CMR: uses 'summary', 'abstract' fields
    - NOAA OneStop: uses 'description', 'keywords' fields
    - CMIP6: uses enriched variable and experiment descriptions
    - ERA5: uses comprehensive reanalysis descriptions
    """
    summary_parts = []

    # Dataset information
    dataset = cmr_entry.get('Dataset', {})
    if dataset.get('title'):
        summary_parts.append(dataset['title'])

    # NASA CMR format
    if dataset.get('summary'):
        summary_parts.append(dataset['summary'])
    if dataset.get('abstract'):
        summary_parts.append(dataset['abstract'])

    # NOAA OneStop format
    if dataset.get('description'):
        summary_parts.append(dataset['description'])

    # NOAA keywords (list of strings)
    if dataset.get('keywords'):
        keywords = dataset['keywords']
        if isinstance(keywords, list):
            # Join keywords as comma-separated text
            keywords_text = ', '.join(str(k) for k in keywords if k)
            if keywords_text:
                summary_parts.append(keywords_text)

    # DataCategory information
    data_category = cmr_entry.get('DataCategory', {})

    # NASA CMR format: DataCategory has 'summary'
    if data_category.get('summary'):
        summary_parts.append(data_category['summary'])

    # NOAA OneStop format: DataCategory has 'name' and 'description'
    if data_category.get('name'):
        summary_parts.append(data_category['name'])
    if data_category.get('description'):
        summary_parts.append(data_category['description'])

    # Variables information (same structure for both NASA and NOAA)
    variables = cmr_entry.get('Variable', [])
    for var in variables:
        for field in ['name', 'long_name', 'description', 'standard_name']:
            if var.get(field):
                summary_parts.append(var[field])

    # Additional metadata (same structure for both NASA and NOAA)
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

    # Handle CMIP6 simulation data
    data_source = cmr_entry.get('data_source', '')
    if data_source == 'CMIP6':
        # CMIP6 datasets have enriched variable and experiment descriptions
        if dataset.get('data_type') == 'CMIP6_SIMULATION':
            # Add CMIP6-specific context for better CESM variable matching
            summary_parts.append("Climate model simulation from CMIP6 (Coupled Model Intercomparison Project Phase 6)")
            summary_parts.append("Earth system model output data for climate research and analysis")

            # Variables already have enriched descriptions from controlled vocabularies
            variables = cmr_entry.get('Variable', [])
            for var in variables:
                if var.get('variable_type') == 'CMIP6_VARIABLE':
                    # These descriptions are already enriched with long_name, units, standard_name
                    if var.get('description'):
                        summary_parts.append(f"Variable data: {var['description']}")
                    if var.get('realm'):
                        summary_parts.append(f"Model realm: {var['realm']}")
                    if var.get('cell_methods'):
                        summary_parts.append(f"Cell methods: {var['cell_methods']}")

    # Handle ERA5 reanalysis data
    elif data_source == 'ERA5':
        # ERA5 datasets have comprehensive reanalysis descriptions
        if dataset.get('data_type') == 'ERA5_REANALYSIS':
            # Add ERA5-specific context for better CESM variable matching
            summary_parts.append("Atmospheric reanalysis data from ERA5 (ECMWF Reanalysis v5)")
            summary_parts.append("Comprehensive atmospheric and surface variable data for climate analysis")

            # Variables have detailed descriptions from ERA5 metadata
            variables = cmr_entry.get('Variable', [])
            for var in variables:
                if var.get('variable_type') == 'ERA5_VARIABLE':
                    if var.get('description'):
                        summary_parts.append(f"Reanalysis variable: {var['description']}")
                    if var.get('units'):
                        summary_parts.append(f"Units: {var['units']}")

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

def convert_cmip6_to_common_format(cmip6_record, dataset_key=None):
    """Convert CMIP6 record to common dataset format for prediction

    Args:
        cmip6_record: CMIP6 dataset record
        dataset_key: Dictionary key (e.g., 'CMIP6.AER.LBLRTM-12-8.RFMIP.rad-irf.r1i1p1f1.gn.v20190514')
    """
    # Load controlled vocabularies for enriched descriptions
    script_parent_dir = os.path.dirname(script_dir)
    cmip6_vocabularies = {}

    # Load variable descriptions
    try:
        variable_vocab_path = os.path.join(script_parent_dir, 'CMIP6Data/CMIP6Meta/CMIP6_variable_id.json')
        with open(variable_vocab_path, 'r') as f:
            cmip6_vocabularies['variable_id'] = json.load(f)
    except:
        cmip6_vocabularies['variable_id'] = {}

    # Load experiment descriptions
    try:
        experiment_vocab_path = os.path.join(script_parent_dir, 'CMIP6Data/CMIP6Meta/CMIP6_experiment_id.json')
        with open(experiment_vocab_path, 'r') as f:
            cmip6_vocabularies['experiment_id'] = json.load(f)
    except:
        cmip6_vocabularies['experiment_id'] = {}

    # Build enriched variable description
    variable_id = cmip6_record.get('variable_id', '')
    variable_info = cmip6_vocabularies['variable_id'].get(variable_id, {})

    variable_description_parts = []
    if variable_info.get('long_name'):
        variable_description_parts.append(variable_info['long_name'])
    if variable_info.get('units'):
        variable_description_parts.append(f"Units: {variable_info['units']}")
    if variable_info.get('standard_name'):
        variable_description_parts.append(f"Standard name: {variable_info['standard_name']}")

    variable_description = " | ".join(variable_description_parts) if variable_description_parts else variable_id

    # Build enriched experiment description
    experiment_id = cmip6_record.get('experiment_id', '')
    experiment_info = cmip6_vocabularies['experiment_id'].get(experiment_id, {})
    experiment_description = experiment_info.get('description', experiment_id)

    # Create dataset record in common format
    # Use dataset_key as the unique ID to match what json_to_csvs.py uses
    dataset = {
        'title': f"CMIP6 {cmip6_record.get('source_id', '')} {experiment_id} {variable_id}",
        'id': f"cmip6_{dataset_key}" if dataset_key else f"cmip6_{cmip6_record.get('instance_id', '')}",
        'description': f"CMIP6 climate model simulation data from {cmip6_record.get('source_id', '')} model. Variable: {variable_description}. Experiment: {experiment_description}. Frequency: {cmip6_record.get('frequency', '')}. Grid: {cmip6_record.get('grid_label', '')}.",
        'summary': f"Climate simulation data for {variable_description} from the {experiment_description} using {cmip6_record.get('source_id', '')} model at {cmip6_record.get('frequency', '')} frequency.",
        'keywords': [
            'CMIP6', 'climate simulation', 'model data',
            cmip6_record.get('activity_id', ''),
            cmip6_record.get('source_id', ''),
            cmip6_record.get('experiment_id', ''),
            cmip6_record.get('variable_id', ''),
            cmip6_record.get('frequency', ''),
            cmip6_record.get('realm', ''),
            'earth system model',
            variable_info.get('realm', ''),
            variable_info.get('cell_methods', '')
        ],
        'data_type': 'CMIP6_SIMULATION'
    }

    # Create variable record
    variable = {
        'name': variable_id,
        'long_name': variable_info.get('long_name', variable_id),
        'description': variable_description,
        'standard_name': variable_info.get('standard_name', ''),
        'units': variable_info.get('units', ''),
        'realm': variable_info.get('realm', ''),
        'cell_methods': variable_info.get('cell_methods', ''),
        'variable_type': 'CMIP6_VARIABLE'
    }

    # Create data category
    data_category = {
        'name': f"CMIP6 {cmip6_record.get('activity_id', '')}",
        'description': f"CMIP6 {cmip6_record.get('activity_id', '')} activity data from {cmip6_record.get('institution_id', '')} institution"
    }

    return {
        'Dataset': dataset,
        'Variable': [variable],
        'DataCategory': data_category,
        'Platform': [{'short_name': cmip6_record.get('source_id', '')}],
        'Instrument': [],
        'RelatedUrl': [],
        'data_source': 'CMIP6'
    }

def convert_era5_to_common_format(era5_data, dataset_key=None):
    """Convert ERA5 record to common dataset format for prediction

    Args:
        era5_data: ERA5 dataset record
        dataset_key: Filename/key identifier (e.g., 'era5_precipitation')
    """
    dataset_id = era5_data.get('id', '')
    title = era5_data.get('title', dataset_id)

    # Extract comprehensive description from webpages data
    description_parts = []

    # Add basic info
    description_parts.append(f"ERA5 reanalysis data: {title}")

    # Extract from webpages content
    webpages = era5_data.get('webpages', {})
    sections = webpages.get('body', {}).get('main', {}).get('sections', [])

    for section in sections:
        if section.get('id') == 'overview':
            blocks = section.get('blocks', [])
            for block in blocks:
                if block.get('id') == 'data_description':
                    content = block.get('content', [])
                    if content and isinstance(content, list):
                        desc_data = content[0]
                        for key, value in desc_data.items():
                            if value and isinstance(value, str):
                                description_parts.append(f"{key.replace('_', ' ').title()}: {value}")

    # Extract variables
    variables = []
    for section in sections:
        if section.get('id') == 'overview':
            blocks = section.get('blocks', [])
            for block in blocks:
                if block.get('id') == 'main_variables-accordion':
                    inner_blocks = block.get('blocks', [])
                    for inner_block in inner_blocks:
                        if inner_block.get('id') == 'main_variables':
                            content = inner_block.get('content', [])

                            # Handle table format
                            if isinstance(content, list):
                                for var in content:
                                    if isinstance(var, dict) and var.get('name'):
                                        variables.append({
                                            'name': var.get('name', ''),
                                            'long_name': var.get('description', ''),
                                            'description': var.get('description', ''),
                                            'units': var.get('units', ''),
                                            'variable_type': 'ERA5_VARIABLE'
                                        })

                            # Handle labels format
                            elif isinstance(content, dict):
                                labels = content.get('labels', {})
                                for var_key, var_name in labels.items():
                                    if var_name:
                                        variables.append({
                                            'name': var_name,
                                            'long_name': var_name,
                                            'description': f"ERA5 {var_name} variable",
                                            'units': '',
                                            'variable_type': 'ERA5_VARIABLE'
                                        })

    # Create dataset record
    # Use id field if present (matches json_to_csvs.py), otherwise fall back to dataset_key (filename)
    stable_id = f"era5_{dataset_id}" if dataset_id else f"era5_{dataset_key}" if dataset_key else "era5_unknown"
    dataset = {
        'title': title,
        'id': stable_id,
        'description': " | ".join(description_parts),
        'summary': f"ERA5 atmospheric reanalysis data providing comprehensive information about {', '.join([v['name'] for v in variables[:5]])}",
        'keywords': era5_data.get('keywords', []) + ['ERA5', 'reanalysis', 'atmospheric data', 'ECMWF'],
        'data_type': 'ERA5_REANALYSIS'
    }

    # Create data category
    data_category = {
        'name': 'ERA5 Reanalysis',
        'description': 'European Centre for Medium-Range Weather Forecasts (ECMWF) fifth generation atmospheric reanalysis data'
    }

    return {
        'Dataset': dataset,
        'Variable': variables,
        'DataCategory': data_category,
        'Platform': [{'short_name': 'ERA5'}],
        'Instrument': [],
        'RelatedUrl': [],
        'data_source': 'ERA5'
    }

def load_and_combine_datasets():
    """Load and combine NASA CMR, NOAA, CMIP6, and ERA5 datasets"""
    all_datasets = []

    # Load NASA CMR data
    print("📖 Loading NASA CMR data...")
    try:
        nasa_data_path = os.path.join(os.path.dirname(script_dir), 'NasaCMRData/json_files/individual_cmr_data.json')
        print(f"   Loading NASA JSON file from {nasa_data_path}...")
        with open(nasa_data_path, 'r', encoding='utf-8') as f:
            nasa_raw_data = json.load(f)
        print(f"✓ Loaded {len(nasa_raw_data)} NASA CMR datasets")

        # NASA format is already a list of records
        all_datasets.extend(nasa_raw_data)

    except FileNotFoundError:
        print(f"⚠️  Could not find NASA data at {nasa_data_path}")

    # Load NOAA data
    print("📖 Loading NOAA OneStop data...")
    try:
        noaa_data_path = os.path.join(os.path.dirname(script_dir), 'NasaCMRData/noaa_json/noaa_nasa_enhanced_multi_query.json')
        print(f"   Loading NOAA JSON file from {noaa_data_path}...")
        with open(noaa_data_path, 'r', encoding='utf-8') as f:
            noaa_raw_data = json.load(f)

        # NOAA format: {Dataset: [...], RelatedUrl: [...], Variable: [...], ...}
        # Need to reconstruct into list of records like NASA format
        if isinstance(noaa_raw_data, dict):
            datasets = noaa_raw_data.get('Dataset', [])
            related_urls = noaa_raw_data.get('RelatedUrl', [])
            variables = noaa_raw_data.get('Variable', [])
            data_categories = noaa_raw_data.get('DataCategory', [])
            platforms = noaa_raw_data.get('Platform', [])
            instruments = noaa_raw_data.get('Instrument', [])

            print(f"✓ Loaded {len(datasets)} NOAA datasets")
            print(f"   - {len(related_urls)} RelatedUrls")
            print(f"   - {len(variables)} Variables")
            print(f"   - {len(data_categories)} DataCategories")

            # Build lookup dictionaries for efficient matching
            dataset_to_urls = {}
            dataset_to_vars = {}
            dataset_to_datacats = {}
            dataset_to_platforms = {}
            dataset_to_instruments = {}

            for url in related_urls:
                dataset_id = url.get('dataset_id', url.get('entry_id'))
                if dataset_id:
                    if dataset_id not in dataset_to_urls:
                        dataset_to_urls[dataset_id] = []
                    dataset_to_urls[dataset_id].append(url)

            for var in variables:
                dataset_id = var.get('dataset_id', var.get('entry_id'))
                if dataset_id:
                    if dataset_id not in dataset_to_vars:
                        dataset_to_vars[dataset_id] = []
                    dataset_to_vars[dataset_id].append(var)

            for dc in data_categories:
                dataset_id = dc.get('dataset_id', dc.get('entry_id'))
                if dataset_id:
                    if dataset_id not in dataset_to_datacats:
                        dataset_to_datacats[dataset_id] = []
                    dataset_to_datacats[dataset_id].append(dc)

            for platform in platforms:
                dataset_id = platform.get('dataset_id', platform.get('entry_id'))
                if dataset_id:
                    if dataset_id not in dataset_to_platforms:
                        dataset_to_platforms[dataset_id] = []
                    dataset_to_platforms[dataset_id].append(platform)

            for instrument in instruments:
                dataset_id = instrument.get('dataset_id', instrument.get('entry_id'))
                if dataset_id:
                    if dataset_id not in dataset_to_instruments:
                        dataset_to_instruments[dataset_id] = []
                    dataset_to_instruments[dataset_id].append(instrument)

            # Reconstruct NOAA datasets into NASA-like format
            for dataset in datasets:
                dataset_id = dataset.get('dataset_id', dataset.get('entry_id'))

                # Create record with Dataset and associated entities
                record = {
                    'Dataset': dataset,
                    'RelatedUrl': dataset_to_urls.get(dataset_id, []),
                    'Variable': dataset_to_vars.get(dataset_id, []),
                    'DataCategory': dataset_to_datacats.get(dataset_id, [{}])[0] if dataset_to_datacats.get(dataset_id) else {},
                    'Platform': dataset_to_platforms.get(dataset_id, []),
                    'Instrument': dataset_to_instruments.get(dataset_id, [])
                }
                all_datasets.append(record)

    except FileNotFoundError:
        print(f"⚠️  Could not find NOAA data at {noaa_data_path}")
    except Exception as e:
        print(f"⚠️  Error loading NOAA data: {e}")

    # Load CMIP6 data
    print("🌡️ Loading CMIP6 simulation data...")
    try:
        cmip6_data_path = os.path.join(os.path.dirname(script_dir), 'CMIP6Data/CMIP6Meta/220514_CMIP6_metaData_restartedInd-24949000.json')
        print(f"   Loading CMIP6 JSON file from {cmip6_data_path}...")

        import ijson
        cmip6_count = 0
        max_cmip6_records = 5000  # Limit for performance

        with open(cmip6_data_path, 'rb') as f:
            # Use kvitems to get both dictionary keys and values
            # This preserves the dataset ID from the dictionary key (e.g., 'CMIP6.AER.LBLRTM-12-8.RFMIP.rad-irf.r1i1p1f1.gn.v20190514')
            for dataset_key, dataset_value in ijson.kvitems(f, ''):
                # Pass the dictionary key to the converter for stable ID generation
                cmip6_record = convert_cmip6_to_common_format(dataset_value, dataset_key=dataset_key)
                all_datasets.append(cmip6_record)
                cmip6_count += 1

                if cmip6_count >= max_cmip6_records:
                    break

        print(f"✓ Loaded {cmip6_count} CMIP6 simulation datasets")

    except FileNotFoundError:
        print(f"⚠️  Could not find CMIP6 data at {cmip6_data_path}")
    except Exception as e:
        print(f"⚠️  Error loading CMIP6 data: {e}")

    # Load ERA5 data
    print("🌍 Loading ERA5 reanalysis data...")
    try:
        era5_dir = os.path.join(os.path.dirname(script_dir), 'ERA5Data/ERA5Meta')
        era5_files = [f for f in os.listdir(era5_dir) if f.endswith('.json')]
        era5_count = 0

        for json_file in era5_files:
            filepath = os.path.join(era5_dir, json_file)
            with open(filepath, 'r', encoding='utf-8') as f:
                era5_data = json.load(f)

            # Use filename (without extension) as dataset key for stable ID
            dataset_key = os.path.splitext(json_file)[0]

            # Convert ERA5 record to common format
            era5_record = convert_era5_to_common_format(era5_data, dataset_key=dataset_key)
            all_datasets.append(era5_record)
            era5_count += 1

        print(f"✓ Loaded {era5_count} ERA5 reanalysis datasets")

    except FileNotFoundError:
        print(f"⚠️  Could not find ERA5 data directory")
    except Exception as e:
        print(f"⚠️  Error loading ERA5 data: {e}")

    print(f"✓ Combined total: {len(all_datasets)} datasets (NASA + NOAA + CMIP6 + ERA5)")
    return all_datasets

def predict_cmr_datasets(confidence_threshold=0.3):
    """Predict CESM variables for NASA CMR, NOAA, CMIP6, and ERA5 datasets"""
    # Load model
    model, tokenizer, id2label = load_trained_model()
    if model is None:
        return

    # Load and combine all dataset types
    print("📚 Loading NASA CMR, NOAA OneStop, CMIP6, and ERA5 data...")
    raw_cmr_data = load_and_combine_datasets()

    if not raw_cmr_data:
        print("❌ No data loaded from any sources (NASA, NOAA, CMIP6, ERA5)")
        return

    # Deduplicate datasets
    cmr_data = deduplicate_datasets(raw_cmr_data)

    print(f" Using confidence threshold: {confidence_threshold}")
    print(f"ì Processing {len(cmr_data)} datasets...")
    
    results = []
    reliable_predictions = 0
    total_predictions = 0
    
    for i, cmr_entry in enumerate(cmr_data):
        # Extract dataset information
        dataset_title = cmr_entry.get('Dataset', {}).get('title', f'Dataset_{i+1}')
        # Use short_name as primary ID (stable across deduplication), fall back to id, then index
        dataset_id = cmr_entry.get('Dataset', {}).get('short_name') or cmr_entry.get('Dataset', {}).get('id') or f'ID_{i+1}'
        data_source = cmr_entry.get('data_source', '')  # Check if this is simulation data
        
        # Create comprehensive summary
        full_summary = extract_dataset_summary(cmr_entry)
        
        if not full_summary.strip():
            print(f"[{i+1:4d}] Üá∩╕Å  Skipping dataset with no summary: {dataset_title[:50]}...")
            continue
        
        try:
            # For simulation data (CMIP6/ERA5), use the full description directly
            # For observational data (NASA/NOAA), use token-based approach
            all_predictions = []

            if data_source in ['CMIP6', 'ERA5']:
                # Simulation data: use entire comprehensive description
                try:
                    predicted_cesm, confidence = predict_cesm_variable(
                        full_summary, model, tokenizer, id2label
                    )

                    all_predictions.append({
                        'variable': predicted_cesm,
                        'confidence': confidence,
                        'token': 'full_description'
                    })

                except Exception as e:
                    print(f"[{i+1:4d}] ¥î Error predicting for simulation data: {e}")
                    continue

            else:
                # Observational data: use token-based approach
                meaningful_tokens = extract_meaningful_tokens(full_summary)

                if not meaningful_tokens:
                    print(f"[{i+1:4d}] Üá∩╕Å  No meaningful tokens after extraction: {dataset_title[:50]}...")
                    continue

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

                # For simulation data (CMIP6/ERA5), always use the highest confidence prediction
                # For observational data (NASA/NOAA), use confidence threshold
                if data_source in ['CMIP6', 'ERA5']:
                    # Simulation data: always take the most likely CESM variable
                    aggregated_confidence = individual_best
                    use_individual = True
                    meets_threshold_requirement = True
                else:
                    # Observational data: use threshold-based selection
                    if individual_best >= confidence_threshold:
                        aggregated_confidence = individual_best
                        use_individual = True
                        meets_threshold_requirement = True
                    else:
                        # Otherwise, try group aggregation with top 2 confidences
                        top_2_sum = sum(p['confidence'] for p in predictions[:2])
                        aggregated_confidence = top_2_sum
                        use_individual = False
                        meets_threshold_requirement = aggregated_confidence >= confidence_threshold

                # Only consider groups that meet the requirements
                if meets_threshold_requirement:
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
            
            # If no groups meet the requirements, skip this dataset
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

                # For simulation data, always meets threshold. For observational data, check threshold
                if data_source in ['CMIP6', 'ERA5']:
                    meets_threshold = True  # Simulation data always accepted
                else:
                    meets_threshold = best_total_confidence >= confidence_threshold

                if meets_threshold:
                    reliable_predictions += 1
                
                # Clean text fields to avoid CSV parsing issues
                def clean_text(text):
                    if not isinstance(text, str):
                        return str(text)
                    # Remove/replace problematic characters
                    return text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').strip()

                result = {
                    'dataset_id': dataset_id,
                    'dataset_title': clean_text(dataset_title),
                    'predicted_cesm_variable': best_prediction,
                    'individual_confidence': best_individual_confidence,
                    'aggregated_confidence': best_total_confidence,
                    'quality_rating': quality,
                    'meets_threshold': meets_threshold,
                    'data_source': data_source,  # Track whether this is simulation or observational data
                    'best_matching_tokens': str(best_tokens[:2]),  # Convert list to string
                    'group_type': best_group,
                    'group_members': str(best_group_members),  # Convert list to string
                    'used_individual_confidence': used_individual,
                    'total_tokens_processed': 1 if data_source in ['CMIP6', 'ERA5'] else len(meaningful_tokens) if 'meaningful_tokens' in locals() else 0,
                    'input_summary': clean_text(full_summary[:500] + "..." if len(full_summary) > 500 else full_summary),
                    'full_summary_length': len(full_summary)
                }
                results.append(result)
            
            # Print progress
            if (i + 1) % 50 == 0 or (i + 1) <= 10:
                source_tag = f"[{data_source}]" if data_source in ['CMIP6', 'ERA5'] else "[OBS]"
                print(f"[{i+1:4d}] {source_tag} è {dataset_title[:40]}... ({len(group_candidates)} predictions)")
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
                
                tokens_processed = 1 if data_source in ['CMIP6', 'ERA5'] else len(meaningful_tokens) if 'meaningful_tokens' in locals() else 0
                print(f"       Processed {tokens_processed} total {'description' if data_source in ['CMIP6', 'ERA5'] else 'tokens'}")
        
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
    # Use proper CSV parameters to handle special characters and quotes
    deduplicated_df.to_csv(output_path, index=False, quoting=1, escapechar='\\', doublequote=True)
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

    # Show breakdown by data source
    source_counts = {}
    source_reliable = {}
    for r in results:
        source = r.get('data_source', 'Unknown')
        source_counts[source] = source_counts.get(source, 0) + 1
        if r['meets_threshold']:
            source_reliable[source] = source_reliable.get(source, 0) + 1

    print(f"\nBreakdown by data source:")
    for source in ['CMIP6', 'ERA5', '', 'Unknown']:  # '' for NASA/NOAA observational data
        if source in source_counts:
            source_label = source if source else 'NASA/NOAA (Observational)'
            reliable_count = source_reliable.get(source, 0)
            total_count = source_counts[source]
            print(f"  {source_label}: {reliable_count}/{total_count} ({reliable_count/total_count*100:.1f}% reliable)")
    
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
    print("🌍  NASA CMR + NOAA + CMIP6 + ERA5 Dataset → CESM Variable Predictor")
    print("=" * 70)
    print("📊  Prediction Strategy:")
    print("   • CMIP6/ERA5 (Simulation): Use full description → highest confidence CESM variable")
    print("   • NASA/NOAA (Observational): Use token extraction → 0.3 confidence threshold")
    print()

    # Run predictions with 0.3 confidence threshold for observational data
    # Simulation data (CMIP6/ERA5) will always use the highest confidence prediction
    results = predict_cmr_datasets(confidence_threshold=0.3)
    
    if results:
        reliable_count = sum(1 for r in results if r['meets_threshold'])
        print(f"\n SUMMARY:")
        print(f"Processed {len(results)} datasets")
        print(f"Found {reliable_count} reliable CESM variable matches")
        print(f"Success rate: {reliable_count/len(results)*100:.1f}%")

if __name__ == "__main__":
    main()
