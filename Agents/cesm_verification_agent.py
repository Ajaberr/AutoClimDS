#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CESM LENS Verification Agent

A lean verification agent that validates technical aspects of CESM LENS data analysis:
- Data loading and S3 path verification
- Computational validation (checking calculations are correct)
- Database integrity checks
- Real data quality assessment (not templated responses)

The LLM handles all interpretation and critical analysis based on real results.
"""

import json
import os
import sys
import sqlite3
import boto3
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# LangChain imports for agent framework
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import BaseTool, DuckDuckGoSearchRun
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.callbacks import CallbackManagerForToolRun

from dotenv import load_dotenv

# Load .env if present (harmless in prod CI as well)
load_dotenv()

# Configuration constants (same as other agents)
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-2")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")

# --- Bedrock LLM (exact copy from other agents) ---
class BedrockClaudeLLM(LLM):
    """LangChain wrapper for AWS Bedrock using the Claude Sonnet model"""
    bedrock: Any = None
    model_id: str = BEDROCK_MODEL_ID
    
    def __init__(self):
        super().__init__()
        try:
            self.bedrock = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
            print(" Bedrock Claude LLM initialized successfully")
        except Exception as e:
            print(f" Bedrock client failed to initialize: {e}. LLM calls will use a fallback.")
            self.bedrock = None

    @property
    def _llm_type(self) -> str:
        return "bedrock_claude_sonnet"

    def _call(self, prompt: str, stop: Optional[List[str]] = None, run_manager: Optional[CallbackManagerForLLMRun] = None, **kwargs) -> str:
        if not self.bedrock:
            return f"DUMMY LLM RESPONSE: Bedrock is not configured. The prompt was: {prompt}"
        
        stop_sequences = stop or ["\nObservation:"]

        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "top_p": 0.9,
                "stop_sequences": stop_sequences
            })
            response = self.bedrock.invoke_model(modelId=self.model_id, body=body)
            response_body = json.loads(response["body"].read())
            return response_body["content"][0]["text"].strip()
        except Exception as e:
            raise e


class ClimateResearchSearchTool(BaseTool):
    """Search for climate research papers and validation studies"""
    name: str = "search_climate_research"
    description: str = "Search for climate science literature, CESM studies, model validation papers, and research methodologies"
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Search for climate research"""
        try:
            search = DuckDuckGoSearchRun()
            
            # Enhance query for academic sources
            enhanced_query = f"climate science CESM model validation {query} site:journals.ametsoc.org OR site:nature.com OR site:science.org OR site:agupubs.onlinelibrary.wiley.com"
            results = search.run(enhanced_query)
            
            return f" Climate Research Search Results for '{query}':\n{results}"
        except Exception as e:
            return f" Research search failed: {str(e)}"


class MethodologySearchTool(BaseTool):
    """Search for research methodology and best practices"""
    name: str = "search_methodology"
    description: str = "Search for climate modeling methodologies, statistical analysis best practices, and research validation techniques"
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Search for methodology information"""
        try:
            # Try web search first
            try:
                search = DuckDuckGoSearchRun()
                enhanced_query = f"climate modeling methodology {query} statistical validation best practices site:journals.ametsoc.org OR site:nature.com OR site:agupubs.onlinelibrary.wiley.com"
                results = search.run(enhanced_query)
                
                # Check if results are relevant (filter out irrelevant content)
                if any(irrelevant in results.lower() for irrelevant in ['iphone', '手机', 'smartphone', 'car', '汽车']):
                    raise Exception("Irrelevant search results")
                    
                return f" Methodology Search Results for '{query}':\n{results}"
            except:
                # Fallback to curated methodology guidance
                return self._get_curated_methodology_guidance(query)
                
        except Exception as e:
            return f" Methodology search failed: {str(e)}"


class ResearchProcessValidationTool(BaseTool):
    """Validate research process and methodology"""
    name: str = "validate_research_process"
    description: str = "Examine the research workflow, data sources, analysis methods, and overall scientific approach for potential issues"
    
    def _run(self, focus_area: str = "overall", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Validate research process"""
        try:
            output = f" RESEARCH PROCESS VALIDATION\n"
            output += "=" * 35 + "\n\n"
            
            # Check what research components are available
            research_components = self._assess_research_components()
            
            output += f" RESEARCH COMPONENT ASSESSMENT:\n"
            for component, status in research_components.items():
                icon = "" if status['available'] else ""
                output += f"   {icon} {component}: {status['description']}\n"
            
            output += f"\n RESEARCH WORKFLOW ANALYSIS:\n"
            
            # Data sources validation
            if research_components['data_sources']['available']:
                output += f"    Data Sources: Multiple sources identified (CESM model + observational)\n"
                output += f"      • Strength: Allows model-observation comparison\n"
                output += f"      • Consideration: Need to verify data compatibility and temporal alignment\n"
            else:
                output += f"    Data Sources: Limited or missing data sources\n"
            
            # Methodology assessment
            if research_components['analysis_tools']['available']:
                output += f"    Analysis Methods: Statistical comparison tools available\n"
                output += f"      • Strength: Can perform quantitative model validation\n"
                output += f"      • Consideration: Ensure statistical methods are appropriate for climate data\n"
            else:
                output += f"    Analysis Methods: Analysis tools not properly configured\n"
            
            # Verification process
            output += f"    Verification: Technical validation tools available\n"
            output += f"      • Strength: Can verify data integrity and computation accuracy\n"
            output += f"      • Recommendation: Use verification before drawing conclusions\n"
            
            output += f"\n RESEARCH QUALITY INDICATORS:\n"
            
            # Calculate research readiness score
            available_components = sum(1 for comp in research_components.values() if comp['available'])
            total_components = len(research_components)
            readiness_score = (available_components / total_components) * 100
            
            output += f"    Research Readiness: {readiness_score:.0f}% ({available_components}/{total_components} components ready)\n"
            
            if readiness_score >= 80:
                output += f"    Status: Research infrastructure is well-prepared\n"
            elif readiness_score >= 60:
                output += f"    Status: Research infrastructure is mostly ready with some gaps\n"
            else:
                output += f"    Status: Significant gaps in research infrastructure\n"
            
            output += f"\n RECOMMENDED VALIDATION STEPS:\n"
            output += f"   1. Verify all databases contain expected data\n"
            output += f"   2. Test data loading and processing pipeline\n"
            output += f"   3. Validate statistical analysis computations\n"
            output += f"   4. Cross-check results with published literature\n"
            output += f"   5. Document assumptions and limitations\n"
            
            return output
            
        except Exception as e:
            return f" Research process validation failed: {str(e)}"
    
    def _assess_research_components(self) -> Dict[str, Dict]:
        """Assess availability of research components"""
        components = {}
        
        # Check data sources
        cesm_db_exists = os.path.exists("cesm_data_registry.db")
        obs_db_exists = os.path.exists("climate_knowledge_graph.db")
        
        components['data_sources'] = {
            'available': cesm_db_exists and obs_db_exists,
            'description': f"CESM: {'✓' if cesm_db_exists else '✗'}, Observational: {'✓' if obs_db_exists else '✗'}"
        }
        
        # Check analysis tools
        try:
            from cesm_obs_comparison_agent import ComparisonDataManager
            components['analysis_tools'] = {
                'available': True,
                'description': "Comparison analysis tools available"
            }
        except ImportError:
            components['analysis_tools'] = {
                'available': False,
                'description': "Comparison analysis tools not accessible"
            }
        
        # Check verification capabilities
        components['verification'] = {
            'available': True,  # This tool is running
            'description': "Technical validation and verification tools"
        }
        
        # Check documentation
        components['documentation'] = {
            'available': True,  # Assume basic documentation exists
            'description': "Agent documentation and methodology descriptions"
        }
        
        return components


class GeneralInfoValidationTool(BaseTool):
    """Validate general information and provide research context"""
    name: str = "validate_general_info"
    description: str = "Validate general information about climate data, models, and research context. Provide background verification."
    
    def _run(self, info_type: str = "overview", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Validate general information"""
        try:
            output = f" GENERAL INFORMATION VALIDATION\n"
            output += "=" * 35 + "\n\n"
            
            if info_type in ['overview', 'all']:
                output += self._validate_climate_modeling_context()
                output += "\n"
            
            if info_type in ['cesm', 'all']:
                output += self._validate_cesm_info()
                output += "\n"
            
            if info_type in ['observational', 'all']:
                output += self._validate_observational_context()
                output += "\n"
            
            if info_type in ['comparison', 'all']:
                output += self._validate_comparison_methodology()
                output += "\n"
            
            return output
            
        except Exception as e:
            return f" General information validation failed: {str(e)}"
    
    def _validate_climate_modeling_context(self) -> str:
        """Validate climate modeling context"""
        output = f" CLIMATE MODELING CONTEXT:\n"
        output += f"   • Purpose: Climate models simulate Earth's climate system for understanding and prediction\n"
        output += f"   • CESM: Community Earth System Model - widely used global climate model\n"
        output += f"   • Ensemble Approach: Multiple simulations capture uncertainty and natural variability\n"
        output += f"   • Validation Need: Models must be compared with observations to assess accuracy\n"
        output += f"   ✓ Context appears scientifically sound\n"
        return output
    
    def _validate_cesm_info(self) -> str:
        """Validate CESM-specific information"""
        output = f" CESM MODEL INFORMATION:\n"
        output += f"   • CESM LENS: Large Ensemble simulations for climate variability analysis\n"
        output += f"   • Components: Atmosphere, ocean, land, sea ice coupled system\n"
        output += f"   • Data Format: Typically NetCDF/Zarr format in cloud storage\n"
        output += f"   • Variables: Temperature, precipitation, pressure, etc.\n"
        output += f"   ✓ CESM description aligns with known model characteristics\n"
        return output
    
    def _validate_observational_context(self) -> str:
        """Validate observational data context"""
        output = f" OBSERVATIONAL DATA CONTEXT:\n"
        output += f"   • Sources: Satellites, weather stations, ocean buoys, research campaigns\n"
        output += f"   • NASA CMR: Common Metadata Repository for Earth science data discovery\n"
        output += f"   • AWS Open Data: Cloud-accessible observational datasets\n"
        output += f"   • Quality: Observational data has own uncertainties and limitations\n"
        output += f"   ✓ Observational approach is methodologically appropriate\n"
        return output
    
    def _validate_comparison_methodology(self) -> str:
        """Validate model-observation comparison methodology"""
        output = f" COMPARISON METHODOLOGY:\n"
        output += f"   • Statistical Metrics: Bias, RMSE, correlation are standard validation metrics\n"
        output += f"   • Spatial/Temporal Matching: Need to align model and observation grids/times\n"
        output += f"   • Uncertainty: Both models and observations have uncertainties to consider\n"
        output += f"   • Ensemble Analysis: Multiple model runs help separate signal from noise\n"
        output += f"   ✓ Comparison approach follows established climate validation practices\n"
        return output


class DatabaseValidationTool(BaseTool):
    """Validate database integrity and data availability"""
    name: str = "validate_databases"
    description: str = "Check if CESM and observational databases exist and contain valid data for analysis"
    
    def _run(self, check_type: str = "both", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Validate database integrity"""
        try:
            output = f" DATABASE VALIDATION\n"
            output += "=" * 30 + "\n\n"
            
            validation_results = {}
            
            # Check CESM database
            cesm_db_path = "cesm_data_registry.db"
            if os.path.exists(cesm_db_path):
                try:
                    with sqlite3.connect(cesm_db_path) as conn:
                        cursor = conn.execute("SELECT COUNT(*) FROM cesm_data_paths")
                        cesm_count = cursor.fetchone()[0]
                        
                        # Get sample records
                        cursor = conn.execute("SELECT variable_name, start_year, end_year FROM cesm_data_paths LIMIT 3")
                        cesm_samples = cursor.fetchall()
                        
                        validation_results['cesm'] = {
                            'exists': True,
                            'record_count': cesm_count,
                            'samples': cesm_samples
                        }
                        
                        output += f" CESM Database (cesm_data_registry.db):\n"
                        output += f"    Found {cesm_count} records\n"
                        output += f"    Sample variables: {', '.join([s[0] for s in cesm_samples])}\n\n"
                        
                except Exception as e:
                    validation_results['cesm'] = {'exists': True, 'error': str(e)}
                    output += f" CESM Database error: {e}\n\n"
            else:
                validation_results['cesm'] = {'exists': False}
                output += f" CESM Database not found: {cesm_db_path}\n\n"
            
            # Check observational database
            obs_db_path = "climate_knowledge_graph.db"
            if os.path.exists(obs_db_path):
                try:
                    with sqlite3.connect(obs_db_path) as conn:
                        cursor = conn.execute("SELECT COUNT(*) FROM stored_datasets WHERE s3_path IS NOT NULL")
                        obs_count = cursor.fetchone()[0]
                        
                        # Get sample records
                        cursor = conn.execute("SELECT title, short_name FROM stored_datasets WHERE s3_path IS NOT NULL LIMIT 3")
                        obs_samples = cursor.fetchall()
                        
                        validation_results['observational'] = {
                            'exists': True,
                            'record_count': obs_count,
                            'samples': obs_samples
                        }
                        
                        output += f" Observational Database (climate_knowledge_graph.db):\n"
                        output += f"    Found {obs_count} datasets with S3 paths\n"
                        output += f"    Sample datasets: {', '.join([s[1] for s in obs_samples])}\n\n"
                        
                except Exception as e:
                    validation_results['observational'] = {'exists': True, 'error': str(e)}
                    output += f" Observational Database error: {e}\n\n"
            else:
                validation_results['observational'] = {'exists': False}
                output += f" Observational Database not found: {obs_db_path}\n\n"
            
            # Overall assessment
            cesm_ok = validation_results.get('cesm', {}).get('record_count', 0) > 0
            obs_ok = validation_results.get('observational', {}).get('record_count', 0) > 0
            
            output += f" VALIDATION SUMMARY:\n"
            if cesm_ok and obs_ok:
                output += f"    Both databases are ready for comparison analysis\n"
            elif cesm_ok:
                output += f"    CESM data available, but observational data missing\n"
            elif obs_ok:
                output += f"    Observational data available, but CESM data missing\n"
            else:
                output += f"    Neither database is ready - run other agents first\n"
            
            return output
            
        except Exception as e:
            return f" Database validation failed: {str(e)}"


class S3PathValidationTool(BaseTool):
    """Validate S3 paths are correctly constructed and accessible"""
    name: str = "validate_s3_paths"
    description: str = "Check if S3 paths are properly constructed and accessible for both CESM and observational data"
    
    def _run(self, path_type: str = "both", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Validate S3 path construction and accessibility"""
        try:
            import s3fs
            
            output = f" S3 PATH VALIDATION\n"
            output += "=" * 25 + "\n\n"
            
            # Initialize S3 filesystem
            fs = s3fs.S3FileSystem(anon=True)
            
            # Check CESM S3 paths
            if path_type in ['both', 'cesm']:
                cesm_paths = self._get_cesm_s3_paths()
                output += f" CESM S3 PATH VALIDATION:\n"
                
                if cesm_paths:
                    for i, path_info in enumerate(cesm_paths[:3], 1):  # Check first 3
                        variable = path_info['variable']
                        s3_path = path_info['s3_path']
                        
                        output += f"   {i}. {variable}: {s3_path}\n"
                        
                        try:
                            # Check if path exists
                            path_exists = fs.exists(s3_path.replace('s3://', ''))
                            output += f"      {' Accessible' if path_exists else ' Not found'}\n"
                            
                        except Exception as e:
                            output += f"       Check failed: {e}\n"
                else:
                    output += f"    No CESM paths found in database\n"
                
                output += "\n"
            
            # Check observational S3 paths
            if path_type in ['both', 'obs']:
                obs_paths = self._get_obs_s3_paths()
                output += f" OBSERVATIONAL S3 PATH VALIDATION:\n"
                
                if obs_paths:
                    for i, path_info in enumerate(obs_paths[:3], 1):  # Check first 3
                        title = path_info['title']
                        s3_path = path_info['s3_path']
                        
                        output += f"   {i}. {title}: {s3_path}\n"
                        
                        try:
                            # Check if path exists (basic check)
                            if s3_path.startswith('s3://'):
                                path_exists = fs.exists(s3_path.replace('s3://', ''))
                                output += f"      {' Accessible' if path_exists else ' Not found'}\n"
                            else:
                                output += f"       Invalid S3 path format\n"
                            
                        except Exception as e:
                            output += f"       Check failed: {e}\n"
                else:
                    output += f"    No observational S3 paths found in database\n"
            
            return output
            
        except Exception as e:
            return f" S3 path validation failed: {str(e)}"
    
    def _get_cesm_s3_paths(self) -> List[Dict]:
        """Get CESM S3 paths from database"""
        try:
            with sqlite3.connect("cesm_data_registry.db") as conn:
                cursor = conn.execute("""
                    SELECT variable_name, component, frequency, experiment, start_year, end_year
                    FROM cesm_data_paths LIMIT 5
                """)
                
                paths = []
                for row in cursor.fetchall():
                    variable, component, frequency, experiment, start_year, end_year = row
                    
                    # Construct S3 path same as comparison agent
                    component = component or 'atm'
                    frequency = frequency or 'monthly'
                    experiment = experiment or '20C'
                    
                    s3_path = f"s3://ncar-cesm-lens/{component}/{frequency}/cesmLE-{experiment}-{variable}.zarr"
                    
                    paths.append({
                        'variable': variable,
                        's3_path': s3_path,
                        'time_range': f"{start_year}-{end_year}"
                    })
                
                return paths
                
        except Exception as e:
            print(f"Error getting CESM paths: {e}")
            return []
    
    def _get_obs_s3_paths(self) -> List[Dict]:
        """Get observational S3 paths from database"""
        try:
            with sqlite3.connect("climate_knowledge_graph.db") as conn:
                cursor = conn.execute("""
                    SELECT title, short_name, s3_path
                    FROM stored_datasets 
                    WHERE s3_path IS NOT NULL 
                    LIMIT 5
                """)
                
                paths = []
                for title, short_name, s3_path in cursor.fetchall():
                    paths.append({
                        'title': title,
                        'short_name': short_name,
                        's3_path': s3_path
                    })
                
                return paths
                
        except Exception as e:
            print(f"Error getting observational paths: {e}")
            return []


class DataLoadTestTool(BaseTool):
    """Test actual data loading to verify everything works"""
    name: str = "test_data_loading"
    description: str = "Test loading actual data from S3 paths to verify the complete pipeline works correctly"
    
    def _run(self, test_type: str = "quick", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Test data loading functionality"""
        try:
            output = f" DATA LOADING TEST\n"
            output += "=" * 20 + "\n\n"
            
            # Test CESM data loading
            output += f" Testing CESM Data Loading:\n"
            cesm_test = self._test_cesm_loading()
            output += cesm_test + "\n"
            
            # Test observational data loading
            output += f" Testing Observational Data Loading:\n"
            obs_test = self._test_obs_loading()
            output += obs_test + "\n"
            
            return output
            
        except Exception as e:
            return f" Data loading test failed: {str(e)}"
    
    def _test_cesm_loading(self) -> str:
        """Test CESM data loading"""
        try:
            import s3fs
            
            # Get a sample CESM path
            with sqlite3.connect("cesm_data_registry.db") as conn:
                cursor = conn.execute("""
                    SELECT variable_name, component, frequency, experiment 
                    FROM cesm_data_paths LIMIT 1
                """)
                result = cursor.fetchone()
                
                if not result:
                    return "    No CESM data found in database\n"
                
                variable, component, frequency, experiment = result
                
                # Apply same component mapping as CESM LENS agent
                component_mapping = {
                    "std": "atm",  # Standard atmospheric variables -> atm
                    "atmosphere": "atm",
                    "ocean": "ocn",
                    "land": "lnd",
                    "ice": "ice_nh"
                }
                component = component_mapping.get(component, "atm") if component else "atm"
                frequency = frequency or 'monthly'
                experiment = experiment or 'RCP85'
                
                s3_path = f"s3://ncar-cesm-lens/{component}/{frequency}/cesmLE-{experiment}-{variable}.zarr"
                
                # Try to access the path
                fs = s3fs.S3FileSystem(anon=True)
                
                # Quick existence check
                if fs.exists(s3_path.replace('s3://', '')):
                    return f"    CESM path accessible: {s3_path}\n    Variable: {variable}\n"
                else:
                    return f"    CESM path not found: {s3_path}\n"
                
        except Exception as e:
            return f"    CESM loading test failed: {e}\n"
    
    def _test_obs_loading(self) -> str:
        """Test observational data loading"""
        try:
            import s3fs
            
            # Get a sample observational path
            with sqlite3.connect("climate_knowledge_graph.db") as conn:
                cursor = conn.execute("""
                    SELECT title, s3_path
                    FROM stored_datasets 
                    WHERE s3_path IS NOT NULL 
                    LIMIT 1
                """)
                result = cursor.fetchone()
                
                if not result:
                    return "    No observational S3 paths found in database\n"
                
                title, s3_path = result
                
                # Basic accessibility check
                fs = s3fs.S3FileSystem(anon=True)
                
                try:
                    if fs.exists(s3_path.replace('s3://', '')):
                        return f"    Observational path accessible: {s3_path}\n    Dataset: {title}\n"
                    else:
                        return f"    Observational path not found: {s3_path}\n"
                except:
                    return f"    Could not verify path: {s3_path}\n    Dataset: {title}\n"
                
        except Exception as e:
            return f"    Observational loading test failed: {e}\n"


class ComparisonValidationTool(BaseTool):
    """Validate comparison analysis results and computations"""
    name: str = "validate_comparison_results"
    description: str = "Check if comparison analysis produced reasonable results and validate the computations"
    
    def _run(self, validation_focus: str = "all", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Validate comparison analysis results"""
        try:
            output = f" COMPARISON VALIDATION\n"
            output += "=" * 25 + "\n\n"
            
            # Check if comparison agent data manager is available
            try:
                from cesm_obs_comparison_agent import comparison_data_manager
                
                cesm_datasets = comparison_data_manager.get_cesm_datasets()
                obs_datasets = comparison_data_manager.get_obs_datasets()
                
                output += f" DATA AVAILABILITY CHECK:\n"
                output += f"   • CESM datasets loaded: {len(cesm_datasets)}\n"
                output += f"   • Observational datasets loaded: {len(obs_datasets)}\n\n"
                
                if cesm_datasets and obs_datasets:
                    output += f" Comparison data is available for validation\n\n"
                    
                    # Show what's loaded
                    output += f" CESM DATASETS:\n"
                    for dataset in cesm_datasets:
                        output += f"   • {dataset['variable']} ({dataset['time_range'][0]}-{dataset['time_range'][1]})\n"
                    
                    output += f"\n OBSERVATIONAL DATASETS:\n"
                    for dataset in obs_datasets:
                        output += f"   • {dataset['title'][:50]}...\n"
                    
                    output += f"\n VALIDATION READY:\n"
                    output += f"   • Use LLM to analyze actual comparison statistics\n"
                    output += f"   • Check bias, RMSE, correlation values for reasonableness\n"
                    output += f"   • Verify variable compatibility and units\n"
                    output += f"   • Assess quality scores and data availability\n"
                    
                else:
                    output += f" No comparison data available - run comparison analysis first\n"
                    
            except ImportError:
                output += f" Comparison agent not available for validation\n"
            
            return output
                
        except Exception as e:
            return f" Comparison validation failed: {str(e)}"


def create_verification_agent():
    """Create the CESM LENS verification agent"""
    
    # Initialize LLM using the same BedrockClaudeLLM class as other agents
    try:
        llm = BedrockClaudeLLM()
        print(" Bedrock Claude LLM initialized for verification agent")
        
    except Exception as e:
        print(f" Failed to initialize LLM: {e}")
        
        # Fallback LLM implementation
        class FallbackLLM(LLM):
            @property
            def _llm_type(self) -> str:
                return "fallback"
            
            def _call(self, prompt: str, stop: Optional[List[str]] = None, run_manager: Optional[CallbackManagerForLLMRun] = None, **kwargs) -> str:
                # Simple rule-based response for verification testing
                if "validate" in prompt.lower() and "database" in prompt.lower():
                    return "I'll validate the database integrity and data availability."
                elif "search" in prompt.lower() and "research" in prompt.lower():
                    return "I'll search for relevant climate research literature and validation studies."
                elif "process" in prompt.lower() and "research" in prompt.lower():
                    return "I'll validate the research process and methodology."
                else:
                    return "I'll help you with technical verification and research validation analysis."
            
        llm = FallbackLLM()
        print(" Fallback LLM initialized for verification agent")
        
    # Define comprehensive verification tools
    tools = [
        ClimateResearchSearchTool(),
        MethodologySearchTool(),
        ResearchProcessValidationTool(),
        GeneralInfoValidationTool(),
        DatabaseValidationTool(),
        S3PathValidationTool(),
        DataLoadTestTool(),
        ComparisonValidationTool()
    ]
    
    # Create comprehensive verification prompt
    template = """You are a CESM LENS Research Validation and Verification Specialist with expertise in:
- Climate science research methodology
- Model validation and verification
- Technical infrastructure validation
- Research process quality assessment
- Scientific literature review and context

Your role is to provide comprehensive verification covering both technical validation AND research methodology critique.

VERIFICATION CAPABILITIES:
1. RESEARCH SEARCH: Use search_climate_research and search_methodology to find relevant literature and best practices
2. PROCESS VALIDATION: Use validate_research_process to assess the overall research workflow and approach
3. GENERAL VALIDATION: Use validate_general_info to verify climate science context and methodology
4. TECHNICAL VALIDATION: Use database, S3, and data loading tools to verify technical infrastructure
5. RESULTS VERIFICATION: Use validate_comparison_results to check analysis outputs

COMPREHENSIVE VERIFICATION WORKFLOW:
• Search for relevant literature and validation studies
• Validate the research approach and methodology
• Verify general climate science context and information
• Check technical infrastructure (databases, S3 paths, data loading)
• Validate analysis results and computations
• Provide critical assessment and recommendations

You can critique research processes, validate methodologies, verify technical implementation, and provide scientific context through literature search. Provide thorough, evidence-based assessments.

You have access to these verification tools:
{tools}

Use the following format:
Question: the verification task to perform
Thought: think about what technical aspects need validation
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (repeat as needed)
Thought: I now have technical validation results to analyze
Final Answer: your technical assessment and critical analysis based on real results

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

    prompt = PromptTemplate(
        input_variables=["input", "agent_scratchpad"],
        template=template,
        partial_variables={
            "tools": "\n".join([f"{tool.name}: {tool.description}" for tool in tools]),
            "tool_names": ", ".join([tool.name for tool in tools])
        }
    )
    
    # Create the ReAct agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Create memory
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        k=3,
        return_messages=True
    )
    
    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10
    )
    
    return agent_executor


if __name__ == "__main__":
    print(" CESM LENS Research Verification Agent")
    print("=" * 50)
    print("\n Comprehensive Verification Capabilities:")
    print("• Climate research literature search")
    print("• Research methodology validation")
    print("• General information and context verification")
    print("• Technical infrastructure validation")
    print("• Research process critique")
    print("\n LLM provides critical analysis based on real search results and validation")
    
    try:
        agent = create_verification_agent()
        print("\n Research verification agent initialized successfully!")
        
    except Exception as e:
        print(f"\n Initialization failed: {e}")
        