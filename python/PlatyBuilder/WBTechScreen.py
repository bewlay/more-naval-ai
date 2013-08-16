## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums

# globals
gc = CyGlobalContext()
g_pCity = None

class WBTechScreen:

	def __init__(self):
		self.iEra = 1000
		self.iList = []

	def interfaceScreen(self, pTeam):
		screen = CyGInterfaceScreen( "WBTechScreen", CvScreenEnums.WB_TECH)
		global g_pTeam
		g_pTeam = pTeam

		self.nTableWidth = screen.getXResolution() - 40
		self.nTableHeight = screen.getYResolution() - 100
		screen.setRenderInterfaceOnly(True)
		screen.addPanel( "MainBG", u"", u"", True, False, -10, -10, screen.getXResolution() + 20, screen.getYResolution() + 20, PanelStyles.PANEL_STYLE_MAIN )
		screen.setDimensions(0,0, screen.getXResolution(), screen.getYResolution())
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)

		screen.setText("WBTechExit", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 25, screen.getYResolution() - 40, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )
		screen.setText("TechHeader", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_TECH", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		szDropdownName = str("TechEra")
		screen.addDropDownBoxGFC(szDropdownName, 20, 20, 180, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_ALL", ()), 0, 0, True)
##		for i in xrange(gc.getNumEraInfos()):
		for i in xrange(3):#in FfH2, the other eras have no techs but are just dummies used for religion specific music and graphics
			screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_ERA",(gc.getEraInfo(i).getDescription(),)), i + 1, i + 1, i == self.iEra)

		szDropdownName = str("TechCommands")
		screen.addDropDownBoxGFC(szDropdownName, screen.getXResolution() - 200, 20, 180, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_COMMANDS", ()), 0, 0, True)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_GRANT_ALL", ()), 1, 1, False)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_CLEAR_ALL", ()), 2, 2, False)

		nColumns = 5
		screen.addTableControlGFC( "WBTech", nColumns, 20, 60, self.nTableWidth, self.nTableHeight, True, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		for i in xrange(nColumns):
			screen.setTableColumnHeader( "WBTech", i, "", self.nTableWidth/nColumns)

		self.iList = []
		for i in xrange(gc.getNumTechInfos()):
			ItemInfo = gc.getTechInfo(i)
			iEra = ItemInfo.getEra()
			if self.iEra == 1000 or self.iEra == iEra:
				self.iList.append([ItemInfo.getDescription(), i])
		self.iList.sort()

		nRows = (len(self.iList) + nColumns - 1) / nColumns
		for i in xrange(nRows):
			screen.appendTableRow("WBTech")

		for iCount in xrange(len(self.iList)):
			item = self.iList[iCount]
			iRow = iCount % nRows
			iColumn = iCount / nRows
			sItem = item[0]
			ItemInfo = gc.getTechInfo(item[1])
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			if ItemInfo.isRepeat():
				if pTeam.getTechCount(item[1]):
					sItem += " (" + str(pTeam.getTechCount(item[1])) +")"
					sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			elif pTeam.isHasTech(item[1]):
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			screen.setTableText("WBTech", iColumn, iRow, sColor + sItem + "</color>", ItemInfo.getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, item[1], 1, CvUtil.FONT_LEFT_JUSTIFY )

	def handleInput (self, inputClass):
		if inputClass.getFunctionName() == "TechEra":
			self.handlePlatyTechEraCB(inputClass.getData())
			return 1
		if inputClass.getFunctionName() == "TechCommands":
			self.handlePlatyTechCommandsCB(inputClass.getData())
			return 1
		if inputClass.getData1() > -1 and inputClass.getData2() == 1:
			self.handlePlatySetTechCB(inputClass.getData1())
			return 1
		return 1

	def handlePlatySetTechCB (self, iData1) :
		g_pTeam.setHasTech(iData1, not g_pTeam.isHasTech(iData1), g_pTeam.getLeaderID(), False, False)
		self.interfaceScreen(g_pTeam)
		return 1

	def handlePlatyTechEraCB (self, argsList) :
		self.iEra = int(argsList) - 1
		if int(argsList) == 0:
			self.iEra = 1000
		self.interfaceScreen(g_pTeam)
		return 1

	def handlePlatyTechCommandsCB(self, argsList):
		if int(argsList) == 1:
			for item in self.iList:
				ItemInfo = gc.getTechInfo(item[1])
				if ItemInfo.isRepeat(): continue
				g_pTeam.setHasTech(item[1], True, g_pTeam.getLeaderID(), False, False)
				self.interfaceScreen(g_pTeam)
		elif int(argsList) == 2:
			for item in self.iList:
				g_pTeam.setHasTech(item[1], False, g_pTeam.getLeaderID(), False, False)
				self.interfaceScreen(g_pTeam)
		return 1

	def update(self, fDelta):
		return 1