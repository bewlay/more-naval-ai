from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums
import WBEventScreen
import WBPlayerUnits
import WBCityEditScreen
import WBUnitScreen
import WBPlayerScreen
import WBTeamScreen
import WBInfoScreen
import CvPlatyBuilderScreen
import Popup
gc = CyGlobalContext()

bAdd = True
bSensibility = True
iEditType = 0
iChange = 1
iCounter = -1
iCulturePlayer = 0
iSelectedClass = -1

bReal = False#Magister

class WBPlotScreen:

	def __init__(self):
		self.iTable_Y = 110

	def interfaceScreen(self, pPlotX):
		screen = CyGInterfaceScreen( "WBPlotScreen", CvScreenEnums.WB_PLOT)
		global pPlot
		global iWidth
		pPlot = pPlotX
		iWidth = screen.getXResolution()/5 - 20

		screen.setRenderInterfaceOnly(True)
		screen.addPanel( "MainBG", u"", u"", True, False, -10, -10, screen.getXResolution() + 20, screen.getYResolution() + 20, PanelStyles.PANEL_STYLE_MAIN )
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)

		screen.setText("PlotExit", "Background", "<font=4>" + CyTranslator().getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 30, screen.getYResolution() - 42, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )

		iX = 10
		iY = 50
		screen.addDropDownBoxGFC("CurrentPlayer", iX, iY, iWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("CurrentPlayer", CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ()), -1, -1, pPlot.getOwner() == -1)
		for i in xrange(gc.getMAX_PLAYERS()):
			pPlayerX = gc.getPlayer(i)
			if pPlayerX.isAlive():
				screen.addPullDownString("CurrentPlayer", pPlayerX.getName(), i, i, i == pPlot.getOwner())

		iY += 30
		screen.addDropDownBoxGFC("ChangeType", iX, iY, iWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("ChangeType", CyTranslator().getText("TXT_KEY_WB_CITY_ADD", ()), 1, 1, bAdd)
		screen.addPullDownString("ChangeType", CyTranslator().getText("TXT_KEY_WB_CITY_REMOVE", ()), 0, 0, not bAdd)

		iY += 30
		iButtonWidth = 28
		screen.addCheckBoxGFC("SensibilityCheck", ",Art/Interface/Buttons/WorldBuilder/Gems.dds,Art/Interface/Buttons/FinalFrontier1_Atlas.dds,1,16", CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
					 iX, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_PYTHON, 1029, 24, ButtonStyles.BUTTON_STYLE_LABEL)
		screen.setState("SensibilityCheck", bSensibility)

#Magister Start
		screen.addCheckBoxGFC("RealType", ",Art/Interface/Buttons/WorldBuilder/Metamagic.dds,Art/Interface/Buttons/FinalFrontier1_Atlas.dds,1,16", CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
					 iX+iButtonWidth, iY, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_PYTHON, 1029, 35, ButtonStyles.BUTTON_STYLE_LABEL)
		screen.setState("RealType", bReal)

		screen.addDropDownBoxGFC("EditType", iX + 2*iButtonWidth, iY, iWidth - 2*iButtonWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)#magister
##		screen.addDropDownBoxGFC("EditType", iX + iButtonWidth, iY, iWidth - iButtonWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
#Magister Stop
		screen.addPullDownString("EditType", CyTranslator().getText("TXT_KEY_WB_SINGLE_PLOT", ()), 0, 0, iEditType == 0)
		screen.addPullDownString("EditType", CyTranslator().getText("TXT_KEY_WB_AREA_PLOTS", ()), 1, 1, iEditType == 1)
		screen.addPullDownString("EditType", CyTranslator().getText("TXT_KEY_WB_ALL_PLOTS", ()), 2, 2, iEditType == 2)

		iY += 30
		screen.addDropDownBoxGFC("ChangeBy", iX, iY, iWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		i = 1
		while i < 1000001:
			screen.addPullDownString("ChangeBy", "(+/-) " + str(i), i, i, iChange == i)
			if str(i)[0] == "1":
				i *= 5
			else:
				i *= 2

		screen.addDropDownBoxGFC("CurrentPage", iX, screen.getYResolution() - 42, iWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_PLOT_DATA", ()), 0, 0, True)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_CONCEPT_EVENTS", ()), 1, 1, False)
		if pPlot.isOwned():
			screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_PLAYER_DATA", ()), 2, 2, False)
			screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_TEAM_DATA", ()), 3, 3, False)
			screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_UNIT", ()) + " + " + CyTranslator().getText("TXT_KEY_CONCEPT_CITIES", ()), 6, 6, False)
			if pPlot.isCity():
				screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_CITY_DATA", ()), 4, 4, False)
		if pPlot.getNumUnits() > 0:
			screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_UNIT_DATA", ()), 5, 5, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_INFO_SCREEN", ()), 11, 11, False)

		iIndex = -1
		for i in xrange(CyMap().numPlots()):
			pLoopPlot = CyMap().plotByIndex(i)
			if pLoopPlot.getX() == pPlot.getX() and pLoopPlot.getY() == pPlot.getY():
				iIndex = i
				break
		sText = CyTranslator().getText("TXT_KEY_WB_PLOT_DATA", ())
		if pPlot.isCity():
			pCity = pPlot.getPlotCity()
			sText += " (" + pCity.getName() + ")"
		screen.setLabel("PlotScreenHeader", "Background", "<font=4b>" + sText + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 20, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		sText = u"<font=3b>%s ID: %d, %s: %d</font>" %(CyTranslator().getText("TXT_KEY_WB_PLOT", ()), iIndex, CyTranslator().getText("TXT_KEY_WB_AREA_ID", ()), pPlot.getArea())
		screen.setLabel("PlotScreenHeaderB", "Background", "<font=4b>" + sText + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 50, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		sText = "<font=3b>%s, X: %d, Y: %d</font>" %(CyTranslator().getText("TXT_KEY_WB_LATITUDE",(pPlot.getLatitude(),)), pPlot.getX(), pPlot.getY())
		screen.setLabel("PlotLocation", "Background", sText, CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 70, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		screen.addDropDownBoxGFC("BonusClass", screen.getXResolution() *4/5 + 10, self.iTable_Y - 60, iWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("BonusClass", CyTranslator().getText("TXT_KEY_WB_CITY_ALL",()), -1, -1, True)
		screen.addPullDownString("BonusClass", CyTranslator().getText("TXT_KEY_GLOBELAYER_RESOURCES_GENERAL",()), 0, 0, 0 == iSelectedClass)
		iBonusClass = 1
		while not gc.getBonusClassInfo(iBonusClass) is None:
			sText = gc.getBonusClassInfo(iBonusClass).getType()
			sText = sText[sText.find("_") +1:]
			sText = sText.lower()
			sText = sText.capitalize()
			screen.addPullDownString("BonusClass", sText, iBonusClass, iBonusClass, iBonusClass == iSelectedClass)
			iBonusClass += 1

		screen.setImageButton("NextPlotUpButton", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_GENERAL_UPARROW").getPath(),
				screen.getXResolution()/2 - 12, self.iTable_Y, 24, 24, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setImageButton("NextPlotDownButton", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_GENERAL_DOWNARROW").getPath(),
				screen.getXResolution()/2 - 12, self.iTable_Y + 48, 24, 24, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setImageButton("NextPlotLeftButton", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_LEFT").getPath(),
				screen.getXResolution()/2 - 36, self.iTable_Y + 24, 24, 24, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setImageButton("NextPlotRightButton", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_RIGHT").getPath(),
				screen.getXResolution()/2 + 12, self.iTable_Y + 24, 24, 24, WidgetTypes.WIDGET_GENERAL, -1, -1)

		global lRoutes
		global lFeatures
		global lImprovements

		lFeatures = []
		for i in xrange(gc.getNumFeatureInfos()):
			ItemInfo = gc.getFeatureInfo(i)
			for j in xrange(ItemInfo.getNumVarieties()):
				sText = ItemInfo.getDescription()
				if ItemInfo.getNumVarieties() > 1:
					sText += " (" + str(j) + ")"
				lFeatures.append([sText, j * 10000 + i])
		lFeatures.sort()

		lRoutes = []
		for i in xrange(gc.getNumRouteInfos()):
			ItemInfo = gc.getRouteInfo(i)
			lRoutes.append([ItemInfo.getDescription(), i])
		lRoutes.sort()

		lImprovements = []
		for i in xrange(gc.getNumImprovementInfos()):
			ItemInfo = gc.getImprovementInfo(i)
			if ItemInfo.isGraphicalOnly(): continue
			lImprovements.append([ItemInfo.getDescription(), i])
		lImprovements.sort()

		self.createBonusList()
		self.placeScript()
		self.placeStats()
		self.placePlotType()
		self.placeTerrain()
		self.placeFeature()
		self.placeRoutes()
		self.placeImprovements()

	def placeSigns(self):
		screen = CyGInterfaceScreen("WBPlotScreen", CvScreenEnums.WB_PLOT)
		iX = 10
		iY = screen.getYResolution()/2
		iSignWidth = screen.getXResolution() * 2/5 - 20
		iHeight = (screen.getYResolution() - 42 - iY) /24 * 24 + 2

		screen.setButtonGFC("EditCulturePlus", "", "", 10, iY - 30, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("EditCultureMinus", "", "", 35, iY - 30, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = CyTranslator().getText("[ICON_CULTURE]", ()) + gc.getPlayer(iCulturePlayer).getName()
		screen.setLabel("PlotCultureText", "Background", "<font=3>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, 65, iY - 30, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		sText = CyTranslator().getText("[COLOR_SELECTED_TEXT]", ()) + "<font=3b>" + CyTranslator().getText("TXT_KEY_WB_LANDMARKS", ()) + "</color></font>"
		screen.setText("EditLandMark", "Background", sText, CvUtil.FONT_RIGHT_JUSTIFY, iX + iSignWidth, iY - 30, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		lSigns = []
		for iPlayerX in xrange(gc.getMAX_PLAYERS()):
			lSigns.append(-1)
		for i in xrange(CyEngine().getNumSigns()):
			pSign = CyEngine().getSignByIndex(i)
			if pSign.getPlot().getX() != pPlot.getX(): continue
			if pSign.getPlot().getY() != pPlot.getY(): continue
			lSigns[pSign.getPlayerType()] = i

		screen.addTableControlGFC("WBSigns", 4, iX, iY, iSignWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		screen.setTableColumnHeader("WBSigns", 0, "", 24)
		screen.setTableColumnHeader("WBSigns", 1, "", 24)
		screen.setTableColumnHeader("WBSigns", 2, "", (iSignWidth - 48) /3)
		screen.setTableColumnHeader("WBSigns", 3, "", (iSignWidth - 48) *2/3)

		for iPlayerX in xrange(gc.getMAX_PLAYERS()):
			pPlayerX = gc.getPlayer(iPlayerX)
			if pPlayerX.isEverAlive():
				iRow = screen.appendTableRow("WBSigns")
				iCivilization = pPlayerX.getCivilizationType()
				iLeader = pPlayerX.getLeaderType()
				screen.setTableText("WBSigns", 0, iRow, "", gc.getCivilizationInfo(iCivilization).getButton(), WidgetTypes.WIDGET_PYTHON, 7872, iPlayerX * 10000 + iCivilization, CvUtil.FONT_LEFT_JUSTIFY )
				screen.setTableText("WBSigns", 1, iRow, "", gc.getLeaderHeadInfo(iLeader).getButton(), WidgetTypes.WIDGET_PYTHON, 7876, iPlayerX * 10000 + iLeader, CvUtil.FONT_LEFT_JUSTIFY )
				sText = "<font=3>" + CvPlatyBuilderScreen.CvWorldBuilderScreen().addComma(pPlot.getCulture(iPlayerX)) + CyTranslator().getText("[ICON_CULTURE]", ()) + "</font>"
				screen.setTableText("WBSigns", 2, iRow, sText, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY)
				iIndex = lSigns[iPlayerX]
				sText = ""
				if iIndex > -1:
					sText = CyEngine().getSignByIndex(iIndex).getCaption()
				screen.setTableText("WBSigns", 3, iRow, "<font=3>" + sText + "</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

	def placeMap(self):
		screen = CyGInterfaceScreen("WBPlotScreen", CvScreenEnums.WB_PLOT)
		iMapHeight = min((screen.getYResolution()/2 - 30 - (self.iTable_Y + 48 + 24)), iWidth * 2/3)
		iMapWidth = iMapHeight * 3/2
		screen.addPlotGraphicGFC("PlotView", screen.getXResolution()/2 - iMapWidth/2, screen.getYResolution()/2 - 30 - iMapHeight, iMapWidth, iMapHeight, pPlot, 350, False, WidgetTypes.WIDGET_GENERAL, -1, -1)

	def placeStats(self):
		screen = CyGInterfaceScreen("WBPlotScreen", CvScreenEnums.WB_PLOT)
		iY = 180
		screen.setLabel("YieldHeader", "Background", "<font=3b>" + CyTranslator().getText("TXT_KEY_PEDIA_YIELDS", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/10, iY, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		iY += 30
		for i in xrange(YieldTypes.NUM_YIELD_TYPES):
			iX = 10
			iYield = pPlot.getYield(YieldTypes(i))
			iImprovement = pPlot.getImprovementType()
			if iImprovement > -1:
				iYield -= pPlot.calculateImprovementYieldChange(iImprovement, YieldTypes(i), pPlot.getOwner(), False)
			screen.setButtonGFC("BaseYieldPlus" + str(i), "", "", iX, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, i, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
			screen.setButtonGFC("BaseYieldMinus" + str(i), "", "", iX + 25, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, i, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
			sText = CyTranslator().getText("TXT_KEY_WB_BASE_YIELD", (gc.getYieldInfo(i).getDescription(), iYield,))
			sText = u"%s%c" %(sText, gc.getYieldInfo(i).getChar())
			screen.setLabel("BaseYieldText" + str(i), "Background", "<font=3>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iX + 50, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			iY += 30

#Magister Start
		iY = 50
		iX = screen.getXResolution()* 3/10
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if pPlot.isMoveDisabledAI():
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		sText = CyTranslator().getText("TXT_KEY_WB_MOVE_DISABLED_AI", ())
		screen.setText("MoveDisabledAIText", "Background", "<font=3>" + sColor + sText + "</color></font>", CvUtil.FONT_CENTER_JUSTIFY, iX, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		iY += 25
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if pPlot.isMoveDisabledHuman():
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		sText = CyTranslator().getText("TXT_KEY_WB_MOVE_DISABLED_HUMAN", ())
		screen.setText("MoveDisabledHumanText", "Background", "<font=3>" + sColor + sText + "</color></font>", CvUtil.FONT_CENTER_JUSTIFY, iX, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		iY += 25
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if pPlot.isBuildDisabled():
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		sText = CyTranslator().getText("TXT_KEY_WB_BUILD_DISABLED", ())
		screen.setText("BuildDisabledText", "Background", "<font=3>" + sColor + sText + "</color></font>", CvUtil.FONT_CENTER_JUSTIFY, iX , iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		iY += 25
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if pPlot.isFoundDisabled():
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		sText = CyTranslator().getText("TXT_KEY_WB_FOUND_DISABLED", ())
		screen.setText("FoundDisabledText", "Background", "<font=3>" + sColor + sText + "</color></font>", CvUtil.FONT_CENTER_JUSTIFY, iX , iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		iY += 25
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if not pPlot.isPythonActive():
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		sText = CyTranslator().getText("TXT_KEY_WB_PYTHON_INACTIVE", ())
		screen.setText("PythonActiveText", "Background", "<font=3>" + sColor + sText + "</color></font>", CvUtil.FONT_CENTER_JUSTIFY, iX , iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY = 210
		iX = screen.getXResolution() / 5
		screen.setButtonGFC("MinLevelPlus", "", "", iX , iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("MinLevelMinus", "", "", iX + 25, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = CyTranslator().getText("TXT_KEY_WB_PLOT_MIN_LEVEL", ()) + " " + str(pPlot.getMinLevel())
		screen.setLabel("MinLevelText", "Background", "<font=3>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iX + 55, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		iY += 30
		screen.setButtonGFC("PlotCounterPlus", "", "", iX , iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("PlotCounterMinus", "", "", iX + 25, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = CyTranslator().getText("TXT_KEY_WB_PLOT_COUNTER", ()) + " " + str(pPlot.getPlotCounter())
		screen.setLabel("PlotCounterText", "Background", "<font=3>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iX + 55, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		iY += 30
		screen.setButtonGFC("PortalExitXPlus", "", "", iX , iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("PortalExitXMinus", "", "", iX + 25, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = CyTranslator().getText("TXT_KEY_WB_PORTAL_X_COORDINATE", ()) + " " + str(pPlot.getPortalExitX())
		screen.setLabel("PortalExitXText", "Background", "<font=3>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iX + 55, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		iY += 30
		screen.setButtonGFC("PortalExitYPlus", "", "", iX, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("PortalExitYMinus", "", "", iX + 25, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = CyTranslator().getText("TXT_KEY_WB_PORTAL_Y_COORDINATE", ()) + " " + str(pPlot.getPortalExitY())
		screen.setLabel("PortalExitYText", "Background", "<font=3>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iX + 55, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
#Magister Stop

		self.placeSigns()
		self.placeRivers()

	def placeRivers(self):
		screen = CyGInterfaceScreen( "WBPlotScreen", CvScreenEnums.WB_PLOT)
		iX = screen.getXResolution()/2
		iY = screen.getYResolution()/2
		screen.setLabel("PlotRiverHeader", "Background", "<font=3b>" + CyTranslator().getText("TXT_KEY_MISC_RIVERS", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, iX, iY - 30, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		pWestPlot = CyMap().plot(pPlot.getX() - 1, pPlot.getY())
		pNorthPlot = CyMap().plot(pPlot.getX(), pPlot.getY() + 1)
		if not pNorthPlot.isNone():
			screen.addCheckBoxGFC("RiverNorthAButton", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_LEFT").getPath(), CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
				iX - 36, iY, 24, 24, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)
			screen.addCheckBoxGFC("RiverNorthBButton", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_CANCEL").getPath(), CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
				iX - 12, iY, 24, 24, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)
			screen.addCheckBoxGFC("RiverNorthCButton", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_RIGHT").getPath(), CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
				iX + 12, iY, 24, 24, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)
			screen.setState("RiverNorthAButton", pNorthPlot.getRiverWEDirection() == CardinalDirectionTypes.CARDINALDIRECTION_WEST)
			screen.setState("RiverNorthBButton", pNorthPlot.getRiverWEDirection() == CardinalDirectionTypes.NO_CARDINALDIRECTION)
			screen.setState("RiverNorthCButton", pNorthPlot.getRiverWEDirection() == CardinalDirectionTypes.CARDINALDIRECTION_EAST)

		iY += 24
		if not pWestPlot.isNone():
			screen.addCheckBoxGFC("RiverWestAButton", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_GENERAL_UPARROW").getPath(), CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
				iX - 60, iY, 24, 24, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)
		screen.addCheckBoxGFC("RiverEastAButton", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_GENERAL_UPARROW").getPath(), CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
				iX + 36, iY, 24, 24, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)
		iY += 24
		if not pWestPlot.isNone():
			screen.addCheckBoxGFC("RiverWestBButton", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_CANCEL").getPath(), CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
				iX - 60, iY, 24, 24, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)
		screen.addCheckBoxGFC("RiverEastBButton", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_CANCEL").getPath(), CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
				iX + 36, iY, 24, 24, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)
		iY += 24
		if not pWestPlot.isNone():
			screen.addCheckBoxGFC("RiverWestCButton", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_GENERAL_DOWNARROW").getPath(), CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
				iX - 60, iY, 24, 24, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)
		screen.addCheckBoxGFC("RiverEastCButton", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_GENERAL_DOWNARROW").getPath(), CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
				iX + 36, iY, 24, 24, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)
		if not pWestPlot.isNone():
			screen.setState("RiverWestAButton", pWestPlot.getRiverNSDirection() == CardinalDirectionTypes.CARDINALDIRECTION_NORTH)
			screen.setState("RiverWestBButton", pWestPlot.getRiverNSDirection() == CardinalDirectionTypes.NO_CARDINALDIRECTION)
			screen.setState("RiverWestCButton", pWestPlot.getRiverNSDirection() == CardinalDirectionTypes.CARDINALDIRECTION_SOUTH)

		screen.setState("RiverEastAButton", pPlot.getRiverNSDirection() == CardinalDirectionTypes.CARDINALDIRECTION_NORTH)
		screen.setState("RiverEastBButton", pPlot.getRiverNSDirection() == CardinalDirectionTypes.NO_CARDINALDIRECTION)
		screen.setState("RiverEastCButton", pPlot.getRiverNSDirection() == CardinalDirectionTypes.CARDINALDIRECTION_SOUTH)

		iY += 24
		screen.addCheckBoxGFC("RiverSouthAButton", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_LEFT").getPath(), CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
				iX - 36, iY, 24, 24, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)
		screen.addCheckBoxGFC("RiverSouthBButton", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_CANCEL").getPath(), CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
				iX - 12, iY, 24, 24, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)
		screen.addCheckBoxGFC("RiverSouthCButton", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_RIGHT").getPath(), CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
				iX + 12, iY, 24, 24, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)
		screen.setState("RiverSouthAButton", pPlot.getRiverWEDirection() == CardinalDirectionTypes.CARDINALDIRECTION_WEST)
		screen.setState("RiverSouthBButton", pPlot.getRiverWEDirection() == CardinalDirectionTypes.NO_CARDINALDIRECTION)
		screen.setState("RiverSouthCButton", pPlot.getRiverWEDirection() == CardinalDirectionTypes.CARDINALDIRECTION_EAST)
		global iPlotType_Y
		iPlotType_Y = iY + 30

	def placeRoutes(self):
		screen = CyGInterfaceScreen( "WBPlotScreen", CvScreenEnums.WB_PLOT)
		iX = screen.getXResolution() *3/5 + 10#Magister		iX = screen.getXResolution() *4/5 + 10
		iY = screen.getYResolution()/2
		iHeight = 3 * 24 + 2#Magister		iHeight = (screen.getYResolution() - 42 - iY) /24 * 24 + 2
		iRoute = pPlot.getRouteType()
#Magister Start
		if bReal:
			iRoute = pPlot.getRealRouteType()
			iY2 = iY + iHeight
			screen.setButtonGFC("RouteTempTimerPlus", "", "", iX, iY2, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
			screen.setButtonGFC("RouteTempTimerMinus", "", "", iX + 25, iY2, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
			sText = CyTranslator().getText("TXT_KEY_WB_TEMP_TIMER", (pPlot.getTempRouteTimer(),))
			screen.setLabel("RouteTempTimerText", "Background", "<font=3>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iX + 50, iY2, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		else:
			screen.hide("RouteTempTimerPlus")
			screen.hide("RouteTempTimerMinus")
			screen.hide("RouteTempTimerText")
#Magister Stop

		sText = CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ())
		sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		if iRoute > -1:
			sText = gc.getRouteInfo(iRoute).getDescription()
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		screen.setLabel("RouteHeader", "Background", "<font=3b>" + sText + "</font>", CvUtil.FONT_CENTER_JUSTIFY, iX + screen.getXResolution()/10 - 10, iY - 30, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addTableControlGFC("WBPlotRoutes", 1, iX, iY, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		screen.setTableColumnHeader("WBPlotRoutes", 0, "", iWidth)

		screen.appendTableRow("WBPlotRoutes")
		screen.setTableText("WBPlotRoutes", 0, 0, "<font=3>" + sColor + CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ()) + "</font></color>", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_CANCEL").getPath(), WidgetTypes.WIDGET_PYTHON, 6788, -1, CvUtil.FONT_LEFT_JUSTIFY )
		for item in lRoutes:
			iRow = screen.appendTableRow("WBPlotRoutes")
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			if iRoute == item[1]:
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			screen.setTableText("WBPlotRoutes", 0, iRow, "<font=3>" + sColor + item[0] + "</font></color>", gc.getRouteInfo(item[1]).getButton(), WidgetTypes.WIDGET_PYTHON, 6788, item[1], CvUtil.FONT_LEFT_JUSTIFY )

	def placeFeature(self):
		screen = CyGInterfaceScreen( "WBPlotScreen", CvScreenEnums.WB_PLOT)
		iX = screen.getXResolution() *3/5 + 10
		iY = self.iTable_Y
		iHeight = (screen.getYResolution()/2 - 32 - iY) /24 * 24 + 2
		iFeature = pPlot.getFeatureType()
		iVariety = pPlot.getFeatureVariety()
#Magister Start
		if bReal:
			iFeature = pPlot.getRealFeatureType()
			iVariety = pPlot.getRealFeatureVariety()
			iHeight -= 20
			iY2 = iY + iHeight
			screen.setButtonGFC("FeatureTempTimerPlus", "", "", iX, iY2, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
			screen.setButtonGFC("FeatureTempTimerMinus", "", "", iX + 25, iY2, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
			sText = CyTranslator().getText("TXT_KEY_WB_TEMP_TIMER", (pPlot.getTempFeatureTimer(),))
			screen.setLabel("FeatureTempTimerText", "Background", "<font=3>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iX + 50, iY2, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		else:
			screen.hide("FeatureTempTimerPlus")
			screen.hide("FeatureTempTimerMinus")
			screen.hide("FeatureTempTimerText")
#Magister Stop

		sText = CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ())
		sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		if iFeature > -1:
			sText = gc.getFeatureInfo(iFeature).getDescription()
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())

		screen.setLabel("FeatureHeader", "Background", "<font=3b>" + sText + "</font>", CvUtil.FONT_CENTER_JUSTIFY, iX + screen.getXResolution()/10 - 10, iY - 30, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addTableControlGFC("WBPlotFeature", 1, iX, iY, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		screen.setTableColumnHeader("WBPlotFeature", 0, "", iWidth)

		screen.appendTableRow("WBPlotFeature")
		screen.setTableText("WBPlotFeature", 0, 0, "<font=3>" + sColor + CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ()) + "</font></color>", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_CANCEL").getPath(), WidgetTypes.WIDGET_PYTHON, 7874, -1, CvUtil.FONT_LEFT_JUSTIFY )
		for item in lFeatures:
			iRow = screen.appendTableRow("WBPlotFeature")
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			iType = item[1] % 10000
			if iFeature == iType and iVariety == item[1] / 10000:
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			screen.setTableText("WBPlotFeature", 0, iRow, "<font=3>" + sColor + item[0] + "</font></color>", gc.getFeatureInfo(iType).getButton(), WidgetTypes.WIDGET_PYTHON, 7874, item[1], CvUtil.FONT_LEFT_JUSTIFY )

	def placeImprovements(self):
		screen = CyGInterfaceScreen( "WBPlotScreen", CvScreenEnums.WB_PLOT)
		screen.hide("UpgradeTimePlus")
		screen.hide("UpgradeTimeMinus")
		screen.hide("UpgradeTimeText")
		iX = screen.getXResolution() *4/5 + 10#Magister		iX = screen.getXResolution() *3/5 + 10
		iY = screen.getYResolution()/2
		iUpgrade_Y = screen.getYResolution() - 70
		iHeight = (iUpgrade_Y - iY) /24 * 24 + 2
		iImprovement = pPlot.getImprovementType()
#Magister Start
		if bReal:
			iImprovement = pPlot.getRealImprovementType()
			iHeight -= 20
			iY2 = iY + iHeight
			screen.setButtonGFC("ImprovementTempTimerPlus", "", "", iX, iY2, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
			screen.setButtonGFC("ImprovementTempTimerMinus", "", "", iX + 25, iY2, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
			sText = CyTranslator().getText("TXT_KEY_WB_TEMP_TIMER", (pPlot.getTempImprovementTimer(),))
			screen.setLabel("ImprovementTempTimerText", "Background", "<font=3>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iX + 50, iY2, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		else:
			screen.hide("ImprovementTempTimerPlus")
			screen.hide("ImprovementTempTimerMinus")
			screen.hide("ImprovementTempTimerText")
#Magister Stop

		sText = CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ())
		sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		if iImprovement > -1:
			if not bReal:
				if gc.getImprovementInfo(iImprovement).getUpgradeTime():
					screen.setButtonGFC("UpgradeTimePlus", "", "", iX, iUpgrade_Y, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
					screen.setButtonGFC("UpgradeTimeMinus", "", "", iX + 25, iUpgrade_Y, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
					sText = CyTranslator().getText("TXT_KEY_WB_UPGRADE_PROGRESS", (pPlot.getUpgradeTimeLeft(iImprovement, pPlot.getOwner()),))
					screen.setLabel("UpgradeTimeText", "Background", "<font=3>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iX + 55, iUpgrade_Y + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

			sText = gc.getImprovementInfo(iImprovement).getDescription()
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		screen.setLabel("ImprovementHeader", "Background", "<font=3b>" + sText + "</font>", CvUtil.FONT_CENTER_JUSTIFY, iX + screen.getXResolution()/10 - 10, iY - 30, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addTableControlGFC("WBPlotImprovement", 1, iX, iY, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		screen.setTableColumnHeader("WBPlotImprovement", 0, "", iWidth)

		screen.appendTableRow("WBPlotImprovement")
		screen.setTableText("WBPlotImprovement", 0, 0, "<font=3>" + sColor + CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ()) + "</font></color>", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_CANCEL").getPath(), WidgetTypes.WIDGET_PYTHON, 7877, -1, CvUtil.FONT_LEFT_JUSTIFY )
		for item in lImprovements:
			iRow = screen.appendTableRow("WBPlotImprovement")
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			if iImprovement == item[1]:
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			screen.setTableText("WBPlotImprovement", 0, iRow, "<font=3>" + sColor + item[0] + "</font></color>", gc.getImprovementInfo(item[1]).getButton(), WidgetTypes.WIDGET_PYTHON, 7877, item[1], CvUtil.FONT_LEFT_JUSTIFY )

	def createBonusList(self):
		global lBonus
		lBonus = []
		for i in xrange(gc.getNumBonusInfos()):
			ItemInfo = gc.getBonusInfo(i)
			if iSelectedClass != ItemInfo.getBonusClassType() and iSelectedClass > -1: continue
			lBonus.append([ItemInfo.getDescription(), i])
		lBonus.sort()
		self.placeBonus()

	def placeBonus(self):
		screen = CyGInterfaceScreen( "WBPlotScreen", CvScreenEnums.WB_PLOT)
		iX = screen.getXResolution() *4/5 + 10
		iY = self.iTable_Y
		iHeight = (screen.getYResolution()/2 - 32 - iY) /24 * 24 + 2
		iBonus = pPlot.getBonusType(-1)
#Magister Start
		if bReal:
			iBonus = pPlot.getRealBonusType()
			iHeight -= 20
			iY2 = iY + iHeight
			screen.setButtonGFC("BonusTempTimerPlus", "", "", iX, iY2, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
			screen.setButtonGFC("BonusTempTimerMinus", "", "", iX + 25, iY2, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
			sText = CyTranslator().getText("TXT_KEY_WB_TEMP_TIMER", (pPlot.getTempBonusTimer(),))
			screen.setLabel("BonusTempTimerText", "Background", "<font=3>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iX + 50, iY2, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		else:
			screen.hide("BonusTempTimerPlus")
			screen.hide("BonusTempTimerMinus")
			screen.hide("BonusTempTimerText")
#Magister Stop

		sText = CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ())
		sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		if iBonus > -1:
			sText = gc.getBonusInfo(iBonus).getDescription()
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		screen.setLabel("BonusHeader", "Background", "<font=3b>" + sText + "</font>", CvUtil.FONT_CENTER_JUSTIFY, iX + screen.getXResolution()/10 - 10, iY - 30, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addTableControlGFC("WBPlotBonus", 1, iX, iY, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		screen.setTableColumnHeader("WBPlotBonus", 0, "", iWidth)

		screen.appendTableRow("WBPlotBonus")
		screen.setTableText("WBPlotBonus", 0, 0, "<font=3>" + sColor + CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ()) + "</font></color>", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_CANCEL").getPath(), WidgetTypes.WIDGET_PYTHON, 6788, -1, CvUtil.FONT_LEFT_JUSTIFY )
		for item in lBonus:
			iRow = screen.appendTableRow("WBPlotBonus")
			ItemInfo = gc.getBonusInfo(item[1])
			sButton = ItemInfo.getButton()
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			if iBonus == item[1]:
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			screen.setTableText("WBPlotBonus", 0, iRow, "<font=3>" + sColor + item[0] + "</font></color>", sButton, WidgetTypes.WIDGET_PYTHON, 7878, item[1], CvUtil.FONT_LEFT_JUSTIFY )

	def placeTerrain(self):
		screen = CyGInterfaceScreen( "WBPlotScreen", CvScreenEnums.WB_PLOT)
#Magister Start
##		iX = screen.getXResolution() /5 + 10
##		iY = self.iTable_Y
##		iHeight = (screen.getYResolution()/2 - 32 - iY) /24 * 24 + 2
##		iTerrain = pPlot.getTerrainType()

		iX = screen.getXResolution() *3/5 + 10
		iY = iPlotType_Y
		iHeight = (screen.getYResolution() - 52 - iY) /24 * 24 + 2
		iTerrain = pPlot.getTerrainType()

		if bReal:
			iTerrain = pPlot.getRealTerrainType()
			iHeight -= 20
			iY2 = iY + iHeight
			screen.setButtonGFC("TerrainTempTimerPlus", "", "", iX, iY2, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
			screen.setButtonGFC("TerrainTempTimerMinus", "", "", iX + 25, iY2, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
			sText = CyTranslator().getText("TXT_KEY_WB_TEMP_TIMER", (pPlot.getTempTerrainTimer(),))
			screen.setLabel("TerrainTempTimerText", "Background", "<font=3>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iX + 50, iY2, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		else:
			screen.hide("TerrainTempTimerPlus")
			screen.hide("TerrainTempTimerMinus")
			screen.hide("TerrainTempTimerText")

		sText = CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ())
		sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		if iTerrain  > -1:
			sText = gc.getTerrainInfo(iTerrain).getDescription()
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())

#Magister Stop
		screen.setLabel("TerrainHeader", "Background", "<font=3b>" + sText + "</font>", CvUtil.FONT_CENTER_JUSTIFY, iX + screen.getXResolution()/10 - 10, iY - 30, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addTableControlGFC("WBPlotTerrain", 1, iX, iY, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		screen.setTableColumnHeader("WBPlotTerrain", 0, "", iWidth)

		if bReal:
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			iRow = screen.appendTableRow("WBPlotTerrain")
			screen.setTableText("WBPlotTerrain", 0, 0, "<font=3>" + sColor + CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ()) + "</font></color>", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_CANCEL").getPath(), WidgetTypes.WIDGET_PYTHON, 7875, -1, CvUtil.FONT_LEFT_JUSTIFY )

		for i in xrange(gc.getNumTerrainInfos()):
			TerrainInfo = gc.getTerrainInfo(i)
			if TerrainInfo.isGraphicalOnly(): continue
			if TerrainInfo.isWater() != pPlot.isWater(): continue
			iRow = screen.appendTableRow("WBPlotTerrain")
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			if iTerrain == i:
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			sText = "<font=3>" + sColor + TerrainInfo.getDescription() + "</font></color>"
			screen.setTableText("WBPlotTerrain", 0, iRow, sText, TerrainInfo.getButton(), WidgetTypes.WIDGET_PYTHON, 7875, i, CvUtil.FONT_LEFT_JUSTIFY)

	def placeScript(self):
		screen = CyGInterfaceScreen("WBPlotScreen", CvScreenEnums.WB_PLOT)
		global iScript_Y
		iScript_Y = screen.getYResolution() - 120
		sText = CyTranslator().getText("[COLOR_SELECTED_TEXT]", ()) + "<font=3b>" + CyTranslator().getText("TXT_KEY_WB_SCRIPT_DATA", ()) + "</color></font>"
		screen.setText("PlotEditScriptData", "Background", sText, CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, iScript_Y, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addPanel( "ScriptPanel", "", "", False, False, screen.getXResolution()/2 - iWidth/2, iScript_Y + 25, iWidth, screen.getYResolution() - iScript_Y - 70, PanelStyles.PANEL_STYLE_IN)
		screen.addMultilineText("GameScriptDataText", pPlot.getScriptData(), screen.getXResolution()/2 - iWidth/2, iScript_Y + 25, iWidth, screen.getYResolution() - iScript_Y - 70, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

	def placePlotType(self):
		screen = CyGInterfaceScreen( "WBPlotScreen", CvScreenEnums.WB_PLOT)
		iX = screen.getXResolution() *2/5 + 10
		iY = iPlotType_Y
		iHeight = min(PlotTypes.NUM_PLOT_TYPES, (iScript_Y - iPlotType_Y)/24) * 24 + 2

		screen.addTableControlGFC("WBPlotType", 1, iX, iY, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		screen.setTableColumnHeader("WBPlotType", 0, "", iWidth)
		for iTerrain in xrange(PlotTypes.NUM_PLOT_TYPES):
			screen.appendTableRow("WBPlotType")

		iTerrain = gc.getInfoTypeForString("TERRAIN_PEAK")
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		TerrainInfo = gc.getTerrainInfo(iTerrain)
		if pPlot.getPlotType() == PlotTypes.PLOT_PEAK:
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			sHeader = TerrainInfo.getDescription()
		sText = "<font=3>" + sColor + TerrainInfo.getDescription() + "</font></color>"
		screen.setTableText("WBPlotType", 0, 0, sText, TerrainInfo.getButton(), WidgetTypes.WIDGET_PYTHON, 7875, iTerrain, CvUtil.FONT_LEFT_JUSTIFY)

		iTerrain = gc.getInfoTypeForString("TERRAIN_HILL")
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		TerrainInfo = gc.getTerrainInfo(iTerrain)
		if pPlot.getPlotType() == PlotTypes.PLOT_HILLS:
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			sHeader = TerrainInfo.getDescription()
		sText = "<font=3>" + sColor + TerrainInfo.getDescription() + "</font></color>"
		screen.setTableText("WBPlotType", 0, 1, sText, TerrainInfo.getButton(), WidgetTypes.WIDGET_PYTHON, 7875, iTerrain, CvUtil.FONT_LEFT_JUSTIFY)

		iTerrain = gc.getInfoTypeForString("TERRAIN_GRASS")
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		TerrainInfo = gc.getTerrainInfo(iTerrain)
		if pPlot.getPlotType() == PlotTypes.PLOT_LAND:
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			sHeader = TerrainInfo.getDescription()
		sText = "<font=3>" + sColor + TerrainInfo.getDescription() + "</font></color>"
		screen.setTableText("WBPlotType", 0, 2, sText, TerrainInfo.getButton(), WidgetTypes.WIDGET_PYTHON, 7875, iTerrain, CvUtil.FONT_LEFT_JUSTIFY)

		iTerrain = gc.getInfoTypeForString("TERRAIN_OCEAN")
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		TerrainInfo = gc.getTerrainInfo(iTerrain)
		if pPlot.getPlotType() == PlotTypes.PLOT_OCEAN:
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			sHeader = TerrainInfo.getDescription()
		sText = "<font=3>" + sColor + TerrainInfo.getDescription() + "</font></color>"
		screen.setTableText("WBPlotType", 0, 3, sText, TerrainInfo.getButton(), WidgetTypes.WIDGET_PYTHON, 7875, iTerrain, CvUtil.FONT_LEFT_JUSTIFY)

	def handleInput(self, inputClass):
		screen = CyGInterfaceScreen("WBPlotScreen", CvScreenEnums.WB_PLOT)
		global bAdd
		global bSensibility
		global iEditType
		global iChange
		global iCulturePlayer
		global iSelectedClass
		global bReal #Magister

		if inputClass.getFunctionName() == "ChangeBy":
			iChange = screen.getPullDownData("ChangeBy", screen.getSelectedPullDownID("ChangeBy"))

		elif inputClass.getFunctionName() == "CurrentPlayer":
			iIndex = screen.getPullDownData("CurrentPlayer", screen.getSelectedPullDownID("CurrentPlayer"))
			pPlot.setOwner(iIndex)

		elif inputClass.getFunctionName() == "ChangeType":
			bAdd = screen.getPullDownData("ChangeType", screen.getSelectedPullDownID("ChangeType"))

		elif inputClass.getFunctionName() == "EditType":
			iEditType = screen.getPullDownData("EditType", screen.getSelectedPullDownID("EditType"))

		elif inputClass.getFunctionName() == "CurrentPage":
			iIndex = screen.getPullDownData("CurrentPage", screen.getSelectedPullDownID("CurrentPage"))
			iPlayer = pPlot.getOwner()
			if iIndex == 1:
				WBEventScreen.WBEventScreen().interfaceScreen(pPlot)
			elif iIndex == 2:
				WBPlayerScreen.WBPlayerScreen().interfaceScreen(iPlayer)
			elif iIndex == 3:
				WBTeamScreen.WBTeamScreen().interfaceScreen(pPlot.getTeam())
			elif iIndex == 4:
				if pPlot.isCity():
					WBCityEditScreen.WBCityEditScreen(CvPlatyBuilderScreen.CvWorldBuilderScreen()).interfaceScreen(pPlot.getPlotCity())
			elif iIndex == 5:
				pUnit = pPlot.getUnit(0)
				if pUnit:
					WBUnitScreen.WBUnitScreen(CvPlatyBuilderScreen.CvWorldBuilderScreen()).interfaceScreen(pUnit)
			elif iIndex == 6:
				WBPlayerUnits.WBPlayerUnits().interfaceScreen(iPlayer)
			elif iIndex == 11:
				if iPlayer == -1:
					iPlayer = CyGame().getActivePlayer()
				WBInfoScreen.WBInfoScreen().interfaceScreen(iPlayer)

		elif inputClass.getFunctionName() == "NextPlotUpButton":
			pNewPlot = CyMap().plot(pPlot.getX(), pPlot.getY() + 1)
			if not pNewPlot.isNone():
				self.interfaceScreen(pNewPlot)
		elif inputClass.getFunctionName() == "NextPlotDownButton":
			pNewPlot = CyMap().plot(pPlot.getX(), pPlot.getY() - 1)
			if not pNewPlot.isNone():
				self.interfaceScreen(pNewPlot)
		elif inputClass.getFunctionName() == "NextPlotLeftButton":
			pNewPlot = CyMap().plot(pPlot.getX() - 1, pPlot.getY())
			if not pNewPlot.isNone():
				self.interfaceScreen(pNewPlot)
		elif inputClass.getFunctionName() == "NextPlotRightButton":
			pNewPlot = CyMap().plot(pPlot.getX() + 1, pPlot.getY())
			if not pNewPlot.isNone():
				self.interfaceScreen(pNewPlot)

		elif inputClass.getFunctionName().find("BaseYield") > -1:
			i = YieldTypes(inputClass.getData2())
			if inputClass.getData1() == 1030:
				CyGame().setPlotExtraYield(pPlot.getX(), pPlot.getY(), i, iChange)
			elif inputClass.getData1() == 1031:
				iYield = pPlot.getYield(i)
				iImprovement = pPlot.getImprovementType()
				if iImprovement > -1:
					iYield -= pPlot.calculateImprovementYieldChange(iImprovement, i, pPlot.getOwner(), False)
				CyGame().setPlotExtraYield(pPlot.getX(), pPlot.getY(), i, - min(iChange, iYield))
			self.placeStats()

		elif inputClass.getFunctionName() == "RiverWestAButton":
			pWestPlot = CyMap().plot(pPlot.getX() - 1, pPlot.getY())
			pWestPlot.setWOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_NORTH)
			self.placeStats()
		elif inputClass.getFunctionName() == "RiverWestBButton":
			pWestPlot = CyMap().plot(pPlot.getX() - 1, pPlot.getY())
			pWestPlot.setWOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
			self.placeStats()
		elif inputClass.getFunctionName() == "RiverWestCButton":
			pWestPlot = CyMap().plot(pPlot.getX() - 1, pPlot.getY())
			pWestPlot.setWOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_SOUTH)
			self.placeStats()

		elif inputClass.getFunctionName() == "RiverEastAButton":
			pPlot.setWOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_NORTH)
			self.placeStats()
		elif inputClass.getFunctionName() == "RiverEastBButton":
			pPlot.setWOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
			self.placeStats()
		elif inputClass.getFunctionName() == "RiverEastCButton":
			pPlot.setWOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_SOUTH)
			self.placeStats()

		elif inputClass.getFunctionName() == "RiverNorthAButton":
			pNorthPlot = CyMap().plot(pPlot.getX(), pPlot.getY() + 1)
			pNorthPlot.setNOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_WEST)
			self.placeStats()
		elif inputClass.getFunctionName() == "RiverNorthBButton":
			pNorthPlot = CyMap().plot(pPlot.getX(), pPlot.getY() + 1)
			pNorthPlot.setNOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
			self.placeStats()
		elif inputClass.getFunctionName() == "RiverNorthCButton":
			pNorthPlot = CyMap().plot(pPlot.getX(), pPlot.getY() + 1)
			pNorthPlot.setNOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_EAST)
			self.placeStats()

		elif inputClass.getFunctionName() == "RiverSouthAButton":
			pPlot.setNOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_WEST)
			self.placeStats()
		elif inputClass.getFunctionName() == "RiverSouthBButton":
			pPlot.setNOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
			self.placeStats()
		elif inputClass.getFunctionName() == "RiverSouthCButton":
			pPlot.setNOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_EAST)
			self.placeStats()

		elif inputClass.getFunctionName() == "WBSigns":
			if inputClass.getData1() == 7876 or inputClass.getData1() == 7872:
				iCulturePlayer = inputClass.getData2() /10000
				self.placeSigns()

		elif inputClass.getFunctionName().find("EditCulture") > -1:
			if inputClass.getData1() == 1030:
				pPlot.changeCulture(iCulturePlayer, iChange, True)
			elif inputClass.getData1() == 1031:
				pPlot.changeCulture(iCulturePlayer, -min(iChange, pPlot.getCulture(iCulturePlayer)), True)
			self.interfaceScreen(pPlot)

		elif inputClass.getFunctionName() == "WBPlotType":
			if iEditType == 0:
				pPlot.setPlotType(PlotTypes(inputClass.getData()), True, True)
			elif iEditType == 1:
				for i in xrange(CyMap().numPlots()):
					pLoopPlot = CyMap().plotByIndex(i)
					if pLoopPlot.isNone(): continue
					if pLoopPlot.getArea() == pPlot.getArea():
						pLoopPlot.setPlotType(PlotTypes(inputClass.getData()), True, True)
			else:
				CyMap().setAllPlotTypes(PlotTypes(inputClass.getData()))
			self.interfaceScreen(pPlot)

		elif inputClass.getFunctionName() == "WBPlotTerrain":
			iTerrain = inputClass.getData2()

			if bReal:
				if iEditType == 0:
					pPlot.setRealTerrainType(iTerrain)
				else:
					for i in xrange(CyMap().numPlots()):
						pLoopPlot = CyMap().plotByIndex(i)
						if pLoopPlot.isNone(): continue
						if iEditType == 1:
							if pLoopPlot.getArea() == pPlot.getArea():
								pLoopPlot.setRealTerrainType(iTerrain)
						elif iEditType == 2:
							if bSensibility and pLoopPlot.isWater() != pPlot.isWater(): continue
							pLoopPlot.setRealTerrainType(iTerrain)

			else:
				if iEditType == 0:
					pPlot.setTerrainType(iTerrain, True, True)
				else:
					for i in xrange(CyMap().numPlots()):
						pLoopPlot = CyMap().plotByIndex(i)
						if pLoopPlot.isNone(): continue
						if iEditType == 1:
							if pLoopPlot.getArea() == pPlot.getArea():
								pLoopPlot.setTerrainType(iTerrain, True, True)
						elif iEditType == 2:
							if bSensibility and pLoopPlot.isWater() != pPlot.isWater(): continue
							pLoopPlot.setTerrainType(iTerrain, True, True)
			self.interfaceScreen(pPlot)

		elif inputClass.getFunctionName() == "BonusClass":
			iSelectedClass = screen.getPullDownData("BonusClass", screen.getSelectedPullDownID("BonusClass"))
			self.createBonusList()

		elif inputClass.getFunctionName() == "WBPlotBonus":
			iBonus = inputClass.getData2()
##Magister Start
			if bReal:
				if iEditType == 0:
					if bAdd:
						pPlot.setRealBonusType(iBonus)
					else:
						pPlot.setRealBonusType(-1)
				else:
					for i in xrange(CyMap().numPlots()):
						pLoopPlot = CyMap().plotByIndex(i)
						if pLoopPlot.isNone(): continue
						if iEditType == 1 and pLoopPlot.getArea() != pPlot.getArea(): continue
						iOld = pLoopPlot.getRealBonusType()
						if bAdd:
							pLoopPlot.setRealBonusType(-1)
							if iBonus > -1 and bSensibility and not pLoopPlot.canHaveBonus(iBonus, False):
								pLoopPlot.setRealBonusType(iOld)
								continue
							pLoopPlot.setRealBonusType(iBonus)
						else:
							pLoopPlot.setRealBonusType(-1)

			else:
				if iEditType == 0:
					if bAdd:
						pPlot.setBonusType(iBonus)
					else:
						pPlot.setBonusType(-1)
				else:
					for i in xrange(CyMap().numPlots()):
						pLoopPlot = CyMap().plotByIndex(i)
						if pLoopPlot.isNone(): continue
						if iEditType == 1 and pLoopPlot.getArea() != pPlot.getArea(): continue
						iOld = pLoopPlot.getBonusType(-1)
						if bAdd:
							pLoopPlot.setBonusType(-1)
							if iBonus > -1 and bSensibility and not pLoopPlot.canHaveBonus(iBonus, False):
								pLoopPlot.setBonusType(iOld)
								continue
							pLoopPlot.setBonusType(iBonus)
						else:
							pLoopPlot.setBonusType(-1)

##Magister Stop
			self.placeBonus()

		elif inputClass.getFunctionName() == "WBPlotImprovement":
			iImprovement = inputClass.getData2()


##Magister Start
			if bReal:
				if iEditType == 0:
					if bAdd:
						pPlot.setRealImprovementType(iImprovement)
					else:
						pPlot.setRealImprovementType(-1)
				else:
					for i in xrange(CyMap().numPlots()):
						pLoopPlot = CyMap().plotByIndex(i)
						if pLoopPlot.isNone(): continue
						if iEditType == 1 and pLoopPlot.getArea() != pPlot.getArea(): continue
						if bAdd:
							if iImprovement > -1 and bSensibility and not pLoopPlot.canHaveImprovement(iImprovement, -1, True): continue
							pLoopPlot.setRealImprovementType(iImprovement)
						else:
							pLoopPlot.setRealImprovementType(-1)
			else:
				if iEditType == 0:
					if bAdd:
						pPlot.setImprovementType(iImprovement)
					else:
						pPlot.setImprovementType(-1)
				else:
					for i in xrange(CyMap().numPlots()):
						pLoopPlot = CyMap().plotByIndex(i)
						if pLoopPlot.isNone(): continue
						if iEditType == 1 and pLoopPlot.getArea() != pPlot.getArea(): continue
						if bAdd:
							if iImprovement > -1 and bSensibility and not pLoopPlot.canHaveImprovement(iImprovement, -1, True): continue
							pLoopPlot.setImprovementType(iImprovement)
						else:
							pLoopPlot.setImprovementType(-1)
##Magister Stop
			self.placeImprovements()
#Magister Start
			self.placeBonus()#Needed to make sure that bonuses update when an improvement like a mana node changes the bonus
			self.placeSigns()#Needed to update the landmarks placed on unique features in FfH2 or MNAI, or the signs from the Elohim or Celestial Compass in MagisterModmod
			self.placeRoutes()#I think that I set some unique features to automatically have roads then created, which should be shown on this screen



		elif inputClass.getFunctionName().find("ImprovementTempTimer") > -1:
			if inputClass.getData1() == 1030:
				pPlot.changeTempImprovementTimer(iChange)
			elif inputClass.getData1() == 1031:
				pPlot.changeTempImprovementTimer(-min(iChange, pPlot.getTempImprovementTimer()))

			self.placeImprovements()

		elif inputClass.getFunctionName().find("FeatureTempTimer") > -1:
			if inputClass.getData1() == 1030:
				pPlot.changeTempFeatureTimer(iChange)
			elif inputClass.getData1() == 1031:
				pPlot.changeTempFeatureTimer(-min(iChange, pPlot.getTempFeatureTimer()))
			self.placeFeature()

		elif inputClass.getFunctionName().find("BonusTempTimer") > -1:
			if inputClass.getData1() == 1030:
				pPlot.changeTempBonusTimer(iChange)
			elif inputClass.getData1() == 1031:
				pPlot.changeTempBonusTimer(-min(iChange, pPlot.getTempBonusTimer()))
			self.placeBonus()

		elif inputClass.getFunctionName().find("RouteTempTimer") > -1:
			if inputClass.getData1() == 1030:
				pPlot.changeTempRouteTimer(iChange)
			elif inputClass.getData1() == 1031:
				pPlot.changeTempRouteTimer(-min(iChange, pPlot.getTempRouteTimer()))
			self.placeRoutes()

		elif inputClass.getFunctionName().find("TerrainTempTimer") > -1:
			if inputClass.getData1() == 1030:
				pPlot.changeTempTerrainTimer(iChange)
			elif inputClass.getData1() == 1031:
				pPlot.changeTempTerrainTimer(-min(iChange, pPlot.getTempTerrainTimer()))
			self.placeTerrain()




#Magister Stop
		elif inputClass.getFunctionName().find("UpgradeTime") > -1:
			if not bReal:
				if inputClass.getData1() == 1030:
					pPlot.changeUpgradeProgress(- iChange)
				elif inputClass.getData1() == 1031:
					pPlot.changeUpgradeProgress(min(iChange, pPlot.getUpgradeTimeLeft(pPlot.getImprovementType(), pPlot.getOwner()) - 1))
				self.placeImprovements()

		elif inputClass.getFunctionName() == "WBPlotFeature":
			iFeature = inputClass.getData2() % 10000
			iVariety = inputClass.getData2() / 10000

			if bReal:
				if iVariety < 0 or iFeature < 0:
					iFeature = -1
					iVariety = 0
				if iEditType == 0:
					if bAdd:
						pPlot.setRealFeatureType(iFeature)
						pPlot.setRealFeatureVariety(iVariety)
					else:
						pPlot.setRealFeatureType(-1)
						pPlot.setRealFeatureVariety(0)
				else:
					for i in xrange(CyMap().numPlots()):
						pLoopPlot = CyMap().plotByIndex(i)
						if pLoopPlot.isNone(): continue
						if iEditType == 1 and pLoopPlot.getArea() != pPlot.getArea(): continue
						iOldFeature = pLoopPlot.getRealFeatureType()
						iOldVariety = pLoopPlot.getRealFeatureVariety()
						if bAdd:

							pLoopPlot.setRealFeatureType(-1)
							pLoopPlot.setRealFeatureVariety(0)

							if iFeature > -1 and bSensibility and not pLoopPlot.canHaveFeature(iFeature):

								pLoopPlot.setRealFeatureType(iOldFeature)
								pLoopPlot.setRealFeatureVariety(iOldVariety)
								continue
							pLoopPlot.setRealFeatureType(iFeature)
							pLoopPlot.setRealFeatureVariety(iVariety)
						else:
							pLooppPlot.setRealFeatureType(-1)
							pLooppPlot.setRealFeatureVariety(0)

			else:

				if iVariety < 0 or iFeature < 0:
					iFeature = -1
					iVariety = 0
				if iEditType == 0:
					if bAdd:
						pPlot.setFeatureType(iFeature, iVariety)
					else:
						pPlot.setFeatureType(-1, 0)
				else:
					for i in xrange(CyMap().numPlots()):
						pLoopPlot = CyMap().plotByIndex(i)
						if pLoopPlot.isNone(): continue
						if iEditType == 1 and pLoopPlot.getArea() != pPlot.getArea(): continue
						iOldFeature = pLoopPlot.getFeatureType()
						iOldVariety = pLoopPlot.getFeatureVariety()
						if bAdd:
							pLoopPlot.setFeatureType(-1, 0)
							if iFeature > -1 and bSensibility and not pLoopPlot.canHaveFeature(iFeature):
								pLoopPlot.setFeatureType(iOldFeature, iOldVariety)
								continue
							pLoopPlot.setFeatureType(iFeature, iVariety)
						else:
							pLoopPlot.setFeatureType(-1, 0)


			self.placeFeature()

		elif inputClass.getFunctionName() == "WBPlotRoutes":
			iRoute = inputClass.getData2()

			if bReal:
				if iEditType == 0:
					if bAdd:
						pPlot.setRealRouteType(iRoute)
					else:
						pPlot.setRealRouteType(-1)
				else:
					for i in xrange(CyMap().numPlots()):
						pLoopPlot = CyMap().plotByIndex(i)
						if pLoopPlot.isNone(): continue
						if bSensibility:
							if pLoopPlot.isImpassable(): continue
							if pLoopPlot.isWater(): continue
						if iEditType == 1 and pLoopPlot.getArea() != pPlot.getArea(): continue
						if bAdd:
							pLoopPlot.setRealRouteType(iRoute)
						else:
							if pLoopPlot.getRealRouteType() == iRoute:
								pLoopPlot.setRealRouteType(-1)

			else:
				if iEditType == 0:
					if bAdd:
						pPlot.setRouteType(iRoute)
					else:
						pPlot.setRouteType(-1)
				else:
					for i in xrange(CyMap().numPlots()):
						pLoopPlot = CyMap().plotByIndex(i)
						if pLoopPlot.isNone(): continue
						if bSensibility:
							if pLoopPlot.isImpassable(): continue
							if pLoopPlot.isWater(): continue
						if iEditType == 1 and pLoopPlot.getArea() != pPlot.getArea(): continue
						if bAdd:
							pLoopPlot.setRouteType(iRoute)
						else:
							if pLoopPlot.getRouteType() == iRoute:
								pLoopPlot.setRouteType(-1)


			self.placeRoutes()

		elif inputClass.getFunctionName() == "PlotEditScriptData":
			popup = Popup.PyPopup(5555, EventContextTypes.EVENTCONTEXT_ALL)
			popup.setHeaderString(CyTranslator().getText("TXT_KEY_WB_SCRIPT", ()))
			popup.setUserData((pPlot.getX(), pPlot.getY()))
			popup.createEditBox(pPlot.getScriptData())
			popup.launch()

		elif inputClass.getFunctionName() == "EditLandMark":
			iIndex = -1
			sText = ""
			for i in xrange(CyEngine().getNumSigns()):
				pSign = CyEngine().getSignByIndex(i)
				if pSign.getPlot().getX() != pPlot.getX(): continue
				if pSign.getPlot().getY() != pPlot.getY(): continue
				if pSign.getPlayerType() == iCulturePlayer:
					iIndex = i
					sText = pSign.getCaption()
					break

			popup = Popup.PyPopup(CvUtil.EventWBLandmarkPopup, EventContextTypes.EVENTCONTEXT_ALL)
			popup.setHeaderString(CyTranslator().getText("TXT_KEY_WB_LANDMARKS", ()))
			popup.setUserData((pPlot.getX(), pPlot.getY(), iCulturePlayer, iIndex))
			popup.createEditBox(sText)
			popup.launch()

		elif inputClass.getFunctionName() == "SensibilityCheck":
			bSensibility = not bSensibility
			screen.setState("SensibilityCheck", bSensibility)


#Magister Start
		elif inputClass.getFunctionName() == "RealType":
			bReal = not bReal
			screen.setState("RealType", bReal)

			self.placeStats()
			self.placeTerrain()
			self.placeFeature()
			self.placeImprovements()
			self.placeBonus()
			self.placeSigns()
			self.placeRoutes()


		elif inputClass.getFunctionName() == "MoveDisabledAIText":
			pPlot.setMoveDisabledAI(not pPlot.isMoveDisabledAI())
			self.placeStats()

		elif inputClass.getFunctionName() == "MoveDisabledHumanText":
			pPlot.setMoveDisabledHuman(not pPlot.isMoveDisabledHuman())
			self.placeStats()

		elif inputClass.getFunctionName() == "BuildDisabledText":
			pPlot.setBuildDisabled(not pPlot.isBuildDisabled())
			self.placeStats()

		elif inputClass.getFunctionName() == "FoundDisabledText":
			pPlot.setFoundDisabled(not pPlot.isFoundDisabled())
			self.placeStats()

		elif inputClass.getFunctionName() == "PythonActiveText":
			pPlot.setPythonActive(not pPlot.isPythonActive())
			self.placeStats()

		elif inputClass.getFunctionName().find("MinLevel") > -1:
			if inputClass.getData1() == 1030:
				pPlot.setMinLevel(pPlot.getMinLevel() + iChange)
			elif inputClass.getData1() == 1031:
				pPlot.setMinLevel(max(-1, pPlot.getMinLevel() - iChange))
			self.placeStats()

		elif inputClass.getFunctionName().find("PlotCounter") > -1:
			if inputClass.getData1() == 1030:
				pPlot.changePlotCounter(iChange)
			elif inputClass.getData1() == 1031:
				pPlot.changePlotCounter(-iChange)
			self.placeStats()
			self.placeTerrain()#Magister: Changing the Plot Counter may change a terrain to its hell terrain equivalent or vice versa

		elif inputClass.getFunctionName().find("PortalExitX") > -1:
			if inputClass.getData1() == 1030:
				pPlot.setPortalExitX(min(CyMap().getGridWidth(),pPlot.getPortalExitX() + iChange))
			elif inputClass.getData1() == 1031:
				pPlot.setPortalExitX(max(0, pPlot.getPortalExitX() - iChange))
			self.placeStats()

		elif inputClass.getFunctionName().find("PortalExitY") > -1:
			if inputClass.getData1() == 1030:
				pPlot.setPortalExitY(min(CyMap().getGridHeight(),pPlot.getPortalExitY() + iChange))
			elif inputClass.getData1() == 1031:
				pPlot.setPortalExitY(max(0, pPlot.getPortalExitY() - iChange))
			self.placeStats()

#Magister Stop

		return 1

	def update(self, fDelta):
		self.placeMap()
		global iCounter
		if iCounter > 0:
			iCounter -= 1
		elif iCounter == 0:
			self.placeSigns()
			iCounter = -1
		return 1