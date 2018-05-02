FROM ictu/docker-protractor-headless

RUN apt-get update
RUN apt-get install -y git man

WORKDIR /root/

RUN git clone --depth 1 --single-branch --branch=master https://github.com/ICTU/quality-report.git

RUN npm install -g coffee-script
RUN npm install @ictu/testx

WORKDIR /root/quality-report/testx

CMD ["conf.coffee"]
