FROM python:3.8

RUN apt update && apt upgrade -y && apt-get install -y --no-install-recommends autoconf automake pkg-config libtool iputils-ping traceroute nano dnsutils

RUN /usr/local/bin/python -m pip install --upgrade pip

COPY ./ /app/

# We will use internal functions of the API
# So install all dependencies of the API
RUN cd app && pip install -r requirements.txt

WORKDIR /app

ENTRYPOINT celery -A worker worker --loglevel=INFO
