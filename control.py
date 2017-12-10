import serial
import time

def serial_connect(port=0):
	s = serial.Serial(port='/dev/ttyUSB%d' % usb, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=None)
	if s.isOpen():
		print('Begin serial connection')
	return s

def transmit_control(serial, angle, distance):
	direction_control  = convert_angle(angle)
	speed_control = convert_distance(distance)
	s.write("%.1f\n" % distance_control))
	s.write("%.1f\n" % speed_control)
	

def convert_angle(angle):
	a = angle + 90
	a *= (255 / 180)
	if a > 255: a = 255
	elif a < 0: a = 0 
	return int(a)


def convert_distance(distance):
	return 127


def main(): 
	input = [1, 0, 2, 1, 0, 0, 2, 1, 1, 1, 2, 1]
	s = serial_connect() 
	for i in input:
		if not s.isOpen():
			break;
		if i == 0:
			print('LEFT')
			s.write('0\n')
		elif i==1:
			print('STRAIGHT')
			s.write('1\n')
		elif i==2:
			print('RIGHT')
			s.write('2\n')
		time.sleep(1)


	s.close()
	exit()


if __name__ == "__main__":
	main()
