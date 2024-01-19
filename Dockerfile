# Use an official Python runtime as a base image
FROM python:3.11.7-slim-bookworm

# Set the working directory in the Docker image
WORKDIR /app

# Copy the rest of the application's code into the image
COPY . .

# Install the application's dependencies inside the Docker image
RUN pip install -r requirements.txt

# Expose the port the application runs on
EXPOSE 5000

# Define the command that should be executed when the Docker container starts
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]