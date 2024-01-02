from flask import Flask, render_template, request
import cv2
import numpy as np
from util import extract, plotting
from datetime import datetime
import base64
import subprocess
import time
from util.ocr import processs_OCR

process = None

app = Flask(__name__)
app.app_context()

@app.route('/', methods=['GET'])
def home():
    global process
    if process:
        process.kill()
        process = None
    return render_template('index.html')


@app.route('/image', methods=['GET'])
def start_img():
    return render_template('upload.html')

@app.route('/video', methods=['GET'])
def start_vid():
    return render_template('video.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
         return "No file found", 400
      
    file = request.files['file']
    image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)

    # Process the image
    roi = extract.roi(image, 0)
    result = []

    for r in roi:
        x, y, x1, y1 = r
        plate = image[y:y1, x:x1].copy()
        # cv2.imwrite('plate.jpg', plate)
        data = processs_OCR(plate, r)
        image = plotting.plotting(image, r, data['plate_name'] + ' ' + data['serial_value'])

        result.append(data)

    # Convert the CV2 image to a binary format (PNG or JPEG)
    _, buffer = cv2.imencode('.jpg', image)
    # Convert the binary image data to base64 encoding
    base64_image = base64.b64encode(buffer).decode('utf-8')
    end_result = {
        'filename': file.filename,
        'prediction': result
    }

    return render_template('result.html',base64_image=base64_image, **end_result)


@app.route('/camera')
def cam():
    global process
    try:
        process = subprocess.Popen(['python', 'cam_test.py'])
    except:
        print("Error Running Script ot run camera")

    time.sleep(5)
    return render_template('stream.html')

        

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug= True)
