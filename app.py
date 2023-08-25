from flask import Flask, render_template, request, jsonify, send_file, Response
import cv2
import torch
import numpy as np
from util import extract, plotting, post_process, image_pre
import easyocr
from datetime import datetime
import base64
import pytz

# Replace 'Asia/Phnom_Penh' with the desired time zone
time_zone = pytz.timezone('Asia/Phnom_Penh')

# check if GPU is available
is_gpu = torch.cuda.is_available()
print('GPU:', is_gpu)

reader = easyocr.Reader(['en'], gpu = is_gpu)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
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
        cv2.imwrite('plate.jpg', plate)

        place, bbox = extract.get_info(plate)

        pl_img = plate.copy()
        if len(bbox) >= 4:
            cv2.rectangle(pl_img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0,255,0), 2)

        cv2.imwrite('place_det.jpg', pl_img)
        

        serials = extract.roi(plate, 1)

        # set default to image for do ocr
        img_for_ocr = plate
        if len(serials) > 0:
            serials = serials[0]
            a, b, a1, b1 = serials

            img_for_ocr = plate[b:b1, a:a1].copy()
        else:
            if len(bbox) > 0:
                img_for_ocr = cv2.rectangle(plate, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255,255,255), -1)
        
        origin_ocr = reader.readtext(img_for_ocr)

        label_conf = [{"label": t[-2], "conf": t[-1]} for t in origin_ocr]

        

        preprocess_img = image_pre.img_shapen(image_pre.pre_process(img_for_ocr))

        # set default serial value and its confident score
        serial_val = ''
        conf = 0

        read_text = reader.readtext(preprocess_img)
        for t in read_text:
            label_conf.append({"label": t[-2], "conf": t[-1]})
        

        for i in label_conf:
            if len(i['label']) >= 6 and i['conf'] > conf:
                serial_val = post_process.char_map(i['label'], place)
                conf = i['conf']

        image = plotting.plotting(image, r, place + ' ' + serial_val + ' ' + f'{conf:.3f}')
        print(label_conf)
        result.append({
            "plate_roi": r,
            "plate_name": place,
            "serial_value": serial_val,
            "conf": conf,
            "datetime": str(datetime.now(time_zone))
        })

    # save the figure
    cv2.imwrite('image.jpg', image)

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
    return render_template('stream.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug= True)