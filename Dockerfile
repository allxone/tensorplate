FROM tiangolo/uwsgi-nginx-flask:python3.5

# Copy over and install the requirements
COPY ./requirements.txt /requirements.txt
COPY ./object_detection /object_detection
COPY ./terraform /terraform
RUN pip install -r /requirements.txt

COPY ./mqtt.py /mqtt.py

COPY ./flask-server /app

RUN python /mqtt.py

