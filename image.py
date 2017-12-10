import cv2
import numpy as np

img = cv2.imread('Video_screenshot_09.12.2017.png')
hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
hsl_img = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
cv2.namedWindow('image')


def get_color(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        bgr = img[y, x]
        hsv = hsv_img[y,x]
        hsl = hsl_img[y, x]
        print("BGR: %s   | HSV: %s   | HSL: %s" % (bgr, hsv, hsl))


cv2.setMouseCallback('image', get_color)

while 1:
    cv2.imshow('image', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cv2.destroyAllWindows()
