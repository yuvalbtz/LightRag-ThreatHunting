#!/bin/bash
# Activate conda environment and start the app

source /opt/conda/etc/profile.d/conda.sh
conda activate lightrag_env

# Start the server with stdout/stderr forwarded
exec python api.py
