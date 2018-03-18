import sys, io, json
import numpy as np
import tensorflow as tf
import label_map_util
from grpc.beta import implementations
from PIL import Image
from tensorflow_serving.apis import predict_pb2k, prediction_service_pb2

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = '/utils/mscoco_label_map.pbtxt'
NUM_CLASSES = 90

class Client():
  """Client to forward/receive prediction requests/responses."""

  def __init__(self, hostport, model, version):
    self.host, self.port = hostport.split(":")
    self.model = model
    self.model_version = version
    self.channel = implementations.insecure_channel(self.host, int(self.port))
    self.stub = prediction_service_pb2.beta_create_PredictionService_stub(self.channel)
    self.label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
    self.categories = label_map_util.convert_label_map_to_categories(self.label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
    self.category_index = label_map_util.create_category_index(self.categories)

  def predict(self, image_data):
    """Predict.

    Args:
      request: image bytes

    Returns:
      The list of detected objects.

    Raises:
      IOError: An error occurred processing request.
    """
    
    # Convert image to array
    image = Image.open(io.BytesIO(image_data))
    image_np = load_image_into_numpy_array(image)

    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
    image_np_expanded = np.expand_dims(image_np, axis=0)

    # Create predict request
    request = self.stub.PredictRequest()
    request.model_spec.name = self.model
    request.model_spec.signature_name = 'serving_default'
    request.inputs['inputs'].CopyFrom(
        tf.contrib.util.make_tensor_proto(image_np_expanded, shape=[1, image.size, 3]))
    response = self.stub.Predict(request)
    json_data = parse_score_results(0.5, response.outputs['detection_classes'], response.outputs['detection_scores'])

    return json_data

def load_image_into_numpy_array(image):
	(im_width, im_height) = image.size
	return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)

def parse_score_results(self, threshold, detected_classes, detected_scores):
	image_valid_scores = []
	for idx,score in enumerate(detected_scores):
		if score >= threshold:
			detected_class = detected_classes[idx]
			image_valid_scores.append((detected_class, self.category_index[detected_class]['name']))

  #JSONIFY
  data = {}
  for sc in image_valid_scores:
    if sc[1] in data:
      data[sc[1]] += 1
    else:
      data[sc[1]] = 1

  json_data = json.dumps(data)
	return json_data