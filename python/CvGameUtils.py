## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
##
## Implementaion of miscellaneous game functions

import CvUtil
from CvPythonExtensions import *
import CvEventInterface
import CustomFunctions
import ScenarioFunctions

import PyHelpers
PyPlayer = PyHelpers.PyPlayer

# globals
cf = CustomFunctions.CustomFunctions()
gc = CyGlobalContext()
sf = ScenarioFunctions.ScenarioFunctions()

import CvModName

class CvGameUtils:
	"Miscellaneous game functions"
	def __init__(self):
		pass

	def isVictoryTest(self):
		return CyGame().getElapsedGameTurns() > 10

	def isVictory(self, argsList):
		eVictory = argsList[0]
		return True

	def isPlayerResearch(self, argsList):
		ePlayer = argsList[0]
		return True

	def getExtraCost(self, argsList):
		ePlayer = argsList[0]
		return 0

	def createBarbarianCities(self):
		return False

	def createBarbarianUnits(self):
		return False

	def skipResearchPopup(self,argsList):
		ePlayer = argsList[0]
		return False

	def showTechChooserButton(self,argsList):
		ePlayer = argsList[0]
		return True

	def getFirstRecommendedTech(self,argsList):
		ePlayer = argsList[0]
		return TechTypes.NO_TECH

	def getSecondRecommendedTech(self,argsList):
		ePlayer = argsList[0]
		eFirstTech = argsList[1]
		return TechTypes.NO_TECH

	def canRazeCity(self,argsList):
		iRazingPlayer, pCity = argsList
		return True

	def canDeclareWar(self,argsList):
		iAttackingTeam, iDefendingTeam = argsList
		return True

	def skipProductionPopup(self,argsList):
		pCity = argsList[0]
		return False

	def showExamineCityButton(self,argsList):
		pCity = argsList[0]
		return True

	def getRecommendedUnit(self,argsList):
		pCity = argsList[0]
		return UnitTypes.NO_UNIT

	def getRecommendedBuilding(self,argsList):
		pCity = argsList[0]
		return BuildingTypes.NO_BUILDING

	def updateColoredPlots(self):
		return False

	def isActionRecommended(self,argsList):
		pUnit = argsList[0]
		iAction = argsList[1]
		return False

	def unitCannotMoveInto(self,argsList):
		ePlayer = argsList[0]
		iUnitId = argsList[1]
		iPlotX = argsList[2]
		iPlotY = argsList[3]
		return False

	def cannotHandleAction(self,argsList):
		pPlot = argsList[0]
		iAction = argsList[1]
		bTestVisible = argsList[2]
		return False

	def canBuild(self,argsList):
		iX, iY, iBuild, iPlayer = argsList
		return -1	# Returning -1 means ignore; 0 means Build cannot be performed; 1 or greater means it can

	def cannotFoundCity(self,argsList):
		iPlayer, iPlotX, iPlotY = argsList
		return False

	def cannotSelectionListMove(self,argsList):
		pPlot = argsList[0]
		bAlt = argsList[1]
		bShift = argsList[2]
		bCtrl = argsList[3]
		return False

	def cannotSelectionListGameNetMessage(self,argsList):
		eMessage = argsList[0]
		iData2 = argsList[1]
		iData3 = argsList[2]
		iData4 = argsList[3]
		iFlags = argsList[4]
		bAlt = argsList[5]
		bShift = argsList[6]
		return False

	def cannotDoControl(self,argsList):
		eControl = argsList[0]
		return False

	def canResearch(self,argsList):
		ePlayer = argsList[0]
		eTech = argsList[1]
		bTrade = argsList[2]
		return False

	def cannotResearch(self,argsList):
		ePlayer = argsList[0]
		eTech = argsList[1]
		bTrade = argsList[2]
		pPlayer = gc.getPlayer(ePlayer)
		iCiv = pPlayer.getCivilizationType()
		eTeam = gc.getTeam(pPlayer.getTeam())

		bNonReligiousPlayer = False
		if pPlayer.hasTrait(gc.getInfoTypeForString('TRAIT_AGNOSTIC')):
			bNonReligiousPlayer = True
		elif pPlayer.isBarbarian():
			bNonReligiousPlayer = True

		if eTech == gc.getInfoTypeForString('TECH_ORDERS_FROM_HEAVEN'):
			if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_RELIGION_1):
				return True
			if bNonReligiousPlayer:
				return True

		if eTech == gc.getInfoTypeForString('TECH_WAY_OF_THE_EARTHMOTHER'):
			if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_RELIGION_3):
				return True
			if bNonReligiousPlayer:
				return True

		if eTech == gc.getInfoTypeForString('TECH_WAY_OF_THE_FORESTS'):
			if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_RELIGION_0):
				return True
			if bNonReligiousPlayer:
				return True

		if eTech == gc.getInfoTypeForString('TECH_MESSAGE_FROM_THE_DEEP'):
			if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_RELIGION_2):
				return True
			if bNonReligiousPlayer:
				return True

		if eTech == gc.getInfoTypeForString('TECH_CORRUPTION_OF_SPIRIT'):
			if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_RELIGION_4):
				return True
			if bNonReligiousPlayer:
				return True

		if eTech == gc.getInfoTypeForString('TECH_HONOR'):
			if bNonReligiousPlayer:
				return True

		if eTech == gc.getInfoTypeForString('TECH_DECEPTION'):
			if bNonReligiousPlayer:
				return True

		if eTech == gc.getInfoTypeForString('TECH_SEAFARING'):
			if iCiv != gc.getInfoTypeForString('CIVILIZATION_LANUN'):
				return True

		if CyGame().getWBMapScript():
			bBlock = sf.cannotResearch(ePlayer, eTech, bTrade)
			if bBlock:
				return True

		return False

	def canDoCivic(self,argsList):
		ePlayer = argsList[0]
		eCivic = argsList[1]
		return False

	def cannotDoCivic(self,argsList):
		ePlayer = argsList[0]
		eCivic = argsList[1]
		return False

	def canTrain(self,argsList):
		pCity = argsList[0]
		eUnit = argsList[1]
		bContinue = argsList[2]
		bTestVisible = argsList[3]
		bIgnoreCost = argsList[4]
		bIgnoreUpgrades = argsList[5]
		return False

	def cannotTrain(self,argsList):
		pCity = argsList[0]
		eUnit = argsList[1]
		bContinue = argsList[2]
		bTestVisible = argsList[3]
		bIgnoreCost = argsList[4]
		bIgnoreUpgrades = argsList[5]
		ePlayer = pCity.getOwner()
		pPlayer = gc.getPlayer(ePlayer)
##		eUnitClass = gc.getUnitInfo(eUnit).getUnitClassType()
##		eTeam = gc.getTeam(pPlayer.getTeam())

		if pPlayer.getCivics(gc.getInfoTypeForString('CIVICOPTION_CULTURAL_VALUES')) == gc.getInfoTypeForString('CIVIC_CRUSADE'):
			if eUnit in [gc.getInfoTypeForString('UNIT_WORKER'), gc.getInfoTypeForString('UNIT_SETTLER'), gc.getInfoTypeForString('UNIT_WORKBOAT')]:
				return True

		if eUnit == gc.getInfoTypeForString('UNIT_BEAST_OF_AGARES'):
			if pCity.getPopulation() <= 5:
				return True


		elif eUnit == gc.getInfoTypeForString('UNIT_ACHERON'):
			if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_ACHERON):
				return True

		elif eUnit == gc.getInfoTypeForString('UNIT_DUIN'):
			if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_DUIN):
				return True

		if CyGame().getWBMapScript():
			bBlock = sf.cannotTrain(pCity, eUnit, bContinue, bTestVisible, bIgnoreCost, bIgnoreUpgrades)
			if bBlock:
				return True

		return False

	def canConstruct(self,argsList):
		pCity = argsList[0]
		eBuilding = argsList[1]
		bContinue = argsList[2]
		bTestVisible = argsList[3]
		bIgnoreCost = argsList[4]
		return False

	def cannotConstruct(self,argsList):
		pCity = argsList[0]
		eBuilding = argsList[1]
		bContinue = argsList[2]
		bTestVisible = argsList[3]
		bIgnoreCost = argsList[4]
		pPlayer = gc.getPlayer(pCity.getOwner())
##		iBuildingClass = gc.getBuildingInfo(eBuilding).getBuildingClassType()
##		eTeam = gc.getTeam(pPlayer.getTeam())

		if pPlayer.hasTrait(gc.getInfoTypeForString('TRAIT_AGNOSTIC')):
			if eBuilding in [	gc.getInfoTypeForString('BUILDING_TEMPLE_OF_LEAVES'),
							gc.getInfoTypeForString('BUILDING_TEMPLE_OF_KILMORPH'),
							gc.getInfoTypeForString('BUILDING_TEMPLE_OF_THE_EMPYREAN'),
							gc.getInfoTypeForString('BUILDING_TEMPLE_OF_THE_OVERLORDS'),
							gc.getInfoTypeForString('BUILDING_TEMPLE_OF_THE_VEIL'),
							gc.getInfoTypeForString('BUILDING_TEMPLE_OF_THE_ORDER')
							]:
				return True

		if pPlayer.getCivics(gc.getInfoTypeForString('CIVICOPTION_CULTURAL_VALUES')) == gc.getInfoTypeForString('CIVIC_CRUSADE'):
			if eBuilding in [	gc.getInfoTypeForString('BUILDING_ELDER_COUNCIL'),
						gc.getInfoTypeForString('BUILDING_MARKET'),
						gc.getInfoTypeForString('BUILDING_MONUMENT'),
						gc.getInfoTypeForString('BUILDING_MONEYCHANGER'),
						gc.getInfoTypeForString('BUILDING_THEATRE'),
						gc.getInfoTypeForString('BUILDING_AQUEDUCT'),
						gc.getInfoTypeForString('BUILDING_PUBLIC_BATHS'),
						gc.getInfoTypeForString('BUILDING_HERBALIST'),
						gc.getInfoTypeForString('BUILDING_CARNIVAL'),
						gc.getInfoTypeForString('BUILDING_COURTHOUSE'),
						gc.getInfoTypeForString('BUILDING_GAMBLING_HOUSE'),
						gc.getInfoTypeForString('BUILDING_GRANARY'),
						gc.getInfoTypeForString('BUILDING_SMOKEHOUSE'),
						gc.getInfoTypeForString('BUILDING_LIBRARY'),
						gc.getInfoTypeForString('BUILDING_HARBOR'),
						gc.getInfoTypeForString('BUILDING_ALCHEMY_LAB'),
						gc.getInfoTypeForString('BUILDING_BREWERY')
						]:
				return True

		listAltars =[	gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR'),
				gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_ANOINTED'),
				gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_BLESSED'),
				gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_CONSECRATED'),
				gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_DIVINE'),
				gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_EXALTED'),
				gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_FINAL')
				]

		if eBuilding in listAltars:
			if pPlayer.getAlignment() == gc.getInfoTypeForString('ALIGNMENT_EVIL'):
				return True
			for iAltar in listAltars[listAltars.index(eBuilding):]:
				if pPlayer.countNumBuildings(iAltar) > 0:
					return True

		elif eBuilding == gc.getInfoTypeForString('BUILDING_MERCURIAN_GATE'):
			if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_HYBOREM_OR_BASIUM):
				return True
			if pPlayer.getStateReligion() == gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL'):
				return True
			if pCity.isCapital():
				return True

		elif eBuilding == gc.getInfoTypeForString('BUILDING_SHRINE_OF_THE_CHAMPION'):
			iHero = cf.getHero(pPlayer)
			if iHero == -1:
				return True
			if not CyGame().isUnitClassMaxedOut(iHero, 0):
				return True
			if pPlayer.getUnitClassCount(iHero) > 0:
				return True

		elif eBuilding == gc.getInfoTypeForString('BUILDING_SMUGGLERS_PORT'):
			if not pPlayer.isSmugglingRing():
				return True


### Start AI restrictions ###
		if not pPlayer.isHuman():
			if eBuilding == gc.getInfoTypeForString('BUILDING_PROPHECY_OF_RAGNAROK'):
				if pPlayer.getAlignment() != gc.getInfoTypeForString('ALIGNMENT_EVIL'):
					return True

			elif eBuilding == gc.getInfoTypeForString('BUILDING_MERCURIAN_GATE'):
				if pPlayer.getAlignment() == gc.getInfoTypeForString('ALIGNMENT_EVIL'):
					return True
				if pCity.isHolyCity():
					return True
				if pCity.getAltarLevel() > 0:
					return True
### End AI restrictions ###
		return False

	def canCreate(self,argsList):
		pCity = argsList[0]
		eProject = argsList[1]
		bContinue = argsList[2]
		bTestVisible = argsList[3]
		return False

	def cannotCreate(self,argsList):
		pCity = argsList[0]
		eProject = argsList[1]
		bContinue = argsList[2]
		bTestVisible = argsList[3]
		pPlayer = gc.getPlayer(pCity.getOwner())
##		eTeam = gc.getTeam(pPlayer.getTeam())

		if eProject == gc.getInfoTypeForString('PROJECT_PURGE_THE_UNFAITHFUL'):
			if not pPlayer.isHuman():
				return True
			if pPlayer.getStateReligion() == -1:
				return True

		if eProject == gc.getInfoTypeForString('PROJECT_BIRTHRIGHT_REGAINED'):
			if not pPlayer.isFeatAccomplished(FeatTypes.FEAT_GLOBAL_SPELL):
				return True

		if eProject == gc.getInfoTypeForString('PROJECT_STIR_FROM_SLUMBER'):
			if pPlayer.getPlayersKilled() == 0:
				return True

		if eProject == gc.getInfoTypeForString('PROJECT_GLORY_EVERLASTING'):
			if not pPlayer.isHuman():
				if pPlayer.getCivilizationType() != gc.getInfoTypeForString('CIVILIZATION_INFERNALS'):
					return True

		if eProject == gc.getInfoTypeForString('PROJECT_ASCENSION'):
			if pPlayer.getCivilizationType() != gc.getInfoTypeForString('CIVILIZATION_ILLIANS'):
				return True

		if eProject == gc.getInfoTypeForString('PROJECT_SAMHAIN'):
			if not pPlayer.isHuman():
				if pPlayer.getNumCities() <= 3:
					return True

		if eProject == gc.getInfoTypeForString('PROJECT_THE_DRAW'):
			if not pPlayer.isHuman():
				if not pPlayer.isHasTech(gc.getInfoTypeForString('TECH_OMNISCIENCE')):
					return True

		return False

	def canMaintain(self,argsList):
		pCity = argsList[0]
		eProcess = argsList[1]
		bContinue = argsList[2]
		return False

	def cannotMaintain(self,argsList):
		pCity = argsList[0]
		eProcess = argsList[1]
		bContinue = argsList[2]
		return False

	def AI_chooseTech(self,argsList):
		ePlayer = argsList[0]
		bFree = argsList[1]
		pPlayer = gc.getPlayer(ePlayer)

		return TechTypes.NO_TECH

	def AI_chooseProduction(self,argsList):
		pCity = argsList[0]
		ePlayer = pCity.getOwner()
		pPlayer = gc.getPlayer(ePlayer)
		pPlot = pCity.plot()

		## AI catches for buildings and projects that have python-only effects
		if not pPlayer.isHuman():

			iCivType = pPlayer.getCivilizationType()
			if pPlayer.hasTrait(gc.getInfoTypeForString('TRAIT_TOLERANT')):
				iCivType = pCity.getCivilizationType()

			## Barbarians
			if pPlayer.isBarbarian():
				if pCity.canTrain(gc.getInfoTypeForString('UNIT_ACHERON'), True, False):
					pCity.pushOrder(OrderTypes.ORDER_TRAIN, gc.getInfoTypeForString('UNIT_ACHERON'), -1, False, False, False, False)
					return 1

			## Illians - make sure we build our best projects
			if iCivType == gc.getInfoTypeForString('CIVILIZATION_ILLIANS'):
				if pCity.getPopulation() > 3:
					if pCity.canConstruct(gc.getInfoTypeForString('BUILDING_TEMPLE_OF_THE_HAND'), True, False, False):
						iBadTileCount = 0
						for iiX in range(pCity.getX()-1, pCity.getX()+2, 1):
							for iiY in range(pCity.getY()-1, pCity.getY()+2, 1):
								pNearbyPlot = CyMap().plot(iiX,iiY)
								if (not pNearbyPlot.isWater()):
									if (pNearbyPlot.getYield(YieldTypes.YIELD_FOOD) < 2):
										iBadTileCount += 1
						if (iBadTileCount >= 4):
							pCity.pushOrder(OrderTypes.ORDER_CONSTRUCT,gc.getInfoTypeForString('BUILDING_TEMPLE_OF_THE_HAND'),-1, False, False, False, False)
							return 1

				if pCity.findYieldRateRank(YieldTypes.YIELD_PRODUCTION) < 3:
					if pCity.canCreate(gc.getInfoTypeForString('PROJECT_THE_WHITE_HAND'), True, True):
						pCity.pushOrder(OrderTypes.ORDER_CREATE,gc.getInfoTypeForString('PROJECT_THE_WHITE_HAND'),-1, False, False, False, False)
						return 1
					if pCity.canCreate(gc.getInfoTypeForString('PROJECT_ASCENSION'), True, True):
						pCity.pushOrder(OrderTypes.ORDER_CREATE,gc.getInfoTypeForString('PROJECT_ASCENSION'),-1, False, False, False, False)
						return 1
			## Clan should build Warrens
			elif iCivType == gc.getInfoTypeForString('CIVILIZATION_CLAN_OF_EMBERS'):
				if (pCity.getCultureLevel() > 1) and (pCity.getPopulation() > 3):
					if pCity.canConstruct(gc.getInfoTypeForString('BUILDING_WARRENS'), True, False, False):
						pCity.pushOrder(OrderTypes.ORDER_CONSTRUCT,gc.getInfoTypeForString('BUILDING_WARRENS'),-1, False, False, False, False)
						return 1
			## Amurites should build Cave of Ancestors
			elif iCivType == gc.getInfoTypeForString('CIVILIZATION_AMURITES'):
				if (pCity.getNumBuilding(gc.getInfoTypeForString('BUILDING_MAGE_GUILD')) > 0):
					if pCity.canConstruct(gc.getInfoTypeForString('BUILDING_CAVE_OF_ANCESTORS'), True, False, False):
						pCity.pushOrder(OrderTypes.ORDER_CONSTRUCT,gc.getInfoTypeForString('BUILDING_CAVE_OF_ANCESTORS'),-1, False, False, False, False)
						return 1
			## Demons should build Demon Altars
			#if gc.getCivilizationInfo(pPlayer.getCivilizationType()).getDefaultRace == gc.getInfoTypeForString('PROMOTION_DEMON'):
			elif pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_INFERNAL'):
				if pCity.canConstruct(gc.getInfoTypeForString('BUILDING_DEMONS_ALTAR'), True, False, False):
						pCity.pushOrder(OrderTypes.ORDER_CONSTRUCT,gc.getInfoTypeForString('BUILDING_DEMONS_ALTAR'),-1, False, False, False, False)
						return 1

			if pCity.canTrain(gc.getInfoTypeForString('UNIT_HAWK'), True, False):
				if pPlot.countNumAirUnits(pPlayer.getTeam()) == 0:
					pCity.pushOrder(OrderTypes.ORDER_TRAIN, gc.getInfoTypeForString('UNIT_HAWK'), -1, False, False, False, False)
					return 1

		return False

	def AI_unitUpdate(self,argsList):
		pUnit = argsList[0]
		pPlot = pUnit.plot()
		iUnitType = pUnit.getUnitType()
		iPlayer = pUnit.getOwner()
		pPlayer = gc.getPlayer(iPlayer)

		if pPlayer.isBarbarian():
			if iUnitType == gc.getInfoTypeForString('UNIT_GIANT_SPIDER'):
				iX = pUnit.getX()
				iY = pUnit.getY()
				for iDirection in range(DirectionTypes.NUM_DIRECTION_TYPES):
					pLoopPlot= plotDirection(iX, iY, DirectionTypes(iDirection))
					if not pLoopPlot.isNone():
						for i in range(pLoopPlot.getNumUnits()):
							if pLoopPlot.getUnit(i).getOwner() != iPlayer:
								return 0
				pUnit.getGroup().pushMission(MissionTypes.MISSION_SKIP, 0, 0, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
				return 1

		if iUnitType == gc.getInfoTypeForString('UNIT_ACHERON'):
			if pPlot.isVisibleEnemyUnit(iPlayer):
				pUnit.cast(gc.getInfoTypeForString('SPELL_BREATH_FIRE'))

		# iImprovement = pPlot.getImprovementType()
		# if iImprovement != -1:
			# if (iImprovement == gc.getInfoTypeForString('IMPROVEMENT_BARROW') or iImprovement == gc.getInfoTypeForString('IMPROVEMENT_RUINS') or iImprovement == gc.getInfoTypeForString('IMPROVEMENT_HELLFIRE')):
				# if not pUnit.isAnimal():
					# if pPlot.getNumUnits() - pPlot.getNumAnimalUnits() == 1:
						# pUnit.getGroup().pushMission(MissionTypes.MISSION_SKIP, 0, 0, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
						# return 1
			# if (iImprovement == gc.getInfoTypeForString('IMPROVEMENT_BEAR_DEN') or iImprovement == gc.getInfoTypeForString('IMPROVEMENT_LION_DEN')):
				# if pUnit.isAnimal():
					# if pPlot.getNumAnimalUnits() == 1:
						# pUnit.getGroup().pushMission(MissionTypes.MISSION_SKIP, 0, 0, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
						# return 1
			# if iImprovement == gc.getInfoTypeForString('IMPROVEMENT_GOBLIN_FORT'):
				# if pUnit.getUnitCombatType() == gc.getInfoTypeForString('UNITCOMBAT_ARCHER'):
					# pUnit.getGroup().pushMission(MissionTypes.MISSION_SKIP, 0, 0, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
					# return 1
				# if not pUnit.isAnimal():
					# if pPlot.getNumUnits() - pPlot.getNumAnimalUnits() <= 2:
						# pUnit.getGroup().pushMission(MissionTypes.MISSION_SKIP, 0, 0, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
						# return 1

		return False

	def AI_doWar(self,argsList):
		eTeam = argsList[0]
		return False

	def AI_doDiplo(self,argsList):
		ePlayer = argsList[0]
		return False

	def calculateScore(self,argsList):
		ePlayer = argsList[0]
		bFinal = argsList[1]
		bVictory = argsList[2]

		iPopulationScore = CvUtil.getScoreComponent(gc.getPlayer(ePlayer).getPopScore(), CyGame().getInitPopulation(), CyGame().getMaxPopulation(), gc.getDefineINT("SCORE_POPULATION_FACTOR"), True, bFinal, bVictory)
		iLandScore = CvUtil.getScoreComponent(gc.getPlayer(ePlayer).getLandScore(), CyGame().getInitLand(), CyGame().getMaxLand(), gc.getDefineINT("SCORE_LAND_FACTOR"), True, bFinal, bVictory)
		iTechScore = CvUtil.getScoreComponent(gc.getPlayer(ePlayer).getTechScore(), CyGame().getInitTech(), CyGame().getMaxTech(), gc.getDefineINT("SCORE_TECH_FACTOR"), True, bFinal, bVictory)
		iWondersScore = CvUtil.getScoreComponent(gc.getPlayer(ePlayer).getWondersScore(), CyGame().getInitWonders(), CyGame().getMaxWonders(), gc.getDefineINT("SCORE_WONDER_FACTOR"), False, bFinal, bVictory)
		return int(iPopulationScore + iLandScore + iWondersScore + iTechScore)

	def doHolyCity(self):
		return False

	def doHolyCityTech(self,argsList):
		eTeam = argsList[0]
		ePlayer = argsList[1]
		eTech = argsList[2]
		bFirst = argsList[3]
		return False

	def doGold(self,argsList):
		ePlayer = argsList[0]
		return False

	def doResearch(self,argsList):
		ePlayer = argsList[0]
		return False

	def doGoody(self,argsList):
		ePlayer = argsList[0]
		pPlot = argsList[1]
		pUnit = argsList[2]
		return False

	def doGrowth(self,argsList):
		pCity = argsList[0]
		return False

	def doProduction(self,argsList):
		pCity = argsList[0]
		return False

	def doCulture(self,argsList):
		pCity = argsList[0]
		pPlayer = gc.getPlayer(pCity.getOwner())
		if pPlayer.isBarbarian():
			if pCity.getNumRealBuilding(gc.getInfoTypeForString('BUILDING_THE_DRAGONS_HORDE')) == 0:
				return 1
		return False

	def doPlotCulture(self,argsList):
		pCity = argsList[0]
		bUpdate = argsList[1]
		ePlayer = argsList[2]
		iCultureRate = argsList[3]
		return False

	def doReligion(self,argsList):
		pCity = argsList[0]
		return False

	def cannotSpreadReligion(self,argsList):
		iOwner, iUnitID, iReligion, iX, iY = argsList[0]
		return False

	def doGreatPeople(self,argsList):
		pCity = argsList[0]
		return False

	def doMeltdown(self,argsList):
		pCity = argsList[0]
		return False

	def doReviveActivePlayer(self,argsList):
		"allows you to perform an action after an AIAutoPlay"
		iPlayer = argsList[0]
		return False

	def doPillageGold(self, argsList):
		"controls the gold result of pillaging"
		pPlot = argsList[0]
		pUnit = argsList[1]
		iPillageGold = CyGame().getSorenRandNum(gc.getImprovementInfo(pPlot.getImprovementType()).getPillageGold(), "Pillage Gold 1")
		iPillageGold += CyGame().getSorenRandNum(gc.getImprovementInfo(pPlot.getImprovementType()).getPillageGold(), "Pillage Gold 2")
		iPillageGold += (pUnit.getPillageChange() * iPillageGold) / 100
		return iPillageGold

	def doCityCaptureGold(self, argsList):
		"controls the gold result of capturing a city"
		pOldCity = argsList[0]
		iCaptureGold = gc.getDefineINT("BASE_CAPTURE_GOLD")
		iCaptureGold += (pOldCity.getPopulation() * gc.getDefineINT("CAPTURE_GOLD_PER_POPULATION"))
		iCaptureGold += CyGame().getSorenRandNum(gc.getDefineINT("CAPTURE_GOLD_RAND1"), "Capture Gold 1")
		iCaptureGold += CyGame().getSorenRandNum(gc.getDefineINT("CAPTURE_GOLD_RAND2"), "Capture Gold 2")
		if gc.getDefineINT("CAPTURE_GOLD_MAX_TURNS") > 0:
			iCaptureGold *= cyIntRange((CyGame().getGameTurn() - pOldCity.getGameTurnAcquired()), 0, gc.getDefineINT("CAPTURE_GOLD_MAX_TURNS"))
			iCaptureGold /= gc.getDefineINT("CAPTURE_GOLD_MAX_TURNS")
		return iCaptureGold

	def citiesDestroyFeatures(self,argsList):
		iX, iY= argsList
		return True

	def canFoundCitiesOnWater(self,argsList):
		iX, iY= argsList
		return False

	def doCombat(self,argsList):
		pSelectionGroup, pDestPlot = argsList
		return False

	def getConscriptUnitType(self, argsList):
		iPlayer = argsList[0]
		iConscriptUnitType = -1 #return this with the value of the UNIT TYPE you want to be conscripted, -1 uses default system
		return iConscriptUnitType

	def getCityFoundValue(self, argsList):
		iPlayer, iPlotX, iPlotY = argsList
		iFoundValue = -1 # Any value besides -1 will be used
		return iFoundValue

	def canPickPlot(self, argsList):
		pPlot = argsList[0]
		return True

	def getUnitCostMod(self, argsList):
		iPlayer, iUnit = argsList
		iCostMod = -1 # Any value > 0 will be used
		return iCostMod

	def getBuildingCostMod(self, argsList):
		iPlayer, iCityID, iBuilding = argsList
		iCostMod = -1 # Any value > 0 will be used
		pPlayer = gc.getPlayer(iPlayer)
		pCity = pPlayer.getCity(iCityID)
		if iBuilding == gc.getInfoTypeForString('BUILDING_GAMBLING_HOUSE'):
			if pPlayer.isGamblingRing():
				iCostMod = 25
		return iCostMod

	def canUpgradeAnywhere(self, argsList):
		pUnit = argsList
		bCanUpgradeAnywhere = 0
		return bCanUpgradeAnywhere

	def getWidgetHelp(self, argsList):
		eWidgetType, iData1, iData2, bOption = argsList
## Religion Screen ##
		if eWidgetType == WidgetTypes.WIDGET_HELP_RELIGION:
			if iData1 == -1:
				return CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ())
## Platy WorldBuilder ##
		elif eWidgetType == WidgetTypes.WIDGET_PYTHON:
			if iData1 == 1027:
				return CyTranslator().getText("TXT_KEY_WB_PLOT_DATA",())
			elif iData1 == 1028:
				return gc.getGameOptionInfo(iData2).getHelp()
			elif iData1 == 1029:
				if iData2 == 0:
					sText = CyTranslator().getText("TXT_KEY_WB_PYTHON", ())
					sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onFirstContact"
					sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onChangeWar"
					sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onVassalState"
					sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onCityAcquired"
					sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onCityBuilt"
					sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onCultureExpansion"
					sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onGoldenAge"
					sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onEndGoldenAge"
					sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onGreatPersonBorn"
					sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onPlayerChangeStateReligion"
					sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onReligionFounded"
					sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onReligionSpread"
					sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onReligionRemove"
					sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onCorporationFounded"
					sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onCorporationSpread"
					sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onCorporationRemove"
					sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onUnitCreated"
					sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onUnitLost"
					sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onUnitPromoted"
					sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onBuildingBuilt"
					sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onProjectBuilt"
					sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onTechAcquired"
					sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onImprovementBuilt"
					sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onImprovementDestroyed"
					sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onRouteBuilt"
					sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onPlotRevealed"
					return sText
				elif iData2 == 1:
					return CyTranslator().getText("TXT_KEY_WB_PLAYER_DATA",())
				elif iData2 == 2:
					return CyTranslator().getText("TXT_KEY_WB_TEAM_DATA",())
				elif iData2 == 3:
					return CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_TECH",())
				elif iData2 == 4:
					return CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_PROJECT",())
				elif iData2 == 5:
					return CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_UNIT", ()) + " + " + CyTranslator().getText("TXT_KEY_CONCEPT_CITIES", ())
				elif iData2 == 6:
					return CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_PROMOTION",())
				elif iData2 == 7:
					return CyTranslator().getText("TXT_KEY_WB_CITY_DATA2",())
				elif iData2 == 8:
					return CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_BUILDING",())
				elif iData2 == 9:
					return CvModName.getName() + '\nVersion: ' + CvModName.getVersion() + "\nPlaty Builder\nVersion: 4.17b"
				elif iData2 == 10:
					return CyTranslator().getText("TXT_KEY_CONCEPT_EVENTS",())
				elif iData2 == 11:
					return CyTranslator().getText("TXT_KEY_WB_RIVER_PLACEMENT",())
				elif iData2 == 12:
					return CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_IMPROVEMENT",())
				elif iData2 == 13:
					return CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_BONUS",())
				elif iData2 == 14:
					return CyTranslator().getText("TXT_KEY_WB_PLOT_TYPE",())
				elif iData2 == 15:
					return CyTranslator().getText("TXT_KEY_CONCEPT_TERRAIN",())
				elif iData2 == 16:
					return CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_ROUTE",())
				elif iData2 == 17:
					return CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_FEATURE",())
				elif iData2 == 18:
					return CyTranslator().getText("TXT_KEY_MISSION_BUILD_CITY",())
				elif iData2 == 19:
					return CyTranslator().getText("TXT_KEY_WB_ADD_BUILDINGS",())
				elif iData2 == 20:
					return CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_RELIGION",())
				elif iData2 == 21:
					return CyTranslator().getText("TXT_KEY_CONCEPT_CORPORATIONS",())
				elif iData2 == 22:
					return CyTranslator().getText("TXT_KEY_ESPIONAGE_CULTURE",())
				elif iData2 == 23:
					return CyTranslator().getText("TXT_KEY_PITBOSS_GAME_OPTIONS",())
				elif iData2 == 24:
					return CyTranslator().getText("TXT_KEY_WB_SENSIBILITY",())
				elif iData2 == 27:
					return CyTranslator().getText("TXT_KEY_WB_ADD_UNITS",())
				elif iData2 == 28:
					return CyTranslator().getText("TXT_KEY_WB_TERRITORY",())
				elif iData2 == 29:
					return CyTranslator().getText("TXT_KEY_WB_ERASE_ALL_PLOTS",())
				elif iData2 == 30:
					return CyTranslator().getText("TXT_KEY_WB_REPEATABLE",())
				elif iData2 == 31:
					return CyTranslator().getText("TXT_KEY_PEDIA_HIDE_INACTIVE", ())
				elif iData2 == 32:
					return CyTranslator().getText("TXT_KEY_WB_STARTING_PLOT", ())
				elif iData2 == 33:
					return CyTranslator().getText("TXT_KEY_INFO_SCREEN", ())
				elif iData2 == 34:
					return CyTranslator().getText("TXT_KEY_CONCEPT_TRADE", ())
#Magister Start
				elif iData2 == 35:
					return CyTranslator().getText("TXT_KEY_WB_REAL",())
#Magister Stop
			elif iData1 > 1029 and iData1 < 1040:
				if iData1 %2:
					return "-"
				return "+"
			elif iData1 == 1041:
				return CyTranslator().getText("TXT_KEY_WB_KILL",())
			elif iData1 == 1042:
				return CyTranslator().getText("TXT_KEY_MISSION_SKIP",())
			elif iData1 == 1043:
				if iData2 == 0:
					return CyTranslator().getText("TXT_KEY_WB_DONE",())
				elif iData2 == 1:
					return CyTranslator().getText("TXT_KEY_WB_FORTIFY",())
				elif iData2 == 2:
					return CyTranslator().getText("TXT_KEY_WB_WAIT",())
			elif iData1 == 6782:
				return CyGameTextMgr().parseCorporationInfo(iData2, False)
			elif iData1 == 6785:
				return CyGameTextMgr().getProjectHelp(iData2, False, CyCity())
			elif iData1 == 6787:
				return gc.getProcessInfo(iData2).getDescription()
			elif iData1 == 6788:
				if iData2 == -1:
					return CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ())
				return gc.getRouteInfo(iData2).getDescription()
## City Hover Text ##
			elif iData1 > 7199 and iData1 < 7300:
				iPlayer = iData1 - 7200
				pPlayer = gc.getPlayer(iPlayer)
				pCity = pPlayer.getCity(iData2)
				if CyGame().GetWorldBuilderMode():
					sText = "<font=3>"
					if pCity.isCapital():
						sText += CyTranslator().getText("[ICON_STAR]", ())
					elif pCity.isGovernmentCenter():
						sText += CyTranslator().getText("[ICON_SILVER_STAR]", ())
					sText += u"%s: %d<font=2>" %(pCity.getName(), pCity.getPopulation())
					sTemp = ""
					if pCity.isConnectedToCapital(iPlayer):
						sTemp += CyTranslator().getText("[ICON_TRADE]", ())
					for i in xrange(gc.getNumReligionInfos()):
						if pCity.isHolyCityByType(i):
							sTemp += u"%c" %(gc.getReligionInfo(i).getHolyCityChar())
						elif pCity.isHasReligion(i):
							sTemp += u"%c" %(gc.getReligionInfo(i).getChar())

					for i in xrange(gc.getNumCorporationInfos()):
						if pCity.isHeadquartersByType(i):
							sTemp += u"%c" %(gc.getCorporationInfo(i).getHeadquarterChar())
						elif pCity.isHasCorporation(i):
							sTemp += u"%c" %(gc.getCorporationInfo(i).getChar())
					if len(sTemp) > 0:
						sText += "\n" + sTemp

					iMaxDefense = pCity.getTotalDefense(False)
					if iMaxDefense > 0:
						sText += u"\n%s: " %(CyTranslator().getText("[ICON_DEFENSE]", ()))
						iCurrent = pCity.getDefenseModifier(False)
						if iCurrent != iMaxDefense:
							sText += u"%d/" %(iCurrent)
						sText += u"%d%%" %(iMaxDefense)

					sText += u"\n%s: %d/%d" %(CyTranslator().getText("[ICON_FOOD]", ()), pCity.getFood(), pCity.growthThreshold())
					iFoodGrowth = pCity.foodDifference(True)
					if iFoodGrowth != 0:
						sText += u" %+d" %(iFoodGrowth)

					if pCity.isProduction():
						sText += u"\n%s:" %(CyTranslator().getText("[ICON_PRODUCTION]", ()))
						if not pCity.isProductionProcess():
							sText += u" %d/%d" %(pCity.getProduction(), pCity.getProductionNeeded())
							iProduction = pCity.getCurrentProductionDifference(False, True)
							if iProduction != 0:
								sText += u" %+d" %(iProduction)
						sText += u" (%s)" %(pCity.getProductionName())

					iGPRate = pCity.getGreatPeopleRate()
					iProgress = pCity.getGreatPeopleProgress()
					if iGPRate > 0 or iProgress > 0:
						sText += u"\n%s: %d/%d %+d" %(CyTranslator().getText("[ICON_GREATPEOPLE]", ()), iProgress, pPlayer.greatPeopleThreshold(False), iGPRate)

					sText += u"\n%s: %d/%d (%s)" %(CyTranslator().getText("[ICON_CULTURE]", ()), pCity.getCulture(iPlayer), pCity.getCultureThreshold(), gc.getCultureLevelInfo(pCity.getCultureLevel()).getDescription())

					lTemp = []
					for i in xrange(CommerceTypes.NUM_COMMERCE_TYPES):
						iAmount = pCity.getCommerceRateTimes100(i)
						if iAmount <= 0: continue
						sTemp = u"%d.%02d%c" %(pCity.getCommerceRate(i), pCity.getCommerceRateTimes100(i)%100, gc.getCommerceInfo(i).getChar())
						lTemp.append(sTemp)
					if len(lTemp) > 0:
						sText += "\n"
						for i in xrange(len(lTemp)):
							sText += lTemp[i]
							if i < len(lTemp) - 1:
								sText += ", "

					iMaintenance = pCity.getMaintenanceTimes100()
					if iMaintenance != 0:
						sText += "\n" + CyTranslator().getText("[COLOR_WARNING_TEXT]", ()) + CyTranslator().getText("INTERFACE_CITY_MAINTENANCE", ()) + " </color>"
						sText += u"-%d.%02d%c" %(iMaintenance/100, iMaintenance%100, gc.getCommerceInfo(CommerceTypes.COMMERCE_GOLD).getChar())

#Magister Start
					iRevIndex = pCity.getRevolutionIndex()
					if iRevIndex != 0:
						sText += "\n" + CyTranslator().getText("TXT_KEY_WB_REV_INDEX", (iRevIndex,))

					sText += "\n" + "X: " + str(pCity.getX()) + ", Y: " + str(pCity.getY())
					sText += "\n" + CyTranslator().getText("TXT_KEY_WB_AREA_ID", ()) + ": " + str(pCity.plot().getArea())
#Magister Stop

					lBuildings = []
					lWonders = []
					for i in xrange(gc.getNumBuildingInfos()):
						if pCity.isHasBuilding(i):
							Info = gc.getBuildingInfo(i)
							if isLimitedWonderClass(Info.getBuildingClassType()):
								lWonders.append(Info.getDescription())
							else:
								lBuildings.append(Info.getDescription())
					if len(lBuildings) > 0:
						lBuildings.sort()
						sText += "\n" + CyTranslator().getText("[COLOR_BUILDING_TEXT]", ()) + CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_BUILDING", ()) + ": </color>"
						for i in xrange(len(lBuildings)):
							sText += lBuildings[i]
							if i < len(lBuildings) - 1:
								sText += ", "
					if len(lWonders) > 0:
						lWonders.sort()
						sText += "\n" + CyTranslator().getText("[COLOR_SELECTED_TEXT]", ()) + CyTranslator().getText("TXT_KEY_CONCEPT_WONDERS", ()) + ": </color>"
						for i in xrange(len(lWonders)):
							sText += lWonders[i]
							if i < len(lWonders) - 1:
								sText += ", "
					sText += "</font>"
					return sText
## Religion Widget Text##
			elif iData1 == 7869:
				return CyGameTextMgr().parseReligionInfo(iData2, False)
## Building Widget Text##
			elif iData1 == 7870:
				return CyGameTextMgr().getBuildingHelp(iData2, False, False, False, None)
## Tech Widget Text##
			elif iData1 == 7871:
				if iData2 == -1:
					return CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ())
				return CyGameTextMgr().getTechHelp(iData2, False, False, False, False, -1)
## Civilization Widget Text##
			elif iData1 == 7872:
				iCiv = iData2 % 10000
				return CyGameTextMgr().parseCivInfos(iCiv, False)
## Promotion Widget Text##
			elif iData1 == 7873:
				return CyGameTextMgr().getPromotionHelp(iData2, False)
## Feature Widget Text##
			elif iData1 == 7874:
				if iData2 == -1:
					return CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ())
				iFeature = iData2 % 10000
				return CyGameTextMgr().getFeatureHelp(iFeature, False)
## Terrain Widget Text##
			elif iData1 == 7875:
				return CyGameTextMgr().getTerrainHelp(iData2, False)
## Leader Widget Text##
			elif iData1 == 7876:
				iLeader = iData2 % 10000
				return CyGameTextMgr().parseLeaderTraits(iLeader, -1, False, False)
## Improvement Widget Text##
			elif iData1 == 7877:
				if iData2 == -1:
					return CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ())
				return CyGameTextMgr().getImprovementHelp(iData2, False)
## Bonus Widget Text##
			elif iData1 == 7878:
				if iData2 == -1:
					return CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ())
				return CyGameTextMgr().getBonusHelp(iData2, False)
## Specialist Widget Text##
			elif iData1 == 7879:
				return CyGameTextMgr().getSpecialistHelp(iData2, False)
## Yield Text##
			elif iData1 == 7880:
				return gc.getYieldInfo(iData2).getDescription()
## Commerce Text##
			elif iData1 == 7881:
				return gc.getCommerceInfo(iData2).getDescription()
## Build Text##
			elif iData1 == 7882:
				return gc.getBuildInfo(iData2).getDescription()
## Corporation Screen ##
			elif iData1 == 8201:
				return CyGameTextMgr().parseCorporationInfo(iData2, False)
## Military Screen ##
			elif iData1 == 8202:
				if iData2 == -1:
					return CyTranslator().getText("TXT_KEY_PEDIA_ALL_UNITS", ())
				return CyGameTextMgr().getUnitHelp(iData2, False, False, False, None)
			elif iData1 > 8299 and iData1 < 8400:
				iPlayer = iData1 - 8300
				pUnit = gc.getPlayer(iPlayer).getUnit(iData2)
				if pUnit != -1:
					sText = CyGameTextMgr().getSpecificUnitHelp(pUnit, True, False)
					if CyGame().GetWorldBuilderMode():
#Magister Start
						i = pUnit.getScenarioCounter()
						if -1 < i < gc.getNumUnitInfos():
							if i != pUnit.getUnitType():
								sText += "\n" + CyTranslator().getText("TXT_KEY_WB_SCENARIO_COUNTER_UNIT", ()) + ": " + gc.getUnitInfo(i).getDescription()

						if pUnit.isHasCasted():
							sText += "\n" + CyTranslator().getText("TXT_KEY_UNIT_HAS_CASTED", ())

						i = pUnit.getSummoner()
						if i > 0:
							pPlayer = gc.getPlayer(pUnit.getOwner())
							pSummoner = pPlayer.getUnit(i)
							if not pSummoner.isNone():
								sText += "\n" + CyTranslator().getText("TXT_KEY_WB_SUMMONER", ()) + ": " + pSummoner.getName()
								sText += "\n" + CyTranslator().getText("TXT_KEY_WB_SUMMONER", ()) + " ID: " + str(i)

						if pUnit.isPermanentSummon():
							sText += "\n" + CyTranslator().getText("TXT_KEY_WB_IS_PERMANENT_SUMMON", ())

						i = pUnit.getDuration()
						if i > 0:
							sText += "\n" + CyTranslator().getText("TXT_KEY_WB_DURATION", ()) + ": " + str(i)

						i = pUnit.getImmobileTimer()
						if i > 0:
							sText += "\n" + CyTranslator().getText("TXT_KEY_WB_IMMOBILE_TIMER", ()) + ": " + str(i)

						i = pUnit.getFortifyTurns()
						if i > 0:
							sText += "\n" + CyTranslator().getText("TXT_KEY_WB_FORTIFY_TURNS", ()) + ": " + str(i)
#Magister Stop
						sText += "\n" + CyTranslator().getText("TXT_KEY_WB_UNIT", ()) + " ID: " + str(iData2)
						sText += "\n" + CyTranslator().getText("TXT_KEY_WB_GROUP", ()) + " ID: " + str(pUnit.getGroupID())
						sText += "\n" + "X: " + str(pUnit.getX()) + ", Y: " + str(pUnit.getY())
						sText += "\n" + CyTranslator().getText("TXT_KEY_WB_AREA_ID", ()) + ": " + str(pUnit.plot().getArea())
					return sText
## Civics Screen ##
			elif iData1 == 8205 or iData1 == 8206:
				sText = CyGameTextMgr().parseCivicInfo(iData2, False, True, False)
				if gc.getCivicInfo(iData2).getUpkeep() > -1:
					sText += "\n" + gc.getUpkeepInfo(gc.getCivicInfo(iData2).getUpkeep()).getDescription()
				else:
					sText += "\n" + CyTranslator().getText("TXT_KEY_CIVICS_SCREEN_NO_UPKEEP", ())
				return sText
#Magister Start
			elif iData1 == 9000:
				return CyGameTextMgr().parseTraits(iData2, CivilizationTypes.NO_CIVILIZATION, False )
			elif iData1 == 9001:
				return CyGameTextMgr().getSpellHelp(iData2, False)
			elif iData1 == 9002:
				return CyTranslator().getText("TXT_KEY_WB_TOGGLE",()) + CyTranslator().getText("TXT_KEY_WB_HAS_CAST",())
			elif iData1 == 9003:
				if iData2 == 0:
					return CyTranslator().getText("TXT_KEY_WB_CAN_CAST",())
				elif iData2 == 1:
					return CyTranslator().getText("TXT_KEY_WB_HAS_CAST",())
#Magister Stop

## Ultrapack ##
		return u""

	def getUpgradePriceOverride(self, argsList):
		iPlayer, iUnitID, iUnitTypeUpgrade = argsList
		return -1	# Any value 0 or above will be used

	def getExperienceNeeded(self, argsList):
		# use this function to set how much experience a unit needs
		iLevel, iOwner = argsList
		# regular epic game experience
		iExperienceNeeded = iLevel * iLevel + 1
		iModifier = gc.getPlayer(iOwner).getLevelExperienceModifier()
		if 0 != iModifier:
			iExperienceNeeded += (iExperienceNeeded * iModifier + 99) / 100  # ROUND UP
		return iExperienceNeeded

##--------	Unofficial Bug Fix: Added by Denev 2009/12/31
	def applyBuildEffects(self, argsList):
		pUnit, pCity = argsList
		if pCity.getNumBuilding(gc.getInfoTypeForString('BUILDING_CHANCEL_OF_GUARDIANS')) > 0:
			if not pUnit.noDefensiveBonus() and pUnit.baseCombatStrDefense() > 0:
				if CyGame().getSorenRandNum(100, "Chancel of Guardians") < 20:
					pUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_DEFENSIVE'), True)

		if pCity.getNumBuilding(gc.getInfoTypeForString('BUILDING_CAVE_OF_ANCESTORS')) > 0:
			if pUnit.getUnitCombatType() == gc.getInfoTypeForString('UNITCOMBAT_ADEPT'):
				iNumManaKinds = 0
				for iBonus in range(gc.getNumBonusInfos()):
					if pCity.hasBonus(iBonus):
						if gc.getBonusInfo(iBonus).getBonusClassType() == gc.getInfoTypeForString('BONUSCLASS_MANA'):
							iNumManaKinds += 1
				if iNumManaKinds > 0:
					pUnit.changeExperience(iNumManaKinds, -1, False, False, False)

		if pCity.getNumBuilding(gc.getInfoTypeForString('BUILDING_ASYLUM')) > 0:
			if pUnit.isAlive():
				if not isWorldUnitClass(pUnit.getUnitClassType()):
					if CyGame().getSorenRandNum(100, "Asylum") < 10:
						pUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_CRAZED'), True)
						pUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_ENRAGED'), True)

		if pUnit.getRace() == gc.getInfoTypeForString('PROMOTION_GOLEM'):
			if pCity.getNumBuilding(gc.getInfoTypeForString('BUILDING_BLASTING_WORKSHOP')) > 0:
				pUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_FIRE2'), True)
			if pCity.getNumBuilding(gc.getInfoTypeForString('BUILDING_PALLENS_ENGINE')) > 0:
				pUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_PERFECT_SIGHT'), True)
			if pCity.getNumBuilding(gc.getInfoTypeForString('BUILDING_ADULARIA_CHAMBER')) > 0:
				pUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_HIDDEN'), True)

		elif pUnit.getRace() == gc.getInfoTypeForString('PROMOTION_DWARF'):
			if pCity.getNumBuilding(gc.getInfoTypeForString('BUILDING_BREWERY')) > 0:
				pUnit.changeExperience(2, -1, False, False, False)

		elif pUnit.getRace() == gc.getInfoTypeForString('PROMOTION_DEMON'):
			if pCity.getNumBuilding(gc.getInfoTypeForString('BUILDING_DEMONS_ALTAR')) > 0:
				pUnit.changeExperience(2, -1, False, False, False)
##--------	Unofficial Bug Fix: End Add


# Return 1 if a Mission was pushed
	def AI_MageTurn(self, argsList):
		pUnit = argsList[0]
		pPlot = pUnit.plot()
		iPlayer = pUnit.getOwner()
		pPlayer = gc.getPlayer(iPlayer)
		eTeam = gc.getTeam(pPlayer.getTeam())
		iCiv = pPlayer.getCivilizationType()
		iX = pUnit.getX()
		iY = pUnit.getY()

		if pUnit.getUnitAIType() == gc.getInfoTypeForString('UNITAI_TERRAFORMER'):

#-----------------------------------
#TERRAFORMING
#
#SETTING FLAGS
#
#-----------------------------------

			searchdistance=3

#-----------------------------------
#SETTING FLAGS
#
#INIT
#CIV SPECIFIC
#UNIT SPECIFIC
#-----------------------------------

#INIT
			iIllians = gc.getInfoTypeForString('CIVILIZATION_ILLIANS')
			iInfernal = gc.getInfoTypeForString('CIVILIZATION_INFERNAL')
			iDoviello = gc.getInfoTypeForString('CIVILIZATION_DOVIELLO')
			iLjosalfar = gc.getInfoTypeForString('CIVILIZATION_LJOSALFAR')
			iSvartalfar = gc.getInfoTypeForString('CIVILIZATION_SVARTALFAR')

			iFoL = gc.getInfoTypeForString('RELIGION_FELLOWSHIP_OF_LEAVES')

			iLife1 = gc.getInfoTypeForString('PROMOTION_LIFE1')
			iNature2 = gc.getInfoTypeForString('PROMOTION_NATURE2')
			iNature3 = gc.getInfoTypeForString('PROMOTION_NATURE3')
			iSun1 = gc.getInfoTypeForString('PROMOTION_SUN1')
			iWater1 = gc.getInfoTypeForString('PROMOTION_WATER1')

			iSmoke = gc.getInfoTypeForString('IMPROVEMENT_SMOKE')
			iFlood = gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS')
			iDesert = gc.getInfoTypeForString('TERRAIN_DESERT')
			iMarsh = gc.getInfoTypeForString('TERRAIN_MARSH')
			iGrass = gc.getInfoTypeForString('TERRAIN_GRASS')
			iPlains = gc.getInfoTypeForString('TERRAIN_PLAINS')
			iSnow = gc.getInfoTypeForString('TERRAIN_SNOW')
			iTundra = gc.getInfoTypeForString('TERRAIN_TUNDRA')

			lHellTerrains = [	gc.getInfoTypeForString('TERRAIN_BROKEN_LANDS'),
						gc.getInfoTypeForString('TERRAIN_BURNING_SANDS'),
						gc.getInfoTypeForString('TERRAIN_FIELDS_OF_PERDITION'),
						gc.getInfoTypeForString('TERRAIN_SHALLOWS')
						]

			lBloomableTerrains = [	iGrass, gc.getInfoTypeForString('TERRAIN_PLAINS'),
						gc.getInfoTypeForString('TERRAIN_TUNDRA'),
						gc.getInfoTypeForString('TERRAIN_MARSH')
						]

			iSpellSpring = gc.getInfoTypeForString('SPELL_SPRING')
			iSpellVitalize = gc.getInfoTypeForString('SPELL_VITALIZE')
			iSpellScorch = gc.getInfoTypeForString('SPELL_SCORCH')
			iSpellSanctify = gc.getInfoTypeForString('SPELL_SANCTIFY')
			iSpellBloom = gc.getInfoTypeForString('SPELL_BLOOM')

			smokeb = False #terraformer tries to put out smoke
			desertb = False #terraformer tries to spring deserts
			plainsb = False #terraformer tries to improve plains
			snowb = False #terraformer tries to scorch snow to tundra
			tundrab = False #terraformer tries to scorch tundra to plains
			marshb = False #terraformer tries to scorch marsh to grassland
			hellterrb = False #terraformer tries to remove hell terrain
			treesb = False #terraformer tries to Create Trees


#CIV SPECIFICS
##			if iCiv == iInfernal:
##				smokeb = False
##				hellterrb = False
##			elif iCiv == iIllians:
##				snowb = False
##				tundrab = False
##			elif iCiv == iDoviello:
##				tundrab = False


#UNIT SPECIFIC
			if pUnit.isHasPromotion(iLife1) or pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_DEVOUT'):
				if not iCiv == iInfernal:
					hellterrb = True #terraformer tries to remove hell terrain

			if pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_PRIEST_OF_LEAVES'):
				treesb = True #terraformer tries to Create Trees
				treesimpb = False
				if iCiv in [gc.getInfoTypeForString('CIVILIZATION_LJOSALFAR'), gc.getInfoTypeForString('CIVILIZATION_SVARTALFAR')]:
					treesimpb = True
				if not (treesimpb or pPlayer.getStateReligion() == iFoL):
					if not pPlayer.isHuman():
						pUnit.setUnitAIType(gc.getInfoTypeForString('UNITAI_MEDIC'))
						return 0

			if pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_WATER1')):
				smokeb = True
				desertb = True

			if pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_SUN1')):
#				tundrab = True
				marshb = True
				if not iCiv == iIllians:
					snowb = True

			if pUnit.isHasPromotion(iNature3):
				desertb = True
				plainsb = True
				tundrab = True
				marshb = True
				if not iCiv == iIllians:
					snowb = True

#TERRAFORMING CURRENT PLOT
			iImprovement = pPlot.getImprovementType()
			iTerrain = pPlot.getTerrainType()
			iFeature = pPlot.getFeatureType()

			if pPlot.getOwner() == iPlayer:
				if desertb or pPlot.isRiver():
					if iTerrain == iDesert:
						if pUnit.canCast(iSpellSpring,False):
							pUnit.cast(iSpellSpring)
						elif pUnit.canCast(iSpellVitalize,False):
							pUnit.cast(iSpellVitalize)
				if smokeb:
					if iImprovement == iSmoke:
						if pUnit.canCast(iSpellSpring,False):
							pUnit.cast(iSpellSpring)

				if snowb and iTerrain == iSnow:
					if pUnit.canCast(iSpellScorch,False):
						pUnit.cast(iSpellScorch)
					elif pUnit.canCast(iSpellVitalize,False):
						pUnit.cast(iSpellVitalize)

				if tundrab and iTerrain == iTundra:
					if pUnit.canCast(iSpellScorch,False):
						pUnit.cast(iSpellScorch)
					elif pUnit.canCast(iSpellVitalize,False):
						pUnit.cast(iSpellVitalize)

				if plainsb and iTerrain == iPlains:
					if pUnit.canCast(iSpellVitalize,False):
						pUnit.cast(iSpellVitalize)

				if marshb and iTerrain == iMarsh:
					if pUnit.canCast(iSpellScorch,False):
						pUnit.cast(iSpellScorch)
					elif pUnit.canCast(iSpellVitalize,False):
						pUnit.cast(iSpellVitalize)

				if hellterrb:
					if pUnit.canCast(iSpellSanctify,False):
						pUnit.cast(iSpellSanctify)

				if treesb:
					if pPlot.getFeatureType() == -1:
						if pUnit.canCast(iSpellBloom,False):
							if treesimpb or pPlot.getBonusType(-1) == -1:
								pUnit.cast(iSpellBloom)
								return 1

## LOOK FOR WORK
			if not pUnit.canMove():
				return 2

			for isearch in range(1,searchdistance,1):
				for iiX in range(iX-isearch, iX+isearch+1, 1):
					for iiY in range(iY-isearch, iY+isearch+1, 1):
						pPlot2 = CyMap().plot(iiX,iiY)
						if pPlot2.isNone():continue
						if pPlot2.getOwner() != iPlayer:continue
						if pPlot2.isImpassable():continue
						if not pUnit.canMoveInto(pPlot2,False,False,False):continue
						if pPlot2.isVisibleEnemyUnit(iPlayer):continue
						iImprovement = pPlot2.getImprovementType()
						if not (iImprovement != -1 and gc.getImprovementInfo(iImprovement).isUnique()):
							iTerrain = pPlot2.getTerrainType()
							iFeature = pPlot2.getFeatureType()
							if smokeb:
								if iImprovement == iSmoke:
									pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, iiX, iiY, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
									return 2
							if desertb:
								if iTerrain == iDesert and iFeature != iFlood:
									pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, iiX, iiY, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
									return 2
							if snowb:
								if iTerrain == iSnow:
									pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, iiX, iiY, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
									return 2
							if tundrab:
								if iTerrain == iTundra:
									pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, iiX, iiY, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
									return 2
							if marshb:
								if iTerrain == iMarsh:
									pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, iiX, iiY, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
									return 2
							if plainsb:
								if iTerrain == iPlains:
									pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, iiX, iiY, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
									return 2
							if hellterrb:
								if iTerrain in lHellTerrains:
									pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, iiX, iiY, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
									return 2
						if treesb:
							if not pPlot2.isCity():
								if iFeature == -1:
									if treesimpb or iImprovement == -1:
										if iTerrain in lBloomableTerrains:
											pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, iiX, iiY, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
											return 2

#Nothing to do, lets move on to another City!
			iBestCount=0
			pBestCity=0
			for icity in range(pPlayer.getNumCities()):
				pCity = pPlayer.getCity(icity)
				if not pCity.isNone():
					iCount=0
					for iI in range(1, 21):
						pPlot2 = pCity.getCityIndexPlot(iI)
						if pPlot2.isNone():continue
						if pPlot2.getOwner() != iPlayer:continue
						if pPlot2.isImpassable():continue
						if not pUnit.canMoveInto(pPlot2,False,False,False):continue
						if pPlot2.isVisibleEnemyUnit(iPlayer):continue
						iImprovement = pPlot2.getImprovementType()
						if not (iImprovement != -1 and gc.getImprovementInfo(iImprovement).isUnique()):
							iTerrain = pPlot2.getTerrainType()
							iFeature = pPlot2.getFeatureType()
							if smokeb:
								if iImprovement == iSmoke:
									iCount += 1
							if desertb or pPlot.isRiver():
								if iTerrain == iDesert and iFeature != iFlood:
									iCount += 1
							if snowb:
								if iTerrain == iSnow:
									iCount += 1
							if tundrab:
								if iTerrain == iTundra:
									iCount += 1
							if marshb:
								if iTerrain == iMarsh:
									iCount += 1
							if hellterrb:
								if iTerrain in lHellTerrains:
									iCount += 1
							if treesb:
								if not pPlot2.isCity():
									if iFeature == -1:
										if treesimpb or iImprovement == -1:
											if iTerrain in lBloomableTerrains:
												iCount += 1

					if iCount > iBestCount:
						pBestCity=pCity
						iBestCount=iCount
			if pBestCity!=0:
				pCPlot = pBestCity.plot()
				CX = pCPlot.getX()
				CY = pCPlot.getY()
				pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, CX, CY, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
				return 1
			return 0

	def AI_Mage_UPGRADE_MANA(self, argsList):
		pUnit = argsList[0]

#-----------------------------------
#UNITAI_MANA_UPGRADE
#Terraformer looks around for mana, changes UNITAI if he doesn't find some
#
# 1) Look for non raw mana and upgrade
# 2) Look for raw mana, decide how to upgrade, and do it!
# 3) Look for mana to dispel, and do it!
#-----------------------------------

		pPlot = pUnit.plot()
		iPlayer = pUnit.getOwner()
		pPlayer = gc.getPlayer(iPlayer)
		eTeam = gc.getTeam(pPlayer.getTeam())
		iX = pUnit.getX()
		iY = pUnit.getY()


		iRawMana = gc.getInfoTypeForString('BONUSCLASS_RAWMANA')
		iMana = gc.getInfoTypeForString('BONUSCLASS_MANA')
		lManasAlteration = [	gc.getInfoTypeForString('BONUS_MANA_BODY'),
					gc.getInfoTypeForString('BONUS_MANA_LIFE'),
					gc.getInfoTypeForString('BONUS_MANA_ENCHANTMENT'),
					gc.getInfoTypeForString('BONUS_MANA_NATURE'),
					gc.getInfoTypeForString('BONUS_MANA_NATURE')
					]
		lManasDivination = [	gc.getInfoTypeForString('BONUS_MANA_LAW'),
					gc.getInfoTypeForString('BONUS_MANA_SUN'),
					gc.getInfoTypeForString('BONUS_MANA_SPIRIT'),
					gc.getInfoTypeForString('BONUS_MANA_MIND')
					]
		lManasElementalism = [	gc.getInfoTypeForString('BONUS_MANA_EARTH'),
					gc.getInfoTypeForString('BONUS_MANA_FIRE'),
					gc.getInfoTypeForString('BONUS_MANA_AIR'),
					gc.getInfoTypeForString('BONUS_MANA_WATER')
					]
		lManasNecromancy = [	gc.getInfoTypeForString('BONUS_MANA_CHAOS'),
					gc.getInfoTypeForString('BONUS_MANA_DEATH'),
					gc.getInfoTypeForString('BONUS_MANA_ENTROPY'),
					gc.getInfoTypeForString('BONUS_MANA_SHADOW')
					]
#Look for Mana to Dispel
		searchdistance=15

		if pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_METAMAGIC2')):
			for isearch in range(1,searchdistance+1,1):
				for iiY in range(iY-isearch, iY+isearch, 1):
					for iiX in range(iX-isearch, iX+isearch, 1):
						pPlot2 = CyMap().plot(iiX,iiY)
						if pPlot2.isNone():continue
						if pPlot2.isImpassable():continue
						if pPlot2.isVisibleEnemyUnit(iPlayer):continue
						if pPlot2.getOwner() != iPlayer:continue
						iBonus = pPlot2.getBonusType(TeamTypes.NO_TEAM)
						if iBonus != -1:
							if gc.getBonusInfo(iBonus).getBonusClassType() == iMana:
								bDispel = True
								if pPlayer.getArcaneTowerVictoryFlag() == 0:
									if CyGame().getSorenRandNum(50, "Don't have to Dispel all the Time"):
										bDispel = False
								if pPlayer.getArcaneTowerVictoryFlag() == 1:
									if iBonus in lManasAlteration:
										if pPlayer.getNumAvailableBonuses(iBonus) == 1:
											bDispel = False
								if pPlayer.getArcaneTowerVictoryFlag() == 2:
									if iBonus in lManasDivination:
										if pPlayer.getNumAvailableBonuses(iBonus) == 1:
											bDispel = False
								if pPlayer.getArcaneTowerVictoryFlag() == 3:
									if iBonus in lManasNecromancy:
										if pPlayer.getNumAvailableBonuses(iBonus) == 1:
											bDispel = False
								if pPlayer.getArcaneTowerVictoryFlag() == 4:
									if iBonus in lManasElementalism:
										if pPlayer.getNumAvailableBonuses(iBonus) == 1:
											bDispel = False
								if bDispel:
									if pUnit.atPlot(pPlot2):
										if pUnit.canCast(gc.getInfoTypeForString('SPELL_DISPEL_MAGIC'),False):
											pUnit.cast(gc.getInfoTypeForString('SPELL_DISPEL_MAGIC'))
											return 1
									else:
#										CyInterface().addImmediateMessage('Searching for stuff to Dispel', "AS2D_NEW_ERA")
										pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, iiX, iiY, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
										return 1

#Dispel more if we seek Tower Victory Condition
			if pPlayer.getArcaneTowerVictoryFlag() > 0:
				iBestCount=0
				pBestCity=0
				for icity in range(pPlayer.getNumCities()):
					pCity = pPlayer.getCity(icity)
					if not pCity.isNone():
						iCount = 0
						for iI in range(1, 21):
							pPlot2 = pCity.getCityIndexPlot(iI)
							if pPlot2.isNone():continue
							if pPlot2.isImpassable():continue
							if pPlot2.isVisibleEnemyUnit(iPlayer):continue
							if pPlot2.getOwner() != iPlayer:continue
							iBonus = pPlot2.getBonusType(TeamTypes.NO_TEAM)
							if iBonus != -1:
								if gc.getBonusInfo(iBonus).getBonusClassType() in [iMana, iRawMana]:
									iCount += 1

						if iCount > iBestCount:
							pBestCity=pCity
							iBestCount=iCount
				if pBestCity != 0:
					pCPlot = pBestCity.plot()
					CX = pCPlot.getX()
					CY = pCPlot.getY()
					pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, CX, CY, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
					return 1

#found no mana, return 2 so UNITAI is reset

		return 2

#returns the current flag for Tower Victory
	def AI_TowerMastery(self, argsList):
		ePlayer = argsList[0]
		flag = argsList[1]

		pPlayer = gc.getPlayer(ePlayer)
		eTeam = gc.getTeam(pPlayer.getTeam())

#		CyInterface().addImmediateMessage('This is AI_TowerMastery ', "AS2D_NEW_ERA")
#		CyInterface().addImmediateMessage('Flag is '+str(pPlayer.getArcaneTowerVictoryFlag()), "AS2D_NEW_ERA")

		if flag == 0:
#			if eTeam.isHasTech(gc.getInfoTypeForString('TECH_SORCERY')) == False :
#				return 0
#			if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_METAMAGIC'))==0:
#				return 0

			iRawMana = gc.getInfoTypeForString('BONUSCLASS_RAWMANA')
			iMana = gc.getInfoTypeForString('BONUSCLASS_MANA')

			possiblemana=0
			for i in range (CyMap().numPlots()):
				pPlot = CyMap().plotByIndex(i)
				if pPlot.getOwner() == ePlayer:
					iBonus = pPlot.getBonusType(TeamTypes.NO_TEAM)
					if iBonus != -1:
						if gc.getBonusInfo(iBonus).getBonusClassType() in [iMana, iRawMana]:
							possiblemana += 1

			if possiblemana < 4:
				return 0

			if eTeam.isHasTech(gc.getInfoTypeForString('TECH_ALTERATION')):
				if eTeam.getBuildingClassCount(gc.getInfoTypeForString('BUILDINGCLASS_TOWER_OF_ALTERATION')) == 0:
					return 1

			if eTeam.isHasTech(gc.getInfoTypeForString('TECH_DIVINATION')):
				if eTeam.getBuildingClassCount(gc.getInfoTypeForString('BUILDINGCLASS_TOWER_OF_DIVINATION')) == 0:
					return 2

			if eTeam.isHasTech(gc.getInfoTypeForString('TECH_NECROMANCY')):
				if eTeam.getBuildingClassCount(gc.getInfoTypeForString('BUILDINGCLASS_TOWER_OF_NECROMANCY')) == 0:
					if not pPlayer.isCivic(CvUtil.findInfoTypeNum(gc.getCivicInfo,gc.getNumCivicInfos(),'CIVIC_OVERCOUNCIL')):
						return 3

			if eTeam.isHasTech(gc.getInfoTypeForString('TECH_ELEMENTALISM')):
				if eTeam.getBuildingClassCount(gc.getInfoTypeForString('BUILDINGCLASS_TOWER_OF_THE_ELEMENTS')) == 0:
					return 4

		if flag==1:
			if eTeam.getBuildingClassCount(gc.getInfoTypeForString('BUILDINGCLASS_TOWER_OF_ALTERATION')) > 0:
				return 0
			else:
				return 1

		if flag==2:
			if eTeam.getBuildingClassCount(gc.getInfoTypeForString('BUILDINGCLASS_TOWER_OF_DIVINATION')) > 0:
				return 0
			else:
				return 2

		if flag==3:
			if eTeam.getBuildingClassCount(gc.getInfoTypeForString('BUILDINGCLASS_TOWER_OF_NECROMANCY')) > 0:
				return 0
			else:
				return 3

		if flag==4:
			if eTeam.getBuildingClassCount(gc.getInfoTypeForString('BUILDINGCLASS_TOWER_OF_THE_ELEMENTS')) > 0:
				return 0
			else:
				return 4

		return 0
