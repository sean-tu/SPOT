import numpy as np
import cv2
import math


def main():
    print(cv2.__version__)
    # Open video capture source, 0 is webcam
    source = '/home/sean/Desktop/laser2.avi'
    cap = cv2.VideoCapture(source)
    width = int(cap.get(3))
    height = int(cap.get(4))
    origin = (width // 2, height - 45)
    print("Size: %d x %d\nOrigin: %d, %d" % (width, height, origin[0], origin[1]))
    t = -1

    # Save video
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('demo_vid.avi', fourcc, 20.0, (width, height))

    while cap.isOpened():
        _, frame = cap.read(10)
        if frame is None:
            print("Video stream ended")
            break

        t += 1  # time

        # red = frame[:, :, 2]                            # examine the red color channel of RGB image
        # red = cv2.medianBlur(red, 5)                    # blur to reduce noise
        # (_, maxVal, _, maxLoc) = cv2.minMaxLoc(red)     # locate the pixel with the highest intensity value
        # mask = cv2.inRange(red, maxVal, 255)

        # frame = cv2.medianBlur(frame, 5)
        frame = cv2.GaussianBlur(frame, (5, 5), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Red range
        target_min = np.array([170, 0, 0])
        target_max = np.array([255, 255, 255])

        # White range
        target_lower_min = np.array([0, 0, 0])
        target_lower_max = np.array([255, 12, 255])

        # Create masks
        mask1 = cv2.inRange(hsv, target_min, target_max)
        mask2 = cv2.inRange(hsv, target_lower_min, target_lower_max)
        mask = cv2.addWeighted(mask1, 1, mask2, 1, 0)

        #  Draw origin and centerline
        # cv2.circle(frame, origin, 10, 255, 20)
        # cv2.line(frame, (width//2, height), (width//2, 0), 0, 2)
        # draw_grid(frame, 120, 120, width, height)


        # cv2.imshow("Video", frame)
        #
        # threshold = 220
        # if maxVal > threshold:
        #     # cv2.circle(frame, maxLoc, 5, (255, 0, 0), 2)
        #     # cv2.line(frame, origin, maxLoc, 255, 3)
        #     dist = distance(origin, maxLoc)
        #     x = maxLoc[0] - width//2
        #     y = height - maxLoc[1]
        #     theta = angle(x, y)
        #     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        #     bgr_val = frame[maxLoc]
        #     hsv_val = hsv[maxLoc]
        #     print(bgr_val, hsv_val)
        #     # print(dist, theta, t)
        #     string = str(dist) + ", " + str(theta) + "deg"
        #     # cv2.rectangle(frame, (0, 0), (300, 100), (255, 255, 255), thickness=-1)
        #     cv2.putText(frame, string, (maxLoc[0] - 5, maxLoc[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2, cv2.LINE_AA)
        # else:
        #     print("None")
        #
        # out.write(frame)
        #
        mask = morph(mask)
        contours(mask)
        masked = cv2.bitwise_and(frame, frame, mask=mask)
        cv2.imshow('Masked', mask)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release capture and clean up windows
    cap.release()
    cv2.destroyAllWindows()


def contours(img):
    conts = cv2.findContours(img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    print conts

def morph(img):
    img = cv2.erode(img, None, iterations=2)
    img = cv2.dilate(img, None, iterations=2)
    return img


def detect(img):
    img = cv2.GaussianBlur(img, (5, 5), 0)
    red = img[:, :, 2]                            # examine the red color channel of RGB image
    (_, maxVal, _, maxLoc) = cv2.minMaxLoc(red)     # locate the pixel with the highest intensity value
    mask = cv2.inRange(red, maxVal, 255)

    # Draw origin and centerline
    cv2.circle(img, origin, 10, 255, 20)
    cv2.line(frame, (width//2, height), (width//2, 0), 0, 2)
    draw_grid(frame, 120, 120, width, height)


    cv2.imshow("Video", frame)

    threshold = 220
    if maxVal > threshold:
        # cv2.circle(frame, maxLoc, 5, (255, 0, 0), 2)
        # cv2.line(frame, origin, maxLoc, 255, 3)
        dist = distance(origin, maxLoc)
        x = maxLoc[0] - width//2
        y = height - maxLoc[1]
        theta = angle(x, y)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        bgr_val = frame[maxLoc]
        hsv_val = hsv[maxLoc]
        # print(dist, theta, t)
        string = str(dist) + ", " + str(theta) + "deg"
        # cv2.rectangle(frame, (0, 0), (300, 100), (255, 255, 255), thickness=-1)
        cv2.putText(frame, string, (maxLoc[0] - 5, maxLoc[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2, cv2.LINE_AA)
    else:
        print("None")


def detect2(img):
    frame = cv2.GaussianBlur(img, (5, 5), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Red range
    target_min = np.array([170, 0, 0])
    target_max = np.array([255, 255, 255])

    # White range
    target_lower_min = np.array([0, 0, 0])
    target_lower_max = np.array([255, 12, 255])

    # Create masks
    mask1 = cv2.inRange(hsv, target_min, target_max)
    mask2 = cv2.inRange(hsv, target_lower_min, target_lower_max)
    mask = cv2.addWeighted(mask1, 1, mask2, 1, 0)


def draw_grid(frame, x_step, y_step, width, height):
    for x in range(0, width, x_step):
        cv2.line(frame, (x, height), (x, 0), (0, 0, 0), 1)

    for y in range(0, height, y_step):
        cv2.line(frame, (width, y), (0, y), (0, 0, 0), 1)


def angle(x, y):
    """Returns the angle between the point and the center line relative to the origin.

    A negative value indicates a detection left of the center line."""
    rads = math.atan2(y, x)
    deg = int(math.degrees(rads))
    if deg < 90:
        deg = 90 - deg
    elif deg >= 90:
        deg = deg - 90

    if x < 0:
        deg *= -1
    return deg


def distance(p1, p2):
    """Returns the Euclidean distance between two points."""
    x1, y1 = p1
    x2, y2 = p2
    return int(math.sqrt((x1-x2)**2 + (y1-y2)**2))


if __name__ == "__main__":
    main()
