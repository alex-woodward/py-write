FROM python:3.11-slim
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ src/

CMD ["python", "src/manage.py", "-l"]
