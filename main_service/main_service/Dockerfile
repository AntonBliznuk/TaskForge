FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app/
RUN /bin/sh -c pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && pip list

COPY . /app

EXPOSE 8000

CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:${PORT:-8000}"]