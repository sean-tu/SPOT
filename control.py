import serial
import time

class Control:

	__init__(self, port=0):
		
def serial_connect(port=0):
	s = serial.Serial(port='/dev/ttyUSB%d' % usb, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=None)
	if s.isOpen():
		print('Serial connection opened.')
	else:
		print('Serial connection failed.')
	return s


def transmit_control(serial, angle, distance):
	(pulse1, pulse2) = get_command(angle, distance)
	s.write("%d\n" % pulse1)
	s.write("%d\n" % pulse2)
	

def get_command(angle, distance):
	rotate_right = (770, 770)
	rotate_left = (730, 730)
	full_ahead = (850, 650)
	half_ahead = (775, 725)
	slight_right = (850, 700)
	right = (850, 725)
	left = (775, 650) 
	slight_left = (800, 600)
	stop = (750, 750) 

	full_ahead = [full_ahead, slight_right, light_left]
	mid = [half_ahead, right, left]
	low = [stop, rotate_right, rotate_left] 

	commands = [low, mid, full] 

	speed_level = get_speed(distance)
	direction = get_direction(angle)	
	
	command = commands[speed_level][direction]
	print(command, angle, distance)
	return command 
		

def get_speed(distance):
	if distance > 170: return 2 
	elif distance > 10: return 1
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
