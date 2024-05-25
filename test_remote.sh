#!/bin/bash
set -e


SUBLINKS="menetrend menetrend?megallo=valami menetrend?megallo=lármákl menetrend?jarat=3 bus?lines=True all_lines nyomtatas?megallo=lármákl get_all_nyomtatas all_cities"

MATI_LINK="https://mati.e5tv.hu/"

for sublink in $SUBLINKS ;
do

    full_link="${MATI_LINK}/${sublink}"
    #curl "${full_link}"
    response=$(curl --write-out '%{http_code}' --silent --output /dev/null "${full_link}")
    echo "Test: ${sublink}:  HTTP return code: ${response}"
    if [ $response != 200 ] && [ $response != 500 ] ; then
        echo "Failed:"
        echo "${full_link}"
        exit 1
    fi
    sleep 2
done
