FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .

# Remove Windows-specific package and install dependencies
RUN grep -v "pywin32" requirements.txt > requirements_docker.txt && \
    pip install --no-cache-dir -r requirements_docker.txt && \
    rm requirements_docker.txt

# Create upload directories
RUN mkdir -p /app/static/uploads/photos && \
    mkdir -p /app/static/uploads/cv

# Copy application code
COPY . .

# Create volume for database persistence
VOLUME ["/app/instance"]

# Environment variables (these will be overridden at runtime)
# ENV PUSHBULLET_KEY="your_pushbullet_key" \
#     EMAIL_MESSAGERIE="your_email" \
#     EMAIL_MESSAGERIE_PASSWORD="your_password"

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
