#!/bin/sh
# change this to fit your needs
cd /home/$USER/rembg
source env/bin/activate
export U2NET_HOME="./.u2net"
export FLASK_APP=rembg
export ALLOWED_ORIGIN="https://example.com"

pip install -r requirements.txt

python env/lib/python3.10/site-packages/functions_framework/__main__.py --target rembg --port=8080