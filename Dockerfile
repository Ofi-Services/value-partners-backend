# Use the official Python runtime image
FROM python:3.13

# Create the app directory
RUN mkdir /app

# Set the working directory inside the container
WORKDIR /app

# Set environment variables 
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# Upgrade pip
RUN pip install --upgrade pip

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the .env file to the app directory (if using environment variables)
COPY .env /app/

# Copy the Django project to the container
COPY . /app/

# Run migrations and start the Django app with Gunicorn
CMD ["sh", "-c", "python manage.py migrate && \
                 python manage.py collectstatic --no-input && \
                 python manage.py runserver 0.0.0.0:8000"]
