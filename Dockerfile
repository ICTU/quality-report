FROM frolvlad/alpine-python2

MAINTAINER Frank Niessink <frank.niessink@ictu.nl>

RUN addgroup jenkins && adduser -s /bin/bash -D -G jenkins jenkins

RUN pip install quality_report
RUN apk --update add \
		bash \
		curl \
		git \
		graphviz \
		subversion \
		ttf-dejavu \
	&& rm -rf \
		/var/cache/apk/* \
		/tmp/

USER jenkins

ENTRYPOINT ["quality_report.py"]
