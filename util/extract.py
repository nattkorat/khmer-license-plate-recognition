from ultralytics import YOLO
import torch


# plate_model = YOLO('runs/detect/plate_and_info_det/weights/best.pt')
# plate_model = YOLO('plate_detect.pt')
# info_model = YOLO('runs/detect/place_classify/weights/best.pt') # yolov8 model
info_model = torch.hub.load('ultralytics/yolov5', 'custom', path='/home/nattkorat/Desktop/trainning/yolov5/runs/train/exp4/weights/best.pt') # new model of yolov5

# seg_model = YOLO('runs\detect/plate_info_v2/weights/best.pt')
# seg_model =  torch.hub.load('ultralytics/yolov5', 'custom', path='runs/detect/v5_plat_info/best.pt')

seg_model =  torch.hub.load('ultralytics/yolov5', 'custom', path='/home/nattkorat/Desktop/trainning/yolov5/runs/train/exp3/weights/best.pt')



def roi(img, opt: int): # return only one of detect object
    '''
        Extract only Region of Interest (license plate, or region of serial in plate)
        --------------
        img: source of image or array image
        opt: roi (0 for whole plate, 1 for serial)
        
    '''
    # img = cv2.imread(image)
    
    # result = seg_model.predict(img)
    result = seg_model(img, size= 640)
    
    area = []

    for re in result.xyxy:
        for r in re:
            if int(r[-1]) == opt and r[-2] > 0.5: # threshold is r[-2]
                area.append([int(i) for i in r[:4]])
    # for r in result:
    #     for box in r.boxes:
    #         c = box.cls
    #         if c == opt:
    #             area.append([round(i) for i in box.xyxy[0].tolist()])
    return area



def get_info(img):
    result = info_model(img, size= 640)
    class_names = "" # for getting the class name
    bbox = []
    for re in result.xyxy:
        # boxes = r.boxes
        # for b in boxes:
        #     c = b.cls
        #     conf = b.conf
        for r in re:
            c = r[-1]
            conf = r[-2]

            if conf > 0.8:
                class_names = info_model.names[int(c)]
                bbox = [int(i) for i in r[:4]]

    return class_names, bbox


def get_area(model_result, option = 0):
    '''
        generate xyxy of plate and serial
        ---------------------
        option = 1 for getting whole plate xyxy
    '''
    region = ''
    data = []
    if option == 1:
        region = 'car-license-plate'
    else:
        region = 'info'
    
    for r in model_result:
        key = ''
        for k in r.keys():
            key = k
            
        if key == region:
            data.append(r[region])
    return data
    
def xyxy_serial(plate):
    result = seg_model.predict(plate)

    if result[0] == 0:
        return []
    
    area = []
    for r in result:
        for box in r.boxes:
            c = box.cls
            class_name = seg_model.names[int(c)]
            if class_name == 'info':
                for bo in box.xyxy:   
                    area.append([int(i) for i in bo.tolist()])

    return area

if __name__ == '__main__': # to test if it works or not
    
    import cv2

    img = cv2.imread('img/motor_license.jpg')
    