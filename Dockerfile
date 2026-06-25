FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgdal-dev \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Agents/ ./Agents/

WORKDIR /app/Agents

EXPOSE 8501

CMD ["streamlit", "run", "app_new_streamlitv2.py", "--server.port=8501", "--server.address=0.0.0.0"]
