#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JSON to OpenCypher CSV Converter

This script converts JSON data from NASA's CMR (Common Metadata Repository)
to CSV files in the OpenCypher format required by Amazon Neptune Bulk Loader.
Includes CESM variable to dataset mapping using pre-computed ML predictions.
"""

import os
import json
import csv
import argparse
from pathlib import Path
import logging
import uuid
import boto3
import re
import pandas as pd
import sys
import numpy as np
from collections import defaultdict
from difflib import SequenceMatcher

def clean_csv_text(text):
    """
    Clean text by removing ALL punctuation to prevent CSV parsing issues
    """
    if text is None:
        return ""
    
    text = str(text)
    
    # Remove ALL punctuation, keep only alphanumeric and spaces
    text = re.sub(r'[^\w\s]', '', text)
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text

# For embedding generation - using same model as machine_learning.py
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available. Install with: pip install sentence-transformers")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress transformers and sentence-transformers verbose logging
logging.getLogger("transformers").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

# Early warning about missing sentence-transformers
if not SENTENCE_TRANSFORMERS_AVAILABLE:
    logger.warning("Üá∩╕Å sentence-transformers not available. Install with: pip install sentence-transformers")
    logger.warning("Üá∩╕Å Text embedding generation will be disabled")

class JSONToCSVConverter:
    """Class for converting JSON data to Neptune OpenCypher CSV format."""
    
    def __init__(self, generate_embeddings=False):
        """Initialize the converter."""
        self.reset_state()
        self.generate_embeddings = generate_embeddings
        self.embedding_model = None
        self.embedding_batch_size = 100
        self.embedding_queue = []  # Store (node_id, text) tuples
        
        # Initialize embedding model if requested
        if self.generate_embeddings and SENTENCE_TRANSFORMERS_AVAILABLE:
            self._load_embedding_model()
        
        # Define all the collections/classes from NASA Knowledge Graph
        self.collections = [
            "Dataset",
            "DataCategory",
            "DataFormat",
            "CoordinateSystem",
            "Location",
            "Station",
            "Organization",
            "Platform",
            "Consortium",
            "TemporalExtent",
            "Variable",          # NASA CMR variables
            "CESMVariable",      # CESM variables
            "Component",         # CESM components
            "Contact",           # Contact information
            "Project",           # Project information
            "SpatialResolution", # Spatial resolution info
            "TemporalResolution", # Temporal resolution info
            "Instrument",        # Instrument information
            "ScienceKeyword",    # Science keywords
            "ProcessingLevel",   # Processing levels
            "Link",              # Data access links (S3, Earthdata, etc.)
            
            # Climate ML workflow nodes
            "SurrogateModelingWorkflow",        # Physics-first: neural operators as surrogates
            "HybridMLPhysicsWorkflow",          # Physics-first: hybrid ML-physics simulations  
            "EquationDiscoveryWorkflow",        # Physics-first: discovering governing equations
            "ParameterizationBenchmarkWorkflow", # Physics-first: benchmarking ML parameterizations
            "UncertaintyQuantificationWorkflow", # Data-first: simulation-based uncertainty quantification
            "ParameterInferenceWorkflow",       # Data-first: probabilistic parameter inference
            "SubseasonalForecastingWorkflow",   # ML-first: subseasonal forecasting
            "TransferLearningWorkflow"          # ML-first: transfer learning for sparse predictions
        ]
        
        # Define relationship mapping
        self.relationship_map = {
            # Dataset relationships (order-based)
            "hasDataCategory": ("Dataset", "DataCategory"),
            "hasDataFormat": ("Dataset", "DataFormat"),
            "usesCoordinateSystem": ("Dataset", "CoordinateSystem"),
            "hasLocation": ("Dataset", "Location"),
            "hasStation": ("Dataset", "Station"),
            "hasOrganization": ("Dataset", "Organization"),
            "hasPlatform": ("Dataset", "Platform"),
            "hasConsortium": ("Dataset", "Consortium"),
            "hasTemporalExtent": ("Dataset", "TemporalExtent"),
            "hasContact": ("Dataset", "Contact"),
            "hasProject": ("Dataset", "Project"),
            "hasRelatedUrl": ("Dataset", "RelatedUrl"),
            "hasSpatialResolution": ("Dataset", "SpatialResolution"),
            "hasTemporalResolution": ("Dataset", "TemporalResolution"),
            "hasGranule": ("Dataset", "Granule"),
            "hasInstrument": ("Dataset", "Instrument"),
            "hasScienceKeyword": ("Dataset", "ScienceKeyword"),
            "hasProcessingLevel": ("Dataset", "ProcessingLevel"),
            
            # Variable relationships
            "hasVariable": ("Dataset", "Variable"),           # Dataset -> NASA CMR Variable
            # "hasCESMVariable": ("Dataset", "CESMVariable"), # REMOVED: Created separately via ML predictions
            "belongsToComponent": ("CESMVariable", "Component"),  # CESM Variable -> Component
            "similarCESMVariable": ("CESMVariable", "CESMVariable"), # CESMVariable -> CESMVariable (string similarity based grouping)
            
            # Climate research workflow relationships
            "measuredByInstrument": ("Variable", "Instrument"),    # Variable -> Instrument (data provenance)
            "deployedOnPlatform": ("Instrument", "Platform"),     # Instrument -> Platform (measurement chain)
            "operatesAtLocation": ("Platform", "Location"),       # Platform -> Location (spatial context)
            "worksForOrganization": ("Contact", "Organization"),  # Contact -> Organization (data stewardship)
            "belongsToConsortium": ("Organization", "Consortium"), # Organization -> Consortium (collaboration)
            "describesVariable": ("ScienceKeyword", "CESMVariable"),  # ScienceKeyword -> CESMVariable (semantic linking)
            "producesFormat": ("Instrument", "DataFormat"),       # Instrument -> DataFormat (technical specs)
            
            # Physics-First Workflow Relationships (based on high-resolution simulation data)
            
            # SurrogateModelingWorkflow: Neural operators for PDE solving
            "SurrogateModelingWorkflow_usesDataset": ("SurrogateModelingWorkflow", "Dataset"),
            "SurrogateModelingWorkflow_requiresHighResData": ("SurrogateModelingWorkflow", "SpatialResolution"),  # High-resolution simulation data
            "SurrogateModelingWorkflow_requiresTemporalData": ("SurrogateModelingWorkflow", "TemporalResolution"), # Time-series training data
            "SurrogateModelingWorkflow_appliesTo": ("SurrogateModelingWorkflow", "Component"),  # Atmosphere, ocean, land components
            
            # HybridMLPhysicsWorkflow: CRM-based ML surrogates
            "HybridMLPhysicsWorkflow_usesDataset": ("HybridMLPhysicsWorkflow", "Dataset"),
            "HybridMLPhysicsWorkflow_requiresAtmosphericData": ("HybridMLPhysicsWorkflow", "Variable"),  # Atmospheric state variables
            "HybridMLPhysicsWorkflow_appliesTo": ("HybridMLPhysicsWorkflow", "Component"),  # Atmosphere component
            "HybridMLPhysicsWorkflow_requiresOrganization": ("HybridMLPhysicsWorkflow", "Organization"), # E3SM-MMF data
            
            # EquationDiscoveryWorkflow: Sparse equation discovery
            "EquationDiscoveryWorkflow_usesDataset": ("EquationDiscoveryWorkflow", "Dataset"),
            "EquationDiscoveryWorkflow_requiresHighResSimulations": ("EquationDiscoveryWorkflow", "SpatialResolution"),
            "EquationDiscoveryWorkflow_appliesTo": ("EquationDiscoveryWorkflow", "Component"),  # Ocean, atmosphere, land
            "EquationDiscoveryWorkflow_requiresOrganization": ("EquationDiscoveryWorkflow", "Organization"), # MITgcm simulations
            
            # ParameterizationBenchmarkWorkflow: Systematic ML parameterization testing
            "ParameterizationBenchmarkWorkflow_usesDataset": ("ParameterizationBenchmarkWorkflow", "Dataset"),
            "ParameterizationBenchmarkWorkflow_requiresSimulationData": ("ParameterizationBenchmarkWorkflow", "Variable"),
            "ParameterizationBenchmarkWorkflow_appliesTo": ("ParameterizationBenchmarkWorkflow", "Component"), # QG model testing
            
            # Data-First Workflow Relationships (based on observations)
            
            # UncertaintyQuantificationWorkflow: Satellite retrieval uncertainty
            "UncertaintyQuantificationWorkflow_usesDataset": ("UncertaintyQuantificationWorkflow", "Dataset"),
            "UncertaintyQuantificationWorkflow_requiresInstrument": ("UncertaintyQuantificationWorkflow", "Instrument"),  # EMIT satellite
            "UncertaintyQuantificationWorkflow_requiresSpectra": ("UncertaintyQuantificationWorkflow", "Variable"),  # Electromagnetic spectra
            "UncertaintyQuantificationWorkflow_requiresOrganization": ("UncertaintyQuantificationWorkflow", "Organization"), # NASA JPL
            "UncertaintyQuantificationWorkflow_appliesTo": ("UncertaintyQuantificationWorkflow", "Component"), # Atmosphere, land, ocean
            
            # ParameterInferenceWorkflow: Probabilistic parameter estimation
            "ParameterInferenceWorkflow_usesDataset": ("ParameterInferenceWorkflow", "Dataset"),
            "ParameterInferenceWorkflow_requiresInstrument": ("ParameterInferenceWorkflow", "Instrument"), # For observed distributions
            "ParameterInferenceWorkflow_requiresVariable": ("ParameterInferenceWorkflow", "Variable"), # System state variables
            "ParameterInferenceWorkflow_requiresOrganization": ("ParameterInferenceWorkflow", "Organization"), # Model parameters
            "ParameterInferenceWorkflow_appliesTo": ("ParameterInferenceWorkflow", "Component"), # Land, ocean, atmosphere
            
            # ML-First Workflow Relationships (pure ML approaches)
            
            # SubseasonalForecastingWorkflow: 2-6 week forecasting
            "SubseasonalForecastingWorkflow_usesDataset": ("SubseasonalForecastingWorkflow", "Dataset"),
            "SubseasonalForecastingWorkflow_requiresReanalysisData": ("SubseasonalForecastingWorkflow", "Variable"), # ERA5 reanalysis
            "SubseasonalForecastingWorkflow_requiresPlatform": ("SubseasonalForecastingWorkflow", "Platform"), # Global atmospheric data
            "SubseasonalForecastingWorkflow_requiresOrganization": ("SubseasonalForecastingWorkflow", "Organization"), # ECMWF ERA5
            "SubseasonalForecastingWorkflow_appliesTo": ("SubseasonalForecastingWorkflow", "Component"), # Atmosphere
            
            # TransferLearningWorkflow: Sparse observation extrapolation
            "TransferLearningWorkflow_usesDataset": ("TransferLearningWorkflow", "Dataset"),
            "TransferLearningWorkflow_requiresSparseObservations": ("TransferLearningWorkflow", "Variable"), # Limited real observations
            "TransferLearningWorkflow_requiresLocation": ("TransferLearningWorkflow", "Location"), # Cross-domain applications
            "TransferLearningWorkflow_requiresOrganization": ("TransferLearningWorkflow", "Organization"), # SOCAT data
            "TransferLearningWorkflow_appliesTo": ("TransferLearningWorkflow", "Component") # Atmosphere, land, ocean
        }
        
        # Define property types for CSV headers
        self.property_types = {
            "id": "String",
            "type": "String",
            "short_name": "String",
            "title": "String",
            "links": "String",
            "summary": "String",
            "original_format": "String",
            "data_format": "String",
            "format_source": "String",
            "category": "String",
            "boxes": "String",
            "polygons": "String",
            "points": "String",
            "place_names": "String",
            # Enhanced Dataset properties
            "data_center": "String",
            "dataset_id": "String",
            "entry_id": "String",
            "version_id": "String",
            "processing_level_id": "String",
            "online_access_flag": "Boolean",
            "browse_flag": "Boolean",
            "science_keywords": "String",
            "doi": "String",
            "doi_authority": "String",
            "collection_data_type": "String",
            "data_set_language": "String",
            "archive_center": "String",
            "native_id": "String",
            "granule_count": "Integer",
            "day_night_flag": "String",
            "cloud_cover": "String",
            # CoordinateSystem properties
            "name": "String",
            "projection_type": "String",
            "datum": "String",
            "units": "String",
            # Variable properties
            "variable_id": "String",
            "cesm_name": "String",
            "standard_name": "String",
            "long_name": "String",
            "description": "String",
            "domain": "String",
            "component": "String",
            "source_dataset": "String",
            "match_confidence": "Double",
            "match_type": "String",
            "matched_term": "String",
            "variable_type": "String",
            "source": "String",
            # Component properties
            "component_id": "String",
            "component_name": "String",
            "full_name": "String",
            "abbreviation": "String",
            # Contact properties
            "contact_id": "String",
            "contact_type": "String",
            "contact_name": "String",
            "roles": "String",
            "email": "String",
            "organization": "String",
            "phone": "String",
            # Project properties
            "project_id": "String",
            "project_name": "String",
            "project_description": "String",
            # RelatedUrl properties
            "url_id": "String",
            "url": "String",
            "type": "String",
            "subtype": "String",
            "url_description": "String",
            "url_format": "String",
            # Resolution properties
            "spatial_id": "String",
            "spatial_resolution": "String",
            "spatial_units": "String",
            "temporal_id": "String",
            "temporal_resolution": "String",
            "temporal_frequency": "String",
            # ScienceKeyword properties
            "keyword_id": "String",
            "category": "String",
            "topic": "String",
            "term": "String",
            "variable_level_1": "String",
            "variable_level_2": "String",
            "variable_level_3": "String",
            "detailed_variable": "String",
            # ProcessingLevel properties
            "processing_level_id": "String",
            "id": "String",
            "level_description": "String",
            # Other properties
            "platforms": "String",
            "start_time": "String",
            "end_time": "String",
            "updated": "String",
            # Workflow properties
            "workflow_id": "String",
            "workflow_name": "String",
            "workflow_type": "String",
            "workflow_description": "String",
            "methodology": "String",
            "primary_approach": "String",
            "key_techniques": "String",
            "data_requirements": "String",
            "computational_complexity": "String",
            "typical_timescales": "String",
            "strengths": "String",
            "limitations": "String",
            "example_applications": "String",
            "maturity_level": "String",
            "target_domain": "String",
            # Link properties
            "url": "String",
            "link_type": "String", 
            "link_rel": "String",
            "length": "String",
            "hreflang": "String",
            # Embedding property
            "embedding": "List"
        }

    def reset_state(self):
        """Reset the state of the converter."""
        self.nodes = {}
        self.relationships = []
        # Global caches for deduplication
        self.format_cache = {}
        self.location_cache = {}
        self.category_cache = {}
        self.coordinate_system_cache = {}
        self.station_cache = {}
        self.organization_cache = {}
        self.platform_cache = {}
        self.consortium_cache = {}
        self.contact_cache = {}
        self.project_cache = {}
        self.url_cache = {}
        self.spatial_cache = {}
        self.temporal_cache = {}
        self.keyword_cache = {}
        self.processing_cache = {}
        self.relationship_id_counter = 0
        
        # CESM variable to dataset mapping
        self.cesm_variable_mappings = {}
        
        # Link node creation counter
        self.link_nodes_created = 0








    def select_vars(self, scores, max_len=15):
        """
        Statistical approach to selecting variables based on scores.
        
        Intuition behind each step:
        - ╬╝é  0.5 ╧âé: Adaptive threshold based on score distribution
        - ╬s ëñ 0.07: Elbow detection for topical relevance
        - Floor 0.50: Minimum quality threshold
        - Back-off if < 6: Guards against under-selection
        - Hard ceiling 15: Prevents pathological cases
        
        Args:
            scores: List of scores in descending order
            max_len: Maximum number of variables to return
            
        Returns:
            List of indices to keep
        """
        keep = [0]  # always keep top-1 (index)
        if len(scores) < 2:
            return keep

        # Calculate adaptive threshold using scores 2-5
        mu5 = sum(scores[1:5]) / min(4, len(scores)-1)
        sigma5 = (sum((x-mu5)**2 for x in scores[1:5]) /
                min(4, len(scores)-1)) ** 0.5
        tau = max(0.50, mu5 - 0.5*sigma5)

        # Apply filtering criteria
        i = 1
        while i < len(scores) and len(keep) < max_len:
            # Stop if score is below threshold OR if there's a sharp drop (>0.07)
            if scores[i] < tau or scores[i-1] - scores[i] > 0.07:
                break
            keep.append(i)
            i += 1

        # Ensure at least 6 variables if possible (back-off mechanism)
        while len(keep) < 6 and i < len(scores) and scores[i] >= tau - 0.02:
            keep.append(i)
            i += 1

        return keep

    def load_cesm_variables(self):
        """Load CESM variables from the raw CSV file."""
        try:
            cesm_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "NasaCMRData", "cesm_variables_raw.csv")
            if os.path.exists(cesm_file_path):
                df = pd.read_csv(cesm_file_path)
                return df.to_dict('records')
            else:
                logger.warning(f"CESM variables file not found at {cesm_file_path}")
                return []
        except Exception as e:
            logger.error(f"Error loading CESM variables: {e}")
            return []

    def _load_embedding_model(self):
        """Load the sentence transformer model for embedding generation - same as machine_learning.py."""
        try:
            logger.info("Loading sentence transformer model: all-MiniLM-L6-v2 (same as machine_learning.py)")
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info(" Embedding model loaded successfully - compatible with machine_learning.py")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            self.generate_embeddings = False

    def _create_text_for_embedding(self, node_type, item):
        """Create text representation for embedding based on node type."""
        if node_type == "DataCategory":
            summary = item.get('summary', '')
            return f"Data Category: {summary}"
            
        elif node_type == "Variable":
            name = item.get('name', '')
            standard_name = item.get('standard_name', '')
            long_name = item.get('long_name', '')
            description = item.get('description', '')
            units = item.get('units', '')
            
            text_parts = []
            if name:
                text_parts.append(f"Variable name: {name}")
            if standard_name:
                text_parts.append(f"Standard name: {standard_name}")
            if long_name:
                text_parts.append(f"Long name: {long_name}")
            if description:
                text_parts.append(f"Description: {description}")
            if units:
                text_parts.append(f"Units: {units}")
            
            return " | ".join(text_parts) if text_parts else "Variable"
            
        elif node_type == "CESMVariable":
            cesm_name = item.get('cesm_name', '')
            standard_name = item.get('standard_name', '')
            long_name = item.get('long_name', '')
            description = item.get('description', '')
            units = item.get('units', '')
            domain = item.get('domain', '')
            component = item.get('component', '')
            
            text_parts = []
            if cesm_name:
                text_parts.append(f"CESM name: {cesm_name}")
            if standard_name:
                text_parts.append(f"Standard name: {standard_name}")
            if long_name:
                text_parts.append(f"Long name: {long_name}")
            if description:
                text_parts.append(f"Description: {description}")
            if units:
                text_parts.append(f"Units: {units}")
            if domain:
                text_parts.append(f"Domain: {domain}")
            if component:
                text_parts.append(f"Component: {component}")
            
            return " | ".join(text_parts) if text_parts else "CESM Variable"
            
        elif node_type == "ScienceKeyword":
            category = item.get('category', '')
            topic = item.get('topic', '')
            term = item.get('term', '')
            variable_level_1 = item.get('variable_level_1', '')
            variable_level_2 = item.get('variable_level_2', '')
            variable_level_3 = item.get('variable_level_3', '')
            detailed_variable = item.get('detailed_variable', '')
            
            text_parts = []
            if category:
                text_parts.append(f"Category: {category}")
            if topic:
                text_parts.append(f"Topic: {topic}")
            if term:
                text_parts.append(f"Term: {term}")
            if variable_level_1:
                text_parts.append(f"Variable Level 1: {variable_level_1}")
            if variable_level_2:
                text_parts.append(f"Variable Level 2: {variable_level_2}")
            if variable_level_3:
                text_parts.append(f"Variable Level 3: {variable_level_3}")
            if detailed_variable:
                text_parts.append(f"Detailed Variable: {detailed_variable}")
            
            return " | ".join(text_parts) if text_parts else "Science Keyword"
        
        elif node_type in ['Workflow', 'PhysicsFirstWorkflow', 'DataFirstWorkflow', 'MLFirstWorkflow', 'HybridWorkflow']:
            workflow_name = item.get('workflow_name', '')
            description = item.get('workflow_description', '')
            methodology = item.get('methodology', '')
            techniques = item.get('key_techniques', '')
            data_reqs = item.get('data_requirements', '')
            domain = item.get('target_domain', '')
            
            text_parts = []
            if workflow_name:
                text_parts.append(f"Workflow: {workflow_name}")
            if description:
                text_parts.append(f"Description: {description}")
            if methodology:
                text_parts.append(f"Methodology: {methodology}")
            if techniques:
                text_parts.append(f"Techniques: {techniques}")
            if data_reqs:
                text_parts.append(f"Data Requirements: {data_reqs}")
            if domain:
                text_parts.append(f"Target Domain: {domain}")
            
            return " | ".join(text_parts) if text_parts else f"{node_type} Workflow"
        
        elif node_type == "Location":
            name = item.get('name', '')
            place_names = item.get('place_names', '')
            scope = item.get('scope', '')
            countries = item.get('countries', '')
            continents = item.get('continents', '')
            boxes = item.get('boxes', '')
            
            text_parts = []
            if name:
                text_parts.append(f"Location: {name}")
            if place_names:
                text_parts.append(f"Places: {place_names}")
            if scope:
                text_parts.append(f"Scope: {scope}")
            if countries:
                text_parts.append(f"Countries: {countries}")
            if continents:
                text_parts.append(f"Continents: {continents}")
            if boxes:
                text_parts.append(f"Geographic bounds: {boxes}")
            
            return " | ".join(text_parts) if text_parts else "Geographic Location"
        
        elif node_type in ["SpatialResolution", "TemporalResolution"]:
            resolution = item.get('resolution', '')
            units = item.get('units', '') if node_type == "SpatialResolution" else item.get('frequency', '')
            
            text_parts = []
            text_parts.append(f"{node_type.replace('Resolution', ' Resolution')}: {resolution}")
            if units:
                text_parts.append(f"Units: {units}")
            
            # Add semantic descriptors for better search
            if node_type == "SpatialResolution" and resolution:
                res_str = str(resolution).lower()
                if any(term in res_str for term in ['km', 'kilometer']):
                    if any(val in res_str for val in ['0.', '1 ', '2 ', '3 ', '4 ', '5 ']):
                        text_parts.append("High spatial resolution")
                    elif any(val in res_str for val in ['10', '25', '50']):
                        text_parts.append("Medium spatial resolution")
                    else:
                        text_parts.append("Coarse spatial resolution")
                elif any(term in res_str for term in ['degree', 'deg', '°']):
                    if any(val in res_str for val in ['0.1', '0.2', '0.25', '0.5']):
                        text_parts.append("High spatial resolution")
                    else:
                        text_parts.append("Coarse spatial resolution")
            
            elif node_type == "TemporalResolution" and resolution:
                res_str = str(resolution).lower()
                if any(term in res_str for term in ['hour', 'minute', 'second']):
                    text_parts.append("High temporal resolution")
                elif any(term in res_str for term in ['daily', 'day']):
                    text_parts.append("Daily temporal resolution")
                elif any(term in res_str for term in ['monthly', 'month']):
                    text_parts.append("Monthly temporal resolution")
                elif any(term in res_str for term in ['yearly', 'annual', 'year']):
                    text_parts.append("Annual temporal resolution")
            
            return " | ".join(text_parts) if text_parts else f"{node_type}"
        
        else:
            return str(item)

    def _queue_embedding(self, node_id, text):
        """Queue text for batch embedding processing."""
        if not self.generate_embeddings or self.embedding_model is None:
            return
        
        self.embedding_queue.append((node_id, text))
        
        # Process batch when queue reaches batch size
        if len(self.embedding_queue) >= self.embedding_batch_size:
            self._process_embedding_batch()
    
    def _process_embedding_batch(self):
        """Process queued embeddings in batch."""
        if not self.embedding_queue or not self.generate_embeddings or self.embedding_model is None:
            return
        
        try:
            texts = [item[1] for item in self.embedding_queue]
            node_ids = [item[0] for item in self.embedding_queue]
            
            # Count total processed so far
            if not hasattr(self, '_total_embeddings_processed'):
                self._total_embeddings_processed = 0
            
            logger.info(f"🧠 Processing embedding batch: {len(texts)} items (total processed: {self._total_embeddings_processed})")
            
            # Generate embeddings for entire batch
            embeddings = self.embedding_model.encode(
                texts, 
                convert_to_tensor=True, 
                normalize_embeddings=True,
                batch_size=self.embedding_batch_size,
                show_progress_bar=False
            )
            
            self._total_embeddings_processed += len(texts)
            
            # Process each embedding
            for i, embedding in enumerate(embeddings):
                node_id = node_ids[i]
                
                # Convert to numpy and flatten
                embedding = embedding.cpu().numpy().flatten()
                
                # Validate: ensure no NaN or Inf values
                if np.any(np.isnan(embedding)) or np.any(np.isinf(embedding)):
                    # Replace invalid values with zeros
                    embedding = np.nan_to_num(embedding, nan=0.0, posinf=0.0, neginf=0.0)
                
                # Convert to list of FP32 floats
                embedding_list = [float(x) for x in embedding]
                
                # Store embedding in node
                if node_id in self.nodes:
                    self.nodes[node_id]['embedding'] = embedding_list
                    
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
        
        # Clear the queue
        self.embedding_queue = []
    
    def _finalize_embeddings(self):
        """Process any remaining embeddings in the queue."""
        if self.embedding_queue:
            self._process_embedding_batch()
    
    def _generate_embedding(self, text):
        """Generate embedding for a given text - deprecated, returns None for batch processing."""
        # This method is kept for compatibility but doesn't generate embeddings
        # Embeddings are now handled via batch processing
        return None

    def create_graphson_vertex(self, vertex_id, vertex_type, vertex_data):
        """Create a GraphSON-style vertex with embedding for Neptune OpenCypher analytics."""
        # Create text for embedding
        text_for_embedding = self._create_text_for_embedding(vertex_type, vertex_data)
        
        # Queue embedding for batch processing
        self._queue_embedding(vertex_id, text_for_embedding)
        
        # Create GraphSON vertex structure
        vertex = {
            "~id": vertex_id,
            "~label": vertex_type
        }
        
        # Add embedding if available
        if embedding:
            vertex["embedding"] = embedding
        
        # Add vertex properties in GraphSON format
        for key, value in vertex_data.items():
            if key != 'id' and key != 'type':  # Skip internal fields
                vertex[key] = {"~value": value}
        
        return vertex

    def process_json_file(self, json_file):
        """Process a single JSON file and extract nodes and relationships."""
        try:
            # Check if file exists (Windows-compatible)
            if not os.path.exists(json_file):
                raise FileNotFoundError(f"JSON file not found: {json_file}")
            
            # Read JSON file with error handling
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f" Successfully loaded JSON data from {json_file}")
            except json.JSONDecodeError as e:
                logger.error(f"¥î Invalid JSON format in {json_file}: {e}")
                raise
            except Exception as e:
                logger.error(f"¥î Error reading {json_file}: {e}")
                raise

            # Process each node type
            nodes_processed = 0
            for node_type in self.collections:
                if node_type in data:
                    # Handle CESMVariable separately (will be processed normally)
                    if node_type == 'CESMVariable':
                        logger.info("Processing CESMVariable nodes...")
                        try:
                            self.process_cesm_variables(data[node_type])
                            nodes_processed += len(data[node_type]) if isinstance(data[node_type], list) else 1
                        except Exception as e:
                            logger.error(f"¥î Error processing CESMVariable nodes: {e}")
                        continue
                    
                    # Handle Dataset nodes specially to extract and create Link nodes
                    elif node_type == 'Dataset':
                        logger.info("Processing Dataset nodes and extracting links...")
                        try:
                            if isinstance(data[node_type], list):
                                for i, dataset in enumerate(data[node_type]):
                                    self.process_dataset_with_links(dataset, i)
                                    nodes_processed += 1
                            nodes_processed += self.link_nodes_created
                        except Exception as e:
                            logger.error(f"¥î Error processing Dataset nodes: {e}")
                        continue
                        
                    # Handle other node types as arrays
                    if isinstance(data[node_type], list):
                        for i, item in enumerate(data[node_type]):
                            try:
                                self.process_node(node_type, item, i)
                                nodes_processed += 1
                            except Exception as e:
                                logger.error(f"¥î Error processing {node_type} node {i}: {e}")
                                continue
                    elif isinstance(data[node_type], dict):
                        # Handle dict-based node types
                        for key, item in data[node_type].items():
                            try:
                                self.process_node(node_type, item, key)
                                nodes_processed += 1
                            except Exception as e:
                                logger.error(f"¥î Error processing {node_type} node {key}: {e}")
                                continue
                else:
                    logger.debug(f"Node type '{node_type}' not found in JSON data")

            logger.info(f" Processed {nodes_processed} nodes from JSON file")

            # Create order-based relationships for datasets
            try:
                self.create_order_based_relationships(data)
                logger.info(" Successfully created order-based relationships")
            except Exception as e:
                logger.error(f"¥î Error creating order-based relationships: {e}")
            
            # Create workflow-specific relationships
            try:
                self.create_workflow_relationships(data)
                logger.info(" Successfully created workflow relationships")
            except Exception as e:
                logger.error(f"¥î Error creating workflow relationships: {e}")
            
            # Create CESM variable to dataset mappings using pre-computed predictions
            try:
                self.create_cesm_variable_mappings(data)
                logger.info(" Successfully processed CESM variable mappings")
            except Exception as e:
                logger.error(f"¥î Error creating CESM variable mappings: {e}")
            
            # Create CESM variable similarity relationships
            try:
                self.create_cesm_similarity_relationships(threshold=0.7)
                logger.info(" Successfully created CESM variable similarity relationships")
            except Exception as e:
                logger.error(f"¥î Error creating CESM similarity relationships: {e}")
            
            # Create climate ML workflow nodes
            try:
                self.create_climate_workflows()
                logger.info(" Successfully created climate ML workflow nodes")
            except Exception as e:
                logger.error(f"¥î Error creating climate workflows: {e}")

        except Exception as e:
            logger.error(f"¥î Error processing {json_file}: {str(e)}")
            raise

    def process_dataset_with_links(self, dataset, index):
        """Process a dataset and extract its links as separate Link nodes"""
        # First, extract links and create Link nodes
        links = dataset.get('links', [])
        dataset_id = self.create_node_id('Dataset', dataset, index)
        
        if links and isinstance(links, list):
            for link_idx, link in enumerate(links):
                if isinstance(link, dict) and 'href' in link:
                    # Create Link node
                    link_id = f"link_{dataset_id}_{link_idx}"
                    
                    # Determine link type
                    href = link.get('href', '')
                    if href.startswith('s3://'):
                        link_type = 'S3'
                    elif 'earthdata.nasa.gov' in href.lower():
                        link_type = 'Earthdata'  
                    elif href.startswith('https://doi.org/'):
                        link_type = 'DOI'
                    elif href.startswith('http'):
                        link_type = 'HTTP'
                    else:
                        link_type = 'Other'
                    
                    # Create the Link node
                    link_node = {
                        'id': link_id,
                        'type': 'Link',
                        'url': href,
                        'link_type': link_type,
                        'link_rel': link.get('rel', ''),
                        'length': link.get('length', ''),
                        'hreflang': link.get('hreflang', '')
                    }
                    
                    self.nodes[link_id] = link_node
                    self.link_nodes_created += 1
                    
                    # Create relationship: Dataset -> hasLink -> Link
                    relationship = {
                        'id': f"rel_{dataset_id}_hasLink_{link_id}",
                        'type': 'hasLink',
                        'from': dataset_id,
                        'to': link_id,
                        'from_type': 'Dataset',
                        'to_type': 'Link'
                    }
                    self.relationships.append(relationship)
        
        # Process the dataset normally (but remove links property first to avoid duplication)
        dataset_copy = dataset.copy()
        if 'links' in dataset_copy:
            del dataset_copy['links']
        
        self.process_node('Dataset', dataset_copy, index)

    def process_node(self, node_type, item, index):
        """Process a single node."""
        # Create node ID based on type
        node_id = self.create_node_id(node_type, item, index)
        
        # Add node properties
        properties = {
            'id': node_id,
            'type': node_type
        }
        
        # Add type-specific properties
        if node_type == 'Dataset':
            properties.update({
                'short_name': item.get('short_name', ''),
                'title': item.get('title', ''),
                'links': str(item.get('links', [])),
                'data_center': item.get('data_center', ''),
                'dataset_id': item.get('dataset_id', ''),
                'entry_id': item.get('entry_id', ''),
                'version_id': item.get('version_id', ''),
                'processing_level_id': item.get('processing_level_id', ''),
                'online_access_flag': item.get('online_access_flag', False),
                'browse_flag': item.get('browse_flag', False),
                'science_keywords': str(item.get('science_keywords', [])),
                'doi': item.get('doi', ''),
                'doi_authority': item.get('doi_authority', ''),
                'collection_data_type': item.get('collection_data_type', ''),
                'data_set_language': item.get('data_set_language', ''),
                'archive_center': item.get('archive_center', ''),
                'native_id': item.get('native_id', ''),
                'granule_count': item.get('granule_count', 0),
                'day_night_flag': item.get('day_night_flag', ''),
                'cloud_cover': item.get('cloud_cover', '')
            })
        elif node_type == 'DataCategory':
            properties.update({
                'summary': item.get('summary', '')
            })
        elif node_type == 'DataFormat':
            properties.update({
                'original_format': item.get('original_format', ''),
                'data_format': item.get('data_format', ''),
                'format_source': item.get('format_source', ''),
                'collection_data_type': item.get('collection_data_type', '')
            })
        elif node_type == 'CoordinateSystem':
            properties.update({
                'name': item.get('name', ''),
                'projection_type': item.get('projection_type', ''),
                'datum': item.get('datum', ''),
                'units': item.get('units', '')
            })
        elif node_type == 'Location':
            properties.update({
                'boxes': str(item.get('boxes', [])),
                'polygons': str(item.get('polygons', [])),
                'points': str(item.get('points', [])),
                'place_names': str(item.get('place_names', []))
            })
        elif node_type == 'Station':
            properties.update({
                'platforms': str(item.get('platforms', [])),
                'data_center': item.get('data_center', '')
            })
        elif node_type == 'Organization':
            properties.update({
                'name': item.get('name', ''),
                'type': item.get('type', '')
            })
        elif node_type == 'Platform':
            properties.update({
                'name': item.get('name', ''),
                'type': item.get('type', '')
            })
        elif node_type == 'Consortium':
            properties.update({
                'name': item.get('name', ''),
                'type': item.get('type', '')
            })
        elif node_type == 'TemporalExtent':
            properties.update({
                'start_time': item.get('start_time', ''),
                'end_time': item.get('end_time', ''),
                'updated': item.get('updated', '')
            })
        elif node_type == 'Variable':
            properties.update({
                'variable_id': item.get('variable_id', ''),
                'name': item.get('name', ''),
                'standard_name': item.get('standard_name', ''),
                'long_name': item.get('long_name', ''),
                'units': item.get('units', ''),
                'description': item.get('description', ''),
                'source': item.get('source', ''),
                'variable_type': item.get('variable_type', ''),
                'dataset_id': item.get('dataset_id', '')
            })
        elif node_type == 'Component':
            properties.update({
                'component_id': item.get('component_id', ''),
                'name': item.get('name', ''),
                'abbreviation': item.get('abbreviation', ''),
                'description': item.get('description', ''),
                'domain': item.get('domain', '')
            })
        elif node_type == 'Contact':
            properties.update({
                'contact_id': item.get('contact_id', ''),
                'contact_type': item.get('type', ''),
                'name': item.get('name', ''),
                'roles': str(item.get('roles', [])),
                'email': item.get('email', ''),
                'organization': item.get('organization', ''),
                'phone': item.get('phone', '')
            })
        elif node_type == 'Project':
            properties.update({
                'project_id': item.get('project_id', ''),
                'name': item.get('name', ''),
                'description': item.get('description', '')
            })
        elif node_type == 'RelatedUrl':
            properties.update({
                'url_id': item.get('url_id', ''),
                'url': item.get('url', ''),
                'type': item.get('type', ''),
                'subtype': item.get('subtype', ''),
                'description': item.get('description', ''),
                'format': item.get('format', '')
            })
        elif node_type == 'SpatialResolution':
            properties.update({
                'spatial_id': item.get('spatial_id', ''),
                'resolution': item.get('resolution', ''),
                'units': item.get('units', '')
            })
        elif node_type == 'TemporalResolution':
            properties.update({
                'temporal_id': item.get('temporal_id', ''),
                'resolution': item.get('resolution', ''),
                'frequency': item.get('frequency', '')
            })
        elif node_type == 'ScienceKeyword':
            properties.update({
                'keyword_id': item.get('keyword_id', ''),
                'category': item.get('category', ''),
                'topic': item.get('topic', ''),
                'term': item.get('term', ''),
                'variable_level_1': item.get('variable_level_1', ''),
                'variable_level_2': item.get('variable_level_2', ''),
                'variable_level_3': item.get('variable_level_3', ''),
                'detailed_variable': item.get('detailed_variable', '')
            })
        elif node_type == 'ProcessingLevel':
            properties.update({
                'processing_level_id': item.get('processing_level_id', ''),
                'id': item.get('id', ''),
                'description': item.get('description', '')
            })
        elif node_type in ['Workflow', 'PhysicsFirstWorkflow', 'DataFirstWorkflow', 'MLFirstWorkflow', 'HybridWorkflow']:
            properties.update({
                'workflow_id': item.get('workflow_id', ''),
                'workflow_name': item.get('workflow_name', ''),
                'workflow_type': item.get('workflow_type', node_type),
                'workflow_description': item.get('workflow_description', ''),
                'methodology': item.get('methodology', ''),
                'primary_approach': item.get('primary_approach', ''),
                'key_techniques': item.get('key_techniques', ''),
                'data_requirements': item.get('data_requirements', ''),
                'computational_complexity': item.get('computational_complexity', ''),
                'typical_timescales': item.get('typical_timescales', ''),
                'strengths': item.get('strengths', ''),
                'limitations': item.get('limitations', ''),
                'example_applications': item.get('example_applications', ''),
                'maturity_level': item.get('maturity_level', ''),
                'target_domain': item.get('target_domain', '')
            })
        
        # Queue embedding for specific vertex types
        if self.generate_embeddings and node_type in ["DataCategory", "Variable", "CESMVariable", "ScienceKeyword", 
                                                      "Location", "SpatialResolution", "TemporalResolution",
                                                      "SurrogateModelingWorkflow", "HybridMLPhysicsWorkflow", "EquationDiscoveryWorkflow",
                                                      "ParameterizationBenchmarkWorkflow", "UncertaintyQuantificationWorkflow", 
                                                      "ParameterInferenceWorkflow", "SubseasonalForecastingWorkflow", "TransferLearningWorkflow"]:
            text_for_embedding = self._create_text_for_embedding(node_type, item)
            self._queue_embedding(node_id, text_for_embedding)
        
        self.nodes[node_id] = properties
        
        # Debug logging for dataset nodes
        if node_type == 'Dataset':
            dataset_count = len([n for n in self.nodes.values() if n.get('type') == 'Dataset'])
            logger.debug(f"Created Dataset node #{dataset_count}: {node_id}")

    def create_node_id(self, node_type, item, index):
        """Create a unique node ID based on type and content."""
        if node_type == 'Dataset':
            short_name = item.get('short_name', str(index))
            clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', short_name)
            # Ensure uniqueness by including index to prevent overwrites from duplicate short_names
            return f"dataset_{clean_name}_{index}"
        elif node_type == 'DataFormat':
            fmt = item.get('original_format', '')
            clean_fmt = re.sub(r'[^a-zA-Z0-9_]', '_', fmt) if fmt else f"format_{index}"
            if clean_fmt in self.format_cache:
                return self.format_cache[clean_fmt]
            else:
                node_id = f"dataformat_{clean_fmt}"
                self.format_cache[clean_fmt] = node_id
                return node_id
        elif node_type == 'DataCategory':
            # Each dataset should have its own unique DataCategory node
            return f"datacategory_{index}"
        elif node_type == 'CoordinateSystem':
            coord_name = item.get('name', '')
            clean_coord_name = re.sub(r'[^a-zA-Z0-9_]', '_', coord_name) if coord_name else f"coord_{index}"
            if clean_coord_name in self.coordinate_system_cache:
                return self.coordinate_system_cache[clean_coord_name]
            else:
                node_id = f"coordinatesystem_{clean_coord_name}"
                self.coordinate_system_cache[clean_coord_name] = node_id
                return node_id
        elif node_type == 'Location':
            key = (
                str(item.get('boxes', [])),
                str(item.get('polygons', [])),
                str(item.get('points', [])),
                str(item.get('place_names', []))
            )
            if key in self.location_cache:
                return self.location_cache[key]
            else:
                node_id = f"location_{index}"
                self.location_cache[key] = node_id
                return node_id
        elif node_type == 'Station':
            # Use content-based caching instead of ID-based
            station_key = (
                str(item.get('platforms', [])),
                str(item.get('data_center', ''))
            )
            if station_key in self.station_cache:
                return self.station_cache[station_key]
            else:
                node_id = f"station_{len(self.station_cache)}"
                self.station_cache[station_key] = node_id
                return node_id
        elif node_type == 'Variable':
            var_id = item.get('variable_id', f'var_{index}')
            clean_var_id = re.sub(r'[^a-zA-Z0-9_]', '_', str(var_id))
            return clean_var_id
        elif node_type == 'CESMVariable':
            var_id = item.get('variable_id', f'cesm_var_{index}')
            clean_var_id = re.sub(r'[^a-zA-Z0-9_]', '_', str(var_id))
            return clean_var_id
        elif node_type == 'Component':
            comp_id = item.get('component_id', f'comp_{index}')
            clean_comp_id = re.sub(r'[^a-zA-Z0-9_]', '_', str(comp_id))
            return clean_comp_id
        elif node_type == 'Contact':
            contact_id = item.get('contact_id', f'contact_{index}')
            clean_contact_id = re.sub(r'[^a-zA-Z0-9_]', '_', str(contact_id))
            if clean_contact_id in self.contact_cache:
                return self.contact_cache[clean_contact_id]
            else:
                self.contact_cache[clean_contact_id] = contact_id
                return contact_id
        elif node_type == 'Project':
            project_id = item.get('project_id', f'project_{index}')
            clean_project_id = re.sub(r'[^a-zA-Z0-9_]', '_', str(project_id))
            if clean_project_id in self.project_cache:
                return self.project_cache[clean_project_id]
            else:
                self.project_cache[clean_project_id] = project_id
                return project_id
        elif node_type == 'RelatedUrl':
            url_id = item.get('url_id', f'url_{index}')
            clean_url_id = re.sub(r'[^a-zA-Z0-9_]', '_', str(url_id))
            if clean_url_id in self.url_cache:
                return self.url_cache[clean_url_id]
            else:
                self.url_cache[clean_url_id] = url_id
                return url_id
        elif node_type == 'SpatialResolution':
            spatial_id = item.get('spatial_id', f'spatial_{index}')
            clean_spatial_id = re.sub(r'[^a-zA-Z0-9_]', '_', str(spatial_id))
            if clean_spatial_id in self.spatial_cache:
                return self.spatial_cache[clean_spatial_id]
            else:
                self.spatial_cache[clean_spatial_id] = spatial_id
                return spatial_id
        elif node_type == 'TemporalResolution':
            temporal_id = item.get('temporal_id', f'temporal_{index}')
            clean_temporal_id = re.sub(r'[^a-zA-Z0-9_]', '_', str(temporal_id))
            if clean_temporal_id in self.temporal_cache:
                return self.temporal_cache[clean_temporal_id]
            else:
                self.temporal_cache[clean_temporal_id] = temporal_id
                return temporal_id
        elif node_type == 'ScienceKeyword':
            keyword_id = item.get('keyword_id', f'keyword_{index}')
            clean_keyword_id = re.sub(r'[^a-zA-Z0-9_]', '_', str(keyword_id))
            if clean_keyword_id in self.keyword_cache:
                return self.keyword_cache[clean_keyword_id]
            else:
                self.keyword_cache[clean_keyword_id] = keyword_id
                return keyword_id
        elif node_type == 'ProcessingLevel':
            level_id = item.get('processing_level_id', f'level_{index}')
            clean_level_id = re.sub(r'[^a-zA-Z0-9_]', '_', str(level_id))
            if clean_level_id in self.processing_cache:
                return self.processing_cache[clean_level_id]
            else:
                self.processing_cache[clean_level_id] = level_id
                return level_id
        elif node_type == 'Organization':
            # Use content-based caching
            org_key = (
                str(item.get('name', '')),
                str(item.get('type', ''))
            )
            if org_key in self.organization_cache:
                return self.organization_cache[org_key]
            else:
                node_id = f"organization_{len(self.organization_cache)}"
                self.organization_cache[org_key] = node_id
                return node_id
        elif node_type == 'Platform':
            # Use content-based caching
            platform_key = (
                str(item.get('name', '')),
                str(item.get('type', ''))  
            )
            if platform_key in self.platform_cache:
                return self.platform_cache[platform_key]
            else:
                node_id = f"platform_{len(self.platform_cache)}"
                self.platform_cache[platform_key] = node_id
                return node_id
        elif node_type == 'Consortium':
            # Use content-based caching
            consortium_key = (
                str(item.get('name', '')),
                str(item.get('type', ''))
            )
            if consortium_key in self.consortium_cache:
                return self.consortium_cache[consortium_key]
            else:
                node_id = f"consortium_{len(self.consortium_cache)}"
                self.consortium_cache[consortium_key] = node_id
                return node_id
        elif node_type in ['Workflow', 'PhysicsFirstWorkflow', 'DataFirstWorkflow', 'MLFirstWorkflow', 'HybridWorkflow']:
            workflow_id = item.get('workflow_id', '')
            if workflow_id:
                clean_workflow_id = re.sub(r'[^a-zA-Z0-9_]', '_', str(workflow_id))
                return clean_workflow_id
            else:
                workflow_name = item.get('workflow_name', f'{node_type.lower()}_{index}')
                clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', str(workflow_name))
                return f"workflow_{clean_name}"
        else:
            return f"{node_type.lower()}_{index}"

    def process_cesm_variables(self, cesm_variables):
        """Process CESM variables and store for later mapping."""
        for i, var in enumerate(cesm_variables):
            var_id = self.create_node_id('CESMVariable', var, i)
            cesm_name = var.get('cesm_name', var.get('name', ''))
            properties = {
                'id': var_id,
                'type': 'CESMVariable',
                'variable_id': var.get('variable_id', ''),
                'cesm_name': cesm_name,
                'name': var.get('name', ''),
                'standard_name': var.get('standard_name', ''),
                'long_name': var.get('long_name', ''),
                'units': var.get('units', ''),
                'description': var.get('description', ''),
                'domain': var.get('domain', ''),
                'component': var.get('component', ''),
                'variable_type': var.get('variable_type', ''),
                'source_dataset': var.get('source_dataset', '')
            }
            self.nodes[var_id] = properties

    def create_climate_workflows(self):
        """Create climate ML workflow nodes based on LEAP research."""
        workflows = [
            {
                'workflow_id': 'wf_surrogate_modeling',
                'workflow_name': 'Surrogate Modeling Workflow',
                'workflow_type': 'SurrogateModelingWorkflow',
                'workflow_description': 'Replace expensive PDE solvers with fast ML approximators using neural operators like FNO and SFNO',
                'methodology': 'Physics-First: Generate data using high-resolution simulations, train neural operators to learn mappings like initial condition åÆ future state, deploy as surrogate models in climate simulators',
                'primary_approach': 'Neural operator learning for PDE solving',
                'key_techniques': 'Fourier Neural Operators (FNO), Spherical Fourier Neural Operators (SFNO)',
                'data_requirements': 'High-resolution simulation data for training neural operators',
                'computational_complexity': 'High (training), Very Low (inference)',
                'typical_timescales': 'Training on simulation data, real-time inference',
                'strengths': 'Fast inference, learns solution operators',
                'limitations': 'Ensuring long-term stability and physical consistency',
                'example_applications': 'PDE solver replacement in climate models',
                'maturity_level': 'Research',
                'target_domain': 'atmosphere,ocean,land'
            },
            {
                'workflow_id': 'wf_hybrid_ml_physics',
                'workflow_name': 'Hybrid ML-Physics Workflow',
                'workflow_type': 'HybridMLPhysicsWorkflow',
                'workflow_description': 'ML emulation of subgrid physics using Cloud-Resolving Models data, deployed via PyTorch-Fortran bindings',
                'methodology': 'Physics-First: Use CRM-based simulations to create training data, train surrogates on inputoutput pairs (macro-scale åÆ CRM effects), deploy using PyTorchFortran bindings in climate simulators',
                'primary_approach': 'ML surrogates for subgrid physics parameterizations',
                'key_techniques': 'PyTorch-Fortran bindings, CRM-based training data, macro-scale to CRM effect mapping',
                'data_requirements': 'E3SM-MMF simulations, Cloud-Resolving Model output, macro-scale atmospheric state data',
                'computational_complexity': 'Medium (training), Low (inference)',
                'typical_timescales': 'Days to weeks for training, real-time deployment',
                'strengths': 'Scalable and clean interface for MLphysics hybrid simulations',
                'limitations': 'Depends on quality of CRM training data',
                'example_applications': 'Cloud parameterization, subgrid convection',
                'maturity_level': 'Research',
                'target_domain': 'atmosphere'
            },
            {
                'workflow_id': 'wf_equation_discovery',
                'workflow_name': 'Equation Discovery Workflow',
                'workflow_type': 'EquationDiscoveryWorkflow',
                'workflow_description': 'Discover interpretable parameterizations using ML methods like Relevance Vector Machines',
                'methodology': 'Physics-First: Generate coarsefine simulation pairs, use ML to discover interpretable closure equations, validate against deep nets and analytical models',
                'primary_approach': 'Sparse Bayesian learning for interpretable equation discovery',
                'key_techniques': 'Relevance Vector Machines (RVMs), coarse-fine simulation pairs, interpretable closure equations',
                'data_requirements': 'High-resolution simulations, coarse-grained simulation pairs for training',
                'computational_complexity': 'Medium to High',
                'typical_timescales': 'Weeks to months for equation discovery',
                'strengths': 'Recovers physical laws with minimal terms, interpretable results',
                'limitations': 'Limited to available simulation data quality',
                'example_applications': 'Ocean eddy parameterizations, atmospheric turbulence closure',
                'maturity_level': 'Research',
                'target_domain': 'atmosphere,land,ocean'
            },
            {
                'workflow_id': 'wf_parameterization_benchmark',
                'workflow_name': 'Parameterization Benchmarking Workflow',
                'workflow_type': 'ParameterizationBenchmarkWorkflow',
                'workflow_description': 'Systematically test ML parameterization design choices in idealized models using multiple diagnostic metrics',
                'methodology': 'Physics-First: Train FCNNs on coarse-grained simulations, compare input filters, subgrid forcing definitions, and padding methods, evaluate using multiple diagnostic metrics',
                'primary_approach': 'Benchmarking ML parameterizations against analytical models',
                'key_techniques': 'FCNNs, input filters, subgrid forcing definitions, padding methods, spectral RMSE, Wasserstein distance',
                'data_requirements': 'Quasi-geostrophic model simulations, coarse-grained training data',
                'computational_complexity': 'Medium',
                'typical_timescales': 'Weeks to months',
                'strengths': 'Systematic evaluation, multiple metrics, design guidance',
                'limitations': 'Limited to idealized models, computational cost',
                'example_applications': 'Quasi-geostrophic parameterizations, subgrid turbulence',
                'maturity_level': 'Research',
                'target_domain': 'atmosphere,ocean'
            },
            {
                'workflow_id': 'wf_uncertainty_quantification',
                'workflow_name': 'Uncertainty Quantification Workflow',
                'workflow_type': 'UncertaintyQuantificationWorkflow',
                'workflow_description': 'Quantify uncertainty in satellite retrievals using simulation-based approaches with emulated forward functions',
                'methodology': 'Data-First: Simulate true Earth states using Gaussian Processes, emulate forward function (spectrum generation) with ML, apply retrieval algorithm to simulated spectra, use unsupervised learning to approximate joint distributions',
                'primary_approach': 'Simulation-based uncertainty quantification for remote sensing',
                'key_techniques': 'Gaussian Processes, ML forward function emulation, Gaussian mixture models, conditional uncertainty estimates',
                'data_requirements': 'Satellite spectra, retrieval algorithms, simulated Earth states',
                'computational_complexity': 'Medium to High',
                'typical_timescales': 'Days to weeks for processing',
                'strengths': 'Provides uncertainty estimates, improves data assimilation',
                'limitations': 'Requires multiple observation sources, complex error correlations',
                'example_applications': 'NASA EMIT mission uncertainty quantification, satellite retrieval validation',
                'maturity_level': 'Operational',
                'target_domain': 'atmosphere,land,ocean'
            },
            {
                'workflow_id': 'wf_parameter_inference',
                'workflow_name': 'Parameter Inference Workflow',
                'workflow_type': 'ParameterInferenceWorkflow',
                'workflow_description': 'Infer physical model parameters from observed distributions using probabilistic programming',
                'methodology': 'Data-First: Train conditional normalizing flows on simulation data, use Maximum Mean Discrepancy to find best-fitting parameters',
                'primary_approach': 'Probabilistic parameter inference from distributions',
                'key_techniques': 'Conditional normalizing flows (cNF), Maximum Mean Discrepancy (MMD), probabilistic inference',
                'data_requirements': 'Simulation data with forcing-distribution pairs, observed parameter distributions',
                'computational_complexity': 'High',
                'typical_timescales': 'Weeks to months',
                'strengths': 'Reduces parameter uncertainty, improves model skill',
                'limitations': 'Computationally intensive, may overfit to calibration period',
                'example_applications': 'Land surface model calibration, ocean biogeochemistry tuning',
                'maturity_level': 'Research',
                'target_domain': 'land,ocean,atmosphere'
            },
            {
                'workflow_id': 'wf_subseasonal_forecasting',
                'workflow_name': 'Subseasonal Forecasting Workflow',
                'workflow_type': 'SubseasonalForecastingWorkflow',
                'workflow_description': 'Benchmark ML models for predicting Earth state from reanalysis data at 2-6 week timescales',
                'methodology': 'ML-First: Train models to predict global atmospheric variables at different lead times, compare autoregressive vs. direct prediction strategies, evaluate using MSE and visual metrics',
                'primary_approach': 'ML-based subseasonal forecasting',
                'key_techniques': 'FNO, ResNet, ClimaX, autoregressive prediction, direct prediction strategies',
                'data_requirements': 'ERA5 reanalysis data, global atmospheric variables, historical climate data',
                'computational_complexity': 'Medium to High',
                'typical_timescales': 'Hours for inference, days for training',
                'strengths': 'Can capture complex nonlinear patterns, fast inference',
                'limitations': 'Limited physical interpretability, requires extensive training data',
                'example_applications': 'Temperature and precipitation forecasts, extreme event prediction',
                'maturity_level': 'Operational',
                'target_domain': 'atmosphere'
            },
            {
                'workflow_id': 'wf_transfer_learning',
                'workflow_name': 'Transfer Learning Workflow',
                'workflow_type': 'TransferLearningWorkflow',
                'workflow_description': 'Extrapolate sparse observations across domains using pre-trained models and fine-tuning approaches',
                'methodology': 'ML-First: Pre-train models on synthetic data, fine-tune on real observations using transfer learning, leverage shared structure to improve generalization',
                'primary_approach': 'Transfer learning for sparse prediction problems',
                'key_techniques': 'Pre-training on synthetic data, fine-tuning on real observations, shared structure exploitation',
                'data_requirements': 'Synthetic training data, limited real-world observations, pre-trained model weights',
                'computational_complexity': 'Medium',
                'typical_timescales': 'Days to weeks',
                'strengths': 'Reduces data requirements, leverages existing knowledge',
                'limitations': 'Domain shift can reduce performance, requires careful validation',
                'example_applications': 'Regional climate downscaling, cross-sensor calibration',
                'maturity_level': 'Research',
                'target_domain': 'atmosphere,land,ocean'
            }
        ]
        
        logger.info(f"Creating {len(workflows)} climate ML workflow nodes...")
        
        for i, workflow in enumerate(workflows):
            workflow_type = workflow['workflow_type']
            node_id = self.create_node_id(workflow_type, workflow, i)
            
            properties = {
                'id': node_id,
                'type': workflow_type
            }
            properties.update(workflow)
            
            self.nodes[node_id] = properties
        
        logger.info(f" Created {len(workflows)} climate ML workflow nodes")

    def create_cesm_variable_mappings(self, data):
        """Create CESM variable to dataset mappings using ML model predictions."""
        if 'Dataset' not in data:
            logger.warning("No Dataset data found - skipping CESM variable mappings")
            return
        
        # Load ML predictions from CSV file
        try:
            import pandas as pd
            predictions_file = "../ML Model/predictions/cmr_dataset_predictions.csv"
            predictions_df = pd.read_csv(predictions_file)
            logger.info(f" Loaded {len(predictions_df)} ML predictions from {predictions_file}")
        except FileNotFoundError:
            logger.warning("¥î Could not find cmr_dataset_predictions.csv - skipping CESM variable mappings")
            return
        except Exception as e:
            logger.error(f"¥î Error loading ML predictions: {e}")
            return
        
        datasets = data['Dataset']
        logger.info(f"Creating CESM variable mappings for {len(datasets)} datasets...")
        
        # Build CESM variable lookup dictionary for O(1) access
        logger.info("Building CESM variable lookup dictionary...")
        cesm_var_lookup = {}
        for node_id, node in self.nodes.items():
            if node.get('type') == 'CESMVariable':
                cesm_name = node.get('cesm_name')
                if cesm_name:
                    cesm_var_lookup[cesm_name] = node_id
        logger.info(f" Built lookup for {len(cesm_var_lookup)} CESM variables")
        
        successful_mappings = 0
        failed_mappings = 0
        
        # Process ML predictions and create edges to existing CESM variable nodes
        for _, prediction_row in predictions_df.iterrows():
            try:
                ml_dataset_id = str(prediction_row['dataset_id']).strip()
                predicted_cesm = str(prediction_row['predicted_cesm_variable']).strip()
                aggregated_confidence = float(prediction_row['aggregated_confidence'])
                individual_confidence = float(prediction_row['individual_confidence'])
                quality_rating = str(prediction_row['quality_rating'])
                meets_threshold = bool(prediction_row['meets_threshold'])
                
                # Only process high-quality predictions
                if not meets_threshold or aggregated_confidence < 0.3:
                    continue
                
                # Extract dataset index from ML dataset ID (e.g., "ID_4" -> 3 as 0-based index)
                try:
                    dataset_index = int(ml_dataset_id.split('_')[1]) - 1  # Convert to 0-based index
                    if dataset_index < 0 or dataset_index >= len(datasets):
                        logger.warning(f"Dataset index {dataset_index} out of range for {ml_dataset_id}")
                        failed_mappings += 1
                        continue
                    
                    # Get the actual dataset and create its ID
                    dataset = datasets[dataset_index]
                    dataset_id = self.create_node_id('Dataset', dataset, dataset_index)
                    
                except (ValueError, IndexError) as e:
                    logger.error(f"Invalid dataset ID format: {ml_dataset_id} - {e}")
                    failed_mappings += 1
                    continue
                
                # Find existing CESM variable node using O(1) lookup
                cesm_var_id = cesm_var_lookup.get(predicted_cesm)
                
                if not cesm_var_id:
                    logger.warning(f"¥î Could not find existing CESM variable node for '{predicted_cesm}'")
                    failed_mappings += 1
                    continue
                
                # Don't add prediction metadata to CESM variable node - keep it intrinsic
                # Prediction metadata goes in the relationship properties instead
                
                # Create hasCESMVariable relationship - with existence check
                if dataset_id in self.nodes and cesm_var_id in self.nodes:
                    self.relationship_id_counter += 1
                    self.relationships.append({
                        'id': f"rel_{self.relationship_id_counter}",
                        'from': dataset_id,
                        'to': cesm_var_id,
                        'type': 'hasCESMVariable',
                        'individual_confidence': individual_confidence,
                        'aggregated_confidence': aggregated_confidence,
                        'quality_rating': quality_rating,
                        'prediction_method': 'climatebert_model',
                        'best_matching_tokens': str(prediction_row.get('best_matching_tokens', '')),
                        'group_type': str(prediction_row.get('group_type', '')),
                        'meets_threshold': meets_threshold
                    })
                else:
                    logger.debug(f"Skipped hasCESMVariable relationship: dataset_id={dataset_id} exists={dataset_id in self.nodes}, cesm_var_id={cesm_var_id} exists={cesm_var_id in self.nodes}")
                    failed_mappings += 1
                    continue
                
                successful_mappings += 1
                
            except Exception as e:
                logger.error(f"¥î Error processing ML prediction: {e}")
                failed_mappings += 1
                continue
        
        cesm_relationship_count = len([r for r in self.relationships if r['type'] == 'hasCESMVariable'])
        logger.info(f" Created {cesm_relationship_count} hasCESMVariable relationships")
        logger.info(f" Successfully processed {successful_mappings} predictions, {failed_mappings} failed")
        
        # Print quality distribution from relationships
        quality_counts = {}
        for rel in self.relationships:
            if rel.get('type') == 'hasCESMVariable' and rel.get('prediction_method') == 'climatebert_model':
                quality = rel.get('quality_rating', 'UNKNOWN')
                quality_counts[quality] = quality_counts.get(quality, 0) + 1
        
        if quality_counts:
            total_predictions = sum(quality_counts.values())
            logger.info(f"è ML Prediction quality distribution ({total_predictions} predictions):")
            for quality, count in sorted(quality_counts.items()):
                logger.info(f"   {quality}: {count} predictions")

    def map_domain_to_component(self, domain):
        """Map domain to component ID."""
        domain_to_component = {
            'atmosphere': 'comp_atm',
            'land': 'comp_lnd',
            'ocean': 'comp_ocn',
            'sea_ice': 'comp_ice',
            'river': 'comp_rof',
            'ice_sheet': 'comp_glc',
            'ocean_waves': 'comp_wav'
        }
        
        component_id = domain_to_component.get(domain)
        if component_id:
            # Check if component exists in nodes
            for node_id, node in self.nodes.items():
                if node.get('type') == 'Component' and node_id == component_id:
                    return component_id
        
        return None

    def escape_csv_value(self, value):
        """Properly escape CSV values according to Neptune's requirements."""
        if value is None:
            return ""
        # Convert to string
        value_str = str(value)
        
        # Check if value needs to be quoted (contains comma, newline, carriage return, or quote)
        needs_quoting = any(c in value_str for c in [',', '\n', '\r', '"'])
        
        # Always escape internal quotes by doubling them
        if '"' in value_str:
            value_str = value_str.replace('"', '""')
            needs_quoting = True  # Force quoting if there were quotes
        
        # Wrap in quotes if needed
        if needs_quoting:
            value_str = f'"{value_str}"'
            
        return value_str

    def write_nodes_csv(self, output_dir):
        """Write nodes to CSV file in Neptune CSV format."""
        if not self.nodes:
            logger.warning("No nodes to write")
            return

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Group nodes by label
        nodes_by_label = {}
        for node_id, node in self.nodes.items():
            label = node['type']
            if label not in nodes_by_label:
                nodes_by_label[label] = []
            nodes_by_label[label].append(node)
        
        # Write separate CSV files for each node label
        for label, nodes in nodes_by_label.items():
            # Skip empty node lists
            if not nodes:
                continue
                
            output_file = os.path.join(output_dir, f"{label.lower()}_nodes.csv")
            logger.info(f"Writing {len(nodes)} {label} nodes to {output_file}")
            
            # Collect properties used by this node type (excluding 'id' and 'type')
            properties_for_label = set()
            for node in nodes:
                properties_for_label.update(node.keys())
            
            # Remove 'id' and 'type' from properties as they are handled specially
            properties_for_label.discard('id')
            properties_for_label.discard('type')
            
            # Create CSV header using Neptune format
            header = ["~id", "~label"]
            for prop in sorted(properties_for_label):
                # Use correct Neptune Analytics vector format for embeddings
                if prop == 'embedding':
                    header.append("embedding:vector")
                else:
                    header.append(prop)  # Simple property names, no type annotations
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
                writer.writerow(header)
                
                for node in nodes:
                    row = [(node['id']), (node['type'])]  # ~id and ~label
                    for prop in sorted(properties_for_label):
                        value = node.get(prop, "")
                        # Clean the value for Neptune CSV
                        if isinstance(value, str):
                            # Simplify complex values
                            if prop == 'links' and value.startswith('['):
                                try:
                                    links = eval(value)
                                    if isinstance(links, list):
                                        # Extract href URLs from links array
                                        href_urls = []
                                        for link in links:
                                            if isinstance(link, dict) and 'href' in link:
                                                href_urls.append(link['href'])
                                        # Join URLs with pipe separator for easy splitting later
                                        value = '|'.join(href_urls) if href_urls else ""
                                    else:
                                        value = ""
                                except:
                                    value = ""
                            # Clean text by removing all punctuation (but skip links and URLs to preserve URLs)
                            if prop not in ['links', 'url', 'link_rel']:
                                value = clean_csv_text(value)
                            # Truncate long text
                            if len(value) > 500:
                                value = value[:500]
                        elif isinstance(value, list) and prop == 'embedding':
                            # Handle embeddings specially - ensure they are stored as float arrays
                            # Convert to semicolon-separated float values for Neptune Analytics vector format
                            try:
                                float_values = []
                                for x in value:
                                    f_val = float(x)
                                    # Handle very small scientific notation values that Neptune doesn't support
                                    if abs(f_val) < 1e-30:
                                        f_val = 0.0
                                    float_values.append(f_val)
                                # Use semicolons as separators, avoid scientific notation
                                value = ';'.join(f'{x:.8f}' for x in float_values)
                            except (ValueError, TypeError):
                                logger.warning(f"Invalid embedding values for node {node['id']}, skipping embedding")
                                value = ""
                        row.append((value))
                    writer.writerow(row)
            
            logger.info(f"Successfully wrote {label} nodes to {output_file}")

    def write_relationships_csv(self, output_dir):
        """Write relationships to CSV file in Neptune CSV format."""
        if not self.relationships:
            logger.warning("No relationships to write")
            return

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Group relationships by type
        rels_by_type = {}
        for rel in self.relationships:
            rel_type = rel['type']
            if rel_type not in rels_by_type:
                rels_by_type[rel_type] = []
            rels_by_type[rel_type].append(rel)
        
        # Write separate CSV files for each relationship type
        for rel_type, rels in rels_by_type.items():
            # Skip empty relationship lists
            if not rels:
                continue
                
            output_file = os.path.join(output_dir, f"{rel_type.lower()}_edges.csv")
            logger.info(f"Writing {len(rels)} {rel_type} relationships to {output_file}")
            
            # Create CSV header using Neptune format
            header = ["~id", "~from", "~to", "~label"]
            
            # Check for various confidence and quality attributes
            has_confidence = any('confidence' in rel for rel in rels)
            has_individual_confidence = any('individual_confidence' in rel for rel in rels)
            has_aggregated_confidence = any('aggregated_confidence' in rel for rel in rels)
            has_quality_rating = any('quality_rating' in rel for rel in rels)
            has_similarity_score = any('similarity_score' in rel for rel in rels)
            
            if has_confidence:
                header.append("confidence:Double")
            if has_individual_confidence:
                header.append("individual_confidence:Double")
            if has_aggregated_confidence:
                header.append("aggregated_confidence:Double")
            if has_quality_rating:
                header.append("quality_rating:String")
            if has_similarity_score:
                header.append("similarity_score:Double")
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
                writer.writerow(header)
                
                for rel in rels:
                    row = [
                        (rel['id']),
                        (rel['from']),
                        (rel['to']),
                        (rel['type'])
                    ]
                    
                    # Add confidence and quality attributes if available
                    if has_confidence:
                        confidence = rel.get('confidence', 0.0)
                        row.append((confidence))
                    if has_individual_confidence:
                        individual_conf = rel.get('individual_confidence', 0.0)
                        row.append((individual_conf))
                    if has_aggregated_confidence:
                        aggregated_conf = rel.get('aggregated_confidence', 0.0)
                        row.append((aggregated_conf))
                    if has_quality_rating:
                        quality = rel.get('quality_rating', '')
                        quality = clean_csv_text(str(quality))
                        row.append((quality))
                    if has_similarity_score:
                        similarity = rel.get('similarity_score', 0.0)
                        row.append((similarity))
                    
                    writer.writerow(row)
            
            logger.info(f"Successfully wrote {rel_type} relationships to {output_file}")

    def create_order_based_relationships(self, data):
        """Create order-based relationships between datasets and other nodes."""
        # Get all array-based node types
        array_node_types = [nt for nt in self.collections if nt in data and isinstance(data[nt], list)]
        
        if not array_node_types:
            return
            
        # Use Dataset length as the primary constraint since it's the main entity
        dataset_length = len(data.get('Dataset', []))
        if dataset_length == 0:
            logger.warning("No datasets found - skipping relationship creation")
            return
        
        # Create relationships for each dataset index
        successful_relationships = 0
        skipped_relationships = 0
        
        # DEBUG: Check actual dataset nodes before relationship creation
        actual_dataset_nodes = [n for n in self.nodes.values() if n.get('type') == 'Dataset']
        logger.info(f"DEBUG: Before relationship creation - {len(actual_dataset_nodes)} dataset nodes in self.nodes")
        
        for i in range(dataset_length):
            nodes_at_index = {}
            
            # Get node IDs for each type at this index
            for node_type in array_node_types:
                if i < len(data[node_type]):
                    item = data[node_type][i]
                    node_id = self.create_node_id(node_type, item, i)
                    nodes_at_index[node_type] = node_id

            # Create relationships based on the mapping
            for rel_type, (from_type, to_type) in self.relationship_map.items():
                if from_type in nodes_at_index and to_type in nodes_at_index:
                    from_id = nodes_at_index[from_type]
                    to_id = nodes_at_index[to_type]
                    
                    # Only create relationship if both nodes actually exist in self.nodes
                    if from_id in self.nodes and to_id in self.nodes:
                        # Create the relationship
                        self.relationship_id_counter += 1
                        self.relationships.append({
                            'id': f"rel_{self.relationship_id_counter}",
                            'from': from_id,
                            'to': to_id,
                            'type': rel_type
                        })
                        successful_relationships += 1
                    else:
                        skipped_relationships += 1
                        logger.info(f"SKIPPED {rel_type} at index {i}: from_id={from_id} exists={from_id in self.nodes}, to_id={to_id} exists={to_id in self.nodes}")
        
        logger.info(f" Created {successful_relationships} order-based relationships, skipped {skipped_relationships}")
        
        # Debug: Show relationship counts by type
        rel_counts_debug = {}
        for rel in self.relationships:
            rel_type = rel.get('type', 'Unknown')
            rel_counts_debug[rel_type] = rel_counts_debug.get(rel_type, 0) + 1
        
        dataset_rel_types = ['hasDataCategory', 'hasDataFormat', 'hasLocation', 'hasStation', 'hasOrganization']
        dataset_node_count = len([n for n in self.nodes.values() if n.get('type') == 'Dataset'])
        
        logger.info(f"DEBUG: Dataset nodes created: {dataset_node_count}")
        logger.info("DEBUG: Dataset-related relationship counts:")
        for rel_type in dataset_rel_types:
            count = rel_counts_debug.get(rel_type, 0)
            logger.info(f"  {rel_type}: {count}")
            if count > dataset_node_count:
                logger.warning(f"  Üá∩╕Å {rel_type} count ({count}) > Dataset count ({dataset_node_count})")

    def create_workflow_relationships(self, data):
        """Create relationships between ML workflow nodes and data nodes."""
        logger.info("ù Creating ML workflow relationships...")
        
        # Get workflow nodes
        workflow_nodes = [n for n in self.nodes.values() if n.get('type', '').endswith('Workflow')]
        if not workflow_nodes:
            logger.warning("No workflow nodes found - skipping workflow relationships")
            return
            
        logger.info(f"Found {len(workflow_nodes)} workflow nodes")
        
        # Get available data nodes of each type
        available_datasets = [n for n in self.nodes.values() if n.get('type') == 'Dataset']
        available_variables = [n for n in self.nodes.values() if n.get('type') == 'Variable']
        available_components = [n for n in self.nodes.values() if n.get('type') == 'Component'] 
        available_instruments = [n for n in self.nodes.values() if n.get('type') == 'Instrument']
        available_organizations = [n for n in self.nodes.values() if n.get('type') == 'Organization']
        available_platforms = [n for n in self.nodes.values() if n.get('type') == 'Platform']
        available_spatial_res = [n for n in self.nodes.values() if n.get('type') == 'SpatialResolution']
        available_temporal_res = [n for n in self.nodes.values() if n.get('type') == 'TemporalResolution']
        available_locations = [n for n in self.nodes.values() if n.get('type') == 'Location']
        
        successful_workflow_relationships = 0
        
        # Process each workflow type and create appropriate relationships
        for workflow_node in workflow_nodes:
            workflow_type = workflow_node.get('type')
            workflow_id = workflow_node.get('id')
            
            # Create relationships based on workflow-specific data requirements
            workflow_rels = []
            
            # All workflows use datasets
            if available_datasets:
                target_dataset = available_datasets[0]  # Use first available dataset
                workflow_rels.append({
                    'from': workflow_id,
                    'to': target_dataset.get('id'),
                    'type': f"{workflow_type}_usesDataset"
                })
            
            # Workflow-specific relationships based on the paper analysis
            if workflow_type == 'SurrogateModelingWorkflow':
                if available_spatial_res:
                    workflow_rels.append({
                        'from': workflow_id,
                        'to': available_spatial_res[0].get('id'),
                        'type': f"{workflow_type}_requiresHighResData"
                    })
                if available_temporal_res:
                    workflow_rels.append({
                        'from': workflow_id,
                        'to': available_temporal_res[0].get('id'),
                        'type': f"{workflow_type}_requiresTemporalData"
                    })
                if available_components:
                    workflow_rels.append({
                        'from': workflow_id,
                        'to': available_components[0].get('id'),
                        'type': f"{workflow_type}_appliesTo"
                    })
                    
            elif workflow_type == 'HybridMLPhysicsWorkflow':
                if available_variables:
                    workflow_rels.append({
                        'from': workflow_id,
                        'to': available_variables[0].get('id'),
                        'type': f"{workflow_type}_requiresAtmosphericData"
                    })
                if available_components:
                    workflow_rels.append({
                        'from': workflow_id,
                        'to': available_components[0].get('id'),
                        'type': f"{workflow_type}_appliesTo"
                    })
                if available_organizations:
                    workflow_rels.append({
                        'from': workflow_id,
                        'to': available_organizations[0].get('id'),
                        'type': f"{workflow_type}_requiresOrganization"
                    })
                    
            elif workflow_type == 'UncertaintyQuantificationWorkflow':
                if available_instruments:
                    workflow_rels.append({
                        'from': workflow_id,
                        'to': available_instruments[0].get('id'),
                        'type': f"{workflow_type}_requiresInstrument"
                    })
                if available_variables:
                    workflow_rels.append({
                        'from': workflow_id,
                        'to': available_variables[0].get('id'),
                        'type': f"{workflow_type}_requiresSpectra"
                    })
                if available_organizations:
                    workflow_rels.append({
                        'from': workflow_id,
                        'to': available_organizations[0].get('id'),
                        'type': f"{workflow_type}_requiresOrganization"
                    })
                if available_components:
                    workflow_rels.append({
                        'from': workflow_id,
                        'to': available_components[0].get('id'),
                        'type': f"{workflow_type}_appliesTo"
                    })
                    
            elif workflow_type == 'SubseasonalForecastingWorkflow':
                if available_variables:
                    workflow_rels.append({
                        'from': workflow_id,
                        'to': available_variables[0].get('id'),
                        'type': f"{workflow_type}_requiresReanalysisData"
                    })
                if available_platforms:
                    workflow_rels.append({
                        'from': workflow_id,
                        'to': available_platforms[0].get('id'),
                        'type': f"{workflow_type}_requiresPlatform"
                    })
                if available_organizations:
                    workflow_rels.append({
                        'from': workflow_id,
                        'to': available_organizations[0].get('id'),
                        'type': f"{workflow_type}_requiresOrganization"
                    })
                if available_components:
                    workflow_rels.append({
                        'from': workflow_id,
                        'to': available_components[0].get('id'),
                        'type': f"{workflow_type}_appliesTo"
                    })
                    
            elif workflow_type == 'TransferLearningWorkflow':
                if available_variables:
                    workflow_rels.append({
                        'from': workflow_id,
                        'to': available_variables[0].get('id'),
                        'type': f"{workflow_type}_requiresSparseObservations"
                    })
                if available_locations:
                    workflow_rels.append({
                        'from': workflow_id,
                        'to': available_locations[0].get('id'),
                        'type': f"{workflow_type}_requiresLocation"
                    })
                if available_organizations:
                    workflow_rels.append({
                        'from': workflow_id,
                        'to': available_organizations[0].get('id'),
                        'type': f"{workflow_type}_requiresOrganization"
                    })
                if available_components:
                    workflow_rels.append({
                        'from': workflow_id,
                        'to': available_components[0].get('id'),
                        'type': f"{workflow_type}_appliesTo"
                    })
            
            # Add other workflow types with generic relationships
            else:
                if available_variables:
                    workflow_rels.append({
                        'from': workflow_id,
                        'to': available_variables[0].get('id'),
                        'type': f"{workflow_type}_requiresVariable"
                    })
                if available_components:
                    workflow_rels.append({
                        'from': workflow_id,
                        'to': available_components[0].get('id'),
                        'type': f"{workflow_type}_appliesTo"
                    })
                if available_organizations:
                    workflow_rels.append({
                        'from': workflow_id,
                        'to': available_organizations[0].get('id'),
                        'type': f"{workflow_type}_requiresOrganization"
                    })
            
            # Add all workflow relationships to the main relationships list
            for rel in workflow_rels:
                self.relationship_id_counter += 1
                rel['id'] = f"rel_{self.relationship_id_counter}"
                self.relationships.append(rel)
                successful_workflow_relationships += 1
        
        logger.info(f" Created {successful_workflow_relationships} workflow relationships")

    def string_similarity(self, a, b):
        """Calculate string similarity between two strings using SequenceMatcher"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def find_similar_cesm_variables(self, variable_name, all_variables, threshold=0.7):
        """Find CESM variables with high string similarity"""
        similar = []
        for var in all_variables:
            if var != variable_name:
                similarity = self.string_similarity(variable_name, var)
                if similarity >= threshold:
                    similar.append((var, similarity))
        return similar

    def create_cesm_similarity_relationships(self, threshold=0.7):
        """Create similarCESMVariable relationships based on string similarity"""
        logger.info("ù Creating CESM variable similarity relationships...")
        
        # Get all CESM variable nodes
        cesm_variables = [n for n in self.nodes.values() if n.get('type') == 'CESMVariable']
        if not cesm_variables:
            logger.warning("No CESM variable nodes found - skipping similarity relationships")
            return
            
        logger.info(f"Found {len(cesm_variables)} CESM variables for similarity analysis")
        
        # Extract variable names for similarity comparison
        all_variable_names = [var.get('short_name', var.get('id', '')) for var in cesm_variables]
        variable_name_to_node = {var.get('short_name', var.get('id', '')): var for var in cesm_variables}
        
        successful_similarity_relationships = 0
        processed_pairs = set()  # To avoid duplicate bidirectional relationships
        
        # Process each CESM variable
        for var_node in cesm_variables:
            var_name = var_node.get('short_name', var_node.get('id', ''))
            if not var_name:
                continue
                
            # Find similar variables
            similar_vars = self.find_similar_cesm_variables(var_name, all_variable_names, threshold)
            
            for similar_var_name, similarity_score in similar_vars:
                # Create a sorted tuple to avoid duplicate relationships
                pair_key = tuple(sorted([var_name, similar_var_name]))
                if pair_key in processed_pairs:
                    continue
                    
                processed_pairs.add(pair_key)
                
                # Get the similar variable node
                similar_var_node = variable_name_to_node.get(similar_var_name)
                if not similar_var_node:
                    continue
                
                # Create bidirectional similarity relationships
                # Relationship 1: var1 -> var2
                self.relationship_id_counter += 1
                rel1 = {
                    'id': f"rel_{self.relationship_id_counter}",
                    'from': var_node.get('id'),
                    'to': similar_var_node.get('id'),
                    'type': 'similarCESMVariable',
                    'similarity_score': round(similarity_score, 3)
                }
                self.relationships.append(rel1)
                successful_similarity_relationships += 1
                
                # Relationship 2: var2 -> var1 (bidirectional)
                self.relationship_id_counter += 1
                rel2 = {
                    'id': f"rel_{self.relationship_id_counter}",
                    'from': similar_var_node.get('id'),
                    'to': var_node.get('id'),
                    'type': 'similarCESMVariable',
                    'similarity_score': round(similarity_score, 3)
                }
                self.relationships.append(rel2)
                successful_similarity_relationships += 1
                
        logger.info(f" Created {successful_similarity_relationships} CESM variable similarity relationships (threshold: {threshold})")

    def convert_to_csvs(self, input_file, output_dir):
        """Convert JSON data to Neptune CSV format."""
        try:
            self.reset_state()
            
            # Log system information and capabilities
            logger.info(f" SYSTEM INFORMATION:")
            logger.info(f"    Operating System: {os.name}")
            logger.info(f"    Python Version: {sys.version}")
            logger.info(f"    Working Directory: {os.getcwd()}")
            logger.info(f"    Script Location: {os.path.abspath(__file__)}")
            
            # Log available components
            logger.info(f" AVAILABLE COMPONENTS:")
            logger.info(f"    SentenceTransformers: {' Available' if SENTENCE_TRANSFORMERS_AVAILABLE else '¥î Missing'}")
            logger.info(f"    Pandas: {' Available' if 'pandas' in sys.modules else '¥î Missing'}")
            logger.info(f"    Embedding Generation: {' Enabled' if self.generate_embeddings else '¥î Disabled'}")
            
            # Using pre-computed ML predictions for CESM variable mapping
            logger.info("Using pre-computed ML predictions for CESM variable to dataset mapping")
            
            # Process JSON file (Windows-compatible path)
            input_file_path = os.path.abspath(input_file)
            logger.info(f"Processing JSON file: {input_file_path}")
            
            if not os.path.exists(input_file_path):
                raise FileNotFoundError(f"Input JSON file not found: {input_file_path}")
                
            self.process_json_file(input_file_path)
            
            # Write CSV files (Windows-compatible path)
            output_dir_path = os.path.abspath(output_dir)
            logger.info(f"Writing CSV files to: {output_dir_path}")
            
            self.write_nodes_csv(output_dir_path)
            self.write_relationships_csv(output_dir_path)
            
            # Write summary
            summary = {
                'total_nodes': len(self.nodes),
                'total_relationships': len(self.relationships),
                'node_counts_by_type': {},
                'relationship_counts_by_type': {},
                'embedding_generation_enabled': self.generate_embeddings
            }
            
            # Count nodes by type
            for node in self.nodes.values():
                node_type = node['type']
                summary['node_counts_by_type'][node_type] = summary['node_counts_by_type'].get(node_type, 0) + 1
            
            # Count relationships by type  
            for rel in self.relationships:
                rel_type = rel['type']
                summary['relationship_counts_by_type'][rel_type] = summary['relationship_counts_by_type'].get(rel_type, 0) + 1
            
            summary_path = os.path.join(output_dir_path, 'conversion_summary.json')
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2)
            
            # Finalize any remaining embeddings
            if self.generate_embeddings:
                logger.info(" Processing remaining embeddings...")
                self._finalize_embeddings()
                total_with_embeddings = sum(1 for node in self.nodes.values() if 'embedding' in node)
                logger.info(f" Generated embeddings for {total_with_embeddings} nodes")
            
            logger.info(f" Conversion complete. Created {len(self.nodes)} nodes and {len(self.relationships)} relationships")
            logger.info(f" Conversion summary written to {summary_path}")
            
            return summary_path
            
        except Exception as e:
            logger.error(f"¥î Error in conversion: {str(e)}")
            raise

def upload_to_s3(local_dir, bucket_name, prefix):
    """Upload CSV files to S3 bucket."""
    try:
        s3 = boto3.client('s3')
        
        # Walk through the directory and upload each file
        for root, _, files in os.walk(local_dir):
            for file in files:
                local_path = os.path.join(root, file)
                # Create S3 key by replacing local path with S3 prefix
                rel_path = os.path.relpath(local_path, local_dir)
                s3_key = f"{prefix}/{rel_path}"
                
                logger.info(f"Uploading {local_path} to s3://{bucket_name}/{s3_key}")
                s3.upload_file(local_path, bucket_name, s3_key)
        
        logger.info(f"Successfully uploaded all files to s3://{bucket_name}/{prefix}/")
        return True
    except Exception as e:
        logger.error(f"Error uploading to S3: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Convert JSON to Neptune CSV format')
    parser.add_argument('--input', default='../NasaCMRData/json_files/structured_cmr_data.json', help='Input JSON file path')
    parser.add_argument('--output-dir', default='neptune_csvs', help='Output directory for CSV files')
    parser.add_argument('--upload-s3', help='S3 bucket name to upload files (optional)')
    parser.add_argument('--s3-prefix', default='neptune-data/', help='S3 prefix for uploaded files')
    parser.add_argument('--generate-embeddings', action='store_true', default=True,
                       help='Generate text embeddings for DataCategory, Variable, CESMVariable, ScienceKeyword, Location, SpatialResolution, and TemporalResolution vertices (default: True)')
    
    args = parser.parse_args()
    
    try:
        converter = JSONToCSVConverter(generate_embeddings=args.generate_embeddings)
        summary_path = converter.convert_to_csvs(args.input, args.output_dir)
        
        logger.info("Generated files follow Neptune OpenCypher format:")
        logger.info("- Separate CSV file for each node type (e.g., dataset_nodes.csv)")
        logger.info("- Separate CSV file for each relationship type (e.g., hasdatacategory_edges.csv)")
        logger.info("- Node files have :ID, property:Type columns, and :LABEL")
        logger.info("- Relationship files have :ID, :START_ID, :END_ID, and :TYPE columns")
        
        if args.upload_s3:
            upload_to_s3(args.output_dir, args.upload_s3, args.s3_prefix)
            logger.info(f"Files uploaded to S3 bucket: {args.upload_s3}")
            
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    exit(main())
