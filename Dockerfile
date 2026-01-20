# Use a lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Use Gunicorn for production instead of the Flask dev server
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app