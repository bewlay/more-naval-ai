from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums
import WBPlotScreen
import WBEventScreen
import WBCityEditScreen
import WBUnitScreen
import WBPlayerScreen
import WBTeamScreen
import Popup
gc = CyGlobalContext()
iCounter = -1

class WBLandMarks:

	def __init__(self, main):
		self.top = main
		self.iTable_Y = 80

	def interfaceScreen(self, pPlotX):
		screen = CyGInterfaceScreen("WBLandMarks", CvScreenEnums.WB_LANDMARK)
		
		global pPlot
		global iWidth

		pPlot = pPlotX
		iWidth = screen.getXResolution() - 40
		
		screen.setRenderInterfaceOnly(True)
		screen.addPanel( "MainBG", u"", u"", True, False, -10, -10, screen.getXResolution() + 20, screen.getYResolution() + 20, PanelStyles.PANEL_STYLE_MAIN )
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)

		screen.setLabel("LandMarkHeader", "Background", "<font=4b>" + CyTranslator().getText("TXT_KEY_WB_LANDMARKS", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setText("LandMarkExit", "Background", "<font=4>" + CyTranslator().getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 30, screen.getYResolution() - 42, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )

		screen.addDropDownBoxGFC("CurrentPage", 20, screen.getYResolution() - 42, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_HELP19", ()), 0, 0, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_CONCEPT_EVENTS", ()), 1, 1, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_LANDMARKS", ()), 2, 2, True)
		if pPlot.isOwned():
			screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_HELP4", ()), 3, 3, False)
			screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_TEAM_DATA", ()), 4, 4, False)
			if pPlot.isCity():
				screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_CITY_DATA", ()), 5, 5, False)
		if pPlot.getNumUnits() > 0:
			screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_UNIT_DATA", ()), 6, 6, False)

		self.placeSigns()

	def placeSigns(self):
		screen = CyGInterfaceScreen("WBLandMarks", CvScreenEnums.WB_LANDMARK)
		lSigns = []
		for iPlayerX in xrange(gc.getMAX_PLAYERS()):
			lSigns.append(-1)
		for i in xrange(CyEngine().getNumSigns()):
			pSign = CyEngine().getSignByIndex(i)
			if pSign.getPlot().getX() != pPlot.getX(): continue
			if pSign.getPlot().getY() != pPlot.getY(): continue
			lSigns[pSign.getPlayerType()] = i

		iHeight = (screen.getYResolution() - self.iTable_Y - 42) / 24 * 24 + 2
		screen.addTableControlGFC("WBSigns", 3, 20, self.iTable_Y, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		screen.setTableColumnHeader("WBSigns", 0, "", iWidth/6)
		screen.setTableColumnHeader("WBSigns", 1, "", iWidth/6)
		screen.setTableColumnHeader("WBSigns", 2, "", iWidth * 2/3)

		screen.appendTableRow("WBSigns")
		screen.setTableText("WBSigns", 0, 0, "<font=3>" + CyTranslator().getText("TXT_KEY_WB_LANDMARKS", ()) + "</font>", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_GENERAL_QUESTIONMARK").getPath(), WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
		screen.setTableText("WBSigns", 1, 0, "<font=3>" + CyTranslator().getText("TXT_KEY_WB_LANDMARKS", ()) + "</font>", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_GENERAL_QUESTIONMARK").getPath(), WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
		iIndex = lSigns[gc.getBARBARIAN_PLAYER()]
		sText = ""
		if iIndex > -1:
			sText = CyEngine().getSignByIndex(iIndex).getCaption()
			screen.setTableText("WBSigns", 2, 0, "<font=3>" + sText + "</font>", "", WidgetTypes.WIDGET_PYTHON, 1027, iIndex, CvUtil.FONT_LEFT_JUSTIFY)
		else:
			screen.setTableText("WBSigns", 2, 0, "<font=3>" + sText + "</font>", "", WidgetTypes.WIDGET_PYTHON, 1026, gc.getBARBARIAN_PLAYER(), CvUtil.FONT_LEFT_JUSTIFY)
			
		for iPlayerX in xrange(gc.getMAX_PLAYERS()):
			if iPlayerX == gc.getBARBARIAN_PLAYER(): continue
			pPlayerX = gc.getPlayer(iPlayerX)
			if pPlayerX.isEverAlive():
				iRow = screen.appendTableRow("WBSigns")
				sColor = u"<color=%d,%d,%d,%d>" %(pPlayerX.getPlayerTextColorR(), pPlayerX.getPlayerTextColorG(), pPlayerX.getPlayerTextColorB(), pPlayerX.getPlayerTextColorA())
				iCivilization = pPlayerX.getCivilizationType()
				iLeader = pPlayerX.getLeaderType()
				sText = "<font=3>" + sColor + pPlayerX.getCivilizationShortDescription(0) + "</font></color>"
				screen.setTableText("WBSigns", 0, iRow, sText, gc.getCivilizationInfo(iCivilization).getButton(), WidgetTypes.WIDGET_PYTHON, 7872, iPlayerX * 10000 + iCivilization, CvUtil.FONT_LEFT_JUSTIFY )
				sText = "<font=3>" + sColor + pPlayerX.getName() + "</font></color>"
				screen.setTableText("WBSigns", 1, iRow, sText, gc.getLeaderHeadInfo(iLeader).getButton(), WidgetTypes.WIDGET_PYTHON, 7876, iPlayerX * 10000 + iLeader, CvUtil.FONT_LEFT_JUSTIFY )
				iIndex = lSigns[iPlayerX]
				sText = ""
				if iIndex > -1:
					sText = CyEngine().getSignByIndex(iIndex).getCaption()
					screen.setTableText("WBSigns", 2, iRow, "<font=3>" + sText + "</font>", "", WidgetTypes.WIDGET_PYTHON, 1027, iIndex, CvUtil.FONT_LEFT_JUSTIFY)
				else:
					screen.setTableText("WBSigns", 2, iRow, "<font=3>" + sText + "</font>", "", WidgetTypes.WIDGET_PYTHON, 1026, iPlayerX, CvUtil.FONT_LEFT_JUSTIFY)

	def handleInput(self, inputClass):
		screen = CyGInterfaceScreen("WBLandMarks", CvScreenEnums.WB_LANDMARK)

		if inputClass.getFunctionName() == "CurrentPage":
			iIndex = screen.getPullDownData("CurrentPage", screen.getSelectedPullDownID("CurrentPage"))
			if iIndex == 0:
				WBPlotScreen.WBPlotScreen(self.top).interfaceScreen(pPlot)
			elif iIndex == 1:
				WBEventScreen.WBEventScreen(self.top).interfaceScreen(pPlot)
			elif iIndex == 3:
				WBPlayerScreen.WBPlayerScreen(self.top).interfaceScreen(pPlot.getOwner())
			elif iIndex == 4:
				WBTeamScreen.WBTeamScreen(self.top).interfaceScreen(pPlot.getTeam())
			elif iIndex == 5:
				if pPlot.isCity():
					WBCityEditScreen.WBCityEditScreen(self.top).interfaceScreen(pPlot.getPlotCity())
			elif iIndex == 6:
				if self.iUnit > -1 and iEventPlayer > -1:
					pUnit = gc.getPlayer(iEventPlayer).getUnit(self.iUnit)
				else:
					pUnit = pPlot.getUnit(0)
				if pUnit:
					WBUnitScreen.WBUnitScreen(self.top).interfaceScreen(pUnit)

		elif inputClass.getFunctionName() == "WBSigns":
			iPlayer = -1
			iIndex = -1
			sText = ""
			if inputClass.getData1() == 1026:
				iPlayer = inputClass.getData2()
			elif inputClass.getData1() == 1027:
				iIndex = inputClass.getData2()
				sText = CyEngine().getSignByIndex(iIndex).getCaption()

			popup = Popup.PyPopup(CvUtil.EventWBLandmarkPopup, EventContextTypes.EVENTCONTEXT_ALL)
			popup.setHeaderString(CyTranslator().getText("TXT_KEY_WB_EDIT_SIGN", ()))
			popup.setUserData((pPlot.getX(), pPlot.getY(), iPlayer, iIndex))
			popup.createEditBox(sText)
			popup.launch()
		return 1

	def update(self, fDelta):
		global iCounter
		if iCounter > 0:
			iCounter -= 1
		elif iCounter == 0:
			self.placeSigns()
			iCounter = -1
		return 1