#!/bin/sh

LAPTOP_IP=192.168.1.201
PERSON_ID=alice

python3 Iot/face_client.py --mode enroll --person-id ${PERSON_ID} --enroll-url http://${LAPTOP_IP}:8000/face/enroll
