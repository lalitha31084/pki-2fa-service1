# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
COPY requirements.txt .
# Create a virtual environment at /opt/venv
RUN python -m venv /opt/venv
# Activate venv by adding it to PATH
ENV PATH="/opt/venv/bin:$PATH"
# Install dependencies into the venv
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim as runtime

# Critical: Set Timezone to UTC
ENV TZ=UTC

WORKDIR /app

# Install system tools (Cron and Timezone data)
RUN apt-get update && apt-get install -y \
    cron \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Configure Timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv
# Activate venv in the runtime stage
ENV PATH="/opt/venv/bin:$PATH"

# Copy Application Code
COPY . .

# Create Volume Mount Points (for persistence)
RUN mkdir -p /data /cron && chmod 755 /data /cron

# Setup Cron Job
# We copy the cron file to the system cron directory
COPY cron/2fa-cron /etc/cron.d/2fa-cron
RUN chmod 0644 /etc/cron.d/2fa-cron && crontab /etc/cron.d/2fa-cron

# Expose API Port
EXPOSE 8080

# Start Command: Runs BOTH Cron and FastAPI
CMD cron && uvicorn app.main:app --host 0.0.0.0 --port 8080