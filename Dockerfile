FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 DATA_DIR=/app/data
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --uid 10001 --create-home astra
COPY astrobot ./astrobot
RUN mkdir /app/data && chown -R astra:astra /app
USER astra
CMD ["python", "-m", "astrobot"]
