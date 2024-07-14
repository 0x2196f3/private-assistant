# Use an official Python image as a base
FROM arm64v8/python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Install the necessary packages for PyAudio
RUN apt update && apt install -y libportaudio2 portaudio19-dev gcc
# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Run the command to start the application
CMD ["python", "main.py"]