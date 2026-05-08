from ultralytics import YOLO

# YOLOv8n is the smallest/fastest variant, good enough for face counting
# It will be auto-downloaded on first run
_model = YOLO("yolov8n.pt")

def count_faces(frame) -> int:
    """
    Given a BGR frame (numpy array from OpenCV),
    returns the number of faces detected.
    """
    results = _model(frame, verbose=False)
    
    # Class 0 in the COCO dataset is "person"
    # We count persons as a proxy for faces since we're just counting attendance
    persons = [
        box for box in results[0].boxes
        if int(box.cls[0]) == 0
    ]
    
    return len(persons)