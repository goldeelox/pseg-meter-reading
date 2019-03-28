FROM joyzoursky/python-chromedriver:2.7-alpine3.7
ADD requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
ADD main.py /main.py
CMD python /main.py