FROM python:3.11-slim
WORKDIR /app

LABEL org.opencontainers.image.source=https://github.com/alex-woodward/pywrite

# Copy the dependencies file to the working directory
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/

ENTRYPOINT ["python", "src/manage.py"]
