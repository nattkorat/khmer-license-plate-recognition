import cv2

def plotting(img, bbox: list, label = ""):
    if len(bbox) == 4:
        x, y, x1, y1 = bbox
        img = cv2.rectangle(img, (x, y), (x1, y1), (0, 255, 0), 2)
        img = cv2.putText(img, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

        return img
    return None