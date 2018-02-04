FROM tiangolo/uwsgi-nginx-flask:python3.5

# Copy over and install the requirements
COPY ./requirements.txt /requirements.txt
COPY ./flask-server /app
RUN apt-get update && apt-get install -y protobuf-compiler python-pil python-lxml
RUN pip install -r /requirements.txt
RUN cd / && git clone https://github.com/tensorflow/models
RUN cd /models/research && protoc object_detection/protos/*.proto --python_out=.