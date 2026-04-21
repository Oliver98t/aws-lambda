#!/bin/bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r lambda_src/dev_env_requirements.txt
