import cv2

cap = cv2.VideoCapture(0)

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
            continue

        cv2.imshow("Live Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
