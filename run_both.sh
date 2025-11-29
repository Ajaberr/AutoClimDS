#!/bin/bash

# Script to run both predict_cmr.py and json_to_csvs.py from parent directory
# Usage: bash run_both.sh

echo "========================================"
echo "🚀 Running Climate KG Pipeline"
echo "========================================"

# Get the parent directory (where this script is located)
PARENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📁 Parent directory: $PARENT_DIR"

# Set up error handling
set -e

echo ""
echo "========================================"
echo "🔍 Step 1: Generate ML Predictions"
echo "========================================"

# Navigate to ML Model directory and run predict_cmr.py
cd "$PARENT_DIR/ML Model"
echo "📁 Current directory: $(pwd)"
echo "🧠 Running ML predictions..."

if python3 predict_cmr.py; then
    echo "✅ ML predictions completed successfully"
else
    echo "❌ ML predictions failed with exit code $?"
    exit 1
fi

echo ""
echo "========================================"
echo "🗺️  Step 2: Generate Knowledge Graph"
echo "========================================"

# Navigate to KGNeptune directory and run json_to_csvs.py
cd "$PARENT_DIR/KGNeptune"
echo "📁 Current directory: $(pwd)"
echo "🗺️  Running knowledge graph generation..."

if python3 json_to_csvs.py; then
    echo "✅ Knowledge graph generation completed successfully"
else
    echo "❌ Knowledge graph generation failed with exit code $?"
    exit 1
fi

echo ""
echo "========================================"
echo "🎉 Pipeline Completed Successfully!"
echo "========================================"
echo "📊 Check the output files:"
echo "   - ML predictions: $PARENT_DIR/ML Model/predictions/"
echo "   - Knowledge graph: $PARENT_DIR/KGNeptune/neptune_csvs/"
echo "========================================"