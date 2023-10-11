class SqlQueries:
    staging_events_table_create = """
        CREATE TABLE IF NOT EXISTS "staging_events" (
            artist        TEXT,
            auth          CHARACTER VARYING(20),
            firstName     CHARACTER VARYING(100),
            gender        CHAR(1),
            itemInSession SMALLINT,
            lastName      CHARACTER VARYING(100),
            length        DOUBLE PRECISION,
            level         CHARACTER VARYING(30),
            location      TEXT,
            method        CHARACTER VARYING(10),
            page          CHARACTER VARYING(30),
            registration  BIGINT,
            sessionId     INT,
            song          TEXT,
            status        SMALLINT,
            ts            BIGINT,
            userAgent     TEXT,
            userId        INT
        );
    """

    staging_songs_table_create = """
        CREATE TABLE IF NOT EXISTS "staging_songs" (
            num_songs           SMALLINT,
            artist_id           CHARACTER VARYING(30),
            artist_latitude     DOUBLE PRECISION,
            artist_longitude    DOUBLE PRECISION,
            artist_location     TEXT,
            name                TEXT,
            song_id             CHARACTER VARYING(30),
            title               TEXT,
            duration            DOUBLE PRECISION,
            year                SMALLINT
        );
    """
    songplay_table_insert = ("""
        SELECT
                md5(events.sessionid || events.start_time) songplay_id,
                events.start_time,
                events.userid,
                events.level,
                songs.song_id,
                songs.artist_id,
                events.sessionid,
                events.location,
                events.useragent
                FROM (SELECT TIMESTAMP 'epoch' + ts/1000 * interval '1 second' AS start_time, *
            FROM staging_events
            WHERE page='NextSong') events
            LEFT JOIN staging_songs songs
            ON events.song = songs.title
                AND events.artist = songs.artist_name
                AND events.length = songs.duration
    """)

    user_table_insert = ("""
        SELECT distinct userid, firstname, lastname, gender, level
        FROM staging_events
        WHERE page='NextSong'
    """)

    song_table_insert = ("""
        SELECT distinct song_id, title, artist_id, year, duration
        FROM staging_songs
    """)

    artist_table_insert = ("""
        SELECT distinct artist_id, artist_name, artist_location, artist_latitude, artist_longitude
        FROM staging_songs
    """)

    time_table_insert = ("""
        SELECT start_time, extract(hour from start_time), extract(day from start_time), extract(week from start_time),
               extract(month from start_time), extract(year from start_time), extract(dayofweek from start_time)
        FROM songplays
    """)