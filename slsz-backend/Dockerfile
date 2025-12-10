# Django
FROM python:3.11-buster

RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list
RUN apt-get update && apt-get install -y vim
WORKDIR /etc/uwsgi/slsz
RUN python3 -m pip install uwsgi uwsgi-tools -i https://pypi.tuna.tsinghua.edu.cn/simple/
ADD requirements.txt /etc/uwsgi/slsz/requirements.txt
RUN python3 -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

CMD uwsgi --ini /etc/uwsgi/slsz/uwsgi.ini

#ADD uwsgi.ini uwsgi.ini
#ADD . /etc/uwsgi/django
#EXPOSE 8086
#CMD uwsgi --ini /etc/uwsgi/django/uwsgi.ini
#采用卷挂载，在docker-compose.yml文件中配置