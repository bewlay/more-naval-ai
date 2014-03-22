from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums

import FontUtil#magister

gc = CyGlobalContext()
iChange = 1

class WBDiplomacyScreen:
	def __init__(self):
		self.iList = []
		self.bDiplomacyPage = False
		self.iPlayer = 0
		self.iTeam = 0
		self.bTowardsPlayer = False
		self.iMemory = 0

	def interfaceScreen(self, iPlayer):
		screen = CyGInterfaceScreen( "WBDiplomacyScreen", CvScreenEnums.WB_DIPLOMACY)
		self.iPlayer = iPlayer
		if not gc.getPlayer(iPlayer).isAlive():
			self.iPlayer = CyGame().getActivePlayer()
		self.iTeam = gc.getPlayer(self.iPlayer).getTeam()

		self.nTableWidth = screen.getXResolution() - 40
		self.nTableHeight = screen.getYResolution() - 120
		screen.setRenderInterfaceOnly(True)
		screen.addPanel( "MainBG", "", "", True, False, -10, -10, screen.getXResolution() + 20, screen.getYResolution() + 20, PanelStyles.PANEL_STYLE_MAIN )
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)
	
		screen.setText("DiplomacyExit", "Background", "<font=4b>" + CyTranslator().getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 25, screen.getYResolution() - 40, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )
		
		sButton = ButtonStyles.BUTTON_STYLE_ARROW_RIGHT
		sTarget = CyTranslator().getText("TXT_KEY_WB_CITY_ALL", ())
		if self.bTowardsPlayer:
			sButton = ButtonStyles.BUTTON_STYLE_ARROW_LEFT
			sTarget = gc.getPlayer(self.iPlayer).getName()
		screen.setButtonGFC("TowardsPlayer", CyTranslator().getText("TXT_KEY_WB_TOWARDS", (sTarget,)), "", 180, 50, screen.getXResolution()/5, 24, WidgetTypes.WIDGET_GENERAL, -1, -1, sButton)

		screen.addDropDownBoxGFC("CurrentPlayer", 20, 20, 160, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		self.iList = []
		for i in xrange(gc.getMAX_PLAYERS()):
			if gc.getPlayer(i).isAlive():
				screen.addPullDownString("CurrentPlayer", gc.getPlayer(i).getName(), i, i, i == self.iPlayer)
				if gc.getPlayer(i).getTeam() != self.iTeam:
					self.iList.append(i)

		screen.addDropDownBoxGFC("ChangeBy", 20, 50, 160, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		i = 1
		while i < 100001:
			screen.addPullDownString("ChangeBy", CyTranslator().getText("TXT_KEY_WB_CHANGE_BY",(i,)), i, i, iChange == i)
			if str(i)[0] == "1":
				i *= 5
			else:
				i *= 2
		
		if self.bDiplomacyPage:
			self.setEspionagePage()
		else:
			self.setGeneralPage()

	def setGeneralPage(self):
		screen = CyGInterfaceScreen( "WBDiplomacyScreen", CvScreenEnums.WB_DIPLOMACY)
		screen.setButtonGFC( "DiplomacyPage", CyTranslator().getText("TXT_KEY_ESPIONAGE_CULTURE",()), "", 180, 20, screen.getXResolution()/5, 24, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_ARROW_RIGHT)
		screen.setLabel("LegendText", "Background", "<font=3b>" + CyTranslator().getText("TXT_KEY_WB_DIPLOMACY_LEGEND", ()) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, 20, screen.getYResolution() - 40, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		
		screen.addTableControlGFC( "WBDiplomacy", 16, 20, 80, self.nTableWidth, self.nTableHeight, True, True, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		iWidth1 = 100
		iWidth2 = (self.nTableWidth - 24 * 10 - 70 - iWidth1 * 3)/2
		screen.setTableColumnHeader( "WBDiplomacy", 0, CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_CIV", ()), iWidth2)	## Civ
		screen.setTableColumnHeader( "WBDiplomacy", 1, CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_LEADER", ()), iWidth2)	## Leader + Name
		screen.setTableColumnHeader( "WBDiplomacy", 2, CyTranslator().getText("TXT_KEY_WB_TEAM", ()), 50)			## Team
		screen.setTableColumnHeader( "WBDiplomacy", 3, "", 24)
		screen.setTableColumnHeader( "WBDiplomacy", 4, CyTranslator().getText("TXT_KEY_WB_ATTITUDE", ()), iWidth1)		## Attitude
		screen.setTableColumnHeader( "WBDiplomacy", 5, "", 24)
		screen.setTableColumnHeader( "WBDiplomacy", 6, "", 24)
		screen.setTableColumnHeader( "WBDiplomacy", 7, CyTranslator().getText("TXT_KEY_WB_RELATIONSHIP", ()), iWidth1)		## Relationship
		screen.setTableColumnHeader( "WBDiplomacy", 8, "", 24)
		screen.setTableColumnHeader( "WBDiplomacy", 9, CyTranslator().getText("[ICON_ANGRYPOP]", ()), 24)			## Meet
		screen.setTableColumnHeader( "WBDiplomacy", 10, CyTranslator().getText("[ICON_OPENBORDERS]", ()), 24)			## Open Borders
		screen.setTableColumnHeader( "WBDiplomacy", 11, CyTranslator().getText("[ICON_DEFENSIVEPACT]", ()), 24)		## Defensive Pact
		screen.setTableColumnHeader( "WBDiplomacy", 12, CyTranslator().getText("[ICON_OCCUPATION]", ()), 24)			## War
		screen.setTableColumnHeader( "WBDiplomacy", 13, "", 24)
		screen.setTableColumnHeader( "WBDiplomacy", 14, "", 24)
		screen.setTableColumnHeader( "WBDiplomacy", 15, CyTranslator().getText("TXT_KEY_CONCEPT_WAR_WEARINESS", ()), iWidth1 + 20)	## War Weariness
		
		iX = 20 + iWidth2 * 2 + 50 + 24
		screen.addTableControlGFC("AttitudeAll", AttitudeTypes.NUM_ATTITUDE_TYPES, iX, 50, AttitudeTypes.NUM_ATTITUDE_TYPES * 25, 25, False, False, 24, 24, TableStyles.TABLE_STYLE_EMPTY)
		screen.appendTableRow("AttitudeAll")
##		for i in xrange(AttitudeTypes.NUM_ATTITUDE_TYPES):
##			screen.setTableColumnHeader( "AttitudeAll", i, "", 24)
##			screen.setTableText("AttitudeAll", i, 0, "", self.getAttitudeButton(i), WidgetTypes.WIDGET_PYTHON, 1030, i, CvUtil.FONT_CENTER_JUSTIFY )
#magister
		lSymbol = [FontUtil.getChar('ATTITUDE_FURIOUS'), FontUtil.getChar('ATTITUDE_ANNOYED'), FontUtil.getChar('ATTITUDE_CAUTIOUS'), FontUtil.getChar('ATTITUDE_PLEASED'), FontUtil.getChar('ATTITUDE_FRIENDLY')]
		lColor = ["[COLOR_RED]", "[COLOR_CYAN]", "[COLOR_CLEAR]", "[COLOR_GREEN]", "[COLOR_YELLOW]"]

		for iAttitude in xrange(AttitudeTypes.NUM_ATTITUDE_TYPES):
			sAttitude = lSymbol[iAttitude] + gc.getAttitudeInfo(iAttitude).getDescription()
			sColor = CyTranslator().getText(lColor[iAttitude], ())
			screen.setTableText("WBAttitude", 1, 0, sColor + sAttitude, "", WidgetTypes.WIDGET_PYTHON, 1030, iAttitude, CvUtil.FONT_CENTER_JUSTIFY )
#magister

		screen.setLabel("AttitudeAllText", "Background", "<font=4b>" + CyTranslator().getText("TXT_KEY_WB_CITY_ALL", ()) + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, iX, 50, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		
		iX = 20 + iWidth2 * 2 + 50 + 24 * 4 + iWidth1 * 2
		screen.addTableControlGFC("DiplomacyAll", 4, iX, 25, 125, 50, False, True, 24, 24, TableStyles.TABLE_STYLE_EMPTY)
		screen.appendTableRow("DiplomacyAll")
		screen.appendTableRow("DiplomacyAll")
		for i in xrange(4):
			screen.setTableColumnHeader("DiplomacyAll", i, "", 24)
		screen.setTableText("DiplomacyAll", 0, 0, "<font=4>" + CyTranslator().getText("[ICON_ANGRYPOP]", ()) + "<\font>", "", WidgetTypes.WIDGET_PYTHON, 1030, 0, CvUtil.FONT_CENTER_JUSTIFY)
		screen.setTableText("DiplomacyAll", 1, 0, "<font=4>" + CyTranslator().getText("[ICON_OPENBORDERS]", ()) + "<\font>", "", WidgetTypes.WIDGET_PYTHON, 1030, 1, CvUtil.FONT_CENTER_JUSTIFY)
		screen.setTableText("DiplomacyAll", 2, 0, "<font=4>" + CyTranslator().getText("[ICON_DEFENSIVEPACT]", ()) + "<\font>", "", WidgetTypes.WIDGET_PYTHON, 1030, 2, CvUtil.FONT_CENTER_JUSTIFY)
		screen.setTableText("DiplomacyAll", 3, 0, "<font=4>" + CyTranslator().getText("[ICON_OCCUPATION]", ()) + "<\font>", "", WidgetTypes.WIDGET_PYTHON, 1030, 3, CvUtil.FONT_CENTER_JUSTIFY)
		screen.setTableText("DiplomacyAll", 1, 1, "<font=4>" + "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_CANCEL").getPath(), WidgetTypes.WIDGET_PYTHON, 1031, 4, CvUtil.FONT_CENTER_JUSTIFY)
		screen.setTableText("DiplomacyAll", 2, 1, "<font=4>" + "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_CANCEL").getPath(), WidgetTypes.WIDGET_PYTHON, 1031, 5, CvUtil.FONT_CENTER_JUSTIFY)
		screen.setTableText("DiplomacyAll", 3, 1, "<font=4>" + "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_CANCEL").getPath(), WidgetTypes.WIDGET_PYTHON, 1031, 6, CvUtil.FONT_CENTER_JUSTIFY)
		screen.setLabel("DiplomacyAllText", "Background", "<font=4b>" + CyTranslator().getText("TXT_KEY_WB_CITY_ALL", ()) + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, iX, 50, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		
		screen.setButtonGFC("WearinessAllPlus", u"", "", screen.getXResolution() - 70, 52, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("WearinessAllMinus", u"", "", screen.getXResolution() - 45, 52, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		screen.setLabel("WearinessAllText", "Background", "<font=4b>" + CyTranslator().getText("TXT_KEY_WB_CITY_ALL", ()) + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 70, 50, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		
		for i in xrange(len(self.iList)):
			screen.appendTableRow("WBDiplomacy")
			iPlayer = self.iList[i]
			pPlayer = gc.getPlayer(iPlayer)
			iTeam = pPlayer.getTeam()
			pTeam = gc.getTeam(iTeam)
			sColor = u"<color=%d,%d,%d,%d>" %(pPlayer.getPlayerTextColorR(), pPlayer.getPlayerTextColorG(), pPlayer.getPlayerTextColorB(), pPlayer.getPlayerTextColorA())
			iCivilization = pPlayer.getCivilizationType()
			sText = pPlayer.getCivilizationShortDescription(0)
			screen.setTableText("WBDiplomacy", 0, i, "<font=3>" + sColor + sText + "</font></color>", gc.getCivilizationInfo(iCivilization).getButton(), WidgetTypes.WIDGET_PYTHON, 7872, iCivilization, CvUtil.FONT_LEFT_JUSTIFY )
			iLeader = pPlayer.getLeaderType()
			screen.setTableText("WBDiplomacy", 1, i, "<font=3>" + sColor + pPlayer.getName() + "</font></color>", gc.getLeaderHeadInfo(iLeader).getButton(), WidgetTypes.WIDGET_PYTHON, 7876, iLeader, CvUtil.FONT_LEFT_JUSTIFY )
			screen.setTableInt("WBDiplomacy", 2, i, "<font=3>" + sColor + str(iTeam) + "</font></color>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY )
			
			if self.bTowardsPlayer:
				iAttitude = pPlayer.AI_getAttitude(self.iPlayer)
				sWeariness = str(pTeam.getWarWeariness(self.iTeam))
			else:
				iAttitude = gc.getPlayer(self.iPlayer).AI_getAttitude(iPlayer)
				sWeariness = str(gc.getTeam(self.iTeam).getWarWeariness(iTeam))
			screen.setTableText("WBDiplomacy", 3, i, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_LEFT").getPath(), WidgetTypes.WIDGET_PYTHON, 1031, iTeam, CvUtil.FONT_CENTER_JUSTIFY )

##			screen.setTableText("WBDiplomacy", 4, i, "<font=3>" + gc.getAttitudeInfo(iAttitude).getDescription() + "</font>", self.getAttitudeButton(iAttitude), WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY )
#magister
			sAttitude = lSymbol[iAttitude] + gc.getAttitudeInfo(iAttitude).getDescription()
			sColor = CyTranslator().getText(lColor[iAttitude], ())

			screen.setTableText("WBDiplomacy", 4, i, sColor + sAttitude, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY )

#magister
			screen.setTableText("WBDiplomacy", 5, i, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_RIGHT").getPath(), WidgetTypes.WIDGET_PYTHON, 1030, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			
			if self.bTowardsPlayer:
				iRelationshipStatus = self.RelationshipStatus(iTeam, self.iTeam)
			else:
				iRelationshipStatus = self.RelationshipStatus(self.iTeam, iTeam)
			sText = CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ())
			if iRelationshipStatus == 0:
				sText = CyTranslator().getText("TXT_KEY_WB_FVASSAL",())
			elif iRelationshipStatus == 1:
				sText = CyTranslator().getText("TXT_KEY_WB_CVASSAL",())
			elif iRelationshipStatus == 2:
				sText = CyTranslator().getText("TXT_KEY_WB_MASTER",())
			screen.setTableText("WBDiplomacy", 6, i, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_LEFT").getPath(), WidgetTypes.WIDGET_PYTHON, 1035, iTeam , CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBDiplomacy", 7, i, "<font=3>" + sText + "</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBDiplomacy", 8, i, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_RIGHT").getPath(), WidgetTypes.WIDGET_PYTHON, 1036, iTeam , CvUtil.FONT_CENTER_JUSTIFY )

			sText = ""
			if pTeam.isHasMet(self.iTeam):
				sText = CyTranslator().getText("[ICON_ANGRYPOP]",())
			screen.setTableText("WBDiplomacy", 9, i, "<font=4>" + sText + "</font>", "", WidgetTypes.WIDGET_PYTHON, 1034, iTeam , CvUtil.FONT_CENTER_JUSTIFY )
			sText = ""
			if pTeam.isOpenBorders(self.iTeam):
				sText = CyTranslator().getText("[ICON_OPENBORDERS]",())
			screen.setTableText("WBDiplomacy", 10, i, "<font=4>" + sText + "</font>", "", WidgetTypes.WIDGET_PYTHON, 1037, iTeam , CvUtil.FONT_CENTER_JUSTIFY )
			sText = ""
			if pTeam.isDefensivePact(self.iTeam):
				sText = CyTranslator().getText("[ICON_DEFENSIVEPACT]",())
			screen.setTableText("WBDiplomacy", 11, i, "<font=4>" + sText + "</font>", "", WidgetTypes.WIDGET_PYTHON, 1038, iTeam , CvUtil.FONT_CENTER_JUSTIFY )
			sText = ""
			if pTeam.isAtWar(self.iTeam):
				sText = CyTranslator().getText("[ICON_OCCUPATION]",())
			screen.setTableText("WBDiplomacy", 12, i, "<font=4>" + sText + "</font>", "", WidgetTypes.WIDGET_PYTHON, 1039, iTeam , CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBDiplomacy", 13, i, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_PLUS").getPath(), WidgetTypes.WIDGET_PYTHON, 1032, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBDiplomacy", 14, i, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_MINUS").getPath(), WidgetTypes.WIDGET_PYTHON, 1033, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBDiplomacy", 15, i, "<font=3>" + sWeariness + "</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY )
			
	def setEspionagePage(self):
		screen = CyGInterfaceScreen( "WBDiplomacyScreen", CvScreenEnums.WB_DIPLOMACY)
		screen.setButtonGFC( "DiplomacyPage", CyTranslator().getText("TXT_PEDIA_GENERAL",()), "", 180, 20, screen.getXResolution()/5, 24, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_ARROW_LEFT)
		
		screen.addDropDownBoxGFC("CurrentMemory", 20, screen.getYResolution() - 40, 450, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		for i in xrange(MemoryTypes.NUM_MEMORY_TYPES):
			screen.addPullDownString("CurrentMemory", gc.getMemoryInfo(i).getDescription(), i, i, i == self.iMemory)

		screen.addTableControlGFC( "WBEspionage", 17, 20, 80, self.nTableWidth, self.nTableHeight, True, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		iWidth1 = 80
		iWidth2 = (self.nTableWidth - (iWidth1 + 48) * 5) /2
		screen.setTableColumnHeader( "WBEspionage", 0, CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_CIV", ()), iWidth2)	## Civ
		screen.setTableColumnHeader( "WBEspionage", 1, CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_LEADER", ()), iWidth2)	## Leader + Name
		screen.setTableColumnHeader( "WBEspionage", 2, "", 24)
		screen.setTableColumnHeader( "WBEspionage", 3, "", 24)
		screen.setTableColumnHeader( "WBEspionage", 4, CyTranslator().getText("TXT_KEY_WB_MEMORY", ()), iWidth1)						## Memory
		screen.setTableColumnHeader( "WBEspionage", 5, "", 24)
		screen.setTableColumnHeader( "WBEspionage", 6, "", 24)
		screen.setTableColumnHeader( "WBEspionage", 7, CyTranslator().getText("TXT_KEY_ESPIONAGE_CULTURE", ()), iWidth1)	## Espionage
		screen.setTableColumnHeader( "WBEspionage", 8, "", 24)
		screen.setTableColumnHeader( "WBEspionage", 9, "", 24)
		screen.setTableColumnHeader( "WBEspionage", 10, CyTranslator().getText("TXT_KEY_WB_ESPIONAGE_WEIGHT", ()), iWidth1)	## Weight
		screen.setTableColumnHeader( "WBEspionage", 11, "", 24)
		screen.setTableColumnHeader( "WBEspionage", 12, "", 24)
		screen.setTableColumnHeader( "WBEspionage", 13, CyTranslator().getText("TXT_KEY_WB_TURNS", ()), iWidth1)		## Counter Espionage Turns
		screen.setTableColumnHeader( "WBEspionage", 14, "", 24)
		screen.setTableColumnHeader( "WBEspionage", 15, "", 24)
		screen.setTableColumnHeader( "WBEspionage", 16, CyTranslator().getText("TXT_KEY_WB_MODIFIER", ()), iWidth1)		## Counter Espionage Weight
		
		sText = CyTranslator().getText("TXT_KEY_WB_CITY_ALL", ())
		iX = 20 + iWidth2 * 2 + 48 + iWidth1
		screen.setLabel("EspionageHeader", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_ESPIONAGE_CULTURE", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, iX + 50 + iWidth1, 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setButtonGFC("EspionageAllPlus", u"", "", iX, 52, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("EspionageAllMinus", u"", "", iX + 25, 52, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		screen.setLabel("EspionageAll", "Background", u"<font=4b>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iX + 50, 50, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		
		iX += 48 + iWidth1
		screen.setButtonGFC("WeightAllPlus", u"", "", iX, 52, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("WeightAllMinus", u"", "", iX + 25, 52, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		screen.setLabel("WeightAll", "Background", u"<font=4b>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iX + 50, 50, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		
		iX += 48 + iWidth1
		screen.setLabel("CounterEspionageHeader", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_WB_COUNTER_ESPIONAGE", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, iX + 50 + iWidth1, 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setButtonGFC("CETurnsAllPlus", u"", "", iX, 52, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CETurnsAllMinus", u"", "", iX + 25, 52, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		screen.setLabel("CETurnsAll", "Background", u"<font=4b>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iX + 50, 50, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		
		iX += 48 + iWidth1
		screen.setButtonGFC("CEModAllPlus", u"", "", iX, 52, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("CEModAllMinus", u"", "", iX + 25, 52, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		screen.setLabel("CEModAll", "Background", u"<font=4b>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iX + 50, 50, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		
		for i in xrange(len(self.iList)):
			screen.appendTableRow("WBEspionage")
			iPlayer = self.iList[i]
			pPlayer = gc.getPlayer(iPlayer)
			iTeam = pPlayer.getTeam()
			pTeam = gc.getTeam(iTeam)
			sColor = u"<color=%d,%d,%d,%d>" %(pPlayer.getPlayerTextColorR(), pPlayer.getPlayerTextColorG(), pPlayer.getPlayerTextColorB(), pPlayer.getPlayerTextColorA())
			iCivilization = pPlayer.getCivilizationType()
			screen.setTableText("WBEspionage", 0, i, "<font=3>" + sColor + pPlayer.getCivilizationShortDescription(0) + "</font></color>", gc.getCivilizationInfo(iCivilization).getButton(), WidgetTypes.WIDGET_PYTHON, 7872, iCivilization, CvUtil.FONT_LEFT_JUSTIFY )
			iLeader = pPlayer.getLeaderType()
			screen.setTableText("WBEspionage", 1, i, "<font=3>" + sColor + pPlayer.getName() + "</font></color>", gc.getLeaderHeadInfo(iLeader).getButton(), WidgetTypes.WIDGET_PYTHON, 7876, iLeader, CvUtil.FONT_LEFT_JUSTIFY )
			if self.bTowardsPlayer:
				sMemory = str(pPlayer.AI_getMemoryCount(self.iPlayer, self.iMemory))
				sEspionage = str(pTeam.getEspionagePointsAgainstTeam(self.iTeam))
				sWeight = str(pPlayer.getEspionageSpendingWeightAgainstTeam(self.iTeam))
				sTurns = str(pTeam.getCounterespionageTurnsLeftAgainstTeam(self.iTeam))
				sModifier = str(pTeam.getCounterespionageModAgainstTeam(self.iTeam))
			else:
				sMemory = str(gc.getPlayer(self.iPlayer).AI_getMemoryCount(iPlayer, self.iMemory))
				sEspionage = str(gc.getTeam(self.iTeam).getEspionagePointsAgainstTeam(iTeam))
				sWeight = str(gc.getPlayer(self.iPlayer).getEspionageSpendingWeightAgainstTeam(iTeam))
				sTurns = str(gc.getTeam(self.iTeam).getCounterespionageTurnsLeftAgainstTeam(iTeam))
				sModifier = str(gc.getTeam(self.iTeam).getCounterespionageModAgainstTeam(iTeam))
			screen.setTableText("WBEspionage", 2, i, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_PLUS").getPath(), WidgetTypes.WIDGET_PYTHON, 1030, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBEspionage", 3, i, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_MINUS").getPath(), WidgetTypes.WIDGET_PYTHON, 1031, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBEspionage", 4, i, "<font=3>" + sMemory + "</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY )
			screen.setTableText("WBEspionage", 5, i, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_PLUS").getPath(), WidgetTypes.WIDGET_PYTHON, 1032, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBEspionage", 6, i, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_MINUS").getPath(), WidgetTypes.WIDGET_PYTHON, 1033, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableInt("WBEspionage", 7, i, "<font=3>" + sEspionage + "</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY )
			screen.setTableText("WBEspionage", 8, i, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_PLUS").getPath(), WidgetTypes.WIDGET_PYTHON, 1034, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBEspionage", 9, i, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_MINUS").getPath(), WidgetTypes.WIDGET_PYTHON, 1035, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableInt("WBEspionage", 10, i, "<font=3>" + sWeight + "</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY )
		
			screen.setTableText("WBEspionage", 11, i, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_PLUS").getPath(), WidgetTypes.WIDGET_PYTHON, 1036, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBEspionage", 12, i, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_MINUS").getPath(), WidgetTypes.WIDGET_PYTHON, 1037, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableInt("WBEspionage", 13, i, "<font=3>" + sTurns + "</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY )
			screen.setTableText("WBEspionage", 14, i, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_PLUS").getPath(), WidgetTypes.WIDGET_PYTHON, 1038, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBEspionage", 15, i, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_MINUS").getPath(), WidgetTypes.WIDGET_PYTHON, 1039, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableInt("WBEspionage", 16, i, "<font=3>" + sModifier + "</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY )
			
	def handleInput (self, inputClass):
		screen = CyGInterfaceScreen( "WBDiplomacyScreen", CvScreenEnums.WB_DIPLOMACY)
		global iChange

		if inputClass.getFunctionName() == "ChangeBy":
			iIndex = screen.getSelectedPullDownID("ChangeBy")
			iChange = screen.getPullDownData("ChangeBy", iIndex)
		elif inputClass.getFunctionName() == "CurrentPlayer":
			iIndex = screen.getSelectedPullDownID("CurrentPlayer")
			self.iPlayer = screen.getPullDownData("CurrentPlayer", iIndex)
		elif inputClass.getFunctionName() == "DiplomacyPage":
			self.bDiplomacyPage = not self.bDiplomacyPage
		elif inputClass.getFunctionName() == "TowardsPlayer":
			self.bTowardsPlayer = not self.bTowardsPlayer

		if self.bDiplomacyPage:
			if inputClass.getFunctionName() == "CurrentMemory":
				self.iMemory = inputClass.getData()
			elif inputClass.getFunctionName().find("EspionageAll") > -1:
				self.handlePlatyEspionageAll(inputClass.getData1())
			elif inputClass.getFunctionName().find("WeightAll") > -1:
				self.handlePlatyWeightAll(inputClass.getData1())
			elif inputClass.getFunctionName().find("CETurnsAll") > -1:
				self.handlePlatyCETurnsAll(inputClass.getData1())
			elif inputClass.getFunctionName().find("CEModAll") > -1:
				self.handlePlatyCEModAll(inputClass.getData1())

			elif inputClass.getData1() == 1030:
				self.handlePlatyChangeMemoryCB(inputClass.getData2(), iChange)
			elif inputClass.getData1() == 1031:
				self.handlePlatyChangeMemoryCB(inputClass.getData2(), - iChange)
			elif inputClass.getData1() == 1032:
				self.handlePlatyChangeEspionage(inputClass.getData2(), iChange)
			elif inputClass.getData1() == 1033:
				self.handlePlatyChangeEspionage(inputClass.getData2(), - iChange)
			elif inputClass.getData1() == 1034:
				self.handlePlatyChangeWeight(inputClass.getData2(), iChange)
			elif inputClass.getData1() == 1035:
				self.handlePlatyChangeWeight(inputClass.getData2(), - iChange)
			elif inputClass.getData1() == 1036:
				self.handlePlatyChangeCETurns(inputClass.getData2(), iChange)
			elif inputClass.getData1() == 1037:
				self.handlePlatyChangeCETurns(inputClass.getData2(), - iChange)
			elif inputClass.getData1() == 1038:
				self.handlePlatyChangeCEModifier(inputClass.getData2(), iChange)
			elif inputClass.getData1() == 1039:
				self.handlePlatyChangeCEModifier(inputClass.getData2(), - iChange)

		else:
			if inputClass.getFunctionName() == "AttitudeAll":
				self.handlePlatyAttitudeAll(inputClass.getData2())
			elif inputClass.getFunctionName() == "DiplomacyAll":
				self.handlePlatyDiplomacyAll(inputClass.getData2())
			elif inputClass.getFunctionName().find("WearinessAll") > -1:
				self.handlePlatyWearinessAll(inputClass.getData1())

			elif inputClass.getData1() == 1030:
				self.handlePlatyChangeAttitude(inputClass.getData2(), 1)
			elif inputClass.getData1() == 1031:
				self.handlePlatyChangeAttitude(inputClass.getData2(), -1)
			elif inputClass.getData1() == 1032:
				self.handlePlatyChangeWarWeariness(self.iTeam, inputClass.getData2(), iChange)
			elif inputClass.getData1() == 1033:
				self.handlePlatyChangeWarWeariness(self.iTeam, inputClass.getData2(), - iChange)
			elif inputClass.getData1() == 1034:
				gc.getTeam(self.iTeam).meet(inputClass.getData2(), False)
			elif inputClass.getData1() == 1035:
				self.handlePlatyRelationshipDecrease(inputClass.getData2())
			elif inputClass.getData1() == 1036:
				self.handlePlatyRelationshipIncrease(inputClass.getData2())
			elif inputClass.getData1() == 1037:
				self.handlePlatyOpenBordersCB(inputClass.getData2())
			elif inputClass.getData1() == 1038:
				self.handlePlatyDefensivePactCB(inputClass.getData2())
			elif inputClass.getData1() == 1039:
				self.handlePlatyWarCB(inputClass.getData2())
		self.interfaceScreen(self.iPlayer)
		return 1

	def handlePlatyRelationshipIncrease(self, iTeam):
		iTeam2 = iTeam
		iTeam1 = self.iTeam
		if self.bTowardsPlayer:
			iTeam1 = iTeam
			iTeam2 = self.iTeam
		iRelationship = self.RelationshipStatus(iTeam1, iTeam2)
		if iRelationship == 2: return
		gc.getTeam(iTeam1).freeVassal(iTeam2)
		gc.getTeam(iTeam2).freeVassal(iTeam1)
		if iRelationship == 1:
			gc.getTeam(iTeam2).assignVassal(iTeam1, False)
		elif iRelationship == 3:
			gc.getTeam(iTeam1).assignVassal(iTeam2, True)
		return 1

	def handlePlatyRelationshipDecrease(self, iTeam):
		iTeam2 = iTeam
		iTeam1 = self.iTeam
		if self.bTowardsPlayer:
			iTeam1 = iTeam
			iTeam2 = self.iTeam
		iRelationship = self.RelationshipStatus(iTeam1, iTeam2)
		if iRelationship == 1: return
		gc.getTeam(iTeam1).freeVassal(iTeam2)
		gc.getTeam(iTeam2).freeVassal(iTeam1)
		if iRelationship == 0:
			gc.getTeam(iTeam2).assignVassal(iTeam1, True)
		elif iRelationship == 3:
			gc.getTeam(iTeam2).assignVassal(iTeam1, False)
		return 1

##	def getAttitudeButton(self, iAttitude):
##		lAttitude = ["INTERFACE_ATTITUDE_0", "INTERFACE_ATTITUDE_1", "INTERFACE_ATTITUDE_2", "INTERFACE_ATTITUDE_3", "INTERFACE_ATTITUDE_4"]
##		if iAttitude < len(lAttitude):
##			sButton = CyArtFileMgr().getInterfaceArtInfo(lAttitude[iAttitude])
##			if sButton:
##				return sButton.getPath()
##		return ""


	def handlePlatyWarCB (self, iTeam):
		if gc.getTeam(self.iTeam).isAtWar(iTeam):
			gc.getTeam(self.iTeam).makePeace(iTeam)
		else:
			gc.getTeam(self.iTeam).declareWar(iTeam, True, -1)
		return 1

	def handlePlatyDefensivePactCB (self, iTeam):
		if gc.getTeam(self.iTeam).isDefensivePact(iTeam):
			for i in xrange(CyGame().getIndexAfterLastDeal()):
				pDeal = CyGame().getDeal(i)
				iPlayer1 = pDeal.getFirstPlayer()
				iPlayer2 = pDeal.getSecondPlayer()
				if iPlayer1 == -1 or iPlayer2 == -1: continue
				iTeam1 = gc.getPlayer(pDeal.getFirstPlayer()).getTeam()
				iTeam2 = gc.getPlayer(pDeal.getSecondPlayer()).getTeam()
				if (iTeam1 == iTeam and iTeam2 == self.iTeam) or (iTeam2 == iTeam and iTeam1 == self.iTeam):
					for j in xrange(pDeal.getLengthFirstTrades()):
						if pDeal.getFirstTrade(j).ItemType == TradeableItems.TRADE_DEFENSIVE_PACT:	
							pDeal.kill()
							self.interfaceScreen(self.iPlayer)
							return 1
		else:
			gc.getTeam(self.iTeam).signDefensivePact(iTeam)
			return 1

	def handlePlatyOpenBordersCB (self, iTeam):
		if gc.getTeam(self.iTeam).isOpenBorders(iTeam):
			for i in xrange(CyGame().getIndexAfterLastDeal()):
				pDeal = CyGame().getDeal(i)
				iPlayer1 = pDeal.getFirstPlayer()
				iPlayer2 = pDeal.getSecondPlayer()
				if iPlayer1 == -1 or iPlayer2 == -1: continue
				iTeam1 = gc.getPlayer(pDeal.getFirstPlayer()).getTeam()
				iTeam2 = gc.getPlayer(pDeal.getSecondPlayer()).getTeam()
				if (iTeam1 == iTeam and iTeam2 == self.iTeam) or (iTeam2 == iTeam and iTeam1 == self.iTeam):
					for j in xrange(pDeal.getLengthFirstTrades()):
						if pDeal.getFirstTrade(j).ItemType == TradeableItems.TRADE_OPEN_BORDERS:	
							pDeal.kill()
							return 1
		else:
			gc.getTeam(self.iTeam).signOpenBorders(iTeam)
			return 1

	def handlePlatyDiplomacyAll(self, iData2) :
		if iData2 == 0:
			for iTeam in xrange(gc.getMAX_CIV_TEAMS()):
				if iTeam == self.iTeam: continue
				pTeam = gc.getTeam(iTeam)
				if not pTeam.isAlive(): continue
				if pTeam.isHasMet(self.iTeam): continue
				pTeam.meet(self.iTeam, False)
		elif iData2 == 1:
			for iTeam in xrange(gc.getMAX_CIV_TEAMS()):
				if iTeam == self.iTeam: continue
				pTeam = gc.getTeam(iTeam)
				if not pTeam.isAlive(): continue
				if pTeam.isHasMet(self.iTeam):
					pTeam.signOpenBorders(self.iTeam)
		elif iData2 == 2:
			for iTeam in xrange(gc.getMAX_CIV_TEAMS()):
				if iTeam == self.iTeam: continue
				pTeam = gc.getTeam(iTeam)
				if not pTeam.isAlive(): continue
				if pTeam.isHasMet(self.iTeam):
					pTeam.signDefensivePact(self.iTeam)
		elif iData2 == 3:
			for iTeam in xrange(gc.getMAX_CIV_TEAMS()):
				if iTeam == self.iTeam: continue
				pTeam = gc.getTeam(iTeam)
				if not pTeam.isAlive(): continue
				if gc.getTeam(self.iTeam).canDeclareWar(iTeam):
					gc.getTeam(self.iTeam).declareWar(iTeam, True, -1)
		elif iData2 == 4:
			for iDeal in xrange(CyGame().getIndexAfterLastDeal()):
				pDeal = CyGame().getDeal(iDeal)
				iPlayer1 = pDeal.getFirstPlayer()
				iPlayer2 = pDeal.getSecondPlayer()
				if iPlayer1 == -1 or iPlayer2 == -1: continue
				iTeam1 = gc.getPlayer(pDeal.getFirstPlayer()).getTeam()
				iTeam2 = gc.getPlayer(pDeal.getSecondPlayer()).getTeam()
				if iTeam1 == self.iTeam or iTeam2 == self.iTeam:
					for j in xrange(pDeal.getLengthFirstTrades()):
						if pDeal.getFirstTrade(j).ItemType == TradeableItems.TRADE_OPEN_BORDERS:	
							pDeal.kill()
		elif iData2 == 5:
			for iDeal in xrange(CyGame().getIndexAfterLastDeal()):
				pDeal = CyGame().getDeal(iDeal)
				iPlayer1 = pDeal.getFirstPlayer()
				iPlayer2 = pDeal.getSecondPlayer()
				if iPlayer1 == -1 or iPlayer2 == -1: continue
				iTeam1 = gc.getPlayer(pDeal.getFirstPlayer()).getTeam()
				iTeam2 = gc.getPlayer(pDeal.getSecondPlayer()).getTeam()
				if iTeam1 == self.iTeam or iTeam2 == self.iTeam:
					for j in xrange(pDeal.getLengthFirstTrades()):
						if pDeal.getFirstTrade(j).ItemType == TradeableItems.TRADE_DEFENSIVE_PACT:	
							pDeal.kill()
		elif iData2 == 6:
			for iTeam in xrange(gc.getMAX_CIV_TEAMS()):
				if iTeam == self.iTeam: continue
				pTeam = gc.getTeam(iTeam)
				if not pTeam.isAlive(): continue
				if pTeam.isHasMet(self.iTeam):
					pTeam.makePeace(self.iTeam)
		return 1

	def handlePlatyChangeEspionage(self, iTeam, iCount):
		iTeam2 = iTeam
		iTeam1 = self.iTeam
		if self.bTowardsPlayer:
			iTeam1 = iTeam
			iTeam2 = self.iTeam
		if iCount < 0:
			iCount = max(iCount, - gc.getTeam(iTeam1).getEspionagePointsAgainstTeam(iTeam2))
		gc.getTeam(iTeam1).changeEspionagePointsAgainstTeam(iTeam2, iCount)
		return 1

	def handlePlatyChangeWeight(self, iPlayer, iCount):
		pPlayer = gc.getPlayer(iPlayer)
		iTeam2 = pPlayer.getTeam()
		iPlayer1 = self.iPlayer
		if self.bTowardsPlayer:
			iPlayer1 = iPlayer
			iTeam2 = self.iTeam
		gc.getPlayer(iPlayer1).changeEspionageSpendingWeightAgainstTeam(iTeam2, iCount)
		return 1

	def handlePlatyEspionageAll(self, iData1) :
		for iTeamX in xrange(gc.getMAX_CIV_TEAMS()):
			if iTeamX == self.iTeam: continue
			pTeamX = gc.getTeam(iTeamX)
			if not pTeamX.isAlive(): continue
			if not pTeamX.isHasMet(self.iTeam): continue
			if iData1%2:
				self.handlePlatyChangeEspionage(iTeamX, - iChange)
			else:
				self.handlePlatyChangeEspionage(iTeamX, iChange)
		return 1

	def handlePlatyWeightAll(self, iData1) :
		for iPlayerX in xrange(gc.getMAX_CIV_PLAYERS()):
			pPlayerX = gc.getPlayer(iPlayerX)
			if not pPlayerX.isAlive(): continue
			iTeamX = pPlayerX.getTeam()
			if iTeamX == self.iTeam: continue
			if not gc.getTeam(iTeamX).isHasMet(self.iTeam): continue
			if iData1%2:
				self.handlePlatyChangeWeight(iPlayerX, - iChange)
			else:
				self.handlePlatyChangeWeight(iPlayerX, iChange)
		return 1

	def handlePlatyChangeCETurns(self, iTeam, iCount):
		iTeam2 = iTeam
		iTeam1 = self.iTeam
		if self.bTowardsPlayer:
			iTeam1 = iTeam
			iTeam2 = self.iTeam
		if iCount < 0:
			iCount = max(iCount, - gc.getTeam(iTeam1).getCounterespionageTurnsLeftAgainstTeam(iTeam2))
		gc.getTeam(iTeam1).changeCounterespionageTurnsLeftAgainstTeam(iTeam2, iCount)
		return 1

	def handlePlatyChangeCEModifier(self, iTeam, iCount):
		iTeam2 = iTeam
		iTeam1 = self.iTeam
		if self.bTowardsPlayer:
			iTeam1 = iTeam
			iTeam2 = self.iTeam
		if iCount < 0:
			iCount = max(iCount, - gc.getTeam(iTeam1).getCounterespionageModAgainstTeam(iTeam2))
		gc.getTeam(iTeam1).changeCounterespionageModAgainstTeam(iTeam2, iCount)
		return 1

	def handlePlatyCETurnsAll(self, iData1) :
		for iTeamX in xrange(gc.getMAX_CIV_TEAMS()):
			if iTeamX == self.iTeam: continue
			pTeamX = gc.getTeam(iTeamX)
			if not pTeamX.isAlive(): continue
			if not pTeamX.isHasMet(self.iTeam): continue
			if iData1%2:
				self.handlePlatyChangeCETurns(iTeamX, - iChange)
			else:
				self.handlePlatyChangeCETurns(iTeamX, iChange)
		return 1

	def handlePlatyCEModAll(self, iData1) :
		for iTeamX in xrange(gc.getMAX_CIV_TEAMS()):
			if iTeamX == self.iTeam: continue
			pTeamX = gc.getTeam(iTeamX)
			if not pTeamX.isAlive(): continue
			if not pTeamX.isHasMet(self.iTeam): continue
			if iData1%2:
				self.handlePlatyChangeCEModifier(iTeamX, - iChange)
			else:
				self.handlePlatyChangeCEModifier(iTeamX, iChange)
		return 1

	def handlePlatyChangeAttitude(self, iPlayer, iChange):
		pPlayer = gc.getPlayer(iPlayer)
		if pPlayer.isBarbarian() or pPlayer.isMinorCiv():
			return 1
		if self.RelationshipStatus(pPlayer.getTeam(), self.iTeam) == 0:
			return 1
		iPlayer2 = iPlayer
		pPlayer1 = gc.getPlayer(self.iPlayer)
		if self.bTowardsPlayer:
			pPlayer1 = pPlayer
			iPlayer2 = self.iPlayer
		iNewAttitude = max(0, pPlayer1.AI_getAttitude(iPlayer2) - 1)
		if iChange == 1:
			iNewAttitude = min(pPlayer1.AI_getAttitude(iPlayer2) + 1, AttitudeTypes.NUM_ATTITUDE_TYPES - 1)
		while iNewAttitude != pPlayer1.AI_getAttitude(iPlayer2):
			pPlayer1.AI_changeAttitudeExtra(iPlayer2, iChange)
		return 1

	def handlePlatyChangeMemoryCB (self, iPlayer, iChange):
		iPlayer2 = iPlayer
		pPlayer1 = gc.getPlayer(self.iPlayer)
		if self.bTowardsPlayer:
			pPlayer1 = gc.getPlayer(iPlayer)
			iPlayer2 = self.iPlayer
		pPlayer1.AI_changeMemoryCount(iPlayer2, self.iMemory, iChange)
		if pPlayer1.AI_getMemoryCount (iPlayer2, self.iMemory) < 0:
			pPlayer1.AI_changeMemoryCount(iPlayer2, self.iMemory, - pPlayer1.AI_getMemoryCount (iPlayer2, self.iMemory))
		return 1

	def handlePlatyChangeWarWeariness(self, iTeam1, iTeam2, iChange):
		if self.bTowardsPlayer:
			gc.getTeam(iTeam2).changeWarWeariness(iTeam1, iChange)
		else:
			gc.getTeam(iTeam1).changeWarWeariness(iTeam2, iChange)
		return 1

	def handlePlatyCEModAll(self, iData1) :
		for iTeamX in xrange(gc.getMAX_CIV_TEAMS()):
			if iTeamX == self.iTeam: continue
			pTeamX = gc.getTeam(iTeamX)
			if not pTeamX.isAlive(): continue
			if not pTeamX.isHasMet(self.iTeam): continue
			if iData1%2:
				self.handlePlatyChangeCEModifier(iTeamX, - iChange)
			else:
				self.handlePlatyChangeCEModifier(iTeamX, iChange)
		return 1

	def handlePlatyWearinessAll(self, iData1) :
		for iTeamX in xrange(gc.getMAX_CIV_TEAMS()):
			if iTeamX == self.iTeam: continue
			pTeamX = gc.getTeam(iTeamX)
			if not pTeamX.isAlive(): continue
			if not pTeamX.isHasMet(self.iTeam): continue
			if iData1%2:
				self.handlePlatyChangeWarWeariness(self.iTeam, iTeamX, - iChange)
			else:
				self.handlePlatyChangeWarWeariness(self.iTeam, iTeamX, iChange)
		return 1

	def handlePlatyAttitudeAll(self, iData1):
		for iPlayerX in xrange(gc.getMAX_CIV_PLAYERS()):
			pPlayerX = gc.getPlayer(iPlayerX)
			if not pPlayerX.isAlive(): continue
			iTeamX = pPlayerX.getTeam()
			if iTeamX == self.iTeam: continue
			if not gc.getTeam(iTeamX).isHasMet(self.iTeam): continue
			if self.RelationshipStatus(iTeamX, self.iTeam) == 0: continue
			if self.bTowardsPlayer:
				while iData1 != pPlayerX.AI_getAttitude(self.iPlayer):
					if iData1 > pPlayerX.AI_getAttitude(self.iPlayer):
						pPlayerX.AI_changeAttitudeExtra(self.iPlayer, 1)
					else:
						pPlayerX.AI_changeAttitudeExtra(self.iPlayer, -1)
			else:
				while iData1 != gc.getPlayer(self.iPlayer).AI_getAttitude(iPlayerX):
					if iData1 > gc.getPlayer(self.iPlayer).AI_getAttitude(iPlayerX):
						gc.getPlayer(self.iPlayer).AI_changeAttitudeExtra(iPlayerX, 1)
					else:
						gc.getPlayer(self.iPlayer).AI_changeAttitudeExtra(iPlayerX, -1)
		return 1

	def RelationshipStatus(self, iTeam1, iTeam2):
		if gc.getTeam(iTeam1).isVassal(iTeam2):
			for i in range(CyGame().getIndexAfterLastDeal()):
				pDeal = CyGame().getDeal(i)
				iPlayer1 = pDeal.getFirstPlayer()
				iPlayer2 = pDeal.getSecondPlayer()
				if iPlayer1 == -1 or iPlayer2 == -1: continue
				iTeamX = gc.getPlayer(pDeal.getFirstPlayer()).getTeam()
				iTeamY = gc.getPlayer(pDeal.getSecondPlayer()).getTeam()
				if (iTeam1 == iTeamX and iTeam2 == iTeamY) or (iTeam2 == iTeamX and iTeam1 == iTeamY):
					for j in xrange(pDeal.getLengthFirstTrades()):
						if pDeal.getFirstTrade(j).ItemType == TradeableItems.TRADE_VASSAL:	
							return 0
						if pDeal.getFirstTrade(j).ItemType == TradeableItems.TRADE_SURRENDER:	
							return 1
					for j in xrange(pDeal.getLengthSecondTrades()):
						if pDeal.getSecondTrade(j).ItemType == TradeableItems.TRADE_VASSAL:	
							return 0
						if pDeal.getSecondTrade(j).ItemType == TradeableItems.TRADE_SURRENDER:	
							return 1
		elif gc.getTeam(iTeam2).isVassal(iTeam1):
			return 2
		return 3

	def update(self, fDelta):
		return 1