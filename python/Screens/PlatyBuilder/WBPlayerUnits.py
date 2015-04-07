from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums
import WBPlayerScreen
import WBTeamScreen
import WBProjectScreen
import WBTechScreen
import WBCityEditScreen
import WBUnitScreen
import WBInfoScreen
import WBCityDataScreen
import WBBuildingScreen
import WBPromotionScreen
import WBPlotScreen
import WBEventScreen
import CvPlatyBuilderScreen

gc = CyGlobalContext()
iCityID = -1
iUnitID = -1

class WBPlayerUnits:

	def interfaceScreen(self, iPlayerX):
		screen = CyGInterfaceScreen( "WBPlayerUnits", CvScreenEnums.WB_UNITLIST)
		global iPlayer
		global pPlayer
		global iTeam
		global pTeam
		global iMapWidth
		global iMapHeight
		iPlayer = iPlayerX
		pPlayer = gc.getPlayer(iPlayer)
		iTeam = pPlayer.getTeam()
		pTeam = gc.getTeam(iTeam)
		iMapWidth = screen.getXResolution()/4
		iMapHeight = iMapWidth * 3/4

		screen.setRenderInterfaceOnly(True)
		screen.addPanel( "MainBG", u"", u"", True, False, -10, -10, screen.getXResolution() + 20, screen.getYResolution() + 20, PanelStyles.PANEL_STYLE_MAIN )
		screen.setDimensions(0,0, screen.getXResolution(), screen.getYResolution())
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)
		screen.setText("WBExit", "Background", "<font=4>" + CyTranslator().getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 30, screen.getYResolution() - 42, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )

		screen.addDropDownBoxGFC("CurrentPlayer", 20, 20, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		for i in xrange(gc.getMAX_PLAYERS()):
			pPlayerX = gc.getPlayer(i)
			if pPlayerX.isEverAlive():
				sText = pPlayerX.getName()
				if not pPlayerX.isAlive():
					sText = "*" + sText
				if pPlayerX.isTurnActive():
					sText = "[" + sText + "]"
				screen.addPullDownString("CurrentPlayer", sText, i, i, i == iPlayer)

		screen.setLabel("DeleteCitiesText", "Background", "<font=3b>" + CyTranslator().getText("TXT_KEY_WB_CITY_ALL", ()) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, 44, 50 + iMapHeight, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setImageButton("DeleteAllCities", "Art/Interface/Buttons/Actions/Delete.dds", 20, 50 + iMapHeight, 24, 24, WidgetTypes.WIDGET_PYTHON, 1041, -1)
		screen.setLabel("DeleteUnitsText", "Background", "<font=3b>" + CyTranslator().getText("TXT_KEY_WB_CITY_ALL", ()) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, screen.getXResolution()/2 + 58, 50 + iMapHeight, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setImageButton("DeleteAllUnits", "Art/Interface/Buttons/Actions/Delete.dds", 34 + screen.getXResolution()/2, 50 + iMapHeight, 24, 24, WidgetTypes.WIDGET_PYTHON, 1041, -1)
		screen.setImageButton("EndAllUnits", gc.getMissionInfo(MissionTypes.MISSION_SKIP).getButton(), 10 + screen.getXResolution()/2, 50 + iMapHeight, 24, 24, WidgetTypes.WIDGET_PYTHON, 1042, -1)

		self.setCityTable()
		self.setUnitTable()
		self.addPageSwitch()

	def addPageSwitch(self):
		screen = CyGInterfaceScreen( "WBPlayerUnits", CvScreenEnums.WB_UNITLIST)
		screen.addDropDownBoxGFC("CurrentPage", 20, screen.getYResolution() - 42, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_PLAYER_DATA", ()), 0, 0, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_TEAM_DATA", ()), 1, 1, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_PROJECT", ()), 2, 2, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_TECH", ()), 3, 3, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_UNIT", ()) + " + " + CyTranslator().getText("TXT_KEY_CONCEPT_CITIES", ()), 4, 4, True)
		if not pPlayer.getCity(iCityID).isNone():
			screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_CITY_DATA", ()), 9, 9, False)
			screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_CITY_DATA2", ()), 10, 10, False)
			screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_BUILDING", ()), 14, 14, False)
			screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_CITY", ()) + " " + CyTranslator().getText("TXT_KEY_WB_PLOT_DATA", ()), 12, 12, False)
			screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_CITY", ()) + " " + CyTranslator().getText("TXT_KEY_CONCEPT_EVENTS", ()), 13, 13, False)
		if not pPlayer.getUnit(iUnitID).isNone():
			screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_UNIT_DATA", ()), 5, 5, False)
			screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_PROMOTION", ()), 6, 6, False)
			screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_UNIT", ()) + " " + CyTranslator().getText("TXT_KEY_WB_PLOT_DATA", ()), 7, 7, False)
			screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_UNIT", ()) + " " + CyTranslator().getText("TXT_KEY_CONCEPT_EVENTS", ()), 8, 8, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_INFO_SCREEN", ()), 11, 11, False)

	def setUnitTable(self):
		screen = CyGInterfaceScreen( "WBPlayerUnits", CvScreenEnums.WB_UNITLIST)
		global iUnitID
		iY = 80 + iMapHeight
		iWidth = screen.getXResolution()/2 - 30
		iHeight = (screen.getYResolution() - iY - 42) / 24 * 24 + 2
		iColWidth = (iWidth - 24*3 - 10) /10

		lStatus = [CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_CANCEL").getPath(), gc.getMissionInfo(MissionTypes.MISSION_FORTIFY).getButton(), gc.getMissionInfo(MissionTypes.MISSION_SKIP).getButton()]

		screen.addTableControlGFC( "WBUnitList", 9, 10 + screen.getXResolution()/2, iY, iWidth, iHeight, True, True, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		screen.setTableColumnHeader( "WBUnitList", 0, "", 24)
		screen.setTableColumnHeader( "WBUnitList", 1, "", 24)
		screen.setTableColumnHeader( "WBUnitList", 2, "", 24)
		screen.setTableColumnHeader( "WBUnitList", 3, CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_UNIT", ()), iColWidth * 4)
		screen.setTableColumnHeader( "WBUnitList", 4, CyTranslator().getText("TXT_KEY_WB_UNIT", ()) + " ID", iColWidth * 2)
		screen.setTableColumnHeader( "WBUnitList", 5, CyTranslator().getText("TXT_KEY_WB_AREA_ID", ()), iColWidth * 2)
		screen.setTableColumnHeader( "WBUnitList", 6, "X", iColWidth)
		screen.setTableColumnHeader( "WBUnitList", 7, "Y", iColWidth)
		screen.setTableColumnHeader( "WBUnitList", 8, "", 10)
		screen.enableSort("WBUnitList")

		(loopUnit, iter) = pPlayer.firstUnit(False)
		while(loopUnit):
			iRow = screen.appendTableRow("WBUnitList")
			if pPlayer.getUnit(iUnitID).isNone():
				iUnitID = loopUnit.getID()
			screen.setTableText("WBUnitList", 0, iRow, "", gc.getMissionInfo(MissionTypes.MISSION_SKIP).getButton(), WidgetTypes.WIDGET_PYTHON, 1042, loopUnit.getID(), CvUtil.FONT_LEFT_JUSTIFY)
			screen.setTableText("WBUnitList", 1, iRow, "", "Art/Interface/Buttons/Actions/Delete.dds", WidgetTypes.WIDGET_PYTHON, 1041, loopUnit.getID(), CvUtil.FONT_LEFT_JUSTIFY)

			iStatus = 0
			if loopUnit.movesLeft() > 0:
				iStatus = 1
			if loopUnit.getGroup().readyToMove(False):
				iStatus = 2
			sColor = CyTranslator().getText("[COLOR_NEGATIVE_TEXT]", ())
			if iUnitID == loopUnit.getID():
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			screen.setTableText("WBUnitList", 2, iRow, str(iStatus), lStatus[iStatus], WidgetTypes.WIDGET_PYTHON, 1043, iStatus, CvUtil.FONT_LEFT_JUSTIFY)
			screen.setTableText("WBUnitList", 3, iRow, "<font=3>" + sColor + loopUnit.getName() + "</color></font>", loopUnit.getButton(), WidgetTypes.WIDGET_PYTHON, 8300 + iPlayer, loopUnit.getID(), CvUtil.FONT_LEFT_JUSTIFY)
			screen.setTableInt("WBUnitList", 4, iRow, "<font=3>" + str(loopUnit.getID()) + "</font>", "", WidgetTypes.WIDGET_PYTHON, 8300 + iPlayer, loopUnit.getID(), CvUtil.FONT_LEFT_JUSTIFY)
			screen.setTableInt("WBUnitList", 5, iRow, "<font=3>" + str(loopUnit.plot().getArea()) + "</font>", "", WidgetTypes.WIDGET_PYTHON, 8300 + iPlayer, loopUnit.getID(), CvUtil.FONT_LEFT_JUSTIFY)
			screen.setTableInt("WBUnitList", 6, iRow, "<font=3>" + str(loopUnit.getX()) + "</font>", "", WidgetTypes.WIDGET_PYTHON, 8300 + iPlayer, loopUnit.getID(), CvUtil.FONT_LEFT_JUSTIFY)
			screen.setTableInt("WBUnitList", 7, iRow, "<font=3>" + str(loopUnit.getY()) + "</font>", "", WidgetTypes.WIDGET_PYTHON, 8300 + iPlayer, loopUnit.getID(), CvUtil.FONT_LEFT_JUSTIFY)
			(loopUnit, iter) = pPlayer.nextUnit(iter, False)
		self.placeUnitMap()

	def setCityTable(self):
		screen = CyGInterfaceScreen( "WBPlayerUnits", CvScreenEnums.WB_UNITLIST)
		global iCityID
		iY = 80 + iMapHeight
		iWidth = screen.getXResolution()/2 - 30
		iHeight = (screen.getYResolution() - iY - 42) / 24 * 24 + 2
		iColWidth = (iWidth - 24) /10

		screen.addTableControlGFC( "WBCityList", 6, 20, iY, iWidth, iHeight, True, True, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		screen.setTableColumnHeader( "WBCityList", 0, "", 24)
		screen.setTableColumnHeader( "WBCityList", 1, CyTranslator().getText("TXT_KEY_CONCEPT_CITIES", ()), iColWidth * 4)
		screen.setTableColumnHeader( "WBCityList", 2, CyTranslator().getText("TXT_KEY_WB_CITY", ()) + " ID", iColWidth * 2)
		screen.setTableColumnHeader( "WBCityList", 3, CyTranslator().getText("TXT_KEY_WB_AREA_ID", ()), iColWidth * 2)
		screen.setTableColumnHeader( "WBCityList", 4, "X", iColWidth)
		screen.setTableColumnHeader( "WBCityList", 5, "Y", iColWidth)
		screen.enableSort("WBCityList")

		(loopCity, iter) = pPlayer.firstCity(False)
		while(loopCity):
			iRow = screen.appendTableRow("WBCityList")
			if pPlayer.getCity(iCityID).isNone():
				iCityID = loopCity.getID()
			sColor = CyTranslator().getText("[COLOR_NEGATIVE_TEXT]", ())
			if iCityID == loopCity.getID():
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			sFont = "<font=3>"
			if iCityID == loopCity.getID():
				sFont = "<font=3b>"
			screen.setTableText("WBCityList", 0, iRow, "", "Art/Interface/Buttons/Actions/Delete.dds", WidgetTypes.WIDGET_PYTHON, 1041, loopCity.getID(), CvUtil.FONT_LEFT_JUSTIFY)
			screen.setTableText("WBCityList", 1, iRow, "<font=3>" + sColor + loopCity.getName() + "</color></font>", gc.getCivilizationInfo(loopCity.getCivilizationType()).getButton(), WidgetTypes.WIDGET_PYTHON, 7200 + iPlayer, loopCity.getID(), CvUtil.FONT_LEFT_JUSTIFY)
			screen.setTableInt("WBCityList", 2, iRow, "<font=3>" + str(loopCity.getID()) + "</font>", "", WidgetTypes.WIDGET_PYTHON, 7200 + iPlayer, loopCity.getID(), CvUtil.FONT_LEFT_JUSTIFY)
			screen.setTableInt("WBCityList", 3, iRow, "<font=3>" + str(loopCity.plot().getArea()) + "</font>", "", WidgetTypes.WIDGET_PYTHON, 7200 + iPlayer, loopCity.getID(), CvUtil.FONT_LEFT_JUSTIFY)
			screen.setTableInt("WBCityList", 4, iRow, "<font=3>" + str(loopCity.getX()) + "</font>", "", WidgetTypes.WIDGET_PYTHON, 7200 + iPlayer, loopCity.getID(), CvUtil.FONT_LEFT_JUSTIFY)
			screen.setTableInt("WBCityList", 5, iRow, "<font=3>" + str(loopCity.getY()) + "</font>", "", WidgetTypes.WIDGET_PYTHON, 7200 + iPlayer, loopCity.getID(), CvUtil.FONT_LEFT_JUSTIFY)
			(loopCity, iter) = pPlayer.nextCity(iter, False)
		self.placeCityMap()

	def placeCityMap(self):
		screen = CyGInterfaceScreen("WBPlayerUnits", CvScreenEnums.WB_UNITLIST)
		screen.hide("GoToCity")
		screen.hide("CityView")
		pCity = pPlayer.getCity(iCityID)
		if pCity.isNone(): return
		sText = CyTranslator().getText("[COLOR_SELECTED_TEXT]", ()) + "<font=4b>" + pCity.getName() + "</color></font>"
		screen.setText("GoToCity", "Background", sText, CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/4, 50, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addPlotGraphicGFC("CityView", screen.getXResolution()/4 - iMapWidth/2, 80, iMapWidth, iMapHeight, pCity.plot(), 350, False, WidgetTypes.WIDGET_GENERAL, -1, -1)

	def placeUnitMap(self):
		screen = CyGInterfaceScreen("WBPlayerUnits", CvScreenEnums.WB_UNITLIST)
		screen.hide("GoToUnit")
		screen.hide("UnitView")
		pUnit = pPlayer.getUnit(iUnitID)
		if pUnit.isNone(): return
		sText = CyTranslator().getText("[COLOR_SELECTED_TEXT]", ()) + "<font=4b>" + pUnit.getName() + "</color></font>"
		screen.setText("GoToUnit", "Background", sText, CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()*3/4, 50, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addPlotGraphicGFC("UnitView", screen.getXResolution() * 3/4 - iMapWidth/2, 80, iMapWidth, iMapHeight, pUnit.plot(), 350, True, WidgetTypes.WIDGET_GENERAL, -1, -1)

	def handleInput(self, inputClass):
		screen = CyGInterfaceScreen("WBPlayerUnits", CvScreenEnums.WB_UNITLIST)
		global iCityID
		global iUnitID
		if inputClass.getFunctionName() == "CurrentPage":
			iIndex = screen.getPullDownData("CurrentPage", screen.getSelectedPullDownID("CurrentPage"))
			if iIndex == 0:
				WBPlayerScreen.WBPlayerScreen().interfaceScreen(iPlayer)
			elif iIndex == 1:
				WBTeamScreen.WBTeamScreen().interfaceScreen(iTeam)
			elif iIndex == 2:
				WBProjectScreen.WBProjectScreen().interfaceScreen(iTeam)
			elif iIndex == 3:
				WBTechScreen.WBTechScreen().interfaceScreen(iTeam)
			elif iIndex == 11:
				WBInfoScreen.WBInfoScreen().interfaceScreen(iPlayer)
			elif iIndex == 5:
				WBUnitScreen.WBUnitScreen(CvPlatyBuilderScreen.CvWorldBuilderScreen()).interfaceScreen(pPlayer.getUnit(iUnitID))
			elif iIndex == 6:
				WBPromotionScreen.WBPromotionScreen().interfaceScreen(pPlayer.getUnit(iUnitID))
			elif iIndex == 7:
				WBPlotScreen.WBPlotScreen().interfaceScreen(pPlayer.getUnit(iUnitID).plot())
			elif iIndex == 8:
				WBEventScreen.WBEventScreen().interfaceScreen(pPlayer.getUnit(iUnitID).plot())
			elif iIndex == 9:
				WBCityEditScreen.WBCityEditScreen(CvPlatyBuilderScreen.CvWorldBuilderScreen()).interfaceScreen(pPlayer.getCity(iCityID))
			elif iIndex == 10:
				WBCityDataScreen.WBCityDataScreen().interfaceScreen(pPlayer.getCity(iCityID))
			elif iIndex == 14:
				WBBuildingScreen.WBBuildingScreen().interfaceScreen(pPlayer.getCity(iCityID))
			elif iIndex == 12:
				WBPlotScreen.WBPlotScreen().interfaceScreen(pPlayer.getCity(iCityID).plot())
			elif iIndex == 13:
				WBEventScreen.WBEventScreen().interfaceScreen(pPlayer.getCity(iCityID).plot())

		elif inputClass.getFunctionName() == "CurrentPlayer":
			iIndex = screen.getPullDownData("CurrentPlayer", screen.getSelectedPullDownID("CurrentPlayer"))
			iCityID = -1
			iUnitID = -1
			self.interfaceScreen(iIndex)

		elif inputClass.getFunctionName() == "WBCityList":
			iCityID = inputClass.getData2()
			if inputClass.getData1() == 1041:
				pPlayer.getCity(iCityID).kill()
				self.addPageSwitch()
			else:
				self.placeCityMap()
			self.setCityTable()

		elif inputClass.getFunctionName() == "GoToCity":
			WBCityEditScreen.WBCityEditScreen(CvPlatyBuilderScreen.CvWorldBuilderScreen()).interfaceScreen(pPlayer.getCity(iCityID))

		elif inputClass.getFunctionName() == "GoToUnit":
			WBUnitScreen.WBUnitScreen(CvPlatyBuilderScreen.CvWorldBuilderScreen()).interfaceScreen(pPlayer.getUnit(iUnitID))

		elif inputClass.getFunctionName() == "DeleteAllCities":
			pPlayer.killCities()
			self.setCityTable()
			self.addPageSwitch()

		elif inputClass.getFunctionName() == "WBUnitList":
			if inputClass.getData1() == 1043: return
			iUnitID = inputClass.getData2()
			if inputClass.getData1() == 1042:
				pPlayer.getUnit(iUnitID).finishMoves()
			elif inputClass.getData1() == 1041:
				pPlayer.getUnit(iUnitID).kill(False, PlayerTypes.NO_PLAYER)
				self.setUnitTable()
				self.addPageSwitch()
			else:
				self.placeUnitMap()
			self.setUnitTable()

		elif inputClass.getFunctionName() == "DeleteAllUnits":
			pPlayer.killUnits()
			self.setUnitTable()
			self.addPageSwitch()

		elif inputClass.getFunctionName() == "EndAllUnits":
			(loopUnit, iter) = pPlayer.firstUnit(False)
			while(loopUnit):
				loopUnit.finishMoves()
				(loopUnit, iter) = pPlayer.nextUnit(iter, False)
			self.setUnitTable()

		return

	def update(self, fDelta):
		return 1