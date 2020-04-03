FROM python:3-alpine3.6 

LABEL maintainer="Arista Ansible Team <ansible@arista.com>"
LABEL com.example.version="1.0.2"
LABEL vendor1="Arista"
LABEL com.example.release-date="2019-10-29"
LABEL com.example.version.is-production="False"

ENV PS1='py3-ansible-cvp:\u% '

WORKDIR /tmp

COPY requirements.txt .
RUN apk add --update --no-cache ca-certificates \
                                openssh-client \
                                build-base \
                                gcc \
                                g++ \
                                make \
                                python-dev \
                                py-pip \
                                libffi-dev \
                                sshpass \
                                libressl-dev &&\
                                pip install --upgrade pip && \
                                pip install -r requirements.txt &&\
                                apk del -r --purge gcc make g++ &&\
                                rm -rf /source/* &&\
                                rm -rf /var/cache/apk/* &&\
                                rm -rf /tmp/*

WORKDIR /project
ADD ansible_collections/arista/ arista/
RUN ansible-galaxy collection build --force arista/cvp && \
    for i in *.tar.gz; do ansible-galaxy collection install $i -p /usr/share/ansible/collections; done

WORKDIR /playbooks
ADD examples/inventory.ini.example ./
RUN cp inventory.ini.example inventory.ini

VOLUME /playbooks