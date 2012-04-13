# Sid Meier's Civilization 4
# Copyright Firaxis Games 2005

#
# Sevopedia 2.3
#   sevotastic.blogspot.com
#   sevotastic@yahoo.com
#
# additional work by Gaurav, Progor, Ket, Vovan, Fitchn, LunarMongoose
# see ReadMe for details
#

from CvPythonExtensions import *
import CvUtil
import ScreenInput
import SevoScreenEnums
import string

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class SevoPediaImprovement:

	def __init__(self, main):
		self.iImprovement = -1
		self.top = main

##--------	BUGFfH: Modofied by Denev 2009/10/08
		X_MERGIN = self.top.X_MERGIN
		Y_MERGIN = self.top.Y_MERGIN

		self.X_UPPER_PANE = self.top.X_PEDIA_PAGE
		self.Y_UPPER_PANE = self.top.Y_PEDIA_PAGE
		self.W_UPPER_PANE = 323
		self.H_UPPER_PANE = 116

		self.W_ICON = 100
		self.H_ICON = 100
		self.X_ICON = self.X_UPPER_PANE + (self.H_UPPER_PANE - self.H_ICON) / 2
		self.Y_ICON = self.Y_UPPER_PANE + (self.H_UPPER_PANE - self.H_ICON) / 2
		self.ICON_SIZE = 64

		self.X_STATUS = self.X_UPPER_PANE + self.W_ICON + X_MERGIN
		self.Y_STATUS = self.Y_UPPER_PANE
		self.W_STATUS = self.W_UPPER_PANE - self.W_ICON - X_MERGIN
		self.H_STATUS = self.H_UPPER_PANE

		self.W_UPGRADES_TO = 170
		self.X_UPGRADES_TO = self.X_UPPER_PANE + self.W_UPPER_PANE - self.W_UPGRADES_TO
		self.Y_UPGRADES_TO = self.Y_UPPER_PANE + self.H_UPPER_PANE + Y_MERGIN
		self.H_UPGRADES_TO = 110

		self.X_REQUIRES = self.X_UPPER_PANE
		self.Y_REQUIRES = self.Y_UPGRADES_TO
		self.W_REQUIRES = self.X_UPGRADES_TO - self.X_UPPER_PANE - X_MERGIN
		self.H_REQUIRES = self.H_UPGRADES_TO

		self.X_IMPROVENEMT_ANIMATION = self.X_UPPER_PANE + self.W_UPPER_PANE + X_MERGIN
		self.W_IMPROVENEMT_ANIMATION = self.top.R_PEDIA_PAGE - self.X_IMPROVENEMT_ANIMATION
		self.Y_IMPROVENEMT_ANIMATION = self.Y_UPPER_PANE + 7
		self.H_IMPROVENEMT_ANIMATION = self.Y_REQUIRES + self.H_REQUIRES - self.top.Y_PEDIA_PAGE - 7
		self.X_ROTATION_IMPROVENEMT_ANIMATION = -20
		self.Z_ROTATION_IMPROVENEMT_ANIMATION = 30
		self.SCALE_ANIMATION = 0.7

		self.W_HISTORY = 300
		self.X_HISTORY = self.top.R_PEDIA_PAGE - self.W_HISTORY
		self.Y_HISTORY = self.Y_IMPROVENEMT_ANIMATION + self.H_IMPROVENEMT_ANIMATION + Y_MERGIN
		self.H_HISTORY = self.top.B_PEDIA_PAGE - self.Y_HISTORY

		self.W_BONUS_YIELDS = 200
		self.X_BONUS_YIELDS = self.top.R_PEDIA_PAGE - self.W_BONUS_YIELDS
		self.Y_BONUS_YIELDS = self.Y_IMPROVENEMT_ANIMATION + self.H_IMPROVENEMT_ANIMATION + Y_MERGIN
		self.H_BONUS_YIELDS = self.top.B_PEDIA_PAGE - self.Y_BONUS_YIELDS

		self.X_IMPROVEMENTS = self.X_UPPER_PANE
		self.Y_IMPROVEMENTS = self.Y_REQUIRES + self.H_REQUIRES + Y_MERGIN
		self.W_IMPROVEMENTS = self.X_BONUS_YIELDS - self.top.X_PEDIA_PAGE -X_MERGIN
		self.H_IMPROVEMENTS = 185

		self.X_EFFECTS = self.X_UPPER_PANE
		self.Y_EFFECTS = self.Y_IMPROVEMENTS + self.H_IMPROVEMENTS + Y_MERGIN
		self.W_EFFECTS = self.W_IMPROVEMENTS
		self.H_EFFECTS = self.top.B_PEDIA_PAGE - self.Y_EFFECTS

	def adjustPanePosition(self):
		X_MERGIN = self.top.X_MERGIN
		Y_MERGIN = self.top.Y_MERGIN

		self.W_UPPER_PANE = 236
		self.H_UPPER_PANE = self.W_UPPER_PANE

		self.W_ICON = 150
		self.H_ICON = 150
		self.X_ICON = self.X_UPPER_PANE + (self.H_UPPER_PANE - self.H_ICON) / 2
		self.Y_ICON = self.Y_UPPER_PANE + (self.H_UPPER_PANE - self.H_ICON) / 2

		self.X_IMPROVENEMT_ANIMATION = self.X_UPPER_PANE + self.W_UPPER_PANE + X_MERGIN
		self.W_IMPROVENEMT_ANIMATION = self.top.R_PEDIA_PAGE - self.X_IMPROVENEMT_ANIMATION
		self.H_IMPROVENEMT_ANIMATION = self.H_UPPER_PANE - 7

		self.W_IMPROVEMENTS = self.X_HISTORY - self.top.X_PEDIA_PAGE - X_MERGIN

		self.W_EFFECTS = self.W_IMPROVEMENTS
##--------	BUGFfH: End Modify



	def interfaceScreen(self, iImprovement):
		self.iImprovement = iImprovement
		screen = self.top.getScreen()

##--------	BUGFfH: Added by Denev 2009/08/16
		# Header...
		szHeader = u"<font=4b>" + gc.getImprovementInfo(self.iImprovement).getDescription() + u"</font>"
		szHeaderId = "PediaMainHeader"
		screen.setText(szHeaderId, "Background", szHeader, CvUtil.FONT_CENTER_JUSTIFY, self.top.X_SCREEN, self.top.Y_TITLE, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		# adjust pane position whether improvement is global or not
		if self.getImprovementType(iImprovement)==SevoScreenEnums.TYPE_UNIQUE_FEATURES:
			self.adjustPanePosition()
##--------	BUGFfH: End Add

		screen.addPanel( self.top.getNextWidgetName(), "", "", False, False, self.X_UPPER_PANE, self.Y_UPPER_PANE, self.W_UPPER_PANE, self.H_UPPER_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_MAIN)
		screen.addDDSGFC(self.top.getNextWidgetName(), gc.getImprovementInfo(self.iImprovement).getButton(), self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		screen.addImprovementGraphicGFC(self.top.getNextWidgetName(), self.iImprovement, self.X_IMPROVENEMT_ANIMATION, self.Y_IMPROVENEMT_ANIMATION, self.W_IMPROVENEMT_ANIMATION, self.H_IMPROVENEMT_ANIMATION, WidgetTypes.WIDGET_GENERAL, -1, -1, self.X_ROTATION_IMPROVENEMT_ANIMATION, self.Z_ROTATION_IMPROVENEMT_ANIMATION, self.SCALE_ANIMATION, True)

##--------	BUGFfH: Modofied by Denev 2009/08/14
		"""
		self.placeSpecial()
		self.placeBonusYield()
		self.placeYield()
		self.placeRequires()
		"""
		self.placeYield()
		self.placeSpecial(self.getImprovementType(iImprovement)==SevoScreenEnums.TYPE_UNIQUE_FEATURES)
		if self.getImprovementType(iImprovement)==SevoScreenEnums.TYPE_UNIQUE_FEATURES:
			self.placeHistory()
		else:			
			self.placeStatus()
			self.placeRequires()
			self.placeUpgradesTo()
			self.placeBonusYield()
##--------	BUGFfH: End Modify



##--------	BUGFfH: Modofied by Denev 2009/10/08
	def placeStatus(self):
		screen = self.top.getScreen()

		panelTitle = self.top.getNextWidgetName()
		screen.addListBoxGFC(panelTitle, "", self.X_STATUS, self.Y_STATUS + 10, self.W_STATUS, self.H_STATUS - 10, TableStyles.TABLE_STYLE_EMPTY)
		screen.enableSelect(panelTitle, False)

		szCostTitle = localText.getText("TXT_KEY_PEDIA_IMPROVEMENT_COST_TITLE", ())
		screen.appendListBoxStringNoUpdate(panelTitle, u"<font=3>" + szCostTitle.upper() + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

		panelBody = self.top.getNextWidgetName()

		lBuildCostText = []
		for iLoopBuild in range(gc.getNumBuildInfos()):
			if gc.getBuildInfo(iLoopBuild).getImprovement() == self.iImprovement:
				buildInfo = gc.getBuildInfo(iLoopBuild)
				lWorkableUnitClassList = self.getWorkableUnitClassList(iLoopBuild)
				for iLoopUnitClass in lWorkableUnitClassList:
					iWorkableUnit = gc.getUnitClassInfo(iLoopUnitClass).getDefaultUnitIndex()
					pWorkableUnit = gc.getUnitInfo(iWorkableUnit)

					iWorkerTurns = buildInfo.getTime() // pWorkableUnit.getWorkRate()
					if buildInfo.getTime()%pWorkableUnit.getWorkRate():
						iWorkerTurns += 1
					iWorkerTurns = max(1, iWorkerTurns)

					szLinkedName = u"<link=%s>%s</link>" % (pWorkableUnit.getType(), pWorkableUnit.getDescription())

					if not buildInfo.isKill():
						szReqWorkerTurns = localText.getText("TXT_KEY_PEDIA_IMPROVEMENT_COST", (iWorkerTurns, szLinkedName))
					else:
						if iWorkerTurns == 1:
							szReqWorkerTurns = localText.getText("TXT_KEY_PEDIA_IMPROVEMENT_COST_KILL", (szLinkedName, ))
						else:
							szReqWorkerTurns = localText.getText("TXT_KEY_PEDIA_IMPROVEMENT_COST_KILL_MULTIPLE", (iWorkerTurns, szLinkedName))
					lBuildCostText.append(u"<font=3>" + szReqWorkerTurns + u"</font>")

				if lBuildCostText:
					textName = self.top.getNextWidgetName()
					szBuildCostText = "\n".join(lBuildCostText)
					screen.addMultilineText(textName, szBuildCostText, self.X_STATUS + 5, self.Y_STATUS + 30, self.W_STATUS - 5, self.H_STATUS - 32, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)	

					screen.updateListBox(panelTitle)
					screen.updateListBox(panelBody)
				break
##--------	BUGFfH: End Add



##--------	BUGFfH: Modofied by Denev 2009/10/08
	def placeYield(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_BASE_YIELDS", ()), "", true, true,
				 self.X_IMPROVEMENTS, self.Y_IMPROVEMENTS, self.W_IMPROVEMENTS, self.H_IMPROVEMENTS, PanelStyles.PANEL_STYLE_BLUE50 )
		listName = self.top.getNextWidgetName()
		screen.attachListBoxGFC( panelName, listName, "", TableStyles.TABLE_STYLE_EMPTY )
		screen.enableSelect(listName, False)
		info = gc.getImprovementInfo(self.iImprovement)
		for k in range(YieldTypes.NUM_YIELD_TYPES):
			iYieldChange = gc.getImprovementInfo(self.iImprovement).getYieldChange(k)
			if (iYieldChange != 0):
				szYield = u""
				if (iYieldChange > 0):
					sign = "+"
				else:
					sign = ""
				szYield += (u"%s: %s%i%c" % (gc.getYieldInfo(k).getDescription(), sign, iYieldChange, gc.getYieldInfo(k).getChar()))
				screen.appendListBoxString( listName, szYield, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )

		for k in range(YieldTypes.NUM_YIELD_TYPES):
			iYieldChange = gc.getImprovementInfo(self.iImprovement).getIrrigatedYieldChange(k)
			if (iYieldChange != 0):
				szYield = localText.getText("TXT_KEY_PEDIA_IRRIGATED_YIELD", (gc.getYieldInfo(k).getTextKey(), iYieldChange, gc.getYieldInfo(k).getChar()))
				screen.appendListBoxString( listName, szYield, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )

		for k in range(YieldTypes.NUM_YIELD_TYPES):
			iYieldChange = gc.getImprovementInfo(self.iImprovement).getHillsYieldChange(k)
			if (iYieldChange != 0):
				szYield = localText.getText("TXT_KEY_PEDIA_HILLS_YIELD", (gc.getYieldInfo(k).getTextKey(), iYieldChange, gc.getYieldInfo(k).getChar()))
				screen.appendListBoxString( listName, szYield, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )

		for k in range(YieldTypes.NUM_YIELD_TYPES):
			iYieldChange = gc.getImprovementInfo(self.iImprovement).getRiverSideYieldChange(k)
			if (iYieldChange != 0):
				szYield = localText.getText("TXT_KEY_PEDIA_RIVER_YIELD", (gc.getYieldInfo(k).getTextKey(), iYieldChange, gc.getYieldInfo(k).getChar()))
				screen.appendListBoxString( listName, szYield, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )

		for iTech in range(gc.getNumTechInfos()):
			for k in range(YieldTypes.NUM_YIELD_TYPES):
				iYieldChange = gc.getImprovementInfo(self.iImprovement).getTechYieldChanges(iTech, k)
				if (iYieldChange != 0):
					szYield = localText.getText("TXT_KEY_PEDIA_TECH_YIELD", (gc.getYieldInfo(k).getTextKey(), iYieldChange, gc.getYieldInfo(k).getChar(), gc.getTechInfo(iTech).getDescription()))
					screen.appendListBoxString( listName, szYield, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )

		for iCivic in range(gc.getNumCivicInfos()):
			for k in range(YieldTypes.NUM_YIELD_TYPES):
				iYieldChange = gc.getCivicInfo(iCivic).getImprovementYieldChanges(self.iImprovement, k)
				if (iYieldChange != 0):
					szYield = localText.getText("TXT_KEY_PEDIA_TECH_YIELD", (gc.getYieldInfo(k).getTextKey(), iYieldChange, gc.getYieldInfo(k).getChar(), gc.getCivicInfo(iCivic).getDescription()))
					screen.appendListBoxString( listName, szYield, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )

		for iRoute in range(gc.getNumRouteInfos()):
			for k in range(YieldTypes.NUM_YIELD_TYPES):
				iYieldChange = gc.getImprovementInfo(self.iImprovement).getRouteYieldChanges(iRoute, k)
				if (iYieldChange != 0):										
					szYield = localText.getText("TXT_KEY_PEDIA_ROUTE_YIELD", (gc.getYieldInfo(k).getTextKey(), iYieldChange, gc.getYieldInfo(k).getChar(), gc.getRouteInfo(iRoute).getTextKey())) + u"\n"
					screen.appendListBoxString( listName, szYield, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )



	def placeBonusYield(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_BONUS_YIELDS", ()), "", True, True, self.X_BONUS_YIELDS, self.Y_BONUS_YIELDS, self.W_BONUS_YIELDS, self.H_BONUS_YIELDS, PanelStyles.PANEL_STYLE_BLUE50 )
		info = gc.getImprovementInfo(self.iImprovement)
		for j in range(gc.getNumBonusInfos()):
			bFirst = True
			szYield = u""
			bEffect = False
			for k in range(YieldTypes.NUM_YIELD_TYPES):
				iYieldChange = info.getImprovementBonusYield(j, k)
				if (iYieldChange != 0):
					bEffect = True
					# Uncomment for 3.13 behavior. Note that Uranium shows incorrect hammer yield (should be +2)
					#iYieldChange += info.getYieldChange(k)
					if (bFirst):
						bFirst = False
					else:
						szYield += u", "
					if (iYieldChange > 0):
						sign = u"+"
					else:
						sign = u""
					szYield += (u"%s%i%c" % (sign, iYieldChange, gc.getYieldInfo(k).getChar()))
			if (bEffect):
				childPanelName = self.top.getNextWidgetName()
				screen.attachPanel(panelName, childPanelName, "", "", False, False, PanelStyles.PANEL_STYLE_EMPTY)
				screen.attachLabel(childPanelName, "", "  ")
				screen.attachImageButton( childPanelName, "", gc.getBonusInfo(j).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, j, 1, False )
				screen.attachLabel(childPanelName, "", u"<font=4>" + szYield + u"</font>")



	def placeRequires(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_REQUIRES", ()), "", False, True, self.X_REQUIRES, self.Y_REQUIRES, self.W_REQUIRES, self.H_REQUIRES, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.attachLabel(panelName, "", "  ")
		for iBuild in range(gc.getNumBuildInfos()):
			if (gc.getBuildInfo(iBuild).getImprovement() == self.iImprovement):
				iTech = gc.getBuildInfo(iBuild).getTechPrereq()
				if (iTech > -1):
					screen.attachImageButton( panelName, "", gc.getTechInfo(iTech).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iTech, 1, False )

##--------	BUGFfH: Added by Denev 2009/10/08
		#Civilization Requirement
		iCivPrereq = gc.getImprovementInfo(self.iImprovement).getPrereqCivilization()
		if iCivPrereq != CivilizationTypes.NO_CIVILIZATION:
			screen.attachImageButton( panelName, "", gc.getCivilizationInfo(iCivPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, iCivPrereq, 1, False )
##--------	BUGFfH: End Add



##--------	BUGFfH: Added by Denev 2009/10/08
	def placeUpgradesTo(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_UPGRADES_TO", ()), "", False, True, self.X_UPGRADES_TO, self.Y_UPGRADES_TO, self.W_UPGRADES_TO, self.H_UPGRADES_TO, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.attachLabel(panelName, "", "  ")

		iUpgradesTo = gc.getImprovementInfo(self.iImprovement).getImprovementUpgrade()
		if iUpgradesTo != ImprovementTypes.NO_IMPROVEMENT:
			szButton = gc.getImprovementInfo(iUpgradesTo).getButton()
			szUpgradeTurns = localText.getText("INTERFACE_CITY_TURNS", (CyGame().getImprovementUpgradeTime(self.iImprovement), ))

			childPanelName = self.top.getNextWidgetName()
			screen.attachPanel(panelName, childPanelName, "", "", False, False, PanelStyles.PANEL_STYLE_EMPTY)
			screen.attachImageButton(childPanelName, "", szButton, GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_IMPROVEMENT, iUpgradesTo, 1, False )
			screen.attachLabel(childPanelName, "", szUpgradeTurns)
##--------	BUGFfH: End Add



##--------	BUGFfH: Modofied by Denev 2009/10/08
#	def placeSpecial(self):
	def placeSpecial(self, bGlobal):
##--------	BUGFfH: End Modify
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
##--------	BUGFfH: Modofied by Denev 2009/10/08
#		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_EFFECTS", ()), "", True, False, self.X_EFFECTS, self.Y_EFFECTS, self.W_EFFECTS, self.H_EFFECTS, PanelStyles.PANEL_STYLE_BLUE50 )
		szPanelTitle = localText.getText("TXT_KEY_PEDIA_EFFECTS", ())
		if not bGlobal:
			szPanelTitle += localText.getText("TXT_KEY_OR", ()) + localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY", ())
		screen.addPanel( panelName, szPanelTitle, "", True, False, self.X_EFFECTS, self.Y_EFFECTS, self.W_EFFECTS, self.H_EFFECTS, PanelStyles.PANEL_STYLE_BLUE50 )
##--------	BUGFfH: End Add

		listName = self.top.getNextWidgetName()
		szSpecialText = CyGameTextMgr().getImprovementHelp(self.iImprovement, True)

##--------	BUGFfH: Modofied by Denev 2009/10/08
#		screen.addMultilineText(listName, szSpecialText, self.X_EFFECTS+5, self.Y_EFFECTS+5, self.W_EFFECTS-10, self.H_EFFECTS-10, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		if not bGlobal:
			if len(gc.getImprovementInfo(self.iImprovement).getCivilopedia()) > 0:
				szSpecialText += u"\n\n"
				szSpecialText += localText.getText("TXT_KEY_CIVILOPEDIA_BACKGROUND", ())
				szSpecialText += gc.getImprovementInfo(self.iImprovement).getCivilopedia()
		szSpecialText = szSpecialText.strip("\n")	#trim empty lines
		screen.addMultilineText(listName, szSpecialText, self.X_EFFECTS + 5, self.Y_EFFECTS + 30, self.W_EFFECTS - 5, self.H_EFFECTS - 32, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
##--------	BUGFfH: End Add



##--------	BUGFfH: Added by Denev 2009/08/14
	def placeHistory(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY", ()), "", True, True, self.X_HISTORY, self.Y_HISTORY, self.W_HISTORY, self.H_HISTORY, PanelStyles.PANEL_STYLE_BLUE50)
		textName = self.top.getNextWidgetName()
		szText = u""
		if len(gc.getImprovementInfo(self.iImprovement).getStrategy()) > 0:
			szText += localText.getText("TXT_KEY_CIVILOPEDIA_STRATEGY", ())
			szText += gc.getImprovementInfo(self.iImprovement).getStrategy()
			szText += u"\n\n"
		szText += localText.getText("TXT_KEY_CIVILOPEDIA_BACKGROUND", ())
		szText += gc.getImprovementInfo(self.iImprovement).getCivilopedia()
		screen.addMultilineText(textName, szText, self.X_HISTORY + 5, self.Y_HISTORY + 30, self.W_HISTORY - 5, self.H_HISTORY - 32, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def getWorkableUnitClassList(self, iBuild):
		lWorkableUnitClassList = []
		for iLoopUnit in range(gc.getNumUnitInfos()):
			pUnit = gc.getUnitInfo(iLoopUnit)
			if pUnit.getBuilds(iBuild):
				iUnitClass = pUnit.getUnitClassType()
				if not isWorldUnitClass(iUnitClass):
					if not isTeamUnitClass(iUnitClass):
#						if not isNationalUnitClass(iUnitClass):
							if pUnit.getProductionCost() > 0:
								lWorkableUnitClassList.append(iUnitClass)
		lWorkableUnitClassList = sorted(set(lWorkableUnitClassList))
		return lWorkableUnitClassList
##--------	BUGFfH: End Add



##--------	BUGFfH: Added by Denev 2009/08/12 (from CvPediaImprovement.py by Kael)
	def getImprovementType(self, iImprovement):
		if (gc.getImprovementInfo(iImprovement).isUnique()):
			return SevoScreenEnums.TYPE_UNIQUE_FEATURES
#		if gc.getImprovementInfo(iImprovement).getImprovementClassType()==0:
#			return SevoScreenEnums.TYPE_PRIMARY		
#		if gc.getImprovementInfo(iImprovement).getImprovementClassType()==1:
#			return SevoScreenEnums.TYPE_SECONDARY				
		# regular Improvement #
		return SevoScreenEnums.TYPE_REGULAR				
##--------	BUGFfH: End Add



	def handleInput (self, inputClass):
		return 0
