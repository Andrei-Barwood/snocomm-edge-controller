FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema requeridas para scipy, numpy, y generador de certificados
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libc-dev \
    libffi-dev \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias
COPY requirements_pro.txt .
RUN pip install --no-cache-dir -r requirements_pro.txt

# Copiar el resto del código
COPY . .

# Generar certificados TLS para Modbus si no existen
RUN chmod +x generate_certs.sh && ./generate_certs.sh

EXPOSE 8080 5020 8020

# Arrancar el edge controller
CMD ["python", "main_industrial.py"]
