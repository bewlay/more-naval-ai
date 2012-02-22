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

class SevoPediaEquipment:

	def __init__(self, main):
		self.iEquipment = -1
		self.top = main
	
		self.BUTTON_SIZE = 46
		
		self.X_UNIT_PANE = self.top.X_PEDIA_PAGE
		self.Y_UNIT_PANE = self.top.Y_PEDIA_PAGE
		self.W_UNIT_PANE = 216
		self.H_UNIT_PANE = self.W_UNIT_PANE

		self.W_ICON = 150
		self.H_ICON = 150
		self.X_ICON = self.X_UNIT_PANE + (self.H_UNIT_PANE - self.H_ICON) / 2
		self.Y_ICON = self.Y_UNIT_PANE + (self.H_UNIT_PANE - self.H_ICON) / 2
		self.ICON_SIZE = 64

		self.X_UNIT_ANIMATION = self.X_UNIT_PANE + self.W_UNIT_PANE + 10
		self.W_UNIT_ANIMATION = self.top.R_PEDIA_PAGE - self.X_UNIT_ANIMATION
		self.Y_UNIT_ANIMATION = self.Y_UNIT_PANE + 7
		self.H_UNIT_ANIMATION = self.H_UNIT_PANE - 7
		self.X_ROTATION_UNIT_ANIMATION = -20
		self.Z_ROTATION_UNIT_ANIMATION = 30
		self.SCALE_ANIMATION = 0.7

		self.W_SPELL_PANE = self.top.W_PEDIA_PAGE
		self.H_SPELL_PANE = 110

		self.X_SPELL_PANE = self.X_UNIT_PANE
		self.Y_SPELL_PANE = self.top.B_PEDIA_PAGE - self.H_SPELL_PANE

		self.X_SPECIAL_PANE = self.X_UNIT_PANE
		self.Y_SPECIAL_PANE = self.Y_UNIT_PANE + self.H_UNIT_PANE + 10
		self.W_SPECIAL_PANE = self.top.W_PEDIA_PAGE
		self.H_SPECIAL_PANE = self.Y_SPELL_PANE - self.Y_SPECIAL_PANE - 10



	def interfaceScreen(self, iEquipment):
		self.iEquipment = iEquipment
		screen = self.top.getScreen()

#BUGFfH: Added by Denev 2009/08/16
		# Header...
		szHeader = u"<font=4b>" + gc.getPromotionInfo(self.iEquipment).getDescription() + u"</font>"
		szHeaderId = "PediaMainHeader"
		screen.setText(szHeaderId, "Background", szHeader, CvUtil.FONT_CENTER_JUSTIFY, self.top.X_SCREEN, self.top.Y_TITLE, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
#BUGFfH: End Add

		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_UNIT_PANE, self.Y_UNIT_PANE, self.W_UNIT_PANE, self.H_UNIT_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_MAIN)
		screen.addDDSGFC(self.top.getNextWidgetName(), gc.getPromotionInfo(self.iEquipment).getButton(), self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1)

		szEquipmentName = gc.getPromotionInfo(self.iEquipment).getDescription()
		for iUnit in range(gc.getNumUnitInfos()):
			if gc.getUnitInfo(iUnit).getDescription() == szEquipmentName:
				self.iUnit = iUnit
				screen.addUnitGraphicGFC(self.top.getNextWidgetName(), self.iUnit, self.X_UNIT_ANIMATION, self.Y_UNIT_ANIMATION, self.W_UNIT_ANIMATION, self.H_UNIT_ANIMATION, WidgetTypes.WIDGET_GENERAL, -1, -1, self.X_ROTATION_UNIT_ANIMATION, self.Z_ROTATION_UNIT_ANIMATION, self.SCALE_ANIMATION, True)
				break

		self.placeSpecial()
		self.placeSpells()



	def placeSpecial(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_SPECIAL_ABILITIES", ()), "", True, False, self.X_SPECIAL_PANE, self.Y_SPECIAL_PANE, self.W_SPECIAL_PANE, self.H_SPECIAL_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		listName = self.top.getNextWidgetName()
		szSpecialText = CyGameTextMgr().getPromotionHelp(self.iEquipment, True)[1:]
		screen.addMultilineText(listName, szSpecialText, self.X_SPECIAL_PANE+5, self.Y_SPECIAL_PANE+30, self.W_SPECIAL_PANE-10, self.H_SPECIAL_PANE-35, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	# Place Leads To...
	def placeSpells(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_SPELLS (or LEADS_TO)", ()), "", false, true, self.X_SPELL_PANE, self.Y_SPELL_PANE, self.W_SPELL_PANE, self.H_SPELL_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")
		for j in range(gc.getNumSpellInfos()):
			iPrereq = gc.getSpellInfo(j).getPromotionPrereq1()
			if (iPrereq == self.iEquipment):
				screen.attachImageButton( panelName, "", gc.getSpellInfo(j).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_SPELL, j, 1, False )
			iPrereq = gc.getSpellInfo(j).getPromotionPrereq2()
			if (iPrereq == self.iEquipment):
				screen.attachImageButton( panelName, "", gc.getSpellInfo(j).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_SPELL, j, 1, False )



	def handleInput (self, inputClass):
		return 0
