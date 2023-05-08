import io
import base64
import PIL
from PIL import Image
from rembg import remove
import functions_framework
import logging
import sys
import os

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
        500:
            failed to read the size of all the uploaded files
        423:
            total upload size too big
            upload less images or smaller images
    """


    # Set the cors headers to the ALLOWED_ORIGIN env variable or to "*"
    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': os.environ.get('ALLOWED_ORIGIN', '*'),
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': os.environ.get('ALLOWED_ORIGIN', '*')
    }

    
    # check to see that all uploaded files combined are smaller than 30mb
    size = 0
    try:
        for file in request.files.getlist('files[]'):
            
            blob = file.read()
            size = size + len(blob)
    except Exception as e:
        logging.error(e)
        return ("Failed to read files", 500, headers)

    size = size / 1000000
    logging.info(f"size: {size}")

    if size > 30:
        return ("Upload size too large", 418, headers)

    
    images = []

    # loop through each uploaded file
    for file in request.files.getlist('files[]'):

        # check to see if the file is an image
        if not is_image_file(file):
            images.append({
                    'name': file.filename,
                    'image': None,
                    'message': 'File is not a valid image',
                })
            continue

        # convert file to pillow object
        img = Image.open(file.stream)
        try:
            # run rembg on the pillow object and get a pillow object back
            result = remove(img, alpha_matting=True)

            # convert pillow object to base64 string
            with io.BytesIO() as f:
                result.save(f, format='PNG')
                f.seek(0)
                # append the base64 string to the images array plus the
                # file name and a success message
                images.append({
                        'name': file.filename,
                        'image': base64.b64encode(f.read()).decode('utf-8'),
                        'message': 'Procesed successfully',
                    })
                
        except Exception as e:
            logging.error(e)
            # add an error message to the image object if
            # something goes wrong
            images.append({
                    'name': file.filename,
                    'image': None,
                    'message': 'Failed to process image',
                })

    logging.info(str(len(images)) + ' images proccesed')
    return ({'images': images}, 200, headers)
