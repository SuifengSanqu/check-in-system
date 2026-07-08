FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    chromium \
    chromium-common \
    fonts-noto-cjk \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdrm2 \
    libgbm1 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g puppeteer puppeteer-extra puppeteer-extra-plugin-stealth

COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY web/package.json web/package-lock.json /tmp/web/
WORKDIR /tmp/web
RUN npm install

COPY web/ /tmp/web/
RUN npm run build

WORKDIR /app
COPY backend/ /app/
RUN mkdir -p /app/static \
    && cp -r /tmp/web/dist/* /app/static/ \
    && ls -la /app/static/ \
    && echo "--- static contents ---" \
    && ls -la /app/static/assets/ 2>/dev/null || echo "no assets dir"

ENV NODE_PATH=/usr/local/lib/node_modules

EXPOSE 7860

CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
