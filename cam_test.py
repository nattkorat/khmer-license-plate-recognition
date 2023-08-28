import cv2
from mjpeg_streamer import MjpegServer, Stream
from util import extract, plotting
from flask import Flask, request, Response, jsonify

app = Flask(__name__)

usr = "Cam21"
password = "Idri@2023"
ip = "172.23.32.181"

cam = cv2.VideoCapture(f"rtsp://{usr}:{password}@{ip}:88/videoMain")
# cam = cv2.VideoCapture("video/y2mate.is - 2020 camry review in khmer-22iyZsAuHe4-720p-1692774674.mp4")

frame_rate = cam.get(cv2.CAP_PROP_FPS)

stream = Stream("stream_camera", quality=50, fps=64)

server = MjpegServer("0.0.0.0", 5050)
server.add_stream(stream)

report = [] # test data

def main():
    server.start()
    while True:
        ret, frame = cam.read()
        if not ret:
            print('No frame read')
            break

        # Send to the stream
        stream.set_frame(frame)
        
        if cv2.waitKey(int(1000/frame_rate)) == ord("q"):
            print('User exit the program')
            break

    server.stop()
    cam.release()
    cv2.destroyAllWindows()


def processingROI(frame):
    roi = extract.roi(frame, 0)
    for r in roi:
        frame = plotting.plotting(frame, r)
    
    return frame

# Run main program
main()