FROM python:3.12-slim

# tesseract-ocr : necessaire pour l'OCR des labels de plans et des factures materiaux (image).
# libgl1 : requis par opencv-python-headless au runtime sur certaines distros slim.
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-fra \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV STORAGE_DIR=/app/storage
RUN mkdir -p /app/storage

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
