#install docker
#sudo curl -sSL get.docker.com | sh

#x86
FROM python:3
#docker build -t f80hub/cluster_bench_x86 . & docker push f80hub/cluster_bench_x86:latest
#docker rm -f clusterbench && docker pull f80hub/cluster_bench_x86:latest && docker run --restart=always -v /datas:/app/datas -v /clustering:/app/clustering -p 5000:5000 --name clusterbench -d f80hub/cluster_bench_x86:latest

#arm
#FROM arm64v8/python
#FROM armhf/python
#FROM resin/rpi-raspbian:stretch

# Install dependencies
#RUN sudo apt-get update -y
#RUN sudo apt-get dist-upgrade
#RUN sudo apt-get install -y python3 python3-dev python3-pip python3-virtualenv --no-install-recommends && ln -s /usr/bin/python3 /usr/bin/python && rm -rf /var/lib/apt/lists/*

#FROM hypriot/rpi-python
#RUN apt-get update -y
#RUN apt-get upgrade -y
#RUN apt-get dist-upgrade -y
#RUN apt-get install build-essential python-dev python-setuptools python-pip python-smbus -y
#RUN apt-get install libncursesw5-dev libgdbm-dev libc6-dev -y
#RUN apt-get install zlib1g-dev libsqlite3-dev tk-dev -y
#RUN apt-get install libssl-dev openssl -y
#RUN apt-get install libffi-dev -y
#RUN apt-get install -y python3
#RUN apt-get autoremove -y
#RUN wget https://github.com/python/cpython/archive/v3.7.1.tar.gz
#RUN tar -xvf v3.7.1.tar.gz
#RUN cd v3.7.1 & ./configure --prefix=$HOME/.local --enable-optimizations && make && make altinstall

#docker build -t f80hub/cluster_bench_arm . & docker push f80hub/cluster_bench_arm:latest
#docker rm -f clusterbench && docker pull f80hub/cluster_bench_arm:latest
#docker run --restart=always -p 5000:5000 --name clusterbench -d f80hub/cluster_bench_arm:latest


#test:docker run -p 5000:5000 -t f80hub/cluster_bench_x86:latest



#test SocketServer : http://45.77.160.220:5000

#arm
#docker build -t hhoareau/cluster_bench_arm .
#docker push hhoareau/cluster_bench_arm:latest

EXPOSE 5000

RUN mkdir /app
RUN mkdir /app/datas
RUN mkdir /app/clustering
RUN mkdir /app/saved
RUN mkdir /app/metrics

WORKDIR /app



COPY requirements.txt /app/requirements.txt
COPY datas /app/datas
COPY clustering /app/clustering
COPY fullchain.pem /app
COPY privkey.pem /app

RUN pip3 install --upgrade pip
RUN pip3 install setuptools

RUN pip3 install -r requirements.txt

COPY . /app

CMD python app.py