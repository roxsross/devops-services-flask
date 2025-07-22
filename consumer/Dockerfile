# Utiliza la imagen base oficial de Python 3.12 con Alpine Linux para crear un entorno ligero.
# Añade una etiqueta de propietario para identificar al responsable de la imagen.
# Establece el directorio de trabajo dentro del contenedor en /app.
# Copia el archivo requirements.txt al directorio de trabajo del contenedor.
# Instala las dependencias de Python listadas en requirements.txt sin guardar la caché.
# Copia todos los archivos del contexto de construcción al directorio de trabajo del contenedor.
# Define el comando por defecto para ejecutar el archivo consumer.py usando Python.
FROM python:3.12-alpine
LABEL owner="roxs"
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . . 
CMD ["python", "consumer.py"]