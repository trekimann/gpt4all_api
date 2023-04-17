FROM python:3.8

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements_common.txt .
RUN pip install -r requirements_common.txt

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000 5001 5678
# CMD ["gunicorn", "-b", "0.0.0.0:5000", "--worker-class", "eventlet", "-w", "1", "app:app"]
CMD ["python", "app.py"]

