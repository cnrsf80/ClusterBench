#x86
#docker build -t hhoareau/cluster_bench_x86 .
#docker push hhoareau/cluster_bench_x86:latest
#docker run -p 5000:5000 -t hhoareau/cluster_bench_x86:latest

#arm
#docker build -t hhoareau/cluster_bench_arm .
#docker push hhoareau/cluster_bench_arm:latest

FROM python:3
#FROM arm32v7/python

EXPOSE 5000

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app

CMD python app.py