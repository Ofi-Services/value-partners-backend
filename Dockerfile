# Use the official Python runtime image
FROM python:3.11

# Create the app directory
RUN mkdir /app

# Set the working directory inside the container
WORKDIR /app

# Set environment variables 
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1
# Django settings
ENV DJANGO_ALLOWED_HOSTS="localhost 127.0.0.1 [::1]"

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip
# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create directories for static and media files
RUN mkdir -p /app/static /app/media

# Copy only the Django app code
COPY manage.py /app/
COPY api /app/api
COPY ofi_dashboard_backend /app/ofi_dashboard_backend

# Make the entrypoint script executable
RUN chmod +x /app/manage.py

# Run migrations and start the Django app
CMD ["sh", "-c", "python manage.py migrate && \
                  python manage.py collectstatic --no-input && \
                  python manage.py runserver 0.0.0.0:8000"]
