FROM python:3.10-slim

# Install dependencies and netcat
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/* 

WORKDIR /app

COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Flask default port
EXPOSE 5001

# Copy the wait-for-db script
COPY wait-for-db.sh /app/

# Command to run the app, using the wait-for-db script
CMD ["/app/wait-for-db.sh", "python", "app.py"]

