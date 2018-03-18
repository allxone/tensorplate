FROM allxone/tensorflow-serving-devel-gpu
LABEL maintainer="allxone@hotmail.com"

# OPEN ISSUE: missing variables https://github.com/tensorflow/models/issues/1988
RUN mkdir -p /model/1 && curl http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v1_coco_2017_11_17.tar.gz -o ssd_mobilenet_v1_coco_2017_11_17.tar.gz && \
    tar -C /model/1 --strip-components=2 -xvf ssd_mobilenet_v1_coco_2017_11_17.tar.gz ssd_mobilenet_v1_coco_2017_11_17/saved_model/ && \
    rm ssd_mobilenet_v1_coco_2017_11_17.tar.gz
EXPOSE 9000
CMD ["tensorflow_model_server","--port=9000","--model_name=model","--model_base_path=/model/"]