import cv2
import imutils


class DetectBirds(object):
    def __init__(self, camera_url, mx_num_birds=6):
        self.cap = cv2.VideoCapture(camera_url)
        self.birdsCascade = cv2.CascadeClassifier("data/cascade.xml")
        self.MAX_NUM_BIRDS = mx_num_birds
        self.running = True

    def detect(self):
        while self.running:
            # Capture frame-by-frame from a video
            ret, frame = self.cap.read()
            if ret:
                # convert the frame into gray scale for better analysis
                dim = 1200
                blur_kernel = (5, 5)
                resized = imutils.resize(frame, width=dim)
                gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
                blur = cv2.GaussianBlur(gray, blur_kernel, 0)
                closed = cv2.morphologyEx(blur, cv2.MORPH_CLOSE, (3, 3))
                # Detect birds in the gray scale image
                birds = self.birdsCascade.detectMultiScale(
                    closed,
                    scaleFactor=1.4,
                    minNeighbors=50,
                    # minSize=(10, 10),
                    maxSize=(300, 300),
                    flags=cv2.CASCADE_SCALE_IMAGE,
                )
                if len(birds) >= self.MAX_NUM_BIRDS:
                    print("Detected {0} Birds".format(len(birds)))

                # Draw a rectangle around the detected birds approaching the farm
                for (x, y, w, h) in birds:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 200, 0), 2)

                # Display the resulting frame
                cv2.imshow("frame", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    self.running = False
            else:
                self.running = False

        # When everything done, release the capture and go back take another one
        self.cap.release()
        cv2.destroyAllWindows()


# Create the haar cascade that reads the properties of objects to be detected from an already made xml file.
# The xml file is generated as a result of machine learning from all possible object samples provided.


if __name__ == "__main__":
    D = DetectBirds("birds.mp4")
    D.detect()
