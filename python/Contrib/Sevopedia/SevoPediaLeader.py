# Sid Meier's Civilization 4
# Copyright Firaxis Games 2005

#
# Sevopedia 2.3
#   sevotastic.blogspot.com
#   sevotastic@yahoo.com
#
# additional work by Gaurav, Progor, Ket, Vovan, Fitchn, LunarMongoose, lfgr
# see ReadMe for details
#

from CvPythonExtensions import *
import CvUtil
import ScreenInput
import SevoScreenEnums
import random

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class SevoPediaLeader:

	def __init__(self, main):
		self.iLeader = -1
		self.top = main
	
	
	def initPositions( self ) :
##--------	BUGFfH: Modified by Denev 2009/10/04
		X_MERGIN = self.top.X_MERGIN
		Y_MERGIN = self.top.Y_MERGIN

		self.X_LEADERHEAD_PANE = self.top.X_PEDIA_PAGE
		self.Y_LEADERHEAD_PANE = self.top.Y_PEDIA_PAGE
		self.W_LEADERHEAD_PANE = 240
		self.H_LEADERHEAD_PANE = 290

		self.W_LEADERHEAD = self.W_LEADERHEAD_PANE - 30
		self.H_LEADERHEAD = self.H_LEADERHEAD_PANE - 34
		self.X_LEADERHEAD = self.X_LEADERHEAD_PANE + (self.W_LEADERHEAD_PANE - self.W_LEADERHEAD) / 2
		self.Y_LEADERHEAD = self.Y_LEADERHEAD_PANE + (self.H_LEADERHEAD_PANE - self.H_LEADERHEAD) / 2 + 3

		self.W_CIV = 64
		self.H_CIV = 64
		self.X_CIV = self.X_LEADERHEAD_PANE + (self.W_LEADERHEAD_PANE - self.W_CIV) / 2
		self.Y_CIV = self.Y_LEADERHEAD_PANE + self.H_LEADERHEAD_PANE + Y_MERGIN

		self.X_CIVIC = self.X_LEADERHEAD_PANE + self.W_LEADERHEAD_PANE + X_MERGIN
		self.Y_CIVIC = self.Y_LEADERHEAD_PANE
		self.W_CIVIC = self.top.R_PEDIA_PAGE - self.X_CIVIC
		self.H_CIVIC = 80

		self.X_TRAITS = self.X_LEADERHEAD_PANE + self.W_LEADERHEAD_PANE + X_MERGIN
		self.Y_TRAITS = self.Y_CIVIC + self.H_CIVIC + Y_MERGIN
		self.W_TRAITS = self.top.R_PEDIA_PAGE - self.X_TRAITS
		self.H_TRAITS = self.Y_CIV + self.H_CIV - self.Y_TRAITS

		self.X_HISTORY = self.X_LEADERHEAD_PANE
		self.Y_HISTORY = self.Y_CIV + self.H_CIV + Y_MERGIN
		self.W_HISTORY = self.top.R_PEDIA_PAGE - self.X_HISTORY
		self.H_HISTORY = self.top.B_PEDIA_PAGE - self.Y_HISTORY
##--------	BUGFfH: End Modify


	def interfaceScreen(self, iLeader):
		self.initPositions()
		
		self.iLeader = iLeader
		screen = self.top.getScreen()

		leaderPanelWidget = self.top.getNextWidgetName()
		screen.addPanel(leaderPanelWidget, "", "", True, True, self.X_LEADERHEAD_PANE, self.Y_LEADERHEAD_PANE, self.W_LEADERHEAD_PANE, self.H_LEADERHEAD_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		self.leaderWidget = self.top.getNextWidgetName()
		screen.addLeaderheadGFC(self.leaderWidget, self.iLeader, AttitudeTypes.ATTITUDE_PLEASED, self.X_LEADERHEAD, self.Y_LEADERHEAD, self.W_LEADERHEAD, self.H_LEADERHEAD, WidgetTypes.WIDGET_GENERAL, -1, -1)

##--------	BUGFfH: Added by Denev 2009/08/16
		# Header...
		szHeader = u"<font=4b>" + gc.getLeaderHeadInfo(self.iLeader).getDescription() + u"</font>"
		szHeaderId = "PediaMainHeader"
		screen.setText(szHeaderId, "Background", szHeader, CvUtil.FONT_CENTER_JUSTIFY, self.top.X_SCREEN, self.top.Y_TITLE, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
##--------	BUGFfH: End Add

		self.placeHistory()
		self.placeCivic()
##--------	BUGFfH: Deleted by Denev 2009/10/05
#		self.placeReligion()
##--------	BUGFfH: End Delete
		self.placeCiv()
		self.placeTraits()



	def placeCiv(self):
		screen = self.top.getScreen()
##--------	BUGFfH: Added by Denev 2009/08/16
		lLeaderCivList = []
##--------	BUGFfH: End Add
		for iCiv in range(gc.getNumCivilizationInfos()):
			civ = gc.getCivilizationInfo(iCiv)
			if civ.isLeaders(self.iLeader):
##--------	BUGFfH: Modified by Denev 2009/08/16
#				screen.setImageButton(self.top.getNextWidgetName(), civ.getButton(), self.X_CIV, self.Y_CIV, self.W_CIV, self.H_CIV, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, iCiv, 1)
				lLeaderCivList.append( (iCiv, civ) )
		if lLeaderCivList:
			fEachMargin = float( self.W_LEADERHEAD_PANE / len(lLeaderCivList) )

			fX = float( self.X_LEADERHEAD_PANE - (self.W_CIV + fEachMargin) / 2 )
			for loopCiv in lLeaderCivList:
				fX += fEachMargin
				screen.setImageButton(self.top.getNextWidgetName(), loopCiv[1].getButton(), int(fX), self.Y_CIV, self.W_CIV, self.H_CIV, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, loopCiv[0], 1)
##--------	BUGFfH: End Modify



	def placeTraits(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_TRAITS", ()), "", True, False, self.X_TRAITS, self.Y_TRAITS, self.W_TRAITS, self.H_TRAITS, PanelStyles.PANEL_STYLE_BLUE50)
		listName = self.top.getNextWidgetName()
		iNumCivs = 0
		iLeaderCiv = -1
		for iCiv in range(gc.getNumCivilizationInfos()):
			civ = gc.getCivilizationInfo(iCiv)
			if civ.isLeaders(self.iLeader):
				iNumCivs += 1
				iLeaderCiv = iCiv
		if iNumCivs == 1:
			szSpecialText = CyGameTextMgr().parseLeaderTraits(self.iLeader, iLeaderCiv, False, True)
		else:
			szSpecialText = CyGameTextMgr().parseLeaderTraits(self.iLeader, -1, False, True)
##--------	BUGFfH: Modified by Denev 2009/10/05
#		szSpecialText = szSpecialText[1:]
		szSpecialText= szSpecialText.strip("\n")
##--------	BUGFfH: End Modify

##--------	BUGFfH: Modified by Denev 2009/08/16
#		screen.addMultilineText(listName, szSpecialText, self.X_TRAITS+5, self.Y_TRAITS+30, self.W_TRAITS-10, self.H_TRAITS-35, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.addMultilineText(listName, szSpecialText, self.X_TRAITS+5, self.Y_TRAITS+30, self.W_TRAITS-5, self.H_TRAITS-32, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
##--------	BUGFfH: End Modify



	def placeCivic(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
##--------	BUGFfH: Modified by Denev 2009/08/16
		"""
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_FAV_CIVIC_AND_RELIGION", ()), "", True, True, self.X_CIVIC, self.Y_CIVIC, self.W_CIVIC, self.H_CIVIC, PanelStyles.PANEL_STYLE_BLUE50)
		iCivic = gc.getLeaderHeadInfo(self.iLeader).getFavoriteCivic()
		if (-1 != iCivic):
			szCivicText = u"<link=literal>" + gc.getCivicInfo(iCivic).getDescription() + u"</link>"
			listName = self.top.getNextWidgetName()
			screen.addMultilineText(listName, szCivicText, self.X_CIVIC+5, self.Y_CIVIC+30, self.W_CIVIC-10, self.H_CIVIC-10, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		"""
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_FAV_CIVIC", ()), "", True, True, self.X_CIVIC, self.Y_CIVIC, self.W_CIVIC, self.H_CIVIC, PanelStyles.PANEL_STYLE_BLUE50)
		iCivic = gc.getLeaderHeadInfo(self.iLeader).getFavoriteCivic()
		if (-1 != iCivic):
			szCivicText = u"<link=" + gc.getCivicInfo(iCivic).getType() + ">" + gc.getCivicInfo(iCivic).getDescription() + u"</link>"
			szCivicText = localText.getText("TXT_KEY_MISC_FAVORITE_CIVIC", ()) + u" " + szCivicText
		iWonder = gc.getLeaderHeadInfo(self.iLeader).getFavoriteWonder()
		if (-1 != iWonder):
			szWonderText = u"<link=" + gc.getBuildingInfo(iWonder).getType() + ">" + gc.getBuildingInfo(iWonder).getDescription() + u"</link>"
			szCivicText += u"\n" + localText.getText("TXT_KEY_MISC_FAVORITE_WONDER", ()) + u" " + szWonderText
			listName = self.top.getNextWidgetName()
			screen.addMultilineText(listName, szCivicText, self.X_CIVIC + 5, self.Y_CIVIC + 30, self.W_CIVIC - 5, self.H_CIVIC - 32, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
##--------	BUGFfH: End Modify


##--------	BUGFfH: Deleted by Denev 2009/10/05
			"""
	def placeReligion(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		iReligion = gc.getLeaderHeadInfo(self.iLeader).getFavoriteReligion()
		if (-1 != iReligion):
			szReligionText = u"<link=literal>" + gc.getReligionInfo(iReligion).getDescription() + u"</link>"
			listName = self.top.getNextWidgetName()
			screen.addMultilineText(listName, szReligionText, self.X_CIVIC+5, self.Y_CIVIC+50, self.W_CIVIC-10, self.H_CIVIC-10, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
			"""
##--------	BUGFfH: End Delete



	def placeHistory(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, "", "", True, True, self.X_HISTORY, self.Y_HISTORY, self.W_HISTORY, self.H_HISTORY, PanelStyles.PANEL_STYLE_BLUE50)
		historyTextName = self.top.getNextWidgetName()
		CivilopediaText = gc.getLeaderHeadInfo(self.iLeader).getCivilopedia()
		CivilopediaText = u"<font=2>" + CivilopediaText + u"</font>"
##--------	BUGFfH: Modified by Denev 2009/08/16
#		screen.attachMultilineText(panelName, historyTextName, CivilopediaText, WidgetTypes.WIDGET_GENERAL,-1,-1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.addMultilineText(historyTextName, CivilopediaText, self.X_HISTORY + 5, self.Y_HISTORY + 8, self.W_HISTORY - 5, self.H_HISTORY - 10, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
##--------	BUGFfH: End Modify



	def handleInput (self, inputClass):
		if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CHARACTER):
			if (inputClass.getData() == int(InputTypes.KB_0)):
				self.top.getScreen().performLeaderheadAction(self.leaderWidget, LeaderheadAction.LEADERANIM_GREETING)
			elif (inputClass.getData() == int(InputTypes.KB_6)):
				self.top.getScreen().performLeaderheadAction(self.leaderWidget, LeaderheadAction.LEADERANIM_DISAGREE)
			elif (inputClass.getData() == int(InputTypes.KB_7)):
				self.top.getScreen().performLeaderheadAction(self.leaderWidget, LeaderheadAction.LEADERANIM_AGREE)
			elif (inputClass.getData() == int(InputTypes.KB_1)):
				self.top.getScreen().setLeaderheadMood(self.leaderWidget, AttitudeTypes.ATTITUDE_FRIENDLY)
				self.top.getScreen().performLeaderheadAction(self.leaderWidget, LeaderheadAction.NO_LEADERANIM)
			elif (inputClass.getData() == int(InputTypes.KB_2)):
				self.top.getScreen().setLeaderheadMood(self.leaderWidget, AttitudeTypes.ATTITUDE_PLEASED)
				self.top.getScreen().performLeaderheadAction(self.leaderWidget, LeaderheadAction.NO_LEADERANIM)
			elif (inputClass.getData() == int(InputTypes.KB_3)):
				self.top.getScreen().setLeaderheadMood(self.leaderWidget, AttitudeTypes.ATTITUDE_CAUTIOUS)
				self.top.getScreen().performLeaderheadAction(self.leaderWidget, LeaderheadAction.NO_LEADERANIM)
			elif (inputClass.getData() == int(InputTypes.KB_4)):
				self.top.getScreen().setLeaderheadMood(self.leaderWidget, AttitudeTypes.ATTITUDE_ANNOYED)
				self.top.getScreen().performLeaderheadAction(self.leaderWidget, LeaderheadAction.NO_LEADERANIM)
			elif (inputClass.getData() == int(InputTypes.KB_5)):
				self.top.getScreen().setLeaderheadMood(self.leaderWidget, AttitudeTypes.ATTITUDE_FURIOUS)
				self.top.getScreen().performLeaderheadAction(self.leaderWidget, LeaderheadAction.NO_LEADERANIM)
			else:
				self.top.getScreen().leaderheadKeyInput(self.leaderWidget, inputClass.getData())
		return 0
		
# MINOR_LEADERS_PEDIA 08/2013 lfgr
	def getLeaderType( self, eLeader ) :
		for eCiv in range( gc.getNumCivilizationInfos() ) :
			if( gc.getCivilizationInfo( eCiv ).isLeaders( eLeader ) ) :
				return SevoScreenEnums.TYPE_MAJOR

		return SevoScreenEnums.TYPE_MINOR
# MINOR_LEADERS_PEDIA end
