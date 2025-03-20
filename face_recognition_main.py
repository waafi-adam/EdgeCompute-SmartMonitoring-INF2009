import cv2
import os
import pickle
import face_recognition
from datetime import datetime

# Constants
DATASET_DIR = "dataset"
ENCODINGS_FILE = "encodings.pickle"
NUM_IMAGES = 5

def capture_images(person_name):
    """Captures 5 images for a new user and stores them in the dataset."""
    person_dir = os.path.join(DATASET_DIR, person_name)
    os.makedirs(person_dir, exist_ok=True)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Unable to access the webcam.")
        return
    
    print(f"[INFO] Capturing images for '{person_name}'. Press 's' to save, 'q' to quit.")
    captured_count = 0
    
    while captured_count < NUM_IMAGES:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to capture image.")
            break
        
        cv2.imshow("Capture", frame)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('s'):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{person_name}_{timestamp}.jpg"
            filepath = os.path.join(person_dir, filename)
            cv2.imwrite(filepath, frame)
            print(f"[INFO] Saved image {captured_count + 1}/{NUM_IMAGES}: {filepath}")
            captured_count += 1
        elif key == ord('q'):
            print("[INFO] Image capture aborted.")
            break
    
    cap.release()
    cv2.destroyAllWindows()

def process_images():
    """Processes the images in the dataset and generates facial encodings."""
    print("[INFO] Processing images for face encodings...")
    image_paths = []
    for root, _, files in os.walk(DATASET_DIR):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_paths.append(os.path.join(root, file))
    
    known_encodings = []
    known_names = []
    
    for image_path in image_paths:
        print(f"[INFO] Processing {image_path}...")
        image = cv2.imread(image_path)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb, model="hog")
        encodings = face_recognition.face_encodings(rgb, boxes)
        
        name = os.path.basename(os.path.dirname(image_path))
        for encoding in encodings:
            known_encodings.append(encoding)
            known_names.append(name)
    
    data = {"encodings": known_encodings, "names": known_names}
    with open(ENCODINGS_FILE, "wb") as f:
        pickle.dump(data, f)
    print(f"[INFO] Encodings saved to '{ENCODINGS_FILE}'.")

def recognize_faces():
    """Loads encodings and runs real-time face recognition using webcam."""
    if not os.path.exists(ENCODINGS_FILE):
        print("[ERROR] No trained encodings found! Please add a new user first.")
        return

    print("[INFO] Loading encodings...")
    with open(ENCODINGS_FILE, "rb") as f:
        data = pickle.load(f)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Unable to access the webcam.")
        return
    
    print("[INFO] Starting face recognition. Press 'q' to quit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to capture frame.")
            break
        
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb, model="hog")
        encodings = face_recognition.face_encodings(rgb, boxes)
        
        names = []
        for encoding in encodings:
            matches = face_recognition.compare_faces(data["encodings"], encoding)
            name = "Unknown"
            if True in matches:
                matched_idxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}
                for i in matched_idxs:
                    name = data["names"][i]
                    counts[name] = counts.get(name, 0) + 1
                name = max(counts, key=counts.get)
            names.append(name)
        
        for ((top, right, bottom, left), name) in zip(boxes, names):
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
        
        cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    while True:
        print("\n[1] Add a new user")
        print("[2] Run face recognition")
        print("[3] Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            person_name = input("Enter the name of the person: ").strip()
            if person_name:
                capture_images(person_name)
                process_images()
            else:
                print("[ERROR] No name entered.")
        elif choice == "2":
            recognize_faces()
        elif choice == "3":
            print("[INFO] Exiting program.")
            break
        else:
            print("[ERROR] Invalid choice. Please enter 1, 2, or 3.")
