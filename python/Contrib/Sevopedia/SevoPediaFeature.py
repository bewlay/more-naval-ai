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

class SevoPediaFeature:

	def __init__(self, main):
		self.iFeature = -1
		self.top = main

##--------	BUGFfH: Added by Denev 2009/10/07
		X_MERGIN = self.top.X_MERGIN
		Y_MERGIN = self.top.Y_MERGIN

		self.W_REQUIRES = 200
		self.H_REQUIRES = 110
		self.X_REQUIRES = self.top.R_PEDIA_PAGE - self.W_REQUIRES
		self.Y_REQUIRES = self.top.Y_PEDIA_PAGE

		self.X_UPGRADES_TO = self.X_REQUIRES
		self.Y_UPGRADES_TO = self.Y_REQUIRES + self.H_REQUIRES + Y_MERGIN
		self.W_UPGRADES_TO = self.W_REQUIRES
		self.H_UPGRADES_TO = 110
##--------	BUGFfH: End Add

		self.X_ICON_PANE = self.top.X_PEDIA_PAGE
		self.Y_ICON_PANE = self.top.Y_PEDIA_PAGE
##--------	BUGFfH: Modified by Denev 2009/10/07
		"""
		self.W_ICON_PANE = self.top.W_PEDIA_PAGE
		self.H_ICON_PANE = 210
		"""
		self.W_ICON_PANE = self.top.W_PEDIA_PAGE - self.W_REQUIRES - X_MERGIN
		self.H_ICON_PANE = self.Y_UPGRADES_TO + self.H_UPGRADES_TO - self.Y_ICON_PANE
##--------	BUGFfH: End Modify

		self.W_ICON = 150
		self.H_ICON = 150
		self.X_ICON = self.X_ICON_PANE + (self.H_ICON_PANE - self.H_ICON) / 2
		self.Y_ICON = self.Y_ICON_PANE + (self.H_ICON_PANE - self.H_ICON) / 2
		self.ICON_SIZE = 64

##--------	BUGFfH: Modified by Denev 2009/10/07
		"""
		self.X_STATS_PANE = self.X_ICON_PANE + 210
		self.W_STATS_PANE = self.top.R_PEDIA_PAGE - self.X_STATS_PANE
		self.Y_STATS_PANE = 130
		self.H_STATS_PANE = 110
		"""
		self.X_STATS_PANE = self.X_ICON + self.W_ICON + 10
		self.Y_STATS_PANE = self.Y_ICON
		self.W_STATS_PANE = self.X_ICON_PANE + self.W_ICON_PANE - self.X_STATS_PANE
		self.H_STATS_PANE = self.Y_ICON_PANE + self.H_ICON_PANE - self.Y_STATS_PANE
##--------	BUGFfH: End Modify

		self.X_SPECIAL_PANE = self.X_ICON_PANE
##--------	BUGFfH: Modified by Denev 2009/10/07
#		self.W_SPECIAL_PANE = self.W_ICON_PANE
		self.W_SPECIAL_PANE = self.top.W_PEDIA_PAGE
##--------	BUGFfH: End Modify
		self.Y_SPECIAL_PANE = self.Y_ICON_PANE + self.H_ICON_PANE + 10
		self.H_SPECIAL_PANE = self.top.B_PEDIA_PAGE - self.Y_SPECIAL_PANE



	def interfaceScreen(self, iFeature):
		self.iFeature = iFeature
		screen = self.top.getScreen()

##--------	BUGFfH: Added by Denev 2009/08/16
		# Header...
		szHeader = u"<font=4b>" + gc.getFeatureInfo(self.iFeature).getDescription() + u"</font>"
		szHeaderId = "PediaMainHeader"
		screen.setText(szHeaderId, "Background", szHeader, CvUtil.FONT_CENTER_JUSTIFY, self.top.X_SCREEN, self.top.Y_TITLE, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
##--------	BUGFfH: End Add

		screen.addPanel( self.top.getNextWidgetName(), "", "", False, False, self.X_ICON_PANE, self.Y_ICON_PANE, self.W_ICON_PANE, self.H_ICON_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_MAIN)
		screen.addDDSGFC(self.top.getNextWidgetName(), gc.getFeatureInfo(self.iFeature).getButton(), self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1 )

		self.placeStats()
		self.placeSpecial()
##--------	BUGFfH: Added by Denev 2009/10/07
		self.placeRequires()
		self.placeUpgradesTo()



	def placeRequires(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_REQUIRES", ()), "", False, True, self.X_REQUIRES, self.Y_REQUIRES, self.W_REQUIRES, self.H_REQUIRES, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")

		iRequires = gc.getFeatureInfo(self.iFeature).getPrereqStateReligion()
		if iRequires != ReligionTypes.NO_RELIGION:
			screen.attachImageButton(panelName, "", gc.getReligionInfo(iRequires).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, iRequires, 1, False)



	def placeUpgradesTo(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_UPGRADES_TO", ()), "", False, True, self.X_UPGRADES_TO, self.Y_UPGRADES_TO, self.W_UPGRADES_TO, self.H_UPGRADES_TO, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")

		iUpgradeFeature = gc.getFeatureInfo(self.iFeature).getFeatureUpgrade()
		if iUpgradeFeature != FeatureTypes.NO_FEATURE:
			screen.attachImageButton(panelName, "", gc.getFeatureInfo(iUpgradeFeature).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_FEATURE, iUpgradeFeature, 1, False)

			szProbability = u"<font=3>(%d%%)" % gc.getDefineINT("FEATURE_UPGRADE_CHANCE")
			iRequires = gc.getFeatureInfo(iUpgradeFeature).getPrereqStateReligion()
			if iRequires != ReligionTypes.NO_RELIGION:
				szProbability += u"\n(%c: %c)" % (CyGame().getSymbolID(FontSymbols.RELIGION_CHAR), gc.getReligionInfo(iRequires).getChar())
			szProbability += u"</font>"
			screen.attachLabel(panelName, "", szProbability)
##--------	BUGFfH: End Add



	def placeStats(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addListBoxGFC(panelName, "", self.X_STATS_PANE, self.Y_STATS_PANE, self.W_STATS_PANE, self.H_STATS_PANE, TableStyles.TABLE_STYLE_EMPTY)
		screen.enableSelect(panelName, False)
		for k in range(YieldTypes.NUM_YIELD_TYPES):
			iYieldChange = gc.getFeatureInfo(self.iFeature).getYieldChange(k)
			if (iYieldChange != 0):
				if (iYieldChange > 0):
					sign = "+"
				else:
					sign = ""
				szYield = (u"%s: %s%i " % (gc.getYieldInfo(k).getDescription().upper(), sign, iYieldChange))
				screen.appendListBoxString(panelName, u"<font=3>" + szYield + (u"%c" % gc.getYieldInfo(k).getChar()) + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)



	def placeSpecial(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_SPECIAL_ABILITIES", ()), "", True, False, self.X_SPECIAL_PANE, self.Y_SPECIAL_PANE, self.W_SPECIAL_PANE, self.H_SPECIAL_PANE, PanelStyles.PANEL_STYLE_BLUE50 )
		listName = self.top.getNextWidgetName()
		screen.attachListBoxGFC( panelName, listName, "", TableStyles.TABLE_STYLE_EMPTY )
		screen.enableSelect(listName, False)
		szSpecialText = CyGameTextMgr().getFeatureHelp(self.iFeature, True)
		
		szSpecialText += u"\n\n" + gc.getFeatureInfo(self.iFeature).getCivilopedia()
##--------	BUGFfH: Modified by Denev 2009/10/07
		"""
		splitText = string.split( szSpecialText, "\n" )
		for special in splitText:
			if len( special ) != 0:
				screen.appendListBoxString( listName, special, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
		"""
		szSpecialText = szSpecialText.strip("\n")	#trim empty lines
		screen.addMultilineText(listName, szSpecialText, self.X_SPECIAL_PANE + 5, self.Y_SPECIAL_PANE + 30, self.W_SPECIAL_PANE - 5, self.H_SPECIAL_PANE - 32, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
##--------	BUGFfH: End Modify



	def handleInput (self, inputClass):
		return 0
