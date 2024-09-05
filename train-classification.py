from ultralytics import YOLO
model = YOLO("pre-trained/yolov8n-cls.pt")  # load a pretrained model (recommended for training)
results = model.train(data="dataset/data-classification", epochs=50, imgsz=224)