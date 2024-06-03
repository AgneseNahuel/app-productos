# Usar una imagen base ligera de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo en /app
WORKDIR /app

# Copiar los archivos necesarios al contenedor
COPY requirements.txt .
COPY tu_aplicacion.py .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto 80
EXPOSE 80

# Comando para ejecutar la aplicación
CMD ["python", "tu_aplicacion.py"]
