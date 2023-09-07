import torch, cv2
from util.post_process import major_vote
from ultralytics import YOLO

# model initial
info_model = torch.hub.load('ultralytics/yolov5', 'custom', path='models/v2_place_detection_model_yolov5.pt', verbose=False) 
seg_model =  torch.hub.load('ultralytics/yolov5', 'custom', path='models/localize_plate_serial_model_yolov5.pt', verbose=False)
front_rear_model = torch.hub.load('ultralytics/yolov5', 'custom', path='models/front_rear_model_yolov5.pt', verbose=False)
vehicle_detect_model = YOLO()

# check if the vehicle appear in the frame
def is_vehicle(img, is_bbox = False):
    result = vehicle_detect_model.predict(img, verbose = False)
    for re in result:
        for r in re.boxes:
            if int(r.cls) in [2,5,7]:
                bbox = [int(i) for i in r.xyxy[0].tolist()]
                if is_bbox:
                    return bbox
                return True
    return False


# check status of vehicle if front or rear detected
def front_rear(img):
    """
    It will return
        0: rear
        1: front
        None: not detected
    """
    if type(img) == str:
        img = cv2.imread(img)

    detect = front_rear_model(img, size=640)
    data = []
    for result in detect.xyxy:
        for re in result:
            data.append(int(re[-1]))

    return major_vote(data) if len(data) > 0 else None

def roi(img, opt: int): # return only one of detect object
    '''
        Extract only Region of Interest (license plate, or region of serial in plate)
        --------------
        img: source of image or array of an image
        opt: roi (0 for whole plate, 1 for serial)
        
    '''
    # result = seg_model.predict(img)
    result = seg_model(img, size= 640)
    
    area = []
    for re in result.xyxy:
        for r in re:
            if int(r[-1]) == opt and r[-2] > 0.5: # threshold is r[-2]
                area.append([int(i) for i in r[:4]])

    return area

def get_info(img):
    result = info_model(img, size= 640)
    class_names = "" # for getting the class name
    bbox = []
    for re in result.xyxy:
        for r in re:
            c = r[-1]
            conf = r[-2]
            if conf > 0.8:
                class_names = info_model.names[int(c)]
                bbox = [int(i) for i in r[:4]]

    return class_names, bbox

if __name__ == '__main__':
    import cv2
    img = cv2.imread('/home/nattkorat/Desktop/demo_images/custom plate.jpg')
    vehichle = is_vehicle(img)
    if vehichle:
        print(front_rear(img))
    else:
        print("No vehicle!")
    
