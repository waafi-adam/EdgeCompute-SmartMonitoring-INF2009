import cv2
import os
from datetime import datetime

PERSON_NAME = "vianiece"
dataset_folder = "dataset"
person_folder = os  .path.join(dataset_folder, PERSON_NAME)

if not os.path.exists(person_folder):
    os.makedirs(person_folder)

video_capture = cv2.VideoCapture(0)
print(f"Taking photos for {PERSON_NAME}. Press SPACE to capture, 'q' to quit.")
photo_count = 0

while True:
    ret, frame = video_capture.read()
    if not ret:
        print("[ERROR] Failed to capture frame")
        break

    cv2.imshow('Capture', frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord(' '):
        photo_count += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{PERSON_NAME}_{timestamp}.jpg"
        filepath = os.path.join(person_folder, filename)
        cv2.imwrite(filepath, frame)
        print(f"Photo {photo_count} saved: {filepath}")

    elif key == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
print(f"Photo capture completed. {photo_count} photos saved for {PERSON_NAME}.")
