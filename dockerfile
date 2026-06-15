FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    QUARTO_VERSION=1.9.38

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    librsvg2-bin \
    && rm -rf /var/lib/apt/lists/*

RUN curl -o quarto.deb -L "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.deb" \
    && dpkg -i quarto.deb \
    && rm quarto.deb

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5500

CMD ["sh", "-c", "python construir_entrega_final.py && quarto render relatorio.qmd --to html"]