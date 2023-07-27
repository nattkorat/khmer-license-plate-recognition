import cv2
import numpy as np

import cv2
import numpy as np

import cv2

def pre_process(img):
    # Stretch the image to have a width of 640 and maintain the aspect ratio
    desired_width = 640
    aspect_ratio = img.shape[1] / img.shape[0]
    desired_height = int(desired_width / aspect_ratio)

    # Resize the image
    resized_img = cv2.resize(img, (desired_width, desired_height), interpolation=cv2.INTER_LINEAR)

    # Convert the image to grayscale
    gray_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred_img = cv2.GaussianBlur(gray_img, (5, 5), 0)

    # Apply Otsu's thresholding
    _, thresholded_image = cv2.threshold(blurred_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return thresholded_image




def img_shapen(img):
    # create a sharpen kernel
    sharpen_filter = np.array(
        [
            [-1,-1,-1],
            [-1, 9, -1],
            [-1,-1,-1]
        ]
    )

    sh_img = cv2.filter2D(img, -1, sharpen_filter)

    return sh_img
    

if __name__ == '__main__':
    import easyocr

    reader = easyocr.Reader(['en'], verbose=False)

    
    image = cv2.imread("serial.jpg")
    thres = pre_process(image)

    sh_img = img_shapen(thres)
    txt = reader.readtext(sh_img)
    print(txt)
    
    cv2.imwrite("sharpen.jpg", sh_img)

