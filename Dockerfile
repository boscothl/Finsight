
# Python image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies required for some python packages (like database drivers)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Expose port (Cloud Run defaults to 8080)
EXPOSE 8080

# Automatically run database migrations, collect static, and start gunicorn
# CMD python manage.py migrate --noinput && \
CMD python manage.py collectstatic --noinput && \
    gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 8 --timeout 0 --log-level debug --error-logfile - Finsight.wsgi:application

