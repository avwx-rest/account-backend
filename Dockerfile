# Start from the official Python 3.9 container
FROM python:3.9.6

# Expose the default application port
EXPOSE 8080

# Set the main working directory
WORKDIR /home/api

# Create new user to run as non-root
RUN useradd -m -r user && chown user /home/api

# Add Tini for better signal handling and thread cleanup
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]

# Install the require Python packages
COPY requirements.txt .
RUN pip install -U pip
RUN pip install -Ur requirements.txt --no-cache-dir --compile

# Copy the application code
COPY ./account ./account

# Run as new user
USER user

# Run the application
CMD ["uvicorn", "account.main:app", "--port", "8080", "--workers", "4"]