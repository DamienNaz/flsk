# app.py
from flask import Flask, render_template, request, flash
import requests
from datetime import datetime, timedelta
import time

app = Flask(__name__)
app.secret_key = 'super secret key'

def format_date_time(timestamp):
    dt_object = datetime.utcfromtimestamp(timestamp)
    return dt_object.strftime("%Y-%m-%d %H:%M:%S UTC")

def create_game_table(fixture):
    home_team = fixture['teams']['home']['name']
    away_team = fixture['teams']['away']['name']
    score_home = fixture['goals']['home']
    score_away = fixture['goals']['away']
    status = fixture['fixture']['status']['long']
    minutes = fixture['fixture']['status']['elapsed']

    table_row = f"{format_date_time(fixture['fixture']['timestamp'])}\n{home_team} {score_home if score_home is not None else 'N/A'} - {score_away if score_away is not None else 'N/A'} {away_team} ({status}, {minutes} min)"
    return table_row

@app.route("/filter_games", methods=["GET", "POST"], endpoint="filter_games_form")
def filter_games():
    if request.method == 'POST':
        min_minutes = int(request.form['min_minutes'])
        max_minutes = int(request.form['max_minutes'])
        min_goals = int(request.form['min_goals'])
        max_goals = int(request.form['max_goals'])

        url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
        querystring = {"live": "all"}

        headers = {
            "X-RapidAPI-Key": "42edaff283mshf3c8ef78d3fb068p15ff20jsn134491fdbdbf",
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)

        if response.status_code == 200:
            fixtures = response.json()['response']
            filtered_games = []

            for fixture in fixtures:
                elapsed_time = fixture['fixture']['status'].get('elapsed')
                home_goals = fixture['goals']['home']
                away_goals = fixture['goals']['away']

                if (elapsed_time is not None and home_goals is not None and away_goals is not None and
                        min_minutes <= elapsed_time <= max_minutes and
                        min_goals <= (home_goals + away_goals) <= max_goals):
                    filtered_games.append(create_game_table(fixture))

            return render_template('filtered_games.html', games_info=filtered_games)

        else:
            flash("Error in request: {}".format(response.status_code))

    return render_template('filter_games_form.html')

if __name__ == "__main__":
    app.run(debug=True)
