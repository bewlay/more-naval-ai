## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums

# globals
gc = CyGlobalContext()
g_pCity = None

class WBCorporationScreen:

	def __init__(self):
		self.iList = []

	def interfaceScreen(self, pCity):
		screen = CyGInterfaceScreen( "WBCorporationScreen", CvScreenEnums.WB_CORPORATION)
		global g_pCity
		g_pCity = pCity

		self.nTableWidth = screen.getXResolution() - 40
##		self.nTableHeight = screen.getYResolution()/2 - 100
		self.nTableHeight = screen.getYResolution() - 100
		screen.setRenderInterfaceOnly(True)
		screen.addPanel( "MainBG", u"", u"", True, False, -10, -10, screen.getXResolution() + 20, screen.getYResolution() + 20, PanelStyles.PANEL_STYLE_MAIN )
		screen.setDimensions(0, 0, screen.getXResolution(), screen.getYResolution())
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)

##		screen.addPanel( "CorporationBG", u"", u"", True, False, 0, 0, screen.getXResolution(), screen.getYResolution()/2, PanelStyles.PANEL_STYLE_MAIN )
##		screen.addPanel( "ReligionBG", u"", u"", True, False, 0, screen.getYResolution()/2, screen.getXResolution(), screen.getYResolution()/2, PanelStyles.PANEL_STYLE_MAIN )
		screen.addPanel( "ReligionBG", u"", u"", True, False, 0, 0, screen.getXResolution(), screen.getYResolution(), PanelStyles.PANEL_STYLE_MAIN )



		screen.setText("CorporationExit", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 25, screen.getYResolution() - 45, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )

##		screen.setText("CorporationHeader", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_CONCEPT_CORPORATIONS", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
##		screen.setText("ReligionHeader", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_RELIGION", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, screen.getYResolution()/2 + 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setText("ReligionHeader", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_RELIGION", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

##		szDropdownName = str("CorporationCommands")
##		screen.addDropDownBoxGFC(szDropdownName, screen.getXResolution() - 200, 20, 180, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
##		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_COMMANDS", ()), 0, 0, True)
##		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_CLEAR_ALL", ()), 1, 1, False)
##		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_COPY_ALL", ()), 2, 2, False)

		szDropdownName = str("ReligionCommands")
##		screen.addDropDownBoxGFC(szDropdownName, screen.getXResolution() - 200, screen.getYResolution()/2 + 20, 180, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addDropDownBoxGFC(szDropdownName, screen.getXResolution() - 200, 20, 180, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)

		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_COMMANDS", ()), 0, 0, True)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_GRANT_ALL", ()), 1, 1, False)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_CLEAR_ALL", ()), 2, 2, False)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_COPY_ALL", ()), 3, 3, False)

		nColumns = 2#Magister

##		nColumns = 6
##		screen.addTableControlGFC( "WBCorporation", nColumns, 20, 60, self.nTableWidth, self.nTableHeight, True, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
##		for i in xrange(0, nColumns, 2):
##			screen.setTableColumnHeader( "WBCorporation", i, CyTranslator().getText("[ICON_STAR]", ()), 24)
##			screen.setTableColumnHeader( "WBCorporation", i + 1, "", self.nTableWidth/(nColumns/2) - 24)
##
##		self.iList = []
##		for i in xrange(gc.getNumCorporationInfos()):
##			ItemInfo = gc.getCorporationInfo(i)
##			self.iList.append([ItemInfo.getDescription(), i])
##		self.iList.sort()
##
##		nRows = (len(self.iList) + (nColumns/2) - 1) / (nColumns/2)
##		for i in xrange(nRows):
##			screen.appendTableRow("WBCorporation")
##
##		for iCount in xrange(len(self.iList)):
##			item = self.iList[iCount]
##			iRow = iCount % nRows
##			iColumn = iCount / nRows
##			ItemInfo = gc.getCorporationInfo(item[1])
##			sHoly = ""
##			if pCity.isHeadquartersByType(item[1]):
##				sColor = CyTranslator().getText("[COLOR_YELLOW]", ())
##				sHoly = CyTranslator().getText("[ICON_STAR]", ())
##			elif pCity.isHasCorporation(item[1]):
##				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
##			else:
##				sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
##			screen.setTableText("WBCorporation", iColumn * 2 + 1, iRow, sColor + item[0] + "</color>", ItemInfo.getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_CORPORATION, item[1], 1, CvUtil.FONT_LEFT_JUSTIFY )
##			screen.setTableText("WBCorporation", iColumn * 2, iRow, sHoly, "", WidgetTypes.WIDGET_PEDIA_JUMP_TO_CORPORATION, item[1], 2, CvUtil.FONT_LEFT_JUSTIFY )
				





##		screen.addTableControlGFC( "WBReligion", nColumns, 20, screen.getYResolution()/2 + 60, self.nTableWidth, self.nTableHeight, True, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )

		screen.addTableControlGFC( "WBReligion", nColumns, 20, 60, self.nTableWidth, self.nTableHeight, True, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		for i in xrange(0, nColumns, 2):
			screen.setTableColumnHeader( "WBReligion", i, CyTranslator().getText("[ICON_STAR]", ()), 24)
			screen.setTableColumnHeader( "WBReligion", i + 1, "", self.nTableWidth/(nColumns/2) - 24)

		self.iList = []
		for i in xrange(gc.getNumReligionInfos()):
			ItemInfo = gc.getReligionInfo(i)
			self.iList.append([ItemInfo.getDescription(), i])
##		self.iList.sort()

		nRows = (len(self.iList) + (nColumns/2) - 1) / (nColumns/2)
		for i in xrange(nRows):
			screen.appendTableRow("WBReligion")

		for iCount in xrange(len(self.iList)):
			item = self.iList[iCount]
			iRow = iCount % nRows
			iColumn = iCount / nRows
			ItemInfo = gc.getReligionInfo(item[1])
			sHoly = ""
			if pCity.isHolyCityByType(item[1]):
				sColor = CyTranslator().getText("[COLOR_YELLOW]", ())
				sHoly = CyTranslator().getText("[ICON_STAR]", ())
			elif pCity.isHasReligion(item[1]):
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			else:
				sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			screen.setTableText("WBReligion", iColumn * 2 + 1, iRow, sColor + item[0] + "</color>", ItemInfo.getButton(), WidgetTypes.WIDGET_HELP_RELIGION, item[1], 3, CvUtil.FONT_LEFT_JUSTIFY )
			screen.setTableText("WBReligion", iColumn * 2, iRow, sHoly, "", WidgetTypes.WIDGET_HELP_RELIGION, item[1], 4, CvUtil.FONT_LEFT_JUSTIFY )

	def handleInput (self, inputClass):
		global g_pCity
		if inputClass.getNotifyCode() == NotifyCode.NOTIFY_LISTBOX_ITEM_SELECTED:
##			if inputClass.getFunctionName() == "CorporationCommands":
##				self.handlePlatyCorporationCommandsCB(inputClass.getData())
##				return 1
##			elif inputClass.getFunctionName() == "ReligionCommands":
			if inputClass.getFunctionName() == "ReligionCommands":
				self.handlePlatyReligionCommandsCB(inputClass.getData())
				return 1
		if inputClass.getData2() == 1 and inputClass.getData1() > -1:
			self.handlePlatySetCorporationCB(inputClass.getData1())
			return 1
		if inputClass.getData2() == 2 and inputClass.getData1() > -1:
			self.handlePlatySetHeadquartersCB(inputClass.getData1())
			return 1
		if inputClass.getData2() == 3 and inputClass.getData1() > -1:
			self.handlePlatySetReligionCB(inputClass.getData1())
			return 1
		if inputClass.getData2() == 4 and inputClass.getData1() > -1:
			self.handlePlatySetHolyCityCB(inputClass.getData1())
			return 1
		return 1

##	def handlePlatySetCorporationCB (self, iData1) :
##		g_pCity.setHasCorporation(iData1, not g_pCity.isHasCorporation(iData1), False, False)
##		if g_pCity.isHeadquartersByType(iData1) and not g_pCity.isHasCorporation(iData1):
##			CyGame().clearHeadquarters(iData1)
##		self.interfaceScreen(g_pCity)
##		return 1
##
##	def handlePlatySetHeadquartersCB (self, iData1):
##		if not g_pCity.isHeadquartersByType(iData1):
##			CyGame().clearHeadquarters(iData1)
##			CyGame().setHeadquarters(iData1, g_pCity, False)
##		else:
##			CyGame().clearHeadquarters(iData1)
##		self.interfaceScreen(g_pCity)
##		return 1
##
##	def handlePlatyCorporationCommandsCB (self, argsList) :
##		if int(argsList) == 1:
##			for item in self.iList:
##				g_pCity.setHasCorporation(item[1], False, False, False)
##				if g_pCity.isHeadquartersByType(item[1]):
##					CyGame().clearHeadquarters(item[1])
##				self.interfaceScreen(g_pCity)
##		elif int(argsList) == 2:
##			for item in self.iList:
##				(loopCity, iter) = gc.getPlayer(g_pCity.getOwner()).firstCity(false)
##				while(loopCity):
##					if g_pCity.isHasCorporation(item[1]):
##						loopCity.setHasCorporation(item[1], True, False, False)
##					else:
##						loopCity.setHasCorporation(item[1], False, False, False)
##						if loopCity.isHeadquartersByType(item[1]):
##							CyGame().clearHeadquarters(item[1])
##					(loopCity, iter) = gc.getPlayer(g_pCity.getOwner()).nextCity(iter, false)
##		return 1

	def handlePlatySetReligionCB (self, iData1) :
		g_pCity.setHasReligion(iData1, not g_pCity.isHasReligion(iData1), False, False)
		if g_pCity.isHolyCityByType(iData1) and not g_pCity.isHasReligion(iData1):
			CyGame().clearHolyCity(iData1)
		self.interfaceScreen(g_pCity)
		return 1

	def handlePlatySetHolyCityCB (self, iData1):
		if not g_pCity.isHolyCityByType(iData1):
			CyGame().clearHolyCity(iData1)
			CyGame().setHolyCity(iData1, g_pCity, False)
		else:
			CyGame().clearHolyCity(iData1)
		self.interfaceScreen(g_pCity)
		return 1

	def handlePlatyReligionCommandsCB (self, argsList) :
		if int(argsList) == 1:
			for item in self.iList:
				g_pCity.setHasReligion(item[1], True, False, False)
				self.interfaceScreen(g_pCity)
		elif int(argsList) == 2:
			for item in self.iList:
				g_pCity.setHasReligion(item[1], False, False, False)
				if g_pCity.isHolyCityByType(item[1]):
					CyGame().clearHolyCity(item[1])
				self.interfaceScreen(g_pCity)
		elif int(argsList) == 3:
			for item in self.iList:
				(loopCity, iter) = gc.getPlayer(g_pCity.getOwner()).firstCity(false)
				while(loopCity):
					if g_pCity.isHasReligion(item[1]):
						loopCity.setHasReligion(item[1], True, False, False)
					else:
						loopCity.setHasReligion(item[1], False, False, False)
						if loopCity.isHolyCityByType(item[1]):
							CyGame().clearHolyCity(item[1])
					(loopCity, iter) = gc.getPlayer(g_pCity.getOwner()).nextCity(iter, false)
		return 1

	def update(self, fDelta):
		return 1