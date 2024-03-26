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
    if station:
        if result:
            now = datetime.datetime.now()
            for item in result:
                #for item in result:
                jarat_found = item[0]
                station_found = item[5]
                arrive_minute = item[4]
                actual_minute = now.minute
                while arrive_minute < actual_minute:
                    arrive_minute += item[3]
                html_result += 'Megálló: {station}<br />\r\n' \
                        'Ennyi perc múlva jön a {jarat} járat: {arrive_minute} perc<br />\r\n' \
                        '<hr>\r\n'.format(
                            station=station_found,
                            jarat=jarat_found,
                            arrive_minute=arrive_minute-actual_minute)
        else:
            html_result = 'Nincs találat'
    else:
        html_result = result

    return html_result


if __name__ == '__main__':
    # Manual test
    get_menetrend()
