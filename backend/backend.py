import migrate
from datetime import datetime
import requests, calendar
from flask import Flask, jsonify

woeid = 2122265
month = datetime.now().month
year = datetime.now().year
format1 = "%Y-%m-%dT%H:%M:%S.%fZ"
format2 = "%d.%m.%Y %H:%M:%S.%f"
format3 = "%Y-%m-%d"
format4 = "%d.%m.%Y"
name_table = migrate.name_table
run_date = 1
data_for_update = []


# getting weather forecast data in json format from api
def get_json_data(mm, dd):
    url = f'https://www.metaweather.com/api/location/{woeid}/{year}/{mm}/{dd}/'
    resp = requests.get(url)
    if resp.status_code == 200:
        weather = resp.json()
    else:
        print("We have a problem with getting data from api, status code = ", resp.status_code)
    return weather


# parse json data and insert it into database table
def prepare_data(raw_data, rows_exist_in_db, save_row_for_update):
    cursor = migrate.create_con_cur()
    for i in range(0, len(raw_data)):
        forecast_id = raw_data[i]["id"]
        if forecast_id not in rows_exist_in_db:
            weather_state_name = raw_data[i]["weather_state_name"]
            wind_direction_compass = raw_data[i]["wind_direction_compass"]
            created = raw_data[i]["created"]
            applicable_date = raw_data[i]["applicable_date"]
            min_temp = raw_data[i]["min_temp"]
            max_temp = raw_data[i]["max_temp"]
            the_temp = raw_data[i]["the_temp"]
            cursor.execute("insert into " + name_table + " values (%s, %s, %s, %s, %s, %s, %s, %s)",
                           (forecast_id, weather_state_name, wind_direction_compass, created, applicable_date, min_temp,
                            max_temp, the_temp))
            if save_row_for_update:
                new_row = [forecast_id, weather_state_name, wind_direction_compass, datetime.strptime(created, format1).strftime(format2),
                           datetime.strptime(applicable_date, format3).strftime(format4), round(min_temp, 1), round(max_temp, 1), round(the_temp, 1)]
                # rows added during last update (after clicking the Data update button)
                data_for_update.append(new_row)
    cursor.close()


# load data by days from api and check if they are in the database
def store_data_into_db(first_date, from_update):
    global run_date
    print("Start update data from day number:", run_date)
    for day in range(first_date, calendar.monthrange(year, month)[1] + 1):
        check_date = (str(year) + '-' + str(month) + '-' + str(day))
        rows_exist_in_db = data_from_db(check_date, "id", "data_check")
        if not rows_exist_in_db or day >= run_date:
            print("Load data from api www.metaweather.com. Day:", day)
            prepare_data(get_json_data(month, day), rows_exist_in_db, from_update)
    run_date = datetime.now().day
    print("Next time the data will be updated from day number:", run_date)


# update data (after clicking the Data update button)
def db_data_update():
    global run_date
    data_for_update.clear()
    if datetime.now().day < run_date:
        run_date = 1
    store_data_into_db(run_date, True)


# get data from database
def data_from_db(applicable_date, db_field, who_request):
    cursor = migrate.create_con_cur()
    cursor.execute("select " + db_field + " from " + name_table + " where applicable_date = '" + applicable_date + "' order by created")
    rows = cursor.fetchall()
    ids_for_check = []
    rows_for_html = []
    output_data = []
    # form a list for later comparison
    if who_request == "data_check":
        for row in rows:
            ids_for_check.append(row[0])
        output_data = ids_for_check
    # create a list to display on a web page
    elif who_request == "show_data":
        for row in rows:
            row_for_html = list(row)
            row_for_html[3] = datetime.strptime(row[3], format1).strftime(format2)
            row_for_html[4] = datetime.strftime(row[4], format4)
            row_for_html[5] = round(row[5], 1)
            row_for_html[6] = round(row[6], 1)
            row_for_html[7] = round(row[7], 1)
            rows_for_html.append(row_for_html)
        output_data = rows_for_html
    cursor.close()
    return output_data


# delete the latest forecast for today from the database (for testing purposes)
def delete_row():
    cursor = migrate.create_con_cur()
    applicable_date = (str(year) + "-" + str(month) + "-" + str(datetime.now().day))
    cursor.execute("select max(created) from " + name_table + " where applicable_date = '" + applicable_date + "'")
    max_created = cursor.fetchone()
    if max_created[0] is None:
        message = "There are no more rows in database for current day"
    else:
        cursor.execute("select * from " + name_table + " where created = '" + max_created[0] + "'")
        deleted_row = cursor.fetchall()
        cursor.execute("delete from " + name_table + " where id = " + str(deleted_row[0][0]))
        message = "Forecast " + str(deleted_row[0][0]) + " for " + datetime.strftime(deleted_row[0][4], format4) + \
                  " created " + datetime.strptime(deleted_row[0][3], format1).strftime(format2) + " deleted from the database."
        cursor.close()
    return message


app = Flask(__name__)
print("Backend v1.8 is ready")
load_start_time = datetime.now()
store_data_into_db(run_date, False)
load_end_time = datetime.now()
print("Data received for: ", load_end_time - load_start_time, " sec.")


@app.route("/get_data/<set_date>", methods=["GET"])
def start_page(set_date):
    data = data_from_db(set_date, "*", "show_data")
    return jsonify(data)


@app.route("/update", methods=["GET"])
def update():
    db_data_update()
    return jsonify(data_for_update)


@app.route("/delete", methods=["GET"])
def delete():
    info = delete_row()
    return jsonify(info)


# if __name__ == "__main__":
#     app.run(host="0.0.0.0")