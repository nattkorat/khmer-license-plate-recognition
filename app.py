from flask import Flask, render_template, request, jsonify, send_file
import cv2
import numpy as np
from util import extract, plotting
import easyocr
from datetime import datetime

custom_conf = r'--oem 3 --psm 6'

reader = easyocr.Reader(['en'], gpu=True, verbose= False)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def start():
    return render_template('upload.html')


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


        plate = image[y:y1, x:x1]
        place = extract.get_info(plate)

        image = plotting.plotting(image, r, place)
        

        serials = extract.roi(plate, 1)
        if len(serials) > 0: 
            serials = serials[0]
            a, b, a1, b1 = serials
            # cv2.imwrite('image.jpg', plate[b-5:b1+5, a-5:a1+5])
            info = reader.readtext(plate[b-5:b1+5, a-5:a1+5])

            serial_val = []
            
            for inf in info:
                if inf[-1] > 0.2:
                    serial_val.append(inf[1]) # get data from reader
                    serial_val.append(inf[2]) # get the conf score

                    # plot to the info to the image
                    image = plotting.plotting(image, r, place + ' ' + inf[1])

                print(inf)

            result.append({
                "plate_roi": r,
                "serial_roi": serials,
                "plate_name": place,
                "serail_value": serial_val,
                "datetime": datetime.now()
            })

    # save the figure
    cv2.imwrite('image.jpg', image)

    return jsonify({
        'filename': file.filename,
        'predicttion': result
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug= True)