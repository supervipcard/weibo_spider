FROM python:3.6.6
ADD . /code
WORKDIR /code
COPY scrapydweb_settings_v10.py /code
EXPOSE 8888
RUN pip3 install scrapydweb
CMD scrapydweb
