import cv2

cap = cv2.VideoCapture(0)  # Try changing 0 → 1 or 2 if using an external camera

if not cap.isOpened():
    print("🚨 ERROR: Camera failed to initialize. Check if another process is using it.")
    exit()

def get_camera_frame():
    """ Returns the latest camera frame. """
    ret, frame = cap.read()
    if not ret:
        return None
    return frame

if __name__ == "__main__":
    while True:
        frame = get_camera_frame()
        if frame is None:
            print("🚨 ERROR: No camera frame detected. Camera might be in use by another process.")
            continue

        cv2.imshow("Live Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
