FROM python:3.11-slim

WORKDIR /backend
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY db ./db

ENV FLASK_APP=app
EXPOSE 5000

CMD ["sh", "-c", "python db/seed.py || true && flask run --host=0.0.0.0 --port=5000"]
