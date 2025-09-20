FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p app/uploads

# Expose ports
EXPOSE 8003 8505

# Environment variables
ENV PYTHONPATH=/app
ENV GEMINI_API_KEY=""

# Start script
COPY docker-start.sh /app/
RUN chmod +x /app/docker-start.sh

CMD ["/app/docker-start.sh"]