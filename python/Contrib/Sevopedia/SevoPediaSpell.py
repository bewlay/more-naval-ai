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

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class SevoPediaSpell:
	
	def __init__(self, main):
		self.iSpell = -1
		self.top = main

		X_MERGIN = self.top.X_MERGIN
		Y_MERGIN = self.top.Y_MERGIN

		self.X_MAIN_PANE = self.top.X_PEDIA_PAGE
		self.Y_MAIN_PANE = self.top.Y_PEDIA_PAGE
		self.W_MAIN_PANE = 300
		self.H_MAIN_PANE = 215

		self.W_ICON = 120
		self.H_ICON = 120
		self.X_ICON = self.X_MAIN_PANE + 30
		self.Y_ICON = self.Y_MAIN_PANE + (self.H_MAIN_PANE - self.H_ICON) / 2
		self.ICON_SIZE = 64

		self.X_STATUS = self.X_ICON + self.W_ICON + 10
		self.Y_STATUS = self.Y_ICON
		self.W_STATUS = self.X_MAIN_PANE + self.W_MAIN_PANE - self.X_STATUS
		self.H_STATUS = self.Y_MAIN_PANE + self.H_MAIN_PANE - self.Y_STATUS

		self.X_REQUIRES = self.X_MAIN_PANE + self.W_MAIN_PANE + X_MERGIN
#		self.W_REQUIRES = self.top.R_PEDIA_PAGE - self.X_REQUIRES
#		self.W_REQUIRES = (self.top.R_PEDIA_PAGE - self.X_REQUIRES) / 2 +15
		self.W_REQUIRES = (self.top.R_PEDIA_PAGE - self.X_MAIN_PANE) /2 -10
		self.H_REQUIRES = 110
#		self.Y_REQUIRES = self.Y_MAIN_PANE + self.H_MAIN_PANE - self.H_REQUIRES
		self.Y_REQUIRES = self.Y_MAIN_PANE + 10

#		self.X_PLAYER_REQS = self.X_REQUIRES
#		self.X_PLAYER_REQS = self.X_MAIN_PANE + self.W_MAIN_PANE + X_MERGIN + self.W_REQUIRES +20
#		self.W_PLAYER_REQS = self.W_REQUIRES
#		self.H_PLAYER_REQS = 110
#		self.Y_PLAYER_REQS = self.Y_REQUIRES - self.H_PLAYER_REQS - Y_MERGIN
#		self.Y_PLAYER_REQS = self.Y_MAIN_PANE + 10

		self.X_PLAYER_REQS = self.X_REQUIRES
		self.Y_PLAYER_REQS = self.Y_REQUIRES + self.H_REQUIRES + Y_MERGIN
		self.W_PLAYER_REQS = (self.top.R_PEDIA_PAGE - self.X_MAIN_PANE) /2 -10
		self.H_PLAYER_REQS = 110
		
		self.X_SPECIAL = self.X_MAIN_PANE
		self.Y_SPECIAL = self.Y_MAIN_PANE + self.H_MAIN_PANE + Y_MERGIN
		self.W_SPECIAL = self.top.R_PEDIA_PAGE - self.X_SPECIAL
		self.H_SPECIAL = 180

#		self.X_OBSOLETES = self.X_REQUIRES
#		self.Y_OBSOLETES = self.Y_REQUIRES + self.H_REQUIRES + Y_MERGIN
#		self.W_OBSOLETES = (self.top.R_PEDIA_PAGE - self.X_MAIN_PANE) /2 -10
#		self.H_OBSOLETES = 110

#		self.X_OBSOLETED = self.X_OBSOLETES + self.W_OBSOLETES+20
#		self.Y_OBSOLETED = self.Y_OBSOLETES 
#		self.W_OBSOLETED = self.W_OBSOLETES
#		self.H_OBSOLETED = 110
		
		self.X_TEXT = self.X_MAIN_PANE
		self.Y_TEXT = self.Y_SPECIAL + self.H_SPECIAL + Y_MERGIN
		self.W_TEXT = self.top.R_PEDIA_PAGE - self.X_MAIN_PANE
		self.H_TEXT = self.top.B_PEDIA_PAGE - self.Y_TEXT



	def interfaceScreen(self, iSpell):
		self.iSpell = iSpell
		screen = self.top.getScreen()

		# Header...
		szHeader = u"<font=4b>" + gc.getSpellInfo(self.iSpell).getDescription() + u"</font>"
		szHeaderId = "PediaMainHeader"
		screen.setText(szHeaderId, "Background", szHeader, CvUtil.FONT_CENTER_JUSTIFY, self.top.X_SCREEN, self.top.Y_TITLE, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_MAIN_PANE, self.Y_MAIN_PANE, self.W_MAIN_PANE, self.H_MAIN_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_MAIN)
		screen.addDDSGFC(self.top.getNextWidgetName(), gc.getSpellInfo(self.iSpell).getButton(), self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1)

		self.placeStats()
		self.placePlayerReqs()
		self.placeRequires()
		self.placeSpecial()
#		self.placeObsoletes()
		self.placeText()



	def placeStats(self):
		screen = self.top.getScreen()

		panelName = self.top.getNextWidgetName()
		screen.addListBoxGFC(panelName, "", self.X_STATUS, self.Y_STATUS, self.W_STATUS, self.H_STATUS, TableStyles.TABLE_STYLE_EMPTY)
		screen.enableSelect(panelName, False)

		pSpell = gc.getSpellInfo(self.iSpell)

		szSpellType = u""
		if (pSpell.isGlobal()):
			szSpellType = localText.getText("TXT_KEY_GLOBAL_SPELL_PEDIA", ())
		screen.appendListBoxString(panelName, u"<font=4>" + szSpellType.upper() + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

		iCost = pSpell.getCost()
		if iCost:
			if (iCost > 0):
				szCost = localText.getText("TXT_KEY_PEDIA_COST", (iCost, ))
			elif (iCost < 0):
				szCost = localText.getText("TXT_KEY_PEDIA_GAIN", (-iCost, ))
			szCost = u"<font=4>" + szCost.upper() + u"%c" % gc.getCommerceInfo(CommerceTypes.COMMERCE_GOLD).getChar() + u"</font>"
			screen.appendListBoxString(panelName, szCost, WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

		iDelay = pSpell.getDelay()
		if iDelay:
			szDelay = u"<font=4>" + localText.getText("TXT_KEY_PEDIA_DELAY", (iDelay, )).upper() + u"</font>"
			screen.appendListBoxString(panelName, szDelay, WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)



	def placePlayerReqs(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_REQUIRES", ()), "", false, true, self.X_PLAYER_REQS, self.Y_PLAYER_REQS, self.W_PLAYER_REQS, self.H_PLAYER_REQS, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.attachLabel(panelName, "", "  ")

		#add civilization buttons
		iPrereqCiv = gc.getSpellInfo(self.iSpell).getCivilizationPrereq()
		if iPrereqCiv != CivilizationTypes.NO_CIVILIZATION:
			screen.attachImageButton(panelName, "", gc.getCivilizationInfo(iPrereqCiv).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, iPrereqCiv, 1, False)

		#add tech buttons
		iPrereqTech = gc.getSpellInfo(self.iSpell).getTechPrereq()
		if iPrereqTech != TechTypes.NO_TECH:
			screen.attachImageButton(panelName, "", gc.getTechInfo(iPrereqTech).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iPrereqTech, 1, False)

		#add building buttons
		iPrereqBuildingClass = gc.getSpellInfo(self.iSpell).getBuildingClassOwnedPrereq()
		if iPrereqBuildingClass != BuildingClassTypes.NO_BUILDINGCLASS:
			iPrereqBuilding = BuildingTypes.NO_BUILDING
			if self.top.iActiveCiv != CivilizationTypes.NO_CIVILIZATION:
				iPrereqBuilding = gc.getCivilizationInfo(self.top.iActiveCiv).getCivilizationBuildings(iPrereqBuildingClass)
			if iPrereqBuilding == BuildingTypes.NO_BUILDING:
				iPrereqBuilding = gc.getBuildingClassInfo(iPrereqBuildingClass).getDefaultBuildingIndex()
			screen.attachImageButton(panelName, "", gc.getBuildingInfo(iPrereqBuilding).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iPrereqBuilding, 1, False)

		#add religion buttons
		iPrereqReligion = gc.getSpellInfo(self.iSpell).getStateReligionPrereq()
		if iPrereqReligion != ReligionTypes.NO_RELIGION:
			screen.attachImageButton(panelName, "", gc.getReligionInfo(iPrereqReligion).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, iPrereqReligion, 1, False)



	def placeRequires(self):
		screen = self.top.getScreen()

		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_CASTER_PREREQ", ()), "", false, true,
				 self.X_REQUIRES, self.Y_REQUIRES, self.W_REQUIRES, self.H_REQUIRES, PanelStyles.PANEL_STYLE_BLUE50 )

		screen.attachLabel(panelName, "", "  ")

		iPrereqCiv = gc.getSpellInfo(self.iSpell).getCivilizationPrereq()

		#add building buttons
		iPrereqBuilding = gc.getSpellInfo(self.iSpell).getBuildingPrereq()
		if iPrereqBuilding != BuildingTypes.NO_BUILDING:
			screen.attachImageButton(panelName, "", gc.getBuildingInfo(iPrereqBuilding).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iPrereqBuilding, 1, False)

		#add unit combat buttons
		iPrereqUnitCombat = gc.getSpellInfo(self.iSpell).getUnitCombatPrereq()
		if iPrereqUnitCombat != UnitCombatTypes.NO_UNITCOMBAT:
			screen.attachImageButton(panelName, "", gc.getUnitCombatInfo(iPrereqUnitCombat).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT_COMBAT, iPrereqUnitCombat, 1, False)

		#prepare button UnitArtStyle
		iPrereqUnitClass = gc.getSpellInfo(self.iSpell).getUnitClassPrereq()

		iActiveUnit = UnitTypes.NO_UNIT
		if self.top.iActiveCiv != CivilizationTypes.NO_CIVILIZATION:
			iActiveUnit = gc.getCivilizationInfo(self.top.iActiveCiv).getCivilizationUnits(iPrereqUnitClass)

		iQualifiedCiv = CivilizationTypes.NO_CIVILIZATION
		if iPrereqCiv != CivilizationTypes.NO_CIVILIZATION:
			iQualifiedCiv = iPrereqCiv
		elif iActiveUnit != UnitTypes.NO_UNIT:
			iQualifiedCiv = self.top.iActiveCiv

		#add unit class buttons
		iPrereqUnitClass = gc.getSpellInfo(self.iSpell).getUnitClassPrereq()
		if iPrereqUnitClass != UnitClassTypes.NO_UNITCLASS:
			iPrereqUnit = gc.getUnitClassInfo(iPrereqUnitClass).getDefaultUnitIndex()
			if iQualifiedCiv != CivilizationTypes.NO_CIVILIZATION:
				iPrereqUnit = gc.getCivilizationInfo(iQualifiedCiv).getCivilizationUnits(iPrereqUnitClass)
			szUnitIcon = gc.getUnitInfo(iPrereqUnit).getUnitButtonWithCivArtStyle(iQualifiedCiv)
			screen.attachImageButton(panelName, "", szUnitIcon, GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iPrereqUnit, 1, False)

		#add unit buttons
		iPrereqUnit = gc.getSpellInfo(self.iSpell).getUnitPrereq()
		if iPrereqUnit != UnitTypes.NO_UNIT:
			szUnitIcon = gc.getUnitInfo(iPrereqUnit).getUnitButtonWithCivArtStyle(iQualifiedCiv)
			screen.attachImageButton(panelName, "", szUnitIcon, GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iPrereqUnit, 1, False)

		#add improvement buttons
		iPrereqImprovement = gc.getSpellInfo(self.iSpell).getImprovementPrereq()
		if iPrereqImprovement != ImprovementTypes.NO_IMPROVEMENT:
			screen.attachImageButton(panelName, "", gc.getImprovementInfo(iPrereqImprovement).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_IMPROVEMENT, iPrereqImprovement, 1, False)

		#add religion buttons
		iPrereqReligion = gc.getSpellInfo(self.iSpell).getReligionPrereq()
		if iPrereqReligion != ReligionTypes.NO_RELIGION:
			screen.attachImageButton(panelName, "", gc.getReligionInfo(iPrereqReligion).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, iPrereqReligion, 1, False)

		#add promotion buttons
		ePromo = gc.getSpellInfo(self.iSpell).getPromotionPrereq1()
		if (ePromo != PromotionTypes.NO_PROMOTION):
			screen.attachImageButton( panelName, "", gc.getPromotionInfo(ePromo).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, ePromo, 1, False )

		ePromo = gc.getSpellInfo(self.iSpell).getPromotionPrereq2()
		if (ePromo != PromotionTypes.NO_PROMOTION):
			screen.attachImageButton( panelName, "", gc.getPromotionInfo(ePromo).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, ePromo, 1, False )

	def placeSpecial(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_EFFECTS", ()), "", False, True, self.X_SPECIAL, self.Y_SPECIAL, self.W_SPECIAL, self.H_SPECIAL, PanelStyles.PANEL_STYLE_BLUE50)
		listName = self.top.getNextWidgetName()
		szSpecialText = CyGameTextMgr().getSpellHelp(self.iSpell, True)[1:]
		screen.addMultilineText(listName, szSpecialText, self.X_SPECIAL+5, self.Y_SPECIAL+30, self.W_SPECIAL-5, self.H_SPECIAL-32, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

	def placeText(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY",  ()), "", False, True, self.X_TEXT, self.Y_TEXT, self.W_TEXT, self.H_TEXT, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")
		listName = self.top.getNextWidgetName()
		pediaText = gc.getSpellInfo(self.iSpell).getCivilopedia()
		screen.addMultilineText(listName, pediaText, self.X_TEXT+5, self.Y_TEXT+30, self.W_TEXT-5, self.H_TEXT-32, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def getSpellType(self, iSpell):
		return gc.getSpellInfo(iSpell).isAbility()



	def handleInput (self, inputClass):
		return 0
