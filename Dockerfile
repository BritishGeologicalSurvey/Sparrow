FROM python:3.7-alpine

COPY ./docker-scripts/build-deps /install/build-deps
RUN /install/build-deps
COPY ./backend/requirements.txt /install/requirements.txt

RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r /install/requirements.txt

COPY ./config/docker.cfg /config/docker.cfg
ENV LABDATA_CONFIG=/config/docker.cfg
COPY ./bin/import-vocabularies /bin
COPY ./docker-scripts/run /bin
EXPOSE 5000
RUN mkdir /app
WORKDIR /app
COPY ./backend/setup.py /app
COPY ./backend/labdata /app
RUN pip3 install -e .
CMD ["/bin/run"]