FROM python:3.10.6-slim-buster

COPY . /app
WORKDIR /app
COPY .env .env

COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "1111"]