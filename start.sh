#!/bin/sh

docker-compose -f docker-compose.yml up --detach --scale worker=8 --build
