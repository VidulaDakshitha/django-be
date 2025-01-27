ARG PYTHON_VERSION=3.11.2-bullseye
FROM python:${PYTHON_VERSION} as python
LABEL author='Dinal Fernando'

WORKDIR /app

# Environment
RUN apt-get update && \
    apt-get install -y bash vim nano postgresql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

# Major pinned python dependencies
RUN pip install --no-cache-dir flake8==3.8.4

# Regular Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY ./docker/local/django/start /start
RUN sed -i 's/\r$//g' /start && chmod +x /start

# Copy our codebase into the container
COPY . .

# Ops Parameters
ENV WORKERS=2
ENV PORT=80
ENV PYTHONUNBUFFERED=1

EXPOSE ${PORT}
CMD ["/start"]