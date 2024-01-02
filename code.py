import numpy
print(numpy.version.version)
import smbus
import time
import cv2
from pynput.keyboard import Key, Listener
BOARD_I2C_ADDR = 0x40
CHANNEL_0_START = 0x06
CHANNEL_0_END = 0x08
CHANNEL_1_START = 0x0A
CHANNEL_1_END = 0x0C
CHANNEL_2_START = 0x0E
CHANNEL_2_END = 0x10
CHANNEL_3_START = 0x12
CHANNEL_3_END = 0x14
MODE1_REG_ADDR = 0
PRE_SCALE_REG_ADDR = 0xFE
bus = smbus.SMBus(1)
# Enable prescaler change
bus.write_byte_data(BOARD_I2C_ADDR, MODE1_REG_ADDR, 0x10)
# Set prescaler to 50Hz from datasheet calculation
bus.write_byte_data(BOARD_I2C_ADDR, PRE_SCALE_REG_ADDR, 0x80)
time.sleep(.25)
# Enable word writes
bus.write_byte_data(BOARD_I2C_ADDR, MODE1_REG_ADDR, 0x20)
# Set channel start times
bus.write_word_data(BOARD_I2C_ADDR, CHANNEL_0_START, 0)  # 0us
bus.write_word_data(BOARD_I2C_ADDR, CHANNEL_1_START, 0)
bus.write_word_data(BOARD_I2C_ADDR, CHANNEL_2_START, 0)
bus.write_word_data(BOARD_I2C_ADDR, CHANNEL_3_START, 0)
x = 200
y = 69
#while True:

def on_press(key):
	global x,y
	if key== Key.up:
		y+=10
		bus.write_word_data(BOARD_I2C_ADDR,CHANNEL_1_END,y)
		print(y)
	elif key == Key.down:
		y -=10
		bus.write_word_data(BOARD_I2C_ADDR,CHANNEL_1_END,y)
		print(y)
	elif key == Key.left:
		x-=10
		bus.write_word_data(BOARD_I2C_ADDR,CHANNEL_0_END,x)
		print(x)
	elif key == Key.right:
		x+=10
		bus.write_word_data(BOARD_I2C_ADDR,CHANNEL_0_END,x)
		print(x)
def on_release(key):
	if key == Key.esc:
		print("Stopped")
		return False
#with Listener(on_press=on_press,on_release=on_release) as listener:

		#listener.join()
#uncomment the above to use keyboard controls
cam = cv2.VideoCapture(0)
frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

print(f"Frame Width: {frame_width}")
print(f"Frame Height: {frame_height}")

def toservo(deltax,deltay,servo_position_x,servo_position_y):
	
	frame_dimensionx = 620
	frame_dimensiony = 400
	servo_rangex = 520-310
	servo_rangey = 380-250
	servo_position_changex = int(deltax / frame_dimensionx * servo_rangex*0.1)
	servo_position_changey = int(deltay / frame_dimensiony * servo_rangey*0.1)
	
    # Calculate the servo position change based on the proportion and the servo range

	print("Before changeX: ",servo_position_changex,"changeY: ",servo_position_changey)

    # Calculate the new servo position, ensuring it's within the allowed range
	positionx = servo_position_x + servo_position_changex
	positionx = max(310, min(positionx, 520))
	positiony = servo_position_y + servo_position_changey

	positiony = max(250, min(positiony, 380))
	print("position x: ",positionx)
	print("position y: ",positiony)
	return positionx,positiony
    
#display_window = cv2.namedWindow("Faces")
face_cascade = cv2.CascadeClassifier('/home/admin/Desktop/haarcascade_frontalface_default.xml')
#face_cascade = cv2.CascadeClassifier('/home/admin/Desktop/haarcascade_frontalface_alt2.xml')
servo_position_x = 380
servo_position_y = 280
bus.write_word_data(BOARD_I2C_ADDR,CHANNEL_0_END,int(servo_position_x))
bus.write_word_data(BOARD_I2C_ADDR,CHANNEL_1_END,int(servo_position_y))

while True:
	ret, image = cam.read()
	
	if ret:
		image = cv2.flip(image,0)
		#image = frame.array

		#FACE DETECTION STUFF

		gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
		faces = face_cascade.detectMultiScale(gray, 1.5, 3)
		bus.write_word_data(BOARD_I2C_ADDR, CHANNEL_3_END, 0)

		for (x,y,w,h) in faces:
			
			cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2)
			center_of_face_x = x + (w/2)
			center_of_face_y = y + (h/2)
			deltax= (center_of_face_x - (620/2))
			deltay = -(center_of_face_y - (400/2))
			
			xx,yy = toservo(deltax,deltay,servo_position_x,servo_position_y)
			servo_position_x = xx
			servo_position_y = yy

			#296 center screen
			bus.write_word_data(BOARD_I2C_ADDR, CHANNEL_3_END, 400)
			bus.write_word_data(BOARD_I2C_ADDR,CHANNEL_0_END,int(xx))
			bus.write_word_data(BOARD_I2C_ADDR,CHANNEL_1_END,int(yy))
			print("Target Found at x: ",xx,"y: ",yy,"Deltax: ",deltax,"Deltay: ", deltay)
			break
			break
		cv2.imshow("gg",image)
		cv2.waitKey(1)
		
		
