# Sid Meier's Civilization 4
# Copyright Firaxis Games 2006
#
# CvEventManager
# This class is passed an argsList from CvAppInterface.onEvent
# The argsList can contain anything from mouse location to key info
# The EVENTLIST that are being notified can be found

from CvPythonExtensions import *
import CvUtil
import CvScreensInterface
import CvDebugTools
#import CvWBPopups
import PyHelpers
import Popup as PyPopup
import CvCameraControls
import CvTopCivs
import sys
#import CvWorldBuilderScreen
import CvAdvisorUtils
import CvTechChooser

import CvIntroMovieScreen
import CustomFunctions
import ScenarioFunctions

#FfH: Card Game: begin
import CvSomniumInterface
import CvCorporationScreen
#FfH: Card Game: end

#FfH: Added by Kael 10/15/2008 for OOS Logging
import OOSLogger
#FfH: End Add

## Ultrapack ##
import WBCityEditScreen
import WBUnitScreen
import WBPlayerScreen
import WBGameDataScreen
import WBPlotScreen
import CvPlatyBuilderScreen
## Ultrapack ##

import Blizzards		#Added in Blizzards: TC01

# globals
cf = CustomFunctions.CustomFunctions()
gc = CyGlobalContext()
localText = CyTranslator()
PyPlayer = PyHelpers.PyPlayer
PyInfo = PyHelpers.PyInfo
sf = ScenarioFunctions.ScenarioFunctions()
game = gc.getGame()

#FfH: Card Game: begin
cs = CvCorporationScreen.cs
#FfH: Card Game: end

Blizzards = Blizzards.Blizzards()		#Added in Blizzards: TC01

# globals
###################################################
class CvEventManager:
	def __init__(self):
		#################### ON EVENT MAP ######################
		#print "EVENTMANAGER INIT"

		self.bCtrl = False
		self.bShift = False
		self.bAlt = False
		self.bAllowCheats = False

		# OnEvent Enums
		self.EventLButtonDown=1
		self.EventLcButtonDblClick=2
		self.EventRButtonDown=3
		self.EventBack=4
		self.EventForward=5
		self.EventKeyDown=6
		self.EventKeyUp=7

		self.__LOG_MOVEMENT = 0
		self.__LOG_BUILDING = 0
		self.__LOG_COMBAT = 0
		self.__LOG_CONTACT = 0
		self.__LOG_IMPROVEMENT =0
		self.__LOG_CITYLOST = 0
		self.__LOG_CITYBUILDING = 0
		self.__LOG_TECH = 0
		self.__LOG_UNITBUILD = 0
		self.__LOG_UNITKILLED = 1
		self.__LOG_UNITLOST = 0
		self.__LOG_UNITPROMOTED = 0
		self.__LOG_UNITSELECTED = 0
		self.__LOG_UNITPILLAGE = 0
		self.__LOG_GOODYRECEIVED = 0
		self.__LOG_GREATPERSON = 0
		self.__LOG_RELIGION = 0
		self.__LOG_RELIGIONSPREAD = 0
		self.__LOG_GOLDENAGE = 0
		self.__LOG_ENDGOLDENAGE = 0
		self.__LOG_WARPEACE = 0
		self.__LOG_PUSH_MISSION = 0

		## EVENTLIST
		self.EventHandlerMap = {
			'mouseEvent'			: CvEventManager.onMouseEvent.__get__(self,CvEventManager),
			'kbdEvent' 				: CvEventManager.onKbdEvent.__get__(self,CvEventManager),
			'ModNetMessage'					: CvEventManager.onModNetMessage.__get__(self,CvEventManager),
			'Init'					: CvEventManager.onInit.__get__(self,CvEventManager),
			'Update'				: CvEventManager.onUpdate.__get__(self,CvEventManager),
			'UnInit'				: CvEventManager.onUnInit.__get__(self,CvEventManager),
			'OnSave'				: CvEventManager.onSaveGame.__get__(self,CvEventManager),
			'OnPreSave'				: CvEventManager.onPreSave.__get__(self,CvEventManager),
			'OnLoad'				: CvEventManager.onLoadGame.__get__(self,CvEventManager),
			'GameStart'				: CvEventManager.onGameStart.__get__(self,CvEventManager),
			'GameEnd'				: CvEventManager.onGameEnd.__get__(self,CvEventManager),
			'plotRevealed' 			: CvEventManager.onPlotRevealed.__get__(self,CvEventManager),
			'plotFeatureRemoved' 	: CvEventManager.onPlotFeatureRemoved.__get__(self,CvEventManager),
			'plotPicked'			: CvEventManager.onPlotPicked.__get__(self,CvEventManager),
			'nukeExplosion'			: CvEventManager.onNukeExplosion.__get__(self,CvEventManager),
			'gotoPlotSet'			: CvEventManager.onGotoPlotSet.__get__(self,CvEventManager),
			'BeginGameTurn'			: CvEventManager.onBeginGameTurn.__get__(self,CvEventManager),
			'EndGameTurn'			: CvEventManager.onEndGameTurn.__get__(self,CvEventManager),
			'BeginPlayerTurn'		: CvEventManager.onBeginPlayerTurn.__get__(self,CvEventManager),
			'EndPlayerTurn'			: CvEventManager.onEndPlayerTurn.__get__(self,CvEventManager),
			'endTurnReady'			: CvEventManager.onEndTurnReady.__get__(self,CvEventManager),
			'combatResult'			: CvEventManager.onCombatResult.__get__(self,CvEventManager),
			'combatLogCalc'			: CvEventManager.onCombatLogCalc.__get__(self,CvEventManager),
			'combatLogHit'			: CvEventManager.onCombatLogHit.__get__(self,CvEventManager),
			'improvementBuilt'		: CvEventManager.onImprovementBuilt.__get__(self,CvEventManager),
			'improvementDestroyed'	: CvEventManager.onImprovementDestroyed.__get__(self,CvEventManager),
			'routeBuilt'			: CvEventManager.onRouteBuilt.__get__(self,CvEventManager),
			'firstContact'			: CvEventManager.onFirstContact.__get__(self,CvEventManager),
			'cityBuilt'				: CvEventManager.onCityBuilt.__get__(self,CvEventManager),
			'cityRazed'				: CvEventManager.onCityRazed.__get__(self,CvEventManager),
			'cityAcquired' 			: CvEventManager.onCityAcquired.__get__(self,CvEventManager),
			'cityAcquiredAndKept' 	: CvEventManager.onCityAcquiredAndKept.__get__(self,CvEventManager),
			'cityLost'				: CvEventManager.onCityLost.__get__(self,CvEventManager),
			'cultureExpansion' 		: CvEventManager.onCultureExpansion.__get__(self,CvEventManager),
			'cityGrowth' 			: CvEventManager.onCityGrowth.__get__(self,CvEventManager),
			'cityDoTurn' 			: CvEventManager.onCityDoTurn.__get__(self,CvEventManager),
			'cityBuildingUnit'	: CvEventManager.onCityBuildingUnit.__get__(self,CvEventManager),
			'cityBuildingBuilding'	: CvEventManager.onCityBuildingBuilding.__get__(self,CvEventManager),
			'cityRename'				: CvEventManager.onCityRename.__get__(self,CvEventManager),
			'cityHurry'				: CvEventManager.onCityHurry.__get__(self,CvEventManager),
			'selectionGroupPushMission'		: CvEventManager.onSelectionGroupPushMission.__get__(self,CvEventManager),
			'unitMove' 				: CvEventManager.onUnitMove.__get__(self,CvEventManager),
			'unitSetXY' 			: CvEventManager.onUnitSetXY.__get__(self,CvEventManager),
			'unitCreated' 			: CvEventManager.onUnitCreated.__get__(self,CvEventManager),
			'unitBuilt' 			: CvEventManager.onUnitBuilt.__get__(self,CvEventManager),
			'unitKilled'			: CvEventManager.onUnitKilled.__get__(self,CvEventManager),
			'unitLost'				: CvEventManager.onUnitLost.__get__(self,CvEventManager),
			'unitPromoted'			: CvEventManager.onUnitPromoted.__get__(self,CvEventManager),
			'unitSelected'			: CvEventManager.onUnitSelected.__get__(self,CvEventManager),
			'UnitRename'				: CvEventManager.onUnitRename.__get__(self,CvEventManager),
			'unitPillage'				: CvEventManager.onUnitPillage.__get__(self,CvEventManager),
			'unitSpreadReligionAttempt'	: CvEventManager.onUnitSpreadReligionAttempt.__get__(self,CvEventManager),
			'unitGifted'				: CvEventManager.onUnitGifted.__get__(self,CvEventManager),
			'unitBuildImprovement'				: CvEventManager.onUnitBuildImprovement.__get__(self,CvEventManager),
			'goodyReceived'        	: CvEventManager.onGoodyReceived.__get__(self,CvEventManager),
			'greatPersonBorn'      	: CvEventManager.onGreatPersonBorn.__get__(self,CvEventManager),
			'buildingBuilt' 		: CvEventManager.onBuildingBuilt.__get__(self,CvEventManager),
			'projectBuilt' 			: CvEventManager.onProjectBuilt.__get__(self,CvEventManager),
			'techAcquired'			: CvEventManager.onTechAcquired.__get__(self,CvEventManager),
			'techSelected'			: CvEventManager.onTechSelected.__get__(self,CvEventManager),
			'religionFounded'		: CvEventManager.onReligionFounded.__get__(self,CvEventManager),
			'religionSpread'		: CvEventManager.onReligionSpread.__get__(self,CvEventManager),
			'religionRemove'		: CvEventManager.onReligionRemove.__get__(self,CvEventManager),
			'corporationFounded'	: CvEventManager.onCorporationFounded.__get__(self,CvEventManager),
			'corporationSpread'		: CvEventManager.onCorporationSpread.__get__(self,CvEventManager),
			'corporationRemove'		: CvEventManager.onCorporationRemove.__get__(self,CvEventManager),
			'goldenAge'				: CvEventManager.onGoldenAge.__get__(self,CvEventManager),
			'endGoldenAge'			: CvEventManager.onEndGoldenAge.__get__(self,CvEventManager),
			'chat' 					: CvEventManager.onChat.__get__(self,CvEventManager),
			'victory'				: CvEventManager.onVictory.__get__(self,CvEventManager),
			'vassalState'			: CvEventManager.onVassalState.__get__(self,CvEventManager),
			'changeWar'				: CvEventManager.onChangeWar.__get__(self,CvEventManager),
			'setPlayerAlive'		: CvEventManager.onSetPlayerAlive.__get__(self,CvEventManager),
			'playerChangeStateReligion'		: CvEventManager.onPlayerChangeStateReligion.__get__(self,CvEventManager),
			'playerGoldTrade'		: CvEventManager.onPlayerGoldTrade.__get__(self,CvEventManager),
			'windowActivation'		: CvEventManager.onWindowActivation.__get__(self,CvEventManager),
			'gameUpdate'			: CvEventManager.onGameUpdate.__get__(self,CvEventManager),		# sample generic event
		}

		################## Events List ###############################
		#
		# Dictionary of Events, indexed by EventID (also used at popup context id)
		#   entries have name, beginFunction, applyFunction [, randomization weight...]
		#
		# Normal events first, random events after
		#
		################## Events List ###############################
		self.Events={
			CvUtil.EventEditCityName : ('EditCityName', self.__eventEditCityNameApply, self.__eventEditCityNameBegin),
			CvUtil.EventPlaceObject : ('PlaceObject', self.__eventPlaceObjectApply, self.__eventPlaceObjectBegin),
			CvUtil.EventAwardTechsAndGold: ('AwardTechsAndGold', self.__eventAwardTechsAndGoldApply, self.__eventAwardTechsAndGoldBegin),
			CvUtil.EventEditUnitName : ('EditUnitName', self.__eventEditUnitNameApply, self.__eventEditUnitNameBegin),
## Platy Builder ##
			CvUtil.EventWBLandmarkPopup : ('WBLandmarkPopup', self.__eventWBLandmarkPopupApply, self.__eventWBScriptPopupBegin),
			CvUtil.EventShowWonder: ('ShowWonder', self.__eventShowWonderApply, self.__eventShowWonderBegin),
			1111 : ('WBPlayerScript', self.__eventWBPlayerScriptPopupApply, self.__eventWBScriptPopupBegin),
			2222 : ('WBCityScript', self.__eventWBCityScriptPopupApply, self.__eventWBScriptPopupBegin),
			3333 : ('WBUnitScript', self.__eventWBUnitScriptPopupApply, self.__eventWBScriptPopupBegin),
			4444 : ('WBGameScript', self.__eventWBGameScriptPopupApply, self.__eventWBScriptPopupBegin),
			5555 : ('WBPlotScript', self.__eventWBPlotScriptPopupApply, self.__eventWBScriptPopupBegin),
#Magister Start
			6666 : ('WBPlayerRename', self.__eventEditPlayerNameApply, self.__eventEditPlayerNameBegin),
			6777 : ('WBPlayerRename', self.__eventEditCivNameApply, self.__eventEditCivNameBegin),
			6888 : ('WBPlayerRename', self.__eventEditCivShortNameApply, self.__eventEditCivShortNameBegin),
			6999 : ('WBPlayerRename', self.__eventEditCivAdjApply, self.__eventEditCivAdjBegin),
#Magister Stop
## Platy Builder ##
		}
## FfH Card Game: begin
		self.Events[CvUtil.EventSelectSolmniumPlayer] = ('selectSolmniumPlayer', self.__EventSelectSolmniumPlayerApply, self.__EventSelectSolmniumPlayerBegin)
		self.Events[CvUtil.EventSolmniumAcceptGame] = ('solmniumAcceptGame', self.__EventSolmniumAcceptGameApply, self.__EventSolmniumAcceptGameBegin)
		self.Events[CvUtil.EventSolmniumConcedeGame] = ('solmniumConcedeGame', self.__EventSolmniumConcedeGameApply, self.__EventSolmniumConcedeGameBegin)
## FfH Card Game: end

#################### EVENT STARTERS ######################
	def handleEvent(self, argsList):
		'EventMgr entry point'
		# extract the last 6 args in the list, the first arg has already been consumed
		self.origArgsList = argsList	# point to original
		tag = argsList[0]				# event type string
		idx = len(argsList)-6
		bDummy = False
		self.bDbg, bDummy, self.bAlt, self.bCtrl, self.bShift, self.bAllowCheats = argsList[idx:]
		ret = 0
		if self.EventHandlerMap.has_key(tag):
			fxn = self.EventHandlerMap[tag]
			ret = fxn(argsList[1:idx])
		return ret

#################### EVENT APPLY ######################
	def beginEvent( self, context, argsList=-1 ):
		'Begin Event'
		entry = self.Events[context]
		return entry[2]( argsList )

	def applyEvent( self, argsList ):
		'Apply the effects of an event '
		context, playerID, netUserData, popupReturn = argsList

		if context == CvUtil.PopupTypeEffectViewer:
			return CvDebugTools.g_CvDebugTools.applyEffectViewer( playerID, netUserData, popupReturn )

		entry = self.Events[context]

		if ( context not in CvUtil.SilentEvents ):
			self.reportEvent(entry, context, (playerID, netUserData, popupReturn) )
		return entry[1]( playerID, netUserData, popupReturn )   # the apply function

	def reportEvent(self, entry, context, argsList):
		'Report an Event to Events.log '
		if (gc.getGame().getActivePlayer() != -1):
			message = "DEBUG Event: %s (%s)" %(entry[0], gc.getActivePlayer().getName())
			CyInterface().addImmediateMessage(message,"")
			CvUtil.pyPrint(message)
		return 0

#################### ON EVENTS ######################
	def onKbdEvent(self, argsList):
		'keypress handler - return 1 if the event was consumed'

		eventType,key,mx,my,px,py = argsList
		game = gc.getGame()

		if (self.bAllowCheats):
			# notify debug tools of input to allow it to override the control
			argsList = (eventType,key,self.bCtrl,self.bShift,self.bAlt,mx,my,px,py,gc.getGame().isNetworkMultiPlayer())
			if ( CvDebugTools.g_CvDebugTools.notifyInput(argsList) ):
				return 0

		if ( eventType == self.EventKeyDown ):
			theKey=int(key)

#FfH: Added by Kael 07/05/2008
			if (theKey == int(InputTypes.KB_LEFT)):
				if self.bCtrl:
						CyCamera().SetBaseTurn(CyCamera().GetBaseTurn() - 45.0)
						return 1
				elif self.bShift:
						CyCamera().SetBaseTurn(CyCamera().GetBaseTurn() - 10.0)
						return 1

			if (theKey == int(InputTypes.KB_RIGHT)):
					if self.bCtrl:
							CyCamera().SetBaseTurn(CyCamera().GetBaseTurn() + 45.0)
							return 1
					elif self.bShift:
							CyCamera().SetBaseTurn(CyCamera().GetBaseTurn() + 10.0)
							return 1
#FfH: End Add

			CvCameraControls.g_CameraControls.handleInput( theKey )

			if (self.bAllowCheats):
				# Shift - T (Debug - No MP)
				if (theKey == int(InputTypes.KB_T)):
					if ( self.bShift ):
						CvEventManager.beginEvent(self,CvUtil.EventAwardTechsAndGold)
						#self.beginEvent(CvUtil.EventCameraControlPopup)
						return 1

				elif (theKey == int(InputTypes.KB_W)):
					if ( self.bShift and self.bCtrl):
						CvEventManager.beginEvent(self,CvUtil.EventShowWonder)
						return 1

				# Shift - ] (Debug - currently mouse-overd unit, health += 10
				elif (theKey == int(InputTypes.KB_LBRACKET) and self.bShift ):
					unit = CyMap().plot(px, py).getUnit(0)
					if ( not unit.isNone() ):
						d = min( unit.maxHitPoints()-1, unit.getDamage() + 10 )
						unit.setDamage( d, PlayerTypes.NO_PLAYER )

				# Shift - [ (Debug - currently mouse-overd unit, health -= 10
				elif (theKey == int(InputTypes.KB_RBRACKET) and self.bShift ):
					unit = CyMap().plot(px, py).getUnit(0)
					if ( not unit.isNone() ):
						d = max( 0, unit.getDamage() - 10 )
						unit.setDamage( d, PlayerTypes.NO_PLAYER )

				elif (theKey == int(InputTypes.KB_F1)):
					if ( self.bShift ):
						CvScreensInterface.replayScreen.showScreen(False)
						return 1
					# don't return 1 unless you want the input consumed

				elif (theKey == int(InputTypes.KB_F2)):
					if ( self.bShift ):
						import CvDebugInfoScreen
						CvScreensInterface.showDebugInfoScreen()
						return 1

				elif (theKey == int(InputTypes.KB_F3)):
					if ( self.bShift ):
						CvScreensInterface.showDanQuayleScreen(())
						return 1

				elif (theKey == int(InputTypes.KB_F4)):
					if ( self.bShift ):
						CvScreensInterface.showUnVictoryScreen(())
						return 1

		return 0

	def onModNetMessage(self, argsList):
		'Called whenever CyMessageControl().sendModNetMessage() is called - this is all for you modders!'

		iData1, iData2, iData3, iData4, iData5 = argsList

#		print("Modder's net message!")
#		CvUtil.pyPrint( 'onModNetMessage' )

#FfH Card Game: begin
		if iData1 == CvUtil.Somnium : # iData1 == 0 : Solmnium message, iData2 = function, iData3 to iData5 = parameters
			if iData2 == 0 :
				if (iData3 == gc.getGame().getActivePlayer()):
					self.__EventSelectSolmniumPlayerBegin()
			elif iData2 == 1 :
				if (iData4 == gc.getGame().getActivePlayer()):
					self.__EventSolmniumConcedeGameBegin((iData3, iData4))
			else :
				cs.applyAction(iData2, iData3, iData4, iData5)
# FfH Card Game: end

## OOS fix by Snarko
		elif (iData1 == CvUtil.ChangeCiv): #iData1 is unused, to allow for a condition here. It must not be zero (would trigger somnium)
			CyGame().reassignPlayerAdvanced(iData2, iData3, -1)
## Declare war to Barbarians.
		elif (iData1 == CvUtil.BarbarianWar):
			gc.getTeam(iData2).declareWar(iData3, False, WarPlanTypes.WARPLAN_TOTAL)
		elif (iData1 == CvUtil.HyboremWhisper):
			pPlayer = gc.getPlayer(iData2)
			pPlot = CyMap().plot(iData3, iData4)
			pCity = pPlot.getPlotCity()
			pPlayer.acquireCity(pCity, False, True)

	def onInit(self, argsList):
		'Called when Civ starts up'
		CvUtil.pyPrint( 'OnInit' )

	def onUpdate(self, argsList):
		'Called every frame'
		fDeltaTime = argsList[0]

		# allow camera to be updated
		CvCameraControls.g_CameraControls.onUpdate( fDeltaTime )

	def onWindowActivation(self, argsList):
		'Called when the game window activates or deactivates'
		bActive = argsList[0]

	def onUnInit(self, argsList):
		'Called when Civ shuts down'
		CvUtil.pyPrint('OnUnInit')

	def onPreSave(self, argsList):
		"called before a game is actually saved"
		CvUtil.pyPrint('OnPreSave')

	def onSaveGame(self, argsList):
		"return the string to be saved - Must be a string"
		return ""

	def onLoadGame(self, argsList):
		CvAdvisorUtils.resetNoLiberateCities()
		return 0

	def onGameStart(self, argsList):
		'Called at the start of the game'

		if CyGame().getWBMapScript():
			sf.gameStart()
		else:
			introMovie = CvIntroMovieScreen.CvIntroMovieScreen()
			introMovie.interfaceScreen()

		if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_THAW):
# Enhanced End of Winter - Adpated from FlavourMod
			'''		
			iDesert = gc.getInfoTypeForString('TERRAIN_DESERT')
			iGrass = gc.getInfoTypeForString('TERRAIN_GRASS')
			iPlains = gc.getInfoTypeForString('TERRAIN_PLAINS')
			iSnow = gc.getInfoTypeForString('TERRAIN_SNOW')
			iTundra = gc.getInfoTypeForString('TERRAIN_TUNDRA')
			for i in range (CyMap().numPlots()):
				pPlot = CyMap().plotByIndex(i)
				if pPlot.getFeatureType() == -1:
					if pPlot.getImprovementType() == -1:
						if pPlot.isWater() == False:
							iTerrain = pPlot.getTerrainType()
							if iTerrain == iTundra:
								pPlot.setTempTerrainType(iSnow, CyGame().getSorenRandNum(90, "Bob") + 10)
							if iTerrain == iGrass:
								pPlot.setTempTerrainType(iTundra, CyGame().getSorenRandNum(90, "Bob") + 10)
							if iTerrain == iPlains:
								pPlot.setTempTerrainType(iTundra, CyGame().getSorenRandNum(90, "Bob") + 10)
							if iTerrain == iDesert:
								pPlot.setTempTerrainType(iPlains, CyGame().getSorenRandNum(90, "Bob") + 10)
			'''
			FLAT_WORLDS = [ # map scripts with wrapping but no equator
				"ErebusWrap", "Erebus", "Erebus_mst",
			]
			MAX_EOW_PERCENTAGE = 0.25 						# percentage of EoW on total game turns 
			THAW_DELAY_PERCENTAGE = 0.05 					# don't start thawing for x percent of EoW

			# forest varieties
			DECIDUOUS_FOREST = 0
			CONIFEROUS_FOREST = 1
			SNOWY_CONIFEROUS_FOREST = 2
			
			dice = gc.getGame().getSorenRand()

			iDesert = gc.getInfoTypeForString('TERRAIN_DESERT')
			iGrass = gc.getInfoTypeForString('TERRAIN_GRASS')
			iMarsh = gc.getInfoTypeForString('TERRAIN_MARSH')
			iPlains = gc.getInfoTypeForString('TERRAIN_PLAINS')
			iSnow = gc.getInfoTypeForString('TERRAIN_SNOW')
			iTundra = gc.getInfoTypeForString('TERRAIN_TUNDRA')
			iIce = gc.getInfoTypeForString('FEATURE_ICE')
			iForest = gc.getInfoTypeForString('FEATURE_FOREST')
			iJungle = gc.getInfoTypeForString('FEATURE_JUNGLE')
			iFloodplains = gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS')
			iBlizzard = gc.getInfoTypeForString('FEATURE_BLIZZARD')

#			iTotalGameTurns = gc.getGameSpeedInfo(CyGame().getGameSpeedType()).getGameTurnInfo(0).iNumGameTurnsPerIncrement
#			iMaxEOWTurns = max(1, int(iTotalGameTurns * MAX_EOW_PERCENTAGE))
#			iThawDelayTurns = max(1, int(iMaxEOWTurns * THAW_DELAY_PERCENTAGE))

			iMaxLatitude = max(CyMap().getTopLatitude(), abs(CyMap().getBottomLatitude()))
			bIsFlatWorld = not (CyMap().isWrapX() or CyMap().isWrapY()) or CyMap().getMapScriptName() in FLAT_WORLDS

			for i in range (CyMap().numPlots()):
				pPlot = CyMap().plotByIndex(i)
				eTerrain = pPlot.getTerrainType()
				eFeature = pPlot.getFeatureType()
				iVariety = pPlot.getFeatureVariety()
				eBonus = pPlot.getBonusType(TeamTypes.NO_TEAM)

				iTurns = dice.get(110, "Thaw") + 40
				iTurns = (iTurns * gc.getGameSpeedInfo(CyGame().getGameSpeedType()).getVictoryDelayPercent()) / 100
				if not bIsFlatWorld:
					iLatitude = abs(pPlot.getLatitude())
					iTurns = int(iTurns * ((float(iLatitude) / iMaxLatitude) ** 0.4))
#				iTurns += iThawDelayTurns

				# cover erebus' oceans and lakes in ice
				if pPlot.isWater():
					if bIsFlatWorld:
						if dice.get(100, "Bob") < 90:
							pPlot.setTempFeatureType(iIce, 0, iTurns)
					elif iLatitude + 10 > dice.get(50, "Bob"):
						pPlot.setTempFeatureType(iIce, 0, iTurns)

				# change terrains to colder climate versions
				if eTerrain == iTundra:
					if dice.get(100, "Tundra to Snow") < 90:
						pPlot.setTempTerrainType(iSnow, iTurns)
				elif eTerrain == iGrass:
					if eFeature != iJungle: 
						if dice.get(100, "Grass to Snow or Tundra") < 60:
							pPlot.setTempTerrainType(iSnow, iTurns)
						else:
							pPlot.setTempTerrainType(iTundra, iTurns)
				elif eTerrain == iPlains:
					if dice.get(100, "Plains to Snow or Tundra") < 30:
						pPlot.setTempTerrainType(iSnow, iTurns)
					else:
						pPlot.setTempTerrainType(iTundra, iTurns)
				elif eTerrain == iDesert:
					if dice.get(100, "Desert to Tundra or Plains") < 50:
						pPlot.setTempTerrainType(iTundra, iTurns)
					else:
						pPlot.setTempTerrainType(iPlains, iTurns)
				elif eTerrain == iMarsh:
					pPlot.setTempTerrainType(iGrass, iTurns)

				# change forests to colder climate versions
				if eFeature == iForest:
					if iVariety == DECIDUOUS_FOREST:
						pPlot.setTempFeatureType(iForest, CONIFEROUS_FOREST, iTurns)
					elif iVariety == CONIFEROUS_FOREST:
						pPlot.setTempFeatureType(iForest, SNOWY_CONIFEROUS_FOREST, iTurns)
				elif eFeature == iJungle:
					pPlot.setTempFeatureType(iForest, DECIDUOUS_FOREST, iTurns)
				elif eFeature == iFloodplains:
					pPlot.setTempFeatureType(FeatureTypes.NO_FEATURE, -1, iTurns)
				elif eFeature == FeatureTypes.NO_FEATURE:
					if dice.get(100, "Spawn Blizzard") < 5:
						pPlot.setFeatureType(iBlizzard, -1)

				# temporarily remove invalid bonuses or replace them (if food) with a valid surrogate
				if eBonus != BonusTypes.NO_BONUS and not gc.getBonusInfo(eBonus).isMana():
					pPlot.setBonusType(BonusTypes.NO_BONUS)
					if not pPlot.canHaveBonus(eBonus, True):
						if gc.getBonusInfo(eBonus).getYieldChange(YieldTypes.YIELD_FOOD) > 0:
							iPossibleTempFoodBonuses = []
							for iLoopBonus in range(gc.getNumBonusInfos()):
								if gc.getBonusInfo(iLoopBonus).getYieldChange(YieldTypes.YIELD_FOOD) > 0:
									if pPlot.canHaveBonus(iLoopBonus, True):
										iPossibleTempFoodBonuses.append(iLoopBonus)
							pPlot.setBonusType(eBonus)
							if len(iPossibleTempFoodBonuses) > 0:
								pPlot.setTempBonusType(iPossibleTempFoodBonuses[dice.get(len(iPossibleTempFoodBonuses), "Bob")], iTurns)
							else:
								pPlot.setTempBonusType(BonusTypes.NO_BONUS, iTurns)
						else:
							pPlot.setBonusType(eBonus)
							pPlot.setTempBonusType(BonusTypes.NO_BONUS, iTurns)
					else:
						pPlot.setBonusType(eBonus)
			Blizzards.doBlizzardTurn()
# End Enhanced End of Winter

		for iPlayer in range(gc.getMAX_PLAYERS()):
			player = gc.getPlayer(iPlayer)
			if player.isAlive():
				if player.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_ELOHIM'):
					cf.showUniqueImprovements(iPlayer)

		if not gc.getGame().isNetworkMultiPlayer():
			t = "TROPHY_FEAT_INTRODUCTION"
			if not CyGame().isHasTrophy(t):
				CyGame().changeTrophyValue(t, 1)
				sf.addPopupWB(CyTranslator().getText("TXT_KEY_FFH_INTRO",()),'art/interface/popups/FfHIntro.dds')

		if CyGame().isOption(gc.getInfoTypeForString('GAMEOPTION_NO_BARBARIANS')) == False and (not CyGame().getWBMapScript()):
			iGoblinFort = gc.getInfoTypeForString('IMPROVEMENT_GOBLIN_FORT')
			bPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
			for i in range (CyMap().numPlots()):
				pPlot = CyMap().plotByIndex(i)
				if pPlot.getImprovementType() == iGoblinFort:
					newDefenseUnit1 = bPlayer.initUnit(gc.getInfoTypeForString('UNIT_ARCHER_SCORPION_CLAN'), pPlot.getX(), pPlot.getY(), UnitAITypes.UNITAI_LAIRGUARDIAN, DirectionTypes.DIRECTION_SOUTH)
					newDefenseUnit1.setUnitAIType(gc.getInfoTypeForString('UNITAI_LAIRGUARDIAN'))

		if (gc.getGame().getGameTurnYear() == gc.getDefineINT("START_YEAR") and not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_ADVANCED_START)):
			if not CyGame().getWBMapScript():
				for iPlayer in range(gc.getMAX_PLAYERS()):
					player = gc.getPlayer(iPlayer)
					if player.isAlive() and player.isHuman():
						popupInfo = CyPopupInfo()
						popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
						popupInfo.setText(u"showDawnOfMan")
						popupInfo.addPopup(iPlayer)
		else:
			CyInterface().setSoundSelectionReady(True)

		if gc.getGame().isPbem():
			for iPlayer in range(gc.getMAX_PLAYERS()):
				player = gc.getPlayer(iPlayer)
				if player.isAlive() and player.isHuman():
					popupInfo = CyPopupInfo()
					popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_DETAILS)
					popupInfo.setOption1(False)
					popupInfo.addPopup(iPlayer)

		# Super Forts
		CyMap().calculateCanalAndChokePoints()

		CvAdvisorUtils.resetNoLiberateCities()

	def onGameEnd(self, argsList):
		'Called at the End of the game'
		print("Game is ending")
		return

	def onBeginGameTurn(self, argsList):
		'Called at the beginning of the end of each turn'
		iGameTurn = argsList[0]

		if not CyGame().isUnitClassMaxedOut(gc.getInfoTypeForString('UNITCLASS_ORTHUS'), 0):
			if not CyGame().isOption(gc.getInfoTypeForString('GAMEOPTION_NO_ORTHUS')):
				iOrthusTurn = 75
				bOrthus = False
				if CyGame().getGameSpeedType() == gc.getInfoTypeForString('GAMESPEED_QUICK'):
					if iGameTurn >= iOrthusTurn / 3 * 2:
						bOrthus = True
				elif CyGame().getGameSpeedType() == gc.getInfoTypeForString('GAMESPEED_NORMAL'):
					if iGameTurn >= iOrthusTurn:
						bOrthus = True
				elif CyGame().getGameSpeedType() == gc.getInfoTypeForString('GAMESPEED_EPIC'):
					if iGameTurn >= iOrthusTurn * 3 / 2:
						bOrthus = True
				elif CyGame().getGameSpeedType() == gc.getInfoTypeForString('GAMESPEED_MARATHON'):
					if iGameTurn >= iOrthusTurn * 3:
						bOrthus = True
				if bOrthus:
					bValid=True
					for i in range (CyMap().numPlots()):
						pPlot = CyMap().plotByIndex(i)
						iPlot = -1
						if pPlot.getImprovementType()==gc.getInfoTypeForString('IMPROVEMENT_GOBLIN_FORT'):
							bPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
							if not pPlot.isVisibleOtherUnit(gc.getBARBARIAN_PLAYER()):
								bPlayer.initUnit(gc.getInfoTypeForString('UNIT_ORTHUS'), pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
								bValid=False
								break
					if bValid:
						iUnit = gc.getInfoTypeForString('UNIT_ORTHUS')
						cf.addUnit(iUnit)
						if( CyGame().getAIAutoPlay(CyGame().getActivePlayer()) == 0 ) :
							cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_ORTHUS_CREATION",()), str(gc.getUnitInfo(iUnit).getImage()))

		if not CyGame().isOption(gc.getInfoTypeForString('GAMEOPTION_NO_PLOT_COUNTER')):
			cf.doHellTerrain()

		if CyGame().getWBMapScript():
			sf.doTurn()

# FfH Card Game: begin
		cs.doTurn()
# FfH Card Game: end

		Blizzards.doBlizzardTurn()		#Added in Blizzards: TC01
		
#		if( CyGame().getAIAutoPlay(self) == 0 ) :
		if( game.getAIAutoPlay(game.getActivePlayer()) == 0 ) :
			CvTopCivs.CvTopCivs().turnChecker(iGameTurn)

	def onEndGameTurn(self, argsList):
		'Called at the end of the end of each turn'
		iGameTurn = argsList[0]

	def onBeginPlayerTurn(self, argsList):
		'Called at the beginning of a players turn'
		iGameTurn, iPlayer = argsList
		pPlayer = gc.getPlayer(iPlayer)
		player = PyPlayer(iPlayer)

		if not pPlayer.isHuman():
			if not CyGame().getWBMapScript():
				cf.warScript(iPlayer)

		if pPlayer.getCivics(gc.getInfoTypeForString('CIVICOPTION_CULTURAL_VALUES')) == gc.getInfoTypeForString('CIVIC_CRUSADE'):
			cf.doCrusade(iPlayer)

		if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_KHAZAD'):
			cf.doTurnKhazad(iPlayer)
		elif pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_LUCHUIRP'):
			cf.doTurnLuchuirp(iPlayer)

		if pPlayer.hasTrait(gc.getInfoTypeForString('TRAIT_INSANE')):
			if CyGame().getSorenRandNum(1000, "Insane") < 20:
				iEvent = CvUtil.findInfoTypeNum(gc.getEventTriggerInfo, gc.getNumEventTriggerInfos(),'EVENTTRIGGER_TRAIT_INSANE')
				triggerData = pPlayer.initTriggeredData(iEvent, True, -1, -1, -1, iPlayer, -1, -1, -1, -1, -1)

		if pPlayer.hasTrait(gc.getInfoTypeForString('TRAIT_ADAPTIVE')):
			iBaseCycle = 100
			iCycle = (iBaseCycle * gc.getGameSpeedInfo(CyGame().getGameSpeedType()).getVictoryDelayPercent()) / 100
			for i in range(10):
				if (i * iCycle) - 5 == iGameTurn:
					iEvent = CvUtil.findInfoTypeNum(gc.getEventTriggerInfo, gc.getNumEventTriggerInfos(),'EVENTTRIGGER_TRAIT_ADAPTIVE')
					triggerData = pPlayer.initTriggeredData(iEvent, True, -1, -1, -1, iPlayer, -1, -1, -1, -1, -1)

		if pPlayer.isHuman():
			if pPlayer.hasTrait(gc.getInfoTypeForString('TRAIT_BARBARIAN')):
				eTeam = gc.getTeam(gc.getPlayer(gc.getBARBARIAN_PLAYER()).getTeam())
				iTeam = pPlayer.getTeam()
				if eTeam.isAtWar(iTeam) == False:
					if 2 * CyGame().getPlayerScore(iPlayer) >= 3 * CyGame().getPlayerScore(CyGame().getRankPlayer(1)):
						if iGameTurn >= 20:
							eTeam.declareWar(iTeam, False, WarPlanTypes.WARPLAN_TOTAL)
							if iPlayer == CyGame().getActivePlayer():
								cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_BARBARIAN_DECLARE_WAR",()), 'art/interface/popups/Barbarian.dds')


	def onEndPlayerTurn(self, argsList):
		'Called at the end of a players turn'
		iGameTurn, iPlayer = argsList
		pPlayer = gc.getPlayer(iPlayer)
		if gc.getGame().getElapsedGameTurns() == 1:
			if pPlayer.isHuman():
				if pPlayer.canRevolution(0):
					popupInfo = CyPopupInfo()
					popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_CHANGECIVIC)
					popupInfo.addPopup(iPlayer)

		CvAdvisorUtils.resetAdvisorNags()
		CvAdvisorUtils.endTurnFeats(iPlayer)

	def onEndTurnReady(self, argsList):
		iGameTurn = argsList[0]

	def onFirstContact(self, argsList):
	## Platy Builder ##
		if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
	## Platy Builder ##
		'Contact'
		iTeamX,iHasMetTeamY = argsList
		if (not self.__LOG_CONTACT):
			return
		CvUtil.pyPrint('Team %d has met Team %d' %(iTeamX, iHasMetTeamY))

	def onCombatResult(self, argsList):
		'Combat Result'
		pWinner,pLoser = argsList
		playerX = PyPlayer(pWinner.getOwner())
		unitX = PyInfo.UnitInfo(pWinner.getUnitType())
		playerY = PyPlayer(pLoser.getOwner())
		unitY = PyInfo.UnitInfo(pLoser.getUnitType())

## Advanced Tactics Start - ships and siege engines can be captured
## adopted from mechaerik War Prize ModComp
		if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_ADVANCED_TACTICS):
			pPlayer = gc.getPlayer(pWinner.getOwner())
			pPlayerLoser = gc.getPlayer(pLoser.getOwner())
			if (not pWinner.isHiddenNationality()):
				if (pLoser.canMoveInto(pWinner.plot(), True, True, False)):
					if (unitX.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL")):
						if (unitY.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL")):
							if CyGame().getSorenRandNum(100, "WarPrizes Naval") <= 25:
								iUnit = pLoser.getUnitType()
								newUnit = pPlayer.initUnit(pLoser.getUnitType(), pWinner.getX(), pWinner.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.NO_DIRECTION)
								newUnit.finishMoves()
								newUnit.setDamage(75, pWinner.getOwner())
								if (pPlayer.isHuman()):
									CyInterface().addMessage(pWinner.getOwner(),False,20,CyTranslator().getText("TXT_KEY_WEHAVECAPTUREDSOMETHING",(pLoser.getName(),)),'',0,gc.getUnitInfo(newUnit.getUnitType()).getButton(),ColorTypes(gc.getInfoTypeForString("COLOR_GREEN")), pWinner.getX(), pWinner.getY(), True,True)
								elif (pPlayerLoser.isHuman()):
									CyInterface().addMessage(pLoser.getOwner(),False,20,CyTranslator().getText("TXT_KEY_WEHAVELOSTSOMETHING",(pLoser.getName(),)),'',0,gc.getUnitInfo(newUnit.getUnitType()).getButton(),ColorTypes(gc.getInfoTypeForString("COLOR_RED")), pLoser.getX(), pLoser.getY(), True,True)
					if (unitY.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_SIEGE")):
						if CyGame().getSorenRandNum(100, "WarPrizes Siege") <= 15:
							iUnit = pLoser.getUnitType()
							newUnit = pPlayer.initUnit(pLoser.getUnitType(), pWinner.getX(), pWinner.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.NO_DIRECTION)
							newUnit.finishMoves()
							newUnit.setDamage(75, pWinner.getOwner())
							if (pPlayer.isHuman()):
								CyInterface().addMessage(pWinner.getOwner(),False,20,CyTranslator().getText("TXT_KEY_MISC_WARPRIZES_SUCCESS",(pLoser.getName(),)),'',0,gc.getUnitInfo(newUnit.getUnitType()).getButton(),ColorTypes(gc.getInfoTypeForString("COLOR_GREEN")), pWinner.getX(), pWinner.getY(), True,True)
							elif (pPlayerLoser.isHuman()):
								CyInterface().addMessage(pLoser.getOwner(),False,20,CyTranslator().getText("TXT_KEY_MISC_WARPRIZES_FAILURE",(pLoser.getName(),)),'',0,gc.getUnitInfo(newUnit.getUnitType()).getButton(),ColorTypes(gc.getInfoTypeForString("COLOR_RED")), pLoser.getX(), pLoser.getY(), True,True)
## End Advanced Tactics

		if not self.__LOG_COMBAT:
			return
		if playerX and playerX and unitX and playerY:
			CvUtil.pyPrint('Player %d Civilization %s Unit %s has defeated Player %d Civilization %s Unit %s'
				%(playerX.getID(), playerX.getCivilizationName(), unitX.getDescription(),
				playerY.getID(), playerY.getCivilizationName(), unitY.getDescription()))

	def onCombatLogCalc(self, argsList):
		'Combat Result'
		genericArgs = argsList[0][0]
		cdAttacker = genericArgs[0]
		cdDefender = genericArgs[1]
		iCombatOdds = genericArgs[2]
		CvUtil.combatMessageBuilder(cdAttacker, cdDefender, iCombatOdds)

	def onCombatLogHit(self, argsList):
		'Combat Message'
		global gCombatMessages, gCombatLog
		genericArgs = argsList[0][0]
		cdAttacker = genericArgs[0]
		cdDefender = genericArgs[1]
		iIsAttacker = genericArgs[2]
		iDamage = genericArgs[3]

		if cdDefender.eOwner == cdDefender.eVisualOwner:
			szDefenderName = gc.getPlayer(cdDefender.eOwner).getNameKey()
		else:
			szDefenderName = localText.getText("TXT_KEY_TRAIT_PLAYER_UNKNOWN", ())
		if cdAttacker.eOwner == cdAttacker.eVisualOwner:
			szAttackerName = gc.getPlayer(cdAttacker.eOwner).getNameKey()
		else:
			szAttackerName = localText.getText("TXT_KEY_TRAIT_PLAYER_UNKNOWN", ())

		if (iIsAttacker == 0):
			combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_HIT", (szDefenderName, cdDefender.sUnitName, iDamage, cdDefender.iCurrHitPoints, cdDefender.iMaxHitPoints))
			CyInterface().addCombatMessage(cdAttacker.eOwner,combatMessage)
			CyInterface().addCombatMessage(cdDefender.eOwner,combatMessage)
			if (cdDefender.iCurrHitPoints <= 0):
				combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_DEFEATED", (szAttackerName, cdAttacker.sUnitName, szDefenderName, cdDefender.sUnitName))
				CyInterface().addCombatMessage(cdAttacker.eOwner,combatMessage)
				CyInterface().addCombatMessage(cdDefender.eOwner,combatMessage)
		elif (iIsAttacker == 1):
			combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_HIT", (szAttackerName, cdAttacker.sUnitName, iDamage, cdAttacker.iCurrHitPoints, cdAttacker.iMaxHitPoints))
			CyInterface().addCombatMessage(cdAttacker.eOwner,combatMessage)
			CyInterface().addCombatMessage(cdDefender.eOwner,combatMessage)
			if (cdAttacker.iCurrHitPoints <= 0):
				combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_DEFEATED", (szDefenderName, cdDefender.sUnitName, szAttackerName, cdAttacker.sUnitName))
				CyInterface().addCombatMessage(cdAttacker.eOwner,combatMessage)
				CyInterface().addCombatMessage(cdDefender.eOwner,combatMessage)

	def onImprovementBuilt(self, argsList):
	## Platy Builder ##
		if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
	## Platy Builder ##
		'Improvement Built'
		iImprovement, iX, iY = argsList
		pPlot = CyMap().plot(iX, iY)

		if gc.getImprovementInfo(iImprovement).isUnique():
			CyEngine().addLandmark(pPlot, CvUtil.convertToStr(gc.getImprovementInfo(iImprovement).getDescription()))

			if iImprovement == gc.getInfoTypeForString('IMPROVEMENT_RING_OF_CARCER'):
				pPlot.setMinLevel(15)
				bPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
				bPlayer.initUnit(gc.getInfoTypeForString('UNIT_BRIGIT_HELD'), pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
			elif iImprovement == gc.getInfoTypeForString('IMPROVEMENT_SEVEN_PINES'):
				pPlot.setTerrainType(gc.getInfoTypeForString('TERRAIN_GRASS'), True, True)
				pPlot.setFeatureType(gc.getInfoTypeForString('FEATURE_FOREST'), 1)

		if (not self.__LOG_IMPROVEMENT):
			return
		CvUtil.pyPrint('Improvement %s was built at %d, %d'
			%(PyInfo.ImprovementInfo(iImprovement).getDescription(), iX, iY))

	def onImprovementDestroyed(self, argsList):
	## Platy Builder ##
		if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
	## Platy Builder ##
		'Improvement Destroyed'
		iImprovement, iOwner, iX, iY = argsList
		if gc.getImprovementInfo(iImprovement).isUnique():
			pPlot = CyMap().plot(iX, iY)
			CyEngine().removeLandmark(pPlot)
			if iImprovement == gc.getInfoTypeForString('IMPROVEMENT_RING_OF_CARCER'):
				pPlot.setMinLevel(-1)

		if iImprovement == gc.getInfoTypeForString('IMPROVEMENT_NECROTOTEM'):
			CyGame().changeGlobalCounter(-2)

		if CyGame().getWBMapScript():
			sf.onImprovementDestroyed(iImprovement, iOwner, iX, iY)

		if (not self.__LOG_IMPROVEMENT):
			return
		CvUtil.pyPrint('Improvement %s was Destroyed at %d, %d'
			%(PyInfo.ImprovementInfo(iImprovement).getDescription(), iX, iY))

	def onRouteBuilt(self, argsList):
	## Platy Builder ##
		if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
	## Platy Builder ##
		'Route Built'
		iRoute, iX, iY = argsList
		if (not self.__LOG_IMPROVEMENT):
			return
		CvUtil.pyPrint('Route %s was built at %d, %d'
			%(gc.getRouteInfo(iRoute).getDescription(), iX, iY))

	def onPlotRevealed(self, argsList):
	## Platy Builder ##
		if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
	## Platy Builder ##
		'Plot Revealed'
		pPlot = argsList[0]
		iTeam = argsList[1]

	def onPlotFeatureRemoved(self, argsList):
		'Plot Revealed'
		pPlot = argsList[0]
		iFeatureType = argsList[1]
		pCity = argsList[2] # This can be null

	def onPlotPicked(self, argsList):
		'Plot Picked'
		pPlot = argsList[0]
		CvUtil.pyPrint('Plot was picked at %d, %d'
			%(pPlot.getX(), pPlot.getY()))

	def onNukeExplosion(self, argsList):
		'Nuke Explosion'
		pPlot, pNukeUnit = argsList
		CvUtil.pyPrint('Nuke detonated at %d, %d'
			%(pPlot.getX(), pPlot.getY()))

	def onGotoPlotSet(self, argsList):
		'Nuke Explosion'
		pPlot, iPlayer = argsList

	def onBuildingBuilt(self, argsList):
		'Building Completed'
		pCity, iBuildingType = argsList
		player = pCity.getOwner()
		pPlayer = gc.getPlayer(player)
		pPlot = pCity.plot()
		game = gc.getGame()
		iBuildingClass = gc.getBuildingInfo(iBuildingType).getBuildingClassType()

		if not gc.getGame().isNetworkMultiPlayer() and (pCity.getOwner() == gc.getGame().getActivePlayer()) and isWorldWonderClass(iBuildingClass):
	## Platy Builder ##
			if not CyGame().GetWorldBuilderMode():
	## Platy Builder ##
				if gc.getBuildingInfo(iBuildingType).getMovie():
					# If this is a wonder...
					popupInfo = CyPopupInfo()
					popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
					popupInfo.setData1(iBuildingType)
					popupInfo.setData2(pCity.getID())
					popupInfo.setData3(0)
					popupInfo.setText(u"showWonderMovie")
					popupInfo.addPopup(pCity.getOwner())

		if iBuildingType == gc.getInfoTypeForString('BUILDING_INFERNAL_GRIMOIRE'):
			if CyGame().getSorenRandNum(100, "Bob") < 20:
				pPlot2 = cf.findClearPlot(-1, pPlot)
				if pPlot2 != -1:
					bPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
					newUnit = bPlayer.initUnit(gc.getInfoTypeForString('UNIT_BALOR'), pPlot2.getX(), pPlot2.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
					CyInterface().addMessage(pCity.getOwner(),True,25,CyTranslator().getText("TXT_KEY_MESSAGE_INFERNAL_GRIMOIRE_BALOR",()),'AS2D_BALOR',1,'Art/Interface/Buttons/Units/Balor.dds',ColorTypes(7),newUnit.getX(),newUnit.getY(),True,True)
					if pCity.getOwner() == CyGame().getActivePlayer():
						cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_INFERNAL_GRIMOIRE_BALOR",()), 'art/interface/popups/Balor.dds')

		elif iBuildingType == gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_FINAL'):
			pCity.setNumRealBuilding(gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_EXALTED'), 0)
		elif iBuildingType == gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_EXALTED'):
			pCity.setNumRealBuilding(gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_DIVINE'), 0)
		elif iBuildingType == gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_DIVINE'):
			pCity.setNumRealBuilding(gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_CONSECRATED'), 0)
		elif iBuildingType == gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_CONSECRATED'):
			pCity.setNumRealBuilding(gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_BLESSED'), 0)
		elif iBuildingType == gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_BLESSED'):
			pCity.setNumRealBuilding(gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_ANOINTED'), 0)
		elif iBuildingType == gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_ANOINTED'):
			pCity.setNumRealBuilding(gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR'), 0)

		elif iBuildingType == gc.getInfoTypeForString('BUILDING_MERCURIAN_GATE'):
			for iLoop in range(pPlot.getNumUnits(), -1, -1):
				pUnit = pPlot.getUnit(iLoop)
				pUnit.jumpToNearestValidPlot()

			iMercurianPlayer = pPlayer.initNewEmpire(gc.getInfoTypeForString('LEADER_BASIUM'), gc.getInfoTypeForString('CIVILIZATION_MERCURIANS'))
			if iMercurianPlayer != PlayerTypes.NO_PLAYER:
				pMercurianPlayer = gc.getPlayer(iMercurianPlayer)
				iTeam = pPlayer.getTeam()
				iMercurianTeam = pMercurianPlayer.getTeam()
				if iTeam < iMercurianTeam:
					gc.getTeam(iTeam).addTeam(iMercurianTeam)
				else:
					gc.getTeam(iMercurianTeam).addTeam(iTeam)

				pBasiumUnit = gc.getPlayer(iMercurianPlayer).initUnit(gc.getInfoTypeForString('UNIT_BASIUM'), pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
				pBasiumUnit.setAvatarOfCivLeader(True)
				gc.getPlayer(iMercurianPlayer).initUnit(gc.getInfoTypeForString('UNIT_SETTLER'), pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
				gc.getPlayer(iMercurianPlayer).initUnit(gc.getInfoTypeForString('UNIT_ANGEL'), pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
				gc.getPlayer(iMercurianPlayer).initUnit(gc.getInfoTypeForString('UNIT_ANGEL'), pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
				gc.getPlayer(iMercurianPlayer).initUnit(gc.getInfoTypeForString('UNIT_ANGEL'), pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
				gc.getPlayer(iMercurianPlayer).initUnit(gc.getInfoTypeForString('UNIT_ANGEL'), pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
				gc.getPlayer(iMercurianPlayer).initUnit(gc.getInfoTypeForString('UNIT_ANGEL'), pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
				gc.getPlayer(iMercurianPlayer).initUnit(gc.getInfoTypeForString('UNIT_ANGEL'), pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
				gc.getPlayer(iMercurianPlayer).initUnit(gc.getInfoTypeForString('UNIT_WORKER'), pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)

				if pPlayer.isHuman():
					popupInfo = CyPopupInfo()
					popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
					popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_CONTROL_MERCURIANS",()))
					popupInfo.setData1(player)
					popupInfo.setData2(iMercurianPlayer)
					popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_YES", ()), "")
					popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_NO", ()), "")
					popupInfo.setOnClickedPythonCallback("reassignPlayer")
					popupInfo.addPopup(player)

		elif iBuildingType == gc.getInfoTypeForString('BUILDING_TOWER_OF_THE_ELEMENTS'):
			lList = ['UNIT_AIR_ELEMENTAL', 'UNIT_EARTH_ELEMENTAL', 'UNIT_FIRE_ELEMENTAL', 'UNIT_WATER_ELEMENTAL']
			iUnit = gc.getInfoTypeForString(lList[CyGame().getSorenRandNum(len(lList), "Pick Elemental")-1])
			newUnit = pPlayer.initUnit(iUnit, pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_CITY_DEFENSE, DirectionTypes.DIRECTION_SOUTH)
			newUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_HELD'), True)
			CyInterface().addMessage(player,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_TOWER_OF_THE_ELEMENTS_SPAWN",()),'',1,gc.getUnitInfo(iUnit).getButton(),ColorTypes(8),pCity.getX(),pCity.getY(),True,True)
			iElemental = gc.getInfoTypeForString('PROMOTION_ELEMENTAL')
			iStrong = gc.getInfoTypeForString('PROMOTION_STRONG')
			apUnitList = PyPlayer(player).getUnitList()
			for pUnit in apUnitList:
				if pUnit.isHasPromotion(iElemental):
					pUnit.setHasPromotion(iStrong, True)

		elif iBuildingType == gc.getInfoTypeForString('BUILDING_TOWER_OF_NECROMANCY'):
			iUndead = gc.getInfoTypeForString('PROMOTION_UNDEAD')
			iStrong = gc.getInfoTypeForString('PROMOTION_STRONG')
			apUnitList = PyPlayer(player).getUnitList()
			for pUnit in apUnitList:
				if pUnit.isHasPromotion(iUndead):
					pUnit.setHasPromotion(iStrong, True)

		elif iBuildingType == gc.getInfoTypeForString('BUILDING_TEMPLE_OF_THE_HAND'):
			iSnow = gc.getInfoTypeForString('TERRAIN_SNOW')
			iFlames = gc.getInfoTypeForString('FEATURE_FLAMES')
			iFloodPlains = gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS')
			iForest = gc.getInfoTypeForString('FEATURE_FOREST')
			iJungle = gc.getInfoTypeForString('FEATURE_JUNGLE')
			iScrub = gc.getInfoTypeForString('FEATURE_SCRUB')
			iSmoke = gc.getInfoTypeForString('IMPROVEMENT_SMOKE')
			iBlizzard = gc.getInfoTypeForString('FEATURE_BLIZZARD')
			iX = pCity.getX()
			iY = pCity.getY()
			for iiX in range(iX-2, iX+3, 1):
				for iiY in range(iY-2, iY+3, 1):
					pLoopPlot = CyMap().plot(iiX,iiY)
					if not pLoopPlot.isNone():
						if not pLoopPlot.isWater():
							pLoopPlot.setTerrainType(iSnow, True, True)
							if pLoopPlot.getImprovementType() == iSmoke:
								pLoopPlot.setImprovementType(-1)
							iFeature = pLoopPlot.getFeatureType()
							if iFeature == iForest:
								pLoopPlot.setFeatureType(iForest, 2)
							if iFeature == iJungle:
								pLoopPlot.setFeatureType(iForest, 2)
							if iFeature == iFlames:
								pLoopPlot.setFeatureType(-1, -1)
							if iFeature == iFloodPlains:
								pLoopPlot.setFeatureType(-1, -1)
							if iFeature == iScrub:
								pLoopPlot.setFeatureType(-1, -1)
							if CyGame().getSorenRandNum(100, "Snowfall") < 2:
								pLoopPlot.setFeatureType(iBlizzard, -1)
			CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SNOWFALL'),pPlot.getPoint())

		elif iBuildingType == gc.getInfoTypeForString('BUILDING_GRAND_MENAGERIE'):
			if pPlayer.isHuman():
				if not CyGame().getWBMapScript():
					t = "TROPHY_FEAT_GRAND_MENAGERIE"
					if not CyGame().isHasTrophy(t):
						CyGame().changeTrophyValue(t, 1)

		CvAdvisorUtils.buildingBuiltFeats(pCity, iBuildingType)

		if (not self.__LOG_BUILDING):
			return
		CvUtil.pyPrint('%s was finished by Player %d Civilization %s'
			%(PyInfo.BuildingInfo(iBuildingType).getDescription(), pCity.getOwner(), gc.getPlayer(pCity.getOwner()).getCivilizationDescription(0)))

	def onProjectBuilt(self, argsList):
		'Project Completed'
		pCity, iProjectType = argsList
		game = gc.getGame()
		iPlayer = pCity.getOwner()
		pPlayer = gc.getPlayer(iPlayer)
		if not gc.getGame().isNetworkMultiPlayer() and pCity.getOwner() == gc.getGame().getActivePlayer():
	## Platy Builder ##
			if not CyGame().GetWorldBuilderMode():
	## Platy Builder ##
				popupInfo = CyPopupInfo()
				popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
				popupInfo.setData1(iProjectType)
				popupInfo.setData2(pCity.getID())
				popupInfo.setData3(2)
				popupInfo.setText(u"showWonderMovie")
				popupInfo.addPopup(iPlayer)

		if iProjectType == gc.getInfoTypeForString('PROJECT_BANE_DIVINE'):
			iCombatDisciple = gc.getInfoTypeForString('UNITCOMBAT_DISCIPLE')
			for iLoopPlayer in range(gc.getMAX_PLAYERS()):
				pLoopPlayer = gc.getPlayer(iLoopPlayer)
				if pLoopPlayer.isAlive() :
					apUnitList = PyPlayer(iLoopPlayer).getUnitList()
					for pUnit in apUnitList:
						if pUnit.getUnitCombatType() == iCombatDisciple:
							pUnit.kill(False, pCity.getOwner())

		elif iProjectType == gc.getInfoTypeForString('PROJECT_GENESIS'):
			if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_ILLIANS'):
				cf.snowgenesis(iPlayer)
			else:
				cf.genesis(iPlayer)

		elif iProjectType == gc.getInfoTypeForString('PROJECT_GLORY_EVERLASTING'):
			iDemon = gc.getInfoTypeForString('PROMOTION_DEMON')
			iUndead = gc.getInfoTypeForString('PROMOTION_UNDEAD')
			for iLoopPlayer in range(gc.getMAX_PLAYERS()):
				pLoopPlayer = gc.getPlayer(iLoopPlayer)
				player = PyPlayer(iLoopPlayer)
				if pLoopPlayer.isAlive():
					apUnitList = player.getUnitList()
					for pUnit in apUnitList:
						if (pUnit.isHasPromotion(iDemon) or pUnit.isHasPromotion(iUndead)):
							pUnit.kill(False, iPlayer)

		elif iProjectType == gc.getInfoTypeForString('PROJECT_RITES_OF_OGHMA'):
			i = 7
			iSize = CyMap().getWorldSize()
			if iSize == gc.getInfoTypeForString('WORLDSIZE_DUEL'):
				i -= 3
			elif iSize == gc.getInfoTypeForString('WORLDSIZE_TINY'):
				i =- 2
			elif iSize == gc.getInfoTypeForString('WORLDSIZE_SMALL'):
				i -= 1
			elif iSize == gc.getInfoTypeForString('WORLDSIZE_LARGE'):
				i += 1
			elif iSize == gc.getInfoTypeForString('WORLDSIZE_HUGE'):
				i += 3
			cf.addBonus('BONUS_MANA',i,'Art/Interface/Buttons/WorldBuilder/mana_button.dds')

		elif iProjectType == gc.getInfoTypeForString('PROJECT_NATURES_REVOLT'):
			bPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
			py = PyPlayer(gc.getBARBARIAN_PLAYER())
			iAxeman = gc.getInfoTypeForString('UNITCLASS_AXEMAN')
			iBear = gc.getInfoTypeForString('UNIT_BEAR')
			iHeroicDefense = gc.getInfoTypeForString('PROMOTION_HEROIC_DEFENSE')
			iHeroicDefense2 = gc.getInfoTypeForString('PROMOTION_HEROIC_DEFENSE2')
			iHeroicStrength = gc.getInfoTypeForString('PROMOTION_HEROIC_STRENGTH')
			iHeroicStrength2 = gc.getInfoTypeForString('PROMOTION_HEROIC_STRENGTH2')
			iHunter = gc.getInfoTypeForString('UNITCLASS_HUNTER')
			iLion = gc.getInfoTypeForString('UNIT_LION')
			iScout = gc.getInfoTypeForString('UNITCLASS_SCOUT')
			iTiger = gc.getInfoTypeForString('UNIT_TIGER')
			iWarrior = gc.getInfoTypeForString('UNITCLASS_WARRIOR')
			iWolf = gc.getInfoTypeForString('UNIT_WOLF')
			iWorker = gc.getInfoTypeForString('UNITCLASS_WORKER')
			for pUnit in py.getUnitList():
				bValid = False
				if pUnit.getUnitClassType() == iWorker:
					iNewUnit = iWolf
					bValid = True
				elif pUnit.getUnitClassType() == iScout:
					iNewUnit = iLion
					bValid = True
				elif pUnit.getUnitClassType() == iWarrior:
					iNewUnit = iLion
					bValid = True
				elif pUnit.getUnitClassType() == iHunter:
					iNewUnit = iTiger
					bValid = True
				elif pUnit.getUnitClassType() == iAxeman:
					iNewUnit = iBear
					bValid = True
				if bValid:
					newUnit = bPlayer.initUnit(iNewUnit, pUnit.getX(), pUnit.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
					newUnit = bPlayer.initUnit(iNewUnit, pUnit.getX(), pUnit.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
					newUnit = bPlayer.initUnit(iNewUnit, pUnit.getX(), pUnit.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
					pUnit.kill(True, PlayerTypes.NO_PLAYER)
			for iLoopPlayer in range(gc.getMAX_PLAYERS()):
				pLoopPlayer = gc.getPlayer(iLoopPlayer)
				if pLoopPlayer.isAlive():
					py = PyPlayer(iLoopPlayer)
					for pUnit in py.getUnitList():
						if pUnit.isAnimal():
							pUnit.setHasPromotion(iHeroicDefense, True)
							pUnit.setHasPromotion(iHeroicDefense2, True)
							pUnit.setHasPromotion(iHeroicStrength, True)
							pUnit.setHasPromotion(iHeroicStrength2, True)

		elif iProjectType == gc.getInfoTypeForString('PROJECT_BLOOD_OF_THE_PHOENIX'):
			py = PyPlayer(iPlayer)
			apUnitList = py.getUnitList()
			for pUnit in apUnitList:
				if pUnit.isAlive():
					if pUnit.getUnitCombatType() != UnitCombatTypes.NO_UNITCOMBAT:
						pUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_IMMORTAL'), True)

		elif iProjectType == gc.getInfoTypeForString('PROJECT_PURGE_THE_UNFAITHFUL'):
			for pyCity in PyPlayer(iPlayer).getCityList():
				pCity2 = pyCity.GetCy()
				iRnd = CyGame().getSorenRandNum(2, "Bob")
				StateBelief = pPlayer.getStateReligion()
				if StateBelief == gc.getInfoTypeForString('RELIGION_THE_ORDER'):
					iRnd = iRnd - 1
				for iTarget in range(gc.getNumReligionInfos()):
					if (StateBelief != iTarget and pCity2.isHasReligion(iTarget) and pCity2.isHolyCityByType(iTarget) == False):
						pCity2.setHasReligion(iTarget, False, True, True)
						iRnd = iRnd + 1
						for i in range(gc.getNumBuildingInfos()):
							if gc.getBuildingInfo(i).getPrereqReligion() == iTarget:
								pCity2.setNumRealBuilding(i, 0)
				if iRnd > 0:
					pCity2.setOccupationTimer(iRnd)

		elif iProjectType == gc.getInfoTypeForString('PROJECT_BIRTHRIGHT_REGAINED'):
			pPlayer.setFeatAccomplished(FeatTypes.FEAT_GLOBAL_SPELL, False)

		elif iProjectType == gc.getInfoTypeForString('PROJECT_SAMHAIN'):
			for pyCity in PyPlayer(iPlayer).getCityList():
				pCity = pyCity.GetCy()
				pCity.changeHappinessTimer(20)
			iCount = CyGame().countCivPlayersAlive() + int(CyGame().getHandicapType()) - 5
			for i in range(iCount):
				cf.addUnit(gc.getInfoTypeForString('UNIT_FROSTLING'))
				cf.addUnit(gc.getInfoTypeForString('UNIT_FROSTLING'))
				cf.addUnit(gc.getInfoTypeForString('UNIT_FROSTLING_ARCHER'))
				cf.addUnit(gc.getInfoTypeForString('UNIT_FROSTLING_WOLF_RIDER'))
			cf.addUnit(gc.getInfoTypeForString('UNIT_MOKKA'))

		elif iProjectType == gc.getInfoTypeForString('PROJECT_THE_WHITE_HAND'):
			newUnit1 = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_PRIEST_OF_WINTER'), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
			newUnit1.setName("Dumannios")
			newUnit2 = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_PRIEST_OF_WINTER'), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
			newUnit2.setName("Riuros")
			newUnit3 = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_PRIEST_OF_WINTER'), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
			newUnit3.setName("Anagantios")

		elif iProjectType == gc.getInfoTypeForString('PROJECT_THE_DEEPENING'):
			iDesert = gc.getInfoTypeForString('TERRAIN_DESERT')
			iGrass = gc.getInfoTypeForString('TERRAIN_GRASS')
			iMarsh = gc.getInfoTypeForString('TERRAIN_MARSH')
			iPlains = gc.getInfoTypeForString('TERRAIN_PLAINS')
			iSnow = gc.getInfoTypeForString('TERRAIN_SNOW')
			iTundra = gc.getInfoTypeForString('TERRAIN_TUNDRA')
			iBlizzard = gc.getInfoTypeForString('FEATURE_BLIZZARD')
			iModifier = (gc.getGameSpeedInfo(CyGame().getGameSpeedType()).getVictoryDelayPercent() * 20) / 100
			iTimer = 40 + iModifier
			for i in range (CyMap().numPlots()):
				pPlot = CyMap().plotByIndex(i)
				bValid = False
				if pPlot.isWater() == False:
					if CyGame().getSorenRandNum(100, "The Deepening") < 25:
						iTerrain = pPlot.getTerrainType()
						chance = CyGame().getSorenRandNum(100, "Bob")
						if iTerrain == iSnow:
							bValid = True
						elif iTerrain == iTundra:
							pPlot.setTempTerrainType(iSnow, CyGame().getSorenRandNum(iTimer, "Bob") + 10)
							bValid = True
						elif iTerrain == iGrass or iTerrain == iMarsh:
							if chance < 40:
								pPlot.setTempTerrainType(iSnow, CyGame().getSorenRandNum(iTimer, "Bob") + 10)
							else:
								pPlot.setTempTerrainType(iTundra, CyGame().getSorenRandNum(iTimer, "Bob") + 10)
							bValid = True
						elif iTerrain == iPlains:
							if chance < 60:
								pPlot.setTempTerrainType(iSnow, CyGame().getSorenRandNum(iTimer, "Bob") + 10)
							else:
								pPlot.setTempTerrainType(iTundra, CyGame().getSorenRandNum(iTimer, "Bob") + 10)
							bValid = True
						elif iTerrain == iDesert:
							if chance < 10:
								pPlot.setTempTerrainType(iSnow, CyGame().getSorenRandNum(iTimer, "Bob") + 10)
							elif chance < 30:
								pPlot.setTempTerrainType(iTundra, CyGame().getSorenRandNum(iTimer, "Bob") + 10)
							else:
								pPlot.setTempTerrainType(iPlains, CyGame().getSorenRandNum(iTimer, "Bob") + 10)
						if bValid:
							if CyGame().getSorenRandNum(750, "The Deepening") < 10:
								pPlot.setFeatureType(iBlizzard,-1)

		elif iProjectType == gc.getInfoTypeForString('PROJECT_STIR_FROM_SLUMBER'):
			pPlayer.initUnit(gc.getInfoTypeForString('UNIT_DRIFA'), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

		elif iProjectType == gc.getInfoTypeForString('PROJECT_THE_DRAW'):
			iTeam = pPlayer.getTeam()
			eTeam = gc.getTeam(iTeam)
			for iLoopPlayer in range(gc.getMAX_PLAYERS()):
				pLoopPlayer = gc.getPlayer(iLoopPlayer)
				if pLoopPlayer.isAlive() and pLoopPlayer.getTeam() == iTeam:
					pLoopPlayer.changeNoDiplomacyWithEnemies(1)
			for iLoopTeam in range(gc.getMAX_TEAMS()):
				if iLoopTeam != iTeam:
					if iLoopTeam != gc.getPlayer(gc.getBARBARIAN_PLAYER()).getTeam():
						eLoopTeam = gc.getTeam(iLoopTeam)
						if eLoopTeam.isAlive():
							if not eLoopTeam.isAVassal():
								eTeam.declareWar(iLoopTeam, False, WarPlanTypes.WARPLAN_LIMITED)
			py = PyPlayer(iPlayer)
			for pUnit in py.getUnitList():
				iDmg = pUnit.getDamage() * 2
				if iDmg > 99:
					iDmg = 99
				if iDmg < 50:
					iDmg = 50
				pUnit.setDamage(iDmg, iPlayer)
			for pyCity in PyPlayer(iPlayer).getCityList():
				pLoopCity = pyCity.GetCy()
				iPop = int(pLoopCity.getPopulation() / 2)
				if iPop < 1:
					iPop = 1
				pLoopCity.setPopulation(iPop)

		elif iProjectType == gc.getInfoTypeForString('PROJECT_ASCENSION'):
			pAuricUnit = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_AURIC_ASCENDED'), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
			pAuricUnit.setAvatarOfCivLeader(True)
			if pPlayer.isHuman():
				t = "TROPHY_FEAT_ASCENSION"
				if not CyGame().isHasTrophy(t):
					CyGame().changeTrophyValue(t, 1)
			if not CyGame().getWBMapScript():
				iBestPlayer = -1
				iBestValue = 0
				for iLoopPlayer in range(gc.getMAX_PLAYERS()):
					pLoopPlayer = gc.getPlayer(iLoopPlayer)
					if pLoopPlayer.isAlive():
						if not pLoopPlayer.isBarbarian():
							if pLoopPlayer.getTeam() != pPlayer.getTeam():
								iValue = CyGame().getSorenRandNum(500, "Ascension")
								if pLoopPlayer.isHuman():
									iValue += 2000
								iValue += (20 - CyGame().getPlayerRank(iLoopPlayer)) * 50
								if iValue > iBestValue:
									iBestValue = iValue
									iBestPlayer = iLoopPlayer
				if iBestPlayer != -1:
					pBestPlayer = gc.getPlayer(iBestPlayer)
					pBestCity = pBestPlayer.getCapitalCity()
					if pBestPlayer.isHuman():
						iEvent = CvUtil.findInfoTypeNum(gc.getEventTriggerInfo, gc.getNumEventTriggerInfos(),'EVENTTRIGGER_GODSLAYER')
						triggerData = gc.getPlayer(iBestPlayer).initTriggeredData(iEvent, True, -1, pBestCity.getX(), pBestCity.getY(), iBestPlayer, -1, -1, -1, -1, -1)
					else:
						pBestPlayer.initUnit(gc.getInfoTypeForString('EQUIPMENT_GODSLAYER'), pBestCity.getX(), pBestCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

		elif iProjectType == gc.getInfoTypeForString('PROJECT_PACT_OF_THE_NILHORN'):
			newUnit1 = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_HILL_GIANT'), pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_NORTH)
			newUnit1.setName("Larry")
			newUnit1.AI_setGroupflag(10)
			newUnit1.setUnitAIType(gc.getInfoTypeForString('UNITAI_ATTACK_CITY'))
			newUnit2 = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_HILL_GIANT'), pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_NORTH)
			newUnit2.setName("Curly")
			newUnit2.AI_setGroupflag(10)
			newUnit2.setUnitAIType(gc.getInfoTypeForString('UNITAI_ATTACK_CITY'))
			newUnit3 = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_HILL_GIANT'), pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_NORTH)
			newUnit3.setName("Moe")
			newUnit3.AI_setGroupflag(10)
			newUnit3.setUnitAIType(gc.getInfoTypeForString('UNITAI_ATTACK_CITY'))

#some AI help
			if pPlayer.isHuman():
				newUnit1.setHasPromotion(gc.getInfoTypeForString('PROMOTION_HIDDEN_NATIONALITY'), True)
				newUnit2.setHasPromotion(gc.getInfoTypeForString('PROMOTION_HIDDEN_NATIONALITY'), True)
				newUnit3.setHasPromotion(gc.getInfoTypeForString('PROMOTION_HIDDEN_NATIONALITY'), True)



	def onSelectionGroupPushMission(self, argsList):
		'selection group mission'
		eOwner = argsList[0]
		eMission = argsList[1]
		iNumUnits = argsList[2]
		listUnitIds = argsList[3]
		if not self.__LOG_PUSH_MISSION:
			return
		if pHeadUnit:
			CvUtil.pyPrint("Selection Group pushed mission %d" %(eMission))

	def onUnitMove(self, argsList):
		'unit move'
		pPlot,pUnit,pOldPlot = argsList
		player = PyPlayer(pUnit.getOwner())
		unitInfo = PyInfo.UnitInfo(pUnit.getUnitType())
		if not self.__LOG_MOVEMENT:
			return
		if player and unitInfo:
			CvUtil.pyPrint('Player %d Civilization %s unit %s is moving to %d, %d' 
				%(player.getID(), player.getCivilizationName(), unitInfo.getDescription(), 
				pUnit.getX(), pUnit.getY()))

	def onUnitSetXY(self, argsList):
		'units xy coords set manually'
		pPlot,pUnit = argsList
		player = PyPlayer(pUnit.getOwner())
		unitInfo = PyInfo.UnitInfo(pUnit.getUnitType())
		if not self.__LOG_MOVEMENT:
			return

	def onUnitCreated(self, argsList):
	## Platy Builder ##
		if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
	## Platy Builder ##
		'Unit Completed'
		unit = argsList[0]
		player = PyPlayer(unit.getOwner())
		pPlayer = gc.getPlayer(unit.getOwner())
		iChanneling2 = gc.getInfoTypeForString('PROMOTION_CHANNELING2')
		iChanneling3 = gc.getInfoTypeForString('PROMOTION_CHANNELING3')

		if unit.getUnitCombatType() == gc.getInfoTypeForString('UNITCOMBAT_ADEPT'):
			lCheckThis = ['AIR', 'BODY', 'CHAOS', 'DEATH', 'EARTH', 'ENCHANTMENT', 'ENTROPY', 'FIRE', 'ICE', 'LAW', 'LIFE', 'METAMAGIC', 'MIND', 'NATURE', 'SHADOW', 'SPIRIT', 'SUN', 'WATER']
			for item in lCheckThis:
				iNum = pPlayer.getNumAvailableBonuses(gc.getInfoTypeForString('BONUS_MANA_' + item))
				if iNum > 1:
					unit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_' + item + '1'), True)
					if (iNum > 2 and unit.isHasPromotion(iChanneling2)):
						unit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_' + item + '2'), True)
						if (iNum > 3 and unit.isHasPromotion(iChanneling3)):
							unit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_' + item + '3'), True)

		if unit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_ELEMENTAL')):
			if pPlayer.getNumBuilding(gc.getInfoTypeForString('BUILDING_TOWER_OF_THE_ELEMENTS')) > 0:
				unit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_STRONG'), True)

		if unit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_UNDEAD')):
			if pPlayer.getNumBuilding(gc.getInfoTypeForString('BUILDING_TOWER_OF_NECROMANCY')) > 0:
				unit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_STRONG'), True)

#UNITAI for Adepts and Terraformers
		if not pPlayer.isHuman() and not pPlayer.isBarbarian():
			if unit.getUnitType() == gc.getInfoTypeForString('UNIT_DEVOUT'):
				numberterraformer = 0
				for pUnit in player.getUnitList():
					if pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_DEVOUT'):
						if pUnit.getUnitAIType() == gc.getInfoTypeForString('UNITAI_TERRAFORMER'):
							numberterraformer += 1
				if numberterraformer < pPlayer.getNumCities()*CyGame().getGlobalCounter()/100:
					unit.setUnitAIType(gc.getInfoTypeForString('UNITAI_TERRAFORMER'))
				elif numberterraformer < 3:
					unit.setUnitAIType(gc.getInfoTypeForString('UNITAI_TERRAFORMER'))

			numTreeTerraformer=0
			if unit.getUnitType() == gc.getInfoTypeForString('UNIT_PRIEST_OF_LEAVES'):
				neededTreeTerraformer = 1
				if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_LJOSALFAR') or pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_SVARTALFAR'):
					neededTreeTerraformer += pPlayer.getNumCities()/3
				for pUnit in player.getUnitList():
					if pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_PRIEST_OF_LEAVES'):
						if pUnit.getUnitAIType() == gc.getInfoTypeForString('UNITAI_TERRAFORMER'):
							numTreeTerraformer += 1
				if numTreeTerraformer < neededTreeTerraformer:
					unit.setUnitAIType(gc.getInfoTypeForString('UNITAI_TERRAFORMER'))

			if unit.getUnitClassType() == gc.getInfoTypeForString('UNITCLASS_ADEPT'):

				bCanMageTerraform = False
				if pPlayer.countOwnedBonuses(gc.getInfoTypeForString('BONUS_MANA_WATER'), False) > 0:
					bCanMageTerraform = True
				elif pPlayer.countOwnedBonuses(gc.getInfoTypeForString('BONUS_MANA_SUN'), False) > 0:
					bCanMageTerraform = True

				numbermageterrafomer = (pPlayer.AI_getNumAIUnits(gc.getInfoTypeForString('UNITAI_TERRAFORMER')) - numTreeTerraformer)
				numbermanaupgrade = pPlayer.AI_getNumAIUnits(gc.getInfoTypeForString('UNITAI_MANA_UPGRADE'))

				bHasAI = False
				canupgrademana = False

				if pPlayer.isHasTech(gc.getInfoTypeForString('TECH_SORCERY')):
					canupgrademana=True
				elif pPlayer.isHasTech(gc.getInfoTypeForString('TECH_ALTERATION')):
					canupgrademana=True
				elif pPlayer.isHasTech(gc.getInfoTypeForString('TECH_DIVINATION')):
					canupgrademana=True
				elif pPlayer.isHasTech(gc.getInfoTypeForString('TECH_ELEMENTALISM')):
					canupgrademana=True
				elif pPlayer.isHasTech(gc.getInfoTypeForString('TECH_NECROMANCY')):
					canupgrademana=True


				if numbermanaupgrade == 0:
					unit.setUnitAIType(gc.getInfoTypeForString('UNITAI_MANA_UPGRADE'))
					bHasAI = True
				if canupgrademana:
					if pPlayer.countOwnedBonuses(gc.getInfoTypeForString('BONUS_MANA'), False) > numbermanaupgrade * 2:
						unit.setUnitAIType(gc.getInfoTypeForString('UNITAI_MANA_UPGRADE'))
						bHasAI = True

				if not bHasAI:
					if bCanMageTerraform:
						if numbermageterrafomer < 2:
							unit.setUnitAIType(gc.getInfoTypeForString('UNITAI_TERRAFORMER'))
							bHasAI = True

				if not bHasAI:
					pPlot = unit.plot()
					if pPlayer.AI_getNumAIUnits(gc.getInfoTypeForString('UNITAI_MAGE')) < pPlayer.getNumCities() / 2:
						unit.setUnitAIType(gc.getInfoTypeForString('UNITAI_MAGE'))
					elif pPlot.area().getAreaAIType(pPlayer.getTeam()) == AreaAITypes.AREAAI_DEFENSIVE:
						unit.setUnitAIType(gc.getInfoTypeForString('UNITAI_MAGE'))
					else:
						unit.setUnitAIType(gc.getInfoTypeForString('UNITAI_WARWIZARD'))

		if CyGame().getWBMapScript():
			sf.onUnitCreated(unit)

		if not self.__LOG_UNITBUILD:
			return

	def onUnitBuilt(self, argsList):
		'Unit Completed'
		city = argsList[0]
		unit = argsList[1]
		player = PyPlayer(city.getOwner())
		pPlayer = gc.getPlayer(unit.getOwner())

		# Advanced Tactics - Diverse Grigori (idea and base code taken from FFH Tweakmod)
		if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_ADVANCED_TACTICS):
			if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_GRIGORI'):
				unit.setReligion(-1)
				if unit.getRace() == -1:
					iChance = 40
					if CyGame().getSorenRandNum(100, "Grigori Racial Diversity") <= iChance:
						race = CyGame().getSorenRandNum(3, "Bob")
						if race == 0 and unit.isAlive():
							unit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_ORC'), True)
						elif race == 1 and unit.isAlive():
							race = CyGame().getSorenRandNum(2, "Elvish division")
							if race == 0:
								unit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_ELF'), True)
							elif race == 1:
								unit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_DARK_ELF'), True)
						elif race == 2:
							if (unit.isAlive()):
								unit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_DWARF'), True)
		# End Advanced Tactics

		if unit.getUnitType() == gc.getInfoTypeForString('UNIT_BEAST_OF_AGARES'):
			if city.getCivilizationType() != gc.getInfoTypeForString('CIVILIZATION_INFERNAL'):
				iPop = city.getPopulation() - 4
				if iPop <= 1:
					iPop = 1
				city.setPopulation(iPop)
				city.setOccupationTimer(4)

		elif unit.getUnitType() == gc.getInfoTypeForString('UNIT_ACHERON'):
			unit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_HELD'), True)
			city.setNumRealBuilding(gc.getInfoTypeForString('BUILDING_THE_DRAGONS_HORDE'), 1)
			iX = city.getX()
			iY = city.getY()
			for iiX in range(iX-1, iX+2, 1):
				for iiY in range(iY-1, iY+2, 1):
					pPlot = CyMap().plot(iiX,iiY)
					if (pPlot.getFeatureType() == gc.getInfoTypeForString('FEATURE_FOREST') or pPlot.getFeatureType() == gc.getInfoTypeForString('FEATURE_JUNGLE')):
						pPlot.setFeatureType(gc.getInfoTypeForString('FEATURE_FLAMES'), 0)
			if( game.getAIAutoPlay(game.getActivePlayer()) == 0 ) :
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_ACHERON_CREATION",()), str(gc.getUnitInfo(unit.getUnitType()).getImage()))

		if city.getNumRealBuilding(gc.getInfoTypeForString('BUILDING_WARRENS')) > 0:
			if isWorldUnitClass(unit.getUnitClassType()) == False:
				if isNationalUnitClass(unit.getUnitClassType()) == False:
					if not unit.isMechUnit():
#						if unit.getUnitCombatType() != UnitCombatTypes.NO_UNITCOMBAT:
						if unit.isAlive():
							newUnit = pPlayer.initUnit(unit.getUnitType(), city.getX(), city.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
							city.applyBuildEffects(newUnit)

		CvAdvisorUtils.unitBuiltFeats(city, unit)

		if not self.__LOG_UNITBUILD:
			return
		CvUtil.pyPrint('%s was finished by Player %d Civilization %s'
			%(PyInfo.UnitInfo(unit.getUnitType()).getDescription(), player.getID(), player.getCivilizationName()))

	def onUnitKilled(self, argsList):
		'Unit Killed'
		unit, iAttacker = argsList
		iPlayer = unit.getOwner()
		pPlayer = gc.getPlayer(iPlayer)
		player = PyPlayer(iPlayer)
		attacker = PyPlayer(iAttacker)
		pPlot = unit.plot()
		iX = unit.getX()
		iY = unit.getY()

		if unit.isAlive() and not unit.isImmortal():
			iSoulForge = gc.getInfoTypeForString('BUILDING_SOUL_FORGE')
			if gc.getGame().getBuildingClassCreatedCount(gc.getInfoTypeForString("BUILDINGCLASS_SOUL_FORGE")) > 0:
				for iiX in range(iX-1, iX+2, 1):
					for iiY in range(iY-1, iY+2, 1):
						pPlot2 = CyMap().plot(iiX,iiY)
						if pPlot2.isCity():
							pCity = pPlot2.getPlotCity()
							if pCity.getNumRealBuilding(iSoulForge) > 0:
								pCity.changeProduction(unit.getExperience() + 10)
								CyInterface().addMessage(pCity.getOwner(),True,25,CyTranslator().getText("TXT_KEY_MESSAGE_SOUL_FORGE",()),'AS2D_DISCOVERBONUS',1,'Art/Interface/Buttons/Buildings/Soulforge.dds',ColorTypes(7),pCity.getX(),pCity.getY(),True,True)

			if pPlot.isCity():
				pCity = pPlot.getPlotCity()
				if pCity.getNumRealBuilding(gc.getInfoTypeForString('BUILDING_MOKKAS_CAULDRON')) > 0:
					if pCity.getOwner() == unit.getOwner():
						iUnit = cf.getUnholyVersion(unit)
						if iUnit != -1:
							newUnit = pPlayer.initUnit(iUnit, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
							newUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_DEMON'), True)
							newUnit.setDamage(50, PlayerTypes.NO_PLAYER)
							newUnit.finishMoves()
							szBuffer = gc.getUnitInfo(newUnit.getUnitType()).getDescription()
							CyInterface().addMessage(unit.getOwner(),True,25,CyTranslator().getText("TXT_KEY_MESSAGE_MOKKAS_CAULDRON",((szBuffer, ))),'AS2D_DISCOVERBONUS',1,'Art/Interface/Buttons/Buildings/Mokkas Cauldron.dds',ColorTypes(7),pCity.getX(),pCity.getY(),True,True)

			if (unit.getReligion() == gc.getInfoTypeForString('RELIGION_COUNCIL_OF_ESUS') or unit.getReligion() == gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL') or unit.getReligion() == gc.getInfoTypeForString('RELIGION_OCTOPUS_OVERLORDS') or unit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_DEATH1')) or unit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_ENTROPY1'))):
				cf.giftUnit(gc.getInfoTypeForString('UNIT_MANES'), gc.getInfoTypeForString('CIVILIZATION_INFERNAL'), 0, unit.plot(), unit.getOwner())
				cf.giftUnit(gc.getInfoTypeForString('UNIT_MANES'), gc.getInfoTypeForString('CIVILIZATION_INFERNAL'), 0, unit.plot(), unit.getOwner())
			elif (unit.getReligion() == gc.getInfoTypeForString('RELIGION_THE_EMPYREAN') or unit.getReligion() == gc.getInfoTypeForString('RELIGION_THE_ORDER') or unit.getReligion() == gc.getInfoTypeForString('RELIGION_RUNES_OF_KILMORPH') or (unit.getUnitCombatType() != gc.getInfoTypeForString('UNITCOMBAT_ANIMAL') and pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_MERCURIANS'))):
				cf.giftUnit(gc.getInfoTypeForString('UNIT_ANGEL'), gc.getInfoTypeForString('CIVILIZATION_MERCURIANS'), unit.getExperience(), unit.plot(), unit.getOwner())

			if unit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_SPIRIT_GUIDE')):
				if unit.getExperience() > 0:
					py = PyPlayer(iPlayer)
					lUnits = []
					for pLoopUnit in py.getUnitList():
						if pLoopUnit.isAlive():
							if not pLoopUnit.isOnlyDefensive():
								if not pLoopUnit.isDelayedDeath():
									lUnits.append(pLoopUnit)
					if len(lUnits) > 0:
						pUnit = lUnits[CyGame().getSorenRandNum(len(lUnits), "Spirit Guide")-1]
						iXP = unit.getExperience() / 2
						pUnit.changeExperience(iXP, -1, False, False, False)
#						unit.changeExperience(iXP * -1, -1, False, False, False)
						CyInterface().addMessage(unit.getOwner(),True,25,CyTranslator().getText("TXT_KEY_MESSAGE_SPIRIT_GUIDE",()),'AS2D_DISCOVERBONUS',1,'Art/Interface/Buttons/Promotions/SpiritGuide.dds',ColorTypes(7),pUnit.getX(),pUnit.getY(),True,True)

		if unit.getUnitType() == gc.getInfoTypeForString('UNIT_ACHERON'):
			unit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_HELD'), False)

		if CyGame().getWBMapScript():
			sf.onUnitKilled(unit, iAttacker)

#		if not self.__LOG_UNITKILLED:
#			return
#		CvUtil.pyPrint('Player %d Civilization %s Unit %s was killed by Player %d' 
#			%(player.getID(), player.getCivilizationName(), PyInfo.UnitInfo(unit.getUnitType()).getDescription(), attacker.getID()))

	def onUnitLost(self, argsList):
	## Platy Builder ##
		if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
	## Platy Builder ##
		'Unit Lost'
		unit = argsList[0]
		iPlayer = unit.getOwner()
		player = PyPlayer(iPlayer)
		pPlot = unit.plot()

		if unit.getUnitType() == gc.getInfoTypeForString('UNIT_TREANT'):
			if pPlot.getFeatureType() == -1:
				if pPlot.canHaveFeature(gc.getInfoTypeForString('FEATURE_FOREST_NEW')):
					if pPlot.getOwner() == iPlayer:
						if CyGame().getSorenRandNum(100, "Treant Spawn Chance") < 50:
							pPlot.setFeatureType(gc.getInfoTypeForString('FEATURE_FOREST_NEW'), 0)

		if not self.__LOG_UNITLOST:
			return
		CvUtil.pyPrint('%s was lost by Player %d Civilization %s' 
			%(PyInfo.UnitInfo(unit.getUnitType()).getDescription(), player.getID(), player.getCivilizationName()))

	def onUnitPromoted(self, argsList):
		'Unit Promoted'
		pUnit, iPromotion = argsList
		if not self.__LOG_UNITPROMOTED:
			return
		CvUtil.pyPrint('Unit Promotion Event: %s - %s' %(player.getCivilizationName(), pUnit.getName(),))

	def onUnitSelected(self, argsList):
		'Unit Selected'
		unit = argsList[0]
		player = PyPlayer(unit.getOwner())
		if (not self.__LOG_UNITSELECTED):
			return
		CvUtil.pyPrint('%s was selected by Player %d Civilization %s' 
			%(PyInfo.UnitInfo(unit.getUnitType()).getDescription(), player.getID(), player.getCivilizationName()))

	def onUnitRename(self, argsList):
		'Unit is renamed'
		pUnit = argsList[0]
		if (pUnit.getOwner() == gc.getGame().getActivePlayer()):
			self.__eventEditUnitNameBegin(pUnit)

	def onUnitPillage(self, argsList):
		'Unit pillages a plot'
		pUnit, iImprovement, iRoute, iOwner = argsList
		iPlotX = pUnit.getX()
		iPlotY = pUnit.getY()
		pPlot = CyMap().plot(iPlotX, iPlotY)
		pPlayer = gc.getPlayer(pUnit.getOwner())

		if (not self.__LOG_UNITPILLAGE):
			return
		CvUtil.pyPrint("Player %d's %s pillaged improvement %d and route %d at plot at (%d, %d)" 
			%(iOwner, PyInfo.UnitInfo(pUnit.getUnitType()).getDescription(), iImprovement, iRoute, iPlotX, iPlotY))

	def onUnitSpreadReligionAttempt(self, argsList):
		'Unit tries to spread religion to a city'
		pUnit, iReligion, bSuccess = argsList

		iX = pUnit.getX()
		iY = pUnit.getY()
		pPlot = CyMap().plot(iX, iY)
		pCity = pPlot.getPlotCity()

	def onUnitGifted(self, argsList):
		'Unit is gifted from one player to another'
		pUnit, iGiftingPlayer, pPlotLocation = argsList

	def onUnitBuildImprovement(self, argsList):
		'Unit begins enacting a Build (building an Improvement or Route)'
		pUnit, iBuild, bFinished = argsList

	def onGoodyReceived(self, argsList):
		'Goody received'
		iPlayer, pPlot, pUnit, iGoodyType = argsList
		if (not self.__LOG_GOODYRECEIVED):
			return
		CvUtil.pyPrint('%s received a goody' %(gc.getPlayer(iPlayer).getCivilizationDescription(0)),)

	def onGreatPersonBorn(self, argsList):
	## Platy Builder ##
		if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
	## Platy Builder ##
		'Unit Promoted'
		pUnit, iPlayer, pCity = argsList
		player = PyPlayer(iPlayer)
		if pUnit.isNone() or pCity.isNone():
			return
		if (not self.__LOG_GREATPERSON):
			return
		CvUtil.pyPrint('A %s was born for %s in %s' %(pUnit.getName(), player.getCivilizationName(), pCity.getName()))

	def onTechAcquired(self, argsList):
	## Platy Builder ##
		if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
	## Platy Builder ##
		'Tech Acquired'
		iTechType, iTeam, iPlayer, bAnnounce = argsList
		# Note that iPlayer may be NULL (-1) and not a refer to a player object
		pPlayer = gc.getPlayer(iPlayer)

		# Show tech splash when applicable
		if iPlayer > -1 and bAnnounce and not CyInterface().noTechSplash():
			if gc.getGame().isFinalInitialized() and not gc.getGame().GetWorldBuilderMode():
				if not gc.getGame().isNetworkMultiPlayer() and iPlayer == gc.getGame().getActivePlayer():
					popupInfo = CyPopupInfo()
					popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
					popupInfo.setData1(iTechType)
					popupInfo.setText(u"showTechSplash")
					popupInfo.addPopup(iPlayer)
		if iPlayer != -1 and iPlayer != gc.getBARBARIAN_PLAYER():
			pPlayer = gc.getPlayer(iPlayer)
			iReligion = -1
			if iTechType == gc.getInfoTypeForString('TECH_CORRUPTION_OF_SPIRIT'):
				iUnit = gc.getInfoTypeForString('UNIT_DISCIPLE_THE_ASHEN_VEIL')
				iReligion = gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL')
			elif iTechType == gc.getInfoTypeForString('TECH_ORDERS_FROM_HEAVEN'):
				iUnit = gc.getInfoTypeForString('UNIT_DISCIPLE_THE_ORDER')
				iReligion = gc.getInfoTypeForString('RELIGION_THE_ORDER')
			elif iTechType == gc.getInfoTypeForString('TECH_WAY_OF_THE_FORESTS'):
				iUnit = gc.getInfoTypeForString('UNIT_DISCIPLE_FELLOWSHIP_OF_LEAVES')
				iReligion = gc.getInfoTypeForString('RELIGION_FELLOWSHIP_OF_LEAVES')
			elif iTechType == gc.getInfoTypeForString('TECH_WAY_OF_THE_EARTHMOTHER'):
				iUnit = gc.getInfoTypeForString('UNIT_DISCIPLE_RUNES_OF_KILMORPH')
				iReligion = gc.getInfoTypeForString('RELIGION_RUNES_OF_KILMORPH')
			elif iTechType == gc.getInfoTypeForString('TECH_MESSAGE_FROM_THE_DEEP'):
				iUnit = gc.getInfoTypeForString('UNIT_DISCIPLE_OCTOPUS_OVERLORDS')
				iReligion = gc.getInfoTypeForString('RELIGION_OCTOPUS_OVERLORDS')
			elif iTechType == gc.getInfoTypeForString('TECH_HONOR'):
				iUnit = gc.getInfoTypeForString('UNIT_DISCIPLE_EMPYREAN')
				iReligion = gc.getInfoTypeForString('RELIGION_THE_EMPYREAN')
			elif iTechType == gc.getInfoTypeForString('TECH_DECEPTION'):
				iUnit = gc.getInfoTypeForString('UNIT_NIGHTWATCH')
				iReligion = gc.getInfoTypeForString('RELIGION_COUNCIL_OF_ESUS')
			if iReligion != -1:
				if (iReligion==pPlayer.getFavoriteReligion()):
					pPlayer.getCapitalCity().setHasReligion(iReligion,True,True,True)	
				if CyGame().isReligionFounded(iReligion):
					cf.giftUnit(iUnit, pPlayer.getCivilizationType(), 0, -1, -1)

		if not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_HYBOREM_OR_BASIUM):
			if iTechType == gc.getInfoTypeForString('TECH_INFERNAL_PACT') and iPlayer != -1:
				#iCount = 0
				#for iTeam in range(gc.getMAX_TEAMS()):
					#pTeam = gc.getTeam(iTeam)
					#if pTeam.isHasTech(gc.getInfoTypeForString('TECH_INFERNAL_PACT')):
						#iCount = iCount + 1
				#if iCount == 1:
				if not CyGame().isCivEverActive(gc.getInfoTypeForString('CIVILIZATION_INFERNAL')):
					iInfernalPlayer = pPlayer.initNewEmpire(gc.getInfoTypeForString('LEADER_HYBOREM'), gc.getInfoTypeForString('CIVILIZATION_INFERNAL'))
					if iInfernalPlayer != PlayerTypes.NO_PLAYER:
						pInfernalPlayer = gc.getPlayer(iInfernalPlayer)
						pTeam = gc.getTeam(pInfernalPlayer.getTeam())

						pBestPlot = -1
						iBestPlotValue = -1
						for iLoop in range (CyMap().numPlots()):
							pPlot = CyMap().plotByIndex(iLoop)
							iX = pPlot.getX()
							iY = pPlot.getY()
							iPlotValue = -1
							if pInfernalPlayer.canFound(iX, iY):
								if pPlot.getNumUnits() == 0:
									iPlotValue = CyGame().getSorenRandNum(50, "Place Hyborem")
									iPlotValue += 50
									iPlotValue += pPlot.area().getNumTiles() * 2
									iPlotValue += pPlot.area().getNumUnownedTiles() * 10
									if pPlot.isAdjacentOwned():
										iPlotValue -= 150;

									## Check Big Fat Cross for other players, resources and terrain
									for iCityPlotX in range(iX-1, iX+2, 1):
										for iCityPlotY in range(iY-1, iY+2, 1):
											pCityPlot = CyMap().plot(iCityPlotX,iCityPlotY)
											iCityTerrain = pCityPlot.getTerrainType()
											iCityPlot = pCityPlot.getPlotType()
											iCityBonus = pCityPlot.getBonusType(TeamTypes.NO_TEAM)

											for jPlayer in range(gc.getMAX_PLAYERS()):
												lPlayer = gc.getPlayer(jPlayer)
												if lPlayer.isAlive():
													if pCityPlot.getCulture(jPlayer) > 100:
														iPlotValue -= 150
#											if pCityPlot.isOwned():
#												iPlotValue -= 25
#											else:
											iPlotValue += 15
											if (iCityTerrain == gc.getInfoTypeForString('TERRAIN_SNOW')) or (iCityTerrain == gc.getInfoTypeForString("TERRAIN_DESERT")):
												iPlotValue -= 25
											elif (iCityTerrain == gc.getInfoTypeForString('TERRAIN_TUNDRA')):
												iPlotValue -= 10
#											if (pCityPlot.isWater()):
#												iPlotValue -= 25
#											if not iCityBonus == BonusTypes.NO_BONUS:
#												iPlotValue += gc.getBonusInfo(iCityBonus).getYieldChange(YieldTypes.YIELD_PRODUCTION) * 25
#												iPlotValue += gc.getBonusInfo(iCityBonus).getYieldChange(YieldTypes.YIELD_COMMERCE) * 15
#												iPlotValue += gc.getBonusInfo(iCityBonus).getAIObjective() * 25

							if iPlotValue > iBestPlotValue:
								iBestPlotValue = iPlotValue
								pBestPlot = pPlot

						if pBestPlot != -1:
							iFounderTeam = gc.getPlayer(iPlayer).getTeam()
							pFounderTeam = gc.getTeam(gc.getPlayer(iPlayer).getTeam())
							iInfernalTeam = gc.getPlayer(iInfernalPlayer).getTeam()
							pInfernalTeam = gc.getTeam(iInfernalTeam)

							iBarbTeam = gc.getBARBARIAN_TEAM()
							pInfernalTeam.makePeace(iBarbTeam)
							pInfernalPlayer.AI_changeAttitudeExtra(iPlayer, 4)

							iX = pBestPlot.getX()
							iY = pBestPlot.getY()
							pNewUnit = pInfernalPlayer.initUnit(gc.getInfoTypeForString('UNIT_HYBOREM'), iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
							pNewUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_IMMORTAL'), True)
							pNewUnit.setHasCasted(True)
							pNewUnit.setAvatarOfCivLeader(True)
							iIronWeapon		= gc.getInfoTypeForString('PROMOTION_IRON_WEAPONS')
							iMobility1		= gc.getInfoTypeForString('PROMOTION_MOBILITY1')
							iSettlerBonus	= gc.getInfoTypeForString('PROMOTION_STARTING_SETTLER')
							liStartingUnits = [	(2,	gc.getInfoTypeForString('UNIT_LONGBOWMAN'),	[iMobility1]				),
												(2,	gc.getInfoTypeForString('UNIT_CHAMPION'),	[iMobility1, iIronWeapon]	),
												(1,	gc.getInfoTypeForString('UNIT_WORKER'),		[]							),
												(1,	gc.getInfoTypeForString('UNIT_IMP'),		[iMobility1]				),
												(3,	gc.getInfoTypeForString('UNIT_MANES'),		[]							),
												(2,	gc.getInfoTypeForString('UNIT_SETTLER'),	[iSettlerBonus]				)	]
							for iNumUnits, iUnit, liPromotions in liStartingUnits:
								for iLoop in range(iNumUnits):
									pNewUnit = pInfernalPlayer.initUnit(iUnit, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
									for iPromotion in liPromotions:
										pNewUnit.setHasPromotion(iPromotion, True)

							if (game.isOption(GameOptionTypes.GAMEOPTION_ADVANCED_TACTICS)):
								pFounderTeam.setHasEmbassy(iInfernalTeam, True)
								pInfernalTeam.setHasEmbassy(iFounderTeam, True)

							pFounderTeam.signOpenBorders(iInfernalTeam)
							pInfernalTeam.signOpenBorders(iFounderTeam)
							for iPlotIndex in range(CyMap().numPlots()):
								pLoopPlot = CyMap().plotByIndex(iPlotIndex)
								if pLoopPlot.isRevealed(iFounderTeam, False):
									pLoopPlot.setRevealed(iInfernalTeam, True, False, iFounderTeam)
								if pLoopPlot.isRevealed(iInfernalTeam, False):
									pLoopPlot.setRevealed(iFounderTeam, True, False, iInfernalTeam)
							for iLoopTeam in range(gc.getMAX_CIV_TEAMS()):
								pLoopTeam = gc.getTeam(iLoopTeam)
								if pLoopTeam.isHasMet(iFounderTeam):
									if pLoopTeam.isAlive():
										pLoopTeam.meet(iInfernalTeam, True)
							for iTeam in range(gc.getMAX_TEAMS()):
								if iTeam != iBarbTeam:
									pTeam = gc.getTeam(iTeam)
									if pTeam.isAlive():
										if pFounderTeam.isAtWar(iTeam):
											pInfernalTeam.declareWar(iTeam, False, WarPlanTypes.WARPLAN_LIMITED)

							if gc.getPlayer(iPlayer).isHuman():
								popupInfo = CyPopupInfo()
								popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
								popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_CONTROL_INFERNAL",()))
								popupInfo.setData1(iPlayer)
								popupInfo.setData2(iInfernalPlayer)
								popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_YES", ()), "")
								popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_NO", ()), "")
								popupInfo.setOnClickedPythonCallback("reassignPlayer")
								popupInfo.addPopup(iPlayer)

		if CyGame().getWBMapScript():
			sf.onTechAcquired(iTechType, iTeam, iPlayer, bAnnounce)

		if (not self.__LOG_TECH):
			return
		CvUtil.pyPrint('%s was finished by Team %d' 
			%(PyInfo.TechnologyInfo(iTechType).getDescription(), iTeam))

	def onTechSelected(self, argsList):
		'Tech Selected'
		iTechType, iPlayer = argsList
		if (not self.__LOG_TECH):
			return
		CvUtil.pyPrint('%s was selected by Player %d' %(PyInfo.TechnologyInfo(iTechType).getDescription(), iPlayer))

	def onReligionFounded(self, argsList):
	## Platy Builder ##
		if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
	## Platy Builder ##
		'Religion Founded'
		iReligion, iFounder = argsList
		player = PyPlayer(iFounder)
		pPlayer = gc.getPlayer(iFounder)

		iCityId = gc.getGame().getHolyCity(iReligion).getID()
		if gc.getGame().isFinalInitialized() and not gc.getGame().GetWorldBuilderMode():
			if not gc.getGame().isNetworkMultiPlayer() and iFounder == gc.getGame().getActivePlayer():
				popupInfo = CyPopupInfo()
				popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
				popupInfo.setData1(iReligion)
				popupInfo.setData2(iCityId)
				if iReligion == gc.getInfoTypeForString('RELIGION_THE_EMPYREAN') or iReligion == gc.getInfoTypeForString('RELIGION_COUNCIL_OF_ESUS'):
					popupInfo.setData3(3)
				else:
					popupInfo.setData3(1)
				popupInfo.setText(u"showWonderMovie")
				popupInfo.addPopup(iFounder)


		if CyGame().getWBMapScript():
			sf.onReligionFounded(iReligion, iFounder)

		if (not self.__LOG_RELIGION):
			return
		CvUtil.pyPrint('Player %d Civilization %s has founded %s'
			%(iFounder, player.getCivilizationName(), gc.getReligionInfo(iReligion).getDescription()))

	def onReligionSpread(self, argsList):
	## Platy Builder ##
		if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
	## Platy Builder ##
		'Religion Has Spread to a City'
		iReligion, iOwner, pSpreadCity = argsList
		player = PyPlayer(iOwner)
		pPlayer = gc.getPlayer(iOwner)

		iOrder = gc.getInfoTypeForString('RELIGION_THE_ORDER')
		iVeil = gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL')

		if iReligion == iOrder and CyGame().getGameTurn() != CyGame().getStartTurn():
			if (pPlayer.getStateReligion() == iOrder and pSpreadCity.getOccupationTimer() <= 0):
				if (CyGame().getSorenRandNum(100, "Order Spawn") < gc.getDefineINT('ORDER_SPAWN_CHANCE')):
					eTeam = gc.getTeam(pPlayer.getTeam())
					if eTeam.isHasTech(gc.getInfoTypeForString('TECH_FANATICISM')):
						iUnit = gc.getInfoTypeForString('UNIT_CRUSADER')
						CyInterface().addMessage(iOwner,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_ORDER_SPAWN_CRUSADER",()),'AS2D_UNIT_BUILD_UNIT',1,'Art/Interface/Buttons/Units/Crusader.dds',ColorTypes(8),pSpreadCity.getX(),pSpreadCity.getY(),True,True)
					else:
						iUnit = gc.getInfoTypeForString('UNIT_DISCIPLE_THE_ORDER')
						CyInterface().addMessage(iOwner,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_ORDER_SPAWN_ACOLYTE",()),'AS2D_UNIT_BUILD_UNIT',1,'Art/Interface/Buttons/Units/Disciple Order.dds',ColorTypes(8),pSpreadCity.getX(),pSpreadCity.getY(),True,True)
					newUnit = pPlayer.initUnit(iUnit, pSpreadCity.getX(), pSpreadCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
		if pSpreadCity.isHasReligion(iVeil) and iReligion == iOrder:
			if not pSpreadCity.isHolyCity():
				result = CyGame().getSorenRandNum(100, "Order-Veil")
				if (result < 35):
					CyInterface().addMessage(iOwner,True,25,"A bloodbath ensues as the Order and Veil battle for control of the city! In the end, Ritualists lie dead in the streets. The Order is triumphant!",'AS2D_UNIT_BUILD_UNIT',1,'Art/Interface/Buttons/Religions/Order.dds',ColorTypes(14),pSpreadCity.getX(),pSpreadCity.getY(),True,True)
					pSpreadCity.setHasReligion(gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL'), False, True, True)
					iPop = pSpreadCity.getPopulation()-1
					if (iPop > 0):
						pSpreadCity.setPopulation(iPop)
					CyGame().changeGlobalCounter(-1)
				else:
					CyInterface().addMessage(iOwner,True,25,"A bloodbath ensues as the Order and Veil battle for control of the city! In the end, the streets are coated in Crusader blood. The Veil is victorious!",'AS2D_UNIT_BUILD_UNIT',1,'Art/Interface/Buttons/Religions/Ashen.dds',ColorTypes(5),pSpreadCity.getX(),pSpreadCity.getY(),True,True)
					pSpreadCity.setHasReligion(gc.getInfoTypeForString('RELIGION_THE_ORDER'), False, True, True)
		elif pSpreadCity.isHasReligion(iOrder) and iReligion == iVeil:
			if not pSpreadCity.isHolyCity():
				result = CyGame().getSorenRandNum(100, "Veil-Order")
				if (result < 35):
					CyInterface().addMessage(iOwner,True,25,"A bloodbath ensues as the Order and Veil battle for control of the city! In the end, the streets are coated in Crusader blood. The Veil is victorious!",'AS2D_UNIT_BUILD_UNIT',1,'Art/Interface/Buttons/Religions/Ashen.dds',ColorTypes(5),pSpreadCity.getX(),pSpreadCity.getY(),True,True)
					pSpreadCity.setHasReligion(gc.getInfoTypeForString('RELIGION_THE_ORDER'), False, True, True)
					iPop = pSpreadCity.getPopulation()-1
					if (iPop > 0):
						pSpreadCity.setPopulation(iPop)
					CyGame().changeGlobalCounter(1)
				else :
					CyInterface().addMessage(iOwner,True,25,"A bloodbath ensues as the Order and Veil battle for control of the city! In the end, Ritualists lie dead in the streets. The Order is triumphant!",'AS2D_UNIT_BUILD_UNIT',1,'Art/Interface/Buttons/Religions/Order.dds',ColorTypes(14),pSpreadCity.getX(),pSpreadCity.getY(),True,True)
					pSpreadCity.setHasReligion(gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL'), False, True, True)

		if (not self.__LOG_RELIGIONSPREAD):
			return
		CvUtil.pyPrint('%s has spread to Player %d Civilization %s city of %s'
			%(gc.getReligionInfo(iReligion).getDescription(), iOwner, player.getCivilizationName(), pSpreadCity.getName()))

	def onReligionRemove(self, argsList):
	## Platy Builder ##
		if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
	## Platy Builder ##
		'Religion Has been removed from a City'
		iReligion, iOwner, pRemoveCity = argsList
		player = PyPlayer(iOwner)
		if (not self.__LOG_RELIGIONSPREAD):
			return
		CvUtil.pyPrint('%s has been removed from Player %d Civilization %s city of %s'
			%(gc.getReligionInfo(iReligion).getDescription(), iOwner, player.getCivilizationName(), pRemoveCity.getName()))

	def onCorporationFounded(self, argsList):
	## Platy Builder ##
		if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
	## Platy Builder ##
		'Corporation Founded'
		iCorporation, iFounder = argsList
		player = PyPlayer(iFounder)
		if (not self.__LOG_RELIGION):
			return
		CvUtil.pyPrint('Player %d Civilization %s has founded %s'
			%(iFounder, player.getCivilizationName(), gc.getCorporationInfo(iCorporation).getDescription()))

	def onCorporationSpread(self, argsList):
	## Platy Builder ##
		if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
	## Platy Builder ##
		'Corporation Has Spread to a City'
		iCorporation, iOwner, pSpreadCity = argsList
		player = PyPlayer(iOwner)
		if (not self.__LOG_RELIGIONSPREAD):
			return
		CvUtil.pyPrint('%s has spread to Player %d Civilization %s city of %s'
			%(gc.getCorporationInfo(iCorporation).getDescription(), iOwner, player.getCivilizationName(), pSpreadCity.getName()))

	def onCorporationRemove(self, argsList):
	## Platy Builder ##
		if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
	## Platy Builder ##
		'Corporation Has been removed from a City'
		iCorporation, iOwner, pRemoveCity = argsList
		player = PyPlayer(iOwner)
		if (not self.__LOG_RELIGIONSPREAD):
			return
		CvUtil.pyPrint('%s has been removed from Player %d Civilization %s city of %s'
			%(gc.getReligionInfo(iReligion).getDescription(), iOwner, player.getCivilizationName(), pRemoveCity.getName()))

	def onGoldenAge(self, argsList):
	## Platy Builder ##
		if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
	## Platy Builder ##
		'Golden Age'
		iPlayer = argsList[0]
		player = PyPlayer(iPlayer)
		if (not self.__LOG_GOLDENAGE):
			return
		CvUtil.pyPrint('Player %d Civilization %s has begun a golden age'
			%(iPlayer, player.getCivilizationName()))

	def onEndGoldenAge(self, argsList):
	## Platy Builder ##
		if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
	## Platy Builder ##
		'End Golden Age'
		iPlayer = argsList[0]
		player = PyPlayer(iPlayer)
		if (not self.__LOG_ENDGOLDENAGE):
			return
		CvUtil.pyPrint('Player %d Civilization %s golden age has ended'
			%(iPlayer, player.getCivilizationName()))

	def onChangeWar(self, argsList):
	## Platy Builder ##
		if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
	## Platy Builder ##
		'War Status Changes'
		bIsWar = argsList[0]
		iTeam = argsList[1]
		iRivalTeam = argsList[2]

	def onChat(self, argsList):
		'Chat Message Event'
		chatMessage = "%s" %(argsList[0],)

	def onSetPlayerAlive(self, argsList):
		'Set Player Alive Event'
		iPlayerID = argsList[0]
		bNewValue = argsList[1]
		CvUtil.pyPrint("Player %d's alive status set to: %d" %(iPlayerID, int(bNewValue)))

		if not bNewValue and gc.getGame().getGameTurnYear() >= 5:
			pPlayer = gc.getPlayer(iPlayerID)
			if pPlayer.getAlignment() == gc.getInfoTypeForString('ALIGNMENT_GOOD'):
				CyGame().changeGlobalCounter(5)
			elif pPlayer.getAlignment() == gc.getInfoTypeForString('ALIGNMENT_EVIL'):
				CyGame().changeGlobalCounter(-5)
			if CyGame().getWBMapScript():
				sf.playerDefeated(pPlayer)
			else:
				iLeader = pPlayer.getLeaderType()
				if iLeader == gc.getInfoTypeForString('LEADER_ALEXIS'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_CALABIM",()),'art/interface/popups/Alexis.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_AMELANCHIER'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_LJOSALFAR",()),'art/interface/popups/Amelanchier.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_ARENDEL'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_LJOSALFAR",()),'art/interface/popups/Arendel.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_ARTURUS'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_KHAZAD",()),'art/interface/popups/Arturus.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_AURIC'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_ILLIANS",()),'art/interface/popups/Auric.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_BASIUM'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_MERCURIANS",()),'art/interface/popups/Basium.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_BEERI'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_LUCHUIRP",()),'art/interface/popups/Beeri.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_CAPRIA'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_BANNOR",()),'art/interface/popups/Capria.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_CARDITH'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_KURIOTATES",()),'art/interface/popups/Cardith.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_CASSIEL'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_GRIGORI",()),'art/interface/popups/Cassiel.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_CHARADON'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_DOVIELLO",()),'art/interface/popups/Charadon.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_DAIN'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_AMURITES",()),'art/interface/popups/Dain.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_DECIUS'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_DECIUS",()),'art/interface/popups/Decius.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_EINION'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_ELOHIM",()),'art/interface/popups/Einion.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_ETHNE'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_ELOHIM",()),'art/interface/popups/Ethne.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_FAERYL'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_SVARTALFAR",()),'art/interface/popups/Faeryl.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_FALAMAR'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_LANUN",()),'art/interface/popups/Falamar.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_FLAUROS'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_CALABIM",()),'art/interface/popups/Flauros.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_GARRIM'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_LUCHUIRP",()),'art/interface/popups/Garrim.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_HANNAH'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_HANNAH",()),'art/interface/popups/Hannah.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_HYBOREM'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_INFERNAL",()),'art/interface/popups/Hyborem.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_JONAS'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_CLAN_OF_EMBERS",()),'art/interface/popups/Jonus.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_KANDROS'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_KHAZAD",()),'art/interface/popups/Kandros.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_KEELYN'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_KEELYN",()),'art/interface/popups/Keelyn.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_MAHALA'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_DOVIELLO",()),'art/interface/popups/Mahala.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_SANDALPHON'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_SIDAR",()),'art/interface/popups/Sandalphon.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_OS-GABELLA'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_SHEAIM",()),'art/interface/popups/Os-Gabella.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_PERPENTACH'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_BALSERAPHS",()),'art/interface/popups/Perpentach.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_RHOANNA'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_HIPPUS",()),'art/interface/popups/Rhoanna.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_SABATHIEL'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_BANNOR",()),'art/interface/popups/Sabathiel.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_SHEELBA'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_CLAN_OF_EMBERS",()),'art/interface/popups/Sheelba.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_TASUNKE'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_HIPPUS",()),'art/interface/popups/Tasunke.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_TEBRYN'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_SHEAIM",()),'art/interface/popups/Tebryn.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_THESSA'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_LJOSALFAR",()),'art/interface/popups/Thessa.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_VALLEDIA'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_AMURITES",()),'art/interface/popups/Valledia.dds')
				elif iLeader == gc.getInfoTypeForString('LEADER_VARN'):
					cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_MALAKIM",()),'art/interface/popups/Varn.dds')

	def onPlayerChangeStateReligion(self, argsList):
	## Platy Builder ##
		if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
	## Platy Builder ##
		'Player changes his state religion'
		iPlayer, iNewReligion, iOldReligion = argsList
		if iNewReligion != iOldReligion:
			pPlayer = gc.getPlayer(iPlayer)
			if iNewReligion == -1:
				iCurrentEra = pPlayer.getCurrentEra()
				iEra = iCurrentEra
				if not (iCurrentEra == gc.getInfoTypeForString('ERA_ANCIENT') or iCurrentEra == gc.getInfoTypeForString('ERA_CLASSICAL') or iCurrentEra == gc.getInfoTypeForString('ERA_MEDIEVAL')):
					iEra = gc.getGame().getStartEra()
					pPlayer.setCurrentEra(iEra)
			elif iNewReligion == gc.getInfoTypeForString('RELIGION_THE_ORDER'):
				pPlayer.setCurrentEra(gc.getInfoTypeForString('ERA_ORDE'))
			elif iNewReligion == gc.getInfoTypeForString('RELIGION_THE_EMPYREAN'):
				pPlayer.setCurrentEra(gc.getInfoTypeForString('ERA_EMPY'))
			elif iNewReligion == gc.getInfoTypeForString('RELIGION_RUNES_OF_KILMORPH'):
				pPlayer.setCurrentEra(gc.getInfoTypeForString('ERA_RUNE'))
			elif iNewReligion == gc.getInfoTypeForString('RELIGION_FELLOWSHIP_OF_LEAVES'):
				pPlayer.setCurrentEra(gc.getInfoTypeForString('ERA_LEAF'))
			elif iNewReligion == gc.getInfoTypeForString('RELIGION_OCTOPUS_OVERLORDS'):
				pPlayer.setCurrentEra(gc.getInfoTypeForString('ERA_OCTO'))
			elif iNewReligion == gc.getInfoTypeForString('RELIGION_COUNCIL_OF_ESUS'):
				pPlayer.setCurrentEra(gc.getInfoTypeForString('ERA_COUN'))
			elif iNewReligion == gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL'):
				pPlayer.setCurrentEra(gc.getInfoTypeForString('ERA_VEIL'))

	def onPlayerGoldTrade(self, argsList):
		'Player Trades gold to another player'
		iFromPlayer, iToPlayer, iGoldAmount = argsList

	def onCityBuilt(self, argsList):
		'City Built'
		city = argsList[0]
		pPlot = city.plot()
		pPlayer = gc.getPlayer(city.getOwner())

		if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_INFERNAL'):
			city.setHasReligion(gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL'), True, True, True)
			city.setPopulation(3)
			city.setNumRealBuilding(gc.getInfoTypeForString('BUILDING_ELDER_COUNCIL'), 1)
			city.setNumRealBuilding(gc.getInfoTypeForString('BUILDING_TRAINING_YARD'), 1)
			city.setNumRealBuilding(gc.getInfoTypeForString('BUILDING_OBSIDIAN_GATE'), 1)
			city.setNumRealBuilding(gc.getInfoTypeForString('BUILDING_FORGE'), 1)
			city.setNumRealBuilding(gc.getInfoTypeForString('BUILDING_MAGE_GUILD'), 1)
			city.setNumRealBuilding(gc.getInfoTypeForString('BUILDING_DEMONIC_CITIZENS'), 1)

		elif pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_BARBARIAN'):
			eTeam = gc.getTeam(gc.getPlayer(gc.getBARBARIAN_PLAYER()).getTeam())
			iUnit = gc.getInfoTypeForString('UNIT_WARRIOR')
			if (eTeam.isHasTech(gc.getInfoTypeForString('TECH_BRONZE_WORKING')) or CyGame().getStartEra() > gc.getInfoTypeForString('ERA_ANCIENT') ):
				iUnit = gc.getInfoTypeForString('UNIT_AXEMAN')
			if (eTeam.isHasTech(gc.getInfoTypeForString('TECH_IRON_WORKING')) or CyGame().getStartEra() > gc.getInfoTypeForString('ERA_CLASSICAL') ):
				iUnit = gc.getInfoTypeForString('UNIT_OGRE')
			newUnit = pPlayer.initUnit(iUnit, city.getX(), city.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)
			newUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_ORC'), true)
			iUnit = gc.getInfoTypeForString('UNIT_ARCHER')
			if eTeam.isHasTech(gc.getInfoTypeForString('TECH_BOWYERS')) or CyGame().getStartEra() > gc.getInfoTypeForString('ERA_CLASSICAL'):
				iUnit = gc.getInfoTypeForString('UNIT_LONGBOWMAN')
			newUnit2 = pPlayer.initUnit(iUnit, city.getX(), city.getY(), UnitAITypes.UNITAI_CITY_DEFENSE, DirectionTypes.DIRECTION_SOUTH)
			newUnit3 = pPlayer.initUnit(iUnit, city.getX(), city.getY(), UnitAITypes.UNITAI_CITY_DEFENSE, DirectionTypes.DIRECTION_SOUTH)
			newUnit2.setHasPromotion(gc.getInfoTypeForString('PROMOTION_ORC'), True)
			newUnit3.setHasPromotion(gc.getInfoTypeForString('PROMOTION_ORC'), True)
			if not eTeam.isHasTech(gc.getInfoTypeForString('TECH_ARCHERY')) or CyGame().getStartEra() == gc.getInfoTypeForString('ERA_ANCIENT'):
				newUnit2.setHasPromotion(gc.getInfoTypeForString('PROMOTION_WEAK'), True)
				newUnit3.setHasPromotion(gc.getInfoTypeForString('PROMOTION_WEAK'), True)

		if CyGame().getWBMapScript():
			sf.onCityBuilt(city)

		if (city.getOwner() == CyGame().getActivePlayer())and ( CyGame().getAIAutoPlay(CyGame().getActivePlayer()) == 0 ):
			if not CyGame().GetWorldBuilderMode():#Platy WorldBuilder
				self.__eventEditCityNameBegin(city, False)
		CvUtil.pyPrint('City Built Event: %s' %(city.getName()))

	def onCityRazed(self, argsList):
	## Platy Builder ##
		if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
	## Platy Builder ##
		'City Razed'
		city, iPlayer = argsList
		iOwner = city.findHighestCulture()

#### messages - wonder destroyed start by The_J (modified by Terkhen) ####
		if city.getNumWorldWonders() > 0:
			for i in range(gc.getNumBuildingInfos()):
				if city.getNumBuilding(i) > 0:
					pThisBuilding = gc.getBuildingInfo(i)
					if gc.getBuildingClassInfo(pThisBuilding.getBuildingClassType()).getMaxGlobalInstances() == 1:
						pConquerPlayer = gc.getPlayer(city.getOwner())
						iConquerTeam = pConquerPlayer.getTeam()
						sConquerName = pConquerPlayer.getName()
						sWonderName = pThisBuilding.getDescription()
						iX = city.getX()
						iY = city.getY()

						for iLoopPlayer in range (gc.getMAX_CIV_PLAYERS()):
							iLoopTeam = gc.getPlayer(iLoopPlayer).getTeam()
							if iLoopTeam == iConquerTeam or gc.getTeam(iLoopTeam).isHasMet(iConquerTeam):

								if iLoopPlayer == city.getOwner():
									sText = "TXT_KEY_YOU_DESTROYED_WONDER"
								else:
									sText = "TXT_KEY_DESTROYED_WONDER"
								CyInterface().addMessage(iLoopPlayer, False, 15, CyTranslator().getText(sText, (sConquerName,sWonderName)), '', 0,'Art/Interface/Buttons/General/warning_popup.dds', ColorTypes(gc.getInfoTypeForString("COLOR_RED")), iX, iY, True, True)
#### messages - wonder destroyed end ####

		# Partisans!
#		if city.getPopulation > 1 and iOwner != -1 and iPlayer != -1:
#			owner = gc.getPlayer(iOwner)
#			if not owner.isBarbarian() and owner.getNumCities() > 0:
#				if gc.getTeam(owner.getTeam()).isAtWar(gc.getPlayer(iPlayer).getTeam()):
#					if gc.getNumEventTriggerInfos() > 0: # prevents mods that don't have events from getting an error
#						iEvent = CvUtil.findInfoTypeNum(gc.getEventTriggerInfo, gc.getNumEventTriggerInfos(),'EVENTTRIGGER_PARTISANS')
#						if iEvent != -1 and gc.getGame().isEventActive(iEvent) and owner.getEventTriggerWeight(iEvent) >= 0:
#							triggerData = owner.initTriggeredData(iEvent, True, -1, city.getX(), city.getY(), iPlayer, city.getID(), -1, -1, -1, -1)

		iAngel = gc.getInfoTypeForString('UNIT_ANGEL')
		iInfernal = gc.getInfoTypeForString('CIVILIZATION_INFERNAL')
		iManes = gc.getInfoTypeForString('UNIT_MANES')
		iMercurians = gc.getInfoTypeForString('CIVILIZATION_MERCURIANS')
		pPlayer = gc.getPlayer(iPlayer)
		if gc.getPlayer(city.getOriginalOwner()).getAlignment() == gc.getInfoTypeForString('ALIGNMENT_EVIL'):
			if gc.getPlayer(city.getOriginalOwner()).getCivilizationType() != iInfernal:
				for i in range(city.getPopulation()):
					cf.giftUnit(iManes, iInfernal, 0, city.plot(), city.getOwner())

		elif gc.getPlayer(city.getOriginalOwner()).getAlignment() == gc.getInfoTypeForString('ALIGNMENT_NEUTRAL'):
			for i in range((city.getPopulation() / 4) + 1):
				cf.giftUnit(iManes, iInfernal, 0, city.plot(), city.getOwner())
				cf.giftUnit(iManes, iInfernal, 0, city.plot(), city.getOwner())
				cf.giftUnit(iAngel, iMercurians, 0, city.plot(), city.getOwner())

		elif gc.getPlayer(city.getOriginalOwner()).getAlignment() == gc.getInfoTypeForString('ALIGNMENT_GOOD'):
			for i in range((city.getPopulation() / 2) + 1):
				cf.giftUnit(iAngel, iMercurians, 0, city.plot(), city.getOwner())

		pPlot = city.plot()
		iPop = city.getPopulation()
		iCalabim = gc.getInfoTypeForString('CIVILIZATION_CALABIM')
		if pPlayer.getCivilizationType() == iCalabim and iPop > 2:
			iVampire = gc.getInfoTypeForString('PROMOTION_VAMPIRE')
			for i in range(pPlot.getNumUnits()):
				if iPop < 3: break
				pUnit = pPlot.getUnit(i)
				if pUnit.isHasPromotion(iVampire):
					pUnit.changeExperience(iPop, -1, False, False, False)
					iPop = iPop - 1

		if CyGame().getWBMapScript():
			sf.onCityRazed(city, iPlayer)

		CvUtil.pyPrint("City Razed Event: %s" %(city.getName(),))

	def onCityAcquired(self, argsList):
	## Platy Builder ##
		if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
	## Platy Builder ##
		'City Acquired'
		iPreviousOwner,iNewOwner,pCity,bConquest,bTrade = argsList
		pPlayer = gc.getPlayer(iNewOwner)
		pPrevious = gc.getPlayer(iPreviousOwner)

## FFH
		if pPrevious.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_INFERNAL'):
			pCity.setNumRealBuilding(gc.getInfoTypeForString('BUILDING_OBSIDIAN_GATE'), 0)

		if CyGame().getWBMapScript():
			sf.onCityAcquired(iPreviousOwner, iNewOwner, pCity, bConquest, bTrade)

		if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_INFERNAL'):
			pCity.setNumRealBuilding(gc.getInfoTypeForString('BUILDING_ELDER_COUNCIL'), 1)
			pCity.setNumRealBuilding(gc.getInfoTypeForString('BUILDING_TRAINING_YARD'), 1)
			pCity.setNumRealBuilding(gc.getInfoTypeForString('BUILDING_OBSIDIAN_GATE'), 1)
			pCity.setNumRealBuilding(gc.getInfoTypeForString('BUILDING_FORGE'), 1)
			pCity.setNumRealBuilding(gc.getInfoTypeForString('BUILDING_MAGE_GUILD'), 1)
			pCity.setNumRealBuilding(gc.getInfoTypeForString('BUILDING_DEMONIC_CITIZENS'), 1)
## END FFH

	def onCityAcquiredAndKept(self, argsList):
		'City Acquired and Kept'
		iOwner,pCity = argsList

		#Functions added here tend to cause OOS issues

#### messages - wonder captured start by The_J (modified by Terkhen) ####
		#UI only stuff should be okay, though.
		if pCity.getNumWorldWonders() > 0:
			for i in range(gc.getNumBuildingInfos()):
				if pCity.getNumBuilding(i) > 0:
					pThisBuilding = gc.getBuildingInfo(i)
					if gc.getBuildingClassInfo(pThisBuilding.getBuildingClassType()).getMaxGlobalInstances() == 1:
						pConquerPlayer = gc.getPlayer(pCity.getOwner())
						iConquerTeam = pConquerPlayer.getTeam()
						sConquerName = pConquerPlayer.getName()
						sWonderName = pThisBuilding.getDescription()
						iX = pCity.getX()
						iY = pCity.getY()

						for iLoopPlayer in range (gc.getMAX_CIV_PLAYERS()):
							iLoopTeam = gc.getPlayer(iLoopPlayer).getTeam()
							if iLoopTeam == iConquerTeam or gc.getTeam(iLoopTeam).isHasMet(iConquerTeam):

								if iLoopPlayer == pCity.getOwner():
									sText = "TXT_KEY_YOU_CAPTURED_WONDER"
								else:
									sText = "TXT_KEY_CAPTURED_WONDER"

								if iLoopTeam == iConquerTeam:
									sColor = "COLOR_GREEN"
								else:
									sColor = "COLOR_RED"
								CyInterface().addMessage(iLoopPlayer, False, 15, CyTranslator().getText(sText, (sConquerName,sWonderName)), '', 0,'Art/Interface/Buttons/General/warning_popup.dds', ColorTypes(gc.getInfoTypeForString(sColor)), iX, iY, True, True)
#### messages - wonder captured end ####

		CvUtil.pyPrint('City Acquired and Kept Event: %s' %(pCity.getName()))

	def onCityLost(self, argsList):
		'City Lost'
		city = argsList[0]
		player = PyPlayer(city.getOwner())
		if (not self.__LOG_CITYLOST):
			return
		CvUtil.pyPrint('City %s was lost by Player %d Civilization %s' 
			%(city.getName(), player.getID(), player.getCivilizationName()))

	def onCultureExpansion(self, argsList):
	## Platy Builder ##
		if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
	## Platy Builder ##
		'City Culture Expansion'
		pCity = argsList[0]
		iPlayer = argsList[1]
		CvUtil.pyPrint("City %s's culture has expanded" %(pCity.getName(),))

	def onCityGrowth(self, argsList):
		'City Population Growth'
		pCity = argsList[0]
		iPlayer = argsList[1]
		CvUtil.pyPrint("%s has grown" %(pCity.getName(),))

	def onCityDoTurn(self, argsList):
		'City Production'
		pCity = argsList[0]
		iPlayer = argsList[1]
		pPlot = pCity.plot()
		iPlayer = pCity.getOwner()
		pPlayer = gc.getPlayer(iPlayer)

		if pCity.getNumRealBuilding(gc.getInfoTypeForString('BUILDING_CITADEL_OF_LIGHT')) > 0:
			iX = pCity.getX()
			iY = pCity.getY()
			eTeam = gc.getTeam(pPlayer.getTeam())
			iBestValue = 0
			pBestPlot = -1
			for iiX in range(iX-2, iX+3, 1):
				for iiY in range(iY-2, iY+3, 1):
					pPlot2 = CyMap().plot(iiX,iiY)
					bEnemy = False
					bNeutral = False
					iValue = 0
					if pPlot2.isVisibleEnemyUnit(iPlayer):
						for i in range(pPlot2.getNumUnits()):
							pUnit = pPlot2.getUnit(i)
							if eTeam.isAtWar(pUnit.getTeam()):
								iValue += 5 * pUnit.baseCombatStr()
							else:
								bNeutral = True
						if (iValue > iBestValue and bNeutral == False):
							iBestValue = iValue
							pBestPlot = pPlot2
			if pBestPlot != -1:
				for i in range(pBestPlot.getNumUnits()):
					pUnit = pBestPlot.getUnit(i)
					pUnit.doDamageNoCaster(20, 40, gc.getInfoTypeForString('DAMAGE_FIRE'), False)
				if (pBestPlot.getFeatureType() == gc.getInfoTypeForString('FEATURE_FOREST') or pBestPlot.getFeatureType() == gc.getInfoTypeForString('FEATURE_JUNGLE')):
					bValid = True
					iImprovement = pPlot.getImprovementType()
					if iImprovement != -1 :
						if gc.getImprovementInfo(iImprovement).isPermanent():
							bValid = False
					if bValid:
						if CyGame().getSorenRandNum(100, "Flames Spread") < gc.getDefineINT('FLAMES_SPREAD_CHANCE'):
							pBestPlot.setImprovementType(gc.getInfoTypeForString('IMPROVEMENT_SMOKE'))
				CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_PILLAR_OF_FIRE'),pBestPlot.getPoint())

		if pCity.getNumRealBuilding(gc.getInfoTypeForString('BUILDING_HALL_OF_MIRRORS')) > 0:
			if CyGame().getSorenRandNum(100, "Hall of Mirrors") < 100:
				pUnit = -1
				iBestValue = -1
				iX = pCity.getX()
				iY = pCity.getY()
				eTeam = gc.getTeam(pPlayer.getTeam())
				for iiX in range(iX-1, iX+2, 1):
					for iiY in range(iY-1, iY+2, 1):
						pLoopPlot = CyMap().plot(iiX,iiY)
						if not pLoopPlot.isNone():
							if pLoopPlot.isVisibleEnemyUnit(iPlayer):
								for i in range(pLoopPlot.getNumUnits()):
									pUnit2 = pLoopPlot.getUnit(i)
									if eTeam.isAtWar(pUnit2.getTeam()):
										iValue = CyGame().getSorenRandNum(100, "Hall of Mirrors")
										if (iValue > iBestValue):
											iBestValue = iValue
											pUnit = pUnit2
				if pUnit != -1:
					newUnit = pPlayer.initUnit(pUnit.getUnitType(), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
					newUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_ILLUSION'), True)

##--------		Unofficial Bug Fix: Modified by Denev	--------##
# Copy not only unit type, but also unit artstyle.
					newUnit.setUnitArtStyleType(pUnit.getUnitArtStyleType())
##--------		Unofficial Bug Fix: End Modify			--------##

					if pPlayer.hasTrait(gc.getInfoTypeForString('TRAIT_SUMMONER')):
						newUnit.setDuration(5)
					else:
						newUnit.setDuration(3)

		if pCity.getNumRealBuilding(gc.getInfoTypeForString('BUILDING_EYES_AND_EARS_NETWORK')) > 0:
			iArete = gc.getInfoTypeForString('TECH_ARETE')
			iHiddenPaths = gc.getInfoTypeForString('TECH_HIDDEN_PATHS')
			iInfernalPact = gc.getInfoTypeForString('TECH_INFERNAL_PACT')
			iMindStapling = gc.getInfoTypeForString('TECH_MIND_STAPLING')
			iSeafaring = gc.getInfoTypeForString('TECH_SEAFARING')
			eTeam = gc.getTeam(pPlayer.getTeam())
			listTeams = []
			for iPlayer2 in range(gc.getMAX_PLAYERS()):
				pPlayer2 = gc.getPlayer(iPlayer2)
				if (pPlayer2.isAlive() and iPlayer2 != iPlayer):
					iTeam2 = pPlayer2.getTeam()
					if eTeam.isOpenBorders(iTeam2):
						listTeams.append(gc.getTeam(iTeam2))
			if len(listTeams) >= 3:
				for iTech in range(gc.getNumTechInfos()):
					if (iTech != iArete and iTech != iMindStapling and iTech != iHiddenPaths and iTech != iInfernalPact and iTech != iSeafaring):
						if eTeam.isHasTech(iTech) == False:
							if pPlayer.canResearch(iTech, False):
								iCount = 0
								for i in range(len(listTeams)):
									if listTeams[i].isHasTech(iTech):
										iCount = iCount + 1
								if iCount >= 3:
									eTeam.setHasTech(iTech, True, iPlayer, False, True)
									CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EYES_AND_EARS_NETWORK_FREE_TECH",()),'AS2D_TECH_DING',1,'Art/Interface/Buttons/Buildings/Eyesandearsnetwork.dds',ColorTypes(8),pCity.getX(),pCity.getY(),True,True)

		if pCity.getNumRealBuilding(gc.getInfoTypeForString('BUILDING_PLANAR_GATE')) > 0:
			iMax = 1
			iMult = 1
			if CyGame().getGlobalCounter() >= 50:
				iMax = 2
				iMult = 1.5
			if CyGame().getGlobalCounter() >= 75:
				iMax = 3
				iMult = 2
			if CyGame().getGlobalCounter() == 100:
				iMax = 4
				iMult = 2.5
			if CyGame().getSorenRandNum(10000, "Planar Gate") < gc.getDefineINT('PLANAR_GATE_CHANCE') * iMult:
				listUnits = []
				iMax = iMax * pPlayer.countNumBuildings(gc.getInfoTypeForString('BUILDING_PLANAR_GATE'))
				if pCity.getNumBuilding(gc.getInfoTypeForString('BUILDING_GAMBLING_HOUSE')) > 0:
					if pPlayer.getUnitClassCount(gc.getInfoTypeForString('UNITCLASS_REVELERS')) < iMax:
						listUnits.append(gc.getInfoTypeForString('UNIT_REVELERS'))
				if pCity.getNumBuilding(gc.getInfoTypeForString('BUILDING_MAGE_GUILD')) > 0:
					if pPlayer.getUnitClassCount(gc.getInfoTypeForString('UNITCLASS_MOBIUS_WITCH')) < iMax:
						listUnits.append(gc.getInfoTypeForString('UNIT_MOBIUS_WITCH'))
				if pCity.getNumBuilding(gc.getInfoTypeForString('BUILDING_CARNIVAL')) > 0:
					if pPlayer.getUnitClassCount(gc.getInfoTypeForString('UNITCLASS_CHAOS_MARAUDER')) < iMax:
						listUnits.append(gc.getInfoTypeForString('UNIT_CHAOS_MARAUDER'))
				if pCity.getNumBuilding(gc.getInfoTypeForString('BUILDING_GROVE')) > 0:
					if pPlayer.getUnitClassCount(gc.getInfoTypeForString('UNITCLASS_MANTICORE')) < iMax:
						listUnits.append(gc.getInfoTypeForString('UNIT_MANTICORE'))
				if pCity.getNumBuilding(gc.getInfoTypeForString('BUILDING_PUBLIC_BATHS')) > 0:
					if pPlayer.getUnitClassCount(gc.getInfoTypeForString('UNITCLASS_SUCCUBUS')) < iMax:
						listUnits.append(gc.getInfoTypeForString('UNIT_SUCCUBUS'))
				if pCity.getNumBuilding(gc.getInfoTypeForString('BUILDING_OBSIDIAN_GATE')) > 0:
					if pPlayer.getUnitClassCount(gc.getInfoTypeForString('UNITCLASS_MINOTAUR')) < iMax:
						listUnits.append(gc.getInfoTypeForString('UNIT_MINOTAUR'))
				if pCity.getNumBuilding(gc.getInfoTypeForString('BUILDING_TEMPLE_OF_THE_VEIL')) > 0:
					if pPlayer.getUnitClassCount(gc.getInfoTypeForString('UNITCLASS_TAR_DEMON')) < iMax:
						listUnits.append(gc.getInfoTypeForString('UNIT_TAR_DEMON'))
				if len(listUnits) > 0:
					iUnit = listUnits[CyGame().getSorenRandNum(len(listUnits), "Planar Gate")]
					newUnit = pPlayer.initUnit(iUnit, pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
					CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_PLANAR_GATE",()),'AS2D_DISCOVERBONUS',1,gc.getUnitInfo(newUnit.getUnitType()).getButton(),ColorTypes(8),pCity.getX(),pCity.getY(),True,True)
					if iUnit == gc.getInfoTypeForString('UNIT_MOBIUS_WITCH'):
						promotions = [ 'PROMOTION_AIR1','PROMOTION_BODY1','PROMOTION_CHAOS1','PROMOTION_DEATH1','PROMOTION_EARTH1','PROMOTION_ENCHANTMENT1','PROMOTION_ENTROPY1','PROMOTION_FIRE1','PROMOTION_LAW1','PROMOTION_LIFE1','PROMOTION_MIND1','PROMOTION_NATURE1','PROMOTION_SHADOW1','PROMOTION_SPIRIT1','PROMOTION_SUN1','PROMOTION_WATER1' ]
						newUnit.setLevel(4)
						newUnit.setExperience(14, -1)
						for i in promotions:
							if CyGame().getSorenRandNum(10, "Bob") == 1:
								newUnit.setHasPromotion(gc.getInfoTypeForString(i), True)

		if gc.getPlayer(pCity.getOwner()).getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_INFERNAL'):
			if pCity.isHasReligion(gc.getInfoTypeForString('RELIGION_THE_ORDER')):
				pCity.setHasReligion(gc.getInfoTypeForString('RELIGION_THE_ORDER'), False, True, True)
			if pCity.isHasReligion(gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL')) == False:
				pCity.setHasReligion(gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL'), True, True, True)

		if gc.getPlayer(pCity.getOwner()).getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_MERCURIANS'):
			if pCity.isHasReligion(gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL')):
				pCity.setHasReligion(gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL'), False, True, True)

		if pCity.getNumRealBuilding(gc.getInfoTypeForString('BUILDING_SHRINE_OF_SIRONA')) > 0:
			pPlayer.setFeatAccomplished(FeatTypes.FEAT_HEAL_UNIT_PER_TURN, True)

		if pCity.getNumRealBuilding(gc.getInfoTypeForString('BUILDING_THE_DRAGONS_HORDE')) > 0:
			if pPlayer.isBarbarian():
				if CyGame().getSorenRandNum(100, "Bob") < gc.getHandicapInfo(gc.getGame().getHandicapType()).getLairSpawnRate():
					iUnit = gc.getInfoTypeForString('UNIT_DISCIPLE_OF_ACHERON')
#					eTeam = gc.getTeam(pPlayer.getTeam())
#					if eTeam.isHasTech(gc.getInfoTypeForString('TECH_SORCERY')):
#						iUnit = gc.getInfoTypeForString('UNIT_SON_OF_THE_INFERNO')
					newUnit = pPlayer.initUnit(iUnit, pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

		CvAdvisorUtils.cityAdvise(pCity, iPlayer)

	def onCityBuildingUnit(self, argsList):
		'City begins building a unit'
		pCity = argsList[0]
		iUnitType = argsList[1]
		if (not self.__LOG_CITYBUILDING):
			return
		CvUtil.pyPrint("%s has begun building a %s" %(pCity.getName(),gc.getUnitInfo(iUnitType).getDescription()))

	def onCityBuildingBuilding(self, argsList):
		'City begins building a Building'
		pCity = argsList[0]
		iBuildingType = argsList[1]
		if (not self.__LOG_CITYBUILDING):
			return
		CvUtil.pyPrint("%s has begun building a %s" %(pCity.getName(),gc.getBuildingInfo(iBuildingType).getDescription()))

	def onCityRename(self, argsList):
		'City is renamed'
		pCity = argsList[0]
		if (pCity.getOwner() == gc.getGame().getActivePlayer()):
			self.__eventEditCityNameBegin(pCity, True)

	def onCityHurry(self, argsList):
		'City is renamed'
		pCity = argsList[0]
		iHurryType = argsList[1]

	def onVictory(self, argsList):
		'Victory'
		iTeam, iVictory = argsList
		if (iVictory >= 0 and iVictory < gc.getNumVictoryInfos()):
			for iPlayer in range(gc.getMAX_PLAYERS()):
				pPlayer = gc.getPlayer(iPlayer)
				if pPlayer.isAlive():
					if pPlayer.isHuman():
						if pPlayer.getTeam() == iTeam:
							if CyGame().getWBMapScript():
								sf.onVictory(iPlayer, iVictory)
							else:
								iCiv = pPlayer.getCivilizationType()
								if iCiv == gc.getInfoTypeForString('CIVILIZATION_AMURITES'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_AMURITES", 1)
								elif iCiv == gc.getInfoTypeForString('CIVILIZATION_BALSERAPHS'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_BALSERAPHS", 1)
								elif iCiv == gc.getInfoTypeForString('CIVILIZATION_BANNOR'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_BANNOR", 1)
								elif iCiv == gc.getInfoTypeForString('CIVILIZATION_CALABIM'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_CALABIM", 1)
								elif iCiv == gc.getInfoTypeForString('CIVILIZATION_CLAN_OF_EMBERS'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_CLAN_OF_EMBERS", 1)
								elif iCiv == gc.getInfoTypeForString('CIVILIZATION_DOVIELLO'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_DOVIELLO", 1)
								elif iCiv == gc.getInfoTypeForString('CIVILIZATION_ELOHIM'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_ELOHIM", 1)
								elif iCiv == gc.getInfoTypeForString('CIVILIZATION_GRIGORI'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_GRIGORI", 1)
								elif iCiv == gc.getInfoTypeForString('CIVILIZATION_HIPPUS'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_HIPPUS", 1)
								elif iCiv == gc.getInfoTypeForString('CIVILIZATION_ILLIANS'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_ILLIANS", 1)
								elif iCiv == gc.getInfoTypeForString('CIVILIZATION_INFERNAL'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_INFERNAL", 1)
								elif iCiv == gc.getInfoTypeForString('CIVILIZATION_KHAZAD'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_KHAZAD", 1)
								elif iCiv == gc.getInfoTypeForString('CIVILIZATION_KURIOTATES'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_KURIOTATES", 1)
								elif iCiv == gc.getInfoTypeForString('CIVILIZATION_LANUN'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_LANUN", 1)
								elif iCiv == gc.getInfoTypeForString('CIVILIZATION_LJOSALFAR'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_LJOSALFAR", 1)
								elif iCiv == gc.getInfoTypeForString('CIVILIZATION_LUCHUIRP'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_LUCHUIRP", 1)
								elif iCiv == gc.getInfoTypeForString('CIVILIZATION_MALAKIM'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_MALAKIM", 1)
								elif iCiv == gc.getInfoTypeForString('CIVILIZATION_MERCURIANS'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_MERCURIANS", 1)
								elif iCiv == gc.getInfoTypeForString('CIVILIZATION_SHEAIM'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_SHEAIM", 1)
								elif iCiv == gc.getInfoTypeForString('CIVILIZATION_SIDAR'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_SIDAR", 1)
								elif iCiv == gc.getInfoTypeForString('CIVILIZATION_SVARTALFAR'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_SVARTALFAR", 1)

								if iVictory == gc.getInfoTypeForString('VICTORY_ALTAR_OF_THE_LUONNOTAR'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_ALTAR_OF_THE_LUONNOTAR", 1)
								elif iVictory == gc.getInfoTypeForString('VICTORY_CONQUEST'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_CONQUEST", 1)
								elif iVictory == gc.getInfoTypeForString('VICTORY_CULTURAL'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_CULTURAL", 1)
								elif iVictory == gc.getInfoTypeForString('VICTORY_DOMINATION'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_DOMINATION", 1)
								elif iVictory == gc.getInfoTypeForString('VICTORY_RELIGIOUS'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_RELIGIOUS", 1)
								elif iVictory == gc.getInfoTypeForString('VICTORY_SCORE'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_SCORE", 1)
								elif iVictory == gc.getInfoTypeForString('VICTORY_TIME'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_TIME", 1)
								elif iVictory == gc.getInfoTypeForString('VICTORY_TOWER_OF_MASTERY'):
									CyGame().changeTrophyValue("TROPHY_VICTORY_TOWER_OF_MASTERY", 1)

								if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_BARBARIAN_WORLD):
									CyGame().changeTrophyValue("TROPHY_VICTORY_BARBARIAN_WORLD", 1)
								if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_CHALLENGE_CUT_LOSERS):
									CyGame().changeTrophyValue("TROPHY_VICTORY_FINAL_FIVE", 1)
								if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_CHALLENGE_HIGH_TO_LOW):
									CyGame().changeTrophyValue("TROPHY_VICTORY_HIGH_TO_LOW", 1)
								if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_CHALLENGE_INCREASING_DIFFICULTY):
									CyGame().changeTrophyValue("TROPHY_VICTORY_INCREASING_DIFFICULTY", 1)

			victoryInfo = gc.getVictoryInfo(int(iVictory))
			CvUtil.pyPrint("Victory!  Team %d achieves a %s victory"
				%(iTeam, victoryInfo.getDescription()))

	def onVassalState(self, argsList):
		'Vassal State'
		iMaster, iVassal, bVassal = argsList

		if (bVassal):
			CvUtil.pyPrint("Team %d becomes a Vassal State of Team %d"
				%(iVassal, iMaster))
		else:
			CvUtil.pyPrint("Team %d revolts and is no longer a Vassal State of Team %d"
				%(iVassal, iMaster))

	def onGameUpdate(self, argsList):
		'sample generic event, called on each game turn slice'
		genericArgs = argsList[0][0]	# tuple of tuple of my args
		turnSlice = genericArgs[0]

#FfH: 10/15/2008 Added by Kael for OOS logging.
		OOSLogger.doGameUpdate()
#FfH: End add

	def onMouseEvent(self, argsList):
		'mouse handler - returns 1 if the event was consumed'
		eventType,mx,my,px,py,interfaceConsumed,screens = argsList
		if ( px!=-1 and py!=-1 ):
			if ( eventType == self.EventLButtonDown ):
				if (self.bAllowCheats and self.bCtrl and self.bAlt and CyMap().plot(px,py).isCity() and not interfaceConsumed):
					# Launch Edit City Event
					CvEventManager.beginEvent(self, CvUtil.EventEditCity, (px,py) )
					return 1

				elif (self.bAllowCheats and self.bCtrl and self.bShift and not interfaceConsumed):
					# Launch Place Object Event
					CvEventManager.beginEvent(self, CvUtil.EventPlaceObject, (px, py) )
					return 1

		if ( eventType == self.EventBack ):
			return CvScreensInterface.handleBack(screens)
		elif ( eventType == self.EventForward ):
			return CvScreensInterface.handleForward(screens)

		return 0


#################### TRIGGERED EVENTS ##################

	def __eventPlaceObjectBegin(self, argsList):
		'Place Object Event'
		CvDebugTools.CvDebugTools().initUnitPicker(argsList)

	def __eventPlaceObjectApply(self, playerID, userData, popupReturn):
		'Place Object Event Apply'
		if (getChtLvl() > 0):
			CvDebugTools.CvDebugTools().applyUnitPicker( (popupReturn, userData) )

	def __eventAwardTechsAndGoldBegin(self, argsList):
		'Award Techs & Gold Event'
		CvDebugTools.CvDebugTools().cheatTechs()

	def __eventAwardTechsAndGoldApply(self, playerID, netUserData, popupReturn):
		'Award Techs & Gold Event Apply'
		if (getChtLvl() > 0):
			CvDebugTools.CvDebugTools().applyTechCheat( (popupReturn) )

	def __eventShowWonderBegin(self, argsList):
		'Show Wonder Event'
		CvDebugTools.CvDebugTools().wonderMovie()

	def __eventShowWonderApply(self, playerID, netUserData, popupReturn):
		'Wonder Movie Apply'
		if (getChtLvl() > 0):
			CvDebugTools.CvDebugTools().applyWonderMovie( (popupReturn) )

## Platy Builder ##

	def __eventEditUnitNameBegin(self, argsList):
		pUnit = argsList
		popup = PyPopup.PyPopup(CvUtil.EventEditUnitName, EventContextTypes.EVENTCONTEXT_ALL)
		popup.setUserData((pUnit.getID(), CyGame().getActivePlayer()))
		popup.setBodyString(localText.getText("TXT_KEY_RENAME_UNIT", ()))
		popup.createEditBox(pUnit.getNameNoDesc())
		popup.setEditBoxMaxCharCount(25)
		popup.launch()

	def __eventEditUnitNameApply(self, playerID, userData, popupReturn):
		unit = gc.getPlayer(userData[1]).getUnit(userData[0])
		newName = popupReturn.getEditBoxString(0)
		unit.setName(newName)
		if CyGame().GetWorldBuilderMode():
			WBUnitScreen.WBUnitScreen(CvPlatyBuilderScreen.CvWorldBuilderScreen()).placeStats()
			WBUnitScreen.WBUnitScreen(CvPlatyBuilderScreen.CvWorldBuilderScreen()).placeCurrentUnit()

	def __eventEditCityNameBegin(self, city, bRename):
		popup = PyPopup.PyPopup(CvUtil.EventEditCityName, EventContextTypes.EVENTCONTEXT_ALL)
		popup.setUserData((city.getID(), bRename, CyGame().getActivePlayer()))
		popup.setHeaderString(localText.getText("TXT_KEY_NAME_CITY", ()))
		popup.setBodyString(localText.getText("TXT_KEY_SETTLE_NEW_CITY_NAME", ()))
		popup.createEditBox(city.getName())
		popup.setEditBoxMaxCharCount(15)
		popup.launch()

	def __eventEditCityNameApply(self, playerID, userData, popupReturn):
		city = gc.getPlayer(userData[2]).getCity(userData[0])
		cityName = popupReturn.getEditBoxString(0)
		city.setName(cityName, not userData[1])
		if CyGame().GetWorldBuilderMode() and not CyGame().isInAdvancedStart():
			WBCityEditScreen.WBCityEditScreen().placeStats()
## Platy Builder ##

#Magister Start
	def __eventEditPlayerNameBegin(self, argsList):
		pUnit = argsList
		popup = PyPopup.PyPopup(6666, EventContextTypes.EVENTCONTEXT_ALL)
		popup.setUserData((pPlayer.getID(),))
		popup.setBodyString(localText.getText("TXT_KEY_MENU_LEADER_NAME", ()))
		popup.createEditBox(pPlayer.getName())
		popup.launch()

	def __eventEditPlayerNameApply(self, playerID, userData, popupReturn):
		'Edit Player Name Event'
		newName = popupReturn.getEditBoxString(0)
		if (len(newName) > 25):
			newName = newName[:25]
		gc.getPlayer(playerID).setName(newName)
		if CyGame().GetWorldBuilderMode():
			WBPlayerScreen.WBPlayerScreen().placeStats()

	def __eventEditCivNameBegin(self, argsList):
		pUnit = argsList
		popup = PyPopup.PyPopup(6777, EventContextTypes.EVENTCONTEXT_ALL)
		popup.setUserData((pPlayer.getID(),))
		popup.setBodyString(localText.getText("TXT_KEY_RENAME_PLAYER", ()))
		popup.setBodyString(CyTranslator().getText("TXT_KEY_MENU_CIV_DESC", ()))
		popup.createEditBox(pPlayer.getCivilizationDescription(pPlayer.getID()))
		popup.launch()

	def __eventEditCivNameApply(self, playerID, userData, popupReturn):
		'Edit Player Name Event'
		pPlayer = gc.getPlayer(playerID)
		szNewDesc = pPlayer.getCivilizationDescription(playerID)
		szNewShort = pPlayer.getCivilizationShortDescription(playerID)
		szNewAdj = pPlayer.getCivilizationAdjective(playerID)
		sNew = popupReturn.getEditBoxString(0)
		if (len(sNew) > 25):
			sNew = sNew[:25]
		pPlayer.setCivName(sNew,szNewShort, szNewAdj)
		if CyGame().GetWorldBuilderMode():
			WBPlayerScreen.WBPlayerScreen().placeStats()

	def __eventEditCivShortNameBegin(self, argsList):
		pUnit = argsList
		popup = PyPopup.PyPopup(6888, EventContextTypes.EVENTCONTEXT_ALL)
		popup.setUserData((pPlayer.getID(),))
		popup.setBodyString(localText.getText("TXT_KEY_RENAME_PLAYER", ()))
		popup.setBodyString(CyTranslator().getText("TXT_KEY_MENU_CIV_SHORT_DESC", ()))
		popup.createEditBox(pPlayer.getCivilizationShortDescription(pPlayer.getID()))
		popup.launch()

	def __eventEditCivShortNameApply(self, playerID, userData, popupReturn):
		'Edit Player Name Event'
		pPlayer = gc.getPlayer(playerID)
		szNewDesc = pPlayer.getCivilizationDescription(playerID)
		szNewShort = pPlayer.getCivilizationShortDescription(playerID)
		szNewAdj = pPlayer.getCivilizationAdjective(playerID)
		sNew = popupReturn.getEditBoxString(0)
		if (len(sNew) > 25):
			sNew = sNew[:25]
		pPlayer.setCivName(szNewDesc,sNew, szNewAdj)
		if CyGame().GetWorldBuilderMode():
			WBPlayerScreen.WBPlayerScreen().placeStats()

	def __eventEditCivAdjBegin(self, argsList):
		pUnit = argsList
		popup = PyPopup.PyPopup(6999, EventContextTypes.EVENTCONTEXT_ALL)
		popup.setUserData((pPlayer.getID(),))
		popup.setBodyString(localText.getText("TXT_KEY_RENAME_PLAYER", ()))
		popup.setBodyString(CyTranslator().getText("TXT_KEY_MENU_CIV_ADJ", ()))
		popup.createEditBox(pPlayer.getCivilizationAdjective(pPlayer.getID()))
		popup.launch()

	def __eventEditCivAdjApply(self, playerID, userData, popupReturn):
		'Edit Player Name Event'
		pPlayer = gc.getPlayer(playerID)
		szNewDesc = pPlayer.getCivilizationDescription(playerID)
		szNewShort = pPlayer.getCivilizationShortDescription(playerID)
		szNewAdj = pPlayer.getCivilizationAdjective(playerID)
		sNew = popupReturn.getEditBoxString(0)
		if (len(sNew) > 25):
			sNew = sNew[:25]
		pPlayer.setCivName(szNewDesc,szNewShort, sNew)
		if CyGame().GetWorldBuilderMode():
			WBPlayerScreen.WBPlayerScreen().placeStats()
#Magister Stop

	def __eventWBPlayerScriptPopupApply(self, playerID, userData, popupReturn):
		sScript = popupReturn.getEditBoxString(0)
		gc.getPlayer(userData[0]).setScriptData(CvUtil.convertToStr(sScript))
		WBPlayerScreen.WBPlayerScreen().placeScript()
		return

	def __eventWBCityScriptPopupApply(self, playerID, userData, popupReturn):
		sScript = popupReturn.getEditBoxString(0)
		pCity = gc.getPlayer(userData[0]).getCity(userData[1])
		pCity.setScriptData(CvUtil.convertToStr(sScript))
		WBCityEditScreen.WBCityEditScreen().placeScript()
		return

	def __eventWBUnitScriptPopupApply(self, playerID, userData, popupReturn):
		sScript = popupReturn.getEditBoxString(0)
		pUnit = gc.getPlayer(userData[0]).getUnit(userData[1])
		pUnit.setScriptData(CvUtil.convertToStr(sScript))
		WBUnitScreen.WBUnitScreen(CvPlatyBuilderScreen.CvWorldBuilderScreen()).placeScript()
		return

	def __eventWBScriptPopupBegin(self):
		return

	def __eventWBGameScriptPopupApply(self, playerID, userData, popupReturn):
		sScript = popupReturn.getEditBoxString(0)
		CyGame().setScriptData(CvUtil.convertToStr(sScript))
		WBGameDataScreen.WBGameDataScreen(CvPlatyBuilderScreen.CvWorldBuilderScreen()).placeScript()
		return

	def __eventWBPlotScriptPopupApply(self, playerID, userData, popupReturn):
		sScript = popupReturn.getEditBoxString(0)
		pPlot = CyMap().plot(userData[0], userData[1])
		pPlot.setScriptData(CvUtil.convertToStr(sScript))
		WBPlotScreen.WBPlotScreen().placeScript()
		return

	def __eventWBLandmarkPopupApply(self, playerID, userData, popupReturn):
		sScript = popupReturn.getEditBoxString(0)
		pPlot = CyMap().plot(userData[0], userData[1])
		iPlayer = userData[2]
		if userData[3] > -1:
			pSign = CyEngine().getSignByIndex(userData[3])
			iPlayer = pSign.getPlayerType()
			CyEngine().removeSign(pPlot, iPlayer)
		if len(sScript):
			if iPlayer == gc.getBARBARIAN_PLAYER():
				CyEngine().addLandmark(pPlot, CvUtil.convertToStr(sScript))
			else:
				CyEngine().addSign(pPlot, iPlayer, CvUtil.convertToStr(sScript))
		WBPlotScreen.iCounter = 10
		return
## Platy Builder ##

## FfH Card Game: begin
	def __EventSelectSolmniumPlayerBegin(self):
		iHUPlayer = gc.getGame().getActivePlayer()

		if iHUPlayer == -1 : return 0
		if not cs.canStartGame(iHUPlayer) : return 0

		popup = PyPopup.PyPopup(CvUtil.EventSelectSolmniumPlayer, EventContextTypes.EVENTCONTEXT_ALL)

		sResText = CyUserProfile().getResolutionString(CyUserProfile().getResolution())
		sX, sY = sResText.split("x")
		iXRes = int(sX)
		iYRes = int(sY)

		iW = 620
		iH = 650

		popup.setSize(iW, iH)
		popup.setPosition((iXRes - iW) / 2, 30)

		lStates = []

		for iPlayer in range(gc.getMAX_CIV_PLAYERS()) :
			pPlayer = gc.getPlayer(iPlayer)

			if pPlayer.isNone() : continue

			if pPlayer.isHuman() :
				lPlayerState = cs.getStartGameMPWith(iHUPlayer, iPlayer)
				if lPlayerState[0][0] in ["No", "notMet"] : continue
				lStates.append([iPlayer, lPlayerState])
			else :
				lPlayerState = cs.getStartGameAIWith(iHUPlayer, iPlayer)
				if lPlayerState[0][0] in ["No", "notMet"] : continue
				lStates.append([iPlayer, lPlayerState])

		lPlayerButtons = []

		popup.addDDS(CyArtFileMgr().getInterfaceArtInfo("SOMNIUM_POPUP_INTRO").getPath(), 0, 0, 512, 128)
		popup.addSeparator()
		#popup.setHeaderString(localText.getText("TXT_KEY_SOMNIUM_START", ()), CvUtil.FONT_CENTER_JUSTIFY)
		if len(lStates) == 0 :
			popup.setBodyString(localText.getText("TXT_KEY_SOMNIUM_NOONE_MET", ()))
		else :
			#popup.setBodyString(localText.getText("TXT_KEY_SOMNIUM_PLAY_WITH", ()))
			popup.addSeparator()
			popup.addSeparator()

			sText = u""
			for iPlayer, lPlayerState in lStates :
				pPlayer = gc.getPlayer(iPlayer)
				sPlayerName = pPlayer.getName()
				iPositiveChange = gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getMemoryAttitudePercent(MemoryTypes.MEMORY_SOMNIUM_POSITIVE) / 100
				iNegativeChange = gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getMemoryAttitudePercent(MemoryTypes.MEMORY_SOMNIUM_NEGATIVE) / 100
				bShift = True

				for item in lPlayerState :

					sTag = item[0]
					if (sTag == "atWar") :
						if len(sText) > 0 : sText += localText.getText("[NEWLINE]", ())
						sText += localText.getText("TXT_KEY_SOMNIUM_AT_WAR", (sPlayerName, ))

					elif (sTag == "InGame") :
						if len(sText) > 0 : sText += localText.getText("[NEWLINE]", ())
						sText += localText.getText("TXT_KEY_SOMNIUM_IN_GAME", (sPlayerName, ))

					elif (sTag == "relation") :
						delay = item[1]
						if (delay > 0) :
							if len(sText) > 0 : sText += localText.getText("[NEWLINE]", ())
							sText += localText.getText("TXT_KEY_SOMNIUM_GAME_DELAYED", (sPlayerName, delay))
						else :
							if bShift :
								bShift = False
								popup.addSeparator()
							popup.addButton(localText.getText("TXT_KEY_SOMNIUM_GAME_RELATION", (sPlayerName, iPositiveChange, iNegativeChange)))
							lPlayerButtons.append((iPlayer, -1))

					elif (sTag == "gold") :
						for iGold in item[1] :
							if bShift :
								bShift = False
								popup.addSeparator()
							if iGold == 0 :
								popup.addButton(localText.getText("TXT_KEY_SOMNIUM_GAME_FUN", (sPlayerName, )))
								lPlayerButtons.append((iPlayer, iGold))
							else :
								popup.addButton(localText.getText("TXT_KEY_SOMNIUM_GAME_GOLD", (sPlayerName, iGold)))
								lPlayerButtons.append((iPlayer, iGold))

			if len(sText) > 0 :
				popup.addSeparator()
				popup.addSeparator()
				popup.setBodyString(sText)

		popup.setUserData(tuple(lPlayerButtons))
		popup.launch()

	def __EventSelectSolmniumPlayerApply(self, playerID, userData, popupReturn):
		if userData :
			idButtonCliked = popupReturn.getButtonClicked()
			if idButtonCliked in range(len(userData)) :
				iOpponent, iGold = userData[idButtonCliked]

				pLeftPlayer = gc.getPlayer(playerID)
				pRightPlayer = gc.getPlayer(iOpponent)

				if not pRightPlayer.isHuman() :
					if (cs.canStartGame(playerID)) and (pLeftPlayer.isAlive()) and (pRightPlayer.isAlive()) :
						cs.startGame(playerID, iOpponent, iGold)
					else :
						CyInterface().addMessage(playerID, True, 25, CyTranslator().getText("TXT_KEY_SOMNIUM_CANT_START_GAME", (gc.getPlayer(iOpponent).getName(), )), '', 1, '', ColorTypes(7), -1, -1, False, False)
				else :
					if (cs.canStartGame(playerID)) and (cs.canStartGame(iOpponent)) and (pLeftPlayer.isAlive()) and (pRightPlayer.isAlive()) :
						if (iOpponent == gc.getGame().getActivePlayer()):
							self.__EventSolmniumAcceptGameBegin((playerID, iOpponent, iGold))
					else :
						CyInterface().addMessage(playerID, True, 25, CyTranslator().getText("TXT_KEY_SOMNIUM_CANT_START_GAME", (gc.getPlayer(iOpponent).getName(), )), '', 1, '', ColorTypes(7), -1, -1, False, False)

	def __EventSolmniumAcceptGameBegin(self, argslist):
		iPlayer, iOpponent, iGold = argslist
		if not gc.getPlayer(iOpponent).isAlive() : return 0

		popup = PyPopup.PyPopup(CvUtil.EventSolmniumAcceptGame, EventContextTypes.EVENTCONTEXT_ALL)

		popup.setUserData(argslist)

		popup.setHeaderString(localText.getText("TXT_KEY_SOMNIUM_START", ()))
		if iGold > 0 :
			popup.setBodyString(localText.getText("TXT_KEY_SOMNIUM_ACCEPT_GAME", (gc.getPlayer(iPlayer).getName(), iGold)))
		else :
			popup.setBodyString(localText.getText("TXT_KEY_SOMNIUM_ACCEPT_GAME_FUN", (gc.getPlayer(iPlayer).getName(), )))

		popup.addButton( localText.getText("AI_DIPLO_ACCEPT_1", ()) )
		popup.addButton( localText.getText("AI_DIPLO_NO_PEACE_3", ()) )

		popup.launch(False, PopupStates.POPUPSTATE_IMMEDIATE)

	def __EventSolmniumAcceptGameApply(self, playerID, userData, popupReturn):
		if userData :
			iPlayer, iOpponent, iGold = userData
			idButtonCliked = popupReturn.getButtonClicked()
			if idButtonCliked == 0 :
				if (cs.canStartGame(iPlayer)) and (cs.canStartGame(iOpponent)) and (gc.getPlayer(iPlayer).isAlive()) and (gc.getPlayer(iOpponent).isAlive()) :
					cs.startGame(iPlayer, iOpponent, iGold)
				else :
					CyInterface().addMessage(iPlayer, True, 25, CyTranslator().getText("TXT_KEY_SOMNIUM_CANT_START_GAME", (gc.getPlayer(iOpponent).getName(), )), '', 1, '', ColorTypes(7), -1, -1, False, False)
					CyInterface().addMessage(iOpponent, True, 25, CyTranslator().getText("TXT_KEY_SOMNIUM_CANT_START_GAME", (gc.getPlayer(iPlayer).getName(), )), '', 1, '', ColorTypes(7), -1, -1, False, False)
			else :
					CyInterface().addMessage(iPlayer, True, 25, CyTranslator().getText("TXT_KEY_SOMNIUM_REFUSE_GAME", (gc.getPlayer(iOpponent).getName(), iGold)), '', 1, '', ColorTypes(7), -1, -1, False, False)

	def __EventSolmniumConcedeGameBegin(self, argslist):
		popup = PyPopup.PyPopup(CvUtil.EventSolmniumConcedeGame, EventContextTypes.EVENTCONTEXT_ALL)

		popup.setUserData(argslist)

		popup.setHeaderString(localText.getText("TXT_KEY_SOMNIUM_START", ()))
		popup.setBodyString(localText.getText("TXT_KEY_SOMNIUM_CONCEDE_GAME", ()))

		popup.addButton( localText.getText("AI_DIPLO_ACCEPT_1", ()) )
		popup.addButton( localText.getText("AI_DIPLO_NO_PEACE_3", ()) )

		popup.launch(False, PopupStates.POPUPSTATE_IMMEDIATE)

	def __EventSolmniumConcedeGameApply(self, playerID, userData, popupReturn):
		if userData :
			idButtonCliked = popupReturn.getButtonClicked()
			if idButtonCliked == 0 :
				cs.endGame(userData[0], userData[1])
## FfH Card Game: end
