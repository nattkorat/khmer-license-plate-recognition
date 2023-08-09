from ultralytics import YOLO
import torch


# model initial
info_model = torch.hub.load('ultralytics/yolov5', 'custom', path='models/place_detection_model_yolov5.pt') 
seg_model =  torch.hub.load('ultralytics/yolov5', 'custom', path='models/localize_plate_serial_model_yolov5.pt')



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


if __name__ == '__main__': # to test if it works or not
    
    import cv2
    import plotting

    img = cv2.imread('place_det.jpg')
    result = roi(img, 1)
    print(result)
    for re in result:
        img = plotting.plotting(img, re)

    cv2.imshow('test', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()