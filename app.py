from flask import Flask, render_template, request, jsonify, send_file, Response
import cv2
import torch
import numpy as np
from util import extract, plotting, post_process, image_pre
import easyocr
from datetime import datetime
import base64

# check if GPU is available
is_gpu = torch.cuda.is_available()
print('GPU:', is_gpu)

reader = easyocr.Reader(['en'], gpu = is_gpu)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/image', methods=['GET'])
def start_img():
    return render_template('upload.html')

@app.route('/video', methods=['GET'])
def start_vid():
    return render_template('video.html')

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


        plate = image[y:y1, x:x1].copy()
        cv2.imwrite('plate.jpg', plate)

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
            cv2.imwrite(f'det_serial/{place}_{x}serial.jpg', sh_img)

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


        result.append({
            "plate_roi": r,
            "serial_roi": serials,
            "plate_name": place,
            "serial_value": serial_val,
            "datetime": datetime.now()
        })

    # save the figure
    cv2.imwrite('image.jpg', image)

    # Convert the CV2 image to a binary format (PNG or JPEG)
    _, buffer = cv2.imencode('.jpg', image)

    # Convert the binary image data to base64 encoding
    base64_image = base64.b64encode(buffer).decode('utf-8')

    end_result = {
        'filename': file.filename,
        'prediction': result
    }

    return render_template('result.html',base64_image=base64_image, **end_result)



def process_image(image):
    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Perform any additional processing you want here

    return gray_image

def generate_frames(video_path):
    cap = cv2.VideoCapture(video_path)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Process the frame
        processed_frame = process_image(frame)

        # Convert the frame to JPEG format
        _, buffer = cv2.imencode('.jpg', processed_frame)

        # Convert the binary image data to base64 encoding
        base64_image = base64.b64encode(buffer).decode('utf-8')

        # Yield the frame as a response to the client
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + base64_image.encode('utf-8') + b'\r\n')

    cap.release()


def write_video(input_video_path, output_video_path):
    # Open the input video
    cap = cv2.VideoCapture(input_video_path)

    # Get the video's width, height, and frames per second (fps)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Define the codec for the output video (XVID for .avi format)
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')

    # Create a VideoWriter object to write the output video
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    # Loop through each frame of the input video and write it to the output video
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Do any processing on the frame here (if needed)
        frame = process_image(frame)

        # Write the frame to the output video
        out.write(frame)

        # Display the frame (optional)
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the VideoWriter and close the input video
    out.release()
    cap.release()

    # Close any OpenCV windows opened during the process
    cv2.destroyAllWindows()


@app.route('/video_feed', methods=['POST'])
def video_feed():
    # Get the video file uploaded by the user
    file = request.files['video']

    # Save the video to a temporary file (you may want to use a more robust method to handle video files in production)
    temp_video_path = 'temp_video.mp4'
    file.save(temp_video_path)

    # process video and save
    write_video(temp_video_path, "output.avi")

    # Return the streaming response
    # return Response(generate_frames(temp_video_path), mimetype='multipart/x-mixed-replace; boundary=frame')
    return render_template('video_result.html', video_path="output.avi")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug= True)