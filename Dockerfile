FROM andimajore/miniconda3_kinetic
WORKDIR /usr/src/mesidha/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apt-get update
RUN apt-get install -y supervisor nginx
RUN apt-get install -y libgtk-3-dev
RUN apt-get install wget

RUN conda install conda python=3.8

RUN pip install psycopg2-binary
COPY ./requirements.txt /usr/src/mesidha/requirements.txt
RUN pip install -r /usr/src/mesidha/requirements.txt

RUN pip install mqhandler==0.0.24
COPY . /usr/src/mesidha/

COPY ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000
