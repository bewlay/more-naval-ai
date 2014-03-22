from CvPythonExtensions import *
import CvUtil
import CvScreensInterface
import ScreenInput
import CvEventInterface
import CvScreenEnums
import time
import WBPlotScreen
import WBCityEditScreen
import WBPlayerScreen
import WBUnitScreen
import WBGameDataScreen
import Popup
gc = CyGlobalContext()
iChange = 1

class CvWorldBuilderScreen:

	def __init__ (self) :
		self.m_advancedStartTabCtrl = None
		self.m_bNormalPlayer = True
		self.m_bNormalMap = False
		self.m_bReveal = False
		self.m_bShowBigBrush = False
		self.m_bChangeFocus = False
		self.m_iAdvancedStartCurrentIndexes = []
		self.m_iAdvancedStartCurrentList = []
		self.m_iCurrentPlayer = 0
		self.m_iCurrentTeam = 0
		self.m_iCurrentX = -1
		self.m_iCurrentY = -1
		self.m_pCurrentPlot = 0
		self.m_pRiverStartPlot = -1
		
		self.m_iASUnitTabID = 1
		self.m_iASUnitListID = 0
		self.m_iASCityTabID = 0
		self.m_iASCityListID = 0
		self.m_iASBuildingsListID = 2
		self.m_iASAutomateListID = 1
		self.m_iASImprovementsTabID = 2
		self.m_iASRoutesListID = 0
		self.m_iASImprovementsListID = 1
		self.m_iASVisibilityTabID = 3
		self.m_iASVisibilityListID = 0
		self.m_iASTechTabID = 4
		self.m_iASTechListID = 0
		self.iScreenWidth = 228
		
		self.m_bSideMenuDirty = false
		self.m_bASItemCostDirty = false
		self.m_iCost = 0

## Platy Builder ##
		self.m_iRevealMode = 2
		self.m_iBrushSize = 1
		self.iPlayerAddMode = "Units"
		self.iSelection = -1
		self.iSelectClass = -2
		self.m_lMoveUnit = []
## Platy Builder ##

	def interfaceScreen (self):
		screen = CyGInterfaceScreen( "WorldBuilderScreen", CvScreenEnums.WORLDBUILDER_SCREEN )
		self.__init__()
		screen.setCloseOnEscape(False)
		screen.setAlwaysShown(True)
		self.setSideMenu()
		self.refreshSideMenu()
		self.refreshAdvancedStartTabCtrl(false)
		
		if CyInterface().isInAdvancedStart():
			pPlayer = gc.getPlayer(self.m_iCurrentPlayer)
			pPlot = pPlayer.getStartingPlot()
			CyCamera().JustLookAtPlot(pPlot)
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, True)
		screen.setForcedRedraw( True )

	def killScreen(self):			
		screen = CyGInterfaceScreen( "WorldBuilderScreen", CvScreenEnums.WORLDBUILDER_SCREEN )
		screen.hideScreen()
		CyEngine().clearColoredPlots(PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS)
		CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_REVEALED_PLOTS)
		CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_WORLD_BUILDER)
		CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_HIGHLIGHT_PLOT)

	def mouseOverPlot (self, argsList):
		self.m_pCurrentPlot = CyInterface().getMouseOverPlot()
		if self.m_bReveal:
			if CyInterface().isLeftMouseDown():
				self.setMultipleReveal(True)
			elif CyInterface().isRightMouseDown():
				self.setMultipleReveal(False)
		else:
			self.m_iCurrentX = self.m_pCurrentPlot.getX()
			self.m_iCurrentY = self.m_pCurrentPlot.getY()
			if CyInterface().isLeftMouseDown():
				if self.useLargeBrush():
					self.placeMultipleObjects()
				else:
					self.placeObject()
			elif CyInterface().isRightMouseDown():
				if self.iPlayerAddMode != "EditCity" and self.iPlayerAddMode != "EditUnit":
					if self.useLargeBrush():
						self.removeMultipleObjects()
					else:
						self.removeObject()
		return

	def getHighlightPlot (self, argsList):
		self.refreshASItemCost()
		if self.m_pCurrentPlot != 0:
			if CyInterface().isInAdvancedStart():
				if self.m_iCost <= 0:
					return []
				
		if ((self.m_pCurrentPlot != 0) and not self.m_bShowBigBrush and isMouseOverGameSurface()):
			return (self.m_pCurrentPlot.getX(), self.m_pCurrentPlot.getY())
		return []

	def update(self, fDelta):
		if (not self.m_bChangeFocus) and (not isMouseOverGameSurface()):
			self.m_bChangeFocus = True
		if (self.m_bChangeFocus and isMouseOverGameSurface() and (self.iPlayerAddMode != "EditUnit" and self.iPlayerAddMode != "EditCity")):
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
			self.refreshAdvancedStartTabCtrl(true)
			CyInterface().setDirty(InterfaceDirtyBits.Advanced_Start_DIRTY_BIT, false)
		
		self.m_bShowBigBrush = self.useLargeBrush()
		if self.iPlayerAddMode == "River":
			if self.m_pRiverStartPlot != -1:
				self.setRiverHighlights()
				return 0
		self.highlightBrush()
		return 0

	def refreshReveal ( self ) :
		CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_REVEALED_PLOTS)
		for i in xrange(CyMap().numPlots()):
			pPlot = CyMap().plotByIndex(i)
			if pPlot.isNone(): continue
			self.showRevealed(pPlot)
		return 1

## Platy World Builder Start ##
	
	########################################################
	### Advanced Start Stuff
	########################################################
	
	def refreshASItemCost(self):
		if (CyInterface().isInAdvancedStart()):
			self.m_iCost = 0
			if (self.m_pCurrentPlot != 0):
				if (self.m_pCurrentPlot.isRevealed(CyGame().getActiveTeam(), false)):
					
					# Unit mode
					if (self.getASActiveUnit() != -1):
						self.m_iCost = gc.getPlayer(self.m_iCurrentPlayer).getAdvancedStartUnitCost(self.getASActiveUnit(), true, self.m_pCurrentPlot)
					elif (self.getASActiveCity() != -1):
						self.m_iCost = gc.getPlayer(self.m_iCurrentPlayer).getAdvancedStartCityCost(true, self.m_pCurrentPlot)
					elif (self.getASActivePop() != -1 and self.m_pCurrentPlot.isCity()):
						self.m_iCost = gc.getPlayer(self.m_iCurrentPlayer).getAdvancedStartPopCost(true, self.m_pCurrentPlot.getPlotCity())
					elif (self.getASActiveCulture() != -1 and self.m_pCurrentPlot.isCity()):
						self.m_iCost = gc.getPlayer(self.m_iCurrentPlayer).getAdvancedStartCultureCost(true, self.m_pCurrentPlot.getPlotCity())
					elif (self.getASActiveBuilding() != -1 and self.m_pCurrentPlot.isCity()):
						self.m_iCost = gc.getPlayer(self.m_iCurrentPlayer).getAdvancedStartBuildingCost(self.getASActiveBuilding(), true, self.m_pCurrentPlot.getPlotCity())
					elif (self.getASActiveRoute() != -1):
						self.m_iCost = gc.getPlayer(self.m_iCurrentPlayer).getAdvancedStartRouteCost(self.getASActiveRoute(), true, self.m_pCurrentPlot)
					elif (self.getASActiveImprovement() != -1):
						self.m_iCost = gc.getPlayer(self.m_iCurrentPlayer).getAdvancedStartImprovementCost(self.getASActiveImprovement(), true, self.m_pCurrentPlot)
						
				elif (self.m_pCurrentPlot.isAdjacentNonrevealed(CyGame().getActiveTeam())):
					if (self.getASActiveVisibility() != -1):
						self.m_iCost = gc.getPlayer(self.m_iCurrentPlayer).getAdvancedStartVisibilityCost(true, self.m_pCurrentPlot)
			self.m_iCost = max(0, self.m_iCost)
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
		if self.m_iCurrentX == -1 or self.m_iCurrentY == -1: return
		if CyInterface().isInAdvancedStart():
			pPlayer = gc.getPlayer(self.m_iCurrentPlayer)
			pPlot = CyMap().plot(self.m_iCurrentX, self.m_iCurrentY)
			iActiveTeam = CyGame().getActiveTeam()
			if (self.m_pCurrentPlot.isRevealed(iActiveTeam, false)):
				# City Tab
				if (self.m_advancedStartTabCtrl.getActiveTab() == self.m_iASCityTabID):
					# City List
					if (self.m_iAdvancedStartCurrentList[self.m_advancedStartTabCtrl.getActiveTab()] == self.m_iASCityListID):
						iOptionID = self.m_iAdvancedStartCurrentIndexes[self.m_advancedStartTabCtrl.getActiveTab()]
						# Place City
						if (iOptionID == 0):
							if (pPlayer.getAdvancedStartCityCost(true, pPlot) != -1):
								CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_CITY, self.m_iCurrentPlayer, self.m_iCurrentX, self.m_iCurrentY, -1, true)	#Action, Player, X, Y, Data, bAdd
						
						# City Population
						elif (iOptionID == 1):
							if (pPlot.isCity()):
								pCity = pPlot.getPlotCity()
								if (pPlayer.getAdvancedStartPopCost(true, pCity) != -1):
									CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_POP, self.m_iCurrentPlayer, self.m_iCurrentX, self.m_iCurrentY, -1, true)	#Action, Player, X, Y, Data, bAdd
						
						# City Culture
						elif (iOptionID == 2):
							if (pPlot.isCity()):
								pCity = pPlot.getPlotCity()
								if (pPlayer.getAdvancedStartCultureCost(true, pCity) != -1):
									CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_CULTURE, self.m_iCurrentPlayer, self.m_iCurrentX, self.m_iCurrentY, -1, true)	#Action, Player, X, Y, Data, bAdd
										
					# Buildings List
					elif (self.m_iAdvancedStartCurrentList[self.m_advancedStartTabCtrl.getActiveTab()] == self.m_iASBuildingsListID):
							if (pPlot.isCity()):
								pCity = pPlot.getPlotCity()
								iBuildingType = getASBuilding(self.m_iAdvancedStartCurrentIndexes[self.m_advancedStartTabCtrl.getActiveTab()])
								if (iBuildingType != -1 and pPlayer.getAdvancedStartBuildingCost(iBuildingType, true, pCity) != -1):
									CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_BUILDING, self.m_iCurrentPlayer, self.m_iCurrentX, self.m_iCurrentY, iBuildingType, true)	#Action, Player, X, Y, Data, bAdd
				
				# Unit Tab
				elif (self.m_advancedStartTabCtrl.getActiveTab() == self.m_iASUnitTabID):
					iUnitType = getASUnit(self.m_iAdvancedStartCurrentIndexes[self.m_advancedStartTabCtrl.getActiveTab()])
					if (iUnitType != -1 and pPlayer.getAdvancedStartUnitCost(iUnitType, true, pPlot) != -1):
						CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_UNIT, self.m_iCurrentPlayer, self.m_iCurrentX, self.m_iCurrentY, iUnitType, true)	#Action, Player, X, Y, Data, bAdd
							
				# Improvements Tab
				elif (self.m_advancedStartTabCtrl.getActiveTab() == self.m_iASImprovementsTabID):
					# Routes List
					if (self.m_iAdvancedStartCurrentList[self.m_advancedStartTabCtrl.getActiveTab()] == self.m_iASRoutesListID):
						iRouteType = getASRoute(self.m_iAdvancedStartCurrentIndexes[self.m_advancedStartTabCtrl.getActiveTab()])
						if (iRouteType != -1 and pPlayer.getAdvancedStartRouteCost(iRouteType, true, pPlot) != -1):
							CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_ROUTE, self.m_iCurrentPlayer, self.m_iCurrentX, self.m_iCurrentY, iRouteType, true)	#Action, Player, X, Y, Data, bAdd
					
					# Improvements List
					elif (self.m_iAdvancedStartCurrentList[self.m_advancedStartTabCtrl.getActiveTab()] == self.m_iASImprovementsListID):
						iImprovementType = getASImprovement(self.m_iAdvancedStartCurrentIndexes[self.m_advancedStartTabCtrl.getActiveTab()])
						if (pPlayer.getAdvancedStartImprovementCost(iImprovementType, true, pPlot) != -1):
							CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_IMPROVEMENT, self.m_iCurrentPlayer, self.m_iCurrentX, self.m_iCurrentY, iImprovementType, true)	#Action, Player, X, Y, Data, bAdd
							
			# Adjacent nonrevealed
			else:
				# Visibility Tab
				if (self.m_advancedStartTabCtrl.getActiveTab() == self.m_iASVisibilityTabID):
					if (pPlayer.getAdvancedStartVisibilityCost(true, pPlot) != -1):
						CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_VISIBILITY, self.m_iCurrentPlayer, self.m_iCurrentX, self.m_iCurrentY, -1, true)	#Action, Player, X, Y, Data, bAdd
			self.m_bSideMenuDirty = true
			self.m_bASItemCostDirty = true
			return 1

		if self.iPlayerAddMode == "EraseAll":
			self.m_pCurrentPlot.erase()
			CyEngine().removeLandmark(self.m_pCurrentPlot)
			for iPlayerX in xrange(gc.getMAX_PLAYERS()):
				CyEngine().removeSign(self.m_pCurrentPlot, iPlayerX)
		elif self.iPlayerAddMode == "AddLandMark":
			iIndex = -1
			for i in xrange(CyEngine().getNumSigns()):
				pSign = CyEngine().getSignByIndex(i)
				if pSign.getPlot().getX() != self.m_pCurrentPlot.getX(): continue
				if pSign.getPlot().getY() != self.m_pCurrentPlot.getY(): continue
				if pSign.getPlayerType() == self.m_iCurrentPlayer:
					iIndex = i
					break
			sText = ""
			if iIndex > -1:
				sText = CyEngine().getSignByIndex(iIndex).getCaption()
			popup = Popup.PyPopup(CvUtil.EventWBLandmarkPopup, EventContextTypes.EVENTCONTEXT_ALL)
			popup.setHeaderString(CyTranslator().getText("TXT_KEY_WB_EDIT_SIGN", ()))
			popup.setUserData((self.m_pCurrentPlot.getX(), self.m_pCurrentPlot.getY(), self.m_iCurrentPlayer, iIndex))
			popup.createEditBox(sText)
			popup.launch()
		elif self.iSelection == -1: return
		elif self.iPlayerAddMode == "Ownership":
			self.m_pCurrentPlot.setOwner(self.m_iCurrentPlayer)
		elif self.iPlayerAddMode == "Units":
			for i in xrange(iChange):
				gc.getPlayer(self.m_iCurrentPlayer).initUnit(self.iSelection, self.m_pCurrentPlot.getX(), self.m_pCurrentPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.NO_DIRECTION)
		elif self.iPlayerAddMode == "Buildings":
			if self.m_pCurrentPlot.isCity():
				self.m_pCurrentPlot.getPlotCity().setNumRealBuilding(self.iSelection, 1)
		elif self.iPlayerAddMode == "City":
			if self.m_pCurrentPlot.isCity(): return
			gc.getPlayer(self.m_iCurrentPlayer).initCity(self.m_pCurrentPlot.getX(), self.m_pCurrentPlot.getY())
		elif self.iPlayerAddMode == "Improvements":
			self.m_pCurrentPlot.setImprovementType(self.iSelection)
		elif self.iPlayerAddMode == "Bonus":
			self.m_pCurrentPlot.setBonusType(self.iSelection)
		elif self.iPlayerAddMode == "Routes":
			self.m_pCurrentPlot.setRouteType(self.iSelection)
		elif self.iPlayerAddMode == "Terrain":
			self.m_pCurrentPlot.setTerrainType(self.iSelection, True, True)
		elif self.iPlayerAddMode == "PlotType":
			if self.iSelection == gc.getInfoTypeForString("TERRAIN_PEAK"):
				self.m_pCurrentPlot.setPlotType(PlotTypes.PLOT_PEAK, True, True)
			elif self.iSelection == gc.getInfoTypeForString("TERRAIN_HILL"):
				self.m_pCurrentPlot.setPlotType(PlotTypes.PLOT_HILLS, True, True)
			elif self.iSelection == gc.getInfoTypeForString("TERRAIN_GRASS"):
				self.m_pCurrentPlot.setPlotType(PlotTypes.PLOT_LAND, True, True)
			elif self.iSelection == gc.getInfoTypeForString("TERRAIN_OCEAN"):
				self.m_pCurrentPlot.setPlotType(PlotTypes.PLOT_OCEAN, True, True)
		elif self.iPlayerAddMode == "Features":
			self.m_pCurrentPlot.setFeatureType(self.iSelection, self.iSelectClass)
		elif self.iPlayerAddMode == "River":
			if self.m_pRiverStartPlot == self.m_pCurrentPlot:
				self.m_pRiverStartPlot = -1
				CyEngine().clearColoredPlots(PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS)
			elif self.m_pRiverStartPlot != -1:
				iXDiff = abs(self.m_pCurrentPlot.getX() - self.m_pRiverStartPlot.getX())
				iYDiff = abs(self.m_pCurrentPlot.getY() - self.m_pRiverStartPlot.getY())

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
		return 1

	def removeObject( self ):
		if self.m_iCurrentX == -1 or self.m_iCurrentY == -1: return
		# Advanced Start
		if CyInterface().isInAdvancedStart():
			pPlayer = gc.getPlayer(self.m_iCurrentPlayer)
			pPlot = CyMap().plot(self.m_iCurrentX, self.m_iCurrentY)
			iActiveTeam = CyGame().getActiveTeam()
			if self.m_pCurrentPlot.isRevealed(iActiveTeam, false):		
				# City Tab
				if (self.m_advancedStartTabCtrl.getActiveTab() == self.m_iASCityTabID):
					# City List
					if (self.m_iAdvancedStartCurrentList[self.m_advancedStartTabCtrl.getActiveTab()] == self.m_iASCityListID):
						iOptionID = self.m_iAdvancedStartCurrentIndexes[self.m_advancedStartTabCtrl.getActiveTab()]
						# City Population
						if (iOptionID == 1):
							if (pPlot.isCity()):
								if (pPlot.getPlotCity().getOwner() == self.m_iCurrentPlayer):
									CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_POP, self.m_iCurrentPlayer, self.m_iCurrentX, self.m_iCurrentY, -1, false)	#Action, Player, X, Y, Data, bAdd
						
					# Buildings List
					elif (self.m_iAdvancedStartCurrentList[self.m_advancedStartTabCtrl.getActiveTab()] == self.m_iASBuildingsListID):
						if (pPlot.isCity()):
							if (pPlot.getPlotCity().getOwner() == self.m_iCurrentPlayer):
								iBuildingType = getASBuilding(self.m_iAdvancedStartCurrentIndexes[self.m_advancedStartTabCtrl.getActiveTab()])
								if -1 != iBuildingType:
									CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_BUILDING, self.m_iCurrentPlayer, self.m_iCurrentX, self.m_iCurrentY, iBuildingType, false)	#Action, Player, X, Y, Data, bAdd
				
				# Unit Tab
				elif (self.m_advancedStartTabCtrl.getActiveTab() == self.m_iASUnitTabID):
					iUnitType = getASUnit(self.m_iAdvancedStartCurrentIndexes[self.m_advancedStartTabCtrl.getActiveTab()])
					if -1 != iUnitType:
						CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_UNIT, self.m_iCurrentPlayer, self.m_pCurrentPlot.getX(), self.m_pCurrentPlot.getY(), iUnitType, false)	#Action, Player, X, Y, Data, bAdd
							
				# Improvements Tab
				elif (self.m_advancedStartTabCtrl.getActiveTab() == self.m_iASImprovementsTabID):
					# Routes List
					if (self.m_iAdvancedStartCurrentList[self.m_advancedStartTabCtrl.getActiveTab()] == self.m_iASRoutesListID):
						iRouteType = getASRoute(self.m_iAdvancedStartCurrentIndexes[self.m_advancedStartTabCtrl.getActiveTab()])
						if -1 != iRouteType:
							CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_ROUTE, self.m_iCurrentPlayer, self.m_iCurrentX, self.m_iCurrentY, iRouteType, false)	#Action, Player, X, Y, Data, bAdd
					
					# Improvements List
					elif (self.m_iAdvancedStartCurrentList[self.m_advancedStartTabCtrl.getActiveTab()] == self.m_iASImprovementsListID):
						iImprovementType = getASImprovement(self.m_iAdvancedStartCurrentIndexes[self.m_advancedStartTabCtrl.getActiveTab()])
						if -1 != iImprovementType:
							CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_IMPROVEMENT, self.m_iCurrentPlayer, self.m_iCurrentX, self.m_iCurrentY, iImprovementType, false)	#Action, Player, X, Y, Data, bAdd
						
			# Adjacent nonrevealed
			else:
				# Visibility Tab
				if (self.m_advancedStartTabCtrl.getActiveTab() == self.m_iASVisibilityTabID):
					return 1
			self.m_bSideMenuDirty = true
			self.m_bASItemCostDirty = true
			return 1

		if self.iPlayerAddMode == "EraseAll":
			self.m_pCurrentPlot.erase()
			CyEngine().removeLandmark(self.m_pCurrentPlot)
			for iPlayerX in xrange(gc.getMAX_PLAYERS()):
				CyEngine().removeSign(self.m_pCurrentPlot, iPlayerX)
		elif self.iPlayerAddMode == "Ownership":
			self.m_pCurrentPlot.setOwner(-1)
		elif self.iPlayerAddMode == "Units":
			for i in xrange (self.m_pCurrentPlot.getNumUnits()):
				pUnit = self.m_pCurrentPlot.getUnit(i)
				if pUnit.getUnitType() == self.iSelection:
					pUnit.kill(false, PlayerTypes.NO_PLAYER)
					return 1
			if self.m_pCurrentPlot.getNumUnits() > 0:
				pUnit = self.m_pCurrentPlot.getUnit(0)
				pUnit.kill(false, PlayerTypes.NO_PLAYER)
				return 1
		elif self.iPlayerAddMode == "Buildings":
			if self.m_pCurrentPlot.isCity():
				self.m_pCurrentPlot.getPlotCity().setNumRealBuilding(self.iSelection, 0)
		elif self.iPlayerAddMode == "City":
			if self.m_pCurrentPlot.isCity():
				self.m_pCurrentPlot.getPlotCity().kill()
		elif self.iPlayerAddMode == "Improvements":
			self.m_pCurrentPlot.setImprovementType(-1)
			return 1
		elif self.iPlayerAddMode == "Bonus":
			self.m_pCurrentPlot.setBonusType(-1)
			return 1
		elif self.iPlayerAddMode == "Features":
			self.m_pCurrentPlot.setFeatureType(FeatureTypes.NO_FEATURE, -1)
		elif self.iPlayerAddMode == "Routes":
			self.m_pCurrentPlot.setRouteType(-1)
		elif self.iPlayerAddMode == "River":
			if self.m_pRiverStartPlot != -1:
				self.m_pRiverStartPlot = -1
				CyEngine().clearColoredPlots(PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS)
			else:
				self.m_pCurrentPlot.setNOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
				self.m_pCurrentPlot.setWOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
		elif self.iPlayerAddMode == "AddLandMark":
			CyEngine().removeSign(self.m_pCurrentPlot, self.m_iCurrentPlayer)
		return 1
		
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

	def toggleUnitEditCB(self):
		self.m_bNormalPlayer = False
		self.m_bNormalMap = False
		self.m_bReveal = False
		self.iPlayerAddMode = "EditUnit"
		self.refreshSideMenu()
		return

	def normalPlayerTabModeCB(self):
		self.m_bNormalPlayer = True
		self.m_bNormalMap = False
		self.m_bReveal = False
		self.m_iCurrentTeam = gc.getPlayer(self.m_iCurrentPlayer).getTeam()
		self.iPlayerAddMode = "Units"
		self.iSelectClass = -2
		self.iSelection = -1
		self.refreshSideMenu()
		getWBToolNormalPlayerTabCtrl().enable(False)
		getWBToolNormalMapTabCtrl().enable(False)
		return

	def normalMapTabModeCB(self):
		self.m_bNormalPlayer = False
		self.m_bNormalMap = True
		self.m_bReveal = False
		self.iPlayerAddMode = "PlotData"
		self.refreshSideMenu()
		return

	def revealTabModeCB(self):
		self.m_bNormalPlayer = False
		self.m_bNormalMap = False
		self.m_bReveal = True
		self.iPlayerAddMode = 0
		self.refreshSideMenu()
		self.refreshReveal()
		return

	def toggleCityEditCB(self):
		self.m_bNormalPlayer = False
		self.m_bNormalMap = False
		self.m_bReveal = False
		self.iPlayerAddMode = "EditCity"
		self.refreshSideMenu()
		return

	def landmarkModeCB(self):
		self.iPlayerAddMode = "AddLandMark"
		self.m_iCurrentPlayer = gc.getBARBARIAN_PLAYER()
		self.refreshSideMenu()
		return

	def eraseCB(self):
		self.m_bNormalPlayer = False
		self.m_bNormalMap = False
		self.m_bReveal = False
		self.m_pRiverStartPlot = -1
		self.iPlayerAddMode = "EraseAll"
		self.refreshSideMenu()
		return

	def setCurrentAdvancedStartIndex(self, argsList):
		iIndex = int(argsList)
		self.m_iAdvancedStartCurrentIndexes [self.m_advancedStartTabCtrl.getActiveTab()] = int(argsList)
		return 1

	def setCurrentAdvancedStartList(self, argsList):
		self.m_iAdvancedStartCurrentList[self.m_advancedStartTabCtrl.getActiveTab()] = int(argsList)
		return 1

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
		if self.m_bShowBigBrush:
			if self.m_pCurrentPlot == 0: return
			CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_WORLD_BUILDER)
			for x in range(self.m_pCurrentPlot.getX() - self.m_iBrushSize +1, self.m_pCurrentPlot.getX() + self.m_iBrushSize):
				for y in range(self.m_pCurrentPlot.getY() - self.m_iBrushSize +1, self.m_pCurrentPlot.getY() + self.m_iBrushSize):
					pPlot = CyMap().plot(x,y)
					if pPlot.isNone(): continue
					CyEngine().fillAreaBorderPlotAlt(pPlot.getX(), pPlot.getY(), AreaBorderLayers.AREA_BORDER_LAYER_WORLD_BUILDER, "COLOR_GREEN", 1)
		return

	def placeMultipleObjects(self):
		permCurrentPlot = self.m_pCurrentPlot
		for x in range(permCurrentPlot.getX() - self.m_iBrushSize +1, permCurrentPlot.getX() + self.m_iBrushSize):
			for y in range(permCurrentPlot.getY() - self.m_iBrushSize +1, permCurrentPlot.getY() + self.m_iBrushSize):
				self.m_pCurrentPlot = CyMap().plot(x,y)
				if self.m_pCurrentPlot.isNone(): continue
				if self.m_iBrushSize > 1:
					if self.iPlayerAddMode == "Improvements":
						if self.m_pCurrentPlot.canHaveImprovement(self.iSelection, -1, True):
							self.placeObject()
					elif self.iPlayerAddMode == "Bonus":
						iOldBonus = self.m_pCurrentPlot.getBonusType(-1)
						self.m_pCurrentPlot.setBonusType(-1)
						if self.m_pCurrentPlot.canHaveBonus(self.iSelection, False):
							self.placeObject()
						else:
							self.m_pCurrentPlot.setBonusType(iOldBonus)
					elif self.iPlayerAddMode == "Features":
						iOldFeature = self.m_pCurrentPlot.getFeatureType()
						iOldVariety = self.m_pCurrentPlot.getFeatureVariety()
						self.m_pCurrentPlot.setFeatureType(-1, 0)
						if self.m_pCurrentPlot.canHaveFeature(self.iSelection):
							self.placeObject()
						else:
							self.m_pCurrentPlot.setFeatureType(iOldFeature, iOldVariety)
					elif self.iPlayerAddMode == "Routes":
						if not (self.m_pCurrentPlot.isImpassable() or self.m_pCurrentPlot.isWater()):
							self.placeObject()
					elif self.iPlayerAddMode == "Terrain":
						if self.m_pCurrentPlot.isWater() == gc.getTerrainInfo(self.iSelection).isWater():
							self.placeObject()
					elif self.iPlayerAddMode == "PlotType":
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
				if self.m_pCurrentPlot.isNone(): continue
				self.removeObject()
		self.m_pCurrentPlot = permCurrentPlot
		return

	def setMultipleReveal(self, bReveal):
		print "setMultipleReveal"
		for x in xrange(self.m_pCurrentPlot.getX() - self.m_iBrushSize +1, self.m_pCurrentPlot.getX() + self.m_iBrushSize):
			for y in xrange(self.m_pCurrentPlot.getY() - self.m_iBrushSize +1, self.m_pCurrentPlot.getY() + self.m_iBrushSize):
				pPlot = CyMap().plot(x,y)
				if pPlot.isNone(): continue
				self.RevealCurrentPlot(bReveal, pPlot)
		self.refreshReveal()
		return

	def useLargeBrush(self):
		if self.m_bReveal:
			return True
		if self.iPlayerAddMode == "EraseAll":
			return True
		if self.iPlayerAddMode == "Improvements":
			return True
		if self.iPlayerAddMode == "Bonus":
			return True
		if self.iPlayerAddMode == "PlotType":
			return True
		if self.iPlayerAddMode == "Terrain":
			return True
		if self.iPlayerAddMode == "Routes":
			return True
		if self.iPlayerAddMode == "Features":
			return True
		return False
## Platy Multi Tile End ##

	def setSideMenu(self):
		screen = CyGInterfaceScreen( "WorldBuilderScreen", CvScreenEnums.WORLDBUILDER_SCREEN )
		iScreenHeight = 10+37+37
		iButtonWidth = 32

		iX = screen.getXResolution() - self.iScreenWidth
		if (CyInterface().isInAdvancedStart()):
			iX = 0
			
		screen.addPanel( "WorldBuilderBackgroundPanel", "", "", True, True, iX, 0, self.iScreenWidth, iScreenHeight, PanelStyles.PANEL_STYLE_MAIN )
				
		if CyInterface().isInAdvancedStart():
									
			iX = 50
			iY = 15
			szText = u"<font=4>" + CyTranslator().getText("TXT_KEY_WB_AS_POINTS", (gc.getPlayer(CyGame().getActivePlayer()).getAdvancedStartPoints(), )) + "</font>"
			screen.setLabel("AdvancedStartPointsText", "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, iX, iY, -2, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
			
			iY += 30
			szText = CyTranslator().getText("TXT_KEY_ADVANCED_START_BEGIN_GAME", ())
			screen.setButtonGFC( "WorldBuilderExitButton", szText, "", iX, iY, 130, 28, WidgetTypes.WIDGET_WB_EXIT_BUTTON, -1, -1, ButtonStyles.BUTTON_STYLE_STANDARD )

			szText = u"<font=4>" + CyTranslator().getText("TXT_KEY_WB_AS_COST_THIS_LOCATION", (self.m_iCost, )) + u"</font>"
			iY = 85
			screen.setLabel("AdvancedStartCostText", "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, iX-20, iY, -2, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
			
		else:
			iX = screen.getXResolution() - self.iScreenWidth + 8
			iY = 46
			screen.addCheckBoxGFC("WorldBuilderUnitEditModeButton", ",Art/Interface/Buttons/Units/Warrior.dds,Art/Interface/Buttons/Afterworld_Atlas.dds,8,5", CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
				iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_WB_UNIT_EDIT_BUTTON, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)	
			iX += 35
			screen.addCheckBoxGFC("WorldBuilderCityEditModeButton", CyArtFileMgr().getInterfaceArtInfo("WORLDBUILDER_TOGGLE_CITY_EDIT_MODE").getPath(), CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
				iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_WB_CITY_EDIT_BUTTON, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)	
			iX += 35
			screen.addCheckBoxGFC("WorldBuilderNormalPlayerModeButton", CyArtFileMgr().getInterfaceArtInfo("WORLDBUILDER_NORMAL_UNIT_MODE").getPath(), CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
				iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_WB_NORMAL_PLAYER_TAB_MODE_BUTTON, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)
			iX += 35
			screen.addCheckBoxGFC("WorldBuilderNormalMapModeButton", CyArtFileMgr().getInterfaceArtInfo("WORLDBUILDER_NORMAL_MAP_MODE").getPath(), CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
				iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_WB_NORMAL_MAP_TAB_MODE_BUTTON, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)
			iX += 35
			screen.addCheckBoxGFC("WorldBuilderRevealTileModeButton", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_TECH_LOS").getPath(), CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
				iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_WB_REVEAL_TAB_MODE_BUTTON, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)
			iX += 35
			screen.setImageButton("WorldBuilderDiplomacyModeButton", CyArtFileMgr().getInterfaceArtInfo("WORLDBUILDER_DIPLOMACY_MODE").getPath(), 
				iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_WB_DIPLOMACY_MODE_BUTTON, -1, -1)
			iX = screen.getXResolution() - self.iScreenWidth + 8
			iY = 10
			screen.setImageButton("WorldBuilderRegenerateMap", CyArtFileMgr().getInterfaceArtInfo("WORLDBUILDER_REVEAL_ALL_TILES").getPath(), iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_WB_REGENERATE_MAP, -1, -1)
			iX += 35
			screen.addCheckBoxGFC("WorldBuilderEraseButton", CyArtFileMgr().getInterfaceArtInfo("WORLDBUILDER_ERASE").getPath(), CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
				iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_WB_ERASE_BUTTON, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)
			iX += 35
			screen.setImageButton("WorldBuilderGameDataButton", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_TECH_FREETECH").getPath(), iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_PYTHON, 1029, 2)
			iX += 35
			screen.setImageButton("WorldBuilderSaveButton", CyArtFileMgr().getInterfaceArtInfo("WORLDBUILDER_SAVE").getPath(), iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_WB_SAVE_BUTTON, -1, -1)
			iX += 35
			screen.setImageButton("WorldBuilderLoadButton", CyArtFileMgr().getInterfaceArtInfo("WORLDBUILDER_LOAD").getPath(), iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_WB_LOAD_BUTTON, -1, -1)
			iX += 35
			screen.setImageButton("WorldBuilderExitButton", CyArtFileMgr().getInterfaceArtInfo("WORLDBUILDER_EXIT").getPath(), iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_WB_EXIT_BUTTON, -1, -1)
			self.setCurrentModeCheckbox()
		return

	def refreshSideMenu(self):
		screen = CyGInterfaceScreen( "WorldBuilderScreen", CvScreenEnums.WORLDBUILDER_SCREEN )
		CyEngine().clearColoredPlots(PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS)
		CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_WORLD_BUILDER)
		CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_REVEALED_PLOTS)
		iScreenHeight = 10+37+37 
		iButtonWidth = 32
		
		if CyInterface().isInAdvancedStart():
			iX = 50
			iY = 15
			szText = u"<font=4>" + CyTranslator().getText("TXT_KEY_WB_AS_POINTS", (gc.getPlayer(CyGame().getActivePlayer()).getAdvancedStartPoints(), )) + "</font>"
			screen.setLabel("AdvancedStartPointsText", "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, iX, iY, -2, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
			szText = u"<font=4>" + CyTranslator().getText("TXT_KEY_WB_AS_COST_THIS_LOCATION", (self.m_iCost, )) + u"</font>"
			iY = 85
			screen.setLabel("AdvancedStartCostText", "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, iX-20, iY, -2, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		else:
			screen.deleteWidget("WorldBuilderPlayerChoice")
			screen.deleteWidget("WorldBuilderBrushSize")
			screen.deleteWidget("WorldBuilderLandmarkButton")
			screen.deleteWidget("WorldBuilderTeamChoice")
			screen.deleteWidget("WorldBuilderRevealAll")
			screen.deleteWidget("WorldBuilderUnrevealAll")
			screen.deleteWidget("WorldBuilderRevealPanel")
			screen.deleteWidget("WorldBuilderBackgroundBottomPanel")
			screen.deleteWidget("WorldBuilderPlayerData")
			screen.deleteWidget("ChangeBy")
			screen.deleteWidget("AddOwnershipButton")
			screen.deleteWidget("AddUnitsButton")
			screen.deleteWidget("AddBuildingsButton")
			screen.deleteWidget("AddCityButton")
			screen.deleteWidget("PlotDataButton")
			screen.deleteWidget("AddImprovementButton")
			screen.deleteWidget("AddBonusButton")
			screen.deleteWidget("AddPlotTypeButton")
			screen.deleteWidget("AddTerrainButton")
			screen.deleteWidget("AddRouteButton")
			screen.deleteWidget("AddFeatureButton")
			screen.deleteWidget("AddRiverButton")
			screen.deleteWidget("WBCurrentItem")
			screen.deleteWidget("WBSelectClass")
			screen.deleteWidget("WBSelectItem")
			screen.deleteWidget("RevealPlotButton")
			screen.deleteWidget("RevealSubmarineButton")
			screen.deleteWidget("RevealStealthButton")
			screen.deleteWidget("WorldBuilderEraseAll")
## Panel Screen ##
			iHeight = 45
			if self.m_bReveal or self.m_bNormalPlayer or self.m_bNormalMap:
				iHeight += 37
				if self.iPlayerAddMode == "AddLandMark":
					iHeight += 37
			screen.addPanel("WorldBuilderBackgroundBottomPanel", "", "", True, True, screen.getXResolution() - self.iScreenWidth, 10+32+32, self.iScreenWidth, iHeight, PanelStyles.PANEL_STYLE_MAIN )		
			iX = screen.getXResolution() - self.iScreenWidth + 8
			iY = 10 + 36 * 2
			if self.m_bNormalPlayer:
				screen.addCheckBoxGFC("AddOwnershipButton", gc.getCivilizationInfo(gc.getPlayer(self.m_iCurrentPlayer).getCivilizationType()).getButton(), CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
					 iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_PYTHON, 1029, 18, ButtonStyles.BUTTON_STYLE_LABEL)
				iX += 35
				screen.addDropDownBoxGFC("WorldBuilderPlayerChoice", iX, iY, screen.getXResolution() - 8 - iX, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
				for iPlayer in xrange(gc.getMAX_PLAYERS()):
					if gc.getPlayer(iPlayer).isEverAlive():
						sName = gc.getPlayer(iPlayer).getName()
						sCiv = gc.getPlayer(iPlayer).getCivilizationShortDescription(0)
						sName += " (" + sCiv + ")"
						if not gc.getPlayer(iPlayer).isAlive():
							sName = "*" + sName
						screen.addPullDownString("WorldBuilderPlayerChoice", sName, iPlayer, iPlayer, self.m_iCurrentPlayer == iPlayer)
## Player Data ##
				iX = screen.getXResolution() - self.iScreenWidth + 8
				iY += 36
				screen.setImageButton("WorldBuilderPlayerData", gc.getLeaderHeadInfo(gc.getPlayer(self.m_iCurrentPlayer).getLeaderType()).getButton(), iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_PYTHON, 1029, 4)
				iX += 35
				screen.addCheckBoxGFC("AddUnitsButton", ",Art/Interface/Buttons/Units/Warrior.dds,Art/Interface/Buttons/Warlords_Atlas_1.dds,6,10", CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
					 iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_PYTHON, 1029, 8, ButtonStyles.BUTTON_STYLE_LABEL)
				iX += 35
				screen.addCheckBoxGFC("AddBuildingsButton", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_CITYSELECTION").getPath(), CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
					 iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_PYTHON, 1029, 9, ButtonStyles.BUTTON_STYLE_LABEL)
				iX += 35
				screen.addCheckBoxGFC("AddCityButton", ",Art/Interface/Buttons/Actions/FoundCity.dds,Art/Interface/Buttons/Charlemagne_Atlas.dds,4,2", CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
					 iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_PYTHON, 1029, 10, ButtonStyles.BUTTON_STYLE_LABEL)
				iX += 35
				screen.addDropDownBoxGFC("ChangeBy", iX, iY, screen.getXResolution() - 8 - iX, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
				i = 1
				while i < 1001:
					screen.addPullDownString("ChangeBy", str(i), i, i, iChange == i)
					if str(i)[0] == "1":
						i *= 5
					else:
						i *= 2
			elif self.m_bNormalMap:
				screen.addCheckBoxGFC("WorldBuilderLandmarkButton", CyArtFileMgr().getInterfaceArtInfo("WORLDBUILDER_LANDMARK_MODE").getPath(), CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
					iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_WB_LANDMARK_BUTTON, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)
				iX += 35
				screen.addCheckBoxGFC("PlotDataButton", ",Art/Interface/Buttons/WorldBuilder/Gems.dds,Art/Interface/Buttons/FinalFrontier1_Atlas.dds,4,16", CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
					 iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_PYTHON, 1029, 19, ButtonStyles.BUTTON_STYLE_LABEL)
				iX += 35
				screen.addCheckBoxGFC("AddRiverButton", CyArtFileMgr().getInterfaceArtInfo("WORLDBUILDER_RIVER_PLACEMENT").getPath(), CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
					 iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_PYTHON, 1029, 17, ButtonStyles.BUTTON_STYLE_LABEL)
				iX += 35
				screen.addDropDownBoxGFC("WorldBuilderBrushSize", iX, iY, screen.getXResolution() - 8 - iX, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
				screen.addPullDownString("WorldBuilderBrushSize", "1x1", 1, 1, self.m_iBrushSize == 1)
				screen.addPullDownString("WorldBuilderBrushSize", "3x3", 2, 2, self.m_iBrushSize == 2)
				screen.addPullDownString("WorldBuilderBrushSize", "5x5", 3, 3, self.m_iBrushSize == 3)
				screen.addPullDownString("WorldBuilderBrushSize", "7x7", 4, 4, self.m_iBrushSize == 4)
				iX = screen.getXResolution() - self.iScreenWidth + 8
				iY += 36
				screen.addCheckBoxGFC("AddImprovementButton", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_TECH_FEATURE_PRODUCTION").getPath(), CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
					 iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_PYTHON, 1029, 11, ButtonStyles.BUTTON_STYLE_LABEL)
				iX += 35
				screen.addCheckBoxGFC("AddBonusButton", ",Art/Interface/Buttons/WorldBuilder/Gems.dds,Art/Interface/Buttons/Warlords_Atlas_1.dds,7,9", CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
					 iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_PYTHON, 1029, 14, ButtonStyles.BUTTON_STYLE_LABEL)
				iX += 35
				screen.addCheckBoxGFC("AddPlotTypeButton", CyArtFileMgr().getInterfaceArtInfo("WORLDBUILDER_CHANGE_ALL_PLOTS").getPath(), CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
					 iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_PYTHON, 1029, 12, ButtonStyles.BUTTON_STYLE_LABEL)
				iX += 35
				screen.addCheckBoxGFC("AddTerrainButton", ",Art/Interface/Buttons/BaseTerrain/Grassland.dds,Art/Interface/Buttons/BaseTerrain_TerrainFeatures_Atlas.dds,3,1", CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
					 iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_PYTHON, 1029, 13, ButtonStyles.BUTTON_STYLE_LABEL)
				iX += 35
				screen.addCheckBoxGFC("AddRouteButton", "Art/Interface/Buttons/Builds/BuildRoad.dds", CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
					 iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_PYTHON, 1029, 15, ButtonStyles.BUTTON_STYLE_LABEL)
				iX += 35
				screen.addCheckBoxGFC("AddFeatureButton", ",Art/Interface/Buttons/TerrainFeatures/Forest.dds,Art/Interface/Buttons/BaseTerrain_TerrainFeatures_Atlas.dds,3,3", CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
					 iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_PYTHON, 1029, 16, ButtonStyles.BUTTON_STYLE_LABEL)

## LandMark ##
				iX = screen.getXResolution() - self.iScreenWidth + 8
				iY += 36
				if self.iPlayerAddMode == "AddLandMark":
					screen.addDropDownBoxGFC("WorldBuilderPlayerChoice", iX, iY, screen.getXResolution() - 8 - iX, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
					screen.addPullDownString("WorldBuilderPlayerChoice", CyTranslator().getText("TXT_KEY_WB_LANDMARKS", ()), gc.getBARBARIAN_PLAYER(), gc.getBARBARIAN_PLAYER(), self.m_iCurrentPlayer == gc.getBARBARIAN_PLAYER())
					for iPlayer in xrange(gc.getMAX_PLAYERS()):
						if iPlayer == gc.getBARBARIAN_PLAYER(): continue
						if gc.getPlayer(iPlayer).isEverAlive():
							sName = gc.getPlayer(iPlayer).getName()
							sCiv = gc.getPlayer(iPlayer).getCivilizationShortDescription(0)
							sName += " (" + sCiv + ")"
							if not gc.getPlayer(iPlayer).isAlive():
								sName = "*" + sName
							screen.addPullDownString("WorldBuilderPlayerChoice", sName, iPlayer, iPlayer, self.m_iCurrentPlayer == iPlayer)

			elif self.m_bReveal:
				screen.setImageButton( "WorldBuilderRevealAll", CyArtFileMgr().getInterfaceArtInfo("WORLDBUILDER_REVEAL_ALL_TILES").getPath(), iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_WB_REVEAL_ALL_BUTTON, -1, -1)
				iX += 35
				screen.setImageButton( "WorldBuilderUnrevealAll", CyArtFileMgr().getInterfaceArtInfo("WORLDBUILDER_UNREVEAL_ALL_TILES").getPath(), iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_WB_UNREVEAL_ALL_BUTTON, -1, -1)
				iX += 35
				screen.addDropDownBoxGFC("WorldBuilderTeamChoice", iX, iY, screen.getXResolution() - 8 - iX, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
				for i in xrange(gc.getMAX_CIV_TEAMS()):
					if gc.getTeam(i).isAlive():
						screen.addPullDownString("WorldBuilderTeamChoice", gc.getTeam(i).getName(), i, i, self.m_iCurrentTeam == i)
				iX = screen.getXResolution() - self.iScreenWidth + 8
				iY += 36
				screen.addCheckBoxGFC("RevealPlotButton", ",Art/Interface/Buttons/Actions/Recon.dds,Art/Interface/Buttons/Actions_Builds_LeaderHeads_Specialists_Atlas.dds,3,6", CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
					 iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_PYTHON, 1029, 5, ButtonStyles.BUTTON_STYLE_LABEL)
				iX += 35
				screen.addCheckBoxGFC("RevealSubmarineButton", ",Art/Interface/Buttons/Units/ICBM.dds,Art/Interface/Buttons/Beyond_the_Sword_Atlas.dds,4,12", CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
					 iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_PYTHON, 1029, 6, ButtonStyles.BUTTON_STYLE_LABEL)
				iX += 35
				screen.addCheckBoxGFC("RevealStealthButton", ",Art/Interface/Buttons/Units/ICBM.dds,Art/Interface/Buttons/Beyond_the_Sword_Atlas.dds,3,12", CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
					 iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_PYTHON, 1029, 7, ButtonStyles.BUTTON_STYLE_LABEL)
				
				iX += 35
				screen.addDropDownBoxGFC("WorldBuilderBrushSize", iX, iY, screen.getXResolution() - 8 - iX, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
				screen.addPullDownString("WorldBuilderBrushSize", "1x1", 1, 1, self.m_iBrushSize == 1)
				screen.addPullDownString("WorldBuilderBrushSize", "3x3", 2, 2, self.m_iBrushSize == 2)
				screen.addPullDownString("WorldBuilderBrushSize", "5x5", 3, 3, self.m_iBrushSize == 3)
				screen.addPullDownString("WorldBuilderBrushSize", "7x7", 4, 4, self.m_iBrushSize == 4)
## Erase Multi Tiles Start ##
			elif self.iPlayerAddMode == "EraseAll":
				screen.setImageButton( "WorldBuilderEraseAll", CyArtFileMgr().getInterfaceArtInfo("WORLDBUILDER_UNREVEAL_ALL_TILES").getPath(), iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_PYTHON, 1029, 1)
				iX += 35
				screen.addDropDownBoxGFC("WorldBuilderBrushSize", iX, iY, screen.getXResolution() - 8 - iX, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
				screen.addPullDownString("WorldBuilderBrushSize", "1x1", 1, 1, self.m_iBrushSize == 1)
				screen.addPullDownString("WorldBuilderBrushSize", "3x3", 2, 2, self.m_iBrushSize == 2)
				screen.addPullDownString("WorldBuilderBrushSize", "5x5", 3, 3, self.m_iBrushSize == 3)
				screen.addPullDownString("WorldBuilderBrushSize", "7x7", 4, 4, self.m_iBrushSize == 4)
## Erase Multi Tiles End ##
			else:
				screen.deleteWidget("WorldBuilderBackgroundBottomPanel")
			self.setCurrentModeCheckbox()
			self.setSelectionTable()
		return

	def setCurrentModeCheckbox(self):
		screen = CyGInterfaceScreen( "WorldBuilderScreen", CvScreenEnums.WORLDBUILDER_SCREEN )
		screen.setState("WorldBuilderUnitEditModeButton", self.iPlayerAddMode == "EditUnit")
		screen.setState("WorldBuilderCityEditModeButton", self.iPlayerAddMode == "EditCity")
		screen.setState("WorldBuilderNormalPlayerModeButton", self.m_bNormalPlayer)
		screen.setState("WorldBuilderNormalMapModeButton", self.m_bNormalMap)
		screen.setState("WorldBuilderRevealTileModeButton", self.m_bReveal)
		screen.setState("WorldBuilderLandmarkButton", self.iPlayerAddMode == "AddLandMark")
		screen.setState("WorldBuilderEraseButton", self.iPlayerAddMode == "EraseAll")
		screen.setState("AddOwnershipButton", self.iPlayerAddMode == "Ownership")
		screen.setState("AddUnitsButton", self.iPlayerAddMode == "Units")
		screen.setState("AddBuildingsButton", self.iPlayerAddMode == "Buildings")
		screen.setState("AddCityButton", self.iPlayerAddMode == "City")
		screen.setState("PlotDataButton", self.iPlayerAddMode == "PlotData")
		screen.setState("AddRiverButton", self.iPlayerAddMode == "River")
		screen.setState("AddImprovementButton", self.iPlayerAddMode == "Improvements")
		screen.setState("AddBonusButton", self.iPlayerAddMode == "Bonus")
		screen.setState("AddPlotTypeButton", self.iPlayerAddMode == "PlotType")
		screen.setState("AddTerrainButton", self.iPlayerAddMode == "Terrain")
		screen.setState("AddRouteButton", self.iPlayerAddMode == "Routes")
		screen.setState("AddFeatureButton", self.iPlayerAddMode == "Features")
		screen.setState("RevealSubmarineButton", self.m_iRevealMode == 0)
		screen.setState("RevealStealthButton", self.m_iRevealMode == 1)
		screen.setState("RevealPlotButton", self.m_iRevealMode == 2)
		return

	def setSelectionTable(self):
		screen = CyGInterfaceScreen( "WorldBuilderScreen", CvScreenEnums.WORLDBUILDER_SCREEN)
		iWidth = 200
		if self.iPlayerAddMode == "Units":
			iY = 25
			screen.addDropDownBoxGFC("WBSelectClass", 0, iY, iWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
			screen.addPullDownString("WBSelectClass", CyTranslator().getText("TXT_KEY_WB_CITY_ALL",()), -2, -2, -2 == self.iSelectClass)
			screen.addPullDownString("WBSelectClass", CyTranslator().getText("TXT_PEDIA_NON_COMBAT",()), -1, -1, -1 == self.iSelectClass)
			for iCombatClass in xrange(gc.getNumUnitCombatInfos()):
				screen.addPullDownString("WBSelectClass", gc.getUnitCombatInfo(iCombatClass).getDescription(), iCombatClass, iCombatClass, iCombatClass == self.iSelectClass)

			lItems = []
			for i in xrange(gc.getNumUnitInfos()):
				ItemInfo = gc.getUnitInfo(i)
				if ItemInfo.getUnitCombatType() != self.iSelectClass and self.iSelectClass > -2: continue
				lItems.append([ItemInfo.getDescription(), i])
			lItems.sort()

			iY += 30
			iHeight = min(len(lItems) * 24 + 2, screen.getYResolution() - iY)
			screen.addTableControlGFC("WBSelectItem", 1, 0, iY, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_EMPTY)
			screen.setTableColumnHeader("WBSelectItem", 0, "", iWidth)
			for item in lItems:
				iRow = screen.appendTableRow("WBSelectItem")
				if self.iSelection == -1:
					self.iSelection = item[1]
				screen.setTableText("WBSelectItem", 0, iRow, "<font=3>" + item[0] + "</font>", gc.getUnitInfo(item[1]).getButton(), WidgetTypes.WIDGET_PYTHON, 8202, item[1], CvUtil.FONT_LEFT_JUSTIFY)

		elif self.iPlayerAddMode == "Buildings":
			iY = 25
			sWonder = CyTranslator().getText("TXT_KEY_CONCEPT_WONDERS", ())
			screen.addDropDownBoxGFC("WBSelectClass", 0, iY, iWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
			screen.addPullDownString("WBSelectClass", CyTranslator().getText("TXT_KEY_WB_CITY_ALL",()), 0, 0, 0 == self.iSelectClass)
			screen.addPullDownString("WBSelectClass", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_BUILDING",()), 1, 1, 1 == self.iSelectClass)
			screen.addPullDownString("WBSelectClass", CyTranslator().getText("TXT_KEY_PEDIA_NATIONAL_WONDER", ()), 2, 2, 2 == self.iSelectClass)
			screen.addPullDownString("WBSelectClass", CyTranslator().getText("TXT_KEY_PEDIA_TEAM_WONDER", ()), 3, 3, 3 == self.iSelectClass)
			screen.addPullDownString("WBSelectClass", CyTranslator().getText("TXT_KEY_PEDIA_WORLD_WONDER", ()), 4, 4, 4 == self.iSelectClass)

			lItems = []
			for i in xrange(gc.getNumBuildingInfos()):
				ItemInfo = gc.getBuildingInfo(i)
				BuildingClass = ItemInfo.getBuildingClassType()
				if self.iSelectClass == 1:
					if isLimitedWonderClass(BuildingClass): continue
				elif self.iSelectClass == 2:
					if not isNationalWonderClass(BuildingClass): continue
				elif self.iSelectClass == 3:
					if not isTeamWonderClass(BuildingClass): continue
				elif self.iSelectClass == 4:
					if not isWorldWonderClass(BuildingClass): continue
				lItems.append([ItemInfo.getDescription(), i])
			lItems.sort()

			iY += 30
			iHeight = min(len(lItems) * 24 + 2, screen.getYResolution() - iY)
			screen.addTableControlGFC("WBSelectItem", 1, 0, iY, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_EMPTY)
			screen.setTableColumnHeader("WBSelectItem", 0, "", iWidth)
			for item in lItems:
				iRow = screen.appendTableRow("WBSelectItem")
				if self.iSelection == -1:
					self.iSelection = item[1]
				screen.setTableText("WBSelectItem", 0, iRow, "<font=3>" + item[0] + "</font>", gc.getBuildingInfo(item[1]).getButton(), WidgetTypes.WIDGET_HELP_BUILDING, item[1], item[1], CvUtil.FONT_LEFT_JUSTIFY)

		elif self.iPlayerAddMode == "Features":
			iY = 55
			lItems = []
			for i in xrange(gc.getNumFeatureInfos()):
				ItemInfo = gc.getFeatureInfo(i)
				lItems.append([ItemInfo.getDescription(), i])
			lItems.sort()

			iHeight = min(len(lItems) * 24 + 2, screen.getYResolution() - iY)
			screen.addTableControlGFC("WBSelectItem", 1, 0, iY, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_EMPTY)
			screen.setTableColumnHeader("WBSelectItem", 0, "", iWidth)
			for item in lItems:
				iRow = screen.appendTableRow("WBSelectItem")
				if self.iSelection == -1:
					self.iSelection = item[1]
				screen.setTableText("WBSelectItem", 0, iRow, "<font=3>" + item[0] + "</font>", gc.getFeatureInfo(item[1]).getButton(), WidgetTypes.WIDGET_PYTHON, 7874, item[1], CvUtil.FONT_LEFT_JUSTIFY)

		elif self.iPlayerAddMode == "Improvements":
			iY = 25
			lItems = []
			for i in xrange(gc.getNumImprovementInfos()):
				ItemInfo = gc.getImprovementInfo(i)
				if ItemInfo.isGraphicalOnly(): continue
				lItems.append([ItemInfo.getDescription(), i])
			lItems.sort()

			iHeight = min(len(lItems) * 24 + 2, screen.getYResolution() - iY)
			screen.addTableControlGFC("WBSelectItem", 1, 0, iY, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_EMPTY)
			screen.setTableColumnHeader("WBSelectItem", 0, "", iWidth)
			for item in lItems:
				iRow = screen.appendTableRow("WBSelectItem")
				if self.iSelection == -1:
					self.iSelection = item[1]
				screen.setTableText("WBSelectItem", 0, iRow, "<font=3>" + item[0] + "</font>", gc.getImprovementInfo(item[1]).getButton(), WidgetTypes.WIDGET_PYTHON, 7877, item[1], CvUtil.FONT_LEFT_JUSTIFY)

		elif self.iPlayerAddMode == "Bonus":
			iY = 25
			screen.addDropDownBoxGFC("WBSelectClass", 0, iY, iWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
			screen.addPullDownString("WBSelectClass", CyTranslator().getText("TXT_KEY_WB_CITY_ALL",()), -1, -1, -1 == self.iSelectClass)
			screen.addPullDownString("WBSelectClass", CyTranslator().getText("TXT_PEDIA_GENERAL",()), 0, 0, 0 == self.iSelectClass)
			iBonusClass = 1
			while not gc.getBonusClassInfo(iBonusClass) is None:
				sText = gc.getBonusClassInfo(iBonusClass).getType()
				sText = sText[sText.find("_") +1:]
				sText = sText.lower()
				sText = sText.capitalize()
				screen.addPullDownString("WBSelectClass", sText, iBonusClass, iBonusClass, iBonusClass == self.iSelectClass)
				iBonusClass += 1

			lItems = []
			for i in xrange(gc.getNumBonusInfos()):
				ItemInfo = gc.getBonusInfo(i)
				if ItemInfo.getBonusClassType() != self.iSelectClass and self.iSelectClass > -1: continue
				lItems.append([ItemInfo.getDescription(), i])
			lItems.sort()

			iY += 30
			iHeight = min(len(lItems) * 24 + 2, screen.getYResolution() - iY)
			screen.addTableControlGFC("WBSelectItem", 1, 0, iY, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_EMPTY)
			screen.setTableColumnHeader("WBSelectItem", 0, "", iWidth)
			for item in lItems:
				iRow = screen.appendTableRow("WBSelectItem")
				if self.iSelection == -1:
					self.iSelection = item[1]
				screen.setTableText("WBSelectItem", 0, iRow, "<font=3>" + item[0] + "</font>", gc.getBonusInfo(item[1]).getButton(), WidgetTypes.WIDGET_PYTHON, 7878, item[1], CvUtil.FONT_LEFT_JUSTIFY)

		elif self.iPlayerAddMode == "Routes":
			iY = 25
			lItems = []
			for i in xrange(gc.getNumRouteInfos()):
				ItemInfo = gc.getRouteInfo(i)
				lItems.append([ItemInfo.getDescription(), i])
			lItems.sort()

			iHeight = min(len(lItems) * 24 + 2, screen.getYResolution() - iY)
			screen.addTableControlGFC("WBSelectItem", 1, 0, iY, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_EMPTY)
			screen.setTableColumnHeader("WBSelectItem", 0, "", iWidth)
			for item in lItems:
				iRow = screen.appendTableRow("WBSelectItem")
				if self.iSelection == -1:
					self.iSelection = item[1]
				screen.setTableText("WBSelectItem", 0, iRow, "<font=3>" + item[0] + "</font>", gc.getRouteInfo(item[1]).getButton(), WidgetTypes.WIDGET_PYTHON, 6788, item[1], CvUtil.FONT_LEFT_JUSTIFY)

		elif self.iPlayerAddMode == "Terrain":
			iY = 25
			lItems = []
			for i in xrange(gc.getNumTerrainInfos()):
				ItemInfo = gc.getTerrainInfo(i)
				if ItemInfo.isGraphicalOnly(): continue
				lItems.append([ItemInfo.getDescription(), i])
			lItems.sort()

			iHeight = min(len(lItems) * 24 + 2, screen.getYResolution() - iY)
			screen.addTableControlGFC("WBSelectItem", 1, 0, iY, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_EMPTY)
			screen.setTableColumnHeader("WBSelectItem", 0, "", iWidth)
			for item in lItems:
				iRow = screen.appendTableRow("WBSelectItem")
				if self.iSelection == -1:
					self.iSelection = item[1]
				screen.setTableText("WBSelectItem", 0, iRow, "<font=3>" + item[0] + "</font>", gc.getTerrainInfo(item[1]).getButton(), WidgetTypes.WIDGET_PYTHON, 7875, item[1], CvUtil.FONT_LEFT_JUSTIFY)

		elif self.iPlayerAddMode == "PlotType":
			iY = 25
			iHeight = 4 * 24 + 2
			screen.addTableControlGFC("WBSelectItem", 1, 0, 25, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_EMPTY)
			screen.setTableColumnHeader("WBSelectItem", 0, "", iWidth)
			for i in xrange(PlotTypes.NUM_PLOT_TYPES):
				screen.appendTableRow("WBSelectItem")
			item = gc.getInfoTypeForString("TERRAIN_PEAK")
			if self.iSelection == -1:
				self.iSelection = item
			screen.setTableText("WBSelectItem", 0, 0, "<font=3>" + gc.getTerrainInfo(item).getDescription() + "</font>", gc.getTerrainInfo(item).getButton(), WidgetTypes.WIDGET_PYTHON, 7875, item, CvUtil.FONT_LEFT_JUSTIFY)
			item = gc.getInfoTypeForString("TERRAIN_HILL")
			screen.setTableText("WBSelectItem", 0, 1, "<font=3>" + gc.getTerrainInfo(item).getDescription() + "</font>", gc.getTerrainInfo(item).getButton(), WidgetTypes.WIDGET_PYTHON, 7875, item, CvUtil.FONT_LEFT_JUSTIFY)
			item = gc.getInfoTypeForString("TERRAIN_GRASS")
			screen.setTableText("WBSelectItem", 0, 2, "<font=3>" + gc.getTerrainInfo(item).getDescription() + "</font>", gc.getTerrainInfo(item).getButton(), WidgetTypes.WIDGET_PYTHON, 7875, item, CvUtil.FONT_LEFT_JUSTIFY)
			item = gc.getInfoTypeForString("TERRAIN_OCEAN")
			screen.setTableText("WBSelectItem", 0, 3, "<font=3>" + gc.getTerrainInfo(item).getDescription() + "</font>", gc.getTerrainInfo(item).getButton(), WidgetTypes.WIDGET_PYTHON, 7875, item, CvUtil.FONT_LEFT_JUSTIFY)
		self.refreshSelection()

	def refreshSelection(self):
		if self.iSelection == -1: return
		screen = CyGInterfaceScreen( "WorldBuilderScreen", CvScreenEnums.WORLDBUILDER_SCREEN)
		iWidth = 200
		screen.addTableControlGFC("WBCurrentItem", 1, 0, 0, iWidth, 25, False, True, 24, 24, TableStyles.TABLE_STYLE_EMPTY)
		screen.setTableColumnHeader("WBCurrentItem", 0, "", iWidth)
		screen.appendTableRow("WBCurrentItem")
		if self.iPlayerAddMode == "Units":
			ItemInfo = gc.getUnitInfo(self.iSelection)
			sText = "<font=3>" + CyTranslator().getText("[COLOR_HIGHLIGHT_TEXT]", ()) + ItemInfo.getDescription() + "</color></font>"
			screen.setTableText("WBCurrentItem", 0, 0 , sText, ItemInfo.getButton(), WidgetTypes.WIDGET_PYTHON, 8202, self.iSelection, CvUtil.FONT_LEFT_JUSTIFY)
		elif self.iPlayerAddMode == "Buildings":
			ItemInfo = gc.getBuildingInfo(self.iSelection)
			sText = "<font=3>" + CyTranslator().getText("[COLOR_HIGHLIGHT_TEXT]", ()) + ItemInfo.getDescription() + "</color></font>"
			screen.setTableText("WBCurrentItem", 0, 0 , sText, ItemInfo.getButton(), WidgetTypes.WIDGET_HELP_BUILDING, self.iSelection, 1, CvUtil.FONT_LEFT_JUSTIFY)
		elif self.iPlayerAddMode == "Features":
			ItemInfo = gc.getFeatureInfo(self.iSelection)
			sText = "<font=3>" + CyTranslator().getText("[COLOR_HIGHLIGHT_TEXT]", ()) + ItemInfo.getDescription() + "</color></font>"
			screen.setTableText("WBCurrentItem", 0, 0 , sText, ItemInfo.getButton(), WidgetTypes.WIDGET_PYTHON, 7874, self.iSelection, CvUtil.FONT_LEFT_JUSTIFY)
			if ItemInfo.getNumVarieties() > 1:
				screen.addDropDownBoxGFC("WBSelectClass", 0, 25, iWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
				for i in xrange(ItemInfo.getNumVarieties()):
					screen.addPullDownString("WBSelectClass", CyTranslator().getText("TXT_KEY_WB_FEATURE_VARIETY", (i,)), i, i, i == self.iSelectClass)
			else:
				self.iSelectClass = 0
				screen.hide("WBSelectClass")
		elif self.iPlayerAddMode == "Improvements":
			ItemInfo = gc.getImprovementInfo(self.iSelection)
			sText = "<font=3>" + CyTranslator().getText("[COLOR_HIGHLIGHT_TEXT]", ()) + ItemInfo.getDescription() + "</color></font>"
			screen.setTableText("WBCurrentItem", 0, 0 , sText, ItemInfo.getButton(), WidgetTypes.WIDGET_PYTHON, 7877, self.iSelection, CvUtil.FONT_LEFT_JUSTIFY)
		elif self.iPlayerAddMode == "Bonus":
			ItemInfo = gc.getBonusInfo(self.iSelection)
			sText = "<font=3>" + CyTranslator().getText("[COLOR_HIGHLIGHT_TEXT]", ()) + ItemInfo.getDescription() + "</color></font>"
			screen.setTableText("WBCurrentItem", 0, 0 , sText, ItemInfo.getButton(), WidgetTypes.WIDGET_PYTHON, 7878, self.iSelection, CvUtil.FONT_LEFT_JUSTIFY)
		elif self.iPlayerAddMode == "Routes":
			ItemInfo = gc.getRouteInfo(self.iSelection)
			sText = "<font=3>" + CyTranslator().getText("[COLOR_HIGHLIGHT_TEXT]", ()) + ItemInfo.getDescription() + "</color></font>"
			screen.setTableText("WBCurrentItem", 0, 0 , sText, ItemInfo.getButton(), WidgetTypes.WIDGET_PYTHON, 6788, self.iSelection, CvUtil.FONT_LEFT_JUSTIFY)
		elif self.iPlayerAddMode == "Terrain" or self.iPlayerAddMode == "PlotType":
			ItemInfo = gc.getTerrainInfo(self.iSelection)
			sText = "<font=3>" + CyTranslator().getText("[COLOR_HIGHLIGHT_TEXT]", ()) + ItemInfo.getDescription() + "</color></font>"
			screen.setTableText("WBCurrentItem", 0, 0 , sText, ItemInfo.getButton(), WidgetTypes.WIDGET_PYTHON, 7875, self.iSelection, CvUtil.FONT_LEFT_JUSTIFY)
		else:
			screen.hide("WBCurrentItem")

## Platy Reveal Mode Start ##
	def revealAll(self, bReveal):
		for i in xrange(CyMap().numPlots()):
			pPlot = CyMap().plotByIndex(i)
			if pPlot.isNone(): continue
			self.RevealCurrentPlot(bReveal, pPlot)
		self.refreshReveal()
		return

	def RevealCurrentPlot(self, bReveal, pPlot):
		if self.m_iRevealMode == 2:
			if bReveal or (not pPlot.isVisible(self.m_iCurrentTeam, False)):
				pPlot.setRevealed(self.m_iCurrentTeam, bReveal, False, -1);
		elif bReveal:
			if pPlot.isInvisibleVisible(self.m_iCurrentTeam, self.m_iRevealMode): return
			pPlot.changeInvisibleVisibilityCount(self.m_iCurrentTeam, self.m_iRevealMode, 1)
		else:
			pPlot.changeInvisibleVisibilityCount(self.m_iCurrentTeam, self.m_iRevealMode, - pPlot.getInvisibleVisibilityCount(self.m_iCurrentTeam, self.m_iRevealMode))
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
		CyInterface().setWorldBuilder(false)
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
			self.m_advancedStartTabCtrl.addTabSection(CyTranslator().getText("TXT_KEY_WB_AS_CITIES",()));
			self.m_iAdvancedStartCurrentIndexes.append(0)
			
			self.m_iAdvancedStartCurrentList.append(self.m_iASCityListID)

			self.m_advancedStartTabCtrl.setNumColumns((gc.getNumUnitInfos()/10)+2);
			self.m_advancedStartTabCtrl.addTabSection(CyTranslator().getText("TXT_KEY_WB_AS_UNITS",()));
			self.m_iAdvancedStartCurrentIndexes.append(0)
			
			self.m_iAdvancedStartCurrentList.append(0)

			self.m_advancedStartTabCtrl.setNumColumns((gc.getNumImprovementInfos()/10)+2);
			self.m_advancedStartTabCtrl.addTabSection(CyTranslator().getText("TXT_KEY_WB_AS_IMPROVEMENTS",()));
			self.m_iAdvancedStartCurrentIndexes.append(0)
			
			self.m_iAdvancedStartCurrentList.append(self.m_iASRoutesListID)

			self.m_advancedStartTabCtrl.setNumColumns(1);
			self.m_advancedStartTabCtrl.addTabSection(CyTranslator().getText("TXT_KEY_WB_AS_VISIBILITY",()));
			self.m_iAdvancedStartCurrentIndexes.append(0)
			
			self.m_iAdvancedStartCurrentList.append(0)

			self.m_advancedStartTabCtrl.setNumColumns(1);
			self.m_advancedStartTabCtrl.addTabSection(CyTranslator().getText("TXT_KEY_WB_AS_TECH",()));
			self.m_iAdvancedStartCurrentIndexes.append(0)
			
			self.m_iAdvancedStartCurrentList.append(0)
			
			addWBAdvancedStartControlTabs()

			self.m_advancedStartTabCtrl.setActiveTab(iActiveTab)
			self.setCurrentAdvancedStartIndex(iActiveIndex)
			self.setCurrentAdvancedStartList(iActiveList)
		else:
			self.m_advancedStartTabCtrl = getWBToolAdvancedStartTabCtrl()
			self.m_advancedStartTabCtrl.enable(false)
		return
		
	def setRiverHighlights(self):
		CyEngine().clearColoredPlots(PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS)
		CyEngine().addColoredPlotAlt(self.m_pRiverStartPlot.getX(), self.m_pRiverStartPlot.getY(), PlotStyles.PLOT_STYLE_RIVER_SOUTH, PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS, "COLOR_GREEN", 1)

		for x in xrange(self.m_pRiverStartPlot.getX() - 1, self.m_pRiverStartPlot.getX() + 2):
			for y in xrange(self.m_pRiverStartPlot.getY() - 1, self.m_pRiverStartPlot.getY() + 2):
				if x == self.m_pRiverStartPlot.getX() and y == self.m_pRiverStartPlot.getY(): continue
				CyEngine().addColoredPlotAlt(x, y, PlotStyles.PLOT_STYLE_BOX_FILL, PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS, "COLOR_WHITE", .2)
		return

	def leftMouseDown (self, argsList):
		bShift, bCtrl, bAlt = argsList
		if CyInterface().isInAdvancedStart():
			self.placeObject()
		elif bAlt or self.iPlayerAddMode == "EditUnit":
			if self.m_pCurrentPlot.getNumUnits():
				WBUnitScreen.WBUnitScreen(self).interfaceScreen(self.m_pCurrentPlot.getUnit(0))
		elif bCtrl or self.iPlayerAddMode == "EditCity":
			if self.m_pCurrentPlot.isCity():
				WBCityEditScreen.WBCityEditScreen(self).interfaceScreen(self.m_pCurrentPlot.getPlotCity())
		elif self.m_bReveal:
			if self.m_pCurrentPlot:
				self.setMultipleReveal(True)
		elif self.iPlayerAddMode == "PlotData":
			WBPlotScreen.WBPlotScreen(self).interfaceScreen(self.m_pCurrentPlot)
		elif self.iPlayerAddMode == "MoveUnit":
			for i in self.m_lMoveUnit:
				pUnit = gc.getPlayer(self.m_iCurrentPlayer).getUnit(i)
				if pUnit.isNone(): continue
				pUnit.setXY(self.m_pCurrentPlot.getX(), self.m_pCurrentPlot.getY(), True, True, False)
			self.iPlayerAddMode = "EditUnit"
			self.m_lMoveUnit = []
		elif self.useLargeBrush():
			self.placeMultipleObjects()
		else:
			self.placeObject()
		return 1

	def rightMouseDown (self, argsList):
		if CyInterface().isInAdvancedStart():
			self.removeObject()
		elif self.m_bReveal:
			if self.m_pCurrentPlot:
				self.setMultipleReveal(False)
		elif self.useLargeBrush():
			self.removeMultipleObjects()
		else:
			self.removeObject()
		return 1

## Add "," ##
	def addComma(self, iValue):
		sTemp = str(iValue)
		sValue = sTemp[-3:]
		while len(sTemp) > 3:
			sTemp = sTemp[:-3]
			sValue = sTemp[-3:] + "," + sValue
		return sValue
## Add "," ##

	def handleInput (self, inputClass):
		screen = CyGInterfaceScreen( "WorldBuilderScreen", CvScreenEnums.WORLDBUILDER_SCREEN )
		global iChange
		if inputClass.getFunctionName() == "WorldBuilderEraseAll":
			for i in xrange(CyMap().numPlots()):
				self.m_pCurrentPlot = CyMap().plotByIndex(i)
				self.placeObject()

		elif inputClass.getFunctionName() == "WorldBuilderGameDataButton":
			WBGameDataScreen.WBGameDataScreen(self).interfaceScreen()

		elif inputClass.getFunctionName() == "WorldBuilderPlayerData":
			WBPlayerScreen.WBPlayerScreen(self).interfaceScreen(self.m_iCurrentPlayer)

		elif inputClass.getFunctionName() == "WorldBuilderPlayerChoice":
			iIndex = screen.getSelectedPullDownID("WorldBuilderPlayerChoice")
			self.m_iCurrentPlayer = screen.getPullDownData("WorldBuilderPlayerChoice", iIndex)
			self.m_iCurrentTeam = gc.getPlayer(self.m_iCurrentPlayer).getTeam()
			self.refreshSideMenu()

		elif inputClass.getFunctionName() == "ChangeBy":
			iIndex = screen.getSelectedPullDownID("ChangeBy")
			iChange = screen.getPullDownData("ChangeBy", iIndex)

		elif inputClass.getFunctionName() == "AddOwnershipButton":
			self.iPlayerAddMode = "Ownership"
			self.refreshSideMenu()

		elif inputClass.getFunctionName() == "AddUnitsButton":
			self.iPlayerAddMode = "Units"
			self.iSelectClass = -2
			self.iSelection = -1
			self.refreshSideMenu()

		elif inputClass.getFunctionName() == "AddBuildingsButton":
			self.iPlayerAddMode = "Buildings"
			self.iSelectClass = 0
			self.iSelection = -1
			self.refreshSideMenu()

		elif inputClass.getFunctionName() == "AddCityButton":
			self.iPlayerAddMode = "City"
			self.refreshSideMenu()

		elif inputClass.getFunctionName() == "PlotDataButton":
			self.iPlayerAddMode = "PlotData"
			self.refreshSideMenu()
			CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_WORLD_BUILDER)
			CyEngine().clearColoredPlots(PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS)

		elif inputClass.getFunctionName() == "AddImprovementButton":
			self.iPlayerAddMode = "Improvements"
			self.iSelection = -1
			self.refreshSideMenu()
			CyEngine().clearColoredPlots(PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS)

		elif inputClass.getFunctionName() == "AddBonusButton":
			self.iPlayerAddMode = "Bonus"
			self.iSelectClass = -1
			self.iSelection = -1
			self.refreshSideMenu()
			CyEngine().clearColoredPlots(PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS)

		elif inputClass.getFunctionName() == "AddPlotTypeButton":
			self.iPlayerAddMode = "PlotType"
			self.iSelection = -1
			self.refreshSideMenu()
			CyEngine().clearColoredPlots(PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS)

		elif inputClass.getFunctionName() == "AddTerrainButton":
			self.iPlayerAddMode = "Terrain"
			self.iSelection = -1
			self.refreshSideMenu()
			CyEngine().clearColoredPlots(PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS)

		elif inputClass.getFunctionName() == "AddRouteButton":
			self.iPlayerAddMode = "Routes"
			self.iSelection = -1
			self.refreshSideMenu()
			CyEngine().clearColoredPlots(PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS)

		elif inputClass.getFunctionName() == "AddFeatureButton":
			self.iPlayerAddMode = "Features"
			self.iSelectClass = 0
			self.iSelection = -1
			self.refreshSideMenu()
			CyEngine().clearColoredPlots(PlotLandscapeLayers.PLOT_LANDSCAPE_LAYER_REVEALED_PLOTS)

		elif inputClass.getFunctionName() == "AddRiverButton":
			self.iPlayerAddMode = "River"
			CyEngine().clearAreaBorderPlots(AreaBorderLayers.AREA_BORDER_LAYER_WORLD_BUILDER)
			self.refreshSideMenu()

		elif inputClass.getFunctionName() == "WBSelectClass":
			iIndex = screen.getSelectedPullDownID("WBSelectClass")
			self.iSelectClass = screen.getPullDownData("WBSelectClass", iIndex)
			if self.iPlayerAddMode != "Features":
				self.iSelection = -1
				self.refreshSideMenu()

		elif inputClass.getFunctionName() == "WBSelectItem":
			self.iSelection = inputClass.getData2()
			self.refreshSelection()

		elif inputClass.getFunctionName() == "RevealSubmarineButton":
			self.m_iRevealMode = 0
			self.refreshSideMenu()
			self.refreshReveal()
		elif inputClass.getFunctionName() == "RevealStealthButton":
			self.m_iRevealMode = 1
			self.refreshSideMenu()
			self.refreshReveal()
		elif inputClass.getFunctionName() == "RevealPlotButton":
			self.m_iRevealMode = 2
			self.refreshSideMenu()
			self.refreshReveal()

		elif inputClass.getFunctionName() == "WorldBuilderBrushSize":
			self.m_iBrushSize = inputClass.getData() + 1

		elif inputClass.getFunctionName() == "WorldBuilderTeamChoice":
			iIndex = screen.getSelectedPullDownID("WorldBuilderTeamChoice")
			self.m_iCurrentTeam = screen.getPullDownData("WorldBuilderTeamChoice", iIndex)
			self.refreshReveal()
		return 1