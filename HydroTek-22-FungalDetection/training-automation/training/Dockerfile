FROM python:3.8-slim

USER root
ENV LANG C.UTF-8
COPY . /TrainingApi
WORKDIR /TrainingApi



RUN pip install -r requirements.txt
RUN curl -sSL https://sdk.cloud.google.com | bash

COPY googleserviceAcc.json /root/googleserviceAcc.json
COPY boto.txt /root/.boto
EXPOSE 5001

CMD ["python", "train_api.py"]
