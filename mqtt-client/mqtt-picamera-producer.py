import io
import time
import picamera
import paho.mqtt.publish as publish
import os
import datetime
import traceback
import math
import random, string
import base64
from time import sleep
from time import gmtime, strftime

def randomword(length):
 return ''.join(random.choice(string.lowercase) for i in range(length))


def send(camera):
 img_name = 'pi_image_{0}_{1}.jpg'.format(randomword(3),strftime("%Y%m%d%H%M%S",gmtime()))
 
#Capture Image from Pi Camera
 camera.capture(img_name,resize=(320,240))
  
 f=open(img_name)
 fileContent = f.read()
 byteArr = bytearray(fileContent)
 f.close()
 message = byteArr
 publish.single("tensorplate/samantha/in",payload=message, hostname="130.211.134.220")
 os.remove(img_name)
import glob
camera = picamera.PiCamera()

try:
 for i in range(100):
  send(camera)
  time.sleep(10)
  print(i)

finally:
 camera.close()
