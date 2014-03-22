from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums
import WBProjectScreen
import WBTeamScreen
import WBPlayerScreen
import WBPlayerUnits
gc = CyGlobalContext()

class WBTechScreen:

	def __init__(self, main):
		self.top = main
		self.iEra = -1
		self.iTable_Y = 80

	def interfaceScreen(self, pTeamX):
		screen = CyGInterfaceScreen( "WBTechScreen", CvScreenEnums.WB_TECH)
		global pTeam
		pTeam = pTeamX

		screen.setRenderInterfaceOnly(True)
		screen.addPanel( "MainBG", u"", u"", True, False, -10, -10, screen.getXResolution() + 20, screen.getYResolution() + 20, PanelStyles.PANEL_STYLE_MAIN )
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)
	
		screen.setText("WBTechExit", "Background", "<font=4>" + CyTranslator().getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 30, screen.getYResolution() - 42, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )
		screen.setLabel("TechHeader", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_TECH", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		screen.addDropDownBoxGFC("CurrentTeam", 20, 20, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		for i in xrange(gc.getMAX_TEAMS()):
			if gc.getTeam(i).isAlive():
				iLeader = gc.getTeam(i).getLeaderID()
				sName = gc.getPlayer(iLeader).getName()
				if gc.getTeam(i).getNumMembers() > 1:
					sName += " + " + str(gc.getTeam(i).getNumMembers() -1) + " " + CyTranslator().getText("TXT_KEY_WB_MEMBERS", ())
				screen.addPullDownString("CurrentTeam", sName, i, i, i == pTeamX.getID())

		screen.addDropDownBoxGFC("CurrentPage", 20, screen.getYResolution() - 42, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_HELP4", ()), 0, 0, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_TEAM_DATA", ()), 1, 1, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_PROJECT", ()), 2, 2, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_TECH", ()), 3, 3, True)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_UNIT", ()) + " + " + CyTranslator().getText("TXT_KEY_CONCEPT_CITIES", ()), 4, 4, False)

		screen.addDropDownBoxGFC("TechEra", 20, self.iTable_Y - 30, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("TechEra", CyTranslator().getText("TXT_KEY_WB_CITY_ALL", ()), -1, -1, True)
		for i in xrange(gc.getNumEraInfos()):
			screen.addPullDownString("TechEra", CyTranslator().getText("TXT_KEY_WB_ERA",(gc.getEraInfo(i).getDescription(),)), i, i, i == self.iEra)

		screen.setButtonGFC("TechAllPlus", u"", "", screen.getXResolution() - 70, self.iTable_Y - 30, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("TechAllMinus", u"", "", screen.getXResolution() - 45, self.iTable_Y - 30, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		screen.setLabel("TechAll", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_WB_CITY_ALL", ()) + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 70, self.iTable_Y - 30, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		
		self.createTechList()
		self.placeTechs()

	def placeTechs(self):
		screen = CyGInterfaceScreen( "WBTechScreen", CvScreenEnums.WB_TECH)
		iMaxRows = (screen.getYResolution() - self.iTable_Y - 42) / 24
		nColumns = max(1, min(5, (len(lTech) + iMaxRows - 1)/iMaxRows))
		iWidth = screen.getXResolution() - 40
		iHeight = iMaxRows * 24 + 2
		screen.addTableControlGFC( "WBTech", nColumns, 20, self.iTable_Y, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		for i in xrange(nColumns):
			screen.setTableColumnHeader( "WBTech", i, "", iWidth/nColumns)
		
		nRows = (len(lTech) + nColumns - 1) / nColumns
		for i in xrange(nRows):
			screen.appendTableRow("WBTech")

		for iCount in xrange(len(lTech)):
			item = lTech[iCount]
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
			screen.setTableText("WBTech", iColumn, iRow, "<font=3>" + sColor + sItem + "</font></color>", ItemInfo.getButton(), WidgetTypes.WIDGET_PYTHON, 7871, item[1], CvUtil.FONT_LEFT_JUSTIFY )
				
	def handleInput(self, inputClass):
		screen = CyGInterfaceScreen( "WBTechScreen", CvScreenEnums.WB_TECH)
		if inputClass.getFunctionName() == "TechEra":
			self.iEra = inputClass.getData() - 1
			self.createTechList()
			self.placeTechs()

		elif inputClass.getFunctionName() == "CurrentTeam":
			iIndex = screen.getPullDownData("CurrentTeam", screen.getSelectedPullDownID("CurrentTeam"))
			self.interfaceScreen(gc.getTeam(iIndex))

		elif inputClass.getFunctionName() == "CurrentPage":
			iIndex = screen.getPullDownData("CurrentPage", screen.getSelectedPullDownID("CurrentPage"))
			if iIndex == 0:
				WBPlayerScreen.WBPlayerScreen(self.top).interfaceScreen(pTeam.getLeaderID())
			elif iIndex == 1:
				WBTeamScreen.WBTeamScreen(self.top).interfaceScreen(pTeam.getID())
			elif iIndex == 2:
				WBProjectScreen.WBProjectScreen(self.top).interfaceScreen(pTeam)
			elif iIndex == 4:
				WBPlayerUnits.WBPlayerUnits(self.top).interfaceScreen(pTeam.getLeaderID())

		elif inputClass.getFunctionName().find("TechAll") > -1:
			self.handlePlatyTechAll(inputClass.getData1()%2)
			self.placeTechs()

		elif inputClass.getFunctionName() == "WBTech":
			pTeam.setHasTech(inputClass.getData2(), not pTeam.isHasTech(inputClass.getData2()), pTeam.getLeaderID(), False, False)
			self.interfaceScreen(pTeam)
		return 1

	def createTechList(self):
		global lTech
		lTech = []
		for i in xrange(gc.getNumTechInfos()):
			ItemInfo = gc.getTechInfo(i)
			if self.iEra == -1 or self.iEra == ItemInfo.getEra():
				lTech.append([ItemInfo.getDescription(), i])
		lTech.sort()

	def handlePlatyTechAll(self, bEnable):
		for item in lTech:
			ItemInfo = gc.getTechInfo(item[1])
			if ItemInfo.isRepeat(): continue
			pTeam.setHasTech(item[1], not bEnable, pTeam.getLeaderID(), False, False)

	def update(self, fDelta):
		return 1