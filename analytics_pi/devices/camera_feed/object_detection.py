import cv2
import time
import os
from datetime import datetime
from ultralytics import YOLO

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILENAME = "best.pt"
MODEL_PATH = os.path.join(CURRENT_DIR, MODEL_FILENAME)
OUTPUT_DIR = os.path.join(CURRENT_DIR, "detected_items")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load model once
model = YOLO(MODEL_PATH)

# Global tracking variables
detected_objects = {}
captured_objects = set()
stationary_threshold = 10  # seconds

def detect_objects(frame):
    alerts = []

    # Perform object detection
    results = model.predict(source=frame, stream=False, verbose=False, conf=0.5)

    for result in results:
        for box in result.boxes:
            try:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf)
                cls = int(box.cls)
                label = model.names[cls]
            except Exception as e:
                print("[ERROR] Parsing bounding box:", e)
                continue

            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            # Use a more tolerant grid for keying
            key = f"{label}_{center_x//50}_{center_y//50}"

            if key in detected_objects:
                prev_center, first_detected = detected_objects[key]
                distance = ((center_x - prev_center[0]) ** 2 + (center_y - prev_center[1]) ** 2) ** 0.5

                if distance < 10:
                    elapsed_time = time.time() - first_detected
                    if elapsed_time > stationary_threshold and key not in captured_objects:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        image_path = os.path.join(OUTPUT_DIR, f"object_{label}_{timestamp}.jpg")

                        # Save image with red box
                        color = (0, 0, 255)
                        frame_copy = frame.copy()
                        cv2.rectangle(frame_copy, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(frame_copy, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                        cv2.imwrite(image_path, frame_copy)

                        alert_msg = f"Object detected: {label}"
                        alerts.append(alert_msg)
                        captured_objects.add(key)
            else:
                detected_objects[key] = ((center_x, center_y), time.time())

            # Draw detection box
            color = (0, 255, 0) if key in captured_objects else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    return frame, alerts