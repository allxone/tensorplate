from flask import Flask, request, Response
import os, sys
import json
#Models import

# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("../models/research")

import numpy as np
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile

from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image

from utils import label_map_util
from utils import visualization_utils as vis_util

#Global Variables
APP_NAME = "tensortraffic-webserver"
#0.0.0.0 to open port to external
HOST = "0.0.0.0"
PORT = 80

#Define Flask Application
app = Flask(APP_NAME)

# What model to download.
MODEL_NAME = 'ssd_mobilenet_v1_coco_2017_11_17'
MODEL_FILE = MODEL_NAME + '.tar.gz'
DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'

# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join('data', 'mscoco_label_map.pbtxt')

NUM_CLASSES = 90


#Setup vars
label_map = None
categories = None
category_index = None

detection_graph = None


'''
Setup method
'''
def setupApplication(app):
	#Check if model is downloaded
	opener = urllib.request.URLopener()
	opener.retrieve(DOWNLOAD_BASE + MODEL_FILE, MODEL_FILE)
	tar_file = tarfile.open(MODEL_FILE)
	for file in tar_file.getmembers():
		file_name = os.path.basename(file.name)
		if 'frozen_inference_graph.pb' in file_name:
			tar_file.extract(file, os.getcwd())

	#Load model in memory
	detection_graph = tf.Graph()
	with detection_graph.as_default():
		od_graph_def = tf.GraphDef()
		with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
			serialized_graph = fid.read()
			od_graph_def.ParseFromString(serialized_graph)
			tf.import_graph_def(od_graph_def, name='')

	label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
	categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
	category_index = label_map_util.create_category_index(categories)

	return label_map, categories, category_index, detection_graph


label_map, categories, category_index, detection_graph = setupApplication(app)

def load_image_into_numpy_array(image):
	(im_width, im_height) = image.size
	return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)


def parse_score_results(threshold, detected_classes, detected_scores):
	image_valid_scores = []
	for idx,score in enumerate(detected_scores):
		if score >= threshold:
			detected_class = detected_classes[idx]
			image_valid_scores.append((detected_class,category_index[detected_class]['name']))
	return image_valid_scores

def score_single_image(image):
	with detection_graph.as_default():
		with tf.Session(graph=detection_graph) as sess:
			# Definite input and output Tensors for detection_graph
			image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
			# Each box represents a part of the image where a particular object was detected.
			detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
			# Each score represent how level of confidence for each of the objects.
			# Score is shown on the result image, together with the class label.
			detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
			detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
			num_detections = detection_graph.get_tensor_by_name('num_detections:0')
			# the array based representation of the image will be used later in order to prepare the
			# result image with boxes and labels on it.
			image_np = load_image_into_numpy_array(image)
			# Expand dimensions since the model expects images to have shape: [1, None, None, 3]
			image_np_expanded = np.expand_dims(image_np, axis=0)
			# Actual detection.
			(boxes, scores, classes, num) = sess.run([detection_boxes, detection_scores,detection_classes, num_detections],
				feed_dict={image_tensor: image_np_expanded})
	return parse_score_results(threshold=0.5, detected_classes=classes[0], detected_scores=scores[0])

@app.route("/scoreImage", methods = ['POST'])
#@accept('multipart/form-data')
def scoreImage():
	#TODO: supported only multipart/form-data passing the image in the array. Should be fixed
	if 'multipart/form-data' in request.headers['Content-Type']:
		#Retrieve image
		data = request.files['image']
		image = Image.open(data)

		response = score_single_image(image)

		#JSONIFY
		data = {}
		for sc in response:
			if sc[1] in data:
				data[sc[1]] += 1
			else:
				data[sc[1]] = 1

		json_data = json.dumps(data)
		return Response(json_data, mimetype='application/json')

#Launch application
if __name__ == '__main__':
	label_map, categories, category_index, detection_graph = setupApplication(app)
	app.run(host=HOST, port=PORT)