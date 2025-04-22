FROM python:3.11-slim

WORKDIR /app

# Install essential packages
RUN apt-get update && apt-get install -y dos2unix && apt-get clean

# Install dependencies
COPY requirements.txt .

# Fix encoding issues with requirements.txt and install dependencies
RUN dos2unix requirements.txt && \
    grep -v "pywin32" requirements.txt > requirements_docker.txt && \
    pip install --no-cache-dir -r requirements_docker.txt && \
    rm requirements_docker.txt

# Create upload directories
RUN mkdir -p /app/static/uploads/photos && \
    mkdir -p /app/static/uploads/cv

# Copy application code
COPY . .

# Create volume for database persistence
VOLUME ["/app/instance"]

# Environment variables will be set at runtime
ENV PUSHBULLET_KEY="" \
    EMAIL_MESSAGERIE="" \
    EMAIL_MESSAGERIE_PASSWORD=""

# Expose port
EXPOSE 5000

# Make entrypoint script executable
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Set entrypoint
ENTRYPOINT ["docker-entrypoint.sh"]

# Run the application
CMD ["python", "app.py"]
