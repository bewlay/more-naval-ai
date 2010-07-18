# Sid Meier's Civilization 4
# Copyright Firaxis Games 2005
from CvPythonExtensions import *
import PyHelpers
import CvUtil
import ScreenInput
import CvScreenEnums
import Trophies
# globals
gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class CvTrophyHall:
	def __init__(self):
		self.SCREEN_NAME = "TrophyHall"
		self.WIDGET_ID = "TrophyHallWidget"
		self.WIDGET_HEADER = "TrophyHallWidgetHeader"
		self.EXIT_ID = "TrophyHallExitWidget"
		self.BACKGROUND_ID = "TrophyHallBackground"
		self.X_SCREEN = 0
		self.Y_SCREEN = 0
		self.W_SCREEN = 1024
		self.H_SCREEN = 768
		self.Y_TITLE = 12

		self.Y_START = 60
		self.Y_SPACING = 9
		self.SIZE = 50

		self.X_START = 12
		self.X_SPACING = 9
		self.X_MAX = 974

		self.TEXT_MARGIN = 15
		self.Z_BACKGROUND = -2.1
		self.Z_CONTROLS = self.Z_BACKGROUND - 0.2
		self.DZ = -0.2
		self.X_EXIT = 994
		self.Y_EXIT = 726

		self.nWidgetCount = 0

	def getScreen(self):
		return CyGInterfaceScreen(self.SCREEN_NAME, 101)

	def interfaceScreen (self):
		self.iActiveLeader = CyGame().getActivePlayer()
		player = gc.getPlayer(self.iActiveLeader)

		screen = self.getScreen()
		if screen.isActive():
			return
		screen.showScreen( PopupStates.POPUPSTATE_IMMEDIATE, False)
		screen.setDimensions(screen.centerX(self.X_SCREEN), screen.centerY(self.Y_SCREEN), self.W_SCREEN, self.H_SCREEN)
		screen.addDDSGFC(self.BACKGROUND_ID, ArtFileMgr.getInterfaceArtInfo("MAINMENU_TROPHY_BACKGROUND").getPath(), 0, 0, self.W_SCREEN, self.H_SCREEN, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		screen.addPanel( "TechTopPanel", u"", u"", True, False, 0, 0, self.W_SCREEN, 55, PanelStyles.PANEL_STYLE_TOPBAR )
		screen.addPanel( "TechBottomPanel", u"", u"", True, False, 0, 713, self.W_SCREEN, 55, PanelStyles.PANEL_STYLE_BOTTOMBAR )

		screen.showWindowBackground(False)
		screen.setText(self.EXIT_ID, "Background", u"<font=4>" + localText.getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, self.X_EXIT, self.Y_EXIT, self.Z_CONTROLS, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )
		screen.setLabel(self.WIDGET_HEADER, "Background", u"<font=4b>" + localText.getText("TXT_KEY_TROPHY_HALL_TITLE", ()).upper() + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, 500, self.Y_TITLE, self.Z_CONTROLS, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		x=self.X_START
		y=self.Y_START
		screen.addPanel( "AchievedLine", u"" + localText.getText("TXT_KEY_TROPHY_SCREEN_ACHIEVED", ()).upper(), u"", True, False, x, y, self.W_SCREEN, 25, PanelStyles.PANEL_STYLE_MAIN_WHITE )
		screen.addPanel( "UnachievedLine", u"" + localText.getText("TXT_KEY_TROPHY_SCREEN_UNACHIEVED", ()).upper(), u"", True, False, x, y+354, self.W_SCREEN, 25, PanelStyles.PANEL_STYLE_MAIN_WHITE )

		self.drawContents()

	def drawContents(self):
		self.deleteAllWidgets()
		screen = self.getScreen()
		screen.setForcedRedraw( True )
		a=PanelStyles.PANEL_STYLE_MAIN_WHITE
		a=PanelStyles.PANEL_STYLE_CITY_COLUMNR
		x=self.X_START
		y=self.Y_START + 30
		Trophies.init()
		Trophies.update()
		for t in Trophies.ALL_TROPHIES:
			name = self.getNextWidgetName()
			if t.has:
				screen.addDDSGFC(name,t.enabledDDS,x,y, self.SIZE, self.SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1)
				n1=self.getNextWidgetName()
				screen.addPanel( n1, "", t.description, true, true, x, y, self.SIZE, self.SIZE,PanelStyles.PANEL_STYLE_MAIN_WHITE)
				a=PanelStyles.PANEL_STYLE_MAIN_WHITE
				x+=self.X_SPACING+self.SIZE
				if x>self.X_MAX:
					x=self.X_START
					y+=self.Y_SPACING + self.SIZE
		x=self.X_START
		y=self.Y_START + 384
		for t in Trophies.ALL_TROPHIES:
			name = self.getNextWidgetName()
			if not t.has:
				screen.addDDSGFC(name,t.disabledDDS,x,y, self.SIZE, self.SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1)
				n1=self.getNextWidgetName()
				screen.addPanel( n1, "", t.description, true, true, x, y, self.SIZE, self.SIZE,PanelStyles.PANEL_STYLE_MAIN_WHITE)
				a=PanelStyles.PANEL_STYLE_MAIN_WHITE
				x+=self.X_SPACING+self.SIZE
				if x>self.X_MAX:
					x=self.X_START
					y+=self.Y_SPACING + self.SIZE
				
	def handleInput (self, inputClass):
		return 0
	
	def getNextWidgetName(self):
		szName = self.WIDGET_ID + str(self.nWidgetCount)
		self.nWidgetCount += 1
		return szName

	def deleteAllWidgets(self):
		screen = self.getScreen()
		i = self.nWidgetCount - 1
		while (i >= 0):
			self.nWidgetCount = i
			screen.deleteWidget(self.getNextWidgetName())
			i -= 1
		self.nWidgetCount = 0

	def update(self, fDelta):
		return
