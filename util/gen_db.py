import extract
import os
import cv2

# base dir of image storing
db_dir = "C:/Users/nathk\Desktop/temdata/db_gen/202306291"
# db_dir = "C:/Users/nathk\Desktop/temdata/img"

# list all file in the directory
img_list = os.listdir(db_dir)

print(f'Total image: {len(img_list)}')

# distination of dir to store the result
dis_dir ="D:/cadt/KLPR/plate_datasets/images"

# create new dir if not exists
if not os.path.isdir(dis_dir):
    os.makedirs(dis_dir)

# print(img_list[:10])
j = 0
print("Generating ...")
for i in img_list:
    img = cv2.imread(os.path.join(db_dir, i)) # read image to cv2 format one by one
    resutls = extract.roi(img, 0) # get the roi (xyxy format)
    
    for result in resutls:
        x, y, x1, y1 = result
        dx = int(x1) - int(x)
        dy = int(y1) - int(y)

        dxy = abs(dx - dy) # find the positive different of diff x to x1 and diff y to y1
        hdxy = dxy // 2 # make it to half or near half for scaling up and down
        img_x, img_y = img.shape[:2]

        # print info of image
        print(f"Image size {img_x} x {img_y} - Roi center (x = {dx} y = {dy})")
        print(f"Image: {i}")

        if dx > dy:  # This code below is to scale x or y up to the maximume diff of them
            less_y = 0
            y = y - hdxy
            if y < 0:
                less_y = abs(y)
                y = 0
            y1 = y1 + hdxy + less_y
            if y1 > img_y:
                y1 = img_y
        else:
            less_x = 0
            x = x - hdxy
            if x < 0:
                less_x = abs(x)
                x = 0
            x1 = x1 + hdxy
            if x1 > img_x:
                x1 = img_x

        # cv2.imwrite(f'{dis_dir}/{j}_{i}', img[y:y1, x:x1])
        try:
            resized = cv2.resize(img[y:y1, x:x1], (640, 640))
            cv2.imwrite(f"{dis_dir}/{j}_{i}", resized)
            j += 1
            print(f'{j} saved!')
        except:
            print("Too small that cannot resize and save!!")