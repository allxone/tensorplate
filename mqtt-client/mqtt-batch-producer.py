# import numpy as np
# import cv2

import io
import time
import paho.mqtt.publish as publish
import os, glob
import datetime
import traceback
import math
import random, string
import base64
from time import sleep
from time import gmtime, strftime


inpath = "./files"
mqtthost = "104.154.62.50"
mqttqueue = "tensorplate/samantha/in"

#Read images
try:
 for infile in glob.glob( os.path.join(inpath, "*.jpg") ):  
  f=open(infile)
  fileContent = f.read()
  byteArr = bytearray(fileContent)
  f.close()
  message = byteArr
  publish.single(mqttqueue, payload=message, hostname=mqtthost)
  print('Sent ' + infile)
  time.sleep(10)
finally:
 print('Closing up')