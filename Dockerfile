FROM kalilinux/kali

# Python install
RUN apt-get update && apt-get -y install \
                      python3 \
                      python3-pip


COPY ./src /src
WORKDIR ./src

RUN env

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["/bin/sh","-c","python3 ./app.py"]
