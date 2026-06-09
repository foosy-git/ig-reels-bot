# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install system dependencies (ImageMagick is REQUIRED for MoviePy text rendering)
RUN apt-get update && apt-get install -y \
    imagemagick \
    ffmpeg \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Fix ImageMagick policy to allow text rendering (Ignore if file doesn't exist on newer Debian)
RUN sed -i 's/<policy domain="path" rights="none" pattern="@\*"/<!-- <policy domain="path" rights="none" pattern="@\*" -->/' /etc/ImageMagick-6/policy.xml || true

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install schedule

# Copy the rest of the application code
COPY . .

# Run the background bot script
CMD ["python", "main.py"]
