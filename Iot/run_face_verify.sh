#!/bin/sh

LAPTOP_IP=192.168.1.201

python3 Iot/face_client.py --mode upload --upload-url http://${LAPTOP_IP}:8000/face/upload --interval 0.2
