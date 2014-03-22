from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums
import WBProjectScreen
import WBTechScreen
import WBTeamScreen
import WBPlayerUnits
import Popup
gc = CyGlobalContext()
iChange = 1

class WBPlayerScreen:

	def __init__(self, main):
		self.top = main

		self.iAlignment_Y = 30#magister
		self.iTrait_Y = 110#magister
		self.iReligion_Y = 140#magister

		self.iIconSize = 64
		self.iResearch_Y = self.iReligion_Y + self.iIconSize +40#magister

	def interfaceScreen(self, iPlayerX):
		screen = CyGInterfaceScreen( "WBPlayerScreen", CvScreenEnums.WB_PLAYER)
		global iPlayer
		global pPlayer
		global iTeam
		global pTeam
		iPlayer = iPlayerX
		pPlayer = gc.getPlayer(iPlayer)
		iTeam = pPlayer.getTeam()
		pTeam = gc.getTeam(iTeam)
		
		screen.setRenderInterfaceOnly(True)
		screen.addPanel( "MainBG", u"", u"", True, False, -10, -10, screen.getXResolution() + 20, screen.getYResolution() + 20, PanelStyles.PANEL_STYLE_MAIN )
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)

		screen.setLabel("ReligionsHeader", "Background", "<font=3b>" + CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_RELIGION",()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution() * 7/8, self.iReligion_Y - 30, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

#magister
		screen.setLabel("AlignmentsHeader", "Background", "<font=3b>" + CyTranslator().getText("TXT_KEY_ALIGNMENT_TAG",()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution() * 7/8, self.iAlignment_Y - 30, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setLabel("TraitsHeader", "Background", "<font=3b>" + CyTranslator().getText("TXT_KEY_PEDIA_TRAITS",()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution() /2, self.iTrait_Y-30, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
#magister

		screen.setText("PlayerExit", "Background", "<font=4>" + CyTranslator().getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 30, screen.getYResolution() - 42, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )

		screen.addDropDownBoxGFC("CurrentPage", 20, screen.getYResolution() - 42, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_HELP4", ()), 0, 0, True)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_TEAM_DATA", ()), 1, 1, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_PROJECT", ()), 2, 2, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_TECH", ()), 3, 3, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_UNIT", ()) + " + " + CyTranslator().getText("TXT_KEY_CONCEPT_CITIES", ()), 4, 4, False)

		iY = 80
		screen.addDropDownBoxGFC("CurrentPlayer", 20, iY, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		for i in xrange(gc.getMAX_PLAYERS()):
			pPlayerX = gc.getPlayer(i)
			if pPlayerX.isEverAlive():
				sText = pPlayerX.getName()
				if not pPlayerX.isAlive():
					sText = "*" + sText
				screen.addPullDownString("CurrentPlayer", sText, i, i, i == iPlayer)

		iY += 30
		screen.addDropDownBoxGFC("CurrentEra", 20, iY, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		for i in xrange(gc.getNumEraInfos()):
			screen.addPullDownString("CurrentEra", CyTranslator().getText("TXT_KEY_WB_ERA",(gc.getEraInfo(i).getDescription(),)), i, i, i == pPlayer.getCurrentEra())

		iY += 30
		screen.addDropDownBoxGFC("ChangeBy", 20, iY, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		i = 1
		while i < 1000001:
			screen.addPullDownString("ChangeBy", CyTranslator().getText("TXT_KEY_WB_CHANGE_BY",(i,)), i, i, iChange == i)
			if str(i)[0] == "1":
				i *= 5
			else:
				i *= 2
#Magister
		global lTraits
		lTraits = []
		for i in xrange(gc.getNumTraitInfos()):
			ItemInfo = gc.getTraitInfo(i)
			lTraits.append([ItemInfo.getDescription(), i])
		lTraits.sort()
#Magister
		global lReligions

		lReligions = []
		for i in xrange(gc.getNumReligionInfos()):
			ItemInfo = gc.getReligionInfo(i)
			lReligions.append([ItemInfo.getDescription() + " (" + str(pPlayer.getHasReligionCount(i)) + ")", i])
##		lReligions.sort()#MagisterModmod has the religions listed in the XML in the order I prefer


#magister
		self.placeAlignment()
		self.placeTraits()
#magister
		self.placeStats()
		self.placeCivics()
		self.placeReligions()
		self.placeResearch()
		self.placeScript()

	def placeStats(self):
		screen = CyGInterfaceScreen( "WBPlayerScreen", CvScreenEnums.WB_PLAYER)
		iLeader = pPlayer.getLeaderType()
		iCiv = pPlayer.getCivilizationType()
##		screen.addDDSGFC("LeaderPic", gc.getLeaderHeadInfo(iLeader).getButton(), screen.getXResolution() * 3/8 - self.iIconSize/2, 80, self.iIconSize, self.iIconSize, WidgetTypes.WIDGET_PYTHON, 7876, iLeader)
##		screen.addDDSGFC("CivPic", gc.getCivilizationInfo(iCiv).getButton(), screen.getXResolution() * 5/8 - self.iIconSize/2, 80, self.iIconSize, self.iIconSize, WidgetTypes.WIDGET_PYTHON, 7872, iCiv)

#magister
		screen.addDDSGFC("LeaderPic", gc.getLeaderHeadInfo(iLeader).getButton(), screen.getXResolution() /4 +20, 0, self.iIconSize, self.iIconSize, WidgetTypes.WIDGET_PYTHON, 7876, iLeader)
		screen.addDDSGFC("CivPic", gc.getCivilizationInfo(iCiv).getButton(), screen.getXResolution() * 3/4 -20 - self.iIconSize, 0, self.iIconSize, self.iIconSize, WidgetTypes.WIDGET_PYTHON, 7872, iCiv)

		sText = "<font=4b>" + CyTranslator().getText("[COLOR_BLACK]", ()) + CyTranslator().getText("TXT_KEY_WB_REVIVE",()).upper() + "</color></font>"
		if pPlayer.isAlive():
			sText = "<font=4b>" + CyTranslator().getText("[COLOR_BLACK]", ()) + CyTranslator().getText("TXT_KEY_WB_KILL",()).upper() + "</color></font>"
		screen.setButtonGFC("KillPlayer", sText, "", 20, 20, screen.getXResolution()/5, 30, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)

		if not pPlayer.isHuman():
			if not (gc.getGame().isGameMultiPlayer () or gc.getGame().isHotSeat() or gc.getGame().isNetworkMultiPlayer()):
				sText = "<font=4b>" + CyTranslator().getText("[COLOR_BLACK]", ()) + CyTranslator().getText("TXT_KEY_WB_SWITCH_PLAYER",()).upper() + "</color></font>"
				screen.setButtonGFC("SwitchPlayer", sText, "", 20, 50, screen.getXResolution()/5, 30, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)

#magister

		sText = "Player ID: " + str(pPlayer.getID()) + ", Team ID: " +str(pPlayer.getTeam())
		screen.setLabel("PlayerID", "Background", "<font=3b>" + sText + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 5, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		sText = pPlayer.getName()

		if pPlayer.isHuman():
			screen.setText("PlayerName", "Background", "<font=4b>" + sText + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 20, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			screen.setText("CivilizationName", "Background", "<font=3>" + CyTranslator().getText("TXT_KEY_MENU_CIV_DESC", ()) + "\n" + pPlayer.getCivilizationDescription(iPlayer) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 55, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			screen.setText("CivilizationNameShort", "Background", "<font=3>" +CyTranslator().getText("TXT_KEY_MENU_CIV_SHORT_DESC", ()) + "\n" + pPlayer.getCivilizationShortDescription(iPlayer) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()*1/3, 55, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			screen.setText("CivilizationAdj", "Background", "<font=3>" +CyTranslator().getText("TXT_KEY_MENU_CIV_ADJ", ()) +  "\n" + pPlayer.getCivilizationAdjective(iPlayer) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()*2/3, 55, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		else:
			screen.setLabel("PlayerName", "Background", "<font=4b>" + sText + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 20, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			screen.setLabel("CivilizationName", "Background", "<font=4b>" + pPlayer.getCivilizationDescription(0) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 50, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)


		iY = 180

		screen.setButtonGFC("PlayerGoldPlus", "", "", 20, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("PlayerGoldMinus", "", "", 45, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = u"%s %s%c" %(CyTranslator().getText("TXT_KEY_WB_GOLD", ()), self.top.addComma(pPlayer.getGold()), gc.getCommerceInfo(CommerceTypes.COMMERCE_GOLD).getChar())
		screen.setLabel("PlayerGoldText", "Background", "<font=3>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, 75, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 25
		screen.setButtonGFC("CombatXPPlus", "", "", 20, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CombatXPMinus", "", "", 45, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = u"%s: %d/%d" %(CyTranslator().getText("TXT_KEY_MISC_COMBAT_EXPERIENCE", ()), pPlayer.getCombatExperience(), pPlayer.greatPeopleThreshold(True))
		screen.setLabel("CombatXPText", "Background", "<font=3>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, 75, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 25
		screen.setButtonGFC("GoldenAgePlus", "", "", 20, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("GoldenAgeMinus", "", "", 45, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = u"%s: %d" %(CyTranslator().getText("TXT_KEY_CONCEPT_GOLDEN_AGE", ()), pPlayer.getGoldenAgeTurns())
		screen.setLabel("GoldenAgeText", "Background", "<font=3>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, 75, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 25
		screen.setButtonGFC("GPRequiredPlus", "", "", 20, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("GPRequiredMinus", "", "", 45, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = CyTranslator().getText("TXT_KEY_WB_GOLDEN_AGE_UNITS", (pPlayer.unitsRequiredForGoldenAge(),))
		screen.setLabel("GPRequiredText", "Background", "<font=3>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, 75, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 25
		screen.setButtonGFC("AnarchyPlus", "", "", 20, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("AnarchyMinus", "", "", 45, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = CyTranslator().getText("TXT_KEY_WB_ANARCHY", (pPlayer.getAnarchyTurns(),))
		screen.setLabel("AnarchyText", "Background", "<font=3>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, 75, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 25
		screen.setButtonGFC("CoastalTradePlus", "", "", 20, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CoastalTradeMinus", "", "", 45, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = CyTranslator().getText("TXT_KEY_WB_COASTAL_TRADE", (pPlayer.getCoastalTradeRoutes(),))
		screen.setLabel("CoastalTradeText", "Background", "<font=3>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, 75, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)


#Magister


		iY += 25
		screen.setButtonGFC("DisableProductionPlu", "", "", 20, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("DisableProductionMinus", "", "", 45, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = "<font=3>" + CyTranslator().getText("TXT_KEY_MESSAGE_DISABLE_PRODUCTION",(pPlayer.getDisableProduction(),)) + "</font>"
		screen.setLabel("DisableProductionText", "Background", "<font=3>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, 75, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 25
		screen.setButtonGFC("DisableResearchPlus", "", "", 20, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("DisableResearchMinus", "", "", 45, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = "<font=3>" + CyTranslator().getText("TXT_KEY_MESSAGE_DISABLE_RESEARCH",(pPlayer.getDisableResearch(),)) + "</font>"
		screen.setLabel("DisableResearchText", "Background", "<font=3>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, 75, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 25
		screen.setButtonGFC("DisableSpellcastingPlus", "", "", 20, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("DisableSpellcastingMinus", "", "", 45, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = "<font=3>" + CyTranslator().getText("TXT_KEY_MESSAGE_DISABLE_SPELLCASTING",(pPlayer.getDisableSpellcasting(),)) + "</font>"
		screen.setLabel("DisableSpellcastingText", "Background", "<font=3>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, 75, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)



#Magister
		iY += 25
		iWidth = screen.getXResolution() /4
		iHeight = min(6, CommerceTypes.NUM_COMMERCE_TYPES) * 24 + 2
		screen.addTableControlGFC("WBCommerceFlexible", 4, 20, iY, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_EMPTY)
		screen.setTableColumnHeader("WBCommerceFlexible", 0, "", 24)
		screen.setTableColumnHeader("WBCommerceFlexible", 1, "", 24)
		screen.setTableColumnHeader("WBCommerceFlexible", 2, "", 83)
		screen.setTableColumnHeader("WBCommerceFlexible", 3, "", iWidth - 131)

		for i in xrange(CommerceTypes.NUM_COMMERCE_TYPES):
			screen.appendTableRow("WBCommerceFlexible")
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			if pPlayer.isCommerceFlexible(i):
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			screen.setTableText("WBCommerceFlexible", 0, i, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_PLUS").getPath(), WidgetTypes.WIDGET_PYTHON, 1030, i, CvUtil.FONT_LEFT_JUSTIFY)
			screen.setTableText("WBCommerceFlexible", 1, i, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_MINUS").getPath(), WidgetTypes.WIDGET_PYTHON, 1031, i, CvUtil.FONT_LEFT_JUSTIFY)
			sText = u"<font=3>%c: %d%%</font>" %(gc.getCommerceInfo(i).getChar(), pPlayer.getCommercePercent(i))
			screen.setTableText("WBCommerceFlexible", 2, i, sColor + sText + "</color>", "", WidgetTypes.WIDGET_PYTHON, 7881, i, CvUtil.FONT_LEFT_JUSTIFY)
			sText = "<font=3>" + CyTranslator().getText("TXT_KEY_MISC_POS_GOLD_PER_TURN", (pPlayer.getCommerceRate(CommerceTypes(i)),)) + "</font>"
			screen.setTableText("WBCommerceFlexible", 3, i, sColor + sText + "</color>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		global iCivics_Y
		iCivics_Y = iY + iHeight + 30

	def placeScript(self):
		screen = CyGInterfaceScreen( "WBPlayerScreen", CvScreenEnums.WB_PLAYER)
		iY = iCivics_Y - 120
		screen.setText("PlayerEditScriptData", "Background", "<font=3b>" + CyTranslator().getText("TXT_KEY_WB_SCRIPT_DATA", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, iY, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addPanel( "ScriptPanel", "", "", False, False, screen.getXResolution()/4 + 20, iY + 25, screen.getXResolution()/2 - 40, iCivics_Y - iY - 55, PanelStyles.PANEL_STYLE_IN)
		screen.addMultilineText("PlayerScriptDataText", pPlayer.getScriptData(), screen.getXResolution()/4 + 20, iY + 25, screen.getXResolution()/2 - 40, iCivics_Y - iY - 55, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

	def placeResearch(self):
		screen = CyGInterfaceScreen( "WBPlayerScreen", CvScreenEnums.WB_PLAYER)
		iWidth = screen.getXResolution()/2 - 40
		iMaxRow = (iCivics_Y - 122 - self.iResearch_Y) / 24
		iHeight = iMaxRow * 24 + 2
		nColumns = 2
		screen.addTableControlGFC("WBPlayerResearch", nColumns, screen.getXResolution() /4 + 20, self.iResearch_Y, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		for i in xrange(nColumns):
			screen.setTableColumnHeader("WBPlayerResearch", i, "", iWidth/nColumns)

		iCurrentTech = pPlayer.getCurrentResearch()
		iCount = 1
		iMaxRows = 0
		sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		if iCurrentTech > -1:
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		screen.appendTableRow("WBPlayerResearch")
		screen.setTableText("WBPlayerResearch", 0, 0, "<font=3>" + sColor + CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ()) + "</font></color>", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_CANCEL").getPath(), WidgetTypes.WIDGET_PYTHON, 7871, -1, CvUtil.FONT_LEFT_JUSTIFY )
		for iTech in xrange(gc.getNumTechInfos()):
##			if pPlayer.canResearch(iTech, False):
#Magister
			iColumn = iCount % nColumns
			iRow = iCount /nColumns
			if iRow > iMaxRows:
				screen.appendTableRow("WBPlayerResearch")
				iMaxRows = iRow
			iCount += 1
			ItemInfo = gc.getTechInfo(iTech)

			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			if iCurrentTech == iTech:
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			elif pPlayer.isHasTech(iTech):
				sColor = CyTranslator().getText("[COLOR_HIGHLIGHT_TEXT]", ())
			elif pPlayer.canResearch(iTech, False):
				sColor = CyTranslator().getText("[COLOR_YELLOW]", ())
#Magister
			sText = u"%s%s</color> (%d/%d)%c" %(sColor, ItemInfo.getDescription(), pTeam.getResearchProgress(iTech), pTeam.getResearchCost(iTech), gc.getCommerceInfo(CommerceTypes.COMMERCE_RESEARCH).getChar())
			screen.setTableText("WBPlayerResearch", iColumn, iRow, "<font=3>" + sText + "</font>", ItemInfo.getButton(), WidgetTypes.WIDGET_PYTHON, 7871, iTech, CvUtil.FONT_LEFT_JUSTIFY)

		sText = CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ())
		if iCurrentTech > -1:
			iY = self.iReligion_Y + iHeight + 10
			sText = u"%s: %d/%d%c" %(gc.getTechInfo(iCurrentTech).getDescription(), pTeam.getResearchProgress(iCurrentTech), pTeam.getResearchCost(iCurrentTech), gc.getCommerceInfo(CommerceTypes.COMMERCE_RESEARCH).getChar())
			screen.setButtonGFC("CurrentResearchPlus", "", "", screen.getXResolution() * 3/4 - 70, self.iResearch_Y - 30, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
			screen.setButtonGFC("CurrentResearchMinus", "", "", screen.getXResolution() * 3/4 - 45, self.iResearch_Y - 30, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		screen.setLabel("CurrentProgressText", "Background", "<font=3b>" + sText + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, self.iResearch_Y - 30, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)


	def placeReligions(self):
		screen = CyGInterfaceScreen( "WBPlayerScreen", CvScreenEnums.WB_PLAYER)
		iWidth = screen.getXResolution()/4 - 40

		iMaxRow = (iCivics_Y - 120 - self.iReligion_Y) / 24
#		iHeight = min(iMaxRow, gc.getNumReligionInfos() + 1) * 24 + 2
		iHeight = min(iMaxRow, 7 + 1) * 24 + 2

		screen.addTableControlGFC("WBPlayerReligions", 1, screen.getXResolution() * 3/4 + 20, self.iReligion_Y, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		screen.setTableColumnHeader("WBPlayerReligions", 0, "", iWidth)

		sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		if pPlayer.getStateReligion() > -1:
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		screen.appendTableRow("WBPlayerReligions")
		screen.setTableText("WBPlayerReligions", 0, 0, "<font=3>" + sColor + CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ()) + "</font></color>", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_CANCEL").getPath(), WidgetTypes.WIDGET_HELP_RELIGION, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
		for item in lReligions:
			iRow = screen.appendTableRow("WBPlayerReligions")
			ItemInfo = gc.getReligionInfo(item[1])
			sChar = ItemInfo.getChar()
			if pPlayer.hasHolyCity(item[1]):
				sChar = ItemInfo.getHolyCityChar()
			sText = u"<font=4>%c <font=3>%s</font>" %(sChar, item[0])
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			if pPlayer.getStateReligion() == item[1]:
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			elif pPlayer.getHasReligionCount(item[1]) > 0:
				sColor = CyTranslator().getText("[COLOR_YELLOW]", ())
			screen.setTableText("WBPlayerReligions", 0, iRow, sColor + sText + "</color>", "", WidgetTypes.WIDGET_HELP_RELIGION, item[1], -1, CvUtil.FONT_LEFT_JUSTIFY)

		iY = self.iReligion_Y + iHeight + 10
		screen.setButtonGFC("StateReligionUnitPlus", "", "", screen.getXResolution() * 3/4 + 20, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("StateReligionUnitMinus", "", "", screen.getXResolution() * 3/4 + 45, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = "<font=3>" + CyTranslator().getText("TXT_KEY_WB_STATE_RELIGION_UNIT",(pPlayer.getStateReligionUnitProductionModifier(),)) + "</font>"
		screen.setLabel("StateReligionUnitText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, screen.getXResolution() * 3/4 + 75, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += 30
		screen.setButtonGFC("StateReligionBuildingPlus", "", "", screen.getXResolution() * 3/4 + 20, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("StateReligionBuildingMinus", "", "", screen.getXResolution() * 3/4 + 45, iY, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = "<font=3>" + CyTranslator().getText("TXT_KEY_WB_STATE_RELIGION_BUILDING",(pPlayer.getStateReligionBuildingProductionModifier(),)) + "</font>"
		screen.setLabel("StateReligionBuildingText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, screen.getXResolution() * 3/4 + 75, iY + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)


#Magister
#feats dont't have much to do with religion, but just below the state religion buildings is the place where there is the most spare room and it is easier to make sure it aligns if it is in the same function
		iFeat = FeatTypes.FEAT_GLOBAL_SPELL
		sText = CyTranslator().getText("TXT_KEY_WB_HAS_CAST_WORLD_SPELL", ())

		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if pPlayer.isFeatAccomplished(iFeat):
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		iY += 30
		screen.setText("WorldSpellFeatToggleText", "Background", "<font=3>" + sColor + sText + "</color></font>", CvUtil.FONT_LEFT_JUSTIFY, screen.getXResolution()*3/4 + 75, iY + 1, -0.1, FontTypes.TITLE_FONT,  WidgetTypes.WIDGET_GENERAL, -1, -1)

		iFeat = FeatTypes.FEAT_HEAL_UNIT_PER_TURN
		sText = CyTranslator().getText("TXT_KEY_SPELL_SIRONAS_TOUCH", ())

		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if pPlayer.isFeatAccomplished(iFeat):
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		iY += 30
		screen.setText("SironaFeatToggleText", "Background", "<font=3>" + sColor + sText + "</color></font>", CvUtil.FONT_LEFT_JUSTIFY, screen.getXResolution()*3/4 + 75, iY + 1, -0.1, FontTypes.TITLE_FONT,  WidgetTypes.WIDGET_GENERAL, -1, -1)


		iFeat = FeatTypes.FEAT_TRUST
		sText = CyTranslator().getText("TXT_KEY_SPELL_TRUST", ())

		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if pPlayer.isFeatAccomplished(iFeat):
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		iY += 30
		screen.setText("TrustFeatToggleText", "Background", "<font=3>" + sColor + sText + "</color></font>", CvUtil.FONT_LEFT_JUSTIFY, screen.getXResolution()*3/4 + 75, iY + 1, -0.1, FontTypes.TITLE_FONT,  WidgetTypes.WIDGET_GENERAL, -1, -1)

#Magister

	def placeCivics(self):
		screen = CyGInterfaceScreen( "WBPlayerScreen", CvScreenEnums.WB_PLAYER)
		screen.setLabel("CivicsHeader", "Background", "<font=3b>" + CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_CIVIC",()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution() /2, iCivics_Y - 30, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		iWidth = screen.getXResolution() - 40
		iHeight = (screen.getYResolution() - iCivics_Y - 40) /24 * 24 + 2
		iColumns = min(iWidth/160, gc.getNumCivicOptionInfos())
		screen.addTableControlGFC("WBPlayerCivics", iColumns, 20, iCivics_Y, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		for i in xrange(iColumns):
			screen.setTableColumnHeader("WBPlayerCivics", i, "", iWidth / iColumns)

		iMaxRow = -1
		iCurrentMaxRow = 0

		for iCivicOption in xrange(gc.getNumCivicOptionInfos()):
			iColumn = iCivicOption % iColumns
			iRow = iCurrentMaxRow
			if iRow > iMaxRow:
				screen.appendTableRow("WBPlayerCivics")
				iMaxRow = iRow
			sText = "<font=3>" + CyTranslator().getText("[COLOR_HIGHLIGHT_TEXT]", ()) + gc.getCivicOptionInfo(iCivicOption).getDescription() + "</font></color>"
			screen.setTableText("WBPlayerCivics", iColumn, iRow, sText, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)
			for item in xrange(gc.getNumCivicInfos()):
				ItemInfo = gc.getCivicInfo(item)
				if ItemInfo.getCivicOptionType() != iCivicOption: continue
				iRow += 1
				if iRow > iMaxRow:
					screen.appendTableRow("WBPlayerCivics")
					iMaxRow = iRow
				sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
				if pPlayer.isCivic(item):
					sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
				elif pPlayer.canDoCivics(item):
					sColor = CyTranslator().getText("[COLOR_YELLOW]", ())
				screen.setTableText("WBPlayerCivics", iColumn, iRow,"<font=3>" + sColor + ItemInfo.getDescription() + "</font></color>", ItemInfo.getButton(), WidgetTypes.WIDGET_PYTHON, 8205, item, CvUtil.FONT_LEFT_JUSTIFY)
			if iCivicOption % iColumns == iColumns -1 and iCivicOption < gc.getNumCivicOptionInfos() -1:
				screen.appendTableRow("WBPlayerCivics")
				iCurrentMaxRow = iMaxRow + 2

#magister
	def placeAlignment(self):
		screen = CyGInterfaceScreen( "WBPlayerScreen", CvScreenEnums.WB_PLAYER)
		iWidth = screen.getXResolution()/4 - 40
		iHeight = 3 * 24 + 2

		screen.addTableControlGFC("WBPlayerAlignments", 1, screen.getXResolution() * 3/4 + 20, self.iAlignment_Y, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		screen.setTableColumnHeader("WBPlayerAlignments", 0, "", iWidth)

		iAlignment = gc.getInfoTypeForString('ALIGNMENT_EVIL')
		sButton = "Art/interface/LeaderHeads/Random Evil.dds"
		sText = CyTranslator().getText("TXT_KEY_ALIGNMENT_EVIL", ())

		iRow = screen.appendTableRow("WBPlayerAlignments")
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if pPlayer.getAlignment() == iAlignment:
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		screen.setTableText("WBPlayerAlignments", 0, iRow,"<font=3>" + sColor + sText + "</font></color>", sButton, WidgetTypes.WIDGET_PYTHON, 1030, iAlignment, CvUtil.FONT_LEFT_JUSTIFY)

		iAlignment = gc.getInfoTypeForString('ALIGNMENT_NEUTRAL')
		sButton = "Art/interface/LeaderHeads/Random NEUTRAL.dds"
		sText = CyTranslator().getText("TXT_KEY_ALIGNMENT_NEUTRAL", ())

		iRow = screen.appendTableRow("WBPlayerAlignments")
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if pPlayer.getAlignment() == iAlignment:
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		screen.setTableText("WBPlayerAlignments", 0, iRow,"<font=3>" + sColor + sText + "</font></color>", sButton, WidgetTypes.WIDGET_PYTHON, 1030, iAlignment, CvUtil.FONT_LEFT_JUSTIFY)

		iAlignment = gc.getInfoTypeForString('ALIGNMENT_GOOD')
		sButton = "Art/interface/LeaderHeads/Random GOOD.dds"
		sText = CyTranslator().getText("TXT_KEY_ALIGNMENT_GOOD", ())

		iRow = screen.appendTableRow("WBPlayerAlignments")
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if pPlayer.getAlignment() == iAlignment:
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		screen.setTableText("WBPlayerAlignments", 0, iRow,"<font=3>" + sColor + sText + "</font></color>", sButton, WidgetTypes.WIDGET_PYTHON, 1030, iAlignment, CvUtil.FONT_LEFT_JUSTIFY)

	def placeTraits(self):
		screen = CyGInterfaceScreen( "WBPlayerScreen", CvScreenEnums.WB_PLAYER)
		iWidth = screen.getXResolution()/2 - 40
		iMaxRow = (self.iResearch_Y - 20 - self.iTrait_Y) / 24
		iHeight = iMaxRow * 24 + 2
		nColumns = 5
		screen.addTableControlGFC("WBPlayerTraits", nColumns, screen.getXResolution() /4 + 20, self.iTrait_Y, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		for i in xrange(nColumns):
			screen.setTableColumnHeader("WBPlayerTraits", i, "", iWidth/nColumns)
		iCount = 0
		iMaxRows = -1
		for item in lTraits:
			sText = item[0]
			iTrait = item[1]

			iColumn = iCount % nColumns
			iRow = iCount /nColumns
			if iRow > iMaxRows:
				screen.appendTableRow("WBPlayerTraits")
				iMaxRows = iRow
			iCount += 1

			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			if pPlayer.hasTrait(iTrait):
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			elif iTrait == gc.getCivilizationInfo(pPlayer.getCivilizationType()).getCivTrait():
				sColor = CyTranslator().getText("[COLOR_YELLOW]", ())
			elif gc.getLeaderHeadInfo(pPlayer.getLeaderType()).hasTrait(iTrait):#I thought it would be useful to show  what traits a leader lost and could regain if its avatar was ressureted
				sColor = CyTranslator().getText("[COLOR_YELLOW]", ())

			screen.setTableText("WBPlayerTraits", iColumn, iRow, sColor + sText + "</color>", "", WidgetTypes.WIDGET_PYTHON, 9000, iTrait, CvUtil.FONT_LEFT_JUSTIFY)
#magister

	def handleInput (self, inputClass):
		screen = CyGInterfaceScreen( "WBPlayerScreen", CvScreenEnums.WB_PLAYER)
		global iChange

		if inputClass.getFunctionName() == "ChangeBy":
			iIndex = screen.getSelectedPullDownID("ChangeBy")
			iChange = screen.getPullDownData("ChangeBy", iIndex)

		elif inputClass.getFunctionName() == "CurrentPage":
			iIndex = screen.getPullDownData("CurrentPage", screen.getSelectedPullDownID("CurrentPage"))
			if iIndex == 1:
				WBTeamScreen.WBTeamScreen(self.top).interfaceScreen(iTeam)
			elif iIndex == 2:
				WBProjectScreen.WBProjectScreen(self.top).interfaceScreen(pTeam)
			elif iIndex == 3:
				WBTechScreen.WBTechScreen(self.top).interfaceScreen(pTeam)
			elif iIndex == 4:
				WBPlayerUnits.WBPlayerUnits(self.top).interfaceScreen(iPlayer)

		elif inputClass.getFunctionName() == "CurrentPlayer":
			iIndex = screen.getPullDownData("CurrentPlayer", screen.getSelectedPullDownID("CurrentPlayer"))
			self.interfaceScreen(iIndex)

		elif inputClass.getFunctionName() == "CurrentEra":
			iIndex = screen.getSelectedPullDownID("CurrentEra")
			pPlayer.setCurrentEra(screen.getPullDownData("CurrentEra", iIndex))

		elif inputClass.getFunctionName().find("PlayerGold") > -1:
			if inputClass.getData1() == 1030:
				pPlayer.changeGold(iChange)
			elif inputClass.getData1() == 1031:
				pPlayer.changeGold(- min(iChange, pPlayer.getGold()))
			self.placeStats()

		elif inputClass.getFunctionName().find("CombatXP") > -1:
			if inputClass.getData1() == 1030:
				pPlayer.changeCombatExperience(iChange)
			elif inputClass.getData1() == 1031:
				pPlayer.changeCombatExperience(- min(iChange, pPlayer.getCombatExperience()))
			self.placeStats()

		elif inputClass.getFunctionName().find("GoldenAge") > -1:
			if inputClass.getData1() == 1030:
				pPlayer.changeGoldenAgeTurns(iChange)
			elif inputClass.getData1() == 1031:
				pPlayer.changeGoldenAgeTurns(- min(iChange, pPlayer.getGoldenAgeTurns()))
			self.placeStats()

		elif inputClass.getFunctionName().find("GPRequired") > -1:
			if inputClass.getData1() == 1030:
				pPlayer.changeNumUnitGoldenAges(iChange)
			elif inputClass.getData1() == 1031:
				pPlayer.changeNumUnitGoldenAges(- min(iChange, pPlayer.unitsRequiredForGoldenAge() - 1))
			self.placeStats()

		elif inputClass.getFunctionName().find("Anarchy") > -1:
			if inputClass.getData1() == 1030:
				pPlayer.changeAnarchyTurns(iChange)
			elif inputClass.getData1() == 1031:
				pPlayer.changeAnarchyTurns(- min(iChange, pPlayer.getAnarchyTurns()))
			self.placeStats()

		elif inputClass.getFunctionName().find("CoastalTrade") > -1:
			if inputClass.getData1() == 1030:
				pPlayer.changeCoastalTradeRoutes(iChange)
			elif inputClass.getData1() == 1031:
				pPlayer.changeCoastalTradeRoutes(- min(iChange, pPlayer.getCoastalTradeRoutes()))
			self.placeStats()

		elif inputClass.getFunctionName() == "WBCommerceFlexible":
			iCommerce = CommerceTypes(inputClass.getData2())
			if inputClass.getData1() == 7881:
				if pPlayer.isCommerceFlexible(iCommerce):
					pTeam.changeCommerceFlexibleCount(iCommerce, - pTeam.getCommerceFlexibleCount(iCommerce))
				else:
					pTeam.changeCommerceFlexibleCount(iCommerce, 1)
			elif inputClass.getData1() == 1030:
				if pPlayer.isCommerceFlexible(iCommerce):
					pPlayer.changeCommercePercent(iCommerce, iChange)
			elif inputClass.getData1() == 1031:
				if pPlayer.isCommerceFlexible(iCommerce):
					pPlayer.changeCommercePercent(iCommerce, - min(iChange, pPlayer.getCommercePercent(iCommerce)))
			self.placeStats()

		elif inputClass.getFunctionName() == "WBPlayerResearch":
			iTech = inputClass.getData2()
			if iTech == -1:
				pPlayer.clearResearchQueue()
			else:
				pPlayer.pushResearch(iTech, True)
			self.interfaceScreen(iPlayer)

		elif inputClass.getFunctionName().find("CurrentResearch") > -1:
			iTech = pPlayer.getCurrentResearch()
			if inputClass.getData1() == 1030:
				pTeam.changeResearchProgress(pPlayer.getCurrentResearch(), iChange, iPlayer)
			elif inputClass.getData1() == 1031:
				pTeam.changeResearchProgress(pPlayer.getCurrentResearch(), - min(iChange, pTeam.getResearchProgress(iTech)), iPlayer)
			self.placeResearch()

		elif inputClass.getFunctionName() == "WBPlayerReligions":
			iReligion = inputClass.getData1()
##			if iReligion == -1 or pPlayer.getHasReligionCount(iReligion) > 0:#Magister: I like being able to set a player to a state religion not found in any cities, even before the player has cities
			pPlayer.setLastStateReligion(inputClass.getData1())
			self.placeReligions()

		elif inputClass.getFunctionName().find("StateReligionUnit") > -1:
			if inputClass.getData1() == 1030:
				pPlayer.changeStateReligionUnitProductionModifier(iChange)
			elif inputClass.getData1() == 1031:
				pPlayer.changeStateReligionUnitProductionModifier(- min(iChange, pPlayer.getStateReligionUnitProductionModifier()))
			self.placeReligions()

		elif inputClass.getFunctionName().find("StateReligionBuilding") > -1:
			if inputClass.getData1() == 1030:
				pPlayer.changeStateReligionBuildingProductionModifier(iChange)
			elif inputClass.getData1() == 1031:
				pPlayer.changeStateReligionBuildingProductionModifier(- min(iChange, pPlayer.getStateReligionBuildingProductionModifier()))
			self.placeReligions()

		elif inputClass.getFunctionName() == "WBPlayerCivics":
			iCivic = inputClass.getData2()
			if pPlayer.canDoCivics(iCivic):
				pPlayer.setCivics(gc.getCivicInfo(iCivic).getCivicOptionType(), iCivic)
			self.interfaceScreen(iPlayer)

#Magister

		elif inputClass.getFunctionName().find("DisableProduction") > -1:
			if inputClass.getData1() == 1030:
				pPlayer.changeDisableProduction(iChange)
			elif inputClass.getData1() == 1031:
				pPlayer.changeDisableProduction(- min(iChange, pPlayer.getDisableProduction()))
			self.placeStats()

		elif inputClass.getFunctionName().find("DisableResearch") > -1:
			if inputClass.getData1() == 1030:
				pPlayer.changeDisableResearch(iChange)
			elif inputClass.getData1() == 1031:
				pPlayer.changeDisableResearch(- min(iChange, pPlayer.getDisableResearch()))
			self.placeStats()

		elif inputClass.getFunctionName().find("DisableSpellcasting") > -1:
			if inputClass.getData1() == 1030:
				pPlayer.changeDisableSpellcasting(iChange)
			elif inputClass.getData1() == 1031:
				pPlayer.changeDisableSpellcasting(- min(iChange, pPlayer.getDisableSpellcasting()))
			self.placeStats()

		elif inputClass.getFunctionName() == "PlayerName":
			popup = Popup.PyPopup(6666, EventContextTypes.EVENTCONTEXT_ALL)
			popup.setUserData((iPlayer, True))
			popup.setBodyString(CyTranslator().getText("TXT_KEY_NAME_CITY", ()))
			popup.createEditBox(pPlayer.getName())
			popup.launch()
			self.interfaceScreen(iPlayer)

		elif inputClass.getFunctionName() == "CivilizationName":
			popup = Popup.PyPopup(6777, EventContextTypes.EVENTCONTEXT_ALL)
			popup.setUserData((iPlayer, True))
			popup.setBodyString(CyTranslator().getText("TXT_KEY_MENU_CIV_DESC", ()))
			popup.createEditBox(pPlayer.getCivilizationDescription(iPlayer))
			popup.launch()
			self.interfaceScreen(iPlayer)

		elif inputClass.getFunctionName() == "CivilizationNameShort":
			popup = Popup.PyPopup(6888, EventContextTypes.EVENTCONTEXT_ALL)
			popup.setUserData((iPlayer, True))
			popup.setBodyString(CyTranslator().getText("TXT_KEY_MENU_CIV_SHORT_DESC", ()))
			popup.createEditBox(pPlayer.getCivilizationShortDescription(iPlayer))
			popup.launch()
			self.interfaceScreen(iPlayer)

		elif inputClass.getFunctionName() == "CivilizationAdj":
			popup = Popup.PyPopup(6999, EventContextTypes.EVENTCONTEXT_ALL)
			popup.setUserData((iPlayer, True))
			popup.setBodyString(CyTranslator().getText("TXT_KEY_MENU_CIV_ADJ", ()))
			popup.createEditBox(pPlayer.getCivilizationAdjective(iPlayer))
			popup.launch()
			self.interfaceScreen(iPlayer)

		elif inputClass.getFunctionName() == "WBPlayerAlignments":
			iAlignment = inputClass.getData2()
			pPlayer.setAlignment(iAlignment)
			self.interfaceScreen(iPlayer)

		elif inputClass.getFunctionName() == "WBPlayerTraits":
			iTrait = inputClass.getData2()
			pPlayer.setHasTrait(iTrait, not pPlayer.hasTrait(iTrait))
			self.interfaceScreen(iPlayer)

###I'm not sure why I cannot get the generalized form to work
##		elif inputClass.getFunctionName() == "FeatToggleText":
##			iFeat = inputClass.getData2()
##			pPlayer.setFeatAccomplished(iFeat, not pPlayer.isFeatAccomplished(iFeat))
##			self.placeReligions()

		elif inputClass.getFunctionName() == "WorldSpellFeatToggleText":
			iFeat = FeatTypes.FEAT_GLOBAL_SPELL
			pPlayer.setFeatAccomplished(iFeat, not pPlayer.isFeatAccomplished(iFeat))
			self.placeReligions()##

		elif inputClass.getFunctionName() == "SironaFeatToggleText":
			iFeat = FeatTypes.FEAT_HEAL_UNIT_PER_TURN
			pPlayer.setFeatAccomplished(iFeat, not pPlayer.isFeatAccomplished(iFeat))
			self.placeReligions()

		elif inputClass.getFunctionName() == "TrustFeatToggleText":
			iFeat = FeatTypes.FEAT_TRUST
			pPlayer.setFeatAccomplished(iFeat, not pPlayer.isFeatAccomplished(iFeat))
			self.placeReligions()

		elif inputClass.getFunctionName() == "SwitchPlayer":
			for iLoopPlayer in range(gc.getMAX_PLAYERS()):
				pLoopPlayer = gc.getPlayer(iLoopPlayer)
				if pLoopPlayer.isAlive():
					if pLoopPlayer.isHuman():
						CyGame().reassignPlayerAdvanced(iLoopPlayer, iPlayer, -1)
						break
			self.interfaceScreen(iPlayer)
#Magister

		elif inputClass.getFunctionName() == "KillPlayer":
			if pPlayer.isAlive():
				pPlayer.killCities()
				pPlayer.killUnits()
				pPlayer.setAlive(False)
			else:
				pPlayer.setAlive(True)
				screen.hideScreen()
				self.top.m_iCurrentPlayer = iPlayer
				self.top.normalPlayerTabModeCB()


			screen.hideScreen()

		elif inputClass.getFunctionName() == "PlayerEditScriptData":
			popup = Popup.PyPopup(1111, EventContextTypes.EVENTCONTEXT_ALL)
			popup.setHeaderString(CyTranslator().getText("TXT_KEY_WB_SCRIPT", ()))
			popup.setUserData((pPlayer.getID(),))
			popup.createEditBox(pPlayer.getScriptData())
			popup.launch()
			return
		return 1

	def update(self, fDelta):
		return 1