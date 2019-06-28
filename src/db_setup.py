import psycopg2
import logging

ConnString = "dbname='fantasy_bball' user= 'postgres' host= 'localhost' port='5430' password = '' "


def ExecuteNonQuery(sql):
    with psycopg2.connect(ConnString) as conn:
        with conn.cursor() as curs:
            try:
                curs.execute(sql)
            except psycopg2.Error as error:
                print(error)


def ExecuteQuery(query):
    try:
        print('About to try an connectr')
        print(query)
        conn = psycopg2.connect(ConnString)
    except:
        logging.error("I am unable to connect to the database")
        conn = None
    if conn:
        print('We have a connection')
        cur = conn.cursor()
        try:
            cur.execute(query)
            rows = cur.fetchall()
            return rows

        except Exception as e:
            logging.error('Major issue connecting: {}'.format(e))
    else:
        logging.error("Exiting without connecting to database")

def CreateDb():
    query = """CREATE DATABASE fantasy_bball
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;"""


def CreateSchemas():
    commands = (
        """ CREATE SCHEMA stat AUTHORIZATION postgres;""",
        """CREATE SCHEMA basic_info AUTHORIZATION postgres;""",
        """CREATE SCHEMA fantasy_details AUTHORIZATION postgres;"""
    )
    for command in commands:
        ExecuteNonQuery(command)

def CreateTables():
    commands = (
        """
        CREATE TABLE stat.player_game_line(
          id SERIAL NOT NULL,
          player_id integer NOT NULL,
          game_id integer NOT NULL,
          total_pt integer NOT NULL DEFAULT 0,
          three_pointers_made integer NOT NULL DEFAULT 0,
          rebound integer NOT NULL DEFAULT 0,
          assist integer NOT NULL DEFAULT 0,
          steal integer NOT NULL DEFAULT 0,
          turnover integer NOT NULL DEFAULT 0,
          block integer NOT NULL DEFAULT 0,
          CONSTRAINT position_key PRIMARY KEY (id)
          )""",
        """
        CREATE TABLE basic_info.player(
           id SERIAL NOT NULL,
           player_id integer NOT NULL,
           first_name text NOT NULL,
           last_name text NOT NULL,
           team_id integer NOT NULL,
           pos_id integer NOT NULL,
           active boolean DEFAULT true,
           CONSTRAINT player_pkey PRIMARY KEY (id)
           )""",
        """
        CREATE TABLE basic_info.position(
            id SERIAL NOT NULL,
            name text NOT NULL,
            abbr text NOT NULL,
            CONSTRAINT position_pkey PRIMARY KEY (id)
            )""",
        """
             CREATE TABLE basic_info.team(
                 id SERIAL NOT NULL,
                 nba_team_id integer NOT NULL,
                 name text NOT NULL,
                 tricode text NOT NULL,
                 CONSTRAINT team_pkey PRIMARY KEY (id)
                 )""",
        """
        CREATE TABLE basic_info.schedule(
            id SERIAL NOT NULL,
            nba_game_id oid NOT NULL,
            game_time timestamp without time zone NOT NULL,
            home_team_id integer NOT NULL,
            home_team_score integer,
            road_team_id integer NOT NULL,
            road_team_score integer
            )""",
        """
        CREATE TABLE fantasy_details.league(
            id SERIAL NOT NULL,
            name text NOT NULL,
            CONSTRAINT league_pkey PRIMARY KEY (id)
            )""",
        """
        CREATE TABLE fantasy_details.point_type(
            id SERIAL NOT NULL,
            name text NOT NULL,
            CONSTRAINT point_type_pkey PRIMARY KEY (id)
            )""",
        """
        CREATE TABLE fantasy_details.scoring(
            id SERIAL NOT NULL,
            point_type_id integer NOT NULL,
            league_id integer NOT NULL,
            value double precision NOT NULL,
            CONSTRAINT scoring_key PRIMARY KEY (id)
            )"""
    )
    for query in commands:
        ExecuteNonQuery(query)


if __name__ == "__main__":
    pass
    # CreateTables()