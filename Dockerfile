# Base Python image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy application files into the container
COPY . .

WORKDIR /usr/src/app

RUN apt-get update

# Install artiq_ibeam_smart module
RUN pip install .

ENV PYTHONUNBUFFERED=1

# Specify the default command to run the service
CMD ["python", "artiq_ibeam_smart/aqctl_artiq_ibeam_smart.py", "--simulation"]
#CMD ["pytest", "artiq_ibeam_smart/test_artiq_ibeam_smart.py"]
