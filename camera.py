import cv2
import analyze
from datetime import datetime
from util.plotting import plotting

# usr = "Cam21"
# password = "Idri2023"
# ip = "172.23.32.232"

# cam = cv2.VideoCapture(f"rtsp://{usr}:{password}@{ip}:88/videoMain")
cam = cv2.VideoCapture("vid_demo/C1588.MP4")

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
    if abs(current_time - initial_time) >= 100000: # 1000000 microseconds per second
        if analyze.detected(frame): # this will work utill the model detect the vehicle and plate
            initial_time = datetime.now().microsecond # set the initial time to the current time in the machine
            file_name = analyze.server_datetime()
            cv2.imwrite(f'temp_img/{file_name}.jpg', frame) # save the frame to the temp folder that can allow model to predict and save data from it
            print('Writing image:',file_name)
        else:
            analyze.process_data('temp_img')

    xyxy = analyze.vehicle_xyxy(frame)
    if xyxy:
        frame = plotting(frame, xyxy)  
    cv2.imshow('Frame', frame)

    if cv2.waitKey(1) & 0xff == ord('q'):
        break
    
cam.release()
cv2.destroyAllWindows()