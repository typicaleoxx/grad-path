# Make sure the script is LF and not CRLF. Otherwise, it will fail to run in Linux environment.

#!/bin/sh
set -e

echo "===== Starting pipeline ====="

python src/load_data.py

echo "===== grad_dist ====="

python src/grad_dist.py

echo "===== prerequisite_checker ====="

python src/prerequisite_checker.py

echo "===== demand_report ====="

python src/demand_report.py

echo "===== Files created ====="

ls -R data/intermediate
ls -R outputs

echo "===== Starting Streamlit ====="

exec streamlit run app.py \
    --server.address=0.0.0.0 \
    --server.port=8501