import cv2
from util import extract, plotting
from util.ocr import processs_OCR
from util.post_process import check_order, major_vote

# Replace 'path_to_video_file.mp4' with the actual path to your video file
video_path = 'video/IMG_0482.MOV'

# Create a VideoCapture object to read the video file
cap = cv2.VideoCapture(video_path)

# Set the desired width and height
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 250)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Check if the video file was opened successfully
if not cap.isOpened():
    print("Error opening video file")
    exit()

report = [] # test data
record = []

while True:   
    # Read a frame from the video
    ret, image = cap.read()

    # Check if the frame was read successfully
    if not ret:
        break

    # Process the image
    roi = extract.roi(image, 0)
    for r in roi:
        x, y, x1, y1 = r
        counter = 0 # set counter back to 0
        width, height = x1 - x, y1 - y
        size = width * height
        center_point = (width + height) / 2

        plate = image[y:y1, x:x1].copy()
        data = processs_OCR(plate, r)

        # check the center point
        if record:
            last_record = record[-1]
            
            if abs(last_record['center'] - center_point) > 100 or len(record) > 20:
                common = [entry['serial_value'] for entry in record]
                winner = major_vote(common)

                status = check_order([i['plate_size'] for i in record])
                
                if not report or winner != report[-1]['serial_value']:
                    temp = record[common.index(winner)]
                    temp['status'] = status       
                    report.append(temp)
                    record = []
            else:
                record.append(data)
        else:
            record.append(data)
 
        image = plotting.plotting(image, r, data['plate_name'] + ' ' + data['serial_value'] + ' ' + f'{data["conf"]:.3f}')

    cv2.imshow('Video', image)

    # Check for 'q' key to exit the loop
    if cv2.waitKey(64) & 0xFF == ord('q'):
        break

# Release the VideoCapture and close the OpenCV windows
cap.release()
cv2.destroyAllWindows()

print(report)