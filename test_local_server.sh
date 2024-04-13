#!/bin/bash

if [ -z "${DB_PASSWORD}"]; then
    echo "[ERROR] DB_PASSWORD variable has not set! Exit!"
    exit 1
fi
curl 127.0.0.1:5000/menetrend?jarat=3
curl 127.0.0.1:5000/nyomtatas?megallo="Bolya"

