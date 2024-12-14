FROM python:3.10-slim

WORKDIR /app

COPY ./auth_service/auth_service/requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8000

CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:${PORT:-8000}"]
