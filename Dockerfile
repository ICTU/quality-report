FROM python:3.6-alpine

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"

ARG hq_version

RUN addgroup jenkins && adduser -s /bin/bash -D -G jenkins jenkins

RUN apk --update add gcc musl-dev libxml2-dev libxslt-dev bash git subversion openssh-client \
    && pip install git+https://github.com/wekan/wekan-python-api-client.git#egg=wekanapi\&subdirectory=src \
    && pip install "quality_report==$hq_version" \
    && apk del gcc musl-dev  \
    && rm -rf /var/cache/apk/* /tmp/

VOLUME /home/jenkins/.ssh

USER jenkins

ENTRYPOINT ["quality_report.py"]

