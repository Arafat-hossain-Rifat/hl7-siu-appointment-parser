# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Skip dependencies installation (no external packages required)
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt || echo "No requirements to install"

# Set default entrypoint
ENTRYPOINT ["python", "parser.py"]
