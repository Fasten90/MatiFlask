#!/bin/bash

if [ -z "${DB_PASSWORD}"]; then
    echo "[ERROR] DB_PASSWORD variable has not set! Exit!"
    exit 1
fi

venv/bin/python app.py
