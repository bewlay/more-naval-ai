from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums
import WBCityDataScreen
import WBCityEditScreen
import WBPlayerScreen
import WBTeamScreen
import WBPlotScreen
import WBEventScreen
import WBPlayerUnits
gc = CyGlobalContext()

class WBBuildingScreen:

	def __init__(self, main):
		self.top = main
		self.iWonder = 0
		self.iBuilding = 0

	def interfaceScreen(self, pCityX):
		screen = CyGInterfaceScreen( "WBBuildingScreen", CvScreenEnums.WB_BUILDING)
		global pCity
		pCity = pCityX

		screen.setRenderInterfaceOnly(True)
		screen.addPanel( "MainBG", u"", u"", True, False, -10, -10, screen.getXResolution() + 20, screen.getYResolution() + 20, PanelStyles.PANEL_STYLE_MAIN )
		screen.addPanel( "BuildingBG", u"", u"", True, False, 0, 0, screen.getXResolution(), screen.getYResolution()/2, PanelStyles.PANEL_STYLE_MAIN )
		screen.addPanel( "WonderBG", u"", u"", True, False, 0, screen.getYResolution()/2, screen.getXResolution(), screen.getYResolution()/2, PanelStyles.PANEL_STYLE_MAIN )
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)

		screen.setLabel("BuildingHeader", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_BUILDING", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setLabel("WonderHeader", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_CONCEPT_WONDERS", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, screen.getYResolution()/2 + 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setText("BuildingCopy", "Background", u"<font=3b>" + CyTranslator().getText("TXT_KEY_WB_COPY_ALL", (CyTranslator().getText("TXT_KEY_CONCEPT_CITIES", ()),)) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, 20, 50, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setText("BuildingAvailable", "Background", u"<font=3b>" + CyTranslator().getText("TXT_KEY_WB_GRANT_AVAILABLE", ()) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, screen.getXResolution()/5 + 20, 50, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setText("WonderAvailable", "Background", u"<font=3b>" + CyTranslator().getText("TXT_KEY_WB_GRANT_AVAILABLE", ()) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, screen.getXResolution()/5 + 20, screen.getYResolution()/2 + 50, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setText("WBBuildingExit", "Background", "<font=4>" + CyTranslator().getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 30, screen.getYResolution() - 42, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )

		screen.setLabel("BuildingAllText", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_WB_CITY_ALL", ()) + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 70, 50, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setButtonGFC("BuildingAllPlus", "", "", screen.getXResolution() - 70, 52, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("BuildingAllMinus", "", "", screen.getXResolution() - 45, 52, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)

		screen.setLabel("WonderAllText", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_WB_CITY_ALL", ()) + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 70, screen.getYResolution()/2 + 50, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setButtonGFC("WonderAllPlus", "", "", screen.getXResolution() - 70, screen.getYResolution()/2 + 52, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("WonderAllMinus", "", "", screen.getXResolution() - 45, screen.getYResolution()/2 + 52, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)

		pPlayer = gc.getPlayer(pCity.getOwner())
		screen.addDropDownBoxGFC("CurrentCity", screen.getXResolution()*4/5, 20, screen.getXResolution()/6, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		(loopCity, iter) = pPlayer.firstCity(False)
		while(loopCity):
			screen.addPullDownString("CurrentCity", loopCity.getName(), loopCity.getID(), loopCity.getID(), loopCity.getID() == pCity.getID())
			(loopCity, iter) = pPlayer.nextCity(iter, False)

#magister
		screen.addDropDownBoxGFC("BuildingClass", 20, 20, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("BuildingClass", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_BUILDING", ()), 0, 0, self.iBuilding == 0)
		screen.addPullDownString("BuildingClass", CyTranslator().getText("TXT_KEY_CIV_BUILDINGS", ()), 1, 1, self.iBuilding == 1)
		screen.addPullDownString("BuildingClass", CyTranslator().getText("TXT_KEY_REL_BUILDINGS", ()), 2, 2, self.iBuilding == 2)
		screen.addPullDownString("BuildingClass", CyTranslator().getText("TXT_KEY_SPELL_BUILDINGS", ()), 3, 3, self.iBuilding == 3)
		screen.addPullDownString("BuildingClass", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_ITEMS", ()), 4, 4, self.iBuilding == 4)
		screen.addPullDownString("BuildingClass", CyTranslator().getText("TXT_KEY_WB_SHOW_HIDDEN", ()), 5, 5, self.iBuilding == 5)
		screen.addPullDownString("BuildingClass", CyTranslator().getText("TXT_KEY_ALL", ()), 6, 6, self.iBuilding == 6)
#magister



		screen.addDropDownBoxGFC("WonderClass", 20, screen.getYResolution()/2 + 50, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("WonderClass", CyTranslator().getText("TXT_KEY_WB_CITY_ALL", ()), 0, 0, self.iWonder == 0)
		screen.addPullDownString("WonderClass", CyTranslator().getText("TXT_KEY_PEDIA_NATIONAL_WONDER", ()), 1, 1, self.iWonder == 1)
		screen.addPullDownString("WonderClass", CyTranslator().getText("TXT_KEY_PEDIA_TEAM_WONDER", ()), 2, 2, self.iWonder == 2)
		screen.addPullDownString("WonderClass", CyTranslator().getText("TXT_KEY_PEDIA_WORLD_WONDER", ()), 3, 3, self.iWonder == 3)

		screen.addDropDownBoxGFC("CurrentPage", 20, screen.getYResolution() - 42, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_CITY_DATA", ()), 0, 0, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_CITY_DATA2", ()), 1, 1, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_BUILDING", ()), 2, 2, True)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_HELP4", ()), 3, 3, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_TEAM_DATA", ()), 4, 4, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_UNIT", ()) + " + " + CyTranslator().getText("TXT_KEY_CONCEPT_CITIES", ()), 5, 5, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_HELP19", ()), 6, 6, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_CONCEPT_EVENTS", ()), 7, 7, False)

		global lBuilding
		global lNational
		global lTeam
		global lWorld


		global lWonder
		global lAll
		global lStandard
		global lUnique
		global lSpell
		global lReligion
		global lEquipment
		global lHidden

		lStandard = []
		lBuilding = []
		lNational = []
		lTeam = []
		lWorld = []

		lWonder = []
		lAll = []

		lUnique = []
		lSpell = []
		lReligion = []
		lEquipment = []
		lHidden= []

		for i in xrange(gc.getNumBuildingInfos()):
			BuildingInfo = gc.getBuildingInfo(i)
			iBuildingClass = BuildingInfo.getBuildingClassType()
			sDesc = BuildingInfo.getDescription()

			lAll.append([sDesc, i])

			if BuildingInfo.isGraphicalOnly():
				lHidden.append([sDesc, i])
			else:
				if isLimitedWonderClass(iBuildingClass):
					lWonder.append([sDesc, i])

					if isNationalWonderClass(iBuildingClass):
						lNational.append([sDesc, i])
					if isTeamWonderClass(iBuildingClass):
						lTeam.append([sDesc, i])
					if isWorldWonderClass(iBuildingClass):
						lWorld.append([sDesc, i])

				elif BuildingInfo.getProductionCost() > -1:
					lStandard.append([sDesc, i])

				if BuildingInfo.getPrereqCiv() != -1:
					lUnique.append([sDesc, i])

				if BuildingInfo.getReligionType() != -1:
					lReligion.append([sDesc, i])

				if BuildingInfo.isRequiresCaster():
					lSpell.append([sDesc, i])

				if BuildingInfo.isEquipment():
					lEquipment.append([sDesc, i])




		lNational.sort()
		lTeam.sort()
		lWorld.sort()
		lBuilding.sort()


		lWonder.sort()

		lUnique.sort()
		lSpell.sort()
		lReligion.sort()
		lEquipment.sort()
		lHidden.sort()


		self.placeBuildings()
		self.placeWonders()

	def placeBuildings(self):
		screen = CyGInterfaceScreen( "WBBuildingScreen", CvScreenEnums.WB_BUILDING)
#Magister
		if self.iBuilding == 0:
			lBuilding = lStandard
		elif self.iBuilding == 1:
			lBuilding = lUnique
		elif self.iBuilding == 2:
			lBuilding = lReligion
		elif self.iBuilding == 3:
			lBuilding = lSpell
		elif self.iBuilding == 4:
			lBuilding = lEquipment
		elif self.iBuilding == 5:
			lBuilding = lHidden
		elif self.iBuilding == 6:
			lBuilding = lAll
#Magister

		iMaxRows = (screen.getYResolution()/2 - 120) / 24
		nColumns = max(1, min(5, (len(lBuilding) + iMaxRows - 1)/iMaxRows))
		iHeight = iMaxRows * 24 + 2

		screen.addTableControlGFC("WBBuilding", nColumns, 20, 80, screen.getXResolution() - 40, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		for i in xrange(nColumns):
			screen.setTableColumnHeader( "WBBuilding", i, "", (screen.getXResolution() - 40)/nColumns)

		nRows = len(lBuilding)/ nColumns
		if len(lBuilding) % nColumns:
			nRows += 1
		for i in xrange(nRows):
			screen.appendTableRow("WBBuilding")

		for iCount in xrange(len(lBuilding)):
			item = lBuilding[iCount]
			iRow = iCount % nRows
			iColumn = iCount / nRows
			ItemInfo = gc.getBuildingInfo(item[1])
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			if pCity.getNumRealBuilding(item[1]):
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			elif pCity.isHasBuilding(item[1]):
				sColor = CyTranslator().getText("[COLOR_YELLOW]", ())
			screen.setTableText("WBBuilding", iColumn, iRow, "<font=3>" + sColor + item[0] + "</font></color>", ItemInfo.getButton(), WidgetTypes.WIDGET_HELP_BUILDING, item[1], 1, CvUtil.FONT_LEFT_JUSTIFY )

	def placeWonders(self):
		screen = CyGInterfaceScreen( "WBBuildingScreen", CvScreenEnums.WB_BUILDING)
#Magister
		if self.iWonder == 0:
			lWonders = lWonder
		elif self.iWonder == 1:
			lWonders = lNational
		elif self.iWonder == 2:
			lWonders = lTeam
		else:
			lWonders = lWorld
#Magister

		iMaxRows = (screen.getYResolution()/2 - 120) / 24
		nColumns = max(1, min(5, (len(lWonders) + iMaxRows - 1)/iMaxRows))
		iHeight = iMaxRows * 24 + 2
		screen.addTableControlGFC("WBWonders", nColumns, 20, screen.getYResolution()/2 + 80, screen.getXResolution() - 40, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		for i in xrange(nColumns):
			screen.setTableColumnHeader( "WBWonders", i, "", (screen.getXResolution() - 40)/nColumns)

		nRows = (len(lWonders) + nColumns - 1) / nColumns
		for i in xrange(nRows):
			screen.appendTableRow("WBWonders")

		for iCount in xrange(len(lWonders)):
			item = lWonders[iCount]
			iRow = iCount % nRows
			iColumn = iCount / nRows
			ItemInfo = gc.getBuildingInfo(item[1])
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			if pCity.getNumRealBuilding(item[1]):
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			elif pCity.isHasBuilding(item[1]):
				sColor = CyTranslator().getText("[COLOR_YELLOW]", ())
			screen.setTableText("WBWonders", iColumn, iRow, "<font=3>" + sColor + item[0] + "</font></color>", ItemInfo.getButton(), WidgetTypes.WIDGET_HELP_BUILDING, item[1], 1, CvUtil.FONT_LEFT_JUSTIFY )

	def handleInput (self, inputClass):
		screen = CyGInterfaceScreen( "WBBuildingScreen", CvScreenEnums.WB_BUILDING)
		if inputClass.getFunctionName() == "CurrentPage":
			iIndex = screen.getPullDownData("CurrentPage", screen.getSelectedPullDownID("CurrentPage"))
			if iIndex == 0:
				WBCityEditScreen.WBCityEditScreen(self.top).interfaceScreen(pCity)

			elif iIndex == 1:
				WBCityDataScreen.WBCityDataScreen(self.top).interfaceScreen(pCity)
			elif iIndex == 3:
				WBPlayerScreen.WBPlayerScreen(self.top).interfaceScreen(pCity.getOwner())
			elif iIndex == 4:
				WBTeamScreen.WBTeamScreen(self.top).interfaceScreen(pCity.getTeam())
			elif iIndex == 5:
				WBPlayerUnits.WBPlayerUnits(self.top).interfaceScreen(pCity.getOwner())
			elif iIndex == 6:
				WBPlotScreen.WBPlotScreen(self.top).interfaceScreen(pCity.plot())
			elif iIndex == 7:
				WBEventScreen.WBEventScreen(self.top).interfaceScreen(pCity.plot())

		elif inputClass.getFunctionName() == "CurrentCity":
			iIndex = screen.getSelectedPullDownID("CurrentCity")
			self.interfaceScreen(gc.getPlayer(pCity.getOwner()).getCity(iIndex))

		elif inputClass.getFunctionName() == "BuildingCopy":
			self.handlePlatyBuildingCopy()

		elif inputClass.getFunctionName() == "BuildingAvailable":
			self.handlePlatyGrantAvailable(lBuilding)
			self.placeBuildings()

		elif inputClass.getFunctionName().find("BuildingAll") > -1:
			self.handlePlatyGrantAll(lBuilding, inputClass.getData1())
			self.placeBuildings()

		elif inputClass.getFunctionName() == "WBBuilding":
			pCity.setNumRealBuilding(inputClass.getData1(), not pCity.getNumRealBuilding(inputClass.getData1()))
			self.placeBuildings()


		elif inputClass.getFunctionName() == "BuildingClass":
			self.iBuilding = inputClass.getData()
			self.placeBuildings()


		elif inputClass.getFunctionName() == "WonderClass":
			self.iWonder = inputClass.getData()
			self.placeWonders()

		elif inputClass.getFunctionName() == "WonderAvailable":
			if self.iWonder == 0:
				self.handlePlatyGrantAvailable(lNational + lTeam + lWorld)
			elif self.iWonder == 1:
				self.handlePlatyGrantAvailable(lNational)
			elif self.iWonder == 2:
				self.handlePlatyGrantAvailable(lTeam)
			elif self.iWonder == 3:
				self.handlePlatyGrantAvailable(lWorld)
			self.placeWonders()

		elif inputClass.getFunctionName().find("WonderAll") > -1:
			if self.iWonder == 0:
				self.handlePlatyGrantAll(lNational + lTeam + lWorld, inputClass.getData1())
			elif self.iWonder == 1:
				self.handlePlatyGrantAll(lNational, inputClass.getData1())
			elif self.iWonder == 2:
				self.handlePlatyGrantAll(lTeam, inputClass.getData1())
			elif self.iWonder == 3:
				self.handlePlatyGrantAll(lWorld, inputClass.getData1())
			self.placeWonders()

		elif inputClass.getFunctionName() == "WBWonders":
			pCity.setNumRealBuilding(inputClass.getData1(), not pCity.getNumRealBuilding(inputClass.getData1()))
			self.placeWonders()
		return 1

	def handlePlatyBuildingCopy(self):
		(loopCity, iter) = gc.getPlayer(pCity.getOwner()).firstCity(false)
		while(loopCity):
			if loopCity.getID() != pCity.getID():
				for item in lBuilding:
					ItemInfo = gc.getBuildingInfo(item[1])
					if ItemInfo.isWater() and not loopCity.isCoastal(ItemInfo.getMinAreaSize()): continue
					if ItemInfo.isRiver() and not loopCity.plot().isRiver(): continue
					loopCity.setNumRealBuilding(item[1], pCity.getNumRealBuilding(item[1]))
			(loopCity, iter) = gc.getPlayer(pCity.getOwner()).nextCity(iter, false)

	def handlePlatyGrantAvailable(self, lList):
		for item in lList:
			ItemInfo = gc.getBuildingInfo(item[1])
			if ItemInfo.isCapital(): continue
			iHolyReligion = ItemInfo.getHolyCity()
			if iHolyReligion > -1 and not pCity.isHolyCityByType(iHolyReligion): continue
			if pCity.canConstruct(item[1], True, False, True):
				pCity.setNumRealBuilding(item[1], 1)

	def handlePlatyGrantAll(self, lList, iData1):
		for item in lList:
			pCity.setNumRealBuilding(item[1], not iData1 % 2)

	def update(self, fDelta):
		return 1