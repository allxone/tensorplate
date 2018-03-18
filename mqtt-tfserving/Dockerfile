FROM python:3.5

# Copy over and install the requirements
COPY ./requirements.txt /requirements.txt
COPY ./mqtt-tfserving.py /mqtt-tfserving.py
COPY ./utils /utils

RUN pip install -r /requirements.txt

ENV SCORING_ADDRESS localhost:9000
ENV MQTT_SERVER 127.0.0.1
ENV MQTT_SERVER_PORT 1883
ENV MODEL_NAME model
ENV MODEL_VERSION 1

CMD [ "python", "/mqtt-tfserving.py" ]
