FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY pressure_monitor.py .
COPY config.json .

# Create volume for persistent data
VOLUME ["/app/data"]

# Use data directory for persistent files
ENV DATA_FILE=/app/data/pressure_data.json
ENV LOG_FILE=/app/data/pressure_monitor.log

# Run the monitor
CMD ["python", "pressure_monitor.py"]
