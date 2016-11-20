FROM praekeltfoundation/supervisor
COPY ./blinky.conf /etc/supervisor/conf.d/blinky.conf
RUN pip install gunicorn
COPY . /app/
RUN pip install -e /app/
