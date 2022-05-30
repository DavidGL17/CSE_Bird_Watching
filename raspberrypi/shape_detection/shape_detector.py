# import the necessary packages
import cv2
import imutils
import numpy as np
from skimage.metrics import structural_similarity as compare_ssim


class ShapeDetector:

    def __init__(self):
        pass

    def detect(self, c):
        # initialize the shape name and approximate the contour
        shape = "unidentified"
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)

        # if the shape is a triangle, it will have 3 vertices
        if len(approx) == 3:
            shape = "triangle"
        # if the shape has 4 vertices, it is either a square or a rectangle
        elif len(approx) == 4:
            # compute the bounding box of the contour and use the bounding box to compute the aspect ratio
            (x, y, w, h) = cv2.boundingRect(approx)
            ar = w / float(h)
            # a square will have an aspect ratio that is approximately equal to one, otherwise, the shape is a rectangle
            shape = "square" if ar >= 0.95 and ar <= 1.05 else "rectangle"
        # if the shape is a pentagon, it will have 5 vertices
        elif len(approx) == 5:
            shape = "pentagon"
        elif len(approx) == 6 :
            shape = "hexagone"
        elif len(approx) == 7:
            shape = "heptagone"
        elif len(approx) == 8:
            shape = "hexagone"
        elif len(approx) == 9:
            shape = "nonagone"
        # otherwise, we assume the shape is a circle
        else:
            shape = "circle"

        # return the name of the shape
        return shape

def show(name,image):
    cv2.imshow(name, image)
    cv2.waitKey(0)


if __name__ == "__main__":
    running = True
    cap = cv2.VideoCapture("birds1.mp4")
    lower_range = np.array([17, 15, 100])
    upper_range = np.array([62, 174, 250])
    have_last_image = 0
    img_counter = 0

    while running:
        ret, frame = cap.read()
        # essayer de travailler avec uniquement une couleur (que bleu par exemple)
        # Extraire R G et B et appliquer des filtres sur chacune
        # tester sur HSV (extraire H S et V)
        # Ycbcr idem
        
        if ret:
            if img_counter != 30:
                img_counter += 1
                continue
            else:
                img_counter = 0
            if have_last_image == 0:
                have_last_image = 1
                last_image = frame
                continue
            # load the image and resize it to a smaller factor so that the shapes can be approximated better
            dim = 1200
            blur_kernel = (5,5)
            canny_thr1 = 20
            canny_thr2 = 150
            canny_aperture = 3
            resized = imutils.resize(frame, width=dim)
            last_image_resized = imutils.resize(last_image, width=dim)
            show("resized", resized)

            ratio = frame.shape[0] / float(resized.shape[0])
            # hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
            # mask = cv2.inRange(hsv, lower_range, upper_range)
            # convert the resized image to grayscale, blur it slightly, and threshold it
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray,blur_kernel,0)
            show("blur", blur)
            canny = cv2.Canny(blur, canny_thr1, canny_thr2, canny_aperture)
            show("canny", canny)
            dilate = cv2.dilate(canny, (3,3), iterations=0)
            show("dilate", dilate)
            last_image_gray = cv2.cvtColor(last_image_resized, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(last_image_gray, blur_kernel,0)
            canny = cv2.Canny(blur, canny_thr1, canny_thr2, canny_aperture)
            last_image_dilate = cv2.dilate(canny, (3,3), iterations=0)
            (score, diff) = compare_ssim(dilate, last_image_dilate, full=True)
            show("diff", diff)
            diff = (diff * 255).astype("uint8")
            show("diff uint8", diff)
            print("SSIM: {}".format(score))
            closed = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, (3,3))
            show("closed", closed)
            thresh = cv2.threshold(closed, 90, 255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
            show("thresh", thresh.copy())
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            # for c in cnts:
            #     # compute the bounding box of the contour and then draw the
            #     # bounding box on both input images to represent where the two
            #     # images differ
            #     (x, y, w, h) = cv2.boundingRect(c)
            #     cv2.rectangle(last_image_resized, (x, y), (x + w, y + h), (0, 0, 255), 2)
            
            # blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            # thresh = cv2.threshold(blurred, 90, 255, cv2.THRESH_BINARY)[1]
            # # find contours in the thresholded image and initialize the shape detector
            # cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            # cnts = imutils.grab_contours(cnts)
            sd = ShapeDetector()

            # loop over the contours
            for c in cnts:
                # compute the center of the contour, then detect the name of the shape using only the contour
                M = cv2.moments(c)
                if  M["m00"] == 0:
                    continue
                cX = int((M["m10"] / M["m00"]) * ratio)
                cY = int((M["m01"] / M["m00"]) * ratio)
                shape = sd.detect(c)
                # multiply the contour (x, y)-coordinates by the resize ratio, then draw the contours and the name of the shape on the image
                c = c.astype("float")
                c *= ratio
                c = c.astype("int")
                cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
                cv2.putText(frame, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255, 255, 255), 2)

            
            # Display the resulting frame
            cv2.imshow("frame", frame)
            if cv2.waitKey(0) & 0xFF == ord("q"):
                running = False
            last_image = frame
            cv2.destroyAllWindows()
        else:
            running = False

    # When everything done, release the capture and go back take another one
    cap.release()
    cv2.destroyAllWindows()
