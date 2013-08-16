## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums

# globals
gc = CyGlobalContext()
g_pCity = None

class WBBonusScreen:

	def __init__(self):
		self.iList = []
		self.iBonusClass = -1

	def interfaceScreen(self, pCity):
		screen = CyGInterfaceScreen( "WBBonusScreen", CvScreenEnums.WB_BONUS)
		global g_pCity
		g_pCity = pCity

		self.nTableWidth = screen.getXResolution() - 40
		self.nTableHeight = screen.getYResolution() - 100
		screen.setRenderInterfaceOnly(True)
		screen.addPanel( "MainBG", u"", u"", True, False, -10, -10, screen.getXResolution() + 20, screen.getYResolution() + 20, PanelStyles.PANEL_STYLE_MAIN )
		screen.setDimensions(0, 0, screen.getXResolution(), screen.getYResolution())
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)
	
		screen.setText("BonusExit", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 25, screen.getYResolution() - 40, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )
		screen.setText("BonusHeader", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_BONUS", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		
		szDropdownName = str("BonusClass")
		screen.addDropDownBoxGFC(szDropdownName, 20, 20, 180, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_ALL",()), 0, 0, True)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_PEDIA_GENERAL",()), 1, 1, 0 == self.iBonusClass)
		iBonusClass = 1
		while not gc.getBonusClassInfo(iBonusClass) is None:
			sText = gc.getBonusClassInfo(iBonusClass).getType()
			sText = sText[sText.find("_") +1:]
			sText = sText.lower()
			sText = sText.capitalize()
			screen.addPullDownString(szDropdownName, sText, iBonusClass + 1, iBonusClass + 1, iBonusClass == self.iBonusClass)
			iBonusClass += 1

		szDropdownName = str("BonusCommands")
		screen.addDropDownBoxGFC(szDropdownName, screen.getXResolution() - 200, 20, 180, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_COMMANDS", ()), 0, 0, True)
		for i in xrange(3):
			screen.addPullDownString(szDropdownName, "+" + CyTranslator().getText("TXT_KEY_WB_ADD_ALL",(10 ** i,)), i + 1, i + 1, False)
		for i in xrange(3):
			screen.addPullDownString(szDropdownName, "-" + CyTranslator().getText("TXT_KEY_WB_ADD_ALL",(10 ** i,)), i + 4, i + 4, False)

		nColumns = 15
		screen.addTableControlGFC( "WBBonus", nColumns, 20, 60, self.nTableWidth, self.nTableHeight, True, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		for i in xrange(0, nColumns, 5):
			screen.setTableColumnHeader( "WBBonus", i, CyTranslator().getText("TXT_KEY_WB_ACCESS", ()), self.nTableWidth/(nColumns/5) - (30*4))
			screen.setTableColumnHeader( "WBBonus", i + 1, "+", 30)
			screen.setTableColumnHeader( "WBBonus", i + 2, "+", 30)
			screen.setTableColumnHeader( "WBBonus", i + 3, "-", 30)
			screen.setTableColumnHeader( "WBBonus", i + 4, "-", 30)

		self.iList = []
		for i in xrange(gc.getNumBonusInfos()):
			ItemInfo = gc.getBonusInfo(i)
			if self.iBonusClass != ItemInfo.getBonusClassType() and self.iBonusClass > -1: continue
			self.iList.append([ItemInfo.getDescription(), i])
		self.iList.sort()

		nRows = (len(self.iList) + (nColumns/5) - 1) / (nColumns/5)
		for i in xrange(nRows):
			screen.appendTableRow("WBBonus")

		for iCount in xrange(len(self.iList)):
			item = self.iList[iCount]
			iRow = iCount % nRows
			iColumn = iCount / nRows
			sItem = item[0]
			ItemInfo = gc.getBonusInfo(item[1])
			sButton = ItemInfo.getButton()
			iNum = pCity.getFreeBonus(item[1])
			if iNum > 0:
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
				sItem += " (" + str(iNum) + ")"
			else:
				sColor = CyTranslator().getText("[COLOR_YELLOW]", ())
			if pCity.isNoBonus(item[1]):
				sButton = CyArtFileMgr().getInterfaceArtInfo("WORLDBUILDER_EXIT").getPath()
				sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			screen.setTableText("WBBonus", iColumn * 5, iRow, sColor + sItem + "</color>", sButton, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, item[1], 1, CvUtil.FONT_LEFT_JUSTIFY )
			screen.setTableText("WBBonus", iColumn * 5 + 1, iRow, CyTranslator().getText("[COLOR_POSITIVE_TEXT]10[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, item[1], 2, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBBonus", iColumn * 5 + 2, iRow, CyTranslator().getText("[COLOR_POSITIVE_TEXT]1[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, item[1], 3, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBBonus", iColumn * 5 + 3, iRow, CyTranslator().getText("[COLOR_WARNING_TEXT]1[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, item[1], 4, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBBonus", iColumn * 5 + 4, iRow, CyTranslator().getText("[COLOR_WARNING_TEXT]10[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, item[1], 5, CvUtil.FONT_CENTER_JUSTIFY )
	
	def handleInput (self, inputClass):
		global g_pCity
		if inputClass.getFunctionName() == "BonusCommands":
			self.handlePlatyBonusCommandsCB(inputClass.getData())
			return 1
		if inputClass.getFunctionName() == "BonusClass":
			self.handlePlatyBonusClassCB(inputClass.getData())
			return 1
		if inputClass.getData2() == 1 and inputClass.getData1() > -1:
			self.handlePlatyNoBonusCB(inputClass.getData1())
			return 1
		if inputClass.getData2() == 2 and inputClass.getData1() > -1:
			self.handlePlatyFreeBonusCB(inputClass.getData1(), 10)
			return 1
		if inputClass.getData2() == 3 and inputClass.getData1() > -1:
			self.handlePlatyFreeBonusCB(inputClass.getData1(), 1)
			return 1
		if inputClass.getData2() == 4 and inputClass.getData1() > -1:
			self.handlePlatyFreeBonusCB(inputClass.getData1(), -1)
			return 1
		if inputClass.getData2() == 5 and inputClass.getData1() > -1:
			self.handlePlatyFreeBonusCB(inputClass.getData1(), -10)
			return 1
		return 1

	def handlePlatyBonusClassCB ( self, argsList ) :
		self.iBonusClass = int(argsList) - 1
		self.interfaceScreen(g_pCity)
		return 1

	def handlePlatyFreeBonusCB (self, iData1, iCount) :
		g_pCity.changeFreeBonus(iData1, iCount)
		if g_pCity.getFreeBonus(iData1) < 0:
			g_pCity.changeFreeBonus(iData1, - g_pCity.getFreeBonus(iData1))
		self.interfaceScreen(g_pCity)
		return 1

	def handlePlatyNoBonusCB (self, iData1):
		if g_pCity.isNoBonus(iData1):
			g_pCity.changeNoBonusCount(iData1, -1)
		else:
			g_pCity.changeNoBonusCount(iData1, 1)
		self.interfaceScreen(g_pCity)
		return 1

	def handlePlatyBonusCommandsCB (self, argsList) :
		iIndex = int(argsList) - 1
		if iIndex < 3:
			for item in self.iList:
				g_pCity.changeFreeBonus(item[1], 10 ** iIndex)
		else:
			iIndex -= 3
			for item in self.iList:
				g_pCity.changeFreeBonus(item[1], -10 ** iIndex)
				if g_pCity.getFreeBonus(item[1]) < 0:
					g_pCity.changeFreeBonus(item[1], - g_pCity.getFreeBonus(item[1]))
		self.interfaceScreen(g_pCity)
		return 1

	def update(self, fDelta):
		return 1