#!/bin/bash
# entrypoint.sh

set -e

echo "Installing JupyterLab and Notebook..."
pip install jupyterlab notebook

echo "Checking database..."
if [ -f /srv/jupyterhub/jupyterhub.sqlite ]; then
    echo "Database exists. Upgrading if needed..."
    jupyterhub upgrade-db -f /srv/jupyterhub/jupyterhub_config.py || true
else
    echo "No database found. Will create on first run."
fi

echo "Starting JupyterHub..."
exec jupyterhub -f /srv/jupyterhub/jupyterhub_config.py