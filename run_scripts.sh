#!/bin/bash
cd "ML Model"
python3 predict_cmr.py
cd ..

cd "KGNeptune"
python3 json_to_csvs.py
cd ..

