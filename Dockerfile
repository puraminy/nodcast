FROM python:3.11-slim
WORKDIR /app

# Copy your local project into the container
COPY . /app

# Install it (assumes you have setup.py or pyproject.toml)
RUN pip install .

ENV TERM=xterm-256color

ENTRYPOINT ["nodcast"]

