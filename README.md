this is a simple hosted function that uses rembg to remove the background of an image

create a virtual environment

then here are some of the commands to run it
source env/bin/activate
export U2NET_HOME="./.u2net"
export FLASK_APP=rembg
export ALLOWED_ORIGIN="https://example.com"

pip install -r requirements.txt

python env/lib/python3.10/site-packages/functions_framework/__main__.py --target rembg --port=8080
