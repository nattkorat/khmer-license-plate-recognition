import cv2
import easyocr
import torch
from util import extract, image_pre, post_process
import time

# check if GPU is available
is_gpu = torch.cuda.is_available()
print('GPU:', is_gpu)
reader = easyocr.Reader(['en'], gpu = is_gpu)
counter = 1
def processs_OCR(plate_data, xyxy = [0,0,0,0]):
    # set default serial value and its confident score
    global counter
    serial_val = ''
    conf = 0
    width, height = xyxy[2] - xyxy[0], xyxy[3] - xyxy[1]
    size = width * height
    point = (width + height) / 2
    place, bbox = extract.get_info(plate_data)


    serials = extract.roi(plate_data, 1)
    print(f'Process: {counter}')

    # set default to image for do ocr
    img_for_ocr = plate_data
    if len(serials) > 0:
        serials = serials[0]
        a, b, a1, b1 = serials
        img_for_ocr = plate_data[b:b1, a:a1].copy()
    else:
        if len(bbox) > 0:
            img_for_ocr = cv2.rectangle(plate_data, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255,255,255), -1)
    
    origin_ocr = reader.readtext(img_for_ocr)
    label_conf = [{"label": t[-2], "conf": t[-1]} for t in origin_ocr]

    preprocess_img = image_pre.img_shapen(image_pre.pre_process(img_for_ocr))


    read_text = reader.readtext(preprocess_img)
    for t in read_text:
        label_conf.append({"label": t[-2], "conf": t[-1]})
    
    for i in label_conf:
        if len(i['label']) >= 6 and i['conf'] > conf:
            serial_val = post_process.char_map(i['label'], place)
            conf = i['conf']
    counter += 1
        

    return {
        "plate_name": place,
        "serial_value": serial_val,
        "conf": conf,
        "ROI": xyxy,
        "plate_size": size,
        "center": point
    }