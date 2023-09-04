import cv2
from util import extract, plotting
from datetime import datetime

usr = "Cam21"
password = "Idri@2023"
ip = "172.23.32.181"

# cam = cv2.VideoCapture(f"rtsp://{usr}:{password}@{ip}:88/videoMain")
cam = cv2.VideoCapture("video/y2mate.is - 2020 camry review in khmer-22iyZsAuHe4-720p-1692774674.mp4")

if not cam.isOpened():
    print("Error: Could not open video file.")
    exit()

initial_time = datetime.now().microsecond
counter = 0
while True:
    ret, frame= cam.read()
    counter += 1
    if not ret:
        print('Cannot read camera.')
        break
    current_time = datetime.now().microsecond
    if abs(current_time - initial_time) >= 500000: # 1000000 per second
        if extract.is_vehicle(frame): # this will work utill the model detect the vehicle
            initial_time = datetime.now().microsecond # set the initial time to the current time in the machine

            front_rear = extract.front_rear(frame)
            if front_rear is not None: # save the image untill front or rear model detected from the car
                print(datetime.now().year, datetime.now().hour, datetime.now().minute, datetime.now().second)

                file_name = str(front_rear) + '_' + str(datetime.now().year) + '-' + str(datetime.now().month) + '_' + str(datetime.now().day) + '_' \
                + str(datetime.now().hour) + '_' + str(datetime.now().minute) + '_' + str(datetime.now().second) + '_' + str(datetime.now().microsecond)
                cv2.imwrite(f'temp_img/{file_name}.jpg', frame) # save the frame to the temp folder that can allow model to predict and save data from it
                print('Writing image:',file_name)
                
    cv2.imshow('Frame', frame)

    if cv2.waitKey(64) & 0xff == ord('q'):
        break
cam.release()
cv2.destroyAllWindows()
