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

class SevoPediaUnit:

	def __init__(self, main):
		self.iUnit = -1
		self.top = main

##--------	BUGFfH: Added by Denev 2009/10/07
		X_MERGIN = self.top.X_MERGIN
		Y_MERGIN = self.top.Y_MERGIN
##--------	BUGFfH: End Add

##--------	BUGFfH: Modified by Denev 2009/10/07
		self.X_UNIT_PANE = self.top.X_PEDIA_PAGE
		self.Y_UNIT_PANE = self.top.Y_PEDIA_PAGE
		self.W_UNIT_PANE = 325
		self.H_UNIT_PANE = 145

		self.W_ICON = 100
		self.H_ICON = 100
		self.X_ICON = self.X_UNIT_PANE + (self.H_UNIT_PANE - self.H_ICON) / 2
		self.Y_ICON = self.Y_UNIT_PANE + (self.H_UNIT_PANE - self.H_ICON) / 2

		self.ICON_SIZE = 64
		self.BUTTON_SIZE = 64
		self.PROMOTION_ICON_SIZE = 32
		self.PROMOTION_ICON_SIZE_SMALL = 24

		self.X_STATS_PANE = self.X_UNIT_PANE + 130
		self.Y_STATS_PANE = self.Y_UNIT_PANE + 42
		self.W_STATS_PANE = 250
		self.H_STATS_PANE = 200

		self.X_UNIT_ANIMATION = self.X_UNIT_PANE + self.W_UNIT_PANE + X_MERGIN
		self.W_UNIT_ANIMATION = self.top.R_PEDIA_PAGE - self.X_UNIT_ANIMATION
		self.Y_UNIT_ANIMATION = self.Y_UNIT_PANE + 7
		self.H_UNIT_ANIMATION = self.H_UNIT_PANE - 7
		self.X_ROTATION_UNIT_ANIMATION = -20
		self.Z_ROTATION_UNIT_ANIMATION = 30
		self.SCALE_ANIMATION = 1.0

		self.X_PREREQ_PANE = self.X_UNIT_PANE
		self.Y_PREREQ_PANE = self.Y_UNIT_PANE + self.H_UNIT_PANE + Y_MERGIN
		self.W_PREREQ_PANE = self.top.W_PEDIA_PAGE / 2
		self.H_PREREQ_PANE = 110

		self.X_UPGRADES_TO_PANE = self.X_PREREQ_PANE + self.W_PREREQ_PANE + X_MERGIN
		self.Y_UPGRADES_TO_PANE = self.Y_PREREQ_PANE
		self.W_UPGRADES_TO_PANE = self.top.R_PEDIA_PAGE - self.X_UPGRADES_TO_PANE
		self.H_UPGRADES_TO_PANE = self.H_PREREQ_PANE

		self.X_SPECIAL_PANE = self.X_UNIT_PANE
		self.Y_SPECIAL_PANE = self.Y_PREREQ_PANE + self.H_PREREQ_PANE + Y_MERGIN
		self.W_SPECIAL_PANE = (self.top.W_PEDIA_PAGE - X_MERGIN) * 3 / 5
		self.H_SPECIAL_PANE = 175

		self.X_PROMO_PANE = self.X_SPECIAL_PANE + self.W_SPECIAL_PANE + X_MERGIN
		self.Y_PROMO_PANE = self.Y_SPECIAL_PANE
		self.W_PROMO_PANE = self.top.R_PEDIA_PAGE - self.X_PROMO_PANE
		self.H_PROMO_PANE = self.H_SPECIAL_PANE

		self.X_HISTORY_PANE = self.X_UNIT_PANE
		self.Y_HISTORY_PANE = self.Y_SPECIAL_PANE + self.H_SPECIAL_PANE + Y_MERGIN
		self.W_HISTORY_PANE = self.top.R_PEDIA_PAGE - self.X_HISTORY_PANE
		self.H_HISTORY_PANE = self.top.B_PEDIA_PAGE - self.Y_HISTORY_PANE
##--------	BUGFfH: End Modify



	def interfaceScreen(self, iUnit):
		self.iUnit = iUnit
		screen = self.top.getScreen()

##--------	BUGFfH: Added by Denev 2009/09/12
		# Header...
		szHeader = u"<font=4b>" + gc.getUnitInfo(self.iUnit).getDescription() + u"</font>"
		szHeaderId = "PediaMainHeader"
		screen.setText(szHeaderId, "Background", szHeader, CvUtil.FONT_CENTER_JUSTIFY, self.top.X_SCREEN, self.top.Y_TITLE, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		# Unit Icon with ArtStyle
		szUnitIcon = gc.getUnitInfo(self.iUnit).getUnitButtonWithCivArtStyle(gc.getGame().getActiveCivilizationType())
##--------	BUGFfH: End Add

		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_UNIT_PANE, self.Y_UNIT_PANE, self.W_UNIT_PANE, self.H_UNIT_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_MAIN)
##--------	BUGFfH: Modified by Denev 2009/09/12
#		screen.addDDSGFC(self.top.getNextWidgetName(), gc.getUnitInfo(self.iUnit).getButton(), self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addDDSGFC(self.top.getNextWidgetName(), szUnitIcon, self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1)
##--------	BUGFfH: End Modify
		screen.addUnitGraphicGFC(self.top.getNextWidgetName(), self.iUnit, self.X_UNIT_ANIMATION, self.Y_UNIT_ANIMATION, self.W_UNIT_ANIMATION, self.H_UNIT_ANIMATION, WidgetTypes.WIDGET_GENERAL, -1, -1, self.X_ROTATION_UNIT_ANIMATION, self.Z_ROTATION_UNIT_ANIMATION, self.SCALE_ANIMATION, True)

##--------	BUGFfH: Added by Denev 2009/08/12
		if self.getUnitType(iUnit):
			szImage = str(gc.getUnitInfo(iUnit).getImage())
			iHeight = self.W_UPGRADES_TO_PANE / 3
			iPositionY = self.Y_UPGRADES_TO_PANE + self.H_UPGRADES_TO_PANE - iHeight
			screen.addDDSGFC(self.top.getNextWidgetName(), szImage, self.X_UPGRADES_TO_PANE, iPositionY, self.W_UPGRADES_TO_PANE, iHeight, WidgetTypes.WIDGET_GENERAL, -1, -1 )
##--------	BUGFfH: End Add

		self.placeStats()
		self.placeUpgradesTo()
		self.placeRequires()
		self.placeSpecial()
		self.placePromotions()
		self.placeHistory()



	def placeStats(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		iCombatType = gc.getUnitInfo(self.iUnit).getUnitCombatType()
		if (iCombatType != -1):
			screen.setImageButton(self.top.getNextWidgetName(), gc.getUnitCombatInfo(iCombatType).getButton(), self.X_STATS_PANE, self.Y_STATS_PANE - 35, 32, 32, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT_COMBAT, iCombatType, 0)
			screen.setText(self.top.getNextWidgetName(), "", u"<font=3>" + gc.getUnitCombatInfo(iCombatType).getDescription() + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, self.X_STATS_PANE + 37, self.Y_STATS_PANE - 30, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT_COMBAT, iCombatType, 0)
		screen.addListBoxGFC(panelName, "", self.X_STATS_PANE -15, self.Y_STATS_PANE, self.W_STATS_PANE, self.H_STATS_PANE, TableStyles.TABLE_STYLE_EMPTY)
		screen.enableSelect(panelName, False)
		if (gc.getUnitInfo(self.iUnit).getAirCombat() > 0 and gc.getUnitInfo(self.iUnit).getCombat() == 0):
			iStrength = gc.getUnitInfo(self.iUnit).getAirCombat()
		else:
			iStrength = gc.getUnitInfo(self.iUnit).getCombat()
		szName = self.top.getNextWidgetName()

#BUGFfH Defense Str: Added by Denev 2009/08/12 (from CvPediaUnit.py by Kael)
#		szStrength = localText.getText("TXT_KEY_PEDIA_STRENGTH", (iStrength,))
		if iStrength == gc.getUnitInfo(self.iUnit).getCombatDefense():
			szStrength = localText.getText("TXT_KEY_PEDIA_STRENGTH", ( iStrength, ) )
		else:
			szStrength = localText.getText("TXT_KEY_PEDIA_STRENGTH_DEFENSE", ( iStrength, gc.getUnitInfo(self.iUnit).getCombatDefense()) )
##--------	BUGFfH: End Add

		screen.appendListBoxStringNoUpdate(panelName, u"<font=4>" + szStrength.upper() + u"%c" % CyGame().getSymbolID(FontSymbols.STRENGTH_CHAR) + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)
		szName = self.top.getNextWidgetName()
		szMovement = localText.getText("TXT_KEY_PEDIA_MOVEMENT", (gc.getUnitInfo(self.iUnit).getMoves(),))
		#Afforess ~ Do not show movement for air units.
		if (gc.getUnitInfo(self.iUnit).getAirRange() <= 0):
			screen.appendListBoxStringNoUpdate(panelName, u"<font=4>" + szMovement.upper() + u"%c" % CyGame().getSymbolID(FontSymbols.MOVES_CHAR) + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)
		if (gc.getUnitInfo(self.iUnit).getProductionCost() >= 0 and not gc.getUnitInfo(self.iUnit).isFound()):
			szName = self.top.getNextWidgetName()
			if self.top.iActivePlayer == -1:
				szCost = localText.getText("TXT_KEY_PEDIA_COST", ((gc.getUnitInfo(self.iUnit).getProductionCost() * gc.getDefineINT("UNIT_PRODUCTION_PERCENT"))/100,))
			else:
				szCost = localText.getText("TXT_KEY_PEDIA_COST", (gc.getActivePlayer().getUnitProductionNeeded(self.iUnit),))
			screen.appendListBoxStringNoUpdate(panelName, u"<font=4>" + szCost.upper() + u"%c" % gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar() + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)
		if (gc.getUnitInfo(self.iUnit).getAirRange() > 0):
			szName = self.top.getNextWidgetName()
			szRange = localText.getText("TXT_KEY_PEDIA_RANGE", (gc.getUnitInfo(self.iUnit).getAirRange(),))
			screen.appendListBoxStringNoUpdate(panelName, u"<font=4>" + szRange.upper() + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)
		screen.updateListBox(panelName)



	def placeRequires(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_REQUIRES", ()), "", False, True, self.X_PREREQ_PANE, self.Y_PREREQ_PANE, self.W_PREREQ_PANE, self.H_PREREQ_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")
		
		iPrereqCiv = gc.getUnitInfo(self.iUnit).getPrereqCiv()
		if (iPrereqCiv != CivilizationTypes.NO_CIVILIZATION):
			screen.attachImageButton( panelName, "", gc.getCivilizationInfo(iPrereqCiv).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, iPrereqCiv, 1, False )
		
		iPrereq = gc.getUnitInfo(self.iUnit).getPrereqAndTech()
		if (iPrereq >= 0):
			screen.attachImageButton(panelName, "", gc.getTechInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iPrereq, 1, False)
		for j in range(gc.getDefineINT("NUM_UNIT_AND_TECH_PREREQS")):
			iPrereq = gc.getUnitInfo(self.iUnit).getPrereqAndTechs(j)
			if (iPrereq >= 0):
				screen.attachImageButton(panelName, "", gc.getTechInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iPrereq, -1, False)
		bFirst = True
		iPrereq = gc.getUnitInfo(self.iUnit).getPrereqAndBonus()
		if (iPrereq >= 0):
			bFirst = False
			screen.attachImageButton(panelName, "", gc.getBonusInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iPrereq, -1, False)

##--------	BUGFfH: Modified by Denev 2009/09/26
		"Even if AND resource doesn't exist, bracket off OR resources"
		"""
		nOr = 0
		for j in range(gc.getNUM_UNIT_PREREQ_OR_BONUSES()):
			if (gc.getUnitInfo(self.iUnit).getPrereqOrBonuses(j) > -1):
				nOr += 1
		szLeftDelimeter = ""
		szRightDelimeter = ""
		if (not bFirst):
			if (nOr > 1):
				szLeftDelimeter = localText.getText("TXT_KEY_AND", ()) + "("
				szRightDelimeter = ") "
			elif (nOr > 0):
				szLeftDelimeter = localText.getText("TXT_KEY_AND", ())
		if len(szLeftDelimeter) > 0:
			screen.attachLabel(panelName, "", szLeftDelimeter)
		bFirst = True
		for j in range(gc.getNUM_UNIT_PREREQ_OR_BONUSES()):
			eBonus = gc.getUnitInfo(self.iUnit).getPrereqOrBonuses(j)
			if (eBonus > -1):
				if (not bFirst):
					screen.attachLabel(panelName, "", localText.getText("TXT_KEY_OR", ()))
				else:
					bFirst = False
				screen.attachImageButton(panelName, "", gc.getBonusInfo(eBonus).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, eBonus, -1, False)
		if len(szRightDelimeter) > 0:
			screen.attachLabel(panelName, "", szRightDelimeter)
		"""
		"list up all OR resources"
		liBonusPrereq = []
		for iIndex in range(gc.getNUM_UNIT_PREREQ_OR_BONUSES()):
			iBonusPrereq = gc.getUnitInfo(self.iUnit).getPrereqOrBonuses(iIndex)
			if (iBonusPrereq != BonusTypes.NO_BONUS):
				liBonusPrereq.append(iBonusPrereq)

		"place OR resources"
		if not bFirst:
			if len(liBonusPrereq) > 0:
				screen.attachLabel(panelName, "", localText.getText("TXT_KEY_AND", ()))
		if len(liBonusPrereq) > 1:
			screen.attachLabel(panelName, "", "(")

		bFirst = true
		for iBonusPrereq in liBonusPrereq:
			if not bFirst:
				screen.attachLabel(panelName, "", localText.getText("TXT_KEY_OR", ()))
			screen.attachImageButton( panelName, "", gc.getBonusInfo(iBonusPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iBonusPrereq, -1, False )
			bFirst = false

		if len(liBonusPrereq) > 1:
			screen.attachLabel(panelName, "", ")")
##--------	BUGFfH: End Modify

##--------	BUGFfH: Moved to below(*1) by Denev 2009/10/07
		"""
		iPrereq = gc.getUnitInfo(self.iUnit).getPrereqReligion()
		if (iPrereq >= 0):
			screen.attachImageButton(panelName, "", gc.getReligionInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_HELP_RELIGION, iPrereq, -1, False)
		"""
##--------	BUGFfH: End Move

		iPrereq = gc.getUnitInfo(self.iUnit).getPrereqBuilding()
		if (iPrereq >= 0):
			screen.attachImageButton(panelName, "", gc.getBuildingInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iPrereq, -1, False)

##--------	BUGFfH: Added by Denev 2009/10/07
		iPrereq = gc.getUnitInfo(self.iUnit).getPrereqBuildingClass()
		if (iPrereq >= 0):
			liAvailableBuilding = self.top.getListTrainableBuilding(iPrereq, self.iUnit)
			if len(liAvailableBuilding) == 1:
				iPrereq = liAvailableBuilding[0]
			elif self.top.iActiveCiv != CivilizationTypes.NO_CIVILIZATION\
			 and gc.getCivilizationInfo(self.top.iActiveCiv).getCivilizationBuildings(iPrereq) in liAvailableBuilding:
				iPrereq = gc.getCivilizationInfo(self.top.iActiveCiv).getCivilizationBuildings(iPrereq)
			else:
				iPrereq = gc.getBuildingClassInfo(iPrereq).getDefaultBuildingIndex()
			screen.attachImageButton( panelName, "", gc.getBuildingInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iPrereq, -1, False )

		iPrereq = gc.getUnitInfo(self.iUnit).getPrereqCivic()
		if (iPrereq >= 0):
			screen.attachImageButton( panelName, "", gc.getCivicInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC, iPrereq, -1, False )
##--------	BUGFfH: End Add

##--------	BUGFfH: Moved from above(*1) by Denev 2009/10/07
		# add religion buttons
		iPrereq = gc.getUnitInfo(self.iUnit).getStateReligion()
		if (iPrereq != ReligionTypes.NO_RELIGION):
			screen.attachLabel(panelName, "", u"  <font=3>(" + localText.getText("TXT_KEY_PEDIA_REQ_STATE_RELIGION", ()) + u"</font>")
			screen.attachImageButton( panelName, "", gc.getReligionInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, iPrereq, -1, False )
			screen.attachLabel(panelName, "", u"<font=3>)</font>")
		else:
			iPrereq = gc.getUnitInfo(self.iUnit).getPrereqReligion()
			if (iPrereq != ReligionTypes.NO_RELIGION):
				screen.attachLabel(panelName, "", u"  <font=3>(" + localText.getText("TXT_KEY_PEDIA_REQ_CITY_HAS", ()) + u"</font>")
				screen.attachImageButton( panelName, "", gc.getReligionInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, iPrereq, -1, False )
				screen.attachLabel(panelName, "", u"<font=3>)</font>")
##--------	BUGFfH: End Move

##--------	BUGFfH: Added by Denev 2009/10/07
		# add spell buttons
		if gc.getUnitInfo(self.iUnit).getProductionCost() < 0:
			liSummining = []
			liReincarnation = []
			for iSpell in range(gc.getNumSpellInfos()):
				if self.iUnit == gc.getSpellInfo(iSpell).getCreateUnitType():
					liSummining.append(iSpell)
				if self.iUnit == gc.getSpellInfo(iSpell).getConvertUnitType():
					liReincarnation.append(iSpell)
			for iSummining in liSummining:
				screen.attachImageButton( panelName, "", gc.getSpellInfo(iSummining).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_SPELL, iSummining, -1, False )
			if len(liSummining) == 0:
				for iReincarnation in liReincarnation:
					screen.attachImageButton( panelName, "", gc.getSpellInfo(iReincarnation).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_SPELL, iReincarnation, -1, False )
##--------	BUGFfH: End Add



	def placeUpgradesTo(self):

##--------	BUGFfH: Added by Denev 2009/10/07
		if not self.getUnitType(self.iUnit):
##--------	BUGFfH: End Add

			screen = self.top.getScreen()
			panelName = self.top.getNextWidgetName()
			screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_UPGRADES_TO", ()), "", False, True, self.X_UPGRADES_TO_PANE, self.Y_UPGRADES_TO_PANE, self.W_UPGRADES_TO_PANE, self.H_UPGRADES_TO_PANE, PanelStyles.PANEL_STYLE_BLUE50)
			screen.attachLabel(panelName, "", "  ")
##--------	BUGFfH: Modified by Denev 2009/10/07
			"""
			for k in range(gc.getNumUnitClassInfos()):
				if self.top.iActivePlayer == -1:
					eLoopUnit = gc.getUnitClassInfo(k).getDefaultUnitIndex()
				else:
					eLoopUnit = gc.getCivilizationInfo(gc.getGame().getActiveCivilizationType()).getCivilizationUnits(k)
				if (eLoopUnit >= 0 and gc.getUnitInfo(self.iUnit).getUpgradeUnitClass(k)):
					screen.attachImageButton(panelName, "", gc.getUnitInfo(eLoopUnit).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, eLoopUnit, 1, False)
			"""
			#get available civilizations which can use the selected unit.
			liAvailableCiv = self.top.getListUnitCivilization(self.iUnit)

			#if active player's civilization can use the selected unit, adopt it only.
			if self.top.iActiveCiv in liAvailableCiv:
				liAvailableCiv = [self.top.iActiveCiv]

			ltUpgradeUnit = []
			for iUpgradeUnitClass in range(gc.getNumUnitClassInfos()):
				ltUpgradeUnitTemp = []

				#get UnitType (and icon) on each avilable civilization
				for iAvailableCiv in liAvailableCiv:
					iUpgradeUnit = gc.getCivilizationInfo(iAvailableCiv).getCivilizationUnits(iUpgradeUnitClass)

					#does loop UnitClass match to the unit as upgrade target?
					if iUpgradeUnit != UnitTypes.NO_UNIT\
					and gc.getUnitInfo(self.iUnit).getUpgradeUnitClass(iUpgradeUnitClass)\
					and not gc.getUnitInfo(iUpgradeUnit).isDisableUpgradeTo():
						szUnitIcon = gc.getUnitInfo(iUpgradeUnit).getUnitButtonWithCivArtStyle(iAvailableCiv)
						ltUpgradeUnitTemp.append( (iUpgradeUnit, szUnitIcon) )

				#remove repeated items
				ltUpgradeUnitTemp = sorted(set(ltUpgradeUnitTemp))

				#if UnitType and icon can be selected uniquely, adopt it.
				if len(ltUpgradeUnitTemp) == 1:
					ltUpgradeUnit.append(ltUpgradeUnitTemp[0])
				#if more than one kind of unit icon exists, adopt default.
				elif len(ltUpgradeUnitTemp) > 1:
					iUpgradeUnit = gc.getUnitClassInfo(iUpgradeUnitClass).getDefaultUnitIndex()
					szUnitIcon = gc.getUnitInfo(iUpgradeUnit).getButton()
					ltUpgradeUnit.append( (iUpgradeUnit, szUnitIcon) )

			#place unit icons.
			for iUpgradeUnit, szUpgradeUnitName in ltUpgradeUnit:
				screen.attachImageButton(panelName, "", szUpgradeUnitName, GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUpgradeUnit, 1, False)
##--------	BUGFfH: End Modify



	def placeSpecial(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_SPECIAL_ABILITIES", ()), "", True, False, self.X_SPECIAL_PANE, self.Y_SPECIAL_PANE, self.W_SPECIAL_PANE, self.H_SPECIAL_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		listName = self.top.getNextWidgetName()
##--------	BUGFfH: Modified by Denev 2009/10/07
		"""
		szSpecialText = CyGameTextMgr().getUnitHelp(self.iUnit, True, False, False, None)[1:]
		screen.addMultilineText(listName, szSpecialText, self.X_SPECIAL_PANE+5, self.Y_SPECIAL_PANE+30, self.W_SPECIAL_PANE-10, self.H_SPECIAL_PANE-35, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		"""
		szSpecialText = CyGameTextMgr().getUnitHelp( self.iUnit, True, False, False, None )
		szSpecialText = szSpecialText.strip("\n")	#Trim empty line
		screen.addMultilineText(listName, szSpecialText, self.X_SPECIAL_PANE + 5, self.Y_SPECIAL_PANE + 30, self.W_SPECIAL_PANE - 5, self.H_SPECIAL_PANE - 32, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
##--------	BUGFfH: End Modify



	def placeHistory(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY", ()), "", True, True, self.X_HISTORY_PANE, self.Y_HISTORY_PANE, self.W_HISTORY_PANE, self.H_HISTORY_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		textName = self.top.getNextWidgetName()
		szText = u""
		if len(gc.getUnitInfo(self.iUnit).getStrategy()) > 0:
			szText += localText.getText("TXT_KEY_CIVILOPEDIA_STRATEGY", ())
			szText += gc.getUnitInfo(self.iUnit).getStrategy()
			szText += u"\n\n"
		szText += localText.getText("TXT_KEY_CIVILOPEDIA_BACKGROUND", ())
		szText += gc.getUnitInfo(self.iUnit).getCivilopedia()
##--------	BUGFfH: Modified by Denev 2009/08/16
#		screen.addMultilineText(textName, szText, self.X_HISTORY_PANE + 15, self.Y_HISTORY_PANE + 40, self.W_HISTORY_PANE - (15 * 2), self.H_HISTORY_PANE - (15 * 2) - 25, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.addMultilineText(textName, szText, self.X_HISTORY_PANE + 5, self.Y_HISTORY_PANE + 30, self.W_HISTORY_PANE - 5, self.H_HISTORY_PANE - 32, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
##--------	BUGFfH: End Modify



	def placePromotions(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_CATEGORY_PROMOTION", ()), "", True, True, self.X_PROMO_PANE, self.Y_PROMO_PANE, self.W_PROMO_PANE, self.H_PROMO_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		rowListName = self.top.getNextWidgetName()
##--------	BUGFfH: Added by Denev 2009/08/12 (from CvPediaUnit.py by Kael)
#		screen.addMultiListControlGFC(rowListName, "", self.X_PROMO_PANE+15, self.Y_PROMO_PANE+40, self.W_PROMO_PANE-20, self.H_PROMO_PANE-40, 1, self.PROMOTION_ICON_SIZE, self.PROMOTION_ICON_SIZE, TableStyles.TABLE_STYLE_STANDARD)
		iChanneling1 = gc.getInfoTypeForString('PROMOTION_CHANNELING1')
		iChanneling2 = gc.getInfoTypeForString('PROMOTION_CHANNELING2')
		iChanneling3 = gc.getInfoTypeForString('PROMOTION_CHANNELING3')

		liAvailablePromo = []
##--------	BUGFfH: End Add
		for k in range(gc.getNumPromotionInfos()):
			if (isPromotionValid(k, self.iUnit, False) and not gc.getPromotionInfo(k).isGraphicalOnly()):
##--------	BUGFfH: Added by Denev 2009/08/12 (from CvPediaUnit.py by Kael)
#				screen.appendMultiListButton(rowListName, gc.getPromotionInfo(k).getButton(), 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, k, -1, False)
				if (gc.getPromotionInfo(k).getPromotionPrereqAnd() != iChanneling1 or gc.getUnitInfo(self.iUnit).getFreePromotions(iChanneling1)):
					if (gc.getPromotionInfo(k).getPromotionPrereqAnd() != iChanneling2 or gc.getUnitInfo(self.iUnit).getFreePromotions(iChanneling2)):
						if (gc.getPromotionInfo(k).getPromotionPrereqAnd() != iChanneling3 or gc.getUnitInfo(self.iUnit).getFreePromotions(iChanneling3)):
							liAvailablePromo.append(k)
		if len(liAvailablePromo) > 20:
			iIconSize = self.PROMOTION_ICON_SIZE_SMALL
		else:
			iIconSize = self.PROMOTION_ICON_SIZE
		screen.addMultiListControlGFC(rowListName, "", self.X_PROMO_PANE+5, self.Y_PROMO_PANE+30, self.W_PROMO_PANE-5, self.H_PROMO_PANE-30, 1, iIconSize, iIconSize, TableStyles.TABLE_STYLE_STANDARD)

		for iAvailablePromo in liAvailablePromo:
			screen.appendMultiListButton( rowListName, gc.getPromotionInfo(iAvailablePromo).getButton(), 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iAvailablePromo, -1, false )
##--------	BUGFfH: End Add

	def getUnitType(self, iUnit):
		if isWorldUnitClass(gc.getUnitInfo(iUnit).getUnitClassType()):
			return SevoScreenEnums.TYPE_WORLDUNIT
		bSummon=false
		for i in range(gc.getNumSpellInfos()):
			if gc.getSpellInfo(i).getCreateUnitType()==iUnit:
				bSummon=true
				break
		if bSummon:
			return SevoScreenEnums.TYPE_SUMMON
		return SevoScreenEnums.TYPE_REGULAR


	def handleInput (self, inputClass):
		return 0
