FROM python:3.6-alpine as data

LABEL maintainer="Ivan Milenkovic <ivan.milenkovic@ictu.nl>"

RUN pip install --quiet --upgrade pip --upgrade-strategy only-if-needed

RUN apk --update add gcc musl-dev libxml2-dev libxslt-dev bash git subversion openssh-client \
    && rm -rf /var/cache/apk/* /tmp/

ADD ./ /root/quality-report/

WORKDIR /root/quality-report/

RUN pip install --quiet -r backend/requirements.txt
RUN python ./backend/quality_report.py --project docs/examples/quality_report --report /root/x_report --log ERROR

CMD ["bash"]
