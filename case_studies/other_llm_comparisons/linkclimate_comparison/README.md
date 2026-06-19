# AutoClimDS KG vs LinkClimate KG: Knowledge Graph Comparison

For the full comparison with complete schema details, node/edge type listings, and task-based evaluation, see the paper:

**AutoClimDS**: [https://arxiv.org/abs/XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX)

## Citation

```bibtex
@article{wu2022linkclimate,
  author = {Wu, J. and Orlandi, F. and O'Sullivan, D. and Dev, S.},
  title = {{LinkClimate: An interoperable knowledge graph platform for climate data}},
  journal = {Computers \& Geosciences},
  volume = {169},
  pages = {105215},
  year = {2022},
  doi = {10.1016/j.cageo.2022.105215},
  url = {https://www.sciencedirect.com/science/article/pii/S0098300422001649},
}
```

- **Paper**: https://www.sciencedirect.com/science/article/pii/S0098300422001649
- **ArXiv**: https://arxiv.org/abs/2210.16050
- **GitHub**: https://github.com/futaoo/LinkClimate
- **SPARQL Endpoint**: http://jresearch.ucd.ie/kg/ (offline as of 2025)

---

## KG vs KG Summary

| Dimension | AutoClimDS KG | LinkClimate KG |
|---|---|---|
| **Graph model** | Labeled property graph (OpenCypher) | RDF triple store (SPARQL) |
| **Database** | AWS Neptune Analytics (serverless) | Apache Fuseki (UCD server, offline) |
| **Scale** | ~1.48M nodes, ~5.8M edges | ~thousands of nodes |
| **Schema complexity** | 42 node types, 39 edge types | ~5 RDF classes, ~10 predicates |
| **Data sources** | NASA CMR + CMIP6 + NOAA OneStop + ERA5 | NOAA CDO + OpenStreetMap + Wikidata |
| **Datasets indexed** | ~208,000 (106K observational + 102K simulation) | IE/UK NOAA CDO daily summaries |
| **Geographic scope** | Global (258 location boundaries) | Ireland & UK |
| **Variable coverage** | 2,308 CESM variables + thousands observed | ~5 weather variables (TMAX, TMIN, PRCP, SNOW, AWND) |
| **Semantic search** | 384-dim vector embeddings + HNSW index | None |
| **Procedural knowledge** | Yes (access URLs with downloadability weights, variable mappings) | No (metadata only) |
| **Agent-ready** | Yes (designed for LLM agent consumption) | No (designed for human SPARQL queries) |
| **Federated query** | No (centralized) | Yes (SPARQL federation to Wikidata) |

### Key Structural Difference

AutoClimDS encodes **procedural reasoning paths** — not just what data exists, but how to access, download, and use it (`Link` nodes with downloadability weights, `CESMVariable` → `similarCESMVariable` fallback edges, `ProcessingLevel` nodes). LinkClimate encodes **static metadata relationships** for human-driven SPARQL exploration (stations → observations → values, with OSM/Wikidata entity linking).
