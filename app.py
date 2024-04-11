import os

from flask import Flask, render_template, flash, request, redirect, session, send_from_directory
from flask_wtf import csrf

import mati_db

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
from datetime import datetime, timedelta, date
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
                hour = request.args.get('hour', type = int)
                minute = request.args.get('minute', type = int)
                second = request.args.get('second', type = int)
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
    if request.method == 'GET':
        try:
            jarat = request.args.get('jarat', type = int)
            station = request.args.get('megallo', type = str)
            limit = request.args.get('limit', type = int, default=100)
        except Exception as ex:
            print('Exception: {}'.format(ex))
    return mati_db.get_menetrend_wrap(jarat, station, limit)


@app.route('/nyomtatas', methods=['GET'])
def get_menetrend_nyomtatas():
    if request.method == 'GET':
        try:
            station = request.args.get('megallo', type = str)
        except Exception as ex:
            print('Exception: {}'.format(ex))
        result = mati_db.get_menetrend_nyomtatas(jarat=None, station=station)
    else:
        result = 'It only works with ?megallo=<megallonev>'
    return result


# For debug: Start debug mode this file
if __name__ == '__main__':
    app.run()
