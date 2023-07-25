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
    

        
        # for ser in serial:
        #     # sx,sy, sx1, sy1 = ser
        #     # img_ser = plate[sy:sy1, sx:sx1]

        #     # txt = reader.readtext(img_ser, detail = 0, paragraph=True)[0]
        #     # serials.append(txt)

        #     serials.append(ser)



    # result = []

    # for d in data:
    #     x,y,x1,y1 = d
    #     txt = " "
    #     # plate = image[y:y1, x:x1]
    #     place = extract.get_info(img=image)
    #     # cv2.imwrite('result.jpg', image[y:y1, x:x1])
    #     # pl = cv2.imread('result.jpg')
    #     serials = extract.roi(image, 1)
    #     for serial in serials:
    #         if len(serial) > 0:
    #             a,b, a1, b1 = serial
    #             # read with origin image 
    #             # processed = image_pre.pre_process(plate[b:b1, a:a1])
    #             # sharpen = image_pre.img_shapen(processed)       
    #             # txt = pytesseract.image_to_string(processed, config=custom_conf)
    #             txt = reader.readtext(image[b:b1, a:a1], detail = 0, paragraph=True)[0]
    #             # txt = reader.readtext(sharpen, detail = 0, paragraph = True )[0]                       
    #             cv2.imwrite('result.jpg', image[b:b1, a:a1])

            
    #     # if len(serials) > 0:
    #     #     serial = serials[0]

    #     #     ext = image[y:y1, x:x1]

    #     #     info = extract.xyxy_serial(ext)
    #     #     for inf in info:
    #     #         if len(inf) > 0:
    #     #             a,b,a1,b1 = info[0]
    #     #             # read with origin image 
    #     #             processed = image_pre.pre_process(ext[b:b1, a:a1])
    #     #             sharpen = image_pre.img_shapen(processed)       
    #     #             # txt = pytesseract.image_to_string(processed, config=custom_conf)
    #     #             txt = reader.readtext(ext[b:b1, a:a1], detail = 0, paragraph=True)[0]
    #     #             # txt = reader.readtext(sharpen, detail = 0, paragraph = True )[0]                       
    #     #             cv2.imwrite('result.jpg', sharpen)
    #     #             # txt = txt.strip()


    #     result.append({
    #         'place' : place,
    #         'xyxy': d,
    #         'info' : txt
    #     })

    # save the figure
    cv2.imwrite('image.jpg', image)

    # return send_file('image.jpg', mimetype='image/jpeg')

    return jsonify({
        'filename': file.filename,
        'predicttion': result
    })



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug= True)