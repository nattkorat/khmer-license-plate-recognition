import cv2
import analyze
from datetime import datetime

# usr = "Cam21"
# password = "Idri2023"
# ip = "172.23.32.232"

# cam = cv2.VideoCapture(f"rtsp://{usr}:{password}@{ip}:88/videoMain")
cam = cv2.VideoCapture("video/y2mate.is - 2020 camry review in khmer-22iyZsAuHe4-720p-1692774674.mp4")

if not cam.isOpened():
    print("Error: Could not open video file.")
    exit()

initial_time = datetime.now().microsecond
while True:
    ret, frame= cam.read()
    if not ret:
        print('Cannot read camera.')
        break
    current_time = datetime.now().microsecond
    if abs(current_time - initial_time) >= 500000: # 1000000 microseconds per second
        if analyze.detected(frame): # this will work utill the model detect the vehicle and plate
            initial_time = datetime.now().microsecond # set the initial time to the current time in the machine
            print(datetime.now().year, datetime.now().hour, datetime.now().minute, datetime.now().second)

            file_name = str(datetime.now().year) + '_' + str(datetime.now().month) + '_' + str(datetime.now().day) + '_' \
            + str(datetime.now().hour) + '_' + str(datetime.now().minute) + '_' + str(datetime.now().second) + '_' + str(datetime.now().microsecond)

            cv2.imwrite(f'temp_img/{file_name}.jpg', frame) # save the frame to the temp folder that can allow model to predict and save data from it
            print('Writing image:',file_name)

    cv2.imshow('Frame', frame)
    analyze.process_data('temp_img')

    if cv2.waitKey(32) & 0xff == ord('q'):
        break
    
cam.release()
cv2.destroyAllWindows()
