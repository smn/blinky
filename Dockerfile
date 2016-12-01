FROM praekeltfoundation/supervisor
COPY ./blinky.conf /etc/supervisor/conf.d/blinky.conf
RUN pip install gunicorn psycopg2
COPY . /app/
RUN pip install -e /app/
