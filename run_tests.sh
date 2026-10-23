#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m pip install -r requirements-dev.txt
mkdir -p reports
python3 -m pytest --cov=log_analyzer --cov-branch --cov-report=term-missing --cov-report=html:reports/coverage --html=reports/tests.html --self-contained-html
