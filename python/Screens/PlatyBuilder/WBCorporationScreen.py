from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums
import WBGameDataScreen
import WBReligionScreen
import WBPlayerScreen
import WBTeamScreen
import WBCityEditScreen
import WBInfoScreen
import CvPlatyBuilderScreen
gc = CyGlobalContext()

bHeadquarter = False

class WBCorporationScreen:

	def __init__(self):
		self.iTable_Y = 80

	def interfaceScreen(self, iPlayerX):
		screen = CyGInterfaceScreen("WBCorporationScreen", CvScreenEnums.WB_CORPORATION)
		global iSelectedPlayer

		iSelectedPlayer = iPlayerX

		screen.setRenderInterfaceOnly(True)
		screen.addPanel("MainBG", u"", u"", True, False, -10, -10, screen.getXResolution() + 20, screen.getYResolution() + 20, PanelStyles.PANEL_STYLE_MAIN )
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)
	
		screen.setText("WBCorporationExit", "Background", "<font=4>" + CyTranslator().getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 30, screen.getYResolution() - 42, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )
		screen.setLabel("CorporationHeader", "Background", "<font=4b>" + CyTranslator().getText("TXT_KEY_CONCEPT_CORPORATIONS", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 20, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setLabel("HeadquarterHeader", "Background", "<font=3b>" + CyTranslator().getText("TXT_KEY_CORPORATION_HEADQUARTERS", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/8, self.iTable_Y - 30, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		
		iWidth = screen.getXResolution()/4 - 40
		screen.addDropDownBoxGFC("CurrentPage", 20, screen.getYResolution() - 42, iWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_PLAYER_DATA", ()), 0, 0, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_TEAM_DATA", ()), 1, 1, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_RELIGION", ()), 8, 8, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_CONCEPT_CORPORATIONS", ()), 9, 9, True)
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

		sText = "<font=3b>" + CyTranslator().getText("TXT_KEY_CORPORATION_HEADQUARTERS", ()) + "</font>"
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if bHeadquarter:
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		screen.setText("SetHeadquarter", "Background", sColor + sText + "</color>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 20, self.iTable_Y - 30, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		
		self.placeHeadquarter()
		self.placePlayerCities()

	def placePlayerCities(self):
		screen = CyGInterfaceScreen("WBCorporationScreen", CvScreenEnums.WB_CORPORATION)
		iX = screen.getXResolution()/4
		iY = self.iTable_Y
		iWidth = screen.getXResolution() * 3/4 - 20
		iHeight = (screen.getYResolution() - iY - 100) / 24 * 24 + 2

		screen.addTableControlGFC("WBAllCorporations", 1 + gc.getNumCorporationInfos(), iX, iY, iWidth, 50, False, True, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		screen.setTableColumnHeader("WBAllCorporations", 0, "", 150)
		for i in xrange(2):
			screen.appendTableRow("WBAllCorporations")
		sText = CyTranslator().getText("TXT_KEY_WB_CITY_ALL", ())
		screen.setTableText("WBAllCorporations", 0, 0, "<font=3b>" + sText + " (+)</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)
		screen.setTableText("WBAllCorporations", 0, 1, "<font=3b>" + sText + " (-)</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)

		for i in xrange(gc.getNumCorporationInfos()):
			sText = u"%c" %(gc.getCorporationInfo(i).getChar())
			screen.setTableColumnHeader("WBAllCorporations", i + 1, "", (iWidth - 150) / gc.getNumCorporationInfos())
			screen.setTableText("WBAllCorporations", i + 1, 0, "<font=4>" + sText + "</font>", "", WidgetTypes.WIDGET_PYTHON, 6782, i, CvUtil.FONT_CENTER_JUSTIFY)
			screen.setTableText("WBAllCorporations", i + 1, 1, "<font=4>" + sText + "</font>", "", WidgetTypes.WIDGET_PYTHON, 8201, i, CvUtil.FONT_CENTER_JUSTIFY)
			
		screen.addTableControlGFC("WBCityCorporations", 1 + gc.getNumCorporationInfos(), iX, iY + 60, iWidth, iHeight, False, True, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		screen.setTableColumnHeader("WBCityCorporations", 0, "", 150)
		for i in xrange(gc.getNumCorporationInfos()):
			screen.setTableColumnHeader("WBCityCorporations", i + 1, "", (iWidth - 150) / gc.getNumCorporationInfos())

		pPlayer = gc.getPlayer(iSelectedPlayer)
		(loopCity, iter) = pPlayer.firstCity(False)
		while(loopCity):
			iRow = screen.appendTableRow("WBCityCorporations")
			screen.setTableText("WBCityCorporations", 0, iRow, "<font=3>" + loopCity.getName() + "</font>", gc.getCivilizationInfo(loopCity.getCivilizationType()).getButton(), WidgetTypes.WIDGET_PYTHON, 7200 + iSelectedPlayer, loopCity.getID(), CvUtil.FONT_LEFT_JUSTIFY)
			for i in xrange(gc.getNumCorporationInfos()):
				sText = " "
				if loopCity.isHasCorporation(i):
					sText = u"%c" %(gc.getCorporationInfo(i).getChar())
				if loopCity.isHeadquartersByType(i):
					sText = u"%c" %(gc.getCorporationInfo(i).getHeadquarterChar())
				screen.setTableText("WBCityCorporations", i + 1, iRow, "<font=4>" + sText + "</font>", "", WidgetTypes.WIDGET_PYTHON, 8201, i, CvUtil.FONT_CENTER_JUSTIFY)
			(loopCity, iter) = pPlayer.nextCity(iter, False)

	def placeHeadquarter(self):
		screen = CyGInterfaceScreen("WBCorporationScreen", CvScreenEnums.WB_CORPORATION)
		iX = 20
		iY = self.iTable_Y
		iWidth = screen.getXResolution()/4 - 40
		iHeight = (screen.getYResolution() - iY - 40) / 24 * 24 + 2

		screen.addTableControlGFC("WBHeadquarter", 3, iX, iY, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		screen.setTableColumnHeader("WBHeadquarter", 0, "", 24)
		screen.setTableColumnHeader("WBHeadquarter", 1, "", 24)
		screen.setTableColumnHeader("WBHeadquarter", 2, "", iWidth - 48)

		for i in xrange(gc.getNumCorporationInfos()):
			iRow = screen.appendTableRow("WBHeadquarter")
			screen.setTableText("WBHeadquarter", 0, iRow, "", gc.getCorporationInfo(i).getButton(), WidgetTypes.WIDGET_PYTHON, 8201, i, CvUtil.FONT_LEFT_JUSTIFY)
			pHeadquarter = CyGame().getHeadquarters(i)
			if not pHeadquarter.isNone():
				iPlayerX = pHeadquarter.getOwner()
				pPlayerX = gc.getPlayer(iPlayerX)
				iLeader = pPlayerX.getLeaderType()
				screen.setTableText("WBHeadquarter", 1, iRow, "", gc.getLeaderHeadInfo(iLeader).getButton(), WidgetTypes.WIDGET_PYTHON, 7876, iPlayerX * 10000 + iLeader, CvUtil.FONT_LEFT_JUSTIFY)
				screen.setTableText("WBHeadquarter", 2, iRow, "<font=3>" + pHeadquarter.getName() + "</font>", gc.getCivilizationInfo(pHeadquarter.getCivilizationType()).getButton(), WidgetTypes.WIDGET_PYTHON, 7200 + iPlayerX, pHeadquarter.getID(), CvUtil.FONT_LEFT_JUSTIFY)
	
	def handleInput(self, inputClass):
		screen = CyGInterfaceScreen("WBCorporationScreen", CvScreenEnums.WB_CORPORATION)
		global iSelectedPlayer
		global bHeadquarter

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
			elif iIndex == 8:
				WBReligionScreen.WBReligionScreen().interfaceScreen(iSelectedPlayer)
			elif iIndex == 10:
				WBGameDataScreen.WBGameDataScreen(CvPlatyBuilderScreen.CvWorldBuilderScreen()).interfaceScreen()
			elif iIndex == 11:
				WBInfoScreen.WBInfoScreen().interfaceScreen(iSelectedPlayer)

		elif inputClass.getFunctionName() == "CurrentPlayer":
			iSelectedPlayer = screen.getPullDownData("CurrentPlayer", screen.getSelectedPullDownID("CurrentPlayer"))
			self.interfaceScreen(iSelectedPlayer)

		elif inputClass.getFunctionName() == "WBCityCorporations":
			if inputClass.getData1() == 8201:
				pPlayer = gc.getPlayer(iSelectedPlayer)
				(loopCity, iter) = pPlayer.firstCity(False)
				while(loopCity):
					if iter - 1 == inputClass.getData():
						if bHeadquarter:
							self.editHeadquarter(inputClass.getData2(), loopCity)
						else:
							self.editCorporation(inputClass.getData2(), loopCity, 2)
						break
					(loopCity, iter) = pPlayer.nextCity(iter, False)
				self.placePlayerCities()

		elif inputClass.getFunctionName() == "WBAllCorporations":
			if inputClass.getButtonType() == WidgetTypes.WIDGET_PYTHON:
				pPlayer = gc.getPlayer(iSelectedPlayer)
				(loopCity, iter) = pPlayer.firstCity(False)
				while(loopCity):
					self.editCorporation(inputClass.getData2(), loopCity, inputClass.getData1() == 6782)
					(loopCity, iter) = pPlayer.nextCity(iter, False)
				self.placePlayerCities()

		elif inputClass.getFunctionName() == "SetHeadquarter":
			bHeadquarter = not bHeadquarter
			sText = "<font=3b>" + CyTranslator().getText("TXT_KEY_CORPORATION_HEADQUARTERS", ()) + "</font>"
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			if bHeadquarter:
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			screen.modifyString("SetHeadquarter", sColor + sText + "</color>", 0)
		return 1

	def editHeadquarter(self, item, pCity):
		if pCity.isHeadquartersByType(item):
			CyGame().clearHeadquarters(item)
		else:
			CyGame().setHeadquarters(item, pCity, False)
		self.placeHeadquarter()

	def editCorporation(self, item, pCity, iType):
		if iType == 2:
			iType = not pCity.isHasCorporation(item)
		if not iType and pCity.isHeadquartersByType(item):
			CyGame().clearHeadquarters(item)
			self.placeHeadquarter()
		pCity.setHasCorporation(item, iType, False, False)

	def update(self, fDelta):
		return 1