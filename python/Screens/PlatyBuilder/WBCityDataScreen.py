from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums
import WBBuildingScreen
import WBCityEditScreen
import WBPlayerScreen
import WBTeamScreen
import WBPlotScreen
import WBEventScreen
import WBPlayerUnits
gc = CyGlobalContext()
iChange = 1

class WBCityDataScreen:

	def __init__(self, main):
		self.top = main
		self.iBonusClass = -1

	def interfaceScreen(self, pCityX):
		screen = CyGInterfaceScreen( "WBCityDataScreen", CvScreenEnums.WB_CITYDATA)
		global pCity
		global iTableWidth
		global iHeight
		pCity = pCityX
		iHeight = (screen.getYResolution()/2 - 120) / 24 * 24 + 2
		iTableWidth = screen.getXResolution()/3 - 40

		screen.setRenderInterfaceOnly(True)
		screen.addPanel( "MainBG", u"", u"", True, False, -10, -10, screen.getXResolution() + 20, screen.getYResolution() + 20, PanelStyles.PANEL_STYLE_MAIN )
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)

		screen.addPanel( "SpecialistBG", u"", u"", True, False, 0, 0, screen.getXResolution()/3, screen.getYResolution()/2, PanelStyles.PANEL_STYLE_MAIN )
		screen.addPanel( "GreatPeopleBG", u"", u"", True, False, screen.getXResolution() /3, 0, screen.getXResolution()/3, screen.getYResolution()/2, PanelStyles.PANEL_STYLE_MAIN )
		screen.addPanel( "CorporationBG", u"", u"", True, False, 0, screen.getYResolution()/2, screen.getXResolution()/3, screen.getYResolution()/2, PanelStyles.PANEL_STYLE_MAIN )
		screen.addPanel( "ReligionBG", u"", u"", True, False, screen.getXResolution() /3, screen.getYResolution()/2, screen.getXResolution()/3, screen.getYResolution()/2, PanelStyles.PANEL_STYLE_MAIN )
		screen.addPanel( "BonusBG", u"", u"", True, False, screen.getXResolution() * 2/3, 0, screen.getXResolution()/3, screen.getYResolution(), PanelStyles.PANEL_STYLE_MAIN )

		screen.setLabel("SpecialistHeader", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_WB_FREE_SPECIALISTS", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/6 + 20, 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setLabel("GreatPeopleHeader", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_WB_GREAT_PEOPLE", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2 + 20, 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setLabel("BonusHeader", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_BONUS", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution() * 5/6 + 20, 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setLabel("ReligionHeader", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_RELIGION", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/6 + 20, screen.getYResolution()/2 + 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setLabel("CorporationHeader", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_CONCEPT_CORPORATIONS", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2 + 20, screen.getYResolution()/2 + 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setText("ReligionCopy", "Background", u"<font=3b>" + CyTranslator().getText("TXT_KEY_WB_COPY_ALL", (CyTranslator().getText("TXT_KEY_CONCEPT_CITIES", ()),)) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, 20, screen.getYResolution()/2 + 50, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setText("CorporationCopy", "Background", u"<font=3b>" + CyTranslator().getText("TXT_KEY_WB_COPY_ALL", (CyTranslator().getText("TXT_KEY_CONCEPT_CITIES", ()),)) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, screen.getXResolution()/3 + 20, screen.getYResolution()/2 + 50, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setText("SpecialistExit", "Background", "<font=4>" + CyTranslator().getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 30, screen.getYResolution() - 42, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )
		
		screen.addDropDownBoxGFC("CurrentPage", 20, screen.getYResolution() - 42, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_CITY_DATA", ()), 0, 0, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_CITY_DATA2", ()), 1, 1, True)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_BUILDING", ()), 2, 2, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_HELP4", ()), 3, 3, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_TEAM_DATA", ()), 4, 4, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_UNIT", ()) + " + " + CyTranslator().getText("TXT_KEY_CONCEPT_CITIES", ()), 5, 5, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_HELP19", ()), 6, 6, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_CONCEPT_EVENTS", ()), 7, 7, False)

		screen.addDropDownBoxGFC("ChangeBy", 20, 50, 160, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		i = 1
		while i < 1001:
			screen.addPullDownString("ChangeBy", CyTranslator().getText("TXT_KEY_WB_CHANGE_BY",(i,)), i, i, iChange == i)
			if str(i)[0] == "1":
				i *= 5
			else:
				i *= 2
		
		screen.addDropDownBoxGFC("BonusClass", screen.getXResolution() * 2/3 + 20, 50, 100, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("BonusClass", CyTranslator().getText("TXT_KEY_WB_CITY_ALL",()), -1, -1, True)
		screen.addPullDownString("BonusClass", CyTranslator().getText("TXT_PEDIA_GENERAL",()), 0, 0, 0 == self.iBonusClass)
		iBonusClass = 1
		while not gc.getBonusClassInfo(iBonusClass) is None:
			sText = gc.getBonusClassInfo(iBonusClass).getType()
			sText = sText[sText.find("_") +1:]
			sText = sText.lower()
			sText = sText.capitalize()
			screen.addPullDownString("BonusClass", sText, iBonusClass, iBonusClass, iBonusClass == self.iBonusClass)
			iBonusClass += 1

		screen.setButtonGFC("GreatPeopleRatePlus", u"", "", screen.getXResolution()/3 + 20, screen.getYResolution()/2 - 40, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("GreatPeopleRateMinus", u"", "", screen.getXResolution()/3 + 45, screen.getYResolution()/2 - 40, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)

		sText = CyTranslator().getText("TXT_KEY_WB_CITY_ALL", ())
		screen.setLabel("ReligionAll", "Background", u"<font=4b>" + sText + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution()/3 - 70, screen.getYResolution()/2 + 50, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setButtonGFC("ReligionAllPlus", u"", "", screen.getXResolution()/3 - 70, screen.getYResolution()/2 + 51, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("ReligionAllMinus", u"", "", screen.getXResolution()/3 - 45, screen.getYResolution()/2 + 51, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)

		screen.setLabel("CorporationAll", "Background", u"<font=4b>" + sText + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() * 2/3 - 70, screen.getYResolution()/2 + 50, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setButtonGFC("CorporationAllMinus", u"", "", screen.getXResolution() * 2/3 - 45, screen.getYResolution()/2 + 51, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)

		screen.setLabel("SpecialistAll", "Background", u"<font=4b>" + sText + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution()/3 - 70, 50, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setButtonGFC("SpecialistAllPlus", u"", "", screen.getXResolution()/3 - 70, 51, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("SpecialistAllMinus", u"", "", screen.getXResolution()/3 - 45, 51, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)

		screen.setLabel("GreatPeopleProgressAll", "Background", u"<font=4b>" + sText + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() * 2/3 - 70, 50, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setButtonGFC("GreatPeopleProgressPlus", u"", "", screen.getXResolution() * 2/3 - 70, 51, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("GreatPeopleProgressMinus", u"", "", screen.getXResolution() * 2/3 - 45, 51, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)

		screen.setLabel("BonusAll", "Background", u"<font=4b>" + sText + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 70, 50, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setButtonGFC("BonusAllPlus", u"", "", screen.getXResolution() - 70, 51, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("BonusAllMinus", u"", "", screen.getXResolution() - 45, 51, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)

		global lCorporations
		global lReligions
		global lSpecialist
		global lGreatPeople

		lCorporations = []
		for i in xrange(gc.getNumCorporationInfos()):
			ItemInfo = gc.getCorporationInfo(i)
			lCorporations.append([ItemInfo.getDescription(), i])
		lCorporations.sort()

		lReligions = []
		for i in xrange(gc.getNumReligionInfos()):
			ItemInfo = gc.getReligionInfo(i)
			lReligions.append([ItemInfo.getDescription(), i])
		lReligions.sort()

		lSpecialist = []
		lGreatPeople = []
		for i in xrange(gc.getNumSpecialistInfos()):
			ItemInfo = gc.getSpecialistInfo(i)
			lSpecialist.append((ItemInfo.getDescription(), i))
			iGPClass = ItemInfo.getGreatPeopleUnitClass()
			if iGPClass == -1: continue
			iGP = gc.getCivilizationInfo(pCity.getCivilizationType()).getCivilizationUnits(iGPClass)
			if iGP == -1: continue
			if not iGP in lGreatPeople:
				lGreatPeople.append(iGP)

		for i in xrange(gc.getNumBuildingInfos()):
			ItemInfo = gc.getBuildingInfo(i)
			iGPClass = ItemInfo.getGreatPeopleUnitClass()
			if iGPClass == -1: continue
			iGP = gc.getCivilizationInfo(pCity.getCivilizationType()).getCivilizationUnits(iGPClass)
			if iGP == -1: continue
			if not iGP in lGreatPeople:
				lGreatPeople.append(iGP)

		for i in xrange(len(lGreatPeople)):
			GPInfo = gc.getUnitInfo(lGreatPeople[i])
			lGreatPeople[i] = [GPInfo.getDescription(), lGreatPeople[i]]
		lSpecialist.sort()
		lGreatPeople.sort()

		self.createBonusList()
		self.placeGreatPeople()
		self.placeBonus()
		self.placeSpecialist()
		self.placeReligions()
		self.placeCorporations()

	def placeCorporations(self):
		screen = CyGInterfaceScreen( "WBCityDataScreen", CvScreenEnums.WB_CITYDATA)
		screen.addTableControlGFC( "WBCorporation", 2, screen.getXResolution()/3 + 20, screen.getYResolution()/2 + 80, iTableWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		screen.setTableColumnHeader( "WBCorporation", 0, CyTranslator().getText("[ICON_STAR]", ()), 24)
		screen.setTableColumnHeader( "WBCorporation", 1, "", iTableWidth)
		
		for item in lCorporations:
			iRow = screen.appendTableRow("WBCorporation")
			ItemInfo = gc.getCorporationInfo(item[1])
			sHoly = CyTranslator().getText("[ICON_SILVER_STAR]", ())
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			if pCity.isHeadquartersByType(item[1]):
				sColor = CyTranslator().getText("[COLOR_YELLOW]", ())
				sHoly = CyTranslator().getText("[ICON_STAR]", ())
			elif pCity.isHasCorporation(item[1]):
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			screen.setTableText("WBCorporation", 1, iRow, "<font=3>" + sColor + item[0] + "</font></color>", ItemInfo.getButton(), WidgetTypes.WIDGET_PYTHON, 8201, item[1], CvUtil.FONT_LEFT_JUSTIFY )
			screen.setTableText("WBCorporation", 0, iRow, sHoly, "", WidgetTypes.WIDGET_PYTHON, 6782, item[1], CvUtil.FONT_CENTER_JUSTIFY )

	def placeReligions(self):
		screen = CyGInterfaceScreen( "WBCityDataScreen", CvScreenEnums.WB_CITYDATA)
		screen.addTableControlGFC( "WBReligion", 2, 20, screen.getYResolution()/2 + 80, iTableWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		screen.setTableColumnHeader( "WBReligion", 0, CyTranslator().getText("[ICON_STAR]", ()), 24)
		screen.setTableColumnHeader( "WBReligion", 1, "", iTableWidth - 24)

		for item in lReligions:
			iRow = screen.appendTableRow("WBReligion")
			ItemInfo = gc.getReligionInfo(item[1])
			sHoly = CyTranslator().getText("[ICON_SILVER_STAR]", ())
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			if pCity.isHolyCityByType(item[1]):
				sColor = CyTranslator().getText("[COLOR_YELLOW]", ())
				sHoly = CyTranslator().getText("[ICON_STAR]", ())
			elif pCity.isHasReligion(item[1]):
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			screen.setTableText("WBReligion", 1, iRow, "<font=3>" + sColor + item[0] + "</font></color>", ItemInfo.getButton(), WidgetTypes.WIDGET_HELP_RELIGION, item[1], 1, CvUtil.FONT_LEFT_JUSTIFY )
			screen.setTableText("WBReligion", 0, iRow, sHoly, "", WidgetTypes.WIDGET_HELP_RELIGION, item[1], 2, CvUtil.FONT_CENTER_JUSTIFY )

	def placeSpecialist(self):
		screen = CyGInterfaceScreen( "WBCityDataScreen", CvScreenEnums.WB_CITYDATA)
		screen.setLabel("GreatPeopleRateText", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_WB_BASE_RATE", (pCity.getBaseGreatPeopleRate(),)) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, screen.getXResolution()/3 + 70, screen.getYResolution()/2 - 40, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addTableControlGFC( "WBSpecialist", 3, 20, 80, iTableWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		screen.setTableColumnHeader( "WBSpecialist", 0, "", 24)
		screen.setTableColumnHeader( "WBSpecialist", 1, "", 24)
		screen.setTableColumnHeader( "WBSpecialist", 2, "", iTableWidth - 50)

		for item in lSpecialist:
			iRow = screen.appendTableRow("WBSpecialist")
			sItem = item[0]
			ItemInfo = gc.getSpecialistInfo(item[1])
			iNum = pCity.getFreeSpecialistCount(item[1])
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			if iNum > 0:
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
				sItem += " (" + str(iNum) + ")"
			screen.setTableText("WBSpecialist", 0, iRow, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_PLUS").getPath(), WidgetTypes.WIDGET_PYTHON, 1030, item[1], CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBSpecialist", 1, iRow, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_MINUS").getPath(), WidgetTypes.WIDGET_PYTHON, 1031, item[1], CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBSpecialist", 2, iRow, "<font=3>" + sColor + sItem + "</font></color>", ItemInfo.getButton(), WidgetTypes.WIDGET_PYTHON, 7879, item[1], CvUtil.FONT_LEFT_JUSTIFY )

	def placeGreatPeople(self):
		screen = CyGInterfaceScreen( "WBCityDataScreen", CvScreenEnums.WB_CITYDATA)
		screen.setLabel("GreatPeopleProgressText", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_WB_PROGRESS", (pCity.getGreatPeopleProgress(),)) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, screen.getXResolution()/3 + 20, 50, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addTableControlGFC( "WBGreatPeople", 3, screen.getXResolution()/3 + 20, 80, iTableWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		screen.setTableColumnHeader( "WBGreatPeople", 0, "", 24)
		screen.setTableColumnHeader( "WBGreatPeople", 1, "", 24)
		screen.setTableColumnHeader( "WBGreatPeople", 2, "", iTableWidth - 50)

		for item in lGreatPeople:
			iRow = screen.appendTableRow("WBGreatPeople")
			sItem = item[0]
			ItemInfo = gc.getUnitInfo(item[1])
			iNum = pCity.getGreatPeopleUnitProgress(item[1])
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			if iNum > 0:
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
				sItem += " (" + str(iNum) + ")"
			screen.setTableText("WBGreatPeople", 0, iRow, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_PLUS").getPath(), WidgetTypes.WIDGET_PYTHON, 1030, item[1], CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBGreatPeople", 1, iRow, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_MINUS").getPath(), WidgetTypes.WIDGET_PYTHON, 1031, item[1], CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBGreatPeople", 2, iRow, "<font=3>" + sColor + sItem + "</font></color>", ItemInfo.getButton(), WidgetTypes.WIDGET_PYTHON, 8202, item[1], CvUtil.FONT_LEFT_JUSTIFY )

	def createBonusList(self):
		global lBonus
		lBonus = []
		for i in xrange(gc.getNumBonusInfos()):
			ItemInfo = gc.getBonusInfo(i)
			if self.iBonusClass != ItemInfo.getBonusClassType() and self.iBonusClass > -1: continue
			lBonus.append([ItemInfo.getDescription(), i])
		lBonus.sort()

	def placeBonus(self):
		screen = CyGInterfaceScreen( "WBCityDataScreen", CvScreenEnums.WB_CITYDATA)
		iHeight2 = (screen.getYResolution() - 120) / 24 * 24 + 2

		screen.addTableControlGFC( "WBBonus", 3, screen.getXResolution() * 2/3 + 20, 80, iTableWidth, iHeight2, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		screen.setTableColumnHeader( "WBBonus", 0, "", 24)
		screen.setTableColumnHeader( "WBBonus", 1, "", 24)
		screen.setTableColumnHeader( "WBBonus", 2, "", iTableWidth - 50)

		for item in lBonus:
			iRow = screen.appendTableRow("WBBonus")
			sItem = item[0]
			ItemInfo = gc.getBonusInfo(item[1])
			sButton = ItemInfo.getButton()
			iNum = pCity.getFreeBonus(item[1])
			sColor = CyTranslator().getText("[COLOR_YELLOW]", ())
			if iNum > 0:
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
				sItem += " (" + str(iNum) + ")"
			if pCity.isNoBonus(item[1]):
				sButton = CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_CANCEL").getPath()
				sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			screen.setTableText("WBBonus", 0, iRow, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_PLUS").getPath(), WidgetTypes.WIDGET_PYTHON, 1030, item[1], CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBBonus", 1, iRow, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_MINUS").getPath(), WidgetTypes.WIDGET_PYTHON, 1031, item[1], CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBBonus", 2, iRow, "<font=3>" + sColor + sItem + "</font></color>", sButton, WidgetTypes.WIDGET_PYTHON, 7878, item[1], CvUtil.FONT_LEFT_JUSTIFY )

	def handleInput (self, inputClass):
		screen = CyGInterfaceScreen( "WBCityDataScreen", CvScreenEnums.WB_CITYDATA)
		global iChange
		if inputClass.getFunctionName() == "ChangeBy":
			iIndex = screen.getSelectedPullDownID("ChangeBy")
			iChange = screen.getPullDownData("ChangeBy", iIndex)

		elif inputClass.getFunctionName() == "CurrentPage":
			iIndex = screen.getPullDownData("CurrentPage", screen.getSelectedPullDownID("CurrentPage"))
			if iIndex == 0:
				WBCityEditScreen.WBCityEditScreen(self.top).interfaceScreen(pCity)
			elif iIndex == 2:
				WBBuildingScreen.WBBuildingScreen(self.top).interfaceScreen(pCity)
			elif iIndex == 3:
				WBPlayerScreen.WBPlayerScreen(self.top).interfaceScreen(pCity.getOwner())
			elif iIndex == 4:
				WBTeamScreen.WBTeamScreen(self.top).interfaceScreen(pCity.getTeam())
			elif iIndex == 5:
				WBPlayerUnits.WBPlayerUnits(self.top).interfaceScreen(pCity.getOwner())
			elif iIndex == 6:
				WBPlotScreen.WBPlotScreen(self.top).interfaceScreen(pCity.plot())
			elif iIndex == 7:
				WBEventScreen.WBEventScreen(self.top).interfaceScreen(pCity.plot())

		elif inputClass.getFunctionName().find("SpecialistAll") > -1:
			self.handlePlatySpecialistAll(inputClass.getData1())
			self.placeSpecialist()

		elif inputClass.getFunctionName() == "WBSpecialist":
			if inputClass.getData1() == 1030:
				self.handlePlatyFreeSpecialist(inputClass.getData2(), iChange)
			elif inputClass.getData1() == 1031:
				self.handlePlatyFreeSpecialist(inputClass.getData2(), - iChange)
			self.placeSpecialist()

		elif inputClass.getFunctionName().find("GreatPeopleProgress") > -1:
			self.handlePlatyGreatPeopleProgressAll(inputClass.getData1())
			self.placeGreatPeople()

		elif inputClass.getFunctionName().find("GreatPeopleRate") > -1:
			self.handlePlatyGreatPeopleRate(inputClass.getData1())
			screen.setLabel("GreatPeopleRateText", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_WB_BASE_RATE", (pCity.getBaseGreatPeopleRate(),)) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, screen.getXResolution()/3 + 70, screen.getYResolution()/2 - 40, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		elif inputClass.getFunctionName() == "WBGreatPeople":
			if inputClass.getData1() == 1030:
				self.handlePlatyGreatPeopleProgress(inputClass.getData2(), iChange)
			elif inputClass.getData1() == 1031:
				self.handlePlatyGreatPeopleProgress(inputClass.getData2(), - iChange)
			self.placeGreatPeople()

		elif inputClass.getFunctionName() == "BonusClass":
			self.iBonusClass = inputClass.getData() - 1
			self.createBonusList()
			self.placeBonus()

		elif inputClass.getFunctionName().find("BonusAll") > -1:
			self.handlePlatyBonusAll(inputClass.getData1())
			self.placeBonus()

		elif inputClass.getFunctionName() == "WBBonus":
			if inputClass.getData1() == 1030:
				self.handlePlatyFreeBonus(inputClass.getData2(), iChange)
			elif inputClass.getData1() == 1031:
				self.handlePlatyFreeBonus(inputClass.getData2(), - iChange)
			elif inputClass.getData1() == 7878:
				self.handlePlatyNoBonusCB(inputClass.getData2())
			self.placeBonus()

		elif inputClass.getFunctionName().find("ReligionAll") > -1:
			self.handlePlatyReligionAll(inputClass.getData1() %2)
			self.placeReligions()

		elif inputClass.getFunctionName() == "ReligionCopy":
			self.handlePlatyReligionCopy()

		elif inputClass.getFunctionName() == "WBReligion":
			if inputClass.getData2() == 1:
				self.handlePlatySetReligionCB(inputClass.getData1())
			elif inputClass.getData2() == 2:
				self.handlePlatySetHolyCityCB(inputClass.getData1())
			self.placeReligions()

		elif inputClass.getFunctionName().find("CorporationAll") > -1:
			self.handlePlatyCorporationAll()
			self.placeCorporations()

		elif inputClass.getFunctionName() == "CorporationCopy":
			self.handlePlatyCorporationCopy()

		elif inputClass.getFunctionName() == "WBCorporation":
			if inputClass.getData1() == 8201:
				self.handlePlatySetCorporationCB(inputClass.getData2())
			elif inputClass.getData1() == 6782:
				self.handlePlatySetHeadquartersCB(inputClass.getData2())
			self.placeCorporations()
		return 1

	def handlePlatySetCorporationCB (self, iData1) :
		if pCity.isHeadquartersByType(iData1):
			CyGame().clearHeadquarters(iData1)
		pCity.setHasCorporation(iData1, not pCity.isHasCorporation(iData1), False, False)

	def handlePlatySetHeadquartersCB (self, iData1):
		if pCity.isHeadquartersByType(iData1):
			CyGame().clearHeadquarters(iData1)
		else:
			CyGame().clearHeadquarters(iData1)
			CyGame().setHeadquarters(iData1, pCity, False)

	def handlePlatyCorporationCopy(self):
		for i in xrange(gc.getNumCorporationInfos()):
			(loopCity, iter) = gc.getPlayer(pCity.getOwner()).firstCity(false)
			while(loopCity):
				if pCity.isHasCorporation(i):
					loopCity.setHasCorporation(i, True, False, False)
				else:
					loopCity.setHasCorporation(i, False, False, False)
					if loopCity.isHeadquartersByType(i):
						CyGame().clearHeadquarters(i)
				(loopCity, iter) = gc.getPlayer(pCity.getOwner()).nextCity(iter, false)

	def handlePlatyCorporationAll(self) :
		for i in xrange(gc.getNumCorporationInfos()):
			pCity.setHasCorporation(i, False, False, False)
			if pCity.isHeadquartersByType(i):
				CyGame().clearHeadquarters(i)

	def handlePlatySetReligionCB (self, iData1) :
		if pCity.isHolyCityByType(iData1):
			CyGame().clearHolyCity(iData1)
		pCity.setHasReligion(iData1, not pCity.isHasReligion(iData1), False, False)

	def handlePlatySetHolyCityCB (self, iData1):
		if pCity.isHolyCityByType(iData1):
			CyGame().clearHolyCity(iData1)
		else:
			CyGame().clearHolyCity(iData1)
			CyGame().setHolyCity(iData1, pCity, False)

	def handlePlatyReligionCopy(self):
		for i in xrange(gc.getNumReligionInfos()):
			(loopCity, iter) = gc.getPlayer(pCity.getOwner()).firstCity(false)
			while(loopCity):
				if pCity.isHasReligion(i):
					loopCity.setHasReligion(i, True, False, False)
				else:
					loopCity.setHasReligion(i, False, False, False)
					if loopCity.isHolyCityByType(i):
						CyGame().clearHolyCity(i)
				(loopCity, iter) = gc.getPlayer(pCity.getOwner()).nextCity(iter, false)

	def handlePlatyReligionAll(self, bDisable) :
		for i in xrange(gc.getNumReligionInfos()):
			pCity.setHasReligion(i, not bDisable, False, False)
			if bDisable:
				if pCity.isHolyCityByType(i):
					CyGame().clearHolyCity(i)

	def handlePlatyFreeBonus(self, iData1, iCount):
		if iCount < 0:
			iCount = max(iCount, - pCity.getFreeBonus(iData1))
		pCity.changeFreeBonus(iData1, iCount)

	def handlePlatyNoBonusCB (self, iData1):
		if pCity.isNoBonus(iData1):
			pCity.changeNoBonusCount(iData1, -1)
		else:
			pCity.changeNoBonusCount(iData1, 1)

	def handlePlatyBonusAll(self, iData1):
		for item in lBonus:
			if self.iBonusClass != gc.getBonusInfo(item[1]).getBonusClassType() and self.iBonusClass > -1: continue
			if iData1%2:
				self.handlePlatyFreeBonus(item[1], - iChange)
			else:
				self.handlePlatyFreeBonus(item[1], iChange)

	def handlePlatyGreatPeopleRate(self, iData1):
		if iData1 % 2:
			pCity.changeBaseGreatPeopleRate(-iChange)
			if pCity.getBaseGreatPeopleRate() < 0:
				pCity.changeBaseGreatPeopleRate(-pCity.getBaseGreatPeopleRate())
		else:
			pCity.changeBaseGreatPeopleRate(iChange)

	def handlePlatyGreatPeopleProgressAll(self, iData1):
		for item in lGreatPeople:
			if iData1 % 2:
				self.handlePlatyGreatPeopleProgress(item[1], - iChange)
			else:
				self.handlePlatyGreatPeopleProgress(item[1], iChange)

	def handlePlatyGreatPeopleProgress(self, iData1, iCount) :
		if iCount < 0:
			iCount = max(iCount, - pCity.getGreatPeopleUnitProgress(iData1))
		pCity.changeGreatPeopleUnitProgress(iData1, iCount)
		pCity.changeGreatPeopleProgress(iCount)

	def handlePlatyFreeSpecialist(self, iData1, iCount) :
		if iCount < 0:
			iCount = max(iCount, - pCity.getFreeSpecialistCount(iData1))
		pCity.changeFreeSpecialistCount(iData1, iCount)

	def handlePlatySpecialistAll(self, iData1):
		for i in xrange(gc.getNumSpecialistInfos()):
			if iData1%2:
				self.handlePlatyFreeSpecialist(i, - iChange)
			else:
				self.handlePlatyFreeSpecialist(i, iChange)

	def update(self, fDelta):
		return 1