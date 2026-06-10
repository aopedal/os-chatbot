#!/bin/bash
uvicorn server:app --host 0.0.0.0 --port 8080 --workers 1 \
  --proxy-headers --forwarded-allow-ips 127.0.0.1 \
  --ws wsproto