FROM python:3.8-slim

COPY . .

RUN  apt-get update \
  && apt-get install -y gnupg2 wget xvfb unzip\
  && rm -rf /var/lib/apt/lists/*

# Adding trusting keys to apt for repositories
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# Adding Google Chrome to the repositories
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# Updating apt to see and install Google Chrome

RUN apt-get -y update
RUN apt-get install -yqq unzip curl

# RUN apt-get install -y xvfb unzip


RUN apt-get install -y google-chrome-stable

# Installing Unzip
RUN apt-get install -yqq unzip

# Download the Chrome Driver
RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \wget https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip -d ./
RUN chmod +x ./chromedriver

# Set display port as an environment variable
ENV DISPLAY=:99

RUN pip install -r requirements.txt


RUN curl -sSL https://sdk.cloud.google.com | bash


COPY googleserviceAcc.json /root/googleserviceAcc.json
COPY boto.txt /root/.boto
EXPOSE 5001

ENTRYPOINT [ "python" ]

CMD ["scraping_api.py"]