FROM nfd:latest

RUN apt-get update -y
RUN apt-get install -y python3 python3-dev python3-pip less vim nano
RUN apt-get install -y git
RUN pip3 install -U git+https://github.com/named-data/python-ndn.git