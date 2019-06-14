import psycopg2
import logging

ConnString = "dbname='basketball' user= 'postgres' host= '192.168.0.5' password = '' "

def ExecuteQuery(query):
    try:
        conn = psycopg2.connect(ConnString)
    except:
        logging.error("I am unable to connect to the database")
    
    cur = conn.cursor()
    try:
        cur.execute(query)
    except Exception as e:
        logging.error('Major issue connecting: {}'.format(e))


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
                CONSTRAIN player_pkey PRIMARY KEY (id)
                )""",
            """
            CREATE TABLE basic_info.position(
                id SERIAL NOT NULL,
                name text NOT NULL,
                abbr text NOT NULL,
                CONSTRAINT position_pkey PRIMARY KEY (id)
                )""",
            """
            CREATE TABLE basic_info.schedule(
                id SERIAL NOT NULL,
                nba_game_id oid NOT NULL,
                game_time timestamp without time zone NOT NULL,
                home_team_id integer NOT NULL,
                home_team_score integer,
                road_team_id integer NOT NULL,
                road_team_score
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
        rows = ExecuteQuery(commands)
        return rows
