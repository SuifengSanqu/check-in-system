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

RUN pip install --no-cache-dir fastapi uvicorn[standard] sqlalchemy python-jose[cryptography] passlib[bcrypt] bcrypt pycryptodome apscheduler requests

COPY web/package.json web/package-lock.json /tmp/web/
WORKDIR /tmp/web
RUN npm install

COPY web/ /tmp/web/
RUN npm run build

COPY backend/ /tmp/backend/
RUN mkdir -p /tmp/backend/static \
    && cp -r /tmp/web/dist/* /tmp/backend/static/ \
    && ls -la /tmp/backend/static/

WORKDIR /app
RUN cp -r /tmp/backend/* /app/

ENV NODE_PATH=/usr/local/lib/node_modules

EXPOSE 7860

CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
