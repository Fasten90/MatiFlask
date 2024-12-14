""" This file contains Menetrend things for Mati """

import os
import datetime
import math
from enum import Enum
import copy
import mysql.connector


CITY_DONTCARE_TEXT = 'Minden város'
TIME_ARRIVE_NOW_TEXT = 'MOST'

DEBUG = False


def database_connection():
    """ Connect to the Database """
    mydb = mysql.connector.connect(
        host='localhost',
        user='fasten',
        password=os.getenv('DB_PASSWORD'),
        database='fasten_mati'
    )

    return mydb


def get_db(jarat=None, station=None, city=None, limit=100):
    """ Get lines (jarat) or station (megallo) from DB """

    result = []

    mydb = database_connection()

    mycursor = mydb.cursor()

    print('Connected to MySQL')

    # Check city:
    if city == CITY_DONTCARE_TEXT:
        city = None

    if jarat and station:
        sql = f"""
        SELECT *
        FROM mati_menetrend
        WHERE `jarat`='{jarat}' AND `station` LIKE '%{station}%'
        """
    elif jarat and city:
        sql = f"""
        SELECT *
        FROM mati_menetrend
        WHERE `jarat`='{jarat}' AND `varos`='{city}'
        """
    elif jarat:
        sql = f"""
        SELECT *
        FROM mati_menetrend
        WHERE `jarat`='{jarat}'
        """
    elif station and city:
        sql = f"""
        SELECT *
        FROM mati_menetrend
        WHERE `station` LIKE '%{station}%' AND `varos`='{city}'
        """
    elif station:
        sql = f"""
        SELECT *
        FROM mati_menetrend
        WHERE `station` LIKE '%{station}%'
        """
    else:
        sql = """
        SELECT *
        FROM mati_menetrend
        """

    print('Execute SQL command: ' + sql)
    try:
        mycursor.execute(sql, {'limit': limit})
        result = mycursor.fetchall()
        column_headers = mycursor.column_names
    except Exception as ex:  # pylint: disable=broad-except
        mydb.close()
        raise Exception(ex)
    else:
        # Move content into dictionary
        results_with_dict = []
        for item in result:
            new_item = {}
            for index, column in enumerate(column_headers):
                new_item[column] = item[index]
            results_with_dict.append(new_item)
        result = results_with_dict
    mydb.close()

    if DEBUG:
        print(result)

    return result


def get_db_all():
    """ Get all things """

    result = []

    mydb = database_connection()

    mycursor = mydb.cursor()

    print('Connected to MySQL')

    sql = """
    SELECT *
    FROM mati_menetrend
    """

    try:
        mycursor.execute(sql)
        result = mycursor.fetchall()
        column_headers = mycursor.column_names
    except Exception as ex:  # pylint: disable=broad-except
        mydb.close()
        raise Exception(ex)

    mydb.close()

    return result, column_headers


def get_db_cities():
    """ Get all available cities from db """

    mydb = database_connection()

    mycursor = mydb.cursor()

    sql = """
        SELECT varos
        FROM `mati_menetrend`
        GROUP by varos;
        """
    print('Execute SQL command: ' + sql)
    try:
        mycursor.execute(sql)
        result = mycursor.fetchall()
    except Exception as ex:  # pylint: disable=broad-except
        mydb.close()
        raise Exception(ex)

    mydb.close()
    return result


def get_next_arrive(menetrend):
    """ Calculate the arrive minutes, and check the next,
        and return with how many minutes are remained """
    now = datetime.datetime.now()
    actual_minute = now.minute
    actual_hour = now.hour
    min_hour = menetrend['min_hour']
    max_hour = menetrend['max_hour']
    jaratsuruseg = get_jaratsuruseg_by_day_type(menetrend['jaratsuruseg_minute'], menetrend['jaratsuruseg_hetvege'])
    arrive_minute = menetrend['start_minute']
    if min_hour < max_hour:  # Normal line
        # Check until if has not started
        while actual_hour < min_hour:
            arrive_minute += 60  # hour = 60minutes
            actual_hour += 1  # Check next "actual (fake)" hour
    if jaratsuruseg >= 60:
        #    arrive_minute
        delta_hour = math.floor(jaratsuruseg / 60)
        remained_minute = jaratsuruseg - (delta_hour * 60)
        arrive_hour = min_hour
        # arrive_minute = start_minute (menetrend['start_minute'])
        is_ok = False
        while not is_ok:
            while arrive_hour < actual_hour:
                arrive_hour += delta_hour
            arrive_minute += remained_minute
            # Check, if it is after the max_hour...
            if arrive_hour > max_hour:
                # It is after the job, exit!
                return None
            if actual_hour <= arrive_hour or actual_minute <= arrive_minute:
                # Arrive in the next hours or in this hour, but later minute
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
    """ Precheck menetrend, for it is travelling or not  """
    new_menetrend = []
    now = datetime.datetime.now()
    actual_hour = now.hour
    for item in menetrend:
        min_hour = item['min_hour']
        max_hour = item['max_hour']
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


def precheck_menetrend2(menetrend, get_all=False):
    """ Precheck line(s) if they are going or not (e.g. workday or not) """
    new_menetrend = []
    for item in menetrend:
        if check_if_it_is_going(item):
            new_menetrend.append(item)
    return new_menetrend


def get_color_by_jarmu_type(jarat, jarat_type):  # pylint: disable=too-many-branches
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
    elif jarat_type == 'VONAT':  # Shall be before the villamos (V)
        text_color = 'white'
        background_color = 'Indigo'
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
        if jarat == 'H5':
            background_color = 'purple'  # Lila
        elif jarat == 'H6':
            background_color = 'brown'
        elif jarat == 'H7':
            background_color = 'orange'
        elif jarat == 'H8':
            background_color = 'DeepPink'
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
        new_item = item
        new_item['arrive_minute'] = get_next_arrive(item)  # Add a calculated field
        new_result.append(new_item)
    return new_result


def extend_get_next_menetrends(result):
    """ Create new menetrends with new arrive values """
    new_result = []
    for item in result:
        if not isinstance(item['arrive_minute'], int) or item['arrive_minute'] < 0:  # There is no arrive data for today?
            # 0 is needed!
            # TODO: Improvement: 'Ma már nem közlekedik' arrive minute
            #modified_item = item.copy()
            #modified_item['arrive_minute'] = new_arrive_minute  # Add a new item with updated arrive minute
            #new_result.append(modified_item)
            continue  # Ignore this line
        jaratsuruseg = get_jaratsuruseg_by_day_type(item['jaratsuruseg_minute'], item['jaratsuruseg_hetvege'])
        if jaratsuruseg:
            new_result.append(item)
            for index in range(1, 28):
                #now = datetime.now().time.minute
                # Last element is the 'arriving minute' - it is calculated
                new_arrive_minute = item['arrive_minute'] + index * jaratsuruseg  # last arrive + n * járatsűrűség
                modified_item = item.copy()
                modified_item['arrive_minute'] = new_arrive_minute  # Add a new item with updated arrive minute
                new_result.append(modified_item)
    return new_result


def extend_with_low_floor(result):
    """ Create new menetrends with low floor properties """
    new_result = []
    floor_calculation = {}
    for item in result:
        modified_item = item.copy()
        if 'low_floor' not in item:
            low_floor = False
        else:
            low_floor = item['low_floor']
        if not low_floor:
            modified_item['low_floor'] = False
            new_result.append(modified_item)
        else:
            # We shall calculate the low floor
            try:
                low_floor1 = int(low_floor.split('_')[0])
                low_floor2 = int(low_floor.split('_')[1])
            except:
                print('Issue with "low_floor", set automatically true')
                modified_item['low_floor'] = True
                new_result.append(modified_item)
                break
            line = item['jarat']
            if line not in floor_calculation:
                floor_calculation[line] = {
                    # Random ~ module of hour
                    'count': datetime.datetime.now().hour % (low_floor1+low_floor2),
                    'low_floor_limit': low_floor1,
                    'max': low_floor1 + low_floor2,
                    }
            if floor_calculation[line]['count'] < floor_calculation[line]['low_floor_limit']:
                modified_item['low_floor'] = True
            else:
                modified_item['low_floor'] = False
            floor_calculation[line]['count'] += 1
            if floor_calculation[line]['count'] >= floor_calculation[line]['max']:
                floor_calculation[line]['count'] = 0
            new_result.append(modified_item)
    return new_result


def order_of_arrive(menetrend):
    """ ordering with remained arrive minutes """
    return menetrend['arrive_minute']  # Calculated field


def check_if_proper_hour(min_hour, max_hour, arrive_time, time):
    if min_hour < max_hour and arrive_time.day != time.day:
        # daytime line, tomorrow day
        return False
    if min_hour < max_hour:
        if min_hour <= arrive_time.hour < max_hour:  # The normal
            # E.g. min hour: 6, actual hour: 14, max hour: 19
            return True
        else:
            return False
    # else: daytime
    if min_hour > max_hour:  # Night travel
        if min_hour <= arrive_time.hour and arrive_time.day == time.day:  # Same day
            return True
        elif arrive_time.hour < max_hour and arrive_time.day == (time.day + 1):  # Next day
            return True
        else:
            return False
    return True


def update_late_arrive_time_to_clock(menetrend):
    """ Update arrive minutes to real time """
    new_menetrend = []
    time = datetime.datetime.now()
    for item in menetrend:
        arrive_minute = item['arrive_minute']
        max_hour = item['max_hour']
        min_hour = item['min_hour']
        if isinstance(arrive_minute, str) and ':' in arrive_minute:
            arrive_time = datetime.datetime.strptime(arrive_minute, '%H:%M')
            if check_if_proper_hour(min_hour, max_hour, arrive_time, time):
                # It is OK
                new_item = item
            else:
                continue
        elif arrive_minute > 60:  # Lot of minutes, format it!
            delta = datetime.timedelta(minutes=arrive_minute)
            arrive_time = time + delta
            if check_if_proper_hour(min_hour, max_hour, arrive_time, time):
                # Format for readable
                arrive_time = datetime.datetime.strftime(arrive_time, '%H:%M')
                new_item = item
                new_item['arrive_minute'] = arrive_time
            else:
                continue
        elif arrive_minute == 0:
            new_item = item
            new_item['arrive_minute'] = TIME_ARRIVE_NOW_TEXT
        else:  # few minutes
            delta = datetime.timedelta(minutes=arrive_minute)
            arrive_time = time + delta
            if check_if_proper_hour(min_hour, max_hour, arrive_time, time):
                new_item = item
            else:
                continue
        new_menetrend.append(new_item)
    return new_menetrend


def get_menetrend(jarat=None, station=None, result=None):
    """ fill the menetrend table by SQL/DB result (rows)
        Application function (not for printing)"""
    html_result = ''
    html_result += '<html>\n'
    html_result += get_html_format_css()
    html_result += '<body>\n'
    now = datetime.datetime.now()
    if station:
        if result:
            result = precheck_menetrend2(result)  # Check if they travel
            result = update_menetrend_with_arrive_minutes(result)  # Add next arrive minute
            result = extend_get_next_menetrends(result)  # Add x new arrives
            result = extend_with_low_floor(result)  # Fill with low_floor field
            result = sorted(result, key=order_of_arrive)  # Sort
            result = update_late_arrive_time_to_clock(result)  # Check max_hour and beautify remained minutes (print clock)
            html_result += '<table>'
            html_result += '<tr><td>Megálló</td><td>Járat</td><td>Érkezik</td></tr>\n'
            for item in result:
                jarat_found = item['jarat']
                station_found = item['station']
                jarat_type = item['jarat_tipus']
                low_floor = item['low_floor']
                arrive_minute_remained = item['arrive_minute']
                now = datetime.datetime.now()
                try:
                    # 6 (minutes remained)
                    time = int(arrive_minute_remained)
                    time = now + datetime.timedelta(minutes=time)
                    time = datetime.datetime.strftime(time, '%H:%M')
                except:
                    # 'MOST'
                    if arrive_minute_remained == TIME_ARRIVE_NOW_TEXT:
                        time = datetime.datetime.strftime(now, '%H:%M')
                    else:
                        # '13:28' format
                        time = arrive_minute_remained
                text_color, background_color = get_color_by_jarmu_type(jarat_found, jarat_type)
                low_floor_start = '<u>' if low_floor else ''
                low_floor_end = '</u>' if low_floor else ''
                html_result += '<tr>'
                html_result += f'<td>{station_found}</td>' \
                        f'<td bgcolor="{background_color}">' \
                        f'<a href="jarat_nezet?jarat={jarat_found}&megallo={station_found}&time={time}">' \
                        f'<font color="{text_color}">{low_floor_start}{jarat_found}{low_floor_end}</font>' \
                        '</a>' \
                        '</td>' \
                        f'<td>{arrive_minute_remained}</td>'
                html_result += '</tr>\n'
            html_result += '</table>\n'
        else:
            html_result = 'Nincs találat :(<br />\n'
    #elif jarat:
    else:
        get_all = True
        if jarat:
            get_all = False
        html_result += '<table>\n'
        html_result += '<tr><td>Járat</td><td>Indulási idő</td>'
        html_result += '<td>Eddig közlekedik</td><td>Járatsűrűség</td><td>Megálló</td></tr>\n'
        result = precheck_menetrend(result, get_all)
        for item in result:
            jarat = item['jarat']
            jarat_type = item['jarat_tipus']
            text_color, background_color = get_color_by_jarmu_type(jarat, jarat_type)
            html_result += '<tr>'
            html_result += f'<td bgcolor="{background_color}">'
            html_result += f'<font color="{text_color}">{jarat}</font></td>'
            html_result += f'<td>{item["min_hour"]:02}:{item["start_minute"]:02}</td>' # Hour, Minute
            html_result += f'<td>{item["max_hour"]:02}:00</td>'
            html_result += f'<td>{item["jaratsuruseg_minute"]} perc</td>'
            html_result += f'<td>{item["station"]}</td>'
            html_result += '</tr>\n'
        html_result += '</table>\n'

    html_result += '<br>\n'
    html_result += f'{now.hour:02}:{now.minute:02}'
    html_result += '</body>\n'
    html_result += '</html>\n'

    return html_result


def get_menetrend_wrap(jarat=None, station=None, city=None, limit=100):
    """ Get menetrend with járat or megálló """
    result = get_db(jarat, station, city, limit)
    return get_menetrend(jarat, station, result)


def calculate_line_view(line, station, time):
    item_list = []
    result = get_db(jarat=line)
    for item in result:
        assert isinstance(item, dict)
        new_item = {}
        new_item['station'] = item['station']
        new_item['time'] = None
        new_item['is_tram_here'] = None
        new_item['start_minute'] = item['start_minute']
        item_list.append(new_item)

    actual_station_start_minute = 0  # start_minute is always in a simple integer (minutes)

    # Calculate station where we are
    for item in item_list:
        if item['station'] == station: # We check this station
            # Save this station times
            item['time'] = time
            actual_station_start_minute = item['start_minute']

    is_found = False
    was_first = False
    now = datetime.datetime.now()
    now_string = datetime.datetime.strftime(now, "%H:%M")
    now_with_fake_date = datetime.datetime.strptime(now_string, "%H:%M")
    # Calculate time for each field
    for index, item in enumerate(item_list):
        diff_minutes_time_from_actual_station = item['start_minute'] - actual_station_start_minute
        this_station_time = datetime.datetime.strptime(time, "%H:%M") + datetime.timedelta(minutes=diff_minutes_time_from_actual_station)
        item['time'] = datetime.datetime.strftime(this_station_time, "%H:%M")

        # Prepare datetime for comparing
        this_station_time.replace(year=now.year, month=now.month, day=now.day)

        if item['time'] == now_string:
            item['is_tram_here'] = True
            is_found = True
        elif this_station_time < now_with_fake_date:
            item['is_tram_here'] = False  # We left this
        elif this_station_time > now_with_fake_date and was_first is False:
            # We are before the first station. Do not sign anything!
            item['is_tram_here'] = False
            is_found = True
        elif this_station_time > now_with_fake_date and was_first is True and is_found is False:
            # Ohh, the next!
            # Create a fake item when we are between two stations, EXCEPT that is the first
            fake_element = copy.copy(item)
            fake_element['is_tram_here'] = True
            fake_element['time'] = now_string
            fake_element['station'] = ''
            item_list.insert(index, fake_element)
            item['is_tram_here'] = False
            is_found = True
        else:
            # Unhandled / Not arrived
            item['is_tram_here'] = False
        was_first = True

    return item_list


def get_line_view(line, station, time):
    """ WRAP Function - used in the MatiGO
    Returns with HTML code
    Note: This function (generated HTML) used in the menetrend - get_menetrend()"""

    station_list = calculate_line_view(line, station, time)

    html = ''
    html += '<html>'
    html += '<body>'
    html += f'<p>Járat: {line}, Megálló ahonnan tervezel: {station}</p>'
    html += '<table>'
    for item in station_list:
        html += '<tr>'
        html += '<td>'
        if item['is_tram_here']:
            html += '<img src="static/tram-car.png" title="tram">'
        else:
            html += '<img src="static/circle.png" title="tram">'
        html += '</td>'
        html += '<td>'
        html += item['time']
        html += '</td>'
        html += '<td>'
        html += item['station']
        html += '</td>'
        html += '</tr>'
    html += '</table>'
    html += '</body>'
    html += '</html>'

    return html


def generate_html_rows_by_jaratsuruseg(line, jaratsuruseg_minute, daytype_text):
    """ Auxuliary HTML generate for jaratsuruseg (line department) table
        Needed for 'get_menetrend_nyomtatas'
    """
    html = ''
    html += f'<tr><td>{daytype_text}</td></tr>\n'
    if jaratsuruseg_minute:
        min_hour = line['min_hour']
        max_hour = line['max_hour']
        start_minute = line['start_minute']
        for hour in range(min_hour, max_hour):
            html += '<tr>'
            html += f'<td>{hour}:</td>'
            for minute in range(start_minute, 60, jaratsuruseg_minute):
                html += f'<td>{minute:02d},</td>'
            html += '</tr>\n'
    else:
        html += '<tr><td>A járat nem közlekedik!</td></tr>\n'
    return html


def get_html_format_css():
    html_code = ''
    html_code += '<head>\n'
    html_code += '<style>\n'
    html_code += 'a:link { text-decoration: none; border-bottom:none;}'
    html_code += 'a:visited { text-decoration: none; border-bottom:none;}'
    html_code += 'a:active { text-decoration: none; border-bottom:none;}'
    html_code += '</style>\n'
    html_code += '</head>'
    return html_code


def get_menetrend_nyomtatas(station="valami", line=None, database=True, result=None):  # pylint: disable=too-many-locals disable=too-many-branches disable=too-many-statements
    """ Menetrend for one station """
    if database:
        if station:
            result = get_db(station=station)
        elif line:
            result = get_db(jarat=line)
        else:
            raise Exception('Nyomtatas not handled without station/line')
    else:
        pass
        # Use parameter 'result'
    need_to_break = False
    if len(result) >= 8:
        need_to_break = math.floor(len(result)/2)

    html_result = ''
    station_found = result[0]['station']
    html_result += '<html><body><table cellpadding="10" border="3">'
    html_result += '<tr><td><font size="24">Megálló</font></td>'
    html_result += f'<td><font size="24">{station_found}</font></td></tr>\n'
    jarat_map = set()
    break_header = ''
    jarat_types = {}
    for item in result:
        assert isinstance(item, dict)
        jarat_found = item['jarat']  # pylint: disable=invalid-sequence-index
        jarat_map.add(jarat_found)
        if jarat_found not in jarat_types:
            jarat_type = item['jarat_tipus']  # pylint: disable=invalid-sequence-index
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
    html_result += '</tr>\n'

    html_result += '<tr>'  # This shall be closed when we have too much lines
    for cnt, jarat_this in enumerate(jarat_map):
        if database:
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
            station_found = item['station']  # pylint: disable=invalid-sequence-index
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
        html_result += '<td>\n'
        # Menetrend table
        html_result += '<table>\n'
        jaratsuruseg_minute = item['jaratsuruseg_minute']  # workday jaratsuruseg
        line = result[this_station_index]
        html_result += generate_html_rows_by_jaratsuruseg(line, jaratsuruseg_minute, 'Hétköznap és munkanap')
        html_result += '</table>\n'  # End of menetrend table
        html_result += '\n'
        ####
        # Welcome to the new world, where the non-workday menetrend (line deparment table) has been appeared :)
        html_result += '<table>'  # Menetrend table
        jaratsuruseg_minute = item['jaratsuruseg_hetvege']  # non-workday jaratsuruseg
        html_result += generate_html_rows_by_jaratsuruseg(line, jaratsuruseg_minute, 'Hétvégén és munkaszüneti napokon')
        html_result += '</table>\n'  # End of menetrend table
        ####

        html_result += '</td></tr>'
        html_result += '</table>\n'  # End of station + starting time table
        html_result += '</td>\n'
    html_result += '</tr>'
    html_result += '</table></body></html>\n'
    return html_result


def get_all_lines():  # For 'Bus app'
    """ Get all lines for Bus app. Useful for selecting a line (where you get on) """
    result = get_db()
    line_set = set()
    for item in result:
        line_set.add(item['jarat'])  # pylint: disable=invalid-sequence-index
    return {'lines': list(line_set)}


def get_line_info(line):  # For 'Bus app'
    """ Get a fix line information for the Bus application """
    result = get_db(jarat=line)
    res_dict = {'line': line, 'end_station': 'végállomás', 'actual_bus_station': 'buszállomás', 'next_bus_station': 'Következő állomás'}
    if result:  # pylint: disable=too-many-nested-blocks
        now = datetime.datetime.now()
        end_station = 'Végállomás'
        last_start_minute = 0
        time_calculated = 0
        for item in result:
            min_hour = item['min_hour']  # pylint: disable=invalid-sequence-index
            max_hour = item['max_hour']  # pylint: disable=invalid-sequence-index
            jaratsuruseg = get_jaratsuruseg_by_day_type(item['jaratsuruseg_minute'], item['jaratsuruseg_hetvege'])  # pylint: disable=invalid-sequence-index
            start_minute = item['start_minute']  # pylint: disable=invalid-sequence-index
            actual_bus_station = item['station']  # pylint: disable=invalid-sequence-index
            if last_start_minute < start_minute:
                end_station = actual_bus_station  # Save this for end_station
                last_start_minute = start_minute
            if time_calculated == 1:
                time_calculated += 1
                res_dict['next_bus_station'] = item['station']  # pylint: disable=invalid-sequence-index
            if not time_calculated:
                if now.hour in range(min_hour, max_hour):
                    # Proper hour
                    for minute in range(start_minute, 59, jaratsuruseg):
                        if now.minute == minute:
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
        line_set.add(item['jarat'])  # pylint: disable=invalid-sequence-index
    for jarat_item in line_set:
        # Find in all items
        first_station = None
        end_station = None
        for item in result:
            jarat = item['jarat']  # pylint: disable=invalid-sequence-index
            if jarat_item == jarat:
                # Get the first element
                station = item['station']  # pylint: disable=invalid-sequence-index
                if not first_station:
                    first_station = station
                    jarat_type = item['jarat_tipus']  # pylint: disable=invalid-sequence-index
                end_station = station  # Set the end station
        # We have this line
        lines.append((jarat_item, first_station, end_station, jarat_type))

    html_result = '<html>\n'
    html_result += get_html_format_css()
    html_result += '<body><table>\n'
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
        html_result += f'<tr><td border="1" bgcolor="{background_color}"><font color="{text_color}"><a style="color:{text_color};" href="nyomtatas?jarat={jarat_number}">{jarat_number}</a></font></td><td>{first_station}</td></tr>\n'
        html_result += f'<tr><td border="1" bgcolor="{background_color}"><font color="{text_color}"><a style="color:{text_color};" href="nyomtatas?jarat={jarat_number}">{jarat_number}</a></font></td><td>{end_station}</td></tr>\n'
        html_result += '</table>\n'
        #
        html_result += '</td>'
        html_result += '</tr>\n'
    html_result += '</table></body></html>\n'
    return html_result


def get_all_nyomtatas_link():
    """ Get all links for the stations, which can be printed """
    result = get_db()
    station_set = set()
    for item in result:
        station = item['station']   # pylint: disable=invalid-sequence-index
        station_set.add(station)

    html_result = '<html><table>\n'
    stations = list(station_set)
    stations.sort()
    for station in stations:
        html_result += f'<tr><td><a href="https://mati.e5tv.hu/nyomtatas?megallo={station}">{station}</a><br /></td></tr>\n'
    html_result += '</table></html>\n'
    return html_result


class DayType(Enum):
    """ Enum for daytypes (workday or not) """
    NONE = 0
    WORKDAY = 1
    NOTWORKDAY = 2

def check_actual_day_type():
    """ Check the day type of actual date """
    now = datetime.datetime.now()
    if 1 <= now.isoweekday() <= 5:
        return DayType.WORKDAY
    return DayType.NOTWORKDAY


def get_jaratsuruseg_by_day_type(jaratsuruseg_workday, jaratsuruseg_nonworkday):
    """ Get jaratsuruseg (proper) by actual date (daytype) """
    workday_type = check_actual_day_type()
    if workday_type == DayType.WORKDAY:
        return jaratsuruseg_workday
    elif workday_type == DayType.NOTWORKDAY:
        return jaratsuruseg_nonworkday
    return jaratsuruseg_workday


def check_if_it_is_going(menetrend):
    """ Check if the line is going today. Maybe it does not go on non-workday """
    if get_jaratsuruseg_by_day_type(menetrend['jaratsuruseg_minute'], menetrend['jaratsuruseg_hetvege']):  # pylint: disable=simplifiable-if-statement
        return True
    else:  # Example: None jaratsuruseg
        return False


def get_all_available_cities():  # For MatiGO
    """ Get all available cities """
    result = get_db_cities()
    new_result = []
    for item in result:
        if item[0] is None:
            new_result.append(CITY_DONTCARE_TEXT)
        else:
            new_result.append(item[0])
    return new_result


def process_and_upload_line(line_infos):
    #line_infos['line']
    #line_infos['min_hour']
    #line_infos['max_hour']
    #line_infos['jaratsuruseg_minute']
    #line_infos['jaratsuruseg_hetvege']
    #line_infos['start_minute']
    #line_infos['station']
    #line_infos['line_type']
    #line_infos['city']
    #line_infos['low_floor']

    mydb = database_connection()

    mycursor = mydb.cursor()

    print('Connected to MySQL')

    sql = 'INSERT INTO `mati_menetrend` (`jarat`, `min_hour`, `max_hour`, `jaratsuruseg_minute`, `start_minute`, `station`, `jarat_tipus`, `jaratsuruseg_hetvege`, `varos`, `low_floor`) \
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    val = list(line_infos.values())
    print('Execute SQL command: ' + sql)
    try:
        mycursor.execute(sql, val)
        mydb.commit()
    except Exception as ex:
        mydb.close()
        raise ex

    mydb.close()


def process_and_edit_line(old_line_infos, new_line_infos):
    #line_infos['line']
    #line_infos['min_hour']
    #line_infos['max_hour']
    #line_infos['jaratsuruseg_minute']
    #line_infos['jaratsuruseg_hetvege']
    #line_infos['start_minute']
    #line_infos['station']
    #line_infos['line_type']
    #line_infos['city']
    #line_infos['low_floor']

    mydb = database_connection()

    mycursor = mydb.cursor()

    print('Connected to MySQL')

    # TODO: Note: Varos/City is hardcoded to NULL (IS NULL)
    sql = 'UPDATE `mati_menetrend` \
           SET `jarat` = %s, `min_hour` = %s, `max_hour` = %s,  `jaratsuruseg_minute` = %s,   `start_minute` = %s,  `station` = %s,  `jarat_tipus` = %s,  `jaratsuruseg_hetvege` = %s,  `low_floor` = %s \
           WHERE `jarat` = %s AND  `min_hour` = %s AND `max_hour` = %s AND  `jaratsuruseg_minute` = %s AND   `start_minute` = %s AND  `station` = %s AND  `jarat_tipus` = %s AND  `jaratsuruseg_hetvege` = %s AND   `varos` IS %s AND  `low_floor` = %s '
    val = list(new_line_infos.values() + old_line_infos.values())
    print('Execute SQL command: ' + sql)
    try:
        mycursor.execute(sql, val)
        mydb.commit()
        try:
            print(mycursor.statement)
        except:
            print(mycursor._executed)
    except Exception as ex:
        mydb.close()
        raise ex

    mydb.close()


def extend_db_with_edit_and_delete(lines_all, lines_all_headers):
    """ Return with new fields with HTML codes """
    new_lines_all = []
    new_lines_all_headers = []
    for line in lines_all:
        # Add edit
        link_get = '<a href="mati_adatbazis'
        for index, param in enumerate(lines_all_headers):
            if index == 0:
                link_get += '?'
            else:
                link_get += '&'
            link_get += param
            link_get += '='
            value_of_item = line[index]  # Value of the line item
            if isinstance(value_of_item, str):
                link_get += value_of_item
            else:
                link_get += str(value_of_item)
        new_item = copy.copy(line)
        assert isinstance(new_item, tuple)
        new_item = new_item + (link_get + '&is_edit=True' + '">Szerkesztés</a>', )
        # Add delete
        new_item = new_item + (link_get + '&is_edit=False&is_delete=True' + '">Törlés</a>', )
        new_lines_all.append(new_item)

    new_lines_all_headers = copy.copy(lines_all_headers)
    new_lines_all_headers = new_lines_all_headers + ('edit', 'delete')

    return new_lines_all, new_lines_all_headers


def delete_record(line_infos):
    mydb = database_connection()

    mycursor = mydb.cursor()

    print('Connected to MySQL')

    # Varos / CITY is hardcoded to null 'IS NULL'
    sql = 'DELETE FROM `mati_menetrend` \
           WHERE `jarat` = %s AND  `min_hour` = %s AND `max_hour` = %s AND  `jaratsuruseg_minute` = %s AND   `start_minute` = %s AND  `station` = %s AND  `jarat_tipus` = %s AND  `jaratsuruseg_hetvege` = %s AND   `varos` IS %s AND  `low_floor` = %s \
           LIMIT 1; '
    val = list(line_infos.values())
    print('Execute SQL command: ' + sql)
    print(val)
    try:
        mycursor.execute(sql, val)
        mydb.commit()
        try:
            print(mycursor.statement)
        except:
            print(mycursor._executed)
        #warnings = mycursor.get_warnings()  # TODO
        #print(warnings)
    except Exception as ex:
        mydb.close()
        raise ex

    mydb.close()

    return


if __name__ == '__main__':
    # Manual test
    #get_menetrend_wrap()
    # Test menetrend with fake result
    #sql_fake_result = [('6', 8, 22, 50, 0, 'Blaha Lujza tér')]

    import csv
    sql_fake_result = []
    with open('test_db.csv', newline='', encoding='utf-8') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        header_done = False  # pylint: disable=invalid-name
        for row in spamreader:
            if not header_done:
                header_done = row
            else:
                new_dict = {}
                for index, item in enumerate(row):
                    field_name = header_done[index]  # pylint: disable=unsubscriptable-object
                    new_dict[field_name] = item
                sql_fake_result.append(new_dict)
    # Beautify
    for item in sql_fake_result:
        # jarat;min_hour;max_hour;jaratsuruseg_minute;start_minute;station;jarat_tipus;jaratsuruseg_hetvege;varos
        int_values = ['min_hour', 'max_hour', 'jaratsuruseg_minute', 'start_minute', 'jaratsuruseg_hetvege']
        for key, val in item.items():
            if val == '"0"':
                item[key] = 0
            elif val == '':
                item[key] = None
            elif key in int_values:
                item[key] = int(val)

    TEST_MENETREND_JARAT = False
    if TEST_MENETREND_JARAT:
        res = get_menetrend(jarat='6', station=None, result=sql_fake_result)
        print(res)

    TEST_MENETREND_STATION = True
    if TEST_MENETREND_STATION:
        res = get_menetrend(jarat=None, station='Teszt1', result=sql_fake_result)
        print(res)
        #res = get_menetrend(jarat=None, station=None, result=sql_fake_result)
        #print(res)

    TEST_NYOMTATAS = False
    if TEST_NYOMTATAS:
        res = get_menetrend_nyomtatas(station="Bolya utca", database=False, result=sql_fake_result)
        print(res)

    check_actual_day_type()

    get_line_view(line='17', station='davvid', time='14:36')
