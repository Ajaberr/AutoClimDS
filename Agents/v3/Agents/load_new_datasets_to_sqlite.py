#!/usr/bin/env python3
"""
Load FloodNet, FloodSimBench, and MRMS datasets into the local SQLite
knowledge graph (climate_knowledge_graph.db) so the Streamlit app can
query them immediately without waiting for a Neptune bulk load.
"""

import json
import sqlite3
import os
from datetime import datetime
from pathlib import Path

DB_PATH = "climate_knowledge_graph.db"

NEW_DATASET_FILES = {
    "FloodNet":       "../FloodNetData/floodnet_json/floodnet_data.json",
    "FloodSimBench":  "../FloodSimBenchData/floodsimbench_json/floodsimbench_data.json",
    "MRMS":           "../MRMSData/mrms_json/mrms_data.json",
}


def insert_datasets(conn: sqlite3.Connection, source_name: str, kg_data: dict) -> int:
    cur = conn.cursor()
    datasets = kg_data.get("Dataset", [])
    inserted = 0

    for ds in datasets:
        dataset_id = f"dataset_{ds.get('dataset_id', ds.get('short_name', ''))}"

        # Build a clean properties blob matching the existing schema
        props = {k: v for k, v in ds.items()
                 if k not in ("links",)}
        props["source"] = source_name

        # Infer relationship types from what fields are present
        rel_types = []
        if ds.get("science_keywords") or props.get("science_keywords"):
            rel_types.append("hasScienceKeyword")
        if ds.get("organizations"):
            rel_types.append("hasOrganization")
        if ds.get("platforms"):
            rel_types.append("hasPlatform")
        if ds.get("time_start") or ds.get("time_end"):
            rel_types.append("hasTemporalExtent")
        if ds.get("boxes") or ds.get("points"):
            rel_types.append("hasLocation")
        if ds.get("links"):
            rel_types.append("hasLink")

        links = ds.get("links", [])

        cur.execute("""
            INSERT OR REPLACE INTO stored_datasets
                (dataset_id, title, short_name, dataset_properties, dataset_labels,
                 total_relationships, relationship_types, links, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dataset_id,
            ds.get("title", ""),
            ds.get("short_name", ""),
            json.dumps(props),
            json.dumps(["Dataset"]),
            len(rel_types),
            json.dumps(rel_types),
            json.dumps(links),
            datetime.utcnow().isoformat(),
            datetime.utcnow().isoformat(),
        ))
        inserted += 1

    conn.commit()
    return inserted


def main():
    script_dir = Path(__file__).parent
    db_path = script_dir / DB_PATH

    if not db_path.exists():
        print(f"ERROR: database not found at {db_path}")
        return

    conn = sqlite3.connect(str(db_path))

    total = 0
    for source_name, rel_path in NEW_DATASET_FILES.items():
        json_path = (script_dir / rel_path).resolve()

        if not json_path.exists():
            print(f"SKIP {source_name}: file not found at {json_path}")
            continue

        with open(json_path, "r", encoding="utf-8") as f:
            kg_data = json.load(f)

        n = insert_datasets(conn, source_name, kg_data)
        print(f"Inserted {n:>5} datasets  [{source_name}]")
        total += n

    conn.close()
    print(f"\nDone. Total inserted: {total} datasets into {db_path}")
    print("Restart the Streamlit app and query again to verify.")


if __name__ == "__main__":
    main()
