FROM python:3.8

RUN pip install --upgrade pip
COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt
RUN pip install pylint
RUN pip install flake8
RUN pip install mutpy

WORKDIR /
RUN mkdir price_formation
COPY . ./price_formation
ENV WORK_DIR=./price_formation
# RUN mv price_formation/run_mut.py_ price_formation/run_mut.py

RUN chmod +x price_formation/pipelines/docker/run_tests.sh
ENTRYPOINT price_formation/pipelines/docker/run_tests.sh