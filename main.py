import io
import base64
import requests
import PIL
from PIL import Image
from rembg import remove
import functions_framework
import logging
import sys 

DEBUG = False
for arg in sys.argv:
    if arg == '--debug':
        print("DEBUG")
        DEBUG = True


def is_image_file(file):
    """Checks to see if a file is an image.
    
    Args:
        file: FileStorage object.

    Returns:
        True if the file is an image, False otherwise.

    Raises:
        TypeError: If a non FileStorage object is passed
    """
    
    if not file.__class__.__name__ == 'FileStorage':
        raise TypeError('is_image_file requires a FileStorage object')
    
    try:
        img = Image.open(file.stream)
        return True
    except PIL.UnidentifiedImageError as e:
        return False


@functions_framework.http
def rembg(request):
    """A functions_framework.http function that removes image backgrounds
    via post request

    Args:
        request
    
    Parameters:
        file objects named: files[]
            eg: from javascript form data: formData.append('files[]', file, file_Name)

    Raises:
        None: non image files will be ignored

    Respones:
        200:
            all valid images procesed. if an indiviudal image fails it will not
            effect the other images.
        423:
            total upload size too big
            upload less images or smaller images
    """

    # Set CORS headers for the main request
    # if DEBUG:
    #     headers = {
    #         'Access-Control-Allow-Origin': '*'
    #     }
    # else:
    #     headers = {
    #         # 'Access-Control-Allow-Origin': 'https://big-byte-solutions.co.za'
    #         'Access-Control-Allow-Origin': '*'
    #     }

    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    images = []
    messages = []
    size = 0

    try:
        for file in request.files.getlist('files[]'):
            
            blob = file.read()
            size = size + len(blob)
    except Exception as e:
        logging.error(e)
        client.report_exception()

    size = size / 1000000
    logging.info(f"size: {size}")

    if size > 30:
        return ("Upload size too large", 418, headers)

    logging.info(request.files.getlist('files[]'))
    print(request.files.getlist('files[]'))

    messages.append({'files': str(request.files.getlist('files[]'))})

    for file in request.files.getlist('files[]'):

        logging.info(file)
        print(file)
        messages.append(str(file))

        if not is_image_file(file):
            logging.warning(file.filename + " is not a valid image")
            print(file.filename + " is not a valid image")
            images.append({
                    'name': file.filename,
                    'image': None,
                    'message': 'File is not a valid image',
                })
            continue

        # convert file to pillow object
        img = Image.open(file.stream)
        try:
            result = remove(img, alpha_matting=True)

            # convert pillow object to base64 string
            with io.BytesIO() as f:
                result.save(f, format='PNG')
                f.seek(0)
                images.append({
                        'name': file.filename,
                        'image': base64.b64encode(f.read()).decode('utf-8'),
                        'message': 'Procesed successfully',
                    })
            messages.append('image procesed')
                
        except Exception as e:
            messages.append('image failed')
            messages.append(str(e))
            logging.error(e)
            print(e)
            images.append({
                    'name': file.filename,
                    'image': None,
                    'message': str(e),
                })
            if not DEBUG:
                from google.cloud import error_reporting
                client = error_reporting.Client()
                client.report_exception()

    logging.info(str(len(images)) + ' images proccesed')
    print(str(len(images)) + ' images proccesed')
    return ({'images': images, 'messages': messages}, 200, headers)


# gcloud functions deploy rembg --env-vars-file .env.yaml --runtime python310 --trigger-http --allow-unauthenticated --entry-point=rembg --memory=4096MB
# gcloud functions deploy rembg --env-vars-file .env.yaml --runtime python310 --trigger-http --allow-unauthenticated --entry-point=rembg --memory=4096MB --allow-unauthenticated
# gcloud functions deploy rembg --env-vars-file .env.yaml --runtime python310 --trigger-http --allow-unauthenticated --entry-point=rembg --memory="4 GiB" --allow-unauthenticated --gen2
# gcloud functions deploy rembg --env-vars-file .env.yaml --runtime python310 --trigger-http --allow-unauthenticated --entry-point=rembg --memory=4096MB
