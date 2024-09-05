from ultralytics import YOLO
model = YOLO("pre-trained/yolov8n.pt")  # load a pretrained model (recommended for training)
results = model.train(data="dataset/data-detection/dataset.yaml", epochs=50, imgsz=640)