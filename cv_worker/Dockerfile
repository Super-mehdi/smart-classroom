FROM python:3.11-slim AS production

WORKDIR /app

# Disable Python output buffering so logs stream live in Docker
ENV PYTHONUNBUFFERED=1

# Install system dependencies needed by OpenCV
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY cv_absence/requirements.txt .
# Pre-install CPU versions of PyTorch to save gigabytes of CUDA library downloads
RUN pip install --default-timeout=1000 --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

# Copy worker code
COPY cv_absence/ .

CMD ["python", "-u", "main.py"]