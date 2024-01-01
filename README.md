# Goal

The goal of this project is to create an ETL pipeline that adds songs featured on the Instagram account, @sleepingongems, to a Spotify playlist.

# Technologies & Tools
- Python
- PostgreSQL
- Selenium
- Flask
- RegEx
- Psycopg2
- Spotify API

# Workflow
1. Extract

The first step of this project is to collect data from the Instagram account. To do this, I used Selenium to replicate user movement. User movement replication is needed so that data from each post can be collected.
The following data is collected and stored in a Postgres database for transformation:
- ID (SQL SERIAL type)
- Post URL
- Caption
- Date
- Likes

2. Transformation

The second step is to transform the collected, raw data into feasible data that can be passed through the Spotify API. Songs are contained within the caption of each post. Songs that are featured in a post follow the form of "Artist Name - Song Name". With a consistent naming convention, regular expression is used to transform a caption into "Artist Name - Song Name", if one exists.
Cleaned captions are stored in another table within the Postgres database, which will be used for the Spotify API.

3. Load

Adding songs to a Spotify playlist requires specific scopes, which can only be enabled through Spotify OAuth. Flask is used to enable user authorization. Once permission is granted, songs from the database will be added to a Spotify playlist using a Spotify API endpoint.


Check out the playlist here!: https://open.spotify.com/playlist/2INb5Xbunic5Ztczd6GIBt?si=cf5ce72a6eea4c2f
