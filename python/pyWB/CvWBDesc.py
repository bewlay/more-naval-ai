from CvPythonExtensions import *
import os
import sys
import CvUtil
from array import *

# globals
gc = CyGlobalContext()
version = 11
fileencoding = "latin_1"	# aka "iso-8859-1"

## self.bSpecial True will load the following additional special effects:
## Team Abilities: MapCentering, MapTrading, OpenBordersTrading, IgnoreIrrigation etc
## Team Effects: NukeInterception, EnemyWarWearinessModifier, ExtraDomainMoves, ExtraRouteChange, ImprovementYieldChange
## Player Effects: GoldenAgeTurns, AnarchyTurns, Coastal Trade Routes, State Religion Building/Unit Production, CombatXP
## City Effects: ExtraHappiness, ExtraHealth, ExtraTradeRoutes, BuildingYieldChange, BuildingCommerceChange, BuildingHappyChange, BuildingHealthChange, FreeBonus, NoBonusCount


#Magister Start
iNumPlayers = gc.getMAX_CIV_PLAYERS()
iNumTeams = gc.getMAX_CIV_TEAMS()
#Magister Stop

#############
def getPlayer(idx):
	"helper function which wraps get player in case of bad index"
	if (gc.getPlayer(idx).isAlive()):
		return gc.getPlayer(idx)
	return None

#############
class CvWBParser:
	"parser functions for WB desc"
	def getTokens(self, line):
		"return a list of (comma separated) tokens from the line.  Strip whitespace on each token"
		if line==None:
			return list()
		toks=line.split(",")
		toksOut=list()
		for tok in toks:
			toksOut.append(tok.strip())
		return toksOut

	def findToken(self, toks, item):
		"return true if item exists in list of tokens"
		for tok in toks:
			if (tok==item):
				return true
		return false

	def findTokenValue(self, toks, item):
		"Search for a token of the form item=value in the list of toks, and return value, or -1 if not found"
		for tok in toks:
			l=tok.split("=")
			if (item==l[0]):
				if (len(l)==1):
					return item
				return l[1]
		return -1		# failed

	def getNextLine(self, f):
		"return the next line from the list of lines"
		return f.readline()

	def findNextToken(self, f, item):
		"Find the next line that contains the token item, return false if not found"
		while True:
			line = self.getNextLine(f)
			if (not line):
				return false	# EOF
			toks=self.getTokens(line)
			if (self.findToken(toks, item)):
				return true
		return false

	def findNextTokenValue(self, f, item):
		"Find the next line that contains item=value, return value or -1 if not found"
		while True:
			line = self.getNextLine(f)
			if (not line):
				return -1		# EOF
			toks=self.getTokens(line)
			val=self.findTokenValue(toks, item)
			if (val != -1):
				return val
		return -1

#############
class CvGameDesc:
	"class for serializing game data"
	def __init__(self):
		self.eraType = "NONE"
		self.speedType = "NONE"
		self.calendarType = "CALENDAR_DEFAULT"
		self.options = ()
		self.mpOptions = ()
		self.forceControls = ()
		self.victories = ()
		self.gameTurn = 0
		self.maxTurns = 0
		self.maxCityElimination = 0
		self.numAdvancedStartPoints = 0
		self.targetScore = 0
		self.iStartYear = -4000
		self.szDescription = ""
		self.szModPath = ""
##		self.szModPath = "Mods\Magister Modmod for FfH2"#Magister
		self.iRandom = 0
#Magister Start
		self.iGlobalCounter = 0
		self.iGlobalLimitCounter = 0
		self.iGameScenarioCounter = 0
#Magister Stop

	def apply(self):
		"after reading, apply the game data"
		gc.getGame().setStartYear(self.iStartYear)

#Magister Start
		if self.iGameScenarioCounter > 0:
			gc.getGame().changeScenarioCounter(self.iGameScenarioCounter - gc.getGame().getScenarioCounter())
		if self.iGlobalLimitCounter > 0:
			gc.getGame().changeGlobalCounterLimit(self.iGlobalLimitCounter - gc.getGame().getGlobalCounterLimit())
		if self.iGlobalCounter > 0:
			gc.getGame().changeGlobalCounter((self.iGlobalCounter - gc.getGame().getGlobalCounter())* gc.getGame().getGlobalCounterLimit()/100)
#Magister Stop

	def write(self, f):
		"write out game data"
		f.write("BeginGame\n")
		f.write("\tEra=%s\n" %(gc.getEraInfo(gc.getGame().getStartEra()).getType(),))
		f.write("\tSpeed=%s\n" %(gc.getGameSpeedInfo(gc.getGame().getGameSpeedType()).getType(),))
		f.write("\tCalendar=%s\n" %(gc.getCalendarInfo(gc.getGame().getCalendar()).getType(),))

		# write options
		for i in range(gc.getNumGameOptionInfos()):
			if (gc.getGame().isOption(i)):
				f.write("\tOption=%s\n" %(gc.getGameOptionInfo(i).getType()))

		# write mp options
		for i in range(gc.getNumMPOptionInfos()):
			if (gc.getGame().isMPOption(i)):
				f.write("\tMPOption=%s\n" %(gc.getMPOptionInfo(i).getType()))

		# write force controls
		for i in range(gc.getNumForceControlInfos()):
			if (gc.getGame().isForcedControl(i)):
				f.write("\tForceControl=%s\n" %(gc.getForceControlInfo(i).getType()))

		# write victories
		for i in range(gc.getNumVictoryInfos()):
			if (gc.getGame().isVictoryValid(i)):
				if (not gc.getVictoryInfo(i).isPermanent()):
					f.write("\tVictory=%s\n" %(gc.getVictoryInfo(i).getType()))

		f.write("\tGameTurn=%d\n" %(gc.getGame().getGameTurn(),))
		f.write("\tMaxTurns=%d\n" %(gc.getGame().getMaxTurns(),))
		f.write("\tMaxCityElimination=%d\n" %(gc.getGame().getMaxCityElimination(),))
		f.write("\tNumAdvancedStartPoints=%d\n" %(gc.getGame().getNumAdvancedStartPoints(),))
		f.write("\tTargetScore=%d\n" %(gc.getGame().getTargetScore(),))

#Magister Start
		f.write("\tiGlobalCounter=%d\n" %(gc.getGame().getGlobalCounter(),))
		f.write("\tiGlobalLimitCounter=%d\n" %(gc.getGame().getGlobalCounterLimit(),))
		f.write("\tiGameScenarioCounter=%d\n" %(gc.getGame().getScenarioCounter(),))
#Magister Stop

		f.write("\tStartYear=%d\n" %(gc.getGame().getStartYear(),))
		f.write("\tDescription=%s\n" % (self.szDescription,))
		f.write("\tModPath=%s\n" % (self.szModPath,))
		f.write("EndGame\n")

	def read(self, f):
		"read in game data"
		self.__init__()

		parser = CvWBParser()
		if (parser.findNextTokenValue(f, "BeginGame")!=-1):
			while (true):
				nextLine = parser.getNextLine(f)
				toks = parser.getTokens(nextLine)
				if (len(toks)==0):
					break

				v = parser.findTokenValue(toks, "Era")
				if v!=-1:
					self.eraType = v
					continue

				v = parser.findTokenValue(toks, "Speed")
				if v!=-1:
					self.speedType = v
					continue

				v = parser.findTokenValue(toks, "Calendar")
				if v!=-1:
					self.calendarType = v
					continue

				v = parser.findTokenValue(toks, "Option")
				if v!=-1:
					self.options = self.options + (v,)
					continue

				v = parser.findTokenValue(toks, "MPOption")
				if v!=-1:
					self.mpOptions = self.mpOptions + (v,)
					continue

				v = parser.findTokenValue(toks, "ForceControl")
				if v!=-1:
					self.forceControls = self.forceControls + (v,)
					continue

				v = parser.findTokenValue(toks, "Victory")
				if v!=-1:
					self.victories = self.victories + (v,)
					continue

				v = parser.findTokenValue(toks, "GameTurn")
				if v!=-1:
					self.gameTurn = int(v)
					continue

				v = parser.findTokenValue(toks, "MaxTurns")
				if v!=-1:
					self.maxTurns = int(v)
					continue

				v = parser.findTokenValue(toks, "MaxCityElimination")
				if v!=-1:
					self.maxCityElimination = int(v)
					continue

				v = parser.findTokenValue(toks, "NumAdvancedStartPoints")
				if v!=-1:
					self.numAdvancedStartPoints = int(v)
					continue

				v = parser.findTokenValue(toks, "TargetScore")
				if v!=-1:
					self.targetScore = int(v)
					continue

#Magister Start
				v = parser.findTokenValue(toks, "iGlobalCounter")
				if v!=-1:
					self.iGlobalCounter = int(v)
					continue

				v = parser.findTokenValue(toks, "iGlobalLimitCounter")
				if v!=-1:
					self.iGlobalLimitCounter = int(v)
					continue

				v = parser.findTokenValue(toks, "iGameScenarioCounter")
				if v!=-1:
					self.iGameScenarioCounter = int(v)
					continue
#Magister Stop

				v = parser.findTokenValue(toks, "StartYear")
				if v!=-1:
					self.iStartYear = int(v)
					continue

				v = parser.findTokenValue(toks, "Description")
				if v!=-1:
					self.szDescription = v
					continue

				v = parser.findTokenValue(toks, "ModPath")
				if v!=-1:
					self.szModPath = v
					continue

				v = parser.findTokenValue(toks, "Random")
				if v!=-1:
					self.iRandom = int(v)
					continue

				if parser.findTokenValue(toks, "EndGame") != -1:
					break

#############
class CvTeamDesc:
	def __init__(self):
		self.techTypes = ()
		self.aaiEspionageAgainstTeams = []
		self.bContactWithTeamList = ()
		self.bWarWithTeamList = ()
		self.bPermanentWarPeaceList = ()
		self.bOpenBordersWithTeamList = ()
		self.bDefensivePactWithTeamList = ()
		self.bVassalOfTeamList = []
		self.projectType = []
		self.bRevealMap = 0
		self.iMasterPower = 0
		self.iVassalPower = 0
		self.iEspionageEver = 0
	## Platy Builder ##
		self.bMapCentering = 0
		self.bMapTrading = 0
		self.bTechTrading = 0
		self.bGoldTrading = 0
		self.bOpenBordersTrading = 0
		self.bDefensivePactTrading = 0
		self.bPermanentAllianceTrading = 0
		self.bVassalStateTrading = 0
		self.bBridgeBuilding = 0
		self.bIrrigation = 0
		self.bIgnoreIrrigation = 0
		self.bWaterWork = 0
		self.bExtraWaterSeeFrom = 0
		self.iNukeInterception = 0
		self.iEnemyWarWeariness = 0
		self.lDomainMoves = []
		self.lRouteMoves = []
		self.lImprovementYield = []

	def write(self, f, idx):
		"write out team data"
		f.write("BeginTeam\n")
		pTeam = gc.getTeam(idx)

		# Team ID (to make things easier to mess with in the text)
		f.write("\tTeamID=%d, (%s)\n" %(idx, pTeam.getName().encode(fileencoding)))

		# write techs
		for i in range(gc.getNumTechInfos()):
			if pTeam.isHasTech(i):
				f.write("\tTech=%s\n" %(gc.getTechInfo(i).getType()))
			if gc.getTechInfo(i).isRepeat():
				for j in range(pTeam.getTechCount(i)):
					f.write("\tTech=%s\n" %(gc.getTechInfo(i).getType()))

		# write Espionage against other teams
		for i in range(iNumTeams):
			if pTeam.getEspionagePointsAgainstTeam(i) > 0:
				f.write("\tEspionageTeam=%d, EspionageAmount=%d, (%s)\n" %(i, pTeam.getEspionagePointsAgainstTeam(i), gc.getTeam(i).getName().encode(fileencoding)))

		# write Espionage Ever against other teams
		if pTeam.getEspionagePointsEver() > 0:
			f.write("\tEspionageEverAmount=%d\n" %(gc.getTeam(idx).getEspionagePointsEver()))
	## Platy Builder ##
		for i in range(iNumTeams):
			if i == idx: continue
			if gc.getTeam(i).isBarbarian(): continue
			if pTeam.isHasMet(i):
				f.write("\tContactWithTeam=%d, (%s)\n" %(i, gc.getTeam(i).getName().encode(fileencoding)))
	## Platy Builder ##
		# write warring teams
		for i in range(iNumTeams):
			if pTeam.isAtWar(i):
				f.write("\tAtWar=%d, (%s)\n" %(i, gc.getTeam(i).getName().encode(fileencoding)))

		# write permanent war/peace teams
		for i in range(iNumTeams):
			if pTeam.isPermanentWarPeace(i):
				f.write("\tPermanentWarPeace=%d, (%s)\n" %(i, gc.getTeam(i).getName().encode(fileencoding)))

		# write open borders other teams
		for i in range(iNumTeams):
			if pTeam.isOpenBorders(i):
				f.write("\tOpenBordersWithTeam=%d, (%s)\n" %(i, gc.getTeam(i).getName().encode(fileencoding)))

		# write defensive pact other teams
		for i in range(iNumTeams):
			if pTeam.isDefensivePact(i):
				f.write("\tDefensivePactWithTeam=%d, (%s)\n" %(i, gc.getTeam(i).getName().encode(fileencoding)))

		# write vassal state
		for i in range(iNumTeams):
			if pTeam.isVassal(i):
				iType = self.getRelationshipStatus(idx, i)
				if iType == 1:
					f.write("\tVassalOfTeam=%d, Type=%s, (%s)\n" %(i, "FREE", gc.getTeam(i).getName().encode(fileencoding)))
				elif iType == 0:
					f.write("\tVassalOfTeam=%d, Type=%s, (%s)\n" %(i, "CAP", gc.getTeam(i).getName().encode(fileencoding)))

		for i in range(gc.getNumProjectInfos()):
			for j in range(pTeam.getProjectCount(i)):
				f.write("\tProjectType=%s\n" %(gc.getProjectInfo(i).getType()))

		f.write("\tRevealMap=%d\n" %(0))

		if pTeam.getVassalPower() != 0:
			f.write("\tVassalPower=%d\n" %(pTeam.getVassalPower()))
		if pTeam.getMasterPower() != 0:
			f.write("\tMasterPower=%d\n" %(pTeam.getMasterPower()))
	## Platy Builder ##
		if pTeam.isMapCentering():
			f.write("\tMapCentering=1\n")
		if pTeam.isMapTrading():
			f.write("\tMapTrading=1\n")
		if pTeam.isTechTrading():
			f.write("\tTechTrading=1\n")
		if pTeam.isGoldTrading():
			f.write("\tGoldTrading=1\n")
		if pTeam.isOpenBordersTrading():
			f.write("\tOpenBordersTrading=1\n")
		if pTeam.isDefensivePactTrading():
			f.write("\tDefensivePactTrading=1\n")
		if pTeam.isPermanentAllianceTrading():
			f.write("\tPermanentAllianceTrading=1\n")
		if pTeam.isVassalStateTrading():
			f.write("\tVassalStateTrading=1\n")
		if pTeam.isBridgeBuilding():
			f.write("\tBridgeBuilding=1\n")
		if pTeam.isIrrigation():
			f.write("\tIrrigation=1\n")
		if pTeam.isIgnoreIrrigation():
			f.write("\tIgnoreIrrigation=1\n")
		if pTeam.isWaterWork():
			f.write("\tWaterWork=1\n")
		if pTeam.isExtraWaterSeeFrom():
			f.write("\tExtraWaterSeeFrom=1\n")
		if pTeam.getNukeInterception() != 0:
			f.write("\tNukeInterception=%d\n" %(pTeam.getNukeInterception()))
		if pTeam.getEnemyWarWearinessModifier() != 0:
			f.write("\tEnemyWarWeariness=%d\n" %(pTeam.getEnemyWarWearinessModifier()))
		for item in xrange(DomainTypes.NUM_DOMAIN_TYPES):
			if pTeam.getExtraMoves(item) != 0:
				f.write("\tDomainType=%s, ExtraMoves=%d\n" %(gc.getDomainInfo(item).getType(), pTeam.getExtraMoves(item)))
		for item in xrange(gc.getNumRouteInfos()):
			if pTeam.getRouteChange(item) != 0:
				f.write("\tRouteType=%s, ExtraMoves=%d\n" %(gc.getRouteInfo(item).getType(), pTeam.getRouteChange(item)))
		for item in xrange(gc.getNumImprovementInfos()):
			for k in xrange(YieldTypes.NUM_YIELD_TYPES):
				if pTeam.getImprovementYieldChange(item, k) != 0:
					f.write("\tImprovementType=%s, YieldType=%s, ExtraYield=%d\n" %(gc.getImprovementInfo(item).getType(), gc.getYieldInfo(k).getType(), pTeam.getImprovementYieldChange(item, k)))
		f.write("EndTeam\n")

	def getRelationshipStatus(self, iTeam1, iTeam2):
		for i in range(CyGame().getIndexAfterLastDeal()):
			pDeal = CyGame().getDeal(i)
			iPlayer1 = pDeal.getFirstPlayer()
			iPlayer2 = pDeal.getSecondPlayer()
			if iPlayer1 == -1 or iPlayer2 == -1: continue
			iTeamX = gc.getPlayer(pDeal.getFirstPlayer()).getTeam()
			iTeamY = gc.getPlayer(pDeal.getSecondPlayer()).getTeam()
			if (iTeam1 == iTeamX and iTeam2 == iTeamY) or (iTeam2 == iTeamX and iTeam1 == iTeamY):
				for j in xrange(pDeal.getLengthFirstTrades()):
					if pDeal.getFirstTrade(j).ItemType == TradeableItems.TRADE_VASSAL:	
						return 1
					if pDeal.getFirstTrade(j).ItemType == TradeableItems.TRADE_SURRENDER:	
						return 0
				for j in xrange(pDeal.getLengthSecondTrades()):
					if pDeal.getSecondTrade(j).ItemType == TradeableItems.TRADE_VASSAL:	
						return 1
					if pDeal.getSecondTrade(j).ItemType == TradeableItems.TRADE_SURRENDER:	
						return 0
		return -1

	def read(self, f):
		"read in team data"
		self.__init__()

		parser = CvWBParser()
		if (parser.findNextTokenValue(f, "BeginTeam")!=-1):
			while (true):
				nextLine = parser.getNextLine(f)
				toks = parser.getTokens(nextLine)
				if (len(toks)==0):
					break

				v = parser.findTokenValue(toks, "Tech")
				if v!=-1:
					self.techTypes = self.techTypes + (v,)
					continue

				v = parser.findTokenValue(toks, "EspionageTeam")
				if v!=-1:
					iTeam = int(v)

					iExtra = int(parser.findTokenValue(toks, "EspionageAmount"))
					self.aaiEspionageAgainstTeams.append([iTeam,iExtra])
					continue

				v = parser.findTokenValue(toks, "EspionageEverAmount")
				if v!=-1:
					self.iEspionageEver = int(v)
					continue

				v = parser.findTokenValue(toks, "ContactWithTeam")
				if v!=-1:
					self.bContactWithTeamList = self.bContactWithTeamList + (int(v),)
					continue

				v = parser.findTokenValue(toks, "AtWar")
				if v!=-1:
					self.bWarWithTeamList = self.bWarWithTeamList + (int(v),)
					continue

				v = parser.findTokenValue(toks, "PermanentWarPeace")
				if v!=-1:
					self.bPermanentWarPeaceList = self.bPermanentWarPeaceList + (int(v),)
					continue

				v = parser.findTokenValue(toks, "OpenBordersWithTeam")
				if v!=-1:
					self.bOpenBordersWithTeamList = self.bOpenBordersWithTeamList + (int(v),)
					continue

				v = parser.findTokenValue(toks, "DefensivePactWithTeam")
				if v!=-1:
					self.bDefensivePactWithTeamList = self.bDefensivePactWithTeamList + (int(v),)
					continue

				v = parser.findTokenValue(toks, "VassalOfTeam")
				if v!=-1:
					iType = str(parser.findTokenValue(toks, "Type")).upper() != "FREE"
					self.bVassalOfTeamList.append([int(v), iType])
					continue

				v = parser.findTokenValue(toks, "ProjectType")
				if v!=-1:
					self.projectType.append(v)
					continue

				v = parser.findTokenValue(toks, "RevealMap")
				if v!=-1:
					self.bRevealMap = int(v)
					continue

				v = parser.findTokenValue(toks, "VassalPower")
				if v!=-1:
					self.iVassalPower = int(v)
					continue

				v = parser.findTokenValue(toks, "MasterPower")
				if v!=-1:
					self.iMasterPower = int(v)
					continue
			## Platy Builder
				v = parser.findTokenValue(toks, "MapCentering")
				if v!=-1:
					self.bMapCentering = int(v)
					continue
				v = parser.findTokenValue(toks, "MapTrading")
				if v!=-1:
					self.bMapTrading = int(v)
					continue
				v = parser.findTokenValue(toks, "TechTrading")
				if v!=-1:
					self.bTechTrading = int(v)
					continue
				v = parser.findTokenValue(toks, "GoldTrading")
				if v!=-1:
					self.bGoldTrading = int(v)
					continue
				v = parser.findTokenValue(toks, "OpenBordersTrading")
				if v!=-1:
					self.bOpenBordersTrading = int(v)
					continue
				v = parser.findTokenValue(toks, "DefensivePactTrading")
				if v!=-1:
					self.bDefensivePactTrading = int(v)
					continue
				v = parser.findTokenValue(toks, "PermanentAllianceTrading")
				if v!=-1:
					self.bPermanentAllianceTrading = int(v)
					continue
				v = parser.findTokenValue(toks, "VassalStateTrading")
				if v!=-1:
					self.bVassalStateTrading = int(v)
					continue
				v = parser.findTokenValue(toks, "BridgeBuilding")
				if v!=-1:
					self.bBridgeBuilding = int(v)
					continue
				v = parser.findTokenValue(toks, "Irrigation")
				if v!=-1:
					self.bIrrigation = int(v)
					continue
				v = parser.findTokenValue(toks, "IgnoreIrrigation")
				if v!=-1:
					self.bIgnoreIrrigation = int(v)
					continue
				v = parser.findTokenValue(toks, "WaterWork")
				if v!=-1:
					self.bWaterWork = int(v)
					continue
				v = parser.findTokenValue(toks, "ExtraWaterSeeFrom")
				if v!=-1:
					self.bExtraWaterSeeFrom = int(v)
					continue
				v = parser.findTokenValue(toks, "NukeInterception")
				if v!=-1:
					self.iNukeInterception = int(v)
					continue
				v = parser.findTokenValue(toks, "EnemyWarWeariness")
				if v!=-1:
					self.iEnemyWarWeariness = int(v)
					continue
				v = parser.findTokenValue(toks, "DomainType")
				if v!=-1:
					item = gc.getInfoTypeForString(v)
					iExtra = int(parser.findTokenValue(toks, "ExtraMoves"))
					self.lDomainMoves.append([item,iExtra])
					continue
				v = parser.findTokenValue(toks, "RouteType")
				if v!=-1:
					item = gc.getInfoTypeForString(v)
					iExtra = int(parser.findTokenValue(toks, "ExtraMoves"))
					self.lRouteMoves.append([item,iExtra])
					continue
				v = parser.findTokenValue(toks, "ImprovementType")
				if v!=-1:
					item = gc.getInfoTypeForString(v)
					iYield = gc.getInfoTypeForString(parser.findTokenValue(toks, "YieldType"))
					iExtra = int(parser.findTokenValue(toks, "ExtraYield"))
					self.lImprovementYield.append([item,iYield,iExtra])
					continue

				if parser.findTokenValue(toks, "EndTeam") != -1:
					return true		# completed successfully

		return false	# failed

#############
class CvPlayerDesc:
	def __init__(self):
		self.szCivDesc = ""
		self.szCivShortDesc = ""
		self.szLeaderName = ""
		self.szCivAdjective = ""
		self.szFlagDecal = ""
		self.isWhiteFlag = 0

		self.leaderType = "NONE"
		self.civType = "NONE"
		self.handicap = gc.getHandicapInfo(gc.getDefineINT("STANDARD_HANDICAP")).getType()
		self.team = -1		# team index
		self.color = "NONE"
		self.artStyle = "NONE"
		self.isPlayableCiv = 1
		self.isMinorNationCiv = 0
		self.iStartingGold = 0
		self.iStartingX = -1
		self.iStartingY = -1
		self.stateReligion = ""
		self.szStartingEra = ""
		self.bRandomStartLocation = "false"

		self.aaiCivics = []
		self.aaiAttitudeExtras = []
		self.aszCityList = []

	## Platy Builder ##
		self.iGoldenAge = 0
		self.iAnarchy = 0
		self.iCombatXP = 0
		self.iCoastalTradeRoute = 0
		self.iStateReligionUnit = 0
		self.iStateReligionBuilding = 0
		self.sScriptData = ""

#Magister Start
		self.sAlignment = ''
		self.TraitType = []
		self.iDisableProduction = 0
		self.iDisableResearch = 0
		self.iDisableSpellcasting = 0

		self.FeatType = []
#Magister Stop

	def write(self, f, idx):
		"write out player data"
		f.write("BeginPlayer\n")
		pPlayer = gc.getPlayer(idx)

		# write team
		f.write("\tTeam=%d\n" %(int(pPlayer.getTeam())))

	## Platy Builder ##
		if pPlayer.getLeaderType() != LeaderHeadTypes.NO_LEADER:
			f.write("\tLeaderType=%s\n" %(gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getType()))
		if pPlayer.getCivilizationType() != CivilizationTypes.NO_CIVILIZATION:
			f.write("\tLeaderName=%s\n" %(pPlayer.getNameKey().encode(fileencoding)))
			f.write("\tCivDesc=%s\n" %(pPlayer.getCivilizationDescriptionKey().encode(fileencoding)))
			f.write("\tCivShortDesc=%s\n" %(pPlayer.getCivilizationShortDescriptionKey().encode(fileencoding)))
			f.write("\tCivAdjective=%s\n" %(pPlayer.getCivilizationAdjectiveKey().encode(fileencoding)))
			f.write("\tFlagDecal=%s\n" %(pPlayer.getFlagDecal().encode(fileencoding)))
			f.write("\tWhiteFlag=%d\n" %(pPlayer.isWhiteFlag(),))
			f.write("\tCivType=%s\n" %(gc.getCivilizationInfo(pPlayer.getCivilizationType()).getType()))
			f.write("\tColor=%s\n" %(gc.getPlayerColorInfo(pPlayer.getPlayerColor()).getType()))
			f.write("\tArtStyle=%s\n" %(gc.getArtStyleTypes(pPlayer.getArtStyleType())))
			f.write("\tPlayableCiv=%d\n" %(int(pPlayer.isPlayable())))
			f.write("\tMinorNationStatus=%d\n" %(pPlayer.isMinorCiv()))
			f.write("\tStartingGold=%d\n" %(pPlayer.getGold()))

			if pPlayer.isAlive():
				pPlot = pPlayer.getStartingPlot()
				if not pPlot.isNone():
					f.write("\tStartingX=%d, StartingY=%d\n" %(pPlot.getX(), pPlot.getY()))

			pPlayerReligionInfo = gc.getReligionInfo(pPlayer.getStateReligion())
			if pPlayerReligionInfo:
				f.write("\tStateReligion=%s\n" %(pPlayerReligionInfo.getType()))

			f.write("\tStartingEra=%s\n" %(gc.getEraInfo(pPlayer.getCurrentEra()).getType()))

			f.write("\tRandomStartLocation=false\n")

			# write Civics
			for iCivicOptionLoop in range(gc.getNumCivicOptionInfos()):
				iCivic = pPlayer.getCivics(iCivicOptionLoop)
				f.write("\tCivicOption=%s, Civic=%s\n" %(gc.getCivicOptionInfo(iCivicOptionLoop).getType(), gc.getCivicInfo(iCivic).getType()))

			# write Attitude Extra
			for i in range(iNumPlayers):
				if pPlayer.AI_getAttitudeExtra(i) != 0:
					f.write("\tAttitudePlayer=%d, AttitudeExtra=%d\n, (%s)" %(i, pPlayer.AI_getAttitudeExtra(i), gc.getPlayer(i).getName().encode(fileencoding)))

			# write City List
			for i in range(pPlayer.getNumCityNames()):
				f.write("\tCityList=%s\n" %(pPlayer.getCityName(i)))

		if pPlayer.getHandicapType() != HandicapTypes.NO_HANDICAP:
			f.write("\tHandicap=%s\n" %(gc.getHandicapInfo(pPlayer.getHandicapType()).getType()))
		## Platy Builder ##
			if pPlayer.getGoldenAgeTurns() > 0:
				f.write("\tGoldenAge=%d\n" %(pPlayer.getGoldenAgeTurns()))
			if pPlayer.getAnarchyTurns() > 0:
				f.write("\tAnarchy=%d\n" %(pPlayer.getAnarchyTurns()))
			if pPlayer.getCombatExperience() > 0:
				f.write("\tCombatXP=%d\n" %(pPlayer.getCombatExperience()))
			if pPlayer.getCoastalTradeRoutes() != 0:
				f.write("\tCoastalTradeRoute=%d\n" %(pPlayer.getCoastalTradeRoutes()))
			if pPlayer.getStateReligionUnitProductionModifier() != 0:
				f.write("\tStateReligionUnit=%d\n" %(pPlayer.getStateReligionUnitProductionModifier()))
			if pPlayer.getStateReligionBuildingProductionModifier() != 0:
				f.write("\tStateReligionBuilding=%d\n" %(pPlayer.getStateReligionBuildingProductionModifier()))
			if pPlayer.getScriptData() != "":
				f.write("\tScriptData=%s\n" %(pPlayer.getScriptData()))

#Magister Start
			if pPlayer.getAlignment() == gc.getInfoTypeForString('ALIGNMENT_EVIL'):
				f.write("\tAlignment=ALIGNMENT_EVIL\n")
			elif pPlayer.getAlignment() == gc.getInfoTypeForString('ALIGNMENT_NEUTRAL'):
				f.write("\tAlignment=ALIGNMENT_NEUTRAL\n")
			elif pPlayer.getAlignment() == gc.getInfoTypeForString('ALIGNMENT_GOOD'):
				f.write("\tAlignment=ALIGNMENT_GOOD\n")

			for iTrait in range(gc.getNumTraitInfos()):
				if pPlayer.hasTrait(iTrait):
					f.write("\tTraitType=%s\n" %(gc.getTraitInfo(iTrait).getType()))

			if pPlayer.getDisableProduction() > 0:
				f.write("\tDisableProduction=%d\n" %(pPlayer.getDisableProduction()))
			if pPlayer.getDisableResearch() > 0:
				f.write("\tDisableResearch=%d\n" %(pPlayer.getDisableResearch()))
			if pPlayer.getDisableSpellcasting() > 0:
				f.write("\tDisableSpellcasting=%d\n" %(pPlayer.getDisableSpellcasting()))


			if pPlayer.isFeatAccomplished(FeatTypes.FEAT_GLOBAL_SPELL):
				f.write("\tFEAT_GLOBAL_SPELL=true\n")
			if pPlayer.isFeatAccomplished(FeatTypes.FEAT_HEAL_UNIT_PER_TURN):
				f.write("\tFEAT_HEAL_UNIT_PER_TURN=true\n")
			if pPlayer.isFeatAccomplished(FeatTypes.FEAT_TRUST):
				f.write("\tFEAT_TRUST=true\n")

			if pPlayer.isFeatAccomplished(FeatTypes.FEAT_UNITCOMBAT_MOUNTED):
				f.write("\tFEAT_UNITCOMBAT_MOUNTED=true\n")
			if pPlayer.isFeatAccomplished(FeatTypes.FEAT_UNITCOMBAT_MELEE):
				f.write("\tFEAT_UNITCOMBAT_MELEE=true\n")
			if pPlayer.isFeatAccomplished(FeatTypes.FEAT_UNITCOMBAT_SIEGE):
				f.write("\tFEAT_UNITCOMBAT_SIEGE=true\n")
			if pPlayer.isFeatAccomplished(FeatTypes.FEAT_UNITCOMBAT_GUN):
				f.write("\tFEAT_UNITCOMBAT_GUN=true\n")
			if pPlayer.isFeatAccomplished(FeatTypes.FEAT_UNITCOMBAT_ARMOR):
				f.write("\tFEAT_UNITCOMBAT_ARMOR=true\n")
			if pPlayer.isFeatAccomplished(FeatTypes.FEAT_UNITCOMBAT_HELICOPTER):
				f.write("\tFEAT_UNITCOMBAT_HELICOPTER=true\n")
			if pPlayer.isFeatAccomplished(FeatTypes.FEAT_UNITCOMBAT_NAVAL):
				f.write("\tFEAT_UNITCOMBAT_NAVAL=true\n")
			if pPlayer.isFeatAccomplished(FeatTypes.FEAT_UNIT_PRIVATEER):
				f.write("\tFEAT_UNIT_PRIVATEER=true\n")
			if pPlayer.isFeatAccomplished(FeatTypes.FEAT_UNIT_SPY):
				f.write("\tFEAT_UNIT_SPY=true\n")
			if pPlayer.isFeatAccomplished(FeatTypes.FEAT_NATIONAL_WONDER):
				f.write("\tFEAT_NATIONAL_WONDER=true\n")
			if pPlayer.isFeatAccomplished(FeatTypes.FEAT_TRADE_ROUTE):
				f.write("\tFEAT_TRADE_ROUTE=true\n")
			if pPlayer.isFeatAccomplished(FeatTypes.FEAT_COPPER_CONNECTED):
				f.write("\tFEAT_COPPER_CONNECTED=true\n")
			if pPlayer.isFeatAccomplished(FeatTypes.FEAT_HORSE_CONNECTED):
				f.write("\tFEAT_HORSE_CONNECTED=true\n")
			if pPlayer.isFeatAccomplished(FeatTypes.FEAT_IRON_CONNECTED):
				f.write("\tFEAT_IRON_CONNECTED=true\n")
			if pPlayer.isFeatAccomplished(FeatTypes.FEAT_LUXURY_CONNECTED):
				f.write("\tFEAT_LUXURY_CONNECTED=true\n")
			if pPlayer.isFeatAccomplished(FeatTypes.FEAT_FOOD_CONNECTED):
				f.write("\tFEAT_FOOD_CONNECTED=true\n")
			if pPlayer.isFeatAccomplished(FeatTypes.FEAT_CORPORATION_ENABLED):
				f.write("\tFEAT_CORPORATION_ENABLED=true\n")
			if pPlayer.isFeatAccomplished(FeatTypes.FEAT_PAD):
				f.write("\tFEAT_PAD=true\n")
#Magister Stop

		f.write("EndPlayer\n")

	def read(self, f):
		"read in player data"
		self.__init__()
		parser = CvWBParser()
		if (parser.findNextTokenValue(f, "BeginPlayer")!=-1):
			while (true):
				nextLine = parser.getNextLine(f)
				toks = parser.getTokens(nextLine)
				if (len(toks)==0):
					break

				v = parser.findTokenValue(toks, "CivDesc")
				if v!=-1:
					self.szCivDesc = v.decode(fileencoding)
					continue

				v = parser.findTokenValue(toks, "CivShortDesc")
				if v!=-1:
					self.szCivShortDesc = v.decode(fileencoding)
					continue

				v = parser.findTokenValue(toks, "LeaderName")
				if v!=-1:
					self.szLeaderName = v.decode(fileencoding)
					continue

				v = parser.findTokenValue(toks, "CivAdjective")
				if v!=-1:
					self.szCivAdjective = v.decode(fileencoding)
					continue

				v = parser.findTokenValue(toks, "FlagDecal")
				if v!=-1:
					self.szFlagDecal = v.decode(fileencoding)
					continue

				v = parser.findTokenValue(toks, "WhiteFlag")
				if v!=-1:
					self.isWhiteFlag = int(v)
					continue

				v = parser.findTokenValue(toks, "LeaderType")
				if v!=-1:
					self.leaderType = v
					continue

				v = parser.findTokenValue(toks, "CivType")
				if v!=-1:
					self.civType = v
					continue

				v = parser.findTokenValue(toks, "Team")
				if v!=-1:
					self.team = int(v)
					continue

				v = parser.findTokenValue(toks, "Handicap")
				if v!=-1:
					self.handicap = v
					continue

				v = parser.findTokenValue(toks, "Color")
				if v!=-1:
					self.color = v
					continue

				v = parser.findTokenValue(toks, "ArtStyle")
				if v!=-1:
					self.artStyle = v
					continue

				v = parser.findTokenValue(toks, "PlayableCiv")
				if v!=-1:
					self.isPlayableCiv = int(v)
					continue

				v = parser.findTokenValue(toks, "MinorNationStatus")
				if v!=-1:
					self.isMinorNationCiv = int(v)
					continue

				v = parser.findTokenValue(toks, "StartingGold")
				if v!=-1:
					self.iStartingGold = int(v)
					continue

				vX = parser.findTokenValue(toks, "StartingX")
				vY = parser.findTokenValue(toks, "StartingY")
				if vX!=-1 and vY!=-1:
					self.iStartingX = int(vX)
					self.iStartingY = int(vY)
					continue

				v = parser.findTokenValue(toks, "StateReligion")
				if v!=-1:
					self.stateReligion = v
					continue

#Magister Start
				v = parser.findTokenValue(toks, "Alignment")
				if v!=-1:
					self.sAlignment = v
					continue

				v = parser.findTokenValue(toks, "TraitType")
				if v!=-1:
					self.TraitType.append(gc.getInfoTypeForString(v))
					continue

				v = parser.findTokenValue(toks, "DisableProduction")
				if v!=-1:
					self.iDisableProduction = int(v)
					continue

				v = parser.findTokenValue(toks, "DisableResearch")
				if v!=-1:
					self.iDisableResearch = int(v)
					continue

				v = parser.findTokenValue(toks, "DisableSpellcasting")
				if v!=-1:
					self.iDisableSpellcasting = int(v)
					continue


				v = parser.findTokenValue(toks, "FEAT_GLOBAL_SPELL")
				if v!=-1:
					if bool(v):self.FeatType.append(FeatTypes.FEAT_GLOBAL_SPELL)
					continue
				v = parser.findTokenValue(toks, "FEAT_HEAL_UNIT_PER_TURN")
				if v!=-1:
					if bool(v):self.FeatType.append(FeatTypes.FEAT_HEAL_UNIT_PER_TURN)
					continue
				v = parser.findTokenValue(toks, "FEAT_TRUST")
				if v!=-1:
					if bool(v):self.FeatType.append(FeatTypes.FEAT_TRUST)
					continue

				v = parser.findTokenValue(toks, "FEAT_UNITCOMBAT_MOUNTED")
				if v!=-1:
					if bool(v):self.FeatType.append(FeatTypes.FEAT_UNITCOMBAT_MOUNTED)
					continue
				v = parser.findTokenValue(toks, "FEAT_UNITCOMBAT_MELEE")
				if v!=-1:
					if bool(v):self.FeatType.append(FeatTypes.FEAT_UNITCOMBAT_MELEE)
					continue
				v = parser.findTokenValue(toks, "FEAT_UNITCOMBAT_SIEGE")
				if v!=-1:
					if bool(v):self.FeatType.append(FeatTypes.FEAT_UNITCOMBAT_SIEGE)
					continue
				v = parser.findTokenValue(toks, "FEAT_UNITCOMBAT_GUN")
				if v!=-1:
					if bool(v):self.FeatType.append(FeatTypes.FEAT_UNITCOMBAT_GUN)
					continue
				v = parser.findTokenValue(toks, "FEAT_UNITCOMBAT_ARMOR")
				if v!=-1:
					if bool(v):self.FeatType.append(FeatTypes.FEAT_UNITCOMBAT_ARMOR)
					continue
				v = parser.findTokenValue(toks, "FEAT_UNITCOMBAT_HELICOPTER")
				if v!=-1:
					if bool(v):self.FeatType.append(FeatTypes.FEAT_UNITCOMBAT_HELICOPTER)
					continue
				v = parser.findTokenValue(toks, "FEAT_UNITCOMBAT_NAVAL")
				if v!=-1:
					if bool(v):self.FeatType.append(FeatTypes.FEAT_UNITCOMBAT_NAVAL)
					continue
				v = parser.findTokenValue(toks, "FEAT_UNIT_PRIVATEER")
				if v!=-1:
					if bool(v):self.FeatType.append(FeatTypes.FEAT_UNIT_PRIVATEER)
					continue
				v = parser.findTokenValue(toks, "FEAT_UNIT_SPY")
				if v!=-1:
					if bool(v):self.FeatType.append(FeatTypes.FEAT_UNIT_SPY)
					continue
				v = parser.findTokenValue(toks, "FEAT_NATIONAL_WONDER")
				if v!=-1:
					if bool(v):self.FeatType.append(FeatTypes.FEAT_NATIONAL_WONDER)
					continue
				v = parser.findTokenValue(toks, "FEAT_TRADE_ROUTE")
				if v!=-1:
					if bool(v):self.FeatType.append(FeatTypes.FEAT_TRADE_ROUTE)
					continue
				v = parser.findTokenValue(toks, "FEAT_COPPER_CONNECTED")
				if v!=-1:
					if bool(v):self.FeatType.append(FeatTypes.FEAT_COPPER_CONNECTED)
					continue
				v = parser.findTokenValue(toks, "FEAT_HORSE_CONNECTED")
				if v!=-1:
					if bool(v):self.FeatType.append(FeatTypes.FEAT_HORSE_CONNECTED)
					continue
				v = parser.findTokenValue(toks, "FEAT_IRON_CONNECTED")
				if v!=-1:
					if bool(v):self.FeatType.append(FeatTypes.FEAT_IRON_CONNECTED)
					continue
				v = parser.findTokenValue(toks, "FEAT_LUXURY_CONNECTED")
				if v!=-1:
					if bool(v):self.FeatType.append(FeatTypes.FEAT_LUXURY_CONNECTED)
					continue
				v = parser.findTokenValue(toks, "FEAT_FOOD_CONNECTED")
				if v!=-1:
					if bool(v):self.FeatType.append(FeatTypes.FEAT_FOOD_CONNECTED)
					continue
				v = parser.findTokenValue(toks, "FEAT_CORPORATION_ENABLED")
				if v!=-1:
					if bool(v):self.FeatType.append(FeatTypes.FEAT_CORPORATION_ENABLED)
					continue
				v = parser.findTokenValue(toks, "FEAT_PAD")
				if v!=-1:
					if bool(v):self.FeatType.append(FeatTypes.FEAT_PAD)
					continue
#Magister Stop

				v = parser.findTokenValue(toks, "StartingEra")
				if v!=-1:
					self.szStartingEra = v
					continue

				v = parser.findTokenValue(toks, "RandomStartLocation")
				if v!=-1:
					self.bRandomStartLocation = v
					continue

				v = parser.findTokenValue(toks, "CivicOption")
				if v!=-1:
					iCivicOptionType = gc.getInfoTypeForString(v)

					v = parser.findTokenValue(toks, "Civic")
					if v!=-1:
						iCivicType = gc.getInfoTypeForString(v)
						self.aaiCivics.append([iCivicOptionType,iCivicType])
						continue

				v = parser.findTokenValue(toks, "AttitudePlayer")
				if v!=-1:
					iPlayer = int(v)

					iExtra = int(parser.findTokenValue(toks, "AttitudeExtra"))
					self.aaiAttitudeExtras.append([iPlayer,iExtra])
					continue

				v = parser.findTokenValue(toks, "CityList")
				if v!=-1:
					self.aszCityList.append(v)
					continue

			## Platy Builder ##
				v = parser.findTokenValue(toks, "GoldenAge")
				if v!=-1:
					self.iGoldenAge = max(0, int(v))
					continue
				v = parser.findTokenValue(toks, "Anarchy")
				if v!=-1:
					self.iAnarchy = max(0, int(v))
					continue
				v = parser.findTokenValue(toks, "CombatXP")
				if v!=-1:
					self.iCombatXP = max(0, int(v))
					continue
				v = parser.findTokenValue(toks, "CoastalTradeRoute")
				if v!=-1:
					self.iCoastalTradeRoute = int(v)
					continue
				v = parser.findTokenValue(toks, "StateReligionUnit")
				if v!=-1:
					self.iStateReligionUnit = int(v)
					continue
				v = parser.findTokenValue(toks, "StateReligionBuilding")
				if v!=-1:
					self.iStateReligionBuilding = int(v)
					continue
				v = parser.findTokenValue(toks, "ScriptData")
				if v!=-1:
					self.sScriptData = v
					continue

				if parser.findTokenValue(toks, "EndPlayer") != -1:
					break

#############
class CvUnitDesc:
	"unit WB serialization"
	def __init__(self):
		self.plotX = -1
		self.plotY = -1
		self.unitType = None
		self.szName = None
		self.leaderUnitType = None
		self.owner =-1
		self.damage = 0
		self.level = 0
		self.experience = 0
		self.promotionType = []
		self.facingDirection = DirectionTypes.NO_DIRECTION;
		self.isSleep = False
		self.isIntercept = False
		self.isPatrol = False
		self.isPlunder = False
		self.szUnitAIType = "NO_UNITAI"

	## Platy Builder ##
		self.szScriptData = ""
		self.iImmobile = 0
		self.iBaseCombatStr = -1
		self.iExtraCargo = 0

#Magister Start
		self.iBaseDefenseCombatStr = -1
		self.iDuration = -1
		self.sUnitReligion = ''
		self.iSummoner = -1
		self.iUnitScenarioCounter = -1
		self.bPermanentSummon = False
		self.bHasCasted = False
		self.bAvatar = False
		self.iImmortal = 0
		self.bPromotionReady = False
		self.bMadeAttack = False
		self.bMadeInterception = False
#Magister Stop

	def write(self, f, unit, plot):
		"save unit desc to a file"
		Info = gc.getUnitInfo(unit.getUnitType())
		f.write("\tBeginUnit\n")
		f.write("\t\tUnitType=%s, UnitOwner=%d, (%s)\n" %(Info.getType(), unit.getOwner(), gc.getPlayer(unit.getOwner()).getName().encode(fileencoding)))
		if (len(unit.getNameNoDesc()) > 0):
			f.write("\t\tUnitName=%s\n" %(unit.getNameNoDesc().encode(fileencoding),))
		if unit.getLeaderUnitType() != -1:
			f.write("\t\tLeaderUnitType=%s\n" %(gc.getUnitInfo(unit.getLeaderUnitType()).getType()))
		if unit.getDamage() > 0:
			f.write("\t\tDamage=%d\n" %(unit.getDamage(),))
		f.write("\t\tLevel=%d, Experience=%d\n" %(unit.getLevel(), unit.getExperience()))
		for i in xrange(gc.getNumPromotionInfos()):
			if unit.isHasPromotion(i):
				f.write("\t\tPromotionType=%s\n" %(gc.getPromotionInfo(i).getType()))

		f.write("\t\tFacingDirection=%d\n" %(unit.getFacingDirection(),))
		if (unit.getGroup().getActivityType() == ActivityTypes.ACTIVITY_SLEEP):
			f.write("\t\tSleep\n")
		elif (unit.getGroup().getActivityType() == ActivityTypes.ACTIVITY_INTERCEPT):
			f.write("\t\tIntercept\n")
		elif (unit.getGroup().getActivityType() == ActivityTypes.ACTIVITY_PATROL):
			f.write("\t\tPatrol\n")
		elif (unit.getGroup().getActivityType() == ActivityTypes.ACTIVITY_PLUNDER):
			f.write("\t\tPlunder\n")
		if unit.getUnitAIType() != -1:
			f.write("\t\tUnitAIType=%s\n" %(gc.getUnitAIInfo(unit.getUnitAIType()).getType()))
		if unit.getScriptData():
			f.write("\t\tScriptData=%s\n" %unit.getScriptData())

	## Platy Builder ##
		if unit.getImmobileTimer() > 0:
			f.write("\t\tImmobile=%d\n" %(unit.getImmobileTimer()))
		if unit.baseCombatStr() != Info.getCombat():
			f.write("\t\tCombatStr=%d\n" %(unit.baseCombatStr()))
		if unit.cargoSpace() != Info.getCargoSpace():
			f.write("\t\tExtraCargo=%d\n" %(unit.cargoSpace() - Info.getCargoSpace()))

#Magister Start
		if unit.getDuration() > 0:
			f.write("\t\tDuration=%d\n" %(unit.getDuration()))
		if unit.baseCombatStrDefense() != Info.getCombatDefense():
			f.write("\t\tCombatDefenseStr=%d\n" %(unit.baseCombatStrDefense()))
		if unit.getReligion() > -1:
			f.write("\t\tUnitReligion=%s\n" %(gc.getReligionInfo(unit.getReligion()).getType()))
		if unit.getSummoner() > -1:
			f.write("\t\tSummoner=%d\n" %(unit.getSummoner()))
		if unit.getScenarioCounter() > -1:
			f.write("\t\tAlternateUnitType=%s\n" %(gc.getUnitInfo(unit.getScenarioCounter()).getType()))
		if unit.isPermanentSummon():
			f.write("\t\tPermanentSummon=%d\n" %(unit.isPermanentSummon()))
		if unit.isHasCasted():
			f.write("\t\tHasCasted=%d\n" %(unit.isHasCasted()))
		if unit.isAvatarOfCivLeader():
			f.write("\t\tUnitAvatar=%d\n" %(unit.isAvatarOfCivLeader()))
		if unit.isImmortal():
			f.write("\t\tImmortal=%d\n" %(int(unit.isImmortal())))
		if unit.isPromotionReady():
			f.write("\t\tPromotionReady=%d\n" %(unit.isPromotionReady()))
		if unit.isMadeAttack():
			f.write("\t\tMadeAttack=%d\n" %(unit.isMadeAttack()))
		if unit.isMadeInterception():
			f.write("\t\tMadeInterception=%d\n" %(unit.isMadeInterception()))
#Magister Start

		f.write("\tEndUnit\n")

	def read(self, f, pX, pY):
		"read in unit data - at this point the first line 'BeginUnit' has already been read"
		self.__init__()
		self.plotX = pX
		self.plotY = pY
		CvUtil.pyAssert(self.plotX>=0 and self.plotY>=0, "invalid plot coords")

		parser = CvWBParser()
		while (true):
			nextLine = parser.getNextLine(f)
			toks = parser.getTokens(nextLine)
			if (len(toks)==0):
				break

			v = parser.findTokenValue(toks, "UnitType")
			vOwner = parser.findTokenValue(toks, "UnitOwner")
			if (v!=-1 and vOwner != -1):
				self.unitType = v
				self.owner = int(vOwner)
				continue

			v = parser.findTokenValue(toks, "UnitName")
			if (v != -1):
				self.szName = v.decode(fileencoding)
				continue

			v = parser.findTokenValue(toks, "LeaderUnitType")
			if (v != -1):
				self.leaderUnitType = v
				continue

			v = parser.findTokenValue(toks, "Damage")
			if (v != -1):
				self.damage = (int(v))
				continue

			v = parser.findTokenValue(toks, "Level")
			if (v != -1):
				self.level = (int(v))
				self.experience = int(parser.findTokenValue(toks, "Experience"))
				continue

			# Units - Promotions
			v = parser.findTokenValue(toks, "PromotionType")
			if v!=-1:
				self.promotionType.append(v)
				continue

			v = parser.findTokenValue(toks, "FacingDirection")
			if (v != -1):
				self.facingDirection = (DirectionTypes(v))
				continue

			if (parser.findTokenValue(toks, "Sleep"))!=-1:
				self.isSleep = True
				continue

			if (parser.findTokenValue(toks, "Intercept"))!=-1:
				self.isIntercept = True
				continue

			if (parser.findTokenValue(toks, "Patrol"))!=-1:
				self.isPatrol = True
				continue

			if (parser.findTokenValue(toks, "Plunder"))!=-1:
				self.isPlunder = True
				continue

			v = parser.findTokenValue(toks, "UnitAIType")
			if (v != -1):
				self.szUnitAIType = v
				continue

			v = parser.findTokenValue(toks, "ScriptData")
			if v!=-1:
				print("found script data: %s" %(v))
				self.szScriptData = v
				continue
		## Platy Builder ##
			v = parser.findTokenValue(toks, "Immobile")
			if v != -1:
				self.iImmobile = int(v)
				continue
			v = parser.findTokenValue(toks, "CombatStr")
			if v != -1:
				self.iBaseCombatStr = int(v)
				continue
			v = parser.findTokenValue(toks, "ExtraCargo")
			if v != -1:
				self.iExtraCargo = int(v)
				continue

#Magister Start
			v = parser.findTokenValue(toks, "CombatDefenseStr")
			if v != -1:
				self.iBaseDefenseCombatStr = int(v)
				continue

			v = parser.findTokenValue(toks, "Duration")
			if v != -1:
				self.iDuration = int(v)
				continue

			v = parser.findTokenValue(toks, "UnitReligion")
			if v != -1:
				self.sUnitReligion = v
				continue

			v = parser.findTokenValue(toks, "Summoner")
			if v != -1:
				self.iSummoner = int(v)
				continue

			v = parser.findTokenValue(toks, "AlternateUnitType")
			if v != -1:
				self.iUnitScenarioCounter = gc.getInfoTypeForString(v)
				continue

			v = parser.findTokenValue(toks, "PermanentSummon")
			if v != -1:
				self.bPermanentSummon = int(v)
				continue

			v = parser.findTokenValue(toks, "HasCasted")
			if v != -1:
				self.bHasCasted = int(v)
				continue

			v = parser.findTokenValue(toks, "UnitAvatar")
			if v != -1:
				self.bAvatar = int(v)
				continue

			v = parser.findTokenValue(toks, "Immortal")
			if v != -1:
				self.iImmortal = int(v)
				continue

			v = parser.findTokenValue(toks, "PromotionReady")
			if v != -1:
				self.bPromotionReady = int(v)
				continue

			v = parser.findTokenValue(toks, "MadeAttack")
			if v != -1:
				self.bMadeAttack = int(v)
				continue

			v = parser.findTokenValue(toks, "MadeInterception")
			if v != -1:
				self.bMadeInterception = int(v)
				continue
#Magister Stop

			if parser.findTokenValue(toks, "EndUnit") != -1:
				break

	def apply(self):
		"after reading, this will actually apply the data"
		player = getPlayer(self.owner)
		if (player):
			# print ("unit apply %d %d" %(self.plotX, self.plotY))
			CvUtil.pyAssert(self.plotX>=0 and self.plotY>=0, "invalid plot coords")
			unitTypeNum = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), self.unitType)
			if (unitTypeNum < 0):
				unit = None
			else:
				if (self.szUnitAIType != "NO_UNITAI"):
					eUnitAI = CvUtil.findInfoTypeNum(gc.getUnitAIInfo, UnitAITypes.NUM_UNITAI_TYPES, self.szUnitAIType) #pUnitAI.getType()
				else:
					eUnitAI = UnitAITypes.NO_UNITAI

				unit = player.initUnit(unitTypeNum, self.plotX, self.plotY, UnitAITypes(eUnitAI), self.facingDirection)
			if unit:
				if (self.szName != None):
					unit.setName(self.szName)
				#leader unit type
				if(self.leaderUnitType != None):
					leaderUnitTypeNum = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), self.leaderUnitType)
					if leaderUnitTypeNum >= 0:
						unit.setLeaderUnitType(leaderUnitTypeNum);

				#other properties
				if self.damage != 0:
					unit.setDamage(self.damage, PlayerTypes.NO_PLAYER)
				if self.level != -1:
					unit.setLevel(self.level)
				if self.experience != -1:
					unit.setExperience(self.experience, -1)
				for promo in self.promotionType:
					promotionTypeNum = CvUtil.findInfoTypeNum(gc.getPromotionInfo, gc.getNumPromotionInfos(), promo)
					unit.setHasPromotion(promotionTypeNum, True)
				if self.isSleep:
					unit.getGroup().setActivityType(ActivityTypes.ACTIVITY_SLEEP)
				elif self.isIntercept:
					unit.getGroup().setActivityType(ActivityTypes.ACTIVITY_INTERCEPT)
				elif self.isPatrol:
					unit.getGroup().setActivityType(ActivityTypes.ACTIVITY_PATROL)
				elif self.isPlunder:
					unit.getGroup().setActivityType(ActivityTypes.ACTIVITY_PLUNDER)

			## Platy Builder ##
				if self.szScriptData != "":
					unit.setScriptData(self.szScriptData)
				unit.setImmobileTimer(self.iImmobile)
				if self.iBaseCombatStr > -1:
					unit.setBaseCombatStr(self.iBaseCombatStr)
				if self.iExtraCargo != 0:
					unit.changeCargoSpace(self.iExtraCargo)

#Magister Start
				if self.iBaseDefenseCombatStr > -1:
					unit.setBaseCombatStrDefense(self.iBaseDefenseCombatStr)
				if self.iDuration > -1:
					unit.setDuration(self.iDuration)
				if self.sUnitReligion != '':
					unit.setReligion(gc.getInfoTypeForString(self.sUnitReligion))
				if self.iSummoner > -1:
					unit.setSummoner(self.iSummoner)
				if self.bHasCasted > -1:
					unit.setHasCasted(self.bHasCasted)
				if self.iUnitScenarioCounter > -1:
					unit.setScenarioCounter(self.iUnitScenarioCounter)
				if self.bPermanentSummon > -1:
					unit.setPermanentSummon(self.bPermanentSummon)
				if self.bAvatar > -1:
					unit.setAvatarOfCivLeader(self.bAvatar)
				if self.bPromotionReady > -1:
					unit.setPromotionReady(self.bPromotionReady)
				if self.bMadeAttack > -1:
					unit.setMadeAttack(self.bMadeAttack)
				if self.bMadeInterception > -1:
					unit.setMadeInterception(self.bMadeInterception)
				if self.iImmortal > 0:
					if not unit.isImmortal():
						unit.changeImmortal(1)
				else:
					while unit.isImmortal():
						unit.changeImmortal(-1)
#Magister Stop

############
class CvCityDesc:
	"serializes city data"
	def __init__(self):
		self.city = None
		self.owner = None
		self.name = None
		self.population = 0
		self.productionUnit = "NONE"
		self.productionBuilding = "NONE"
		self.productionProject = "NONE"
		self.productionProcess = "NONE"
		self.bldgType = []
		self.religions = []
		self.holyCityReligions = []
		self.corporations = []
		self.headquarterCorporations = []
		self.freeSpecialists = []
		self.plotX=-1
		self.plotY=-1
	## Platy Builder ##
		self.szScriptData = ""
		self.lCulture = []
		self.iDamage = 0
		self.iOccupation = 0
		self.iExtraHappiness = 0
		self.iExtraHealth = 0
		self.iExtraTrade = 0
		self.lBuildingYield = []
		self.lBuildingCommerce = []
		self.lBuildingHappy = []
		self.lBuildingHealth = []
		self.lFreeBonus = []
		self.lNoBonus = []

#Magister Start
		self.iRevolutionIndex = 0
		self.iCityCivType = CivilizationTypes.NO_CIVILIZATION
#Magister Stop

	def write(self, f, plot):
		"write out city data"
		city = plot.getPlotCity()
		CvUtil.pyAssert(city.isNone()==0, "null city?")
		f.write("\tBeginCity\n")
		f.write("\t\tCityOwner=%d, (%s)\n" %(city.getOwner(), gc.getPlayer(city.getOwner()).getName().encode(fileencoding)))
		f.write("\t\tCityName=%s\n" %(city.getName().encode(fileencoding),))
		f.write("\t\tCityPopulation=%d\n" %(city.getPopulation(),))
		if (city.isProductionUnit()):
			f.write("\t\tProductionUnit=%s\n" %(gc.getUnitInfo(city.getProductionUnit()).getType(),))
		elif (city.isProductionBuilding()):
			f.write("\t\tProductionBuilding=%s\n" %(gc.getBuildingInfo(city.getProductionBuilding()).getType(),))
		elif (city.isProductionProject()):
			f.write("\t\tProductionProject=%s\n" %(gc.getProjectInfo(city.getProductionProject()).getType(),))
		elif (city.isProductionProcess()):
			f.write("\t\tProductionProcess=%s\n" %(gc.getProcessInfo(city.getProductionProcess()).getType(),))

		for iI in range(gc.getNumBuildingInfos()):
			if city.getNumRealBuilding(iI) > 0:
				f.write("\t\tBuildingType=%s\n" %(gc.getBuildingInfo(iI).getType()))

		for iI in range(gc.getNumReligionInfos()):
			if city.isHasReligion(iI):
				f.write("\t\tReligionType=%s\n" %(gc.getReligionInfo(iI).getType()))
			if (city.isHolyCityByType(iI)):
				f.write("\t\tHolyCityReligionType=%s\n" %(gc.getReligionInfo(iI).getType()))

		for iI in range(gc.getNumCorporationInfos()):
			if city.isHasCorporation(iI):
				f.write("\t\tCorporationType=%s\n" %(gc.getCorporationInfo(iI).getType()))
			if (city.isHeadquartersByType(iI)):
				f.write("\t\tHeadquarterCorporationType=%s\n" %(gc.getCorporationInfo(iI).getType()))

		for iI in range(gc.getNumSpecialistInfos()):
			for iJ in range(city.getAddedFreeSpecialistCount(iI)):
				f.write("\t\tFreeSpecialistType=%s\n" %(gc.getSpecialistInfo(iI).getType()))

		if city.getScriptData():
			f.write("\t\tScriptData=%s\n" %city.getScriptData())

		# Player culture
		for iPlayerLoop in range(iNumPlayers):
			iPlayerCulture = city.getCulture(iPlayerLoop)
			if (iPlayerCulture > 0):
				f.write("\t\tPlayer%dCulture=%d, (%s)\n" %(iPlayerLoop, iPlayerCulture, gc.getPlayer(iPlayerLoop).getName().encode(fileencoding)))
		if city.getDefenseDamage() > 0:
			f.write("\t\tDamage=%d\n" %(city.getDefenseDamage(),))
		if city.getOccupationTimer() > 0:
			f.write("\t\tOccupation=%d\n" %(city.getOccupationTimer(),))
		if city.getExtraHappiness() != 0:
			f.write("\t\tExtraHappiness=%d\n" %(city.getExtraHappiness(),))
		if city.getExtraHealth() != 0:
			f.write("\t\tExtraHealth=%d\n" %(city.getExtraHealth(),))
		if city.getExtraTradeRoutes() != 0:
			f.write("\t\tExtraTrade=%d\n" %(city.getExtraTradeRoutes(),))
		for item in xrange(gc.getNumBuildingClassInfos()):
			for k in xrange(YieldTypes.NUM_YIELD_TYPES):
				if city.getBuildingYieldChange(item, k) != 0:
					f.write("\t\tModifiedBuilding=%s, Yield=%s, Amount=%s\n" %(gc.getBuildingClassInfo(item).getType(), gc.getYieldInfo(k).getType(), city.getBuildingYieldChange(item, k)))
			for k in xrange(CommerceTypes.NUM_COMMERCE_TYPES):
				if city.getBuildingCommerceChange(item, k) != 0:
					f.write("\t\tModifiedBuilding=%s, Commerce=%s, Amount=%s\n" %(gc.getBuildingClassInfo(item).getType(), gc.getCommerceInfo(k).getType(), city.getBuildingCommerceChange(item, k)))
			if city.getBuildingHappyChange(item) != 0:
				f.write("\t\tModifiedBuilding=%s, Happy=%s\n" %(gc.getBuildingClassInfo(item).getType(), city.getBuildingHappyChange(item)))
			if city.getBuildingHealthChange(item) != 0:
				f.write("\t\tModifiedBuilding=%s, Health=%s\n" %(gc.getBuildingClassInfo(item).getType(), city.getBuildingHealthChange(item)))
		for item in xrange(gc.getNumBonusInfos()):
			if city.getFreeBonus(item) > 0:
				f.write("\t\tFreeBonus=%s, Amount=%s\n" %(gc.getBonusInfo(item).getType(), city.getFreeBonus(item)))
			if city.isNoBonus(item):
				f.write("\t\tNoBonus=%s\n" % gc.getBonusInfo(item).getType())

#Magister Start
		if city.getRevolutionIndex() > 0:
			f.write("\t\tRevolutionIndex=%d\n" %(city.getRevolutionIndex(),))

		if city.getCivilizationType() != gc.getPlayer(city.getOwner()).getCivilizationType():
			f.write("\t\tCityCivType=%s\n" %(gc.getCivilizationInfo(city.getCivilizationType()).getType(),))
#Magister Stop
		f.write("\tEndCity\n")

	def read(self, f, iX, iY):
		"read in city data - at this point the first line 'BeginCity' has already been read"
		self.__init__()
		self.plotX=iX
		self.plotY=iY
		parser = CvWBParser()
		while (true):
			nextLine = parser.getNextLine(f)
			toks = parser.getTokens(nextLine)
			if (len(toks)==0):
				break

			# City - Owner
			vOwner=parser.findTokenValue(toks, "CityOwner")
			if (vOwner != -1):
				self.owner = int(vOwner)
				continue

			# City - Name
			vName=parser.findTokenValue(toks, "CityName")
			if (vName != -1):
				self.name = (vName).decode(fileencoding)
				continue

			# City - Population
			v=parser.findTokenValue(toks, "CityPopulation")
			if v!=-1:
				self.population = (int(v))
				continue

			# City - Production Unit
			v=parser.findTokenValue(toks, "ProductionUnit")
			if v!=-1:
				self.productionUnit = v
				continue

			# City - Production Building
			v=parser.findTokenValue(toks, "ProductionBuilding")
			if v!=-1:
				self.productionBuilding = v
				continue

			# City - Production Project
			v=parser.findTokenValue(toks, "ProductionProject")
			if v!=-1:
				self.productionProject = v
				continue

			# City - Production Process
			v=parser.findTokenValue(toks, "ProductionProcess")
			if v!=-1:
				self.productionProcess = v
				continue

			# City - Buildings
			v=parser.findTokenValue(toks, "BuildingType")
			if v!=-1:
				self.bldgType.append(v)
				continue

			# City - Religions
			v=parser.findTokenValue(toks, "ReligionType")
			if v!=-1:
				self.religions.append(v)
				continue

			# City - HolyCity
			v=parser.findTokenValue(toks, "HolyCityReligionType")
			if v!=-1:
				self.holyCityReligions.append(v)
				continue

			# City - Corporations
			v=parser.findTokenValue(toks, "CorporationType")
			if v!=-1:
				self.corporations.append(v)
				continue

			# City - Headquarters
			v=parser.findTokenValue(toks, "HeadquarterCorporationType")
			if v!=-1:
				self.headquarterCorporations.append(v)
				continue

			# City - Free Specialist
			v=parser.findTokenValue(toks, "FreeSpecialistType")
			if v!=-1:
				self.freeSpecialists.append(v)
				continue

			# City - ScriptData
			v=parser.findTokenValue(toks, "ScriptData")
			if v!=-1:
				self.szScriptData = v
				continue

		## Platy Builder ##
			for iPlayerLoop in xrange(iNumPlayers):
				szCityTag = ("Player%dCulture" %(iPlayerLoop))
				v = parser.findTokenValue(toks, szCityTag)
				if v!=-1:
					if int(v) > 0:
						self.lCulture.append([iPlayerLoop, int(v)])
					continue
			v=parser.findTokenValue(toks, "Damage")
			if v!=-1:
				self.iDamage = int(v)
				continue
			v=parser.findTokenValue(toks, "Occupation")
			if v!=-1:
				self.iOccupation = int(v)
				continue
			v=parser.findTokenValue(toks, "ExtraHappiness")
			if v!=-1:
				self.iExtraHappiness = int(v)
				continue
			v=parser.findTokenValue(toks, "ExtraHealth")
			if v!=-1:
				self.iExtraHealth = int(v)
				continue
			v=parser.findTokenValue(toks, "ExtraTrade")
			if v!=-1:
				self.iExtraTrade = int(v)
				continue
			v = parser.findTokenValue(toks, "ModifiedBuilding")
			if v != -1:
				iBuildingClass = gc.getInfoTypeForString(v)
				v = parser.findTokenValue(toks, "Yield")
				if v != -1:
					iYield = gc.getInfoTypeForString(v)
					iAmount = int(parser.findTokenValue(toks, "Amount"))
					self.lBuildingYield.append([iBuildingClass, iYield, iAmount])
					continue
				v = parser.findTokenValue(toks, "Commerce")
				if v != -1:
					iCommerce = gc.getInfoTypeForString(v)
					iAmount = int(parser.findTokenValue(toks, "Amount"))
					self.lBuildingCommerce.append([iBuildingClass, iCommerce, iAmount])
					continue
				v = parser.findTokenValue(toks, "Happy")
				if v != -1:
					self.lBuildingHappy.append([iBuildingClass, int(v)])
					continue
				v = parser.findTokenValue(toks, "Health")
				if v != -1:
					self.lBuildingHealth.append([iBuildingClass, int(v)])
					continue
			v = parser.findTokenValue(toks, "FreeBonus")
			if v != -1:
				item = gc.getInfoTypeForString(v)
				iAmount = int(parser.findTokenValue(toks, "Amount"))
				self.lFreeBonus.append([item, iAmount])
				continue
			v = parser.findTokenValue(toks, "NoBonus")
			if v != -1:
				self.lNoBonus.append(gc.getInfoTypeForString(v))
				continue

#Magister Start
			v=parser.findTokenValue(toks, "RevolutionIndex")
			if v!=-1:
				self.iRevolutionIndex = int(v)
				continue

			v=parser.findTokenValue(toks, "CityCivType")
			if v!=-1:
				self.iCityCivType = gc.getInfoTypeForString(v)
				continue
#Magister Stop

			if parser.findTokenValue(toks, "EndCity")!=-1:
				break

	def apply(self, bSpecial):
		"after reading, this will actually apply the data"
		player = getPlayer(self.owner)
		if (player):

#FfH: Added by Kael 12/23/2008
			iX = self.plotX
			iY = self.plotY
			pLoopPlot = CyMap().plot(iX,iY)
			pLoopPlot.setBonusType(-1)
			for iiX in range(iX-2, iX+3, 1):
				for iiY in range(iY-2, iY+3, 1):
					pLoopPlot = CyMap().plot(iiX,iiY)
					if not pLoopPlot.isNone():
						if pLoopPlot.getImprovementType() != -1:
							if gc.getImprovementInfo(pLoopPlot.getImprovementType()).getSpawnUnitType() != -1 or gc.getImprovementInfo(pLoopPlot.getImprovementType()).isGoody():
								pLoopPlot.setImprovementType(-1)
#FfH: End Add

			self.city = player.initCity(self.plotX, self.plotY)

		if (self.name != None):
			self.city.setName(self.name, False)

		if self.population > -1:
			self.city.setPopulation(self.population)

		for item in self.lCulture:
			self.city.setCulture(item[0], item[1], true)

		for bldg in (self.bldgType):
			bldgTypeNum = CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), bldg)
			self.city.setNumRealBuilding(bldgTypeNum, 1)

		for religion in (self.religions):
			religionTypeNum = CvUtil.findInfoTypeNum(gc.getReligionInfo, gc.getNumReligionInfos(), religion)
			self.city.setHasReligion(religionTypeNum, true, false, true)

		for holyCityRel in (self.holyCityReligions):
			religionTypeNum = CvUtil.findInfoTypeNum(gc.getReligionInfo, gc.getNumReligionInfos(), holyCityRel)
			gc.getGame().setHolyCity(religionTypeNum, self.city, false)

		for corporation in (self.corporations):
			corporationTypeNum = CvUtil.findInfoTypeNum(gc.getCorporationInfo, gc.getNumCorporationInfos(), corporation)
			self.city.setHasCorporation(corporationTypeNum, true, false, true)

		for headquarters in (self.headquarterCorporations):
			corporationTypeNum = CvUtil.findInfoTypeNum(gc.getCorporationInfo, gc.getNumCorporationInfos(), headquarters)
			gc.getGame().setHeadquarters(corporationTypeNum, self.city, false)

		for iSpecialist in self.freeSpecialists:
			specialistTypeNum = CvUtil.findInfoTypeNum(gc.getSpecialistInfo, gc.getNumSpecialistInfos(), iSpecialist)
			self.city.changeFreeSpecialistCount(specialistTypeNum, 1)

		unitTypeNum = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), self.productionUnit)
		buildingTypeNum = CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), self.productionBuilding)
		projectTypeNum = CvUtil.findInfoTypeNum(gc.getProjectInfo, gc.getNumProjectInfos(), self.productionProject)
		processTypeNum = CvUtil.findInfoTypeNum(gc.getProcessInfo, gc.getNumProcessInfos(), self.productionProcess)

		if (unitTypeNum != UnitTypes.NO_UNIT):
			self.city.pushOrder(OrderTypes.ORDER_TRAIN, unitTypeNum, -1, False, False, False, True)
		elif (buildingTypeNum != BuildingTypes.NO_BUILDING):
			self.city.pushOrder(OrderTypes.ORDER_CONSTRUCT, buildingTypeNum, -1, False, False, False, True)
		elif (projectTypeNum != ProjectTypes.NO_PROJECT):
			self.city.pushOrder(OrderTypes.ORDER_CREATE, projectTypeNum, -1, False, False, False, True)
		elif (processTypeNum != ProcessTypes.NO_PROCESS):
			self.city.pushOrder(OrderTypes.ORDER_MAINTAIN, processTypeNum, -1, False, False, False, True)

		if self.szScriptData:
			self.city.setScriptData(self.szScriptData)
	## Platy Builder ##
		if self.iDamage > 0:
			self.city.changeDefenseDamage(self.iDamage)
		if self.iOccupation > 0:
			self.city.setOccupationTimer(self.iOccupation)
		if bSpecial:
			self.city.changeExtraHappiness(self.iExtraHappiness - self.city.getExtraHappiness())
			self.city.changeExtraHealth(self.iExtraHealth - self.city.getExtraHealth())
			self.city.changeExtraTradeRoutes(self.iExtraTrade - self.city.getExtraTradeRoutes())
			for item in self.lBuildingYield:
				self.city.setBuildingYieldChange(item[0], item[1], item[2] - self.city.getBuildingYieldChange(item[0], item[1]))
			for item in self.lBuildingCommerce:
				self.city.setBuildingCommerceChange(item[0], item[1], item[2] - self.city.getBuildingCommerceChange(item[0], item[1]))
			for item in self.lBuildingHappy:
				self.city.setBuildingHappyChange(item[0], item[1] - self.city.getBuildingHappyChange(item[0]))
			for item in self.lBuildingHealth:
				self.city.setBuildingHealthChange(item[0], item[1] - self.city.getBuildingHealthChange(item[0]))
			for item in self.lFreeBonus:
				self.city.changeFreeBonus(item[0], item[1] - self.city.getFreeBonus(item[0]))
			for item in self.lNoBonus:
				if self.city.isNoBonus(item): continue
				self.city.changeNoBonusCount(item, 1)

#Magister Start
		if self.iRevolutionIndex > 0:
			self.city.setRevolutionIndex(self.iRevolutionIndex)

		if self.iCityCivType != CivilizationTypes.NO_CIVILIZATION and self.iCityCivType != self.city.getCivilizationType():
			self.city.setCivilizationType(self.iCityCivType)
#Magister Stop

###########
class CvPlotDesc:
	"serializes plot data"
	def __init__(self):
		self.iX = -1
		self.iY = -1
		self.riverNSDirection = CardinalDirectionTypes.NO_CARDINALDIRECTION
		self.isNOfRiver = 0
		self.riverWEDirection = CardinalDirectionTypes.NO_CARDINALDIRECTION
		self.isWOfRiver = 0
		self.isStartingPlot = 0
		self.bonusType = None
		self.improvementType = None
		self.featureType = None
		self.featureVariety = 0
		self.routeType = None
		self.terrainType = None
		self.plotType = PlotTypes.NO_PLOT
		self.unitDescs = list()
		self.cityDesc = None
		self.szLandmark = ""
	## Platy Builder ##
		self.szScriptData = ""
		self.abTeamPlotRevealed = []
		self.lCulture = []

#Magister Start
		self.bMoveDisabledAI = 0
		self.bMoveDisabledHuman = 0
		self.bBuildDisabled = 0
		self.bFoundDisabled = 0
		self.bPythonActive = 1
		self.plotMinLevel = 0
		self.plotCounter = 0
		self.portalExitX = 0
		self.portalExitY = 0

		self.realBonusType = None
		self.realImprovementType = None
		self.realFeatureType = None
		self.realFeatureVariety = 0
		self.realRouteType = None
		self.realTerrainType = None

		self.tempTimerFeature = 0
		self.tempTimerRoute = 0
		self.tempTimerTerrain = 0
		self.tempTimerBonus = 0
		self.tempTimerImprovement = 0
#Magister Stop

	def needToWritePlot(self, plot):
		"returns true if this plot needs to be written out."
		return True

	def preApply(self):
		"apply plot and terrain type"
		plot = CyMap().plot(self.iX, self.iY)
		if (self.plotType != PlotTypes.NO_PLOT):
			plot.setPlotType(self.plotType, False, False)
		if (self.terrainType):
			terrainTypeNum = CvUtil.findInfoTypeNum(gc.getTerrainInfo, gc.getNumTerrainInfos(), self.terrainType)
			plot.setTerrainType(terrainTypeNum, False, False)

	def write(self, f, plot):
		"save plot desc to a file"
		f.write("BeginPlot\n")
		f.write("\tx=%d,y=%d\n" %(plot.getX(), plot.getY()))

		# scriptData
		if (plot.getScriptData() != ""):
			f.write("\tScriptData=%s\n" %plot.getScriptData())
		# rivers
		if (plot.getRiverNSDirection() != CardinalDirectionTypes.NO_CARDINALDIRECTION):
			f.write("\tRiverNSDirection=%d\n" %(int(plot.getRiverNSDirection()),) )
		if (plot.isNOfRiver()):
			f.write("\tisNOfRiver\n")
		if (plot.getRiverWEDirection() != CardinalDirectionTypes.NO_CARDINALDIRECTION):
			f.write("\tRiverWEDirection=%d\n" %(int(plot.getRiverWEDirection()),) )
		if (plot.isWOfRiver()):
			f.write("\tisWOfRiver\n")
		# extras
		if (plot.isStartingPlot()):
			f.write("\tStartingPlot\n")
		if (plot.getBonusType(-1)!=-1):
			f.write("\tBonusType=%s\n" %(gc.getBonusInfo(plot.getBonusType(-1)).getType()) )
		if (plot.getImprovementType()!=-1):
			f.write("\tImprovementType=%s\n" %(gc.getImprovementInfo(plot.getImprovementType()).getType()) )
		if (plot.getFeatureType()!=-1):
			f.write("\tFeatureType=%s, FeatureVariety=%d\n"
			%(gc.getFeatureInfo(plot.getFeatureType()).getType(), plot.getFeatureVariety(), ) )
		if (plot.getRouteType()!=-1):
			f.write("\tRouteType=%s\n" %(gc.getRouteInfo(plot.getRouteType()).getType()) )
		if (plot.getTerrainType()!=-1):
			f.write("\tTerrainType=%s\n" %(gc.getTerrainInfo(plot.getTerrainType()).getType()) )
		if (plot.getPlotType()!=PlotTypes.NO_PLOT):
			f.write("\tPlotType=%d\n" %(int(plot.getPlotType()),) )

#Magister Start
		if plot.isMoveDisabledAI():
			f.write("\tPlotMoveDisabledAI=%d\n" %(int(plot.isMoveDisabledAI())))
		if plot.isMoveDisabledHuman():
			f.write("\tPlotMoveDisabledHuman=%d\n" %(int(plot.isMoveDisabledHuman())))
		if plot.isBuildDisabled():
			f.write("\tPlotBuildDisabled=%d\n" %(int(plot.isBuildDisabled())))
		if plot.isFoundDisabled():
			f.write("\tPlotFoundDisabled=%d\n" %(int(plot.isFoundDisabled())))
		if not plot.isPythonActive():
			f.write("\tPlotPythonActive=%d\n" %(int(plot.isPythonActive())))
		if plot.getMinLevel() > 0:
			f.write("\tPlotMinLevel=%d\n" %(plot.getMinLevel()))
		if plot.getPlotCounter() > 0:
			f.write("\tPlotCounter=%d\n" %(plot.getPlotCounter()))
		if plot.getPortalExitX() > 0:
			f.write("\tPortalExitX=%d\n" %(plot.getPortalExitX()))
		if plot.getPortalExitY() > 0:
			f.write("\tPortalExitY=%d\n" %(plot.getPortalExitY()))


		if (plot.getRealTerrainType()!=-1):
			f.write("\tTerrainType=%s\n" %(gc.getTerrainInfo(plot.getRealTerrainType()).getType()) )
		if plot.getTempTerrainTimer() > 0:
			f.write("\tTempTerrainTimer=%d\n" %(plot.getTempTerrainTimer()))

		if (plot.getRealBonusType()!=-1):
			f.write("\tRealBonusType=%s\n" %(gc.getBonusInfo(plot.getRealBonusType()).getType()) )
		if plot.getTempBonusTimer() > 0:
			f.write("\tTempBonusTimer=%d\n" %(plot.getTempBonusTimer()))

		if (plot.getRealImprovementType()!=-1):
			f.write("\tRealImprovementType=%s\n" %(gc.getImprovementInfo(plot.getRealImprovementType()).getType()) )
		if plot.getTempImprovementTimer() > 0:
			f.write("\tTempImprovementTimer=%d\n" %(plot.getTempImprovementTimer()))

		if (plot.getRealFeatureType()!=-1):
			f.write("\tRealFeatureType=%s, RealFeatureVariety=%d\n"
			%(gc.getFeatureInfo(plot.getRealFeatureType()).getType(), plot.getRealFeatureVariety(), ) )
		if plot.getTempFeatureTimer() > 0:
			f.write("\tTempFeatureTimer=%d\n" %(plot.getTempFeatureTimer()))

		if (plot.getRealRouteType()!=-1):
			f.write("\tRealRouteType=%s\n" %(gc.getRouteInfo(plot.getRealRouteType()).getType()) )
		if plot.getTempRouteTimer() > 0:
			f.write("\tTempRouteTimer=%d\n" %(plot.getTempRouteTimer()))
#Magister Stop

		# units
		for i in range(plot.getNumUnits()):
			unit=plot.getUnit(i)
			if unit.getUnitType() == -1:
				continue
			CvUnitDesc().write(f, unit, plot)
		# city
		if (plot.isCity()):
			CvCityDesc().write(f, plot)

		# Fog of War
		bFirstReveal=true
		for iTeamLoop in range(iNumTeams):#Magister
			if gc.getTeam(iTeamLoop).isAlive():
				if plot.isRevealed(iTeamLoop,0):
					# Plot is revealed for this Team so write out the fact that it is; if not revealed don't write anything
					if bFirstReveal:
						f.write("\tTeamReveal=")
						bFirstReveal=false
					f.write("%d," %(iTeamLoop))
		if bFirstReveal==false:
			f.write("\n")	# terminate reveal line
	## Platy Builder ##
		for iPlayerLoop in xrange(iNumPlayers):#Magister
			iPlayerCulture = plot.getCulture(iPlayerLoop)
			if iPlayerCulture > 0:
				f.write("\tPlayer%dCulture=%d, (%s)\n" %(iPlayerLoop, iPlayerCulture, gc.getPlayer(iPlayerLoop).getName().encode(fileencoding)))

		f.write("EndPlot\n")

	def read(self, f):
		"read in a plot desc"
		self.__init__()
		parser = CvWBParser()
		if parser.findNextToken(f, "BeginPlot")==false:
			return false	# no more plots
		while (true):
			nextLine = parser.getNextLine(f)
			toks = parser.getTokens(nextLine)
			if (len(toks)==0):
				break

			x = parser.findTokenValue(toks, "x")
			y = parser.findTokenValue(toks, "y")
			if (x!=-1 and y!=-1):
				self.iX = int(x)
				self.iY = int(y)
				# print("plot read %d %d" %(self.iX, self.iY))
				continue

			v = parser.findTokenValue(toks, "Landmark")
			if v!=-1:
				self.szLandmark=v
				continue

			v = parser.findTokenValue(toks, "ScriptData")
			if v!=-1:
				self.szScriptData=v
				continue

			v = parser.findTokenValue(toks, "RiverNSDirection")
			if v!=-1:
				self.riverNSDirection = (CardinalDirectionTypes(v))
				continue

			if (parser.findTokenValue(toks, "isNOfRiver"))!=-1:
				self.isNOfRiver = (true)
				continue

			v = parser.findTokenValue(toks, "RiverWEDirection")
			if v!=-1:
				self.riverWEDirection = (CardinalDirectionTypes(v))
				continue

			if (parser.findTokenValue(toks, "isWOfRiver"))!=-1:
				self.isWOfRiver = (true)
				continue

			if (parser.findTokenValue(toks, "StartingPlot"))!=-1:
				self.isStartingPlot = (true)
				continue

			v = parser.findTokenValue(toks, "BonusType")
			if v!=-1:
				self.bonusType = v
				continue

			v = parser.findTokenValue(toks, "ImprovementType")
			if v!=-1:
				self.improvementType = v
				continue

			v = parser.findTokenValue(toks, "FeatureType")
			if v!=-1:
				self.featureType = v
				v = parser.findTokenValue(toks, "FeatureVariety")
				if v!=-1:
					self.featureVariety = int(v)
				continue

			v = parser.findTokenValue(toks, "RouteType")
			if v!=-1:
				self.routeType = v
				continue

			v = parser.findTokenValue(toks, "TerrainType")
			if v!=-1:
				self.terrainType = v
				continue

			v = parser.findTokenValue(toks, "PlotType")
			if v!=-1:
				self.plotType = PlotTypes(v)
				continue

#Magister Start
			v = parser.findTokenValue(toks, "PlotMoveDisabledAI")
			if v!=-1:
				self.bMoveDisabledAI = int(v)
				continue

			v = parser.findTokenValue(toks, "PlotMoveDisabledHuman")
			if v!=-1:
				self.bMoveDisabledHuman = int(v)
				continue

			v = parser.findTokenValue(toks, "PlotBuildDisabled")
			if v!=-1:
				self.bBuildDisabled = int(v)
				continue

			v = parser.findTokenValue(toks, "PlotFoundDisabled")
			if v!=-1:
				self.bFoundDisabled = int(v)
				continue

			v = parser.findTokenValue(toks, "PlotPythonActive")
			if v!=-1:
				self.bPythonActive = int(v)
				continue

			v = parser.findTokenValue(toks, "PlotMinLevel")
			if v!=-1:
				self.plotMinLevel = int(v)
				continue

			v = parser.findTokenValue(toks, "PlotCounter")
			if v!=-1:
				self.plotCounter = int(v)
				continue

			v = parser.findTokenValue(toks, "PortalExitX")
			if v!=-1:
				self.portalExitX = int(v)
				continue

			v = parser.findTokenValue(toks, "PortalExitY")
			if v!=-1:
				self.portalExitY = int(v)
				continue


			v = parser.findTokenValue(toks, "RealBonusType")
			if v!=-1:
				self.realBonusType = v
				continue

			v = parser.findTokenValue(toks, "RealImprovementType")
			if v!=-1:
				self.realImprovementType = v
				continue

			v = parser.findTokenValue(toks, "RealFeatureType")
			if v!=-1:
				self.realFeatureType = v
				v = parser.findTokenValue(toks, "RealFeatureVariety")
				if v!=-1:
					self.realFeatureVariety = int(v)
				continue

			v = parser.findTokenValue(toks, "RealRouteType")
			if v!=-1:
				self.realRouteType = v
				continue

			v = parser.findTokenValue(toks, "RealTerrainType")
			if v!=-1:
				self.terrainType = v
				continue

			v = parser.findTokenValue(toks, "TempFeatureTimer")
			if v!=-1:
				self.tempTimerFeature = int(v)
				continue

			v = parser.findTokenValue(toks, "TempRouteTimer")
			if v!=-1:
				self.tempTimerRoute = int(v)
				continue

			v = parser.findTokenValue(toks, "TempTerrainTimer")
			if v!=-1:
				self.tempTimerTerrain = int(v)
				continue

			v = parser.findTokenValue(toks, "TempBonusTimer")
			if v!=-1:
				self.tempTimerBonus = int(v)
				continue

			v = parser.findTokenValue(toks, "TempImprovementTimer")
			if v!=-1:
				self.tempTimerImprovement = int(v)
				continue
#Magister Stop

			# Units
			v = parser.findTokenValue(toks, "BeginUnit")
			if v!=-1:
				unitDesc = CvUnitDesc()
				unitDesc.read(f, self.iX, self.iY)
				self.unitDescs.append(unitDesc)
				continue

			# City
			v = parser.findTokenValue(toks, "BeginCity")
			if v!=-1:
				self.cityDesc = CvCityDesc()
				self.cityDesc.read(f, self.iX, self.iY)
				continue

			# Fog of War

			v = parser.findTokenValue(toks, "TeamReveal")
			if v!=-1:
				for iTeamLoop in toks:
					iTeamLoop = iTeamLoop.lstrip('TeamReveal=')
					if len(iTeamLoop):
						self.abTeamPlotRevealed.append(int(iTeamLoop))
				continue

			if parser.findTokenValue(toks, "EndPlot")!=-1:
				break

		## Platy Builder ##
			for iPlayerLoop in xrange(iNumPlayers):#Magister
				szCityTag = ("Player%dCulture" %(iPlayerLoop))
				v = parser.findTokenValue(toks, szCityTag)
				if v!=-1:
					if int(v) > 0:
						self.lCulture.append([iPlayerLoop, int(v)])
					continue
		return True

	def apply(self):
		"after reading, this will actually apply the data"
		#print("apply plot %d %d" %(self.iX, self.iY))
		plot = CyMap().plot(self.iX, self.iY)
		plot.setNOfRiver(self.isNOfRiver, self.riverWEDirection)
		plot.setWOfRiver(self.isWOfRiver, self.riverNSDirection)
		plot.setStartingPlot(self.isStartingPlot)
		if (self.bonusType):
			bonusTypeNum = CvUtil.findInfoTypeNum(gc.getBonusInfo, gc.getNumBonusInfos(), self.bonusType)
			plot.setBonusType(bonusTypeNum)
		if (self.improvementType):
			improvementTypeNum = CvUtil.findInfoTypeNum(gc.getImprovementInfo, gc.getNumImprovementInfos(), self.improvementType)
			plot.setImprovementType(improvementTypeNum)
		if (self.featureType):
			featureTypeNum = CvUtil.findInfoTypeNum(gc.getFeatureInfo, gc.getNumFeatureInfos(), self.featureType)
			plot.setFeatureType(featureTypeNum, self.featureVariety)
		if (self.routeType):
			routeTypeNum = CvUtil.findInfoTypeNum(gc.getRouteInfo, gc.getNumRouteInfos(), self.routeType)
			plot.setRouteType(routeTypeNum)

		if (self.szLandmark != ""):
			CyEngine().addLandmark(CyMap().plot(self.iX, self.iY), "%s" %(self.szLandmark))

		if (self.szScriptData != ""):
			plot.setScriptData(self.szScriptData)

#Magister Start
		plot.setMoveDisabledAI(bool(self.bMoveDisabledAI))
		plot.setMoveDisabledHuman(bool(self.bMoveDisabledHuman))
		plot.setBuildDisabled(bool(self.bBuildDisabled))
		plot.setFoundDisabled(bool(self.bFoundDisabled))
		plot.setPythonActive(bool(self.bPythonActive))
		if self.plotMinLevel > 0:
			plot.setMinLevel(self.plotMinLevel)
		if self.plotCounter > 0:
			plot.changePlotCounter(self.plotCounter -plot.getPlotCounter())
		if self.portalExitX > 0:
			plot.setPortalExitX(self.portalExitX)
		if self.portalExitY > 0:
			plot.setPortalExitY(self.portalExitY)

		if (self.realTerrainType):
			terrainTypeNum = CvUtil.findInfoTypeNum(gc.getBonusInfo, gc.getNumBonusInfos(), self.realTerrainType)
			plot.setRealTerrainType(terrain)

		if (self.realBonusType):
			bonusTypeNum = CvUtil.findInfoTypeNum(gc.getBonusInfo, gc.getNumBonusInfos(), self.realBonusType)
			plot.setRealBonusType(bonusTypeNum)
		if (self.realImprovementType):
			improvementTypeNum = CvUtil.findInfoTypeNum(gc.getImprovementInfo, gc.getNumImprovementInfos(), self.realImprovementType)
			plot.setRealImprovementType(improvementTypeNum)
		if (self.realFeatureType):
			featureTypeNum = CvUtil.findInfoTypeNum(gc.getFeatureInfo, gc.getNumFeatureInfos(), self.realFeatureType)
			plot.setRealFeatureType(featureTypeNum)
			plot.setRealFeatureVariety(self.realFeatureVariety)
		if (self.realRouteType):
			routeTypeNum = CvUtil.findInfoTypeNum(gc.getRouteInfo, gc.getNumRouteInfos(), self.realRouteType)
			plot.setRealRouteType(routeTypeNum)

		if self.tempTimerFeature > 0:
			plot.changeTempFeatureTimer(self.tempTimerFeature)
		if self.tempTimerRoute > 0:
			plot.changeTempRouteTimer(self.tempTimerRoute)
		if self.tempTimerTerrain > 0:
			plot.changeTempTerrainTimer(self.tempTimerTerrain)
		if self.tempTimerBonus > 0:
			plot.changeTempBonusTimer(self.tempTimerBonus)
		if self.tempTimerImprovement > 0:
			plot.changeTempImprovementTimer(self.tempTimerImprovement)
#Magister Stop

	def applyUnits(self):
		#print "--apply units"
		for u in self.unitDescs:
			u.apply()

	def applyCity(self, bSpecial):
		if self.cityDesc:
			#print "--apply city"
			self.cityDesc.apply(bSpecial)

################
class CvMapDesc:
	"serialize map data"
	def __init__(self):
		self.iGridW = 0
		self.iGridH = 0
		self.iTopLatitude = 0
		self.iBottomLatitude = 0
		self.bWrapX = 0
		self.bWrapY = 0
		self.worldSize = None
		self.climate = None
		self.seaLevel = None
		self.numPlotsWritten = 0
		self.numSignsWritten = 0
		self.bRandomizeResources = "false"

#FfH: Added by Kael 10/04/2008
		self.bRandomizeLairs = "false"
		self.bRandomizeUniqueImprovements = "false"
		self.bRandomizeGoodyHuts = "false"
#FfH: End Add

	def write(self, f):
		"write map data"
		map = CyMap()
		iGridW = map.getGridWidth()
		iGridH = map.getGridHeight()
		iNumPlots = iGridW * iGridH
		iNumSigns = CyEngine().getNumSigns()

		f.write("BeginMap\n")
		f.write("\tgrid width=%d\n" %(map.getGridWidth(),))
		f.write("\tgrid height=%d\n" %(map.getGridHeight(),))
		f.write("\ttop latitude=%d\n" %(map.getTopLatitude(),))
		f.write("\tbottom latitude=%d\n" %(map.getBottomLatitude(),))
		f.write("\twrap X=%d\n" %(map.isWrapX(),))
		f.write("\twrap Y=%d\n" %(map.isWrapY(),))
		f.write("\tworld size=%s\n" %(gc.getWorldInfo(map.getWorldSize()).getType(),))
		f.write("\tclimate=%s\n" %(gc.getClimateInfo(map.getClimate()).getType(),))
		f.write("\tsealevel=%s\n" %(gc.getSeaLevelInfo(map.getSeaLevel()).getType(),))
		f.write("\tnum plots written=%d\n" %(iNumPlots,))
		f.write("\tnum signs written=%d\n" %(iNumSigns,))
		f.write("\tRandomize Resources=false\n")

#FfH: Added by Kael 10/04/2008
		f.write("\tRandomize Lairs=false\n")
		f.write("\tRandomize Unique Improvements=false\n")
		f.write("\tRandomize Goody Huts=false\n")
#FfH: End Add

		f.write("EndMap\n")

	def read(self, f):
		"read map data"
		self.__init__()
		parser = CvWBParser()
		if parser.findNextToken(f, "BeginMap")==false:
			print "can't find map"
			return
		while (true):
			nextLine = parser.getNextLine(f)
			toks = parser.getTokens(nextLine)
			if (len(toks)==0):
				break

			v = parser.findTokenValue(toks, "grid width")
			if v!=-1:
				self.iGridW = int(v)
				continue

			v = parser.findTokenValue(toks, "grid height")
			if v!=-1:
				self.iGridH = int(v)
				continue

			v = parser.findTokenValue(toks, "top latitude")
			if v!=-1:
				self.iTopLatitude = int(v)
				continue

			v = parser.findTokenValue(toks, "bottom latitude")
			if v!=-1:
				self.iBottomLatitude = int(v)
				continue

			v = parser.findTokenValue(toks, "wrap X")
			if v!=-1:
				self.bWrapX = int(v)
				continue

			v = parser.findTokenValue(toks, "wrap Y")
			if v!=-1:
				self.bWrapY = int(v)
				continue

			v = parser.findTokenValue(toks, "world size")
			if v!=-1:
				self.worldSize = v
				continue

			v = parser.findTokenValue(toks, "climate")
			if v!=-1:
				self.climate = v
				continue

			v = parser.findTokenValue(toks, "sealevel")
			if v!=-1:
				self.seaLevel = v
				continue

			v = parser.findTokenValue(toks, "num plots written")
			if v!=-1:
				self.numPlotsWritten = int(v)
				continue

			v = parser.findTokenValue(toks, "num signs written")
			if v!=-1:
				self.numSignsWritten = int(v)
				continue

			v = parser.findTokenValue(toks, "Randomize Resources")
			if v!=-1:
				self.bRandomizeResources = v
				continue

#FfH: Added by Kael 10/04/2008
			v = parser.findTokenValue(toks, "Randomize Lairs")
			if v!=-1:
				self.bRandomizeLairs = v
				continue

			v = parser.findTokenValue(toks, "Randomize Unique Improvements")
			if v!=-1:
				self.bRandomizeUniqueImprovements = v
				continue

			v = parser.findTokenValue(toks, "Randomize Goody Huts")
			if v!=-1:
				self.bRandomizeGoodyHuts = v
				continue
#FfH: End Add

			if parser.findTokenValue(toks, "EndMap")!=-1:
				break

################
class CvSignDesc:
	"serialize map data"
	def __init__(self):
		self.iPlotX = 0
		self.iPlotY = 0
		self.playerType = 0
		self.szCaption = ""

	def apply(self):
		plot = CyMap().plot(self.iPlotX, self.iPlotY)
		CyEngine().addSign(plot, self.playerType, self.szCaption)

	def write(self, f, sign):
		"write sign data"
		f.write("BeginSign\n")
		f.write("\tplotX=%d\n" %(sign.getPlot().getX(),))
		f.write("\tplotY=%d\n" %(sign.getPlot().getY(),))
		if sign.getPlayerType() > -1:
			f.write("\tplayerType=%d, (%s)\n" %(sign.getPlayerType(), gc.getPlayer(sign.getPlayerType()).getName().encode(fileencoding)))
		f.write("\tcaption=%s\n" %(sign.getCaption(),))
		f.write("EndSign\n")

	def read(self, f):
		"read sign data"
		self.__init__()
		parser = CvWBParser()
		if parser.findNextToken(f, "BeginSign")==false:
			print "can't find sign"
			return
		while (true):
			nextLine = parser.getNextLine(f)
			toks = parser.getTokens(nextLine)
			if (len(toks)==0):
				break

			v = parser.findTokenValue(toks, "plotX")
			if v!=-1:
				self.iPlotX = int(v)
				continue

			v = parser.findTokenValue(toks, "plotY")
			if v!=-1:
				self.iPlotY = int(v)
				continue

			v = parser.findTokenValue(toks, "playerType")
			if v!=-1:
				self.playerType = int(v)
				continue

			v = parser.findTokenValue(toks, "caption")
			if v!=-1:
				self.szCaption = v
				continue

			if parser.findTokenValue(toks, "EndSign")!=-1:
				break

		return True

class CvWBDesc:
	"handles saving/loading a worldbuilder description file"
	def __init__(self):
		# game data
		self.gameDesc = CvGameDesc()
		self.playersDesc = None
		self.plotDesc = None	# list
		self.signDesc = None	# list
		self.mapDesc = CvMapDesc()

	def getVersion(self):
		return version

	def getDescFileName(self, fileName):
		return fileName+getWBSaveExtension()

	def write(self, fileName):
		"Save out a high-level desc of the world, and height/terrainmaps"
		fileName = os.path.normpath(fileName)
		fileName,ext = os.path.splitext(fileName)
		CvUtil.pyPrint( 'saveDesc:%s, curDir:%s' %(fileName,os.getcwd()) )

		f = file(self.getDescFileName(fileName), "w")		# open text file
	## Platy Builder ##
		f.write("%s\n" %("Platy Builder"))
		f.write("bLoadSpecial=1\n")
	## Platy Builder ##
		f.write("Version=%d\n" %(self.getVersion(),))
		self.gameDesc.write(f)	# write game info

		for i in range(iNumTeams):
			CvTeamDesc().write(f, i)		# write team info

		for i in range(iNumPlayers):
			CvPlayerDesc().write(f, i)		# write player info

		self.mapDesc.write(f)	# write map info

		f.write("\n### Plot Info ###\n")
		iGridW = CyMap().getGridWidth()
		iGridH = CyMap().getGridHeight()
		for iX in range(iGridW):
			for iY in range(iGridH):
				plot = CyMap().plot(iX, iY)
				pDesc = CvPlotDesc()
				if pDesc.needToWritePlot(plot):
					pDesc.write(f, plot)

		f.write("\n### Sign Info ###\n")
		iNumSigns = CyEngine().getNumSigns()
		for i in range(iNumSigns):
			sign = CyEngine().getSignByIndex(i)
			pDesc = CvSignDesc()
			pDesc.write(f, sign)

		f.close()

		print("WBSave done\n")
		return 0	# success

	def applyMap(self):
		"after reading setup the map"

		self.gameDesc.apply()

		# recreate map
		print("map rebuild. gridw=%d, gridh=%d" %(self.mapDesc.iGridW, self.mapDesc.iGridH))
		worldSizeType = CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), self.mapDesc.worldSize)
		climateType = CvUtil.findInfoTypeNum(gc.getClimateInfo, gc.getNumClimateInfos(), self.mapDesc.climate)
		seaLevelType = CvUtil.findInfoTypeNum(gc.getSeaLevelInfo, gc.getNumSeaLevelInfos(), self.mapDesc.seaLevel)
		CyMap().rebuild(self.mapDesc.iGridW, self.mapDesc.iGridH, self.mapDesc.iTopLatitude, self.mapDesc.iBottomLatitude, self.mapDesc.bWrapX, self.mapDesc.bWrapY, WorldSizeTypes(worldSizeType), ClimateTypes(climateType), SeaLevelTypes(seaLevelType), 0, None)

		print "preapply plots"
		for pDesc in self.plotDesc:
			pDesc.preApply()	# set plot type / terrain type

		print("map apply - recalc areas/regions")
		CyMap().recalculateAreas()

		print "apply plots"
		for pDesc in self.plotDesc:
			pDesc.apply()

		print "apply signs"
		for pDesc in self.signDesc:
			pDesc.apply()

		print "Randomize Resources"
		if str(self.mapDesc.bRandomizeResources).lower() != "false":
			for iPlotLoop in range(CyMap().numPlots()):
				pPlot = CyMap().plotByIndex(iPlotLoop)
				pPlot.setBonusType(BonusTypes.NO_BONUS)
			CyMapGenerator().addBonuses()

#FfH: Added by Kael 10/04/2008
		print "Randomize Lairs"
		if (self.mapDesc.bRandomizeLairs != "false"):
			CyMapGenerator().addImprovements()

		print "Randomize Unique Features"
		if (self.mapDesc.bRandomizeUniqueImprovements != "false"):
			CyMapGenerator().addUniqueImprovements()

		print "Randomize Goody Huts"
		if (self.mapDesc.bRandomizeGoodyHuts != "false"):
			CyMapGenerator().addGoodies()
#FfH: End Add

		print ("WB apply done\n")
		return 0	# ok

## Platy Builder ##
	def getAssignedStartingPlots(self):
		for iPlayerLoop in xrange(len(self.playersDesc)):

			pPlayer = gc.getPlayer(iPlayerLoop)
			pWBPlayer = self.playersDesc[iPlayerLoop]

			# Random Start Location
			if (pPlayer.getLeaderType() != -1 and str(pWBPlayer.bRandomStartLocation).lower() != "false"):
				pPlayer.setStartingPlot(pPlayer.findStartingPlot(true), True)

			else:

				# Player's starting plot
				if ((pWBPlayer.iStartingX != -1) and (pWBPlayer.iStartingY != -1)):
					pPlayer.setStartingPlot(CyMap().plot(pWBPlayer.iStartingX, pWBPlayer.iStartingY), True)

		return 0	# ok

	def applyInitialItems(self):
		for iTeamLoop in xrange(len(self.teamsDesc)):
			pTeam = gc.getTeam(iTeamLoop)
			pWBTeam = self.teamsDesc[iTeamLoop]

			for techTypeTag in pWBTeam.techTypes:
				techType = CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), techTypeTag)
				pTeam.setHasTech(techType, true, PlayerTypes.NO_PLAYER, false, false)
			for item in pWBTeam.aaiEspionageAgainstTeams:
				pTeam.setEspionagePointsAgainstTeam(item[0], item[1])
			for item in pWBTeam.bContactWithTeamList:
				pTeam.meet(item, false)
			for item in pWBTeam.bWarWithTeamList:
				pTeam.declareWar(item, false, WarPlanTypes.NO_WARPLAN)
			for item in pWBTeam.bPermanentWarPeaceList:
				pTeam.setPermanentWarPeace(item, true)
			for item in pWBTeam.bOpenBordersWithTeamList:
				pTeam.signOpenBorders(item)
			for item in pWBTeam.bDefensivePactWithTeamList:
				pTeam.signDefensivePact(item)
			for item in pWBTeam.bVassalOfTeamList:
				gc.getTeam(item[0]).assignVassal(iTeamLoop, item[1])
			for project in pWBTeam.projectType:
				projectTypeNum = CvUtil.findInfoTypeNum(gc.getProjectInfo, gc.getNumProjectInfos(), project)
				pTeam.changeProjectCount(projectTypeNum, 1)
				projectCount = pTeam.getProjectCount(projectTypeNum)
				pTeam.setProjectArtType(projectTypeNum, projectCount - 1, 0)

		for iPlayerLoop in xrange(len(self.playersDesc)):
			pPlayer = gc.getPlayer(iPlayerLoop)
			pWBPlayer = self.playersDesc[iPlayerLoop]

			pPlayer.setGold(pWBPlayer.iStartingGold)
			if ((pWBPlayer.iStartingX != -1) and (pWBPlayer.iStartingY != -1)):
				pPlayer.setStartingPlot(CyMap().plot(pWBPlayer.iStartingX, pWBPlayer.iStartingY), True)

			if (pWBPlayer.stateReligion != ""):
				iStateReligionID = gc.getInfoTypeForString(pWBPlayer.stateReligion)
				pPlayer.setLastStateReligion(iStateReligionID)

			if (pWBPlayer.szStartingEra != ""):
				iStartingEra = gc.getInfoTypeForString(pWBPlayer.szStartingEra)
				pPlayer.setCurrentEra(iStartingEra)

			if str(pWBPlayer.bRandomStartLocation).lower() != "false":
				pPlayer.setStartingPlot(pPlayer.findStartingPlot(True), True)
				print("Setting player %d starting location to (%d,%d)", pPlayer.getID(), pPlayer.getStartingPlot().getX(), pPlayer.getStartingPlot().getY())

			for item in pWBPlayer.aaiCivics:
				pPlayer.setCivics(item[0],item[1])
			for item in pWBPlayer.aaiAttitudeExtras:
				pPlayer.AI_setAttitudeExtra(item[0],item[1])
			for item in pWBPlayer.aszCityList:
				pPlayer.addCityName(item)
			pPlayer.setScriptData(pWBPlayer.sScriptData)

#Magister Start
			# Alignment
			if pWBPlayer.sAlignment != '':
				pPlayer.setAlignment(gc.getInfoTypeForString(pWBPlayer.sAlignment))

			#Traits
			if len(pWBPlayer.TraitType) > 0:
				for iTrait in range(gc.getNumTraitInfos()):
					if iTrait in pWBPlayer.TraitType:
						pPlayer.setHasTrait(iTrait, True)
					else:
						pPlayer.setHasTrait(iTrait, False)

			#Disables
			pPlayer.changeDisableProduction(pWBPlayer.iDisableProduction - pPlayer.getDisableProduction())
			pPlayer.changeDisableResearch(pWBPlayer.iDisableResearch - pPlayer.getDisableResearch())
			pPlayer.changeDisableSpellcasting(pWBPlayer.iDisableSpellcasting - pPlayer.getDisableSpellcasting())

			#Feats
			for i in range(len(pWBPlayer.FeatType)):
				iFeat = pWBPlayer.FeatType[i]
				pPlayer.setFeatAccomplished(iFeat, not pPlayer.isFeatAccomplished(iFeat))
#Magister Stop

		for pDesc in self.plotDesc:
			pDesc.applyCity(self.bSpecial)

		for iTeamLoop in xrange(len(self.teamsDesc)):
			pTeam = gc.getTeam(iTeamLoop)
			pWBTeam = self.teamsDesc[iTeamLoop]
			if pWBTeam.bRevealMap:
				CyMap().setRevealedPlots(iTeamLoop, True, False)
			if pWBTeam.iVassalPower > 0:
				pTeam.setVassalPower(pWBTeam.iVassalPower)
			if pWBTeam.iMasterPower > 0:
				pTeam.setMasterPower(pWBTeam.iMasterPower)
			if pWBTeam.iEspionageEver > 0:
				pTeam.setEspionagePointsEver(pWBTeam.iEspionageEver)

	## Platy Builder ##
			if self.bSpecial:
				pTeam.setMapCentering(pWBTeam.bMapCentering)
				pTeam.changeMapTradingCount(pWBTeam.bMapTrading)
				pTeam.changeTechTradingCount(pWBTeam.bTechTrading)
				pTeam.changeGoldTradingCount(pWBTeam.bGoldTrading)
				pTeam.changeOpenBordersTradingCount(pWBTeam.bOpenBordersTrading)
				pTeam.changeDefensivePactTradingCount(pWBTeam.bDefensivePactTrading)
				pTeam.changePermanentAllianceTradingCount(pWBTeam.bPermanentAllianceTrading)
				pTeam.changeVassalTradingCount(pWBTeam.bVassalStateTrading)
				pTeam.changeBridgeBuildingCount(pWBTeam.bBridgeBuilding)
				pTeam.changeIrrigationCount(pWBTeam.bIrrigation)
				pTeam.changeIgnoreIrrigationCount(pWBTeam.bIgnoreIrrigation)
				pTeam.changeWaterWorkCount(pWBTeam.bWaterWork)
				pTeam.changeNukeInterception(pWBTeam.iNukeInterception - pTeam.getNukeInterception())
				pTeam.changeEnemyWarWearinessModifier(pWBTeam.iEnemyWarWeariness- pTeam.getEnemyWarWearinessModifier())
				for item in pWBTeam.lDomainMoves:
					pTeam.changeExtraMoves(item[0], item[1] - pTeam.getExtraMoves(item[0]))
				for item in pWBTeam.lRouteMoves:
					pTeam.changeRouteChange(item[0], item[1] - pTeam.getRouteChange(item[0]))
				for item in pWBTeam.lImprovementYield:
					pTeam.changeImprovementYieldChange(item[0], item[1], item[2] - pTeam.getImprovementYieldChange(item[0], item[1]))

		if self.bSpecial:
			for iPlayerLoop in xrange(len(self.playersDesc)):
				pPlayer = gc.getPlayer(iPlayerLoop)
				pWBPlayer = self.playersDesc[iPlayerLoop]
				pPlayer.changeGoldenAgeTurns(pWBPlayer.iGoldenAge - pPlayer.getGoldenAgeTurns())
				pPlayer.changeAnarchyTurns(pWBPlayer.iAnarchy - pPlayer.getAnarchyTurns())
				pPlayer.setCombatExperience(pWBPlayer.iCombatXP)
				pPlayer.changeCoastalTradeRoutes(pWBPlayer.iCoastalTradeRoute - pPlayer.getCoastalTradeRoutes())
				pPlayer.changeStateReligionUnitProductionModifier(pWBPlayer.iStateReligionUnit - pPlayer.getStateReligionUnitProductionModifier())
				pPlayer.changeStateReligionBuildingProductionModifier(pWBPlayer.iStateReligionBuilding - pPlayer.getStateReligionBuildingProductionModifier())

		for iPlotLoop in range(self.mapDesc.numPlotsWritten):
			pWBPlot = self.plotDesc[iPlotLoop]
			pPlot = CyMap().plot(pWBPlot.iX, pWBPlot.iY)
			for item in pWBPlot.lCulture:
				pPlot.setCulture(item[0], item[1], True)

		for iPlotLoop in range(self.mapDesc.numPlotsWritten):
			pWBPlot = self.plotDesc[iPlotLoop]
			for iTeamLoop in pWBPlot.abTeamPlotRevealed:
				pPlot = CyMap().plot(pWBPlot.iX, pWBPlot.iY)
				pPlot.setRevealed(iTeamLoop, True, False, TeamTypes.NO_TEAM)

		for pDesc in self.plotDesc:
			pDesc.applyUnits()

		return 0

	def read(self, fileName):
		"Load in a high-level desc of the world, and height/terrainmaps"
		fileName = os.path.normpath(fileName)
		fileName,ext=os.path.splitext(fileName)
		if len(ext) == 0:
			ext = getWBSaveExtension()
		CvUtil.pyPrint( 'loadDesc:%s, curDir:%s' %(fileName,os.getcwd()) )

		if (not os.path.isfile(fileName+ext)):
			CvUtil.pyPrint("Error: file %s does not exist" %(fileName+ext,))
			return -1	# failed

		f=file(fileName+ext, "r")# open text file

	## Platy Builder ##
		self.bSpecial = 1
		parser = CvWBParser()
		filePos = f.tell()
		iNumPlayers = gc.getMAX_CIV_PLAYERS()
		iNumTeams = gc.getMAX_CIV_TEAMS()
		line = parser.getNextLine(f)
		if line.find("Platy") > -1:
			iNumPlayers = gc.getMAX_PLAYERS()
			iNumTeams = gc.getMAX_TEAMS()
		else:
			f.seek(filePos)
		filePos = f.tell()
		line = parser.getNextLine(f)
		if line.find("bLoadSpecial") > -1:
			f.seek(filePos)
			self.bSpecial = int(parser.findNextTokenValue(f, "bLoadSpecial"))
		else:
			f.seek(filePos)
		version = int(parser.findNextTokenValue(f, "Version"))
		if (version != self.getVersion()):
			CvUtil.pyPrint("Error: wrong WorldBuilder save version.  Expected %d, got %d" %(self.getVersion(), version))
			return -1	# failed

		print "Reading game desc"
		self.gameDesc.read(f)	# read game info

		print "Reading teams desc"
		filePos = f.tell()
		self.teamsDesc = []
		for i in range(iNumTeams):
			print ("reading team %d" %(i))
			teamsDesc = CvTeamDesc()
			if (teamsDesc.read(f)==false):					# read team info
				f.seek(filePos)								# abort and backup
				break
			self.teamsDesc.append(teamsDesc)

		print "Reading players desc"
		self.playersDesc = []
		for i in range(iNumPlayers):
			playerDesc = CvPlayerDesc()
			playerDesc.read(f)				# read player info
			self.playersDesc.append(playerDesc)
	## Platy Builder ##

		print "Reading map desc"
		self.mapDesc.read(f)	# read map info

		print("Reading/creating %d plot descs" %(self.mapDesc.numPlotsWritten,))
		self.plotDesc = []
		for i in range(self.mapDesc.numPlotsWritten):
			pDesc = CvPlotDesc()
			if pDesc.read(f)==True:
				self.plotDesc.append(pDesc)
			else:
				break

		print("Reading/creating %d sign descs" %(self.mapDesc.numSignsWritten,))
		self.signDesc = []
		for i in range(self.mapDesc.numSignsWritten):
			pDesc = CvSignDesc()
			if pDesc.read(f)==True:
				self.signDesc.append(pDesc)
			else:
				break

		f.close()
		print ("WB read done\n")
		return 0