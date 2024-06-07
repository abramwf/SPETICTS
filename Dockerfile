FROM python:3.10

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt .

RUN pip install -r requirements.txt

RUN python manage.py migrate

COPY . /speticts

WORKDIR /speticts

ENV PORT 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "speticts.wsgi:application"]