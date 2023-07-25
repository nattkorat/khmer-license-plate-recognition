from ultralytics import YOLO

# Load a model
# model = YOLO('yolov8n.yaml')  # build a new model from YAML
model = YOLO('yolov8n.pt')  # load a pretrained model (recommended for training)
# model = YOLO('data.yaml').load('yolov8n.pt')  # build from YAML and transfer weights

# Train the model
model.train(data='datasets/data.yaml', epochs=50, imgsz=640, name = 'place_classify_v2')