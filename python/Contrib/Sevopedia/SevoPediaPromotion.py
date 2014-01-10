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

class SevoPediaPromotion:

	def __init__(self, main):
		self.iPromotion = -1
		self.top = main

##--------	BUGFfH: Added by Denev 2009/10/07
		X_MERGIN = self.top.X_MERGIN
		Y_MERGIN = self.top.Y_MERGIN
##--------	BUGFfH: End Add

		self.BUTTON_SIZE = 46
		
##--------	BUGFfH: Modified by Denev 2009/10/07
		self.X_UNIT_PANE = self.top.X_PEDIA_PAGE
		self.Y_UNIT_PANE = self.top.Y_PEDIA_PAGE
		self.W_UNIT_PANE = 200
		self.H_UNIT_PANE = 116

		self.W_ICON = 100
		self.H_ICON = 100
		self.X_ICON = self.X_UNIT_PANE + (self.H_UNIT_PANE - self.H_ICON) / 2
		self.Y_ICON = self.Y_UNIT_PANE + (self.H_UNIT_PANE - self.H_ICON) / 2
		self.ICON_SIZE = 64

		self.X_PREREQ_PANE = self.X_UNIT_PANE + self.W_UNIT_PANE + X_MERGIN
		self.Y_PREREQ_PANE = self.Y_UNIT_PANE
		self.W_PREREQ_PANE = self.top.R_PEDIA_PAGE - self.X_PREREQ_PANE
		self.H_PREREQ_PANE = self.H_UNIT_PANE

		self.X_LEADS_TO_PANE = self.X_UNIT_PANE
		self.Y_LEADS_TO_PANE = self.Y_UNIT_PANE + self.H_UNIT_PANE + Y_MERGIN
		self.W_LEADS_TO_PANE = self.top.R_PEDIA_PAGE - self.X_LEADS_TO_PANE
		self.H_LEADS_TO_PANE = 110
				
		self.X_SPELL_PANE = self.X_UNIT_PANE
		self.Y_SPELL_PANE = self.top.B_PEDIA_PAGE - self.H_LEADS_TO_PANE
		self.W_SPELL_PANE = self.top.R_PEDIA_PAGE - self.X_LEADS_TO_PANE
		self.H_SPELL_PANE = self.H_LEADS_TO_PANE

		self.X_SPECIAL_PANE = self.X_UNIT_PANE
		self.Y_SPECIAL_PANE = self.Y_LEADS_TO_PANE + self.H_LEADS_TO_PANE + Y_MERGIN
		self.W_SPECIAL_PANE = (self.top.W_PEDIA_PAGE - X_MERGIN) * 2 / 3
		self.H_SPECIAL_PANE = self.Y_SPELL_PANE - self.Y_SPECIAL_PANE - Y_MERGIN

		self.X_UNIT_GROUP_PANE = self.X_SPECIAL_PANE + self.W_SPECIAL_PANE + X_MERGIN
		self.Y_UNIT_GROUP_PANE = self.Y_SPECIAL_PANE
		self.W_UNIT_GROUP_PANE = self.top.R_PEDIA_PAGE - self.X_UNIT_GROUP_PANE
		self.H_UNIT_GROUP_PANE = self.H_SPECIAL_PANE
##--------	BUGFfH: End Modify



	def interfaceScreen(self, iPromotion):
		self.iPromotion = iPromotion
		screen = self.top.getScreen()

##--------	BUGFfH: Added by Denev 2009/08/16
		# Header...
		szHeader = u"<font=4b>" + gc.getPromotionInfo(self.iPromotion).getDescription() + u"</font>"
		szHeaderId = "PediaMainHeader"
		screen.setText(szHeaderId, "Background", szHeader, CvUtil.FONT_CENTER_JUSTIFY, self.top.X_SCREEN, self.top.Y_TITLE, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
##--------	BUGFfH: End Add

		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_UNIT_PANE, self.Y_UNIT_PANE, self.W_UNIT_PANE, self.H_UNIT_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_MAIN)
		screen.addDDSGFC(self.top.getNextWidgetName(), gc.getPromotionInfo(self.iPromotion).getButton(), self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1)

		self.placePrereqs()
		self.placeLeadsTo()
		self.placeSpecial()
##--------	BUGFfH: Added by Denev 2009/08/12 (from CvPediaPromotion.py by Kael)
		self.placeSpells()
##--------	BUGFfH: End Add
		self.placeUnitGroups()



	def placeLeadsTo(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_LEADS_TO", ()), "", False, True, self.X_LEADS_TO_PANE, self.Y_LEADS_TO_PANE, self.W_LEADS_TO_PANE, self.H_LEADS_TO_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")
		for j in range(gc.getNumPromotionInfos()):
			iPrereq = gc.getPromotionInfo(j).getPrereqPromotion()
			if (gc.getPromotionInfo(j).getPrereqPromotion() == self.iPromotion or gc.getPromotionInfo(j).getPrereqOrPromotion1() == self.iPromotion or gc.getPromotionInfo(j).getPrereqOrPromotion2() == self.iPromotion or gc.getPromotionInfo(j).getPromotionPrereqAnd() == self.iPromotion):
				screen.attachImageButton(panelName, "", gc.getPromotionInfo(j).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, j, 1, False)



	def placePrereqs(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_REQUIRES", ()), "", False, True, self.X_PREREQ_PANE, self.Y_PREREQ_PANE, self.W_PREREQ_PANE, self.H_PREREQ_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")

##--------	BUGFfH: Added by Denev 2009/10/07
		"""
		ePromo = gc.getPromotionInfo(self.iPromotion).getPrereqPromotion()
		if (ePromo > -1):
			screen.attachImageButton(panelName, "", gc.getPromotionInfo(ePromo).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, ePromo, 1, False)
		ePromoOr1 = gc.getPromotionInfo(self.iPromotion).getPrereqOrPromotion1()
		ePromoOr2 = gc.getPromotionInfo(self.iPromotion).getPrereqOrPromotion2()

		if (ePromoOr1 > -1):
			if (ePromo > -1):
				screen.attachLabel(panelName, "", localText.getText("TXT_KEY_AND", ()))
				if (ePromoOr2 > -1):
					screen.attachLabel(panelName, "", "(")
			screen.attachImageButton(panelName, "", gc.getPromotionInfo(ePromoOr1).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, ePromoOr1, 1, False)
			if (ePromoOr2 > -1):
				screen.attachLabel(panelName, "", localText.getText("TXT_KEY_OR", ()))
				screen.attachImageButton(panelName, "", gc.getPromotionInfo(ePromoOr2).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, ePromoOr2, 1, False)
				if (ePromo > -1):
					screen.attachLabel(panelName, "", ")")
			if (ePromoOr3 > -1):
				screen.attachLabel(panelName, "", localText.getText("TXT_KEY_OR", ()))
				screen.attachImageButton( panelName, "", gc.getPromotionInfo(ePromoOr3).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, ePromoOr3, 1, False )

			if (ePromoOr4 > -1):
				screen.attachLabel(panelName, "", localText.getText("TXT_KEY_OR", ()))
				screen.attachImageButton( panelName, "", gc.getPromotionInfo(ePromoOr4).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, ePromoOr4, 1, False )

			if (ePromoOr2 > -1):
				screen.attachLabel(panelName, "", ")")

		eTech = gc.getPromotionInfo(self.iPromotion).getTechPrereq()
		if (eTech > -1):
			screen.attachImageButton(panelName, "", gc.getTechInfo(eTech).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, eTech, 1, False)
		eReligion = gc.getPromotionInfo(self.iPromotion).getStateReligionPrereq()
		if (eReligion > -1):
			screen.attachImageButton(panelName, "", gc.getReligionInfo(eReligion).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, eReligion, 1, False)
		"""
		liPromoAnd = []
		liPromoAnd.append(gc.getPromotionInfo(self.iPromotion).getPrereqPromotion())
		liPromoAnd.append(gc.getPromotionInfo(self.iPromotion).getPromotionPrereqAnd())
		liPromoAnd = sorted(set(liPromoAnd), key=liPromoAnd.index)	#remove repeated items
		if liPromoAnd.count(PromotionTypes.NO_PROMOTION):
			liPromoAnd.remove(PromotionTypes.NO_PROMOTION)

		liPromoOr = []
		liPromoOr.append(gc.getPromotionInfo(self.iPromotion).getPrereqOrPromotion1())
		liPromoOr.append(gc.getPromotionInfo(self.iPromotion).getPrereqOrPromotion2())
		liPromoOr.append(gc.getPromotionInfo(self.iPromotion).getPromotionPrereqOr3())
		liPromoOr.append(gc.getPromotionInfo(self.iPromotion).getPromotionPrereqOr4())
		liPromoOr = sorted(set(liPromoOr), key=liPromoOr.index)	#remove repeated items
		if liPromoOr.count(PromotionTypes.NO_PROMOTION):
			liPromoOr.remove(PromotionTypes.NO_PROMOTION)

		bFirst = true
		for iPromotion in liPromoAnd:
			if not bFirst:
				screen.attachLabel(panelName, "", localText.getText("TXT_KEY_AND", ()))
			screen.attachImageButton(panelName, "", gc.getPromotionInfo(iPromotion).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iPromotion, 1, False )
			bFirst = false

		if len(liPromoOr) and not bFirst:
			screen.attachLabel(panelName, "", localText.getText("TXT_KEY_AND", ()))

		if len(liPromoOr) > 1:
			screen.attachLabel(panelName, "", "(")

		bOrFirst = true
		for iPromotion in liPromoOr:
			if not bOrFirst:
				screen.attachLabel(panelName, "", localText.getText("TXT_KEY_OR", ()))
			screen.attachImageButton(panelName, "", gc.getPromotionInfo(iPromotion).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iPromotion, 1, False )
			bFirst = false
			bOrFirst = false

		if len(liPromoOr) > 1:
			screen.attachLabel(panelName, "", ")")

		eTech = gc.getPromotionInfo(self.iPromotion).getTechPrereq()
#		if (eTech != TechTypes.NO_TECH):
		if ((eTech > -1) and (eTech != gc.getInfoTypeForString('TECH_NEVER'))):
			if not bFirst:
				screen.attachLabel(panelName, "", localText.getText("TXT_KEY_AND", ()))
			screen.attachImageButton(panelName, "", gc.getTechInfo(eTech).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, eTech, 1, False)

		eReligion = gc.getPromotionInfo(self.iPromotion).getStateReligionPrereq()
		if (eReligion != ReligionTypes.NO_RELIGION):
			if not bFirst:
				screen.attachLabel(panelName, "", localText.getText("TXT_KEY_AND", ()))
			screen.attachLabel(panelName, "", u"  <font=3>(" + localText.getText("TXT_KEY_PEDIA_REQ_STATE_RELIGION", ()) + u"</font>")
			screen.attachImageButton(panelName, "", gc.getReligionInfo(eReligion).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, eReligion, 1, False)
			screen.attachLabel(panelName, "", u"<font=3>)</font>")

		eUnitReligion = gc.getPromotionInfo(self.iPromotion).getUnitReligionPrereq()
		if (eUnitReligion != ReligionTypes.NO_RELIGION):
			if not bFirst:
				screen.attachLabel(panelName, "", localText.getText("TXT_KEY_AND", ()))
			screen.attachLabel(panelName, "", u"  <font=3>(" + localText.getText("TXT_KEY_PEDIA_REQ_UNIT_RELIGION", ()) + u"</font>")
			screen.attachImageButton(panelName, "", gc.getReligionInfo(eUnitReligion).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, eUnitReligion, 1, False)
			screen.attachLabel(panelName, "", u"<font=3>)</font>")
##--------	BUGFfH: End Modify
##-------- More Naval AI: Bonus requirements for promotions.
		eBonus = gc.getPromotionInfo(self.iPromotion).getBonusPrereq()
		if (eBonus != BonusTypes.NO_BONUS):
			if not bFirst:
				screen.attachLabel(panelName, "", localText.getText("TXT_KEY_AND", ()))
			screen.attachImageButton(panelName, "", gc.getBonusInfo(eBonus).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, eBonus, -1, False)
##-------- More Naval AI: End Modify



	def placeSpecial(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_SPECIAL_ABILITIES", ()), "", True, False, self.X_SPECIAL_PANE, self.Y_SPECIAL_PANE, self.W_SPECIAL_PANE, self.H_SPECIAL_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		listName = self.top.getNextWidgetName()
		szSpecialText = CyGameTextMgr().getPromotionHelp(self.iPromotion, True)[1:]
##--------	BUGFfH: Modified by Denev 2009/09/11
#		screen.addMultilineText(listName, szSpecialText, self.X_SPECIAL_PANE+5, self.Y_SPECIAL_PANE+30, self.W_SPECIAL_PANE-10, self.H_SPECIAL_PANE-35, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.addMultilineText(listName, szSpecialText, self.X_SPECIAL_PANE+5, self.Y_SPECIAL_PANE+30, self.W_SPECIAL_PANE-5, self.H_SPECIAL_PANE-32, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
##--------	BUGFfH: End Modify



	def placeUnitGroups(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_PROMOTION_UNITS", ()), "", True, True, self.X_UNIT_GROUP_PANE, self.Y_UNIT_GROUP_PANE, self.W_UNIT_GROUP_PANE, self.H_UNIT_GROUP_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		szTable = self.top.getNextWidgetName()
##--------	BUGFfH: Modified by Denev 2009/10/07
#		screen.addTableControlGFC(szTable, 1, self.X_UNIT_GROUP_PANE + 10, self.Y_UNIT_GROUP_PANE + 40, self.W_UNIT_GROUP_PANE - 20, self.H_UNIT_GROUP_PANE - 50, False, False, 24, 24, TableStyles.TABLE_STYLE_EMPTY)
		screen.addTableControlGFC(szTable, 1, self.X_UNIT_GROUP_PANE + 5, self.Y_UNIT_GROUP_PANE + 36, self.W_UNIT_GROUP_PANE - 5, self.H_UNIT_GROUP_PANE - 38, False, False, 24, 24, TableStyles.TABLE_STYLE_EMPTY)
##--------	BUGFfH: End Modify
##--------	BUGFfH: Deleted by Denev 2009/10/09
#		i = 0
##--------	BUGFfH: End Delete
		for iI in range(gc.getNumUnitCombatInfos()):
			if (0 != gc.getPromotionInfo(self.iPromotion).getUnitCombat(iI)):
				iRow = screen.appendTableRow(szTable)
##--------	BUGFfH: Modified by Denev 2009/10/07
#				screen.setTableText(szTable, 0, i, u"<font=2>" + gc.getUnitCombatInfo(iI).getDescription() + u"</font>", gc.getUnitCombatInfo(iI).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT_COMBAT, iI, -1, CvUtil.FONT_LEFT_JUSTIFY)
				screen.setTableText(szTable, 0, iRow, u"<font=3>" + gc.getUnitCombatInfo(iI).getDescription() + u"</font>", gc.getUnitCombatInfo(iI).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT_COMBAT, iI, -1, CvUtil.FONT_LEFT_JUSTIFY)
##--------	BUGFfH: End Modify
##--------	BUGFfH: Deleted by Denev 2009/10/09
#				i += 1
##--------	BUGFfH: End Delete



##--------	BUGFfH: Added by Denev 2009/08/12 (from CvPediaPromotion.py by Kael)
	# Place Leads To...
	def placeSpells(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_SPELLS (or LEADS_TO)", ()), "", false, true, self.X_SPELL_PANE, self.Y_SPELL_PANE, self.W_SPELL_PANE, self.H_SPELL_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")
		for j in range(gc.getNumSpellInfos()):
			iPrereq = gc.getSpellInfo(j).getPromotionPrereq1()
			if (iPrereq == self.iPromotion):
				screen.attachImageButton( panelName, "", gc.getSpellInfo(j).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_SPELL, j, 1, False )
			iPrereq = gc.getSpellInfo(j).getPromotionPrereq2()
			if (iPrereq == self.iPromotion):
				screen.attachImageButton( panelName, "", gc.getSpellInfo(j).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_SPELL, j, 1, False )

	def isMagicSpherePromotion(self, pPromotion):
		iBonus = pPromotion.getBonusPrereq()

		# If the promotion itself requires mana, it is a magic sphere promotion.
		if iBonus != BonusTypes.NO_BONUS and gc.getBonusInfo(iBonus).getBonusClassType() == gc.getInfoTypeForString('BONUSCLASS_MANA'):
			return True

		lChannelingPromotions = [gc.getInfoTypeForString('PROMOTION_CHANNELING2'), gc.getInfoTypeForString('PROMOTION_CHANNELING3')]

		# If the current promotion requires channeling 2 or 3, it is possible that it is a magic sphere promotion if it also requires a magic sphere promotion.
		if (pPromotion.getPrereqPromotion() in lChannelingPromotions or pPromotion.getPromotionPrereqAnd() in lChannelingPromotions):
			iRequirementOther = PromotionTypes.NO_PROMOTION
			if pPromotion.getPrereqPromotion() not in lChannelingPromotions:
				iRequirementOther = pPromotion.getPrereqPromotion()
			elif pPromotion.getPromotionPrereqAnd() not in lChannelingPromotions:
				iRequirementOther = pPromotion.getPrereqPromotion()
			if iRequirementOther != PromotionTypes.NO_PROMOTION:
				return self.isMagicSpherePromotion(gc.getPromotionInfo(iRequirementOther))

		return False

	def getPromotionType(self, iPromotion):
		if (gc.getPromotionInfo(iPromotion).isRace()):
			return SevoScreenEnums.TYPE_RACE
		elif (gc.getPromotionInfo(iPromotion).isEquipment()):
			return SevoScreenEnums.TYPE_EQUIPMENT
#		elif (gc.getPromotionInfo(iPromotion).isGear()):
#			return SevoScreenEnums.TYPE_GEAR			
		elif (gc.getPromotionInfo(iPromotion).getMinLevel() < 0):
			return SevoScreenEnums.TYPE_EFFECT
		elif self.isMagicSpherePromotion(gc.getPromotionInfo(iPromotion)):
			return SevoScreenEnums.TYPE_SPHERE
		else:
			return SevoScreenEnums.TYPE_REGULAR
##--------	BUGFfH: End Add



	def handleInput (self, inputClass):
		return 0
