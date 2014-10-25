from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums
import WBBuildingScreen
import WBCityDataScreen
import WBPlayerScreen
import WBTeamScreen
import WBPlotScreen
import WBEventScreen
import WBPlayerUnits
import WBReligionScreen
import WBCorporationScreen
import WBInfoScreen
import CvPlatyBuilderScreen
import Popup
gc = CyGlobalContext()

iChange = 1

class WBCityEditScreen:

	def __init__(self):
		self.iTable_Y = 110

	def interfaceScreen(self, pCityX):
		screen = CyGInterfaceScreen( "WBCityEditScreen", CvScreenEnums.WB_CITYEDIT)
		global pCity
		global iPlayer

		pCity = pCityX
		iPlayer = pCity.getOwner()
		
		screen.setRenderInterfaceOnly(True)
		screen.addPanel( "MainBG", u"", u"", True, False, -10, -10, screen.getXResolution() + 20, screen.getYResolution() + 20, PanelStyles.PANEL_STYLE_MAIN )
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)
		
		screen.setText("WBCityEditExit", "Background", "<font=4>" + CyTranslator().getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 30, screen.getYResolution() - 42, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )
		sText = "<font=3b>%s, X: %d, Y: %d</font>" %(CyTranslator().getText("TXT_KEY_WB_LATITUDE",(pCity.plot().getLatitude(),)), pCity.getX(), pCity.getY())
		
		pPlot = pCity.plot()
		sText = u"<font=3b>%s ID: %d, %s: %d</font>" %(CyTranslator().getText("TXT_KEY_WB_CITY", ()), pCity.getID(), CyTranslator().getText("TXT_KEY_WB_AREA_ID", ()), pPlot.getArea())
		screen.setLabel("PlotScreenHeaderB", "Background", "<font=4b>" + sText + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 50, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		sText = "<font=3b>%s, X: %d, Y: %d</font>" %(CyTranslator().getText("TXT_KEY_WB_LATITUDE",(pPlot.getLatitude(),)), pPlot.getX(), pPlot.getY())
		screen.setLabel("PlotLocation", "Background", sText, CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 70, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iWidth = screen.getXResolution()/4 - 40
		iY = self.iTable_Y - 60
		screen.addDropDownBoxGFC("CityOwner", 20, self.iTable_Y - 60, iWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		for i in xrange(gc.getMAX_PLAYERS()):
			pPlayerX = gc.getPlayer(i)
			if pPlayerX.isEverAlive():
				sText = pPlayerX.getName()
				if not pPlayerX.isAlive():
					sText = "*" + sText
				screen.addPullDownString("CityOwner", sText, i, i, i == iPlayer)

		iY += 30
		iHeight = (screen.getYResolution() - 40 - iY) / 24 * 24 + 2
		screen.addTableControlGFC( "CurrentCity", 1, 20, iY, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		screen.setTableColumnHeader("CurrentCity", 0, "", iWidth)

		pPlayer = gc.getPlayer(iPlayer)
		(loopCity, iter) = pPlayer.firstCity(False)
		while(loopCity):
			iRow = screen.appendTableRow("CurrentCity")
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			if loopCity.getID() == pCity.getID():
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			screen.setTableText("CurrentCity", 0, iRow, "<font=3>" + sColor + loopCity.getName() + "</font></color>", gc.getCivilizationInfo(pCity.getCivilizationType()).getButton(), WidgetTypes.WIDGET_PYTHON, 7200 + iPlayer, loopCity.getID(), CvUtil.FONT_LEFT_JUSTIFY )
			(loopCity, iter) = pPlayer.nextCity(iter, False)

		screen.addDropDownBoxGFC("ChangeBy", screen.getXResolution()/4, self.iTable_Y, iWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		i = 1
		while i < 1000001:
			screen.addPullDownString("ChangeBy", "(+/-) " + str(i), i, i, iChange == i)
			if str(i)[0] == "1":
				i *= 5
			else:
				i *= 2

		screen.addDropDownBoxGFC("CurrentPage", 20, screen.getYResolution() - 42, iWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_CITY_DATA", ()), 0, 0, True)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_CITY_DATA2", ()), 1, 1, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_BUILDING", ()), 2, 2, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_PLAYER_DATA", ()), 3, 3, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_TEAM_DATA", ()), 4, 4, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_RELIGION", ()), 8, 8, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_CONCEPT_CORPORATIONS", ()), 9, 9, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_UNIT", ()) + " + " + CyTranslator().getText("TXT_KEY_CONCEPT_CITIES", ()), 5, 5, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_PLOT_DATA", ()), 6, 6, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_CONCEPT_EVENTS", ()), 7, 7, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_INFO_SCREEN", ()), 11, 11, False)

		self.placeStats()
		self.placeProduction()
		self.placeScript()

	def placeMap(self):
		screen = CyGInterfaceScreen("WBCityEditScreen", CvScreenEnums.WB_CITYEDIT)
		iWidth = screen.getXResolution()/2 - 40
		iMapHeight = min((screen.getYResolution()/2 - 85 - self.iTable_Y), iWidth * 2/3)
		iMapWidth = iMapHeight * 3/2
		screen.addPlotGraphicGFC("PlotView", screen.getXResolution() *3/4 - iMapWidth/2, self.iTable_Y, iMapWidth, iMapHeight, pCity.plot(), 350, True, WidgetTypes.WIDGET_GENERAL, -1, -1)

	def placeStats(self):
		screen = CyGInterfaceScreen("WBCityEditScreen", CvScreenEnums.WB_CITYEDIT)
		sText = CyTranslator().getText("[COLOR_SELECTED_TEXT]", ()) + "<font=4b>" + pCity.getName() + "</color></font>"
		screen.setText("CityName", "Background", sText, CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 20, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_CITY_NAME, -1, -1)
		global iPlayer
		global pPlayer
		iPlayer = pCity.getOwner()
		pPlayer = gc.getPlayer(iPlayer)

		iX = screen.getXResolution()/4
##Magister
		iY = self.iTable_Y

		screen.addDropDownBoxGFC("CivilizationType", 2*iX, iY, screen.getXResolution()/8, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		for i in range(gc.getNumCivilizationInfos()):
			screen.addPullDownString("CivilizationType", gc.getCivilizationInfo(i).getDescription(), i, i, pCity.getCivilizationType() == i)

		iY += 30
##Magister
		screen.addDropDownBoxGFC("CityCultureLevel", iX, iY, screen.getXResolution()/4 - 40, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		for i in xrange(gc.getNumCultureLevelInfos()):
			screen.addPullDownString("CityCultureLevel", gc.getCultureLevelInfo(i).getDescription(), i, i, pCity.getCultureLevel() == i)

		iY += 30
		screen.setButtonGFC("CityChangeCulturePlus", "", "", iX, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityChangeCultureMinus", "", "", iX + 25, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = u"<font=3>%s %s/%s%c</font>" %(CyTranslator().getText("TXT_KEY_WB_CULTURE",()), CvPlatyBuilderScreen.CvWorldBuilderScreen().addComma(pCity.getCulture(iPlayer)), CvPlatyBuilderScreen.CvWorldBuilderScreen().addComma(pCity.getCultureThreshold()), gc.getCommerceInfo(CommerceTypes.COMMERCE_CULTURE).getChar())
		screen.setLabel("CityChangeCultureText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, iX + 50, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 30
		for i in xrange(YieldTypes.NUM_YIELD_TYPES):
			iYield = pCity.getBaseYieldRate(YieldTypes(i))
			screen.setButtonGFC("BaseYieldPlus" + str(i), "", "", iX, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, i, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
			screen.setButtonGFC("BaseYieldMinus" + str(i), "", "", iX + 25, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, i, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
			sText = CyTranslator().getText("TXT_KEY_WB_BASE_YIELD", (gc.getYieldInfo(i).getDescription(), iYield,))
			sText = u"%s%c" %(sText, gc.getYieldInfo(i).getChar())
			screen.setLabel("BaseYieldText" + str(i), "Background", "<font=3>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iX + 50, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			iY += 30

		screen.setButtonGFC("CityFoodPlus", "", "", iX, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityFoodMinus", "", "", iX + 25, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = u"<font=3>%s: %d/%d%c</font>" %(CyTranslator().getText("TXT_KEY_CONCEPT_FOOD",()), pCity.getFood(), pCity.growthThreshold(), gc.getYieldInfo(YieldTypes.YIELD_FOOD).getChar())
		screen.setLabel("CityFoodText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, iX + 50, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 30
		screen.setButtonGFC("CityPopulationPlus", "", "", iX, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityPopulationMinus", "", "", iX + 25, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = "<font=3>" + CyTranslator().getText("TXT_KEY_WB_POPULATION",()) + " " + str(pCity.getPopulation()) + CyTranslator().getText("[ICON_ANGRYPOP]", ()) + "</font>"
		screen.setLabel("CityPopulationText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, iX + 50, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 30
		sText = "<font=3>" + CyTranslator().getText("TXT_KEY_WB_DEFENSE",(pCity.getDefenseModifier(False),)) + "</font>"
		screen.setLabel("CityDefenseValueText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, iX + 50, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 30
		screen.setButtonGFC("CityDefensePlus", "", "", iX, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityDefenseMinus", "", "", iX + 25, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = "<font=3>" + CyTranslator().getText("TXT_KEY_WB_DAMAGE",()) + ": " + str(pCity.getDefenseDamage()) + "</font>"
		screen.setLabel("CityDefenseDamageText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, iX + 50, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 30
		screen.setButtonGFC("CityTradeRoutePlus", "", "", iX, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityTradeRouteMinus", "", "", iX + 25, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = u"<font=3>%s: %d%s</font>" %(CyTranslator().getText("TXT_KEY_CONCEPT_TRADE",()), pCity.getTradeRoutes(), CyTranslator().getText("[ICON_TRADE]",()))
		screen.setLabel("CityCTradeRouteText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, iX + 50, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 30
		screen.setButtonGFC("CityChangeHappyPlus", "", "", iX, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityChangeHappyMinus", "", "", iX + 25, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = "<font=3>%s: %d%s, %d%s</font>" %(CyTranslator().getText("TXT_KEY_CONCEPT_HAPPINESS",()), pCity.happyLevel(), CyTranslator().getText("[ICON_HAPPY]",()), pCity.unhappyLevel(0), CyTranslator().getText("[ICON_UNHAPPY]",()))
		screen.setLabel("CityChangeHappyText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, iX + 50, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 30
		screen.setButtonGFC("CityChangeHealthPlus", "", "", iX, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityChangeHealthMinus", "", "", iX + 25, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = "<font=3>%s: %d%s, %d%s</font>" %(CyTranslator().getText("TXT_KEY_CONCEPT_HEALTH",()), pCity.goodHealth(), CyTranslator().getText("[ICON_HEALTHY]",()), pCity.badHealth(False), CyTranslator().getText("[ICON_UNHEALTHY]",()))
		screen.setLabel("CityChangeHealthText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, iX + 50, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 30
		screen.setButtonGFC("CityOccupationTurnPlus", "", "", iX, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityOccupationTurnMinus", "", "", iX + 25, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = "<font=3>" + CyTranslator().getText("TXT_KEY_CONCEPT_RESISTANCE",()) + ": " + str(pCity.getOccupationTimer()) + CyTranslator().getText("[ICON_OCCUPATION]", ()) + "</font>"
		screen.setLabel("CityOccupationTurnText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, iX + 50, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 30
		screen.setButtonGFC("CityDraftAngerPlus", "", "", iX, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityDraftAngerMinus", "", "", iX + 25, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = "<font=3>" + CyTranslator().getText("TXT_KEY_CONCEPT_DRAFT",()) + CyTranslator().getText(" [ICON_UNHAPPY]: ",()) + str(pCity.getConscriptAngerTimer()) + "</font>"
		screen.setLabel("CityDraftAngerText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, iX + 50, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 30
		screen.setButtonGFC("CityHurryAngerPlus", "", "", iX, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityHurryAngerMinus", "", "", iX + 25, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = "<font=3>" + CyTranslator().getText("TXT_KEY_WB_HURRY_ANGER",(pCity.getHurryAngerTimer(),)) + "</font>"
		screen.setLabel("CityHurryAngerText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, iX + 50, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 30
		screen.setButtonGFC("CityDefyResolutionPlus", "", "", iX, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityDefyResolutionMinus", "", "", iX + 25, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = "<font=3>" + CyTranslator().getText("TXT_KEY_WB_DEFY_RESOLUTION",(pCity.getDefyResolutionAngerTimer(),)) + "</font>"
		screen.setLabel("CityDefyResolutionText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, iX + 50, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 30
		screen.setButtonGFC("CityEspionageHealthPlus", "", "", iX, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityEspionageHealthMinus", "", "", iX + 25, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = u"<font=3>%s %s: %d</font>" %(CyTranslator().getText("TXT_KEY_ESPIONAGE_CULTURE",()), CyTranslator().getText("[ICON_UNHEALTHY]", ()), pCity.getEspionageHealthCounter())
		screen.setLabel("CityEspionageHealthText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, iX + 50, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 30
		screen.setButtonGFC("CityTemporaryHappyPlus", "", "", iX, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityTemporaryHappyMinus", "", "", iX + 25, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = "<font=3>" + CyTranslator().getText("TXT_KEY_WB_TEMP_HAPPY",(pCity.getHappinessTimer(),)) + "</font>"
		screen.setLabel("CityTemporaryHappyText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, iX + 50, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

#Magister Start
		iY += 30
		screen.setButtonGFC("CityRevolutionIndexPlus", "", "", iX, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityRevolutionIndexMinus", "", "", iX + 25, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = "<font=3>" + CyTranslator().getText("TXT_KEY_WB_REV_INDEX",(pCity.getRevolutionIndex(),)) + "</font>"
		screen.setLabel("CityRevolutionIndexText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, iX + 50, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
#Magister Stop

	def placeScript(self):
		screen = CyGInterfaceScreen( "WBCityEditScreen", CvScreenEnums.WB_CITYEDIT)
		iY = screen.getYResolution()/2 - 85
		iX = screen.getXResolution()/2
		sText = CyTranslator().getText("[COLOR_SELECTED_TEXT]", ()) + "<font=3b>" + CyTranslator().getText("TXT_KEY_WB_SCRIPT_DATA", ()) + "</color></font>"
		screen.setText("CityEditScriptData", "Background", sText, CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution() * 3/4, iY, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addPanel("ScriptPanel", "", "", False, False, iX + 20, iY + 25, screen.getXResolution()/2 - 40, 60, PanelStyles.PANEL_STYLE_IN)
		screen.addMultilineText("CityScriptDataText", pCity.getScriptData(), iX + 20, iY + 25, screen.getXResolution()/2 - 40, 60, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

	def placeProduction(self):
		screen = CyGInterfaceScreen( "WBCityEditScreen", CvScreenEnums.WB_CITYEDIT)
		iY = screen.getYResolution()/2
		sText = CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ())
		screen.hide("CurrentProductionMinus")
		screen.hide("CurrentProductionPlus")
		if pCity.isProductionProcess():
			sText = pCity.getProductionName()
		elif pCity.isProduction():
			sText = u"%s: %d/%d%c" %(pCity.getProductionName(), pCity.getProduction(), pCity.getProductionNeeded(), gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar())
			screen.setButtonGFC("CurrentProductionPlus", "", "", screen.getXResolution() - 70, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
			screen.setButtonGFC("CurrentProductionMinus", "", "", screen.getXResolution() - 45, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		
		screen.setLabel("CurrentProductionText", "Background", "<font=3b>" + sText + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution() * 3/4, iY, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		iY += 30
		iWidth = screen.getXResolution()/2 - 40
		iHeight = (screen.getYResolution() - 40 - iY) /24 * 24 + 2
		iColumns = 3
		screen.addTableControlGFC("WBCityProduction", iColumns, screen.getXResolution()/2 + 20, iY, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		for i in xrange(iColumns):
			screen.setTableColumnHeader("WBCityProduction", i, "", iWidth/iColumns)
		iMaxRow = -1
		iRow = 0
		for i in xrange(gc.getNumUnitInfos()):
			if pCity.canTrain(i, True, False):
				if iRow > iMaxRow:
					screen.appendTableRow("WBCityProduction")
					iMaxRow = iRow
				ItemInfo = gc.getUnitInfo(i)
				sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
				if pCity.getProductionUnit() == i:
					sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
				screen.setTableText("WBCityProduction", 0, iRow, "<font=3>" + sColor + ItemInfo.getDescription() + "</font></color>", ItemInfo.getButton(), WidgetTypes.WIDGET_PYTHON, 8202, i, CvUtil.FONT_LEFT_JUSTIFY)
				iRow += 1
		iRow = 0
		for i in xrange(gc.getNumBuildingInfos()):
			bEligible = False
			if pCity.canConstruct(i, True, False, False):
				bEligible = True
			if not bEligible:
				for j in xrange(pCity.getOrderQueueLength()):
					iOrderData = pCity.getOrderFromQueue(j)
					if iOrderData.eOrderType == OrderTypes.ORDER_CONSTRUCT and iOrderData.iData1 == i:
						bEligible = True
			if bEligible:
				if iRow > iMaxRow:
					screen.appendTableRow("WBCityProduction")
					iMaxRow = iRow
				ItemInfo = gc.getBuildingInfo(i)
				sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
				if pCity.getProductionBuilding() == i:
					sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
				screen.setTableText("WBCityProduction", 1, iRow, "<font=3>" + sColor + ItemInfo.getDescription() + "</font></color>", ItemInfo.getButton(), WidgetTypes.WIDGET_HELP_BUILDING, i, -1, CvUtil.FONT_LEFT_JUSTIFY)
				iRow += 1
		sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		if pCity.isProduction():
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		screen.setTableText("WBCityProduction", 2, 0, "<font=3>" + sColor + CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ()) + "</font></color>", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_CANCEL").getPath(), WidgetTypes.WIDGET_PYTHON, 7878, -1, CvUtil.FONT_LEFT_JUSTIFY)
		iRow = 1
		for i in xrange(gc.getNumProjectInfos()):
			bEligible = False
			if pCity.canCreate(i, True, False):
				bEligible = True
			if not bEligible:
				for j in xrange(pCity.getOrderQueueLength()):
					iOrderData = pCity.getOrderFromQueue(j)
					if iOrderData.eOrderType == OrderTypes.ORDER_CREATE and iOrderData.iData1 == i:
						bEligible = True
			if bEligible:
				if iRow > iMaxRow:
					screen.appendTableRow("WBCityProduction")
					iMaxRow = iRow
				ItemInfo = gc.getProjectInfo(i)
				sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
				if pCity.getProductionProject() == i:
					sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
				screen.setTableText("WBCityProduction", 2, iRow, "<font=3>" + sColor + ItemInfo.getDescription() + "</font></color>", ItemInfo.getButton(), WidgetTypes.WIDGET_PYTHON, 6785, i, CvUtil.FONT_LEFT_JUSTIFY)
				iRow += 1

		for i in xrange(gc.getNumProcessInfos()):
			if pCity.canMaintain(i, True):
				if iRow > iMaxRow:
					screen.appendTableRow("WBCityProduction")
					iMaxRow = iRow
				ItemInfo = gc.getProcessInfo(i)
				sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
				if pCity.getProductionProcess() == i:
					sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
				screen.setTableText("WBCityProduction", 2, iRow, "<font=3>" + sColor + ItemInfo.getDescription() + "</font></color>", ItemInfo.getButton(), WidgetTypes.WIDGET_PYTHON, 6787, i, CvUtil.FONT_LEFT_JUSTIFY)
				iRow += 1

	def handleInput (self, inputClass):
		screen = CyGInterfaceScreen( "WBCityEditScreen", CvScreenEnums.WB_CITYEDIT)
		global iChange

		if inputClass.getFunctionName() == "ChangeBy":
			iChange = screen.getPullDownData("ChangeBy", screen.getSelectedPullDownID("ChangeBy"))
		
		elif inputClass.getFunctionName() == "CurrentPage":
			iIndex = screen.getPullDownData("CurrentPage", screen.getSelectedPullDownID("CurrentPage"))
			if iIndex == 1:
				WBCityDataScreen.WBCityDataScreen().interfaceScreen(pCity)
			elif iIndex == 2:
				WBBuildingScreen.WBBuildingScreen().interfaceScreen(pCity)
			elif iIndex == 3:
				WBPlayerScreen.WBPlayerScreen().interfaceScreen(iPlayer)
			elif iIndex == 4:
				WBTeamScreen.WBTeamScreen().interfaceScreen(pCity.getTeam())
			elif iIndex == 5:
				WBPlayerUnits.WBPlayerUnits().interfaceScreen(iPlayer)
			elif iIndex == 6:
				WBPlotScreen.WBPlotScreen().interfaceScreen(pCity.plot())
			elif iIndex == 7:
				WBEventScreen.WBEventScreen().interfaceScreen(pCity.plot())
			elif iIndex == 8:
				WBReligionScreen.WBReligionScreen().interfaceScreen(iPlayer)
			elif iIndex == 9:
				WBCorporationScreen.WBCorporationScreen().interfaceScreen(iPlayer)
			elif iIndex == 11:
				WBInfoScreen.WBInfoScreen().interfaceScreen(iPlayer)

		elif inputClass.getFunctionName() == "CurrentCity":
			self.interfaceScreen(gc.getPlayer(iPlayer).getCity(inputClass.getData2()))

		elif inputClass.getFunctionName() == "CityName":
			popup = Popup.PyPopup(CvUtil.EventEditCityName, EventContextTypes.EVENTCONTEXT_ALL)
			popup.setUserData((pCity.getID(), True, iPlayer))
			popup.setHeaderString(CyTranslator().getText("TXT_KEY_NAME_CITY", ()))
			popup.setBodyString(CyTranslator().getText("TXT_KEY_SETTLE_NEW_CITY_NAME", ()))
			popup.createEditBox(pCity.getName())
			popup.setEditBoxMaxCharCount( 15 )
			popup.launch()

		elif inputClass.getFunctionName() == "CityOwner":
			iIndex = screen.getSelectedPullDownID("CityOwner")
			pPlot = pCity.plot()
			gc.getPlayer(screen.getPullDownData("CityOwner", iIndex)).acquireCity(pCity, False, True)
			self.interfaceScreen(pPlot.getPlotCity())

		elif inputClass.getFunctionName().find("BaseYield") > -1:
			iYield = YieldTypes(inputClass.getData2())
			if inputClass.getData1() == 1030:
				pCity.changeBaseYieldRate(iYield, iChange)
			elif inputClass.getData1() == 1031:
				pCity.changeBaseYieldRate(iYield, - min(iChange, pCity.getBaseYieldRate(iYield)))
			self.placeStats()

		elif inputClass.getFunctionName().find("CityPopulation") > -1:
			if inputClass.getData1() == 1030:
				pCity.changePopulation(iChange)
			elif inputClass.getData1() == 1031:
				pCity.changePopulation(- min(iChange, pCity.getPopulation()))
			self.placeStats()

		elif inputClass.getFunctionName().find("CityFood") > -1:
			if inputClass.getData1() == 1030:
				pCity.changeFood(min(iChange, pCity.growthThreshold() - pCity.getFood()))
			elif inputClass.getData1() == 1031:
				pCity.changeFood(- min(iChange, pCity.getFood()))
			self.placeStats()

		elif inputClass.getFunctionName().find("CityDefense") > -1:
			if inputClass.getData1() == 1030:
				pCity.changeDefenseDamage(min(iChange, gc.getMAX_CITY_DEFENSE_DAMAGE() - pCity.getDefenseDamage()))
			elif inputClass.getData1() == 1031:
				pCity.changeDefenseDamage(- min(iChange, pCity.getDefenseDamage()))
			self.placeStats()

		elif inputClass.getFunctionName().find("CityTradeRoute") > -1:
			if inputClass.getData1() == 1030:
				pCity.changeExtraTradeRoutes(min(iChange, gc.getDefineINT("MAX_TRADE_ROUTES") - pCity.getTradeRoutes()))
			elif inputClass.getData1() == 1031:
				pCity.changeExtraTradeRoutes(- min(iChange, pCity.getTradeRoutes()))
			self.placeStats()

		elif inputClass.getFunctionName().find("CityChangeCulture") > -1:
			if inputClass.getData1() == 1030:
				pCity.changeCulture(iPlayer, iChange, True)
			elif inputClass.getData1() == 1031:
				pCity.changeCulture(iPlayer, - min(iChange, pCity.getCulture(iPlayer)), True)
			self.placeStats()

		elif inputClass.getFunctionName() == ("CityCultureLevel"):
			iIndex = screen.getSelectedPullDownID("CityCultureLevel")
			if iIndex == 0:
				pCity.setOccupationTimer(max(1, pCity.getOccupationTimer()))
			else:
				pCity.setOccupationTimer(0)
				pCity.setCulture(iPlayer, gc.getCultureLevelInfo(iIndex).getSpeedThreshold(CyGame().getGameSpeedType()), True)
			self.placeStats()

#Magister Start
		elif inputClass.getFunctionName() == ("CivilizationType"):
			pCity.setCivilizationType(screen.getSelectedPullDownID("CivilizationType"))
			self.placeStats()
#Magister Stop

		elif inputClass.getFunctionName().find("CityChangeHappy") > -1:
			if inputClass.getData1() == 1030:
				pCity.changeExtraHappiness(iChange)
			elif inputClass.getData1() == 1031:
				pCity.changeExtraHappiness(- iChange)
			self.placeStats()

		elif inputClass.getFunctionName().find("CityChangeHealth") > -1:
			if inputClass.getData1() == 1030:
				pCity.changeExtraHealth(iChange)
			elif inputClass.getData1() == 1031:
				pCity.changeExtraHealth(- iChange)
			self.placeStats()

		elif inputClass.getFunctionName().find("CityOccupationTurn") > -1:
			if inputClass.getData1() == 1030:
				pCity.changeOccupationTimer(iChange)
			elif inputClass.getData1() == 1031:
				pCity.changeOccupationTimer(- min(iChange, pCity.getOccupationTimer()))
			self.placeStats()

		elif inputClass.getFunctionName().find("CityDraftAnger") > -1:
			if inputClass.getData1() == 1030:
				pCity.changeConscriptAngerTimer(iChange)
			elif inputClass.getData1() == 1031:
				pCity.changeConscriptAngerTimer(- min(iChange, pCity.getConscriptAngerTimer()))
			self.placeStats()

		elif inputClass.getFunctionName().find("CityHurryAnger") > -1:
			if inputClass.getData1() == 1030:
				pCity.changeHurryAngerTimer(iChange)
			elif inputClass.getData1() == 1031:
				pCity.changeHurryAngerTimer(- min(iChange, pCity.getHurryAngerTimer()))
			self.placeStats()

		elif inputClass.getFunctionName().find("CityDefyResolution") > -1:
			if inputClass.getData1() == 1030:
				pCity.changeDefyResolutionAngerTimer(iChange)
			elif inputClass.getData1() == 1031:
				pCity.changeDefyResolutionAngerTimer(- min(iChange, pCity.getDefyResolutionAngerTimer()))
			self.placeStats()

		elif inputClass.getFunctionName().find("CityEspionageHappy") > -1:
			if inputClass.getData1() == 1030:
				pCity.changeEspionageHappinessCounter(iChange)
			elif inputClass.getData1() == 1031:
				pCity.changeEspionageHappinessCounter(- min(iChange, pCity.getEspionageHappinessCounter()))
			self.placeStats()

		elif inputClass.getFunctionName().find("CityEspionageHealth") > -1:
			if inputClass.getData1() == 1030:
				pCity.changeEspionageHealthCounter(iChange)
			elif inputClass.getData1() == 1031:
				pCity.changeEspionageHealthCounter(- min(iChange, pCity.getEspionageHealthCounter()))
			self.placeStats()

		elif inputClass.getFunctionName().find("CityTemporaryHappy") > -1:
			if inputClass.getData1() == 1030:
				pCity.changeHappinessTimer(iChange)
			elif inputClass.getData1() == 1031:
				pCity.changeHappinessTimer(- min(iChange, pCity.getHappinessTimer()))
			self.placeStats()

#Magister Start
		elif inputClass.getFunctionName().find("CityRevolutionIndex") > -1:
			if inputClass.getData1() == 1030:
				pCity.setRevolutionIndex(pCity.getRevolutionIndex() + iChange)
			elif inputClass.getData1() == 1031:
				pCity.setRevolutionIndex(pCity.getRevolutionIndex() - iChange)
			self.placeStats()
#Magister Stop

		elif inputClass.getFunctionName() == "WBCityProduction":
			self.handlePlatyChooseProduction(inputClass)
			self.placeProduction()

		elif inputClass.getFunctionName().find("CurrentProduction") > -1:
			if inputClass.getData1() == 1030:
				pCity.changeProduction(min(iChange, pCity.getProductionNeeded() - pCity.getProduction()))
			elif inputClass.getData1() == 1031:
				pCity.changeProduction(- min(iChange, pCity.getProduction()))
			self.placeProduction()

		elif inputClass.getFunctionName().find("CityEditScriptData") > -1:
			popup = Popup.PyPopup(2222, EventContextTypes.EVENTCONTEXT_ALL)
			popup.setHeaderString(CyTranslator().getText("TXT_KEY_WB_SCRIPT", ()))
			popup.setUserData((pCity.getOwner(), pCity.getID()))
			popup.createEditBox(pCity.getScriptData())
			popup.launch()
			return

		return 1

	def handlePlatyChooseProduction(self, inputClass):
		if inputClass.getButtonType() == WidgetTypes.WIDGET_HELP_BUILDING:
			for j in xrange(pCity.getOrderQueueLength()):
				iOrderData = pCity.getOrderFromQueue(j)
				if iOrderData.eOrderType == OrderTypes.ORDER_CONSTRUCT and iOrderData.iData1 == inputClass.getData1():
					pCity.popOrder(j, False, False)
					break
			pCity.pushOrder(OrderTypes.ORDER_CONSTRUCT, inputClass.getData1() , -1, False, False, False, True)
		elif inputClass.getData1() == 8202:
			for j in xrange(pCity.getOrderQueueLength()):
				iOrderData = pCity.getOrderFromQueue(j)
				if iOrderData.eOrderType == OrderTypes.ORDER_TRAIN and iOrderData.iData1 == inputClass.getData2():
					pCity.popOrder(j, False, False)
					break
			pCity.pushOrder(OrderTypes.ORDER_TRAIN, inputClass.getData2() , -1, False, False, False, True)
		elif inputClass.getData1() == 6785:
			for j in xrange(pCity.getOrderQueueLength()):
				iOrderData = pCity.getOrderFromQueue(j)
				if iOrderData.eOrderType == OrderTypes.ORDER_CREATE and iOrderData.iData1 == inputClass.getData2():
					pCity.popOrder(j, False, False)
					break
			pCity.pushOrder(OrderTypes.ORDER_CREATE, inputClass.getData2() , -1, False, False, False, True)
		elif inputClass.getData1() == 6787:
			for j in xrange(pCity.getOrderQueueLength()):
				iOrderData = pCity.getOrderFromQueue(j)
				if iOrderData.eOrderType == OrderTypes.ORDER_MAINTAIN and iOrderData.iData1 == inputClass.getData2():
					pCity.popOrder(j, False, False)
					break
			pCity.pushOrder(OrderTypes.ORDER_MAINTAIN, inputClass.getData2() , -1, False, False, False, True)
		else:
			pCity.clearOrderQueue()

	def update(self, fDelta):
		self.placeMap()
		return 1