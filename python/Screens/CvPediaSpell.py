## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
from CvPythonExtensions import *
import CvUtil
import ScreenInput
##--------	BUGFfH: Added by Denev 2009/09/19
import CvPediaScreen		# base class
##--------	BUGFfH: End Add
import CvScreenEnums

# globals
gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

##--------	BUGFfH: Modified by Denev 2009/09/19
#class CvPediaSpell:
class CvPediaSpell( CvPediaScreen.CvPediaScreen ):
##--------	BUGFfH: End Modify
	"Civilopedia Screen for Spells"

	def __init__(self, main):
		self.iSpell = -1
		self.top = main

##--------	BUGFfH: Modified by Denev 2009/09/21
		"""
		self.BUTTON_SIZE = 46

		self.X_UNIT_PANE = 50
		self.Y_UNIT_PANE = 80
		self.W_UNIT_PANE = 250
		self.H_UNIT_PANE = 210

		self.X_ICON = 98
		self.Y_ICON = 110
		self.W_ICON = 150
		self.H_ICON = 150
		self.ICON_SIZE = 64

		self.X_PREREQ_PANE = 330
		self.Y_PREREQ_PANE = 60
		self.W_PREREQ_PANE = 420
		self.H_PREREQ_PANE = 110

		self.X_HELP_PANE = 330
		self.Y_HELP_PANE = 180
		self.W_HELP_PANE = self.W_PREREQ_PANE
		self.H_HELP_PANE = 110

		self.X_SPECIAL_PANE = 50 #330
		self.Y_SPECIAL_PANE = 294
		self.W_SPECIAL_PANE = self.W_PREREQ_PANE + (330-50)
		self.H_SPECIAL_PANE = 380

		#~ self.X_UNIT_GROUP_PANE = 50
		#~ self.Y_UNIT_GROUP_PANE = 294
		#~ self.W_UNIT_GROUP_PANE = 250
		#~ self.H_UNIT_GROUP_PANE = 380
		#~ self.DY_UNIT_GROUP_PANE = 25
#		self.ITEMS_MARGIN = 18
#		self.ITEMS_SEPARATION = 2
		"""
		X_MERGIN = self.top.X_MERGIN
		Y_MERGIN = self.top.Y_MERGIN

		self.X_MAIN_PANE = self.top.X_PEDIA_PAGE
		self.Y_MAIN_PANE = self.top.Y_PEDIA_PAGE
		self.W_MAIN_PANE = 436
		self.H_MAIN_PANE = 210

		self.W_ICON = 150
		self.H_ICON = 150
		self.X_ICON = self.X_MAIN_PANE + (self.H_MAIN_PANE - self.H_ICON) / 2
		self.Y_ICON = self.Y_MAIN_PANE + (self.H_MAIN_PANE - self.H_ICON) / 2
		self.ICON_SIZE = 64

		self.X_STATUS = self.X_ICON + self.W_ICON + 10
		self.Y_STATUS = self.Y_ICON
		self.W_STATUS = self.X_MAIN_PANE + self.W_MAIN_PANE - self.X_STATUS
		self.H_STATUS = self.Y_MAIN_PANE + self.H_MAIN_PANE - self.Y_STATUS

		self.X_REQUIRES = self.X_MAIN_PANE + self.W_MAIN_PANE + X_MERGIN
		self.W_REQUIRES = self.top.R_PEDIA_PAGE - self.X_REQUIRES
		self.H_REQUIRES = 110
		self.Y_REQUIRES = self.Y_MAIN_PANE + self.H_MAIN_PANE - self.H_REQUIRES

		self.X_PLAYER_REQS = self.X_REQUIRES
		self.W_PLAYER_REQS = self.W_REQUIRES
		self.H_PLAYER_REQS = 110
		self.Y_PLAYER_REQS = self.Y_REQUIRES - self.H_PLAYER_REQS - Y_MERGIN

		self.X_SPECIAL = self.X_MAIN_PANE
		self.Y_SPECIAL = self.Y_MAIN_PANE + self.H_MAIN_PANE + Y_MERGIN
		self.W_SPECIAL = self.top.W_PEDIA_PAGE
		self.H_SPECIAL = (self.top.B_PEDIA_PAGE - self.Y_SPECIAL - Y_MERGIN) // 2

		self.X_TEXT = self.X_MAIN_PANE
		self.Y_TEXT = self.Y_SPECIAL + self.H_SPECIAL + Y_MERGIN
		self.W_TEXT = self.top.W_PEDIA_PAGE
		self.H_TEXT = self.top.B_PEDIA_PAGE - self.Y_TEXT
##--------	BUGFfH: End Modify

	# Screen construction function
	def interfaceScreen(self, iSpell):

		self.iSpell = iSpell

		self.top.deleteAllWidgets()

		screen = self.top.getScreen()

		bNotActive = (not screen.isActive())
		if bNotActive:
			self.top.setPediaCommonWidgets()

		# Header...
		szHeader = u"<font=4b>" + gc.getSpellInfo(self.iSpell).getDescription().upper() + u"</font>"
		szHeaderId = self.top.getNextWidgetName()
		screen.setLabel(szHeaderId, "Background", szHeader, CvUtil.FONT_CENTER_JUSTIFY, self.top.X_SCREEN, self.top.Y_TITLE, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		# Top
##--------	BUGFfH: Modified by Denev 2009/09/19
#		screen.setText(self.top.getNextWidgetName(), "Background", self.top.MENU_TEXT, CvUtil.FONT_LEFT_JUSTIFY, self.top.X_MENU, self.top.Y_MENU, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_PEDIA_MAIN, CivilopediaPageTypes.CIVILOPEDIA_PAGE_SPELL, -1)
		link = CivilopediaPageTypes.CIVILOPEDIA_PAGE_SPELL
		if self.getSpellType(iSpell):
			link = CivilopediaPageTypes.CIVILOPEDIA_PAGE_ABILITY
		screen.setText(self.top.getNextWidgetName(), "Background", self.top.MENU_TEXT, CvUtil.FONT_LEFT_JUSTIFY, self.top.X_MENU, self.top.Y_MENU, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_PEDIA_MAIN, link, -1)
##--------	BUGFfH: End Modify

		if self.top.iLastScreen	!= CvScreenEnums.PEDIA_SPELL or bNotActive:
			self.placeLinks(true)
			self.top.iLastScreen = CvScreenEnums.PEDIA_SPELL
		else:
			self.placeLinks(false)

		# Icon
		screen.addPanel( self.top.getNextWidgetName(), "", "", False, False,
			self.X_MAIN_PANE, self.Y_MAIN_PANE, self.W_MAIN_PANE, self.H_MAIN_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(self.top.getNextWidgetName(), "", "", false, false,
			self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_MAIN)
		screen.addDDSGFC(self.top.getNextWidgetName(), gc.getSpellInfo(self.iSpell).getButton(),
			self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1 )
#		screen.addDDSGFC(self.top.getNextWidgetName(), gc.getSpellInfo(self.iSpell).getButton(), self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, WidgetTypes.WIDGET_GENERAL, self.iSpell, -1 )

##--------	BUGFfH: Added by Denev 2009/09/21
		self.placeStats()
		self.placePlayerReqs()
##--------	BUGFfH: End Add

		# Place Required promotions
		self.placePrereqs()

		# Place Allowing promotions
		self.placeEffects()

		# Place the Special abilities block
		self.placeText()

		#self.placeUnitGroups()


##--------	BUGFfH: Added by Denev 2009/09/21
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
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_REQUIRES", ()), "", false, true,
				 self.X_PLAYER_REQS, self.Y_PLAYER_REQS, self.W_PLAYER_REQS, self.H_PLAYER_REQS, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.attachLabel(panelName, "", "  ")

		iActiveCiv = gc.getGame().getActiveCivilizationType()

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
			if iActiveCiv != CivilizationTypes.NO_CIVILIZATION:
				iPrereqBuilding = gc.getCivilizationInfo(iActiveCiv).getCivilizationBuildings(iPrereqBuildingClass)
			if iPrereqBuilding == BuildingTypes.NO_BUILDING:
				iPrereqBuilding = gc.getBuildingClassInfo(iPrereqBuildingClass).getDefaultBuildingIndex()
			screen.attachImageButton(panelName, "", gc.getBuildingInfo(iPrereqBuilding).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iPrereqBuilding, 1, False)

		#add religion buttons
		iPrereqReligion = gc.getSpellInfo(self.iSpell).getStateReligionPrereq()
		if iPrereqReligion != ReligionTypes.NO_RELIGION:
			screen.attachImageButton(panelName, "", gc.getReligionInfo(iPrereqReligion).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, iPrereqReligion, 1, False)
##--------	BUGFfH: End Add

	# Place prereqs...
	def placePrereqs(self):

		screen = self.top.getScreen()

		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_CASTER_PREREQ", ()), "", false, true,
				 self.X_REQUIRES, self.Y_REQUIRES, self.W_REQUIRES, self.H_REQUIRES, PanelStyles.PANEL_STYLE_BLUE50 )

		screen.attachLabel(panelName, "", "  ")

##--------	BUGFfH: Added by Denev 2009/09/21
		iActiveCiv = gc.getGame().getActiveCivilizationType()
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
		if iActiveCiv != CivilizationTypes.NO_CIVILIZATION:
			iActiveUnit = gc.getCivilizationInfo(iActiveCiv).getCivilizationUnits(iPrereqUnitClass)

		iQualifiedCiv = CivilizationTypes.NO_CIVILIZATION
		if iPrereqCiv != CivilizationTypes.NO_CIVILIZATION:
			iQualifiedCiv = iPrereqCiv
		elif iActiveUnit != UnitTypes.NO_UNIT:
			iQualifiedCiv = iActiveCiv

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
##--------	BUGFfH: End Add

		ePromo = gc.getSpellInfo(self.iSpell).getPromotionPrereq1()
		if (ePromo > -1):
			screen.attachImageButton( panelName, "", gc.getPromotionInfo(ePromo).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, ePromo, 1, False )

			ePromo = gc.getSpellInfo(self.iSpell).getPromotionPrereq2()
			if (ePromo > -1):
				screen.attachTextGFC(panelName, "", localText.getText("TXT_KEY_AND", ()), FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				screen.attachImageButton( panelName, "", gc.getPromotionInfo(ePromo).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, ePromo, 1, False )

		#eTech = gc.getSpellInfo(self.iSpell).getTechPrereq()
		#if (eTech > -1):
		#	screen.attachImageButton( panelName, "", gc.getTechInfo(eTech).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, eTech, 1, False )

	def placeEffects(self):

		screen = self.top.getScreen()

		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_EFFECTS", ()), "", false, true,
				 self.X_SPECIAL, self.Y_SPECIAL, self.W_SPECIAL, self.H_SPECIAL, PanelStyles.PANEL_STYLE_BLUE50 )

		screen.attachLabel(panelName, "", "  ")
		listName = self.top.getNextWidgetName()

		szSpecialText = CyGameTextMgr().getSpellHelp(self.iSpell, True)[1:]

##--------	BUGFfH: Modified by Denev 2009/09/21
#		screen.addMultilineText(listName, szSpecialText, self.X_HELP_PANE+5, self.Y_HELP_PANE+30, self.W_HELP_PANE-10, self.H_HELP_PANE-35, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.addMultilineText(listName, szSpecialText, self.X_SPECIAL + 5, self.Y_SPECIAL + 30, self.W_SPECIAL - 5, self.H_SPECIAL - 32, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
##--------	BUGFfH: End Modify

	def placeText(self):

		screen = self.top.getScreen()

		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY", ()), "", true, false,
				 self.X_TEXT, self.Y_TEXT, self.W_TEXT, self.H_TEXT, PanelStyles.PANEL_STYLE_BLUE50 )

		listName = self.top.getNextWidgetName()


		pediaText = gc.getSpellInfo(self.iSpell).getCivilopedia()

##--------	BUGFfH: Modified by Denev 2009/09/21
#		screen.addMultilineText(listName, pediaText, self.X_SPECIAL_PANE+5, self.Y_SPECIAL_PANE+30, self.W_SPECIAL_PANE-10, self.H_SPECIAL_PANE-35, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.addMultilineText(listName, pediaText, self.X_TEXT + 5, self.Y_TEXT + 30, self.W_TEXT - 5, self.H_TEXT - 32, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
##--------	BUGFfH: End Modify


	def placeLinks(self, bRedraw):

		screen = self.top.getScreen()

		if bRedraw:
			screen.clearListBoxGFC(self.top.LIST_ID)

		# sort techs alphabetically
##--------	BUGFfH: Modified by Denev 2009/09/19
		"""
		listSpells = []
		iCount = 0
		for iSpell in range(gc.getNumSpellInfos()):
			if not gc.getSpellInfo(iSpell).isGraphicalOnly():
				listSpells.append(iSpell)
				iCount += 1

		listSorted = [(0,0)] * iCount
		iI = 0
		for iSpell in listSpells:
			listSorted[iI] = (gc.getSpellInfo(iSpell).getDescription(), iSpell)
			iI += 1
		listSorted.sort()

		i = 0
		iSelected = 0
		for iI in range(len(listSorted)):
			if (not gc.getSpellInfo(iI).isGraphicalOnly()):
				if bRedraw:
					screen.appendListBoxString( self.top.LIST_ID, listSorted[iI][0], WidgetTypes.WIDGET_PEDIA_JUMP_TO_SPELL, listSorted[iI][1], 0, CvUtil.FONT_LEFT_JUSTIFY )
				if listSorted[iI][1] == self.iSpell:
					iSelected = i
				i += 1
		"""
		listSorted = self.getSortedList( gc.getNumSpellInfos(), gc.getSpellInfo, self.getSpellType(self.iSpell), self.getSpellType )

		iSelected = 0
		for iIndex, (szDescription, iSpell) in enumerate(listSorted):
			if (not gc.getSpellInfo(iSpell).isGraphicalOnly()):
				if bRedraw:
					screen.appendListBoxString(self.top.LIST_ID, szDescription, WidgetTypes.WIDGET_PEDIA_JUMP_TO_SPELL, iSpell, 0, CvUtil.FONT_LEFT_JUSTIFY)
				if iSpell == self.iSpell:
					iSelected = iIndex
##--------	BUGFfH: End Modify

		screen.setSelectedListBoxStringGFC(self.top.LIST_ID, iSelected)

##--------	BUGFfH: Added by Denev 2009/09/19
	def getSpellType(self, iSpell):
		return gc.getSpellInfo(iSpell).isAbility()
##--------	BUGFfH: End Add

	# Will handle the input for this screen...
	def handleInput (self, inputClass):
		return 0

