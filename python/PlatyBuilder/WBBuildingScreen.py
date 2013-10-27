## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums

# globals
gc = CyGlobalContext()
g_pCity = None

class WBBuildingScreen:

	def __init__(self):
		self.iList = []
		self.iBuildingCategory = 0

	def interfaceScreen(self, pCity):
		screen = CyGInterfaceScreen( "WBBuildingScreen", CvScreenEnums.WB_BUILDING)
		global g_pCity
		g_pCity = pCity

		self.nTableWidth = screen.getXResolution() - 40
		self.nTableHeight = screen.getYResolution() - 100
		screen.setRenderInterfaceOnly(True)
		screen.addPanel( "MainBG", u"", u"", True, False, -10, -10, screen.getXResolution() + 20, screen.getYResolution() + 20, PanelStyles.PANEL_STYLE_MAIN )
		screen.setDimensions(0,0, screen.getXResolution(), screen.getYResolution())
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)
		sText = CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_BUILDING", ())
##		if self.bWonder:
##			sText = CyTranslator().getText("TXT_KEY_CONCEPT_WONDERS", ())
		screen.setText("BuildingHeader", "Background", u"<font=4b>" + sText + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setText("WBBuildingExit", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 25, screen.getYResolution() - 40, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )

		szDropdownName = str("BuildingCategory")
		screen.addDropDownBoxGFC(szDropdownName, 20, 20, 180, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_BUILDING",()), 0, 0, self.iBuildingCategory == 0)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_CONCEPT_WONDERS",()), 1, 1, self.iBuildingCategory == 1)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_PEDIA_NATIONAL_WONDER",()), 2, 2, self.iBuildingCategory == 2)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_PEDIA_TEAM_WONDER",()), 3, 3, self.iBuildingCategory == 3)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_PEDIA_WORLD_WONDER",()), 4, 4, self.iBuildingCategory == 4)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_CIV_BUILDINGS", ()), 5, 5, self.iBuildingCategory == 5)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_REL_BUILDINGS", ()), 6, 6, self.iBuildingCategory == 6)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_SPELL_BUILDINGS", ()), 7, 7, self.iBuildingCategory == 7)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_ITEMS", ()), 8, 8, self.iBuildingCategory == 8)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_SHOW_HIDDEN", ()), 9, 9, self.iBuildingCategory == 9)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_ALL", ()), 10, 10, self.iBuildingCategory == 10)



		szDropdownName = str("BuildingCommands")
		screen.addDropDownBoxGFC(szDropdownName, screen.getXResolution() - 200, 20, 180, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_COMMANDS", ()), 0, 0, True)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_GRANT_AVAILABLE", ()), 1, 1, False)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_GRANT_ALL", ()), 2, 2, False)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_CLEAR_ALL", ()), 3, 3, False)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_COPY_ALL", ()), 4, 4, False)

		self.iList = []
		for i in xrange(gc.getNumBuildingInfos()):
			BuildingInfo = gc.getBuildingInfo(i)
			iBuildingClass = BuildingInfo.getBuildingClassType()
			if self.iBuildingCategory == 0:#Buildings
				if not isLimitedWonderClass(iBuildingClass):
					if not BuildingInfo.isGraphicalOnly():
						if not BuildingInfo.isEquipment():
							if not BuildingInfo.isRequiresCaster():
								self.iList.append([BuildingInfo.getDescription(), i])
			if self.iBuildingCategory == 1:#Wonders
				if isLimitedWonderClass(iBuildingClass):
					self.iList.append([BuildingInfo.getDescription(), i])
			if self.iBuildingCategory == 2:#National Wonders
				if isNationalWonderClass(iBuildingClass):
					self.iList.append([BuildingInfo.getDescription(), i])
			if self.iBuildingCategory == 3:#Team Wonders
				if isTeamWonderClass(iBuildingClass):
					self.iList.append([BuildingInfo.getDescription(), i])
			if self.iBuildingCategory == 4:#World Wonders
				if isWorldWonderClass(iBuildingClass):
					self.iList.append([BuildingInfo.getDescription(), i])
			if self.iBuildingCategory == 5:#Unique Buildings
				if BuildingInfo.getPrereqCiv() != -1:
					self.iList.append([BuildingInfo.getDescription(), i])
			if self.iBuildingCategory == 6:#Religious Buildings
				if BuildingInfo.getReligionType() != -1:
					self.iList.append([BuildingInfo.getDescription(), i])
			if self.iBuildingCategory == 7:#Spell Buildings
				if BuildingInfo.isRequiresCaster():
					self.iList.append([BuildingInfo.getDescription(), i])
			if self.iBuildingCategory == 8:#Equipment
				if BuildingInfo.isEquipment():
					self.iList.append([BuildingInfo.getDescription(), i])
			if self.iBuildingCategory == 9:#Hidden
				if BuildingInfo.isGraphicalOnly():
					self.iList.append([BuildingInfo.getDescription(), i])
			if self.iBuildingCategory == 10:#All
				self.iList.append([BuildingInfo.getDescription(), i])


		self.iList.sort()

		nColumns = 5
		screen.addTableControlGFC( "WBBuilding", nColumns, 20, 60, self.nTableWidth, self.nTableHeight, True, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		for i in xrange(nColumns):
			screen.setTableColumnHeader( "WBBuilding", i, "", self.nTableWidth/nColumns)

		nRows = (len(self.iList) + nColumns - 1) / nColumns
		for i in xrange(nRows):
			screen.appendTableRow("WBBuilding")

		for iCount in xrange(len(self.iList)):
			item = self.iList[iCount]
			iRow = iCount % nRows
			iColumn = iCount / nRows
			ItemInfo = gc.getBuildingInfo(item[1])
			if g_pCity.getNumRealBuilding(item[1]):
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			elif g_pCity.isHasBuilding(item[1]):
				sColor = CyTranslator().getText("[COLOR_YELLOW]", ())
			else:
				sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			screen.setTableText("WBBuilding", iColumn, iRow, sColor + item[0] + "</color>", ItemInfo.getButton(), WidgetTypes.WIDGET_HELP_BUILDING, item[1], 1, CvUtil.FONT_LEFT_JUSTIFY )

	def handleInput (self, inputClass):
		if inputClass.getFunctionName() == "BuildingCategory":
			self.handlePlatyBuildingCategoryCB(inputClass.getData())
			return 1
		if inputClass.getFunctionName() == "BuildingCommands":
			self.handlePlatyBuildingCommandsCB(inputClass.getData())
			return 1
		if inputClass.getData1() > -1 and inputClass.getData2() == 1:
			self.handlePlatySetBuildingCB(inputClass.getData1())
			return 1
		return 1

	def handlePlatyBuildingCategoryCB ( self, argsList ) :
		self.iBuildingCategory = int(argsList)
		self.interfaceScreen(g_pCity)
		return 1

	def handlePlatySetBuildingCB (self, iData1) :
		g_pCity.setNumRealBuilding(iData1, not g_pCity.getNumRealBuilding(iData1))
		self.interfaceScreen(g_pCity)
		return 1

	def handlePlatyBuildingCommandsCB (self, argsList) :
		if int(argsList) == 1:
			for item in self.iList:
				ItemInfo = gc.getBuildingInfo(item[1])
				iHolyReligion = ItemInfo.getHolyCity()
				if iHolyReligion > -1 and not g_pCity.isHolyCityByType(iHolyReligion): continue
				if g_pCity.canConstruct(item[1], True, True, True):
					g_pCity.setNumRealBuilding(item[1], 1)
				self.interfaceScreen(g_pCity)
		elif int(argsList) == 2:
			for item in self.iList:
				g_pCity.setNumRealBuilding(item[1], 1)
				self.interfaceScreen(g_pCity)
		elif int(argsList) == 3:
			for item in self.iList:
				g_pCity.setNumRealBuilding(item[1], 0)
				self.interfaceScreen(g_pCity)
		elif int(argsList) == 4:
			for item in self.iList:
				(loopCity, iter) = gc.getPlayer(g_pCity.getOwner()).firstCity(false)
				while(loopCity):
					if g_pCity.getNumRealBuilding(item[1]):
						loopCity.setNumRealBuilding(item[1], 1)
					else:
						loopCity.setNumRealBuilding(item[1], 0)
					(loopCity, iter) = gc.getPlayer(g_pCity.getOwner()).nextCity(iter, false)
		return 1

	def update(self, fDelta):
		return 1