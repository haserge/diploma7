from datetime import datetime

import requests
from flask import Flask, render_template, request

app = Flask(__name__)
print("Frontend v1.6 is ready")


# get json data from backend
def get_json_data(item_path):
    url = f'http://backend:5000/{item_path}'
    resp = requests.get(url)
    if resp.status_code == 200:
        out_data = resp.json()
    else:
        print("We have a problem connecting to the backend. Status code = ", resp.status_code)
    return out_data


# the set_date and update routes are handled in the backend
@app.route("/", methods=("GET", "POST"))
def start_page():
    if request.method == "POST":
        update_value = request.form["data_update"]
        if update_value:
            item_path = "update"
            data_for_update = get_json_data(item_path)
            with app.app_context():
                if data_for_update == []:
                    rendered = render_template("no_updates_page.html")
                else:
                    rendered = render_template("update_page.html", data=data_for_update)
            return rendered
        else:
            set_date = request.form["set_date"]
            if set_date:
                script_datetime = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                with app.app_context():
                    item_path = "get_data/" + set_date
                    rendered = render_template("db_data.html", data=get_json_data(item_path), date_time=script_datetime)
                return rendered
    return render_template("start_page.html")


# the delete route is handled in the backend
@app.route("/delete", methods=("GET", "POST"))
def delete():
    if request.method == "POST":
        item_path = "delete"
        return render_template("delete_page.html", info=get_json_data(item_path))
    return render_template("delete_page.html")


# if __name__ == "__main__":
#     app.run(host="0.0.0.0")