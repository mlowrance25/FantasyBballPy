from operator import itemgetter
from fantasy_analyzer import PositionDict,TeamDict,ScoringDict,DraftkingPriceDict,FanduelPriceDict,YesterdaysTeams,TeamsPlayingToday
import database

class PlayerStats:

    def __init__(self,numGames=999):
        self._playerDict = {}
        self.numGameFilter = numGames


    def addPlayerStat(self,playerId,playerName,positionId,teamId,opponentId,totalPt,threePtsMade,rebounds,assist,steal,turnover,block):
        print('Adding. PlayerID:%s. PalyerName:%s. PositionID:%s. TeamID:%s' % (playerId,playerName,positionId,teamId))
        if playerId not in self._playerDict.keys():
            fanduelPrice = 'NA'
            draftkingPrice = 'NA'
            print(playerId in DraftkingPriceDict)
            if playerId in DraftkingPriceDict:
                draftkingPrice = DraftkingPriceDict[playerId]
            if playerId in FanduelPriceDict:
                fanduelPrice = FanduelPriceDict[playerId]
            self._playerDict[playerId] = PlayerStatEntry(playerName,positionId,teamId,opponentId,draftkingPrice,fanduelPrice)
        if self.numGameFilter == 999 or self._playerDict[playerId].numStats < self.numGameFilter:
            print('Should be adding player')
            self._playerDict[playerId].addCurrentStat(totalPt,threePtsMade,rebounds,assist,steal,turnover,block)

    def addOpponentStat(self,positionId,teamId,opponentId,totalPt,threePtsMade,rebounds,assist,steal,turnover,block):
        if opponentId not in self._playerDict.keys():
            self._playerDict[opponentId] = {1 : OpponentStatEntry(),2:OpponentStatEntry(),3:OpponentStatEntry(),4:OpponentStatEntry(),5:OpponentStatEntry()}
        self._playerDict[opponentId][positionId].addCurrentStat(totalPt,threePtsMade,rebounds,assist,steal,turnover,block)

    def DisplayPlayerStatsForPosition(self,posId,positionName,teamDict):
        if self.numGameFilter == 999:
            print("\nShowing stats for position: {}\n".format(positionName))
        else:
            print("\nShowing last {} game stats for position: {}\n".format(self.numGameFilter,positionName))
        squared = list(map(lambda x: (x,self._playerDict[x].totalPts),self._playerDict.keys()))
        playerIds = self._playerDict.keys()
        sortedPoints = sorted(squared,key=itemgetter(1),reverse=True)
        print('SortedPoints: %s ' % (sortedPoints))
        for id in sortedPoints:
            currentId = id[0]
            if self._playerDict[currentId].positionId == posId:
                currentPlayer = self._playerDict[currentId]
                playerName = currentPlayer.name
                teamId = currentPlayer.teamId
                numStats = currentPlayer.numStats
                avgPt = currentPlayer.avgPts
                threePtsMade = currentPlayer.avgThreePtsMade
                rebounds = currentPlayer.avgRebounds
                assist = currentPlayer.avgAssist
                steal = currentPlayer.avgSteal
                turnover = currentPlayer.avgTurnover
                block = currentPlayer.avgBlock
                tripleDoubles = currentPlayer.avgTripleDoubles
                doubleDouble = currentPlayer.avgDoubleDouble

    def DisplayOpponentStat(self,teamDict,PositionDict):
        for teamId in self._playerDict.keys():
            print("\nTeam: {}\n".format(TeamDict[teamId]))
            for id in self._playerDict[teamId]:
                currentPlayer = self._playerDict[teamId][id]
                numStats = currentPlayer.numStats
                avgPt = currentPlayer.avgPts
                threePtsMade = currentPlayer.avgThreePtsMade
                rebounds = currentPlayer.avgRebounds
                assist = currentPlayer.avgAssist
                steal = currentPlayer.avgSteal
                turnover = currentPlayer.avgTurnover
                block = currentPlayer.avgBlock
                tripleDoubles = currentPlayer.avgTripleDoubles
                doubleDouble = currentPlayer.avgDoubleDouble


class PlayerStatEntry:

    def __init__(self,playerName,positionId,teamId,opponentId,draftKingPrice,fanDuelPrice):
        self.name = playerName
        self.position = ''
        self.positionId = positionId
        self.teamId = teamId
        self.opponentId = opponentId
        self.numStats = 0
        self.totalPts = 0
        self.totalThreePtsMade = 0
        self.totalRebounds = 0
        self.totalAssist = 0
        self.totalSteal = 0
        self.totalTurnover = 0
        self.totalBlock = 0
        self.totalDoubleDouble = 0
        self.totalTripleDouble = 0
        self.avgPts = 0
        self.avgThreePtsMade = 0
        self.avgRebounds = 0
        self.avgAssist = 0
        self.avgSteal = 0
        self.avgTurnover = 0
        self.avgBlock = 0
        self.avgDoubleDouble = 0
        self.avgTripleDouble = 0
        self.playedYesterday = self.teamId in YesterdaysTeams
        self.FanDuelPrice = fanDuelPrice
        self.DraftKingPice = draftKingPrice
        self.FanduelScore = 0
        self.DraftkingScore = 0

    def addCurrentStat(self,totalPt,threePtsMade,rebounds,assist,steal,turnover,block):
        self.numStats+=1
        self.totalPts+=totalPt
        self.totalThreePtsMade+= threePtsMade
        self.totalRebounds += rebounds
        self.totalAssist += assist
        self.totalSteal += steal
        self.totalTurnover += turnover
        self.totalBlock += block
        self.avgPts = self.totalPts/self.numStats
        self.avgThreePtsMade = self.totalThreePtsMade/self.numStats
        self.avgRebounds = self.totalRebounds/self.numStats
        self.avgAssist = self.totalAssist/self.numStats
        self.avgSteal = self.totalSteal/self.numStats
        self.avgTurnover = self.totalTurnover/self.numStats
        self.avgBlock = self.totalBlock/self.numStats

        tenOrMore = 0

        if self.totalPts >= 10:
            tenOrMore+=1
        if self.totalRebounds >=10:
            tenOrMore+=1
        if self.totalAssist >= 10:
            tenOrMore+=1
        if self.totalSteal >= 10:
            tenOrMore+=1
        if self.totalBlock >= 10:
            tenOrMore+=1

        if tenOrMore >= 2:
            self.totalDoubleDouble+=1

        if tenOrMore >= 3:
            self.totalTripleDouble = 1

        self.avgDoubleDouble = self.totalDoubleDouble/self.numStats
        self.avgTripleDouble = self.totalTripleDouble/self.numStats
        self.FanduelScore = self.getFantasyScore(2)
        self.DraftkingScore = self.getFantasyScore(1)


    def getFantasyScore(self,fantasyId):
        if fantasyId == 1:
            currentScoring = ScoringDict['DraftKing']
        else:
            currentScoring = ScoringDict['FanDuel']
        
        total = 0
        total += self.avgPts * currentScoring[1]
        total += self.avgThreePtsMade * currentScoring[2]
        total += self.avgRebounds * currentScoring[3]
        total += self.avgAssist * currentScoring[4]
        total += self.avgSteal * currentScoring[6]
        total += self.avgTurnover * currentScoring[7]
        total += self.avgBlock * currentScoring[5]
        total += self.avgDoubleDouble * currentScoring[8]
        total += self.avgTripleDouble * currentScoring[9]
        return total


class OpponentStatEntry:

    def __init__(self):
        self.position = ''
        self.positionId = ''
        self.teamId = ''
        self.opponentId = ''
        self.numStats = 0
        self.totalPts = 0
        self.totalThreePtsMade = 0
        self.totalRebounds = 0
        self.totalAssist = 0
        self.totalSteal = 0
        self.totalTurnover = 0
        self.totalBlock = 0
        self.totalDoubleDouble = 0
        self.totalTripleDouble = 0
        self.avgPts = 0
        self.avgThreePtsMade = 0
        self.avgRebounds = 0
        self.avgAssist = 0
        self.avgSteal = 0
        self.avgTurnover = 0
        self.avgBlock = 0
        self.avgDoubleDouble = 0
        self.avgTripleDouble = 0
        self.FanduelScore = 0
        self.DraftkingScore = 0

    def addCurrentStat(self, totalPt, threePtsMade, rebounds, assist, steal, turnover, block):
        self.numStats += 1
        self.totalPts += totalPt
        self.totalThreePtsMade += threePtsMade
        self.totalRebounds += rebounds
        self.totalAssist += assist
        self.totalSteal += steal
        self.totalTurnover += turnover
        self.totalBlock += block
        self.avgPts = self.totalPts / self.numStats
        self.avgThreePtsMade = self.totalThreePtsMade / self.numStats
        self.avgRebounds = self.totalRebounds / self.numStats
        self.avgAssist = self.totalAssist / self.numStats
        self.avgSteal = self.totalSteal / self.numStats
        self.avgTurnover = self.totalTurnover / self.numStats
        self.avgBlock = self.totalBlock / self.numStats

        tenOrMore = 0

        if self.totalPts >= 10:
            tenOrMore += 1
        if self.totalRebounds >= 10:
            tenOrMore += 1
        if self.totalAssist >= 10:
            tenOrMore += 1
        if self.totalSteal >= 10:
            tenOrMore += 1
        if self.totalBlock >= 10:
            tenOrMore += 1

        if tenOrMore >= 2:
            self.totalDoubleDouble += 1

        if tenOrMore >= 3:
            self.totalTripleDouble += 1

        self.avgDoubleDouble = self.totalDoubleDouble / self.numStats
        self.avgTripleDouble = self.totalTripleDouble / self.numStats
        self.FanduelScore = self.getFantasyScore(2)
        self.DraftkingScore = self.getFantasyScore(1)

    def getFantasyScore(self, fantasyId):
        if fantasyId == 1:
            currentScoring = ScoringDict['DraftKing']
        else:
            currentScoring = ScoringDict['FanDuel']
        total = 0
        total += self.avgPts * currentScoring[1]
        total += self.avgThreePtsMade * currentScoring[2]
        total += self.avgRebounds * currentScoring[3]
        total += self.avgAssist * currentScoring[4]
        total += self.avgSteal * currentScoring[6]
        total -= self.avgTurnover * currentScoring[7]
        total += self.avgBlock * currentScoring[5]
        total += self.avgDoubleDouble * currentScoring[8]
        total += self.avgTripleDouble * currentScoring[9]
        return total