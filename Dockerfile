FROM python:3.7-alpine

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"

ARG hq_version

RUN addgroup jenkins && adduser -s /bin/bash -D -G jenkins jenkins

# Ignore the hadolint warning that ADD should be used instead of COPY for adding a tar archive. In this case we
# don't want to extract the archive since pip will do that for us.
# hadolint ignore=DL3010
COPY backend/dist/quality_report-$hq_version.tar.gz /tmp

RUN apk --update add gcc musl-dev libxml2-dev libxslt-dev bash git subversion openssh-client \
    && pip install git+https://github.com/wekan/wekan-python-api-client.git#egg=wekanapi\&subdirectory=src \
    && pip install /tmp/quality_report-$hq_version.tar.gz \
    && apk del gcc musl-dev  \
    && rm -rf /var/cache/apk/* /tmp/

VOLUME /home/jenkins/.ssh

USER jenkins

ENTRYPOINT ["quality_report.py"]

