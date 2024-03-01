# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app


RUN pip install 'uvicorn[standard]'
RUN pip install gunicorn

COPY requirements.txt .
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


# Copy the rest of application's source code
COPY . .

# Define the command to run your application
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
