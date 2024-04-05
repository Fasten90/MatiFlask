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
    """ Calculate the arrive minutes, and check the next,
        and return with how many minutes are remained """
    now = datetime.datetime.now()
    actual_minute = now.minute
    idokoz = menetrend[3]
    arrive_minute = menetrend[4]
    while arrive_minute < actual_minute:
        arrive_minute += idokoz
    remained_minute = arrive_minute - actual_minute
    return remained_minute


def precheck_menetrend(menetrend, get_all=False):
    """ Precheck menetrend, for it is travelling or not, and what is the type of járat """
    new_menetrend = []
    now = datetime.datetime.now()
    actual_hour = now.hour
    for item in menetrend:
        min_hour = item[1]
        max_hour = item[2]
        jarat = item[0]
        if min_hour < max_hour:
            # Nappali járat
            if min_hour < actual_hour < max_hour or get_all:
                if 'm' in jarat.lower():
                    item = item + ('metro',)
                elif jarat.startswith('2') and len(jarat) >= 2:
                    item = item + ('villamos',)
                else:
                    item = item + ('nappali',)
                new_menetrend.append(item)
        elif min_hour > max_hour:
            if min_hour <= actual_hour < 24 or 0 <= actual_hour <= max_hour or get_all:
                # Éjszakai járat
                if 'm' not in jarat.lower():
                    item = item + ('éjszakai',)
                    new_menetrend.append(item)
        else:
            pass
    return new_menetrend


def get_color_by_jarmu_type(jarat, jarat_type):
    """ Get color (text and background) by járat type """
    if jarat_type == 'nappali':
        text_color = 'white'
        background_color = 'blue'
    elif jarat_type == 'éjszakai':
        text_color = 'white'
        background_color = 'black'
    elif jarat_type == 'villamos':
        text_color = 'black'
        background_color = 'yellow'
    elif jarat_type == 'metro':
        text_color = 'black'
        if jarat == 'M1':
            background_color = 'orange'
        elif jarat == 'M2':
            background_color = 'green'
        elif jarat == 'M3':
            background_color = 'red'
        elif jarat == 'M4':
            background_color = 'red'
        else:
            background_color = 'blue'
    else:
        text_color = 'black'
        background_color = 'white'
    return text_color, background_color


def update_menetrend_with_arrive_minutes(result):
    """ Add new column with arrive minute """
    new_result = []
    for item in result:
        new_item = item + (get_next_arrive(item),)
        new_result.append(new_item)
    return new_result


def extend_get_next_menetrends(result):
    """ Create new menetrends with new arrive values """
    new_result = []
    for item in result:
        new_result.append(item)
        for index in range(1,11):
            #now = datetime.now().time.minute
            # Last element is the 'arriving minute'
            new_arrive_minute = item[-1] + index * item[3]  # last arrive + n * járatsűrűség
            modified_item = item[:-1] + (new_arrive_minute, )
            new_result.append(modified_item)
    return new_result


def order_of_arrive(menetrend):
    """ ordering with remained arrive minutes """
    return menetrend[-1]


def get_menetrend(jarat=None, station=None, result=None):
    """ fill the menetrend table by SQL/DB result (rows) """
    html_result = ''
    now = datetime.datetime.now()
    if station:
        if result:
            result = precheck_menetrend(result)
            result = update_menetrend_with_arrive_minutes(result)
            result = extend_get_next_menetrends(result)
            result = sorted(result, key=order_of_arrive)
            html_result += '<table>'
            html_result += '<tr><td>Megálló</td><td>Járat</td><td>Érkezik</td></tr>\r\n'
            for item in result:
                jarat_found = item[0]
                station_found = item[5]
                jarat_type = item[-2]
                arrive_minute_remained = item[-1]
                text_color, background_color = get_color_by_jarmu_type(jarat_found, jarat_type)
                html_result += '<tr>'
                html_result += f'<td>{station_found}</td>' \
                        f'<td bgcolor="{background_color}">' \
                        f'<font color="{text_color}">{jarat_found}</font>' \
                        '</td>' \
                        f'<td>{arrive_minute_remained}</td>'
                html_result += '</tr>\r\n'
            html_result += '</table>\r\n'
        else:
            html_result = 'Nincs találat :(<br />\r\n'
    #elif jarat:
    else:
        get_all = True
        if jarat:
            get_all = False
        html_result += '<table>\r\n'
        html_result += '<tr><td>Járat</td><td>Indulási idő</td>'
        html_result += '<td>Eddig közlekedik</td><td>Járatsűrűség</td><td>Megálló</td></tr>\r\n'
        result = precheck_menetrend(result, get_all)
        for item in result:
            jarat=item[0]
            jarat_type = item[-1]
            text_color, background_color = get_color_by_jarmu_type(jarat, jarat_type)
            html_result += '<tr>'
            html_result += f'<td bgcolor="{background_color}">'
            html_result += f'<font color="{text_color}">{jarat}</font></td>'
            html_result += '<td>{:02}:{:02}</td>'.format(item[1], item[4])  # Hour, Minute
            html_result += '<td>{max_hour:02}:00</td>'.format(max_hour=item[2])
            html_result += '<td>{jaratsuruseg} perc</td>'.format(jaratsuruseg=item[3])
            html_result += '<td>{megallo}</td>'.format(megallo=item[5])
            html_result += '</tr>\r\n'
        html_result += '</table>\r\n'

    html_result += f'{now.hour:02}:{now.minute:02}'

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
    except Exception as ex:  # pylint: disable=broad-exception-caught
        result = [str(ex)]
    mydb.close()

    # Debug code
    print(result)

    return get_menetrend(jarat, station, result)


if __name__ == '__main__':
    # Manual test
    #get_menetrend_wrap()
    # Test menetrend with fake result
    sql_fake_result = [('6', 8, 20, 15, 0, 'Blaha Lujza tér')]
    res = get_menetrend(jarat='6', station=None, result=sql_fake_result)
    print(res)
    res = get_menetrend(jarat=None, station='Teszt', result=sql_fake_result)
    print(res)
    res = get_menetrend(jarat=None, station=None, result=sql_fake_result)
    print(res)
