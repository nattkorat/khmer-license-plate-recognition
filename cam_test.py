from collections import Counter
import datetime
import cv2
from mjpeg_streamer import MjpegServer, Stream
import torch

import easyocr

from util import extract, image_pre, plotting, post_process

usr = "Cam21"
password = "Idri@2023"
ip = "172.23.32.231"

cam = cv2.VideoCapture(f"rtsp://{usr}:{password}@{ip}:88/videoMain")

stream = Stream("stream_camera", quality=50, fps=64)

server = MjpegServer("0.0.0.0", 5050)
server.add_stream(stream)

# check if GPU is available
is_gpu = torch.cuda.is_available()
print('GPU:', is_gpu)
reader = easyocr.Reader(['en'], gpu = is_gpu)

report = [] # test data

def main():
    server.start()

    while True:
        ret, frame = cam.read()
        if cv2.waitKey(64) == ord("q"):
            print('User exit the program')
            break

        if not ret:
            print('No frame read')
            break

        # Process the image
        image = processingROI(frame)

        # Send to the stream
        stream.set_frame(image)

    server.stop()
    cam.release()
    cv2.destroyAllWindows()

def major_vote(data):
    vote_count = Counter(data)
    winner = vote_count.most_common(1)[0][0]
    return winner

def processingROI(frame):
    roi = extract.roi(frame, 0)
    for r in roi:
        x, y, x1, y1 = r
        frame = cv2.rectangle(frame, (x, y), (x1, y1), (0, 255, 0), 2)
    
    return frame
       

# Run main program
main()