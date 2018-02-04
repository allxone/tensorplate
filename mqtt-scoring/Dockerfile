FROM python:3.5

# Copy over and install the requirements
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./mqtt.py /mqtt.py

ENV SCORING_ADDRESS http://localhost:80
ENV MQTT_SERVER 127.0.0.1
ENV MQTT_SERVER_PORT 188

CMD [ "python", "/mqtt.py" ]
