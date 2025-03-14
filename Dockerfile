FROM python:3.9-slim  

WORKDIR /app  
COPY src/ .  

ENV PYTHONPATH=/app 

RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir numpy  

CMD ["python", "main.py"]  