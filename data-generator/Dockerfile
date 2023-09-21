FROM python:3.10-slim

COPY requirements.txt .

RUN set -ex; \
  	pip install --no-cache-dir -r requirements.txt

ADD coinbase_producer.py .

CMD ["python", "-u", "./coinbase_producer.py"]