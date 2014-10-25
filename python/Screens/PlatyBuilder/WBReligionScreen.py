from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums
import WBGameDataScreen
import WBCorporationScreen
import WBPlayerScreen
import WBTeamScreen
import WBCityEditScreen
import WBInfoScreen
import CvPlatyBuilderScreen
gc = CyGlobalContext()

bHoly = False

class WBReligionScreen:

	def __init__(self):
		self.iTable_Y = 80

	def interfaceScreen(self, iPlayerX):
		screen = CyGInterfaceScreen("WBReligionScreen", CvScreenEnums.WB_RELIGION)
		global iSelectedPlayer

		iSelectedPlayer = iPlayerX

		screen.setRenderInterfaceOnly(True)
		screen.addPanel( "MainBG", u"", u"", True, False, -10, -10, screen.getXResolution() + 20, screen.getYResolution() + 20, PanelStyles.PANEL_STYLE_MAIN )
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)
	
		screen.setText("WBReligionExit", "Background", "<font=4>" + CyTranslator().getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 30, screen.getYResolution() - 42, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )
		screen.setLabel("ReligionHeader", "Background", "<font=4b>" + CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_RELIGION", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 20, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setLabel("HolyCityHeader", "Background", "<font=3b>" + CyTranslator().getText("TXT_KEY_RELIGION_SCREEN_HOLY_CITY", ())[:-1] + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/8, self.iTable_Y - 30, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setLabel("StateReligionHeader", "Background", "<font=3b>" + CyTranslator().getText("TXT_KEY_WB_STATE_RELIGION",()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/8,screen.getYResolution()/2, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		
		iWidth = screen.getXResolution()/4 - 40
		screen.addDropDownBoxGFC("CurrentPage", 20, screen.getYResolution() - 42, iWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_PLAYER_DATA", ()), 0, 0, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_TEAM_DATA", ()), 1, 1, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_RELIGION", ()), 8, 8, True)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_CONCEPT_CORPORATIONS", ()), 9, 9, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PITBOSS_GAME_OPTIONS", ()), 10, 10, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_INFO_SCREEN", ()), 11, 11, False)

		screen.addDropDownBoxGFC("CurrentPlayer", screen.getXResolution()/4, self.iTable_Y - 30, 150, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		for i in xrange(gc.getMAX_PLAYERS()):
			pPlayerX = gc.getPlayer(i)
			if pPlayerX.isEverAlive():
				sText = pPlayerX.getName()
				if not pPlayerX.isAlive():
					sText = "*" + sText
				screen.addPullDownString("CurrentPlayer", sText, i, i, i == iSelectedPlayer)

		sText = "<font=3b>" + CyTranslator().getText("TXT_KEY_RELIGION_SCREEN_HOLY_CITY", ())[:-1] + "</font>"
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if bHoly:
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		screen.setText("SetHoly", "Background", sColor + sText + "</color>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 20, self.iTable_Y - 30, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		
		self.placeHolyCities()
		self.placeStateReligion()
		self.placePlayerCities()

	def placePlayerCities(self):
		screen = CyGInterfaceScreen("WBReligionScreen", CvScreenEnums.WB_RELIGION)
		iX = screen.getXResolution()/4
		iY = self.iTable_Y
		iWidth = screen.getXResolution() * 3/4 - 20
		iHeight = (screen.getYResolution() - iY - 100) / 24 * 24 + 2

		screen.addTableControlGFC("WBAllReligions", 1 + gc.getNumReligionInfos(), iX, iY, iWidth, 50, False, True, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		screen.setTableColumnHeader("WBAllReligions", 0, "", 150)
		for i in xrange(2):
			screen.appendTableRow("WBAllReligions")
		sText = CyTranslator().getText("TXT_KEY_WB_CITY_ALL", ())
		screen.setTableText("WBAllReligions", 0, 0, "<font=3b>" + sText + " (+)</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)
		screen.setTableText("WBAllReligions", 0, 1, "<font=3b>" + sText + " (-)</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)

		for i in xrange(gc.getNumReligionInfos()):
			sText = u"%c" %(gc.getReligionInfo(i).getChar())
			screen.setTableColumnHeader("WBAllReligions", i + 1, "", (iWidth - 150) / gc.getNumReligionInfos())
			screen.setTableText("WBAllReligions", i + 1, 0, "<font=4>" + sText + "</font>", "", WidgetTypes.WIDGET_HELP_RELIGION, i, 1, CvUtil.FONT_CENTER_JUSTIFY)
			screen.setTableText("WBAllReligions", i + 1, 1, "<font=4>" + sText + "</font>", "", WidgetTypes.WIDGET_HELP_RELIGION, i, 2, CvUtil.FONT_CENTER_JUSTIFY)
			
		screen.addTableControlGFC("WBCityReligions", 1 + gc.getNumReligionInfos(), iX, iY + 60, iWidth, iHeight, False, True, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		screen.setTableColumnHeader("WBCityReligions", 0, "", 150)
		for i in xrange(gc.getNumReligionInfos()):
			screen.setTableColumnHeader("WBCityReligions", i + 1, "", (iWidth - 150) / gc.getNumReligionInfos())

		pPlayer = gc.getPlayer(iSelectedPlayer)
		(loopCity, iter) = pPlayer.firstCity(False)
		while(loopCity):
			iRow = screen.appendTableRow("WBCityReligions")
			screen.setTableText("WBCityReligions", 0, iRow, "<font=3>" + loopCity.getName() + "</font>", gc.getCivilizationInfo(loopCity.getCivilizationType()).getButton(), WidgetTypes.WIDGET_PYTHON, 7200 + iSelectedPlayer, loopCity.getID(), CvUtil.FONT_LEFT_JUSTIFY)
			for i in xrange(gc.getNumReligionInfos()):
				sText = " "
				if loopCity.isHasReligion(i):
					sText = u"%c" %(gc.getReligionInfo(i).getChar())
				if loopCity.isHolyCityByType(i):
					sText = u"%c" %(gc.getReligionInfo(i).getHolyCityChar())
				screen.setTableText("WBCityReligions", i + 1, iRow, "<font=4>" + sText + "</font>", "", WidgetTypes.WIDGET_HELP_RELIGION, i, loopCity.getID(), CvUtil.FONT_CENTER_JUSTIFY)
			(loopCity, iter) = pPlayer.nextCity(iter, False)

	def placeHolyCities(self):
		screen = CyGInterfaceScreen("WBReligionScreen", CvScreenEnums.WB_RELIGION)
		iX = 20
		iY = self.iTable_Y
		iWidth = screen.getXResolution()/4 - 40
		iHeight = (screen.getYResolution()/2 - iY) / 24 * 24 + 2

		screen.addTableControlGFC("WBHolyCity", 3, iX, iY, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		screen.setTableColumnHeader("WBHolyCity", 0, "", 24)
		screen.setTableColumnHeader("WBHolyCity", 1, "", 24)
		screen.setTableColumnHeader("WBHolyCity", 2, "", iWidth - 48)

		for i in xrange(gc.getNumReligionInfos()):
			iRow = screen.appendTableRow("WBHolyCity")
			screen.setTableText("WBHolyCity", 0, iRow, "", gc.getReligionInfo(i).getButton(), WidgetTypes.WIDGET_HELP_RELIGION, i, 1, CvUtil.FONT_LEFT_JUSTIFY)
			pHolyCity = CyGame().getHolyCity(i)
			if not pHolyCity.isNone():
				iPlayerX = pHolyCity.getOwner()
				pPlayerX = gc.getPlayer(iPlayerX)
				iLeader = pPlayerX.getLeaderType()
				screen.setTableText("WBHolyCity", 1, iRow, "", gc.getLeaderHeadInfo(iLeader).getButton(), WidgetTypes.WIDGET_PYTHON, 7876, iPlayerX * 10000 + iLeader, CvUtil.FONT_LEFT_JUSTIFY)
				screen.setTableText("WBHolyCity", 2, iRow, "<font=3>" + pHolyCity.getName() + "</font>", gc.getCivilizationInfo(pHolyCity.getCivilizationType()).getButton(), WidgetTypes.WIDGET_PYTHON, 7200 + iPlayerX, pHolyCity.getID(), CvUtil.FONT_LEFT_JUSTIFY)
	
	def placeStateReligion(self):				
		screen = CyGInterfaceScreen("WBReligionScreen", CvScreenEnums.WB_RELIGION)
		iX = 20
		iY = screen.getYResolution()/2 + 30
		iWidth = screen.getXResolution()/4 - 40
		iHeight = (screen.getYResolution() - iY - 40) / 24 * 24 + 2

		screen.addTableControlGFC("WBStateReligion", 3, iX, iY, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		screen.setTableColumnHeader("WBStateReligion", 0, "", 24)
		screen.setTableColumnHeader("WBStateReligion", 1, "", 24)
		screen.setTableColumnHeader("WBStateReligion", 2, "", iWidth - 48)
		
		for iPlayerX in xrange(gc.getMAX_PLAYERS()):
			pPlayerX = gc.getPlayer(iPlayerX)
			if not pPlayerX.isAlive(): continue
			iRow = screen.appendTableRow("WBStateReligion")
			sColor = u"<color=%d,%d,%d,%d>" %(pPlayerX.getPlayerTextColorR(), pPlayerX.getPlayerTextColorG(), pPlayerX.getPlayerTextColorB(), pPlayerX.getPlayerTextColorA())
			iCivilization = pPlayerX.getCivilizationType()
			iLeader = pPlayerX.getLeaderType()
			iStateReligion = pPlayerX.getStateReligion()
			if iStateReligion > -1:
				screen.setTableText("WBStateReligion", 0, iRow, "", gc.getReligionInfo(iStateReligion).getButton(), WidgetTypes.WIDGET_HELP_RELIGION, iStateReligion, 1, CvUtil.FONT_LEFT_JUSTIFY)
			screen.setTableText("WBStateReligion", 1, iRow, "", gc.getCivilizationInfo(iCivilization).getButton(), WidgetTypes.WIDGET_PYTHON, 7872, iPlayerX * 10000 + iCivilization, CvUtil.FONT_LEFT_JUSTIFY)
			screen.setTableText("WBStateReligion", 2, iRow, "<font=3>" + sColor + pPlayerX.getName() + "</font></color>", gc.getLeaderHeadInfo(iLeader).getButton(), WidgetTypes.WIDGET_PYTHON, 7876, iPlayerX * 10000 + iLeader, CvUtil.FONT_LEFT_JUSTIFY)
				
	def handleInput (self, inputClass):
		screen = CyGInterfaceScreen("WBReligionScreen", CvScreenEnums.WB_RELIGION)
		global iSelectedPlayer
		global bHoly

		if inputClass.getButtonType() == WidgetTypes.WIDGET_PYTHON:
			if inputClass.getData1() > 7199 and inputClass.getData1() < 7300:
				iCityID = inputClass.getData2()
				iPlayerX = inputClass.getData1() - 7200
				WBCityEditScreen.WBCityEditScreen().interfaceScreen(gc.getPlayer(iPlayerX).getCity(iCityID))

			elif inputClass.getData1() == 7876 or inputClass.getData1() == 7872:
				iPlayerX = inputClass.getData2() /10000
				WBPlayerScreen.WBPlayerScreen().interfaceScreen(iPlayerX)

		if inputClass.getFunctionName() == "CurrentPage":
			iIndex = screen.getPullDownData("CurrentPage", screen.getSelectedPullDownID("CurrentPage"))
			if iIndex == 0:
				WBPlayerScreen.WBPlayerScreen().interfaceScreen(iSelectedPlayer)
			elif iIndex == 1:
				WBTeamScreen.WBTeamScreen().interfaceScreen(gc.getPlayer(iSelectedPlayer).getTeam())
			elif iIndex == 9:
				WBCorporationScreen.WBCorporationScreen().interfaceScreen(iSelectedPlayer)
			elif iIndex == 10:
				WBGameDataScreen.WBGameDataScreen(CvPlatyBuilderScreen.CvWorldBuilderScreen()).interfaceScreen()
			elif iIndex == 11:
				WBInfoScreen.WBInfoScreen().interfaceScreen(iSelectedPlayer)

		elif inputClass.getFunctionName() == "CurrentPlayer":
			iSelectedPlayer = screen.getPullDownData("CurrentPlayer", screen.getSelectedPullDownID("CurrentPlayer"))
			self.interfaceScreen(iSelectedPlayer)

		elif inputClass.getFunctionName() == "WBCityReligions":
			if inputClass.getButtonType() == WidgetTypes.WIDGET_HELP_RELIGION:
				pPlayer = gc.getPlayer(iSelectedPlayer)
				if bHoly:
					self.editHolyCity(inputClass.getData1(), pPlayer.getCity(inputClass.getData2()))
				else:
					self.editReligion(inputClass.getData1(), pPlayer.getCity(inputClass.getData2()), 2)
				self.placePlayerCities()

		elif inputClass.getFunctionName() == "WBAllReligions":
			if inputClass.getButtonType() == WidgetTypes.WIDGET_HELP_RELIGION:
				pPlayer = gc.getPlayer(iSelectedPlayer)
				(loopCity, iter) = pPlayer.firstCity(False)
				while(loopCity):
					self.editReligion(inputClass.getData1(), loopCity, inputClass.getData2() == 1)
					(loopCity, iter) = pPlayer.nextCity(iter, False)
				self.placePlayerCities()

		elif inputClass.getFunctionName() == "SetHoly":
			bHoly = not bHoly
			sText = "<font=3b>" + CyTranslator().getText("TXT_KEY_RELIGION_SCREEN_HOLY_CITY", ())[:-1] + "</font>"
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			if bHoly:
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			screen.modifyString("SetHoly", sColor + sText + "</color>", 0)
		return 1

	def editHolyCity(self, item, pCity):
		if pCity.isHolyCityByType(item):
			CyGame().clearHolyCity(item)
		else:
			CyGame().setHolyCity(item, pCity, False)
		self.placeHolyCities()

	def editReligion(self, item, pCity, iType):
		if iType == 2:
			iType = not pCity.isHasReligion(item)
		if not iType and pCity.isHolyCityByType(item):
			CyGame().clearHolyCity(item)
			self.placeHolyCities()
		pCity.setHasReligion(item, iType, False, False)

	def update(self, fDelta):
		return 1