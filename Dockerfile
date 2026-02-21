FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -m nltk.downloader punkt stopwords vader_lexicon

# Copy project
COPY . .

# Create media and static directories
RUN mkdir -p media staticfiles

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "insightwrite.wsgi:application"]
