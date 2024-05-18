""" This file contains Menetrend things for Mati """

import os
import datetime
import math
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
    actual_hour = now.hour
    min_hour = menetrend[1]
    max_hour = menetrend[2]
    jaratsuruseg = menetrend[3]
    arrive_minute = menetrend[4]  # start_minute
    start_minute = menetrend[4]
    if min_hour < max_hour:  # Normal line
        while actual_hour < min_hour:
            arrive_minute += 60  # hour = 60minutes
            actual_hour += 1  # Check next "actual (fake)" hour
    if jaratsuruseg >= 60:
        #    arrive_minute
        delta_hour = math.floor(jaratsuruseg / 60)
        remained_minute = jaratsuruseg - (delta_hour * 60)
        arrive_hour = min_hour
        # arrive_minute = start_minute (menetrend[4])
        is_ok = False
        while not is_ok:
            while arrive_hour < actual_hour:
                arrive_hour += delta_hour
            arrive_minute += remained_minute
            # Check, if it is after the max_hour...
            if arrive_hour > max_hour:
                # It is after the job, exit!
                return None
            if arrive_hour > actual_hour or arrive_minute > actual_minute:
                # Arrive in the next hours or in this hour, but late minute
                # It is good!
                is_ok = True
                if arrive_hour == actual_hour:
                    remained_minute = arrive_minute - actual_minute
                else:
                    remained_minute = (60 - actual_minute) + (arrive_hour - actual_hour) + arrive_minute
                break
            else:
                # less minute then the actual, calculate the next arrive!
                pass
    else:
        # Simple handling, calculate from actual hour! It is wrong sometimes, but no problem.
        while arrive_minute < actual_minute:  # If it went, calculate the next
            arrive_minute += jaratsuruseg
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
        if min_hour < max_hour:
            # Nappali járat - most jár éppen
            if min_hour < actual_hour < max_hour or get_all:
                new_menetrend.append(item)
        elif min_hour > max_hour:
            # Éjszakai járat
            if min_hour <= actual_hour < 24 or 0 <= actual_hour <= max_hour or get_all:
                new_menetrend.append(item)
        else:
            new_menetrend.append(item)
    return new_menetrend


def get_color_by_jarmu_type(jarat, jarat_type):
    """ Get color (text and background) by járat type """
    if jarat_type == 'BUSZ':
        text_color = 'white'
        background_color = 'blue'
    elif jarat_type == 'ÉJSZAKAI':
        text_color = 'white'
        background_color = 'black'
    elif jarat_type == 'VOLÁNBUSZ':  # Shall be before the villamos (V)
        text_color = 'black'
        background_color = 'orange'
    elif jarat_type.startswith('V'):  # villamos
        text_color = 'black'
        background_color = 'yellow'
    elif jarat_type == 'M':     # metro
        text_color = 'black'
        if jarat == 'M1':
            background_color = 'yellow'
        elif jarat == 'M2':
            background_color = 'red'
        elif jarat == 'M3':
            background_color = 'blue'
        elif jarat == 'M4':
            background_color = 'green'
        else:
            background_color = 'blue'
    elif jarat_type == 'H':  # Hév
        text_color = 'white'
        background_color = 'green'
    elif jarat_type == 'BUSZTROLI':  # Troli
        text_color = 'white'
        background_color = 'red'
    elif jarat_type == 'DHAJO':  # Hajó / ship
        text_color = 'black'
        background_color = 'pink'
    else:
        text_color = 'black'
        background_color = 'white'
    return text_color, background_color


def update_menetrend_with_arrive_minutes(result):
    """ Add new column with arrive minute """
    new_result = []
    for item in result:
        new_item = item + (get_next_arrive(item),)  # Add arrive_minute to last field/column
        new_result.append(new_item)
    return new_result


def extend_get_next_menetrends(result):
    """ Create new menetrends with new arrive values """
    new_result = []
    for item in result:
        jaratsuruseg = item[3]
        new_result.append(item)
        for index in range(1, 28):
            #now = datetime.now().time.minute
            # Last element is the 'arriving minute'
            # item[-1] = arrive minute!
            new_arrive_minute = item[-1] + index * jaratsuruseg  # last arrive + n * járatsűrűség
            modified_item = item[:-1] + (new_arrive_minute, )  # Add a new item with updated arrive minute
            new_result.append(modified_item)
    return new_result


def order_of_arrive(menetrend):
    """ ordering with remained arrive minutes """
    return menetrend[-1]


def update_late_arrive_time_to_clock(menetrend):
    """ Update arrive minutes to real time """
    new_menetrend = []
    time = datetime.datetime.now()
    for item in menetrend:
        arrive_minute = item[-1]
        max_hour = item[2]
        min_hour = item[1]
        if arrive_minute > 60:
            delta = datetime.timedelta(minutes=arrive_minute)
            arrive_time = time + delta
            if arrive_time.hour >= max_hour:
                # Már nem jár
                continue
            if min_hour < max_hour and arrive_time.day != time.day:
                # Nappali járat, holnapi dátum
                continue
            arrive_time = datetime.datetime.strftime(arrive_time, '%H:%M')
            new_item = item[:-1] + (arrive_time, )
        else:
            new_item = item
        new_menetrend.append(new_item)
    return new_menetrend


def get_menetrend(jarat=None, station=None, result=None):
    """ fill the menetrend table by SQL/DB result (rows) """
    html_result = ''
    now = datetime.datetime.now()
    if station:
        if result:
            #result = precheck_menetrend(result)
            result = update_menetrend_with_arrive_minutes(result)
            result = extend_get_next_menetrends(result)
            result = sorted(result, key=order_of_arrive)
            result = update_late_arrive_time_to_clock(result)
            html_result += '<table>'
            html_result += '<tr><td>Megálló</td><td>Járat</td><td>Érkezik</td></tr>\r\n'
            for item in result:
                jarat_found = item[0]
                station_found = item[5]
                jarat_type = item[6]
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
            jarat = item[0]
            jarat_type = item[6]
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


def get_db(jarat=None, station=None, limit=100):
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
    return result


def get_menetrend_wrap(jarat=None, station=None, limit=100):
    """ Get menetrend with járat or megálló """
    result = get_db(jarat, station)
    return get_menetrend(jarat, station, result)


def get_menetrend_nyomtatas(station="valami", db=True, result=None):
    """ Menetrend for one station """
    if db:
        result = get_db(station=station)
    else:
        pass
        # Use parameter 'result'
    need_to_break = False
    if len(result) >= 8:
        need_to_break = math.floor(len(result)/2)

    html_result = ''
    station_found = result[0][5]
    html_result += '<html><body><table cellpadding="10" border="3">'
    html_result += '<tr><td><font size="24">Megálló</font></td>'
    html_result += f'<td><font size="24">{station_found}</font></td></tr>\r\n'
    jarat_map = set()
    break_header = ''
    jarat_types = {}
    for  item in result:
        jarat_found = item[0]
        jarat_map.add(jarat_found)
        if jarat_found not in jarat_types:
            jarat_type = item[6]
            jarat_types[jarat_found] = jarat_type
    html_result += '<tr>'
    for cnt, item in enumerate(list(jarat_map)):
        jarat_this = item
        jarat_type = jarat_types[jarat_this]
        text_color, background_color = get_color_by_jarmu_type(jarat_this, jarat_type)
        jarat_html = f'<td bgcolor="{background_color}"><font size="24" color="{text_color}">{jarat_this}</font></td>'
        if need_to_break and need_to_break <= cnt:
            # Second parts
            break_header += jarat_html
        else:
            # if not needed to break + first some
            html_result += jarat_html
    html_result += '</tr>\r\n'

    html_result += '<tr>'  # This shall be closed when we have too much lines
    for cnt, jarat_this in enumerate(jarat_map):
        if db:
            result = get_db(jarat=jarat_this)
        this_station_has_found = False
        this_station_index = 0
        if need_to_break and need_to_break == cnt:
            html_result += '</tr>'  # Closed because the too much lines
            html_result += '<tr>'  # Another lines header
            html_result += break_header
            html_result += '</tr>'
            html_result += '<tr>'
        html_result += '<td>'
        # Station + Starting time tables
        html_result += '<table>'
        html_result += '<tr><td>'
        # Station table
        html_result += '<table>'
        for item in result:
            station_found = item[5]
            html_result += '<tr><td>'
            if this_station_has_found:
                # New stations
                text_color = 'black'
            else:
                if station_found == station:
                    # Here!
                    this_station_has_found = True
                    this_station_index = result.index(item)
                    text_color = 'blue'
                else:
                    # previous station
                    text_color = 'grey'
            html_result += f'<td><font color="{text_color}">{station_found}</font>'
            html_result += '</td></tr>'
        html_result += '</table>'  # End of station table
        html_result += '</td>'
        html_result += '<td>\r\n'
        html_result += '<table>'  # Menetrend table
        # result = jarat db
        if this_station_has_found:
            item = result[this_station_index]
            min_hour = item[1]
            max_hour = item[2]
            jaratsuruseg_minute = item[3]
            start_minute = item[4]
            for hour in range(min_hour, max_hour):
                html_result += '<tr>'
                html_result += f'<td>{hour}:</td>'
                for minute in range (start_minute, 60, jaratsuruseg_minute):
                    html_result += f'<td>{minute:02d},</td>'
                html_result += '</tr>\r\n'
        else:
            # Error
            pass
        html_result += '</table>\r\n'  # End of menetrend table
        html_result += '</td></tr>'
        html_result += '</table>\r\n'  # End of station + starting time table
        html_result += '</td>\r\n'
    html_result += '</tr>'
    html_result += '</table></body></html>\r\n'
    return html_result


def get_all_lines():  # For 'Bus app'
    result = get_db()
    line_set = set()
    for item in result:
        line_set.add(item[0])
    return {'lines': list(line_set) }


def get_line_info(line):  # For 'Bus app'
    result = get_db(jarat=line)
    res_dict = {'line': line, 'end_station': 'végállomás', 'actual_bus_station': 'buszállomás', 'next_bus_station': 'Következő állomás'}
    if result:
        now = datetime.datetime.now()
        end_station = 'Végállomás'
        last_start_minute = 0
        time_calculated = 0
        for item in result:
            min_hour = item[1]
            max_hour = item[2]
            jaratsuruseg = item[3]
            start_minute = item[4]
            actual_bus_station = item[5]
            if last_start_minute < start_minute:
                end_station = actual_bus_station  # Save this for end_station
                last_start_minute = start_minute
            if time_calculated == 1:
                time_calculated += 1
                res_dict['next_bus_station'] = item[5]
            if not time_calculated:
                if now.hour in range(min_hour, max_hour):
                    # Proper hour
                    for min in range(start_minute, 59, jaratsuruseg):
                        if now.minute == min:
                            # Found!
                            res_dict['actual_bus_station'] = actual_bus_station
                            # Found end_station
                            time_calculated = 1
                            break
                else:
                    res_dict['actual_bus_station'] = 'Ma már nem közlekedik'
            # Do not exit, because the finding end_station
            if not time_calculated:
                res_dict['actual_bus_station'] = 'Most épp nem jár, a végállomáson vár'
        res_dict['end_station'] = end_station
    return res_dict


def get_all_lines_html():  # For 'MatiBudapestGO'
    """ Get all lines for MatiBudapestGO - HTML format """

    result = get_db()
    line_set = set()
    lines = []
    for item in result:
        line_set.add(item[0])
    for jarat_item in line_set:
        # Find in all items
        first_station = None
        end_station = None
        for item in result:
            jarat = item[0]
            if jarat_item == jarat:
                # Get the first element
                station = item[5]
                if not first_station:
                    first_station = station
                    jarat_type = item[6]
                end_station = station  # Set the end station
        # We have this line
        lines.append((jarat_item, first_station, end_station, jarat_type))

    html_result = '<html><body><table>\n'
    for jarat in lines:
        # Create 2 lines, with first station and with end station
        jarat_number = jarat[0]
        first_station = jarat[1]
        end_station = jarat[2]
        jarat_type = jarat[3]
        text_color, background_color = get_color_by_jarmu_type(jarat_number, jarat_type)
        html_result += '<tr>'
        html_result += '<td>'
        # Inner table
        html_result += '<table border="1">'
        html_result += f'<tr><td border="1" bgcolor="{background_color}"><font color="{text_color}">{jarat_number}</font></td><td>{first_station}</td></tr>\n'
        html_result += f'<tr><td border="1" bgcolor="{background_color}"><font color="{text_color}">{jarat_number}</font></td><td>{end_station}</td></tr>\n'
        html_result += '</table>\n'
        #
        html_result += '</td>'
        html_result += '</tr>\n'
    html_result += '</table></body></html>\n'
    return html_result


def get_all_nyomtatas_link():
    result = get_db()
    station_set = set()
    for item in result:
        station = item[5]
        station_set.add(station)

    html_result = '<html><table>\n'
    stations = list(station_set)
    stations.sort()
    for station in stations:
        html_result += f'<tr><td><a href="https://mati.e5tv.hu/nyomtatas?megallo={station}">{station}</a><br /></td></tr>\n'
    html_result += '</table></html>\n'
    return html_result


if __name__ == '__main__':
    # Manual test
    #get_menetrend_wrap()
    # Test menetrend with fake result
    sql_fake_result = [('6', 8, 22, 50, 0, 'Blaha Lujza tér')]
    #res = get_menetrend(jarat='6', station=None, result=sql_fake_result)
    #print(res)
    res = get_menetrend(jarat=None, station='Teszt', result=sql_fake_result)
    print(res)
    #res = get_menetrend(jarat=None, station=None, result=sql_fake_result)
    #print(res)
    res = get_menetrend_nyomtatas(station="Bolya utca", db=False, result=sql_fake_result)
    print(res)
