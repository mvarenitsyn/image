FROM python:3.9-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Set environment variables
ENV PORT=8080

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application with gunicorn (using shell form to allow environment variable interpolation)
CMD gunicorn --bind 0.0.0.0:$PORT api:app
