import cv2


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
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.resize(gray, (500, 500))
                # Detect birds in the gray scale image
                birds = self.birdsCascade.detectMultiScale(
                    gray,
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
    D = DetectBirds("birds2.mp4")
    D.detect()
