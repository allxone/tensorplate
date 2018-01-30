FROM tiangolo/uwsgi-nginx-flask:python3.5

# Copy over and install the requirements
COPY ./requirements.txt /requirements.txt
COPY ./object_detection /object_detection
RUN pip install -r /requirements.txt

COPY ./mqtt.py /mqtt.py
COPY ./flask-server /app

ENV FLASK_PORT 8888
ENV MQTT_SERVER 127.0.0.1
ENV MQTT_SERVER_PORT 1883

#RUN python /mqtt.py
CMD [ "python", "/mqtt.py" ]
