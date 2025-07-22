# Este Dockerfile crea una imagen ligera de Python 3.12 usando Alpine Linux.
# 1. Establece el propietario de la imagen con una etiqueta.
# 2. Define el directorio de trabajo como /app.
# 3. Copia el archivo requirements.txt y luego instala las dependencias de Python sin usar la caché.
# 4. Copia el resto de los archivos de la aplicación al contenedor.
# 5. Expone el puerto 8000 para el servicio Flask.
# 6. Define el comando de inicio para ejecutar app.py con Python.
FROM python:3.12-alpine
LABEL owner="roxs"
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . . 
EXPOSE 8000
CMD ["python", "app.py"]