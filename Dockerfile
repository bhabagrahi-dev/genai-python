# Use an official lightweight Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Hugging Face Spaces requires port 7860
EXPOSE 7860

# Run the application using Gunicorn (production-grade server)
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app"]