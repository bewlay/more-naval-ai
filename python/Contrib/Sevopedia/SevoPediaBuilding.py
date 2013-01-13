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

class SevoPediaBuilding:

	def __init__(self, main):
		self.iBuilding = -1
		self.top = main

##--------	BUGFfH: Modified by Denev 2009/10/08
		self.iBuildingClass = BuildingClassTypes.NO_BUILDINGCLASS

		X_MERGIN = self.top.X_MERGIN
		Y_MERGIN = self.top.Y_MERGIN

		self.X_MAIN_PANE = self.top.X_PEDIA_PAGE
		self.Y_MAIN_PANE = self.top.Y_PEDIA_PAGE
		self.W_MAIN_PANE = 323
		self.H_MAIN_PANE = 160

		self.W_ICON = 120
		self.H_ICON = 120
		self.X_ICON = self.X_MAIN_PANE + 10
		self.Y_ICON = self.Y_MAIN_PANE + (self.H_MAIN_PANE - self.H_ICON) / 2
		self.ICON_SIZE = 64

		self.X_STATUS = self.X_ICON + self.W_ICON
		self.Y_STATUS = self.Y_ICON
		self.W_STATUS = self.X_MAIN_PANE + self.W_MAIN_PANE - self.X_STATUS
		self.H_STATUS = self.Y_MAIN_PANE + self.H_MAIN_PANE - self.Y_STATUS

		self.X_BUILDING_ANIMATION = self.X_MAIN_PANE + self.W_MAIN_PANE + X_MERGIN
		self.Y_BUILDING_ANIMATION = self.Y_MAIN_PANE + 7
		self.W_BUILDING_ANIMATION = self.top.R_PEDIA_PAGE - self.X_BUILDING_ANIMATION
		self.H_BUILDING_ANIMATION = self.Y_MAIN_PANE + self.H_MAIN_PANE - self.Y_BUILDING_ANIMATION
		self.X_ROTATION_BUILDING_ANIMATION = -20
		self.Z_ROTATION_BUILDING_ANIMATION = 30
		self.SCALE_ANIMATION = 0.7

		self.X_REQUIRES = self.X_MAIN_PANE
		self.Y_REQUIRES = self.Y_MAIN_PANE + self.H_MAIN_PANE + Y_MERGIN
		self.W_REQUIRES = (self.top.W_PEDIA_PAGE - X_MERGIN) / 2
		self.H_REQUIRES = 110

		self.X_ALLOWS = self.X_REQUIRES + self.W_REQUIRES + X_MERGIN
		self.Y_ALLOWS = self.Y_REQUIRES
		self.W_ALLOWS = self.top.R_PEDIA_PAGE - self.X_ALLOWS
		self.H_ALLOWS = self.H_REQUIRES

		self.X_SPECIAL = self.X_REQUIRES
		self.Y_SPECIAL = self.Y_REQUIRES + self.H_REQUIRES + Y_MERGIN
		self.W_SPECIAL = self.top.W_PEDIA_PAGE
		self.H_SPECIAL = 166

		self.X_HISTORY = self.X_SPECIAL
		self.Y_HISTORY = self.Y_SPECIAL + self.H_SPECIAL + Y_MERGIN
		self.W_HISTORY = self.W_SPECIAL
		self.H_HISTORY = self.top.B_PEDIA_PAGE - self.Y_HISTORY
##--------	BUGFfH: End Modify



	def interfaceScreen(self, iBuilding):
		self.iBuilding = iBuilding
##--------	BUGFfH: Added by Denev 2009/10/09
		self.iBuildingClass = gc.getBuildingInfo(iBuilding).getBuildingClassType()
##--------	BUGFfH: End Add
		screen = self.top.getScreen()

##--------	BUGFfH: Added by Denev 2009/08/16
		# Header...
		szHeader = u"<font=4b>" + gc.getBuildingInfo(self.iBuilding).getDescription() + u"</font>"
		szHeaderId = "PediaMainHeader"
		screen.setText(szHeaderId, "Background", szHeader, CvUtil.FONT_CENTER_JUSTIFY, self.top.X_SCREEN, self.top.Y_TITLE, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
##--------	BUGFfH: End Add

		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_MAIN_PANE, self.Y_MAIN_PANE, self.W_MAIN_PANE, self.H_MAIN_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_MAIN)
		screen.addDDSGFC(self.top.getNextWidgetName(), gc.getBuildingInfo(self.iBuilding).getButton(), self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		screen.addBuildingGraphicGFC(self.top.getNextWidgetName(), self.iBuilding, self.X_BUILDING_ANIMATION, self.Y_BUILDING_ANIMATION, self.W_BUILDING_ANIMATION, self.H_BUILDING_ANIMATION, WidgetTypes.WIDGET_GENERAL, -1, -1, self.X_ROTATION_BUILDING_ANIMATION, self.Z_ROTATION_BUILDING_ANIMATION, self.SCALE_ANIMATION, True)

		self.placeStats()
		self.placeRequires()
##--------	BUGFfH: Added by Denev 2009/10/08
		self.placeAllows()
##--------	BUGFfH: End Add
		self.placeSpecial()
		self.placeHistory()



	def placeStats(self):
		screen = self.top.getScreen()
		buildingInfo = gc.getBuildingInfo(self.iBuilding)
		panelName = self.top.getNextWidgetName()
		screen.addListBoxGFC(panelName, "", self.X_STATUS, self.Y_STATUS, self.W_STATUS, self.H_STATUS, TableStyles.TABLE_STYLE_EMPTY)
		screen.enableSelect(panelName, False)

		if (isWorldWonderClass(gc.getBuildingInfo(self.iBuilding).getBuildingClassType())):
			iMaxInstances = gc.getBuildingClassInfo(gc.getBuildingInfo(self.iBuilding).getBuildingClassType()).getMaxGlobalInstances()
			szBuildingType = localText.getText("TXT_KEY_PEDIA_WORLD_WONDER", ())
			if (iMaxInstances > 1):
				szBuildingType += " " + localText.getText("TXT_KEY_PEDIA_WONDER_INSTANCES", (iMaxInstances,))
				screen.appendListBoxStringNoUpdate(panelName, u"<font=4>" + szBuildingType.upper() + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

		if (isTeamWonderClass(gc.getBuildingInfo(self.iBuilding).getBuildingClassType())):
			iMaxInstances = gc.getBuildingClassInfo(gc.getBuildingInfo(self.iBuilding).getBuildingClassType()).getMaxTeamInstances()
			szBuildingType = localText.getText("TXT_KEY_PEDIA_TEAM_WONDER", ())
			if (iMaxInstances > 1):
				szBuildingType += " " + localText.getText("TXT_KEY_PEDIA_WONDER_INSTANCES", (iMaxInstances,))
				screen.appendListBoxStringNoUpdate(panelName, u"<font=4>" + szBuildingType.upper() + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

		if (isNationalWonderClass(gc.getBuildingInfo(self.iBuilding).getBuildingClassType())):
			iMaxInstances = gc.getBuildingClassInfo(gc.getBuildingInfo(self.iBuilding).getBuildingClassType()).getMaxPlayerInstances()
			szBuildingType = localText.getText("TXT_KEY_PEDIA_NATIONAL_WONDER", ())
			if (iMaxInstances > 1):
				szBuildingType += " " + localText.getText("TXT_KEY_PEDIA_WONDER_INSTANCES", (iMaxInstances,))
				screen.appendListBoxStringNoUpdate(panelName, u"<font=4>" + szBuildingType.upper() + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

		if (buildingInfo.getProductionCost() > 0):
			if self.top.iActivePlayer == -1:
				szCost = localText.getText("TXT_KEY_PEDIA_COST", ((buildingInfo.getProductionCost() * gc.getDefineINT("BUILDING_PRODUCTION_PERCENT"))/100,))
			else:
				szCost = localText.getText("TXT_KEY_PEDIA_COST", (gc.getPlayer(self.top.iActivePlayer).getBuildingProductionNeeded(self.iBuilding),))
			screen.appendListBoxStringNoUpdate(panelName, u"<font=4>" + szCost.upper() + u"%c" % gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar() + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

		for k in range(YieldTypes.NUM_YIELD_TYPES):
			if (buildingInfo.getYieldChange(k) != 0):
				if (buildingInfo.getYieldChange(k) > 0):
					szSign = "+"
				else:
					szSign = ""
				szYield = gc.getYieldInfo(k).getDescription() + ": "
				szText1 = szYield.upper() + szSign + str(buildingInfo.getYieldChange(k))
				szText2 = szText1 + (u"%c" % (gc.getYieldInfo(k).getChar()))
				screen.appendListBoxStringNoUpdate(panelName, u"<font=3>" + szText2 + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

		for k in range(CommerceTypes.NUM_COMMERCE_TYPES):
			iTotalCommerce = buildingInfo.getObsoleteSafeCommerceChange(k) + buildingInfo.getCommerceChange(k)
			if (iTotalCommerce != 0):
				if (iTotalCommerce > 0):
					szSign = "+"
				else:
					szSign = ""
				szCommerce = gc.getCommerceInfo(k).getDescription() + ": "
				szText1 = szCommerce.upper() + szSign + str(iTotalCommerce)
				szText2 = szText1 + (u"%c" % (gc.getCommerceInfo(k).getChar()))
				screen.appendListBoxStringNoUpdate(panelName, u"<font=3>" + szText2 + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

		iHappiness = buildingInfo.getHappiness()
		if self.top.iActivePlayer != -1:
			if (self.iBuilding == gc.getCivilizationInfo(gc.getPlayer(self.top.iActivePlayer).getCivilizationType()).getCivilizationBuildings(buildingInfo.getBuildingClassType())):
				iHappiness += gc.getPlayer(self.top.iActivePlayer).getExtraBuildingHappiness(self.iBuilding)

		if (iHappiness > 0):
			szText = localText.getText("TXT_KEY_PEDIA_HAPPY", (iHappiness,)).upper()
			screen.appendListBoxStringNoUpdate(panelName, u"<font=3>" + szText + u"%c" % CyGame().getSymbolID(FontSymbols.HAPPY_CHAR) + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)
		elif (iHappiness < 0):
			szText = localText.getText("TXT_KEY_PEDIA_UNHAPPY", (-iHappiness,)).upper()
			screen.appendListBoxStringNoUpdate(panelName, u"<font=3>" + szText + u"%c" % CyGame().getSymbolID(FontSymbols.UNHAPPY_CHAR) + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

		iHealth = buildingInfo.getHealth()
		if self.top.iActivePlayer != -1:
			if (self.iBuilding == gc.getCivilizationInfo(gc.getPlayer(self.top.iActivePlayer).getCivilizationType()).getCivilizationBuildings(buildingInfo.getBuildingClassType())):
				iHealth += gc.getPlayer(self.top.iActivePlayer).getExtraBuildingHealth(self.iBuilding)

		if (iHealth > 0):
			szText = localText.getText("TXT_KEY_PEDIA_HEALTHY", (iHealth,)).upper()
			screen.appendListBoxStringNoUpdate(panelName, u"<font=3>" + szText + u"%c" % CyGame().getSymbolID(FontSymbols.HEALTHY_CHAR) + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)
		elif (iHealth < 0):
			szText = localText.getText("TXT_KEY_PEDIA_UNHEALTHY", (-iHealth,)).upper()
			screen.appendListBoxStringNoUpdate(panelName, u"<font=3>" + szText + u"%c" % CyGame().getSymbolID(FontSymbols.UNHEALTHY_CHAR) + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

		if (buildingInfo.getGreatPeopleRateChange() != 0):
			szText = localText.getText("TXT_KEY_PEDIA_GREAT_PEOPLE", (buildingInfo.getGreatPeopleRateChange(),)).upper()
			screen.appendListBoxStringNoUpdate(panelName, u"<font=3>" + szText + u"%c" % CyGame().getSymbolID(FontSymbols.GREAT_PEOPLE_CHAR) + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

		screen.updateListBox(panelName)



	def placeRequires(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_REQUIRES", ()), "", False, True, self.X_REQUIRES, self.Y_REQUIRES, self.W_REQUIRES, self.H_REQUIRES, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.attachLabel(panelName, "", "  ")

		iPrereqCiv = gc.getBuildingInfo(self.iBuilding).getPrereqCiv()
		if (iPrereqCiv != CivilizationTypes.NO_CIVILIZATION):
			screen.attachImageButton( panelName, "", gc.getCivilizationInfo(iPrereqCiv).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, iPrereqCiv, 1, False )

		for iPrereq in range(gc.getNumTechInfos()):
			if isTechRequiredForBuilding(iPrereq, self.iBuilding):
				screen.attachImageButton( panelName, "", gc.getTechInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iPrereq, 1, False )

		iPrereq = gc.getBuildingInfo(self.iBuilding).getPrereqAndBonus()
		if (iPrereq >= 0):
			screen.attachImageButton( panelName, "", gc.getBonusInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iPrereq, -1, False )

		for k in range(gc.getNUM_BUILDING_PREREQ_OR_BONUSES()):
			iPrereq = gc.getBuildingInfo(self.iBuilding).getPrereqOrBonuses(k)
			if (iPrereq >= 0):
				screen.attachImageButton( panelName, "", gc.getBonusInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iPrereq, -1, False )

		iCorporation = gc.getBuildingInfo(self.iBuilding).getFoundsCorporation()
		bFirst = True
		if (iCorporation >= 0):
			for k in range(gc.getNUM_CORPORATION_PREREQ_BONUSES()):
				iPrereq = gc.getCorporationInfo(iCorporation).getPrereqBonus(k)
				if (iPrereq >= 0):
					if not bFirst:
						screen.attachLabel(panelName, "", localText.getText("TXT_KEY_OR", ()))
					else:
						bFirst = False
					screen.attachImageButton( panelName, "", gc.getBonusInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iPrereq, -1, False )

##--------	BUGFfH: Added by Denev 2009/10/08
#		# add trait buttons
#		iTrait = gc.getBuildingInfo(self.iBuilding).getPrereqTrait()
#		if iTrait != TraitTypes.NO_TRAIT:
#			screen.attachImageButton( panelName, "", gc.getTraitInfo(iTrait).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TRAIT, iTrait, -1, False )

		# add building buttons
		for iBuildingClass in range(gc.getNumBuildingClassInfos()):
			if gc.getBuildingInfo(self.iBuilding).isBuildingClassNeededInCity(iBuildingClass):
				iBuilding = gc.getBuildingClassInfo(iBuildingClass).getDefaultBuildingIndex()
				screen.attachImageButton( panelName, "", gc.getBuildingInfo(iBuilding).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iBuilding, -1, False )
##--------	BUGFfH: End Add

		# add religion button
##--------	BUGFfH: Modified by Denev 2009/09/25
		"""
		iPrereq = gc.getBuildingInfo(self.iBuilding).getPrereqReligion()
		if (iPrereq >= 0):
			screen.attachImageButton( panelName, "", gc.getReligionInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, iPrereq, -1, False )
		"""
		iPrereq = gc.getBuildingInfo(self.iBuilding).getStateReligion()
		if (iPrereq != ReligionTypes.NO_RELIGION):
			screen.attachLabel(panelName, "", u"  <font=3>(" + localText.getText("TXT_KEY_PEDIA_REQ_STATE_RELIGION", ()) + u"</font>")
			screen.attachImageButton( panelName, "", gc.getReligionInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, iPrereq, -1, False )
			screen.attachLabel(panelName, "", u")")
		else:
			iPrereq = gc.getBuildingInfo(self.iBuilding).getPrereqReligion()
			if (iPrereq != ReligionTypes.NO_RELIGION):
				screen.attachLabel(panelName, "", u"  <font=3>(" + localText.getText("TXT_KEY_PEDIA_REQ_CITY_HAS", ()) + u"</font>")
				screen.attachImageButton( panelName, "", gc.getReligionInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, iPrereq, -1, False )
				screen.attachLabel(panelName, "", u")")
##--------	BUGFfH: End Modify

##--------	BUGFfH: Added by Denev 2009/09/24
		if gc.getBuildingInfo(self.iBuilding).getProductionCost() < 0:
			if not gc.getBuildingInfo(self.iBuilding).isEquipment():
				# add unit buttons
				liUnit = []
				for iUnit in range(gc.getNumUnitInfos()):
					if gc.getUnitInfo(iUnit).getBuildings(self.iBuilding):
						liUnit.append(iUnit)
				if len(liUnit) > 1:
					screen.attachLabel(panelName, "", u"(")
				bFirst = true
				for iUnit in liUnit:
					if not bFirst:
						screen.attachLabel(panelName, "", localText.getText("TXT_KEY_OR", ()))
					bFirst = false
					screen.attachImageButton( panelName, "", gc.getUnitInfo(iUnit).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUnit, -1, False )
				if len(liUnit) > 1:
					screen.attachLabel(panelName, "", u")")

				# add spell buttons
				for iSpell in range(gc.getNumSpellInfos()):
					if self.iBuilding == gc.getSpellInfo(iSpell).getCreateBuildingType():
						screen.attachImageButton( panelName, "", gc.getSpellInfo(iSpell).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_SPELL, iSpell, -1, False )

	# Place Allows
	def placeAllows(self):
		screen = self.top.getScreen()

		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_ALLOWS", ()), "", false, true,
						 self.X_ALLOWS, self.Y_ALLOWS, self.W_ALLOWS, self.H_ALLOWS, PanelStyles.PANEL_STYLE_BLUE50 )

		screen.attachLabel(panelName, "", "  ")

		# add unit buttons
		"get available civilizations which can use the selected building"
		liAvailableCiv = self.top.getListBuildingCivilization(self.iBuilding)

		"if active player's civilization can use the selected building, adopt it only."
		if self.top.iActiveCiv in liAvailableCiv:
			liAvailableCiv = [self.top.iActiveCiv]

		ltAllowUnit = []
		for iAllowUnit in range(gc.getNumUnitInfos()):
			"if loop unit has negative cost (can not be built), skip it"
			if gc.getUnitInfo(iAllowUnit).getProductionCost() < 0:
				continue

			ltAllowUnitTemp = []
			iUnitClass = gc.getUnitInfo(iAllowUnit).getUnitClassType()

			"does loop UnitType match to the allow target?"
			siAvailableCiv = set(liAvailableCiv) & set(self.top.getListUnitCivilization(iAllowUnit))
			if siAvailableCiv != set([]):
				if self.iBuilding == gc.getUnitInfo(iAllowUnit).getPrereqBuilding()\
				or self.iBuildingClass == gc.getUnitInfo(iAllowUnit).getPrereqBuildingClass():
					"get unit icon on each avilable civilization"
					for iAvailableCiv in liAvailableCiv:
						szUnitIcon = gc.getUnitInfo(iAllowUnit).getUnitButtonWithCivArtStyle(iAvailableCiv)
						ltAllowUnitTemp.append( (iUnitClass, iAllowUnit, szUnitIcon) )
					ltAllowUnitTemp = sorted(set(ltAllowUnitTemp))	#remove repeated items

			if len(ltAllowUnitTemp) == 1:
				"if UnitType and icon can be selected uniquely, adopt it"
				ltAllowUnit.append(ltAllowUnitTemp[0])
			elif len(ltAllowUnitTemp) > 1:
				"if more than one kind of unit icon exists, adopt default"
				szUnitIcon = gc.getUnitInfo(iAllowUnit).getButton()
				ltAllowUnit.append( (iUnitClass, iAllowUnit, szUnitIcon) )

		for tAllowUnit in ltAllowUnit:
			screen.attachImageButton(panelName, "", tAllowUnit[2], GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, tAllowUnit[1], 1, False)

		# add building buttons
		for iBuilding in range(gc.getNumBuildingInfos()):
			if gc.getBuildingInfo(iBuilding).isBuildingClassNeededInCity(self.iBuildingClass):
				screen.attachImageButton( panelName, "", gc.getBuildingInfo(iBuilding).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iBuilding, -1, False )

		# add spell buttons
		for iSpell in range(gc.getNumSpellInfos()):
			if self.iBuilding == gc.getSpellInfo(iSpell).getBuildingPrereq()\
			or self.iBuildingClass == gc.getSpellInfo(iSpell).getBuildingClassOwnedPrereq():
				screen.attachImageButton( panelName, "", gc.getSpellInfo(iSpell).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_SPELL, iSpell, -1, False )
##--------	BUGFfH: End Add



	def placeSpecial(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_SPECIAL_ABILITIES", ()), "", True, False, self.X_SPECIAL, self.Y_SPECIAL, self.W_SPECIAL, self.H_SPECIAL, PanelStyles.PANEL_STYLE_BLUE50 )
		listName = self.top.getNextWidgetName()
		szSpecialText = CyGameTextMgr().getBuildingHelp(self.iBuilding, True, False, False, None)[1:]
##--------	BUGFfH: Modified by Denev 2009/09/11
#		screen.addMultilineText(listName, szSpecialText, self.X_SPECIAL_PANE+5, self.Y_SPECIAL_PANE+30, self.W_SPECIAL_PANE-10, self.H_SPECIAL_PANE-35, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.addMultilineText(listName, szSpecialText, self.X_SPECIAL+5, self.Y_SPECIAL+30, self.W_SPECIAL-5, self.H_SPECIAL-32, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
##--------	BUGFfH: End Modify



	def placeHistory(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY", ()), "", True, True, self.X_HISTORY, self.Y_HISTORY, self.W_HISTORY, self.H_HISTORY, PanelStyles.PANEL_STYLE_BLUE50 )
		textName = self.top.getNextWidgetName()
		szText = u""
		if len(gc.getBuildingInfo(self.iBuilding).getStrategy()) > 0:
			szText += localText.getText("TXT_KEY_CIVILOPEDIA_STRATEGY", ())
			szText += gc.getBuildingInfo(self.iBuilding).getStrategy()
			szText += u"\n\n"
		szText += localText.getText("TXT_KEY_CIVILOPEDIA_BACKGROUND", ())
		szText += gc.getBuildingInfo(self.iBuilding).getCivilopedia()
##--------	BUGFfH: Modified by Denev 2009/08/16
#		screen.addMultilineText( textName, szText, self.X_HISTORY_PANE + 15, self.Y_HISTORY_PANE + 40, self.W_HISTORY_PANE - (15 * 2), self.H_HISTORY_PANE - (15 * 2) - 25, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.attachMultilineText(panelName, textName, szText, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
##--------	BUGFfH: End Modify



##--------	BUGFfH: Modified by Denev 2009/10/08
		"""
	def getBuildingType(self, iBuilding):
		if (isWorldWonderClass(gc.getBuildingInfo(iBuilding).getBuildingClassType())):
			return 2
		elif (isNationalWonderClass(gc.getBuildingInfo(iBuilding).getBuildingClassType())):
			return 1
		else:
			return 0
		"""
	def getBuildingType(self, iBuilding):
		if (isWorldWonderClass(gc.getBuildingInfo(iBuilding).getBuildingClassType())):
			return SevoScreenEnums.TYPE_WORLD

		if (isTeamWonderClass(gc.getBuildingInfo(iBuilding).getBuildingClassType())):
			return SevoScreenEnums.TYPE_TEAM

		if (isNationalWonderClass(gc.getBuildingInfo(iBuilding).getBuildingClassType())):
			return SevoScreenEnums.TYPE_NATIONAL

		return SevoScreenEnums.TYPE_REGULAR
##--------	BUGFfH: End Modify



##--------	BUGFfH: Deleted by Denev 2009/10/08
		"""
	def getBuildingSortedList(self, iBuildingType):
		list1 = []
		numInfos = 0
		for iBuilding in range(gc.getNumBuildingInfos()):
			if (self.getBuildingType(iBuilding) == iBuildingType):
				list1.append(iBuilding)
				numInfos += 1
		list2 = [(0,0)] * numInfos
		i = 0
		for iBuilding in list1:
			list2[i] = (gc.getBuildingInfo(iBuilding).getDescription(), iBuilding)
			i += 1
		if self.top.isSortLists():
			list2.sort()
		return list2
		"""
##--------	BUGFfH: End Delete



	def handleInput (self, inputClass):
		return 0
