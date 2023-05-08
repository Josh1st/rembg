#!/bin/sh
cd /home/josh/rembg
source env/bin/activate
export U2NET_HOME="./.u2net"
export FLASK_APP=rembg
export ALLOWED_ORIGIN="https://big-byte-solutions.co.za"

pip install -r requirements.txt

python env/lib/python3.10/site-packages/functions_framework/__main__.py --target rembg --port=8080