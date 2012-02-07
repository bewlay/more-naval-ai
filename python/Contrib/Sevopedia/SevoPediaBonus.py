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

class SevoPediaBonus:

	def __init__(self, main):
		self.iBonus = -1
		self.top = main

##--------	BUGFfH: Added by Denev 2009/10/07
		X_MERGIN = self.top.X_MERGIN
		Y_MERGIN = self.top.Y_MERGIN
##--------	BUGFfH: End Add

##--------	BUGFfH: Modified by Denev 2009/10/09
		self.X_BONUS_PANE = self.top.X_PEDIA_PAGE
		self.Y_BONUS_PANE = self.top.Y_PEDIA_PAGE
		self.W_BONUS_PANE = (self.top.W_PEDIA_PAGE - X_MERGIN) / 2
		self.H_BONUS_PANE = 116

		self.W_ICON = 100
		self.H_ICON = 100
		self.X_ICON = self.X_BONUS_PANE + (self.H_BONUS_PANE - self.H_ICON) / 2
		self.Y_ICON = self.Y_BONUS_PANE + (self.H_BONUS_PANE - self.H_ICON) / 2
		self.ICON_SIZE = 64

		self.X_STATUS = self.X_ICON + self.W_ICON + 10
		self.Y_STATUS = self.Y_ICON + 20
		self.W_STATUS = self.X_BONUS_PANE + self.W_BONUS_PANE - self.X_STATUS
		self.H_STATUS = self.Y_BONUS_PANE + self.H_BONUS_PANE - self.Y_STATUS

		self.X_BONUS_ANIMATION = self.X_BONUS_PANE + self.W_BONUS_PANE + X_MERGIN
		self.Y_BONUS_ANIMATION = self.Y_BONUS_PANE + 7
		self.W_BONUS_ANIMATION = self.top.R_PEDIA_PAGE - self.X_BONUS_ANIMATION 
		self.H_BONUS_ANIMATION = self.H_BONUS_PANE - 7
		self.X_ROTATION_BONUS_ANIMATION = -20
		self.Z_ROTATION_BONUS_ANIMATION = 30
		self.SCALE_ANIMATION = 0.7

		self.X_IMPROVEMENTS = self.X_BONUS_PANE
		self.W_IMPROVEMENTS = self.W_BONUS_PANE
		self.Y_IMPROVEMENTS = self.Y_BONUS_PANE + self.H_BONUS_PANE + Y_MERGIN
		self.H_IMPROVEMENTS = 150

		self.X_EFFECTS = self.X_BONUS_ANIMATION
		self.W_EFFECTS = self.W_BONUS_ANIMATION
		self.Y_EFFECTS = self.Y_IMPROVEMENTS
		self.H_EFFECTS = self.H_IMPROVEMENTS

		self.X_REQUIRES = self.X_BONUS_PANE
		self.W_REQUIRES = self.W_BONUS_PANE
		self.Y_REQUIRES = self.Y_IMPROVEMENTS + self.H_IMPROVEMENTS + Y_MERGIN
		self.H_REQUIRES = 110

		self.X_BUILDINGS = self.X_BONUS_ANIMATION
		self.W_BUILDINGS = self.W_BONUS_ANIMATION
		self.Y_BUILDINGS = self.Y_REQUIRES
		self.H_BUILDINGS = self.H_REQUIRES

		self.X_ALLOWS = self.X_BONUS_PANE
		self.W_ALLOWS = self.top.R_PEDIA_PAGE - self.X_ALLOWS
		self.Y_ALLOWS = self.Y_REQUIRES + self.H_REQUIRES + Y_MERGIN
		self.H_ALLOWS = 110

		self.X_HISTORY = self.X_ALLOWS
		self.W_HISTORY = self.W_ALLOWS
		self.Y_HISTORY = self.Y_ALLOWS + self.H_ALLOWS + Y_MERGIN
		self.H_HISTORY = self.top.B_PEDIA_PAGE - self.Y_HISTORY
##--------	BUGFfH: End Modify



	def interfaceScreen(self, iBonus):
		self.iBonus = iBonus
		screen = self.top.getScreen()

##--------	BUGFfH: Added by Denev 2009/08/16
		# Header...
		szHeader = u"<font=4b>" + gc.getBonusInfo(self.iBonus).getDescription() + u"</font>"
		szHeaderId = "PediaMainHeader"
		screen.setText(szHeaderId, "Background", szHeader, CvUtil.FONT_CENTER_JUSTIFY, self.top.X_SCREEN, self.top.Y_TITLE, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
##--------	BUGFfH: End Add

		screen.addPanel( self.top.getNextWidgetName(), "", "", False, False, self.X_BONUS_PANE, self.Y_BONUS_PANE, self.W_BONUS_PANE, self.H_BONUS_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_MAIN)
		screen.addDDSGFC(self.top.getNextWidgetName(), gc.getBonusInfo(self.iBonus).getButton(), self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		screen.addBonusGraphicGFC(self.top.getNextWidgetName(), self.iBonus, self.X_BONUS_ANIMATION, self.Y_BONUS_ANIMATION, self.W_BONUS_ANIMATION, self.H_BONUS_ANIMATION, WidgetTypes.WIDGET_GENERAL, -1, -1, self.X_ROTATION_BONUS_ANIMATION, self.Z_ROTATION_BONUS_ANIMATION, self.SCALE_ANIMATION, True)

		self.placeStats()
		self.placeYield()
		self.placeRequires()
		self.placeBuildings()
		self.placeAllows()
		self.placeSpecial()
		self.placeHistory()



	def placeStats(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addListBoxGFC(panelName, "", self.X_STATUS, self.Y_STATUS, self.W_STATUS, self.H_STATUS, TableStyles.TABLE_STYLE_EMPTY)
		screen.enableSelect(panelName, False)

##--------	BUGFfH: Added by Denev 2009/10/09
		szTitle = u"<font=3>" + localText.getText("TXT_KEY_BONUS_TILE_MODIFIER", ()).upper() + u"<font>"
		screen.appendListBoxString(panelName, szTitle, WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

		bEffect = false
##--------	BUGFfH: End Add
		for k in range(YieldTypes.NUM_YIELD_TYPES):
			iYieldChange = gc.getBonusInfo(self.iBonus).getYieldChange(k)
			if (iYieldChange != 0):
				if (iYieldChange > 0):
					sign = "+"
				else:
					sign = ""
				szYield = (u"%s: %s%i " % (gc.getYieldInfo(k).getDescription(), sign, iYieldChange))
				screen.appendListBoxString(panelName, u"<font=3>" + szYield.upper() + (u"%c" % gc.getYieldInfo(k).getChar()) + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)
##--------	BUGFfH: Added by Denev 2009/10/09
				bEffect = true
		if not bEffect:
			screen.hide(panelName)
##--------	BUGFfH: End Add



	def placeYield(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_CATEGORY_IMPROVEMENT", ()), "", False, True, self.X_IMPROVEMENTS, self.Y_IMPROVEMENTS, self.W_IMPROVEMENTS, self.H_IMPROVEMENTS, PanelStyles.PANEL_STYLE_BLUE50 )
		bonusInfo = gc.getBonusInfo(self.iBonus)
		for j in range(gc.getNumImprovementInfos()):
			bFirst = True
			szYield = u""
			bEffect = False
			for k in range(YieldTypes.NUM_YIELD_TYPES):
				iYieldChange = gc.getImprovementInfo(j).getImprovementBonusYield(self.iBonus, k)
				if (iYieldChange != 0):
					bEffect = True
					iYieldChange += gc.getImprovementInfo(j).getYieldChange(k)
					if (bFirst):
						bFirst = False
					else:
						szYield += ", "
					if (iYieldChange > 0):
						sign = "+"
					else:
						sign = ""
##--------	BUGFfH: Modified by Denev 2009/10/09
#					szYield += (u"%s%i%c" % (sign, iYieldChange, gc.getYieldInfo(k).getChar()))
					szYield += (u"<font=3>%s%i</font>%c" % (sign, iYieldChange, gc.getYieldInfo(k).getChar()))
##--------	BUGFfH: End Modify

##--------	BUGFfH: Added by Denev 2009/09/23
				"Mana Nodes and World Improvements"
				if gc.getImprovementInfo(j).getBonusConvert() == self.iBonus:
					bEffect = True
##--------	BUGFfH: End Add

			if (bEffect):
				childPanelName = self.top.getNextWidgetName()
				screen.attachPanel(panelName, childPanelName, "", "", False, False, PanelStyles.PANEL_STYLE_EMPTY)
				screen.attachLabel(childPanelName, "", "  ")
				screen.attachImageButton(childPanelName, "", gc.getImprovementInfo(j).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_IMPROVEMENT, j, 1, False )
				screen.attachLabel(childPanelName, "", szYield)



	def placeSpecial(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_EFFECTS", ()), "", True, False,
				 self.X_EFFECTS, self.Y_EFFECTS, self.W_EFFECTS, self.H_EFFECTS, PanelStyles.PANEL_STYLE_BLUE50 )
		listName = self.top.getNextWidgetName()
##--------	BUGFfH: Deleted by Denev 2009/09/11
#		screen.attachListBoxGFC( panelName, listName, "", TableStyles.TABLE_STYLE_EMPTY )
#		screen.enableSelect(listName, False)
##--------	BUGFfH: End Delete
		szSpecialText = CyGameTextMgr().getBonusHelp(self.iBonus, True)
##--------	BUGFfH: Modofied by Denev 2009/10/09
		"""
		splitText = string.split( szSpecialText, "\n" )
		for special in splitText:
			if len( special ) != 0:
				screen.appendListBoxString( listName, special, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
		"""
		szSpecialText = szSpecialText.strip("\n")	#trim empty lines
		screen.addMultilineText(listName, szSpecialText, self.X_EFFECTS + 5, self.Y_EFFECTS + 30, self.W_EFFECTS - 5, self.H_EFFECTS - 32, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
##--------	BUGFfH: End Modify



	def placeRequires(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_REQUIRES", ()), "", False, True, self.X_REQUIRES, self.Y_REQUIRES, self.W_REQUIRES, self.H_REQUIRES, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.attachLabel(panelName, "", "  ")
		iTech = gc.getBonusInfo(self.iBonus).getTechReveal()
		if (iTech > -1):
			screen.attachImageButton( panelName, "", gc.getTechInfo(iTech).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iTech, 1, False )
			screen.attachLabel(panelName, "", u"(" + localText.getText("TXT_KEY_PEDIA_BONUS_APPEARANCE", ()) + u")")
		iTech = gc.getBonusInfo(self.iBonus).getTechCityTrade()
		if (iTech > -1):
			screen.attachImageButton( panelName, "", gc.getTechInfo(iTech).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iTech, 1, False )
			screen.attachLabel(panelName, "", u"(" + localText.getText("TXT_KEY_PEDIA_BONUS_TRADE", ()) + u")")



	def placeHistory(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName,localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY", ()), "", True, True, self.X_HISTORY, self.Y_HISTORY, self.W_HISTORY, self.H_HISTORY, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")
		textName = self.top.getNextWidgetName()
##--------	BUGFfH: Modified by Denev 2009/08/16
#		screen.addMultilineText( textName, gc.getBonusInfo(self.iBonus).getCivilopedia(), self.X_HISTORY_PANE + 15, self.Y_HISTORY_PANE + 40, self.W_HISTORY_PANE - (30), self.H_HISTORY_PANE - (15 * 2) - 25, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.addMultilineText( textName, gc.getBonusInfo(self.iBonus).getCivilopedia(), self.X_HISTORY + 5, self.Y_HISTORY + 30, self.W_HISTORY - 5, self.H_HISTORY - 32, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
##--------	BUGFfH: End Modify



	def placeBuildings(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
##--------	BUGFfH: Modified by Denev 2009/10/09
#		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_CATEGORY_BUILDING", ()), "", False, True, self.X_BUILDINGS, self.Y_BUILDINGS, self.W_BUILDINGS, self.H_BUILDINGS, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_PRODUCING_BUILDINGS", ()), "", false, true, self.X_BUILDINGS, self.Y_BUILDINGS, self.W_BUILDINGS, self.H_BUILDINGS, PanelStyles.PANEL_STYLE_BLUE50 )
##--------	BUGFfH: End Modify
		screen.attachLabel(panelName, "", "  ")
		for iBuilding in range(gc.getNumBuildingInfos()):
##--------	BUGFfH: Modified by Denev 2009/10/09
			"""
			info = gc.getBuildingInfo(iBuilding)
			bShow = (info.getFreeBonus() == self.iBonus
					or info.getBonusHealthChanges(self.iBonus) > 0
					or info.getBonusHappinessChanges(self.iBonus) > 0
					or info.getBonusProductionModifier(self.iBonus) > 0)
			if (not bShow):
				for eYield in range(YieldTypes.NUM_YIELD_TYPES):
					if (info.getBonusYieldModifier(self.iBonus, eYield) > 0):
						bShow = True
						break
			if (bShow):
			"""
			liFreeBonus = [	gc.getBuildingInfo(iBuilding).getFreeBonus(),
							gc.getBuildingInfo(iBuilding).getFreeBonus2(),
							gc.getBuildingInfo(iBuilding).getFreeBonus3()]
			if self.iBonus in liFreeBonus:
##--------	BUGFfH: End Modify
				screen.attachImageButton( panelName, "", gc.getBuildingInfo(iBuilding).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iBuilding, 1, False )



	def placeAllows(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_ALLOWS", ()), "", False, True, self.X_ALLOWS, self.Y_ALLOWS, self.W_ALLOWS, self.H_ALLOWS, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.attachLabel(panelName, "", "  ")
		for eLoopUnit in range(gc.getNumUnitInfos()):
			bFound = False
			if (eLoopUnit >= 0):
				if (gc.getUnitInfo(eLoopUnit).getPrereqAndBonus() == self.iBonus):
					bFound = True	
				else:
					j = 0
					while (not bFound and j < gc.getNUM_UNIT_PREREQ_OR_BONUSES()):
						if (gc.getUnitInfo(eLoopUnit).getPrereqOrBonuses(j) == self.iBonus):
							bFound = True
						j += 1
			if bFound:
				screen.attachImageButton( panelName, "", gc.getUnitInfo(eLoopUnit).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, eLoopUnit, 1, False )

		for eLoopBuilding in range(gc.getNumBuildingInfos()):
			bFound = False
			if (gc.getBuildingInfo(eLoopBuilding).getPrereqAndBonus() == self.iBonus):
				bFound = True
			else:
				j = 0
				while (not bFound and j < gc.getNUM_BUILDING_PREREQ_OR_BONUSES()):
					if (gc.getBuildingInfo(eLoopBuilding).getPrereqOrBonuses(j) == self.iBonus):
						bFound = True
					j += 1
			if bFound:
				screen.attachImageButton( panelName, "", gc.getBuildingInfo(eLoopBuilding).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, eLoopBuilding, 1, False )

##--------	BUGFfH: Added by Denev 2009/10/09
		# add promotion buttons
		for eLoopPromotion in range(gc.getNumPromotionInfos()):
			bFound = False
			if (gc.getPromotionInfo(eLoopPromotion).getBonusPrereq() == self.iBonus):
				screen.attachImageButton( panelName, "", gc.getPromotionInfo(eLoopPromotion).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, eLoopPromotion, 1, False )
##--------	BUGFfH: End Add

	def getBonusType(self, iBonus):
		if gc.getBonusInfo(iBonus).getBonusClassType()==gc.getInfoTypeForString("BONUSCLASS_MANA"):
			return SevoScreenEnums.TYPE_BONUS_MANA
		return SevoScreenEnums.TYPE_REGULAR				



	def handleInput (self, inputClass):
		return 0
