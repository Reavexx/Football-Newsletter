import requests
from datetime import datetime

url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

querystring = {"season": "2023", "team": "15"}

headers = {
    "X-RapidAPI-Key": "dd8fc01dcamsh6ae6e415ceaa845p11bdfcjsn0ca5dd4831ca",
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

class Api:
    def apiRequest():
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()

        fixtures = data['response']

        return fixtures
    
    def getGames():
        all_fixtures = Api.apiRequest()

        fixtures_to_send = []
        
        # Current date
        current_date = datetime.now()

        for fixture in all_fixtures:
            home_team = fixture['teams']['home']['name']
            away_team = fixture['teams']['away']['name']
            league_name = fixture['league']['name']
            venue_name = fixture['fixture']['venue']['name']
            date_str = fixture['fixture']['date']

            # Split the date and time components
            date_components = date_str.split("T")
            date_part = date_components[0]
            time_part = date_components[1].split("+")[0]

            # Combine date and time components into a new date string
            parsed_date_str = f"{date_part} {time_part}"

            # Convert the parsed date string to a datetime object
            date = datetime.strptime(parsed_date_str, "%Y-%m-%d %H:%M:%S")

            # Calculate the difference between the dates
            time_difference = date - current_date

            # Extract the number of days from the time difference
            days_left = time_difference.days

            # Check if games are in 4 weeks or less
            if days_left <= 28 and days_left >= 0:
                # Append the fixture information as a sublist
                fixture_info = [
                    f"Home Team: {home_team}",
                    f"Away Team: {away_team}",
                    f"League Name: {league_name}",
                    f"Venue: {venue_name}",
                    f"Date: {date}"
                ]
                fixtures_to_send.append(fixture_info)
        
        return fixtures_to_send
    
    def send_or_not():
           fixtures_to_send = Api.getGames()
           for fixture_info in fixtures_to_send:
               date_str = fixture_info[4].split(": ")[1]
               date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
               if date.day % 4 == 0:
                   return True
           return False
