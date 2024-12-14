#!/bin/bash

if [ -z "${DB_PASSWORD}"]; then
    echo "[ERROR] DB_PASSWORD variable has not set! For 'start_local_server.sh' it is necessary!"
fi

echo curl 127.0.0.1:5000/menetrend?jarat=3
echo curl 127.0.0.1:5000//menetrend?megallo=L%C3%A1rm%C3%A1kl%20utca
echo curl 127.0.0.1:5000/nyomtatas?megallo="Bolya"
echo curl 127.0.0.1:5000/bus?line=0
echo curl 127.0.0.1:5000/mati_adatbazis

