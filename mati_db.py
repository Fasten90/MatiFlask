import os
import datetime

import mysql.connector


def database_connection():
    mydb = mysql.connector.connect(
        host='localhost',
        user='fasten',
        password=os.getenv('DB_PASSWORD'),
        database='fasten_mati'
    )

    return mydb


def get_next_arrive(menetrend):
    now = datetime.datetime.now()
    actual_minute = now.minute
    idokoz = menetrend[3]
    arrive_minute = menetrend[4]
    while arrive_minute < actual_minute:
        arrive_minute += idokoz
    remained_minute = arrive_minute - actual_minute
    return remained_minute


def precheck_menetrend(menetrend):
    new_menetrend = []
    now = datetime.datetime.now()
    actual_hour = now.hour
    for item in menetrend:
        min_hour = item[1]
        max_hour = item[2]
        if min_hour <= actual_hour<  max_hour:
            new_menetrend.append(item)
    return new_menetrend


def get_menetrend(jarat=None, station=None, limit=100):
    result = []

    mydb = database_connection()

    mycursor = mydb.cursor()

    print('Connected to MySQL')

    if jarat and station:
        sql = """
        SELECT *
        FROM mati_menetrend
        WHERE `jarat`='{}' AND `station` LIKE'%{}%'
        """.format(jarat, station)
    elif jarat:
        sql = """
        SELECT *
        FROM mati_menetrend
        WHERE `jarat`='{}'
        """.format(jarat)
    elif station:
        sql = """
        SELECT *
        FROM mati_menetrend
        WHERE `station` LIKE'%{}%'
        """.format(station)
    else:
        sql = """
        SELECT *
        FROM mati_menetrend
        """

    print('Execute SQL command: ' + sql)
    try:
        mycursor.execute(sql, {'limit': limit})
        result = mycursor.fetchall()
    except Exception as ex:
        # TODO: Temporary error handling
        result = [str(ex)]

    # Debug code
    print(result)

    html_result = ''
    now = datetime.datetime.now()
    if station:
        if result:
            result = precheck_menetrend(result)
            result = sorted(result, key=get_next_arrive)
            for item in result:
                #for item in result:
                jarat_found = item[0]
                station_found = item[5]
                arrive_minute_remained = get_next_arrive(item)
                html_result += 'Megálló: {station}<br />\r\n' \
                        'Ennyi perc múlva jön a {jarat} járat: {arrive_minute} perc<br />\r\n' \
                        '<hr>\r\n'.format(
                            station=station_found,
                            jarat=jarat_found,
                            arrive_minute=arrive_minute_remained)
        else:
            html_result = 'Nincs találat'
    else:
        html_result = result
        # TODO: jarat keresés improvement

    html_result += '{hour}:{minute}'.format(hour=now.hour, minute=now.minute)

    return html_result


if __name__ == '__main__':
    # Manual test
    get_menetrend()
