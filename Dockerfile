FROM python:3.8-slim
USER root
ENV LANG C.UTF-8
WORKDIR /object
EXPOSE 6003
RUN pip install pandas
RUN pip install imutils
RUN pip install tensorflow
RUN pip install tensorflow-object-detection-api
RUN pip install keras
#RUN apt-get install curl -y
RUN apt-get update
RUN pip install opencv-python
RUN pip install flask===1.1.2
RUN pip install flask_restful
COPY . /object
CMD ["python","-u", "api.py", "--host=0.0.0.0"]
