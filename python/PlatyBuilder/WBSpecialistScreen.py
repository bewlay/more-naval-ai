## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums

# globals
gc = CyGlobalContext()
g_pCity = None

class WBSpecialistScreen:

	def __init__(self):
		self.iList = []
		self.iList2 = []

	def interfaceScreen(self, pCity):
		screen = CyGInterfaceScreen( "WBSpecialistScreen", CvScreenEnums.WB_SPECIALIST)
		global g_pCity
		g_pCity = pCity

		self.nTableWidth = screen.getXResolution() - 40
		self.nTableHeight = screen.getYResolution()/2 - 100
		screen.setRenderInterfaceOnly(True)
		screen.addPanel( "MainBG", u"", u"", True, False, -10, -10, screen.getXResolution() + 20, screen.getYResolution() + 20, PanelStyles.PANEL_STYLE_MAIN )
		screen.setDimensions(0, 0, screen.getXResolution(), screen.getYResolution())
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)

		screen.addPanel( "SpecialistBG", u"", u"", True, False, 0, 0, screen.getXResolution(), screen.getYResolution()/2, PanelStyles.PANEL_STYLE_MAIN )
		screen.addPanel( "GreatPeopleBG", u"", u"", True, False, 0, screen.getYResolution()/2, screen.getXResolution(), screen.getYResolution()/2, PanelStyles.PANEL_STYLE_MAIN )
		screen.setText("SpecialistHeader", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_WB_FREE_SPECIALISTS", ()) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, 20, 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		sText = CyTranslator().getText("TXT_KEY_WB_GREAT_PEOPLE_RATE", (pCity.getBaseGreatPeopleRate(),))
		screen.setText("GreatPeopleHeader", "Background", u"<font=4b>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, 20, screen.getYResolution()/2 + 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		sText = CyTranslator().getText("TXT_KEY_WB_PROGRESS", (pCity.getGreatPeopleProgress(), gc.getPlayer(pCity.getOwner()).greatPeopleThreshold(False)))
		screen.setText("GreatPeopleHeader2", "Background", u"<font=4b>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, screen.getXResolution()/2 + 20, screen.getYResolution()/2 + 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		screen.setText("SpecialistExit", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 25, screen.getYResolution() - 40, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )

		szDropdownName = str("SpecialistCommands")
		screen.addDropDownBoxGFC(szDropdownName, screen.getXResolution() - 200, 20, 180, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_COMMANDS", ()), 0, 0, True)
		for i in xrange(3):
			screen.addPullDownString(szDropdownName, "+" + CyTranslator().getText("TXT_KEY_WB_ADD_ALL",(10 ** i,)), i + 1, i + 1, False)
		for i in xrange(3):
			screen.addPullDownString(szDropdownName, "-" + CyTranslator().getText("TXT_KEY_WB_ADD_ALL",(10 ** i,)), i + 4, i + 4, False)

		szDropdownName = str("GreatPeopleRateCommands")
		screen.addDropDownBoxGFC(szDropdownName, screen.getXResolution()/2 - 180, screen.getYResolution()/2 + 20, 180, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_COMMANDS", ()), 0, 0, True)
		for i in xrange(4):
			screen.addPullDownString(szDropdownName, "+" + str(10 ** i,), i + 1, i + 1, False)
		for i in xrange(4):
			screen.addPullDownString(szDropdownName, "-" + str(10 ** i,), i + 5, i + 5, False)

		szDropdownName = str("GreatPeopleCommands")
		screen.addDropDownBoxGFC(szDropdownName, screen.getXResolution() - 200, screen.getYResolution()/2 + 20, 180, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_COMMANDS", ()), 0, 0, True)
		for i in xrange(3):
			screen.addPullDownString(szDropdownName, "+" + CyTranslator().getText("TXT_KEY_WB_ADD_ALL",(10 ** i,)), i + 1, i + 1, False)
		for i in xrange(3):
			screen.addPullDownString(szDropdownName, "-" + CyTranslator().getText("TXT_KEY_WB_ADD_ALL",(10 ** i,)), i + 4, i + 4, False)

		nColumns = 14
		screen.addTableControlGFC( "WBSpecialist", nColumns, 20, 60, self.nTableWidth, self.nTableHeight, True, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		screen.addTableControlGFC( "WBGreatPeople", nColumns, 20, screen.getYResolution()/2 + 60, self.nTableWidth, self.nTableHeight, True, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		for i in xrange(0, nColumns, 7):
			screen.setTableColumnHeader( "WBSpecialist", i, "", self.nTableWidth/(nColumns/7) - (30*6 + 7*2))
			screen.setTableColumnHeader( "WBSpecialist", i + 1, "+", 37)
			screen.setTableColumnHeader( "WBSpecialist", i + 2, "+", 30)
			screen.setTableColumnHeader( "WBSpecialist", i + 3, "+", 30)
			screen.setTableColumnHeader( "WBSpecialist", i + 4, "-", 30)
			screen.setTableColumnHeader( "WBSpecialist", i + 5, "-", 30)
			screen.setTableColumnHeader( "WBSpecialist", i + 6, "-", 37)
			screen.setTableColumnHeader( "WBGreatPeople", i, "", self.nTableWidth/(nColumns/7) - (30*6 + 7*2))
			screen.setTableColumnHeader( "WBGreatPeople", i + 1, "+", 37)
			screen.setTableColumnHeader( "WBGreatPeople", i + 2, "+", 30)
			screen.setTableColumnHeader( "WBGreatPeople", i + 3, "+", 30)
			screen.setTableColumnHeader( "WBGreatPeople", i + 4, "-", 30)
			screen.setTableColumnHeader( "WBGreatPeople", i + 5, "-", 30)
			screen.setTableColumnHeader( "WBGreatPeople", i + 6, "-", 37)

		self.iList = []
		self.iList2 = []
		for i in xrange(gc.getNumSpecialistInfos()):
			ItemInfo = gc.getSpecialistInfo(i)
			self.iList.append((ItemInfo.getDescription(), i))
			iGPClass = ItemInfo.getGreatPeopleUnitClass()
			if iGPClass == -1: continue
			iGP = gc.getCivilizationInfo(pCity.getCivilizationType()).getCivilizationUnits(iGPClass)
			if iGP == -1: continue
			if not iGP in self.iList2:
				self.iList2.append(iGP)

		for i in xrange(gc.getNumBuildingInfos()):
			ItemInfo = gc.getBuildingInfo(i)
			iGPClass = ItemInfo.getGreatPeopleUnitClass()
			if iGPClass == -1: continue
			iGP = gc.getCivilizationInfo(pCity.getCivilizationType()).getCivilizationUnits(iGPClass)
			if iGP == -1: continue
			if not iGP in self.iList2:
				self.iList2.append(iGP)

		for i in xrange(len(self.iList2)):
			GPInfo = gc.getUnitInfo(self.iList2[i])
			self.iList2[i] = [GPInfo.getDescription(), self.iList2[i]]

##		self.iList.sort()
##		self.iList2.sort()

		nRows = (len(self.iList) + (nColumns/5) - 1) / (nColumns/5)
		for i in xrange(nRows):
			screen.appendTableRow("WBSpecialist")

		for iCount in xrange(len(self.iList)):
			item = self.iList[iCount]
			iRow = iCount % nRows
			iColumn = iCount / nRows
			sItem = item[0]
			ItemInfo = gc.getSpecialistInfo(item[1])
			iNum = pCity.getFreeSpecialistCount(item[1])
			if iNum > 0:
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
				sItem += " (" + str(iNum) + ")"
			else:
				sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			screen.setTableText("WBSpecialist", iColumn * 7, iRow, sColor + sItem + "</color>", ItemInfo.getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_SPECIALIST, item[1], 1, CvUtil.FONT_LEFT_JUSTIFY )
			screen.setTableText("WBSpecialist", iColumn * 7 + 1, iRow, CyTranslator().getText("[COLOR_POSITIVE_TEXT]100[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1030, item[1], CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBSpecialist", iColumn * 7 + 2, iRow, CyTranslator().getText("[COLOR_POSITIVE_TEXT]10[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1031, item[1], CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBSpecialist", iColumn * 7 + 3, iRow, CyTranslator().getText("[COLOR_POSITIVE_TEXT]1[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1032, item[1], CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBSpecialist", iColumn * 7 + 4, iRow, CyTranslator().getText("[COLOR_WARNING_TEXT]1[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1033, item[1], CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBSpecialist", iColumn * 7 + 5, iRow, CyTranslator().getText("[COLOR_WARNING_TEXT]10[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1034, item[1], CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBSpecialist", iColumn * 7 + 6, iRow, CyTranslator().getText("[COLOR_WARNING_TEXT]100[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1035, item[1], CvUtil.FONT_CENTER_JUSTIFY )

		nRows = (len(self.iList2) + (nColumns/5) - 1) / (nColumns/5)
		for i in xrange(nRows):
			screen.appendTableRow("WBGreatPeople")

		for iCount in xrange(len(self.iList2)):
			item = self.iList2[iCount]
			iRow = iCount % nRows
			iColumn = iCount / nRows
			sItem = item[0]
			ItemInfo = gc.getUnitInfo(item[1])
			iNum = pCity.getGreatPeopleUnitProgress(item[1])
			if iNum > 0:
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
				sItem += " (" + str(iNum) + ")"
			else:
				sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			screen.setTableText("WBGreatPeople", iColumn * 7, iRow, sColor + sItem + "</color>", ItemInfo.getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, item[1], 1, CvUtil.FONT_LEFT_JUSTIFY )
			screen.setTableText("WBGreatPeople", iColumn * 7 + 1, iRow, CyTranslator().getText("[COLOR_POSITIVE_TEXT]100[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1036, item[1], CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBGreatPeople", iColumn * 7 + 2, iRow, CyTranslator().getText("[COLOR_POSITIVE_TEXT]10[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1037, item[1], CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBGreatPeople", iColumn * 7 + 3, iRow, CyTranslator().getText("[COLOR_POSITIVE_TEXT]1[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1038, item[1], CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBGreatPeople", iColumn * 7 + 4, iRow, CyTranslator().getText("[COLOR_WARNING_TEXT]1[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1039, item[1], CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBGreatPeople", iColumn * 7 + 5, iRow, CyTranslator().getText("[COLOR_WARNING_TEXT]10[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1040, item[1], CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBGreatPeople", iColumn * 7 + 6, iRow, CyTranslator().getText("[COLOR_WARNING_TEXT]100[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1041, item[1], CvUtil.FONT_CENTER_JUSTIFY )

	def handleInput (self, inputClass):
		global g_pCity
		if inputClass.getFunctionName() == "SpecialistCommands":
			self.handlePlatySpecialistCommandsCB(inputClass.getData())
			return 1
		if inputClass.getFunctionName() == "GreatPeopleCommands":
			self.handlePlatyGreatPeopleCommandsCB(inputClass.getData())
			return 1
		if inputClass.getFunctionName() == "GreatPeopleRateCommands":
			self.handlePlatyGreatPeopleRateCommandsCB(inputClass.getData())
			return 1
		if inputClass.getData2() == 1 and inputClass.getData1() > -1 and inputClass.getData1() < 1030:
			self.interfaceScreen(g_pCity)
			return 1
		if inputClass.getData1() == 1030 and inputClass.getData2() > -1:
			self.handlePlatyFreeSpecialistCB(inputClass.getData2(), 100)
			return 1
		if inputClass.getData1() == 1031 and inputClass.getData2() > -1:
			self.handlePlatyFreeSpecialistCB(inputClass.getData2(), 10)
			return 1
		if inputClass.getData1() == 1032 and inputClass.getData2() > -1:
			self.handlePlatyFreeSpecialistCB(inputClass.getData2(), 1)
			return 1
		if inputClass.getData1() == 1033 and inputClass.getData2() > -1:
			self.handlePlatyFreeSpecialistCB(inputClass.getData2(), -1)
			return 1
		if inputClass.getData1() == 1034 and inputClass.getData2() > -1:
			self.handlePlatyFreeSpecialistCB(inputClass.getData2(), -10)
			return 1
		if inputClass.getData1() == 1035 and inputClass.getData2() > -1:
			self.handlePlatyFreeSpecialistCB(inputClass.getData2(), -100)
			return 1
		if inputClass.getData1() == 1036 and inputClass.getData2() > -1:
			self.handlePlatyGreatPeopleProgressCB(inputClass.getData2(), 100)
			return 1
		if inputClass.getData1() == 1037 and inputClass.getData2() > -1:
			self.handlePlatyGreatPeopleProgressCB(inputClass.getData2(), 10)
			return 1
		if inputClass.getData1() == 1038 and inputClass.getData2() > -1:
			self.handlePlatyGreatPeopleProgressCB(inputClass.getData2(), 1)
			return 1
		if inputClass.getData1() == 1039 and inputClass.getData2() > -1:
			self.handlePlatyGreatPeopleProgressCB(inputClass.getData2(), -1)
			return 1
		if inputClass.getData1() == 1040 and inputClass.getData2() > -1:
			self.handlePlatyGreatPeopleProgressCB(inputClass.getData2(), -10)
			return 1
		if inputClass.getData1() == 1041 and inputClass.getData2() > -1:
			self.handlePlatyGreatPeopleProgressCB(inputClass.getData2(), -100)
			return 1
		return 1

	def handlePlatyGreatPeopleRateCommandsCB (self, argsList) :
		iIndex = int(argsList) - 1
		if iIndex < 4:
			g_pCity.changeBaseGreatPeopleRate(10 ** iIndex)
		else:
			iIndex -= 4
			g_pCity.changeBaseGreatPeopleRate(-10 ** iIndex)
			if g_pCity.getBaseGreatPeopleRate() < 0:
				g_pCity.changeBaseGreatPeopleRate(-g_pCity.getBaseGreatPeopleRate())
		self.interfaceScreen(g_pCity)
		return 1

	def handlePlatyGreatPeopleCommandsCB (self, argsList) :
		iIndex = int(argsList) - 1
		if iIndex < 3:
			for item in self.iList2:
				g_pCity.changeGreatPeopleUnitProgress(item[1], 10 ** iIndex)
				g_pCity.changeGreatPeopleProgress(10 ** iIndex)
		else:
			iIndex -= 3
			for item in self.iList2:
				g_pCity.changeGreatPeopleUnitProgress(item[1], -10 ** iIndex)
				g_pCity.changeGreatPeopleProgress(-10 ** iIndex)
				if g_pCity.getGreatPeopleUnitProgress(item[1]) < 0:
					g_pCity.changeGreatPeopleUnitProgress(item[1], - g_pCity.getGreatPeopleUnitProgress(item[1]))
				if g_pCity.getGreatPeopleProgress() < 0:
					g_pCity.changeGreatPeopleProgress(- g_pCity.getGreatPeopleProgress())
		self.interfaceScreen(g_pCity)
		return 1

	def handlePlatyGreatPeopleProgressCB (self, iData1, iCount) :
		g_pCity.changeGreatPeopleUnitProgress(iData1, iCount)
		g_pCity.changeGreatPeopleProgress(iCount)
		if g_pCity.getGreatPeopleUnitProgress(iData1) < 0:
			g_pCity.changeGreatPeopleUnitProgress(iData1, - g_pCity.getGreatPeopleUnitProgress(iData1))
		if g_pCity.getGreatPeopleProgress() < 0:
			g_pCity.changeGreatPeopleProgress(- g_pCity.getGreatPeopleProgress())
		self.interfaceScreen(g_pCity)
		return 1

	def handlePlatyFreeSpecialistCB (self, iData1, iCount) :
		g_pCity.changeFreeSpecialistCount(iData1, iCount)
		if g_pCity.getFreeSpecialistCount(iData1) < 0:
			g_pCity.changeFreeSpecialistCount(iData1, - g_pCity.getFreeSpecialistCount(iData1))
		self.interfaceScreen(g_pCity)
		return 1

	def handlePlatySpecialistCommandsCB (self, argsList) :
		iIndex = int(argsList) - 1
		if iIndex < 3:
			for item in self.iList:
				g_pCity.changeFreeSpecialistCount(item[1], 10 ** iIndex)
		else:
			iIndex -= 3
			for item in self.iList:
				g_pCity.changeFreeSpecialistCount(item[1], -10 ** iIndex)
				if g_pCity.getFreeSpecialistCount(item[1]) < 0:
					g_pCity.changeFreeSpecialistCount(item[1], - g_pCity.getFreeSpecialistCount(item[1]))
		self.interfaceScreen(g_pCity)
		return 1

	def update(self, fDelta):
		return 1