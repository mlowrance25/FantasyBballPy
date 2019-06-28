import requests
from datetime import date

NbaApiHost = "http://data.nba.net"

def Get(route):
    r = requests.get(route)
    requestJson = r.json()
    return requestJson

def GetApiInfoRoute():
    route = NbaApiHost + "/10s/prod/v1/today.json"
    return Get(route)

def GetTeamNameRoute():
    return NbaApiHost + "/prod/v1/2018/teams.json"


def GetLeagueScheduleRoute():
    return NbaApiHost + "/prod/v1/2018/schedule.json"

def GetRosterRoute():
    return NbaApiHost + "/prod/v1/2018/players.json"

def GetScoreboardRoute():
    return NbaApiHost + "/prod/v1/2018/teams.json"

def GetGameScoreboardRoute():
    return NbaApiHost + "/prod/v1/2018/teams.json"

def GetAllNbaTeamNames():
    route = GetTeamNameRoute()
    return Get(route)

def GetLeagueSchedule():
    route = GetLeagueScheduleRoute()
    return Get(route)

def GetLeagueRoster():
    route = GetRosterRoute()
    return Get(route)

def GetStats():
    route = GetScoreboardRoute()
    return Get(route)

def GetGameStats(gameId,dateString):
    route = GetGameScoreboardRoute(gameId,dateString)
    return Get(route)
