# ARG UBUNTU_VERSION=18.04
# FROM ubuntu:${UBUNTU_VERSION} as base

FROM python:3.8-slim

USER root

# RUN apt-get update && apt-get install -y curl

# See http://bugs.python.org/issue19846

ENV LANG C.UTF-8

# RUN apt-get update && apt-get install -y python3 python3-pip

RUN apt update

RUN apt-get install -y libglib2.0-0 libsm6 libxrender1 libxext6

# RUN python3 -m pip install --upgrade pip setuptools

# RUN ln -s $(which python3) /usr/local/bin/python

# RUN apt-get autoremove -y && apt-get remove -y wget

WORKDIR /detection

EXPOSE 8888

COPY . /detection/

RUN pip install -r requirements.txt

RUN pip install flask==1.1.2

RUN pip install flask_restful

RUN pip install gsutil

RUN pip install pymongo

RUN pip install pymongo[srv]

RUN pip install dnspython

# RUN mkdir /nlp_eval

COPY googleserviceAcc.json /root/googleserviceAcc.json

COPY boto.txt /root/.boto

# COPY . /detection/

RUN cd /

RUN cd /detection

CMD ["python","-u","/detection/detect_api.py"]
