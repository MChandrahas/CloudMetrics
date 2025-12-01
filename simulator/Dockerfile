FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Run unbuffered so logs show up immediately
CMD ["python", "-u", "load_simulator.py"]