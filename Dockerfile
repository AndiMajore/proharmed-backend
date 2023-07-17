FROM andimajore/miniconda3_mantic
WORKDIR /usr/src/proharmed/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apt-get update && apt-get dist-upgrade -y
RUN apt-get install -y supervisor nginx
RUN apt-get install -y libgtk-3-dev
RUN apt-get install wget

RUN conda install conda python=3.9
RUN pip install --upgrade pip

RUN pip install psycopg2-binary
COPY ./requirements.txt /usr/src/proharmed/requirements.txt
RUN pip install -r /usr/src/proharmed/requirements.txt

RUN pip install proharmed==0.0.4
COPY . /usr/src/proharmed/

COPY ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000
