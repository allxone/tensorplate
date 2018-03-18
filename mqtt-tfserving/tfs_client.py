import sys

from grpc.beta import implementations
import numpy
import tensorflow as tf

from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2

class Client():
  """Client to forward/receive prediction requests/responses."""

  def __init__(self, hostport, model, version, check_status = True):
    self.host, self.port = hostport.split(":")
    self.model = model
    self.model_version = version
    self.channel = implementations.insecure_channel(self.host, int(self.port))
    self.stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)
    if check_status:
        # TODO: print check_status

  def predict(request):
  """Predict.

  Args:
    request: jpeg binaries.

  Returns:
    The list of detected objects.

  Raises:
    IOError: An error occurred processing request.
  """
  request = predict_pb2.PredictRequest()
  request.model_spec.name = self.model
  request.model_spec.signature_name = 'predict_images'
  request.inputs['image'].CopyFrom(
      tf.contrib.util.make_tensor_proto(image[0], shape=[1, image[0].size]))
  response = stub.Predict(request)
  response_array = numpy.array(
          response.result().outputs['scores'].float_val)
  prediction = numpy.argmax(response)

  return prediction