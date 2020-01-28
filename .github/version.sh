#!/bin/sh

BRANCH=$(git rev-parse --symbolic-full-name --abbrev-ref HEAD)

if [[ $BRANCH == *"/"* ]]; then
    echo ${BRANCH} | awk -F '/' '{print $2}'
else
    echo $(git describe --abbrev=0 --tags)
fi