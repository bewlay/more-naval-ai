## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums
import FontUtil

# globals
gc = CyGlobalContext()
g_pCity = None

class WBDiplomacyScreen:

	def __init__(self):
		self.iList = []
		self.iDiplomacyPage = 0
		self.iPlayer = 0
		self.iTeam = 0
		self.bShowDead = 0
		self.bTowardsPlayer = 0
		self.iMemory = 0

	def interfaceScreen(self, iPlayer):
		screen = CyGInterfaceScreen( "WBDiplomacyScreen", CvScreenEnums.WB_DIPLOMACY)
		self.iPlayer = iPlayer
		self.iTeam = gc.getPlayer(iPlayer).getTeam()

		self.nTableWidth = screen.getXResolution() - 40
		self.nTableHeight = screen.getYResolution() - 100
		screen.setRenderInterfaceOnly(True)
		screen.addPanel( "MainBG", u"", u"", True, False, -10, -10, screen.getXResolution() + 20, screen.getYResolution() + 20, PanelStyles.PANEL_STYLE_MAIN )
		screen.setDimensions(0, 0, screen.getXResolution(), screen.getYResolution())
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)

		screen.setText("DiplomacyExit", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 25, screen.getYResolution() - 40, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )

		szDropdownName = str("DiplomacyPage")
		screen.addDropDownBoxGFC(szDropdownName, 20, 20, 180, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_PEDIA_GENERAL",()), 0, 0, 0 == self.iDiplomacyPage)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_ATTITUDE",()), 1, 1, 1 == self.iDiplomacyPage)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_ESPIONAGE_CULTURE",()), 2, 2, 2 == self.iDiplomacyPage)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_COUNTER_ESPIONAGE",()), 3, 3, 3 == self.iDiplomacyPage)

		szDropdownName = str("TowardsPlayer")
		screen.addDropDownBoxGFC(szDropdownName, 200, screen.getYResolution() - 40, 180, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_TOWARDS_OTHERS", ()), 0, 0, 0 == self.bTowardsPlayer)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_TOWARDS", (gc.getPlayer(self.iPlayer).getName(),)), 1, 1, 1 == self.bTowardsPlayer)

		szDropdownName = str("CurrentPlayer")
		screen.addDropDownBoxGFC(szDropdownName, 200, 20, 180, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		iCount = 0
		self.iList = []
		for i in xrange(gc.getMAX_PLAYERS()):
			if gc.getPlayer(i).isEverAlive():
				sName = gc.getPlayer(i).getName()
				if not gc.getPlayer(i).isAlive():
					sName = "*" + sName
				if (gc.getPlayer(i).isAlive() or self.bShowDead) and gc.getPlayer(i).getTeam() != self.iTeam:
					self.iList.append(i)
				iCount += 1
				screen.addPullDownString(szDropdownName, sName, iCount, iCount, i == self.iPlayer)

		szDropdownName = str("ShowDead")
		screen.addDropDownBoxGFC(szDropdownName, 20, screen.getYResolution() - 40, 180, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_HIDE_DEAD",()), 0, 0, 0 == self.bShowDead)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_SHOW_DEAD",()), 1, 1, 1 == self.bShowDead)

		if self.iDiplomacyPage == 0:
			self.setGeneralPage()
		elif self.iDiplomacyPage == 1:
			self.setAttitudePage()
		elif self.iDiplomacyPage == 2:
			self.setEspionagePage()
		elif self.iDiplomacyPage == 3:
			self.setCounterEspionagePage()

	def setGeneralPage(self):
		screen = CyGInterfaceScreen( "WBDiplomacyScreen", CvScreenEnums.WB_DIPLOMACY)
		screen.setText("DiplomacyHeader", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_WB_DIPLOMACY", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		szDropdownName = str("DiplomacyCommands")
		screen.addDropDownBoxGFC(szDropdownName, screen.getXResolution() - 200, 20, 180, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_COMMANDS", ()), 0, 0, True)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_MEET_ALL", ()), 1, 1, False)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_WAR_ALL", ()), 2, 2, False)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_PEACE_ALL", ()), 3, 3, False)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_OPEN_BORDERS", ()), 4, 4, False)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_CLEAR_OPEN_BORDERS", ()), 5, 5, False)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_DEFENSIVE_PACT", ()), 6, 6, False)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_CLEAR_DEFENSIVE_PACT", ()), 7, 7, False)

		nColumns = 10
		screen.addTableControlGFC( "WBDiplomacy", nColumns, 20, 60, self.nTableWidth, self.nTableHeight, True, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		screen.setTableColumnHeader( "WBDiplomacy", 0, CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_CIV", ()), (self.nTableWidth - 340 * 2) /2)	## Civ
		screen.setTableColumnHeader( "WBDiplomacy", 1, CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_LEADER", ()), (self.nTableWidth - 340 * 2) /2)	## Leader + Name
		screen.setTableColumnHeader( "WBDiplomacy", 2, CyTranslator().getText("TXT_KEY_WB_TEAM", ()), 50)	## Team
		screen.setTableColumnHeader( "WBDiplomacy", 3, CyTranslator().getText("TXT_KEY_WB_MEET", ()), 50)	## Meet
		screen.setTableColumnHeader( "WBDiplomacy", 4, CyTranslator().getText("TXT_KEY_WB_MASTER", ()), 80)	## Master
		screen.setTableColumnHeader( "WBDiplomacy", 5, CyTranslator().getText("TXT_KEY_WB_FVASSAL", ()), 90)	## Free Vassal
		screen.setTableColumnHeader( "WBDiplomacy", 6, CyTranslator().getText("TXT_KEY_WB_CVASSAL", ()), 90)	## Capitulated Vassal
		screen.setTableColumnHeader( "WBDiplomacy", 7, CyTranslator().getText("TXT_KEY_CONCEPT_WAR", ()), 80)	## War
		screen.setTableColumnHeader( "WBDiplomacy", 8, CyTranslator().getText("TXT_KEY_WB_OPEN_BORDERS", ()), 120)	## Open Borders
		screen.setTableColumnHeader( "WBDiplomacy", 9, CyTranslator().getText("TXT_KEY_WB_DEFENSIVE_PACT", ()), 120)	## Defensive Pact
		for i in xrange(len(self.iList)):
			screen.appendTableRow("WBDiplomacy")

		for i in xrange(len(self.iList)):
			iPlayer = self.iList[i]
			pPlayer = gc.getPlayer(iPlayer)
			iTeam = pPlayer.getTeam()
			pTeam = gc.getTeam(iTeam)
			sColor = u"<color=%d,%d,%d,%d>" %(pPlayer.getPlayerTextColorR(), pPlayer.getPlayerTextColorG(), pPlayer.getPlayerTextColorB(), pPlayer.getPlayerTextColorA())
			iCivilization = pPlayer.getCivilizationType()
			sText = pPlayer.getCivilizationShortDescription(0)
			screen.setTableText("WBDiplomacy", 0, i, sColor + sText + "</color>", gc.getCivilizationInfo(iCivilization).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, iCivilization, 1, CvUtil.FONT_LEFT_JUSTIFY )
			sText = pPlayer.getName()
			if not pPlayer.isAlive():
				sText = "*" + sText
			iLeader = pPlayer.getLeaderType()
			screen.setTableText("WBDiplomacy", 1, i, sColor + sText + "</color>", gc.getLeaderHeadInfo(iLeader).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_LEADER, iLeader, 1, CvUtil.FONT_LEFT_JUSTIFY )
			screen.setTableInt("WBDiplomacy", 2, i, sColor + str(iTeam) + "</color>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]",())
			if pTeam.isHasMet(self.iTeam):
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]",())
			sText = CyTranslator().getText("TXT_KEY_WB_MEET",())
			screen.setTableText("WBDiplomacy", 3, i, sColor + sText + "</color>", "", WidgetTypes.WIDGET_PYTHON, 1030, iTeam , CvUtil.FONT_LEFT_JUSTIFY )

			iRelationshipStatus = self.RelationshipStatus(iTeam, self.iTeam)
			bFree = False
			bCapitulated = False
			bMaster = False
			if iRelationshipStatus == 0:
				bFree = True
			elif iRelationshipStatus == 1:
				bCapitulated = True
			elif iRelationshipStatus == 2:
				bMaster = True
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]",())
			if bMaster:
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]",())
			sText = CyTranslator().getText("TXT_KEY_WB_MASTER",())
			screen.setTableText("WBDiplomacy", 4, i, sColor + sText + "</color>", "", WidgetTypes.WIDGET_PYTHON, 1031, iTeam , CvUtil.FONT_LEFT_JUSTIFY )
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]",())
			if bFree:
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]",())
			sText = CyTranslator().getText("TXT_KEY_WB_FVASSAL",())
			screen.setTableText("WBDiplomacy", 5, i, sColor + sText + "</color>", "", WidgetTypes.WIDGET_PYTHON, 1032, iTeam , CvUtil.FONT_LEFT_JUSTIFY )
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]",())
			if bCapitulated:
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]",())
			sText = CyTranslator().getText("TXT_KEY_WB_CVASSAL",())
			screen.setTableText("WBDiplomacy", 6, i, sColor + sText + "</color>", "", WidgetTypes.WIDGET_PYTHON, 1033, iTeam , CvUtil.FONT_LEFT_JUSTIFY )

			if pTeam.isAtWar(self.iTeam):
				sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]",())
				sText = CyTranslator().getText("[ICON_UNHAPPY]",()) + CyTranslator().getText("TXT_KEY_CONCEPT_WAR",())
			else:
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]",())
				sText = CyTranslator().getText("[ICON_HAPPY]",()) + CyTranslator().getText("TXT_KEY_WB_PEACE",())
			screen.setTableText("WBDiplomacy", 7, i, sColor + sText + "</color>", "", WidgetTypes.WIDGET_PYTHON, 1034, iTeam , CvUtil.FONT_LEFT_JUSTIFY )
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]",())
			if pTeam.isOpenBorders(self.iTeam):
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]",())
			sText = CyTranslator().getText("[ICON_OPENBORDERS]",()) + CyTranslator().getText("TXT_KEY_WB_OPEN_BORDERS",())
			screen.setTableText("WBDiplomacy", 8, i, sColor + sText + "</color>", "", WidgetTypes.WIDGET_PYTHON, 1035, iTeam , CvUtil.FONT_LEFT_JUSTIFY )
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]",())
			if pTeam.isDefensivePact(self.iTeam):
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]",())
			sText = CyTranslator().getText("[ICON_DEFENSIVEPACT]",()) + CyTranslator().getText("TXT_KEY_WB_DEFENSIVE_PACT",())
			screen.setTableText("WBDiplomacy", 9, i, sColor + sText + "</color>", "", WidgetTypes.WIDGET_PYTHON, 1036, iTeam , CvUtil.FONT_LEFT_JUSTIFY )

	def setAttitudePage(self):
		screen = CyGInterfaceScreen( "WBDiplomacyScreen", CvScreenEnums.WB_DIPLOMACY)
		screen.setText("AttitudeHeader", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_WB_ATTITUDE", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		szDropdownName = str("CurrentMemory")
		screen.addDropDownBoxGFC(szDropdownName, 380, screen.getYResolution() - 40, 480, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		for i in xrange(MemoryTypes.NUM_MEMORY_TYPES):
			screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_MEMORY", ()) + ": " + gc.getMemoryInfo(i).getDescription(), i, i, i == self.iMemory)

		szDropdownName = str("AttitudeCommands")
		screen.addDropDownBoxGFC(szDropdownName, screen.getXResolution() - 420, 20, 180, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_ATTITUDE", ()) + " " + CyTranslator().getText("TXT_KEY_WB_COMMANDS", ()), 0, 0, True)
		for iAttitude in xrange(AttitudeTypes.NUM_ATTITUDE_TYPES):
			screen.addPullDownString(szDropdownName, gc.getAttitudeInfo(iAttitude).getDescription(), iAttitude + 1, iAttitude + 1, False)

		szDropdownName = str("WarWearinessCommands")
		screen.addDropDownBoxGFC(szDropdownName, screen.getXResolution() - 240, 20, 220, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_CONCEPT_WAR_WEARINESS", ()) + " " + CyTranslator().getText("TXT_KEY_WB_COMMANDS", ()), 0, 0, True)
		for i in xrange(5):
			screen.addPullDownString(szDropdownName, "+" + CyTranslator().getText("TXT_KEY_WB_ADD_ALL",(10 ** i,)), i + 1, i + 1, False)
		for i in xrange(5):
			screen.addPullDownString(szDropdownName, "-" + CyTranslator().getText("TXT_KEY_WB_ADD_ALL",(10 ** i,)), i + 5, i + 5, False)

		nColumns = 21
		iSpace = 30
		screen.addTableControlGFC( "WBAttitude", nColumns, 20, 60, self.nTableWidth, self.nTableHeight, True, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		screen.setTableColumnHeader( "WBAttitude", 0, CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_CIV", ()), (self.nTableWidth - 280 - iSpace * 14) /2)	## Civ
		screen.setTableColumnHeader( "WBAttitude", 1, CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_LEADER", ()), (self.nTableWidth - 280 - iSpace * 14) /2)	## Leader + Name
		screen.setTableColumnHeader( "WBAttitude", 2, CyTranslator().getText("TXT_KEY_WB_ATTITUDE", ()), 95)	## Attitude
		screen.setTableColumnHeader( "WBAttitude", 3, "+", 20)
		screen.setTableColumnHeader( "WBAttitude", 4, "-", 20)
		screen.setTableColumnHeader( "WBAttitude", 5, "M", 37)		## Memory
		screen.setTableColumnHeader( "WBAttitude", 6, "+", iSpace)	## +10
		screen.setTableColumnHeader( "WBAttitude", 7, "+", iSpace)	## +1
		screen.setTableColumnHeader( "WBAttitude", 8, "-", iSpace)	## -1
		screen.setTableColumnHeader( "WBAttitude", 9, "-", iSpace)	## -10

		screen.setTableColumnHeader( "WBAttitude", 10, "WW", 60)## Memory
		screen.setTableColumnHeader( "WBAttitude", 11, "+", iSpace + 10)	## +10000
		screen.setTableColumnHeader( "WBAttitude", 12, "+", iSpace + 7)	## +1000
		screen.setTableColumnHeader( "WBAttitude", 13, "+", iSpace + 7)	## +100
		screen.setTableColumnHeader( "WBAttitude", 14, "+", iSpace)	## +10
		screen.setTableColumnHeader( "WBAttitude", 15, "+", iSpace)	## +1
		screen.setTableColumnHeader( "WBAttitude", 16, "-", iSpace)	## -1
		screen.setTableColumnHeader( "WBAttitude", 17, "-", iSpace)	## -10
		screen.setTableColumnHeader( "WBAttitude", 18, "-", iSpace + 7)	## -100
		screen.setTableColumnHeader( "WBAttitude", 19, "+", iSpace + 7)	## -1000
		screen.setTableColumnHeader( "WBAttitude", 20, "+", iSpace + 10)	## -10000

		for i in xrange(len(self.iList)):
			screen.appendTableRow("WBAttitude")

		for i in xrange(len(self.iList)):
			iPlayer = self.iList[i]
			pPlayer = gc.getPlayer(iPlayer)
			iTeam = pPlayer.getTeam()
			pTeam = gc.getTeam(iTeam)
			sColor = u"<color=%d,%d,%d,%d>" %(pPlayer.getPlayerTextColorR(), pPlayer.getPlayerTextColorG(), pPlayer.getPlayerTextColorB(), pPlayer.getPlayerTextColorA())
			iCivilization = pPlayer.getCivilizationType()
			sText = pPlayer.getCivilizationShortDescription(0)
			screen.setTableText("WBAttitude", 0, i, sColor + sText + "</color>", gc.getCivilizationInfo(iCivilization).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, iCivilization, 1, CvUtil.FONT_LEFT_JUSTIFY )
			sText = pPlayer.getName()
			if not pPlayer.isAlive():
				sText = "*" + sText
			iLeader = pPlayer.getLeaderType()
			screen.setTableText("WBAttitude", 1, i, sColor + sText + "</color>", gc.getLeaderHeadInfo(iLeader).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_LEADER, iLeader, 1, CvUtil.FONT_LEFT_JUSTIFY )
			lSymbol = [FontUtil.getChar('ATTITUDE_FURIOUS'), FontUtil.getChar('ATTITUDE_ANNOYED'), FontUtil.getChar('ATTITUDE_CAUTIOUS'), FontUtil.getChar('ATTITUDE_PLEASED'), FontUtil.getChar('ATTITUDE_FRIENDLY')]
			lColor = ["[COLOR_RED]", "[COLOR_CYAN]", "[COLOR_CLEAR]", "[COLOR_GREEN]", "[COLOR_YELLOW]"]
			if self.bTowardsPlayer:
				iAttitude = pPlayer.AI_getAttitude(self.iPlayer)
				sMemory = str(pPlayer.AI_getMemoryCount(self.iPlayer, self.iMemory))
				sWeariness = str(pTeam.getWarWeariness(self.iTeam))
			else:
				iAttitude = gc.getPlayer(self.iPlayer).AI_getAttitude(iPlayer)
				sMemory = str(gc.getPlayer(self.iPlayer).AI_getMemoryCount(iPlayer, self.iMemory))
				sWeariness = str(gc.getTeam(self.iTeam).getWarWeariness(iTeam))
			sAttitude = lSymbol[iAttitude] + gc.getAttitudeInfo(iAttitude).getDescription()
			sColor = CyTranslator().getText(lColor[iAttitude], ())
			screen.setTableText("WBAttitude", 2, i, sColor + sAttitude, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
			screen.setTableText("WBAttitude", 3, i, CyTranslator().getText("[COLOR_POSITIVE_TEXT]+[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1030, iPlayer, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBAttitude", 4, i, CyTranslator().getText("[COLOR_WARNING_TEXT]-[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1031, iPlayer, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBAttitude", 5, i, sMemory, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY )
			screen.setTableText("WBAttitude", 6, i, CyTranslator().getText("[COLOR_POSITIVE_TEXT]10[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1032, iPlayer, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBAttitude", 7, i, CyTranslator().getText("[COLOR_POSITIVE_TEXT]1[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1033, iPlayer, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBAttitude", 8, i, CyTranslator().getText("[COLOR_WARNING_TEXT]1[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1034, iPlayer, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBAttitude", 9, i, CyTranslator().getText("[COLOR_WARNING_TEXT]10[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1035, iPlayer, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBAttitude", 10, i, sWeariness, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY )
			screen.setTableText("WBAttitude", 11, i, CyTranslator().getText("[COLOR_POSITIVE_TEXT]10K[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1036, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBAttitude", 12, i, CyTranslator().getText("[COLOR_POSITIVE_TEXT]1K[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1037, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBAttitude", 13, i, CyTranslator().getText("[COLOR_POSITIVE_TEXT]100[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1038, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBAttitude", 14, i, CyTranslator().getText("[COLOR_POSITIVE_TEXT]10[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1039, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBAttitude", 15, i, CyTranslator().getText("[COLOR_POSITIVE_TEXT]1[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1040, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBAttitude", 16, i, CyTranslator().getText("[COLOR_WARNING_TEXT]1[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1041, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBAttitude", 17, i, CyTranslator().getText("[COLOR_WARNING_TEXT]10[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1042, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBAttitude", 18, i, CyTranslator().getText("[COLOR_WARNING_TEXT]100[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1043, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBAttitude", 19, i, CyTranslator().getText("[COLOR_WARNING_TEXT]1K[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1044, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBAttitude", 20, i, CyTranslator().getText("[COLOR_WARNING_TEXT]10K[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1045, iTeam, CvUtil.FONT_CENTER_JUSTIFY )

	def setEspionagePage(self):
		screen = CyGInterfaceScreen( "WBDiplomacyScreen", CvScreenEnums.WB_DIPLOMACY)
		screen.setText("EspionageHeader", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_ESPIONAGE_CULTURE", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		szDropdownName = str("EspionageCommands")
		screen.addDropDownBoxGFC(szDropdownName, screen.getXResolution() - 380, 20, 180, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_ESPIONAGE_CULTURE", ()) + " " + CyTranslator().getText("TXT_KEY_WB_COMMANDS", ()), 0, 0, True)
		for i in xrange(5):
			screen.addPullDownString(szDropdownName, "+" + CyTranslator().getText("TXT_KEY_WB_ADD_ALL",(10 ** i,)), i + 1, i + 1, False)
		for i in xrange(5):
			screen.addPullDownString(szDropdownName, "-" + CyTranslator().getText("TXT_KEY_WB_ADD_ALL",(10 ** i,)), i + 5, i + 6, False)

		szDropdownName = str("WeightCommands")
		screen.addDropDownBoxGFC(szDropdownName, screen.getXResolution() - 200, 20, 180, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_ESPIONAGE_WEIGHT", ()) + " " + CyTranslator().getText("TXT_KEY_WB_COMMANDS", ()), 0, 0, True)
		for i in xrange(3):
			screen.addPullDownString(szDropdownName, "+" + CyTranslator().getText("TXT_KEY_WB_ADD_ALL",(10 ** i,)), i + 1, i + 1, False)
		for i in xrange(3):
			screen.addPullDownString(szDropdownName, "-" + CyTranslator().getText("TXT_KEY_WB_ADD_ALL",(10 ** i,)), i + 4, i + 4, False)

		nColumns = 20
		iSpace = 30
		screen.addTableControlGFC( "WBEspionage", nColumns, 20, 60, self.nTableWidth, self.nTableHeight, True, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		screen.setTableColumnHeader( "WBEspionage", 0, CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_CIV", ()), (self.nTableWidth - 80 - 62 - iSpace * 17) /2)	## Civ
		screen.setTableColumnHeader( "WBEspionage", 1, CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_LEADER", ()), (self.nTableWidth - 80 - 62 - iSpace * 17) /2)	## Leader + Name
		screen.setTableColumnHeader( "WBEspionage", 2, CyTranslator().getText("TXT_KEY_ESPIONAGE_CULTURE", ()), 80)	## Espionage
		screen.setTableColumnHeader( "WBEspionage", 3, "+", iSpace + 10)	## + 10000
		screen.setTableColumnHeader( "WBEspionage", 4, "+", iSpace + 7)	## + 1000
		screen.setTableColumnHeader( "WBEspionage", 5, "+", iSpace + 7)	## + 100
		screen.setTableColumnHeader( "WBEspionage", 6, "+", iSpace)	## +10
		screen.setTableColumnHeader( "WBEspionage", 7, "+", iSpace)	## +1
		screen.setTableColumnHeader( "WBEspionage", 8, "-", iSpace)	## -1
		screen.setTableColumnHeader( "WBEspionage", 9, "-", iSpace)	## -10
		screen.setTableColumnHeader( "WBEspionage", 10, "-", iSpace + 7)	## -100
		screen.setTableColumnHeader( "WBEspionage", 11, "-", iSpace + 7)	## -1000
		screen.setTableColumnHeader( "WBEspionage", 12, "-", iSpace + 10)	## -10000
		screen.setTableColumnHeader( "WBEspionage", 13, "W", iSpace)	## Weight
		screen.setTableColumnHeader( "WBEspionage", 14, "+", iSpace + 7)	## + 100
		screen.setTableColumnHeader( "WBEspionage", 15, "+", iSpace)	## +10
		screen.setTableColumnHeader( "WBEspionage", 16, "+", iSpace)	## +1
		screen.setTableColumnHeader( "WBEspionage", 17, "-", iSpace)	## -1
		screen.setTableColumnHeader( "WBEspionage", 18, "-", iSpace)	## -10
		screen.setTableColumnHeader( "WBEspionage", 19, "-", iSpace + 7)	## -100
		for i in xrange(len(self.iList)):
			screen.appendTableRow("WBEspionage")

		for i in xrange(len(self.iList)):
			iPlayer = self.iList[i]
			pPlayer = gc.getPlayer(iPlayer)
			iTeam = pPlayer.getTeam()
			pTeam = gc.getTeam(iTeam)
			sColor = u"<color=%d,%d,%d,%d>" %(pPlayer.getPlayerTextColorR(), pPlayer.getPlayerTextColorG(), pPlayer.getPlayerTextColorB(), pPlayer.getPlayerTextColorA())
			iCivilization = pPlayer.getCivilizationType()
			sText = pPlayer.getCivilizationShortDescription(0)
			screen.setTableText("WBEspionage", 0, i, sColor + sText + "</color>", gc.getCivilizationInfo(iCivilization).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, iCivilization, 1, CvUtil.FONT_LEFT_JUSTIFY )
			sText = pPlayer.getName()
			if not pPlayer.isAlive():
				sText = "*" + sText
			iLeader = pPlayer.getLeaderType()
			screen.setTableText("WBEspionage", 1, i, sColor + sText + "</color>", gc.getLeaderHeadInfo(iLeader).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_LEADER, iLeader, 1, CvUtil.FONT_LEFT_JUSTIFY )
			if self.bTowardsPlayer:
				sEspionage = str(pTeam.getEspionagePointsAgainstTeam(self.iTeam))
				sWeight = str(pPlayer.getEspionageSpendingWeightAgainstTeam(self.iTeam))
			else:
				sEspionage = str(gc.getTeam(self.iTeam).getEspionagePointsAgainstTeam(iTeam))
				sWeight = str(gc.getPlayer(self.iPlayer).getEspionageSpendingWeightAgainstTeam(iTeam))
			screen.setTableText("WBEspionage", 2, i, sEspionage, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY )
			screen.setTableText("WBEspionage", 3, i, CyTranslator().getText("[COLOR_POSITIVE_TEXT]10K[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1030, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBEspionage", 4, i, CyTranslator().getText("[COLOR_POSITIVE_TEXT]1K[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1031, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBEspionage", 5, i, CyTranslator().getText("[COLOR_POSITIVE_TEXT]100[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1032, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBEspionage", 6, i, CyTranslator().getText("[COLOR_POSITIVE_TEXT]10[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1033, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBEspionage", 7, i, CyTranslator().getText("[COLOR_POSITIVE_TEXT]1[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1034, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBEspionage", 8, i, CyTranslator().getText("[COLOR_WARNING_TEXT]1[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1035, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBEspionage", 9, i, CyTranslator().getText("[COLOR_WARNING_TEXT]10[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1036, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBEspionage", 10, i, CyTranslator().getText("[COLOR_WARNING_TEXT]100[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1037, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBEspionage", 11, i, CyTranslator().getText("[COLOR_WARNING_TEXT]1K[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1038, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBEspionage", 12, i, CyTranslator().getText("[COLOR_WARNING_TEXT]10K[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1039, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBEspionage", 13, i, sWeight, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY )
			screen.setTableText("WBEspionage", 14, i, CyTranslator().getText("[COLOR_POSITIVE_TEXT]100[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1040, iPlayer, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBEspionage", 15, i, CyTranslator().getText("[COLOR_POSITIVE_TEXT]10[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1041, iPlayer, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBEspionage", 16, i, CyTranslator().getText("[COLOR_POSITIVE_TEXT]1[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1042, iPlayer, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBEspionage", 17, i, CyTranslator().getText("[COLOR_WARNING_TEXT]1[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1043, iPlayer, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBEspionage", 18, i, CyTranslator().getText("[COLOR_WARNING_TEXT]10[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1044, iPlayer, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBEspionage", 19, i, CyTranslator().getText("[COLOR_WARNING_TEXT]100[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1045, iPlayer, CvUtil.FONT_CENTER_JUSTIFY )

	def setCounterEspionagePage(self):
		screen = CyGInterfaceScreen( "WBDiplomacyScreen", CvScreenEnums.WB_DIPLOMACY)
		screen.setText("CounterEspionageHeader", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_WB_COUNTER_ESPIONAGE", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		szDropdownName = str("TurnsCommands")
		screen.addDropDownBoxGFC(szDropdownName, screen.getXResolution() - 380, 20, 180, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_TURNS", ()) + " " + CyTranslator().getText("TXT_KEY_WB_COMMANDS", ()), 0, 0, True)
		for i in xrange(4):
			screen.addPullDownString(szDropdownName, "+" + CyTranslator().getText("TXT_KEY_WB_ADD_ALL",(10 ** i,)), i + 1, i + 1, False)
		for i in xrange(4):
			screen.addPullDownString(szDropdownName, "-" + CyTranslator().getText("TXT_KEY_WB_ADD_ALL",(10 ** i,)), i + 5, i + 5, False)

		szDropdownName = str("ModifierCommands")
		screen.addDropDownBoxGFC(szDropdownName, screen.getXResolution() - 200, 20, 180, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_MODIFIER", ()) + " " + CyTranslator().getText("TXT_KEY_WB_COMMANDS", ()), 0, 0, True)
		for i in xrange(4):
			screen.addPullDownString(szDropdownName, "+" + CyTranslator().getText("TXT_KEY_WB_ADD_ALL",(10 ** i,)), i + 1, i + 1, False)
		for i in xrange(4):
			screen.addPullDownString(szDropdownName, "-" + CyTranslator().getText("TXT_KEY_WB_ADD_ALL",(10 ** i,)), i + 5, i + 5, False)

		nColumns = 16
		iSpace = 37
		screen.addTableControlGFC( "WBCounterEspionage", nColumns, 20, 60, self.nTableWidth, self.nTableHeight, True, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		screen.setTableColumnHeader( "WBCounterEspionage", 0, CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_CIV", ()), (self.nTableWidth - 80 * 2 - iSpace * 12) /2)	## Civ
		screen.setTableColumnHeader( "WBCounterEspionage", 1, CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_LEADER", ()), (self.nTableWidth - 80 * 2 - iSpace * 12) /2)	## Leader
		screen.setTableColumnHeader( "WBCounterEspionage", 2, CyTranslator().getText("TXT_KEY_WB_TURNS", ()), 80)
		screen.setTableColumnHeader( "WBCounterEspionage", 3, "+", iSpace)	## +100
		screen.setTableColumnHeader( "WBCounterEspionage", 4, "+", iSpace)	## +10
		screen.setTableColumnHeader( "WBCounterEspionage", 5, "+", iSpace)	## +1
		screen.setTableColumnHeader( "WBCounterEspionage", 6, "-", iSpace)	## -1
		screen.setTableColumnHeader( "WBCounterEspionage", 7, "-", iSpace)	## -10
		screen.setTableColumnHeader( "WBCounterEspionage", 8, "-", iSpace)	## -100
		screen.setTableColumnHeader( "WBCounterEspionage", 9, CyTranslator().getText("TXT_KEY_WB_MODIFIER", ()), 80)
		screen.setTableColumnHeader( "WBCounterEspionage", 10, "+", iSpace)	## +100
		screen.setTableColumnHeader( "WBCounterEspionage", 11, "+", iSpace)	## +10
		screen.setTableColumnHeader( "WBCounterEspionage", 12, "+", iSpace)	## +1
		screen.setTableColumnHeader( "WBCounterEspionage", 13, "-", iSpace)	## -1
		screen.setTableColumnHeader( "WBCounterEspionage", 14, "-", iSpace)	## -10
		screen.setTableColumnHeader( "WBCounterEspionage", 15, "-", iSpace)	## -100
		for i in xrange(len(self.iList)):
			screen.appendTableRow("WBCounterEspionage")

		for i in xrange(len(self.iList)):
			iPlayer = self.iList[i]
			pPlayer = gc.getPlayer(iPlayer)
			iTeam = pPlayer.getTeam()
			pTeam = gc.getTeam(iTeam)
			sColor = u"<color=%d,%d,%d,%d>" %(pPlayer.getPlayerTextColorR(), pPlayer.getPlayerTextColorG(), pPlayer.getPlayerTextColorB(), pPlayer.getPlayerTextColorA())
			iCivilization = pPlayer.getCivilizationType()
			sText = pPlayer.getCivilizationShortDescription(0)
			screen.setTableText("WBCounterEspionage", 0, i, sColor + sText + "</color>", gc.getCivilizationInfo(iCivilization).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, iCivilization, 1, CvUtil.FONT_LEFT_JUSTIFY )
			sText = pPlayer.getName()
			if not pPlayer.isAlive():
				sText = "*" + sText
			iLeader = pPlayer.getLeaderType()
			screen.setTableText("WBCounterEspionage", 1, i, sColor + sText + "</color>", gc.getLeaderHeadInfo(iLeader).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_LEADER, iLeader, 1, CvUtil.FONT_LEFT_JUSTIFY )
			if self.bTowardsPlayer:
				sTurns = str(pTeam.getCounterespionageTurnsLeftAgainstTeam(self.iTeam))
				sModifier = str(pTeam.getCounterespionageModAgainstTeam(self.iTeam))
			else:
				sTurns = str(gc.getTeam(self.iTeam).getCounterespionageTurnsLeftAgainstTeam(iTeam))
				sModifier = str(gc.getTeam(self.iTeam).getCounterespionageModAgainstTeam(iTeam))
			screen.setTableText("WBCounterEspionage", 2, i, sTurns, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY )
			screen.setTableText("WBCounterEspionage", 3, i, CyTranslator().getText("[COLOR_POSITIVE_TEXT]100[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1030, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBCounterEspionage", 4, i, CyTranslator().getText("[COLOR_POSITIVE_TEXT]10[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1031, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBCounterEspionage", 5, i, CyTranslator().getText("[COLOR_POSITIVE_TEXT]1[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1032, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBCounterEspionage", 6, i, CyTranslator().getText("[COLOR_WARNING_TEXT]1[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1033, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBCounterEspionage", 7, i, CyTranslator().getText("[COLOR_WARNING_TEXT]10[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1034, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBCounterEspionage", 8, i, CyTranslator().getText("[COLOR_WARNING_TEXT]100[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1035, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBCounterEspionage", 9, i, sModifier, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY )
			screen.setTableText("WBCounterEspionage", 10, i, CyTranslator().getText("[COLOR_POSITIVE_TEXT]100[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1036, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBCounterEspionage", 11, i, CyTranslator().getText("[COLOR_POSITIVE_TEXT]10[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1037, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBCounterEspionage", 12, i, CyTranslator().getText("[COLOR_POSITIVE_TEXT]1[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1038, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBCounterEspionage", 13, i, CyTranslator().getText("[COLOR_WARNING_TEXT]1[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1039, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBCounterEspionage", 14, i, CyTranslator().getText("[COLOR_WARNING_TEXT]10[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1040, iTeam, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBCounterEspionage", 15, i, CyTranslator().getText("[COLOR_WARNING_TEXT]100[COLOR_REVERT]", ()), "", WidgetTypes.WIDGET_PYTHON, 1041, iTeam, CvUtil.FONT_CENTER_JUSTIFY )

	def handleInput (self, inputClass):
		if inputClass.getFunctionName() == "CurrentPlayer":
			self.handlePlatyCurrentPlayerCB(inputClass.getData())
			return 1
		if inputClass.getFunctionName() == "DiplomacyPage":
			self.handlePlatyDiplomacyPageCB(inputClass.getData())
			return 1
		if inputClass.getFunctionName() == "ShowDead":
			self.handlePlatyShowDeadCB(inputClass.getData())
			return 1
		if inputClass.getFunctionName() == "TowardsPlayer":
			self.handlePlatyTowardsPlayerCB(inputClass.getData())
			return 1
		if inputClass.getFunctionName() == "DiplomacyCommands":
			self.handlePlatyDiplomacyCommandsCB(inputClass.getData())
			return 1
		if inputClass.getFunctionName() == "EspionageCommands":
			self.handlePlatyEspionageCommandsCB(inputClass.getData())
			return 1
		if inputClass.getFunctionName() == "WeightCommands":
			self.handlePlatyWeightCommandsCB(inputClass.getData())
			return 1
		if inputClass.getFunctionName() == "TurnsCommands":
			self.handlePlatyTurnsCommandsCB(inputClass.getData())
			return 1
		if inputClass.getFunctionName() == "ModifierCommands":
			self.handlePlatyModifierCommandsCB(inputClass.getData())
			return 1
		if inputClass.getFunctionName() == "CurrentMemory":
			self.handlePlatyCurrentMemoryCB(inputClass.getData())
			return 1
		if inputClass.getFunctionName() == "AttitudeCommands":
			self.handlePlatyAttitudeCommandsCB(inputClass.getData())
			return 1
		if inputClass.getFunctionName() == "WarWearinessCommands":
			self.handlePlatyWarWearinessCommandsCB(inputClass.getData())
			return 1

		if inputClass.getData2() == 1 and inputClass.getData1() > -1 and inputClass.getData1() < 1030:
			self.interfaceScreen(self.iPlayer)
			return 1

		if self.iDiplomacyPage == 0:
			if inputClass.getData1() == 1030 and inputClass.getData2() > -1:
				self.handlePlatyMeetCB(inputClass.getData2())
				return 1
			if inputClass.getData1() == 1031 and inputClass.getData2() > -1:
				self.handlePlatyMasterCB(inputClass.getData2())
				return 1
			if inputClass.getData1() == 1032 and inputClass.getData2() > -1:
				self.handlePlatyFreeVassalCB(inputClass.getData2())
				return 1
			if inputClass.getData1() == 1033 and inputClass.getData2() > -1:
				self.handlePlatyCapitulationCB(inputClass.getData2())
				return 1
			if inputClass.getData1() == 1034 and inputClass.getData2() > -1:
				self.handlePlatyWarCB(inputClass.getData2())
				return 1
			if inputClass.getData1() == 1035 and inputClass.getData2() > -1:
				self.handlePlatyOpenBordersCB(inputClass.getData2())
				return 1
			if inputClass.getData1() == 1036 and inputClass.getData2() > -1:
				self.handlePlatyDefensivePactCB(inputClass.getData2())
				return 1

		if self.iDiplomacyPage == 1:
			if inputClass.getData1() == 1030 and inputClass.getData2() > -1:
				self.handlePlatyChangeAttitudeCB(inputClass.getData2(), 1)
				return 1
			if inputClass.getData1() == 1031 and inputClass.getData2() > -1:
				self.handlePlatyChangeAttitudeCB(inputClass.getData2(), -1)
				return 1

			if inputClass.getData1() == 1032 and inputClass.getData2() > -1:
				self.handlePlatyChangeMemoryCB(inputClass.getData2(), 10)
				return 1
			if inputClass.getData1() == 1033 and inputClass.getData2() > -1:
				self.handlePlatyChangeMemoryCB(inputClass.getData2(), 1)
				return 1
			if inputClass.getData1() == 1034 and inputClass.getData2() > -1:
				self.handlePlatyChangeMemoryCB(inputClass.getData2(), -1)
				return 1
			if inputClass.getData1() == 1035 and inputClass.getData2() > -1:
				self.handlePlatyChangeMemoryCB(inputClass.getData2(), -10)
				return 1

			if inputClass.getData1() == 1036 and inputClass.getData2() > -1:
				self.handlePlatyChangeWarWearinessCB(inputClass.getData2(), 10000)
				return 1
			if inputClass.getData1() == 1037 and inputClass.getData2() > -1:
				self.handlePlatyChangeWarWearinessCB(inputClass.getData2(), 1000)
				return 1
			if inputClass.getData1() == 1038 and inputClass.getData2() > -1:
				self.handlePlatyChangeWarWearinessCB(inputClass.getData2(), 100)
				return 1
			if inputClass.getData1() == 1039 and inputClass.getData2() > -1:
				self.handlePlatyChangeWarWearinessCB(inputClass.getData2(), 10)
				return 1
			if inputClass.getData1() == 1040 and inputClass.getData2() > -1:
				self.handlePlatyChangeWarWearinessCB(inputClass.getData2(), 1)
				return 1
			if inputClass.getData1() == 1041 and inputClass.getData2() > -1:
				self.handlePlatyChangeWarWearinessCB(inputClass.getData2(), -1)
				return 1
			if inputClass.getData1() == 1042 and inputClass.getData2() > -1:
				self.handlePlatyChangeWarWearinessCB(inputClass.getData2(), -10)
				return 1
			if inputClass.getData1() == 1043 and inputClass.getData2() > -1:
				self.handlePlatyChangeWarWearinessCB(inputClass.getData2(), -100)
				return 1
			if inputClass.getData1() == 1044 and inputClass.getData2() > -1:
				self.handlePlatyChangeWarWearinessCB(inputClass.getData2(), -1000)
				return 1
			if inputClass.getData1() == 1045 and inputClass.getData2() > -1:
				self.handlePlatyChangeWarWearinessCB(inputClass.getData2(), -10000)
				return 1

		if self.iDiplomacyPage == 2:
			if inputClass.getData1() == 1030 and inputClass.getData2() > -1:
				self.handlePlatyChangeEspionageCB(inputClass.getData2(), 10000)
				return 1
			if inputClass.getData1() == 1031 and inputClass.getData2() > -1:
				self.handlePlatyChangeEspionageCB(inputClass.getData2(), 1000)
				return 1
			if inputClass.getData1() == 1032 and inputClass.getData2() > -1:
				self.handlePlatyChangeEspionageCB(inputClass.getData2(), 100)
				return 1
			if inputClass.getData1() == 1033 and inputClass.getData2() > -1:
				self.handlePlatyChangeEspionageCB(inputClass.getData2(), 10)
				return 1
			if inputClass.getData1() == 1034 and inputClass.getData2() > -1:
				self.handlePlatyChangeEspionageCB(inputClass.getData2(), 1)
				return 1
			if inputClass.getData1() == 1035 and inputClass.getData2() > -1:
				self.handlePlatyChangeEspionageCB(inputClass.getData2(), -1)
				return 1
			if inputClass.getData1() == 1036 and inputClass.getData2() > -1:
				self.handlePlatyChangeEspionageCB(inputClass.getData2(), -10)
				return 1
			if inputClass.getData1() == 1037 and inputClass.getData2() > -1:
				self.handlePlatyChangeEspionageCB(inputClass.getData2(), -100)
				return 1
			if inputClass.getData1() == 1038 and inputClass.getData2() > -1:
				self.handlePlatyChangeEspionageCB(inputClass.getData2(), -1000)
				return 1
			if inputClass.getData1() == 1039 and inputClass.getData2() > -1:
				self.handlePlatyChangeEspionageCB(inputClass.getData2(), -10000)
				return 1

			if inputClass.getData1() == 1040 and inputClass.getData2() > -1:
				self.handlePlatyChangeWeightCB(inputClass.getData2(), 100)
				return 1
			if inputClass.getData1() == 1041 and inputClass.getData2() > -1:
				self.handlePlatyChangeWeightCB(inputClass.getData2(), 10)
				return 1
			if inputClass.getData1() == 1042 and inputClass.getData2() > -1:
				self.handlePlatyChangeWeightCB(inputClass.getData2(), 1)
				return 1
			if inputClass.getData1() == 1043 and inputClass.getData2() > -1:
				self.handlePlatyChangeWeightCB(inputClass.getData2(), -1)
				return 1
			if inputClass.getData1() == 1044 and inputClass.getData2() > -1:
				self.handlePlatyChangeWeightCB(inputClass.getData2(), -10)
				return 1
			if inputClass.getData1() == 1045 and inputClass.getData2() > -1:
				self.handlePlatyChangeWeightCB(inputClass.getData2(), -100)
				return 1

		if self.iDiplomacyPage == 3:
			if inputClass.getData1() == 1030 and inputClass.getData2() > -1:
				self.handlePlatyChangeCETurnsCB(inputClass.getData2(), 100)
				return 1
			if inputClass.getData1() == 1031 and inputClass.getData2() > -1:
				self.handlePlatyChangeCETurnsCB(inputClass.getData2(), 10)
				return 1
			if inputClass.getData1() == 1032 and inputClass.getData2() > -1:
				self.handlePlatyChangeCETurnsCB(inputClass.getData2(), 1)
				return 1
			if inputClass.getData1() == 1033 and inputClass.getData2() > -1:
				self.handlePlatyChangeCETurnsCB(inputClass.getData2(), -1)
				return 1
			if inputClass.getData1() == 1034 and inputClass.getData2() > -1:
				self.handlePlatyChangeCETurnsCB(inputClass.getData2(), -10)
				return 1
			if inputClass.getData1() == 1035 and inputClass.getData2() > -1:
				self.handlePlatyChangeCETurnsCB(inputClass.getData2(), -100)
				return 1

			if inputClass.getData1() == 1036 and inputClass.getData2() > -1:
				self.handlePlatyChangeCEModifierCB(inputClass.getData2(), 100)
				return 1
			if inputClass.getData1() == 1037 and inputClass.getData2() > -1:
				self.handlePlatyChangeCEModifierCB(inputClass.getData2(), 10)
				return 1
			if inputClass.getData1() == 1038 and inputClass.getData2() > -1:
				self.handlePlatyChangeCEModifierCB(inputClass.getData2(), 1)
				return 1
			if inputClass.getData1() == 1039 and inputClass.getData2() > -1:
				self.handlePlatyChangeCEModifierCB(inputClass.getData2(), -1)
				return 1
			if inputClass.getData1() == 1040 and inputClass.getData2() > -1:
				self.handlePlatyChangeCEModifierCB(inputClass.getData2(), -10)
				return 1
			if inputClass.getData1() == 1041 and inputClass.getData2() > -1:
				self.handlePlatyChangeCEModifierCB(inputClass.getData2(), -100)
				return 1
		return 1

	def handlePlatyCurrentPlayerCB ( self, argsList ) :
		iIndex = argsList
		iCount = 0
		for iPlayer in xrange(gc.getMAX_PLAYERS()):
			if gc.getPlayer(iPlayer).isEverAlive():
				if iCount == int(iIndex):
					self.interfaceScreen(iPlayer)
					return 1
				iCount += 1

	def handlePlatyDiplomacyPageCB ( self, argsList ) :
		self.iDiplomacyPage = int(argsList)
		self.interfaceScreen(self.iPlayer)
		return 1

	def handlePlatyShowDeadCB ( self, argsList ) :
		self.bShowDead = int(argsList)
		self.interfaceScreen(self.iPlayer)
		return 1

	def handlePlatyTowardsPlayerCB ( self, argsList ) :
		self.bTowardsPlayer = int(argsList)
		self.interfaceScreen(self.iPlayer)
		return 1

	def handlePlatyMeetCB (self, iTeam):
		gc.getTeam(self.iTeam).meet(iTeam, False)
		self.interfaceScreen(self.iPlayer)
		return 1

	def handlePlatyCapitulationCB(self, iTeam):
		iTeam2 = iTeam
		iTeam1 = self.iTeam
		if self.bTowardsPlayer:
			iTeam1 = iTeam
			iTeam2 = self.iTeam
		if gc.getTeam(iTeam1).isVassal(iTeam2):
			gc.getTeam(iTeam2).freeVassal(iTeam1)
			gc.getTeam(iTeam1).freeVassal(iTeam2)
		else:
			gc.getTeam(iTeam2).freeVassal(iTeam1)
			gc.getTeam(iTeam1).freeVassal(iTeam2)
			gc.getTeam(iTeam2).assignVassal(iTeam1, True)
		self.interfaceScreen(self.iPlayer)
		return 1

	def handlePlatyFreeVassalCB(self, iTeam):
		iTeam2 = iTeam
		iTeam1 = self.iTeam
		if self.bTowardsPlayer:
			iTeam1 = iTeam
			iTeam2 = self.iTeam
		if gc.getTeam(iTeam1).isVassal(iTeam2):
			gc.getTeam(iTeam2).freeVassal(iTeam1)
			gc.getTeam(iTeam1).freeVassal(iTeam2)
		else:
			gc.getTeam(iTeam2).freeVassal(iTeam1)
			gc.getTeam(iTeam1).freeVassal(iTeam2)
			gc.getTeam(iTeam2).assignVassal(iTeam1, False)
		self.interfaceScreen(self.iPlayer)
		return 1

	def handlePlatyMasterCB(self, iTeam):
		iTeam2 = iTeam
		iTeam1 = self.iTeam
		if self.bTowardsPlayer:
			iTeam1 = iTeam
			iTeam2 = self.iTeam
		if gc.getTeam(iTeam2).isVassal(iTeam1):
			gc.getTeam(iTeam1).freeVassal(iTeam2)
			gc.getTeam(iTeam2).freeVassal(iTeam1)
		else:
			gc.getTeam(iTeam2).freeVassal(iTeam1)
			gc.getTeam(iTeam1).freeVassal(iTeam2)
			gc.getTeam(iTeam1).assignVassal(iTeam2, True)
		self.interfaceScreen(self.iPlayer)
		return 1

	def handlePlatyWarCB (self, iTeam):
		if gc.getTeam(self.iTeam).isAtWar(iTeam):
			gc.getTeam(self.iTeam).makePeace(iTeam)
		else:
			gc.getTeam(self.iTeam).declareWar(iTeam, True, -1)
		self.interfaceScreen(self.iPlayer)
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
			self.interfaceScreen(self.iPlayer)
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
							self.interfaceScreen(self.iPlayer)
							return 1
		else:
			gc.getTeam(self.iTeam).signOpenBorders(iTeam)
			self.interfaceScreen(self.iPlayer)
			return 1

	def handlePlatyDiplomacyCommandsCB (self, argsList) :
		iIndex = int(argsList)
		if iIndex == 1:
			for iTeam in xrange(gc.getMAX_CIV_TEAMS()):
				if iTeam == self.iTeam: continue
				pTeam = gc.getTeam(iTeam)
				if not pTeam.isAlive(): continue
				if pTeam.isHasMet(self.iTeam): continue
				pTeam.meet(self.iTeam, False)
		elif iIndex == 2:
			for iTeam in xrange(gc.getMAX_CIV_TEAMS()):
				if iTeam == self.iTeam: continue
				pTeam = gc.getTeam(iTeam)
				if not pTeam.isAlive(): continue
				if pTeam.isVassal(self.iTeam) or gc.getTeam(self.iTeam).isVassal(iTeam): continue
				if pTeam.isHasMet(self.iTeam):
					gc.getTeam(self.iTeam).declareWar(iTeam, True, -1)
		elif iIndex == 3:
			for iTeam in xrange(gc.getMAX_CIV_TEAMS()):
				if iTeam == self.iTeam: continue
				pTeam = gc.getTeam(iTeam)
				if not pTeam.isAlive(): continue
				if pTeam.isHasMet(self.iTeam):
					pTeam.makePeace(self.iTeam)
		elif iIndex == 4:
			for iTeam in xrange(gc.getMAX_CIV_TEAMS()):
				if iTeam == self.iTeam: continue
				pTeam = gc.getTeam(iTeam)
				if not pTeam.isAlive(): continue
				if pTeam.isHasMet(self.iTeam):
					pTeam.signOpenBorders(self.iTeam)
		elif iIndex == 5:
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
		elif iIndex == 6:
			for iTeam in xrange(gc.getMAX_CIV_TEAMS()):
				if iTeam == self.iTeam: continue
				pTeam = gc.getTeam(iTeam)
				if not pTeam.isAlive(): continue
				if pTeam.isHasMet(self.iTeam):
					pTeam.signDefensivePact(self.iTeam)
		elif iIndex == 7:
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
		self.interfaceScreen(self.iPlayer)
		return 1

	def handlePlatyChangeEspionageCB (self, iTeam, iCount):
		iTeam2 = iTeam
		iTeam1 = self.iTeam
		if self.bTowardsPlayer:
			iTeam1 = iTeam
			iTeam2 = self.iTeam
		gc.getTeam(iTeam1).changeEspionagePointsAgainstTeam(iTeam2, iCount)
		if gc.getTeam(iTeam1).getEspionagePointsAgainstTeam(iTeam2) < 0:
			gc.getTeam(iTeam1).changeEspionagePointsAgainstTeam(iTeam2, - gc.getTeam(iTeam1).getEspionagePointsAgainstTeam(iTeam2))
		self.interfaceScreen(self.iPlayer)
		return 1

	def handlePlatyChangeWeightCB (self, iPlayer, iCount):
		pPlayer = gc.getPlayer(iPlayer)
		iTeam2 = pPlayer.getTeam()
		iPlayer1 = self.iPlayer
		if self.bTowardsPlayer:
			iPlayer1 = iPlayer
			iTeam2 = self.iTeam
		gc.getPlayer(iPlayer1).changeEspionageSpendingWeightAgainstTeam(iTeam2, iCount)
		self.interfaceScreen(self.iPlayer)
		return 1

	def handlePlatyEspionageCommandsCB (self, argsList) :
		iIndex = int(argsList) - 1
		if iIndex < 5:
			for iTeamX in xrange(gc.getMAX_CIV_TEAMS()):
				if iTeamX == self.iTeam: continue
				pTeamX = gc.getTeam(iTeamX)
				if not pTeamX.isAlive(): continue
				if not pTeamX.isHasMet(self.iTeam): continue
				if self.bTowardsPlayer:
					pTeamX.changeEspionagePointsAgainstTeam(self.iTeam, 10 ** iIndex)
				else:
					gc.getTeam(self.iTeam).changeEspionagePointsAgainstTeam(iTeamX, 10 ** iIndex)
		else:
			iIndex -= 5
			for iTeamX in xrange(gc.getMAX_CIV_TEAMS()):
				if iTeamX == self.iTeam: continue
				pTeamX = gc.getTeam(iTeamX)
				if not pTeamX.isAlive(): continue
				if not pTeamX.isHasMet(self.iTeam): continue
				if self.bTowardsPlayer:
					pTeamX.changeEspionagePointsAgainstTeam(self.iTeam, - min(10 ** iIndex, pTeamX.getEspionagePointsAgainstTeam(self.iTeam)))
				else:
					gc.getTeam(self.iTeam).changeEspionagePointsAgainstTeam(iTeamX, - min(10 ** iIndex, gc.getTeam(self.iTeam).getEspionagePointsAgainstTeam(iTeamX)))
		self.interfaceScreen(self.iPlayer)
		return 1

	def handlePlatyWeightCommandsCB (self, argsList) :
		iIndex = int(argsList) - 1
		if iIndex < 3:
			for iPlayerX in self.iList:
				pPlayerX = gc.getPlayer(iPlayerX)
				iTeamX = pPlayerX.getTeam()
				if self.bTowardsPlayer:
					pPlayerX.changeEspionageSpendingWeightAgainstTeam(self.iTeam, 10 ** iIndex)
				else:
					if gc.getTeam(iTeamX).getLeaderID() != iPlayerX: continue
					gc.getPlayer(self.iPlayer).changeEspionageSpendingWeightAgainstTeam(iTeamX, 10 ** iIndex)
		else:
			iIndex -= 3
			for iPlayerX in self.iList:
				pPlayerX = gc.getPlayer(iPlayerX)
				iTeamX = pPlayerX.getTeam()
				if self.bTowardsPlayer:
					pPlayerX.changeEspionageSpendingWeightAgainstTeam(self.iTeam, - 10 ** iIndex)
				else:
					if gc.getTeam(iTeamX).getLeaderID() != iPlayerX: continue
					gc.getPlayer(self.iPlayer).changeEspionageSpendingWeightAgainstTeam(iTeamX, - 10 ** iIndex)
		self.interfaceScreen(self.iPlayer)
		return 1

	def handlePlatyChangeCETurnsCB (self, iTeam, iCount):
		iTeam2 = iTeam
		iTeam1 = self.iTeam
		if self.bTowardsPlayer:
			iTeam1 = iTeam
			iTeam2 = self.iTeam
		gc.getTeam(iTeam1).changeCounterespionageTurnsLeftAgainstTeam(iTeam2, iCount)
		if gc.getTeam(iTeam1).getCounterespionageTurnsLeftAgainstTeam(iTeam2) < 0:
			gc.getTeam(iTeam1).changeCounterespionageTurnsLeftAgainstTeam(iTeam2, - gc.getTeam(iTeam1).getCounterespionageTurnsLeftAgainstTeam(iTeam2))
		self.interfaceScreen(self.iPlayer)
		return 1

	def handlePlatyChangeCEModifierCB (self, iTeam, iCount):
		iTeam2 = iTeam
		iTeam1 = self.iTeam
		if self.bTowardsPlayer:
			iTeam1 = iTeam
			iTeam2 = self.iTeam
		gc.getTeam(iTeam1).changeCounterespionageModAgainstTeam(iTeam2, iCount)
		if gc.getTeam(iTeam1).getCounterespionageModAgainstTeam(iTeam2) < 0:
			gc.getTeam(iTeam1).changeCounterespionageModAgainstTeam(iTeam2, - gc.getTeam(iTeam1).getCounterespionageModAgainstTeam(iTeam2))
		self.interfaceScreen(self.iPlayer)
		return 1

	def handlePlatyModifierCommandsCB (self, argsList) :
		iIndex = int(argsList) - 1
		if iIndex < 4:
			for iTeamX in xrange(gc.getMAX_CIV_TEAMS()):
				if iTeamX == self.iTeam: continue
				pTeamX = gc.getTeam(iTeamX)
				if not pTeamX.isAlive(): continue
				if not pTeamX.isHasMet(self.iTeam): continue
				if self.bTowardsPlayer:
					pTeamX.changeCounterespionageModAgainstTeam(self.iTeam, 10 ** iIndex)
				else:
					gc.getTeam(self.iTeam).changeCounterespionageModAgainstTeam(iTeamX, 10 ** iIndex)
		else:
			iIndex -= 4
			for iTeamX in xrange(gc.getMAX_CIV_TEAMS()):
				if iTeamX == self.iTeam: continue
				pTeamX = gc.getTeam(iTeamX)
				if not pTeamX.isAlive(): continue
				if not pTeamX.isHasMet(self.iTeam): continue
				if self.bTowardsPlayer:
					pTeamX.changeCounterespionageModAgainstTeam(self.iTeam, - min(10 ** iIndex, pTeamX.getCounterespionageModAgainstTeam(self.iTeam)))
				else:
					gc.getTeam(self.iTeam).changeCounterespionageModAgainstTeam(iTeamX, - min(10 ** iIndex, gc.getTeam(self.iTeam).getCounterespionageModAgainstTeam(iTeamX)))
		self.interfaceScreen(self.iPlayer)
		return 1

	def handlePlatyTurnsCommandsCB (self, argsList) :
		iIndex = int(argsList) - 1
		if iIndex < 4:
			for iTeamX in xrange(gc.getMAX_CIV_TEAMS()):
				if iTeamX == self.iTeam: continue
				pTeamX = gc.getTeam(iTeamX)
				if not pTeamX.isAlive(): continue
				if not pTeamX.isHasMet(self.iTeam): continue
				if self.bTowardsPlayer:
					pTeamX.changeCounterespionageTurnsLeftAgainstTeam(self.iTeam, 10 ** iIndex)
				else:
					gc.getTeam(self.iTeam).changeCounterespionageTurnsLeftAgainstTeam(iTeamX, 10 ** iIndex)
		else:
			iIndex -= 4
			for iTeamX in xrange(gc.getMAX_CIV_TEAMS()):
				if iTeamX == self.iTeam: continue
				pTeamX = gc.getTeam(iTeamX)
				if not pTeamX.isAlive(): continue
				if not pTeamX.isHasMet(self.iTeam): continue
				if self.bTowardsPlayer:
					pTeamX.changeCounterespionageTurnsLeftAgainstTeam(self.iTeam, - min(10 ** iIndex, pTeamX.getCounterespionageTurnsLeftAgainstTeam(self.iTeam)))
				else:
					gc.getTeam(self.iTeam).changeCounterespionageTurnsLeftAgainstTeam(iTeamX, - min(10 ** iIndex, gc.getTeam(self.iTeam).getCounterespionageTurnsLeftAgainstTeam(iTeamX)))
		self.interfaceScreen(self.iPlayer)
		return 1

	def handlePlatyCurrentMemoryCB ( self, argsList ) :
		self.iMemory = int(argsList)
		self.interfaceScreen(self.iPlayer)
		return 1

	def handlePlatyChangeAttitudeCB (self, iPlayer, iChange):
		pPlayer = gc.getPlayer(iPlayer)
		if pPlayer.isBarbarian() or pPlayer.isMinorCiv():
			self.interfaceScreen(self.iPlayer)
			return 1
		if self.RelationshipStatus(pPlayer.getTeam(), self.iTeam) == 0:
			self.interfaceScreen(self.iPlayer)
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
		self.interfaceScreen(self.iPlayer)
		return 1

	def handlePlatyChangeMemoryCB (self, iPlayer, iChange):
		iPlayer2 = iPlayer
		pPlayer1 = gc.getPlayer(self.iPlayer)
		if self.bTowardsPlayer:
			pPlayer1 = pPlayer
			iPlayer2 = self.iPlayer
		pPlayer1.AI_changeMemoryCount(iPlayer2, self.iMemory, iChange)
		if pPlayer1.AI_getMemoryCount (iPlayer2, self.iMemory) < 0:
			pPlayer1.AI_changeMemoryCount(iPlayer2, self.iMemory, - pPlayer1.AI_getMemoryCount (iPlayer2, self.iMemory))
		self.interfaceScreen(self.iPlayer)
		return 1

	def handlePlatyChangeWarWearinessCB (self, iTeam, iChange):
		iTeam2 = iTeam
		iTeam1 = self.iTeam
		if self.bTowardsPlayer:
			iTeam1 = iTeam
			iTeam2 = self.iTeam
		gc.getTeam(iTeam1).changeWarWeariness(iTeam2, iChange)
		self.interfaceScreen(self.iPlayer)
		return 1

	def handlePlatyWarWearinessCommandsCB (self, argsList) :
		iIndex = int(argsList) - 1
		if iIndex < 5:
			for iTeamX in xrange(gc.getMAX_CIV_TEAMS()):
				if iTeamX == self.iTeam: continue
				pTeamX = gc.getTeam(iTeamX)
				if not pTeamX.isAlive(): continue
				if not pTeamX.isHasMet(self.iTeam): continue
				if self.bTowardsPlayer:
					pTeamX.changeWarWeariness(self.iTeam, 10 ** iIndex)
				else:
					gc.getTeam(self.iTeam).changeWarWeariness(iTeamX, 10 ** iIndex)
		else:
			iIndex -= 5
			for iTeamX in xrange(gc.getMAX_CIV_TEAMS()):
				if iTeamX == self.iTeam: continue
				pTeamX = gc.getTeam(iTeamX)
				if not pTeamX.isAlive(): continue
				if not pTeamX.isHasMet(self.iTeam): continue
				if self.bTowardsPlayer:
					pTeamX.changeWarWeariness(self.iTeam, -10 ** iIndex)
				else:
					gc.getTeam(self.iTeam).changeWarWeariness(iTeamX, -10 ** iIndex)
		self.interfaceScreen(self.iPlayer)
		return 1

	def handlePlatyAttitudeCommandsCB (self, argsList) :
		iNewAttitude = int(argsList) -1
		for iPlayerX in xrange(gc.getMAX_CIV_PLAYERS()):
			pPlayerX = gc.getPlayer(iPlayerX)
			if not pPlayerX.isAlive(): continue
			iTeamX = pPlayerX.getTeam()
			if iTeamX == self.iTeam: continue
			if not gc.getTeam(iTeamX).isHasMet(self.iTeam): continue
			if self.RelationshipStatus(iTeamX, self.iTeam) == 0: continue
			if self.bTowardsPlayer:
				while iNewAttitude != pPlayerX.AI_getAttitude(self.iPlayer):
					if iNewAttitude > pPlayerX.AI_getAttitude(self.iPlayer):
						pPlayerX.AI_changeAttitudeExtra(self.iPlayer, 1)
					else:
						pPlayerX.AI_changeAttitudeExtra(self.iPlayer, -1)
			else:
				while iNewAttitude != gc.getPlayer(self.iPlayer).AI_getAttitude(iPlayerX):
					if iNewAttitude > gc.getPlayer(self.iPlayer).AI_getAttitude(iPlayerX):
						gc.getPlayer(self.iPlayer).AI_changeAttitudeExtra(iPlayerX, 1)
					else:
						gc.getPlayer(self.iPlayer).AI_changeAttitudeExtra(iPlayerX, -1)
		self.interfaceScreen(self.iPlayer)
		return 1

	def RelationshipStatus(self, iTeam1, iTeam2):
		if not self.bTowardsPlayer:
			iTemp = iTeam2
			iTeam2 = iTeam1
			iTeam1 = iTemp
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