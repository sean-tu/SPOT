"""SPOT: Simple Optical Point Tracker - Vision module

This module performs visual identification of laser pointers using the OpenCV library on a Raspberry Pi 2. It uses video input from a Pi Camera module.

Identification is performed in four main steps. Firstly, the image undergoes Gaussian blurring for smoothing and noise reduction. Next, a mask is created for values within a specified color range, to isolate bright and red regions. The mask is then eroded to reduce noise and protrusions, and dilated to fill in the gaps. From the modified mask, contours are calculated, and filtered by area. The center of the remaining contour closest to the previous detection is chosen as the new detection.

This process requires tuning the parameters of Gaussian blur radius, color thresholds, and erosion/dilation iterations to achieve an acceptable rate of detections. A balance between type 1 and type 2 errors was eventually achieved. 

The output of the vision module is a tuple, specifying the distance from the detected point to the origin (center, bottom pixel) and the angle from the centerline. These values are used for controlling a robot to follow the laser pointer.  
"""

__author__ = "Sean Reedy" 

import cv2
import time
import math
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import numpy as np

from control import Controller

# CONFIG 
PORT = 0
width = 640
height = 480

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--d", "--display", help= "video")
	args = parser.parse_args()

	# Config
	DISPLAY = 1
	FLIP = 0
	RECORD = 1 
	CONTROL = 1 

	# Pi Cam setup
	cam = PiCamera()
	resolution = (width, height)
	cam.resolution = resolution
	cam.framerate = 32
	#cam.brightness = 40
	raw = PiRGBArray(cam, size=resolution)
	time.sleep(0.1)
	
	# BOE-BOT serial connection
	controller = Controller(PORT)

	# Record a quick test video
	#cam.start_recording('testA.avi')
	#print('Recording start')
	#time.sleep(8)
	#cam.stop_recording()
	#print('Rec end')

	# RECORD VIDEO - suprisingly difficult
	save_path = 'capture/img'
	#record_video(cam, 10)

	origin = (width // 2, height)
        if FLIP:
            origin = (width // 2, 0)

	print(resolution, origin)
	t = 0
	prev = origin
	for frame in cam.capture_continuous(raw, format="bgr", use_video_port=True):
		img = frame.array
		if img is None:
			print('Stream ended. t=%d' %t)
			break
		if t == 10:
			cv2.imwrite('test.jpg', img)	

		pt = detect(img, prev)
		if pt is not None:
			img = mark(img, pt, origin)
			d = dist(pt, origin)
			x = pt[0] - width//2
			y = height - pt[1]
			theta = angle_offset(x, y)
			msg = controller.process_detection(theta, d, FLIP)
			#print("Distance: %d, Angle: %d, Time: %d" % (d, theta, t))
			prev = pt
		else:
			msg = controller.process_detection(None, None, FLIP)
		print(msg)		

		if DISPLAY: 
			if FLIP: 
				img = cv2.flip(img, 0)
			cv2.imshow('pi video', img)
		
		if RECORD:
			cv2.imwrite('capture/img%d.jpg' % t, img)
		raw.truncate(0)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
		t += 1
	controller.close()


def morph(img):
	"""First erode the mask to remove noise, the dilate to fill missing points"""
	#img = cv2.erode(img, None, iterations=1)
	img = cv2.dilate(img, None, iterations=3)
	return img


def mask_laser(img):
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	red_hsv_min = np.array([170, 0, 0])
	red_hsv_max = np.array([255, 255, 255])
	
	t_min = 190
	t_max = 200
	red_bgr_min = np.array([0, 0, t_min])
	red_bgr_max = np.array([t_max, t_max, 255])

	bright_hsv_min = np.array([160, 0, 170])
	bright_hsv_max = np.array([255, 40, 255])

	#mask1 = cv2.inRange(hsv, red_hsv_min, red_hsv_max)
	mask1 = cv2.inRange(img, red_bgr_min, red_bgr_max)
	mask2 = cv2.inRange(hsv, bright_hsv_min, bright_hsv_max)

	mask = cv2.addWeighted(mask1, 1, mask2, 1, 0)
	return mask 

def dist(p1, p2):
	"""Returns the Euclidean distance between two points."""
	x1, y1 = p1
	x2, y2 = p2
	return int(math.sqrt((x1-x2)**2 + (y1-y2)**2))


def angle_offset(x, y):
	rads = math.atan2(y, x)
	deg = int(math.degrees(rads))
	if deg < 90:
		deg = 90 - deg
	elif deg >= 90:
		deg = deg - 90
	if x < 0:
		deg *= -1
	return deg	


def mark(img, pt, origin):
        """Draw a circle over the point and a line to the origin."""
	if pt is not None:
		cv2.circle(img, pt, 5, (255, 0, 0), 1)	
		cv2.line(img, origin, pt, 255, 2)
	return img


def record_video(camera, time):
	camera.start_recording('testvid1.h264')
	print('Recording started')
	camera.wait_recording(time)
	camera.stop_recording()
	print('Recording ended')


def contour_select(mask):
        """Extract contours from a mask and examine their area."""
	contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	if len(contours) == 0: return None
	for c in contours[0]:
		area = cv2.contourArea(c)
		#print(area)
	return contours[0]

	
def get_point(contours, prev):
        """From a set of contours, determine the center of each contour using its moments and select the center with the point nearest the previously detected point as the new detection point."""
	if len(contours) > 0:
		centers = []
		for c in contours:
			M = cv2.moments(c)
			if M['m00'] != 0:
				center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))
				centers.append(center)
		if len(centers) > 0:
			pt = min(centers, key=lambda x: dist(x, prev))
			return pt
	return None


def detect(img, prev):
	img = cv2.GaussianBlur(img,  (3, 3), 0)
	mask = mask_laser(img)
	#mask = morph(mask)
	masked = cv2.bitwise_and(img, img, mask=mask)
	#cv2.imshow('Masked', mask)
	contours = contour_select(mask)
	pt = get_point(contours, prev)
	return pt


if __name__ == "__main__":
	main()

