# SevoPediaTrait
#
# Copyright (c) 2008 The BUG Mod.

from CvPythonExtensions import *
import CvUtil
import ScreenInput
import SevoScreenEnums
import string

#BUGFfH: Deleted by Denev 2009/09/11
#import TraitUtil
#BUGFfH: End Delete

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class SevoPediaTrait:

	def __init__(self, main):
		self.iTrait = -1
		self.top = main

		self.X_MAIN_PANE = self.top.X_PEDIA_PAGE
		self.Y_MAIN_PANE = self.top.Y_PEDIA_PAGE
#		self.W_MAIN_PANE = 200
		self.W_MAIN_PANE = 150

		self.X_LEADERS = self.X_MAIN_PANE + self.W_MAIN_PANE + 10
		self.Y_LEADERS = self.Y_MAIN_PANE
		self.W_LEADERS = self.top.R_PEDIA_PAGE - self.X_LEADERS
#		self.H_LEADERS = 110
		self.H_LEADERS = 116

		# lines are 22 pixels high using WB font -- no idea about normal font
#		self.X_SPECIAL = self.X_MAIN_PANE + self.W_MAIN_PANE + 10
		self.X_SPECIAL = self.X_MAIN_PANE
		self.Y_SPECIAL = self.Y_LEADERS + self.H_LEADERS + 10
		self.W_SPECIAL = self.top.R_PEDIA_PAGE - self.X_SPECIAL
#		self.H_SPECIAL = 150
		self.H_SPECIAL = 250

#		self.H_MAIN_PANE = self.Y_SPECIAL + self.H_SPECIAL - self.Y_MAIN_PANE
		self.H_MAIN_PANE = self.H_LEADERS

#		self.W_ICON = 150
#		self.H_ICON = 150
		self.W_ICON = 100
		self.H_ICON = 100
		self.X_ICON = self.X_MAIN_PANE + (self.W_MAIN_PANE - self.W_ICON) / 2
		self.Y_ICON = self.Y_MAIN_PANE + (self.H_MAIN_PANE - self.H_ICON) / 2
		self.ICON_SIZE = 64

		self.X_TEXT = self.X_MAIN_PANE
		self.Y_TEXT = self.Y_SPECIAL + self.H_SPECIAL + 10
		self.W_TEXT = self.top.R_PEDIA_PAGE - self.X_TEXT
		self.H_TEXT = self.top.B_PEDIA_PAGE - self.Y_TEXT



#BUGFfH: Modified by Denev 2009/09/10
#	def interfaceScreen(self, iConcept):
	def interfaceScreen(self, iTrait):
#BUGFfH: End Modify
		self.iLeader = -1
#BUGFfH: Modified by Denev 2009/09/10
#		self.iConcept = iConcept
#		info = gc.getNewConceptInfo(iConcept)
#		sKey = info.getType()
#		sKey = sKey[sKey.find("TRAIT_"):]
#		self.iTrait = gc.getInfoTypeForString(sKey)
		self.iTrait = iTrait
#BUGFfH: End Modify
		
		screen = self.top.getScreen()

#BUGFfH: Added by Denev 2009/08/16
		# Header...
		szHeader = u"<font=4b>" + gc.getTraitInfo(self.iTrait).getDescription() + u"</font>"
		szHeaderId = "PediaMainHeader"
		screen.setText(szHeaderId, "Background", szHeader, CvUtil.FONT_CENTER_JUSTIFY, self.top.X_SCREEN, self.top.Y_TITLE, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
#BUGFfH: End Add

		screen.addPanel( self.top.getNextWidgetName(), "", "", False, False, self.X_MAIN_PANE, self.Y_MAIN_PANE, self.W_MAIN_PANE, self.H_MAIN_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_MAIN)
#BUGFfH: Modified by Denev 2009/09/11
#		screen.addDDSGFC(self.top.getNextWidgetName(), TraitUtil.getButton(self.iTrait), self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		screen.addDDSGFC(self.top.getNextWidgetName(), gc.getTraitInfo(self.iTrait).getButton(), self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1 )
#BUGFfH: End Modify

		self.placeLeaders()
		self.placeSpecial()
		self.placeText()



	def placeLeaders(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
#BUGFfH: Modified by Denev 2009/09/10
#		screen.addPanel( panelName, localText.getText("TXT_KEY_CONCEPT_LEADERS", ()), "", False, True, self.X_LEADERS, self.Y_LEADERS, self.W_LEADERS, self.H_LEADERS, PanelStyles.PANEL_STYLE_BLUE50 )
		szPanelTitle = localText.getText("TXT_KEY_PEDIA_CATEGORY_LEADER", ()) + localText.getText("TXT_KEY_OR", ()) + localText.getText("TXT_KEY_PEDIA_CATEGORY_CIV", ())
		screen.addPanel( panelName, szPanelTitle, "", False, True, self.X_LEADERS, self.Y_LEADERS, self.W_LEADERS, self.H_LEADERS, PanelStyles.PANEL_STYLE_BLUE50 )
#FfH: End Modify
		screen.attachLabel(panelName, "", "  ")
		for iLeader in range(gc.getNumLeaderHeadInfos()):
			pLeader = gc.getLeaderHeadInfo(iLeader)
			if pLeader.hasTrait(self.iTrait) and (not pLeader.isGraphicalOnly()):
				self.iLeader = iLeader
			# MINOR_LEADERS_PEDIA 08/2013 lfgr
			#	for iCiv in range(gc.getNumCivilizationInfos()):
			#		if gc.getCivilizationInfo(iCiv).isLeaders(iLeader):
			#			screen.attachImageButton(panelName, "", gc.getLeaderHeadInfo(iLeader).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_LEADER, iLeader, 1, False)
			#			break
				screen.attachImageButton(panelName, "", gc.getLeaderHeadInfo(iLeader).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_LEADER, iLeader, 1, False)
			# MINOR_LEADERS_PEDIA end
		
#BUGFfH: Added by Denev 2009/09/10
		for iCivilization in range(gc.getNumCivilizationInfos()):
			pCivilization = gc.getCivilizationInfo(iCivilization)
			if pCivilization.getCivTrait() == self.iTrait:
				screen.attachImageButton(panelName, "", pCivilization.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, iCivilization, 1, False)
#FfH: End Add



	def placeSpecial(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_EFFECTS", ()), "", True, False, self.X_SPECIAL, self.Y_SPECIAL, self.W_SPECIAL, self.H_SPECIAL, PanelStyles.PANEL_STYLE_BLUE50 )
		listName = self.top.getNextWidgetName()
		screen.attachListBoxGFC( panelName, listName, "", TableStyles.TABLE_STYLE_EMPTY )
		screen.enableSelect(listName, False)
		
##--------	BUGFfH: Deleted Denev 2009/09/21
		"""
		def append(text):
			screen.appendListBoxString( listName, text, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
		"""
##--------	BUGFfH: End Delete
		
#BUGFfH: Added by Denev 2009/09/10
		szSpecial = CyGameTextMgr().parseTraits(self.iTrait, CivilizationTypes.NO_CIVILIZATION, false)	#bool bDawnOfMan, bool bCivilopediaText
		szSpecial = szSpecial.strip("\n")

		screen.addMultilineText(listName, szSpecial, self.X_SPECIAL+5, self.Y_SPECIAL+30, self.W_SPECIAL-5, self.H_SPECIAL-32, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		return
#BUGFfH: End Add
		
		if self.iLeader != -1:
			pLeader = gc.getLeaderHeadInfo(self.iLeader)
			trait = gc.getTraitInfo(self.iTrait)
			szText = CyGameTextMgr().parseLeaderTraits(self.iLeader, -1, False, True)
			szSpecial = u""
			bFirst = True
			bFound = False
			bSkip = True
			for line in szText.splitlines():
				if not line.startswith(" "):
					# leader or trait
					if line.find(">%s<" % leader.getDescription()) != -1:
						continue # leader, ignore
					elif line.find(">%s<" % trait.getDescription()) != -1:
						# the trait we want
						bFound = True
						bSkip = False
					else:
						# some other trait
						if bFound: break
						bSkip = True
				else:
					if not bSkip:
						if bFirst:
							bFirst = False
						else:
							szSpecial += "\n"
						szSpecial += line[2:]  # strip first two spaces
			if bFound:
#BUGFfH: Modified by Denev 2009/09/11
#				screen.addMultilineText(listName, szSpecial, self.X_SPECIAL+5, self.Y_SPECIAL+27, self.W_SPECIAL-10, self.H_SPECIAL-32, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
				screen.addMultilineText(listName, szSpecial, self.X_SPECIAL+5, self.Y_SPECIAL+30, self.W_SPECIAL-5, self.H_SPECIAL-32, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
#FfH: End Modify



	def placeText(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, "", "", True, True, self.X_TEXT, self.Y_TEXT, self.W_TEXT, self.H_TEXT, PanelStyles.PANEL_STYLE_BLUE50 )
#BUGFfH: Modified by Denev 2009/08/16
#		szText = gc.getNewConceptInfo(self.iConcept).getCivilopedia()
#		screen.attachMultilineText( panelName, "Text", szText, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		textName = self.top.getNextWidgetName()
		szText = gc.getTraitInfo(self.iTrait).getCivilopedia()
		screen.addMultilineText( textName, szText, self.X_TEXT + 5, self.Y_TEXT + 8, self.W_TEXT - 5, self.H_TEXT - 10, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
#FfH: End Modify



	def handleInput (self, inputClass):
		return 0
