FROM python:3.8-slim
COPY . /app
WORKDIR /app
RUN apt-get update 
RUN apt-get install -y python3-opencv 
RUN pip install -r requirements.txt  
RUN curl -sSL https://sdk.cloud.google.com | bash
COPY googleserviceAcc.json /root/googleserviceAcc.json
COPY boto.txt /root/.boto
WORKDIR /app/yolov5/yolov5
ENTRYPOINT [ "python" ]
CMD ["train_api.py"]