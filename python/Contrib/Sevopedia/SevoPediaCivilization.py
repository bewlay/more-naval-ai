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
##--------	BUGFfH: Added by Denev 2009/08/14
import SevoPediaMain
##--------	BUGFfH: End Add

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class SevoPediaCivilization:

	def __init__(self, main):
		self.iCivilization = -1
		self.top = main

##--------	BUGFfH: Modified by Denev 2009/10/08
		X_MERGIN = self.top.X_MERGIN
		Y_MERGIN = self.top.Y_MERGIN

		self.W_CIV_TRAIT = 150
		self.H_CIV_TRAIT = 116
		self.X_CIV_TRAIT = self.top.R_PEDIA_PAGE - self.W_CIV_TRAIT
		self.Y_CIV_TRAIT = self.top.Y_PEDIA_PAGE

		self.W_TECHS = 180
		self.H_TECHS = self.H_CIV_TRAIT
		self.X_TECHS = self.X_CIV_TRAIT - self.W_TECHS - X_MERGIN
		self.Y_TECHS = self.Y_CIV_TRAIT

		self.X_MAIN_PANE = self.top.X_PEDIA_PAGE
		self.Y_MAIN_PANE = self.Y_CIV_TRAIT
		self.W_MAIN_PANE = self.X_TECHS - self.X_MAIN_PANE - X_MERGIN
		self.H_MAIN_PANE = self.H_CIV_TRAIT

		self.W_ICON = 100
		self.H_ICON = 100
		self.X_ICON = self.X_MAIN_PANE + (self.H_MAIN_PANE - self.H_ICON) / 2
		self.Y_ICON = self.Y_MAIN_PANE + (self.H_MAIN_PANE - self.H_ICON) / 2
		self.ICON_SIZE = 64

		self.X_HEROES = self.X_MAIN_PANE
		self.Y_HEROES = self.Y_MAIN_PANE + self.H_MAIN_PANE + Y_MERGIN
		self.W_HEROES = 155
		self.H_HEROES = 110

		self.X_SPELLS = self.X_HEROES + self.W_HEROES + X_MERGIN
		self.Y_SPELLS = self.Y_HEROES
		self.W_SPELLS = 155
		self.H_SPELLS = self.H_HEROES

		self.X_LEADERS = self.X_SPELLS + self.W_SPELLS + X_MERGIN
		self.Y_LEADERS = self.Y_HEROES
		self.W_LEADERS = self.top.R_PEDIA_PAGE - self.X_LEADERS
		self.H_LEADERS = self.H_HEROES

		self.X_BUILDINGS = self.X_MAIN_PANE
		self.Y_BUILDINGS = self.Y_HEROES + self.H_HEROES + Y_MERGIN
		self.W_BUILDINGS = 215
		self.H_BUILDINGS = self.H_HEROES

		self.X_UNITS = self.X_BUILDINGS + self.W_BUILDINGS + X_MERGIN
		self.Y_UNITS = self.Y_BUILDINGS
		self.W_UNITS = self.top.R_PEDIA_PAGE - self.X_UNITS
		self.H_UNITS = self.H_BUILDINGS

		self.X_EX_BUILDINGS = self.X_BUILDINGS
		self.Y_EX_BUILDINGS = self.Y_BUILDINGS + self.H_BUILDINGS + Y_MERGIN
		self.W_EX_BUILDINGS = self.W_BUILDINGS
		self.H_EX_BUILDINGS = self.H_BUILDINGS

		self.X_EX_UNITS = self.X_UNITS
		self.Y_EX_UNITS = self.Y_EX_BUILDINGS
		self.W_EX_UNITS = self.W_UNITS
		self.H_EX_UNITS = self.H_UNITS

		self.X_TEXT = self.X_MAIN_PANE
		self.Y_TEXT = self.Y_EX_BUILDINGS + self.H_EX_BUILDINGS + 10
		self.W_TEXT = self.top.R_PEDIA_PAGE - self.X_TEXT
		self.H_TEXT = self.top.B_PEDIA_PAGE - self.Y_TEXT

		self.Y_WIDE_TEXT = self.Y_EX_BUILDINGS
		self.H_WIDE_TEXT = self.top.B_PEDIA_PAGE - self.Y_WIDE_TEXT
##--------	BUGFfH: End Modify



	def interfaceScreen(self, iCivilization):
		self.iCivilization = iCivilization
		screen = self.top.getScreen()

##--------	BUGFfH: Added by Denev 2009/08/16
		# Header...
		szHeader = u"<font=4b>" + gc.getCivilizationInfo(self.iCivilization).getDescription() + u"</font>"
		szHeaderId = "PediaMainHeader"
		screen.setText(szHeaderId, "Background", szHeader, CvUtil.FONT_CENTER_JUSTIFY, self.top.X_SCREEN, self.top.Y_TITLE, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
##--------	BUGFfH: End Add

		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_MAIN_PANE, self.Y_MAIN_PANE, self.W_MAIN_PANE, self.H_MAIN_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_MAIN)
		screen.addDDSGFC(self.top.getNextWidgetName(), ArtFileMgr.getCivilizationArtInfo(gc.getCivilizationInfo(self.iCivilization).getArtDefineTag()).getButton(), self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1)

		self.placeTech()
		self.placeBuilding()
		self.placeUnit()
		self.placeLeader()

##--------	BUGFfH: Added by Denev 2009/10/08
		self.bWideText = true

		self.placeTrait()
		self.placeHero()
		self.placeWorldSpell()

		szPanelName1 = self.placeBlockedBuilding()
		szPanelName2 = self.placeBlockedUnit()

		if self.bWideText:
			screen.hide(szPanelName1)
			screen.hide(szPanelName2)
##--------	BUGFfH: End Add

		self.placeText()



	def placeTech(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_FREE_TECHS", ()), "", False, True, self.X_TECHS, self.Y_TECHS, self.W_TECHS, self.H_TECHS, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")
		for iTech in range(gc.getNumTechInfos()):
			if (gc.getCivilizationInfo(self.iCivilization).isCivilizationFreeTechs(iTech)):
				screen.attachImageButton(panelName, "", gc.getTechInfo(iTech).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iTech, 1, False)



	def placeBuilding(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_UNIQUE_BUILDINGS", ()), "", False, True, self.X_BUILDINGS, self.Y_BUILDINGS, self.W_BUILDINGS, self.H_BUILDINGS, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")
		for iBuilding in range(gc.getNumBuildingClassInfos()):
			iUniqueBuilding = gc.getCivilizationInfo(self.iCivilization).getCivilizationBuildings(iBuilding)
			iDefaultBuilding = gc.getBuildingClassInfo(iBuilding).getDefaultBuildingIndex()
			if iUniqueBuilding != BuildingTypes.NO_BUILDING:			
				iUniqueCiv = gc.getBuildingInfo(iUniqueBuilding).getPrereqCiv()			
			if (iDefaultBuilding > -1 and iUniqueBuilding > -1 and iDefaultBuilding != iUniqueBuilding):
				screen.attachImageButton(panelName, "", gc.getBuildingInfo(iUniqueBuilding).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iUniqueBuilding, 1, False)
			elif iUniqueCiv != -1 and iUniqueCiv == self.iCivilization:
				if iUniqueBuilding != BuildingTypes.NO_BUILDING:
					szButton = gc.getBuildingInfo(iUniqueBuilding).getButton()
					screen.attachImageButton(panelName, "", szButton, GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iUniqueBuilding, 1, False)


	def placeUnit(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_FREE_UNITS", ()), "", False, True, self.X_UNITS, self.Y_UNITS, self.W_UNITS, self.H_UNITS, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")
		for iUnit in range(gc.getNumUnitClassInfos()):
			iHero = gc.getCivilizationInfo(self.iCivilization).getHero()
			iUniqueUnit = gc.getCivilizationInfo(self.iCivilization).getCivilizationUnits(iUnit)
			iDefaultUnit = gc.getUnitClassInfo(iUnit).getDefaultUnitIndex()
			if iDefaultUnit != iHero:
				if (iDefaultUnit > -1 and iUniqueUnit > -1 and iDefaultUnit != iUniqueUnit):
##--------	BUGFfH: Modified by Denev 2009/09/05
#				screen.attachImageButton(panelName, "", gc.getUnitInfo(iUniqueUnit).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUniqueUnit, 1, False)
					szUnitButton = gc.getUnitInfo(iUniqueUnit).getUnitButtonWithCivArtStyle(self.iCivilization)
					screen.attachImageButton(panelName, "", szUnitButton, GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUniqueUnit, 1, False)
					continue
##--------	BUGFfH: End Modify

##--------	BUGFfH: Added by Denev 2009/10/08
				if iUniqueUnit == UnitTypes.NO_UNIT:
					continue

				iUniqueCiv = gc.getUnitInfo(iUniqueUnit).getPrereqCiv()
				if iUniqueCiv == self.iCivilization:
					szButton = gc.getUnitInfo(iUniqueUnit).getUnitButtonWithCivArtStyle(iUniqueCiv)
					screen.attachImageButton(panelName, "", szButton, GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUniqueUnit, 1, False)
##--------	BUGFfH: End Add



##--------	BUGFfH: Added by Denev 2009/09/02
	def placeBlockedBuilding(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_MISC_CIV_BLOCKED_BUILDINGS", ()), "", False, True, self.X_EX_BUILDINGS, self.Y_EX_BUILDINGS, self.W_EX_BUILDINGS, self.H_EX_BUILDINGS, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")

		for iBuildingClass in range(gc.getNumBuildingClassInfos()):
			iUniqueBuilding = gc.getCivilizationInfo(self.iCivilization).getCivilizationBuildings(iBuildingClass)
			iDefaultBuilding = gc.getBuildingClassInfo(iBuildingClass).getDefaultBuildingIndex()
			if iDefaultBuilding != BuildingTypes.NO_BUILDING:
				if iUniqueBuilding == BuildingTypes.NO_BUILDING:
					BuildingInfo = gc.getBuildingInfo(iDefaultBuilding)
					screen.attachImageButton(panelName, "", BuildingInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iDefaultBuilding, 1, False)

					self.bWideText = false

		return panelName



	def placeBlockedUnit(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_MISC_CIV_BLOCKED_UNITS", ()), "", False, True, self.X_EX_UNITS, self.Y_EX_UNITS, self.W_EX_UNITS, self.H_EX_UNITS, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")

		for iUnitClass in range(gc.getNumUnitClassInfos()):
			iUniqueUnit = gc.getCivilizationInfo(self.iCivilization).getCivilizationUnits(iUnitClass)
			iDefaultUnit = gc.getUnitClassInfo(iUnitClass).getDefaultUnitIndex()
			if iDefaultUnit != UnitTypes.NO_UNIT:
				if iUniqueUnit == UnitTypes.NO_UNIT:
					if not isWorldUnitClass(iUnitClass):
						if gc.getUnitInfo(iDefaultUnit).getPrereqCiv() == CivilizationTypes.NO_CIVILIZATION:
							unitInfo = gc.getUnitInfo(iDefaultUnit)
							screen.attachImageButton(panelName, "", unitInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iDefaultUnit, 1, False)

							self.bWideText = false

		return panelName
##--------	BUGFfH: End Add



	def placeLeader(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_CONCEPT_LEADERS", ()), "", False, True, self.X_LEADERS, self.Y_LEADERS, self.W_LEADERS, self.H_LEADERS, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")
		for iLeader in range(gc.getNumLeaderHeadInfos()):
			civ = gc.getCivilizationInfo(self.iCivilization)
			if civ.isLeaders(iLeader):
				screen.attachImageButton(panelName, "", gc.getLeaderHeadInfo(iLeader).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_LEADER, iLeader, self.iCivilization, False)



	def placeText(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
##--------	BUGFfH: Modified by Denev 2009/10/08
#		screen.addPanel(panelName, "", "", True, True, self.X_TEXT, self.Y_TEXT, self.W_TEXT, self.H_TEXT, PanelStyles.PANEL_STYLE_BLUE50)
		iY, iH = self.Y_TEXT, self.H_TEXT
		if self.bWideText:
			iY, iH = self.Y_WIDE_TEXT, self.H_WIDE_TEXT
		screen.addPanel( panelName, "", "", true, true, self.X_TEXT, iY, self.W_TEXT, iH, PanelStyles.PANEL_STYLE_BLUE50 )
##--------	BUGFfH: End Modify
		szText = gc.getCivilizationInfo(self.iCivilization).getCivilopedia()
		screen.attachMultilineText(panelName, "Text", szText, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



##--------	BUGFfH: Added by Denev 2009/08/14
	def placeTrait(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()


		#terrain yield modifier
		ltTerrainModifier = []
		for iTerrain in range(gc.getNumTerrainInfos()):
			szYield = u""
			bFirst = true
			for iYield in range(YieldTypes.NUM_YIELD_TYPES):
				iYieldChange = gc.getCivilizationInfo(self.iCivilization).getTerrainYieldChanges(iTerrain, iYield, False)
				if (iYieldChange > 0):
					if not bFirst:
						szYield += ", "
					bFirst = false

					szSign = "+"
					if szYield < 0:
						szSign = ""
					szYield += u"<font=3>%s%i%c</font>" % (szSign, iYieldChange, gc.getYieldInfo(iYield).getChar())
			if not bFirst:
				ltTerrainModifier.append( (iTerrain, szYield) )

		#place panel with variable title

		#place each buttons
		for iTerrain, szYield in ltTerrainModifier:
			childPanelName = self.top.getNextWidgetName()
			screen.attachLabel(panelName, "", "  ")
			screen.attachPanel(panelName, childPanelName, "", "", False, False, PanelStyles.PANEL_STYLE_EMPTY)
			screen.attachImageButton(childPanelName, "", gc.getTerrainInfo(iTerrain).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TERRAIN, iTerrain, 1, False)
			screen.attachLabel(childPanelName, "", szYield)


	def placeHero(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_CATEGORY_HERO", ()), "", False, True, self.X_HEROES, self.Y_HEROES, self.W_HEROES, self.H_HEROES, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")

		iHero = gc.getCivilizationInfo(self.iCivilization).getHero()
		if iHero != UnitTypes.NO_UNIT:
			heroInfo = gc.getUnitInfo(iHero)
			screen.attachImageButton(panelName, "", heroInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iHero, 1, False)



	def placeWorldSpell(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_CONCEPT_WORLD_SPELLS", ()), "", False, True, self.X_SPELLS, self.Y_SPELLS, self.W_SPELLS, self.H_SPELLS, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")

		for iSpell in range(gc.getNumSpellInfos()):
			spellInfo = gc.getSpellInfo(iSpell)
			if spellInfo.isGlobal():
				if spellInfo.getCivilizationPrereq() == self.iCivilization:
					screen.attachImageButton(panelName, "", spellInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_SPELL, iSpell, 1, False)
					break
##--------	BUGFfH: End Add



	def handleInput (self, inputClass):
		return 0
