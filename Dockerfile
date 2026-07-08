FROM ghcr.io/puppeteer/puppeteer:latest

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --break-system-packages --no-cache-dir \
    fastapi uvicorn[standard] sqlalchemy python-jose[cryptography] \
    passlib[bcrypt] bcrypt pycryptodome apscheduler requests huggingface_hub

RUN npm install -g puppeteer-extra puppeteer-extra-plugin-stealth

COPY web/package.json web/package-lock.json /tmp/web/
WORKDIR /tmp/web
RUN npm install

COPY web/ /tmp/web/
RUN npm run build

COPY backend/ /tmp/backend/
RUN mkdir -p /tmp/backend/static \
    && cp -r /tmp/web/dist/* /tmp/backend/static/

WORKDIR /app
RUN cp -r /tmp/backend/* /app/

ENV NODE_PATH=/usr/local/lib/node_modules

EXPOSE 7860

CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
