FROM python:3.6-alpine as data

LABEL maintainer="Ivan Milenkovic <ivan.milenkovic@ictu.nl>"

RUN pip install --upgrade pip --upgrade-strategy only-if-needed

RUN apk --update add gcc musl-dev libxml2-dev libxslt-dev bash git subversion openssh-client \
    && pip install git+https://github.com/wekan/wekan-python-api-client.git#egg=wekanapi\&subdirectory=src \
    && pip install quality_report \
    && apk del gcc musl-dev  \
    && rm -rf /var/cache/apk/* /tmp/

WORKDIR /root/

RUN git clone --depth 1 --single-branch --branch=master https://github.com/ICTU/quality-report.git

# copying demo data to the location where url mocker looks for them
RUN mkdir /usr/local/lib/python3.6/docs/ && mkdir /usr/local/lib/python3.6/docs/examples && cp -r /root/quality-report/docs/examples/example_metric_sources /usr/local/lib/python3.6/docs/examples

RUN quality_report.py --project /root/quality-report/docs/examples/quality_report --report /root/quality-report/docs/examples/x_report --log INFO

FROM abiosoft/caddy 

COPY --from=data /root/quality-report/docs/examples/x_report/. /srv

EXPOSE 2015


