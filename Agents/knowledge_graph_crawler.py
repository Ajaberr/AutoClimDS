
import requests
import json
import time
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("crawler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ClimateGraphCrawler:
    """
    A robust crawler to harvest metadata from major climate archives
    and format them for Knowledge Graph ingestion.
    """
    
    def __init__(self, output_file="raw_graph_data.jsonl"):
        self.output_file = output_file
        # Clear previous run
        if os.path.exists(output_file):
            os.remove(output_file)
            
    def _save_record(self, source, record_type, data):
        """Append a record to the JSONL file."""
        entry = {
            "source": source,
            "type": record_type,
            "crawled_at": datetime.utcnow().isoformat(),
            "data": data
        }
        with open(self.output_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def crawl_cmip6_esgf(self, limit=50):
        """
        Crawls the Earth System Grid Federation (ESGF) for CMIP6 metadata.
        Handles pagination to fetch multiple pages of results.
        """
        base_url = "https://esgf-node.llnl.gov/esg-search/search"
        offset = 0
        batch_size = 10 # Small batch for demo, usually 100 or 1000
        total_fetched = 0
        
        logger.info(f"Starting CMIP6 Crawl (Target: {limit} records)...")
        
        while total_fetched < limit:
            params = {
                "project": "CMIP6",
                "experiment_id": "ssp585",  # Focus on one experiment for demo
                "latest": "true",
                "distrib": "false",         # Only search local node for speed
                "format": "application/solr+json",
                "limit": batch_size,
                "offset": offset
            }
            
            try:
                response = requests.get(base_url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                docs = data.get("response", {}).get("docs", [])
                
                if not docs:
                    logger.info("No more CMIP6 records found.")
                    break
                    
                for doc in docs:
                    # Construct valid graph properties
                    node_data = {
                        "id": doc.get("id"),
                        "model": doc.get("source_id"),
                        "institution": doc.get("institution_id"),
                        "variable": doc.get("variable_id"),
                        "grid": doc.get("grid_label"),
                        "resolution": doc.get("nominal_resolution")
                    }
                    self._save_record("CMIP6", "Dataset", node_data)
                    total_fetched += 1
                    if total_fetched >= limit:
                        break
                        
                logger.info(f"  Fetched {len(docs)} CMIP6 records (Total: {total_fetched})...")
                offset += len(docs)
                time.sleep(1) # Be polite to the API
                
            except Exception as e:
                logger.error(f"Error crawling CMIP6: {e}")
                time.sleep(5) # Backoff on error

    def crawl_nasa_cmr(self, keywords, limit=50):
        """
        Crawls NASA's Common Metadata Repository using newer pagination methods.
        """
        base_url = "https://cmr.earthdata.nasa.gov/search/collections.json"
        page_num = 1
        page_size = 10
        total_fetched = 0
        
        logger.info(f"Starting NASA CMR Crawl for '{keywords}' (Target: {limit} records)...")
        
        while total_fetched < limit:
            params = {
                "keyword": keywords,
                "page_size": page_size,
                "page_num": page_num
            }
            
            try:
                response = requests.get(base_url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                entries = data.get("feed", {}).get("entry", [])
                
                if not entries:
                    logger.info("No more NASA records found.")
                    break
                    
                for entry in entries:
                    # Safely extract platforms and instruments handling both dict and string formats
                    platforms = []
                    for p in entry.get("platforms", []):
                        if isinstance(p, dict):
                            platforms.append(p.get("short_name"))
                        elif isinstance(p, str):
                            platforms.append(p)
                            
                    instruments = []
                    for i in entry.get("instruments", []):
                        if isinstance(i, dict):
                            instruments.append(i.get("short_name"))
                        elif isinstance(i, str):
                            instruments.append(i)

                    # Extract valuable graph fields
                    node_data = {
                        "concept_id": entry.get("id"),
                        "title": entry.get("title"),
                        "short_name": entry.get("short_name"),
                        "version": entry.get("version_id"),
                        "updated": entry.get("updated"),
                        "processing_level": entry.get("processing_level_id"),
                        "platforms": platforms,
                        "instruments": instruments
                    }
                    self._save_record("NASA_CMR", "Collection", node_data)
                    total_fetched += 1
                    if total_fetched >= limit:
                        break
                
                logger.info(f"  Fetched {len(entries)} NASA records (Total: {total_fetched})...")
                page_num += 1
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error crawling NASA CMR: {e}")
                break

if __name__ == "__main__":
    crawler = ClimateGraphCrawler()
    
    # 1. Crawl CMIP6 Models
    crawler.crawl_cmip6_esgf(limit=10)
    
    # 2. Crawl NASA Satellite Data (Precipitation)
    crawler.crawl_nasa_cmr(keywords="precipitation", limit=10)
    
    print("\n" + "="*50)
    print(f"Crawl Complete! Data saved to: {crawler.output_file}")
    print("Sample of harvested data:")
    print("="*50)
    
    # Show first few lines of output
    if os.path.exists(crawler.output_file):
        with open(crawler.output_file, 'r') as f:
            for i, line in enumerate(f):
                if i < 3:
                   print(line.strip())
