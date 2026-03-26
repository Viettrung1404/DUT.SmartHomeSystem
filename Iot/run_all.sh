#!/bin/sh

LAPTOP_IP=192.168.1.201

FACE_UPLOAD_URL=http://${LAPTOP_IP}:8000/face/upload \
python3 Iot/iot_client.py
