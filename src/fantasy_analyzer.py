import database
import stat
import os 
import requests
import json
import nba_api_client as nba_client
from operator import itemgetter
import fantasy_setup

TeamDict = fantasy_setup.getTeamNames(False)

TodaysDate = '11242018'
PositionDict = {1:'pg',2:'sg',3:'sf',4:'pf',5:'c'}

