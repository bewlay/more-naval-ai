from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums
import WBTeamScreen
import WBTechScreen
import WBPlayerScreen
import WBPlayerUnits
gc = CyGlobalContext()
iCurrentProject = 0
iChange = 1

class WBProjectScreen:

	def __init__(self, main):
		self.top = main
		self.iTable_Y = 80
		self.iProjectType = 0

	def interfaceScreen(self, pTeamX):
		screen = CyGInterfaceScreen( "WBProjectScreen", CvScreenEnums.WB_PROJECT)
		global pTeam
		pTeam = pTeamX

		screen.setRenderInterfaceOnly(True)
		screen.addPanel( "MainBG", u"", u"", True, False, -10, -10, screen.getXResolution() + 20, screen.getYResolution() + 20, PanelStyles.PANEL_STYLE_MAIN )
		screen.setDimensions(0,0, screen.getXResolution(), screen.getYResolution())
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)
	
		screen.setText("WBProjectExit", "Background", "<font=4>" + CyTranslator().getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 30, screen.getYResolution() - 42, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )
		screen.setLabel("ProjectHeader", "Background", "<font=4b>" + CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_PROJECT", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		screen.addDropDownBoxGFC("CurrentTeam", 20, 20, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		for i in xrange(gc.getMAX_TEAMS()):
			if gc.getTeam(i).isAlive():
				iLeader = gc.getTeam(i).getLeaderID()
				sName = gc.getPlayer(iLeader).getName()
				if gc.getTeam(i).getNumMembers() > 1:
					sName += " + " + str(gc.getTeam(i).getNumMembers() -1) + " " + CyTranslator().getText("TXT_KEY_WB_MEMBERS", ())
				screen.addPullDownString("CurrentTeam", sName, i, i, i == pTeamX.getID())

		screen.addDropDownBoxGFC("ChangeBy", screen.getXResolution() *4/5 - 20, 20, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		i = 1
		while i < 101:
			screen.addPullDownString("ChangeBy", CyTranslator().getText("TXT_KEY_WB_CHANGE_BY",(i,)), i, i, iChange == i)
			if str(i)[0] == "1":
				i *= 5
			else:
				i *= 2

		screen.addDropDownBoxGFC("ProjectType", 20, self.iTable_Y - 30, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("ProjectType", CyTranslator().getText("TXT_KEY_WB_CITY_ALL", ()), 0, 0, self.iProjectType == 0)
		screen.addPullDownString("ProjectType", CyTranslator().getText("TXT_KEY_PEDIA_TEAM_PROJECT", ()), 1, 1, self.iProjectType == 1)
		screen.addPullDownString("ProjectType", CyTranslator().getText("TXT_KEY_PEDIA_WORLD_PROJECT", ()), 2, 2, self.iProjectType == 2)

		screen.addDropDownBoxGFC("CurrentPage", 20, screen.getYResolution() - 42, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_HELP4", ()), 0, 0, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_TEAM_DATA", ()), 1, 1, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_PROJECT", ()), 2, 2, True)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_TECH", ()), 3, 3, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_UNIT", ()) + " + " + CyTranslator().getText("TXT_KEY_CONCEPT_CITIES", ()), 4, 4, False)

		sText = CyTranslator().getText("TXT_KEY_WB_CITY_ALL", ())
		screen.setLabel("ProjectAll", "Background", u"<font=4b>" + sText + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 70, self.iTable_Y - 30, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setButtonGFC("ProjectAllPlus", u"", "", screen.getXResolution() - 70, self.iTable_Y - 30, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("ProjectAllMinus", u"", "", screen.getXResolution() - 45, self.iTable_Y - 30, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		self.sortProjects()

	def sortProjects(self):
		screen = CyGInterfaceScreen( "WBProjectScreen", CvScreenEnums.WB_PROJECT)
		global iCurrentProject
		global lProject
		lProject = []
		for i in xrange(gc.getNumProjectInfos()):
			Info = gc.getProjectInfo(i)
			if self.iProjectType == 1 and not isTeamProject(i): continue
			if self.iProjectType == 2 and not isWorldProject(i): continue
			iTeam = Info.getMaxTeamInstances()
			iWorld = Info.getMaxGlobalInstances()
			iMax = max(iTeam, iWorld)
			if iTeam > -1 and iWorld > -1:
				iMax = min(iTeam, iWorld)
			lProject.append([Info.getDescription(), i, iMax])
		lProject.sort()
		if len(lProject) > 0:
			iCurrentProject = lProject[0][1]
		self.placeProjects()

	def placeProjects(self):
		screen = CyGInterfaceScreen( "WBProjectScreen", CvScreenEnums.WB_PROJECT)
		iMaxRows = (screen.getYResolution() - self.iTable_Y - 42) / 24
		nColumns = max(1, min(5, (len(lProject) + iMaxRows - 1)/iMaxRows))
		iWidth = screen.getXResolution() - 40
		iHeight = iMaxRows * 24 + 2
		screen.hide("CurrentProjectPlus")
		screen.hide("CurrentProjectMinus")
		screen.hide("CurrentProjectText")

		screen.addTableControlGFC("WBProject", nColumns, 20, self.iTable_Y, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		for i in xrange(nColumns):
			screen.setTableColumnHeader("WBProject", i, "", iWidth/nColumns)
		nRows = (len(lProject) + nColumns - 1) / nColumns
		for i in xrange(nRows):
			screen.appendTableRow("WBProject")

		for iCount in xrange(len(lProject)):
			item = lProject[iCount]
			iRow = iCount % nRows
			iColumn = iCount / nRows
			Info = gc.getProjectInfo(item[1])
			iCount = pTeam.getProjectCount(item[1])
			sText = item[0]
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			if item[2] > 1:
				sText = u"%s (%d/%d)" %(sText, iCount, item[2])
				if iCount < item[2]:
					sColor = CyTranslator().getText("[COLOR_YELLOW]", ())
			elif item[2] == -1:
				if iCount > 0:
					sText = u"%s (%d)" %(sText, iCount)
			if iCount == 0:
				sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			if item[1] == iCurrentProject:
				screen.setButtonGFC("CurrentProjectPlus", u"", "", screen.getXResolution() /5 + 25, self.iTable_Y - 30, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
				screen.setButtonGFC("CurrentProjectMinus", u"", "", screen.getXResolution() /5 + 50, self.iTable_Y - 30, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
				screen.setLabel("CurrentProjectText", "Background", "<font=3>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, screen.getXResolution() /5 + 75, self.iTable_Y - 30, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			screen.setTableText("WBProject", iColumn, iRow, "<font=3>" + sColor + sText + "</font></color>", Info.getButton(), WidgetTypes.WIDGET_PYTHON, 6785, item[1], CvUtil.FONT_LEFT_JUSTIFY )

	def handleInput (self, inputClass):
		screen = CyGInterfaceScreen( "WBProjectScreen", CvScreenEnums.WB_PROJECT)
		global iCurrentProject
		global iChange

		if inputClass.getFunctionName() == "ChangeBy":
			iIndex = screen.getSelectedPullDownID("ChangeBy")
			iChange = screen.getPullDownData("ChangeBy", iIndex)

		elif inputClass.getFunctionName() == "CurrentTeam":
			iIndex = screen.getPullDownData("CurrentTeam", screen.getSelectedPullDownID("CurrentTeam"))
			self.interfaceScreen(gc.getTeam(iIndex))

		elif inputClass.getFunctionName() == "ProjectType":
			self.iProjectType = screen.getPullDownData("ProjectType", screen.getSelectedPullDownID("ProjectType"))
			self.sortProjects()

		elif inputClass.getFunctionName() == "CurrentPage":
			iIndex = screen.getPullDownData("CurrentPage", screen.getSelectedPullDownID("CurrentPage"))
			if iIndex == 0:
				WBPlayerScreen.WBPlayerScreen(self.top).interfaceScreen(pTeam.getLeaderID())
			elif iIndex == 1:
				WBTeamScreen.WBTeamScreen(self.top).interfaceScreen(pTeam.getID())
			elif iIndex == 3:
				WBTechScreen.WBTechScreen(self.top).interfaceScreen(pTeam)
			elif iIndex == 4:
				WBPlayerUnits.WBPlayerUnits(self.top).interfaceScreen(pTeam.getLeaderID())

		elif inputClass.getFunctionName().find("ProjectAll") > -1:
			self.handlePlatyProjectAll(inputClass.getData1())
			self.placeProjects()

		elif inputClass.getFunctionName() == "WBProject":
			iCurrentProject = inputClass.getData2()
			self.placeProjects()

		elif inputClass.getFunctionName() == "CurrentProjectPlus":
			self.handlePlatyProjectCount(iCurrentProject, iChange)
			self.placeProjects()

		elif inputClass.getFunctionName() == "CurrentProjectMinus":
			self.handlePlatyProjectCount(iCurrentProject, - iChange)
			self.placeProjects()
		return 1

	def handlePlatyProjectAll(self, iData1):
		for item in lProject:
			if iData1 % 2:
				self.handlePlatyProjectCount(item[1], - iChange)
			else:
				self.handlePlatyProjectCount(item[1], iChange)

	def handlePlatyProjectCount(self, iData1, iCount):
		if iCount < 0:
			iCount = max(iCount, - pTeam.getProjectCount(iData1))
		else:
			Info = gc.getProjectInfo(iData1)
			iTeam = Info.getMaxTeamInstances()
			iWorld = Info.getMaxGlobalInstances()
			iMax = max(iTeam, iWorld)
			if iTeam > -1 and iWorld > -1:
				iMax = min(iTeam, iWorld)
			if iMax > -1:
				iCount = min(iCount, iMax - pTeam.getProjectCount(iData1))
		pTeam.changeProjectCount(iData1, iCount)
		if gc.getProjectInfo(iData1).isAllowsNukes() and CyGame().getProjectCreatedCount(iData1) == 0:
			CyGame().makeNukesValid(False)

	def update(self, fDelta):
		return 1