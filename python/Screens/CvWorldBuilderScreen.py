## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
from CvPythonExtensions import *
import CvUtil
import CvScreensInterface
import ScreenInput
import CvEventInterface
import CvScreenEnums
import time
import Popup as PyPopup

##
import WBBuildingScreen
import WBTechScreen
import WBPromotionScreen
import WBCorporationScreen
import WBBonusScreen
import WBProjectScreen
import WBSpecialistScreen
import WBDiplomacyScreen

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class CvWorldBuilderScreen:
	"World Builder Screen"

	def __init__ (self) :
		print("init-ing world builder screen")
		self.m_advancedStartTabCtrl = None
		self.m_normalPlayerTabCtrl = 0
		self.m_normalMapTabCtrl = 0
		self.m_tabCtrlEdit = 0
		self.m_bCtrlEditUp = False
		self.m_bUnitEdit = False
		self.m_bCityEdit = False
		self.m_bNormalPlayer = True
		self.m_bNormalMap = False
		self.m_bReveal = False
		self.m_bLandmark = False
		self.m_bEraseAll = False
		self.m_bShowBigBrush = False
		self.m_bLeftMouseDown = False
		self.m_bRightMouseDown = False
		self.m_bChangeFocus = False
		self.m_iNormalPlayerCurrentIndexes = []
		self.m_iNormalMapCurrentIndexes = []
		self.m_iNormalMapCurrentList = []
		self.m_iAdvancedStartCurrentIndexes = []
		self.m_iAdvancedStartCurrentList = []
		self.m_iCurrentPlayer = 0
		self.m_iCurrentTeam = 0
		self.m_iCurrentUnit = 0
		self.m_iCurrentX = -1
		self.m_iCurrentY = -1
		self.m_pCurrentPlot = 0
		self.m_pActivePlot = 0
		self.m_pRiverStartPlot = -1

		self.m_iUnitTabID = -1
		self.m_iBuildingTabID = -1
		self.m_iTechnologyTabID = -1
		self.m_iImprovementTabID = -1
		self.m_iBonusTabID = -1
		self.m_iImprovementListID = -1
		self.m_iBonusListID = -1
		self.m_iTerrainTabID = -1
		self.m_iTerrainListID = -1
		self.m_iFeatureListID = -1
		self.m_iPlotTypeListID = -1
		self.m_iRouteListID = -1
		self.m_iTerritoryTabID = -1
		self.m_iTerritoryListID = -1

		self.m_iASUnitTabID = -1
		self.m_iASUnitListID = -1
		self.m_iASCityTabID = -1
		self.m_iASCityListID = -1
		self.m_iASBuildingsListID = -1
		self.m_iASAutomateListID = -1
		self.m_iASImprovementsTabID = -1
		self.m_iASRoutesListID = -1
		self.m_iASImprovementsListID = -1
		self.m_iASVisibilityTabID = -1
		self.m_iASVisibilityListID = -1
		self.m_iASTechTabID = -1
		self.m_iASTechListID = -1

		self.m_iBrushSizeTabID = -1
		self.m_iUnitEditCheckboxID = -1
		self.m_iCityEditCheckboxID = -1
		self.m_iNormalPlayerCheckboxID = -1
		self.m_iNormalMapCheckboxID = -1
		self.m_iRevealTileCheckboxID = -1
		self.m_iDiplomacyCheckboxID = -1
		self.m_iLandmarkCheckboxID = -1
		self.m_iEraseCheckboxID = -1
		self.iScreenWidth = 228

		self.m_bSideMenuDirty = False
		self.m_bASItemCostDirty = False
		self.m_iCost = 0


## Platy Builder ##
		self.m_iNewCivilization = -1
		self.m_iNewLeaderType = -1
		self.m_iImprovement = 0
		self.m_iYield = 0
		self.m_iDomain = 0
		self.m_iRoute = 0
		self.m_pScript = -1
		self.m_bMoveUnit = False
		self.m_iUnitCombat = -99
		self.m_iUnitType = -1
		self.m_iPlotMode = 0
		self.m_iArea = -1
		self.m_iCityTimer = 0
		self.m_iOtherPlayer = -1
		self.m_iEventUnit = -1
		self.m_iBuildingClass = 0
		self.m_iBuildingModifier = 0
		self.m_iRevealMode = 2
		self.m_iBrushSize = 1
		self.m_iVisibleOption = 1
		self.xResolution = 1000
		self.yResolution = 1000
		self.m_iAddUnitCount = 1

		self.iColumnHeight = 41
		self.iColumnWidth = 200

## Platy Builder ##

	def interfaceScreen (self):
		# This is the main interface screen, create it as such
		self.initVars()
		screen = CyGInterfaceScreen( "WorldBuilderScreen", CvScreenEnums.WORLDBUILDER_SCREEN )
		self.xResolution = screen.getXResolution()
		self.yResolution = screen.getYResolution()
		screen.setCloseOnEscape(False)
		screen.setAlwaysShown(True)

		self.setSideMenu()
		self.refreshSideMenu()

		#add interface items
		self.refreshPlayerTabCtrl()

		self.refreshAdvancedStartTabCtrl(False)

		if (CyInterface().isInAdvancedStart()):
			pPlayer = gc.getPlayer(self.m_iCurrentPlayer)
			pPlot = pPlayer.getStartingPlot()
			CyCamera().JustLookAtPlot(pPlot)

		self.m_normalMapTabCtrl = getWBToolNormalMapTabCtrl()

		self.m_normalMapTabCtrl.setNumColumns((gc.getNumBonusInfos()/10)+1);
		self.m_normalMapTabCtrl.addTabSection(localText.getText("TXT_KEY_WB_IMPROVEMENTS",()));
		self.m_iImprovementTabID = 0
		self.m_iNormalMapCurrentIndexes.append(0)

		self.m_iNormalMapCurrentList.append(0)
		self.m_iImprovementListID = 0

		self.m_normalMapTabCtrl.addTabSection(localText.getText("TXT_KEY_WB_BONUSES", ()));
		self.m_iBonusTabID = 1
		self.m_iNormalMapCurrentIndexes.append(0)

		self.m_iNormalMapCurrentList.append(0)
		self.m_iBonusListID = 0

		self.m_normalMapTabCtrl.setNumColumns((gc.getNumTerrainInfos()/10)+1);
		self.m_normalMapTabCtrl.addTabSection(localText.getText("TXT_KEY_WB_TERRAINS",()))
		self.m_iTerrainTabID = 2
		self.m_iNormalMapCurrentIndexes.append(0)

		self.m_iNormalMapCurrentList.append(0)
		self.m_iTerrainListID = 0
		self.m_iPlotTypeListID = 1
		self.m_iFeatureListID = 2
		self.m_iRouteListID = 3

		# Territory

		self.m_normalMapTabCtrl.setNumColumns(8);
		self.m_normalMapTabCtrl.addTabSection(localText.getText("TXT_KEY_WB_TERRITORY",()))
		self.m_iTerritoryTabID = 3
		self.m_iNormalMapCurrentIndexes.append(0)

		self.m_iNormalMapCurrentList.append(0)
		self.m_iTerritoryListID = 0

		# This should be a forced redraw screen
		screen.setForcedRedraw( True )

		screen.setDimensions( 0, 0, self.xResolution, self.yResolution )
		# This should show the screen immidiately and pass input to the game
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, True)

		setWBInitialCtrlTabPlacement()
		return 0

	def killScreen(self):
		if (self.m_tabCtrlEdit != 0):
			self.m_tabCtrlEdit.destroy()
			self.m_tabCtrlEdit = 0

		screen = CyGInterfaceScreen( "WorldBuilderScreen", CvScreenEnums.WORLDBUILDER_SCREEN )
		screen.hideScreen()
		CyEngine().clearColoredPlots(PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS)
		CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_REVEALED_PLOTS)
		CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_WORLD_BUILDER)
		CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_HIGHLIGHT_PLOT)

	def handleInput (self, inputClass):
		if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED) and inputClass.isShiftKeyDown() and inputClass.isCtrlKeyDown():
			return 1
		elif (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED):
			if (inputClass.getFunctionName() == "WorldBuilderEraseAll"):
				self.handleWorldBuilderEraseAllCB()
			elif (inputClass.getFunctionName() == "WorldBuilderVersion"):
				self.setGameOptionEditInfo()
		elif (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CHARACTER):
			key = inputClass.getData()
			if key == int(InputTypes.KB_ESCAPE):
				self.normalPlayerTabModeCB()

		elif (inputClass.getNotifyCode() == NotifyCode.NOTIFY_LISTBOX_ITEM_SELECTED):
			if (inputClass.getFunctionName() == "WorldBuilderPlayerChoice"):
				self.handlePlayerUnitPullDownCB(inputClass.getData())
## Player Game Data ##
			elif(inputClass.getFunctionName() == "WorldBuilderGameData"):
				self.handleWorldBuilderGameDataPullDownCB(inputClass.getData())
			elif(inputClass.getFunctionName() == "WorldBuilderGameCommands"):
				self.handleWorldBuilderGameCommandsPullDownCB(inputClass.getData())
			elif(inputClass.getFunctionName() == "WorldBuilderAddUnits"):
				self.handleWorldBuilderAddUnitsPullDownCB(inputClass.getData())
			elif(inputClass.getFunctionName() == "WorldBuilderUnitCombat"):
				self.handleWorldBuilderUnitCombatPullDownCB(inputClass.getData())
			elif(inputClass.getFunctionName() == "WorldBuilderAddUnitCount"):
				self.handleWorldBuilderAddUnitCountPullDownCB(inputClass.getData())
			elif(inputClass.getFunctionName() == "WorldBuilderSetWinner"):
				self.handleWorldBuilderSetWinnerPullDownCB(inputClass.getData())
#Magsiter Modmod
			elif(inputClass.getFunctionName() == "WorldBuilderReassignPlayer"):
				self.handleWorldBuilderReassignPlayerCB(inputClass.getData())

			elif(inputClass.getFunctionName() == "WorldBuilderChooseCivilization"):
				self.handleWorldBuilderChooseCivilizationPullDownCB(inputClass.getData())
			elif(inputClass.getFunctionName() == "WorldBuilderChooseLeader"):
				self.handleWorldBuilderChooseLeaderPullDownCB(inputClass.getData())
			elif(inputClass.getFunctionName() == "WorldBuilderEditAreaMap"):
				self.handleWorldBuilderEditAreaMapPullDownCB(inputClass.getData())
			elif(inputClass.getFunctionName() == "WorldBuilderModifyAreaPlotType"):
				self.handleWorldBuilderModifyAreaPlotTypePullDownCB(inputClass.getData())
			elif(inputClass.getFunctionName() == "WorldBuilderModifyAreaTerrain"):
				self.handleWorldBuilderModifyAreaTerrainPullDownCB(inputClass.getData())
			elif(inputClass.getFunctionName() == "WorldBuilderModifyAreaRoute"):
				self.handleWorldBuilderModifyAreaRoutePullDownCB(inputClass.getData())
			elif(inputClass.getFunctionName() == "WorldBuilderModifyAreaFeature"):
				self.handleWorldBuilderModifyAreaFeaturePullDownCB(inputClass.getData())
			elif(inputClass.getFunctionName() == "WorldBuilderRevealMode"):
				self.handleWorldBuilderRevealModePullDownCB(inputClass.getData())
			elif(inputClass.getFunctionName() == "WorldBuilderBrushSize"):
				self.handleBrushSizeCB(inputClass.getData())
## Player Game Data ##
			elif(inputClass.getFunctionName() == "WorldBuilderTeamChoice"):
				self.handleSelectTeamPullDownCB(inputClass.getData())
		return 1

	def mouseOverPlot (self, argsList):

		if (self.m_bReveal):
			self.m_pCurrentPlot = CyInterface().getMouseOverPlot()
			if (CyInterface().isLeftMouseDown() and self.m_bLeftMouseDown):
				self.setMultipleReveal(True)
			elif(CyInterface().isRightMouseDown() and self.m_bRightMouseDown):
				self.setMultipleReveal(False)
		else: #if ((self.m_tabCtrlEdit == 0) or (not self.m_tabCtrlEdit.isEnabled())):
			self.m_pCurrentPlot = CyInterface().getMouseOverPlot()
			self.m_iCurrentX = self.m_pCurrentPlot.getX()
			self.m_iCurrentY = self.m_pCurrentPlot.getY()
			if (CyInterface().isLeftMouseDown() and self.m_bLeftMouseDown):
				if (self.useLargeBrush()):
					self.placeMultipleObjects()
				else:
					self.placeObject()
			elif (CyInterface().isRightMouseDown() and self.m_bRightMouseDown):
				if (not (self.m_bCityEdit or self.m_bUnitEdit)):
					if (self.useLargeBrush()):
						self.removeMultipleObjects()
					else:
						self.removeObject()
		return

	def getHighlightPlot (self, argsList):

		self.refreshASItemCost()

		if (self.m_pCurrentPlot != 0):
			if (CyInterface().isInAdvancedStart()):
				if (self.m_iCost <= 0):
					return []

		if ((self.m_pCurrentPlot != 0) and not self.m_bShowBigBrush and isMouseOverGameSurface()):
			return (self.m_pCurrentPlot.getX(), self.m_pCurrentPlot.getY())

		return []

	def leftMouseDown (self, argsList):
		bShift, bCtrl, bAlt = argsList
		self.m_bLeftMouseDown = True

		if CyInterface().isInAdvancedStart():
			self.placeObject()
			return 1
## Edit Area Map ##
		if self.m_bNormalMap:
			if self.m_iPlotMode == 1:
				self.setPlotEditInfo(True)
				return 1
			elif self.m_iPlotMode == 2:
				self.m_iArea = self.m_pCurrentPlot.getArea()
				self.refreshSideMenu()
				return 1
## Add Units ##
		elif self.m_bNormalPlayer and self.m_iUnitType > -1:
			for i in xrange(self.m_iAddUnitCount):
				pNewUnit = gc.getPlayer(self.m_iCurrentPlayer).initUnit(self.m_iUnitType, self.m_iCurrentX, self.m_iCurrentY, UnitAITypes.NO_UNITAI, DirectionTypes.NO_DIRECTION)
			return 1
## Move Unit Start ##
		elif self.m_bMoveUnit:
			pUnit = self.m_pActivePlot.getUnit(self.m_iCurrentUnit)
			pUnit.setXY(self.m_iCurrentX, self.m_iCurrentY, True, True, False)
			self.m_bMoveUnit = False
			self.toggleUnitEditCB()
			return 1
## Move Unit End ##
		elif (bAlt and bCtrl) or  (self.m_bUnitEdit):
			if (self.m_pCurrentPlot.getNumUnits() > 0):
				self.m_iCurrentUnit = 0
				self.setUnitEditInfo(False)
			return 1
		elif (bCtrl) or (self.m_bCityEdit):
			if (self.m_pCurrentPlot.isCity()):
				self.initCityEditScreen()
			return 1
		elif (self.m_bReveal):
			if (self.m_pCurrentPlot != 0):
				self.setMultipleReveal(True)
		elif (bShift and not bCtrl and not bAlt):
			self.setPlotEditInfo(True)
			return 1

		if (self.useLargeBrush()):
			self.placeMultipleObjects()
		else:
			self.placeObject()
		return 1

	def rightMouseDown (self, argsList):
		self.m_bRightMouseDown = True

		if CyInterface().isInAdvancedStart():
			self.removeObject()
			return 1

		if (self.m_bCityEdit or self.m_bUnitEdit):
			self.setPlotEditInfo(True)
		elif (self.m_bReveal):
			if (self.m_pCurrentPlot != 0):
				self.setMultipleReveal(False)
		else:
			if (self.useLargeBrush()):
				self.removeMultipleObjects()
			else:
				self.removeObject()

		return 1

	def update(self, fDelta):
		if (not CyInterface().isLeftMouseDown()):
			self.m_bLeftMouseDown = False
		if (not CyInterface().isRightMouseDown()):
			self.m_bRightMouseDown = False

		if (not self.m_bChangeFocus) and (not isMouseOverGameSurface()):
			self.m_bChangeFocus = True

		if (self.m_bChangeFocus and isMouseOverGameSurface() and (not self.m_bUnitEdit and not self.m_bCityEdit)):
			self.m_bChangeFocus = False
			setFocusToCVG()
		return

	# Will update the screen (every 250 MS)
	def updateScreen(self):
		screen = CyGInterfaceScreen( "WorldBuilderScreen", CvScreenEnums.WORLDBUILDER_SCREEN )

		if (CyInterface().isInAdvancedStart()):
			if (self.m_bSideMenuDirty):
				self.refreshSideMenu()
			if (self.m_bASItemCostDirty):
				self.refreshASItemCost()

		if (CyInterface().isDirty(InterfaceDirtyBits.Advanced_Start_DIRTY_BIT) and not CyInterface().isFocusedWidget()):
			self.refreshAdvancedStartTabCtrl(True)
			CyInterface().setDirty(InterfaceDirtyBits.Advanced_Start_DIRTY_BIT, False)

		if (self.useLargeBrush()):
			self.m_bShowBigBrush = True
		else:
			self.m_bShowBigBrush = False

		if (self.m_bCtrlEditUp):
			if ( (not self.m_bUnitEdit) and (not self.m_bCityEdit) and (not self.m_tabCtrlEdit.isEnabled()) and not CyInterface().isInAdvancedStart()):
				if (self.m_bNormalMap):
					self.m_normalMapTabCtrl.enable(True)
				if (self.m_bNormalPlayer):
					self.m_normalPlayerTabCtrl.enable(True)
				self.m_bCtrlEditUp = False
				return 0
		if ((self.m_bNormalMap) and(self.m_normalMapTabCtrl.getActiveTab() == self.m_iTerrainTabID) and (self.m_iNormalMapCurrentList[self.m_normalMapTabCtrl.getActiveTab()] == self.m_iRouteListID)):
			if (self.m_iNormalMapCurrentIndexes[self.m_normalMapTabCtrl.getActiveTab()] == gc.getNumRouteInfos()):
				if (self.m_pRiverStartPlot != -1):
					self.setRiverHighlights()
					return 0
		self.highlightBrush()
		return 0

	def redraw( self ):
		return 0

	def resetTechButtons( self ) :
		for i in range (gc.getNumTechInfos()):
			strName = "Tech_%s" %(i,)
			self.m_normalPlayerTabCtrl.setCheckBoxState("Technologies", gc.getTechInfo(i).getDescription(), gc.getTeam(gc.getPlayer(self.m_iCurrentPlayer).getTeam()).isHasTech(i))
		return 1

	def refreshReveal ( self ) :
		CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_REVEALED_PLOTS)
		for i in range (CyMap().getGridWidth()):
			for j in range (CyMap().getGridHeight()):
				pPlot = CyMap().plot(i,j)
				if (not pPlot.isNone()):
					self.showRevealed(pPlot)
		return 1

	def handleUnitEditExperienceCB (self, argsList) :
		self.m_pActivePlot.getUnit(self.m_iCurrentUnit).setExperience(int(argsList[0]),-1)
		return 1

	def handleUnitEditLevelCB (self, argsList) :
		self.m_pActivePlot.getUnit(self.m_iCurrentUnit).setLevel(int(argsList[0]))
		return 1

	def handleUnitEditNameCB (self, argsList) :
		if ((len(argsList[0]) < 1) or (self.m_pActivePlot == 0) or (self.m_iCurrentUnit < 0) or (self.m_pActivePlot.getNumUnits() <= self.m_iCurrentUnit)):
			return 1
		szNewName = argsList[0]
		unit = self.m_pActivePlot.getUnit(self.m_iCurrentUnit)
		if (unit):
			unit.setName(szNewName)
		return 1

#MagisterModmod
	def handleUnitEditIDSelectCB ( self, argsList ) :
		ID = int(argsList[0])
		pUnit = gc.getPlayer(self.m_iCurrentPlayer).getUnit(ID)
		if not pUnit.isNone():
			CyCamera().LookAtUnit(pUnit)
			self.m_iCurrentPlot = pUnit.plot()
			self.m_pActivePlot = pUnit.plot()
			for i in xrange(self.m_pActivePlot.getNumUnits()):
				if self.m_pActivePlot.getUnit(i).getID() == ID:
					self.m_iCurrentUnit = i
					self.setUnitEditInfo(True)
		return 1
#MagisterModmod

## Platy World Builder Start ##
## Common ##
	def handleEnterNewScreenCB ( self, argsList ) :
		strName = argsList[0]
		if strName == "PromotionEditScreen":
			WBPromotionScreen.WBPromotionScreen().interfaceScreen(self.m_pActivePlot.getUnit(self.m_iCurrentUnit))
		elif strName == "ProjectEditScreen":
			WBProjectScreen.WBProjectScreen().interfaceScreen(gc.getTeam(self.m_iCurrentTeam))
		elif strName == "TechEditScreen":
			WBTechScreen.WBTechScreen().interfaceScreen(gc.getTeam(self.m_iCurrentTeam))
		elif strName == "BuildingEditScreen":
			WBBuildingScreen.WBBuildingScreen().interfaceScreen(self.m_pActivePlot.getPlotCity())
		elif strName == "ReligionEditScreen":
			WBCorporationScreen.WBCorporationScreen().interfaceScreen(self.m_pActivePlot.getPlotCity())
		elif strName == "CorporationEditScreen":
			WBCorporationScreen.WBCorporationScreen().interfaceScreen(self.m_pActivePlot.getPlotCity())
		elif strName == "FreeSpecialistEditScreen":
			WBSpecialistScreen.WBSpecialistScreen().interfaceScreen(self.m_pActivePlot.getPlotCity())
		elif strName == "FreeBonusEditScreen":
			WBBonusScreen.WBBonusScreen().interfaceScreen(self.m_pActivePlot.getPlotCity())
		elif strName == "CityEditScreen":
			self.setCityEditInfo(True)

##MagisterModmod
		elif strName == "TraitEditScreen":
			self.setTraitEditInfo()
		elif strName == "PlayerEditScreen":
			self.setPlayerEditInfo()
			self.refreshSideMenu()
##MagisterModmod
		return 1

	def handleCivTypeEditPullDownCB( self, argsList ) :
		self.m_pActivePlot.getPlotCity().setCivilizationType(int(argsList[0]))
		return 1
##MagisterModmod

	def handleCurrentPlayerEditPullDownCB ( self, argsList ) :
		iIndex, strName = argsList
		iCount = 0
		for i in xrange(gc.getMAX_PLAYERS()):
			if gc.getPlayer(i).isEverAlive():
				if iCount == int(iIndex):
					self.m_iCurrentPlayer = i
					self.m_iCurrentTeam = gc.getPlayer(i).getTeam()
					if strName == "PlayerEditCurrentPlayer":
						self.setPlayerEditInfo()
						self.refreshSideMenu()
					elif strName == "PlotEditCurrentPlayer":
						self.setPlotEditInfo(False)
					elif strName == "UnitEditOwner":
						pUnit = self.m_pActivePlot.getUnit(self.m_iCurrentUnit)
						pNewUnit = gc.getPlayer(i).initUnit(pUnit.getUnitType(), pUnit.getX(), pUnit.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.NO_DIRECTION)
						pNewUnit.convert(pUnit)
						pNewUnit.setBaseCombatStr(pUnit.baseCombatStr())
						pNewUnit.changeCargoSpace(pUnit.cargoSpace() - pNewUnit.cargoSpace())
						pNewUnit.setImmobileTimer(pUnit.getImmobileTimer())
##MagisterModmod
						pNewUnit.setDuration(pUnit.getDuration())
						pNewUnit.setBaseCombatStrDefense(pUnit.baseCombatStrDefense())
						pNewUnit.setReligion(pUnit.getReligion())
##MagisterModmod

						pUnit.kill(False, -1)
						self.setUnitEditInfo(True)
					elif strName == "CityEditOwner":
						gc.getPlayer(i).acquireCity(self.m_pActivePlot.getPlotCity(), False, False)
						self.setCityEditInfo(True)

					return 1
				iCount += 1

## Side Panel ##

	def handleWorldBuilderEraseAllCB (self):
		for i in xrange(CyMap().numPlots()):
			self.m_pCurrentPlot = CyMap().plotByIndex(i)
			self.placeObject()
		return 1

	def handleWorldBuilderGameDataPullDownCB ( self, argsList ) :
		iIndex = int(argsList)
		if iIndex == 1:
			self.setPlayerEditInfo()
		elif iIndex == 2:
			self.setTeamEditInfo()
		elif iIndex == 3:
			self.setGameEditInfo()
		return 1

	def handleWorldBuilderGameCommandsPullDownCB ( self, argsList ) :
		iIndex = int(argsList)
		if iIndex > 0:
			self.m_iUnitCombat = - iIndex
			if iIndex == 3:
				pPlayer = gc.getPlayer(self.m_iCurrentPlayer)
				(loopCity, iter) = pPlayer.firstCity(False)
				while(loopCity):
					loopCity.kill()
					(loopCity, iter) = pPlayer.nextCity(iter, False)
				(loopUnit, iter) = pPlayer.firstUnit(False)
				while(loopUnit):
					loopUnit.kill(False, -1)
					(loopUnit, iter) = pPlayer.nextUnit(iter, False)
		else:
			self.m_iUnitCombat = -99
		self.m_iUnitType = -1
		self.refreshSideMenu()
		return 1

	def handleWorldBuilderAddUnitsPullDownCB ( self, argsList ) :
		iIndex = int(argsList)
		self.m_iUnitCombat = iIndex -1
		self.m_iUnitType = -1
		self.refreshSideMenu()
		return 1

	def handleWorldBuilderAddUnitCountPullDownCB ( self, argsList ) :
		iIndex = int(argsList)
		if iIndex == 0:
			self.m_iAddUnitCount = 1
		else:
			self.m_iAddUnitCount = iIndex * 10
		return 1

	def handleWorldBuilderUnitCombatPullDownCB ( self, argsList ) :
		iIndex = int(argsList)
		iCount = 0
		for i in xrange(gc.getNumUnitInfos()):
			if gc.getUnitInfo(i).getUnitCombatType() == self.m_iUnitCombat:
				if iCount == iIndex:
					self.m_iUnitType = i
					return 1
				iCount += 1
		self.m_iUnitType = -1
		return 1

	def handleWorldBuilderSetWinnerPullDownCB ( self, argsList ) :
		iIndex = int(argsList)
		CyGame().setWinner(self.m_iCurrentTeam, iIndex -1)
		return 1

#Magister Modmod
	def handleWorldBuilderReassignPlayerCB ( self, argsList ) :
		iIndex = int(argsList)
		CyGame().reassignPlayerAdvanced(self.m_iCurrentPlayer, iIndex, -1)
		return 1

	def handleWorldBuilderChooseCivilizationPullDownCB ( self, argsList ) :
		iIndex = int(argsList)
		iCount = 1
		for i in xrange(gc.getNumCivilizationInfos()):
##			if not CyGame().isCivEverActive(i):#I want to allow multiple leaders of the same civ in the same game
			if iCount == iIndex:
				self.m_iNewCivilization = i
				self.m_iNewLeaderType = -1
				self.refreshSideMenu()
				return 1
			iCount+= 1

	def handleWorldBuilderChooseLeaderPullDownCB ( self, argsList ) :
		iIndex = int(argsList)
		iCount = 1
		for i in xrange(gc.getNumLeaderHeadInfos()):
			if not CyGame().isLeaderEverActive(i):
				if not CyGame().isOption(GameOptionTypes.GAMEOPTION_LEAD_ANY_CIV):
					if not gc.getCivilizationInfo(self.m_iNewCivilization).isLeaders(i): continue
				if iCount == iIndex:
					self.m_iNewLeaderType = i
					for i in xrange(gc.getMAX_CIV_PLAYERS()):
						if not gc.getPlayer(i).isEverAlive():
							CyGame().addPlayer(i, self.m_iNewLeaderType, self.m_iNewCivilization, True)
							self.m_iCurrentPlayer = i
							self.m_iCurrentTeam = gc.getPlayer(i).getTeam()
							self.m_iNewCivilization = -1
							self.refreshSideMenu()
							self.normalPlayerTabModeCB()
							return 1
				iCount+= 1

	def handleWorldBuilderEditAreaMapPullDownCB ( self, argsList ) :
		self.m_iPlotMode = int(argsList)
		self.m_iArea = -1
		self.refreshSideMenu()
		return 1

	def handleWorldBuilderRevealModePullDownCB ( self, argsList ) :
		self.m_iRevealMode = int(argsList)
		self.refreshReveal()
		return 1

	def handleWorldBuilderModifyAreaPlotTypePullDownCB ( self, argsList ) :
		iIndex = int(argsList) -1
		if self.m_iPlotMode == 3:
			CyMap().setAllPlotTypes(iIndex)
		else:
			PlotType = [PlotTypes.PLOT_PEAK, PlotTypes.PLOT_HILLS, PlotTypes.PLOT_LAND, PlotTypes.PLOT_OCEAN]
			for i in xrange(CyMap().numPlots()):
				pPlot = CyMap().plotByIndex(i)
				if (not pPlot.isNone()) and pPlot.getArea() == self.m_iArea:
					pPlot.setPlotType(PlotType[iIndex], True, True)
		self.refreshSideMenu()
		return 1

	def handleWorldBuilderModifyAreaTerrainPullDownCB ( self, argsList ) :
		iIndex = int(argsList) -1
		lTerrain = []
		for i in xrange(gc.getNumTerrainInfos()):
			if gc.getTerrainInfo(i).isGraphicalOnly(): continue
			if self.m_iPlotMode == 3:
				lTerrain.append(i)
			elif CyMap().getArea(self.m_iArea).isWater() and gc.getTerrainInfo(i).isWater():
				lTerrain.append(i)
			elif not CyMap().getArea(self.m_iArea).isWater() and not gc.getTerrainInfo(i).isWater():
				lTerrain.append(i)
		if iIndex < len(lTerrain):
			for i in xrange(CyMap().numPlots()):
				pPlot = CyMap().plotByIndex(i)
				if pPlot.isNone(): continue
				if self.m_iPlotMode == 3:
					if gc.getTerrainInfo(iIndex).isWater() and pPlot.isWater():
						pPlot.setTerrainType(lTerrain[iIndex], True, True)
					elif (not gc.getTerrainInfo(iIndex).isWater()) and (not pPlot.isWater()):
						pPlot.setTerrainType(lTerrain[iIndex], True, True)
				elif pPlot.getArea() == self.m_iArea:
					pPlot.setTerrainType(lTerrain[iIndex], True, True)
		self.refreshSideMenu()
		return 1

	def handleWorldBuilderModifyAreaRoutePullDownCB ( self, argsList ) :
		iIndex = int(argsList) -1
		if iIndex == gc.getNumRouteInfos():
			iIndex = -1
		for i in xrange(CyMap().numPlots()):
			pPlot = CyMap().plotByIndex(i)
			if pPlot.isNone(): continue
			if pPlot.isImpassable(): continue
			if pPlot.isWater(): continue
			if pPlot.getArea() == self.m_iArea or self.m_iPlotMode == 3:
				pPlot.setRouteType(iIndex)
		self.refreshSideMenu()
		return 1

	def handleWorldBuilderModifyAreaFeaturePullDownCB ( self, argsList ) :
		iIndex = int(argsList) -1
		if iIndex == gc.getNumFeatureInfos():
			iIndex = -1
		for i in xrange(CyMap().numPlots()):
			pPlot = CyMap().plotByIndex(i)
			if pPlot.isNone(): continue
			if pPlot.getArea() == self.m_iArea or self.m_iPlotMode == 3:
				if pPlot.canHaveFeature(iIndex):
					pPlot.setFeatureType(iIndex, -1)
		self.refreshSideMenu()
		return 1
## City Data ##

	def handleChooseCityCB (self, argsList) :
		iCount = 0
		(loopCity, iter) = gc.getPlayer(self.m_iCurrentPlayer).firstCity(False)
		while(loopCity):
			if iCount == int(argsList[0]):
				self.m_pActivePlot = loopCity.plot()
				self.setCityEditInfo(True)
				return 1
			iCount += 1
			(loopCity, iter) = gc.getPlayer(self.m_iCurrentPlayer).nextCity(iter, False)

	def handleCityEditPopulationCB (self, argsList) :
		self.m_pActivePlot.getPlotCity().setPopulation(int(argsList[0]))
		self.setCityEditInfo(True)
		return 1
##MagisterModmod MNAI
	def handleCityEditRevIndexCB (self, argsList) :
		self.m_pActivePlot.getPlotCity().setRevolutionIndex(int(argsList[0]))
		self.setCityEditInfo(True)
		return 1
##MagisterModmod MNAI

	def handleCityEditCultureCB (self, argsList) :
		self.m_pActivePlot.getPlotCity().setCulture(self.m_iCurrentPlayer, int(argsList[0]), True)
		self.setCityEditInfo(True)
		return 1

	def handleCityEditCultureLevelCB ( self, argsList ) :
		self.m_pActivePlot.getPlotCity().setCulture(self.m_iCurrentPlayer, gc.getCultureLevelInfo(int(argsList[0])).getSpeedThreshold(CyGame().getGameSpeedType()), True)
		self.setCityEditInfo(True)
		return 1

	def handleCityEditHappinessCB (self, argsList) :
		self.m_pActivePlot.getPlotCity().changeExtraHappiness(int(argsList[0]) - self.m_pActivePlot.getPlotCity().happyLevel() + self.m_pActivePlot.getPlotCity().unhappyLevel(0))
		return 1

	def handleCityEditHealthCB (self, argsList) :
		self.m_pActivePlot.getPlotCity().changeExtraHealth(int(argsList[0]) - self.m_pActivePlot.getPlotCity().goodHealth() + self.m_pActivePlot.getPlotCity().badHealth(False))
		return 1

	def handleCityEditTimersCB (self, argsList) :
		self.m_iCityTimer = int(argsList[0])
		self.setCityEditInfo(True)
		return 1

	def handleCityEditCurrentTimerCB (self, argsList) :
		if self.m_iCityTimer == 0:
			self.m_pActivePlot.getPlotCity().setOccupationTimer(int(argsList[0]))
		elif self.m_iCityTimer == 1:
			self.m_pActivePlot.getPlotCity().changeConscriptAngerTimer(int(argsList[0]) - self.m_pActivePlot.getPlotCity().getConscriptAngerTimer())
		elif self.m_iCityTimer == 2:
			self.m_pActivePlot.getPlotCity().changeHurryAngerTimer(int(argsList[0]) - self.m_pActivePlot.getPlotCity().getHurryAngerTimer())
		elif self.m_iCityTimer == 3:
			self.m_pActivePlot.getPlotCity().changeDefyResolutionAngerTimer(int(argsList[0]) - self.m_pActivePlot.getPlotCity().getDefyResolutionAngerTimer())
		elif self.m_iCityTimer == 4:
			self.m_pActivePlot.getPlotCity().changeEspionageHappinessCounter(int(argsList[0]) - self.m_pActivePlot.getPlotCity().getEspionageHappinessCounter())
		elif self.m_iCityTimer == 5:
			self.m_pActivePlot.getPlotCity().changeEspionageHealthCounter(int(argsList[0]) - self.m_pActivePlot.getPlotCity().getEspionageHealthCounter())
		else:
			self.m_pActivePlot.getPlotCity().changeHappinessTimer(int(argsList[0]) - self.m_pActivePlot.getPlotCity().getHappinessTimer())
		self.setCityEditInfo(True)
		return 1

	def handleCityEditDefenseCB (self, argsList) :
		iNewDefenseDamage =100 - 100 * int(argsList[0])/self.m_pActivePlot.getPlotCity().getTotalDefense(False)
		self.m_pActivePlot.getPlotCity().changeDefenseDamage(iNewDefenseDamage - self.m_pActivePlot.getPlotCity().getDefenseDamage())
		return 1

	def handleCityEditTradeRouteCB (self, argsList) :
		self.m_pActivePlot.getPlotCity().changeExtraTradeRoutes(int(argsList[0]) - self.m_pActivePlot.getPlotCity().getTradeRoutes())
		return 1

	def handleCityEditBonusCB (self, argsList) :
		iIndex, strName = argsList
		self.m_pActivePlot.getPlotCity().changeFreeBonus(int(strName), int(iIndex) - self.m_pActivePlot.getPlotCity().getFreeBonus(int(strName)))
		return 1

	def handleCityEditBuildingClassCB (self, argsList) :
		self.m_iBuildingClass = int(argsList[0])
		self.setCityEditInfo(True)
		return 1

	def handleCityEditModiferCB (self, argsList) :
		self.m_iBuildingModifier = int(argsList[0])
		self.setCityEditInfo(True)
		return 1

	def handleCityEditModifyBuildingClassCB (self, argsList) :
		lBuildingClass = []
		for i in xrange(gc.getNumBuildingClassInfos()):
			lBuildingClass.append([gc.getBuildingClassInfo(i).getDescription(), i])
		lBuildingClass.sort()
		iBuildingClass = lBuildingClass[self.m_iBuildingClass][1]
		pPlayer = gc.getPlayer(self.m_iCurrentPlayer)
		iBuilding = gc.getCivilizationInfo(pPlayer.getCivilizationType()).getCivilizationBuildings(iBuildingClass)
		if self.m_iBuildingModifier < 3:
			self.m_pActivePlot.getPlotCity().setBuildingYieldChange(iBuildingClass, self.m_iBuildingModifier, int(argsList[0]))
		else:
			self.m_pActivePlot.getPlotCity().setBuildingCommerceChange(iBuildingClass, self.m_iBuildingModifier - 3, int(argsList[0]))
		self.setCityEditInfo(True)
		return 1

	def handleCityEditChooseProductionCB (self, argsList) :
		iIndex = int(argsList[0])
		pCity = self.m_pActivePlot.getPlotCity()
		if iIndex == 0:
			pCity.pushOrder(OrderTypes.NO_ORDER, -1, -1, False, True, False, True)
			self.setCityEditInfo(True)
			return 1
		iCount = 1
		for iUnit in xrange(gc.getNumUnitInfos()):
			if pCity.canTrain(iUnit, True, False):
				if iCount == iIndex:
					iUnitClass = gc.getUnitInfo(iUnit).getUnitClassType()
					if gc.getPlayer(self.m_iCurrentPlayer).getUnitClassCountPlusMaking(iUnitClass) == gc.getUnitClassInfo(iUnitClass).getMaxPlayerInstances():
						self.setCityEditInfo(True)
						return 1
					if gc.getTeam(self.m_iCurrentTeam).getUnitClassCountPlusMaking(iUnitClass) == gc.getUnitClassInfo(iUnitClass).getMaxTeamInstances():
						self.setCityEditInfo(True)
						return 1
					if gc.getTeam(self.m_iCurrentTeam).getUnitClassCountPlusMaking(iUnitClass) == gc.getUnitClassInfo(iUnitClass).getMaxGlobalInstances():
						self.setCityEditInfo(True)
						return 1
					pCity.pushOrder(OrderTypes.ORDER_TRAIN, iUnit , -1, False, True, False, True)
					self.setCityEditInfo(True)
					return 1
				iCount += 1
		for iBuilding in xrange(gc.getNumBuildingInfos()):
			if pCity.canConstruct(iBuilding, True, False, False):
				if iCount == iIndex:
					iBuildingClass = gc.getBuildingInfo(iBuilding).getBuildingClassType()
					if gc.getPlayer(self.m_iCurrentPlayer).getBuildingClassCountPlusMaking(iBuildingClass) == gc.getBuildingClassInfo(iBuildingClass).getMaxPlayerInstances():
						self.setCityEditInfo(True)
						return 1
					if gc.getTeam(self.m_iCurrentTeam).getBuildingClassCountPlusMaking(iBuildingClass) == gc.getBuildingClassInfo(iBuildingClass).getMaxTeamInstances():
						self.setCityEditInfo(True)
						return 1
					if gc.getTeam(self.m_iCurrentTeam).getBuildingClassCountPlusMaking(iBuildingClass) == gc.getBuildingClassInfo(iBuildingClass).getMaxGlobalInstances():
						self.setCityEditInfo(True)
						return 1
					pCity.pushOrder(OrderTypes.ORDER_CONSTRUCT, iBuilding , -1, False, True, False, True)
					self.setCityEditInfo(True)
					return 1
				iCount += 1
		for iProject in xrange(gc.getNumProjectInfos()):
			if pCity.canCreate(iProject, True, False):
				if iCount == iIndex:
					if gc.getTeam(self.m_iCurrentTeam).getProjectMaking(iProject) + gc.getTeam(self.m_iCurrentTeam).getProjectCount(iProject) == gc.getProjectInfo(iProject).getMaxTeamInstances():
						self.setCityEditInfo(True)
						return 1
					if gc.getTeam(self.m_iCurrentTeam).getProjectMaking(iProject) + gc.getTeam(self.m_iCurrentTeam).getProjectCount(iProject) == gc.getProjectInfo(iProject).getMaxGlobalInstances():
						self.setCityEditInfo(True)
						return 1
					pCity.pushOrder(OrderTypes.ORDER_CREATE, iProject , -1, False, True, False, True)
					self.setCityEditInfo(True)
					return 1
				iCount += 1
		for iProcess in xrange(gc.getNumProcessInfos()):
			if pCity.canMaintain(iProcess, True):
				if iCount == iIndex:
					pCity.pushOrder(OrderTypes.ORDER_MAINTAIN, iProcess , -1, False, True, False, True)
					self.setCityEditInfo(True)
					return 1
				iCount += 1

	def handleCityEditProductionProgressCB (self, argsList) :
		self.m_pActivePlot.getPlotCity().setProduction(int(argsList[0]))
		self.setCityEditInfo(True)
		return 1

	def handleCityEditFoodCB (self, argsList) :
		self.m_pActivePlot.getPlotCity().setFood(int(argsList[0]))
		self.setCityEditInfo(True)
		return 1

## Unit Data ##

	def handleKillCB (self, argsList) :
		strName = argsList[0]
		self.m_pActivePlot.getUnit(self.m_iCurrentUnit).kill(False, -1)
		self.toggleUnitEditCB()
		return 1

	def handleUnitEditStrengthCB (self, argsList) :
		self.m_pActivePlot.getUnit(self.m_iCurrentUnit).setBaseCombatStr(int(argsList[0]))
		return 1
##Magister
	def handleUnitEditStrengthDefenseCB (self, argsList) :
		self.m_pActivePlot.getUnit(self.m_iCurrentUnit).setBaseCombatStrDefense(int(argsList[0]))
		return 1
##Magister
	def handleUnitEditDamageCB (self, argsList) :
		self.m_pActivePlot.getUnit(self.m_iCurrentUnit).setDamage(int(argsList[0]), -1)
		return 1

	def handleUnitEditMovesCB (self, argsList) :
		self.m_pActivePlot.getUnit(self.m_iCurrentUnit).setMoves(self.m_pActivePlot.getUnit(self.m_iCurrentUnit).maxMoves() - (int(argsList[0]) * gc.getDefineINT("MOVE_DENOMINATOR")))
		return 1

	def handleUnitEditCargoCB (self, argsList) :
		self.m_pActivePlot.getUnit(self.m_iCurrentUnit).changeCargoSpace(int(argsList[0]) - self.m_pActivePlot.getUnit(self.m_iCurrentUnit).cargoSpace())
		return 1

	def handleUnitEditImmobileTimerCB (self, argsList):
		self.m_pActivePlot.getUnit(self.m_iCurrentUnit).setImmobileTimer(int(argsList[0]))
		return 1

##MagisterModmod
	def handleUnitEditDurationCB (self, argsList):
		self.m_pActivePlot.getUnit(self.m_iCurrentUnit).setDuration(int(argsList[0]))
		return 1

	def handleUnitEditSummonerCB (self, argsList):
		self.m_pActivePlot.getUnit(self.m_iCurrentUnit).setSummoner(int(argsList[0]))
		self.setUnitEditInfo(True)
		return 1

	def handleUnitEditScenarioCounterCB (self, argsList):
		self.m_pActivePlot.getUnit(self.m_iCurrentUnit).setScenarioCounter(int(argsList[0]))
		self.setUnitEditInfo(True)
		return 1
##MagisterModmod

	def handleUnitEditPromotionReadyCB (self, argsList) :
		iPromotionReady = int(argsList[0])
		if self.m_pActivePlot.getUnit(self.m_iCurrentUnit).experienceNeeded() > self.m_pActivePlot.getUnit(self.m_iCurrentUnit).getExperience():
			iPromotionReady = 0
		self.m_pActivePlot.getUnit(self.m_iCurrentUnit).setPromotionReady(iPromotionReady)
		self.setUnitEditInfo(True)
		return 1

	def handleUnitEditMadeAttackCB (self, argsList) :
		self.m_pActivePlot.getUnit(self.m_iCurrentUnit).setMadeAttack(int(argsList[0]))
		return 1

	def handleUnitEditMadeInterceptionCB (self, argsList) :
		self.m_pActivePlot.getUnit(self.m_iCurrentUnit).setMadeInterception(int(argsList[0]))
		return 1
##Magister
	def handleUnitEditHasCastedCB (self, argsList) :
		self.m_pActivePlot.getUnit(self.m_iCurrentUnit).setHasCasted(bool(argsList[0]))
		return 1

	def handleUnitEditIsImmortalCB (self, argsList) :
		if bool(argsList[0]):
			self.m_pActivePlot.getUnit(self.m_iCurrentUnit).changeImmortal(1)
		elif self.m_pActivePlot.getUnit(self.m_iCurrentUnit).isImmortal():
			self.m_pActivePlot.getUnit(self.m_iCurrentUnit).changeImmortal(-1)
		self.setUnitEditInfo(True)
		return 1

	def handleUnitEditAvatarOfCivLeaderCB(self, argsList) :
		self.m_pActivePlot.getUnit(self.m_iCurrentUnit).setAvatarOfCivLeader(bool(argsList[0]))
		return 1

	def handleUnitEditPermanentSummonCB(self, argsList) :
		self.m_pActivePlot.getUnit(self.m_iCurrentUnit).setPermanentSummon(bool(argsList[0]))
		return 1

##Magister
	def handleMoveUnitCB (self, argsList) :
		self.m_bMoveUnit = True
		self.toggleUnitEditCB()
		return 1

	def handleUnitEditDirectionCB (self, argsList) :
		iIndex = int(argsList[0])
		iDirection = self.m_pActivePlot.getUnit(self.m_iCurrentUnit).getFacingDirection()
		if iDirection > iIndex:
			for i in range(iDirection - iIndex):
				self.m_pActivePlot.getUnit(self.m_iCurrentUnit).rotateFacingDirectionCounterClockwise()
		else:
			for i in range(iIndex - iDirection):
				self.m_pActivePlot.getUnit(self.m_iCurrentUnit).rotateFacingDirectionClockwise()
		return 1

	def handleUnitEditDuplicateCB (self, argsList) :
		pUnit = self.m_pActivePlot.getUnit(self.m_iCurrentUnit)
		for i in range (2):
			pNewUnit = gc.getPlayer(self.m_iCurrentPlayer).initUnit(pUnit.getUnitType(), pUnit.getX(), pUnit.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.NO_DIRECTION)

##MagisterModmod
##When duplicating Adventurers and other great people, I don't want the double to get the free promotion that the named ones get
			for iProm in range(gc.getNumPromotionInfos()):
				if pNewUnit.isHasPromotion(iProm):
					pNewUnit.setHasPromotion(iProm, False)
##MagisterModmod

			pNewUnit.convert(pUnit)
			pNewUnit.setBaseCombatStr(pUnit.baseCombatStr())
			pNewUnit.changeCargoSpace(pUnit.cargoSpace() - pNewUnit.cargoSpace())
			pNewUnit.setImmobileTimer(pUnit.getImmobileTimer())
			pNewUnit.setScriptData(pUnit.getScriptData())

##MagisterModmod
			pNewUnit.setDuration(pUnit.getDuration())
			pNewUnit.setBaseCombatStrDefense(pUnit.baseCombatStrDefense())
			pNewUnit.setReligion(pUnit.getReligion())
			pNewUnit.setSummoner(pUnit.getSummoner())
##MagisterModmod
		pUnit.kill(False, -1)
		self.setUnitEditInfo(True)
		return 1

	def handleUnitEditLeaderCB (self, argsList) :
		pUnit = self.m_pActivePlot.getUnit(self.m_iCurrentUnit)
##		lUnitType = ["_Platy_-1"]
		lUnitType = [-1]
		for i in xrange(gc.getNumUnitInfos()):
			if gc.getUnitInfo(i).getDomainType() == pUnit.getDomainType():
				lUnitType.append([gc.getUnitInfo(i).getDescription(), i])
		lUnitType.sort()
		iIndex = int(argsList[0]) -1
		pUnit.setLeaderUnitType(lUnitType[iIndex][1])
		return 1

	def handleUnitEditUnitTypeCB (self, argsList) :
		iIndex = int(argsList[0])
		pUnit = self.m_pActivePlot.getUnit(self.m_iCurrentUnit)
		lUnitType = []
		for i in xrange(gc.getNumUnitInfos()):
			lUnitType.append([gc.getUnitInfo(i).getDescription(), i])
		lUnitType.sort()
		pNewUnit = gc.getPlayer(self.m_iCurrentPlayer).initUnit(lUnitType[iIndex][1], pUnit.getX(), pUnit.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.NO_DIRECTION)

##MagisterModmod
		pNewUnit.setImmobileTimer(pUnit.getImmobileTimer())
		pNewUnit.setSummoner(pUnit.getSummoner())
		pNewUnitID = pNewUnit.getID()
		summonerID = pUnit.getID()
		pPlayer = gc.getPlayer(pUnit.getOwner())
		(loopUnit, iter) = pPlayer.firstUnit(False)
		while(loopUnit):
			if not loopUnit.isDead(): #is the unit alive and valid?
				if loopUnit.getSummoner() == summonerID:#is it a summon of pUnit?
					loopUnit.setSummoner(pNewUnitID)
			(loopUnit, iter) = pPlayer.nextUnit(iter, False)
##MagisterModmod

		pNewUnit.convert(pUnit)
		pNewUnit.setScriptData("PlatyCurrentUnit" + pUnit.getScriptData())
		pUnit.kill(False, -1)
		for i in xrange(self.m_pActivePlot.getNumUnits()):
			if self.m_pActivePlot.getUnit(i).getScriptData().find("PlatyCurrentUnit") == 0:
				self.m_iCurrentUnit = i
				self.m_pActivePlot.getUnit(i).setScriptData(self.m_pActivePlot.getUnit(i).getScriptData()[16:])
				self.setUnitEditInfo(True)
				return 1
		self.setCityEditInfo(True)

## Player Data ##

	def handleCurrentEraEditPullDownCB ( self, argsList ) :
		gc.getPlayer(self.m_iCurrentPlayer).setCurrentEra(int(argsList[0]))
		return 1

	def handleTeamEditCommerceFlexibleCB (self, argsList) :
		iIndex, strName = argsList
		if int(iIndex):
			gc.getTeam(self.m_iCurrentTeam).changeCommerceFlexibleCount(int(strName),  1)
		else:
			gc.getTeam(self.m_iCurrentTeam).changeCommerceFlexibleCount(int(strName),  - gc.getTeam(self.m_iCurrentTeam).getCommerceFlexibleCount(int(strName)))
		self.setPlayerEditInfo()
		return 1

	def handlePlayerEditCommercePercentCB (self, argsList) :
		iIndex, strName = argsList
		CommerceType = [CommerceTypes.COMMERCE_GOLD, CommerceTypes.COMMERCE_RESEARCH, CommerceTypes.COMMERCE_CULTURE, CommerceTypes.COMMERCE_ESPIONAGE]
		gc.getPlayer(self.m_iCurrentPlayer).setCommercePercent(CommerceType[int(strName)], int(iIndex))
		self.setPlayerEditInfo()
		return 1

	def handlePlayerEditGoldenAgeCB (self, argsList) :
		gc.getPlayer(self.m_iCurrentPlayer).changeGoldenAgeTurns(int(argsList[0]) - gc.getPlayer(self.m_iCurrentPlayer).getGoldenAgeTurns())
		self.setPlayerEditInfo()
		return 1

	def handlePlayerEditGoldenAgeUnitsCB (self, argsList) :
		gc.getPlayer(self.m_iCurrentPlayer).changeNumUnitGoldenAges(int(argsList[0]) - gc.getPlayer(self.m_iCurrentPlayer).unitsRequiredForGoldenAge())
		return 1

	def handlePlayerEditAnarchyCB (self, argsList) :
		gc.getPlayer(self.m_iCurrentPlayer).changeAnarchyTurns(int(argsList[0]) - gc.getPlayer(self.m_iCurrentPlayer).getAnarchyTurns())
		self.setPlayerEditInfo()
		return 1

	def handlePlayerEditCombatExperienceCB (self, argsList) :
		gc.getPlayer(self.m_iCurrentPlayer).setCombatExperience(int(argsList[0]))
		self.setPlayerEditInfo()
		return 1

	def handlePlayerEditCivicCB ( self, argsList ) :
		iIndex, strName = argsList
		iCount = 0
		for i in xrange(gc.getNumCivicInfos()):
			if gc.getCivicInfo(i).getCivicOptionType() == int(strName):
				if int(iIndex) == iCount:
					if gc.getPlayer(self.m_iCurrentPlayer).canDoCivics(i):
						gc.getPlayer(self.m_iCurrentPlayer).setCivics(int(strName), i)
					self.setPlayerEditInfo()
					return 1
				iCount += 1

##MagisterModmod
	def handleAlignmentEditPullDownCB ( self, argsList ) :
		gc.getPlayer(self.m_iCurrentPlayer).setAlignment(int(argsList[0]))
		return 1

	def handleEditPlayerTraitCB (self, argsList) :
		iIndex, strName = argsList
		gc.getPlayer(self.m_iCurrentPlayer).setHasTrait(int(strName), iIndex)
		return 1

	def handleEditFeatHasCastWorldSpellCB (self, argsList) :
		gc.getPlayer(self.m_iCurrentPlayer).setFeatAccomplished(FeatTypes.FEAT_GLOBAL_SPELL, bool(argsList[0]))

	def handleEditFeatTrustCB (self, argsList) :
		gc.getPlayer(self.m_iCurrentPlayer).setFeatAccomplished(FeatTypes.FEAT_TRUST, bool(argsList[0]))

	def handleEditFeatHealUnitPerTurnCB (self, argsList) :
		gc.getPlayer(self.m_iCurrentPlayer).setFeatAccomplished(FeatTypes.FEAT_HEAL_UNIT_PER_TURN, bool(argsList[0]))

##MagisterModmod

	def handleStateReligionEditPullDownCB ( self, argsList ) :
		gc.getPlayer(self.m_iCurrentPlayer).setLastStateReligion(int(argsList[0]) - 1)
		self.setPlayerEditInfo()
		return 1

	def handlePlayerEditStateReligionUnitProductionCB (self, argsList) :
		gc.getPlayer(self.m_iCurrentPlayer).changeStateReligionUnitProductionModifier(int(argsList[0]) - gc.getPlayer(self.m_iCurrentPlayer).getStateReligionUnitProductionModifier())
		return 1

	def handlePlayerEditStateReligionBuildingProductionCB (self, argsList) :
		gc.getPlayer(self.m_iCurrentPlayer).changeStateReligionBuildingProductionModifier(int(argsList[0]) - gc.getPlayer(self.m_iCurrentPlayer).getStateReligionBuildingProductionModifier())
		return 1

	def handleCurrentTechEditPullDownCB (self, argsList) :
		iCount = 0
		gc.getPlayer(self.m_iCurrentPlayer).clearResearchQueue()
		for i in xrange(gc.getNumTechInfos()):
			if gc.getPlayer(self.m_iCurrentPlayer).canResearch(i, False):
				iCount += 1
				if iCount == int(argsList[0]):
					gc.getPlayer(self.m_iCurrentPlayer).pushResearch(i, True)
					break
		self.setPlayerEditInfo()
		return 1

	def handleTeamEditResearchProgressCB (self, argsList) :
		gc.getTeam(self.m_iCurrentTeam).setResearchProgress(gc.getPlayer(self.m_iCurrentPlayer).getCurrentResearch(), int(argsList[0]), self.m_iCurrentPlayer)
		self.setPlayerEditInfo()
		return 1

	def handlePlayerEditGoldCB (self, argsList) :
		gc.getPlayer(self.m_iCurrentPlayer).setGold(int(argsList[0]))
		return 1

## Team Data ##

	def handleTeamEditPullDownCB ( self, argsList ) :
		lTeam = []
		for i in xrange(gc.getMAX_TEAMS()):
			if gc.getTeam(i).isAlive():
				lTeam.append(i)
		self.m_iCurrentTeam = lTeam[int(argsList[0])]
		self.m_iCurrentPlayer = gc.getTeam(self.m_iCurrentTeam).getLeaderID()
		self.setTeamEditInfo()
		self.refreshSideMenu()
		return 1

	def handleAddTeamCB ( self, argsList ) :
		iCount = 1
		for i in xrange(gc.getMAX_TEAMS()):
			if gc.getTeam(i).isAlive():
				if i == self.m_iCurrentTeam: continue
				if int(argsList[0]) == iCount:
					gc.getTeam(self.m_iCurrentTeam).addTeam(i)
					self.setTeamEditInfo()
					return 1
				iCount += 1

	def handleTeamEditEnemyWarWearinessCB (self, argsList) :
		gc.getTeam(self.m_iCurrentTeam).changeEnemyWarWearinessModifier(int(argsList[0]) - gc.getTeam(self.m_iCurrentTeam).getEnemyWarWearinessModifier())
		return 1

	def handleTeamEditNukeInterceptionCB (self, argsList) :
		gc.getTeam(self.m_iCurrentTeam).changeNukeInterception(int(argsList[0]) - gc.getTeam(self.m_iCurrentTeam).getNukeInterception())
		return 1

	def handleDomainEditPullDownCB ( self, argsList ) :
		self.m_iDomain = int(argsList[0])
		self.setTeamEditInfo()
		return 1

	def handleTeamEditDomainMovesCB (self, argsList) :
		gc.getTeam(self.m_iCurrentTeam).changeExtraMoves(self.m_iDomain, int(argsList[0]) - gc.getTeam(self.m_iCurrentTeam).getExtraMoves(self.m_iDomain))
		return 1

	def handleRouteEditPullDownCB ( self, argsList ) :
		self.m_iRoute = int(argsList[0])
		self.setTeamEditInfo()
		return 1

	def handleTeamEditRouteChangeCB (self, argsList) :
		gc.getTeam(self.m_iCurrentTeam).changeRouteChange(self.m_iRoute, int(argsList[0]) - gc.getTeam(self.m_iCurrentTeam).getRouteChange(self.m_iRoute))
		return 1

	def handleImprovementEditPullDownCB ( self, argsList ) :
		self.m_iImprovement = int(argsList[0])
		self.setTeamEditInfo()
		return 1

	def handleYieldEditPullDownCB ( self, argsList ) :
		self.m_iYield = int(argsList[0])
		self.setTeamEditInfo()
		return 1

	def handleTeamEditImprovementYieldCB (self, argsList) :
		iCount = 0
		for i in xrange(gc.getNumImprovementInfos()):
			if gc.getImprovementInfo(i).isGraphicalOnly(): continue
			if iCount == self.m_iImprovement:
				gc.getTeam(self.m_iCurrentTeam).changeImprovementYieldChange(i, self.m_iYield, int(argsList[0]) - gc.getTeam(self.m_iCurrentTeam).getImprovementYieldChange(i, self.m_iYield))
				return 1
			iCount += 1

	def handleTeamEditMapCenteringCB (self, argsList) :
		gc.getTeam(self.m_iCurrentTeam).setMapCentering(int(argsList[0]))
		return 1

	def handleTeamEditGoldTradingCB (self, argsList) :
		if int(argsList[0]):
			gc.getTeam(self.m_iCurrentTeam).changeGoldTradingCount(1)
		else:
			gc.getTeam(self.m_iCurrentTeam).changeGoldTradingCount( -gc.getTeam(self.m_iCurrentTeam).getGoldTradingCount())
		return 1

	def handleTeamEditTechTradingCB (self, argsList) :
		if int(argsList[0]):
			gc.getTeam(self.m_iCurrentTeam).changeTechTradingCount(1)
		else:
			gc.getTeam(self.m_iCurrentTeam).changeTechTradingCount( -gc.getTeam(self.m_iCurrentTeam).getTechTradingCount())
		return 1

	def handleTeamEditMapTradingCB (self, argsList) :
		if int(argsList[0]):
			gc.getTeam(self.m_iCurrentTeam).changeMapTradingCount(1)
		else:
			gc.getTeam(self.m_iCurrentTeam).changeMapTradingCount( -gc.getTeam(self.m_iCurrentTeam).getMapTradingCount())
		return 1

	def handleTeamEditOpenBordersTradingCB (self, argsList) :
		if int(argsList[0]):
			gc.getTeam(self.m_iCurrentTeam).changeOpenBordersTradingCount(1)
		else:
			gc.getTeam(self.m_iCurrentTeam).changeOpenBordersTradingCount( -gc.getTeam(self.m_iCurrentTeam).getOpenBordersTradingCount())
		return 1

	def handleTeamEditPermanentAllianceTradingCB (self, argsList) :
		if int(argsList[0]):
			gc.getTeam(self.m_iCurrentTeam).changePermanentAllianceTradingCount(1)
		else:
			gc.getTeam(self.m_iCurrentTeam).changePermanentAllianceTradingCount( -gc.getTeam(self.m_iCurrentTeam).getPermanentAllianceTradingCount())
		return 1

	def handleTeamEditDefensivePactTradingCB (self, argsList) :
		if int(argsList[0]):
			gc.getTeam(self.m_iCurrentTeam).changeDefensivePactTradingCount(1)
		else:
			gc.getTeam(self.m_iCurrentTeam).changeDefensivePactTradingCount( -gc.getTeam(self.m_iCurrentTeam).getDefensivePactTradingCount())
		return 1

	def handleTeamEditVassalTradingCB (self, argsList) :
		if int(argsList[0]):
			gc.getTeam(self.m_iCurrentTeam).changeVassalTradingCount(1)
		else:
			gc.getTeam(self.m_iCurrentTeam).changeVassalTradingCount( -gc.getTeam(self.m_iCurrentTeam).getVassalTradingCount())
		return 1

	def handleTeamEditWaterWorkCB (self, argsList) :
		if int(argsList[0]):
			gc.getTeam(self.m_iCurrentTeam).changeWaterWorkCount(1)
		else:
			gc.getTeam(self.m_iCurrentTeam).changeWaterWorkCount( -gc.getTeam(self.m_iCurrentTeam).getWaterWorkCount())
		return 1

	def handleTeamEditExtraWaterSeeFromCB (self, argsList) :
		if int(argsList[0]):
			gc.getTeam(self.m_iCurrentTeam).changeExtraWaterSeeFromCount(1)
		else:
			gc.getTeam(self.m_iCurrentTeam).changeExtraWaterSeeFromCount( -gc.getTeam(self.m_iCurrentTeam).getExtraWaterSeeFromCount())
		return 1

	def handleTeamEditBridgeBuildingCB (self, argsList) :
		if int(argsList[0]):
			gc.getTeam(self.m_iCurrentTeam).changeBridgeBuildingCount(1)
		else:
			gc.getTeam(self.m_iCurrentTeam).changeBridgeBuildingCount( -gc.getTeam(self.m_iCurrentTeam).getBridgeBuildingCount())
		return 1

	def handleTeamEditIrrigationCB (self, argsList) :
		if int(argsList[0]):
			gc.getTeam(self.m_iCurrentTeam).changeIrrigationCount(1)
		else:
			gc.getTeam(self.m_iCurrentTeam).changeIrrigationCount( -gc.getTeam(self.m_iCurrentTeam).getIrrigationCount())
		return 1

	def handleTeamEditIgnoreIrrigationCB (self, argsList) :
		if int(argsList[0]):
			gc.getTeam(self.m_iCurrentTeam).changeIgnoreIrrigationCount(1)
		else:
			gc.getTeam(self.m_iCurrentTeam).changeIgnoreIrrigationCount( -gc.getTeam(self.m_iCurrentTeam).getIgnoreIrrigationCount())
		return 1

	def handleTeamEditForceTeamVoteCB (self, argsList) :
		iIndex, strName = argsList
		if int(iIndex):
			gc.getTeam(self.m_iCurrentTeam).changeForceTeamVoteEligibilityCount(int(strName), 1)
		else:
			gc.getTeam(self.m_iCurrentTeam).changeForceTeamVoteEligibilityCount(int(strName), - gc.getTeam(self.m_iCurrentTeam).getForceTeamVoteEligibilityCount(int(strName)))
		return 1

## Game Options ##

	def handleGameEditStartYearCB (self, argsList) :
		CyGame().setStartYear(int(argsList[0]))
		return 1

	def handleGameEditNukesExplodedCB (self, argsList) :
		CyGame().changeNukesExploded(int(argsList[0]) - CyGame().getNukesExploded())
		return 1

	def handleEditGameOptionCB (self, argsList) :
		iIndex, strName = argsList
		CyGame().setOption(int(strName), int(iIndex))
		if int(strName) == GameOptionTypes.GAMEOPTION_NO_GOODY_HUTS and iIndex:
			for i in xrange(CyMap().numPlots()):
				pPlot = CyMap().plotByIndex(i)
				if pPlot.isGoody():
					pPlot.setImprovementType(-1)
		elif int(strName) == GameOptionTypes.GAMEOPTION_NO_VASSAL_STATES and iIndex:
			for iTeamX in xrange(gc.getMAX_CIV_TEAMS()):
				pTeamX = gc.getTeam(iTeamX)
				for iTeamY in xrange(gc.getMAX_CIV_TEAMS()):
					pTeamX.freeVassal(iTeamY)
		elif int(strName) == GameOptionTypes.GAMEOPTION_ALWAYS_PEACE and iIndex:
			for iTeamX in xrange(gc.getMAX_CIV_TEAMS()):
				pTeamX = gc.getTeam(iTeamX)
				if CyGame().isOption(GameOptionTypes.GAMEOPTION_ALWAYS_WAR) and pTeamX.isHuman(): continue
				for iTeamY in xrange(gc.getMAX_CIV_TEAMS()):
					if CyGame().isOption(GameOptionTypes.GAMEOPTION_ALWAYS_WAR) and gc.getTeam(iTeamY).isHuman(): continue
					pTeamX.makePeace(iTeamY)
		elif int(strName) == GameOptionTypes.GAMEOPTION_ONE_CITY_CHALLENGE and iIndex:
			for iPlayerX in xrange(gc.getMAX_CIV_PLAYERS()):
				pPlayerX = gc.getPlayer(iPlayerX)
				if pPlayerX.isHuman():
					(loopCity, iter) = pPlayerX.firstCity(False)
					while(loopCity):
						if not loopCity.isCapital():
							loopCity.kill()
						(loopCity, iter) = pPlayerX.nextCity(iter, False)
		elif int(strName) == GameOptionTypes.GAMEOPTION_NO_BARBARIANS and iIndex:
			pPlayerBarb = gc.getPlayer(gc.getBARBARIAN_PLAYER ())
			(loopCity, iter) = pPlayerBarb.firstCity(False)
			while(loopCity):
				loopCity.kill()
				(loopCity, iter) = pPlayerBarb.nextCity(iter, False)
			(loopUnit, iter) = pPlayerBarb.firstUnit(False)
			while(loopUnit):
				loopUnit.kill(False, -1)
				(loopUnit, iter) = pPlayerBarb.nextUnit(iter, False)
		return 1

	def handleVisibleOptionsCB (self, argsList):
		iIndex, strName = argsList
		if strName == "ShowAll":
			self.m_iVisibleOption = 0
		elif strName == "ShowVisible":
			self.m_iVisibleOption = 1
		else:
			self.m_iVisibleOption = 2
		self.setGameOptionEditInfo()
		return 1

##MagisterModmod
	def handleGameEditScenarioCounterCB (self, argsList):
		CyGame().changeScenarioCounter(int(argsList[0]))
		return 1

	def handleGlobalCounterEditCB(self, argsList):
##		CyGame().changeGlobalCounter(-10000)#We need to make sure the global counter is 0 for change to equal set
		CyGame().changeGlobalCounter(int((argsList[0] -CyGame().getGlobalCounter())*CyGame().getGlobalCounterLimit()/100))
		return 1

	def handleHandicapEditPullDownCB(self, argsList):
		CyGame().setHandicapType(int(argsList[0]))
		return 1

##MagisterModmod

## Plot Data ##

	def handlePlotEditCultureCB (self, argsList) :
		self.m_pActivePlot.setCulture(self.m_iCurrentPlayer, int(argsList[0]), True)
		self.setPlotEditInfo(False)
		return 1

	def handlePlotEditYieldCB (self, argsList) :
		iIndex, strName = argsList
		if strName == "PlotEditFood":
			CyGame().setPlotExtraYield(self.m_pActivePlot.getX(), self.m_pActivePlot.getY(), YieldTypes.YIELD_FOOD, int(iIndex) - self.m_pActivePlot.getYield(YieldTypes.YIELD_FOOD))
		elif strName == "PlotEditProduction":
			CyGame().setPlotExtraYield(self.m_pActivePlot.getX(), self.m_pActivePlot.getY(), YieldTypes.YIELD_PRODUCTION, int(iIndex) - self.m_pActivePlot.getYield(YieldTypes.YIELD_PRODUCTION))
		else:
			CyGame().setPlotExtraYield(self.m_pActivePlot.getX(), self.m_pActivePlot.getY(), YieldTypes.YIELD_COMMERCE, int(iIndex) - self.m_pActivePlot.getYield(YieldTypes.YIELD_COMMERCE))
		return 1

	def handlePlotAddCityCB ( self, argsList ) :
		gc.getPlayer(self.m_iCurrentPlayer).initCity(self.m_pActivePlot.getX(), self.m_pActivePlot.getY())
		self.setPlotEditInfo(False)
		return 1

	def handlePlotEditPlotTypeCB ( self, argsList ) :
		iIndex = int(argsList[0])
		PlotType = [PlotTypes.PLOT_PEAK, PlotTypes.PLOT_HILLS, PlotTypes.PLOT_LAND, PlotTypes.PLOT_OCEAN]
		self.m_pActivePlot.setPlotType(PlotType[iIndex], True, True)
		self.setPlotEditInfo(False)
		return 1

	def handlePlotEditTerrainCB ( self, argsList ) :
		iIndex = int(argsList[0])
		iCount = 0
		for i in xrange(gc.getNumTerrainInfos()):
			if gc.getTerrainInfo(i).isGraphicalOnly(): continue
			if iCount == iIndex:
				self.m_pActivePlot.setTerrainType(i, True, True)
				self.setPlotEditInfo(False)
				return 1
			iCount += 1

	def handlePlotEditFeatureCB ( self, argsList ) :
		iIndex = int(argsList[0]) -1
		self.m_pActivePlot.setFeatureType(iIndex, 0)
		self.setPlotEditInfo(False)
		return 1

	def handlePlotEditVarietyCB ( self, argsList ) :
		self.m_pActivePlot.setFeatureType(self.m_pActivePlot.getFeatureType(), int(argsList[0]))
		return 1

	def handlePlotEditBonusCB ( self, argsList ) :
		self.m_pActivePlot.setBonusType(int(argsList[0]) - 1)
		self.setPlotEditInfo(False)
		return 1

	def handlePlotEditImprovementCB ( self, argsList ) :
		iIndex = int(argsList[0])
		if iIndex == 0:
			self.m_pActivePlot.setImprovementType(-1)
			self.setPlotEditInfo(False)
			return 1
		iCount = 1
		for i in xrange(gc.getNumImprovementInfos()):
			if gc.getImprovementInfo(i).isGraphicalOnly(): continue
			if iIndex == iCount:
				self.m_pActivePlot.setImprovementType(i)
				self.setPlotEditInfo(False)
				return 1
			iCount += 1

	def handlePlotEditUpgradeProgressCB ( self, argsList ) :
		iUpgradeTime = gc.getImprovementInfo(self.m_pActivePlot.getImprovementType()).getUpgradeTime()
		self.m_pActivePlot.setUpgradeProgress(iUpgradeTime - int(argsList[0]))
		return 1

	def handlePlotEditRouteCB ( self, argsList ) :
		self.m_pActivePlot.setRouteType(int(argsList[0]) - 1)
		self.setPlotEditInfo(False)
		return 1

	def handlePlotEditRiverCB ( self, argsList ) :
		iIndex, strName = argsList
		if strName == "NS":
			if iIndex == 0:
				self.m_pActivePlot.setWOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
			elif iIndex == 1:
				self.m_pActivePlot.setWOfRiver(True, CardinalDirectionTypes.NO_CARDINALDIRECTION)
			elif iIndex == 2:
				self.m_pActivePlot.setWOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_NORTH)
			elif iIndex == 3:
				self.m_pActivePlot.setWOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_SOUTH)
		else:
			if iIndex == 0:
				self.m_pActivePlot.setNOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
			elif iIndex == 1:
				self.m_pActivePlot.setWOfRiver(True, CardinalDirectionTypes.NO_CARDINALDIRECTION)
			elif iIndex == 2:
				self.m_pActivePlot.setNOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_EAST)
			elif iIndex == 3:
				self.m_pActivePlot.setNOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_WEST)
		return 1

	def handleEventOtherPlayerCB ( self, argsList ) :
		if int(argsList[0]) == 0:
			self.m_iOtherPlayer = -1
			self.setPlotEditInfo(False)
			return 1
		iCount = 1
		for i in xrange(gc.getMAX_CIV_PLAYERS()):
			if gc.getPlayer(i).isAlive():
				if i == self.m_iCurrentPlayer: continue
				if iCount == int(argsList[0]):
					self.m_iOtherPlayer = i
					self.setPlotEditInfo(False)
					return 1
				iCount = iCount + 1


	def handleEventUnitCB ( self, argsList ) :
		self.m_iEventUnit = int(argsList[0]) -1
		self.setPlotEditInfo(False)
		return 1

	def handleTriggerEventCB ( self, argsList ) :
		iCityID = -1
		pCity = CyMap().findCity(self.m_pActivePlot.getX(), self.m_pActivePlot.getY(), self.m_iCurrentPlayer, -1, False, False, -1, -1, CyCity())
		if not pCity.isNone():
			iCityID = pCity.getID()
		pPlayer = gc.getPlayer(self.m_iCurrentPlayer)
		iUnit = -1
		if self.m_iEventUnit > -1:
			iUnit = self.m_pActivePlot.getUnit(self.m_iEventUnit).getID()
		triggerData = pPlayer.initTriggeredData(int(argsList[0]) -1, True, iCityID, self.m_pActivePlot.getX(), self.m_pActivePlot.getY(), self.m_iOtherPlayer, -1, pPlayer.getStateReligion(), -1, iUnit, -1)
		self.setPlotEditInfo(False)

##MagisterModmod
	def handlePlotMoveDisabledAICB (self, argsList):
		self.m_pActivePlot.setMoveDisabledAI(int(argsList[0]))
		self.setPlotEditInfo(False)
		return 1

	def handlePlotMoveDisabledHumanCB (self, argsList):
		self.m_pActivePlot.setMoveDisabledHuman(int(argsList[0]))
		self.setPlotEditInfo(False)
		return 1

	def handlePlotBuildDisabledCB (self, argsList):
		self.m_pActivePlot.setBuildDisabled(int(argsList[0]))
		self.setPlotEditInfo(False)
		return 1

	def handlePlotFoundDisabledCB (self, argsList):
		self.m_pActivePlot.setFoundDisabled(int(argsList[0]))
		self.setPlotEditInfo(False)
		return 1

	def handlePlotPythonActiveCB (self, argsList):
		self.m_pActivePlot.setPythonActive(not int(argsList[0]))
		self.setPlotEditInfo(False)
		return 1

	def handlePlotCounterEditCB (self, argsList):
		self.m_pActivePlot.changePlotCounter(int(argsList[0]) - self.m_pActivePlot.getPlotCounter())
		self.setPlotEditInfo(False)
		return 1

	def handlePlotMinLevelCB(self, argsList):
		self.m_pActivePlot.setMinLevel(int(argsList[0]))
		self.setPlotEditInfo(False)
		return 1

	def handlePlotPortalExitXCB (self, argsList):
		self.m_pActivePlot.setPortalExitX(int(argsList[0]))
		return 1

	def handlePlotPortalExitYCB (self, argsList):
		self.m_pActivePlot.setPortalExitY(int(argsList[0]))
		return 1
##MagisterModmod

## Platy World Builder End ##

	def handleCityEditNameCB (self, argsList) :
		if ((len(argsList[0]) < 1) or (not self.m_pActivePlot.isCity())):
			return 1
		szNewName = argsList[0]
		city = self.m_pActivePlot.getPlotCity()
		if (city):
			city.setName(szNewName, False)
		return 1

	def handleUnitEditPullDownCB ( self, argsList ) :
		self.m_iCurrentUnit = int(argsList[0])
		self.setUnitEditInfo(True)
		return 1

	def handleUnitAITypeEditPullDownCB ( self, argsList ) :
		self.m_pActivePlot.getUnit(self.m_iCurrentUnit).setUnitAIType(int(argsList[0]))
		return 1

##MagisterModmod
	def handleUnitReligionEditPullDownCB ( self, argsList ) :
		self.m_pActivePlot.getUnit(self.m_iCurrentUnit).setReligion(int(argsList[0]-1))
		return 1
##MagisterModmod

## Platy World Builder Start ##
	def handlePlayerUnitPullDownCB ( self, argsList ) :
		iIndex = int(argsList)
		iCount = 0
		for i in xrange( gc.getMAX_PLAYERS() ):
			if gc.getPlayer(i).isEverAlive():
				if iCount == iIndex:
					self.m_iCurrentPlayer = i
					self.m_iCurrentTeam = gc.getPlayer(i).getTeam()
					self.refreshSideMenu()
					self.refreshPlayerTabCtrl()
					return 1
				iCount += 1
## Platy World Builder End ##

	def handleSelectTeamPullDownCB ( self, argsList ) :
		iIndex = int(argsList)
		iCount = -1
		for i in xrange( gc.getMAX_CIV_TEAMS() ):
			if gc.getTeam(i).isAlive():
				iCount = iCount + 1
				if (iCount == iIndex):
					self.m_iCurrentTeam = i
		self.refreshReveal()
		return 1

	def hasPromotion(self, iPromotion):
		return self.m_pActivePlot.getUnit(self.m_iCurrentUnit).isHasPromotion(iPromotion)

	def hasTech(self, iTech):
		return gc.getTeam(gc.getPlayer(self.m_iCurrentPlayer).getTeam()).isHasTech(iTech)

	def handleTechCB (self, argsList) :
		bOn, strName = argsList
		if ((strName.find("_") != -1) and (self.m_iCurrentPlayer >= 0)):
			iTech = int(strName[strName.find("_")+1:])
			gc.getTeam(gc.getPlayer(self.m_iCurrentPlayer).getTeam()).setHasTech(iTech, bOn, self.m_iCurrentPlayer, False, False)
			self.resetTechButtons()
		return 1

## Platy Brush Size ##
	def handleBrushSizeCB (self, argsList):
		self.m_iBrushSize = int(argsList) + 1
		return 1
## Platy Brush Size ##

	def handleLandmarkCB (self, argsList):
		return 1

	########################################################
	### Advanced Start Stuff
	########################################################

	def refreshASItemCost(self):

		if (CyInterface().isInAdvancedStart()):

			self.m_iCost = 0

			if (self.m_pCurrentPlot != 0):
				if (self.m_pCurrentPlot.isRevealed(CyGame().getActiveTeam(), False)):

					# Unit mode
					if (self.getASActiveUnit() != -1):
						self.m_iCost = gc.getPlayer(self.m_iCurrentPlayer).getAdvancedStartUnitCost(self.getASActiveUnit(), True, self.m_pCurrentPlot)
					elif (self.getASActiveCity() != -1):
						self.m_iCost = gc.getPlayer(self.m_iCurrentPlayer).getAdvancedStartCityCost(True, self.m_pCurrentPlot)
					elif (self.getASActivePop() != -1 and self.m_pCurrentPlot.isCity()):
						self.m_iCost = gc.getPlayer(self.m_iCurrentPlayer).getAdvancedStartPopCost(True, self.m_pCurrentPlot.getPlotCity())
					elif (self.getASActiveCulture() != -1 and self.m_pCurrentPlot.isCity()):
						self.m_iCost = gc.getPlayer(self.m_iCurrentPlayer).getAdvancedStartCultureCost(True, self.m_pCurrentPlot.getPlotCity())
					elif (self.getASActiveBuilding() != -1 and self.m_pCurrentPlot.isCity()):
						self.m_iCost = gc.getPlayer(self.m_iCurrentPlayer).getAdvancedStartBuildingCost(self.getASActiveBuilding(), True, self.m_pCurrentPlot.getPlotCity())
					elif (self.getASActiveRoute() != -1):
						self.m_iCost = gc.getPlayer(self.m_iCurrentPlayer).getAdvancedStartRouteCost(self.getASActiveRoute(), True, self.m_pCurrentPlot)
					elif (self.getASActiveImprovement() != -1):
						self.m_iCost = gc.getPlayer(self.m_iCurrentPlayer).getAdvancedStartImprovementCost(self.getASActiveImprovement(), True, self.m_pCurrentPlot)

				elif (self.m_pCurrentPlot.isAdjacentNonrevealed(CyGame().getActiveTeam())):
					if (self.getASActiveVisibility() != -1):
						self.m_iCost = gc.getPlayer(self.m_iCurrentPlayer).getAdvancedStartVisibilityCost(True, self.m_pCurrentPlot)

			if (self.m_iCost < 0):
				self.m_iCost = 0

			self.refreshSideMenu()

	def getASActiveUnit(self):
		# Unit Tab
		if (self.m_advancedStartTabCtrl.getActiveTab() == self.m_iASUnitTabID):
			iUnitType = getASUnit(self.m_iAdvancedStartCurrentIndexes[self.m_advancedStartTabCtrl.getActiveTab()])
			return iUnitType

		return -1

	def getASActiveCity(self):
		# City Tab
		if (self.m_advancedStartTabCtrl.getActiveTab() == self.m_iASCityTabID):
			# City List
			if (self.m_iAdvancedStartCurrentList[self.m_advancedStartTabCtrl.getActiveTab()] == self.m_iASCityListID):
				iOptionID = self.m_iAdvancedStartCurrentIndexes[self.m_advancedStartTabCtrl.getActiveTab()]
				# Place City
				if (iOptionID == 0):
					return 1

		return -1

	def getASActivePop(self):
		# City Tab
		if (self.m_advancedStartTabCtrl.getActiveTab() == self.m_iASCityTabID):
			# City List
			if (self.m_iAdvancedStartCurrentList[self.m_advancedStartTabCtrl.getActiveTab()] == self.m_iASCityListID):
				iOptionID = self.m_iAdvancedStartCurrentIndexes[self.m_advancedStartTabCtrl.getActiveTab()]
				# Place Pop
				if (iOptionID == 1):
					return 1

		return -1

	def getASActiveCulture(self):
		# City Tab
		if (self.m_advancedStartTabCtrl.getActiveTab() == self.m_iASCityTabID):
			# City List
			if (self.m_iAdvancedStartCurrentList[self.m_advancedStartTabCtrl.getActiveTab()] == self.m_iASCityListID):
				iOptionID = self.m_iAdvancedStartCurrentIndexes[self.m_advancedStartTabCtrl.getActiveTab()]
				# Place Culture
				if (iOptionID == 2):
					return 1

		return -1

	def getASActiveBuilding(self):
		# Building Tab
		if (self.m_advancedStartTabCtrl.getActiveTab() == self.m_iASCityTabID):
			# Buildings List
			if (self.m_iAdvancedStartCurrentList[self.m_advancedStartTabCtrl.getActiveTab()] == self.m_iASBuildingsListID):
				iBuildingType = getASBuilding(self.m_iAdvancedStartCurrentIndexes[self.m_advancedStartTabCtrl.getActiveTab()])
				return iBuildingType

		return -1

	def getASActiveRoute(self):
		# Improvements Tab
		if (self.m_advancedStartTabCtrl.getActiveTab() == self.m_iASImprovementsTabID):
			# Routes List
			if (self.m_iAdvancedStartCurrentList[self.m_advancedStartTabCtrl.getActiveTab()] == self.m_iASRoutesListID):
				iRouteType = getASRoute(self.m_iAdvancedStartCurrentIndexes[self.m_advancedStartTabCtrl.getActiveTab()])
				if -1 == iRouteType:
					self.m_iAdvancedStartCurrentList[self.m_advancedStartTabCtrl.getActiveTab()] = self.m_iASImprovementsListID
				return iRouteType

		return -1

	def getASActiveImprovement(self):
		# Improvements Tab
		if (self.m_advancedStartTabCtrl.getActiveTab() == self.m_iASImprovementsTabID):
			# Improvements List
			if (self.m_iAdvancedStartCurrentList[self.m_advancedStartTabCtrl.getActiveTab()] == self.m_iASImprovementsListID):
				iImprovementType = getASImprovement(self.m_iAdvancedStartCurrentIndexes[self.m_advancedStartTabCtrl.getActiveTab()])
				if -1 == iImprovementType:
					self.m_iAdvancedStartCurrentList[self.m_advancedStartTabCtrl.getActiveTab()] = self.m_iASRoutesListID
				return iImprovementType

		return -1

	def getASActiveVisibility(self):
		# Visibility Tab
		if (self.m_advancedStartTabCtrl.getActiveTab() == self.m_iASVisibilityTabID):
			return 1

		return -1

	def getASActiveTech(self):
		# Tech Tab
		if (self.m_advancedStartTabCtrl.getActiveTab() == self.m_iASTechTabID):
			return 1

		return -1

	def placeObject( self ) :
		# Advanced Start
		if (CyInterface().isInAdvancedStart()):

			pPlayer = gc.getPlayer(self.m_iCurrentPlayer)
			pPlot = CyMap().plot(self.m_iCurrentX, self.m_iCurrentY)

			iActiveTeam = CyGame().getActiveTeam()
			if (self.m_pCurrentPlot.isRevealed(iActiveTeam, False)):

				# City Tab
				if (self.m_advancedStartTabCtrl.getActiveTab() == self.m_iASCityTabID):

					# City List
					if (self.m_iAdvancedStartCurrentList[self.m_advancedStartTabCtrl.getActiveTab()] == self.m_iASCityListID):

						iOptionID = self.m_iAdvancedStartCurrentIndexes[self.m_advancedStartTabCtrl.getActiveTab()]

						# Place City
						if (iOptionID == 0):

							# Cost -1 means may not be placed here
							if (pPlayer.getAdvancedStartCityCost(True, pPlot) != -1):

								CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_CITY, self.m_iCurrentPlayer, self.m_iCurrentX, self.m_iCurrentY, -1, True)	#Action, Player, X, Y, Data, bAdd

						# City Population
						elif (iOptionID == 1):

							if (pPlot.isCity()):
								pCity = pPlot.getPlotCity()

								# Cost -1 means may not be placed here
								if (pPlayer.getAdvancedStartPopCost(True, pCity) != -1):

										CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_POP, self.m_iCurrentPlayer, self.m_iCurrentX, self.m_iCurrentY, -1, True)	#Action, Player, X, Y, Data, bAdd

						# City Culture
						elif (iOptionID == 2):

							if (pPlot.isCity()):
								pCity = pPlot.getPlotCity()

								# Cost -1 means may not be placed here
								if (pPlayer.getAdvancedStartCultureCost(True, pCity) != -1):

									CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_CULTURE, self.m_iCurrentPlayer, self.m_iCurrentX, self.m_iCurrentY, -1, True)	#Action, Player, X, Y, Data, bAdd

					# Buildings List
					elif (self.m_iAdvancedStartCurrentList[self.m_advancedStartTabCtrl.getActiveTab()] == self.m_iASBuildingsListID):

							if (pPlot.isCity()):
								pCity = pPlot.getPlotCity()

								iBuildingType = getASBuilding(self.m_iAdvancedStartCurrentIndexes[self.m_advancedStartTabCtrl.getActiveTab()])

								# Cost -1 means may not be placed here
								if (iBuildingType != -1 and pPlayer.getAdvancedStartBuildingCost(iBuildingType, True, pCity) != -1):

									CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_BUILDING, self.m_iCurrentPlayer, self.m_iCurrentX, self.m_iCurrentY, iBuildingType, True)	#Action, Player, X, Y, Data, bAdd

				# Unit Tab
				elif (self.m_advancedStartTabCtrl.getActiveTab() == self.m_iASUnitTabID):
					iUnitType = getASUnit(self.m_iAdvancedStartCurrentIndexes[self.m_advancedStartTabCtrl.getActiveTab()])

					# Cost -1 means may not be placed here
					if (iUnitType != -1 and pPlayer.getAdvancedStartUnitCost(iUnitType, True, pPlot) != -1):

						CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_UNIT, self.m_iCurrentPlayer, self.m_iCurrentX, self.m_iCurrentY, iUnitType, True)	#Action, Player, X, Y, Data, bAdd

				# Improvements Tab
				elif (self.m_advancedStartTabCtrl.getActiveTab() == self.m_iASImprovementsTabID):

					# Routes List
					if (self.m_iAdvancedStartCurrentList[self.m_advancedStartTabCtrl.getActiveTab()] == self.m_iASRoutesListID):

						iRouteType = getASRoute(self.m_iAdvancedStartCurrentIndexes[self.m_advancedStartTabCtrl.getActiveTab()])

						# Cost -1 means may not be placed here
						if (iRouteType != -1 and pPlayer.getAdvancedStartRouteCost(iRouteType, True, pPlot) != -1):

							CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_ROUTE, self.m_iCurrentPlayer, self.m_iCurrentX, self.m_iCurrentY, iRouteType, True)	#Action, Player, X, Y, Data, bAdd

					# Improvements List
					elif (self.m_iAdvancedStartCurrentList[self.m_advancedStartTabCtrl.getActiveTab()] == self.m_iASImprovementsListID):

						iImprovementType = getASImprovement(self.m_iAdvancedStartCurrentIndexes[self.m_advancedStartTabCtrl.getActiveTab()])

						# Cost -1 means may not be placed here
						if (pPlayer.getAdvancedStartImprovementCost(iImprovementType, True, pPlot) != -1):

							CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_IMPROVEMENT, self.m_iCurrentPlayer, self.m_iCurrentX, self.m_iCurrentY, iImprovementType, True)	#Action, Player, X, Y, Data, bAdd

			# Adjacent nonrevealed
			else:

				# Visibility Tab
				if (self.m_advancedStartTabCtrl.getActiveTab() == self.m_iASVisibilityTabID):

					# Cost -1 means may not be placed here
					if (pPlayer.getAdvancedStartVisibilityCost(True, pPlot) != -1):

						CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_VISIBILITY, self.m_iCurrentPlayer, self.m_iCurrentX, self.m_iCurrentY, -1, True)	#Action, Player, X, Y, Data, bAdd

			self.m_bSideMenuDirty = True
			self.m_bASItemCostDirty = True

			return 1

		if ((self.m_iNormalPlayerCurrentIndexes[self.m_normalPlayerTabCtrl.getActiveTab()] == -1) or (self.m_iNormalMapCurrentIndexes[self.m_normalMapTabCtrl.getActiveTab()] == -1) or (self.m_iCurrentX == -1) or (self.m_iCurrentY == -1) or (self.m_iCurrentPlayer == -1)):
			return 1

		if (self.m_bEraseAll):
			self.eraseAll()
		elif ((self.m_bNormalPlayer) and (self.m_normalPlayerTabCtrl.getActiveTab() == self.m_iUnitTabID)):
			iUnitType = self.m_iNormalPlayerCurrentIndexes[self.m_normalPlayerTabCtrl.getActiveTab()]
			pPlayer = gc.getPlayer(self.m_iCurrentPlayer)
			iPlotX = self.m_iCurrentX
			iPlotY = self.m_iCurrentY
			pPlayer.initUnit(iUnitType, iPlotX, iPlotY, UnitAITypes.NO_UNITAI, DirectionTypes.NO_DIRECTION)
		elif ((self.m_bNormalPlayer) and (self.m_normalPlayerTabCtrl.getActiveTab() == self.m_iBuildingTabID)):
			iBuildingType = self.m_iNormalPlayerCurrentIndexes[self.m_normalPlayerTabCtrl.getActiveTab()]
			if ((self.m_pCurrentPlot.isCity()) and (iBuildingType != 0)):
				self.m_pCurrentPlot.getPlotCity().setNumRealBuilding(iBuildingType-1, 1)
			if (iBuildingType == 0):
				if (not self.m_pCurrentPlot.isCity()):
					pPlayer = gc.getPlayer(self.m_iCurrentPlayer)
					iX = self.m_pCurrentPlot.getX()
					iY = self.m_pCurrentPlot.getY()
					pPlayer.initCity(iX, iY)
		elif ((self.m_bNormalMap) and (self.m_normalMapTabCtrl.getActiveTab() == self.m_iImprovementTabID)):
			iImprovementType = self.m_iNormalMapCurrentIndexes[self.m_normalMapTabCtrl.getActiveTab()]
			iIndex = -1
			iCounter = -1
			while ((iIndex < iImprovementType) and (iCounter < gc.getNumImprovementInfos())):
				iCounter = iCounter + 1
				if (not gc.getImprovementInfo(iCounter).isGraphicalOnly()):
					iIndex = iIndex + 1
			if (iIndex > -1):
				self.m_pCurrentPlot.setImprovementType(iCounter)
		elif ((self.m_bNormalMap) and (self.m_normalMapTabCtrl.getActiveTab() == self.m_iBonusTabID)):
			iBonusType = self.m_iNormalMapCurrentIndexes[self.m_normalMapTabCtrl.getActiveTab()]
			self.m_pCurrentPlot.setBonusType(iBonusType)
		elif ((self.m_bNormalMap) and (self.m_normalMapTabCtrl.getActiveTab() == self.m_iTerrainTabID)):
			if (self.m_iNormalMapCurrentList[self.m_normalMapTabCtrl.getActiveTab()] == self.m_iTerrainListID):
				iTerrainType = self.m_iNormalMapCurrentIndexes[self.m_normalMapTabCtrl.getActiveTab()]
				self.m_pCurrentPlot.setTerrainType(iTerrainType, True, True)
			elif (self.m_iNormalMapCurrentList[self.m_normalMapTabCtrl.getActiveTab()] == self.m_iFeatureListID):
				iButtonIndex = self.m_iNormalMapCurrentIndexes[self.m_normalMapTabCtrl.getActiveTab()]
				iCount = -1
				for i in range (gc.getNumFeatureInfos()):
					for j in range (gc.getFeatureInfo(i).getNumVarieties()):
						iCount = iCount + 1
						if (iCount == iButtonIndex):
							self.m_pCurrentPlot.setFeatureType(i, j)
			elif (self.m_iNormalMapCurrentList[self.m_normalMapTabCtrl.getActiveTab()] == self.m_iPlotTypeListID):
				iPlotType = self.m_iNormalMapCurrentIndexes[self.m_normalMapTabCtrl.getActiveTab()]
				if (iPlotType >= 0) and (iPlotType < PlotTypes.NUM_PLOT_TYPES):
					self.m_pCurrentPlot.setPlotType(PlotTypes(iPlotType), True, True)
			elif (self.m_iNormalMapCurrentList[self.m_normalMapTabCtrl.getActiveTab()] == self.m_iRouteListID):
				iRouteType = self.m_iNormalMapCurrentIndexes[self.m_normalMapTabCtrl.getActiveTab()]
				if (iRouteType == gc.getNumRouteInfos()):
					if (self.m_pRiverStartPlot == self.m_pCurrentPlot):
						self.m_pRiverStartPlot = -1
						CyEngine().clearColoredPlots(PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS)
						return 1
					if (self.m_pRiverStartPlot != -1):
						iXDiff = 0
						iYDiff = 0
						if (self.m_pRiverStartPlot.getX() < self.m_pCurrentPlot.getX()):
							iXDiff = self.m_pCurrentPlot.getX() - self.m_pRiverStartPlot.getX()
						elif (self.m_pRiverStartPlot.getX() > self.m_pCurrentPlot.getX()):
							iXDiff = self.m_pRiverStartPlot.getX() - self.m_pCurrentPlot.getX()
						if (self.m_pRiverStartPlot.getY() < self.m_pCurrentPlot.getY()):
							iYDiff = self.m_pCurrentPlot.getY() - self.m_pRiverStartPlot.getY()
						elif (self.m_pRiverStartPlot.getY() > self.m_pCurrentPlot.getY()):
							iYDiff = self.m_pRiverStartPlot.getY() - self.m_pCurrentPlot.getY()

						if ((iXDiff == iYDiff) and (iXDiff == 1) and (self.m_pRiverStartPlot.getX() > self.m_pCurrentPlot.getX()) and (self.m_pRiverStartPlot.getY() < self.m_pCurrentPlot.getY())):
							self.placeRiverNW(True)
							self.m_pRiverStartPlot = CyMap().plot(self.m_pRiverStartPlot.getX()-1, self.m_pRiverStartPlot.getY()+1)
						elif ((iXDiff == 0) and (iYDiff == 1) and (self.m_pRiverStartPlot.getY() < self.m_pCurrentPlot.getY())):
							self.placeRiverN(True)
							self.m_pRiverStartPlot = self.m_pCurrentPlot
						elif ((iXDiff == iYDiff) and (iXDiff == 1) and (self.m_pRiverStartPlot.getX() < self.m_pCurrentPlot.getX()) and (self.m_pRiverStartPlot.getY() < self.m_pCurrentPlot.getY())):
							self.placeRiverNE(True)
							self.m_pRiverStartPlot = self.m_pCurrentPlot
						elif ((iXDiff == 1) and (iYDiff == 0) and (self.m_pRiverStartPlot.getX() > self.m_pCurrentPlot.getX())):
							self.placeRiverW(True)
							self.m_pRiverStartPlot = self.m_pCurrentPlot
						elif ((iXDiff == 1) and (iYDiff == 0) and (self.m_pRiverStartPlot.getX() < self.m_pCurrentPlot.getX())):
							self.placeRiverE(True)
							self.m_pRiverStartPlot = self.m_pCurrentPlot
						elif ((iXDiff == iYDiff) and (iXDiff == 1) and (self.m_pRiverStartPlot.getX() > self.m_pCurrentPlot.getX()) and (self.m_pRiverStartPlot.getY() > self.m_pCurrentPlot.getY())):
							self.placeRiverSW(True)
							self.m_pRiverStartPlot = self.m_pCurrentPlot
						elif ((iXDiff == 0) and (iYDiff == 1) and (self.m_pRiverStartPlot.getY() > self.m_pCurrentPlot.getY())):
							self.placeRiverS(True)
							self.m_pRiverStartPlot = self.m_pCurrentPlot
						elif ((iXDiff == iYDiff) and (iXDiff == 1) and (self.m_pRiverStartPlot.getX() < self.m_pCurrentPlot.getX()) and (self.m_pRiverStartPlot.getY() > self.m_pCurrentPlot.getY())):
							self.placeRiverSE(True)
							self.m_pRiverStartPlot = self.m_pCurrentPlot
						else:
							self.m_pRiverStartPlot = self.m_pCurrentPlot
					else:
						self.m_pRiverStartPlot = self.m_pCurrentPlot
				else:
					self.m_pCurrentPlot.setRouteType(iRouteType)
		elif ((self.m_bNormalMap) and (self.m_normalMapTabCtrl.getActiveTab() == self.m_iTerritoryTabID)):
			iPlayer = self.m_iNormalMapCurrentIndexes[self.m_normalMapTabCtrl.getActiveTab()]
			if (gc.getPlayer(iPlayer).isEverAlive()):
				self.m_pCurrentPlot.setOwner(iPlayer)
		elif (self.m_bLandmark):
			CvEventInterface.beginEvent(CvUtil.EventWBLandmarkPopup)
		return 1

	def removeObject( self ):

		# Advanced Start
		if (CyInterface().isInAdvancedStart()):

			pPlayer = gc.getPlayer(self.m_iCurrentPlayer)
			pPlot = CyMap().plot(self.m_iCurrentX, self.m_iCurrentY)

			iActiveTeam = CyGame().getActiveTeam()
			if (self.m_pCurrentPlot.isRevealed(iActiveTeam, False)):

				# City Tab
				if (self.m_advancedStartTabCtrl.getActiveTab() == self.m_iASCityTabID):

					# City List
					if (self.m_iAdvancedStartCurrentList[self.m_advancedStartTabCtrl.getActiveTab()] == self.m_iASCityListID):

						iOptionID = self.m_iAdvancedStartCurrentIndexes[self.m_advancedStartTabCtrl.getActiveTab()]

						# Place City
						if (iOptionID == 0):

							# Ability to remove cities not allowed because of 'sploitz (visibility, chopping down jungle, etc.)
							return 1

							if (self.m_pCurrentPlot.isCity()):

								if (self.m_pCurrentPlot.getPlotCity().getOwner() == self.m_iCurrentPlayer):

									CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_CITY, self.m_iCurrentPlayer, self.m_iCurrentX, self.m_iCurrentY, -1, False)	#Action, Player, X, Y, Data, bAdd

						# City Population
						elif (iOptionID == 1):

							if (pPlot.isCity()):
								if (pPlot.getPlotCity().getOwner() == self.m_iCurrentPlayer):

									CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_POP, self.m_iCurrentPlayer, self.m_iCurrentX, self.m_iCurrentY, -1, False)	#Action, Player, X, Y, Data, bAdd

						# City Culture
						elif (iOptionID == 2):

							# Ability to remove cities not allowed because of 'sploitz (visibility)
							return 1

							if (pPlot.isCity()):
								if (pPlot.getPlotCity().getOwner() == self.m_iCurrentPlayer):

									CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_CULTURE, self.m_iCurrentPlayer, self.m_iCurrentX, self.m_iCurrentY, -1, False)	#Action, Player, X, Y, Data, bAdd

					# Buildings List
					elif (self.m_iAdvancedStartCurrentList[self.m_advancedStartTabCtrl.getActiveTab()] == self.m_iASBuildingsListID):

						if (pPlot.isCity()):
							if (pPlot.getPlotCity().getOwner() == self.m_iCurrentPlayer):

								iBuildingType = getASBuilding(self.m_iAdvancedStartCurrentIndexes[self.m_advancedStartTabCtrl.getActiveTab()])

								if -1 != iBuildingType:
									CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_BUILDING, self.m_iCurrentPlayer, self.m_iCurrentX, self.m_iCurrentY, iBuildingType, False)	#Action, Player, X, Y, Data, bAdd

				# Unit Tab
				elif (self.m_advancedStartTabCtrl.getActiveTab() == self.m_iASUnitTabID):

					iUnitType = getASUnit(self.m_iAdvancedStartCurrentIndexes[self.m_advancedStartTabCtrl.getActiveTab()])

					if -1 != iUnitType:
						CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_UNIT, self.m_iCurrentPlayer, self.m_pCurrentPlot.getX(), self.m_pCurrentPlot.getY(), iUnitType, False)	#Action, Player, X, Y, Data, bAdd

				# Improvements Tab
				elif (self.m_advancedStartTabCtrl.getActiveTab() == self.m_iASImprovementsTabID):

					# Routes List
					if (self.m_iAdvancedStartCurrentList[self.m_advancedStartTabCtrl.getActiveTab()] == self.m_iASRoutesListID):

						iRouteType = getASRoute(self.m_iAdvancedStartCurrentIndexes[self.m_advancedStartTabCtrl.getActiveTab()])

						if -1 != iRouteType:
							CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_ROUTE, self.m_iCurrentPlayer, self.m_iCurrentX, self.m_iCurrentY, iRouteType, False)	#Action, Player, X, Y, Data, bAdd

					# Improvements List
					elif (self.m_iAdvancedStartCurrentList[self.m_advancedStartTabCtrl.getActiveTab()] == self.m_iASImprovementsListID):

						iImprovementType = getASImprovement(self.m_iAdvancedStartCurrentIndexes[self.m_advancedStartTabCtrl.getActiveTab()])

						if -1 != iImprovementType:
							CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_IMPROVEMENT, self.m_iCurrentPlayer, self.m_iCurrentX, self.m_iCurrentY, iImprovementType, False)	#Action, Player, X, Y, Data, bAdd

			# Adjacent nonrevealed
			else:

				# Visibility Tab
				if (self.m_advancedStartTabCtrl.getActiveTab() == self.m_iASVisibilityTabID):

					# Ability to remove sight not allowed because of 'sploitz
					return 1

					# Remove Visibility
					if (pPlot.isRevealed(iActiveTeam, False)):

						CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_VISIBILITY, self.m_iCurrentPlayer, self.m_iCurrentX, self.m_iCurrentY, -1, False)	#Action, Player, X, Y, Data, bAdd

			self.m_bSideMenuDirty = True
			self.m_bASItemCostDirty = True

			return 1

		if ((self.m_iNormalPlayerCurrentIndexes[self.m_normalPlayerTabCtrl.getActiveTab()] == -1) or (self.m_iNormalMapCurrentIndexes[self.m_normalMapTabCtrl.getActiveTab()] == -1) or (self.m_iCurrentX == -1) or (self.m_iCurrentY == -1) or (self.m_iCurrentPlayer == -1)):
			return 1

		if (self.m_bEraseAll):
			self.eraseAll()
		elif ((self.m_bNormalPlayer) and (self.m_normalPlayerTabCtrl.getActiveTab() == self.m_iUnitTabID)):
			for i in range (self.m_pCurrentPlot.getNumUnits()):
				pUnit = self.m_pCurrentPlot.getUnit(i)
				if (pUnit.getUnitType() == self.m_iNormalPlayerCurrentIndexes[self.m_normalPlayerTabCtrl.getActiveTab()]):
					pUnit.kill(False, PlayerTypes.NO_PLAYER)
					return 1
			if (self.m_pCurrentPlot.getNumUnits() > 0):
				pUnit = self.m_pCurrentPlot.getUnit(0)
				pUnit.kill(False, PlayerTypes.NO_PLAYER)
				return 1
		elif ((self.m_bNormalPlayer) and (self.m_normalPlayerTabCtrl.getActiveTab() == self.m_iBuildingTabID)):
			if (self.m_pCurrentPlot.isCity()):
				iBuildingType = self.m_iNormalPlayerCurrentIndexes[self.m_normalPlayerTabCtrl.getActiveTab()]
				if (iBuildingType == 0) :
					self.m_pCurrentPlot.getPlotCity().kill()
				else:
					self.m_pCurrentPlot.getPlotCity().setNumRealBuilding(iBuildingType-1, 0)
		elif ((self.m_bNormalMap) and (self.m_normalMapTabCtrl.getActiveTab() == self.m_iImprovementTabID)):
			self.m_pCurrentPlot.setImprovementType(-1)
			return 1
		elif ((self.m_bNormalMap) and (self.m_normalMapTabCtrl.getActiveTab() == self.m_iBonusTabID)):
			iBonusType = self.m_iNormalMapCurrentIndexes[self.m_normalMapTabCtrl.getActiveTab()]
			self.m_pCurrentPlot.setBonusType(-1)
			return 1
		elif ((self.m_bNormalMap) and (self.m_normalMapTabCtrl.getActiveTab() == self.m_iTerrainTabID)):
			if (self.m_iNormalMapCurrentList[self.m_normalMapTabCtrl.getActiveTab()] == self.m_iTerrainListID):
				return 1
			elif (self.m_iNormalMapCurrentList[self.m_normalMapTabCtrl.getActiveTab()] == self.m_iFeatureListID):
				iFeatureType = self.m_iNormalMapCurrentIndexes[self.m_normalMapTabCtrl.getActiveTab()]
				self.m_pCurrentPlot.setFeatureType(FeatureTypes.NO_FEATURE, -1)
				return 1
			elif (self.m_iNormalMapCurrentList[self.m_normalMapTabCtrl.getActiveTab()] == self.m_iPlotTypeListID):
				return 1
			elif (self.m_iNormalMapCurrentList[self.m_normalMapTabCtrl.getActiveTab()] == self.m_iRouteListID):
				iRouteType = self.m_iNormalMapCurrentIndexes[self.m_normalMapTabCtrl.getActiveTab()]
				if (iRouteType == gc.getNumRouteInfos()):
					if (self.m_pRiverStartPlot != -1):
						self.m_pRiverStartPlot = -1
						CyEngine().clearColoredPlots(PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS)
					else:
						self.m_pCurrentPlot.setNOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
						self.m_pCurrentPlot.setWOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
				else:
					self.m_pCurrentPlot.setRouteType(-1)
		elif ((self.m_bNormalMap) and (self.m_normalMapTabCtrl.getActiveTab() == self.m_iTerritoryTabID)):
			self.m_pCurrentPlot.setOwner(-1)
			return 1
		elif (self.m_bLandmark):
			self.removeLandmarkCB()
		return 1

	def handleClicked( self ):
		return

	def isIntString ( self, arg ):
		for i in range (len(arg)):
			if (arg[i] > '9') :
				return False
			elif (arg[i] < '0') :
				return False
		return True

	def placeRiverNW ( self, bUseCurrent ):
		if (bUseCurrent):
			pRiverStepPlot = CyMap().plot(self.m_pRiverStartPlot.getX(), self.m_pRiverStartPlot.getY())
			if (not pRiverStepPlot.isNone()):
				pRiverStepPlot.setNOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_WEST)

		pRiverStepPlot = CyMap().plot(self.m_pRiverStartPlot.getX()-1, self.m_pRiverStartPlot.getY())
		if (not pRiverStepPlot.isNone()):
			pRiverStepPlot.setWOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_NORTH)
		pRiverStepPlot = CyMap().plot(self.m_pRiverStartPlot.getX()-1, self.m_pRiverStartPlot.getY()+1)
		if (not pRiverStepPlot.isNone()):
			pRiverStepPlot.setWOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_NORTH)
		return

	def placeRiverN ( self, bUseCurrent ):
		if (bUseCurrent):
			pRiverStepPlot = CyMap().plot(self.m_pRiverStartPlot.getX(), self.m_pRiverStartPlot.getY())
			if (not pRiverStepPlot.isNone()):
				pRiverStepPlot.setWOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_NORTH)

		pRiverStepPlot = CyMap().plot(self.m_pRiverStartPlot.getX(), self.m_pRiverStartPlot.getY()+1)
		if (not pRiverStepPlot.isNone()):
			pRiverStepPlot.setWOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_NORTH)
		return

	def placeRiverNE ( self, bUseCurrent ):
		if (bUseCurrent):
			pRiverStepPlot = CyMap().plot(self.m_pRiverStartPlot.getX(), self.m_pRiverStartPlot.getY())
			if (not pRiverStepPlot.isNone()):
				pRiverStepPlot.setNOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_EAST)

		pRiverStepPlot = CyMap().plot(self.m_pRiverStartPlot.getX()+1, self.m_pRiverStartPlot.getY())
		if (not pRiverStepPlot.isNone()):
			pRiverStepPlot.setNOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_EAST)
			pRiverStepPlot.setWOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_NORTH)
		pRiverStepPlot = CyMap().plot(self.m_pRiverStartPlot.getX()+1, self.m_pRiverStartPlot.getY()+1)
		if (not pRiverStepPlot.isNone()):
			pRiverStepPlot.setWOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_NORTH)
		return

	def placeRiverW ( self, bUseCurrent ):
		if (bUseCurrent):
			pRiverStepPlot = CyMap().plot(self.m_pRiverStartPlot.getX(), self.m_pRiverStartPlot.getY())
			if (not pRiverStepPlot.isNone()):
				pRiverStepPlot.setNOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_WEST)

		pRiverStepPlot = CyMap().plot(self.m_pRiverStartPlot.getX()-1, self.m_pRiverStartPlot.getY())
		if (not pRiverStepPlot.isNone()):
			pRiverStepPlot.setNOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_WEST)
		return

	def placeRiverE ( self, bUseCurrent ):
		if (bUseCurrent):
			pRiverStepPlot = CyMap().plot(self.m_pRiverStartPlot.getX(), self.m_pRiverStartPlot.getY())
			if (not pRiverStepPlot.isNone()):
				pRiverStepPlot.setNOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_EAST)

		pRiverStepPlot = CyMap().plot(self.m_pRiverStartPlot.getX()+1, self.m_pRiverStartPlot.getY())
		if (not pRiverStepPlot.isNone()):
			pRiverStepPlot.setNOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_EAST)
		return

	def placeRiverSW ( self, bUseCurrent ):
		if (bUseCurrent):
			pRiverStepPlot = CyMap().plot(self.m_pRiverStartPlot.getX(), self.m_pRiverStartPlot.getY())
			if (not pRiverStepPlot.isNone()):
				pRiverStepPlot.setNOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_WEST)

		pRiverStepPlot = CyMap().plot(self.m_pRiverStartPlot.getX()-1, self.m_pRiverStartPlot.getY()-1)
		if (not pRiverStepPlot.isNone()):
			pRiverStepPlot.setWOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_SOUTH)
		return

	def placeRiverS ( self, bUseCurrent ):
		if (bUseCurrent):
			pRiverStepPlot = CyMap().plot(self.m_pRiverStartPlot.getX(), self.m_pRiverStartPlot.getY())
			if (not pRiverStepPlot.isNone()):
				pRiverStepPlot.setWOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_SOUTH)

		pRiverStepPlot = CyMap().plot(self.m_pRiverStartPlot.getX(), self.m_pRiverStartPlot.getY()-1)
		if (not pRiverStepPlot.isNone()):
			pRiverStepPlot.setWOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_SOUTH)
		return

	def placeRiverSE ( self, bUseCurrent ):
		if (bUseCurrent):
			pRiverStepPlot = CyMap().plot(self.m_pRiverStartPlot.getX(), self.m_pRiverStartPlot.getY())
			if (not pRiverStepPlot.isNone()):
				pRiverStepPlot.setNOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_EAST)

		pRiverStepPlot = CyMap().plot(self.m_pRiverStartPlot.getX()+1, self.m_pRiverStartPlot.getY())
		if (not pRiverStepPlot.isNone()):
			pRiverStepPlot.setNOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_EAST)
		pRiverStepPlot = CyMap().plot(self.m_pRiverStartPlot.getX()+1, self.m_pRiverStartPlot.getY()-1)
		if (not pRiverStepPlot.isNone()):
			pRiverStepPlot.setWOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_SOUTH)
		return

	def setUnitEditInfo(self, bSamePlot):
		initWBToolEditCtrl()
		self.m_tabCtrlEdit = getWBToolEditTabCtrl()

		if not bSamePlot:
			self.m_pActivePlot = self.m_pCurrentPlot

		self.m_tabCtrlEdit.setNumColumns((gc.getNumPromotionInfos()/10)+1)
		self.m_tabCtrlEdit.setColumnLength(15)##MagisterModmod
		self.m_tabCtrlEdit.addTabSection(localText.getText("TXT_KEY_WB_UNIT_DATA",(self.m_pActivePlot.getX(), self.m_pActivePlot.getY())))

		strTest = ()
		for i in range(self.m_pActivePlot.getNumUnits()):
			if (len(self.m_pActivePlot.getUnit(i).getNameNoDesc())):
				strTest = strTest + (self.m_pActivePlot.getUnit(i).getNameNoDesc(),)
			else:
				strTest = strTest + (self.m_pActivePlot.getUnit(i).getName(),)

		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_CURRENT_UNIT",()),  0)
		self.m_tabCtrlEdit.addSectionDropdown("Current_Unit", strTest, "CvScreensInterface", "WorldBuilderHandleUnitEditPullDownCB", "UnitEditPullDown", 0, self.m_iCurrentUnit)

## Platy Builder ##
		self.m_iCurrentPlayer = self.m_pActivePlot.getUnit(self.m_iCurrentUnit).getOwner()
		self.m_iCurrentTeam = gc.getPlayer(self.m_iCurrentPlayer).getTeam()
		pUnit = self.m_pActivePlot.getUnit(self.m_iCurrentUnit)
##MagisterModmod
		pPlayer = gc.getPlayer(self.m_iCurrentPlayer)
## Platy Builder ##


## Unit Type ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_UNIT_TYPE",()),  0)

		lUnitType = []
		for i in xrange(gc.getNumUnitInfos()):
			lUnitType.append([gc.getUnitInfo(i).getDescription(), i])
		lUnitType.sort()

		strTest = ()
		for i in xrange(len(lUnitType)):
			strTest = strTest + (lUnitType[i][0],)
			if pUnit.getUnitType() == lUnitType[i][1]:
				iType = i
		self.m_tabCtrlEdit.addSectionDropdown("Unit_Leader_Type", strTest, "CvScreensInterface", "WorldBuilderHandleUnitEditUnitTypeCB", "UnitEditUnitType", 0, iType)


##MagisterModmod moved
## Owner ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_OWNER",()),  0)
		strTest = ()
		iCount = 0
		for i in xrange(gc.getMAX_PLAYERS()):
			if gc.getPlayer(i).isEverAlive():
				strTest = strTest + (gc.getPlayer(i).getName(),)
				if i == self.m_iCurrentPlayer:
					iUnitOwner = iCount
				iCount = iCount + 1
		self.m_tabCtrlEdit.addSectionDropdown("Unit Owner", strTest, "CvScreensInterface", "WorldBuilderHandleCurrentPlayerEditPullDownCB", "UnitEditOwner", 0, iUnitOwner)

##MagisterModmod
## Unit Religion ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_UNIT_RELIGION",()),  0)
		strTest = (localText.getText("TXT_KEY_WB_NONE",()),)
		for i in xrange(gc.getNumReligionInfos()):
			strTest = strTest + (gc.getReligionInfo(i).getDescription(),)
		self.m_tabCtrlEdit.addSectionDropdown("Unit Religion", strTest, "CvScreensInterface", "WorldBuilderHandleUnitReligionEditPullDownCB", "UnitReligionEditPullDown", 0, pUnit.getReligion()+1)
##MagisterModmod

## Leader Type ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_LEADER_UNIT",()),  0)
		lUnitType = []
		for i in xrange(gc.getNumUnitInfos()):
			if gc.getUnitInfo(i).getDomainType() == pUnit.getDomainType():
				lUnitType.append([gc.getUnitInfo(i).getDescription(), i])
		lUnitType.sort()
		iLeaderType = 0
		strTest = (localText.getText("TXT_KEY_WB_NONE",()),)
		for i in xrange(len(lUnitType)):
			strTest = strTest + (lUnitType[i][0],)
			if pUnit.getLeaderUnitType() == lUnitType[i][1]:
				iLeaderType = i +1
		self.m_tabCtrlEdit.addSectionDropdown("Unit_Leader_Type", strTest, "CvScreensInterface", "WorldBuilderHandleUnitEditLeaderCB", "UnitEditLeader", 0, iLeaderType)
## Unit AI Type ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_UNIT_AI",()),  0)
		strTest = ()
		for i in xrange(UnitAITypes.NUM_UNITAI_TYPES):
			sUnitAI = gc.getUnitAIInfo(i).getDescription()[7:]
			sUnitAI = sUnitAI.lower()
			sUnitAI = sUnitAI.replace("_", " ")
			sUnitAI = sUnitAI.capitalize()
			strTest = strTest + (sUnitAI,)
		self.m_tabCtrlEdit.addSectionDropdown("Unit_AI_Type", strTest, "CvScreensInterface", "WorldBuilderHandleUnitAITypeEditPullDownCB", "UnitAITypeEditPullDown", 0, pUnit.getUnitAIType())
## Direction ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_DIRECTION",()),  0)
		strTest = (localText.getText("TXT_KEY_WB_NORTH",()),) + (localText.getText("TXT_KEY_WB_NORTHEAST",()),) + (localText.getText("TXT_KEY_WB_EAST",()),) + (localText.getText("TXT_KEY_WB_SOUTHEAST",()),)
		strTest += (localText.getText("TXT_KEY_WB_SOUTH",()),) + (localText.getText("TXT_KEY_WB_SOUTHWEST",()),) + (localText.getText("TXT_KEY_WB_WEST",()),) + (localText.getText("TXT_KEY_WB_NORTHWEST",()),)
		self.m_tabCtrlEdit.addSectionDropdown("Unit_Direction", strTest, "CvScreensInterface", "WorldBuilderHandleUnitEditDirectionCB", "UnitEditDirection", 0, pUnit.getFacingDirection())
		self.m_tabCtrlEdit.addSectionLabel("",  0)
## Unit Name ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_UNIT_NAME",()), 0)
		if (len(pUnit.getNameNoDesc())):
			strName = pUnit.getNameNoDesc()
		else:
			strName = pUnit.getName()
		self.m_tabCtrlEdit.addSectionEditCtrl(strName, "CvScreensInterface", "WorldBuilderHandleUnitEditNameCB", "UnitEditName", 0)


## Promotions ##
		self.m_tabCtrlEdit.addSectionButton(localText.getText("TXT_KEY_PEDIA_CATEGORY_PROMOTION",()), "CvScreensInterface", "WorldBuilderHandleEnterNewScreenCB", "PromotionEditScreen", 0)


## Move Unit ##
		self.m_tabCtrlEdit.addSectionButton(localText.getText("TXT_KEY_WB_MOVE_UNIT",()), "CvScreensInterface", "WorldBuilderHandleMoveUnitCB", "MoveUnit", 0)

## Duplicate ##
		self.m_tabCtrlEdit.addSectionButton(localText.getText("TXT_KEY_WB_DUPLICATE",()), "CvScreensInterface", "WorldBuilderHandleUnitEditDuplicateCB", "UnitEditDuplicate", 0)
## Kill ##
		self.m_tabCtrlEdit.addSectionButton(localText.getText("TXT_KEY_WB_KILL",()), "CvScreensInterface", "WorldBuilderHandleKillCB", "Unit", 0)

## Promotion Ready ##
		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_WB_PROMOTION_READY",()), "CvScreensInterface", "WorldBuilderHandleUnitEditPromotionReadyCB", "UnitEditPromotionReady", 0, pUnit.isPromotionReady())
## Made Attack ##
		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_WB_MADE_ATTACK",()), "CvScreensInterface", "WorldBuilderHandleUnitEditMadeAttackCB", "UnitEditMadeAttack", 0, pUnit.isMadeAttack())
## Made Interception ##
		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_WB_MADE_INTERCEPT",()), "CvScreensInterface", "WorldBuilderHandleUnitEditMadeInterceptionCB", "UnitEditMadeInterception", 0, pUnit.isMadeInterception())

##MagisterModmod
##Has Casted
		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_WB_HAS_CAST",()), "CvScreensInterface", "WorldBuilderHandleUnitEditHasCastedCB", "UnitEditHasCasted", 0, pUnit.isHasCasted())
		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_WB_IS_IMMORTAL",()), "CvScreensInterface", "WorldBuilderHandleUnitEditIsImmortalCB", "UnitEditIsImmortal", 0, pUnit.isImmortal())

##Is Avatar
		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_PROMOTION_AVATAR",()), "CvScreensInterface", "WorldBuilderHandleUnitEditAvatarOfCivLeaderCB", "UnitEditAvatarOfCivLeader", 0, pUnit.isAvatarOfCivLeader())

## Is PermanentSummon ##
		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_WB_IS_PERMANENT_SUMMON",()), "CvScreensInterface", "WorldBuilderHandleUnitEditPermanentSummonCB", "UnitEditPermanentSummon", 0, pUnit.isPermanentSummon())

##MagisterModmod

		self.m_tabCtrlEdit.addSectionLabel("",  0)
		self.m_tabCtrlEdit.addSectionLabel("",  0)
##MagisterModmod
## Unit ID ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_UNIT_ID",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("Current_Unit", "CvScreensInterface", "WorldBuilderHandleUnitEditIDSelectCB", "UnitEditIDSelect", 0, -1, 999999999, 1, pUnit.getID(), 0, 0)

## Group ID ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_GROUP_ID",(pUnit.getGroupID(),)), 0)
##MagisterModmod

## Experience ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_EXPERIENCE",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("UnitEditExperienceCB", "CvScreensInterface", "WorldBuilderHandleUnitEditExperienceCB", "UnitEditExperience", 0, 0, 10000, 1, pUnit.getExperience(), 0, 0)
## Level ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_LEVEL",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("UnitEditLevelCB", "CvScreensInterface", "WorldBuilderHandleUnitEditLevelCB", "UnitEditLevel", 0, 1, 100, 1, pUnit.getLevel(), 0, 0)

## Damage % ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_DAMAGE",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("UnitEditDamageCB", 	"CvScreensInterface", "WorldBuilderHandleUnitEditDamageCB", "UnitEditDamage", 0, 0, 100, 1, pUnit.getDamage(), 0, 0)

## Moves ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_MOVES",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("UnitEditMovesCB", "CvScreensInterface", "WorldBuilderHandleUnitEditMovesCB", "UnitEditMoves", 0, 0, pUnit.baseMoves(), 1, pUnit.movesLeft() / gc.getDefineINT("MOVE_DENOMINATOR"), 0, 0)

## Base Strength ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_STRENGTH",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("UnitEditStrengthCB", "CvScreensInterface", "WorldBuilderHandleUnitEditStrengthCB", "UnitEditStrength", 0, 0, 1000, 1, pUnit.baseCombatStr(), 0, 0)
####Magister
## Base Strength ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_STRENGTH_DEFENSE",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("UnitEditStrengthDefenseCB", "CvScreensInterface", "WorldBuilderHandleUnitEditStrengthDefenseCB", "UnitEditStrengthDefense", 0, 0, 1000, 1, pUnit.baseCombatStrDefense(), 0, 0)
##Magister

##		self.m_tabCtrlEdit.addSectionLabel("",  0)
## Summoner ID ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_SUMMONER_ID",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("UnitEditSummonerCB", "CvScreensInterface", "WorldBuilderHandleUnitEditSummonerCB", "UnitEditSummoner", 0, -1, 999999999, 1, pUnit.getSummoner(), 0, 0)

		pSummoner = pPlayer.getUnit(pUnit.getSummoner())
		if pSummoner.isNone():
			self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_SUMMONER_NONE",()),  0)
			self.m_tabCtrlEdit.addSectionLabel("",  0)
		else:
			self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_SUMMONER_DESCRIPTION",(pSummoner.getName(),)), 0)
			self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_SUMMONER_LOCATION",(pSummoner.getX(),pSummoner.getY(),)), 0)


## Duration ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_DURATION",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("UnitEditDurationCB", "CvScreensInterface", "WorldBuilderHandleUnitEditDurationCB", "UnitEditDuration", 0, 0, 100, 1, pUnit.getDuration(), 0, 0)
## Cargo ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_CARGO",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("UnitEditCargoCB", "CvScreensInterface", "WorldBuilderHandleUnitEditCargoCB", 	"UnitEditCargo", 0, 0, min(100, pUnit.cargoSpace() * 100), 1, pUnit.cargoSpace(), 0, 0)

## Immobile Timer ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_IMMOBILE_TIMER",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("UnitEditImmobileTimerCB", "CvScreensInterface", "WorldBuilderHandleUnitEditImmobileTimerCB", "UnitEditImmobileTimer", 0, 0, 100, 1, pUnit.getImmobileTimer(), 0, 0)
##

##MagisterModmod

##ScenarioCounter
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_SCENARIO_COUNTER",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("UnitEditScenarioCounterCB", "CvScreensInterface", "WorldBuilderHandleUnitEditScenarioCounterCB", "UnitEditScenarioCounter", 0, -10000, 10000, 1, pUnit.getScenarioCounter(), 0, 0)

		if -1 < pUnit.getScenarioCounter() < gc.getNumUnitInfos():
			self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_SCENARIO_COUNTER_UNIT",(gc.getUnitInfo(pUnit.getScenarioCounter()).getDescription(),)), 0)
		else:
			self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_SCENARIO_COUNTER_NO_UNIT",()),  0)


##		self.m_tabCtrlEdit.addSectionLabel("",  0)
## Unit Script ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_SCRIPT_DATA",()),  0)
		self.m_tabCtrlEdit.addSectionEditCtrl(pUnit.getScriptData(), "CvScreensInterface", "WorldBuilderHandleEditScriptCB", "UnitEditScript", 0)



		if (not self.m_tabCtrlEdit.isNone()):
			print("Enabling map control 4")
			self.m_normalPlayerTabCtrl.enable(False)
			self.m_normalMapTabCtrl.enable(False)
			self.m_bCtrlEditUp = True
		return

	def setCityEditInfo(self, bSamePlot):
		initWBToolEditCtrl()
		self.m_tabCtrlEdit = getWBToolEditTabCtrl()

## Platy City Data ##
		if not bSamePlot:
			self.m_pActivePlot = self.m_pCurrentPlot
		pCity = self.m_pActivePlot.getPlotCity()
		self.m_iCurrentPlayer = pCity.getOwner()
		self.m_iCurrentTeam = gc.getPlayer(self.m_iCurrentPlayer).getTeam()
		self.m_tabCtrlEdit.setNumColumns(4)
		self.m_tabCtrlEdit.setColumnLength(15)
		self.m_tabCtrlEdit.addTabSection(localText.getText("TXT_KEY_WB_CITY_DATA",(self.m_pActivePlot.getX(), self.m_pActivePlot.getY())))
## Choose City ##
		strTest = ()
		iCount = 0
		(loopCity, iter) = gc.getPlayer(self.m_iCurrentPlayer).firstCity(False)
		while(loopCity):
			if loopCity.getX() == self.m_pActivePlot.getX() and loopCity.getY() == self.m_pActivePlot.getY():
				iCurrentCity = iCount
			strTest = strTest + (loopCity.getName(),)
			iCount += 1
			(loopCity, iter) = gc.getPlayer(self.m_iCurrentPlayer).nextCity(iter, False)
		self.m_tabCtrlEdit.addSectionDropdown("Owner", strTest, "CvScreensInterface", "WorldBuilderHandleChooseCityCB", "ChooseCity", 0, iCurrentCity)
## City Name ##
		self.m_tabCtrlEdit.addSectionEditCtrl(pCity.getName(), "CvScreensInterface", "WorldBuilderHandleCityEditNameCB", "CityEditName", 0)
## Owner ##
		strTest = ()
		iCount = 0
		for i in range(gc.getMAX_PLAYERS()):
			if gc.getPlayer(i).isEverAlive():
				strTest = strTest + (gc.getPlayer(i).getName(),)
				if i == self.m_iCurrentPlayer:
					iOwner = iCount
				iCount = iCount + 1
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_OWNER",()),  0)
		self.m_tabCtrlEdit.addSectionDropdown("Owner", strTest, "CvScreensInterface", "WorldBuilderHandleCurrentPlayerEditPullDownCB", "CityEditOwner", 0, iOwner)
##MagisterModmod
## Civ Type ##

		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_CIV_TYPE",()),  0)
		strTest = ()
		for i in range(gc.getNumCivilizationInfos()):
			strTest = strTest + (gc.getCivilizationInfo(i).getDescription(),)
		self.m_tabCtrlEdit.addSectionDropdown("Civilization Type", strTest, "CvScreensInterface", "WorldBuilderHandleCivTypeEditPullDownCB", "CityEditCivType", 0, pCity.getCivilizationType())
##MagisterModmod

## New Screens ##
		self.m_tabCtrlEdit.addSectionButton(localText.getText("TXT_KEY_PEDIA_CATEGORY_BUILDING",())+"\b\b\b\b\b\b", "CvScreensInterface", "WorldBuilderHandleEnterNewScreenCB", "BuildingEditScreen", 0)
		self.m_tabCtrlEdit.addSectionButton(localText.getText("TXT_KEY_PEDIA_CATEGORY_RELIGION",())+"\b\b\b\b\b\b", "CvScreensInterface", "WorldBuilderHandleEnterNewScreenCB", "ReligionEditScreen", 0)
		self.m_tabCtrlEdit.addSectionButton(localText.getText("TXT_KEY_PEDIA_CATEGORY_SPECIALIST",())+"\b\b\b\b\b\b", "CvScreensInterface", "WorldBuilderHandleEnterNewScreenCB", "FreeSpecialistEditScreen", 0)
		self.m_tabCtrlEdit.addSectionButton(localText.getText("TXT_KEY_PEDIA_CATEGORY_BONUS",())+"\b\b\b\b\b\b", "CvScreensInterface", "WorldBuilderHandleEnterNewScreenCB", "FreeBonusEditScreen", 0)

		self.m_tabCtrlEdit.addSectionLabel("",  0)
		self.m_tabCtrlEdit.addSectionLabel("",  0)
		self.m_tabCtrlEdit.addSectionLabel("",  0)
		self.m_tabCtrlEdit.addSectionLabel("",  0)
		self.m_tabCtrlEdit.addSectionLabel("",  0)

## Population ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_POPULATION",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("CityEditPopulationCB", "CvScreensInterface", "WorldBuilderHandleCityEditPopulationCB", "CityEditPopulation", 0, 1, 1000, 1, pCity.getPopulation(), 0, 0)
## Culture ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_CULTURE",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("CityEditCultureCB", "CvScreensInterface", "WorldBuilderHandleCityEditCultureCB", "CityEditCulture", 0, 1, 100000000, 1, pCity.getCulture(self.m_iCurrentPlayer), 0, 0)
		strTest = ()
		for i in xrange(gc.getNumCultureLevelInfos()):
			strTest = strTest + (gc.getCultureLevelInfo(i).getDescription(),)
		self.m_tabCtrlEdit.addSectionDropdown("CityEditCultureLevelCB", strTest, "CvScreensInterface", "WorldBuilderHandleCityEditCultureLevelCB", "CityEditCultureLevel", 0, pCity.getCultureLevel())
## Happiness ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_NET_HAPPINESS",()),  0)
		strHappiness = str("CityEditHappinessCB")
		self.m_tabCtrlEdit.addSectionSpinner(strHappiness, "CvScreensInterface", "WorldBuilderHandleCityEditHappinessCB", "CityEditHappiness", 0, -1000, 1000, 1, pCity.happyLevel() - pCity.unhappyLevel(0), 0, 0)
## Health ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_NET_HEALTH",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("CityEditHealthCB", "CvScreensInterface", "WorldBuilderHandleCityEditHealthCB", "CityEditHealth", 0, -1000, 1000, 1, pCity.goodHealth() - pCity.badHealth(False), 0, 0)
## Defense ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_DEFENSE",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("CityEditDefenseCB", "CvScreensInterface", "WorldBuilderHandleCityEditDefenseCB", "CityEditDefense", 0, 0, pCity.getTotalDefense(False), 1, pCity.getTotalDefense(False) * (100 - pCity.getDefenseDamage())/100, 0, 0)
## Trade Routes ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_HEADING_TRADEROUTE_LIST",()) + ":",  0)
		self.m_tabCtrlEdit.addSectionSpinner("CityEditTradeRouteCB", "CvScreensInterface", "WorldBuilderHandleCityEditTradeRouteCB", "CityEditTradeRoute", 0, 0, gc.getDefineINT("MAX_TRADE_ROUTES"), 1, pCity.getTradeRoutes(), 0, 0)
## Food ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_CONCEPT_FOOD",()) + ":",  0)
		self.m_tabCtrlEdit.addSectionSpinner("CityEditFoodCB", "CvScreensInterface", "WorldBuilderHandleCityEditFoodCB", "CityEditFood", 0, 0, pCity.growthThreshold(), 1, pCity.getFood(), 0, 0)
## Modify Buildings ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_MODIFIED_BUILDINGS",()),  0)
		lBuildingClass = []
		for i in xrange(gc.getNumBuildingClassInfos()):
			lBuildingClass.append([gc.getBuildingClassInfo(i).getDescription(), i])
		lBuildingClass.sort()

		strTest = ()
		for i in xrange(len(lBuildingClass)):
			strTest += (lBuildingClass[i][0],)
		self.m_tabCtrlEdit.addSectionDropdown("CityEditBuildingClass", strTest, "CvScreensInterface", "WorldBuilderHandleCityEditBuildingClassCB", "BuildingClass", 0, self.m_iBuildingClass)
		strTest = ()
		for i in range(3):
			strTest += (gc.getYieldInfo(i).getDescription(),)
		for i in range(4):
			strTest += (gc.getCommerceInfo(i).getDescription(),)
		self.m_tabCtrlEdit.addSectionDropdown("CityEditModifer", strTest, "CvScreensInterface", "WorldBuilderHandleCityEditModiferCB", "CityEditModifer", 0, self.m_iBuildingModifier)
		iBuildingClass = lBuildingClass[self.m_iBuildingClass][1]
		if self.m_iBuildingModifier < 3:
			iModifier = pCity.getBuildingYieldChange(iBuildingClass, self.m_iBuildingModifier)
		else:
			iModifier = pCity.getBuildingCommerceChange(iBuildingClass, self.m_iBuildingModifier - 3)
		self.m_tabCtrlEdit.addSectionSpinner("CityEditModifyBuildingClassCB", "CvScreensInterface", "WorldBuilderHandleCityEditModifyBuildingClassCB", "CityEditModifyBuildingClass", 0, -100, 100, 1, iModifier, 0, 0)
## Current Production ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_CURRENT_PRODUCTION",()),  0)
		strTest = (localText.getText("TXT_KEY_WB_NONE",()),)
		pPlayer = gc.getPlayer(self.m_iCurrentPlayer)
		iCurrentProduction = 0
		iCount = 1
		for iUnit in xrange(gc.getNumUnitInfos()):
			if pCity.canTrain(iUnit, True, False):
				strTest += (gc.getUnitInfo(iUnit).getDescription(),)
				if pCity.getProductionUnit() == iUnit:
					iCurrentProduction = iCount
				iCount += 1
		for iBuilding in xrange(gc.getNumBuildingInfos()):
			if pCity.canConstruct(iBuilding, True, False, False):
				strTest += (gc.getBuildingInfo(iBuilding).getDescription(),)
				if pCity.getProductionBuilding() == iBuilding:
					iCurrentProduction = iCount
				iCount += 1
		for iProject in xrange(gc.getNumProjectInfos()):
			if pCity.canCreate(iProject, True, False):
				strTest += (gc.getProjectInfo(iProject).getDescription(),)
				if pCity.getProductionProject() == iProject:
					iCurrentProduction = iCount
				iCount += 1
		for iProcess in xrange(gc.getNumProcessInfos()):
			if pCity.canMaintain(iProcess, True):
				strTest += (gc.getProcessInfo(iProcess).getDescription(),)
				if pCity.getProductionProcess() == iProcess:
					iCurrentProduction = iCount
				iCount += 1
		self.m_tabCtrlEdit.addSectionDropdown("CityEditChooseProduction", strTest, "CvScreensInterface", "WorldBuilderHandleCityEditChooseProductionCB", "CityEditChooseProduction", 0, iCurrentProduction)
		if iCurrentProduction == 0 or pCity.getProductionProcess() > -1:
			self.m_tabCtrlEdit.addSectionLabel(" ",  0)
			self.m_tabCtrlEdit.addSectionLabel(" ",  0)
		else:
			self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_PROGRESS_OUT_OF",(pCity.getProductionNeeded(),)),  0)
			self.m_tabCtrlEdit.addSectionSpinner("CityEditProductionProgressCB", "CvScreensInterface", "WorldBuilderHandleCityEditProductionProgressCB", "CityEditProductionProgress", 0, 0, pCity.getProductionNeeded(), 1, pCity.getProduction(), 0, 0)
## Timers##
		strTest = (localText.getText("TXT_KEY_CONCEPT_RESISTANCE",()),) + (localText.getText("TXT_KEY_WB_DRAFT_ANGER",()),) + (localText.getText("TXT_KEY_WB_HURRY_ANGER",()),)
		strTest += (localText.getText("TXT_KEY_WB_DEFY_RESOLUTION",()),) + (localText.getText("TXT_KEY_WB_ESP_HAPPY",()),) + (localText.getText("TXT_KEY_WB_ESP_HEALTH",()),) + (localText.getText("TXT_KEY_WB_TEMP_HAPPY",()),)
		self.m_tabCtrlEdit.addSectionDropdown("Timers", strTest, "CvScreensInterface", "WorldBuilderHandleCityEditTimersCB", "CityEditTimers", 0, self.m_iCityTimer)
		if self.m_iCityTimer == 0:
			iCurrentTimer = pCity.getOccupationTimer()
		elif self.m_iCityTimer == 1:
			iCurrentTimer = pCity.getConscriptAngerTimer()
		elif self.m_iCityTimer == 2:
			iCurrentTimer = pCity.getHurryAngerTimer()
		elif self.m_iCityTimer == 3:
			iCurrentTimer = pCity.getDefyResolutionAngerTimer()
		elif self.m_iCityTimer == 4:
			iCurrentTimer = pCity.getEspionageHappinessCounter()
		elif self.m_iCityTimer == 5:
			iCurrentTimer = pCity.getEspionageHealthCounter()
		else:
			iCurrentTimer = pCity.getHappinessTimer()
		self.m_tabCtrlEdit.addSectionSpinner("CityEditCurrentTimerCB", "CvScreensInterface", "WorldBuilderHandleCityEditCurrentTimerCB", "CityEditCurrentTimer", 0, 0, 100, 1, iCurrentTimer, 0, 0)

##MagisterModmod - MNAI Advanced Tactics
		if CyGame().isOption(GameOptionTypes.GAMEOPTION_ADVANCED_TACTICS):
			self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_REV_INDEX",()),  0)
			self.m_tabCtrlEdit.addSectionSpinner("CityEditRevIndexCB", "CvScreensInterface", "WorldBuilderHandleCityEditRevIndexCB", "CityEditRevIndex", 0, -10000, 10000, 1, pCity.getRevolutionIndex(), 0, 0)
		else:
			self.m_tabCtrlEdit.addSectionLabel("",  0)
			self.m_tabCtrlEdit.addSectionLabel("",  0)
## City Script ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_SCRIPT_DATA",()),  0)
		self.m_tabCtrlEdit.addSectionEditCtrl(pCity.getScriptData(), "CvScreensInterface", "WorldBuilderHandleEditScriptCB", "CityEditScript", 0)

		return

## Player Edit Screen ##
	def setPlayerEditInfo(self):
		initWBToolEditCtrl()
		self.m_tabCtrlEdit = getWBToolEditTabCtrl()
		iNumColumns = 4
		iExtraSpace = max(0, gc.getNumCivicOptionInfos() - 7)
		iColumnLength = 12 + iExtraSpace##MagisterModmod
		self.m_tabCtrlEdit.setNumColumns(iNumColumns)
		self.m_tabCtrlEdit.setColumnLength(iColumnLength)
		self.m_tabCtrlEdit.addTabSection(localText.getText("TXT_KEY_WB_PLAYER_DATA",(self.m_iCurrentPlayer,)))
## Current Player ##
		strTest = ()
		iCount = 0
		for i in xrange(gc.getMAX_PLAYERS()):
			if gc.getPlayer(i).isEverAlive():
				strPlayer = gc.getPlayer(i).getName()
				if not gc.getPlayer(i).isAlive():
					strPlayer = "*" + strPlayer
				lTraits = []
				for iTrait in xrange(gc.getNumTraitInfos()):
					if gc.getPlayer(i).hasTrait(iTrait):
						lTraits.append(iTrait)
				sTrait = " ["
				for iTrait in xrange(len(lTraits)):
					sTrait += localText.getText(gc.getTraitInfo(lTraits[iTrait]).getShortDescription(),())
					if iTrait != len(lTraits) -1:
						sTrait += "/"
				if len(lTraits) == 0:
					sTrait += localText.getText("TXT_KEY_WB_NONE",())
				strPlayer += sTrait + "]"
				strTest = strTest + (strPlayer,)
				if i == self.m_iCurrentPlayer:
					iCurrentPlayer = iCount
				iCount += 1
		self.m_tabCtrlEdit.addSectionDropdown("Current Player", strTest, "CvScreensInterface", "WorldBuilderHandleCurrentPlayerEditPullDownCB", "PlayerEditCurrentPlayer", 0, iCurrentPlayer)
		pPlayer = gc.getPlayer(self.m_iCurrentPlayer)

## Current Era ##
		strTest = ()
		for i in xrange(gc.getNumEraInfos()):
			strTest = strTest + (localText.getText("TXT_KEY_WB_ERA",(gc.getEraInfo(i).getDescription(),)),)
		self.m_tabCtrlEdit.addSectionDropdown("Current Era", strTest, "CvScreensInterface", "WorldBuilderHandleCurrentEraEditPullDownCB", "PlayerEditCurrentEra", 0, pPlayer.getCurrentEra())


## Current Research ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_WB_CURRENT_RESEARCH",()),  0)
		strTest = (localText.getText("TXT_KEY_WB_NONE",()),)
		iCurrentTech = 0
		iCount = 0
		for i in xrange(gc.getNumTechInfos()):
			if pPlayer.canResearch(i, False):
				iCount += 1
				strTest = strTest + (gc.getTechInfo(i).getDescription(),)
				if pPlayer.getCurrentResearch() == i:
					iCurrentTech = iCount
		self.m_tabCtrlEdit.addSectionDropdown("Current Tech", strTest, "CvScreensInterface", "WorldBuilderHandleCurrentTechEditPullDownCB", "CurrentTechEditPullDown", 0, iCurrentTech)
		if pPlayer.getCurrentResearch() == -1:
			self.m_tabCtrlEdit.addSectionLabel(" ",  0)
			self.m_tabCtrlEdit.addSectionLabel(" ",  0)
		else:
			self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_PROGRESS_OUT_OF",(gc.getTeam(self.m_iCurrentTeam).getResearchCost(pPlayer.getCurrentResearch()),)),  0)
			self.m_tabCtrlEdit.addSectionSpinner("TeamEditResearchProgressCB", "CvScreensInterface", "WorldBuilderHandleTeamEditResearchProgressCB", "TeamEditResearchProgress", 0, 0, gc.getTeam(self.m_iCurrentTeam).getResearchCost(pPlayer.getCurrentResearch()), 1, gc.getTeam(self.m_iCurrentTeam).getResearchProgress(pPlayer.getCurrentResearch()), 0, 0)
##
		for i in range (iExtraSpace):
			self.m_tabCtrlEdit.addSectionLabel(" ",  0)
## Civics ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_PEDIA_CATEGORY_CIVIC",()) + ":",  0)
		for iCivicOption in xrange(gc.getNumCivicOptionInfos()):
			strTest = ()
			iCount = 0
			for i in xrange(gc.getNumCivicInfos()):
				if gc.getCivicInfo(i).getCivicOptionType() == iCivicOption:
					strTest = strTest + (gc.getCivicInfo(i).getDescription(),)
					if pPlayer.isCivic(i):
						iCivic = iCount
					iCount = iCount + 1
			self.m_tabCtrlEdit.addSectionDropdown(str(iCivicOption), strTest, "CvScreensInterface", "WorldBuilderHandlePlayerEditCivicCB", str(iCivicOption), 0, iCivic)
##
##		for i in range (iColumnLength - 3 - gc.getNumCivicOptionInfos()):
##			self.m_tabCtrlEdit.addSectionLabel(" ",  0)

##MagisterModmod
		self.m_tabCtrlEdit.addSectionButton(localText.getText("TXT_KEY_WB_TRAITS",())+"      ", "CvScreensInterface", "WorldBuilderHandleEnterNewScreenCB", "TraitEditScreen", 0)

		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_ALIGNMENT",()),  0)
		strTest = (localText.getText("TXT_KEY_ALIGNMENT_GOOD",()), localText.getText("TXT_KEY_ALIGNMENT_NEUTRAL",()), localText.getText("TXT_KEY_ALIGNMENT_EVIL",()))
		self.m_tabCtrlEdit.addSectionDropdown("Alignment", strTest, "CvScreensInterface", "WorldBuilderHandleAlignmentEditPullDownCB", "AlignmentEditPullDown", 0, pPlayer.getAlignment())
##MagisterModmod

## State Religion ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_STATE_RELIGION",()),  0)
		strTest = (localText.getText("TXT_KEY_WB_NONE",()),)
		for i in xrange(gc.getNumReligionInfos()):
			strTest = strTest + (gc.getReligionInfo(i).getDescription(),)
		self.m_tabCtrlEdit.addSectionDropdown("State Religion", strTest, "CvScreensInterface", "WorldBuilderHandleStateReligionEditPullDownCB", "StateReligionEditPullDown", 0, pPlayer.getStateReligion() + 1)

## State Religion Unit Production ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_STATE_RELIGION_UNIT",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("PlayerEditStateReligionUnitProductionCB", "CvScreensInterface", "WorldBuilderHandlePlayerEditStateReligionUnitProductionCB", "PlayerEditStateReligionUnitProduction", 0, 0, 1000, 1, pPlayer.getStateReligionUnitProductionModifier(), 0, 0)
## State Religion Building Production ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_STATE_RELIGION_BUILDING",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("PlayerEditStateReligionBuildingProductionCB", "CvScreensInterface", "WorldBuilderHandlePlayerEditStateReligionBuildingProductionCB", "PlayerEditStateReligionBuildingProduction", 0, 0, 1000, 1, pPlayer.getStateReligionBuildingProductionModifier(), 0, 0)

##		self.m_tabCtrlEdit.addSectionLabel(" ",  0)
##		self.m_tabCtrlEdit.addSectionLabel(" ",  0)
##		self.m_tabCtrlEdit.addSectionLabel(" ",  0)
##		self.m_tabCtrlEdit.addSectionLabel(" ",  0)


##MagisterModmod
##Has Cast World Spell
		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_WB_HAS_CAST_WORLD_SPELL",()), "CvScreensInterface", "WorldBuilderHandleEditFeatHasCastWorldSpellCB", "PlayerEditFeatHasCastedWorldSpell", 0, pPlayer.isFeatAccomplished(FeatTypes.FEAT_GLOBAL_SPELL))
##Trust
		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_SPELL_TRUST",()), "CvScreensInterface", "WorldBuilderHandleEditFeatTrustCB", "PlayerEditFeatTrust", 0, pPlayer.isFeatAccomplished(FeatTypes.FEAT_TRUST))
##Sirona
		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_SPELL_SIRONAS_TOUCH",()), "CvScreensInterface", "WorldBuilderHandleEditFeatHealUnitPerTurnCB", "PlayerEditFeatHealUnitPerTurn", 0, pPlayer.isFeatAccomplished(FeatTypes.FEAT_HEAL_UNIT_PER_TURN))


## Commerce Sliders ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_COMMERCE_SLIDERS",()),  0)
		for i in xrange(4):
			self.m_tabCtrlEdit.addSectionCheckbox(gc.getCommerceInfo(i).getDescription(), "CvScreensInterface", "WorldBuilderHandleTeamEditCommerceFlexibleCB", str(i), 0, pPlayer.isCommerceFlexible(i))
			self.m_tabCtrlEdit.addSectionSpinner("PlayerEditCommercePercentCB", "CvScreensInterface", "WorldBuilderHandlePlayerEditCommercePercentCB", str(i), 0, 0, 100, 10, pPlayer.getCommercePercent(i), 0, 0)
##

		for i in range (iExtraSpace):
			self.m_tabCtrlEdit.addSectionLabel(" ",  0)
		self.m_tabCtrlEdit.addSectionLabel(" ",  0)
		self.m_tabCtrlEdit.addSectionLabel(" ",  0)
		self.m_tabCtrlEdit.addSectionLabel(" ",  0)
## Golden Age ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_CONCEPT_GOLDEN_AGE",()) + ":",  0)
		self.m_tabCtrlEdit.addSectionSpinner("PlayerEditGoldenAgeCB", "CvScreensInterface", "WorldBuilderHandlePlayerEditGoldenAgeCB", "PlayerEditGoldenAge", 0, 0, 1000, 1, pPlayer.getGoldenAgeTurns(), 0, 0)
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_GOLDEN_AGE_UNITS",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("PlayerEditGoldenAgeUnitsCB", "CvScreensInterface", "WorldBuilderHandlePlayerEditGoldenAgeUnitsCB", "PlayerEditGoldenAgeUnits", 0, 1, 10, 1, pPlayer.unitsRequiredForGoldenAge(), 0, 0)
## Anarchy ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_ANARCHY",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("PlayerEditAnarchyCB", "CvScreensInterface", "WorldBuilderHandlePlayerEditAnarchyCB", "PlayerEditAnarchy", 0, 0, 1000, 1, pPlayer.getAnarchyTurns(), 0, 0)
## Combat Experience ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_COMBAT_EXPERIENCE",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("PlayerEditCombatExperienceCB", "CvScreensInterface", "WorldBuilderHandlePlayerEditCombatExperienceCB", "PlayerEditCombatExperience", 0, 0, 1000, 1, pPlayer.getCombatExperience(), 0, 0)
## Gold ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_GOLD",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("PlayerEditGoldCB", "CvScreensInterface", "WorldBuilderHandlePlayerEditGoldCB", "PlayerEditGold", 0, -10000, 1000000, 1, pPlayer.getGold(), 0, 0)
##
		for i in range (iExtraSpace):
			self.m_tabCtrlEdit.addSectionLabel(" ",  0)



## Player Script ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_SCRIPT_DATA",()),  0)
		self.m_tabCtrlEdit.addSectionEditCtrl(pPlayer.getScriptData(), "CvScreensInterface", "WorldBuilderHandleEditScriptCB", "PlayerEditScript", 0)

		if (not self.m_tabCtrlEdit.isNone()):
			self.m_normalPlayerTabCtrl.enable(False)
			self.m_normalMapTabCtrl.enable(False)
			self.m_bCtrlEditUp = True
		return
## Player Edit Screen ##

## Team Edit Screen ##
	def setTeamEditInfo(self):
		initWBToolEditCtrl()
		self.m_tabCtrlEdit = getWBToolEditTabCtrl()
		self.m_tabCtrlEdit.setNumColumns(4)

		iExtraSpace = max(0, gc.getNumVoteSourceInfos() - 2)
		iColumnLength = 8 + iExtraSpace
		self.m_tabCtrlEdit.setColumnLength(iColumnLength)
		self.m_tabCtrlEdit.addTabSection(localText.getText("TXT_KEY_WB_TEAM_DATA",(self.m_iCurrentTeam,)))
## Team ##
		strTest = ()
		iCount = 0
		for i in xrange(gc.getMAX_TEAMS()):
			if gc.getTeam(i).isAlive():
				strTest = strTest + (gc.getTeam(i).getName(),)
				if i == self.m_iCurrentTeam:
					iTeam = iCount
				iCount = iCount + 1
		self.m_tabCtrlEdit.addSectionDropdown("Team", strTest, "CvScreensInterface", "WorldBuilderHandleTeamEditPullDownCB", "TeamEditPullDown", 0, iTeam)
		pTeam = gc.getTeam(self.m_iCurrentTeam)
## Merge Team ##
		strTest = (localText.getText("TXT_KEY_WB_MERGE_TEAM",()),)
		for i in xrange(gc.getMAX_TEAMS()):
			if gc.getTeam(i).isAlive():
				if i == self.m_iCurrentTeam: continue
				strTest = strTest + (gc.getTeam(i).getName(),)
		self.m_tabCtrlEdit.addSectionDropdown("AddTeam", strTest, "CvScreensInterface", "WorldBuilderHandleAddTeamCB", "AddTeam", 0, 0)
## Team Leader ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_LEADER",(gc.getPlayer(pTeam.getLeaderID()).getName(),)),  0)
## Projects ##
		self.m_tabCtrlEdit.addSectionButton(localText.getText("TXT_KEY_PEDIA_CATEGORY_PROJECT",())+"\b\b\b\b\b\b", "CvScreensInterface", "WorldBuilderHandleEnterNewScreenCB", "ProjectEditScreen", 0)
## Technology ##
		self.m_tabCtrlEdit.addSectionButton(localText.getText("TXT_KEY_PEDIA_CATEGORY_TECH",())+"\b\b\b\b\b\b", "CvScreensInterface", "WorldBuilderHandleEnterNewScreenCB", "TechEditScreen", 0)
## Guaranteed Eligiblity ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_GUARANTEED_ELIGIBILITY",()),  0)
		for i in xrange(gc.getNumVoteSourceInfos()):
			self.m_tabCtrlEdit.addSectionCheckbox(gc.getVoteSourceInfo(i).getDescription(), "CvScreensInterface", "WorldBuilderHandleTeamEditForceTeamVoteCB", str(i), 0, pTeam.isForceTeamVoteEligible(i))
##
		for i in xrange(iExtraSpace):
			self.m_tabCtrlEdit.addSectionLabel(" ",  0)
## Domain Moves ##
		strTest = ()
		for i in range(3):
			sDomain = gc.getDomainInfo(i).getDescription()
			sDomain = sDomain[:sDomain.find(" ")]
			strTest = strTest + (localText.getText("TXT_KEY_WB_DOMAIN_MOVES",(sDomain,)),)
		self.m_tabCtrlEdit.addSectionDropdown("TeamSelectDomain", strTest, "CvScreensInterface", "WorldBuilderHandleDomainEditPullDownCB", "DomainEditPullDown", 0, self.m_iDomain)
		self.m_tabCtrlEdit.addSectionSpinner("TeamEditDomainMovesCB", "CvScreensInterface", "WorldBuilderHandleTeamEditDomainMovesCB", "TeamEditDomainMoves", 0, 0, 10, 1, pTeam.getExtraMoves(self.m_iDomain), 0, 0)
## Route Change ##
		strTest = ()
		for i in xrange(gc.getNumRouteInfos()):
			strTest = strTest + (gc.getRouteInfo(i).getDescription() + " " + localText.getText("TXT_KEY_WB_ROUTE_CHANGE",()),)
		self.m_tabCtrlEdit.addSectionDropdown("Route", strTest, "CvScreensInterface", "WorldBuilderHandleRouteEditPullDownCB", "RouteEditPullDown", 0, self.m_iRoute)
		self.m_tabCtrlEdit.addSectionSpinner("TeamEditRouteChangeCB", "CvScreensInterface", "WorldBuilderHandleTeamEditRouteChangeCB", "TeamEditRouteChange", 0, -100, 100, 1, pTeam.getRouteChange(self.m_iRoute), 0, 0)
## Enemy War Weariness ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_ENEMY_WAR_WEARINESS",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("TeamEditEnemyWarWearinessCB", "CvScreensInterface", "WorldBuilderHandleTeamEditEnemyWarWearinessCB", "TeamEditEnemyWarWeariness", 0, 0, 1000, 1, pTeam.getEnemyWarWearinessModifier(), 0, 0)
## Nuke Interception ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_NUKE_INTERCEPTION",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("TeamEditNukeInterceptionCB", "CvScreensInterface", "WorldBuilderHandleTeamEditNukeInterceptionCB", "TeamEditNukeInterception", 0, -100, 100, 1, pTeam.getNukeInterception(), 0, 0)
##
		for i in xrange(iExtraSpace):
			self.m_tabCtrlEdit.addSectionLabel(" ",  0)
## Improvement Extra Yield ##
		strTest = ()
		lImprovements = []
		for i in xrange(gc.getNumImprovementInfos()):
			if gc.getImprovementInfo(i).isGraphicalOnly(): continue
			strTest = strTest + (gc.getImprovementInfo(i).getDescription(),)
			lImprovements.append(i)
		self.m_tabCtrlEdit.addSectionDropdown("Improvement", strTest, "CvScreensInterface", "WorldBuilderHandleImprovementEditPullDownCB", "ImprovementEditPullDown", 0, self.m_iImprovement)
		strTest = ()
		for i in xrange(3):
			strTest = strTest + (localText.getText("TXT_KEY_WB_IMPROVEMENT_YIELD",(gc.getYieldInfo(i).getDescription(),)),)
		self.m_tabCtrlEdit.addSectionDropdown("Yield", strTest, "CvScreensInterface", "WorldBuilderHandleYieldEditPullDownCB", "YieldEditPullDown", 0, self.m_iYield)
		self.m_tabCtrlEdit.addSectionSpinner("TeamEditImprovementYieldCB", "CvScreensInterface", "WorldBuilderHandleTeamEditImprovementYieldCB", "TeamEditImprovementYield", 0, 0, 10, 1, pTeam.getImprovementYieldChange(lImprovements[self.m_iImprovement], self.m_iYield), 0, 0)
## Team Abilities ##
		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_WB_MAP_CENTERING",()), "CvScreensInterface", "WorldBuilderHandleTeamEditMapCenteringCB", "TeamEditMapCentering", 0, pTeam.isMapCentering())
		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_WB_WATER_WORK",()), "CvScreensInterface", "WorldBuilderHandleTeamEditWaterWorkCB", "TeamEditWaterWork", 0, pTeam.isWaterWork())
		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_WB_EXTRA_WATER_SIGHT",()), "CvScreensInterface", "WorldBuilderHandleTeamEditExtraWaterSeeFromCB", "TeamEditExtraWaterSeeFrom", 0, pTeam.isExtraWaterSeeFrom())
		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_WB_BRIDGE_BUILDING",()), "CvScreensInterface", "WorldBuilderHandleTeamEditBridgeBuildingCB", "TeamEditBridgeBuilding", 0, pTeam.isBridgeBuilding())
		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_CONCEPT_IRRIGATION",()), "CvScreensInterface", "WorldBuilderHandleTeamEditIrrigationCB", "TeamEditIrrigation", 0, pTeam.isIrrigation())
##
		for i in xrange(iExtraSpace):
			self.m_tabCtrlEdit.addSectionLabel(" ",  0)
		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_WB_IGNORE_IRRIGATION",()), "CvScreensInterface", "WorldBuilderHandleTeamEditIgnoreIrrigationCB", "TeamEditIgnoreIrrigation", 0, pTeam.isIgnoreIrrigation())
		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_WB_GOLD_TRADING",()), "CvScreensInterface", "WorldBuilderHandleTeamEditGoldTradingCB", "TeamEditGoldTrading", 0, pTeam.isGoldTrading())
		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_WB_TECH_TRADING",()), "CvScreensInterface", "WorldBuilderHandleTeamEditTechTradingCB", "TeamEditTechTrading", 0, pTeam.isTechTrading())
		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_WB_MAP_TRADING",()), "CvScreensInterface", "WorldBuilderHandleTeamEditMapTradingCB", "TeamEditMapTrading", 0, pTeam.isMapTrading())
		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_WB_OPEN_BORDERS",()), "CvScreensInterface", "WorldBuilderHandleTeamEditOpenBordersTradingCB", "TeamEditOpenBordersTrading", 0, pTeam.isOpenBordersTrading())
		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_WB_PERMANENT_ALLIANCE",()), "CvScreensInterface", "WorldBuilderHandleTeamEditPermanentAllianceTradingCB", "TeamEditPermanentAllianceTrading", 0, pTeam.isPermanentAllianceTrading())
		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_WB_DEFENSIVE_PACT",()), "CvScreensInterface", "WorldBuilderHandleTeamEditDefensivePactTradingCB", "TeamEditDefensivePactTrading", 0, pTeam.isDefensivePactTrading())
		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_WB_VASSAL_TRADING",()), "CvScreensInterface", "WorldBuilderHandleTeamEditVassalTradingCB", "TeamEditVassalTrading", 0, pTeam.isVassalStateTrading())

		if (not self.m_tabCtrlEdit.isNone()):
			self.m_normalPlayerTabCtrl.enable(False)
			self.m_normalMapTabCtrl.enable(False)
			self.m_bCtrlEditUp = True
		return
## Team Edit Screen ##


## MagisterModmod
## Trait Edit Screen ##
	def setTraitEditInfo(self):
		initWBToolEditCtrl()
		self.m_tabCtrlEdit = getWBToolEditTabCtrl()

		iNumColumns = 6
		self.m_tabCtrlEdit.setNumColumns(iNumColumns)
		self.m_tabCtrlEdit.addTabSection(localText.getText("TXT_KEY_WB_TRAITS",()))

		iTraitPerColumn = (gc.getNumTraitInfos() +1) /iNumColumns
		if (gc.getNumTraitInfos() +1) % iNumColumns > 0:
			iTraitPerColumn += 1
		iColumnLength = iTraitPerColumn *2
		iTraitColumn = (gc.getNumTraitInfos() +1) / iTraitPerColumn
		if (gc.getNumTraitInfos() +1) % iTraitPerColumn > 0:
			iTraitColumn += 1

		self.m_tabCtrlEdit.setColumnLength(iColumnLength)
		self.m_tabCtrlEdit.setSize(min(self.xResolution, iNumColumns * self.iColumnWidth), min(self.yResolution, max(5, iColumnLength) * self.iColumnHeight))


		for iTrait in xrange(gc.getNumTraitInfos()):
			self.m_tabCtrlEdit.addSectionCheckbox(localText.getText(str(gc.getTraitInfo(iTrait).getDescription()),()), "CvScreensInterface", "WorldBuilderHandleEditPlayerTraitCB", str(iTrait), 0, gc.getPlayer(self.m_iCurrentPlayer).hasTrait(iTrait))

		self.m_tabCtrlEdit.addSectionButton(localText.getText("TXT_KEY_WB_BACK",()) + "      ", "CvScreensInterface", "WorldBuilderHandleEnterNewScreenCB", "PlayerEditScreen", 0)

		if (not self.m_tabCtrlEdit.isNone()):
			self.m_normalPlayerTabCtrl.enable(False)
			self.m_normalMapTabCtrl.enable(False)
			self.m_bCtrlEditUp = True
		return
## Trait Edit Screen ##
## MagisterModmod

## Game Data Screen ##
	def setGameEditInfo(self):
		initWBToolEditCtrl()
		self.m_tabCtrlEdit = getWBToolEditTabCtrl()
		self.m_tabCtrlEdit.setNumColumns(1)
		self.m_tabCtrlEdit.setColumnLength(18)
		self.m_tabCtrlEdit.addTabSection(localText.getText("TXT_KEY_WB_GAME_DATA",()))
## Start Year ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_START_YEAR",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("Start Year", "CvScreensInterface", "WorldBuilderHandleGameEditStartYearCB", "GameEditStartYear", 0, -10000, 10000, 100, CyGame().getStartYear(), 0, 0)
## Nukes Exploded ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_NUKES_EXPLODED",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("Nukes Exploded", "CvScreensInterface", "WorldBuilderHandleGameEditNukesExplodedCB", "GameEditNukesExploded", 0, 0, 10000, 1, CyGame().getNukesExploded(), 0, 0)

##MagisterModmod
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_SCENARIO_COUNTER",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("ScenarioCounterCB", "CvScreensInterface", "WorldBuilderHandleGameEditScenarioCounterCB", "GameEditScenarioCounter", 0, -10000, 10000, 1, CyGame().getScenarioCounter(), 0, 0)

		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_GLOBAL_COUNTER",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("GlobalCounterCB", "CvScreensInterface", "WorldBuilderHandleGlobalCounterEditCB", "GameEditGlobalCounter", 0, 0, 100, 1, CyGame().getGlobalCounter(), 0, 0)


		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_HANDICAP",()),  0)
		strTest = ()
		for i in xrange(gc.getNumHandicapInfos()):
			strTest = strTest + (gc.getHandicapInfo(i).getDescription(),)
		self.m_tabCtrlEdit.addSectionDropdown("HandicapCB", strTest, "CvScreensInterface", "WorldBuilderHandleHandicapEditPullDownCB", "HandicapEditPullDown", 0, CyGame().getHandicapType())
##MagisterModmod



## Game Script ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_SCRIPT_DATA",()),  0)
		self.m_tabCtrlEdit.addSectionEditCtrl(CyGame().getScriptData(), "CvScreensInterface", "WorldBuilderHandleEditScriptCB", "GameEditScript", 0)
##
		if (not self.m_tabCtrlEdit.isNone()):
			self.m_normalPlayerTabCtrl.enable(False)
			self.m_normalMapTabCtrl.enable(False)
			self.m_bCtrlEditUp = True
		return
## Game Data Screen ##

## Game Option Screen ##
	def setGameOptionEditInfo(self):
		initWBToolEditCtrl()
		self.m_tabCtrlEdit = getWBToolEditTabCtrl()

		iNumColumns = 5
		self.m_tabCtrlEdit.setNumColumns(iNumColumns)
		Visible = []
		Hidden = []
		All = []
		lOptions = [All, Visible, Hidden]
		for i in xrange(gc.getNumGameOptionInfos()):
			GOInfo = gc.getGameOptionInfo(i)
			if GOInfo.getVisible():
				Visible.append(i)
			else:
				Hidden.append(i)
			All.append(i)
		bHasHidden = True
		if len(Visible) == len(All):
			bHasHidden = False
		iTotal = len(lOptions[self.m_iVisibleOption])
		iColumnLength = max(iTotal / (iNumColumns - bHasHidden), (3 + (self.m_iVisibleOption == 2) *2))
		if iTotal % iNumColumns > 0:
			iColumnLength += 1
		self.m_tabCtrlEdit.setColumnLength(iColumnLength)
		self.m_tabCtrlEdit.setSize(min(self.xResolution, iNumColumns * 200), min(self.yResolution, max(5, iColumnLength) * 41))

		self.m_tabCtrlEdit.addTabSection(localText.getText("TXT_KEY_WB_HELP2",()))
		if bHasHidden:
			self.m_tabCtrlEdit.addSectionRadioButton(localText.getText("TXT_KEY_WB_SHOW_ALL",()), "CvScreensInterface", "WorldBuilderHandleVisibleOptionsCB", "ShowAll", 0, self.m_iVisibleOption == 0)
			self.m_tabCtrlEdit.addSectionRadioButton(localText.getText("TXT_KEY_WB_SHOW_VISIBLE",()), "CvScreensInterface", "WorldBuilderHandleVisibleOptionsCB", "ShowVisible", 0, self.m_iVisibleOption == 1)
			self.m_tabCtrlEdit.addSectionRadioButton(localText.getText("TXT_KEY_WB_SHOW_HIDDEN",()), "CvScreensInterface", "WorldBuilderHandleVisibleOptionsCB", "ShowHidden", 0, self.m_iVisibleOption == 2)
			if self.m_iVisibleOption == 2:
				self.m_tabCtrlEdit.addSectionLabel("      " + localText.getText("TXT_KEY_WB_DEFAULT_ON",()),  0)
				self.m_tabCtrlEdit.addSectionLabel("      " + localText.getText("TXT_KEY_WB_DEFAULT_OFF",()),  0)
			for i in xrange(iColumnLength - 3 - (self.m_iVisibleOption == 2) *2):
				self.m_tabCtrlEdit.addSectionLabel(" ",  0)
		for i in lOptions[self.m_iVisibleOption]:
			sVisible =""
			if self.m_iVisibleOption == 2:
				GOInfo = gc.getGameOptionInfo(i)
				sVisible = " (O)"
				if GOInfo.getDefault():
					sVisible = " (X)"
			sText = gc.getGameOptionInfo(i).getDescription() + sVisible
			self.m_tabCtrlEdit.addSectionCheckbox(sText, "CvScreensInterface", "WorldBuilderHandleEditGameOptionCB", str(i), 0, CyGame().isOption(i))
		for i in xrange((iNumColumns - bHasHidden) * iColumnLength - iTotal):
			self.m_tabCtrlEdit.addSectionLabel(" ",  0)

		if (not self.m_tabCtrlEdit.isNone()):
			self.m_normalPlayerTabCtrl.enable(False)
			self.m_normalMapTabCtrl.enable(False)
			self.m_bCtrlEditUp = True
		return
## Game Option Screen ##

## Plot Edit Screen ##
	def setPlotEditInfo(self, bNewPlot):

		initWBToolEditCtrl()
		self.m_tabCtrlEdit = getWBToolEditTabCtrl()
		if bNewPlot:
			self.m_pActivePlot = self.m_pCurrentPlot

##MagisterModmod Resize
		self.m_tabCtrlEdit.setNumColumns(5)
		self.m_tabCtrlEdit.setColumnLength(13)
		self.m_tabCtrlEdit.addTabSection(localText.getText("TXT_KEY_WB_PLOT_DATA",(self.m_pActivePlot.getX(), self.m_pActivePlot.getY())))
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_LATITUDE",(self.m_pActivePlot.getLatitude(),)),  0)

## Culture ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_CULTURE",()),  0)
		strTest = ()
		iCount = 0
		for i in xrange(gc.getMAX_PLAYERS()):
			if gc.getPlayer(i).isEverAlive():
				strTest = strTest + (gc.getPlayer(i).getName(),)
				if i == self.m_iCurrentPlayer:
					iOwner = iCount
				iCount = iCount + 1
		self.m_tabCtrlEdit.addSectionDropdown("Owner", strTest, "CvScreensInterface", "WorldBuilderHandleCurrentPlayerEditPullDownCB", "PlotEditCurrentPlayer", 0, iOwner)
		self.m_tabCtrlEdit.addSectionSpinner("PlotEditCultureCB", "CvScreensInterface", "WorldBuilderHandlePlotEditCultureCB", "PlotEditCulture", 0, 1, 100000000, 1, self.m_pActivePlot.getCulture(self.m_iCurrentPlayer), 0, 0)
## Plot Yield ##
		self.m_tabCtrlEdit.addSectionLabel(gc.getYieldInfo(0).getDescription() + ":",  0)
		self.m_tabCtrlEdit.addSectionSpinner("PlotEditYieldCB", "CvScreensInterface", "WorldBuilderHandlePlotEditYieldCB", "PlotEditFood", 0, 0, 20, 1, self.m_pActivePlot.getYield(YieldTypes.YIELD_FOOD), 0, 0)
		self.m_tabCtrlEdit.addSectionLabel(gc.getYieldInfo(1).getDescription() + ":",  0)
		self.m_tabCtrlEdit.addSectionSpinner("PlotEditYieldCB", "CvScreensInterface", "WorldBuilderHandlePlotEditYieldCB", "PlotEditProduction", 0, 0, 20, 1, self.m_pActivePlot.getYield(YieldTypes.YIELD_PRODUCTION), 0, 0)
		self.m_tabCtrlEdit.addSectionLabel(gc.getYieldInfo(2).getDescription() + ":",  0)
		self.m_tabCtrlEdit.addSectionSpinner("PlotEditYieldCB", "CvScreensInterface", "WorldBuilderHandlePlotEditYieldCB", "PlotEditCommerce", 0, 0, 20, 1, self.m_pActivePlot.getYield(YieldTypes.YIELD_COMMERCE), 0, 0)
## Script ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_SCRIPT_DATA",()),  0)
		self.m_tabCtrlEdit.addSectionEditCtrl(self.m_pActivePlot.getScriptData(), "CvScreensInterface", "WorldBuilderHandleEditScriptCB", "PlotEditScript", 0)


##MagisterModmod
		self.m_tabCtrlEdit.addSectionLabel("",  0)
		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_WB_MOVE_DISABLED_AI",()), "CvScreensInterface", "WorldBuilderHandlePlotMoveDisabledAICB", "PlotEditMoveDisabledAI", 0, self.m_pActivePlot.isMoveDisabledAI())

		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_WB_MOVE_DISABLED_HUMAN",()), "CvScreensInterface", "WorldBuilderHandlePlotMoveDisabledHumanCB", "PlotEditMoveDisabledHuman", 0, self.m_pActivePlot.isMoveDisabledHuman())

		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_WB_BUILD_DISABLED",()), "CvScreensInterface", "WorldBuilderHandlePlotBuildDisabledCB", "PlotEditBuildDisabled", 0, self.m_pActivePlot.isBuildDisabled())

		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_WB_FOUND_DISABLED",()), "CvScreensInterface", "WorldBuilderHandlePlotFoundDisabledCB", "PlotEditFoundDisabled", 0, self.m_pActivePlot.isFoundDisabled())


		self.m_tabCtrlEdit.addSectionCheckbox(localText.getText("TXT_KEY_WB_PYTHON_INACTIVE",()), "CvScreensInterface", "WorldBuilderHandlePlotPythonActiveCB", "PlotEditPythonActive", 0, not self.m_pActivePlot.isPythonActive())

		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_PLOT_COUNTER",()), 0)
		self.m_tabCtrlEdit.addSectionSpinner("PlotCounterEditCB", "CvScreensInterface", "WorldBuilderHandlePlotCounterEditCB", "PlotCounterEdit", 0, 0, 100, 1, self.m_pActivePlot.getPlotCounter(), 0, 0)

		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_PORTAL_X_COORDINATE",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("PlotEditPortalExitXCB", "CvScreensInterface", "WorldBuilderHandlePlotEditPortalExitXCB", "PlotEditPortalExitX", 0, 0, CyMap().getGridWidth()-1, 1, self.m_pActivePlot.getPortalExitX(), 0, 0)

		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_PORTAL_Y_COORDINATE",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("PlotEditPortalExitYCB", "CvScreensInterface", "WorldBuilderHandlePlotEditPortalExitYCB", "PlotEditPortalExitY", 0, 0,CyMap().getGridHeight()-1, 1, self.m_pActivePlot.getPortalExitY(), 0, 0)

		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_PLOT_MIN_LEVEL",()),  0)
		self.m_tabCtrlEdit.addSectionSpinner("PlotEditMinLevelCB", "CvScreensInterface", "WorldBuilderHandlePlotEditMinLevelCB", "PlotEditMinLevel", 0, 0, 100, 1, self.m_pActivePlot.getMinLevel(), 0, 0)

		self.m_tabCtrlEdit.addSectionLabel("",  0)
##MagisterModmod

## Plot Type ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_CHANGE_PLOTTYPE",()),  0)
		strTest = (localText.getText("TXT_KEY_TERRAIN_PEAK",()),) + (localText.getText("TXT_KEY_TERRAIN_HILL",()),) + (localText.getText("TXT_KEY_WB_LAND",()),) + (localText.getText("TXT_KEY_TERRAIN_OCEAN",()),)
		self.m_tabCtrlEdit.addSectionDropdown("PlotEditPlotType", strTest, "CvScreensInterface", "WorldBuilderHandlePlotEditPlotTypeCB", "PlotEditPlotType", 0, self.m_pActivePlot.getPlotType())
## Terrain ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_CHANGE_TERRAIN",()),  0)
		strTest = ()
		iTerrain = 0
		iCount = 0
		for i in xrange(gc.getNumTerrainInfos()):
			if gc.getTerrainInfo(i).isGraphicalOnly(): continue
			if self.m_pActivePlot.getTerrainType() == i:
				iTerrain = iCount
			strTest = strTest + (gc.getTerrainInfo(i).getDescription(),)
			iCount += 1
		self.m_tabCtrlEdit.addSectionDropdown("Plot Terrain", strTest, "CvScreensInterface", "WorldBuilderHandlePlotEditTerrainCB", "PlotEditTerrain", 0, iTerrain)
## Bonus ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_BONUS",()),  0)
		strTest = (localText.getText("TXT_KEY_WB_NONE",()),)
		for i in xrange(gc.getNumBonusInfos()):
			strTest = strTest + (gc.getBonusInfo(i).getDescription(),)
		self.m_tabCtrlEdit.addSectionDropdown("Bonus", strTest, "CvScreensInterface", "WorldBuilderHandlePlotEditBonusCB", "PlotEditBonus", 0, self.m_pActivePlot.getBonusType(-1) +1)
## Route ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_CHANGE_ROUTE",()),  0)
		strTest = (localText.getText("TXT_KEY_WB_NONE",()),)
		for i in xrange(gc.getNumRouteInfos()):
			strTest = strTest + (gc.getRouteInfo(i).getDescription(),)
		self.m_tabCtrlEdit.addSectionDropdown("Route", strTest, "CvScreensInterface", "WorldBuilderHandlePlotEditRouteCB", "PlotEditRoute", 0, self.m_pActivePlot.getRouteType() +1)
## Improvement ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_IMPROVEMENT",()),  0)
		strTest = (localText.getText("TXT_KEY_WB_NONE",()),)
		iImprovement = 0
		iCount = 1
		for i in xrange(gc.getNumImprovementInfos()):
			if gc.getImprovementInfo(i).isGraphicalOnly(): continue
			if self.m_pActivePlot.getImprovementType() == i:
				iImprovement = iCount
			strTest = strTest + (gc.getImprovementInfo(i).getDescription(),)
			iCount += 1
		self.m_tabCtrlEdit.addSectionDropdown("Improvement", strTest, "CvScreensInterface", "WorldBuilderHandlePlotEditImprovementCB", "PlotEditImprovement", 0, iImprovement)
## Upgrade Timer ##
		if self.m_pActivePlot.getOwner() > -1 and self.m_pActivePlot.getImprovementType() > -1 and gc.getImprovementInfo(self.m_pActivePlot.getImprovementType()).getUpgradeTime() > 0:
			self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_UPGRADE_PROGRESS",()),  0)
			self.m_tabCtrlEdit.addSectionSpinner("PlotEditUpgradeProgressCB", "CvScreensInterface", "WorldBuilderHandlePlotEditUpgradeProgressCB", "PlotEditUpgradeProgress", 0, 1, 1000, 1, self.m_pActivePlot.getUpgradeTimeLeft(self.m_pActivePlot.getImprovementType(), self.m_pActivePlot.getOwner()), 0, 0)
		else:
			self.m_tabCtrlEdit.addSectionLabel(" ",  0)
			self.m_tabCtrlEdit.addSectionLabel(" ",  0)
## Feature ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_FEATURE_VARIETY",()),  0)
		strTest = (localText.getText("TXT_KEY_WB_NONE",()),)
		for i in xrange(gc.getNumFeatureInfos()):
			strTest = strTest + (gc.getFeatureInfo(i).getDescription(),)
		self.m_tabCtrlEdit.addSectionDropdown("PlotEditFeature", strTest, "CvScreensInterface", "WorldBuilderHandlePlotEditFeatureCB", "PlotEditFeature", 0, self.m_pActivePlot.getFeatureType() +1)
## Variety ##
		if self.m_pActivePlot.getFeatureType() > -1 and gc.getFeatureInfo(self.m_pActivePlot.getFeatureType()).getNumVarieties() > 1:
			self.m_tabCtrlEdit.addSectionSpinner("PlotEditVarietyCB", "CvScreensInterface", "WorldBuilderHandlePlotEditVarietyCB", "PlotEditVariety", 0, 0, gc.getFeatureInfo(self.m_pActivePlot.getFeatureType()).getNumVarieties(), 1, self.m_pActivePlot.getFeatureVariety(), 0, 0)
		else:
			self.m_tabCtrlEdit.addSectionLabel(" ",  0)
## River ##
		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_EAST_RIVER",()),  0)
		strTest = (localText.getText("TXT_KEY_WB_NONE",()),) + (localText.getText("TXT_KEY_WB_NO_DIRECTION",()),) + (localText.getText("TXT_KEY_WB_NORTH",()),) + (localText.getText("TXT_KEY_WB_SOUTH",()),)
		if not self.m_pActivePlot.isWOfRiver():
			iERiver = 0
		elif self.m_pActivePlot.getRiverNSDirection() == -1:
			iERiver = 1
		elif self.m_pActivePlot.getRiverNSDirection() == 0:
			iERiver = 2
		elif self.m_pActivePlot.getRiverNSDirection() == 2:
			iERiver = 3
		self.m_tabCtrlEdit.addSectionDropdown("PlotEditRiver", strTest, "CvScreensInterface", "WorldBuilderHandlePlotEditRiverCB", "NS", 0, iERiver)

		self.m_tabCtrlEdit.addSectionLabel(localText.getText("TXT_KEY_WB_SOUTH_RIVER",()),  0)
		strTest = (localText.getText("TXT_KEY_WB_NONE",()),) + (localText.getText("TXT_KEY_WB_NO_DIRECTION",()),) + (localText.getText("TXT_KEY_WB_EAST",()),) + (localText.getText("TXT_KEY_WB_WEST",()),)
		if not self.m_pActivePlot.isNOfRiver():
			iSRiver = 0
		elif self.m_pActivePlot.getRiverWEDirection() == -1:
			iSRiver = 1
		elif self.m_pActivePlot.getRiverWEDirection() == 1:
			iSRiver = 2
		elif self.m_pActivePlot.getRiverWEDirection() == 3:
			iSRiver = 3
		self.m_tabCtrlEdit.addSectionDropdown("PlotEditRiver", strTest, "CvScreensInterface", "WorldBuilderHandlePlotEditRiverCB", "WE", 0, iSRiver)
## Event ##
		strTest = (localText.getText("TXT_KEY_WB_TRIGGER_EVENT",()),)
		for i in xrange(gc.getNumEventTriggerInfos()):
			sEvent = gc.getEventTriggerInfo(i).getType()[13:]
			sEvent = sEvent.lower()
			sEvent = sEvent.replace("_", " ")
			sEvent = sEvent.capitalize()
			strTest = strTest + (sEvent,)
		self.m_tabCtrlEdit.addSectionDropdown("Trigger Event", strTest, "CvScreensInterface", "WorldBuilderHandleTriggerEventCB", "Trigger Event", 0, 0)
		strTest = (localText.getText("TXT_KEY_WB_EVENT_OTHER_PLAYER",()),)
		iOtherPlayer = 0
		iCount = 1
		for i in xrange(gc.getMAX_CIV_PLAYERS()):
			if gc.getPlayer(i).isAlive():
				if i == self.m_iCurrentPlayer:
					continue
				strTest = strTest + (gc.getPlayer(i).getName(),)
				if i == self.m_iOtherPlayer:
					iOtherPlayer = iCount
				iCount = iCount + 1
		self.m_tabCtrlEdit.addSectionDropdown("Event Other Player", strTest, "CvScreensInterface", "WorldBuilderHandleEventOtherPlayerCB", "Event Other Player", 0, iOtherPlayer)
		strTest = (localText.getText("TXT_KEY_WB_EVENT_UNIT",()),)
		for i in xrange(self.m_pActivePlot.getNumUnits()):
			if (len(self.m_pActivePlot.getUnit(i).getNameNoDesc())):
				strTest = strTest + (self.m_pActivePlot.getUnit(i).getNameNoDesc(),)
			else:
				strTest = strTest + (self.m_pActivePlot.getUnit(i).getName(),)
		self.m_tabCtrlEdit.addSectionDropdown("Current_Unit", strTest, "CvScreensInterface", "WorldBuilderHandleEventUnitCB", "EventUnit", 0, self.m_iEventUnit +1)
## City ##
		if self.m_pActivePlot.isCity():
			self.m_tabCtrlEdit.addSectionButton(localText.getText("TXT_KEY_WB_EDIT_CITY",()) + "\b\b\b\b\b\b", "CvScreensInterface", "WorldBuilderHandleEnterNewScreenCB", "CityEditScreen", 0)
		else:
			self.m_tabCtrlEdit.addSectionButton(localText.getText("TXT_KEY_WB_ADD_CITY",()) + "\b\b\b\b\b\b", "CvScreensInterface", "WorldBuilderHandlePlotAddCityCB", "PlotAddCity", 0)

		if (not self.m_tabCtrlEdit.isNone()):
			print("Enabling map control 5")
			self.m_normalPlayerTabCtrl.enable(False)
			self.m_normalMapTabCtrl.enable(False)
			self.m_bCtrlEditUp = True
		return
## Plot Edit Screen ##

	def initCityEditScreen(self):
		self.setCityEditInfo(False)
		return

	def toggleUnitEditCB(self):
		self.m_bUnitEdit = True
		self.m_bCityEdit = False
		self.m_bNormalPlayer = False
		self.m_bNormalMap = False
		self.m_bReveal = False
		self.m_bLandmark = False
		self.m_bEraseAll = False

		if (self.m_tabCtrlEdit != 0):
			print("Enabling map control 6")
			self.m_tabCtrlEdit.enable(False)

		CyEngine().clearColoredPlots(PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS)
		CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_REVEALED_PLOTS)
		CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_WORLD_BUILDER)

		self.refreshSideMenu()
		self.setCurrentModeCheckbox(self.m_iUnitEditCheckboxID)
		print("Enabling map control 7")
		self.m_normalPlayerTabCtrl.enable(False)
		self.m_normalMapTabCtrl.enable(False)
		if (self.m_tabCtrlEdit != 0):
			self.m_tabCtrlEdit.destroy()
		return

	def toggleCityEditCB(self):
		self.m_bCityEdit = True
		self.m_bUnitEdit = False
		self.m_bNormalPlayer = False
		self.m_bNormalMap = False
		self.m_bReveal = False
		self.m_bLandmark = False
		self.m_bEraseAll = False

		if (self.m_tabCtrlEdit != 0):
			print("Enabling map control 8")
			self.m_tabCtrlEdit.enable(False)

		CyEngine().clearColoredPlots(PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS)
		CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_REVEALED_PLOTS)
		CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_WORLD_BUILDER)

		self.refreshSideMenu()
		self.setCurrentModeCheckbox(self.m_iCityEditCheckboxID)
		print("Enabling map control 9")
		self.m_normalPlayerTabCtrl.enable(False)
		self.m_normalMapTabCtrl.enable(False)
		if (self.m_tabCtrlEdit != 0):
			self.m_tabCtrlEdit.destroy()
		return

	def normalPlayerTabModeCB(self):
		self.m_bCityEdit = False
		self.m_bUnitEdit = False
		self.m_bNormalPlayer = True
		self.m_bNormalMap = False
		self.m_bReveal = False
		self.m_bLandmark = False
		self.m_bEraseAll = False
## Add Units ##
		self.m_iUnitCombat = -99
		self.m_iUnitType = -1
		self.m_iCurrentTeam = gc.getPlayer(self.m_iCurrentPlayer).getTeam()
## Add Units ##

		CyEngine().clearColoredPlots(PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS)
		CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_REVEALED_PLOTS)
		CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_WORLD_BUILDER)

		self.refreshSideMenu()
		self.setCurrentModeCheckbox(self.m_iNormalPlayerCheckboxID)
		if (self.m_normalMapTabCtrl):
			print("Disabling Map Tab")
			self.m_normalMapTabCtrl.enable(False)
		if (not self.m_normalPlayerTabCtrl.isEnabled() and not CyInterface().isInAdvancedStart()):
			print("Enabling Player Tab")
			self.m_normalPlayerTabCtrl.enable(True)
			if (self.m_tabCtrlEdit):
				self.m_tabCtrlEdit.enable(False)
			self.m_bCtrlEditUp = False
		return

	def normalMapTabModeCB(self):
		self.m_bCityEdit = False
		self.m_bUnitEdit = False
		self.m_bNormalPlayer = False
		self.m_bNormalMap = True
		self.m_bReveal = False
		self.m_bLandmark = False
		self.m_bEraseAll = False
## Plot Mode ##
		self.m_iPlotMode = 0
		self.m_iArea = -1
## Plot Mode ##

		CyEngine().clearColoredPlots(PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS)
		CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_REVEALED_PLOTS)
		CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_WORLD_BUILDER)

		self.refreshSideMenu()
		self.setCurrentModeCheckbox(self.m_iNormalMapCheckboxID)
		if (self.m_normalPlayerTabCtrl):
			print("Disabling Player Tab")
			self.m_normalPlayerTabCtrl.enable(False)
		if (not self.m_normalMapTabCtrl.isEnabled() and not CyInterface().isInAdvancedStart()):
			print("Enabling Map Tab")
			self.m_normalMapTabCtrl.enable(True)
			if (self.m_tabCtrlEdit):
				self.m_tabCtrlEdit.enable(False)
			self.m_bCtrlEditUp = False
		return

	def revealTabModeCB(self):
		self.m_bCtrlEditUp = False
		self.m_bCityEdit = False
		self.m_bUnitEdit = False
		self.m_bNormalPlayer = False
		self.m_bNormalMap = False
		self.m_bReveal = True
		self.m_bLandmark = False
		self.m_bEraseAll = False

		CyEngine().clearColoredPlots(PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS)
		CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_REVEALED_PLOTS)
		CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_WORLD_BUILDER)
		self.refreshReveal()
		self.refreshSideMenu()
		self.setCurrentModeCheckbox(self.m_iRevealTileCheckboxID)
		if (self.m_normalPlayerTabCtrl):
			self.m_normalPlayerTabCtrl.enable(False)
		if (self.m_normalMapTabCtrl):
			self.m_normalMapTabCtrl.enable(False)
		if (self.m_tabCtrlEdit):
			self.m_tabCtrlEdit.enable(False)
		return

	def diplomacyModeCB(self):
		self.m_bCtrlEditUp = False
		self.m_bCityEdit = False
		self.m_bUnitEdit = False
		self.m_bNormalPlayer = False
		self.m_bNormalMap = False
		self.m_bReveal = False
		self.m_bLandmark = False
		self.m_bEraseAll = False

		CyEngine().clearColoredPlots(PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS)
		CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_REVEALED_PLOTS)
		CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_WORLD_BUILDER)
		self.refreshSideMenu()
		self.setCurrentModeCheckbox(self.m_iDiplomacyCheckboxID)
		if (self.m_normalPlayerTabCtrl != 0):
			self.m_normalPlayerTabCtrl.enable(False)
		if (self.m_normalMapTabCtrl != 0):
			self.m_normalMapTabCtrl.enable(False)
		if (self.m_tabCtrlEdit != 0):
			self.m_tabCtrlEdit.enable(False)
## Diplomacy Screen ##
		WBDiplomacyScreen.WBDiplomacyScreen().interfaceScreen(self.m_iCurrentPlayer)
## Diplomacy Screen ##
		return

	def landmarkModeCB(self):
		self.m_bCtrlEditUp = False
		self.m_bCityEdit = False
		self.m_bUnitEdit = False
		self.m_bNormalPlayer = False
		self.m_bNormalMap = False
		self.m_bReveal = False
		self.m_bLandmark = True
		self.m_bEraseAll = False

		CyEngine().clearColoredPlots(PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS)
		CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_REVEALED_PLOTS)
		CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_WORLD_BUILDER)
		self.refreshSideMenu()
		self.setCurrentModeCheckbox(self.m_iLandmarkCheckboxID)
		if (self.m_normalPlayerTabCtrl != 0):
			self.m_normalPlayerTabCtrl.enable(False)
		if (self.m_normalMapTabCtrl != 0):
			self.m_normalMapTabCtrl.enable(False)
		if (self.m_tabCtrlEdit != 0):
			self.m_tabCtrlEdit.enable(False)
		return

	def eraseCB(self):
		self.m_bCtrlEditUp = False
		self.m_bCityEdit = False
		self.m_bUnitEdit = False
		self.m_bNormalPlayer = False
		self.m_bNormalMap = False
		self.m_bReveal = False
		self.m_bLandmark = False
		self.m_bEraseAll = True
		self.m_pRiverStartPlot = -1

		CyEngine().clearColoredPlots(PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS)
		CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_REVEALED_PLOTS)
		CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_WORLD_BUILDER)
		self.refreshSideMenu()
		self.setCurrentModeCheckbox(self.m_iEraseCheckboxID)
		if (self.m_normalPlayerTabCtrl != 0):
			self.m_normalPlayerTabCtrl.enable(False)
		if (self.m_normalMapTabCtrl != 0):
			self.m_normalMapTabCtrl.enable(False)
		if (self.m_tabCtrlEdit != 0):
			self.m_tabCtrlEdit.enable(False)
		return

	def setCurrentNormalPlayerIndex(self, argsList):
		iIndex = int(argsList)
		if (self.m_normalPlayerTabCtrl.getActiveTab() != self.m_iTechnologyTabID):
			self.m_iNormalPlayerCurrentIndexes [self.m_normalPlayerTabCtrl.getActiveTab()] = int(argsList)
		else:
			bOn = gc.getTeam(gc.getPlayer(self.m_iCurrentPlayer).getTeam()).isHasTech(iIndex)
			bOn = not bOn
			gc.getTeam(gc.getPlayer(self.m_iCurrentPlayer).getTeam()).setHasTech(iIndex, bOn, self.m_iCurrentPlayer, False, False)
## Add Units Start ##
		self.m_iUnitCombat = -99
		self.m_iUnitType = -1
		self.refreshSideMenu()
## Add Units End ##
		return 1

	def setCurrentNormalMapIndex(self, argsList):
		iIndex = int(argsList)
		self.m_iNormalMapCurrentIndexes [self.m_normalMapTabCtrl.getActiveTab()] = int(argsList)
## Edit Area Map Start ##
		self.m_iPlotMode = 0
		self.m_iArea = -1
		self.refreshSideMenu()
## Edit Area Map End ##
		return 1

	def setCurrentNormalMapList(self, argsList):
		self.m_iNormalMapCurrentList[self.m_normalMapTabCtrl.getActiveTab()] = int(argsList)
		return 1

	def setCurrentAdvancedStartIndex(self, argsList):
		iIndex = int(argsList)
		self.m_iAdvancedStartCurrentIndexes [self.m_advancedStartTabCtrl.getActiveTab()] = int(argsList)
		return 1

	def setCurrentAdvancedStartList(self, argsList):
		self.m_iAdvancedStartCurrentList[self.m_advancedStartTabCtrl.getActiveTab()] = int(argsList)
		return 1

## Platy World Builder Start ##
	def setEditButtonClicked(self, argsList):
		iIndex = int(argsList)
		if self.m_bUnitEdit:
			bOn = not self.m_pActivePlot.getUnit(self.m_iCurrentUnit).isHasPromotion(iIndex)
			self.m_pActivePlot.getUnit(self.m_iCurrentUnit).setHasPromotion(iIndex, bOn)
		return 1
## Platy World Builder End ##

	def getUnitTabID(self):
		return self.m_iUnitTabID

	def getBuildingTabID(self):
		return self.m_iBuildingTabID

	def getTechnologyTabID(self):
		return self.m_iTechnologyTabID

	def getImprovementTabID(self):
		return self.m_iImprovementTabID

	def getBonusTabID(self):
		return self.m_iBonusTabID

	def getImprovementListID(self):
		return self.m_iImprovementListID

	def getBonusListID(self):
		return self.m_iBonusListID

	def getTerrainTabID(self):
		return self.m_iTerrainTabID

	def getTerrainListID(self):
		return self.m_iTerrainListID

	def getFeatureListID(self):
		return self.m_iFeatureListID

	def getPlotTypeListID(self):
		return self.m_iPlotTypeListID

	def getRouteListID(self):
		return self.m_iRouteListID

	def getTerritoryTabID(self):
		return self.m_iTerritoryTabID

	def getTerritoryListID(self):
		return self.m_iTerritoryListID

	def getASUnitTabID(self):
		return self.m_iASUnitTabID

	def getASUnitListID(self):
		return self.m_iASUnitListID

	def getASCityTabID(self):
		return self.m_iASCityTabID

	def getASCityListID(self):
		return self.m_iASCityListID

	def getASBuildingsListID(self):
		return self.m_iASBuildingsListID

	def getASAutomateListID(self):
		return self.m_iASAutomateListID

	def getASImprovementsTabID(self):
		return self.m_iASImprovementsTabID

	def getASRoutesListID(self):
		return self.m_iASRoutesListID

	def getASImprovementsListID(self):
		return self.m_iASImprovementsListID

	def getASVisibilityTabID(self):
		return self.m_iASVisibilityTabID

	def getASVisibilityListID(self):
		return self.m_iASVisibilityListID

	def getASTechTabID(self):
		return self.m_iASTechTabID

	def getASTechListID(self):
		return self.m_iASTechListID

## Platy Multi Tile Start ##
	def highlightBrush(self):
		if (self.m_bShowBigBrush):
			if (self.m_pCurrentPlot == 0):
				return
			CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_WORLD_BUILDER)
			for x in range(self.m_pCurrentPlot.getX() - self.m_iBrushSize +1, self.m_pCurrentPlot.getX() + self.m_iBrushSize):
				for y in range(self.m_pCurrentPlot.getY() - self.m_iBrushSize +1, self.m_pCurrentPlot.getY() + self.m_iBrushSize):
					pPlot = CyMap().plot(x,y)
					if not pPlot.isNone():
						CyEngine().fillAreaBorderPlotAlt(pPlot.getX(), pPlot.getY(), AreaBorderLayers.AREA_BORDER_LAYER_WORLD_BUILDER, "COLOR_GREEN", 1)
		return

	def placeMultipleObjects(self):
		permCurrentPlot = self.m_pCurrentPlot
		for x in range(permCurrentPlot.getX() - self.m_iBrushSize +1, permCurrentPlot.getX() + self.m_iBrushSize):
			for y in range(permCurrentPlot.getY() - self.m_iBrushSize +1, permCurrentPlot.getY() + self.m_iBrushSize):
				self.m_pCurrentPlot = CyMap().plot(x,y)
				if not self.m_pCurrentPlot.isNone():
					if self.m_iBrushSize > 1:
						if (self.m_bNormalMap and (self.m_normalMapTabCtrl.getActiveTab() == self.m_iImprovementTabID)):
							iImprovementType = self.m_iNormalMapCurrentIndexes[self.m_normalMapTabCtrl.getActiveTab()]
							iIndex = -1
							iCounter = -1
							while (iIndex < iImprovementType and iCounter < gc.getNumImprovementInfos()):
								iCounter += 1
								if not gc.getImprovementInfo(iCounter).isGraphicalOnly():
									iIndex += 1
							if iIndex > -1:
								if self.m_pCurrentPlot.canHaveImprovement(iCounter, -1, True):
									self.placeObject()
						elif (self.m_bNormalMap and (self.m_normalMapTabCtrl.getActiveTab() == self.m_iBonusTabID)):
							iBonusType = self.m_iNormalMapCurrentIndexes[self.m_normalMapTabCtrl.getActiveTab()]
							if self.m_pCurrentPlot.canHaveBonus(iBonusType, False):
								self.placeObject()
						elif (self.m_bNormalMap and (self.m_normalMapTabCtrl.getActiveTab() == self.m_iTerrainTabID)):
							if self.m_iNormalMapCurrentList[self.m_normalMapTabCtrl.getActiveTab()] == self.m_iFeatureListID:
								iButtonIndex = self.m_iNormalMapCurrentIndexes[self.m_normalMapTabCtrl.getActiveTab()]
								iCount = -1
								for i in xrange(gc.getNumFeatureInfos()):
									for j in xrange(gc.getFeatureInfo(i).getNumVarieties()):
										iCount += 1
										if iCount == iButtonIndex:
											if self.m_pCurrentPlot.canHaveFeature(i):
												self.placeObject()
							elif (self.m_iNormalMapCurrentList[self.m_normalMapTabCtrl.getActiveTab()] == self.m_iRouteListID):
								iRouteType = self.m_iNormalMapCurrentIndexes[self.m_normalMapTabCtrl.getActiveTab()]
								if iRouteType < gc.getNumRouteInfos():
									if not (self.m_pCurrentPlot.isImpassable() or self.m_pCurrentPlot.isWater()):
										self.placeObject()
						else:
							self.placeObject()
					else:
						self.placeObject()
		self.m_pCurrentPlot = permCurrentPlot
		return

	def removeMultipleObjects(self):
		permCurrentPlot = self.m_pCurrentPlot
		for x in range(permCurrentPlot.getX() - self.m_iBrushSize +1, permCurrentPlot.getX() + self.m_iBrushSize):
			for y in range(permCurrentPlot.getY() - self.m_iBrushSize +1, permCurrentPlot.getY() + self.m_iBrushSize):
				self.m_pCurrentPlot = CyMap().plot(x,y)
				if not self.m_pCurrentPlot.isNone():
					self.removeObject()
		self.m_pCurrentPlot = permCurrentPlot
		return

	def showMultipleReveal(self):
		print "showMultipleReveal"
		self.refreshReveal()
		return

	def setMultipleReveal(self, bReveal):
		print "setMultipleReveal"
		permCurrentPlot = self.m_pCurrentPlot
		for x in range(permCurrentPlot.getX() - self.m_iBrushSize +1, permCurrentPlot.getX() + self.m_iBrushSize):
			for y in range(permCurrentPlot.getY() - self.m_iBrushSize +1, permCurrentPlot.getY() + self.m_iBrushSize):
				self.m_pCurrentPlot = CyMap().plot(x,y)
				if not self.m_pCurrentPlot.isNone():
					self.RevealCurrentPlot(bReveal)
		self.m_pCurrentPlot = permCurrentPlot
		self.showMultipleReveal()
		return

	def useLargeBrush(self):
		if self.m_bReveal or self.m_bEraseAll:
			return True
		if self.m_bNormalMap:
			if (self.m_normalMapTabCtrl.getActiveTab() == self.m_iTerrainTabID and
					(self.m_iNormalMapCurrentList[self.m_normalMapTabCtrl.getActiveTab()] == self.m_iTerrainListID or
					self.m_iNormalMapCurrentList[self.m_normalMapTabCtrl.getActiveTab()] == self.m_iFeatureListID or
					self.m_iNormalMapCurrentList[self.m_normalMapTabCtrl.getActiveTab()] == self.m_iPlotTypeListID or
					(self.m_iNormalMapCurrentList[self.m_normalMapTabCtrl.getActiveTab()] == self.m_iRouteListID and self.m_iNormalMapCurrentIndexes[self.m_normalMapTabCtrl.getActiveTab()] < gc.getNumRouteInfos()))
				or self.m_normalMapTabCtrl.getActiveTab() == self.m_iBonusTabID
				or self.m_normalMapTabCtrl.getActiveTab() == self.m_iTerritoryTabID
				or self.m_normalMapTabCtrl.getActiveTab() == self.m_iImprovementTabID
			):
				return True
		return False
## Platy Multi Tile End ##

	def clearSideMenu(self):
		screen = CyGInterfaceScreen( "WorldBuilderScreen", CvScreenEnums.WORLDBUILDER_SCREEN )
		screen.deleteWidget("WorldBuilderMainPanel")
		screen.deleteWidget("WorldBuilderBackgroundPanel")

		screen.deleteWidget("WorldBuilderSaveButton")
		screen.deleteWidget("WorldBuilderLoadButton")
		screen.deleteWidget("WorldBuilderAllPlotsButton")
		screen.deleteWidget("WorldBuilderExitButton")

		screen.deleteWidget("WorldBuilderUnitEditMode")
		screen.deleteWidget("WorldBuilderCityEditMode")

		screen.deleteWidget("WorldBuilderNormalPlayerMode")
		screen.deleteWidget("WorldBuilderNormalMapMode")
		screen.deleteWidget("WorldBuilderRevealMode")

		screen.deleteWidget("WorldBuilderPlayerChoice")
		screen.deleteWidget("WorldBuilderBrushSize")
		screen.deleteWidget("WorldBuilderRegenerateMap")
		screen.deleteWidget("WorldBuilderTeamChoice")
		screen.deleteWidget("WorldBuilderRevealAll")
		screen.deleteWidget("WorldBuilderUnrevealAll")
		screen.deleteWidget("WorldBuilderRevealPanel")
		screen.deleteWidget("WorldBuilderBackgroundBottomPanel")
## Side Panel ##
		screen.deleteWidget("WorldBuilderGameData")
		screen.deleteWidget("WorldBuilderGameCommands")
		screen.deleteWidget("WorldBuilderAddUnits")
		screen.deleteWidget("WorldBuilderUnitCombat")
		screen.deleteWidget("WorldBuilderAddUnitCount")
		screen.deleteWidget("WorldBuilderSetWinner")
#Magister Modmod
		screen.deleteWidget("WorldBuilderReassignPlayer")

		screen.deleteWidget("WorldBuilderChooseCivilization")
		screen.deleteWidget("WorldBuilderChooseLeader")
		screen.deleteWidget("WorldBuilderEditAreaMap")
		screen.deleteWidget("WorldBuilderModifyAreaPlotType")
		screen.deleteWidget("WorldBuilderModifyAreaTerrain")
		screen.deleteWidget("WorldBuilderModifyAreaRoute")
		screen.deleteWidget("WorldBuilderModifyAreaFeature")
		screen.deleteWidget("WorldBuilderRevealMode")
		screen.deleteWidget("WorldBuilderEraseAll")
## Side Panel ##


		return

	def setSideMenu(self):
		screen = CyGInterfaceScreen( "WorldBuilderScreen", CvScreenEnums.WORLDBUILDER_SCREEN )

		iMaxScreenWidth = self.xResolution
		iMaxScreenHeight = self.yResolution
		iScreenHeight = 10+37+37

		iButtonWidth = 32
		iButtonHeight = 32
		iButtonX = 0
		iButtonY = 0

		iX = iMaxScreenWidth-self.iScreenWidth
		if (CyInterface().isInAdvancedStart()):
			iX = 0

		screen.addPanel( "WorldBuilderBackgroundPanel", "", "", True, True, iX, 0, self.iScreenWidth, iScreenHeight, PanelStyles.PANEL_STYLE_MAIN )
		screen.addScrollPanel( "WorldBuilderMainPanel", "", iX, 0, self.iScreenWidth, iScreenHeight, PanelStyles.PANEL_STYLE_MAIN )

		if CyInterface().isInAdvancedStart():

			iX = 50
			iY = 15
			szText = u"<font=4>" + localText.getText("TXT_KEY_WB_AS_POINTS", (gc.getPlayer(CyGame().getActivePlayer()).getAdvancedStartPoints(), )) + "</font>"
			screen.setLabel("AdvancedStartPointsText", "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, iX, iY, -2, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

			iY += 30
			szText = localText.getText("TXT_KEY_ADVANCED_START_BEGIN_GAME", ())
			screen.setButtonGFC( "WorldBuilderExitButton", szText, "", iX, iY, 130, 28, WidgetTypes.WIDGET_WB_EXIT_BUTTON, -1, -1, ButtonStyles.BUTTON_STYLE_STANDARD )

			szText = u"<font=4>" + localText.getText("TXT_KEY_WB_AS_COST_THIS_LOCATION", (self.m_iCost, )) + u"</font>"
			iY = 85
			screen.setLabel("AdvancedStartCostText", "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, iX-20, iY, -2, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

		else:

			iPanelWidth = 35*6
			screen.attachPanelAt("WorldBuilderMainPanel", "WorldBuilderLoadSavePanel", "", "", False, True, PanelStyles.PANEL_STYLE_CITY_TANSHADE, 70, 0,	iPanelWidth-70, 35, WidgetTypes.WIDGET_GENERAL, -1, -1)

			screen.setImageButtonAt( "WorldBuilderVersion", "WorldBuilderLoadSavePanel", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TECH_FREETECH").getPath(), iButtonX, iButtonY, iButtonWidth, iButtonHeight, WidgetTypes.WIDGET_PYTHON, 1029, 2)
			iButtonX = iButtonX + 35
			screen.setImageButtonAt( "WorldBuilderSaveButton", "WorldBuilderLoadSavePanel", ArtFileMgr.getInterfaceArtInfo("WORLDBUILDER_SAVE").getPath(), iButtonX, iButtonY, iButtonWidth, iButtonHeight, WidgetTypes.WIDGET_WB_SAVE_BUTTON, -1, -1)
			iButtonX = iButtonX + 35
			screen.setImageButtonAt( "WorldBuilderLoadButton", "WorldBuilderLoadSavePanel", ArtFileMgr.getInterfaceArtInfo("WORLDBUILDER_LOAD").getPath(), iButtonX, iButtonY, iButtonWidth, iButtonHeight, WidgetTypes.WIDGET_WB_LOAD_BUTTON, -1, -1)
			iButtonX = iButtonX + 35
			screen.setImageButtonAt( "WorldBuilderExitButton", "WorldBuilderLoadSavePanel", ArtFileMgr.getInterfaceArtInfo("WORLDBUILDER_EXIT").getPath(), iButtonX, iButtonY, iButtonWidth, iButtonHeight, WidgetTypes.WIDGET_WB_EXIT_BUTTON, -1, -1)

			iButtonWidth = 32
			iButtonHeight = 32
			iButtonX = 0
			iButtonY = 0
			self.m_iUnitEditCheckboxID = 0
			screen.addCheckBoxGFC(
				"WorldBuilderUnitEditModeButton",
				ArtFileMgr.getInterfaceArtInfo("WORLDBUILDER_TOGGLE_UNIT_EDIT_MODE").getPath(),
				ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
				(iMaxScreenWidth-self.iScreenWidth)+8+iButtonX,
				(10+36),
				iButtonWidth,
				iButtonHeight,
				WidgetTypes.WIDGET_WB_UNIT_EDIT_BUTTON, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)

			iButtonX = iButtonX + 35
			self.m_iCityEditCheckboxID = 1
			screen.addCheckBoxGFC(
				"WorldBuilderCityEditModeButton",
				ArtFileMgr.getInterfaceArtInfo("WORLDBUILDER_TOGGLE_CITY_EDIT_MODE").getPath(),
				ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
				(iMaxScreenWidth-self.iScreenWidth)+8+iButtonX,
				(10+36),
				iButtonWidth,
				iButtonHeight,
				WidgetTypes.WIDGET_WB_CITY_EDIT_BUTTON, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)

			iButtonX = iButtonX + 35
			self.m_iNormalPlayerCheckboxID = 2
			screen.addCheckBoxGFC(
				"WorldBuilderNormalPlayerModeButton",
				ArtFileMgr.getInterfaceArtInfo("WORLDBUILDER_NORMAL_UNIT_MODE").getPath(),
				ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
				(iMaxScreenWidth-self.iScreenWidth)+8+iButtonX,
				(10+36),
				iButtonWidth,
				iButtonHeight,
				WidgetTypes.WIDGET_WB_NORMAL_PLAYER_TAB_MODE_BUTTON, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)

			iButtonX = iButtonX + 35
			self.m_iNormalMapCheckboxID = 3
			screen.addCheckBoxGFC(
				"WorldBuilderNormalMapModeButton",
				ArtFileMgr.getInterfaceArtInfo("WORLDBUILDER_CHANGE_ALL_PLOTS").getPath(),
				ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
				(iMaxScreenWidth-self.iScreenWidth)+8+iButtonX,
				(10+36),
				iButtonWidth,
				iButtonHeight,
				WidgetTypes.WIDGET_WB_NORMAL_MAP_TAB_MODE_BUTTON, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)

			iButtonX = iButtonX + 35
			self.m_iRevealTileCheckboxID = 4
			screen.addCheckBoxGFC(
				"WorldBuilderRevealTileModeButton",
				ArtFileMgr.getInterfaceArtInfo("INTERFACE_TECH_LOS").getPath(),
				ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
				(iMaxScreenWidth-self.iScreenWidth)+8+iButtonX,
				(10+36),
				iButtonWidth,
				iButtonHeight,
				WidgetTypes.WIDGET_WB_REVEAL_TAB_MODE_BUTTON, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)

			iButtonX = iButtonX + 35
			self.m_iDiplomacyCheckboxID = 5
			screen.addCheckBoxGFC(
				"WorldBuilderDiplomacyModeButton",
				ArtFileMgr.getInterfaceArtInfo("WORLDBUILDER_DIPLOMACY_MODE").getPath(),
				ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
				(iMaxScreenWidth-self.iScreenWidth)+8+iButtonX,
				(10+36),
				iButtonWidth,
				iButtonHeight,
				WidgetTypes.WIDGET_WB_DIPLOMACY_MODE_BUTTON, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)

			iButtonX = 0
			self.m_iLandmarkCheckboxID = 6
			screen.addCheckBoxGFC(
				"WorldBuilderLandmarkButton",
				ArtFileMgr.getInterfaceArtInfo("WORLDBUILDER_LANDMARK_MODE").getPath(),
				ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
				(iMaxScreenWidth-self.iScreenWidth)+8+iButtonX,
				(10),
				iButtonWidth,
				iButtonHeight,
				WidgetTypes.WIDGET_WB_LANDMARK_BUTTON, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)

			iButtonX = iButtonX + 35
			self.m_iEraseCheckboxID = 7
			screen.addCheckBoxGFC(
				"WorldBuilderEraseButton",
				ArtFileMgr.getInterfaceArtInfo("WORLDBUILDER_ERASE").getPath(),
				ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
				(iMaxScreenWidth-self.iScreenWidth)+8+iButtonX,
				(10),
				iButtonWidth,
				iButtonHeight,
				WidgetTypes.WIDGET_WB_ERASE_BUTTON, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)

			self.setCurrentModeCheckbox(self.m_iNormalPlayerCheckboxID)

		return

	def refreshSideMenu(self):
		screen = CyGInterfaceScreen( "WorldBuilderScreen", CvScreenEnums.WORLDBUILDER_SCREEN )

		iMaxScreenWidth = self.xResolution
		iMaxScreenHeight = self.yResolution
		iScreenHeight = 10+37+37

		if (CyInterface().isInAdvancedStart()):

			iX = 50
			iY = 15
			szText = u"<font=4>" + localText.getText("TXT_KEY_WB_AS_POINTS", (gc.getPlayer(CyGame().getActivePlayer()).getAdvancedStartPoints(), )) + "</font>"
			screen.setLabel("AdvancedStartPointsText", "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, iX, iY, -2, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

			szText = u"<font=4>" + localText.getText("TXT_KEY_WB_AS_COST_THIS_LOCATION", (self.m_iCost, )) + u"</font>"
			iY = 85
			screen.setLabel("AdvancedStartCostText", "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, iX-20, iY, -2, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

		else:

			screen.deleteWidget("WorldBuilderPlayerChoice")
			screen.deleteWidget("WorldBuilderBrushSize")
			screen.deleteWidget("WorldBuilderRegenerateMap")
			screen.deleteWidget("WorldBuilderTeamChoice")
			screen.deleteWidget("WorldBuilderRevealAll")
			screen.deleteWidget("WorldBuilderUnrevealAll")
			screen.deleteWidget("WorldBuilderRevealPanel")
			screen.deleteWidget("WorldBuilderBackgroundBottomPanel")
## Game Data ##
			screen.deleteWidget("WorldBuilderGameData")
			screen.deleteWidget("WorldBuilderGameCommands")
			screen.deleteWidget("WorldBuilderAddUnits")
			screen.deleteWidget("WorldBuilderUnitCombat")
			screen.deleteWidget("WorldBuilderAddUnitCount")
			screen.deleteWidget("WorldBuilderSetWinner")
#MagisterModmod
			screen.deleteWidget("WorldBuilderReassignPlayer")

			screen.deleteWidget("WorldBuilderChooseCivilization")
			screen.deleteWidget("WorldBuilderChooseLeader")
			screen.deleteWidget("WorldBuilderEditAreaMap")
			screen.deleteWidget("WorldBuilderModifyAreaPlotType")
			screen.deleteWidget("WorldBuilderModifyAreaTerrain")
			screen.deleteWidget("WorldBuilderModifyAreaRoute")
			screen.deleteWidget("WorldBuilderModifyAreaFeature")
			screen.deleteWidget("WorldBuilderRevealMode")
			screen.deleteWidget("WorldBuilderEraseAll")
## Game Data ##
## Panel Screen ##
			iPanelWidth = 35*6
			if self.m_bReveal:
				screen.addPanel( "WorldBuilderBackgroundBottomPanel", "", "", True, True, iMaxScreenWidth-self.iScreenWidth, 10+32+32, self.iScreenWidth, 45 + 37 * 2, PanelStyles.PANEL_STYLE_MAIN )
			elif self.m_bEraseAll:
				screen.addPanel( "WorldBuilderBackgroundBottomPanel", "", "", True, True, iMaxScreenWidth-self.iScreenWidth, 10+32+32, self.iScreenWidth, 45, PanelStyles.PANEL_STYLE_MAIN )
			elif self.m_bNormalPlayer:
				if self.m_iUnitCombat > -2:
					screen.addPanel( "WorldBuilderBackgroundBottomPanel", "", "", True, True, iMaxScreenWidth-self.iScreenWidth, 10+32+32, self.iScreenWidth, 45 + 37 * 5, PanelStyles.PANEL_STYLE_MAIN )
				elif self.m_iUnitCombat == -2:
					screen.addPanel( "WorldBuilderBackgroundBottomPanel", "", "", True, True, iMaxScreenWidth-self.iScreenWidth, 10+32+32, self.iScreenWidth, 45 + 37 * 3, PanelStyles.PANEL_STYLE_MAIN )
				elif self.m_iUnitCombat == -4:
					if self.m_iNewCivilization == -1:
						screen.addPanel( "WorldBuilderBackgroundBottomPanel", "", "", True, True, iMaxScreenWidth-self.iScreenWidth, 10+32+32, self.iScreenWidth, 45 + 37 * 3, PanelStyles.PANEL_STYLE_MAIN )
					else:
						screen.addPanel( "WorldBuilderBackgroundBottomPanel", "", "", True, True, iMaxScreenWidth-self.iScreenWidth, 10+32+32, self.iScreenWidth, 45 + 37 * 4, PanelStyles.PANEL_STYLE_MAIN )
				elif self.m_iUnitCombat == -5:
					screen.addPanel( "WorldBuilderBackgroundBottomPanel", "", "", True, True, iMaxScreenWidth-self.iScreenWidth, 10+32+32, self.iScreenWidth, 45 + 37 * 3, PanelStyles.PANEL_STYLE_MAIN )
				else:
					screen.addPanel( "WorldBuilderBackgroundBottomPanel", "", "", True, True, iMaxScreenWidth-self.iScreenWidth, 10+32+32, self.iScreenWidth, 45 + 37 * 2, PanelStyles.PANEL_STYLE_MAIN )
			elif self.m_bNormalMap:
				if self.m_iPlotMode == 3:
					screen.addPanel( "WorldBuilderBackgroundBottomPanel", "", "", True, True, iMaxScreenWidth-self.iScreenWidth, 10+32+32, self.iScreenWidth, 45 + 37 * 5, PanelStyles.PANEL_STYLE_MAIN )
				elif self.m_iArea == -1:
					screen.addPanel( "WorldBuilderBackgroundBottomPanel", "", "", True, True, iMaxScreenWidth-self.iScreenWidth, 10+32+32, self.iScreenWidth, 45 + 37, PanelStyles.PANEL_STYLE_MAIN )
				else:
					if CyMap().getArea(self.m_iArea).isWater():
						screen.addPanel( "WorldBuilderBackgroundBottomPanel", "", "", True, True, iMaxScreenWidth-self.iScreenWidth, 10+32+32, self.iScreenWidth, 45 + 37 * 4, PanelStyles.PANEL_STYLE_MAIN )
					else:
						screen.addPanel( "WorldBuilderBackgroundBottomPanel", "", "", True, True, iMaxScreenWidth-self.iScreenWidth, 10+32+32, self.iScreenWidth, 45 + 37 * 5, PanelStyles.PANEL_STYLE_MAIN )
			else:
				screen.addPanel( "WorldBuilderBackgroundBottomPanel", "", "", True, True, iMaxScreenWidth-self.iScreenWidth, 10+32+32, self.iScreenWidth, 45, PanelStyles.PANEL_STYLE_MAIN )

			if (self.m_bNormalPlayer and (not self.m_bUnitEdit) and (not self.m_bCityEdit)):
				szDropdownName = str("WorldBuilderPlayerChoice")
				screen.addDropDownBoxGFC(szDropdownName, (iMaxScreenWidth-self.iScreenWidth)+8, (10+36+36), iPanelWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
## Current Player ##
				for iPlayer in xrange(gc.getMAX_PLAYERS()):
					if (gc.getPlayer(iPlayer).isEverAlive()):
						strPlayerAliveStatus = gc.getPlayer(iPlayer).getName()
						sCiv = gc.getPlayer(iPlayer).getCivilizationShortDescription(0)
						strPlayerAliveStatus += " (" + sCiv + ")"
						if not gc.getPlayer(iPlayer).isAlive():
							strPlayerAliveStatus = "*" + strPlayerAliveStatus
						screen.addPullDownString(szDropdownName, strPlayerAliveStatus, iPlayer, iPlayer, self.m_iCurrentPlayer == iPlayer)
## Game Data Start##
				szDropdownName = str("WorldBuilderGameData")
				screen.addDropDownBoxGFC(szDropdownName, (iMaxScreenWidth-self.iScreenWidth)+8, (10+ 36*3), iPanelWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
				screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_EDIT_DATA",()), 0, 0, True)
				screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_PLAYER_DATA",(self.m_iCurrentPlayer,)), 0, 0, False)
				screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_TEAM_DATA",(self.m_iCurrentTeam,)), 0, 0, False)
				screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_GAME_DATA",()), 0, 0, False)
## Game Commands Start ##
				szDropdownName = str("WorldBuilderGameCommands")
				screen.addDropDownBoxGFC(szDropdownName, (iMaxScreenWidth-self.iScreenWidth)+8, (10+ 36*4), iPanelWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
				screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_COMMANDS",()), 0, 0, True)
				screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_ADD_UNITS",()), 0, 0, self.m_iUnitCombat > -2)
				screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_SET_WINNER",()), 0, 0, self.m_iUnitCombat == -2)
				screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_KILL_PLAYER",(gc.getPlayer(self.m_iCurrentPlayer).getName(),)), 0, 0, False)
				if CyGame().countCivPlayersEverAlive() != gc.getMAX_CIV_PLAYERS():
					screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_ADD_NEW_PLAYER",()), 0, 0, self.m_iUnitCombat == -4)

#Magister Momdod
				if gc.getPlayer(self.m_iCurrentPlayer).isHuman():
					screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_REASSIGN_PLAYER",()), 0, 0, self.m_iUnitCombat == -5)

## Adds Units Start ##
				if self.m_iUnitCombat > -2:
					szDropdownName = str("WorldBuilderAddUnits")
					screen.addDropDownBoxGFC(szDropdownName, (iMaxScreenWidth-self.iScreenWidth)+8, (10+ 36*5), iPanelWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
					screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_NO_CLASS",()), 0, 0, self.m_iUnitCombat == -1)
					for i in xrange(gc.getNumUnitCombatInfos()):
						szPullDownString = gc.getUnitCombatInfo(i).getDescription()
						screen.addPullDownString(szDropdownName, szPullDownString, i, i, self.m_iUnitCombat == i)

					szDropdownName = str("WorldBuilderUnitCombat")
					screen.addDropDownBoxGFC(szDropdownName, (iMaxScreenWidth-self.iScreenWidth)+8, (10+ 36*6), iPanelWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
					iCount = 0
					for i in xrange(gc.getNumUnitInfos()):
						if gc.getUnitInfo(i).getUnitCombatType() == self.m_iUnitCombat:
							if iCount == 0 and self.m_iUnitType == -1:
								self.m_iUnitType = i
							iCount += 1
							szPullDownString = gc.getUnitInfo(i).getDescription()
							screen.addPullDownString(szDropdownName, szPullDownString, i, i, self.m_iUnitType == i)

					szDropdownName = str("WorldBuilderAddUnitCount")
					screen.addDropDownBoxGFC(szDropdownName, (iMaxScreenWidth-self.iScreenWidth)+8, (10+ 36*7), iPanelWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
					screen.addPullDownString(szDropdownName, "1", 0, 0, self.m_iAddUnitCount == 1)
					for i in xrange(1, 11, 1):
						screen.addPullDownString(szDropdownName, str(10 * i), i, i, self.m_iAddUnitCount == 10 * i)
## Set as Winner ##
				elif self.m_iUnitCombat == -2:
					szDropdownName = str("WorldBuilderSetWinner")
					screen.addDropDownBoxGFC(szDropdownName, (iMaxScreenWidth-self.iScreenWidth)+8, (10+ 36*5), iPanelWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
					screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_VICTORY_TYPE",()), 0, 0, True)
					for i in xrange(gc.getNumVictoryInfos()):
						szPullDownString = gc.getVictoryInfo(i).getDescription()
						screen.addPullDownString(szDropdownName, szPullDownString, i, i, False)
				elif self.m_iUnitCombat == -4:
					szDropdownName = str("WorldBuilderChooseCivilization")
					screen.addDropDownBoxGFC(szDropdownName, (iMaxScreenWidth-self.iScreenWidth)+8, (10+ 36*5), iPanelWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
					screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_CHOOSE_CIVILIZATION",()), 0, 0, True)
					for i in xrange(gc.getNumCivilizationInfos()):
						if not CyGame().isCivEverActive(i):
							szPullDownString = gc.getCivilizationInfo(i).getDescription()
							screen.addPullDownString(szDropdownName, szPullDownString, i, i, self.m_iNewCivilization == i)
					if self.m_iNewCivilization > -1:
						szDropdownName = str("WorldBuilderChooseLeader")
						screen.addDropDownBoxGFC(szDropdownName, (iMaxScreenWidth-self.iScreenWidth)+8, (10+ 36*6), iPanelWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
						screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_CHOOSE_LEADER",()), 0, 0, True)
						for iLeader in xrange(gc.getNumLeaderHeadInfos()):
							if CyGame().isLeaderEverActive(iLeader): continue
							if not CyGame().isOption(GameOptionTypes.GAMEOPTION_LEAD_ANY_CIV):
								if not gc.getCivilizationInfo(self.m_iNewCivilization).isLeaders(iLeader): continue
							lTraits = []
							for iTrait in xrange(gc.getNumTraitInfos()):
								if gc.getLeaderHeadInfo(iLeader).hasTrait(iTrait):
									lTraits.append(iTrait)
							sTrait = " ["
							for iTrait in xrange(len(lTraits)):
								sTrait += localText.getText(gc.getTraitInfo(lTraits[iTrait]).getShortDescription(),())
								if iTrait != len(lTraits) -1:
									sTrait += "/"
							if len(lTraits) == 0:
								sTrait = localText.getText("TXT_KEY_WB_NONE",())
							szPullDownString = gc.getLeaderHeadInfo(iLeader).getDescription() + sTrait + "]"
							screen.addPullDownString(szDropdownName, szPullDownString, iLeader, iLeader, self.m_iNewLeaderType == iLeader)

#Magister Modmod
##Reassign Player
				elif self.m_iUnitCombat == -5:
					szDropdownName = str("WorldBuilderReassignPlayer")
					screen.addDropDownBoxGFC(szDropdownName, (iMaxScreenWidth-self.iScreenWidth)+8, (10+36*5), iPanelWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
					for iPlayer in xrange(gc.getMAX_PLAYERS()):
						pPlayer = gc.getPlayer(iPlayer)
						if pPlayer.isAlive() and not pPlayer.isBarbarian():
							strPlayerAliveStatus = pPlayer.getName() + " (" + pPlayer.getCivilizationShortDescription(0) + ")"
							screen.addPullDownString(szDropdownName, strPlayerAliveStatus, iPlayer, iPlayer, self.m_iCurrentPlayer == iPlayer)

## Game Commands Ends ##

			elif(self.m_bNormalMap and (not self.m_bUnitEdit) and (not self.m_bCityEdit)):
				iButtonWidth = 32
				iButtonHeight = 32
				iButtonX = 0
				iButtonY = 0
				screen.setImageButton( "WorldBuilderRegenerateMap", ArtFileMgr.getInterfaceArtInfo("WORLDBUILDER_REVEAL_ALL_TILES").getPath(), (iMaxScreenWidth-self.iScreenWidth)+8+iButtonX, (10+36+36), iButtonWidth, iButtonHeight, WidgetTypes.WIDGET_WB_REGENERATE_MAP, -1, -1)

				szDropdownName = str("WorldBuilderBrushSize")
				screen.addDropDownBoxGFC(szDropdownName, (iMaxScreenWidth-self.iScreenWidth)+48, (10+36+36), iPanelWidth-40, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
				screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_1_BY_1",()), 1, 1, self.m_iBrushSize == 1)
				screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_3_BY_3",()), 2, 2, self.m_iBrushSize == 2)
				screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_5_BY_5",()), 3, 3, self.m_iBrushSize == 3)
				screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_7_BY_7",()), 4, 4, self.m_iBrushSize== 4)

## Edit Area Map Start##
				szDropdownName = str("WorldBuilderEditAreaMap")
				screen.addDropDownBoxGFC(szDropdownName, (iMaxScreenWidth-self.iScreenWidth)+8, (10+ 36*3), iPanelWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
				screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_STANDARD_MODE",()), 0, 0, self.m_iPlotMode == 0)
				screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_PLOT_DATA_MODE",()), 2, 2, self.m_iPlotMode == 1)
				screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_CHANGE_AREA_PLOTS",()), 1, 1, self.m_iPlotMode == 2)
				screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_CHANGE_ALL_PLOTS",()), 2, 2, self.m_iPlotMode == 3)
				if self.m_iArea > -1 or  self.m_iPlotMode == 3:
					szDropdownName = str("WorldBuilderModifyAreaPlotType")
					screen.addDropDownBoxGFC(szDropdownName, (iMaxScreenWidth-self.iScreenWidth)+8, (10+ 36*4), iPanelWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
					screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_CHANGE_PLOTTYPE",()), 0, 0, True)
					screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_TERRAIN_PEAK",()), 0, 0, False)
					screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_TERRAIN_HILL",()), 0, 0, False)
					screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_LAND",()), 0, 0, False)
					screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_TERRAIN_OCEAN",()), 0, 0, False)

					szDropdownName = str("WorldBuilderModifyAreaTerrain")
					screen.addDropDownBoxGFC(szDropdownName, (iMaxScreenWidth-self.iScreenWidth)+8, (10+ 36*5), iPanelWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
					screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_CHANGE_TERRAIN",()), 0, 0, True )
					for i in xrange(gc.getNumTerrainInfos()):
						if gc.getTerrainInfo(i).isGraphicalOnly(): continue
						if self.m_iPlotMode == 3:
							screen.addPullDownString(szDropdownName, gc.getTerrainInfo(i).getDescription(), 0, 0, False)
						elif CyMap().getArea(self.m_iArea).isWater() and gc.getTerrainInfo(i).isWater():
							screen.addPullDownString(szDropdownName, gc.getTerrainInfo(i).getDescription(), 0, 0, False)
						elif not CyMap().getArea(self.m_iArea).isWater() and not gc.getTerrainInfo(i).isWater():
							screen.addPullDownString(szDropdownName, gc.getTerrainInfo(i).getDescription(), 0, 0, False)

					szDropdownName = str("WorldBuilderModifyAreaFeature")
					screen.addDropDownBoxGFC(szDropdownName, (iMaxScreenWidth-self.iScreenWidth)+8, (10+ 36*6), iPanelWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
					screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_CHANGE_FEATURE",()), 0, 0, True )
					for i in xrange(gc.getNumFeatureInfos()):
						screen.addPullDownString(szDropdownName, gc.getFeatureInfo(i).getDescription(), 0, 0, False)
					screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_CLEAR_ALL",()), 0, 0, False)

					if not CyMap().getArea(self.m_iArea).isWater():
						szDropdownName = str("WorldBuilderModifyAreaRoute")
						screen.addDropDownBoxGFC(szDropdownName, (iMaxScreenWidth-self.iScreenWidth)+8, (10+ 36*7), iPanelWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
						screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_CHANGE_ROUTE",()), 0, 0, True )
						for i in xrange(gc.getNumRouteInfos()):
							screen.addPullDownString(szDropdownName, gc.getRouteInfo(i).getDescription(), 0, 0, False)
						screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_CLEAR_ALL",()), 0, 0, False)

## Edit Area Map End ##
			elif(self.m_bReveal):
				iButtonWidth = 32
				iButtonHeight = 32
				iButtonX = 0
				iButtonY = 0
				screen.setImageButton( "WorldBuilderRevealAll", ArtFileMgr.getInterfaceArtInfo("WORLDBUILDER_REVEAL_ALL_TILES").getPath(), (iMaxScreenWidth-self.iScreenWidth)+8+iButtonX, (10+36+36), iButtonWidth, iButtonHeight, WidgetTypes.WIDGET_WB_REVEAL_ALL_BUTTON, -1, -1)
				iButtonX += 35
				screen.setImageButton( "WorldBuilderUnrevealAll", ArtFileMgr.getInterfaceArtInfo("WORLDBUILDER_UNREVEAL_ALL_TILES").getPath(), (iMaxScreenWidth-self.iScreenWidth)+8+iButtonX, (10+36+36), iButtonWidth, iButtonHeight, WidgetTypes.WIDGET_WB_UNREVEAL_ALL_BUTTON, -1, -1)
				iButtonX += 35

				szDropdownName = str("WorldBuilderBrushSize")
				screen.addDropDownBoxGFC(szDropdownName, (iMaxScreenWidth-self.iScreenWidth)+8+80, (10+ 36*2), iPanelWidth-80, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
				screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_1_BY_1",()), 1, 1, self.m_iBrushSize == 1)
				screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_3_BY_3",()), 2, 2, self.m_iBrushSize == 2)
				screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_5_BY_5",()), 3, 3, self.m_iBrushSize == 3)
				screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_7_BY_7",()), 4, 4, self.m_iBrushSize == 4)

				szDropdownName = str("WorldBuilderTeamChoice")
				screen.addDropDownBoxGFC(szDropdownName, (iMaxScreenWidth-self.iScreenWidth)+8, (10+ 36*3), iPanelWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
				for i in xrange(gc.getMAX_CIV_TEAMS()):
					if (gc.getTeam(i).isAlive()):
						screen.addPullDownString(szDropdownName, gc.getTeam(i).getName(), i, i, self.m_iCurrentTeam == i)
## Reveal Invisible Start##
				szDropdownName = str("WorldBuilderRevealMode")
				screen.addDropDownBoxGFC(szDropdownName, (iMaxScreenWidth-self.iScreenWidth)+8, (10+ 36*4), iPanelWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
				screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_REVEAL_SUBMARINE",()), 0, 0, self.m_iRevealMode == 0)
				screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_REVEAL_STEALTH",()), 1, 1, self.m_iRevealMode == 1)
				screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_REVEAL_PLOT",()), 2, 2, self.m_iRevealMode == 2)
## Reveal Invisible End ##
## Erase Multi Tiles Start ##
			elif(self.m_bEraseAll):
				iButtonWidth = 32
				iButtonHeight = 32
				self.m_tabCtrlEdit = getWBToolEditTabCtrl()
				screen.setImageButton( "WorldBuilderEraseAll", ArtFileMgr.getInterfaceArtInfo("WORLDBUILDER_UNREVEAL_ALL_TILES").getPath(), (iMaxScreenWidth-self.iScreenWidth)+8, (10+36+36), iButtonWidth, iButtonHeight, WidgetTypes.WIDGET_PYTHON, 1029, 1)

				szDropdownName = str("WorldBuilderBrushSize")
				screen.addDropDownBoxGFC(szDropdownName, (iMaxScreenWidth-self.iScreenWidth)+8+40, (10+ 36*2), iPanelWidth-40, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
				screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_1_BY_1",()), 1, 1, self.m_iBrushSize == 1)
				screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_3_BY_3",()), 2, 2, self.m_iBrushSize == 2)
				screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_5_BY_5",()), 3, 3, self.m_iBrushSize == 3)
				screen.addPullDownString(szDropdownName, localText.getText("TXT_KEY_WB_7_BY_7",()), 4, 4, self.m_iBrushSize == 4)
## Erase Multi Tiles End ##
			else:
				screen.deleteWidget("WorldBuilderBackgroundBottomPanel")

		return

## Platy Reveal Mode Start ##
	def revealAll(self, bReveal):
		for i in xrange (CyMap().getGridWidth()):
			for j in xrange (CyMap().getGridHeight()):
				pPlot = CyMap().plot(i,j)
				if (not pPlot.isNone()):
					if self.m_iRevealMode == 2:
						if bReveal or (not pPlot.isVisible(self.m_iCurrentTeam, False)):
							pPlot.setRevealed(self.m_iCurrentTeam, bReveal, False, -1);
					elif bReveal:
							pPlot.changeInvisibleVisibilityCount(self.m_iCurrentTeam, self.m_iRevealMode, 1)
					else:
						pPlot.changeInvisibleVisibilityCount(self.m_iCurrentTeam, self.m_iRevealMode, - pPlot.getInvisibleVisibilityCount(self.m_iCurrentTeam, self.m_iRevealMode))
		self.refreshReveal()
		return

	def RevealCurrentPlot(self, bReveal):
		if self.m_iRevealMode == 2:
			if bReveal or (not self.m_pCurrentPlot.isVisible(self.m_iCurrentTeam, False)):
				self.m_pCurrentPlot.setRevealed(self.m_iCurrentTeam, bReveal, False, -1);
		else:
			if bReveal or (not self.m_pCurrentPlot.isInvisibleVisible(self.m_iCurrentTeam, self.m_iRevealMode)):
				self.m_pCurrentPlot.changeInvisibleVisibilityCount(self.m_iCurrentTeam, self.m_iRevealMode, 1)
			if bReveal == False or (not self.m_pCurrentPlot.isInvisibleVisible(self.m_iCurrentTeam, self.m_iRevealMode)):
				self.m_pCurrentPlot.changeInvisibleVisibilityCount(self.m_iCurrentTeam, self.m_iRevealMode, - self.m_pCurrentPlot.getInvisibleVisibilityCount(self.m_iCurrentTeam, self.m_iRevealMode))
		return

	def showRevealed(self, pPlot):
		if self.m_iRevealMode == 2:
			if not pPlot.isRevealed(self.m_iCurrentTeam, False):
				CyEngine().fillAreaBorderPlotAlt(pPlot.getX(), pPlot.getY(), AreaBorderLayers.AREA_BORDER_LAYER_REVEALED_PLOTS, "COLOR_BLACK", 1.0)
		elif self.m_iRevealMode == 1:
			if pPlot.getInvisibleVisibilityCount(self.m_iCurrentTeam, self.m_iRevealMode) == 0:
				CyEngine().fillAreaBorderPlotAlt(pPlot.getX(), pPlot.getY(), AreaBorderLayers.AREA_BORDER_LAYER_REVEALED_PLOTS, "COLOR_RED", 1.0)
		elif self.m_iRevealMode == 0:
			if pPlot.getInvisibleVisibilityCount(self.m_iCurrentTeam, self.m_iRevealMode) == 0:
				CyEngine().fillAreaBorderPlotAlt(pPlot.getX(), pPlot.getY(), AreaBorderLayers.AREA_BORDER_LAYER_REVEALED_PLOTS, "COLOR_BLUE", 1.0)
		return
## Platy Reveal Mode End ##

	def Exit(self):
		CyInterface().setWorldBuilder(False)
		return

	def setLandmarkCB(self, szLandmark):
		self.m_pCurrentPlot = CyInterface().getMouseOverPlot()
		CyEngine().addLandmarkPopup(self.m_pCurrentPlot) # , u"%s" %(szLandmark))
		return

	def removeLandmarkCB(self):
		self.m_pCurrentPlot = CyInterface().getMouseOverPlot()
		CyEngine().removeLandmark(self.m_pCurrentPlot)
		return

	def refreshPlayerTabCtrl(self):

		initWBToolPlayerControl()

		self.m_normalPlayerTabCtrl = getWBToolNormalPlayerTabCtrl()

		self.m_normalPlayerTabCtrl.setNumColumns((gc.getNumUnitInfos()/10)+2);
		self.m_normalPlayerTabCtrl.addTabSection(localText.getText("TXT_KEY_WB_UNITS",()));
		self.m_iUnitTabID = 0
		self.m_iNormalPlayerCurrentIndexes.append(0)

		self.m_normalPlayerTabCtrl.setNumColumns((gc.getNumBuildingInfos()/10)+1);
		self.m_normalPlayerTabCtrl.addTabSection(localText.getText("TXT_KEY_WB_BUILDINGS",()));
		self.m_iBuildingTabID = 1
		self.m_iNormalPlayerCurrentIndexes.append(0)

		self.m_normalPlayerTabCtrl.setNumColumns((gc.getNumTechInfos()/10)+1);
		self.m_normalPlayerTabCtrl.addTabSection(localText.getText("TXT_KEY_WB_TECHNOLOGIES",()));
		self.m_iTechnologyTabID = 2
		self.m_iNormalPlayerCurrentIndexes.append(0)

		addWBPlayerControlTabs()
		return

	def refreshAdvancedStartTabCtrl(self, bReuse):
		if CyInterface().isInAdvancedStart():
			iActiveTab = 0
			iActiveList = 0
			iActiveIndex = 0

			if self.m_advancedStartTabCtrl and bReuse:
				iActiveTab = self.m_advancedStartTabCtrl.getActiveTab()
				iActiveList = self.m_iAdvancedStartCurrentList[iActiveTab]
				iActiveIndex = self.m_iAdvancedStartCurrentIndexes[iActiveTab]

			self.m_iCurrentPlayer = CyGame().getActivePlayer()
			self.m_iCurrentTeam = CyGame().getActiveTeam()
			self.m_iAdvancedStartCurrentIndexes = []
			self.m_iAdvancedStartCurrentList = []

			initWBToolAdvancedStartControl()

			self.m_advancedStartTabCtrl = getWBToolAdvancedStartTabCtrl()

			self.m_advancedStartTabCtrl.setNumColumns((gc.getNumBuildingInfos()/10)+2);
			self.m_advancedStartTabCtrl.addTabSection(localText.getText("TXT_KEY_WB_AS_CITIES",()));
			self.m_iASCityTabID = 0
			self.m_iAdvancedStartCurrentIndexes.append(0)

			self.m_iASCityListID = 0
			self.m_iASBuildingsListID = 2
			self.m_iASAutomateListID = 1
			self.m_iAdvancedStartCurrentList.append(self.m_iASCityListID)

			self.m_advancedStartTabCtrl.setNumColumns((gc.getNumUnitInfos()/10)+2);
			self.m_advancedStartTabCtrl.addTabSection(localText.getText("TXT_KEY_WB_AS_UNITS",()));
			self.m_iASUnitTabID = 1
			self.m_iAdvancedStartCurrentIndexes.append(0)

			self.m_iAdvancedStartCurrentList.append(0)
			self.m_iASUnitListID = 0

			self.m_advancedStartTabCtrl.setNumColumns((gc.getNumImprovementInfos()/10)+2);
			self.m_advancedStartTabCtrl.addTabSection(localText.getText("TXT_KEY_WB_AS_IMPROVEMENTS",()));
			self.m_iASImprovementsTabID = 2
			self.m_iAdvancedStartCurrentIndexes.append(0)

			self.m_iASRoutesListID = 0
			self.m_iASImprovementsListID = 1
			self.m_iAdvancedStartCurrentList.append(self.m_iASRoutesListID)

			self.m_advancedStartTabCtrl.setNumColumns(1);
			self.m_advancedStartTabCtrl.addTabSection(localText.getText("TXT_KEY_WB_AS_VISIBILITY",()));
			self.m_iASVisibilityTabID = 3
			self.m_iAdvancedStartCurrentIndexes.append(0)

			self.m_iAdvancedStartCurrentList.append(0)
			self.m_iASVisibilityListID = 0

			self.m_advancedStartTabCtrl.setNumColumns(1);
			self.m_advancedStartTabCtrl.addTabSection(localText.getText("TXT_KEY_WB_AS_TECH",()));
			self.m_iASTechTabID = 4
			self.m_iAdvancedStartCurrentIndexes.append(0)

			self.m_iAdvancedStartCurrentList.append(0)
			self.m_iASTechListID = 0

			addWBAdvancedStartControlTabs()

			self.m_advancedStartTabCtrl.setActiveTab(iActiveTab)
			self.setCurrentAdvancedStartIndex(iActiveIndex)
			self.setCurrentAdvancedStartList(iActiveList)
		else:

			self.m_advancedStartTabCtrl = getWBToolAdvancedStartTabCtrl()

			self.m_advancedStartTabCtrl.enable(False)

		return

	def eraseAll(self):
		# kill all units on plot if one is selected
		if self.m_pCurrentPlot != 0:
			while (self.m_pCurrentPlot.getNumUnits() > 0):
				pUnit = self.m_pCurrentPlot.getUnit(0)
				pUnit.kill(False, PlayerTypes.NO_PLAYER)

			self.m_pCurrentPlot.setBonusType(-1)
			self.m_pCurrentPlot.setFeatureType(FeatureTypes.NO_FEATURE, -1)
			if self.m_pCurrentPlot.isCity():
				self.m_pCurrentPlot.getPlotCity().kill()

			self.m_pCurrentPlot.setRouteType(-1)
			self.m_pCurrentPlot.setNOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
			self.m_pCurrentPlot.setWOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
			self.m_pCurrentPlot.setImprovementType(-1)
			self.removeLandmarkCB()
		return

## Edit Script ##
	def handleEditScriptCB ( self, argsList ) :
		iScriptData, strName = argsList
		if strName == "UnitEditScript":
			self.m_pActivePlot.getUnit(self.m_iCurrentUnit).setScriptData(str(iScriptData))
		elif strName == "CityEditScript":
			self.m_pActivePlot.getPlotCity().setScriptData(str(iScriptData))
		elif strName == "PlayerEditScript":
			gc.getPlayer(self.m_iCurrentPlayer).setScriptData(str(iScriptData))
		elif strName == "PlotEditScript":
			self.m_pScript = self.m_pActivePlot.setScriptData(str(iScriptData))
		elif strName == "GameEditScript":
			self.m_pScript = CyGame().setScriptData(str(iScriptData))
		return 1
## Edit Script ##

	def setRiverHighlights(self):
		CyEngine().clearColoredPlots(PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS)
		CyEngine().addColoredPlotAlt(self.m_pRiverStartPlot.getX(), self.m_pRiverStartPlot.getY(), PlotStyles.PLOT_STYLE_RIVER_SOUTH, PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS, "COLOR_GREEN", 1)

		fAlpha = .2
		CyEngine().addColoredPlotAlt(self.m_pRiverStartPlot.getX()-1, self.m_pRiverStartPlot.getY()+1, PlotStyles.PLOT_STYLE_BOX_FILL, PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS, "COLOR_WHITE", fAlpha)
		CyEngine().addColoredPlotAlt(self.m_pRiverStartPlot.getX(), self.m_pRiverStartPlot.getY()+1, PlotStyles.PLOT_STYLE_BOX_FILL, PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS, "COLOR_WHITE", fAlpha)
		CyEngine().addColoredPlotAlt(self.m_pRiverStartPlot.getX()+1, self.m_pRiverStartPlot.getY()+1, PlotStyles.PLOT_STYLE_BOX_FILL, PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS, "COLOR_WHITE", fAlpha)
		CyEngine().addColoredPlotAlt(self.m_pRiverStartPlot.getX()-1, self.m_pRiverStartPlot.getY(), PlotStyles.PLOT_STYLE_BOX_FILL, PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS, "COLOR_WHITE", fAlpha)

		CyEngine().addColoredPlotAlt(self.m_pRiverStartPlot.getX()+1, self.m_pRiverStartPlot.getY(), PlotStyles.PLOT_STYLE_BOX_FILL, PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS, "COLOR_WHITE", fAlpha)
		CyEngine().addColoredPlotAlt(self.m_pRiverStartPlot.getX()-1, self.m_pRiverStartPlot.getY()-1, PlotStyles.PLOT_STYLE_BOX_FILL, PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS, "COLOR_WHITE", fAlpha)
		CyEngine().addColoredPlotAlt(self.m_pRiverStartPlot.getX(), self.m_pRiverStartPlot.getY()-1, PlotStyles.PLOT_STYLE_BOX_FILL, PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS, "COLOR_WHITE", fAlpha)
		CyEngine().addColoredPlotAlt(self.m_pRiverStartPlot.getX()+1, self.m_pRiverStartPlot.getY()-1, PlotStyles.PLOT_STYLE_BOX_FILL, PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS, "COLOR_WHITE", fAlpha)
		return

	def setCurrentModeCheckbox(self, iButton):
		screen = CyGInterfaceScreen( "WorldBuilderScreen", CvScreenEnums.WORLDBUILDER_SCREEN )
		screen.setState("WorldBuilderUnitEditModeButton", iButton == self.m_iUnitEditCheckboxID)
		screen.setState("WorldBuilderCityEditModeButton", iButton == self.m_iCityEditCheckboxID)
		screen.setState("WorldBuilderNormalPlayerModeButton", iButton == self.m_iNormalPlayerCheckboxID)
		screen.setState("WorldBuilderNormalMapModeButton", iButton == self.m_iNormalMapCheckboxID)
		screen.setState("WorldBuilderRevealTileModeButton", iButton == self.m_iRevealTileCheckboxID)
		screen.setState("WorldBuilderDiplomacyModeButton", iButton == self.m_iDiplomacyCheckboxID)
		screen.setState("WorldBuilderLandmarkButton", iButton == self.m_iLandmarkCheckboxID)
		screen.setState("WorldBuilderEraseButton", iButton == self.m_iEraseCheckboxID)
		return

	def initVars(self):
		self.m_normalPlayerTabCtrl = 0
		self.m_normalMapTabCtrl = 0
		self.m_tabCtrlEdit = 0
		self.m_bCtrlEditUp = False
		self.m_bUnitEdit = False
		self.m_bCityEdit = False
		self.m_bNormalPlayer = True
		self.m_bNormalMap = False
		self.m_bReveal = False
		self.m_bLandmark = False
		self.m_bEraseAll = False
		self.m_bShowBigBrush = False
		self.m_bLeftMouseDown = False
		self.m_bRightMouseDown = False
		self.m_bChangeFocus = False
		self.m_iNormalPlayerCurrentIndexes = []
		self.m_iNormalMapCurrentIndexes = []
		self.m_iNormalMapCurrentList = []
		self.m_iCurrentPlayer = 0
		self.m_iCurrentTeam = 0
		self.m_iCurrentUnit = 0
		self.m_iCurrentX = -1
		self.m_iCurrentY = -1
		self.m_pCurrentPlot = 0
		self.m_pActivePlot = 0
		self.m_pRiverStartPlot = -1
		self.m_iUnitTabID = -1
		self.m_iBuildingTabID = -1
		self.m_iTechnologyTabID = -1
		self.m_iImprovementTabID = -1
		self.m_iBonusTabID = -1
		self.m_iImprovementListID = -1
		self.m_iBonusListID = -1
		self.m_iTerrainTabID = -1
		self.m_iTerrainListID = -1
		self.m_iFeatureListID = -1
		self.m_iPlotTypeListID = -1
		self.m_iRouteListID = -1
		self.m_iTerritoryTabID = -1
		self.m_iTerritoryListID = -1
		self.m_iBrushSizeTabID = -1
		self.m_iUnitEditCheckboxID = -1
		self.m_iCityEditCheckboxID = -1
		self.m_iNormalPlayerCheckboxID = -1
		self.m_iNormalMapCheckboxID = -1
		self.m_iRevealTileCheckboxID = -1
		self.m_iDiplomacyCheckboxID = -1
		self.m_iLandmarkCheckboxID = -1
		self.m_iEraseCheckboxID = -1
		self.iScreenWidth = 228

## Platy Builder ##
		self.m_iNewCivilization = -1
		self.m_iNewLeaderType = -1
		self.m_iImprovement = 0
		self.m_iYield = 0
		self.m_iDomain = 0
		self.m_iRoute = 0
		self.m_pScript = -1
		self.m_bMoveUnit = False
		self.m_iUnitCombat = -99
		self.m_iUnitType = -1
		self.m_iPlotMode = 0
		self.m_iArea = -1
		self.m_iCityTimer = 0
		self.m_iOtherPlayer = -1
		self.m_iEventUnit = -1
		self.m_iBuildingClass = 0
		self.m_iBuildingModifier = 0
		self.m_iRevealMode = 2
		self.m_iBrushSize = 1
		self.m_iVisibleOption = 1
		self.m_iAddUnitCount = 1
## Platy Builder ##
		return
