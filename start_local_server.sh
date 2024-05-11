#!/bin/bash

if [ -z "${DB_PASSWORD}" ]; then
    echo "[ERROR] DB_PASSWORD variable has not set! Exit!"
    echo "Set it with \"export DB_PASSWORD=1234\""
    exit 1
fi

venv/bin/python app.py
