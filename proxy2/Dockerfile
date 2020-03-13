# Use the Go v1.12 image for the base.
FROM python:3.8-slim
RUN apt-get update
RUN apt-get install -y python3-pip

# Copy the proxy code to the container.
COPY requirements.txt .
RUN pip3 install -r requirements.txt 

COPY proxy_flask.py .

# Run the proxy on container startup.
ENTRYPOINT ["python3"]
CMD [ "proxy_flask.py" ]

# Expose the proxy port.
EXPOSE 8000 9000

