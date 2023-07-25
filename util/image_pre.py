import cv2
import numpy as np

def pre_process(img):
    # Get the original image dimensions
    height, width = img.shape[:2]

    # Calculate the new dimensions
    new_width = width * 5
    new_height = height * 5

    # Resize the image
    resized_image = cv2.resize(img, (new_width, new_height))

    # change to gray scale
    img_new = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)

    # Apply Otsu's thresholding
    _, thresholded_image = cv2.threshold(img_new, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

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

    
    image = cv2.imread("img/img_2330kg_cham.jpg")
    thres = pre_process(image)

    sh_img = img_shapen(thres)
    txt = reader.readtext(sh_img)
    print(txt)
    
    cv2.imwrite("sharpen.jpg", sh_img)

