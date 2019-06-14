'''
Created on Jan 7, 2018

@author: LOW
'''
import database
import stat
import os
import requests
import json
# from tkinter.constants import CURRENT
import nba_api_client as NbaClient
from operator import itemgetter
# TeamDict = database.getTeamDict()
import fantasy_setup

TeamDict = fantasy_setup.getTeamNames(False)

TodaysDate = '11242018'
PositionDict = {1: 'pg', 2: 'sg', 3: 'sf', 4: 'pf', 5: 'c'}
# FantasySetup.GetPlayerStats()
ScoringDict = database.BuildFantasyScoringScaleFromFile()
FanduelPriceDict = fantasy_setup.getPricesFromFileFD(TodaysDate)
DraftkingPriceDict = fantasy_setup.getPricesFromFileDK(TodaysDate)
YesterdaysTeams = database.GetTodaysGames()

playerDict, playerIds = fantasy_setup.getAllPlayers(TeamDict)
teamIds = [int(curId) for curId in TeamDict.keys()]
TeamsPlayingToday, TodaysMatchups, YesterdaysTeams = fantasy_setup.getTodaysSchedule(TeamDict, playerDict)
playerDict = fantasy_setup.GetPlayerStats(teamIds, playerDict, playerIds, TeamsPlayingToday)


# for matchup in teamMatchups:
#     visitorTeam = matchup['VisitorTeam']
#     homeTeam = matchup['HomeTeam']
#     try:
#         print('%s:%s vs %s(%s)' % (teamDict[visitorTeam], visitorTeam, teamDict[homeTeam], homeTeam))
#     except Exception:
#         print('issue')
#         print(homeTeam)
#         print(visitorTeam)


def GetTodaysGames():
    print('Getting Todays Games')
    AllSeasonStats = stat.PlayerStats()
    LastFiveGameStats = stat.PlayerStats(5)
    LastTenGameStats = stat.PlayerStats(10)
    teamList = []
    # todaysTeams = database.GetTodaysGames(TodaysDate)
    # todaysTeams = database.GetTomorrowsGames()
    # for row in TodaysMatchups:
    #     teamList.append(row[0])
    #     teamList.append(row[1])
    # todaysPlayers = database.GetTodaysPlayers(teamList)
    print("Today's games")
    print("---------------------")
    for team in TodaysMatchups:
        print("(H){} vs (V){}".format(TeamDict[team['HomeTeam']], TeamDict[team['VisitorTeam']]))

    for curTeamId in TeamsPlayingToday:
        currentTeam = playerDict[curTeamId]
        print('CurrentTeam: %s' % (currentTeam))
        index = 0
        for player in currentTeam:
            playerID = player['PlayerID']
            playerStats = player['Stats']

            # statDict = dict(Date=dateString, PointsScored=ptsScored, ThreesMade=threePointersMade, Rebounds=rebounds,Assists=assists, Steals=steals, Turnovers=turnovers, Blocks=blocks)

            for playerLine in playerStats:
                gameId = playerLine['GameID']
                playerId = player['PlayerID']
                fName = player['FirstName']
                lName = player['LastName']
                playerName = "{} {}".format(fName, lName)
                positionId = player['PositionID']
                teamId = curTeamId
                opposingTeamId = playerLine['OpposingTeamID']
                totalPt = playerLine['PointsScored']
                threePtsMade = playerLine['ThreesMade']
                rebounds = playerLine['Rebounds']
                assist = playerLine['Assists']
                steal = playerLine['Steals']
                turnover = playerLine['Turnovers']
                block = playerLine['Blocks']
                if not (
                        totalPt == 0 and threePtsMade == 0 and rebounds == 0 and assist == 0 and steal == 0 and turnover == 0 and block == 0):
                    AllSeasonStats.addPlayerStat(playerId, playerName, positionId, teamId, opposingTeamId, totalPt,
                                                 threePtsMade, rebounds, assist, steal, turnover, block)
                    LastFiveGameStats.addPlayerStat(playerId, playerName, positionId, teamId, opposingTeamId, totalPt,
                                                    threePtsMade, rebounds, assist, steal, turnover, block)
                    LastTenGameStats.addPlayerStat(playerId, playerName, positionId, teamId, opposingTeamId, totalPt,
                                                   threePtsMade, rebounds, assist, steal, turnover, block)
        index += 1
        if index == 6:
            break
        break

    allSeasonStats = AllSeasonStats._playerDict
    print('All Season Stats:%s' % allSeasonStats)
    lastFiveGames = LastFiveGameStats._playerDict

    lastTenGames = LastTenGameStats._playerDict
    todaysOpponetStats = GetTodaysOpponentsStatsAgainstPosition()._playerDict
    statsAgainstTodaysOpponent = GetStatsAgainstTodaysOpponent()._playerDict
    # DisplayAllStats(allSeasonStats,lastFiveGames,lastTenGames,todaysOpponetStats,statsAgainstTodaysOpponent)
    DisplayTopStats(allSeasonStats, lastFiveGames, lastTenGames, todaysOpponetStats, statsAgainstTodaysOpponent)

    # AllSeasonStats.DisplayPlayerStatsForPosition(2,PositionDict[2],TeamDict)
    # LastFiveGameStats.DisplayPlayerStatsForPosition(2,PositionDict[2],TeamDict)
    # LastTenGameStats.DisplayPlayerStatsForPosition(2,PositionDict[2],TeamDict)


def GetStatsAgainstTodaysOpponent():
    TodaysInfo = stat.PlayerStats()
    teamList = []
    oppositionTeamDict = {}
    todaysTeams = database.GetTomorrowsGames()
    for row in todaysTeams:
        oppositionTeamDict[row[0]] = row[1]
        oppositionTeamDict[row[1]] = row[0]
        teamList.append(row[0])
        teamList.append(row[1])

    todaysPlayers = database.GetTodaysPlayers(teamList)
    """print("Today's games")
    print("---------------------")
    for team in todaysTeams:
        print("(H){} vs (V){}".format(TeamDict[team[0]],TeamDict[team[1]]))"""
    for playerLine in todaysPlayers:
        gameId = playerLine[0]
        playerId = playerLine[1]
        fName = playerLine[2]
        lName = playerLine[3]
        playerName = "{} {}".format(fName, lName)
        positionId = int(playerLine[4])
        teamId = playerLine[5]
        if teamId == playerLine[6]:
            opposingTeamId = playerLine[7]
        else:
            opposingTeamId = playerLine[6]
        totalPt = int(playerLine[9])
        threePtsMade = int(playerLine[10])
        rebounds = int(playerLine[11])
        assist = int(playerLine[12])
        steal = int(playerLine[13])
        turnover = int(playerLine[14])
        block = int(playerLine[15])

        if oppositionTeamDict[teamId] == opposingTeamId:
            if not (
                    totalPt == 0 and threePtsMade == 0 and rebounds == 0 and assist == 0 and steal == 0 and turnover == 0 and block == 0):
                TodaysInfo.addPlayerStat(playerId, playerName, positionId, teamId, opposingTeamId, totalPt,
                                         threePtsMade, rebounds, assist, steal, turnover, block)
    # TodaysInfo.DisplayPlayerStatsForPosition(2,PositionDict[positionId])
    return TodaysInfo


def GetTodaysOpponentsStatsAgainstPosition():
    TodaysInfo = stat.PlayerStats()
    teamList = []
    gameDict = {}
    todaysTeams = database.GetTomorrowsGames()
    for row in todaysTeams:
        gameDict[row[0]] = row[1]
        gameDict[row[1]] = row[0]
        teamList.append(row[0])
        teamList.append(row[1])

    todaysPlayers = database.GetTodaysOpponents(teamList)
    """:print("Today's games")
    print("---------------------")
    for team in todaysTeams:
        print("(H){} vs (V){}".format(TeamDict[team[0]],TeamDict[team[1]]))"""
    for playerLine in todaysPlayers:
        gameId = playerLine[0]
        playerId = playerLine[1]
        fName = playerLine[2]
        lName = playerLine[3]
        positionId = int(playerLine[4])
        teamId = playerLine[5]
        if teamId == playerLine[6]:
            opposingTeamId = playerLine[7]
        else:
            opposingTeamId = playerLine[6]
        totalPt = int(playerLine[9])
        threePtsMade = int(playerLine[10])
        rebounds = int(playerLine[11])
        assist = int(playerLine[12])
        steal = int(playerLine[13])
        turnover = int(playerLine[14])
        block = int(playerLine[15])

        if opposingTeamId in teamList:
            if not (
                    totalPt == 0 and threePtsMade == 0 and rebounds == 0 and assist == 0 and steal == 0 and turnover == 0 and block == 0):
                TodaysInfo.addOpponentStat(positionId, teamId, opposingTeamId, totalPt, threePtsMade, rebounds, assist,
                                           steal, turnover, block)
    # TodaysInfo.DisplayOpponentStat(TeamDict,PositionDict)
    return TodaysInfo


def DisplayAllStats(allSeasonStats, lastFiveGames, lastTenGames, todaysOpponetStats, statsAgainstTodaysOpponent):
    oppositionTeamDict = {}
    todaysTeams = database.GetTodaysGames()
    for row in todaysTeams:
        oppositionTeamDict[row[0]] = row[1]
        oppositionTeamDict[row[1]] = row[0]
    posId = 2
    squared = list(map(lambda x: (x, allSeasonStats[x].avgPts), allSeasonStats.keys()))
    playerIds = allSeasonStats.keys()
    sortedPoints = sorted(squared, key=itemgetter(1), reverse=True)
    print("\nStats For Position : {}\n".format(PositionDict[posId]))
    print('SortedPoints:' % sortedPoints)
    for id in sortedPoints:
        currentId = id[0]
        print(allSeasonStats[currentId])
        if allSeasonStats[currentId].positionId == posId:
            allStatsObject = allSeasonStats[currentId]
            lastFiveStatsObject = lastFiveGames[currentId]
            lastTenStatsObject = lastTenGames[currentId]
            todaysOpponetStatsObject = todaysOpponetStats[oppositionTeamDict[allStatsObject.teamId]][posId]

            print(
                "\n Player: {}  Team: {} Opponent: {}".format(allStatsObject.name, TeamDict[lastFiveStatsObject.teamId],
                                                              TeamDict[oppositionTeamDict[allStatsObject.teamId]]))
            print(
                "\n All Season\n  Games Played:{}\n  AvgPoints: {:.1f}\n  Three Pointers :{:.1f}\n  Rebounds:{:.1f}\n  Assist: {:.1f}\n  Steal:{:.1f}\n  Turnover:{:.1f} \n  Block: {:.1f}\n Double-Double: {:.1f}\n  Triple-Double: {:.1f}\n DraftKing: {:.1f}\n FanDuel: {:.1f}   ".format(
                    allStatsObject.numStats, allStatsObject.avgPts, allStatsObject.avgThreePtsMade,
                    allStatsObject.avgRebounds, allStatsObject.avgAssist, allStatsObject.avgSteal,
                    allStatsObject.avgTurnover, allStatsObject.avgBlock, allStatsObject.avgDoubleDouble,
                    allStatsObject.avgTripleDouble, allStatsObject.DraftkingScore, allStatsObject.FanduelScore))
            print(
                "\n Last 5 Games\n  AvgPoints: {:.1f}\n  Three Pointers :{:.1f}\n  Rebounds:{:.1f}\n Assist: {:.1f}\n  Steal:{:.1f}\n Turnover:{:.1f} \n  Block: {:.1f}\n Double-Double: {:.1f}\n  Triple-Double: {:.1f}\n DraftKing: {:.1f}\n FanDuel: {:.1f}    ".format(
                    lastFiveStatsObject.avgPts, lastFiveStatsObject.avgThreePtsMade, lastFiveStatsObject.avgRebounds,
                    lastFiveStatsObject.avgAssist, lastFiveStatsObject.avgSteal, lastFiveStatsObject.avgTurnover,
                    lastFiveStatsObject.avgBlock, lastFiveStatsObject.avgDoubleDouble,
                    lastFiveStatsObject.avgTripleDouble, lastFiveStatsObject.DraftkingScore,
                    lastFiveStatsObject.FanduelScore))
            print(
                "\n Last 10 Games\n  AvgPoints: {:.1f}\n  Three Pointers :{:.1f}\n Rebounds:{:.1f}\n Assist: {:.1f}\n  Steal:{:.1f}\n Turnover:{:.1f} \n  Block: {:.1f}\n Double-Double: {:.1f}\n  Triple-Double: {:.1f}\n DraftKing: {:.1f}\n FanDuel: {:.1f}    ".format(
                    lastTenStatsObject.avgPts, lastTenStatsObject.avgThreePtsMade, lastTenStatsObject.avgRebounds,
                    lastTenStatsObject.avgAssist, lastTenStatsObject.avgSteal, lastTenStatsObject.avgTurnover,
                    lastTenStatsObject.avgBlock, allStatsObject.avgDoubleDouble, allStatsObject.avgTripleDouble,
                    allStatsObject.DraftkingScore, allStatsObject.FanduelScore))
            if currentId in statsAgainstTodaysOpponent.keys():
                statsAgainstOpponentObject = statsAgainstTodaysOpponent[currentId]
                print(
                    "\n Against Same Opponent In Past\n  Games Played:{}\n  AvgPoints: {:.1f}\n  Three Pointers :{:.1f}\n  Rebounds:{:.1f}\n  Assist: {:.1f}\n  Steal:{:.1f}\n  Turnover:{:.1f} \n  Block: {:.1f} \n Double-Double: {:.1f}\n  Triple-Double: {:.1f}\n DraftKing: {:.1f}\n FanDuel: {:.1f}   ".format(
                        statsAgainstOpponentObject.numStats, statsAgainstOpponentObject.avgPts,
                        statsAgainstOpponentObject.avgThreePtsMade, statsAgainstOpponentObject.avgRebounds,
                        statsAgainstOpponentObject.avgAssist, statsAgainstOpponentObject.avgSteal,
                        statsAgainstOpponentObject.avgTurnover, statsAgainstOpponentObject.avgBlock,
                        statsAgainstOpponentObject.avgDoubleDouble, statsAgainstOpponentObject.avgTripleDouble,
                        statsAgainstOpponentObject.DraftkingScore, statsAgainstOpponentObject.FanduelScore))
            else:
                print("\n No stats against team yet\n")
            print(
                "\n Todays opponent agaist this position\nTeam: {}\n  Games Played:{}\n  AvgPoints: {:.1f}\n  Three Pointers :{:.1f}\n  Rebounds:{:.1f}\n  Assist: {:.1f}\n  Steal:{:.1f}\n  Turnover:{:.1f} \n  Block: {:.1f} \n Double-Double: {:.1f}\n  Triple-Double: {:.1f}\n DraftKing: {:.1f}\n FanDuel: {:.1f}   ".format(
                    TeamDict[oppositionTeamDict[allStatsObject.teamId]], todaysOpponetStatsObject.numStats,
                    todaysOpponetStatsObject.avgPts, todaysOpponetStatsObject.avgThreePtsMade,
                    todaysOpponetStatsObject.avgRebounds, todaysOpponetStatsObject.avgAssist,
                    todaysOpponetStatsObject.avgSteal, todaysOpponetStatsObject.avgTurnover,
                    todaysOpponetStatsObject.avgBlock, todaysOpponetStatsObject.avgDoubleDouble,
                    todaysOpponetStatsObject.avgTripleDouble, todaysOpponetStatsObject.DraftkingScore,
                    todaysOpponetStatsObject.FanduelScore))


def DisplayTopStats(allSeasonStats, lastFiveGames, lastTenGames, todaysOpponentStats, statsAgainstTodaysOpponent):
    oppositionTeamDict = {}
    todaysTeams = database.GetTomorrowsGames()
    for row in todaysTeams:
        oppositionTeamDict[row[0]] = row[1]
        oppositionTeamDict[row[1]] = row[0]
    allSeasonStatList = list(map(lambda x: (x, allSeasonStats[x].DraftkingScore), allSeasonStats.keys()))
    sortedAllSeasonStats = sorted(allSeasonStatList, key=itemgetter(1), reverse=True)
    lastFiveStatList = list(map(lambda x: (x, lastFiveGames[x].DraftkingScore), allSeasonStats.keys()))
    sortedLastFiveStats = sorted(lastFiveStatList, key=itemgetter(1), reverse=True)
    lastTenStatList = list(map(lambda x: (x, lastFiveGames[x].DraftkingScore), allSeasonStats.keys()))
    sortedLastTenStats = sorted(lastTenStatList, key=itemgetter(1), reverse=True)
    playerIds = allSeasonStats.keys()

    file_name = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop/TopStat_{}.txt'.format(TodaysDate))
    file_object = open(file_name, 'w')
    for i in range(1, 6):
        posId = i
        print("\nStats For Position : {}\n".format(PositionDict[posId]))
        file_object.write("\nStats For Position : {}\n".format(PositionDict[posId]))
        print(
            "Name\t\t\t\t Team\t\t Opp\t\t\tGameB4\tADk\tAFD\t5DK\t5FD\t10DK\t10FD\tVOppDK\tVOppFD\tOppDK\tOppFD\tDk$\tFD$\n")
        file_object.write(
            "{:<25}\t{:<20}\t{:<20}\t\t{}\t{}\t{}\t{}\t\t{}\t\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t\t{}\n".format("NAME",
                                                                                                          "TEAM", "OPP",
                                                                                                          "GAMEB4",
                                                                                                          "TADK", "TFD",
                                                                                                          "5DK", "5FD",
                                                                                                          "10DK",
                                                                                                          "10FD",
                                                                                                          "VOPPDK",
                                                                                                          "VOPPFD",
                                                                                                          "OPPDK",
                                                                                                          "OPPFD",
                                                                                                          "DK$", "FD$"))

        print('Opposisng: %s' % todaysOpponentStats)

        for id in sortedAllSeasonStats:
            currentId = id[0]
            if allSeasonStats[currentId].positionId == posId:
                allStatsObject = allSeasonStats[currentId]
                lastFiveStatsObject = lastFiveGames[currentId]
                lastTenStatsObject = lastTenGames[currentId]
                print('ID:%s' % allStatsObject.teamId)
                todaysOpponetStatsObject = todaysOpponentStats[oppositionTeamDict[allStatsObject.teamId]][posId]

                statLine = "{:<25}\t{:<20}\t{:<20}\t\t{:>6}\t{:>4.1f}\t{:>4.1f}\t{:>4.1f}\t{:>4.1f}\t{:>4.1f}\t{:>4.1f}".format(
                    allStatsObject.name, TeamDict[lastFiveStatsObject.teamId],
                    TeamDict[oppositionTeamDict[allStatsObject.teamId]], allStatsObject.playedYesterday,
                    allStatsObject.DraftkingScore, allStatsObject.FanduelScore, lastFiveStatsObject.DraftkingScore,
                    lastFiveStatsObject.FanduelScore, lastTenStatsObject.DraftkingScore,
                    lastTenStatsObject.FanduelScore)
                if currentId in statsAgainstTodaysOpponent.keys():
                    statsAgainstOpponentObject = statsAgainstTodaysOpponent[currentId]
                    statLine += "\t{:>4.1f}\t{:>4.1f}".format(statsAgainstOpponentObject.DraftkingScore,
                                                              statsAgainstOpponentObject.FanduelScore)
                else:
                    statLine += "\t'NA'\t'NA'"
                statLine += "\t{:.1f}\t{:.1f}\t{:>4}\t{:>4}\n".format(todaysOpponetStatsObject.DraftkingScore,
                                                                      todaysOpponetStatsObject.FanduelScore,
                                                                      allStatsObject.DraftKingPrice,
                                                                      allStatsObject.FanDuelPrice)
                print(statLine)
                file_object.write(statLine)
    file_object.close()


if __name__ == "__main__":
    GetTodaysGames()