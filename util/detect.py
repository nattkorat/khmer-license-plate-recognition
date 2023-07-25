import easyocr
from util.extract import roi
import cv2

reader = easyocr.Reader(['en'])

img = cv2.imread('1200px-Trucks_in_Cambodia_05.jpg')

ROI = roi(img)

img_name = "test.jpg"

if ROI is not None:
    for xyxy in ROI:
        x,y,x1,y1 = xyxy
        cv2.imwrite(img_name, img[y:y1, x:x1])
        result = reader.readtext(img[y:y1, x:x1])
        for re in result:
            print(re[1])


