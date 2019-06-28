import database
import os
import nba_api_client as nba_client

GetTeamNames = False
AddPositionsToDb = False
AddPlayersToDb = False
AddScheduleToDb = False
AddPlayerStats = False

"""Only necessary for DB setup"""

"""This should be commented out until team names are added to db"""
NbaTeamIdToDbIdEnum = database.GetNbaTeamIdToDbIdEnum()
print(NbaTeamIdToDbIdEnum)
PositionPlayerDict = {"pg": 1, "sg": 2, "sf": 3, "pf": 4, "c": 5}


def main():
    teamDict = getTeamNames()
    if GetTeamNames:
        getTeamNames(True)
    if AddScheduleToDb:
        getTodaysSchedule(teamDict)
    if AddPlayersToDb:
        playerDict,playerIds = getAllPlayers(teamDict)
        addPlayersToSystem(playerDict)
    if AddPlayerStats:
        GetPlayerStats()


def showApiInfo():
    dataDict = nba_client.GetApiInfoRoute()
    allRoutes = dataDict['links']
    for link in allRoutes:
        print("%s: %s" % (link, allRoutes[link]))


def printAllTeamName():
    allNames = nba_client.GetAllNbaTeamNames()
    teamNames = allNames['league']
    for name in teamNames.keys():
        print(name)
        for detail in name:
            print(detail)


def getLeagueScoringScale():
    pointDict = {'DraftKing': {}, 'FanDuel': {}}
    cur_file = open('fantasy_details_scoring.csv', 'r')
    linesOfFile = cur_file.readlines()
    for j in range(1, len(linesOfFile)):
        curLine = linesOfFile[j].strip("\n").split(';')
        league = int(curLine[0])
        point_type = curLine[2].strip('\"')
        value = float(curLine[3])
        league_text = 'DraftKing' if league == 1 else 'FanDuel'
        pointDict[league_text][point_type] = value
    return pointDict

"""This function needs to be broken out into two functions
    one for getting team names and one for actually writing
    all of the team names to the database"""
def getTeamNames(writeToDb=False):
    teamNames = nba_client.GetAllNbaTeamNames()
    allTeams = teamNames['league']
    teamDict = dict()
    for currentTeam in allTeams['standard']:
        if currentTeam.get('isNBAFranchise', False) == True:
            apiTeamId = int(currentTeam['teamId'])
            apiTeamName = currentTeam['urlName']
            apiTriCode = currentTeam['tricode']
            teamDict[apiTeamId] = (apiTeamName, apiTriCode)
    for team_id in sorted(teamDict.keys()):
        team_name = teamDict[team_id][0]
        triCode = teamDict[team_id][1].lower()
        #print(team_id, team_name, triCode)
        if writeToDb:
            database.AddTeamToDb(team_id, team_name, triCode)
    return teamDict


def getTodaysSchedule(teamDict):
    print(teamDict.keys())
    nbaID = set()
    yesterdayTeams = []
    teamMatchups = []
    schedule = nba_client.GetLeagueSchedule()
    for game in schedule['league']['standard']:
        gameId = game['gameId']
        startTime = game['startTimeUTC']
        nbaHomeTeamId = int(game['hTeam']['teamId'])
        nbaVisitorTeamId = int(game['vTeam']['teamId'])
        if nbaHomeTeamId in teamDict.keys() and nbaHomeTeamId in teamDict.keys():
            try:
                homeTeamScore = int(game['hTeam']['score'])
                visitorTeamScore = int(game['vTeam']['score'])
            except Exception as error:
                continue
            #database.AddGameToDb(gameId, startTime, nbaHomeTeamId, homeTeamScore, nbaVisitorTeamId, visitorTeamScore)




def add_teams_for_holdoer():
    startTime = ''
    yesterdayTeams = []
    nbaVisitorTeamId = ''
    nbaHomeTeamId = ''
    teamMatchups = []
    nbaID = []
    game = {}
    if startTime > '2018-12-02T08' and startTime < '2018-12-03T08':
        yesterdayTeams.append(nbaHomeTeamId)
        yesterdayTeams.append(nbaVisitorTeamId)
    if startTime > '2018-12-03T08' and startTime < '2018-12-04T08':
        nbaID.append(nbaHomeTeamId)
        nbaID.append(nbaVisitorTeamId)
        todaysMatchup = dict(HomeTeam=nbaHomeTeamId, VisitorTeam=nbaVisitorTeamId)
        teamMatchups.append(todaysMatchup)
        homeTeamScore = game['hTeam']['score'] if game['hTeam']['score'] != '' else 0
        visitorTeamScore = game['vTeam']['score'] if game['vTeam']['score'] != '' else 0

def getAllPlayers(teamDict):
    playerDict = dict()
    allPlayers = nba_client.GetLeagueRoster()
    playerIds = []
    for player in allPlayers['league']['standard']:
        fName = player['firstName'].strip(",").replace(' ', '').replace("'", '').replace(".", '').lower()
        lName = player['lastName']
        nbaPlayerId = int(player['personId'])
        isActive = player['isActive']
        position = player['pos'].lower()
        if position == 'g':
            position = 'pg'
        elif position == 'g-f':
            position = 'sg'
        elif position == 'f':
            position = 'pf'
        elif position == 'f-g':
            position = 'sf'
        elif position == 'f-c':
            position = 'pf'
        elif position == 'f-g':
            position = 'sf'
        elif position == 'c-f':
            position = 'pf'
        try:
            position = PositionPlayerDict[position]
        except Exception as err:
            print('%s not in player dict' % position)
        nbaTeamId = int(player['teamId']) if player['teamId'] else ''
        if nbaTeamId:
            if nbaTeamId not in playerDict.keys():
                playerDict[nbaTeamId] = []
            playerIds.append(nbaPlayerId)
            playerDict[nbaTeamId].append(dict(PlayerID=nbaPlayerId, FirstName=fName, LastName=lName, PositionID=position, Stats=[]))
            #print('Marvin:',dict(PlayerID=nbaPlayerId, FirstName=fName, LastName=lName, PostionID=position, Stats=[]))
    for team in playerDict.keys():
        currentTeam = playerDict[team]
        teamName = teamDict[team][0]
        # print('\nCurrent Roster for %s' % teamName)
        # print('PlayerID\tFName\tLastName\tPostion')
    return playerDict, playerIds


def addPlayersToSystem(playerDict):
    for roster in playerDict:
        teamId = roster
        teamRoster = playerDict[roster]
        for team in teamRoster:
            nbaPlayerId = team.get('PlayerID')
            fName = team.get('FirstName')
            lName = team.get('LastName')
            positionId = team.get('PositionID')
            isActive = True
            database.AddPlayerToDb(nbaPlayerId,fName,lName,teamId,positionId)
            #print(nbaPlayerId, fName, lName, teamId, positionId, isActive)
        print('New Team')

def addPlayersToSystemLegacy(playerDict):
    allPlayers = nba_client.GetLeagueRoster()
    for player in allPlayers['league']['standard']:
        print('CurPlayer:',player)
        fName = player['firstName'].strip(",").replace('  ', '').replace("'", '').replace('.', '').lower()
        lName = player['lastName']
        indexOfSpace = lName.find(' ')
        lName = lName[:indexOfSpace] if indexOfSpace != -1 else lName
        lName = lName.strip(",").replace('  ', '').replace("'", '').replace('.', '').lower()
        nbaPlayerId = player['personId']
        isActive = player['isActive']
        position = player['pos'].lower()
        nbaTeamId = player['teamId']
        if nbaTeamId != '' and int(nbaTeamId) in NbaTeamIdToDbIdEnum.keys():
            currentTeam = NbaTeamIdToDbIdEnum[int(nbaTeamId)]['name']
            print(currentTeam)
            teamId = NbaTeamIdToDbIdEnum[int(nbaTeamId)]['id']
            print('ENUM:',NbaTeamIdToDbIdEnum)

            print('TEAMID:',teamId)
            print('Roster:',playerDict)
            print('PlayerDict:',playerDict)
            # teamRoster = playerDict[teamId]
            teamRoster = playerDict.keys()

            playerFound = False
            print('TEAMROSTER:',teamRoster)
            for possiblePlayer in teamRoster:
                print('PossiblePlayer:',possiblePlayer)
                tempFName = possiblePlayer[0].strip(",").replace('  ', '').replace("'", '').replace('.', '').lower()
                tempLName = possiblePlayer[1].strip(",").replace('  ', '').replace("'", '').replace('.', '').lower()
                if tempFName == fName and tempLName == lName:
                    playerFound = True
                    newPosition = possiblePlayer[2].strip(",").replace('  ', '').replace("'", '').replace('.',
                                                                                                          '').lower()
                    positionId = PositionPlayerDict[newPosition]
                    database.AddPlayerToDb(nbaPlayerId,fName,lName,teamId,positionId,isActive)
                    #print(nbaPlayerId,fName,lName,teamId,positionId,isActive)
            if not playerFound:
                print("{} {} could not be found on the {}".format(fName, lName, currentTeam))
        else:
            pass


def GetPlayerStats(teamIds, playerDict, playerIds, teamsPlayingToday):
    gamesNotInDb = set()
    leagueSchedule = nba_client.GetLeagueSchedule()
    for game in leagueSchedule['league']['standard']:
        nbaGameId = game['gameId']
        dateString = game['startDateEastern']
        homeTeamId = int(game['hTeam']['teamId'])
        visitorTeamId = int(game['vTeam']['teamId'])
        if homeTeamId not in teamsPlayingToday and visitorTeamId not in teamsPlayingToday:
            continue
        else:
            if dateString > '20181016':
                print('GameID:%s Date:%s' % (nbaGameId, dateString))
                statsForGame = nba_client.GetGameStats(nbaGameId, dateString)
                for row in statsForGame['stats']['activePlayers']:
                    nbaTeamId = int(row['teamId'])
                    if nbaTeamId != '' and homeTeamId in teamIds and visitorTeamId in teamIds:
                        gameInDb = database.GameInDb(nbaGameId)
                        if gameInDb:
                            currentNbaPlayerId = int(row['personId'])
                            try:
                                ptsScored = int(row['points'])
                            except Exception as error:
                                ptsScored = 0
                            try:
                                threePointersMade = int(row['tpm'])
                            except Exception as error:
                                threePointersMade = 0
                            try:
                                rebounds = int(row['totReb'])
                            except Exception as error:
                                rebounds = 0
                            try:
                                assists = int(row['assists'])
                            except Exception as error:
                                assists = 0
                            try:
                                steals = int(row['steals'])
                            except Exception as error:
                                steals = 0
                            try:
                                turnovers = int(row['turnovers'])
                            except Exception as error:
                                turnovers = 0
                            try:
                                blocks = int(row['blocks'])
                            except Exception as error:
                                blocks = 0

                            opposingTeamID = visitorTeamId if nbaTeamId == homeTeamId else homeTeamId
                            if currentNbaPlayerId in playerIds:
                                statDict = dict(Date=dateString, GameID=nbaGameId, OpposingTeamID=opposingTeamID,
                                                PointsScored=ptsScored, ThreesMade=threePointersMade, Rebounds=rebounds,
                                                Assists=assists, Steals=steals, Turnovers=turnovers, Blocks=blocks)
                                correctTeam = playerDict[nbaTeamId]
                                for player in correctTeam:
                                    if player['PlayerID'] == currentNbaPlayerId:
                                        player['Stats'].append(statDict)
                                        # print(player)
                                        # database.UpsertPlayerGameStat(currentNbaPlayerId,nbaGameId,ptsScored,threePointersMade,rebounds,assists,steals,turnovers,blocks)
                                        break
                            else:
                                pass
                            # print(currentNbaPlayerId,nbaGameId,ptsScored,threePointersMade,rebounds,assists,steals,turnovers,blocks)
    return playerDict


def addGameStats(scoreBoard, nbaGameId):
    gamesNotInDb = []
    for row in scoreBoard['stats']['activePlayers']:
        nbaTeamId = row['teamId']
        if nbaTeamId != '' and int(nbaTeamId) in NbaTeamIdToDbIdEnum.keys():
            gameInDb = database.GameInDb(nbaGameId)
            if not gameInDb:
                gamesNotInDb.append(nbaGameId)
            currentNbaPlayerId = int(row['personId'])
            ptsScored = int(row['points'])
            threePointersMade = int(row['tpm'])
            rebounds = int(row['totReb'])
            assists = int(row['assists'])
            steals = int(row['steals'])
            turnovers = int(row['turnovers'])
            blocks = int(row['blocks'])
            # database.UpsertPlayerGameStat(currentNbaPlayerId,nbaGameId,ptsScored,threePointtersMad,rebounds, assists, steals, turnovers, blocks)
    print(gamesNotInDb)



if __name__ == "__main__":
    main()
