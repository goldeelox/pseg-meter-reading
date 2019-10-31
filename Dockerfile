FROM alpine:3.10
RUN apk --no-cache add --update \
    chromium \
    chromium-chromedriver \
    python2 \
    py2-pip

ADD requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
ADD main.py /main.py
CMD python /main.py
