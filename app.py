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
        # cv2.imwrite('plate.jpg', plate)

        place, bbox = extract.get_info(plate)

        pl_img = plate.copy()
        if len(bbox) >= 4:
            cv2.rectangle(pl_img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0,255,0), 2)

        # cv2.imwrite('place_det.jpg', pl_img)

        image = plotting.plotting(image, r, place)
        

        serials = extract.roi(plate, 1)
        if len(serials) > 0: 
            serials = serials[0]
            a, b, a1, b1 = serials

            # cv2.imwrite('serial.jpg', plate[b:b1, a:a1])

            orgin = reader.readtext(plate[b:b1, a:a1])

            or_txt = ''
            or_conf = 0
            for inf in orgin:
                print(inf)
                if inf[-1] >= 0.3:
                    or_conf += inf[-1]
                    or_txt = inf[1]

            pre_img = image_pre.pre_process(plate[b:b1, a:a1])
            sh_img = image_pre.img_shapen(pre_img)
            processed = reader.readtext(sh_img)

            pro_txt = ''
            pro_conf = 0

            for inf in processed:
                print(inf)
                if inf[-1] >= 0.3:
                    pro_txt += inf[1]
                    pro_conf = inf[-1]

            if or_conf > pro_conf:
                conf = or_conf
                serial_val = or_txt
            else:
                conf = pro_conf
                serial_val = pro_txt
            
            serial_val = post_process.char_map(serial_val, place) # apply post process method

            image = plotting.plotting(image, r, place + ' ' + serial_val)

            # info = reader.readtext(plate[0:b1, 0:a1])
            # cv2.imwrite(f'det_serial/{place}_{x}serial.jpg', sh_img)

            # serial_val = []

            # print(info)
            
            # for inf in info:
            #     txt = inf[-1]

            #     # clean text
            #     txt = post_process.char_map(txt, place) # need to apply type of license plate next time

            #     # plot to the info to the image
            #     image = plotting.plotting(image, r, place + ' ' + txt)

            #     serial_val.append(txt) # get data from reader

            #     # plot to the info to the image
            #     image = plotting.plotting(image, r, place + ' ' + txt)

            #     print(txt)
        else:
            if len(bbox) > 0:
                plate = cv2.rectangle(plate, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255,255,255), -1)
            
            orgin = reader.readtext(plate)

            or_txt = ''
            or_conf = 0
            for inf in orgin:
                print(inf)
                if inf[-1] >= 0.3:
                    or_conf += inf[-1]
                    or_txt = inf[1]

            pre_img = image_pre.pre_process(plate)
            sh_img = image_pre.img_shapen(pre_img)
            processed = reader.readtext(sh_img)

            pro_txt = ''
            pro_conf = 0

            for inf in processed:
                print(inf)
                if inf[-1] >= 0.3:
                    pro_txt += inf[1]
                    pro_conf = inf[-1]

            if or_conf > pro_conf:
                conf = or_conf
                serial_val = or_txt
            else:
                conf = pro_conf
                serial_val = pro_txt

            serial_val = post_process.char_map(serial_val, place) # apply post process method
            image = plotting.plotting(image, r, place + ' ' + serial_val)
            # cv2.imwrite(f'det_serial/{place}_{x}serial.jpg', sh_img)


            # info = reader.readtext(sh_img, paragraph=True)

            # # info = reader.readtext(plate[0:b1, 0:a1])
            # cv2.imwrite(f'det_serial/{place}_{x}serial.jpg', sh_img)

            # serial_val = []

            # print(info)
            
            # for inf in info:
            #     # txt = post_process.remove_space_special_chars(inf[-1]).upper()
            #     txt = inf[-1]

            #     # clean text
            #     txt = post_process.char_map(txt, place) # need to apply type of license plate next time

            #     # plot to the info to the image
            #     image = plotting.plotting(image, r, place + ' ' + txt)

            #     serial_val.append(txt) # get data from reader

            #     print(txt)


        result.append({
            "plate_roi": r,
            "serial_roi": serials,
            "plate_name": place,
            "serial_value": serial_val,
            "conf": conf,
            "datetime": datetime.now(time_zone)
        })

    # save the figure
    # cv2.imwrite('image.jpg', image)

    # Convert the CV2 image to a binary format (PNG or JPEG)
    _, buffer = cv2.imencode('.jpg', image)

    # Convert the binary image data to base64 encoding
    base64_image = base64.b64encode(buffer).decode('utf-8')

    end_result = {
        'filename': file.filename,
        'prediction': result
    }

    return render_template('result.html',base64_image=base64_image, **end_result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug= True)