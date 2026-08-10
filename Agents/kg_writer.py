"""Write acquired data into Neptune Analytics KG.

Each write_* returns {"written": N, "skipped": M, "errors": [...]}.
Never raises.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import boto3
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

logger = logging.getLogger(__name__)

NEPTUNE_REGION = os.getenv("NEPTUNE_REGION", "us-east-2")
GRAPH_ID       = os.getenv("GRAPH_ID", "g-i89ayfy7d2")
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
KG_WRITE_DISABLED = os.getenv("KG_WRITE_DISABLED") == "1"

_embedding_model = None
try:
    from kg_connector import embedding_model as _embedding_model    # type: ignore
except Exception:
    try:
        from sentence_transformers import SentenceTransformer
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    except Exception as e:
        logger.warning(f"[kg_writer] embedding model unavailable: {e}")
        _embedding_model = None


def _embed(text: str) -> Optional[List[float]]:
    if _embedding_model is None or not text:
        return None
    try:
        return _embedding_model.encode(text).tolist()
    except Exception as e:
        logger.warning(f"[kg_writer] embedding failed: {e}")
        return None


_boto_session = None
def _get_boto_session():
    global _boto_session
    if _boto_session is None:
        _boto_session = boto3.Session()
    return _boto_session


def _execute_cypher(query: str) -> Dict[str, Any]:
    if KG_WRITE_DISABLED:
        return {}
    try:
        endpoint = f"https://{GRAPH_ID}.{NEPTUNE_REGION}.neptune-graph.amazonaws.com"
        url      = f"{endpoint}/openCypher"
        creds    = _get_boto_session().get_credentials()
        req      = AWSRequest(
            method="POST",
            url=url,
            data=json.dumps({"query": query}),
            headers={"Content-Type": "application/json"},
        )
        SigV4Auth(creds, "neptune-graph", NEPTUNE_REGION).add_auth(req)
        resp = requests.post(url, data=req.body, headers=dict(req.headers),
                             verify=True, timeout=30)
        if resp.status_code >= 400:
            logger.warning(f"[kg_writer] neptune {resp.status_code}: {resp.text[:300]}")
            return {}
        return resp.json()
    except Exception as e:
        logger.warning(f"[kg_writer] cypher failed: {e}")
        return {}


def _sq(s: Any) -> str:
    if s is None:
        return "''"
    if isinstance(s, (int, float)):
        return str(s)
    return "'" + str(s).replace("\\", "\\\\").replace("'", "\\'") + "'"


def _vec_literal(vec: Optional[List[float]]) -> str:
    if not vec:
        return "null"
    return "[" + ",".join(f"{v:.6f}" for v in vec) + "]"


def _canonical_id(*parts: Any) -> str:
    joined  = "_".join(str(p) for p in parts if p not in (None, ""))
    cleaned = re.sub(r"[^A-Za-z0-9_\-]+", "_", joined)[:80]
    digest  = hashlib.md5(joined.encode("utf-8")).hexdigest()[:8]
    return f"{cleaned}_{digest}"


def _write_dataset_with_relations(
    dataset_id:   str,
    title:        str,
    short_name:   str,
    data_center:  str,
    doi:          str = "",
    time_start:   Optional[str] = None,
    time_end:     Optional[str] = None,
    location:     Optional[Dict[str, Any]]  = None,
    variable:     Optional[str] = None,
    data_category: Optional[str] = None,
    extra_props:  Optional[Dict[str, Any]] = None,
) -> bool:
    props = {
        "dataset_id":  dataset_id,
        "title":       title[:500] if title else short_name,
        "short_name":  short_name,
        "data_center": data_center,
        "doi":         doi or "",
    }
    if time_start:
        props["time_start"] = time_start
    if time_end:
        props["time_end"] = time_end
    if extra_props:
        for k, v in extra_props.items():
            if v is None:
                continue
            props[k] = v

    set_lines = ",\n    ".join(f"d.{k} = {_sq(v)}" for k, v in props.items())
    cypher = f"""
    MERGE (d:Dataset {{dataset_id: {_sq(dataset_id)}}})
    ON CREATE SET
      {set_lines},
      d.ingested_at = {_sq(datetime.utcnow().isoformat())},
      d.ingestion_source = 'kg_writer'
    ON MATCH SET
      d.last_updated = {_sq(datetime.utcnow().isoformat())}
    RETURN d.dataset_id as id
    """
    result = _execute_cypher(cypher)
    if not result:
        return False

    if location and location.get("name"):
        loc_id  = _canonical_id("loc", data_center, location["name"])
        loc_vec = _embed(location["name"])
        lat     = location.get("latitude")
        lng     = location.get("longitude")
        loc_sets = [f"loc.name = {_sq(location['name'])}",
                    f"loc.source = {_sq(data_center)}"]
        if lat is not None:
            loc_sets.append(f"loc.latitude = {lat}")
        if lng is not None:
            loc_sets.append(f"loc.longitude = {lng}")
        _execute_cypher(f"""
        MERGE (loc:Location {{location_id: {_sq(loc_id)}}})
        ON CREATE SET {', '.join(loc_sets)}
        WITH loc
        MATCH (d:Dataset {{dataset_id: {_sq(dataset_id)}}})
        MERGE (d)-[:hasLocation]->(loc)
        """)
        if loc_vec:
            _upsert_embedding("Location", "location_id", loc_id, loc_vec)

    if time_start or time_end:
        te_id = _canonical_id("te", dataset_id)
        # Neptune date() rejects ISO datetimes with millis; store date-only
        # (YYYY-MM-DD) to match Ayon's convention and let search_by_temporal_extent work.
        _execute_cypher(f"""
        MERGE (te:TemporalExtent {{te_id: {_sq(te_id)}}})
        ON CREATE SET
          te.start_time = {_sq(_to_date(time_start))},
          te.end_time = {_sq(_to_date(time_end))}
        WITH te
        MATCH (d:Dataset {{dataset_id: {_sq(dataset_id)}}})
        MERGE (d)-[:hasTemporalExtent]->(te)
        """)

    if data_category:
        cat_id  = _canonical_id("cat", data_category)
        cat_vec = _embed(data_category)
        _execute_cypher(f"""
        MERGE (c:DataCategory {{category_id: {_sq(cat_id)}}})
        ON CREATE SET c.summary = {_sq(data_category)}
        WITH c
        MATCH (d:Dataset {{dataset_id: {_sq(dataset_id)}}})
        MERGE (d)-[:hasDataCategory]->(c)
        """)
        if cat_vec:
            _upsert_embedding("DataCategory", "category_id", cat_id, cat_vec)

    if variable:
        var_id  = _canonical_id("var", variable)
        var_vec = _embed(variable)
        _execute_cypher(f"""
        MERGE (v:Variable {{variable_id: {_sq(var_id)}}})
        ON CREATE SET
          v.name = {_sq(variable)},
          v.long_name = {_sq(variable)}
        WITH v
        MATCH (d:Dataset {{dataset_id: {_sq(dataset_id)}}})
        MERGE (d)-[:hasVariable]->(v)
        """)
        if var_vec:
            _upsert_embedding("Variable", "variable_id", var_id, var_vec)

    return True


# Neptune Analytics requires vector embeddings to go through this API,
# not via a regular SET n.embedding = [...] clause.
def _upsert_embedding(label: str, id_prop: str, node_id: str,
                      vec: List[float]) -> None:
    vec_lit = _vec_literal(vec)
    if vec_lit == "null":
        return
    _execute_cypher(f"""
    MATCH (n:{label} {{{id_prop}: {_sq(node_id)}}})
    WITH n
    CALL neptune.algo.vectors.upsert(n, {vec_lit}) YIELD node
    RETURN node.{id_prop} as id
    """)


def write_floodnet_events(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    written, skipped, errors = 0, 0, []
    for ev in events or []:
        try:
            sensor_id  = ev.get("sensor_id") or ev.get("device_id") or ""
            sensor_nm  = ev.get("sensor_name") or ev.get("street_address") or sensor_id
            start_t    = ev.get("flood_start_time") or ev.get("start_time") or ""
            end_t      = ev.get("flood_end_time")   or ev.get("end_time")   or ""
            depth      = ev.get("max_depth_inches") or ev.get("max_depth") or ""
            lat        = _safe_float(ev.get("latitude") or ev.get("lat"))
            lng        = _safe_float(ev.get("longitude") or ev.get("lon") or ev.get("lng"))

            if not sensor_id or not start_t:
                skipped += 1
                continue

            dataset_id = _canonical_id("floodnet", sensor_id, start_t)
            title = f"Flood at {sensor_nm} on {start_t[:10]}"
            if depth:
                title += f" (max depth {depth} in)"

            ok = _write_dataset_with_relations(
                dataset_id   = dataset_id,
                title        = title,
                short_name   = f"FLOODNET_{sensor_id}",
                data_center  = "NYC_FloodNet",
                time_start   = start_t,
                time_end     = end_t,
                location     = {"name": sensor_nm, "latitude": lat, "longitude": lng},
                variable     = "flood_depth",
                data_category = "Urban Street Flooding",
                extra_props = {"max_depth_inches": _safe_float(depth), "sensor_id": sensor_id},
            )
            if ok:
                written += 1
            else:
                errors.append(f"cypher failed for {dataset_id}")
        except Exception as e:
            errors.append(str(e))
    logger.info(f"[kg_writer.floodnet] wrote={written} skipped={skipped} errors={len(errors)}")
    return {"written": written, "skipped": skipped, "errors": errors[:5]}


def write_mrms_product(product: str, file_url: str, timestamp: str = "",
                       size_mb: float = 0.0, category: str = "") -> Dict[str, Any]:
    if not product:
        return {"written": 0, "skipped": 1, "errors": ["product required"]}
    try:
        ts = timestamp or datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        dataset_id = _canonical_id("mrms", product, ts)
        category = category or _mrms_category(product)
        title = f"MRMS {product} at {ts}"
        ok = _write_dataset_with_relations(
            dataset_id   = dataset_id,
            title        = title,
            short_name   = f"MRMS_{product}",
            data_center  = "NOAA_MRMS",
            time_start   = _mrms_ts_to_iso(ts),
            time_end     = _mrms_ts_to_iso(ts),
            location     = {"name": "CONUS", "latitude": None, "longitude": None},
            variable     = product,
            data_category = category,
            extra_props  = {
                "mrms_product": product,
                "mrms_category": category,
                "mrms_file_url": file_url,
                "mrms_file_size_mb": size_mb,
                "mrms_grid_res_km": 1.0,
                "mrms_update_interval_min": 2,
                "mrms_coverage": "CONUS",
            },
        )
        return {"written": 1 if ok else 0, "skipped": 0,
                "errors": [] if ok else ["cypher failed"]}
    except Exception as e:
        return {"written": 0, "skipped": 0, "errors": [str(e)]}


# Records are aggregated by (complaint_type, area, month) so the KG gets one
# summary Dataset per bucket instead of millions of individual complaint nodes.
def write_311_complaints(records: List[Dict[str, Any]], city_key: str) -> Dict[str, Any]:
    if not records:
        return {"written": 0, "skipped": 0, "errors": []}

    city_key = (city_key or "nyc").lower()
    data_center = f"{city_key.upper()}_311"
    ct_field   = _city_311_complaint_field(city_key)
    loc_field  = _city_311_location_field(city_key)
    date_field = _city_311_date_field(city_key)

    buckets: Dict[str, Dict[str, Any]] = {}
    for r in records:
        ct  = (r.get(ct_field) or "Unknown").strip()
        loc = (r.get(loc_field) or "Unknown").strip()
        dt  = r.get(date_field) or ""
        month = dt[:7] if len(dt) >= 7 else "unknown"
        key = f"{ct}||{loc}||{month}"
        b = buckets.setdefault(key, {"ct": ct, "loc": loc, "month": month, "count": 0,
                                     "min_dt": dt, "max_dt": dt})
        b["count"] += 1
        if dt:
            if not b["min_dt"] or dt < b["min_dt"]:
                b["min_dt"] = dt
            if not b["max_dt"] or dt > b["max_dt"]:
                b["max_dt"] = dt

    written, errors = 0, []
    for key, b in buckets.items():
        try:
            dataset_id = _canonical_id("311", city_key, b["ct"], b["loc"], b["month"])
            title = f"311 {b['ct']} in {b['loc']} ({b['month']}) - {b['count']} complaints"
            ok = _write_dataset_with_relations(
                dataset_id   = dataset_id,
                title        = title,
                short_name   = f"311_{city_key.upper()}_{_slug(b['ct'])}",
                data_center  = data_center,
                time_start   = b["min_dt"],
                time_end     = b["max_dt"],
                location     = {"name": b["loc"], "latitude": None, "longitude": None},
                variable     = b["ct"],
                data_category = "311 Service Request",
                extra_props  = {
                    "complaint_type": b["ct"],
                    "borough_or_area": b["loc"],
                    "month": b["month"],
                    "complaint_count": b["count"],
                    "city": city_key,
                },
            )
            if ok:
                written += 1
            else:
                errors.append(f"cypher failed for {dataset_id}")
        except Exception as e:
            errors.append(str(e))
    logger.info(f"[kg_writer.311] city={city_key} buckets={len(buckets)} wrote={written}")
    return {"written": written, "skipped": 0, "errors": errors[:5]}


# Deduped by disasterNumber (one hurricane affects many counties in raw data).
def write_fema_disasters(records: List[Dict[str, Any]],
                         dataset_name: str = "DisasterDeclarationsSummaries") -> Dict[str, Any]:
    if not records:
        return {"written": 0, "skipped": 0, "errors": []}

    # Dedupe by disasterNumber
    seen: Dict[str, Dict[str, Any]] = {}
    for r in records:
        dn = str(r.get("disasterNumber") or r.get("DisasterNumber") or "")
        if not dn:
            continue
        if dn not in seen:
            seen[dn] = r

    written, errors = 0, []
    for dn, r in seen.items():
        try:
            incident   = r.get("incidentType")     or r.get("IncidentType")   or "Unknown"
            state      = r.get("state")            or r.get("stateCode")      or r.get("StateCode") or ""
            decl_date  = r.get("declarationDate")  or r.get("DeclarationDate") or ""
            end_date   = r.get("incidentEndDate")  or r.get("IncidentEndDate") or decl_date
            title_field= r.get("declarationTitle") or r.get("DeclarationTitle") or f"{incident} in {state}"

            dataset_id = _canonical_id("fema", dn)
            title = f"FEMA {dataset_name}: {title_field} (#{dn})"
            ok = _write_dataset_with_relations(
                dataset_id   = dataset_id,
                title        = title,
                short_name   = f"FEMA_{dn}",
                data_center  = "FEMA_Disaster",
                time_start   = decl_date,
                time_end     = end_date,
                location     = {"name": state, "latitude": None, "longitude": None},
                variable     = incident,
                data_category = "Disaster Declaration",
                extra_props  = {
                    "disaster_number": dn,
                    "incident_type": incident,
                    "state_code": state,
                    "declaration_type": r.get("declarationType") or r.get("DeclarationType") or "",
                    "fema_dataset": dataset_name,
                },
            )
            if ok:
                written += 1
            else:
                errors.append(f"cypher failed for {dataset_id}")
        except Exception as e:
            errors.append(str(e))
    logger.info(f"[kg_writer.fema] unique_disasters={len(seen)} wrote={written}")
    return {"written": written, "skipped": 0, "errors": errors[:5]}


def _city_311_complaint_field(city: str) -> str:
    return {"nyc": "complaint_type", "chicago": "sr_type",
            "sf": "service_name", "austin": "sr_type_desc"}.get(city, "complaint_type")

def _city_311_location_field(city: str) -> str:
    return {"nyc": "borough", "chicago": "community_area",
            "sf": "neighborhoods_analysis_boundaries", "austin": "council_district"}.get(city, "borough")

def _city_311_date_field(city: str) -> str:
    return {"nyc": "created_date", "chicago": "created_date",
            "sf": "requested_datetime", "austin": "created_date"}.get(city, "created_date")


def _mrms_category(product: str) -> str:
    p = (product or "").lower()
    if "qpe"       in p: return "Precipitation"
    if "reflect"   in p: return "Reflectivity"
    if "rotation"  in p or "shear" in p: return "Severe Weather"
    if "hail"      in p or "mesh"  in p: return "Hail"
    if "lightning" in p: return "Lightning"
    return "Radar / Precipitation"


def _mrms_ts_to_iso(ts: str) -> str:
    m = re.match(r"(\d{4})(\d{2})(\d{2})_?(\d{2})(\d{2})(\d{2})?", ts or "")
    if not m:
        return ""
    y, mo, d, hh, mm, ss = m.groups(default="00")
    return f"{y}-{mo}-{d}T{hh}:{mm}:{ss}Z"


def _safe_float(x: Any) -> Optional[float]:
    try:
        if x is None or x == "":
            return None
        return float(x)
    except Exception:
        return None


def _slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", (s or "").strip())[:40]


def _to_date(s: str) -> str:
    if not s:
        return ""
    m = re.match(r"(\d{4}-\d{2}-\d{2})", str(s))
    return m.group(1) if m else str(s)[:10]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(f"NEPTUNE_REGION={NEPTUNE_REGION}  GRAPH_ID={GRAPH_ID}")
    print(f"embedding: {'yes' if _embedding_model else 'no'}")
    r = write_floodnet_events([{
        "sensor_id": "SMOKE_TEST",
        "sensor_name": "Smoke Test Sensor",
        "flood_start_time": "2026-07-19T12:00:00",
        "flood_end_time":   "2026-07-19T15:00:00",
        "latitude": "40.7128",
        "longitude": "-74.0060",
        "max_depth_inches": "3.2",
    }])
    print(r)
