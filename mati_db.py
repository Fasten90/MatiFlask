import os
import mysql.connector


def database_connection():
    mydb = mysql.connector.connect(
        host='localhost' if not os.getenv('DB_REMOTE', False) else os.getenv('DB_REMOTE'),
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

    return result

