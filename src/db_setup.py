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


def AddFunctionsToDb():
    commands = (
        """
        CREATE OR REPLACE FUNCTION stat.add_player_stat_line(
            _nba_player_id integer,
            _nba_game_id integer,
            _total_pt integer,
            _three_pointers_made integer,
            _rebound integer,
            _assist integer,
            _steal integer,
            _turnover integer,
            _block integer)
          RETURNS void AS
            $BODY$
            DECLARE _id integer;
            BEGIN
                INSERT INTO stat.player_game_line(player_id,game_id,total_pt,three_pointers_made,rebound,assist,steal,turnover,block)
                SELECT player.id player_id, schedule.id game_id,_total_pt,_three_pointers_made,_rebound,_assist,_steal,_turnover,_block
                FROM basic_info.player player
                LEFT OUTER JOIN basic_info.schedule schedule
                ON schedule.nba_game_id = _nba_game_id
                WHERE nba_player_id = _nba_player_id;
            END
            $BODY$
              LANGUAGE plpgsql VOLATILE
                  COST 100;
        ALTER FUNCTION stat.add_player_stat_line(integer, integer, integer, integer, integer, integer, integer, integer, integer)
          OWNER TO postgres;

        """,
        """
        CREATE OR REPLACE FUNCTION stat.get_all_player_stat(
        _ret refcursor,
        _interval integer DEFAULT 999)
        RETURNS refcursor AS
        $BODY$
        BEGIN
        OPEN _ret FOR
            SELECT line.game_id,
		       player.id player_id,
		       player.first_name,
		       player.last_name,
		       player.pos_id,
		       player.team_id player_team_id,
		       schedule.home_team_id home_team_id,
		       schedule.road_team_id road_team_id,
		       schedule.game_time game_date,
		       line.total_pt,
		       line.three_pointers_made,
		       line.rebound,
		       line.assist,
		       line.steal,
		       line.turnover,
		       line.block
		FROM stat.player_game_line line
		INNER JOIN basic_info.player player
		ON line.player_id = player.id
		INNER JOIN basic_info.schedule schedule
		ON schedule.id = line.game_id 
		WHERE schedule.game_time > now() - CAST(_interval || 'day' AS interval)
		ORDER by game_id DESC; 
    
        RETURN _ret;
        END
        $BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100;
        ALTER FUNCTION stat.get_all_player_stat(refcursor, integer)
          OWNER TO postgres;

        """,
        """
        CREATE OR REPLACE FUNCTION stat.get_all_player_stat_by_game(
        _ret refcursor,
        _game_ids integer[],
        _interval integer DEFAULT 999)
      RETURNS refcursor AS
        $BODY$
        BEGIN
        OPEN _ret FOR

		SELECT line.game_id,
		       player.id player_id,
		       player.first_name,
		       player.last_name,
		       player.pos_id,
		       player.team_id player_team_id,
		       schedule.home_team_id home_team_id,
		       schedule.road_team_id road_team_id,
		       schedule.game_time game_date,
		       line.total_pt,
		       line.three_pointers_made,
		       line.rebound,
		       line.assist,
		       line.steal,
		       line.turnover,
		       line.block
		FROM stat.player_game_line line
		INNER JOIN basic_info.player player
		ON line.player_id = player.id
		INNER JOIN basic_info.schedule schedule
		ON schedule.id = line.game_id 
		WHERE schedule.game_time > now() - CAST(_interval || 'day' AS interval)
		AND line.game_id = ANY(_game_ids)
		ORDER by game_id DESC; 

        RETURN _ret;
        END
        $BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100;
        ALTER FUNCTION stat.get_all_player_stat_by_game(refcursor, integer[], integer)
          OWNER TO postgres;
        """,
        """
        CREATE OR REPLACE FUNCTION stat.get_all_player_stat_by_team(
            _ret refcursor,
            _team_ids integer[],
            _interval integer DEFAULT 999)
              RETURNS refcursor AS
            $BODY$
            BEGIN
            OPEN _ret FOR
    
                SELECT line.game_id,
                       player.id player_id,
                       player.first_name,
                       player.last_name,
                       player.pos_id,
                       player.team_id player_team_id,
                       schedule.home_team_id home_team_id,
                       schedule.road_team_id road_team_id,
                       schedule.game_time game_date,
                       line.total_pt,
                       line.three_pointers_made,
                       line.rebound,
                       line.assist,
                       line.steal,
                       line.turnover,
                       line.block
                FROM stat.player_game_line line
                INNER JOIN basic_info.player player
                ON line.player_id = player.id
                INNER JOIN basic_info.schedule schedule
                ON schedule.id = line.game_id 
                WHERE schedule.game_time > now() - CAST(_interval || 'day' AS interval)
                AND player.team_id = ANY(_team_ids)
                ORDER by game_id DESC; 
    
            RETURN _ret;
        END
        $BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100;
        ALTER FUNCTION stat.get_all_player_stat_by_team(refcursor, integer[], integer)
          OWNER TO postgres;
        """,
        """
        CREATE OR REPLACE FUNCTION stat.get_stats_against_team(
        _ret refcursor,
        _opposing_team_ids integer[],
        _interval integer DEFAULT 999)
      RETURNS refcursor AS
            $BODY$
            BEGIN
                OPEN _ret FOR

		SELECT line.game_id,
		       player.id player_id,
		       player.first_name,
		       player.last_name,
		       player.pos_id,
		       player.team_id player_team_id,
		       schedule.home_team_id home_team_id,
		       schedule.road_team_id road_team_id,
		       schedule.game_time game_date,
		       line.total_pt,
		       line.three_pointers_made,
		       line.rebound,
		       line.assist,
		       line.steal,
		       line.turnover,
		       line.block
		FROM stat.player_game_line line
		INNER JOIN basic_info.player player
		ON line.player_id = player.id
		INNER JOIN basic_info.schedule schedule
		ON schedule.id = line.game_id 
		WHERE schedule.game_time > now() - CAST(_interval || 'day' AS interval)
		AND (home_team_id = ANY(_opposing_team_ids) OR road_team_id = ANY(_opposing_team_ids))
		ORDER by game_id DESC; 

            RETURN _ret;
        END
        $BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100;
        ALTER FUNCTION stat.get_stats_against_team(refcursor, integer[], integer)
          OWNER TO postgres;
        """,
        """
        CREATE OR REPLACE FUNCTION stat.get_stats_against_team_by_position(
            _ret refcursor,
            _opposing_team_id integer,
            _position_id integer,
            _interval integer DEFAULT 999)
          RETURNS refcursor AS
            $BODY$
            BEGIN
                OPEN _ret FOR

		SELECT line.game_id,
		       player.id player_id,
		       player.first_name,
		       player.last_name,
		       player.pos_id,
		       player.team_id player_team_id,
		       schedule.home_team_id home_team_id,
		       schedule.road_team_id road_team_id,
		       schedule.game_time game_date,
		       line.total_pt,
		       line.three_pointers_made,
		       line.rebound,
		       line.assist,
		       line.steal,
		       line.turnover,
		       line.block
		FROM stat.player_game_line line
		INNER JOIN basic_info.player player
		ON line.player_id = player.id
		INNER JOIN basic_info.schedule schedule
		ON schedule.id = line.game_id 
		WHERE schedule.game_time > now() - CAST(_interval || 'day' AS interval)
		AND (home_team_id = _opposing_team_id OR road_team_id = _opposing_team_id)
		AND line.pos =  _position_id
		AND player_team_id != _opposing_team_id
		ORDER by game_id DESC; 

        RETURN _ret;
        END
        $BODY$
          LANGUAGE plpgsql VOLATILE
      COST 100;
    ALTER FUNCTION stat.get_stats_against_team_by_position(refcursor, integer, integer, integer)
      OWNER TO postgres;
        """,
        """
        CREATE OR REPLACE FUNCTION stat.upsert_player_stat_line(
            _nba_player_id integer,
            _nba_game_id integer,
            _total_pt integer,
            _three_pointers_made integer,
            _rebound integer,
            _assist integer,
            _steal integer,
            _turnover integer,
            _block integer)
          RETURNS void AS
        $BODY$
        DECLARE _id integer;
        BEGIN

        IF NOT EXISTS (
            SELECT 1
            FROM  stat.player_game_line
            WHERE player_id = (SELECT id FROM basic_info.player WHERE nba_player_id = _nba_player_id)
            AND game_id = (SELECT id FROM basic_info.schedule WHERE nba_game_id = _nba_game_id)
        )
        THEN
        
            INSERT INTO stat.player_game_line(player_id,game_id,total_pt,three_pointers_made,rebound,assist,steal,turnover,block)
            SELECT player.id player_id, schedule.id game_id,_total_pt,_three_pointers_made,_rebound,_assist,_steal,_turnover,_block
            FROM basic_info.player player
            LEFT OUTER JOIN basic_info.schedule schedule
            ON schedule.nba_game_id = _nba_game_id
            WHERE nba_player_id = _nba_player_id;
        
        ELSE
            UPDATE stat.player_game_line player_game_line
            SET total_pt = _total_pt,
                    three_pointers_made = _three_pointers_made,
                rebound = _rebound,
                assist = _assist,
                    steal = _steal,
                    turnover = _turnover,
                    block = _block
            FROM (SELECT player.id player_id, schedule.id game_id
                  FROM basic_info.player player
                  LEFT OUTER JOIN basic_info.schedule schedule
                    ON schedule.nba_game_id = _nba_game_id
                    WHERE nba_player_id = _nba_player_id) AS subquery
                WHERE player_game_line.player_id = subquery.player_id
                AND player_game_line.game_id = subquery.game_id;
          
          END IF;
        END
        $BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100;
        ALTER FUNCTION stat.upsert_player_stat_line(integer, integer, integer, integer, integer, integer, integer, integer, integer)
          OWNER TO postgres;
        """,
        """
        CREATE OR REPLACE FUNCTION fantasy_details.get_scoring_scale(_ret refcursor)
          RETURNS refcursor AS
        $BODY$
        BEGIN
            OPEN _ret FOR
            SELECT scoring.point_type_id,point_type.name,scoring.league_id,scoring.value
            FROM fantasy_details.scoring scoring
            INNER JOIN fantasy_details.point_type point_type
            ON point_type.id = scoring.point_type_id;
        RETURN _ret;
        END
        $BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100;
        ALTER FUNCTION fantasy_details.get_scoring_scale(refcursor)
          OWNER TO postgres;

        """,
        """ 
        CREATE OR REPLACE FUNCTION basic_info.get_days_games(
            _ret refcursor,
            _game_date timestamp without time zone)
          RETURNS refcursor AS
        $BODY$
        BEGIN
            OPEN _ret FOR
                SELECT home_team_id,road_team_id
                FROM basic_info.schedule
                WHERE game_time >= (_game_date + CAST(6 || 'hour' AS interval))
                AND game_time < (_game_date + CAST(1 || 'day' AS interval));
            RETURN _ret;
        END
        $BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100;
        ALTER FUNCTION basic_info.get_days_games(refcursor, timestamp without time zone)
          OWNER TO postgres;

        """,
        """
        CREATE OR REPLACE FUNCTION basic_info.get_todays_games(_ret refcursor)
              RETURNS refcursor AS
            $BODY$
            BEGIN
                OPEN _ret FOR
                    SELECT home_team_id,road_team_id
                    FROM basic_info.schedule
                    WHERE game_time >= (current_date + CAST(6 || 'hour' AS interval))
                    AND game_time < (current_date + CAST(1 || 'day' AS interval));
                RETURN _ret;
            END
            $BODY$
              LANGUAGE plpgsql VOLATILE
              COST 100;
            ALTER FUNCTION basic_info.get_todays_games(refcursor)
              OWNER TO postgres;
        """,
        """
        CREATE OR REPLACE FUNCTION basic_info.get_tomorrows_games(_ret refcursor)
              RETURNS refcursor AS
            $BODY$
            BEGIN
                OPEN _ret FOR
                    SELECT home_team_id,road_team_id
                    FROM basic_info.schedule
                    WHERE game_time >= (current_date + CAST(24 || 'hour' AS interval))
                    AND game_time < (current_date + CAST(48 || 'hour' AS interval));
                RETURN _ret;
            END
            $BODY$
              LANGUAGE plpgsql VOLATILE
              COST 100;
            ALTER FUNCTION basic_info.get_tomorrows_games(refcursor)
              OWNER TO postgres;
        """,
        """
        CREATE OR REPLACE FUNCTION basic_info.get_yesterdays_games(_ret refcursor)
          RETURNS refcursor AS
        $BODY$
        BEGIN
            OPEN _ret FOR
                SELECT home_team_id,road_team_id
                FROM basic_info.schedule
                WHERE game_time >= current_date - CAST(24 || 'hour' AS interval)
                AND game_time < (current_date);
            RETURN _ret;
        END
        $BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100;
        ALTER FUNCTION basic_info.get_yesterdays_games(refcursor)
          OWNER TO postgres;
        """
    )
    for query in commands:
        ExecuteNonQuery(query)

if __name__ == "__main__":
    pass
    # CreateTables()