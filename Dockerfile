# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# updating the and installing awscli
RUN apt update -y && apt install awscli -y

# Install any needed packages specified in requirements.txt
RUN  apt-get update && pip install -r requirements.txt

# Expose the port that your Flask app will run on
EXPOSE 5000

# Define the command to run your Flask app
CMD ["python3", "application.py"]