FROM frolvlad/alpine-python2

MAINTAINER Frank Niessink <frank.niessink@ictu.nl>

RUN addgroup jenkins && adduser -s /bin/bash -D -G jenkins jenkins

RUN pip install quality_report
RUN apk --update add \
		bash \
		git \
		subversion \
		openssh-client \
	&& rm -rf \
		/var/cache/apk/* \
		/tmp/

VOLUME /home/jenkins/.ssh

USER jenkins

ENTRYPOINT ["quality_report.py"]
