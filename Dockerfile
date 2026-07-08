FROM node:18-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    chromium \
    chromium-sandbox \
    dbus \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

RUN pip install --break-system-packages --no-cache-dir \
    fastapi uvicorn[standard] sqlalchemy python-jose[cryptography] \
    pycryptodome apscheduler requests

RUN npm install -g puppeteer puppeteer-extra puppeteer-extra-plugin-stealth puppeteer-extra-plugin-user-preferences puppeteer-extra-plugin-user-data-dir

COPY web/package.json web/package-lock.json /tmp/web/
WORKDIR /tmp/web
RUN npm install
COPY web/ /tmp/web/
RUN npm run build

ARG CACHEBUST=5
COPY backend/ /tmp/backend/
RUN echo "build: ${CACHEBUST}" && mkdir -p /tmp/backend/static \
    && cp -r /tmp/web/dist/* /tmp/backend/static/

WORKDIR /app
RUN cp -r /tmp/backend/* /app/

ENV NODE_PATH=/usr/local/lib/node_modules

EXPOSE 7860

CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
