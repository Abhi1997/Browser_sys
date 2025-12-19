FROM python:3.13-slim

# Disable sandboxing for Qt WebEngine and Chromium flags
ENV QTWEBENGINE_DISABLE_SANDBOX=1 \
    QTWEBENGINE_CHROMIUM_FLAGS="--disable-gpu --disable-software-rasterizer --no-sandbox"

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . /app

# Run application
CMD ["python", "main.py"]
