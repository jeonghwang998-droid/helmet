from ultralytics import YOLO

# Create a new YOLO model from scratch
model = YOLO("yolo11n.yaml")

# Load a pretrained YOLO model (recommended for training)
model = YOLO("yolo11m.pt")

# Train the model using the 'coco8.yaml' dataset for 3 epochs
results = model.train(data="C:/Users/82102/Desktop/yolo_test12/dl_workspace/dl_workspace/archive/working/dataset.yaml", epochs=30)

# Evaluate the model's performance on the validation set
results = model.val()

# Perform object detection on an image using the model
results = model("C:/Users/82102/Desktop/yolo_test12/dl_workspace/dl_workspace/archive/working/images/BikesHelmets102.png")

# Export the model to ONNX format
success = model.export(format="onnx")    