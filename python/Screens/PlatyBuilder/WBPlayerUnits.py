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
gc = CyGlobalContext()
iCityID = 0
iUnitID = 0

class WBPlayerUnits:
	def __init__(self, main):
		self.top = main

	def interfaceScreen(self, iPlayerX):
		screen = CyGInterfaceScreen( "WBPlayerUnits", CvScreenEnums.WB_UNITLIST)
		global iPlayer
		global pPlayer
		global iTeam
		global pTeam
		global iMapWidth
		global iMapHeight
		global iCityID
		global iUnitID
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
		
		screen.addDropDownBoxGFC("CurrentPage", 20, screen.getYResolution() - 42, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_HELP4", ()), 0, 0, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_TEAM_DATA", ()), 1, 1, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_PROJECT", ()), 2, 2, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_TECH", ()), 3, 3, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_UNIT", ()) + " + " + CyTranslator().getText("TXT_KEY_CONCEPT_CITIES", ()), 4, 4, True)

		screen.addDropDownBoxGFC("CurrentPlayer", 20, 20, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		for i in xrange(gc.getMAX_PLAYERS()):
			pPlayerX = gc.getPlayer(i)
			if pPlayerX.isEverAlive():
				sText = pPlayerX.getName()
				if not pPlayerX.isAlive():
					sText = "*" + sText
				screen.addPullDownString("CurrentPlayer", sText, i, i, i == iPlayer)

		iY = 80 + iMapHeight
		iWidth = screen.getXResolution()/2 - 40
		iHeight = (screen.getYResolution() - iY - 42) / 24 * 24 + 2
		screen.addTableControlGFC( "WBCityList", 5, 20, iY, iWidth, iHeight, True, True, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		iColWidth = iWidth/10
		screen.setTableColumnHeader( "WBCityList", 0, CyTranslator().getText("TXT_KEY_CONCEPT_CITIES", ()), iColWidth * 4)
		screen.setTableColumnHeader( "WBCityList", 1, CyTranslator().getText("TXT_KEY_WB_CITY", ()) + " ID", iColWidth * 2)
		screen.setTableColumnHeader( "WBCityList", 2, CyTranslator().getText("TXT_KEY_WB_AREA_ID", ()), iColWidth * 2)
		screen.setTableColumnHeader( "WBCityList", 3, "X", iColWidth)
		screen.setTableColumnHeader( "WBCityList", 4, "Y", iColWidth)
		screen.enableSort("WBCityList")
		
		(loopCity, iter) = pPlayer.firstCity(False)
		while(loopCity):
			iRow = screen.appendTableRow("WBCityList")
			if pPlayer.getCity(iCityID).isNone():
				iCityID = loopCity.getID()
			screen.setTableText("WBCityList", 0, iRow, "<font=3>" + loopCity.getName() + "</font>", gc.getCivilizationInfo(loopCity.getCivilizationType()).getButton(), WidgetTypes.WIDGET_PYTHON, 7200 + iPlayer, loopCity.getID(), CvUtil.FONT_LEFT_JUSTIFY )
			screen.setTableInt("WBCityList", 1, iRow, "<font=3>" + str(loopCity.getID()) + "</font>", "", WidgetTypes.WIDGET_PYTHON, 7200 + iPlayer, loopCity.getID(), CvUtil.FONT_LEFT_JUSTIFY )
			screen.setTableInt("WBCityList", 2, iRow, "<font=3>" + str(loopCity.plot().getArea()) + "</font>", "", WidgetTypes.WIDGET_PYTHON, 7200 + iPlayer, loopCity.getID(), CvUtil.FONT_LEFT_JUSTIFY )
			screen.setTableInt("WBCityList", 3, iRow, "<font=3>" + str(loopCity.getX()) + "</font>", "", WidgetTypes.WIDGET_PYTHON, 7200 + iPlayer, loopCity.getID(), CvUtil.FONT_LEFT_JUSTIFY )
			screen.setTableInt("WBCityList", 4, iRow, "<font=3>" + str(loopCity.getY()) + "</font>", "", WidgetTypes.WIDGET_PYTHON, 7200 + iPlayer, loopCity.getID(), CvUtil.FONT_LEFT_JUSTIFY )
			(loopCity, iter) = pPlayer.nextCity(iter, False)

		screen.addTableControlGFC( "WBUnitList", 5, 20 + screen.getXResolution()/2, iY, iWidth, iHeight, True, True, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		screen.setTableColumnHeader( "WBUnitList", 0, CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_UNIT", ()), iColWidth * 4)
		screen.setTableColumnHeader( "WBUnitList", 1, CyTranslator().getText("TXT_KEY_WB_UNIT", ()) + " ID", iColWidth * 2)
		screen.setTableColumnHeader( "WBUnitList", 2, CyTranslator().getText("TXT_KEY_WB_AREA_ID", ()), iColWidth * 2)
		screen.setTableColumnHeader( "WBUnitList", 3, "X", iColWidth)
		screen.setTableColumnHeader( "WBUnitList", 4, "Y", iColWidth)
		screen.enableSort("WBUnitList")
		
		(loopUnit, iter) = pPlayer.firstUnit(False)
		while(loopUnit):
			iRow = screen.appendTableRow("WBUnitList")
			if pPlayer.getUnit(iUnitID).isNone():
				iUnitID = loopUnit.getID()
			screen.setTableText("WBUnitList", 0, iRow, "<font=3>" + loopUnit.getName() + "</font>", loopUnit.getButton(), WidgetTypes.WIDGET_PYTHON, 8300 + iPlayer, loopUnit.getID(), CvUtil.FONT_LEFT_JUSTIFY )
			screen.setTableInt("WBUnitList", 1, iRow, "<font=3>" + str(loopUnit.getID()) + "</font>", "", WidgetTypes.WIDGET_PYTHON, 8300 + iPlayer, loopUnit.getID(), CvUtil.FONT_LEFT_JUSTIFY )
			screen.setTableInt("WBUnitList", 2, iRow, "<font=3>" + str(loopUnit.plot().getArea()) + "</font>", "", WidgetTypes.WIDGET_PYTHON, 8300 + iPlayer, loopUnit.getID(), CvUtil.FONT_LEFT_JUSTIFY )
			screen.setTableInt("WBUnitList", 3, iRow, "<font=3>" + str(loopUnit.getX()) + "</font>", "", WidgetTypes.WIDGET_PYTHON, 8300 + iPlayer, loopUnit.getID(), CvUtil.FONT_LEFT_JUSTIFY )
			screen.setTableInt("WBUnitList", 4, iRow, "<font=3>" + str(loopUnit.getY()) + "</font>", "", WidgetTypes.WIDGET_PYTHON, 8300 + iPlayer, loopUnit.getID(), CvUtil.FONT_LEFT_JUSTIFY )
			(loopUnit, iter) = pPlayer.nextUnit(iter, False)

		self.placeCityMap()
		self.placeUnitMap()

	def placeCityMap(self):
		screen = CyGInterfaceScreen("WBPlayerUnits", CvScreenEnums.WB_UNITLIST)
		pCity = pPlayer.getCity(iCityID)
		if pCity.isNone(): return
		screen.setText("GoToCity", "Background", "<font=4b>" + pCity.getName() + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/4, 50, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addPlotGraphicGFC("CityView", screen.getXResolution()/4 - iMapWidth/2, 80, iMapWidth, iMapHeight, pCity.plot(), 350, False, WidgetTypes.WIDGET_GENERAL, -1, -1)

	def placeUnitMap(self):
		screen = CyGInterfaceScreen("WBPlayerUnits", CvScreenEnums.WB_UNITLIST)
		pUnit = pPlayer.getUnit(iUnitID)
		if pUnit.isNone(): return
		screen.setText("GoToUnit", "Background", "<font=4b>" + pUnit.getName() + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()*3/4, 50, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addPlotGraphicGFC("UnitView", screen.getXResolution() * 3/4 - iMapWidth/2, 80, iMapWidth, iMapHeight, pUnit.plot(), 350, True, WidgetTypes.WIDGET_GENERAL, -1, -1)

	def handleInput(self, inputClass):
		screen = CyGInterfaceScreen("WBPlayerUnits", CvScreenEnums.WB_UNITLIST)
		global iCityID
		global iUnitID
		if inputClass.getFunctionName() == "CurrentPage":
			iIndex = screen.getPullDownData("CurrentPage", screen.getSelectedPullDownID("CurrentPage"))
			if iIndex == 0:
				WBPlayerScreen.WBPlayerScreen(self.top).interfaceScreen(iPlayer)
			elif iIndex == 1:
				WBTeamScreen.WBTeamScreen(self.top).interfaceScreen(iTeam)
			elif iIndex == 2:
				WBProjectScreen.WBProjectScreen(self.top).interfaceScreen(pTeam)
			elif iIndex == 3:
				WBTechScreen.WBTechScreen(self.top).interfaceScreen(pTeam)

		elif inputClass.getFunctionName() == "CurrentPlayer":
			iIndex = screen.getPullDownData("CurrentPlayer", screen.getSelectedPullDownID("CurrentPlayer"))
			iCityID = 0
			iUnitID = 0
			self.interfaceScreen(iIndex)

		elif inputClass.getFunctionName() == "WBCityList":
			iCityID = inputClass.getData2()
			self.placeCityMap()

		elif inputClass.getFunctionName() == "GoToCity":
			WBCityEditScreen.WBCityEditScreen(self.top).interfaceScreen(pPlayer.getCity(iCityID))

		elif inputClass.getFunctionName() == "WBUnitList":
			iUnitID = inputClass.getData2()
			self.placeUnitMap()

		elif inputClass.getFunctionName() == "GoToUnit":
			WBUnitScreen.WBUnitScreen(self.top).interfaceScreen(pPlayer.getUnit(iUnitID))
		return

	def update(self, fDelta):
		return 1