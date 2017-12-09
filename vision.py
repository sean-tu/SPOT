import cv2
import time
import math
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse


width = 640
height = 480

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--d", "--display", help= "video")
	parser.add_argument("--v", "--video", help = "path to video")
	args = parser.parse_args()

	# Config
	DISPLAY = 1
	FLIP = 0

	# Pi Cam setup
	cam = PiCamera()
	resolution = (width, height)
	cam.resolution = resolution
	cam.framerate = 32
	raw = PiRGBArray(cam, size=resolution)
	time.sleep(0.1)
	
	# Record a quick test video
	#cam.start_recording('testA.avi')
	#print('Recording start')
	#time.sleep(8)
	#cam.stop_recording()
	#print('Rec end')

	origin = (width // 2, height)
	print(resolution)
	print(origin)
	t = 0
	for frame in cam.capture_continuous(raw, format="bgr", use_video_port=True):
		img = frame.array
		if img is None:
			print('Stream ended. t=%d' %t)
			break
		if t == 10:
			cv2.imwrite('test.jpg', img)	

			
		pt = detect(img)
		if pt is not None:
			img = mark(img, pt, origin)
			d = dist(pt, origin)
			x = pt[0] - width//2
			y = height - pt[1]
			theta = angle_offset(x, y)
			print("Distance: %d, Angle: %d, Time: %d" % (d, theta, t))

		if DISPLAY: 
			if FLIP: 
				img = cv2.flip(img, 0)
			cv2.imshow('pi video', img)
		
		raw.truncate(0)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
		t += 1


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
	if pt is not None:
		cv2.circle(img, pt, 5, (255, 0, 0), 1)	
		cv2.line(img, origin, pt, 255, 2)
	return img


def detect(img):
	img = cv2.GaussianBlur(img, (5, 5), 0)
	red = img[:, :, 2]
	(_, maxVal, _, maxLoc) = cv2.minMaxLoc(red)
	threshold = 200 
	if maxVal > threshold:
		return maxLoc
	return None


if __name__ == "__main__":
	main()

