# Usamos una imagen ligera de Python
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos los archivos necesarios
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Exponemos el puerto de Flask
EXPOSE 5000

# Comando para arrancar la app
CMD ["python", "app.py"]
