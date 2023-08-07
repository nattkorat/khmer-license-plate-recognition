import cv2
import torch
import numpy as np
from util import extract, plotting, post_process, image_pre
import easyocr

# check if GPU is available
is_gpu = torch.cuda.is_available()
print('GPU:', is_gpu)
reader = easyocr.Reader(['en'], gpu = is_gpu)

# Replace 'path_to_video_file.mp4' with the actual path to your video file
video_path = 'vid.mp4'

# Create a VideoCapture object to read the video file
cap = cv2.VideoCapture(video_path)

# Check if the video file was opened successfully
if not cap.isOpened():
    print("Error opening video file")
    exit()

while True:
    # Read a frame from the video
    ret, image = cap.read()

    # Check if the frame was read successfully
    if not ret:
        break

    # Do something with the frame (e.g., display it, process it, etc.)
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

        cv2.imwrite('place_det.jpg', pl_img)

        image = plotting.plotting(image, r, place)
        

        serials = extract.roi(plate, 1)
        if len(serials) > 0: 
            serials = serials[0]
            a, b, a1, b1 = serials

            cv2.imwrite('serial.jpg', plate[b:b1, a:a1])

            pre_img = image_pre.pre_process(plate[b:b1, a:a1])
            sh_img = image_pre.img_shapen(pre_img)

            info = reader.readtext(sh_img, paragraph=True)

            # info = reader.readtext(plate[0:b1, 0:a1])
            cv2.imwrite(f'det_serial/{place}_{x}serial.jpg', sh_img)

            serial_val = []

            print(info)
            
            for inf in info:
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

    cv2.imshow('Video', image)

    # Check for 'q' key to exit the loop
    if cv2.waitKey(0) & 0xFF == ord('q'):
        break

# Release the VideoCapture and close the OpenCV windows
cap.release()
cv2.destroyAllWindows()
