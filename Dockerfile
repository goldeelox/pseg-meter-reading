FROM alpine:3.12
RUN apk --no-cache add --update \
    chromium \
    chromium-chromedriver \
    python3 \
    python3-dev \
    py-pip \
    musl-dev \
    gcc

WORKDIR /pseg
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD main.py main.py
ADD discord discord
ADD pseg pseg
CMD python3 ./main.py
