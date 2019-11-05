FROM python:2.7-alpine3.6 

LABEL maintainer="EMEA AS"
LABEL com.example.version="0.5"
LABEL vendor1="Arista"
LABEL com.example.release-date="2019-10-29"
LABEL com.example.version.is-production="False"

ENV PS1='ansible-cvp:\u% '

WORKDIR /tmp
WORKDIR /tmp

RUN apk add --no-cache ca-certificates &&\
                       openssh-client &&\
                       build-base &&\
                       gcc &&\
                       g++ &&\
                       make &&\
                       python-dev &&\
                       py-pip &&\
                       libffi-dev &&\
                       sshpass &&\
                       libssl1.0 &&\
                       openssl-dev

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

RUN apk del -r --purge gcc make g++ &&\
    rm -rf /source/* &&\
    rm -rf /var/cache/apk/* &&\
    rm -rf /tmp/*

WORKDIR /project
ADD arista/ arista/
RUN cat arista/cvp/galaxy.yml
RUN ansible-galaxy collection build --force arista/cvp && \
    for i in *.tar.gz; do ansible-galaxy collection install $i -p /usr/share/ansible/collections; done

WORKDIR /playbooks
ADD examples/* ./
RUN cp inventory.ini.example inventory.ini

VOLUME /playbooks
CMD ["/bin/sh"]
