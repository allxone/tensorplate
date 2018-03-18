import sys, io, json
import numpy as np
import tensorflow as tf
import label_map_util
from grpc.beta import implementations
from PIL import Image
from tensorflow_serving.apis import predict_pb2, prediction_service_pb2

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = '/utils/mscoco_label_map.pbtxt'
NUM_CLASSES = 90

class Client():
  """Client to forward/receive prediction requests/responses."""

  def __init__(self, hostport, model, version, timeout = 60, threshold = 0.5):
    self.host, self.port = hostport.split(":")
    self.model = model
    self.model_version = version
    self.timeout = timeout
    self.threshold = threshold
    self.channel = implementations.insecure_channel(self.host, int(self.port))
    self.stub = prediction_service_pb2.beta_create_PredictionService_stub(self.channel)
    self.category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS)

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
    request = predict_pb2.PredictRequest()
    request.model_spec.name = self.model
    request.model_spec.signature_name = 'serving_default'
    request.inputs['inputs'].CopyFrom(
        tf.contrib.util.make_tensor_proto(image_np_expanded, shape=[1, image.size[0], image.size[1], 3]))
    response = self.stub.Predict(request, self.timeout)
    json_data = parse_score_results(self, self.threshold, 
      tf.contrib.util.make_ndarray(response.outputs['detection_classes'])[0], 
      tf.contrib.util.make_ndarray(response.outputs['detection_scores'])[0]
    )

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
  data = {}
  for sc in image_valid_scores:
    if sc[1] in data:
      data[sc[1]] += 1
    else:
      data[sc[1]] = 1
  json_data = json.dumps(data)
  return json_data