import cv2
import torch
import numpy as np
from util import extract, plotting, post_process, image_pre
import easyocr
from collections import Counter
from datetime import datetime


def major_vote(data):
    vote_count = Counter(data)
    winner = vote_count.most_common(1)[0][0]
    return winner

# check if GPU is available
is_gpu = torch.cuda.is_available()
print('GPU:', is_gpu)
reader = easyocr.Reader(['en'], gpu = is_gpu)

# Replace 'path_to_video_file.mp4' with the actual path to your video file
video_path = 'video/y2mate.is - 2020 camry review in khmer-22iyZsAuHe4-720p-1692774674.mp4'

# Create a VideoCapture object to read the video file
cap = cv2.VideoCapture(video_path)

# Check if the video file was opened successfully
if not cap.isOpened():
    print("Error opening video file")
    exit()

report = [] # test data
record = []
counter = 0

while True:   
    # Read a frame from the video
    ret, image = cap.read()

    # Check if the frame was read successfully
    if not ret:
        break

    # Process the image
    roi = extract.roi(image, 0)

    if len(roi) == 0 and len(record) != 0:
        sec = datetime.now().second
        if record[-1]['time'] - sec > 3:

            temp = [i['label'] for i in record]     
            most = major_vote(temp)
            print("Recode - ", most, "at time", datetime.now())
            report.append(record[temp.index(most)])
            record = []


    for r in roi:
        x, y, x1, y1 = r
        # skip 10 frame 
        if counter == 10:
            counter = 0 # set counter back to 0
            width, height = x1 - x, y1 - y
            size = width * height
            center_point = ((x+x1)+ (y+y1)) / 4

            print('Size:', size)

            plate = image[y:y1, x:x1].copy()
            place, bbox = extract.get_info(plate)
            pl_img = plate.copy()
            if len(bbox) >= 4:
                cv2.rectangle(pl_img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0,255,0), 2)


            serials = extract.roi(plate, 1)
                
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


            # add record to data
            if len(record) > 0:
                # abs(Xn - Xn-1) > 100 consider the different - it really depend on the speed of vehicle
                # so we need to test it in real time or place 
                print(abs(center_point - record[-1]['point']))
                if abs(center_point - record[-1]['point']) > 100: # set the threshold for object
                    # we can do check the data
                    temp = [i['label'] for i in record]
                    
                    most = major_vote(temp)

                    if record[temp.index(most)]['label'] != "" or record[temp.index(most)]['place'] != "":
                        print("Record - ", most)
                        report.append(record[temp.index(most)])
                        
                    record = []
                else:
                    record.append({
                        "roi": roi.copy(),
                        "size": size,
                        "point": center_point,
                        "place": place,
                        "label": serial_val,
                        "time": datetime.now().second
                    })    
            else:
                record.append({
                    "roi": roi.copy(),
                    "size": size,
                    "point": center_point,
                    "place": place,
                    "label": serial_val,
                    "time": datetime.now().second
                })
        try:
            image = plotting.plotting(image, r, place + ' ' + serial_val + ' ' + f'{conf:.3f}')
        except:
            pass
        counter += 1 # increase counter

    cv2.imshow('Video', image)

    # Check for 'q' key to exit the loop
    if cv2.waitKey(64) & 0xFF == ord('q'):
        break

# Release the VideoCapture and close the OpenCV windows
cap.release()
cv2.destroyAllWindows()

print(report)