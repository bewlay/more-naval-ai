from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums
import WBProjectScreen
import WBTechScreen
import WBPlayerScreen
import WBPlayerUnits
gc = CyGlobalContext()
iImprovementType = -1
iChange = 1

class WBTeamScreen:

	def __init__(self, main):
		self.top = main
		self.iImprovement_Y = 80
		self.iAbilities_Y = 270
		self.iRoutes_Y = self.iAbilities_Y + 150
		self.iVotes_Y = self.iAbilities_Y + 13 * 24 + 52
		self.iYieldType = 0

	def interfaceScreen(self, iTeamX):
		screen = CyGInterfaceScreen( "WBTeamScreen", CvScreenEnums.WB_TEAM)
		global iTeam
		global pTeam
		iTeam = iTeamX
		pTeam = gc.getTeam(iTeam)

		screen.setRenderInterfaceOnly(True)
		screen.addPanel( "MainBG", u"", u"", True, False, -10, -10, screen.getXResolution() + 20, screen.getYResolution() + 20, PanelStyles.PANEL_STYLE_MAIN )
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)

		screen.setText("TeamExit", "Background", "<font=4>" + CyTranslator().getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 30, screen.getYResolution() - 42, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )
		screen.setLabel("MemberHeader", "Background", "<font=3b>" + CyTranslator().getText("TXT_KEY_WB_MEMBERS",()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution() * 3/8, self.iImprovement_Y - 30, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setLabel("DomainHeader", "Background", "<font=3b>" + CyTranslator().getText("TXT_KEY_WB_DOMAIN_MOVES",()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution() * 3/8, self.iAbilities_Y - 30, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setLabel("RouteHeader", "Background", "<font=3b>" + CyTranslator().getText("TXT_KEY_WB_ROUTE_CHANGE",()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution() * 3/8, self.iRoutes_Y - 30, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setLabel("VoteHeader", "Background", "<font=3b>" + CyTranslator().getText("TXT_KEY_WB_GUARANTEED_ELIGIBILITY",()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/8, self.iVotes_Y - 30, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		
		screen.addDropDownBoxGFC("CurrentPage", 20, screen.getYResolution() - 42, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_HELP4", ()), 0, 0, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_TEAM_DATA", ()), 1, 1, True)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_PROJECT", ()), 2, 2, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_TECH", ()), 3, 3, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_UNIT", ()) + " + " + CyTranslator().getText("TXT_KEY_CONCEPT_CITIES", ()), 4, 4, False)

		screen.addTableControlGFC("YieldType", YieldTypes.NUM_YIELD_TYPES, screen.getXResolution() - 20 - 25 * YieldTypes.NUM_YIELD_TYPES, 50, 25 * YieldTypes.NUM_YIELD_TYPES, 25, False, False, 24, 24, TableStyles.TABLE_STYLE_EMPTY)
		screen.appendTableRow("YieldType")
		for i in xrange(YieldTypes.NUM_YIELD_TYPES):
			screen.setTableColumnHeader("YieldType", i, "", 24)
			sText = u"<font=4>%c</font>" %(gc.getYieldInfo(i).getChar())
			screen.setTableText("YieldType", i, 0, sText, "", WidgetTypes.WIDGET_PYTHON, 7880, i, CvUtil.FONT_LEFT_JUSTIFY )
		
		screen.addDropDownBoxGFC("ChangeBy", 20, 110, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		i = 1
		while i < 101:
			screen.addPullDownString("ChangeBy", CyTranslator().getText("TXT_KEY_WB_CHANGE_BY",(i,)), i, i, iChange == i)
			if str(i)[0] == "1":
				i *= 5
			else:
				i *= 2

		global lImprovements
		global lRoutes
##		global lVoteBuildings#magister
		global lAbilities

		lImprovements = []
		for i in xrange(gc.getNumImprovementInfos()):
			ItemInfo = gc.getImprovementInfo(i)
			if ItemInfo.isGraphicalOnly(): continue
			lImprovements.append([ItemInfo.getDescription(), i])
		lImprovements.sort()

		lRoutes = []
		for i in xrange(gc.getNumRouteInfos()):
			ItemInfo = gc.getRouteInfo(i)
			lRoutes.append([ItemInfo.getDescription(), i])
		lRoutes.sort()
#magister
##		lVoteBuildings = []
##		for i in xrange(gc.getNumVoteSourceInfos()):
##			iVoteBuilding = -1
##			for j in xrange(gc.getNumBuildingInfos()):
##				if gc.getBuildingInfo(j).getVoteSourceType() == i:
##					iVoteBuilding = j
##					break
##			if iVoteBuilding == -1: continue
##			lVoteBuildings.append([gc.getBuildingInfo(iVoteBuilding).getDescription(), iVoteBuilding])
##		lVoteBuildings.sort()

		lAbilities = []
		for i in xrange(13):
			lAbilities.append([WidgetTypes.WIDGET_GENERAL, -1])
		for i in xrange(gc.getNumTechInfos()):
			ItemInfo = gc.getTechInfo(i)
			if ItemInfo.isMapCentering():
				lAbilities[0][0] = WidgetTypes.WIDGET_HELP_MAP_CENTER
				lAbilities[0][1] = i
			if ItemInfo.isMapTrading():
				lAbilities[1][0] = WidgetTypes.WIDGET_HELP_MAP_TRADE
				lAbilities[1][1] = i
			if ItemInfo.isTechTrading():
				lAbilities[2][0] = WidgetTypes.WIDGET_HELP_TECH_TRADE
				lAbilities[2][1] = i
			if ItemInfo.isGoldTrading():
				lAbilities[3][0] = WidgetTypes.WIDGET_HELP_GOLD_TRADE
				lAbilities[3][1] = i
			if ItemInfo.isOpenBordersTrading():
				lAbilities[4][0] = WidgetTypes.WIDGET_HELP_OPEN_BORDERS
				lAbilities[4][1] = i
			if ItemInfo.isDefensivePactTrading():
				lAbilities[5][0] = WidgetTypes.WIDGET_HELP_DEFENSIVE_PACT
				lAbilities[5][1] = i
			if ItemInfo.isPermanentAllianceTrading():
				lAbilities[6][0] = WidgetTypes.WIDGET_HELP_PERMANENT_ALLIANCE
				lAbilities[6][1] = i
			if ItemInfo.isVassalStateTrading():
				lAbilities[7][0] = WidgetTypes.WIDGET_HELP_VASSAL_STATE
				lAbilities[7][1] = i
			if ItemInfo.isBridgeBuilding():
				lAbilities[8][0] = WidgetTypes.WIDGET_HELP_BUILD_BRIDGE
				lAbilities[8][1] = i
			if ItemInfo.isIrrigation():
				lAbilities[9][0] = WidgetTypes.WIDGET_HELP_IRRIGATION
				lAbilities[9][1] = i
			if ItemInfo.isIgnoreIrrigation():
				lAbilities[10][0]= WidgetTypes.WIDGET_HELP_IGNORE_IRRIGATION
				lAbilities[10][1]= i
			if ItemInfo.isWaterWork():
				lAbilities[11][0] = WidgetTypes.WIDGET_HELP_WATER_WORK
				lAbilities[11][1] = i
			if ItemInfo.isExtraWaterSeeFrom():
				lAbilities[12][0] = WidgetTypes.WIDGET_HELP_LOS_BONUS
				lAbilities[12][1] = i

		self.placeStats()
		self.placeAbilities()
		self.placeImprovements()
		self.placeDomains()
		self.placeRoutes()
		self.placeVotes()

	def placeStats(self):
		screen = CyGInterfaceScreen( "WBTeamScreen", CvScreenEnums.WB_TEAM)
		sText = "<font=4b>" + CyTranslator().getText("TXT_KEY_WB_TEAM_DATA",()).upper() + " (ID: " + str(iTeam) + ")</font>"
		screen.setLabel("TeamHeader", "Background", sText, CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		screen.addDropDownBoxGFC("CurrentTeam", 20, 50, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		for i in xrange(gc.getMAX_TEAMS()):
			if gc.getTeam(i).isAlive():
				iLeader = gc.getTeam(i).getLeaderID()
				sName = gc.getPlayer(iLeader).getName()
				if gc.getTeam(i).getNumMembers() > 1:
					sName += " + " + str(gc.getTeam(i).getNumMembers() -1) + " " + CyTranslator().getText("TXT_KEY_WB_MEMBERS", ())
				screen.addPullDownString("CurrentTeam", sName, i, i, i == iTeam)

		screen.addDropDownBoxGFC("MergeTeam", 20, 80, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("MergeTeam", CyTranslator().getText("TXT_KEY_WB_MERGE_TEAM",()), -1, -1, True)
		for i in xrange(gc.getMAX_TEAMS()):
			if gc.getTeam(i).isAlive():
				if i == iTeam: continue
				iLeader = gc.getTeam(i).getLeaderID()
				sName = gc.getPlayer(iLeader).getName()
				if gc.getTeam(i).getNumMembers() > 1:
					sName += " " + CyTranslator().getText("TXT_KEY_WB_TEAM_MEMBERS", (gc.getTeam(i).getNumMembers() -1,))
				screen.addPullDownString("MergeTeam", sName, i, i, False)

		screen.setButtonGFC("NukeInterceptionPlus", u"", "", 20, 160, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("NukeInterceptionMinus", u"", "", 45, 160, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = "<font=3>" + CyTranslator().getText("TXT_KEY_WB_NUKE_INTERCEPTION",(pTeam.getNukeInterception(),)) + "</font>"
		screen.setLabel("NukeInterceptionText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, 75, 160 + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		screen.setButtonGFC("EnemyWWPlus", u"", "", 20, 190, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("EnemyWWMinus", u"", "", 45, 190, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = "<font=3>" + CyTranslator().getText("TXT_KEY_WB_ENEMY_WAR_WEARINESS",(pTeam.getEnemyWarWearinessModifier(),)) + "</font>"
		screen.setLabel("EnemyWWText", "Background", sText, CvUtil.FONT_LEFT_JUSTIFY, 75, 190 + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iWidth = screen.getXResolution()/4
		iHeight = min(6, pTeam.getNumMembers()) * 24 + 2
		screen.addTableControlGFC("WBTeamMembers", 2, screen.getXResolution()/4, self.iImprovement_Y, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		screen.setTableColumnHeader( "WBTeamMembers", 0, "", iWidth/2)
		screen.setTableColumnHeader( "WBTeamMembers", 1, "", iWidth/2)
		for iPlayerX in xrange(gc.getMAX_PLAYERS()):
			pPlayerX = gc.getPlayer(iPlayerX)
			iTeamX = pPlayerX.getTeam()
			if iTeamX != iTeam: continue
			iRow = screen.appendTableRow("WBTeamMembers")
			sColor = u"<color=%d,%d,%d,%d>" %(pPlayerX.getPlayerTextColorR(), pPlayerX.getPlayerTextColorG(), pPlayerX.getPlayerTextColorB(), pPlayerX.getPlayerTextColorA())
			iCivilization = pPlayerX.getCivilizationType()
			sCiv = pPlayerX.getCivilizationShortDescription(0)
			iLeader = pPlayerX.getLeaderType()
			sName = pPlayerX.getName()
			if not pPlayerX.isAlive():
				sName = "*" + sName
				sCiv = "*" + sCiv
			if gc.getTeam(iTeamX).getLeaderID() == iPlayerX:
				sName = CyTranslator().getText("[ICON_STAR]", ()) + sName
				sCiv = CyTranslator().getText("[ICON_STAR]", ()) + sCiv
			screen.setTableText("WBTeamMembers", 0, iRow, "<font=3>" + sColor + sCiv + "</font></color>", gc.getCivilizationInfo(iCivilization).getButton(), WidgetTypes.WIDGET_PYTHON, 7872, iPlayerX * 10000 + iCivilization, CvUtil.FONT_LEFT_JUSTIFY )
			screen.setTableText("WBTeamMembers", 1, iRow, "<font=3>" + sColor + sName + "</font></color>", gc.getLeaderHeadInfo(iLeader).getButton(), WidgetTypes.WIDGET_PYTHON, 7876, iPlayerX * 10000 + iLeader, CvUtil.FONT_LEFT_JUSTIFY )
		
	def placeVotes(self):
##		screen = CyGInterfaceScreen( "WBTeamScreen", CvScreenEnums.WB_TEAM)
##		iWidth = screen.getXResolution()/5
##		iHeight = min(len(lVoteBuildings), (screen.getYResolution() - self.iVotes_Y - 40) /24) * 24 + 2
##		screen.addTableControlGFC("WBTeamVotes", 1, 20, self.iVotes_Y, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
##		screen.setTableColumnHeader( "WBTeamVotes", 0, "", iWidth)
##		for item in lVoteBuildings:
##			iVoteSource = gc.getBuildingInfo(item[1]).getVoteSourceType()
##			iRow = screen.appendTableRow("WBTeamVotes")
##			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
##			if pTeam.isForceTeamVoteEligible(iVoteSource):
##				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
##			screen.setTableText("WBTeamVotes", 0, iRow, "<font=3>" + sColor + item[0] + "</font></color>", gc.getBuildingInfo(item[1]).getButton(), WidgetTypes.WIDGET_HELP_BUILDING, item[1], -1, CvUtil.FONT_LEFT_JUSTIFY )


#magister

		screen = CyGInterfaceScreen( "WBTeamScreen", CvScreenEnums.WB_TEAM)
		iWidth = screen.getXResolution()/5
		iHeight = max(2, (screen.getYResolution() - self.iVotes_Y - 40) /24) * 24 + 2
		screen.addTableControlGFC("WBTeamVotes", 1, 20, self.iVotes_Y, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		screen.setTableColumnHeader( "WBTeamVotes", 0, "", iWidth)



		iVoteSource = gc.getInfoTypeForString('DIPLOVOTE_OVERCOUNCIL')
		iMembership = gc.getInfoTypeForString('CIVIC_OVERCOUNCIL')


		sButton = gc.getCivicInfo(iMembership).getButton()
		sDescription = gc.getCivicInfo(iMembership).getDescription()
		iRow = screen.appendTableRow("WBTeamVotes")
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if pTeam.isForceTeamVoteEligible(iVoteSource):
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		screen.setTableText("WBTeamVotes", 0, iRow, "<font=3>" + sColor + sDescription + "</font></color>", sButton, WidgetTypes.WIDGET_PYTHON, 8206, iMembership, CvUtil.FONT_LEFT_JUSTIFY )



		iVoteSource = gc.getInfoTypeForString('DIPLOVOTE_UNDERCOUNCIL')
		iMembership = gc.getInfoTypeForString('CIVIC_UNDERCOUNCIL')



		sButton = gc.getCivicInfo(iMembership).getButton()
		sDescription = gc.getCivicInfo(iMembership).getDescription()
		iRow = screen.appendTableRow("WBTeamVotes")
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if pTeam.isForceTeamVoteEligible(iVoteSource):
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		screen.setTableText("WBTeamVotes", 0, iRow, "<font=3>" + sColor + sDescription + "</font></color>", sButton, WidgetTypes.WIDGET_PYTHON, 8205, iMembership, CvUtil.FONT_LEFT_JUSTIFY )



#magister


	def placeRoutes(self):
		screen = CyGInterfaceScreen( "WBTeamScreen", CvScreenEnums.WB_TEAM)
		iWidth = screen.getXResolution()/4
		iHeight = min(len(lRoutes), (screen.getYResolution() - self.iImprovement_Y - 40) /24) * 24 + 2
		screen.addTableControlGFC("WBTeamRoutes", 4, screen.getXResolution()/4, self.iRoutes_Y, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		iWidth1 = 70
		iWidth2 = iWidth - (iWidth1 + 48)
		screen.setTableColumnHeader( "WBTeamRoutes", 0, "", iWidth2)
		screen.setTableColumnHeader( "WBTeamRoutes", 1, "", 24)
		screen.setTableColumnHeader( "WBTeamRoutes", 2, "", 24)
		screen.setTableColumnHeader( "WBTeamRoutes", 3, "", iWidth1)

		for item in lRoutes:
			iRow = screen.appendTableRow("WBTeamRoutes")
			ItemInfo = gc.getRouteInfo(item[1])
			screen.setTableText("WBTeamRoutes", 0, iRow, "<font=3>" + item[0] + "</font>", ItemInfo.getButton(), WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
			sText = u"%d%s" %(pTeam.getRouteChange(item[1]), CyTranslator().getText("[ICON_MOVES]", ()))
			screen.setTableText("WBTeamRoutes", 1, iRow, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_PLUS").getPath(), WidgetTypes.WIDGET_PYTHON, 1030, item[1], CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBTeamRoutes", 2, iRow, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_MINUS").getPath(), WidgetTypes.WIDGET_PYTHON, 1031, item[1], CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableInt("WBTeamRoutes", 3, iRow, "<font=3>" + sText + "</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY )

	def placeDomains(self):
		screen = CyGInterfaceScreen( "WBTeamScreen", CvScreenEnums.WB_TEAM)
		iWidth = screen.getXResolution()/4
		screen.addTableControlGFC("WBTeamDomainMoves", 4, screen.getXResolution()/4, self.iAbilities_Y, iWidth, 4 * 24 + 2, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		iWidth1 = 70
		iWidth2 = iWidth - (iWidth1 + 48)
		screen.setTableColumnHeader( "WBTeamDomainMoves", 0, "", iWidth2)
		screen.setTableColumnHeader( "WBTeamDomainMoves", 1, "", 24)
		screen.setTableColumnHeader( "WBTeamDomainMoves", 2, "", 24)
		screen.setTableColumnHeader( "WBTeamDomainMoves", 3, "", iWidth1)
		for i in xrange(DomainTypes.NUM_DOMAIN_TYPES):
			ItemInfo = gc.getDomainInfo(i)
			screen.appendTableRow("WBTeamDomainMoves")
			screen.setTableText("WBTeamDomainMoves", 0, i, "<font=3>" + ItemInfo.getDescription() + "</font>", ItemInfo.getButton(), WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
			sText = u"%d%s" %(pTeam.getExtraMoves(i), CyTranslator().getText("[ICON_MOVES]", ()))
			screen.setTableText("WBTeamDomainMoves", 1, i, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_PLUS").getPath(), WidgetTypes.WIDGET_PYTHON, 1030, i, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableText("WBTeamDomainMoves", 2, i, "", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_MINUS").getPath(), WidgetTypes.WIDGET_PYTHON, 1031, i, CvUtil.FONT_CENTER_JUSTIFY )
			screen.setTableInt("WBTeamDomainMoves", 3, i, "<font=3>" + sText + "</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY )

	def placeImprovements(self):
		screen = CyGInterfaceScreen( "WBTeamScreen", CvScreenEnums.WB_TEAM)
		global iImprovementType
		iWidth = screen.getXResolution() /2 - 40
		iHeight = min(len(lImprovements), (screen.getYResolution() - self.iImprovement_Y - 40) /24) * 24 + 2
		iColWidth = (iWidth - 8) / (YieldTypes.NUM_YIELD_TYPES + 2)
		screen.addTableControlGFC("WBTeamYield", YieldTypes.NUM_YIELD_TYPES + 2, screen.getXResolution()/2 + 20, self.iImprovement_Y, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		screen.setTableColumnHeader( "WBTeamYield", 0, "", iColWidth * 2)
		for i in xrange(YieldTypes.NUM_YIELD_TYPES):
			screen.setTableColumnHeader( "WBTeamYield", i + 1, "", iColWidth)
		screen.setTableColumnHeader( "WBTeamYield", YieldTypes.NUM_YIELD_TYPES + 1, "", 8)

		for item in lImprovements:
			if iImprovementType == -1:
				iImprovementType = item[1]
			ItemInfo = gc.getImprovementInfo(item[1])
			iRow = screen.appendTableRow("WBTeamYield")
			screen.setTableText("WBTeamYield", 0, iRow, "<font=3>" + item[0] + "</font>", ItemInfo.getButton(), WidgetTypes.WIDGET_PYTHON, 7877, item[1], CvUtil.FONT_LEFT_JUSTIFY )
			for j in xrange(YieldTypes.NUM_YIELD_TYPES):
				iYieldChange = pTeam.getImprovementYieldChange(item[1], j)
				sFont = "<font=3>"
				if abs(iYieldChange) > 99:
					sFont = "<font=2>"
				sText = u"%d%c" %(iYieldChange, gc.getYieldInfo(j).getChar())
				screen.setTableInt("WBTeamYield", j + 1, iRow, sFont + sText + "</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY )

		screen.setButtonGFC("ModifyImprovementPlus", "", "", screen.getXResolution()/2 + 20, self.iImprovement_Y - 30, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("ModifyImprovementMinus", "", "", screen.getXResolution()/2 + 45, self.iImprovement_Y - 30, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		sText = u"<font=3>%s%c</font>" %(CyTranslator().getText("TXT_KEY_WB_MODIFY", (gc.getImprovementInfo(iImprovementType).getDescription(),)), gc.getYieldInfo(self.iYieldType).getChar())
		screen.setLabel("ImprovementText", "Background", "<font=3>" + sText + "</font>", CvUtil.FONT_LEFT_JUSTIFY, screen.getXResolution()/2 + 75, self.iImprovement_Y - 30 + 1, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

	def placeAbilities(self):
		screen = CyGInterfaceScreen( "WBTeamScreen", CvScreenEnums.WB_TEAM)
		iWidth = screen.getXResolution()/5
		screen.setButtonGFC("AbilitiesAllPlus", u"", "", iWidth - 30, self.iAbilities_Y - 30, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("AbilitiesAllMinus", u"", "", iWidth - 5, self.iAbilities_Y - 30, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		screen.setLabel("AbilitiesHeader", "Background", "<font=4b>" + CyTranslator().getText("TXT_KEY_WB_CITY_ALL",()) + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, iWidth - 30, self.iAbilities_Y - 30, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		
		screen.addTableControlGFC("WBAbilities", 1, 20, self.iAbilities_Y, iWidth, 13 * 24 + 2, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		screen.setTableColumnHeader( "WBAbilities", 0, "", iWidth)
	
		iRow = screen.appendTableRow("WBAbilities")
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if pTeam.isMapCentering():
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		screen.setTableText("WBAbilities", 0, iRow, "<font=3>" + sColor + CyTranslator().getText("TXT_KEY_WB_MAP_CENTERING",()) + "</font></color>", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_TECH_MAPCENTER").getPath(), lAbilities[0][0], lAbilities[0][1], -1, CvUtil.FONT_LEFT_JUSTIFY )

		iRow = screen.appendTableRow("WBAbilities")
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if pTeam.isMapTrading():
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		screen.setTableText("WBAbilities", 0, iRow, "<font=3>" + sColor + CyTranslator().getText("TXT_KEY_WB_MAP_TRADING",()) + "</font></color>", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_TECH_MAPTRADING").getPath(), lAbilities[1][0], lAbilities[1][1], -1, CvUtil.FONT_LEFT_JUSTIFY )

		iRow = screen.appendTableRow("WBAbilities")
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if pTeam.isTechTrading():
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		screen.setTableText("WBAbilities", 0, iRow, "<font=3>" + sColor + CyTranslator().getText("TXT_KEY_WB_TECH_TRADING",()) + "</font></color>", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_TECH_TECHTRADING").getPath(), lAbilities[2][0], lAbilities[2][1], -1, CvUtil.FONT_LEFT_JUSTIFY )

		iRow = screen.appendTableRow("WBAbilities")
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if pTeam.isGoldTrading():
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		screen.setTableText("WBAbilities", 0, iRow, "<font=3>" + sColor + CyTranslator().getText("TXT_KEY_WB_GOLD_TRADING",()) + "</font></color>", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_TECH_GOLDTRADING").getPath(), lAbilities[3][0], lAbilities[3][1], -1, CvUtil.FONT_LEFT_JUSTIFY )

		iRow = screen.appendTableRow("WBAbilities")
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if pTeam.isOpenBordersTrading():
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		screen.setTableText("WBAbilities", 0, iRow, "<font=3>" + sColor + CyTranslator().getText("TXT_KEY_MISC_OPEN_BORDERS",()) + "</font></color>", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_TECH_OPENBORDERS").getPath(), lAbilities[4][0], lAbilities[4][1], -1, CvUtil.FONT_LEFT_JUSTIFY )

		iRow = screen.appendTableRow("WBAbilities")
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if pTeam.isDefensivePactTrading():
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		screen.setTableText("WBAbilities", 0, iRow, "<font=3>" + sColor + CyTranslator().getText("TXT_KEY_MISC_DEFENSIVE_PACT",()) + "</font></color>", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_TECH_DEFENSIVEPACT").getPath(), lAbilities[5][0], lAbilities[5][1], -1, CvUtil.FONT_LEFT_JUSTIFY )

		iRow = screen.appendTableRow("WBAbilities")
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if pTeam.isPermanentAllianceTrading():
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		screen.setTableText("WBAbilities", 0, iRow, "<font=3>" + sColor + CyTranslator().getText("TXT_KEY_MISC_PERMANENT_ALLIANCE",()) + "</font></color>", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_TECH_PERMALLIANCE").getPath(), lAbilities[6][0], lAbilities[6][1], -1, CvUtil.FONT_LEFT_JUSTIFY )

		iRow = screen.appendTableRow("WBAbilities")
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if pTeam.isVassalStateTrading():
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		screen.setTableText("WBAbilities", 0, iRow, "<font=3>" + sColor + CyTranslator().getText("TXT_KEY_WB_VASSAL_TRADING",()) + "</font></color>", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_TECH_VASSAL").getPath(), lAbilities[7][0], lAbilities[7][1], -1, CvUtil.FONT_LEFT_JUSTIFY )

		iRow = screen.appendTableRow("WBAbilities")
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if pTeam.isBridgeBuilding():
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		screen.setTableText("WBAbilities", 0, iRow, "<font=3>" + sColor + CyTranslator().getText("TXT_KEY_WB_BRIDGE_BUILDING",()) + "</font></color>", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_TECH_BRIDGEBUILDING").getPath(), lAbilities[8][0], lAbilities[8][1], -1, CvUtil.FONT_LEFT_JUSTIFY )

		iRow = screen.appendTableRow("WBAbilities")
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if pTeam.isIrrigation():
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		screen.setTableText("WBAbilities", 0, iRow, "<font=3>" + sColor + CyTranslator().getText("TXT_KEY_CONCEPT_IRRIGATION",()) + "</font></color>", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_TECH_IRRIGATION").getPath(), lAbilities[9][0], lAbilities[9][1], -1, CvUtil.FONT_LEFT_JUSTIFY )

		iRow = screen.appendTableRow("WBAbilities")
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if pTeam.isIgnoreIrrigation():
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		screen.setTableText("WBAbilities", 0, iRow, "<font=3>" + sColor + CyTranslator().getText("TXT_KEY_WB_IGNORE_IRRIGATION",()) + "</font></color>", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_TECH_NOIRRIGATION").getPath(), lAbilities[10][0], lAbilities[10][1], -1, CvUtil.FONT_LEFT_JUSTIFY )

		iRow = screen.appendTableRow("WBAbilities")
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if pTeam.isWaterWork():
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		screen.setTableText("WBAbilities", 0, iRow, "<font=3>" + sColor + CyTranslator().getText("TXT_KEY_WB_WATER_WORK",()) + "</font></color>", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_TECH_WATERWORK").getPath(), lAbilities[11][0], lAbilities[11][1], -1, CvUtil.FONT_LEFT_JUSTIFY )

		iRow = screen.appendTableRow("WBAbilities")
		sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
		if pTeam.isExtraWaterSeeFrom():
			sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
		screen.setTableText("WBAbilities", 0, iRow, "<font=3>" + sColor + CyTranslator().getText("TXT_KEY_WB_EXTRA_WATER_SIGHT",()) + "</font></color>", CyArtFileMgr().getInterfaceArtInfo("INTERFACE_TECH_LOS").getPath(), lAbilities[12][0], lAbilities[12][1], -1, CvUtil.FONT_LEFT_JUSTIFY )
	
	def handleInput (self, inputClass):
		screen = CyGInterfaceScreen( "WBTeamScreen", CvScreenEnums.WB_TEAM)
		global iImprovementType
		global iChange

		if inputClass.getFunctionName() == "ChangeBy":
			iIndex = screen.getSelectedPullDownID("ChangeBy")
			iChange = screen.getPullDownData("ChangeBy", iIndex)

		elif inputClass.getFunctionName() == "CurrentPage":
			iIndex = screen.getPullDownData("CurrentPage", screen.getSelectedPullDownID("CurrentPage"))
			if iIndex == 0:
				WBPlayerScreen.WBPlayerScreen(self.top).interfaceScreen(pTeam.getLeaderID())
			elif iIndex == 2:
				WBProjectScreen.WBProjectScreen(self.top).interfaceScreen(pTeam)
			elif iIndex == 3:
				WBTechScreen.WBTechScreen(self.top).interfaceScreen(pTeam)
			elif iIndex == 4:
				WBPlayerUnits.WBPlayerUnits(self.top).interfaceScreen(pTeam.getLeaderID())

		elif inputClass.getFunctionName() == "CurrentTeam":
			iIndex = screen.getSelectedPullDownID("CurrentTeam")
			iTeam = screen.getPullDownData("CurrentTeam", iIndex)
			self.interfaceScreen(iTeam)

		elif inputClass.getFunctionName() == "WBTeamMembers":
			if inputClass.getData1() == 7876 or inputClass.getData1() == 7872:
				iPlayer = inputClass.getData2() /10000
				WBPlayerScreen.WBPlayerScreen(self.top).interfaceScreen(iPlayer)

		elif inputClass.getFunctionName() == "MergeTeam":
			iIndex = screen.getSelectedPullDownID("MergeTeam")
			pTeam.addTeam(screen.getPullDownData("MergeTeam", iIndex))
			self.interfaceScreen(pTeam.getID())

		elif inputClass.getFunctionName().find("NukeInterception") > -1:
			if inputClass.getData1() == 1030:
				pTeam.changeNukeInterception(iChange)
			elif inputClass.getData1() == 1031:
				pTeam.changeNukeInterception(- iChange)
			self.placeStats()

		elif inputClass.getFunctionName().find("EnemyWW") > -1:
			if inputClass.getData1() == 1030:
				pTeam.changeEnemyWarWearinessModifier(iChange)
			elif inputClass.getData1() == 1031:
				pTeam.changeEnemyWarWearinessModifier(- iChange)
			self.placeStats()

		elif inputClass.getFunctionName() == "WBTeamRoutes":
			if inputClass.getData1() == 1030:
				pTeam.changeRouteChange(inputClass.getData2(), iChange)
			elif inputClass.getData1() == 1031:
				pTeam.changeRouteChange(inputClass.getData2(), - iChange)
			self.placeRoutes()

		elif inputClass.getFunctionName() == "WBTeamDomainMoves":
			if inputClass.getData1() == 1030:
				pTeam.changeExtraMoves(inputClass.getData2(), iChange)
			elif inputClass.getData1() == 1031:
				pTeam.changeExtraMoves(inputClass.getData2(), - iChange)
			self.placeDomains()

		elif inputClass.getFunctionName() == "YieldType":
			self.iYieldType = inputClass.getData2()
			self.placeImprovements()

		elif inputClass.getFunctionName() == "WBTeamYield":
			if inputClass.getData1() == 7877:
				iImprovementType = inputClass.getData2()
				self.placeImprovements()

		elif inputClass.getFunctionName().find("ModifyImprovement") > -1:
			if inputClass.getData1() == 1030:
				pTeam.changeImprovementYieldChange(iImprovementType, self.iYieldType, iChange)
			elif inputClass.getData1() == 1031:
				pTeam.changeImprovementYieldChange(iImprovementType, self.iYieldType, - iChange)
			self.placeImprovements()

		elif inputClass.getFunctionName() == "WBTeamVotes":
##			iVote = gc.getBuildingInfo(inputClass.getData1()).getVoteSourceType()
			iVote = inputClass.getData2()#magister

			if iVote == gc.getInfoTypeForString('CIVIC_OVERCOUNCIL'):
				iVote = gc.getInfoTypeForString('DIPLOVOTE_OVERCOUNCIL')

			if iVote == gc.getInfoTypeForString('CIVIC_UNDERCOUNCIL'):
				iVote = gc.getInfoTypeForString('DIPLOVOTE_UNDERCOUNCIL')

			if pTeam.isForceTeamVoteEligible(iVote):
				pTeam.changeForceTeamVoteEligibilityCount(iVote, - pTeam.getForceTeamVoteEligibilityCount(iVote))
			else:
				pTeam.changeForceTeamVoteEligibilityCount(iVote, 1)
			self.placeVotes()

		elif inputClass.getFunctionName().find("AbilitiesAll") > -1:
			for i in xrange(13):
				if inputClass.getData1() == 1030:
					self.doTeamAbilities(i, 1)
				elif inputClass.getData1() == 1031:
					self.doTeamAbilities(i, 0)
			self.placeAbilities()

		elif inputClass.getFunctionName() == "WBAbilities":
			iButton = inputClass.getButtonType()
			if iButton == WidgetTypes.WIDGET_HELP_MAP_CENTER:
				self.doTeamAbilities(0, -1)
			elif iButton == WidgetTypes.WIDGET_HELP_MAP_TRADE:
				self.doTeamAbilities(1, -1)
			elif iButton == WidgetTypes.WIDGET_HELP_TECH_TRADE:
				self.doTeamAbilities(2, -1)
			elif iButton == WidgetTypes.WIDGET_HELP_GOLD_TRADE:
				self.doTeamAbilities(3, -1)
			elif iButton == WidgetTypes.WIDGET_HELP_OPEN_BORDERS:
				self.doTeamAbilities(4, -1)
			elif iButton == WidgetTypes.WIDGET_HELP_DEFENSIVE_PACT:
				self.doTeamAbilities(5, -1)
			elif iButton == WidgetTypes.WIDGET_HELP_PERMANENT_ALLIANCE:
				self.doTeamAbilities(6, -1)
			elif iButton == WidgetTypes.WIDGET_HELP_VASSAL_STATE:
				self.doTeamAbilities(7, -1)
			elif iButton == WidgetTypes.WIDGET_HELP_BUILD_BRIDGE:
				self.doTeamAbilities(8, -1)
			elif iButton == WidgetTypes.WIDGET_HELP_IRRIGATION:
				self.doTeamAbilities(9, -1)
			elif iButton == WidgetTypes.WIDGET_HELP_IGNORE_IRRIGATION:
				self.doTeamAbilities(10, -1)
			elif iButton == WidgetTypes.WIDGET_HELP_WATER_WORK:
				self.doTeamAbilities(11, -1)
			elif iButton == WidgetTypes.WIDGET_HELP_LOS_BONUS:
				self.doTeamAbilities(12, -1)
			else:
				self.doTeamAbilities(inputClass.getData(), -1)
			self.placeAbilities()
		return 1

	def doTeamAbilities(self, i, iType):
		if i == 0:
			if iType == -1:
				pTeam.setMapCentering(not pTeam.isMapCentering())
			elif iType == 0:
				pTeam.setMapCentering(False)
			elif iType == 1:
				pTeam.setMapCentering(True)
		elif i == 1:
			if pTeam.isMapTrading():
				if iType !=1:
					pTeam.changeMapTradingCount( - pTeam.getMapTradingCount())
			elif iType != 0:
				pTeam.changeMapTradingCount(1)
		elif i == 2:
			if pTeam.isTechTrading():
				if iType !=1:
					pTeam.changeTechTradingCount( - pTeam.getTechTradingCount())
			elif iType != 0:
				pTeam.changeTechTradingCount(1)
		elif i == 3:
			if pTeam.isGoldTrading():
				if iType !=1:
					pTeam.changeGoldTradingCount( - pTeam.getGoldTradingCount())
			elif iType != 0:
				pTeam.changeGoldTradingCount(1)
		elif i == 4:
			if pTeam.isOpenBordersTrading():
				if iType !=1:
					pTeam.changeOpenBordersTradingCount( - pTeam.getOpenBordersTradingCount())
			elif iType != 0:
				pTeam.changeOpenBordersTradingCount(1)
		elif i == 5:
			if pTeam.isDefensivePactTrading():
				if iType !=1:
					pTeam.changeDefensivePactTradingCount( - pTeam.getDefensivePactTradingCount())
			elif iType != 0:
				pTeam.changeDefensivePactTradingCount(1)
		elif i == 6:
			if pTeam.isPermanentAllianceTrading():
				if iType !=1:
					pTeam.changePermanentAllianceTradingCount( - pTeam.getPermanentAllianceTradingCount())
			elif iType != 0:
				pTeam.changePermanentAllianceTradingCount(1)
		elif i == 7:
			if pTeam.isVassalStateTrading():
				if iType !=1:
					pTeam.changeVassalTradingCount( - pTeam.getVassalTradingCount())
			elif iType != 0:
				pTeam.changeVassalTradingCount(1)
		elif i == 8:
			if pTeam.isBridgeBuilding():
				if iType !=1:
					pTeam.changeBridgeBuildingCount( - pTeam.getBridgeBuildingCount())
			elif iType != 0:
				pTeam.changeBridgeBuildingCount(1)
		elif i == 9:
			if pTeam.isIrrigation():
				if iType !=1:
					pTeam.changeIrrigationCount( - pTeam.getIrrigationCount())
			elif iType != 0:
				pTeam.changeIrrigationCount(1)
		elif i == 10:
			if pTeam.isIgnoreIrrigation():
				if iType !=1:
					pTeam.changeIgnoreIrrigationCount( - pTeam.getIgnoreIrrigationCount())
			elif iType != 0:
				pTeam.changeIgnoreIrrigationCount(1)
		elif i == 11:
			if pTeam.isWaterWork():
				if iType !=1:
					pTeam.changeWaterWorkCount( - pTeam.getWaterWorkCount())
			elif iType != 0:
				pTeam.changeWaterWorkCount(1)
		elif i == 12:
			if pTeam.isExtraWaterSeeFrom():
				if iType !=1:
					pTeam.changeExtraWaterSeeFromCount( - pTeam.getExtraWaterSeeFromCount())
			elif iType != 0:
				pTeam.changeExtraWaterSeeFromCount(1)
	def update(self, fDelta):
		return 1