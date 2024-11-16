import os
from datetime import datetime, timedelta, date

from flask import Flask, render_template, flash, request, redirect, session, send_from_directory
from flask_wtf import csrf

import mati_db
import forms

app = Flask(__name__)
csrf = csrf.CSRFProtect(app)

DEBUG = True

app.debug = True
app.config['SECRET_KEY'] = 'you-will-never-guess'


@app.route('/')
def root_html():
    return send_from_directory('static', 'index.html')


@app.route('/favicon.ico')
def favicon():
    # 'app.send_static_file' does not work
    return send_from_directory('static', 'favicon.ico')


@app.route('/robots.txt')
def robots_txt():
    return send_from_directory('static', 'robots.txt')


clock_time = '13:26:41'
last_set_time = None
@app.route('/clock', methods=['GET', 'POST'])
def clock():
    global clock_time
    global last_set_time
    try:
        if request.method == 'POST':
            print(request)
            return clock_time
        elif request.method == 'GET':
            try:
                hour = request.args.get('hour', type=int)
                minute = request.args.get('minute', type=int)
                second = request.args.get('second', type=int)
                if not hour or not minute or not second:
                    print('missed value, skip it')
                    if not last_set_time:
                        # Never was set, send the set time
                        return clock_time
                    else:
                        # It was set once
                        now_time = datetime.now()
                        delta_time = now_time - last_set_time
                        clock_time_object = datetime.strptime(clock_time, '%H:%M:%S')
                        clock_time_object = datetime.combine(date.today(), clock_time_object.time())
                        sending_time = clock_time_object + delta_time
                        return sending_time.strftime("%H:%M:%S")
                else:
                    clock_time = "{}:{}:{}".format(hour, minute, second)
                    last_set_time = datetime.now()
                    print('Set clock to: {}'.format(clock_time))
                    return 'Successfully set'
            except Exception as ex:
                print('Exception: {}'.format(ex))
                return "[ERROR] "+ str(ex)
        else:
            print('[ERROR] Not acceptable request')
            return clock_time
    except Exception as e:
        return '[ERROR] ' + str(e)


@app.route('/menetrend', methods=['GET'])
def get_menetrend():
    try:
        line = request.args.get('jarat', type=int)
        station = request.args.get('megallo', type=str)
        city = request.args.get('varos', type=str)
        limit = request.args.get('limit', type=int, default=100)
        result = mati_db.get_menetrend_wrap(line, station, city, limit)
    except Exception as ex:
        result = 'FATAL ERROR: Please report it to Apa/Vizi Gábor:<br />\r\n' \
                'https://github.com/Fasten90/MatiFlask<br />\r\n'  \
                f'{ex}'
    return result


@app.route('/all_lines', methods=['GET'])
def get_all_lines():
    return mati_db.get_all_lines_html()


@app.route('/all_cities', methods=['GET'])
def get_all_available_cities():
    return mati_db.get_all_available_cities()


@app.route('/nyomtatas', methods=['GET'])
def get_menetrend_nyomtatas():
    if request.method == 'GET':
        try:
            station = request.args.get('megallo', type=str, default=None)
            line = request.args.get('jarat', type=str, default=None)
        except Exception as ex:
            print('Exception: {}'.format(ex))
        result = mati_db.get_menetrend_nyomtatas(station=station, line=line)
    else:
        result = 'It only works with ?megallo=<megallonev>'
    return result


@app.route('/get_all_nyomtatas', methods=['GET'])
def get_all_nyomtatas():
    return mati_db.get_all_nyomtatas_link()


@app.route('/bus', methods=['GET'])
def get_menetrend_bus():
    if request.method == 'GET':
        try:
            line = request.args.get('line', type=str)
            get_lines = request.args.get('lines', type=bool, default=False)
        except Exception as ex:
            print('Exception: {}'.format(ex))
        if get_lines:
            result = mati_db.get_all_lines()
        elif line:
            result = mati_db.get_line_info(line)
        else:
            result = 'It only works with bus?line=5 or bus?lines'
    else:
        result = 'It only works with bus?line=5 or bus?lines'
    return result


@app.route('/mati_adatbazis', methods=['GET', 'POST'])
def mati_adatbazis():

    form = forms.MatiAdatbazisFeltoltes()

    lines_all, lines_all_headers = None, None

    if request.method == 'POST':
        try:
            if form.validate():
                line_infos = {}
                line_infos['line'] = request.form['jarat']
                line_infos['min_hour'] = request.form['min_hour']
                line_infos['max_hour'] = request.form['max_hour']
                line_infos['jaratsuruseg_minute'] = request.form['jaratsuruseg_minute']
                line_infos['start_minute'] = request.form['start_minute']
                line_infos['station'] = request.form['station']
                line_infos['line_type'] = request.form['jarat_tipus']
                line_infos['jaratsuruseg_hetvege'] = request.form['jaratsuruseg_hetvege']
                line_infos['city'] = None  # By default we ignore it
                print('Received content: ' + str(line_infos))
                result = mati_db.process_and_upload_line(line_infos)
                flash('Result: ' + result)

                lines_all, lines_all_headers = mati_db.get_db_all()
            else:
                print('CSRF ERROR')
        except Exception as ex:
            flash('Result: ' + str(ex))
            print(str(ex))
    else:
        # First call, put default data
        #form.content.data = 'default'
        lines_all, lines_all_headers = mati_db.get_db_all()

    return render_template('mati_adatbazis.html', title='Mati Adatbázis', form=form, lines_all=lines_all, lines_all_headers=lines_all_headers)


tereles_info = ''
@app.route('/tereles', methods=['GET', 'POST'])
def tereles():
    try:
        if request.method == 'POST':
            print(request)
            global tereles_info
            tereles_info  = request.content
            return tereles_info
        elif request.method == 'GET':
            new_text = request.args.get('new', type=str)
            global tereles_info
            tereles_info = new_text
            return tereles_info
        else:
            return tereles_info
    except Exception as ex:
        print('Exception: {}'.format(ex))
        return '[ERROR] ' + str(ex)


# For debug: Start debug mode this file
if __name__ == '__main__':
    app.run()
