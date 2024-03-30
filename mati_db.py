""" This file contains Menetrend things for Mati """

import os
import datetime

import mysql.connector


def database_connection():
    """ Connect to the Database """
    mydb = mysql.connector.connect(
        host='localhost',
        user='fasten',
        password=os.getenv('DB_PASSWORD'),
        database='fasten_mati'
    )

    return mydb


def get_next_arrive(menetrend):
    """ Calculate the arrive minutes, and check the next, and return with how many minutes are remained """
    now = datetime.datetime.now()
    actual_minute = now.minute
    idokoz = menetrend[3]
    arrive_minute = menetrend[4]
    while arrive_minute < actual_minute:
        arrive_minute += idokoz
    remained_minute = arrive_minute - actual_minute
    return remained_minute


def precheck_menetrend(menetrend):
    """ Precheck menetrend, for it is travelling or not, and what is the type of járat """
    new_menetrend = []
    now = datetime.datetime.now()
    actual_hour = now.hour
    for item in menetrend:
        min_hour = item[1]
        max_hour = item[2]
        if min_hour <= actual_hour < max_hour:
            # Nappali járat
            if 'm' in item[0].lower():
                item = item + ('metro',)
            else:
                item = item + ('nappali',)
            new_menetrend.append(item)
        elif min_hour <= actual_hour < 24 or 0 <= actual_hour <= max_hour:
            # Éjszakai járat
            item = item + ('éjszakai',)
            new_menetrend.append(item)
        else:
            pass
    return new_menetrend


def get_color_by_jarmu_type(jarat_type):
    """ Get color (text and background) by járat type """
    if jarat_type == 'nappali':
        text_color = 'black'
        background_color = 'blue'
    elif jarat_type == 'éjszakai':
        text_color = 'white'
        background_color = 'black'
    elif jarat_type == 'metro':
        text_color = 'black'
        background_color = 'orange'
    else:
        text_color = 'black'
        background_color = 'white'
    return text_color, background_color


def get_menetrend(jarat=None, station=None, result=None):
    """ fill the menetrend table by SQL/DB result (rows) """
    html_result = ''
    now = datetime.datetime.now()
    if station:
        if result:
            result = precheck_menetrend(result)
            result = sorted(result, key=get_next_arrive)
            html_result += '<table>'
            for item in result:
                html_result += '<tr>'
                jarat_found = item[0]
                station_found = item[5]
                jarat_type = item[-1]
                arrive_minute_remained = get_next_arrive(item)
                text_color, background_color = get_color_by_jarmu_type(jarat_type)
                html_result += '<td>Megálló: {station}</td>' \
                        '<td>Ennyi perc múlva jön a </td><td bgcolor="{background_color}"><font color="{text_color}">{jarat}</font></td><td> járat: {arrive_minute} perc</td>' \
                        '\r\n'.format(
                            station=station_found,
                            background_color=background_color,
                            text_color=text_color,
                            jarat=jarat_found,
                            arrive_minute=arrive_minute_remained)
                html_result += '</tr>'
            html_result += '</table>'
        else:
            html_result = 'Nincs találat :('
    elif jarat:
        html_result += '<table>'
        html_result += '<tr><td>Járat</td><td></td><td>Indulási idő</td><td>Eddig közlekedik</td><td>Járatsűrűség</td><td>Megálló</td></tr>'
        for item in result:
            html_result += '<tr>'
            html_result += '<td>{jarat}</td>'.format(jarat=item[0])
            html_result += '<td>{star_hour}:{minute}</td>'.format(star_hour=item[1], minute=item[4])
            html_result += '<td>{max_hour}:00</td>'.format(max_hour=item[2])
            html_result += '<td>{jaratsuruseg} perc</td>'.format(jaratsuruseg=item[3])
            html_result += '<td>{megallo}</td>'.format(megallo=item[5])
            html_result += '</tr>'
        html_result += '</table>'
    else:
        html_result = result
        # TODO: jarat keresés improvement

    html_result += '{hour}:{minute}'.format(hour=now.hour, minute=now.minute)

    return html_result


def get_menetrend_wrap(jarat=None, station=None, limit=100):
    """ Get menetrend with járat or megálló """
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
        column_headers = mycursor.column_names  # TODO: Use
    except Exception as ex:
        # TODO: Temporary error handling
        result = [str(ex)]
    mydb.close()

    # Debug code
    print(result)

    get_menetrend_wrap(result)


if __name__ == '__main__':
    # Manual test
    #get_menetrend_wrap()
    # Test menetrend with fake result
    sql_fake_result = [('6', 8, 20, 15, 0, 'Megálló')]
    res = get_menetrend(jarat='6', station=None, result=sql_fake_result)
    print(res)
