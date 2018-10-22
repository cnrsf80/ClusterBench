#x86
#docker build -t hhoareau/cluster_bench_x86 . & docker push hhoareau/cluster_bench_x86:latest
#docker push hhoareau/cluster_bench_x86:latest
#docker pull hhoareau/cluster_bench_x86:latest
#test:docker run -p 5000:5000 -t hhoareau/cluster_bench_x86:latest
#docker rm -f cluster_bench
#deploy:docker run -p 5000:5000 --name cluster_bench -d hhoareau/cluster_bench_x86:latest
#test SocketServer : http://45.77.160.220:5000

#arm
#docker build -t hhoareau/cluster_bench_arm .
#docker push hhoareau/cluster_bench_arm:latest

FROM python:3
#FROM arm32v7/python

EXPOSE 5000

RUN mkdir /app
RUN mkdir /app/datas
RUN mkdir /app/clustering
RUN mkdir /app/saved
RUN mkdir /app/metrics

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app

CMD python app.py