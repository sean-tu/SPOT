"""SPOT: Sean's Point Optical Tracker - Control module

Converts target location information from vision module (angle, distance) to pulses, which are transmitted by serial USB connection to control servos on a BOE-Bot.
"""

__author__= "Sean Reedy"

import serial
import time
from collections import deque


PORT = 1

class Controller:
	"""This class manages the serial connection to the BOE-Bot and commands."""
	def __init__(self, port=0):
		self.serial = serial_connect(port)
		self.detections = deque(maxlen=50)
		self.prev_command = (750, 750)
		self.time_since_last_detection = 0

	def process_detection(self, angle, distance):
		"""Based on detection from vision module, this function determines and transmits the next command."""
		if angle is not None and distance is not None: 
			self.detections.append([angle, distance])	# record detection info	
			command = get_command(angle, distance)
		else:
			self.detections.append([])
			self.time_since_last_detection += 1
			command = self.prev_command
		if self.serial.isOpen():
			transmit_command(self.serial, command)
			self.prev_command = command
	
	def close(self):
		"""End the serial connection."""
		if self.serial.isOpen():
			self.serial.close()
			print("Serial connection closed.")
		else:
			print("Serial connection is already closed.")


def serial_connect(port=0):
	#s = serial.Serial(port='/dev/ttyUSB%d' % port, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=None)
	s = serial.Serial('/dev/ttyUSB%d' % port, 9600)
	if s.isOpen():
		print('Serial connection opened.')
	else:
		print('Serial connection failed.')
	return s

def transmit_command(s, command):
	c = command
	if c == 0:
		s.write('0\n')
	elif c == 1:
		s.write('1\n')
	elif c==2:
		s.write('2\n')
	
def get_command(angle, dist):
	angle_diff = 45
	if angle > angle_diff:
		return 2
	elif angle < -angle_diff: 
		return 0
	else:
		return 1

def transmit_command2(s, command):
	(pulse1, pulse2) = command
	bc1 = byte_command(pulse1)
	bc2 = byte_command(pulse2)
	transmit_bytes(s, bc1)
	transmit_bytes(s, bc2)
	print(bc1, bc2)

def byte_command(pulse):
	"""Translates pulses to 8-bit values in range [0, 255]"""
	command  =  pulse
	bytes = str(command).zfill(3)
	return bytes 
	

def transmit_bytes(s, bytes):
	for b in bytes:
		s.write('%s\n' % b)
		print('%s\n' % b)


def get_command2(angle, distance):
	"""Translates angle and distance to servo motor pulse widths"""
	rotate_right = (770, 770)
	rotate_left = (730, 730)
	full_ahead = (850, 650)
	half_ahead = (775, 725)
	slight_right = (850, 700)
	right = (850, 725)
	left = (775, 650) 
	slight_left = (800, 650)
	stop = (750, 750) 

	full= [full_ahead, slight_right, slight_left]
	mid = [half_ahead, right, left]
	low = [stop, rotate_right, rotate_left] 

	commands = [low, mid, full] 

	speed_level = get_speed(distance)
	direction = get_direction(angle)	
	
	command = commands[speed_level][direction]
	print('Command: %s, angle: %d, distance: %d' % (command, angle, distance))
	return command 
		

def get_direction(angle):
	if angle < -25:
		return -1
	if angle > 25:
		return 1
	return 0


def get_speed(distance):
	if distance > 270: return 2 
	elif distance > 40: return 1
	return 0 


def convert_angle(angle):
	max_out = 1500
	min_out = 1
	a = angle + 90
	a *= (1500 / 180)
	if a > max_out: a = max_out
	elif a < min_out: a = min_out 
	return int(a)


def convert_distance(distance):
	return 127


def main():

	s = serial_connect(PORT)
	while True: 
		c = input("Command:")
		if c == 0:
			s.write('0\n')
		elif c == 1:
			s.write('1\n')
		elif c==2:
			s.write('2\n')
		else:
			break
	s.close()
	exit()


def main2(): 
	"""Test function."""
	TRANSMIT = 1

	if TRANSMIT: 
		s = serial_connect(PORT) 

	while True:
		p1 = input("Enter pulse 1: ")
		if p1 == 0: 
			break

		p2 = input("Enter pulse 2: ")
		if p2 == 0:
			break
		if TRANSMIT: 
			transmit_command(s, (p1, p2))
			time.sleep(1)
		else:
			print('%d %d' % (byte_command(p1), byte_command(p2)))
	if TRANSMIT: 
		s.close()
	exit()


if __name__ == "__main__":
	main()
