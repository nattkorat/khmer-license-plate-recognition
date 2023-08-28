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

<<<<<<< HEAD
# Replace 'your_camera_ip' with the actual IP address of your camera
username = 'camtest'
password = 'Idri@2023'
camera_url = f'rtsp://{username}:{password}@172.23.33.29:88/videoMain'
=======
# Replace 'path_to_video_file.mp4' with the actual path to your video file
video_path = 'video/y2mate.is - 2020 camry review in khmer-22iyZsAuHe4-720p-1692774674.mp4'
>>>>>>> dev

# Create a VideoCapture object to read the video file
cap = cv2.VideoCapture(camera_url)

# Set the desired width and height
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 250)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

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
<<<<<<< HEAD
                    txt = post_process.remove_space_special_chars(txt).upper()
                serial_val.append(txt) # get data from reader

                # plot to the info to the image
                image = plotting.plotting(image, r, place + ' ' + txt)

                print(txt)
        else:
            if len(bbox) > 0:
                plate = cv2.rectangle(plate, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255,255,255), -1)

            pre_img = image_pre.pre_process(plate)
            sh_img = image_pre.img_shapen(pre_img)

            info = reader.readtext(sh_img, paragraph=True)

            # info = reader.readtext(plate[0:b1, 0:a1])
            # cv2.imwrite(f'det_serial/{place}_{x}serial.jpg', sh_img)

            serial_val = []

            print(info)
            
            for inf in info:
                # txt = post_process.remove_space_special_chars(inf[-1]).upper()
                txt = inf[-1]

                # clean text
                if place not in ['Cambodia', 'State', 'Police']:
                    txt = post_process.char_map(txt) # need to apply type of license plate next time
                else:
                    txt = post_process.remove_space_special_chars(txt).upper()
                serial_val.append(txt) # get data from reader

                # plot to the info to the image
                image = plotting.plotting(image, r, place + ' ' + txt)

                print(txt)
    resized_frame = cv2.resize(image, (1280, 720))
=======
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
>>>>>>> dev

    cv2.imshow('Video', resized_frame)

    # Check for 'q' key to exit the loop
<<<<<<< HEAD
    if cv2.waitKey(1) & 0xFF == ord('q'):
=======
    if cv2.waitKey(64) & 0xFF == ord('q'):
>>>>>>> dev
        break

# Release the VideoCapture and close the OpenCV windows
cap.release()
cv2.destroyAllWindows()

print(report)