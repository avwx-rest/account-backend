# Start from the official Python 3.12 container
FROM python:3.12.3

# Expose the default application port
EXPOSE 8080

# Set the main working directory
WORKDIR /home/api

# Create new user to run as non-root
RUN useradd -m -r user && chown user /home/api

# Install the required Python packages
COPY pyproject.toml .
COPY main.py .
COPY ./account ./account
RUN pip install -U pip
RUN pip install -U . --no-cache-dir --compile

# Run as new user
USER user

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4", "--lifespan", "on"]