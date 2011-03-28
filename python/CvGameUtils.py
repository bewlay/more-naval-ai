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



class CvGameUtils:
	"Miscellaneous game functions"
	def __init__(self): 
		pass
	
	def isVictoryTest(self):
		if ( gc.getGame().getElapsedGameTurns() > 10 ):
			return True
		else:
			return False

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
		pPlayer = gc.getPlayer(iPlayer)
		eTeam = gc.getTeam(pPlayer.getTeam())

		return -1	# Returning -1 means ignore; 0 means Build cannot be performed; 1 or greater means it can

	def cannotFoundCity(self,argsList):
		iPlayer, iPlotX, iPlotY = argsList
		pPlot = CyMap().plot(iPlotX,iPlotY)
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
		
		if eTech == gc.getInfoTypeForString('TECH_ORDERS_FROM_HEAVEN'):
			if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_RELIGION_1):
				return True
			if pPlayer.hasTrait(gc.getInfoTypeForString('TRAIT_AGNOSTIC')):
				return True
			if pPlayer.isHuman() == False:
				if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getReligionWeightModifier(gc.getInfoTypeForString('RELIGION_THE_ORDER'))<0:
					return True
		if eTech == gc.getInfoTypeForString('TECH_WAY_OF_THE_EARTHMOTHER'):
			if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_RELIGION_3):
				return True
			if pPlayer.hasTrait(gc.getInfoTypeForString('TRAIT_AGNOSTIC')):
				return True
			if pPlayer.isHuman() == False:
				if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getReligionWeightModifier(gc.getInfoTypeForString('RELIGION_RUNES_OF_KILMORPH'))<0:
					return True
				
		if eTech == gc.getInfoTypeForString('TECH_WAY_OF_THE_FORESTS'):
			if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_RELIGION_0):
				return True
			if pPlayer.hasTrait(gc.getInfoTypeForString('TRAIT_AGNOSTIC')):
				return True
			if pPlayer.isHuman() == False:
				if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getReligionWeightModifier(gc.getInfoTypeForString('RELIGION_FELLOWSHIP_OF_LEAVES'))<0:
					return True
				
		if eTech == gc.getInfoTypeForString('TECH_MESSAGE_FROM_THE_DEEP'):
			if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_RELIGION_2):
				return True
			if pPlayer.hasTrait(gc.getInfoTypeForString('TRAIT_AGNOSTIC')):
				return True
			if pPlayer.isHuman() == False:
				if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getReligionWeightModifier(gc.getInfoTypeForString('RELIGION_OCTOPUS_OVERLORDS'))<0:
					return True
				
		if eTech == gc.getInfoTypeForString('TECH_CORRUPTION_OF_SPIRIT'):
			if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_RELIGION_4):
				return True
			if pPlayer.hasTrait(gc.getInfoTypeForString('TRAIT_AGNOSTIC')):
				return True
			if pPlayer.isHuman() == False:
				if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getReligionWeightModifier(gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL'))<0:
					return True
				
		if eTech == gc.getInfoTypeForString('TECH_HONOR'):
			if pPlayer.hasTrait(gc.getInfoTypeForString('TRAIT_AGNOSTIC')):
				return True		
			if pPlayer.isHuman() == False:
				if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getReligionWeightModifier(gc.getInfoTypeForString('RELIGION_THE_EMPYREAN'))<0:
					return True
				
		if eTech == gc.getInfoTypeForString('TECH_DECEPTION'):
			if pPlayer.hasTrait(gc.getInfoTypeForString('TRAIT_AGNOSTIC')):
				return True		
			if pPlayer.isHuman() == False:
				if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getReligionWeightModifier(gc.getInfoTypeForString('RELIGION_COUNCIL_OF_ESUS'))<0:
					return True

		if eTech == gc.getInfoTypeForString('TECH_SEAFARING'):
			if iCiv != gc.getInfoTypeForString('CIVILIZATION_LANUN'):
				return True
		if pPlayer.isHuman() == False:
			if eTech == gc.getInfoTypeForString('TECH_STIRRUPS'):
				if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_CLAN_OF_EMBERS'):
					return True
				if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_LUCHUIRP'):
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
		pPlayer = gc.getPlayer(ePlayer)
		eTeam = gc.getTeam(pPlayer.getTeam())

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
		eUnitClass = gc.getUnitInfo(eUnit).getUnitClassType()
		eTeam = gc.getTeam(pPlayer.getTeam())

		if eUnit == gc.getInfoTypeForString('UNIT_BEAST_OF_AGARES'):
			if pCity.getPopulation() <= 5:
				return True

		if pPlayer.getCivics(gc.getInfoTypeForString('CIVICOPTION_CULTURAL_VALUES')) == gc.getInfoTypeForString('CIVIC_CRUSADE'):
			if eUnit == gc.getInfoTypeForString('UNIT_WORKER'):
				return True
			if eUnit == gc.getInfoTypeForString('UNIT_SETTLER'):
				return True
			if eUnit == gc.getInfoTypeForString('UNIT_WORKBOAT'):
				return True

		if eUnit == gc.getInfoTypeForString('UNIT_ACHERON'):
			if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_ACHERON):
				return True

		if eUnit == gc.getInfoTypeForString('UNIT_DUIN'):
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
		iBuildingClass = gc.getBuildingInfo(eBuilding).getBuildingClassType()
		eTeam = gc.getTeam(pPlayer.getTeam())
				
		if pPlayer.hasTrait(gc.getInfoTypeForString('TRAIT_AGNOSTIC')):		
			if eBuilding == gc.getInfoTypeForString('BUILDING_TEMPLE_OF_LEAVES'):
				return True
			if eBuilding == gc.getInfoTypeForString('BUILDING_TEMPLE_OF_KILMORPH'):
				return True
			if eBuilding == gc.getInfoTypeForString('BUILDING_TEMPLE_OF_THE_EMPYREAN'):
				return True
			if eBuilding == gc.getInfoTypeForString('BUILDING_TEMPLE_OF_THE_OVERLORDS'):
				return True
			if eBuilding == gc.getInfoTypeForString('BUILDING_TEMPLE_OF_THE_VEIL'):
				return True
			if eBuilding == gc.getInfoTypeForString('BUILDING_TEMPLE_OF_THE_ORDER'):
				return True								
		
		if pPlayer.getCivics(gc.getInfoTypeForString('CIVICOPTION_CULTURAL_VALUES')) == gc.getInfoTypeForString('CIVIC_CRUSADE'):
			if eBuilding == gc.getInfoTypeForString('BUILDING_ELDER_COUNCIL'):
				return True
			if eBuilding == gc.getInfoTypeForString('BUILDING_MARKET'):
				return True
			if eBuilding == gc.getInfoTypeForString('BUILDING_MONUMENT'):
				return True
			if eBuilding == gc.getInfoTypeForString('BUILDING_MONEYCHANGER'):
				return True
			if eBuilding == gc.getInfoTypeForString('BUILDING_THEATRE'):
				return True
			if eBuilding == gc.getInfoTypeForString('BUILDING_AQUEDUCT'):
				return True
			if eBuilding == gc.getInfoTypeForString('BUILDING_PUBLIC_BATHS'):
				return True
			if eBuilding == gc.getInfoTypeForString('BUILDING_HERBALIST'):
				return True
			if eBuilding == gc.getInfoTypeForString('BUILDING_CARNIVAL'):
				return True
			if eBuilding == gc.getInfoTypeForString('BUILDING_COURTHOUSE'):
				return True
			if eBuilding == gc.getInfoTypeForString('BUILDING_GAMBLING_HOUSE'):
				return True
			if eBuilding == gc.getInfoTypeForString('BUILDING_GRANARY'):
				return True
			if eBuilding == gc.getInfoTypeForString('BUILDING_SMOKEHOUSE'):
				return True
			if eBuilding == gc.getInfoTypeForString('BUILDING_LIBRARY'):
				return True
			if eBuilding == gc.getInfoTypeForString('BUILDING_HARBOR'):
				return True
			if eBuilding == gc.getInfoTypeForString('BUILDING_ALCHEMY_LAB'):
				return True
			if eBuilding == gc.getInfoTypeForString('BUILDING_BREWERY'):
				return True

		if eBuilding == gc.getInfoTypeForString('BUILDING_SHRINE_OF_THE_CHAMPION'):
			iHero = cf.getHero(pPlayer)
			if iHero == -1:
				return True
			if CyGame().isUnitClassMaxedOut(iHero, 0) == False:
				return True
			if pPlayer.getUnitClassCount(iHero) > 0:
				return True

		if eBuilding == gc.getInfoTypeForString('BUILDING_MERCURIAN_GATE'):
			if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_HYBOREM_OR_BASIUM):
				return True
			if pPlayer.getStateReligion() == gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL'):
				return True
			if pCity.isCapital():
				return True
			if pPlayer.isHuman() == False:
				if pPlayer.getAlignment() == gc.getInfoTypeForString('ALIGNMENT_EVIL'):
					return True

		iAltar1 = gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR')
		iAltar2 = gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_ANOINTED')
		iAltar3 = gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_BLESSED')
		iAltar4 = gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_CONSECRATED')
		iAltar5 = gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_DIVINE')
		iAltar6 = gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_EXALTED')
		iAltar7 = gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_FINAL')
		if (eBuilding == iAltar1 or eBuilding == iAltar2 or eBuilding == iAltar3 or eBuilding == iAltar4 or eBuilding == iAltar5 or eBuilding == iAltar6 or eBuilding == iAltar7):
			if pPlayer.getAlignment() == gc.getInfoTypeForString('ALIGNMENT_EVIL'):
				return True
			if eBuilding == iAltar1:
				if (pPlayer.countNumBuildings(iAltar2) > 0 or pPlayer.countNumBuildings(iAltar3) > 0 or pPlayer.countNumBuildings(iAltar4) > 0 or pPlayer.countNumBuildings(iAltar5) > 0 or pPlayer.countNumBuildings(iAltar6) > 0 or pPlayer.countNumBuildings(iAltar7) > 0):
					return True
			if eBuilding == iAltar2:
				if (pPlayer.countNumBuildings(iAltar3) > 0 or pPlayer.countNumBuildings(iAltar4) > 0 or pPlayer.countNumBuildings(iAltar5) > 0 or pPlayer.countNumBuildings(iAltar6) > 0 or pPlayer.countNumBuildings(iAltar7) > 0):
					return True
			if eBuilding == iAltar3:
				if (pPlayer.countNumBuildings(iAltar4) > 0 or pPlayer.countNumBuildings(iAltar5) > 0 or pPlayer.countNumBuildings(iAltar6) > 0 or pPlayer.countNumBuildings(iAltar7) > 0):
					return True
			if eBuilding == iAltar4:
				if (pPlayer.countNumBuildings(iAltar5) > 0 or pPlayer.countNumBuildings(iAltar6) > 0 or pPlayer.countNumBuildings(iAltar7) > 0):
					return True
			if eBuilding == iAltar5:
				if (pPlayer.countNumBuildings(iAltar6) > 0 or pPlayer.countNumBuildings(iAltar7) > 0):
					return True
			if eBuilding == iAltar6:
				if pPlayer.countNumBuildings(iAltar7) > 0:
					return True

		if pPlayer.isHuman() == False:
			if eBuilding == gc.getInfoTypeForString('BUILDING_PROPHECY_OF_RAGNAROK'):
				if pPlayer.getAlignment() != gc.getInfoTypeForString('ALIGNMENT_EVIL'):
					return True
					
			if eBuilding == gc.getInfoTypeForString('BUILDING_PLANAR_GATE'):
				if CyGame().getGlobalCounter() < 20:
					return True

		if eBuilding == gc.getInfoTypeForString('BUILDING_SMUGGLERS_PORT'):
			if pPlayer.isSmugglingRing() == False:
				return True

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
		eTeam = gc.getTeam(pPlayer.getTeam())
		
		if eProject == gc.getInfoTypeForString('PROJECT_PURGE_THE_UNFAITHFUL'):
			if pPlayer.isHuman() == False:
				return True
			if pPlayer.getStateReligion() == -1:
				return True

		if eProject == gc.getInfoTypeForString('PROJECT_BIRTHRIGHT_REGAINED'):
			if not pPlayer.isFeatAccomplished(FeatTypes.FEAT_GLOBAL_SPELL):
				return True

		if eProject == gc.getInfoTypeForString('PROJECT_STIR_FROM_SLUMBER'):
			if pPlayer.getPlayersKilled() == 0:
				return True

		if eProject == gc.getInfoTypeForString('PROJECT_ASCENSION'):
			if pPlayer.getCivilizationType() != gc.getInfoTypeForString('CIVILIZATION_ILLIANS'):
				return True
		
		if eProject == gc.getInfoTypeForString('PROJECT_SAMHAIN'):						
			if pPlayer.isHuman() == False:		
				if pPlayer.getNumCities() <= 3:
					return True
		
		if pPlayer.isHuman() == False:
			if pPlayer.getUnitClassCountPlusMaking(gc.getInfoTypeForString('UNITCLASS_WARRIOR')) <= 2:
				if not eTeam.isHasTech(gc.getInfoTypeForString('TECH_BRONZE_WORKING')):
					if not eTeam.isHasTech(gc.getInfoTypeForString('TECH_ARCHERY')):
						return True
			if pCity.getBaseYieldRate(1) <= 10:
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
		return False

	def AI_unitUpdate(self,argsList):
		pUnit = argsList[0]
		pPlot = pUnit.plot()
							
		if pUnit.getUnitClassType() == gc.getInfoTypeForString('UNITCLASS_GIANT_SPIDER'):
			iX = pUnit.getX()
			iY = pUnit.getY()
			for iiX in range(iX-1, iX+2, 1):
				for iiY in range(iY-1, iY+2, 1):
					pLoopPlot = CyMap().plot(iiX,iiY)
					for i in range(pLoopPlot.getNumUnits()):
						if pLoopPlot.getUnit(i).getOwner() != pUnit.getOwner():
							return 0
			pUnit.getGroup().pushMission(MissionTypes.MISSION_SKIP, 0, 0, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)							
			return 1

		if pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_ACHERON'):
			if pPlot.isVisibleEnemyUnit(pUnit.getOwner()):
				pUnit.cast(gc.getInfoTypeForString('SPELL_BREATH_FIRE'))

		iImprovement = pPlot.getImprovementType()
		if iImprovement != -1:
			if (iImprovement == gc.getInfoTypeForString('IMPROVEMENT_BARROW') or iImprovement == gc.getInfoTypeForString('IMPROVEMENT_RUINS') or iImprovement == gc.getInfoTypeForString('IMPROVEMENT_HELLFIRE')):
				if not pUnit.isAnimal():
					if pPlot.getNumUnits() - pPlot.getNumAnimalUnits() == 1:
						pUnit.getGroup().pushMission(MissionTypes.MISSION_SKIP, 0, 0, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)							
						return 1
			if (iImprovement == gc.getInfoTypeForString('IMPROVEMENT_BEAR_DEN') or iImprovement == gc.getInfoTypeForString('IMPROVEMENT_LION_DEN')):
				if pUnit.isAnimal():
					if pPlot.getNumAnimalUnits() == 1:
						pUnit.getGroup().pushMission(MissionTypes.MISSION_SKIP, 0, 0, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)							
						return 1
			if iImprovement == gc.getInfoTypeForString('IMPROVEMENT_GOBLIN_FORT'):
				if pUnit.getUnitCombatType() == gc.getInfoTypeForString('UNITCOMBAT_ARCHER'):
					pUnit.getGroup().pushMission(MissionTypes.MISSION_SKIP, 0, 0, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)							
					return 1
				if not pUnit.isAnimal():
					if pPlot.getNumUnits() - pPlot.getNumAnimalUnits() <= 2:
						pUnit.getGroup().pushMission(MissionTypes.MISSION_SKIP, 0, 0, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)							
						return 1
		
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
		
		iPopulationScore = CvUtil.getScoreComponent(gc.getPlayer(ePlayer).getPopScore(), gc.getGame().getInitPopulation(), gc.getGame().getMaxPopulation(), gc.getDefineINT("SCORE_POPULATION_FACTOR"), True, bFinal, bVictory)
		iLandScore = CvUtil.getScoreComponent(gc.getPlayer(ePlayer).getLandScore(), gc.getGame().getInitLand(), gc.getGame().getMaxLand(), gc.getDefineINT("SCORE_LAND_FACTOR"), True, bFinal, bVictory)
		iTechScore = CvUtil.getScoreComponent(gc.getPlayer(ePlayer).getTechScore(), gc.getGame().getInitTech(), gc.getGame().getMaxTech(), gc.getDefineINT("SCORE_TECH_FACTOR"), True, bFinal, bVictory)
		iWondersScore = CvUtil.getScoreComponent(gc.getPlayer(ePlayer).getWondersScore(), gc.getGame().getInitWonders(), gc.getGame().getMaxWonders(), gc.getDefineINT("SCORE_WONDER_FACTOR"), False, bFinal, bVictory)
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
		
		iPillageGold = 0
		iPillageGold = CyGame().getSorenRandNum(gc.getImprovementInfo(pPlot.getImprovementType()).getPillageGold(), "Pillage Gold 1")
		iPillageGold += CyGame().getSorenRandNum(gc.getImprovementInfo(pPlot.getImprovementType()).getPillageGold(), "Pillage Gold 2")

		iPillageGold += (pUnit.getPillageChange() * iPillageGold) / 100
		
		return iPillageGold
	
	def doCityCaptureGold(self, argsList):
		"controls the gold result of capturing a city"
		
		pOldCity = argsList[0]
		
		iCaptureGold = 0
		
		iCaptureGold += gc.getDefineINT("BASE_CAPTURE_GOLD")
		iCaptureGold += (pOldCity.getPopulation() * gc.getDefineINT("CAPTURE_GOLD_PER_POPULATION"))
		iCaptureGold += CyGame().getSorenRandNum(gc.getDefineINT("CAPTURE_GOLD_RAND1"), "Capture Gold 1")
		iCaptureGold += CyGame().getSorenRandNum(gc.getDefineINT("CAPTURE_GOLD_RAND2"), "Capture Gold 2")

		if (gc.getDefineINT("CAPTURE_GOLD_MAX_TURNS") > 0):
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
		return true
		
	def getUnitCostMod(self, argsList):
		iPlayer, iUnit = argsList
		iCostMod = -1 # Any value > 0 will be used
		
		return iCostMod

	def getBuildingCostMod(self, argsList):
		iPlayer, iCityID, iBuilding = argsList
		pPlayer = gc.getPlayer(iPlayer)
		pCity = pPlayer.getCity(iCityID)

		iCostMod = -1 # Any value > 0 will be used

		if iBuilding == gc.getInfoTypeForString('BUILDING_GAMBLING_HOUSE'):
			if pPlayer.isGamblingRing():
				iCostMod = gc.getBuildingInfo(iBuilding).getProductionCost() / 4
		
		return iCostMod
		
	def canUpgradeAnywhere(self, argsList):
		pUnit = argsList
		
		bCanUpgradeAnywhere = 0
		
		return bCanUpgradeAnywhere
		
	def getWidgetHelp(self, argsList):
		eWidgetType, iData1, iData2, bOption = argsList
		
		return u""
		
	def getUpgradePriceOverride(self, argsList):
		iPlayer, iUnitID, iUnitTypeUpgrade = argsList
		
		return -1	# Any value 0 or above will be used
	
	def getExperienceNeeded(self, argsList):
		# use this function to set how much experience a unit needs
		iLevel, iOwner = argsList
		
		iExperienceNeeded = 0

		# regular epic game experience		
		iExperienceNeeded = iLevel * iLevel + 1

		iModifier = gc.getPlayer(iOwner).getLevelExperienceModifier()
		if (0 != iModifier):
			iExperienceNeeded += (iExperienceNeeded * iModifier + 99) / 100   # ROUND UP
			
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
		pPlayer = gc.getPlayer(pUnit.getOwner())
		eTeam = gc.getTeam(pPlayer.getTeam())
		iCiv = pPlayer.getCivilizationType()
		iX = pUnit.getX()
		iY = pUnit.getY()
		
		if (pUnit.getUnitAIType() == gc.getInfoTypeForString('UNITAI_TERRAFORMER')):

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
			smokeb = true #terraformer tries to put out smoke
			desertb = true #terraformer tries to spring deserts
			snowb = true #terraformer tries to scorch snow to tundra
			tundrab = false #terraformer tries to scorch tundra to plains
			marshb = true #terraformer tries to scorch marsh to grassland
			grassb = false #terraformer tries to scorch grassland to plains			
			hellterrb = true #terraformer tries to remove hell terrain
			treesb = false #terraformer tries to Create Trees
								
			desert = 0
			snow = 0
			tundra = 0
			marsh = 0
			grass = 0
			hellterr = 0
			floodplain = 0
			trees = 0

#CIV SPECIFICS			
			if iCiv == gc.getInfoTypeForString('CIVILIZATION_INFERNAL'):
				smokeb = false
			if iCiv == gc.getInfoTypeForString('CIVILIZATION_ILLIANS'):
				snowb = false
			if (iCiv == gc.getInfoTypeForString('CIVILIZATION_DOVIELLO') or iCiv == gc.getInfoTypeForString('CIVILIZATION_ILLIANS')):
				tundrab = false	
			if iCiv == gc.getInfoTypeForString('CIVILIZATION_INFERNAL'):
				hellterrb = false
				
#UNIT SPECIFIC
			if pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_DEVOUT'):			
				desertb = false #terraformer tries to spring deserts
				snowb = false #terraformer tries to scorch snow to tundra
				tundrab = false #terraformer tries to scorch tundra to plains
				marshb = false #terraformer tries to scorch marsh to grassland
				grassb = false #terraformer tries to scorch grassland to plains			
				hellterrb = true #terraformer tries to remove hell terrain
				treesb = false #terraformer tries to Create Trees				
				treesimpb= false #terraformer can Create Trees in Improvements				

			if pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_PRIEST_OF_LEAVES'):
				desertb = false #terraformer tries to spring deserts
				snowb = false #terraformer tries to scorch snow to tundra
				tundrab = false #terraformer tries to scorch tundra to plains
				marshb = false #terraformer tries to scorch marsh to grassland
				grassb = false #terraformer tries to scorch grassland to plains			
				hellterrb = false #terraformer tries to remove hell terrain				
				treesb = true #terraformer tries to Create Trees			
				treesimpb = false
				if (iCiv == gc.getInfoTypeForString('CIVILIZATION_LJOSALFAR') or iCiv == gc.getInfoTypeForString('CIVILIZATION_SVARTALFAR')):
					treesimpb = true
				if ((treesimpb == False) and (pPlayer.getStateReligion() != gc.getInfoTypeForString('RELIGION_FELLOWSHIP_OF_LEAVES'))):
					if not pPlayer.isHuman():
						pUnit.setUnitAIType(gc.getInfoTypeForString('UNITAI_RESERVE'))
						return 0

				
#TERRAFORMING
			if pPlot.getOwner()==pUnit.getOwner():
				if (desertb or pPlot.isRiver()):
					if pPlot.getTerrainType()==gc.getInfoTypeForString('TERRAIN_DESERT'):
						if pUnit.canCast(gc.getInfoTypeForString('SPELL_SPRING'),false):
							pUnit.cast(gc.getInfoTypeForString('SPELL_SPRING'))
							return 0
				elif smokeb:
					if pPlot.getImprovementType() == gc.getInfoTypeForString('IMPROVEMENT_SMOKE'):
						if pUnit.canCast(gc.getInfoTypeForString('SPELL_SPRING'),false):
							pUnit.cast(gc.getInfoTypeForString('SPELL_SPRING'))
							return 0

				if (snowb and pPlot.getTerrainType()==gc.getInfoTypeForString('TERRAIN_SNOW')):
					if pUnit.canCast(gc.getInfoTypeForString('SPELL_SCORCH'),false):
						pUnit.cast(gc.getInfoTypeForString('SPELL_SCORCH'))
						return 0

				if (tundrab and pPlot.getTerrainType()==gc.getInfoTypeForString('TERRAIN_TUNDRA')):
					if pUnit.canCast(gc.getInfoTypeForString('SPELL_SCORCH'),false):
						pUnit.cast(gc.getInfoTypeForString('SPELL_SCORCH'))
						return 0

				if (marshb and pPlot.getTerrainType()==gc.getInfoTypeForString('TERRAIN_MARSH')):
					if pUnit.canCast(gc.getInfoTypeForString('SPELL_SCORCH'),false):
						pUnit.cast(gc.getInfoTypeForString('SPELL_SCORCH'))
						return 0

				if (grassb and pPlot.getTerrainType()==gc.getInfoTypeForString('TERRAIN_GRASS')):
					if pUnit.canCast(gc.getInfoTypeForString('SPELL_SCORCH'),false):
						pUnit.cast(gc.getInfoTypeForString('SPELL_SCORCH'))
						return 0

				if hellterrb:
					if pUnit.canCast(gc.getInfoTypeForString('SPELL_SANCTIFY'),false):
						pUnit.cast(gc.getInfoTypeForString('SPELL_SANCTIFY'))
						return 0

				if treesb:
					if pPlot.getFeatureType()==-1:
						if pUnit.canCast(gc.getInfoTypeForString('SPELL_BLOOM'),false):
							if treesimpb or pPlot.getBonusType(-1) == -1:
								pUnit.cast(gc.getInfoTypeForString('SPELL_BLOOM'))
								return 0

#-----------------------------------
#LOOK FOR WORK
#
#MALAKIM EXCEPTION
#LOOK FOR WORK
#-----------------------------------


			for isearch in range(1,searchdistance,1):
								
	#LOOK FOR WORK			
				if 1==1:
					for iiX in range(iX-isearch, iX+isearch+1, 1):
						for iiY in range(iY-isearch, iY+isearch+1, 1):
							pPlot2 = CyMap().plot(iiX,iiY)
							if not (pPlot2.isNone() or pPlot2.isImpassable() or pPlot2.isVisibleEnemyUnit(pUnit.getOwner())):
								if pPlot2.getOwner()==pUnit.getOwner():
									if not (pPlot2.getImprovementType() != -1 and (gc.getImprovementInfo(pPlot2.getImprovementType()).isUnique() == true)):									
										if pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_WATER1')):
											if smokeb:
												if (pPlot2.getImprovementType() == gc.getInfoTypeForString('IMPROVEMENT_SMOKE')):
													desert=desert+1
											if (desertb or pPlot.isRiver()):
												if (pPlot2.getTerrainType()==gc.getInfoTypeForString('TERRAIN_DESERT') and not pPlot2.getFeatureType() == gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS')):
													desert=desert+1
										if pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_SUN1')):
											if snowb:
												if pPlot2.getTerrainType()==gc.getInfoTypeForString('TERRAIN_SNOW'):
													snow=snow+1								
											if tundrab:
												if pPlot2.getTerrainType()==gc.getInfoTypeForString('TERRAIN_TUNDRA'):
													tundra=tundra+1								
											if marshb:
												if pPlot2.getTerrainType()==gc.getInfoTypeForString('TERRAIN_MARSH'):
													marsh=marsh+1								
											if grassb:
												if pPlot2.getTerrainType()==gc.getInfoTypeForString('TERRAIN_GRASS'):
													grass=grass+1
										if hellterrb:								
											if pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_LIFE1')):
												if (pPlot2.getTerrainType() == gc.getInfoTypeForString('TERRAIN_BROKEN_LANDS') or pPlot2.getTerrainType() == gc.getInfoTypeForString('TERRAIN_BURNING_SANDS') or pPlot2.getTerrainType() == gc.getInfoTypeForString('TERRAIN_FIELDS_OF_PERDITION') or pPlot2.getTerrainType() == gc.getInfoTypeForString('TERRAIN_SHALLOWS')):
													hellterr=hellterr+1													
										if treesb:
											if (pPlot2.getFeatureType() == -1):
												if (pPlot2.getTerrainType() == gc.getInfoTypeForString('TERRAIN_GRASS') or pPlot2.getTerrainType() == gc.getInfoTypeForString('TERRAIN_PLAINS') or pPlot2.getTerrainType() == gc.getInfoTypeForString('TERRAIN_TUNDRA')):
													if not pPlot2.isCity():
														if (pPlot2.getImprovementType()==-1 or treesimpb):
															trees=trees+1
										
	#Remove some deserts/smoke etc.?			

				if desert>0:
					for iiX in range(iX-isearch, iX+isearch+1, 1):
						for iiY in range(iY-isearch, iY+isearch+1, 1):			
							pPlot2 = CyMap().plot(iiX,iiY)
							if not (pPlot2.isNone() or pPlot2.isImpassable() or pPlot2.isVisibleEnemyUnit(pUnit.getOwner())):
								if pPlot2.getOwner()==pUnit.getOwner():
									if not (pPlot2.getImprovementType() != -1 and (gc.getImprovementInfo(pPlot2.getImprovementType()).isUnique() == true)):									
										if smokeb:
											if (pPlot2.getImprovementType() == gc.getInfoTypeForString('IMPROVEMENT_SMOKE')):
												pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, iiX, iiY, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)							
												return 1
										if (desertb or pPlot.isRiver()):
											if (pPlot2.getTerrainType()==gc.getInfoTypeForString('TERRAIN_DESERT') and not pPlot2.getFeatureType() == gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS')):
												pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, iiX, iiY, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)							
												return 1


				if snow>0:
					for iiX in range(iX-isearch, iX+isearch+1, 1):
						for iiY in range(iY-isearch, iY+isearch+1, 1):			
							pPlot2 = CyMap().plot(iiX,iiY)
							if not (pPlot2.isNone() or pPlot2.isImpassable() or pPlot2.isVisibleEnemyUnit(pUnit.getOwner())):
								if pPlot2.getOwner()==pUnit.getOwner():						
									if not (pPlot2.getImprovementType() != -1 and (gc.getImprovementInfo(pPlot2.getImprovementType()).isUnique() == true)):									
										if pPlot2.getTerrainType()==gc.getInfoTypeForString('TERRAIN_SNOW'):
											pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, iiX, iiY, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)							
											return 1

				if tundra>0:
					for iiX in range(iX-isearch, iX+isearch+1, 1):
						for iiY in range(iY-isearch, iY+isearch+1, 1):			
							pPlot2 = CyMap().plot(iiX,iiY)
							if not (pPlot2.isNone() or pPlot2.isImpassable() or pPlot2.isVisibleEnemyUnit(pUnit.getOwner())):
								if pPlot2.getOwner()==pUnit.getOwner():						
									if not (pPlot2.getImprovementType() != -1 and (gc.getImprovementInfo(pPlot2.getImprovementType()).isUnique() == true)):									
										if pPlot2.getTerrainType()==gc.getInfoTypeForString('TERRAIN_TUNDRA'):
											pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, iiX, iiY, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)							
											return 1
				if marsh>0:
					for iiX in range(iX-isearch, iX+isearch+1, 1):
						for iiY in range(iY-isearch, iY+isearch+1, 1):			
							pPlot2 = CyMap().plot(iiX,iiY)
							if not (pPlot2.isNone() or pPlot2.isImpassable() or pPlot2.isVisibleEnemyUnit(pUnit.getOwner())):
								if pPlot2.getOwner()==pUnit.getOwner():						
									if not (pPlot2.getImprovementType() != -1 and (gc.getImprovementInfo(pPlot2.getImprovementType()).isUnique() == true)):									
										if pPlot2.getTerrainType()==gc.getInfoTypeForString('TERRAIN_MARSH'):
											pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, iiX, iiY, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)							
											return 1

				if grass>0:
					for iiX in range(iX-isearch, iX+isearch+1, 1):
						for iiY in range(iY-isearch, iY+isearch+1, 1):			
							pPlot2 = CyMap().plot(iiX,iiY)
							if not (pPlot2.isNone() or pPlot2.isImpassable() or pPlot2.isVisibleEnemyUnit(pUnit.getOwner())):
								if pPlot2.getOwner()==pUnit.getOwner():						
									if not (pPlot2.getImprovementType() != -1 and (gc.getImprovementInfo(pPlot2.getImprovementType()).isUnique() == true)):									
										if pPlot2.getTerrainType()==gc.getInfoTypeForString('TERRAIN_GRASS'):
											pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, iiX, iiY, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)							
											return 1
																																												

	#Hell terrain to sanctify?
				if (hellterr>0 and pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_LIFE1'))):
					for iiX in range(iX-isearch, iX+isearch+1, 1):
						for iiY in range(iY-isearch, iY+isearch+1, 1):
							pPlot2 = CyMap().plot(iiX,iiY)
							if not (pPlot2.isNone() or pPlot2.isImpassable() or pPlot2.isVisibleEnemyUnit(pUnit.getOwner()) or pPlot2.isWater()):
								if pPlot2.getOwner()==pUnit.getOwner():								
									if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_PLOT_COUNTER):
										if (pPlot2.getTerrainType() == gc.getInfoTypeForString('TERRAIN_BROKEN_LANDS') or pPlot2.getTerrainType() == gc.getInfoTypeForString('TERRAIN_BURNING_SANDS') or pPlot2.getTerrainType() == gc.getInfoTypeForString('TERRAIN_FIELDS_OF_PERDITION') or pPlot2.getTerrainType() == gc.getInfoTypeForString('TERRAIN_SHALLOWS')):
											pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, iiX, iiY, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)																	
									elif pPlot2.getPlotCounter()>7:
										pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, iiX, iiY, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
			
				if floodplain>0:
					for iiX in range(iX-isearch, iX+isearch+1, 1):
						for iiY in range(iY-isearch, iY+isearch+1, 1):			
							pPlot2 = CyMap().plot(iiX,iiY)
							if not (pPlot2.isNone() or pPlot2.isImpassable() or pPlot2.isVisibleEnemyUnit(pUnit.getOwner())):
								if pPlot2.getOwner()==pUnit.getOwner():						
									if not (pPlot2.getImprovementType() != -1 and (gc.getImprovementInfo(pPlot2.getImprovementType()).isUnique() == true)):									
										if (pPlot2.isRiver() and pPlot2.getFeatureType()==-1):
											pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, iiX, iiY, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)							
											return 1

				if trees>0:
					for iiX in range(iX-isearch, iX+isearch+1, 1):
						for iiY in range(iY-isearch, iY+isearch+1, 1):			
							pPlot2 = CyMap().plot(iiX,iiY)
							if not (pPlot2.isNone() or pPlot2.isImpassable() or pPlot2.isVisibleEnemyUnit(pUnit.getOwner())):
								if pPlot2.getOwner()==pUnit.getOwner():						
									if not (pPlot2.getImprovementType() != -1 and (gc.getImprovementInfo(pPlot2.getImprovementType()).isUnique() == true)):									
										if (pPlot2.getFeatureType() == -1):
											if (pPlot2.getTerrainType() == gc.getInfoTypeForString('TERRAIN_GRASS') or pPlot2.getTerrainType() == gc.getInfoTypeForString('TERRAIN_PLAINS') or pPlot2.getTerrainType() == gc.getInfoTypeForString('TERRAIN_TUNDRA')):										
												if not pPlot2.isCity():
													if ((pPlot2.getImprovementType()==-1 and pPlot2.getBonusType(-1)==-1)or treesimpb):										
														pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, iiX, iiY, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)							
														return 1											
			
#Nothing to do, lets move on to another City!
			iBestCount=0
			pBestCity=0
			for icity in range(pPlayer.getNumCities()):
				pCity = pPlayer.getCity(icity)
				if not pCity.isNone():			
					iCount=0
					for iI in range(1, 21):
						pPlot2 = pCity.getCityIndexPlot(iI)					
						if not (pPlot2.isNone() or pPlot2.isImpassable() or pPlot2.isVisibleEnemyUnit(pUnit.getOwner())):
							if pPlot2.getOwner()==pUnit.getOwner():
								if not (pPlot2.getImprovementType() != -1 and (gc.getImprovementInfo(pPlot2.getImprovementType()).isUnique() == true)):									
									if pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_WATER1')):
										if smokeb:
											if (pPlot2.getImprovementType() == gc.getInfoTypeForString('IMPROVEMENT_SMOKE')):
												iCount=iCount+1
										if (desertb or pPlot.isRiver()):
											if (pPlot2.getTerrainType()==gc.getInfoTypeForString('TERRAIN_DESERT') and not pPlot2.getFeatureType() == gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS')):
												iCount=iCount+1
									if pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_SUN1')):
										if snowb:
											if pPlot2.getTerrainType()==gc.getInfoTypeForString('TERRAIN_SNOW'):
												iCount=iCount+1								
										if tundrab:
											if pPlot2.getTerrainType()==gc.getInfoTypeForString('TERRAIN_TUNDRA'):
												iCount=iCount+1								
										if marshb:
											if pPlot2.getTerrainType()==gc.getInfoTypeForString('TERRAIN_MARSH'):
												iCount=iCount+1								
										if grassb:
											if pPlot2.getTerrainType()==gc.getInfoTypeForString('TERRAIN_GRASS'):
												iCount=iCount+1
									if hellterrb:								
										if pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_LIFE1')):
											if (pPlot2.getTerrainType() == gc.getInfoTypeForString('TERRAIN_BROKEN_LANDS') or pPlot2.getTerrainType() == gc.getInfoTypeForString('TERRAIN_BURNING_SANDS') or pPlot2.getTerrainType() == gc.getInfoTypeForString('TERRAIN_FIELDS_OF_PERDITION') or pPlot2.getTerrainType() == gc.getInfoTypeForString('TERRAIN_SHALLOWS')):
												iCount=iCount+1
									if treesb:
										if (pPlot2.getFeatureType() == -1):
											if (pPlot2.getTerrainType() == gc.getInfoTypeForString('TERRAIN_GRASS') or pPlot2.getTerrainType() == gc.getInfoTypeForString('TERRAIN_PLAINS') or pPlot2.getTerrainType() == gc.getInfoTypeForString('TERRAIN_TUNDRA')):										
												if not pPlot2.isCity():
													if (pPlot2.getImprovementType()==-1 or treesimpb):										
														iCount=iCount+1													
				
					if (iCount>iBestCount):
						pBestCity=pCity
						iBestCount=iCount
			if (pBestCity!=0):
				pCPlot = pBestCity.plot()
				CX = pCPlot.getX()
				CY = pCPlot.getY()	
				pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, CX, CY, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)														
				return 1
			return 0
			
# Returns Promotiontype or -1 for no Promotion
	def AI_MagePromotion(self, argsList):
		pUnit = argsList[0]
		pPlot = pUnit.plot()
		pPlayer = gc.getPlayer(pUnit.getOwner())				
		eTeam = gc.getTeam(pPlayer.getTeam())		
		iPromotion = -1
		pCity = -1
		if pPlot.isCity():
			pCity=pPlot.getPlotCity()

#		if CyGame().getSorenRandNum(100, "Don't have check promotions every turn")	<70:
#			return -1
#OVERVIEW
#DIFFERENT FUNCTION FOR UNITAI_MAGE,UNITAI_TERRAFORMER, UNITAI_WARWIZARD
#
#1 List of available Promotion for the UNITAI
#2 Setting StackvaluesMod(Should several mages in the stack be able to cast the spell?)
#3 Adding CivValues
#4 Modify Spells by their action types (Mages with every turn Spells will prefere to add permanant spells)
#5 Add general Spellvalue for the UNITAI
#6 Make sure Adepts will take promos if they are needed for later promos
#7 Make sure Adepts will take promotions if they have enough XP to Upgrade to Mages

#------------
#UNITAI_MAGE
#------------			
		if ((pUnit.getUnitAIType()==gc.getInfoTypeForString('UNITAI_MAGE')) or (pUnit.getUnitAIType()==gc.getInfoTypeForString('UNITAI_HERO'))):
		
#Useless Spells should get a modifier of -10000
#Civvalues should be between 0 and 500
#And Spellvalues between 0 and 1000


#---------------------	
#List of available Promotions
#What Spells need a mage that buffs/defends cities?
#---------------------	
			sType = ['PROMOTION_BODY1','PROMOTION_BODY2','PROMOTION_CHAOS1','PROMOTION_CHAOS2']
			sType = sType +['PROMOTION_DEATH1','PROMOTION_DEATH2','PROMOTION_EARTH1','PROMOTION_ENTROPY1','PROMOTION_ENCHANTMENT1','PROMOTION_ENCHANTMENT2']
			sType = sType +['PROMOTION_ICE1','PROMOTION_MIND1','PROMOTION_MIND2','PROMOTION_NATURE1','PROMOTION_SHADOW1']
			sType = sType +['PROMOTION_SPIRIT1','PROMOTION_SPIRIT2']
			sType = sType +['PROMOTION_COMBAT1','PROMOTION_COMBAT2','PROMOTION_COMBAT3','PROMOTION_COMBAT4','PROMOTION_COMBAT5']

#---------------------				
#StackvaluesMod 
# 0 = doesn't matter, -100 = no way (other values are more interesting for offensive spellcasting
#---------------------	
			lStackvaluesMod = [-100,-100,0,-100,-100]
			lStackvaluesMod = lStackvaluesMod+[0,0,-100,0,-100,-100]
			lStackvaluesMod = lStackvaluesMod+[0,-100,0,-100,-100]
			lStackvaluesMod = lStackvaluesMod+[-100,-100]
			lStackvaluesMod = lStackvaluesMod+[0,0,0,0,0]
			
			lValues = [0]
			for i in range(len(sType)):
				lValues=lValues+[0]

#---------------------					
#Adding Civ Values
#---------------------	
#Amurites				
#Balseraph				
			if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_BALSERAPHS'):
				lValues[sType.index('PROMOTION_CHAOS1')]+=500
				lValues[sType.index('PROMOTION_CHAOS2')]+=500											
#Luchuirp				
			if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_LUCHUIRP'):
				lValues[sType.index('PROMOTION_ENCHANTMENT1')]+=500
				lStackvaluesMod[sType.index('PROMOTION_ENCHANTMENT1')]=-2				
#SHEAIM				
			if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_SHEAIM'):
				lValues[sType.index('PROMOTION_DEATH1')]+=2000			
				lValues[sType.index('PROMOTION_DEATH2')]+=2000							
				
#---------------------	
#Modify Spells by their Stack Value (is it good to have several mages able to cast the spell?)
#---------------------							
			for i in range(len(sType)):
				lPromonbr=0
				for ii in range(pPlot.getNumUnits()):				
					if pPlot.getUnit(ii).isHasPromotion(gc.getInfoTypeForString(sType[i])):
						lPromonbr+=1
				lValues[i]+=lPromonbr*lStackvaluesMod[i]*100
#---------------------					
#Modify Spells by their action type (is it needed to cast them every turn?)
#---------------------				
			bcastoffspell=false
			if pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_DEATH1')):
				bcastoffspell=true				
			elif pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_CHAOS1')):
				bcastoffspell=true				
			elif pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_ENTROPY1')):
				bcastoffspell=true
			elif pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_ICE1')):
				bcastoffspell=true
			elif pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_MIND2')):
				bcastoffspell=true
			elif pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_SHADOW1')):
				bcastoffspell=true
			if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_LUCHUIRP'):
				lValues[sType.index('PROMOTION_ENCHANTMENT1')]+=1000																	
				
			if not bcastoffspell:
				for i in range(len(sType)):
					lValues[sType.index('PROMOTION_DEATH1')]+=1000
					lValues[sType.index('PROMOTION_CHAOS1')]+=1000
					lValues[sType.index('PROMOTION_ENTROPY1')]+=1000
					lValues[sType.index('PROMOTION_ICE1')]+=1000
					lValues[sType.index('PROMOTION_MIND2')]+=1000
					lValues[sType.index('PROMOTION_SHADOW1')]+=1000														

#---------------------					
#Spell Usefullness						
#Some are better than others...
#No, we don't use the XML file, cause these are only for city defenders
#But make sure Adepts take combat promos if necessary to upgrade to mages
#---------------------
			for i in range(len(sType)):
#Permanent Spells						
				if sType[i]=='PROMOTION_BODY2':								
					lValues[i]=lValues[i]+500									
				elif sType[i]=='PROMOTION_EARTH1':
					lValues[i]=lValues[i]+800
				elif sType[i]=='PROMOTION_MIND1':
					lValues[i]=lValues[i]+200
				elif sType[i]=='PROMOTION_SPIRIT2':
					if pPlayer.isHasTech(gc.getInfoTypeForString('TECH_SORCERY')):				
						lValues[i]=lValues[i]+300
				elif sType[i]=='PROMOTION_ENCHANTMENT1':						
					if pPlot.isCity():
						lValues[i]=lValues[i]+250
						if (pCity.getNumBuilding(gc.getInfoTypeForString('BUILDING_TRAINING_YARD')) == 1):
							lValues[i]=lValues[i]+500
				elif sType[i]=='PROMOTION_ENCHANTMENT2':
					if pPlot.isCity():
						lValues[i]=lValues[i]+250
						if (pCity.getNumBuilding(gc.getInfoTypeForString('BUILDING_TRAINING_YARD')) == 1):
							lValues[i]=lValues[i]+500

#Powerfull debuffs
				elif sType[i]=='PROMOTION_DEATH1':
					lValues[i]=lValues[i]+100
				elif sType[i]=='PROMOTION_DEATH2':
					lValues[i]=lValues[i]+400				
				elif sType[i]=='PROMOTION_CHAOS1':
					lValues[i]=lValues[i]+150
				elif sType[i]=='PROMOTION_SHADOW1':
					lValues[i]=lValues[i]+130					
				elif sType[i]=='PROMOTION_ENTROPY1':
					lValues[i]=lValues[i]+800
				elif sType[i]=='PROMOTION_ICE1':
					lValues[i]=lValues[i]+700
				elif sType[i]=='PROMOTION_MIND2':
					lValues[i]=lValues[i]+500		
							
#Spells that are only needed for Upgrade
			if pPlayer.isHasTech(gc.getInfoTypeForString('TECH_SORCERY')):			
				lValues[sType.index('PROMOTION_BODY1')]=lValues[sType.index('PROMOTION_BODY2')]+10									
				lValues[sType.index('PROMOTION_SPIRIT1')]=lValues[sType.index('PROMOTION_SPIRIT2')]+10																			

#---------------------
#Make sure Adepts take combat promos if necessary to be able to upgrade to mage
#---------------------

			lValues[sType.index('PROMOTION_COMBAT1')]+=100
			lValues[sType.index('PROMOTION_COMBAT2')]+=100
			lValues[sType.index('PROMOTION_COMBAT3')]+=100
			lValues[sType.index('PROMOTION_COMBAT4')]+=100			
			lValues[sType.index('PROMOTION_COMBAT5')]+=100

			if pPlayer.isHasTech(gc.getInfoTypeForString('TECH_SORCERY')):
				if (pUnit.getExperience()>=10 and pUnit.getLevel()<4 and pUnit.getUnitClassType()==gc.getInfoTypeForString('UNITCLASS_ADEPT')):
					lValues[sType.index('PROMOTION_COMBAT1')]+=10
					lValues[sType.index('PROMOTION_COMBAT2')]+=10
					lValues[sType.index('PROMOTION_COMBAT3')]+=10
					lValues[sType.index('PROMOTION_COMBAT4')]+=10				
					lValues[sType.index('PROMOTION_COMBAT5')]+=10
					
#---------------------
#Choose the best Spell
#---------------------					
			iBestSpell=-1
			iBestSpellValue=0
			for i in range(len(sType)):
				if lValues[i]>iBestSpellValue:
					if pUnit.canPromote(gc.getInfoTypeForString(sType[i]),-1):
						iBestSpellValue=lValues[i]
						iBestSpell=i
#			CyInterface().addImmediateMessage('IBestSpell is'+sType[iBestSpell], "AS2D_NEW_ERA")										
#			CyInterface().addImmediateMessage('IBestSpell is'+sType[iBestSpell], "AS2D_NEW_ERA")				
#			CyInterface().addImmediateMessage('IValue is'+str(lValues[iBestSpell]), "AS2D_NEW_ERA")				
#			CyInterface().addImmediateMessage('IValue is'+str(sType.index('PROMOTION_COMBAT1')), "AS2D_NEW_ERA")							
						
			if iBestSpell!=-1:
				iBestSpell=gc.getInfoTypeForString(sType[iBestSpell])
				
			
			return iBestSpell

#------------
#UNITAI_WARWIZARD
#------------			
					
		if (pUnit.getUnitAIType()==gc.getInfoTypeForString('UNITAI_WARWIZARD')):

			if pPlayer.isHasTech(gc.getInfoTypeForString('TECH_SORCERY')):	
				countmages=0
				for ii in range (pPlot.getNumUnits()):
					if pPlot.getUnit(ii).getUnitCombatType()==gc.getInfoTypeForString('UNITCOMBAT_ADEPT'):
						countmages+=1
				if countmages<3:
					return -1
#Useless Spells should get a modifier of -10000
#Civvalues should be between 0 and 500
#And Spellvalues between 0 and 1000


#---------------------	
#List of available Promotions
#What Spells need a mage that buffs/defends cities?
#---------------------										

			sType = ['PROMOTION_AIR1','PROMOTION_AIR2','PROMOTION_BODY1','PROMOTION_BODY2','PROMOTION_CHAOS1']
			sType = sType +['PROMOTION_CHAOS2','PROMOTION_DEATH1','PROMOTION_DEATH2','PROMOTION_EARTH1','PROMOTION_EARTH2']
			sType = sType +['PROMOTION_ENTROPY1','PROMOTION_ENCHANTMENT1','PROMOTION_ENCHANTMENT2','PROMOTION_FIRE1','PROMOTION_FIRE2']
			sType = sType +['PROMOTION_ICE1','PROMOTION_LIFE1','PROMOTION_LIFE2','PROMOTION_MIND1']
			sType = sType +['PROMOTION_MIND2','PROMOTION_NATURE1','PROMOTION_NATURE2','PROMOTION_SHADOW1','PROMOTION_SHADOW2','PROMOTION_SPIRIT1']
			sType = sType +['PROMOTION_SUN1','PROMOTION_SUN2']
			sType = sType +['PROMOTION_COMBAT1','PROMOTION_COMBAT2','PROMOTION_COMBAT3','PROMOTION_COMBAT4','PROMOTION_COMBAT5','PROMOTION_MOBILITY1']
			
#---------------------				
#StackvaluesMod 
# 0 = doesn't matter, -100 = no way, normal values should be between 0 and -10 
#---------------------	
			lStackvaluesMod = [-2,-2,-100,-100,-100]
			lStackvaluesMod +=[-100,0,0,0,-2]
			lStackvaluesMod +=[-1,-100,-100,-2,0]
			lStackvaluesMod +=[-2,-2,-7,0]
			lStackvaluesMod +=[-2,-100,-100,-100,-100,-100]
			lStackvaluesMod +=[0,-2]
			lStackvaluesMod +=[0,0,0,0,0,0]			

			if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_LUCHUIRP'):
				lStackvaluesMod[sType.index('PROMOTION_ENCHANTMENT1')]=2			
			
			
			lValues = [0]
			for i in range(len(sType)):
				lValues=lValues+[0]

#---------------------					
#Adding Civ Values
#---------------------	
#Amurites

#Balseraph				
			if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_BALSERAPHS'):
				lValues[sType.index('PROMOTION_CHAOS1')]+=500
				lValues[sType.index('PROMOTION_CHAOS2')]+=500
				
			if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_HIPPUS'):				
				lValues[sType.index('PROMOTION_MOBILITY1')]+=200													
#LJOSALFAR								
								
			if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_LJOSALFAR'):		
				lValues[sType.index('PROMOTION_FIRE2')]+=500
	
#Luchuirp				
			if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_LUCHUIRP'):
				lValues[sType.index('PROMOTION_ENCHANTMENT1')]+=500			
#SVARTALFAR				
			if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_SVARTALFAR'):
				lValues[sType.index('PROMOTION_FIRE2')]+=500
#SHEIAM
			if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_SHEAIM'):
				lValues[sType.index('PROMOTION_DEATH1')]+=500
				lValues[sType.index('PROMOTION_DEATH2')]+=500

#---------------------	
#Modify Spells by their Stack Value (is it good to have several mages able to cast the spell?)
#---------------------							
			for i in range(len(sType)):
				lPromonbr=0
				for ii in range(pPlot.getNumUnits()):				
					if pPlot.getUnit(ii).isHasPromotion(gc.getInfoTypeForString(sType[i])):
						lPromonbr+=1
				lValues[i]+=lPromonbr*lStackvaluesMod[i]*100
#---------------------					
#Modify Spells by their action type (is it needed to cast them every turn?)
#---------------------				
			bcastoffspell=false
			if pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_AIR2')):
				bcastoffspell=true						
			elif pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_CHAOS1')):
				bcastoffspell=true								
			elif pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_DEATH1')):
				bcastoffspell=true				
			elif pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_DEATH2')):
				bcastoffspell=true				
			elif pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_ENTROPY1')):
				bcastoffspell=true
			elif pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_FIRE2')):
				bcastoffspell=true
			elif pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_ICE1')):
				bcastoffspell=true
			elif pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_MIND2')):
				bcastoffspell=true
			elif pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_SHADOW1')):
				bcastoffspell=true
				
			if not bcastoffspell:
				for i in range(len(sType)):
					lValues[sType.index('PROMOTION_AIR2')]+=1000
					lValues[sType.index('PROMOTION_CHAOS1')]+=1000
					lValues[sType.index('PROMOTION_DEATH1')]+=1000
					lValues[sType.index('PROMOTION_DEATH2')]+=1000
					lValues[sType.index('PROMOTION_ENTROPY1')]+=1000
					lValues[sType.index('PROMOTION_FIRE2')]+=1000								
					lValues[sType.index('PROMOTION_MIND2')]+=1000
					lValues[sType.index('PROMOTION_SHADOW1')]+=1000
					
			if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_LUCHUIRP'):
				lValues[sType.index('PROMOTION_ENCHANTMENT1')]+=1000																	
					
#---------------------					
#Spell Usefullness						
#Some are better than others...
#No, we don't use the XML file, cause these are only for city defenders
#But make sure Adepts take combat promos if necessary to upgrade to mages
#---------------------

#Permanent Spells
			lValues[sType.index('PROMOTION_CHAOS1')]+=250														
			lValues[sType.index('PROMOTION_SHADOW1')]+=270
			lValues[sType.index('PROMOTION_SHADOW2')]+=270
			lValues[sType.index('PROMOTION_NATURE1')]+=280
			lValues[sType.index('PROMOTION_SPIRIT1')]+=300			
			lValues[sType.index('PROMOTION_ENCHANTMENT1')]+=300
			lValues[sType.index('PROMOTION_ENCHANTMENT2')]+=300
			lValues[sType.index('PROMOTION_NATURE2')]+=300
			lValues[sType.index('PROMOTION_BODY1')]+=500									
			lValues[sType.index('PROMOTION_BODY2')]+=500			
#Powerfull debuffs			
			lValues[sType.index('PROMOTION_EARTH2')]+=100
			lValues[sType.index('PROMOTION_ICE1')]+=400
			lValues[sType.index('PROMOTION_MIND2')]+=400
			lValues[sType.index('PROMOTION_SUN2')]+=400
			lValues[sType.index('PROMOTION_ENTROPY1')]+=800																							
#Direct damage
			lValues[sType.index('PROMOTION_LIFE2')]+=0 #definetly needs some check																													
			lValues[sType.index('PROMOTION_FIRE2')]+=200																							
			lValues[sType.index('PROMOTION_AIR2')]+=500									
#Summons
			lValues[sType.index('PROMOTION_DEATH2')]+=200
			lValues[sType.index('PROMOTION_FIRE2')]+=220
			
							
#Spells that are only needed for Upgrade			
			if pPlayer.isHasTech(gc.getInfoTypeForString('TECH_SORCERY')):			
				lValues[sType.index('PROMOTION_EARTH1')]=lValues[sType.index('PROMOTION_EARTH2')]+10
				lValues[sType.index('PROMOTION_MIND1')]=lValues[sType.index('PROMOTION_MIND2')]+10
				lValues[sType.index('PROMOTION_LIFE1')]=lValues[sType.index('PROMOTION_LIFE2')]+10						
				lValues[sType.index('PROMOTION_FIRE1')]=lValues[sType.index('PROMOTION_FIRE2')]+10
				lValues[sType.index('PROMOTION_AIR1')]=lValues[sType.index('PROMOTION_AIR2')]+10
				lValues[sType.index('PROMOTION_DEATH1')]=lValues[sType.index('PROMOTION_DEATH2')]+10				

#---------------------
#Make sure Adepts take combat promos if necessary to be able to upgrade to mage
#---------------------

			if pPlayer.isHasTech(gc.getInfoTypeForString('TECH_SORCERY')):
				if (pUnit.getExperience()>=10 and pUnit.getLevel()<4 and pUnit.getUnitClassType()==gc.getInfoTypeForString('UNITCLASS_ADEPT')):
					lValues[sType.index('PROMOTION_COMBAT1')]=10
					lValues[sType.index('PROMOTION_COMBAT2')]=10
					lValues[sType.index('PROMOTION_COMBAT3')]=10
					lValues[sType.index('PROMOTION_COMBAT4')]=10				
					lValues[sType.index('PROMOTION_COMBAT5')]=10
					lValues[sType.index('PROMOTION_MOBILITY1')]=10									
#---------------------
#Choose the best Spell
#---------------------					
			iBestSpell=-1
			iBestSpellValue=0
			for i in range(len(sType)):
				if lValues[i]>iBestSpellValue:
					if pUnit.canPromote(gc.getInfoTypeForString(sType[i]),-1):
						iBestSpellValue=lValues[i]
						iBestSpell=i
#			CyInterface().addImmediateMessage('IBestSpell is'+sType[iBestSpell], "AS2D_NEW_ERA")										
#			CyInterface().addImmediateMessage('IBestSpell is'+sType[iBestSpell], "AS2D_NEW_ERA")				
#			CyInterface().addImmediateMessage('IValue is'+str(lValues[iBestSpell]), "AS2D_NEW_ERA")				
#			CyInterface().addImmediateMessage('IValue is'+str(sType.index('PROMOTION_COMBAT1')), "AS2D_NEW_ERA")							
						
			if iBestSpell!=-1:
				iBestSpell=gc.getInfoTypeForString(sType[iBestSpell])
				
			
			return iBestSpell

#------------
#UNITAI_TERRAFORMER
#------------			
			
		if (pUnit.getUnitAIType()==gc.getInfoTypeForString('UNITAI_TERRAFORMER') or pUnit.getUnitAIType()==gc.getInfoTypeForString('UNITAI_MANA_UPGRADE')):
			if pUnit.getUnitType()==gc.getInfoTypeForString('UNIT_PRIEST_OF_LEAVES'):
				if pUnit.canPromote(gc.getInfoTypeForString('PROMOTION_MOBILITY1'),-1):
					return gc.getInfoTypeForString('PROMOTION_MOBILITY1')			
			if pPlayer.isHasTech(gc.getInfoTypeForString('TECH_SORCERY')):
				if pUnit.canPromote(gc.getInfoTypeForString('PROMOTION_METAMAGIC1'),-1):
					return gc.getInfoTypeForString('PROMOTION_METAMAGIC1')					
				if pUnit.canPromote(gc.getInfoTypeForString('PROMOTION_METAMAGIC2'),-1):
					return gc.getInfoTypeForString('PROMOTION_METAMAGIC2')
				if (pUnit.getExperience()>10 and pUnit.getLevel()==4 and pUnit.getUnitClassType()==gc.getInfoTypeForString('UNITCLASS_ADEPT')):
					return -1
			if CyGame().getGlobalCounter()>15:
				if pUnit.canPromote(gc.getInfoTypeForString('PROMOTION_LIFE1'),-1):
					return gc.getInfoTypeForString('PROMOTION_LIFE1')
			if pUnit.canPromote(gc.getInfoTypeForString('PROMOTION_SUN1'),-1):
				return gc.getInfoTypeForString('PROMOTION_SUN1')
			if not pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_INFERNAL'):														
				if pUnit.canPromote(gc.getInfoTypeForString('PROMOTION_WATER1'),-1):
					return gc.getInfoTypeForString('PROMOTION_WATER1')
			if pUnit.canPromote(gc.getInfoTypeForString('PROMOTION_LIFE1'),-1):
				return gc.getInfoTypeForString('PROMOTION_LIFE1')
			if pUnit.canPromote(gc.getInfoTypeForString('PROMOTION_MOBILITY1'),-1):
					return gc.getInfoTypeForString('PROMOTION_MOBILITY1')
			if pUnit.canPromote(gc.getInfoTypeForString('PROMOTION_BODY1'),-1):
					return gc.getInfoTypeForString('PROMOTION_BODY1')
								

		return iPromotion

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
		pPlayer = gc.getPlayer(pUnit.getOwner())
		eTeam = gc.getTeam(pPlayer.getTeam())
		iX = pUnit.getX()
		iY = pUnit.getY()

		smokeb = true #Civ likes to put out smoke
		desertb = true #Civ likes to spring deserts
		snowb = true #Civ likes to scorch snow to tundra
		tundrab = false #Civ likes to scorch tundra to plains
		marshb = true #Civ likes to scorch marsh to grassland
		grassb = false #Civ likes to scorch grassland to plains			
		hellterrb = true #Civ likes to remove hell terrain

		if (pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_INFERNAL')):
			smokeb = false
			hellterrb = false

#		if (pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_INFERNAL')): 
#			desertb = false

		if (pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_ILLIANS')):
			snowb = false
		
		if pPlayer.getCivilizationType()  == gc.getInfoTypeForString('CIVILIZATION_SHEAIM'):
			hellterrb = false

#Look for non raw mana 		
		searchdistance=15
		imanatype = -1
		
		for isearch in range(1,searchdistance+1,1):
			if imanatype != -1: 
				break
			for iiY in range(iY-isearch, iY+isearch, 1):
				for iiX in range(iX-isearch, iX+isearch, 1):					
					pPlot2 = CyMap().plot(iiX,iiY)
					if not (pPlot2.isNone() or pPlot2.isImpassable() or pPlot2.isVisibleEnemyUnit(pUnit.getOwner())):
						if pPlot2.getOwner() == pUnit.getOwner():
							if pPlot2.getBonusType(-1) != -1:
								iBonus = pPlot2.getBonusType(TeamTypes.NO_TEAM)
								if gc.getBonusInfo(iBonus).getBonusClassType() == gc.getInfoTypeForString('BONUSCLASS_MANA'):
#									if not pPlot2.isPlotGroupConnectedBonus(pUnit.getOwner(),iBonus):								
									imanatype=pPlot2.getBonusType(TeamTypes.NO_TEAM)
									if imanatype != -1:												
										for iBuild in range(gc.getNumBuildInfos()):
											if pUnit.canBuild(pPlot2,iBuild,false):
												pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, iiX, iiY, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
												pUnit.getGroup().pushMission(MissionTypes.MISSION_BUILD, iBuild, -1, 0, True, False, MissionAITypes.NO_MISSIONAI, pPlot, pUnit)
												return 1												

#Look for raw mana 		
		searchdistance=15
		imanatype = -1
		
		for isearch in range(1,searchdistance+1,1):
			if imanatype!=-1: 
				break
			for iiY in range(iY-isearch, iY+isearch, 1):
				for iiX in range(iX-isearch, iX+isearch, 1):
					pPlot2 = CyMap().plot(iiX,iiY)
					if not (pPlot2.isNone() or pPlot2.isImpassable() or pPlot2.isVisibleEnemyUnit(pUnit.getOwner())):
						if pPlot2.getOwner() == pUnit.getOwner():
							if pPlot2.getBonusType(-1) != -1:
								iBonus = pPlot2.getBonusType(TeamTypes.NO_TEAM)
								if (iBonus == gc.getInfoTypeForString('BONUS_MANA') and not (iiX==iX and iiY==iY)):
									pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, iiX, iiY, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)																																												
									return 1
								elif iBonus == gc.getInfoTypeForString('BONUS_MANA'):
#---------------------
#Choose Mana to Build
#
#Set Flags
#----------------------	

									deathmagicb=true
									holymagicb=true
									if pPlayer.getAlignment() == gc.getInfoTypeForString('ALIGNMENT_EVIL'):
										holymagicb = false
									if pPlayer.getAlignment() == gc.getInfoTypeForString('ALIGNMENT_GOOD'):
										deathmagicb = false
#List of Useful Mana

									sType = ['BONUS_MANA_AIR','BONUS_MANA_BODY','BONUS_MANA_CHAOS','BONUS_MANA_DEATH']
									sType = sType +['BONUS_MANA_EARTH','BONUS_MANA_ENCHANTMENT','BONUS_MANA_ENTROPY','BONUS_MANA_FIRE']
									sType = sType +['BONUS_MANA_LAW','BONUS_MANA_LIFE','BONUS_MANA_MIND','BONUS_MANA_NATURE','BONUS_MANA_SHADOW']
									sType = sType +['BONUS_MANA_SPIRIT','BONUS_MANA_SUN','BONUS_MANA_WATER','BONUS_MANA_METAMAGIC']

									sBuildType = ['BUILD_MANA_AIR','BUILD_MANA_BODY','BUILD_MANA_CHAOS','BUILD_MANA_DEATH']
									sBuildType = sBuildType +['BUILD_MANA_EARTH','BUILD_MANA_ENCHANTMENT','BUILD_MANA_ENTROPY','BUILD_MANA_FIRE']
									sBuildType = sBuildType +['BUILD_MANA_LAW','BUILD_MANA_LIFE','BUILD_MANA_MIND','BUILD_MANA_NATURE','BUILD_MANA_SHADOW']
									sBuildType = sBuildType +['BUILD_MANA_SPIRIT','BUILD_MANA_SUN','BUILD_MANA_WATER','BUILD_MANA_METAMAGIC']
									
									lValues = [0]
									lStackvaluesMod = [1] # by default a Civ doesn't like to stack mana
									for i in range(len(sType)):
										lValues=lValues+[1000]
										lStackvaluesMod=lStackvaluesMod+[1]

#---------------------
#Adding Civ Values and their Mana stack values
#---------------------
									if pPlayer.getAlignment() == gc.getInfoTypeForString('ALIGNMENT_EVIL'):
										lValues[sType.index('BONUS_MANA_DEATH')]*=2
										lValues[sType.index('BONUS_MANA_ENTROPY')]*=2
										lValues[sType.index('BONUS_MANA_CHAOS')]*=2
										lValues[sType.index('BONUS_MANA_LIFE')]/=2
										lValues[sType.index('BONUS_MANA_LAW')]/=2
										lValues[sType.index('BONUS_MANA_SPIRIT')]/=2	
										
									if pPlayer.getAlignment() == gc.getInfoTypeForString('ALIGNMENT_GOOD'):
										lValues[sType.index('BONUS_MANA_LIFE')]*=2
										lValues[sType.index('BONUS_MANA_LAW')]*=2
										lValues[sType.index('BONUS_MANA_SPIRIT')]*=2
										lValues[sType.index('BONUS_MANA_DEATH')]/=2
										lValues[sType.index('BONUS_MANA_ENTROPY')]/=2
										lValues[sType.index('BONUS_MANA_CHAOS')]/=2
										
																			
#Amurites
#Balseraph
#									if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_BALSERAPHS'):
#										lValues[sType.index('BONUS_MANA_CHAOS')]+=1000
#LJOSALFAR
									if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_LJOSALFAR'):
										lValues[sType.index('BONUS_MANA_FIRE')]+=250
										lStackvaluesMod[sType.index('BONUS_MANA_FIRE')]=2
#Luchuirp
									if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_LUCHUIRP'):
										lValues[sType.index('BONUS_MANA_ENCHANTMENT')]+=250
										lValues[sType.index('BONUS_MANA_FIRE')]+=250
										lStackvaluesMod[sType.index('BONUS_MANA_ENCHANTMENT')]=2
#SVARTALFAR				
									if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_SVARTALFAR'):
										lValues[sType.index('BONUS_MANA_FIRE')]+=250
										lStackvaluesMod[sType.index('BONUS_MANA_FIRE')]=2
										lValues[sType.index('BONUS_MANA_NATURE')]+=250
										lStackvaluesMod[sType.index('BONUS_MANA_NATURE')]=2
#SHEAIM
									if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_SHEAIM'):
										lValues[sType.index('BONUS_MANA_ENTROPY')]+=250
										lValues[sType.index('BONUS_MANA_DEATH')]+=250
										lStackvaluesMod[sType.index('BONUS_MANA_DEATH')]=2
#MANA TYPE VALUES

#SPELL LEVEL 1
									
#Permanent
									lValues[sType.index('BONUS_MANA_NATURE')]+=50									
									lValues[sType.index('BONUS_MANA_SPIRIT')]+=200
									lValues[sType.index('BONUS_MANA_EARTH')]+=200
									lValues[sType.index('BONUS_MANA_ENCHANTMENT')]+=250
#per turn buffs
									lValues[sType.index('BONUS_MANA_MIND')]+=150
									lValues[sType.index('BONUS_MANA_BODY')]+=250
									lValues[sType.index('BONUS_MANA_CHAOS')]+=200
									lValues[sType.index('BONUS_MANA_SHADOW')]+=200
									lValues[sType.index('BONUS_MANA_ENTROPY')]+=200									
#Summons
									lValues[sType.index('BONUS_MANA_DEATH')]+=200

#SPELL LEVEL 2
									if pPlayer.isHasTech(gc.getInfoTypeForString('TECH_SORCERY')):												
#Direct Damage
										lValues[sType.index('BONUS_MANA_AIR')]+=500
										lValues[sType.index('BONUS_MANA_FIRE')]+=500
	#Permanent
										lValues[sType.index('BONUS_MANA_CHAOS')]+=0									
										lValues[sType.index('BONUS_MANA_SPIRIT')]+=100
										lValues[sType.index('BONUS_MANA_BODY')]+=100
	#per turn buffs
										lValues[sType.index('BONUS_MANA_EARTH')]+=100
										lValues[sType.index('BONUS_MANA_SHADOW')]+=100
										lValues[sType.index('BONUS_MANA_SUN')]+=400
										lValues[sType.index('BONUS_MANA_MIND')]+=400									
	#Summons									
										lValues[sType.index('BONUS_MANA_ENTROPY')]+=100
										lValues[sType.index('BONUS_MANA_DEATH')]+=200

#need mana for terraforming?						
									for pyCity in PyPlayer(pUnit.getOwner()).getCityList():
										pCity = pyCity.GetCy()
										pPlot3 = pCity.plot()
										cX = pPlot3.getX()
										cY = pPlot3.getY()										
										for iiX in range(cX-2, cX+2, 1):
											for iiY in range(cY-2, cY+2, 1):
												pPlot4 = CyMap().plot(iiX,iiY)
												if not (pPlot4.isNone() or pPlot4.isImpassable()):
													if pPlot4.getOwner()==pUnit.getOwner():
														if desertb:
															if (pPlot4.getTerrainType()==gc.getInfoTypeForString('TERRAIN_DESERT') and not pPlot4.getFeatureType() == gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS')):
																if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_WATER'))==0:
																	lValues[sType.index('BONUS_MANA_WATER')]+=60
														if snowb:
															if pPlot4.getTerrainType()==gc.getInfoTypeForString('TERRAIN_SNOW'):
																if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_SUN'))==0:
																	lValues[sType.index('BONUS_MANA_SUN')]+=120
														if tundrab:														
															if pPlot4.getTerrainType()==gc.getInfoTypeForString('TERRAIN_TUNDRA'):
																lValues[sType.index('BONUS_MANA_SUN')]+=60
														if marshb:
															if pPlot4.getTerrainType()==gc.getInfoTypeForString('TERRAIN_MARSH'):
																lValues[sType.index('BONUS_MANA_SUN')]+=60
														if grassb:
															if pPlot4.getTerrainType()==gc.getInfoTypeForString('TERRAIN_GRASS'):
																lValues[sType.index('BONUS_MANA_SUN')]+=60
														if (hellterrb and CyGame().getGlobalCounter()>20):
															if (pPlot2.getTerrainType() == gc.getInfoTypeForString('TERRAIN_BROKEN_LANDS') or pPlot2.getTerrainType() == gc.getInfoTypeForString('TERRAIN_BURNING_SANDS') or pPlot2.getTerrainType() == gc.getInfoTypeForString('TERRAIN_FIELDS_OF_PERDITION') or pPlot2.getTerrainType() == gc.getInfoTypeForString('TERRAIN_SHALLOWS')):
																lValues[sType.index('BONUS_MANA_LIFE')]+=100

#ManaStackvalues
									for i in range(len(sType)):
										iNumberMana=0
										iNumberMana+=pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString(sType[i]))
										lValues[i]-=((iNumberMana * 500) / lStackvaluesMod[i])
										
#Values for Victory Condition
									#if (xPlayer.AI_isDoVictoryStrategy(AI_VICTORY_TOWERMASTERY1)):
									
									if (pPlayer.getArcaneTowerVictoryFlag()>0):
										if pPlayer.isHasTech(gc.getInfoTypeForString('TECH_SORCERY')):
											if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_METAMAGIC'))==0:													
												lValues[sType.index('BONUS_MANA_METAMAGIC')]+=5000
	
										if (pPlayer.getArcaneTowerVictoryFlag()==1):
											if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_BODY'))==0:													
												lValues[sType.index('BONUS_MANA_BODY')]+=4000
											if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_LIFE'))==0:																								
												lValues[sType.index('BONUS_MANA_LIFE')]+=4000	
											if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_ENCHANTMENT'))==0:																																			
												lValues[sType.index('BONUS_MANA_ENCHANTMENT')]+=4000
											if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_NATURE'))==0:																																		
												lValues[sType.index('BONUS_MANA_NATURE')]+=4000
	
										if (pPlayer.getArcaneTowerVictoryFlag()==2):
											if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_LAW'))==0:													
												lValues[sType.index('BONUS_MANA_LAW')]+=4000
											if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_SUN'))==0:																								
												lValues[sType.index('BONUS_MANA_SUN')]+=4000	
											if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_SPIRIT'))==0:																																			
												lValues[sType.index('BONUS_MANA_SPIRIT')]+=4000
											if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_MIND'))==0:																																		
												lValues[sType.index('BONUS_MANA_MIND')]+=4000
	
										if (pPlayer.getArcaneTowerVictoryFlag()==3):
											if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_CHAOS'))==0:													
												lValues[sType.index('BONUS_MANA_CHAOS')]+=4000
											if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_DEATH'))==0:																								
												lValues[sType.index('BONUS_MANA_DEATH')]+=4000
											if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_ENTROPY'))==0:																																			
												lValues[sType.index('BONUS_MANA_ENTROPY')]+=4000
											if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_SHADOW'))==0:																																		
												lValues[sType.index('BONUS_MANA_SHADOW')]+=4000	
	 
										if (pPlayer.getArcaneTowerVictoryFlag()==4):
											if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_EARTH'))==0:													
												lValues[sType.index('BONUS_MANA_EARTH')]+=4000	
											if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_FIRE'))==0:																								
												lValues[sType.index('BONUS_MANA_FIRE')]+=4000
											if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_AIR'))==0:																																			
												lValues[sType.index('BONUS_MANA_AIR')]+=4000	
											if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_WATER'))==0:																																		
												lValues[sType.index('BONUS_MANA_WATER')]+=4000
							

#---------------------
#Choose the best MANA
#---------------------					
# Tholal AI - ToDo  - reserve 1 raw mana if have lots and going for tower victory
#									if (pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUSCLASS_RAWMANA')) == 1:					
	
									iBestMana=-1
									iBestManaValue=0
									for i in range(len(sType)):
										if lValues[i]>iBestManaValue:
											if pUnit.canBuild(pPlot,gc.getInfoTypeForString(sBuildType[i]),false):
												iBestManaValue=lValues[i]
												iBestMana=i
												
									if iBestMana!=-1:
										pUnit.getGroup().pushMission(MissionTypes.MISSION_BUILD,gc.getInfoTypeForString(sBuildType[iBestMana]), -1, 0, False, False, MissionAITypes.MISSIONAI_BUILD, pPlot, pUnit)
										pPlot.setRouteType(gc.getInfoTypeForString('ROUTE_ROAD')) #help out the AI for the moment
										return 1
#Look for Mana to Dispel
		searchdistance=15
		   		
		if pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_METAMAGIC2')):		
			for isearch in range(1,searchdistance+1,1):				
				for iiY in range(iY-isearch, iY+isearch, 1):
					for iiX in range(iX-isearch, iX+isearch, 1):					
						pPlot2 = CyMap().plot(iiX,iiY)
						if not (pPlot2.isNone() or pPlot2.isImpassable() or pPlot2.isVisibleEnemyUnit(pUnit.getOwner())):
							if pPlot2.getOwner()==pUnit.getOwner():
							
								if pPlot2.getBonusType(-1) != -1:
									iBonus = pPlot2.getBonusType(TeamTypes.NO_TEAM)
									if gc.getBonusInfo(iBonus).getBonusClassType() == gc.getInfoTypeForString('BONUSCLASS_MANA'):
										bDispel = true

										if (pPlayer.getArcaneTowerVictoryFlag()==0):
											if CyGame().getSorenRandNum(50, "Don't have to Dispel all the Time"):									
												bDispel = false
										if (pPlayer.getArcaneTowerVictoryFlag()==1):
											if iBonus == gc.getInfoTypeForString('BONUS_MANA_BODY'):
												if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_BODY'))==1:													
													bDispel = false
											if iBonus == gc.getInfoTypeForString('BONUS_MANA_LIFE'):
												if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_LIFE'))==1:													
													bDispel = false									
											if iBonus == gc.getInfoTypeForString('BONUS_MANA_ENCHANTMENT'):
												if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_ENCHANTMENT'))==1:													
													bDispel = false									
											if iBonus == gc.getInfoTypeForString('BONUS_MANA_NATURE'):
												if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_NATURE'))==1:													
													bDispel = false																						

										if (pPlayer.getArcaneTowerVictoryFlag()==2):
											if iBonus == gc.getInfoTypeForString('BONUS_MANA_LAW'):
												if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_LAW'))==1:													
													bDispel = false
											if iBonus == gc.getInfoTypeForString('BONUS_MANA_SUN'):
												if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_SUN'))==1:													
													bDispel = false									
											if iBonus == gc.getInfoTypeForString('BONUS_MANA_SPIRIT'):
												if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_SPIRIT'))==1:													
													bDispel = false									
											if iBonus == gc.getInfoTypeForString('BONUS_MANA_MIND'):
												if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_MIND'))==1:													
													bDispel = false																															

										if (pPlayer.getArcaneTowerVictoryFlag()==3):
											if iBonus == gc.getInfoTypeForString('BONUS_MANA_CHAOS'):
												if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_CHAOS'))==1:													
													bDispel = false
											if iBonus == gc.getInfoTypeForString('BONUS_MANA_DEATH'):
												if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_DEATH'))==1:													
													bDispel = false									
											if iBonus == gc.getInfoTypeForString('BONUS_MANA_ENTROPY'):
												if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_ENTROPY'))==1:													
													bDispel = false									
											if iBonus == gc.getInfoTypeForString('BONUS_MANA_SHADOW'):
												if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_SHADOW'))==1:													
													bDispel = false	
														 
										if (pPlayer.getArcaneTowerVictoryFlag()==4):
											if iBonus == gc.getInfoTypeForString('BONUS_MANA_EARTH'):
												if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_EARTH'))==1:													
													bDispel = false
											if iBonus == gc.getInfoTypeForString('BONUS_MANA_FIRE'):
												if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_FIRE'))==1:													
													bDispel = false									
											if iBonus == gc.getInfoTypeForString('BONUS_MANA_AIR'):
												if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_AIR'))==1:													
													bDispel = false									
											if iBonus == gc.getInfoTypeForString('BONUS_MANA_WATER'):
												if pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_WATER'))==1:													
													bDispel = false	
																					
										if bDispel:
											if not (iiX==iX and iiY==iY):
#												CyInterface().addImmediateMessage('Searching for stuff to Dispel', "AS2D_NEW_ERA")																														
												pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, iiX, iiY, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)																																			
												return 1
											if pUnit.canCast(gc.getInfoTypeForString('SPELL_DISPEL_MAGIC'),false):
												pUnit.cast(gc.getInfoTypeForString('SPELL_DISPEL_MAGIC'))
												return 1
#Dispel more if we seek Tower Victory Condition
			if (pPlayer.getArcaneTowerVictoryFlag()>0):												
				iBestCount=0
				pBestCity=0
				for icity in range(pPlayer.getNumCities()):
					pCity = pPlayer.getCity(icity)
					if not pCity.isNone():			
						iCount=0
						for iI in range(1, 21):
							pPlot2 = pCity.getCityIndexPlot(iI)					
							if not (pPlot2.isNone() or pPlot2.isImpassable() or pPlot2.isVisibleEnemyUnit(pUnit.getOwner())):
								if pPlot2.getOwner()==pUnit.getOwner():							
									if pPlot2.getBonusType(-1) != -1:
										iBonus = pPlot2.getBonusType(TeamTypes.NO_TEAM)
										if gc.getBonusInfo(iBonus).getBonusClassType() == gc.getInfoTypeForString('BONUSCLASS_MANA'):					
											iCount=iCount+1
										if gc.getBonusInfo(iBonus).getBonusClassType() == gc.getInfoTypeForString('BONUSCLASS_RAWMANA'):					
											iCount=iCount+1

						if (iCount>iBestCount):
							pBestCity=pCity
							iBestCount=iCount
				if (pBestCity!=0):
					pCPlot = pBestCity.plot()
					CX = pCPlot.getX()
					CY = pCPlot.getY()	
					pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, CX, CY, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)														
					return 1
												
												
#found no mana, return 2 so UNITAI is set to UNITAI_TERRAFORMER
												
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

			possiblemana=0
			for i in range (CyMap().numPlots()):
				pPlot = CyMap().plotByIndex(i)
				if (pPlot.getOwner()==ePlayer):
					if pPlot.getBonusType(-1) != -1:
						iBonus = pPlot.getBonusType(TeamTypes.NO_TEAM)
						if gc.getBonusInfo(iBonus).getBonusClassType() == gc.getInfoTypeForString('BONUSCLASS_MANA'):					
							possiblemana=possiblemana+1
						if gc.getBonusInfo(iBonus).getBonusClassType() == gc.getInfoTypeForString('BONUSCLASS_RAWMANA'):					
							possiblemana=possiblemana+1

			if possiblemana<4:
				return 0
			
			if pPlayer.isHasTech(gc.getInfoTypeForString('TECH_ALTERATION')):
				if pPlayer.getBuildingClassCount(gc.getInfoTypeForString('BUILDINGCLASS_TOWER_OF_ALTERATION'))==0:
					return 1
			
			if pPlayer.isHasTech(gc.getInfoTypeForString('TECH_DIVINATION')):
				if pPlayer.getBuildingClassCount(gc.getInfoTypeForString('BUILDINGCLASS_TOWER_OF_DIVINATION'))==0:
					return 2

			if pPlayer.isHasTech(gc.getInfoTypeForString('TECH_NECROMANCY')):
				if pPlayer.getBuildingClassCount(gc.getInfoTypeForString('BUILDINGCLASS_TOWER_OF_NECROMANCY'))==0:
					if not pPlayer.isCivic(CvUtil.findInfoTypeNum(gc.getCivicInfo,gc.getNumCivicInfos(),'CIVIC_OVERCOUNCIL')):
						return 3

			if pPlayer.isHasTech(gc.getInfoTypeForString('TECH_ELEMENTALISM')):
				if pPlayer.getBuildingClassCount(gc.getInfoTypeForString('BUILDINGCLASS_TOWER_OF_THE_ELEMENTS'))==0:
					return 4
				
		if flag==1:
			if pPlayer.getBuildingClassCount(gc.getInfoTypeForString('BUILDINGCLASS_TOWER_OF_ALTERATION'))>0:			
				return 0
			else:
				return 1
				
		if flag==2:
			if pPlayer.getBuildingClassCount(gc.getInfoTypeForString('BUILDINGCLASS_TOWER_OF_DIVINATION'))>0:			
				return 0
			else:
				return 2

		if flag==3:
			if pPlayer.getBuildingClassCount(gc.getInfoTypeForString('BUILDINGCLASS_TOWER_OF_NECROMANCY'))>0:			
				return 0
			else:
				return 3

		if flag==4:
			if pPlayer.getBuildingClassCount(gc.getInfoTypeForString('BUILDINGCLASS_TOWER_OF_THE_ELEMENTS'))>0:			
				return 0
			else:
				return 4
				
		return 0
