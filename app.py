from flask import Flask, render_template, request, jsonify, send_file
import cv2
import numpy as np
from util import extract, plotting, post_process
import easyocr
from datetime import datetime
import base64


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


        plate = image[y:y1, x:x1].copy()
        place, bbox = extract.get_info(plate)

        if len(bbox) > 0:
            plate = cv2.rectangle(plate, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255,255,255), -1)

        image = plotting.plotting(image, r, place)
        

        serials = extract.roi(plate, 1)
        if len(serials) > 0: 
            serials = serials[0]
            a, b, a1, b1 = serials

            if len(bbox) > 0:
                # we need to consider the type of license plate (us type or europe type)
                if bbox[0] > a:
                    plate = cv2.rectangle(plate, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255,255,255), -1) # for three lines
                else:
                    plate = cv2.rectangle(plate, (bbox[0], 0), (bbox[2], y1), (255,255,255), -1) # for two lines

            # cv2.imwrite('image.jpg', plate[b-5:b1+5, a-5:a1+5])
            # info = reader.readtext(plate[b-5:b1+5, a-5:a1+5])

            info = reader.readtext(plate[0:b1, 0:a1])
            cv2.imwrite('serial.jpg', plate[0:b1, 0:a1])

            serial_val = []
            
            for inf in info:
                txt = post_process.remove_space_special_chars(inf[1]).upper()
                serial_val.append(txt) # get data from reader
                serial_val.append(inf[2]) # get the conf score

                # plot to the info to the image
                image = plotting.plotting(image, r, place + ' ' + txt)

                print(txt)

            result.append({
                "plate_roi": r,
                "serial_roi": serials,
                "plate_name": place,
                "serail_value": serial_val,
                "datetime": datetime.now()
            })

    # save the figure
    cv2.imwrite('image.jpg', image)

    # Convert the CV2 image to a binary format (PNG or JPEG)
    _, buffer = cv2.imencode('.jpg', image)

    # Convert the binary image data to base64 encoding
    base64_image = base64.b64encode(buffer).decode('utf-8')

    # return jsonify({
    #     'filename': file.filename,
    #     'predicttion': result
    # })

    end_result = {
        'filename': file.filename,
        'prediction': result
    }

    return render_template('result.html',base64_image=base64_image, **end_result)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug= True)