FROM python:3.8-slim

COPY . /pest-detection
WORKDIR /pest-detection


# ENV MONGO_USER=hydrotekai
# ENV MONGO_PWD=Kansas2020!m
# ENV MONGO_HOST=cluster0.x5wba.gcp.mongodb.net

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
       apt-get -y --quiet --fix-missing install python3-opencv \
    && apt-get -y autoremove \
    && apt-get clean autoclean 
RUN pip install -r requirements.txt
RUN curl -sSL https://sdk.cloud.google.com | bash

COPY googleserviceAcc.json /root/googleserviceAcc.json
COPY boto.txt /root/.boto
EXPOSE 5001

ENTRYPOINT [ "python" ]

CMD ["detect_api.py"]