#!/bin/sh
cd /home/josh/rembg
source env/bin/activate
export U2NET_HOME="./.u2net"
export FLASK_APP=rembg

pip install -r requirements.txt

# functions-framework --target rembg --debug --port=8080
python env/lib/python3.10/site-packages/functions_framework/__main__.py --target rembg --debug --port=8080