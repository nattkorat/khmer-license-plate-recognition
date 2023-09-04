import os
from util.extract import roi, get_info
from util.ocr import processs_OCR

temp_folder = 'temp_img'

imgs = os.listdir(temp_folder)
print(imgs)