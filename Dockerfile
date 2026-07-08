FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    chromium \
    chromium-sandbox \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g puppeteer puppeteer-extra puppeteer-extra-plugin-stealth

WORKDIR /app

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --break-system-packages --no-cache-dir -r requirements.txt

COPY web/package.json web/package-lock.json /app/web/
WORKDIR /app/web
RUN npm install

COPY web/ /app/web/
RUN npm run build

WORKDIR /app
COPY backend/ /app/
RUN mkdir -p /app/static && cp -r /app/web/dist/* /app/static/

ENV NODE_PATH=/usr/local/lib/node_modules

EXPOSE 7860

CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
