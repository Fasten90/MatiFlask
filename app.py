import os
import traceback
from datetime import datetime, timedelta, date
import copy

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


# /static/ available

def error_log(line):
    dirpath = os.path.dirname(os.path.abspath(__file__))
    now = datetime.now()
    with open(dirpath + '/app_error.log', 'a') as file:
        file.write(str(now) + ' ' + line + '\n')


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
        result = 'FATAL ERROR: Kérlek szólj Apa/Vizi Gábor-nak:<br />\r\n' \
                '<a href="https://github.com/Fasten90/MatiFlask">https://github.com/Fasten90/MatiFlask</a><br />\r\n'  \
                f'{ex}'
        result += traceback.format_exc()
    return result


@app.route('/jarat_nezet', methods=['GET'])
def get_jarat_nezet():
    try:
        line = request.args.get('jarat', type=str)
        station = request.args.get('megallo', type=str)
        time = request.args.get('time', type=str)
        result = mati_db.get_line_view(line, station, time)
    except Exception as ex:
        result = 'FATAL ERROR: Kérlek szólj Apa/Vizi Gábor-nak:<br />\r\n' \
                '<a href="https://github.com/Fasten90/MatiFlask">https://github.com/Fasten90/MatiFlask</a><br />\r\n'  \
                f'{ex}'
        result += traceback.format_exc()
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


def get_params():
    # Empty line
    empty_line = {}
    empty_line['line'] = ''  # TODO: DB dolumn
    empty_line['min_hour'] = None
    empty_line['max_hour'] = None
    empty_line['jaratsuruseg_minute'] = None
    empty_line['start_minute'] = None
    empty_line['station'] = ''
    empty_line['line_type'] = '' # TODO: DB dolumn
    empty_line['jaratsuruseg_hetvege'] = None
    empty_line['city'] = None  # By default we ignore it
    empty_line['low_floor'] = ''
    empty_line['is_edit'] = False

    try:
        edit_line = copy.copy(empty_line)
        edit_line['line'] = request.args.get('jarat', type=str)  #TODO: DB dolumn
        edit_line['min_hour'] = request.args.get('min_hour', type=int)
        edit_line['max_hour'] = request.args.get('max_hour', type=int)
        edit_line['jaratsuruseg_minute'] = request.args.get('jaratsuruseg_minute', type=int)
        edit_line['start_minute'] = request.args.get('start_minute', type=int)
        edit_line['station'] = request.args.get('station', type=str)
        edit_line['line_type'] = request.args.get('jarat_tipus', type=str)  #TODO: DB dolumn
        edit_line['jaratsuruseg_hetvege'] = request.args.get('jaratsuruseg_hetvege', type=int)
        #edit_line['city'] = request.args.get('varos', type=str)  # By default we ignore it
        edit_line['city'] = None
        edit_line['low_floor'] = request.args.get('low_floor', type=str)
        edit_line['is_edit'] = request.args.get('is_edit', type=str)
        edit_line['is_delete'] = request.args.get('is_delete', type=str)
    except:
        return empty_line
    return edit_line


@app.route('/mati_adatbazis', methods=['GET', 'POST'])
def mati_adatbazis():
    result = ''

    if request.method == 'GET':
        is_modify = False
        try:
            # TODO: MERGE THEM
            edit_line = get_params()
            assert isinstance(edit_line, dict)
            if edit_line['is_edit'] == 'True':
                # Get - edit - not edited, but started to editing
                form = forms.MatiAdatbazisFeltoltes()
                form.jarat.default = edit_line['line']
                form.min_hour.default = edit_line['min_hour']
                form.max_hour.default = edit_line['max_hour']
                form.jaratsuruseg_minute.default = edit_line['jaratsuruseg_minute']
                form.start_minute.default = edit_line['start_minute']
                form.station.default = edit_line['station']
                form.jarat_tipus.default = edit_line['line_type']  #TODO: DB dolumn
                form.jaratsuruseg_hetvege.default = edit_line['jaratsuruseg_hetvege']
                #form.varos.default = edit_line['city']  # We ignore it
                form.low_floor.default = edit_line['low_floor']
                form.is_edit.default = edit_line['is_edit']
                #form.is_delete  # Non existing field in the form
                form.process()
                result += 'Form processed\n'
            elif edit_line['is_delete'] == 'True':
                is_modify = True
                # Get - delete
                result += 'Delete parameter!\n'
                form = forms.MatiAdatbazisFeltoltes()
            else:
                result += 'No edit, no delete!\n'
                form = forms.MatiAdatbazisFeltoltes()
        except:
            # Parameter issues, create a pure form
            result += 'Parameter issue!\n'
            form = forms.MatiAdatbazisFeltoltes()
        try:
            if is_modify:
                result += 'Modification required\n'
                if edit_line['is_delete'] == 'True':
                    result += 'Delete required'
                    del edit_line['is_edit']
                    del edit_line['is_delete']
                    mati_db.delete_record(edit_line)
        except Exception as ex:
            result += str(ex)
            flash('Result: ' + str(ex))
            print(str(ex))
            error_log(result)

    if request.method == 'POST':
        try:
            #if form.validate_on_submit():
            # TODO: Resolve
            if True:
                error_log('1')
                new_line_infos = {}
                new_line_infos['line'] = request.form['jarat']  #TODO: DB dolumn
                new_line_infos['min_hour'] = request.form['min_hour']
                new_line_infos['max_hour'] = request.form['max_hour']
                new_line_infos['jaratsuruseg_minute'] = request.form['jaratsuruseg_minute']
                new_line_infos['start_minute'] = request.form['start_minute']
                new_line_infos['station'] = request.form['station']
                new_line_infos['line_type'] = request.form['jarat_tipus']  #TODO: DB dolumn
                new_line_infos['jaratsuruseg_hetvege'] = request.form['jaratsuruseg_hetvege']
                new_line_infos['city'] = None  # By default we ignore it
                new_line_infos['low_floor'] = request.form['low_floor']
                error_log('4.5')
                #is_edit = request.form['is_edit']  # Not a good check  # Somewhy it cannot be checked
                error_log('4.6')
                print('Received content: ' + str(new_line_infos))
                error_log('2')
                #if is_edit:  # Not a good heck
                    # Edited upload
                edit_line = get_params()
                if 'is_edit' in edit_line and edit_line['is_edit'] == 'True':
                    del edit_line['is_edit']
                    del edit_line['is_delete']
                    del new_line_infos['city']  # Ignored
                    error_log('3')
                    mati_db.process_and_edit_line(edit_line, new_line_infos)
                else:
                    # Pure upload
                    error_log('4')
                    mati_db.process_and_upload_line(new_line_infos)
                # TODO: flash('Result: ' + result)
            else:
                result += 'CSRF ERROR'
                print('CSRF ERROR')
        except Exception as ex:
            result += str(ex)
            flash('Result: ' + str(ex))
            print(str(ex))
            error_log(result)
        # Pure form
        form = forms.MatiAdatbazisFeltoltes()
    else:
        # First call, put default data
        form = forms.MatiAdatbazisFeltoltes()
        pass

    lines_all, lines_all_headers = mati_db.get_db_all()
    # Extend table with 'Edit' and 'delete' mode
    lines_all, lines_all_headers = mati_db.extend_db_with_edit_and_delete(lines_all, lines_all_headers)

    print(f'Result: "{result}"')
    return render_template('mati_adatbazis.html', title='Mati Adatbázis', form=form, lines_all=lines_all, lines_all_headers=lines_all_headers, result=result)


tereles_info = ''
@app.route('/tereles', methods=['GET', 'POST'])
def tereles():
    try:
        global tereles_info
        if request.method == 'POST':
            print(request)
            tereles_info = request.content
            return tereles_info
        elif request.method == 'GET':
            try:
                new_text = request.args.get('new', type=str)
                if new_text:
                    tereles_info = str(new_text)
                return tereles_info
            except Exception as ex:
                print('There is no "new" arg.')
            return tereles_info
        else:
            return tereles_info
    except Exception as ex:
        print('Exception: {}'.format(ex))
        return '[ERROR] ' + str(ex)


# For debug: Start debug mode this file
if __name__ == '__main__':
    app.run()
