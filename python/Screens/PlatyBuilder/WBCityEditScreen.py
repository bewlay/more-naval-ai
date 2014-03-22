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
import Popup
gc = CyGlobalContext()
iChange = 1

class WBCityEditScreen:

	def __init__(self, main):
		self.top = main
		self.iTable_Y = 100
		self.bWonder = False
		self.iModifyBuilding = 0
		self.iYieldType = 0

	def interfaceScreen(self, pCityX):
		screen = CyGInterfaceScreen( "WBCityEditScreen", CvScreenEnums.WB_CITYEDIT)
		global pCity
		global iHeight
		global iModify_Y
		pCity = pCityX
		
		screen.setRenderInterfaceOnly(True)
		screen.addPanel( "MainBG", u"", u"", True, False, -10, -10, screen.getXResolution() + 20, screen.getYResolution() + 20, PanelStyles.PANEL_STYLE_MAIN )
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)
		
		screen.setText("WBCityEditExit", "Background", "<font=4>" + CyTranslator().getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 30, screen.getYResolution() - 42, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )
		sText = "<font=3b>%s, X: %d, Y: %d</font>" %(CyTranslator().getText("TXT_KEY_WB_LATITUDE",(pCity.plot().getLatitude(),)), pCity.getX(), pCity.getY())
		
		screen.addDropDownBoxGFC("CurrentPage", 20, screen.getYResolution() - 42, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_CITY_DATA", ()), 0, 0, True)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_CITY_DATA2", ()), 1, 1, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_BUILDING", ()), 2, 2, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_HELP4", ()), 3, 3, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_TEAM_DATA", ()), 4, 4, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_UNIT", ()) + " + " + CyTranslator().getText("TXT_KEY_CONCEPT_CITIES", ()), 5, 5, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_HELP19", ()), 6, 6, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_CONCEPT_EVENTS", ()), 7, 7, False)

		pPlot = pCity.plot()
		sText = u"<font=3b>%s ID: %d, %s: %d</font>" %(CyTranslator().getText("TXT_KEY_WB_CITY", ()), pCity.getID(), CyTranslator().getText("TXT_KEY_WB_AREA_ID", ()), pPlot.getArea())
		screen.setLabel("PlotScreenHeaderB", "Background", "<font=4b>" + sText + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 50, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		sText = "<font=3b>%s, X: %d, Y: %d</font>" %(CyTranslator().getText("TXT_KEY_WB_LATITUDE",(pPlot.getLatitude(),)), pPlot.getX(), pPlot.getY())
		screen.setLabel("PlotLocation", "Background", sText, CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 70, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		
		self.placeStats()
		self.placeProduction()
		self.sortBuildings()

		iNumColumns = YieldTypes.NUM_YIELD_TYPES + CommerceTypes.NUM_COMMERCE_TYPES
		screen.addTableControlGFC("YieldType", iNumColumns, screen.getXResolution() - 20 - 25 * iNumColumns, iModify_Y, 25 * iNumColumns, 25, False, False, 24, 24, TableStyles.TABLE_STYLE_EMPTY)
		screen.appendTableRow("YieldType")
		for i in xrange(YieldTypes.NUM_YIELD_TYPES):
			screen.setTableColumnHeader("YieldType", i, "", 24)
			sText = u"<font=4>%c</font>" %(gc.getYieldInfo(i).getChar())
			screen.setTableText("YieldType", i, 0, sText, "", WidgetTypes.WIDGET_PYTHON, 7880, i, CvUtil.FONT_LEFT_JUSTIFY)
		for i in xrange(CommerceTypes.NUM_COMMERCE_TYPES):
			screen.setTableColumnHeader("YieldType", YieldTypes.NUM_YIELD_TYPES + i, "", 24)
			sText = u"<font=4>%c</font>" %(gc.getCommerceInfo(i).getChar())
			screen.setTableText("YieldType", YieldTypes.NUM_YIELD_TYPES + i, 0, sText, "", WidgetTypes.WIDGET_PYTHON, 7881, i, CvUtil.FONT_LEFT_JUSTIFY)

		screen.addDropDownBoxGFC("BuildingType", 20, iModify_Y, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("BuildingType", CyTranslator().getText("TXT_KEY_CONCEPT_BUILDINGS", ()), 0, 0, not self.bWonder)
		screen.addPullDownString("BuildingType", CyTranslator().getText("TXT_KEY_CONCEPT_WONDERS", ()), 1, 1, self.bWonder)

	def sortBuildings(self):
		global lBuilding
		lBuilding = []
		for i in xrange(gc.getNumBuildingClassInfos()):
			if gc.getBuildingClassInfo(i).isGraphicalOnly(): continue
			if self.bWonder and not isLimitedWonderClass(i): continue
			if not self.bWonder and isLimitedWonderClass(i): continue
			iBuilding = gc.getCivilizationInfo(pCity.getCivilizationType()).getCivilizationBuildings(i)
			if iBuilding < 0:
				iBuilding = gc.getBuildingClassInfo(i).getDefaultBuildingIndex()
			if iBuilding < 0: continue
			lBuilding.append([gc.getBuildingInfo(iBuilding).getDescription(), iBuilding])
		lBuilding.sort()
		self.placeModify()

	def placeStats(self):
		screen = CyGInterfaceScreen( "WBCityEditScreen", CvScreenEnums.WB_CITYEDIT)
		screen.setText("CityName", "Background", "<font=4b>" + pCity.getName() + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 20, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_CITY_NAME, -1, -1)
		global iPlayer
		global pPlayer
		iPlayer = pCity.getOwner()
		pPlayer = gc.getPlayer(iPlayer)
		
		iY = self.iTable_Y - 30
		screen.addDropDownBoxGFC("CurrentCity", 20, iY, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		(loopCity, iter) = pPlayer.firstCity(False)
		while(loopCity):
			screen.addPullDownString("CurrentCity", loopCity.getName(), loopCity.getID(), loopCity.getID(), loopCity.getID() == pCity.getID())
			(loopCity, iter) = pPlayer.nextCity(iter, False)

		iY += 30
		screen.addDropDownBoxGFC("CityOwner", 20, iY, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		for i in xrange(gc.getMAX_PLAYERS()):
			pPlayerX = gc.getPlayer(i)
			if pPlayerX.isEverAlive():
				sText = pPlayerX.getName()
				if not pPlayerX.isAlive():
					sText = "*" + sText
				screen.addPullDownString("CityOwner", sText, i, i, i == iPlayer)

		screen.setButtonGFC("CityChangeHappyPlus", "", "", screen.getXResolution()/4 + 20, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityChangeHappyMinus", "", "", screen.getXResolution()/4 + 45, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = "<font=3>%s: %d%s, %d%s</font>" %(CyTranslator().getText("TXT_KEY_CONCEPT_HAPPINESS",()), pCity.happyLevel(), CyTranslator().getText("[ICON_HAPPY]",()), pCity.unhappyLevel(0), CyTranslator().getText("[ICON_UNHAPPY]",()))
		screen.setLabel("CityChangeHappyText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, screen.getXResolution()/4 + 75, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 30
		screen.addDropDownBoxGFC("ChangeBy", 20, iY, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		i = 1
		while i < 1000001:
			screen.addPullDownString("ChangeBy", CyTranslator().getText("TXT_KEY_WB_CHANGE_BY",(i,)), i, i, iChange == i)
			if str(i)[0] == "1":
				i *= 5
			else:
				i *= 2

		screen.setButtonGFC("CityChangeHealthPlus", "", "", screen.getXResolution()/4 + 20, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityChangeHealthMinus", "", "", screen.getXResolution()/4 + 45, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = "<font=3>%s: %d%s, %d%s</font>" %(CyTranslator().getText("TXT_KEY_CONCEPT_HEALTH",()), pCity.goodHealth(), CyTranslator().getText("[ICON_HEALTHY]",()), pCity.badHealth(False), CyTranslator().getText("[ICON_UNHEALTHY]",()))
		screen.setLabel("CityChangeHealthText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, screen.getXResolution()/4 + 75, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 30
		screen.setButtonGFC("CityOccupationTurnPlus", "", "", screen.getXResolution()/4 + 20, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityOccupationTurnMinus", "", "", screen.getXResolution()/4 + 45, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = "<font=3>" + CyTranslator().getText("TXT_KEY_CONCEPT_RESISTANCE",()) + ": " + str(pCity.getOccupationTimer()) + CyTranslator().getText("[ICON_OCCUPATION]", ()) + "</font>"
		screen.setLabel("CityOccupationTurnText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, screen.getXResolution()/4 + 75, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		for i in xrange(YieldTypes.NUM_YIELD_TYPES):
			iYield = pCity.getBaseYieldRate(YieldTypes(i))
			screen.setButtonGFC("BaseYieldPlus" + str(i), "", "", 20, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, i, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
			screen.setButtonGFC("BaseYieldMinus" + str(i), "", "", 45, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, i, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
			sText = CyTranslator().getText("TXT_KEY_WB_BASE_YIELD", (gc.getYieldInfo(i).getDescription(), iYield,))
			sText = u"%s%c" %(sText, gc.getYieldInfo(i).getChar())
			screen.setLabel("BaseYieldText" + str(i), "Background", "<font=3>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, 75, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			iY += 30

		iY -= 60
		screen.setButtonGFC("CityDraftAngerPlus", "", "", screen.getXResolution()/4 + 20, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityDraftAngerMinus", "", "", screen.getXResolution()/4 + 45, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = "<font=3>" + CyTranslator().getText("TXT_KEY_CONCEPT_DRAFT",()) + CyTranslator().getText(" [ICON_UNHAPPY]: ",()) + str(pCity.getConscriptAngerTimer()) + "</font>"
		screen.setLabel("CityDraftAngerText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, screen.getXResolution()/4 + 75, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 30
		screen.setButtonGFC("CityHurryAngerPlus", "", "", screen.getXResolution()/4 + 20, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityHurryAngerMinus", "", "", screen.getXResolution()/4 + 45, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = "<font=3>" + CyTranslator().getText("TXT_KEY_WB_HURRY_ANGER",(pCity.getHurryAngerTimer(),)) + "</font>"
		screen.setLabel("CityHurryAngerText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, screen.getXResolution()/4 + 75, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 30
		screen.setButtonGFC("CityFoodPlus", "", "", 20, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityFoodMinus", "", "", 45, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = u"<font=3>%s: %d/%d%c</font>" %(CyTranslator().getText("TXT_KEY_CONCEPT_FOOD",()), pCity.getFood(), pCity.growthThreshold(), gc.getYieldInfo(YieldTypes.YIELD_FOOD).getChar())
		screen.setLabel("CityFoodText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, 75, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		screen.setButtonGFC("CityDefyResolutionPlus", "", "", screen.getXResolution()/4 + 20, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityDefyResolutionMinus", "", "", screen.getXResolution()/4 + 45, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = "<font=3>" + CyTranslator().getText("TXT_KEY_WB_DEFY_RESOLUTION",(pCity.getDefyResolutionAngerTimer(),)) + "</font>"
		screen.setLabel("CityDefyResolutionText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, screen.getXResolution()/4 + 75, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 30
		screen.setButtonGFC("CityPopulationPlus", "", "", 20, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityPopulationMinus", "", "", 45, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = "<font=3>" + CyTranslator().getText("TXT_KEY_WB_POPULATION",()) + " " + str(pCity.getPopulation()) + CyTranslator().getText("[ICON_ANGRYPOP]", ()) + "</font>"
		screen.setLabel("CityPopulationText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, 75, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		screen.setButtonGFC("CityEspionageHappyPlus", "", "", screen.getXResolution()/4 + 20, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityEspionageHappyMinus", "", "", screen.getXResolution()/4 + 45, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = u"<font=3>%s %s: %d</font>" %(CyTranslator().getText("TXT_KEY_ESPIONAGE_CULTURE",()), CyTranslator().getText("[ICON_UNHAPPY]", ()), pCity.getEspionageHappinessCounter())
		screen.setLabel("CityEspionageHappyText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, screen.getXResolution()/4 + 75, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 30
		sText = "<font=3>" + CyTranslator().getText("TXT_KEY_WB_DEFENSE",(pCity.getDefenseModifier(False),)) + "</font>"
		screen.setLabel("CityDefenseValueText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, 75, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		screen.setButtonGFC("CityEspionageHealthPlus", "", "", screen.getXResolution()/4 + 20, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityEspionageHealthMinus", "", "", screen.getXResolution()/4 + 45, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = u"<font=3>%s %s: %d</font>" %(CyTranslator().getText("TXT_KEY_ESPIONAGE_CULTURE",()), CyTranslator().getText("[ICON_UNHEALTHY]", ()), pCity.getEspionageHealthCounter())
		screen.setLabel("CityEspionageHealthText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, screen.getXResolution()/4 + 75, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 30
		screen.setButtonGFC("CityDefensePlus", "", "", 20, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityDefenseMinus", "", "", 45, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = "<font=3>" + CyTranslator().getText("TXT_KEY_WB_DAMAGE",()) + ": " + str(pCity.getDefenseDamage()) + "</font>"
		screen.setLabel("CityDefenseDamageText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, 75, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		screen.setButtonGFC("CityTemporaryHappyPlus", "", "", screen.getXResolution()/4 + 20, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityTemporaryHappyMinus", "", "", screen.getXResolution()/4 + 45, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = "<font=3>" + CyTranslator().getText("TXT_KEY_WB_TEMP_HAPPY",(pCity.getHappinessTimer(),)) + "</font>"
		screen.setLabel("CityTemporaryHappyText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, screen.getXResolution()/4 + 75, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 30
		screen.setButtonGFC("CityTradeRoutePlus", "", "", 20, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityTradeRouteMinus", "", "", 45, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = u"<font=3>%s: %d%s</font>" %(CyTranslator().getText("TXT_KEY_CONCEPT_TRADE",()), pCity.getTradeRoutes(), CyTranslator().getText("[ICON_TRADE]",()))
		screen.setLabel("CityCTradeRouteText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, 75, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		screen.setText("CityEditScriptData", "Background", "<font=3b>" + CyTranslator().getText("TXT_KEY_WB_SCRIPT_DATA", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution() * 3/8, iY, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addPanel( "ScriptPanel", "", "", False, False, screen.getXResolution()/4 + 20, iY + 25, screen.getXResolution()/4 - 40, 60, PanelStyles.PANEL_STYLE_IN)
		screen.addMultilineText("CityScriptDataText", pCity.getScriptData(), screen.getXResolution()/4 + 20, iY + 25, screen.getXResolution()/4 - 40, 60, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

		iY += 30
		screen.setButtonGFC("CityChangeCulturePlus", "", "", 20, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CityChangeCultureMinus", "", "", 45, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = u"<font=3>%s %d/%d%c</font>" %(CyTranslator().getText("TXT_KEY_WB_CULTURE",()), pCity.getCulture(iPlayer), pCity.getCultureThreshold(), gc.getCommerceInfo(CommerceTypes.COMMERCE_CULTURE).getChar())
		screen.setLabel("CityChangeCultureText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, 75, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 30
		screen.addDropDownBoxGFC("CityCultureLevel", 20, iY, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		for i in xrange(gc.getNumCultureLevelInfos()):
			screen.addPullDownString("CityCultureLevel", gc.getCultureLevelInfo(i).getDescription(), i, i, pCity.getCultureLevel() == i)


##MagisterModmod
## Civ Type ##
		if pPlayer.hasTrait(gc.getInfoTypeForString('TRAIT_TOLERANT')):
			iY += 30
			screen.addDropDownBoxGFC("CivilizationType", 20, iY, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
			for i in range(gc.getNumCivilizationInfos()):
				screen.addPullDownString("CivilizationType", gc.getCivilizationInfo(i).getDescription(), i, i, pCity.getCivilizationType() == i)
##MagisterModmod
		global iModify_Y
		iModify_Y = iY + 40

	def placeProduction(self):
		screen = CyGInterfaceScreen( "WBCityEditScreen", CvScreenEnums.WB_CITYEDIT)
		sText = CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ())
		screen.hide("CurrentProductionMinus")
		screen.hide("CurrentProductionPlus")
		if pCity.isProductionProcess():
			sText = pCity.getProductionName()
		elif pCity.isProduction():
			sText = u"%s: %d/%d%c" %(pCity.getProductionName(), pCity.getProduction(), pCity.getProductionNeeded(), gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar())
			screen.setButtonGFC("CurrentProductionPlus", "", "", screen.getXResolution() - 70, self.iTable_Y - 30, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
			screen.setButtonGFC("CurrentProductionMinus", "", "", screen.getXResolution() - 45, self.iTable_Y - 30, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		
		screen.setLabel("CurrentProductionText", "Background", "<font=3b>" + sText + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution() * 3/4, self.iTable_Y - 30, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		iWidth = screen.getXResolution()/2 - 40
		iHeight = (iModify_Y - self.iTable_Y - 12) /24 * 24 + 2
		iColumns = 3
		screen.addTableControlGFC("WBCityProduction", iColumns, screen.getXResolution()/2 + 20, self.iTable_Y, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
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

	def placeModify(self):
		global iModify_Y
		screen = CyGInterfaceScreen( "WBCityEditScreen", CvScreenEnums.WB_CITYEDIT)
		screen.setButtonGFC("EditBuildingPlus", "", "", screen.getXResolution()/4 + 20, iModify_Y, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("EditBuildingMinus", "", "", screen.getXResolution()/4 + 45, iModify_Y, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		if self.iYieldType < YieldTypes.NUM_YIELD_TYPES:
			cYield = gc.getYieldInfo(self.iYieldType).getChar()
		else:
			cYield = gc.getCommerceInfo(self.iYieldType - YieldTypes.NUM_YIELD_TYPES).getChar()
		sText = u"<font=3>%s%c</font>" %(CyTranslator().getText("TXT_KEY_WB_MODIFY", (gc.getBuildingInfo(self.iModifyBuilding).getDescription(),)), cYield)
		screen.setLabel("ModifyText", "Background", "<font=3>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, screen.getXResolution()/4 + 75, iModify_Y + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iWidth = screen.getXResolution() - 40
		iY = iModify_Y + 30
		iHeight = (screen.getYResolution() - iY - 40) /24 * 24 + 2
		iColumns = 2 + YieldTypes.NUM_YIELD_TYPES + CommerceTypes.NUM_COMMERCE_TYPES
		screen.addTableControlGFC("WBModifyBuilding", iColumns, 20, iY, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		iColWidth = (iWidth - 8) / iColumns
		screen.setTableColumnHeader("WBModifyBuilding", 0, "", iColWidth * 2)
		for i in xrange(iColumns - 2):
			screen.setTableColumnHeader("WBModifyBuilding", i + 1, "", iColWidth)
		screen.setTableColumnHeader("WBModifyBuilding", iColumns - 1, "", 8)

		for item in lBuilding:
			ItemInfo = gc.getBuildingInfo(item[1])
			iBuildingClass = ItemInfo.getBuildingClassType()
			iRow = screen.appendTableRow("WBModifyBuilding")
			screen.setTableText("WBModifyBuilding", 0, iRow, "<font=3>" + item[0] + "</font>", ItemInfo.getButton(), WidgetTypes.WIDGET_HELP_BUILDING, item[1], -1, CvUtil.FONT_LEFT_JUSTIFY)
			for j in xrange(YieldTypes.NUM_YIELD_TYPES):
				sText = u"%d%c" %(pCity.getBuildingYieldChange(iBuildingClass, j), gc.getYieldInfo(j).getChar())
				screen.setTableInt("WBModifyBuilding", j + 1, iRow, "<font=3>" + sText + "</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY )
			for j in xrange(CommerceTypes.NUM_COMMERCE_TYPES):
				sText = u"%d%c" %(pCity.getBuildingCommerceChange(iBuildingClass, j), gc.getCommerceInfo(j).getChar())
				screen.setTableInt("WBModifyBuilding", j + 1 + YieldTypes.NUM_YIELD_TYPES, iRow, "<font=3>" + sText + "</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY )

	def handleInput (self, inputClass):
		screen = CyGInterfaceScreen( "WBCityEditScreen", CvScreenEnums.WB_CITYEDIT)
		global iChange

		if inputClass.getFunctionName() == "ChangeBy":
			iIndex = screen.getSelectedPullDownID("ChangeBy")
			iChange = screen.getPullDownData("ChangeBy", iIndex)

		elif inputClass.getFunctionName() == "BuildingType":
			self.bWonder = not self.bWonder
			self.sortBuildings()
		
		elif inputClass.getFunctionName() == "CurrentPage":
			iIndex = screen.getPullDownData("CurrentPage", screen.getSelectedPullDownID("CurrentPage"))
			if iIndex == 1:
				WBCityDataScreen.WBCityDataScreen(self.top).interfaceScreen(pCity)
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

		elif inputClass.getFunctionName() == "CurrentCity":
			iIndex = screen.getSelectedPullDownID("CurrentCity")
			self.interfaceScreen(pPlayer.getCity(iIndex))

		elif inputClass.getFunctionName() == "CityName":
			popup = Popup.PyPopup(CvUtil.EventEditCityName, EventContextTypes.EVENTCONTEXT_ALL)
			popup.setUserData((pCity.getID(), True, pCity.getOwner()))
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
				pCity.changeFood(iChange)
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
				pCity.changeExtraTradeRoutes(iChange)
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

#Magister
		elif inputClass.getFunctionName() == ("CivilizationType"):
			pCity.setCivilizationType(screen.getSelectedPullDownID("CivilizationType"))
			self.placeStats()

#Magister

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

		elif inputClass.getFunctionName() == "YieldType":
			if inputClass.getData1() == 7880:
				self.iYieldType = inputClass.getData2()
			elif inputClass.getData1() == 7881:
				self.iYieldType = inputClass.getData2() + YieldTypes.NUM_YIELD_TYPES
			self.placeModify()

		elif inputClass.getFunctionName().find("EditBuilding") > -1:
			if inputClass.getData1() == 1030:
				self.handlePlatyModifyBuildings(iChange)
			elif inputClass.getData1() == 1031:
				self.handlePlatyModifyBuildings(-iChange)
			self.placeModify()
		
		elif inputClass.getFunctionName() == "WBModifyBuilding":
			if inputClass.getButtonType() == WidgetTypes.WIDGET_HELP_BUILDING:
				self.iModifyBuilding = inputClass.getData1()
				self.placeModify()

		elif inputClass.getFunctionName() == "WBCityProduction":
			self.handlePlatyChooseProduction(inputClass)
			self.placeProduction()

		elif inputClass.getFunctionName().find("CurrentProduction") > -1:
			if inputClass.getData1() == 1030:
				pCity.changeProduction(iChange)
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

	def handlePlatyModifyBuildings(self, iChange):
		iClass = gc.getBuildingInfo(self.iModifyBuilding).getBuildingClassType()
		if self.iYieldType < YieldTypes.NUM_YIELD_TYPES:
			pCity.setBuildingYieldChange(iClass, self.iYieldType, pCity.getBuildingYieldChange(iClass, self.iYieldType) + iChange)
		else:
			iCommerce = self.iYieldType - YieldTypes.NUM_YIELD_TYPES
			pCity.setBuildingCommerceChange(iClass, iCommerce, pCity.getBuildingCommerceChange(iClass, iCommerce) + iChange)

	def update(self, fDelta):
		return 1