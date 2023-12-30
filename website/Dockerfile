FROM python:3.10.6-slim

# Çalışma dizini oluştur
WORKDIR /website
COPY frontend /website/frontend
COPY ml /website/ml
COPY .env .env

# Gerekli Python paketlerini yükle
COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt

# Consumer scriptini kopyala
COPY main.py .

# Consumer scriptini çalıştır
CMD ["python", "main.py"]