## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums

# globals
gc = CyGlobalContext()
g_pCity = None

class WBProjectScreen:

	def __init__(self):
		self.iList = []

	def interfaceScreen(self, pTeam):
		screen = CyGInterfaceScreen( "WBProjectScreen", CvScreenEnums.WB_PROJECT)
		global g_pTeam
		g_pTeam = pTeam

		self.nTableWidth = screen.getXResolution() - 40
		self.nTableHeight = screen.getYResolution() - 100
		screen.setRenderInterfaceOnly(True)
		screen.addPanel( "MainBG", u"", u"", True, False, -10, -10, screen.getXResolution() + 20, screen.getYResolution() + 20, PanelStyles.PANEL_STYLE_MAIN )
		screen.setDimensions(0,0, screen.getXResolution(), screen.getYResolution())
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)

		screen.addPanel( "ProjectBG", u"", u"", True, False, 0, 0, screen.getXResolution(), screen.getYResolution(), PanelStyles.PANEL_STYLE_MAIN )

		screen.setText("WBProjectExit", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 25, screen.getYResolution() - 40, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )

		screen.setText("ProjectHeader", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_PROJECT", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		szDropdownName = str("ProjectCommands")

		screen.addDropDownBoxGFC(szDropdownName, screen.getXResolution() - 200, 20, 180, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_COMMANDS", ()), 0, 0, True)
		for i in xrange(2):
			screen.addPullDownString(szDropdownName, "+" + CyTranslator().getText("TXT_KEY_WB_ADD_ALL",(10 ** i,)), i + 1, i + 1, False)
		for i in xrange(2):
			screen.addPullDownString(szDropdownName, "-" + CyTranslator().getText("TXT_KEY_WB_ADD_ALL",(10 ** i,)), i + 3, i + 3, False)


		nColumns = 3
		screen.addTableControlGFC( "WBProject", nColumns, 20, 60, self.nTableWidth, self.nTableHeight, True, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		for i in xrange(0, nColumns, 3):
			screen.setTableColumnHeader( "WBProject", i, "", self.nTableWidth - (38*2))
			screen.setTableColumnHeader( "WBProject", i + 1, "+1", 38)
			screen.setTableColumnHeader( "WBProject", i + 2, "-1", 38)



		self.iList = []
		for i in xrange(gc.getNumProjectInfos()):
			ItemInfo = gc.getProjectInfo(i)
			self.iList.append([ItemInfo.getDescription(), i])
		self.iList.sort()

		nPRows = len(self.iList)
		for i in xrange(nPRows):
			screen.appendTableRow("WBProject")
		for iCount in xrange(len(self.iList)):
			item = self.iList[iCount]
			iRow = iCount % nPRows
			iColumn = iCount / nPRows
			ItemInfo = gc.getProjectInfo(item[1])
			if pTeam.getProjectCount(item[1]):
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			else:
				sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			screen.setTableText("WBProject", iColumn, iRow, sColor + item[0] + "</color>", ItemInfo.getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROJECT, item[1], 1, CvUtil.FONT_LEFT_JUSTIFY )

		for iCount in xrange(len(self.iList2)):
			item = self.iList2[iCount]
			iRow = iCount % nSRows
			iColumn = iCount / nSRows
			sItem = item[0]
			ItemInfo = gc.getProjectInfo(item[1])
			if pTeam.getProjectCount(item[1]):
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
				sItem += " (" + str(pTeam.getProjectCount(item[1])) + ")"
			else:
				sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			screen.setTableText("WBSpaceship", iColumn * 3, iRow, sColor + sItem + "</color>", ItemInfo.getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROJECT, item[1], 2, CvUtil.FONT_LEFT_JUSTIFY )
			screen.setTableText("WBSpaceship", iColumn * 3 + 1, iRow, CyTranslator().getText("[COLOR_POSITIVE_TEXT]+1[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROJECT, item[1], 3, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBSpaceship", iColumn * 3 + 2, iRow, CyTranslator().getText("[COLOR_WARNING_TEXT]-1[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROJECT, item[1], 4, CvUtil.FONT_CENTER_JUSTIFY )

	def handleInput (self, inputClass):
		if inputClass.getFunctionName() == "ProjectCommands":
##			self.handlePlatyProjectCommandsCB(inputClass.getData())
##			return 1
##		if inputClass.getFunctionName() == "SpaceshipCommands":
			self.handlePlatySpaceshipCommandsCB(inputClass.getData())
			return 1
		if inputClass.getData1() > -1 and inputClass.getData2() == 1:
			self.handlePlatySetProjectCB(inputClass.getData1())
			return 1
		if inputClass.getData1() > -1 and inputClass.getData2() == 2:
			self.interfaceScreen(g_pTeam)
			return 1
		if inputClass.getData1() > -1 and inputClass.getData2() == 3:
			self.handlePlatyChangeProjectCountCB(inputClass.getData1(), 1)
			return 1
		if inputClass.getData1() > -1 and inputClass.getData2() == 4:
			self.handlePlatyChangeProjectCountCB(inputClass.getData1(), -1)
			return 1
		return 1

	def handlePlatySpaceshipCommandsCB (self, argsList) :
		iIndex = int(argsList) - 1
		if iIndex < 2:
			for item in self.iList:
				g_pTeam.changeProjectCount(item[1], 10 ** iIndex)
				info = gc.getProjectInfo(item[1])
				iMax = info.getMaxGlobalInstances()
				if iMax > -1:
					iDiff = gc.getGame().getProjectCreatedCount(item[1]) - iMax
					if iDiff > 0:
						g_pTeam.changeProjectCount(item[1], - iDiff)
				iMax = info.getMaxTeamInstances()
				if iMax > -1:
					iDiff = g_pTeam.getProjectCount(item[1]) - iMax
					if iDiff > 0:
						g_pTeam.changeProjectCount(item[1], - iDiff)
		else:
			iIndex -= 2
			for item in self.iList2:
				g_pTeam.changeProjectCount(item[1], -10 ** iIndex)
				if g_pTeam.getProjectCount(item[1]) < 0:
					g_pTeam.changeProjectCount(item[1], - g_pTeam.getProjectCount(item[1]))
		self.interfaceScreen(g_pTeam)
		return 1

	def handlePlatyChangeProjectCountCB (self, iData1, iCount) :
		g_pTeam.changeProjectCount(iData1, iCount)
		if g_pTeam.getProjectCount(iData1) < 0:
			g_pTeam.changeProjectCount(iData1, - g_pTeam.getProjectCount(iData1))
		info = gc.getProjectInfo(iData1)
		iMax = info.getMaxGlobalInstances()
		if iMax > -1:
			iDiff = gc.getGame().getProjectCreatedCount(iData1) - iMax
			if iDiff > 0:
				g_pTeam.changeProjectCount(iData1, - iDiff)
		iMax = info.getMaxTeamInstances()
		if iMax > -1:
			iDiff = g_pTeam.getProjectCount(iData1) - iMax
			if iDiff > 0:
				g_pTeam.changeProjectCount(iData1, - iDiff)

		self.interfaceScreen(g_pTeam)
		return 1

	def handlePlatySetProjectCB (self, iData1) :
		if g_pTeam.getProjectCount(iData1):
			g_pTeam.changeProjectCount(iData1, -1)
		else:
			g_pTeam.changeProjectCount(iData1, 1)
		if gc.getProjectInfo(iData1).isAllowsNukes() and CyGame().getProjectCreatedCount(iData1) == 0:
			CyGame().makeNukesValid(False)
		self.interfaceScreen(g_pTeam)
		return 1

	def handlePlatyProjectCommandsCB(self, argsList):
		if int(argsList) == 1:
			for item in self.iList:
				if g_pTeam.getProjectCount(item[1]): continue
				g_pTeam.changeProjectCount(item[1], 1)
				self.interfaceScreen(g_pTeam)
		elif int(argsList) == 2:
			for item in self.iList:
				g_pTeam.changeProjectCount(item[1], - g_pTeam.getProjectCount(item[1]))
				self.interfaceScreen(g_pTeam)
				if gc.getProjectInfo(item[1]).isAllowsNukes() and CyGame().getProjectCreatedCount(item[1]) == 0:
					CyGame().makeNukesValid(False)
		return 1

	def update(self, fDelta):
		return 1