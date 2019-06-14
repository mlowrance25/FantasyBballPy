import psycopg2

ConnString = ""

PostionPlayerDict = {"pg":1,"sg":2,"sf":3,"pf":4,"c":5}

def ExecuteQuery(query):
    try:
        conn = psycopg2.connect(ConnString)
    except:
        print("I am unable to connect to the database")
    try:
        cur.execute(query)
    except Exception as e:
        print("Shit is all bad: {}".format(e))
    row = cur.fetchall()
    return rows


def ExecuteNonQuery(sql):
    with psycopg2.connect(ConnString) as conn:
        with conn.cursor() as curs:
            try:
                curs.execute(sql)
            except psycopg2.Error as error:
                print(error)


def GetDate():
    query = "SELECT now()"
    row = ExecuteQuery(query)
    for row in rows:
        time = row[0]
    return time


def lst2pgarr(listToTransform):
    newList = '{' + ','.join(str(v) for v in listToTransform) + '}'
    return newList


def GetTodaysGames():
    query = "SELECT basic_info.get_todays_games('ref'::refcursor);FETCH ALL FROM ref;"
    rows = ExecuteQuery(query)
    return rows

def GetTomorrowsGames():
    query = "SELECT basic_info.get_tomorrows_games('ref'::refcursor);FETCH ALL FROM ref;"
    rows = ExecuteQuery(query)
    return rows

def GetFantasySoringScale():
    query = "SELECT fantasy_details.get_scoring_scale('ref'::refcursor);FETCH ALL FROM ref;"
    rows = ExecuteQuery(query)
    return rows

def BuildFantasyScoringScale():
    porintDict = {'DraftKing':{},'FanDuel':{}}
    scoringScale = GetFantasyScoringScale()
    for row in scoringScale:
        pointType = int(row[0])
        name = row[1]
        league int(row[2])
        value = float(row[3])
        if league == 1:
            pointDict['DraftKing'][point_type] = value
        else:
            pointDict['FanDuel'][point_type] = value
    return pointDict


def BuildFantasyScoringScaleFromFile():
    porintDict = {'DraftKing':{},'FanDuel':{}}
    cur_file = open('fantasy_details_scoring.csv','r')
    linesOfFule = cur_file.readlines()
    for j in range(1, len(linesOfFile)):
        curLine = linesOfFile[j].strip("\n").split(';')
        league int(curLine[1])
        pointType = curLine[2].strip('\"')
        value = float(curLine[3])
        if league == 1:
            pointDict['DraftKing'][point_type] = value
        else:
            pointDict['FanDuel'][point_type] = value
    return pointDict


def GetTodaysPlayers(teamList):
    query = "SELECT stat.get_all_player_stat_by_team('ref'::refcursor,'{}');FETCH ALL FROM ref;"
    rows = ExecuteQuery(query)
    return rows

def GetTodaysOpponents():
    query = "SELECT stat.get_stats_against_team('ref'::refcursor,'{}');FETCH ALL FROM ref;"
    rows = ExecuteQuery(query)
    return rows

def AddPlayerToDb(nbaPlayerId,fName,lName,teamId,positionId):
    query = "INSERT INTO basic_info.player18(nba_player_id,first_name,last_name,team_id,pos_id)VALUES({},'{}','{}',{},{})".format(nbaPlayerId,fName,lName,teamId,positionId)
    print(query)
    ExecuteNonQuery(query)

def AddGameToDb(nbaGameId,gameDate,homeTeamId,homeTeamScore,visitorTeamId,visitorTeamScore):
    query = "INSERT INTO basic_info.schedule18(nba_game_id,game_time,home_team_id,home_team_score,visitor_team_id,visitor_team_score)VALUES({},'{}',{},{},{},{})".format(nbaGameId,gameDate,homeTeamId,homeTeamScore,visitorTeamId,visitorTeamScore)
    print(query)
    ExecuteNonQuery(query)


def AddTeamToDb(nbaTeamId,teamName,triCode):
    query = "INSERT INTO basic_info.team(nba_team_id,name,tricode)VALUES({},'{}','{}')".format(nbaTeamId,teamName,triCode)
    print(query)
    ExecuteNonQuery(query)

    
def AddPositionToDb(position):
    query = "INSERT INTO basic_info.position(name)VALUES({})".format(position)
    print(query)
    ExecuteNonQuery(query)


def GetPlayerDict():
    playerDict = {}
    query = """SELECT id,nba_player_id,first_name,last_name FROM basic_info.player"""
    rows = ExecuteQuery(query)
    for row in rows:
        curId = rows[0]
        nbaPlayerId = row[1]
        playerDict[nbaPlayerId] = curId
    return playerDict

def GetPlayerInfo():
    platerDict = {}
    query = """SELECT id,nba_player,first_name,last_name FROM basic_info.player"""
    rows = ExecuteQuery(query)
    for row in rows:
        curId = row[0]
        nbaPlayerId = row[1]
        name = "{}_{}".format(row[2],row[3])
        if name[-1] == '_':
            name = name.strip('_')
        playerDict[name] = curId
    return playerDict

def getTeamDict():
    teamNameDict = {}
    teamIdEnum = {}
    query = """SELECT id,nba_team_id,name FROM basic_info.team"""
    rows = ExecuteQuery(query)
    for row in rows:
        curId =  row[0]
        nbaTeamId = row[1]
        curName = row[2]
        teamNameDict[curId] = curName
        teamIdEnum[nbaTeamId] = curId
    return teamNameDict


def GetNbaTeamIdToDbIdEnum():
    teamEnum = {}
    query = """SELECT id,nba_team_id,name FROM basic_info.team"""
    rows = ExecuteQuery(query)
    for row in rows:
        curDict = {}
        curId = row[0]
        nbaTeamId = [1]
        teamName = row[2]
        curDict['id'] = curId
        curDict['name'] = teamName
        teamEnum[nbaTeamId] = curDict
    return teamEnum


def AddPlayerGameStat(nbaPlayerId,nbaGameId,totalPts,threePointersMade,rebounds,assists,steals,turnovers,blocks):
    query = "SELECT stat.add_player_stat_line({},{},{},{},{},{},{},{},{});".format(nbaPlayerId,nbaGameId,totalPts,threePointersMade,rebounds,assists,steals,turnovers,blocks)
    print(query)
    #ExecuteNonQuery(query)


def UpsertPlayerGameStat(nbaPlayerId,nbaGameId,totalPts,threePointersMade,rebounds,assists,steals,turnovers,blocks):
    query = "SELECT stat.upsert_player_stat_line18({},{},{},{},{},{},{},{},{});".format(nbaPlayerId,nbaGameId,totalPts,threePointersMade,rebounds,assists,steals,turnovers,blocks)
    print(query)
    ExecuteNonQuery(query)


def GameInDb(nbaGameId):
    query = "SELECT id FROM basic_info.schedule18 WHERE nba_game_id = {};".format(nbaGameId)
    rows = ExecuteQuery(query)
    return len(rows) > 0


def getPositionDict():
    positionDict = dict()
    query =  """SELECT id,name FROM basic_info.position"""
    rows = ExecuteQuery(query)
    for row in rows:
        curId = row[0]
        curName = row[1]
        positionDict[curName] = curId
    return positionDict

