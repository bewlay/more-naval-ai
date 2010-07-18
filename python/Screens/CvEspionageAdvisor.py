# Fall from Heaven
# Scenario Screen
# Made by Kael
from CvPythonExtensions import *
import CvUtil
import os
import ScreenInput
import CvScreenEnums
import CvWBDesc
import CustomFunctions

# globals
cf = CustomFunctions.CustomFunctions()
gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()
WBDesc = CvWBDesc.CvWBDesc()

class CvEspionageAdvisor:

	def __init__(self):
		self.SCREEN_NAME = "EspionageAdvisor"
		self.DEBUG_DROPDOWN_ID =  "EspionageAdvisorDropdownWidget"
		self.WIDGET_ID = "EspionageAdvisorWidget"
		self.WIDGET_HEADER = "EspionageAdvisorWidgetHeader"
		self.EXIT_ID = "EspionageAdvisorExitWidget"
		self.BACKGROUND_ID = "EspionageAdvisorBackground"
		self.X_SCREEN = 500
		self.Y_SCREEN = 396
		self.W_SCREEN = 1024
		self.H_SCREEN = 768
		self.Y_TITLE = 12
		self.BORDER_WIDTH = 4
		self.PANE_HEIGHT = 450
		self.PANE_WIDTH = 283
		self.X_SLIDERS = 50
		self.X_INCOME = 373
		self.TEXT_MARGIN = 15
		self.Z_BACKGROUND = -2.1
		self.Z_CONTROLS = self.Z_BACKGROUND - 0.2
		self.DZ = -0.2	
		self.X_EXIT = 994
		self.Y_EXIT = 726
		self.nWidgetCount = 0
		self.iDirtyBit = 0
		self.currentScen = "Grand Menagerie"
		self.szDetail = -1
		self.szPopup = "art/interface/popups/Grand Menagerie.dds"

	def getScreen(self):
		return CyGInterfaceScreen(self.SCREEN_NAME, CvScreenEnums.ESPIONAGE_ADVISOR)

	def interfaceScreen (self):
		screen = self.getScreen()
		if screen.isActive():
			return
		screen.setRenderInterfaceOnly(True);
		screen.showScreen( PopupStates.POPUPSTATE_IMMEDIATE, False)
		screen.setDimensions(screen.centerX(0), screen.centerY(0), self.W_SCREEN, self.H_SCREEN)
		screen.addDDSGFC(self.BACKGROUND_ID, ArtFileMgr.getInterfaceArtInfo("SCREEN_BG_OPAQUE").getPath(), 0, 0, self.W_SCREEN, self.H_SCREEN, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		screen.addPanel( "TechTopPanel", u"", u"", True, False, 0, 0, self.W_SCREEN, 55, PanelStyles.PANEL_STYLE_TOPBAR )
		screen.addPanel( "TechBottomPanel", u"", u"", True, False, 0, 713, self.W_SCREEN, 55, PanelStyles.PANEL_STYLE_BOTTOMBAR )
		screen.showWindowBackground(False)
		if not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_WB_LOAD_SCREEN):
			screen.setText(self.EXIT_ID, "Background", u"<font=4>" + localText.getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, self.X_EXIT, self.Y_EXIT, self.Z_CONTROLS, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )
		screen.setLabel(self.WIDGET_HEADER, "Background", u"<font=4b>" + localText.getText("TXT_KEY_SCENARIO_SCREEN", ()).upper() + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, self.X_SCREEN, self.Y_TITLE, self.Z_CONTROLS, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		self.drawContents()

	def drawContents(self):
		self.deleteAllWidgets()
		screen = self.getScreen()
		self.X_LEFT_PANE = 10
		self.Y_LEFT_PANE = 70
		self.W_LEFT_PANE = 184
		self.H_LEFT_PANE = 630
		self.szLeftPaneWidget = "LeftPane"
		screen.addPanel( self.szLeftPaneWidget, "", "", true, true,
			self.X_LEFT_PANE, self.Y_LEFT_PANE, self.W_LEFT_PANE, self.H_LEFT_PANE, PanelStyles.PANEL_STYLE_MAIN )

		self.X_RIGHT_PANE = self.X_LEFT_PANE + self.W_LEFT_PANE + 10
		self.Y_RIGHT_PANE = 474
		self.W_RIGHT_PANE = 800
		self.H_RIGHT_PANE = 224
		self.szRightPaneWidget = "RightPane"
		screen.addPanel( self.szRightPaneWidget, "", "", true, true,
			self.X_RIGHT_PANE, self.Y_RIGHT_PANE, self.W_RIGHT_PANE, self.H_RIGHT_PANE, PanelStyles.PANEL_STYLE_MAIN )
		screen.addDDSGFC('Popup', self.szPopup, self.X_RIGHT_PANE, self.Y_LEFT_PANE + 4, 800, 400, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		self.szMakingText = "MakingText"
		self.X_MAKING_TEXT = 225
		self.Y_MAKING_TEXT = 490
		if self.szDetail == -1:
			self.szDetail = localText.getText("TXT_KEY_WB_GRAND_MENAGERIE_DESC", ())
		szText = u"<font=3>" + self.szDetail + "</font>"
		screen.addMultilineText( self.szMakingText, szText, 225, 490, 780, 200, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

		iX = 14
		iXText = 50
		iY = 85
		iSpace = 33
		iButtonSize = 34

		szButton = 'art/interface/buttons/play.dds'
		if CyGame().isHasTrophy("TROPHY_WB_GRAND_MENAGERIE"):
			szButton = 'art/interface/buttons/trophy.dds'
		screen.addCheckBoxGFC("Grand Menagerie Button", szButton, ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), iX, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_STANDARD)
		screen.setText("Grand Menagerie", "", u"<font=3>" + localText.getText("TXT_KEY_WB_GRAND_MENAGERIE", ()) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iXText, iY + 5, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += iSpace
		szButton = 'art/interface/buttons/play.dds'
		iButtonStyle = ButtonStyles.BUTTON_STYLE_STANDARD
		if not self.isUnlocked("The Momus"):
			szButton = 'art/interface/buttons/lock.dds'
			iButtonStyle = ButtonStyles.BUTTON_STYLE_IMAGE
		if CyGame().isHasTrophy("TROPHY_WB_THE_MOMUS"):
			szButton = 'art/interface/buttons/trophy.dds'
		screen.addCheckBoxGFC("The Momus Button", szButton, ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), iX, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_GENERAL, -1, -1, iButtonStyle)
		screen.setText("The Momus", "", u"<font=3>" + localText.getText("TXT_KEY_WB_THE_MOMUS", ()) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iXText, iY + 5, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += iSpace
		szButton = 'art/interface/buttons/play.dds'
		iButtonStyle = ButtonStyles.BUTTON_STYLE_STANDARD
		if not self.isUnlocked("The Radiant Guard"):
			szButton = 'art/interface/buttons/lock.dds'
			iButtonStyle = ButtonStyles.BUTTON_STYLE_IMAGE
		if CyGame().isHasTrophy("TROPHY_WB_THE_RADIANT_GUARD"):
			szButton = 'art/interface/buttons/trophy.dds'
		screen.addCheckBoxGFC("The Radiant Guard Button", szButton, ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), iX, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_GENERAL, -1, -1, iButtonStyle)
		screen.setText("The Radiant Guard", "", u"<font=3>" + localText.getText("TXT_KEY_WB_THE_RADIANT_GUARD", ()) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iXText, iY + 5, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += iSpace
		szButton = 'art/interface/buttons/play.dds'
		iButtonStyle = ButtonStyles.BUTTON_STYLE_STANDARD
		if not self.isUnlocked("The Black Tower"):
			szButton = 'art/interface/buttons/lock.dds'
			iButtonStyle = ButtonStyles.BUTTON_STYLE_IMAGE
		if CyGame().isHasTrophy("TROPHY_WB_THE_BLACK_TOWER"):
			szButton = 'art/interface/buttons/trophy.dds'
		screen.addCheckBoxGFC("The Black Tower Button", szButton, ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), iX, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_GENERAL, -1, -1, iButtonStyle)
		screen.setText("The Black Tower", "", u"<font=3>" + localText.getText("TXT_KEY_WB_THE_BLACK_TOWER", ()) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iXText, iY + 5, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += iSpace
		szButton = 'art/interface/buttons/play.dds'
		iButtonStyle = ButtonStyles.BUTTON_STYLE_STANDARD
		if CyGame().isHasTrophy("TROPHY_WB_FALL_OF_CUANTINE"):
			szButton = 'art/interface/buttons/trophy.dds'
		screen.addCheckBoxGFC("Fall of Cuantine Button", szButton, ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), iX, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_GENERAL, -1, -1, iButtonStyle)
		screen.setText("Fall of Cuantine", "", u"<font=3>" + localText.getText("TXT_KEY_WB_FALL_OF_CUANTINE", ()) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iXText, iY + 5, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += iSpace
		szButton = 'art/interface/buttons/play.dds'
		iButtonStyle = ButtonStyles.BUTTON_STYLE_STANDARD
		if not self.isUnlocked("Into the Desert"):
			szButton = 'art/interface/buttons/lock.dds'
			iButtonStyle = ButtonStyles.BUTTON_STYLE_IMAGE
		if CyGame().isHasTrophy("TROPHY_WB_INTO_THE_DESERT"):
			szButton = 'art/interface/buttons/trophy.dds'
		screen.addCheckBoxGFC("Into the Desert Button", szButton, ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), iX, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_GENERAL, -1, -1, iButtonStyle)
		screen.setText("Into the Desert", "", u"<font=3>" + localText.getText("TXT_KEY_WB_INTO_THE_DESERT", ()) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iXText, iY + 5, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += iSpace
		szButton = 'art/interface/buttons/play.dds'
		iButtonStyle = ButtonStyles.BUTTON_STYLE_STANDARD
		if not self.isUnlocked("Wages of Sin"):
			szButton = 'art/interface/buttons/lock.dds'
			iButtonStyle = ButtonStyles.BUTTON_STYLE_IMAGE
		if CyGame().isHasTrophy("TROPHY_WB_WAGES_OF_SIN"):
			szButton = 'art/interface/buttons/trophy.dds'
		screen.addCheckBoxGFC("Wages of Sin Button", szButton, ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), iX, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_GENERAL, -1, -1, iButtonStyle)
		screen.setText("Wages of Sin", "", u"<font=3>" + localText.getText("TXT_KEY_WB_WAGES_OF_SIN", ()) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iXText, iY + 5, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += iSpace
		szButton = 'art/interface/buttons/play.dds'
		iButtonStyle = ButtonStyles.BUTTON_STYLE_STANDARD
		if not self.isUnlocked("Against the Grey"):
			szButton = 'art/interface/buttons/lock.dds'
			iButtonStyle = ButtonStyles.BUTTON_STYLE_IMAGE
		if CyGame().isHasTrophy("TROPHY_WB_AGAINST_THE_GREY"):
			szButton = 'art/interface/buttons/trophy.dds'
		screen.addCheckBoxGFC("Against the Grey Button", szButton, ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), iX, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_GENERAL, -1, -1, iButtonStyle)
		screen.setText("Against the Grey", "", u"<font=3>" + localText.getText("TXT_KEY_WB_AGAINST_THE_GREY", ()) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iXText, iY + 5, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += iSpace
		szButton = 'art/interface/buttons/play.dds'
		if CyGame().isHasTrophy("TROPHY_WB_RETURN_OF_WINTER"):
			szButton = 'art/interface/buttons/trophy.dds'
		screen.addCheckBoxGFC("Return of Winter Button", szButton, ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), iX, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_STANDARD)
		screen.setText("Return of Winter", "", u"<font=3>" + localText.getText("TXT_KEY_WB_RETURN_OF_WINTER", ()) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iXText, iY + 5, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += iSpace
		szButton = 'art/interface/buttons/play.dds'
		iButtonStyle = ButtonStyles.BUTTON_STYLE_STANDARD
		if not self.isUnlocked("Blood of Angels"):
			szButton = 'art/interface/buttons/lock.dds'
			iButtonStyle = ButtonStyles.BUTTON_STYLE_IMAGE
		if CyGame().isHasTrophy("TROPHY_WB_BLOOD_OF_ANGELS"):
			szButton = 'art/interface/buttons/trophy.dds'
		screen.addCheckBoxGFC("Blood of Angels Button", szButton, ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), iX, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_GENERAL, -1, -1, iButtonStyle)
		screen.setText("Blood of Angels", "", u"<font=3>" + localText.getText("TXT_KEY_WB_BLOOD_OF_ANGELS", ()) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iXText, iY + 5, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += iSpace
		szButton = 'art/interface/buttons/play.dds'
		iButtonStyle = ButtonStyles.BUTTON_STYLE_STANDARD
		if not self.isUnlocked("Beneath the Heel"):
			szButton = 'art/interface/buttons/lock.dds'
			iButtonStyle = ButtonStyles.BUTTON_STYLE_IMAGE
		if CyGame().isHasTrophy("TROPHY_WB_BENEATH_THE_HEEL"):
			szButton = 'art/interface/buttons/trophy.dds'
		screen.addCheckBoxGFC("Beneath the Heel Button", szButton, ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), iX, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_GENERAL, -1, -1, iButtonStyle)
		screen.setText("Beneath the Heel", "", u"<font=3>" + localText.getText("TXT_KEY_WB_BENEATH_THE_HEEL", ()) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iXText, iY + 5, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += iSpace
		szButton = 'art/interface/buttons/play.dds'
		iButtonStyle = ButtonStyles.BUTTON_STYLE_STANDARD
		if not self.isUnlocked("The Cult"):
			szButton = 'art/interface/buttons/lock.dds'
			iButtonStyle = ButtonStyles.BUTTON_STYLE_IMAGE
		if CyGame().isHasTrophy("TROPHY_WB_THE_CULT"):
			szButton = 'art/interface/buttons/trophy.dds'
		screen.addCheckBoxGFC("The Cult Button", szButton, ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), iX, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_GENERAL, -1, -1, iButtonStyle)
		screen.setText("The Cult", "", u"<font=3>" + localText.getText("TXT_KEY_WB_THE_CULT", ()) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iXText, iY + 5, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += iSpace
		szButton = 'art/interface/buttons/play.dds'
		iButtonStyle = ButtonStyles.BUTTON_STYLE_STANDARD
		if not self.isUnlocked("Mulcarn Reborn"):
			szButton = 'art/interface/buttons/lock.dds'
			iButtonStyle = ButtonStyles.BUTTON_STYLE_IMAGE
		if CyGame().isHasTrophy("TROPHY_WB_MULCARN_REBORN"):
			szButton = 'art/interface/buttons/trophy.dds'
		screen.addCheckBoxGFC("Mulcarn Reborn Button", szButton, ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), iX, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_GENERAL, -1, -1, iButtonStyle)
		screen.setText("Mulcarn Reborn", "", u"<font=3>" + localText.getText("TXT_KEY_WB_MULCARN_REBORN", ()) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iXText, iY + 5, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += iSpace
		szButton = 'art/interface/buttons/play.dds'
		if CyGame().isHasTrophy("TROPHY_WB_BARBARIAN_ASSAULT"):
			szButton = 'art/interface/buttons/trophy.dds'
		screen.addCheckBoxGFC("Barbarian Assault Button", szButton, ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), iX, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_STANDARD)
		screen.setText("Barbarian Assault", "", u"<font=3>" + localText.getText("TXT_KEY_WB_BARBARIAN_ASSAULT", ()) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iXText, iY + 5, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += iSpace
		szButton = 'art/interface/buttons/play.dds'
		if CyGame().isHasTrophy("TROPHY_WB_THE_SPLINTERED_COURT"):
			szButton = 'art/interface/buttons/trophy.dds'
		screen.addCheckBoxGFC("The Splintered Court Button", szButton, ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), iX, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_STANDARD)
		screen.setText("The Splintered Court", "", u"<font=3>" + localText.getText("TXT_KEY_WB_THE_SPLINTERED_COURT", ()) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iXText, iY + 5, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += iSpace
		szButton = 'art/interface/buttons/play.dds'
		if CyGame().isHasTrophy("TROPHY_WB_GIFT_OF_KYLORIN"):
			szButton = 'art/interface/buttons/trophy.dds'
		screen.addCheckBoxGFC("Gift of Kylorin Button", szButton, ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), iX, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_STANDARD)
		screen.setText("Gift of Kylorin", "", u"<font=3>" + localText.getText("TXT_KEY_WB_GIFT_OF_KYLORIN", ()) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iXText, iY + 5, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += iSpace
		szButton = 'art/interface/buttons/play.dds'
		if CyGame().isHasTrophy("TROPHY_WB_AGAINST_THE_WALL"):
			szButton = 'art/interface/buttons/trophy.dds'
		screen.addCheckBoxGFC("Against the Wall Button", szButton, ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), iX, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_STANDARD)
		screen.setText("Against the Wall", "", u"<font=3>" + localText.getText("TXT_KEY_WB_AGAINST_THE_WALL", ()) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iXText, iY + 5, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iY += iSpace
		szButton = 'art/interface/buttons/play.dds'
		iButtonStyle = ButtonStyles.BUTTON_STYLE_STANDARD
		if not self.isUnlocked("Lord of the Balors"):
			szButton = 'art/interface/buttons/lock.dds'
			iButtonStyle = ButtonStyles.BUTTON_STYLE_IMAGE
		if CyGame().isHasTrophy("TROPHY_WB_LORD_OF_THE_BALORS"):
			szButton = 'art/interface/buttons/trophy.dds'
		screen.addCheckBoxGFC("Lord of the Balors Button", szButton, ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), iX, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_GENERAL, -1, -1, iButtonStyle)
		screen.setText("Lord of the Balors", "", u"<font=3>" + localText.getText("TXT_KEY_WB_LORD_OF_THE_BALORS", ()) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iXText, iY + 5, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

	def refreshScreen(self):
		self.deleteAllWidgets()
		screen = self.getScreen()
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

	def handleInput (self, inputClass):
		screen = self.getScreen()
		if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED):
			if inputClass.getFunctionName() == "Grand Menagerie":
				self.currentScen = "Grand Menagerie"
				self.szDetail = localText.getText("TXT_KEY_WB_GRAND_MENAGERIE_DESC", ())
				self.szPopup = "art/interface/popups/Grand Menagerie.dds"
			if inputClass.getFunctionName() == "The Momus":
				self.currentScen = "The Momus"
				self.szDetail = localText.getText("TXT_KEY_WB_THE_MOMUS_DESC", ())
				self.szPopup = "art/interface/popups/The Momus.dds"
			if inputClass.getFunctionName() == "The Radiant Guard":
				self.currentScen = "The Radiant Guard"
				self.szDetail = localText.getText("TXT_KEY_WB_THE_RADIANT_GUARD_DESC", ())
				self.szPopup = "art/interface/popups/The Radiant Guard.dds"
			if inputClass.getFunctionName() == "The Black Tower":
				self.currentScen = "The Black Tower"
				self.szDetail = localText.getText("TXT_KEY_WB_THE_BLACK_TOWER_DESC", ())
				self.szPopup = "art/interface/popups/The Black Tower.dds"
			if inputClass.getFunctionName() == "Fall of Cuantine":
				self.currentScen = "Fall of Cuantine"
				self.szDetail = localText.getText("TXT_KEY_WB_FALL_OF_CUANTINE_DESC", ())
				self.szPopup = "art/interface/popups/Fall of Cuantine.dds"
			if inputClass.getFunctionName() == "Into the Desert":
				self.currentScen = "Into the Desert"
				self.szDetail = localText.getText("TXT_KEY_WB_INTO_THE_DESERT_DESC", ())
				self.szPopup = "art/interface/popups/Into the Desert.dds"
			if inputClass.getFunctionName() == "Wages of Sin":
				self.currentScen = "Wages of Sin"
				self.szDetail = localText.getText("TXT_KEY_WB_WAGES_OF_SIN_DESC", ())
				self.szPopup = "art/interface/popups/Wages of Sin.dds"
			if inputClass.getFunctionName() == "Against the Grey":
				self.currentScen = "Against the Grey"
				self.szDetail = localText.getText("TXT_KEY_WB_AGAINST_THE_GREY_DESC", ())
				self.szPopup = "art/interface/popups/Against the Grey.dds"
			if inputClass.getFunctionName() == "Return of Winter":
				self.currentScen = "Return of Winter"
				self.szDetail = localText.getText("TXT_KEY_WB_RETURN_OF_WINTER_DESC", ())
				self.szPopup = "art/interface/popups/Return of Winter.dds"
			if inputClass.getFunctionName() == "Blood of Angels":
				self.currentScen = "Blood of Angels"
				self.szDetail = localText.getText("TXT_KEY_WB_BLOOD_OF_ANGELS_DESC", ())
				self.szPopup = "art/interface/popups/Blood of Angels.dds"
			if inputClass.getFunctionName() == "The Cult":
				self.currentScen = "The Cult"
				self.szDetail = localText.getText("TXT_KEY_WB_THE_CULT_DESC", ())
				self.szPopup = "art/interface/popups/The Cult.dds"
			if inputClass.getFunctionName() == "Against the Wall":
				self.currentScen = "Against the Wall"
				self.szDetail = localText.getText("TXT_KEY_WB_AGAINST_THE_WALL_DESC", ())
				self.szPopup = "art/interface/popups/Against the Wall.dds"
			if inputClass.getFunctionName() == "Beneath the Heel":
				self.currentScen = "Beneath the Heel"
				self.szDetail = localText.getText("TXT_KEY_WB_BENEATH_THE_HEEL_DESC", ())
				self.szPopup = "art/interface/popups/Beneath the Heel.dds"
			if inputClass.getFunctionName() == "Mulcarn Reborn":
				self.currentScen = "Mulcarn Reborn"
				self.szDetail = localText.getText("TXT_KEY_WB_MULCARN_REBORN_DESC", ())
				self.szPopup = "art/interface/popups/Mulcarn Reborn.dds"
			if inputClass.getFunctionName() == "Barbarian Assault":
				self.currentScen = "Barbarian Assault"
				self.szDetail = localText.getText("TXT_KEY_WB_BARBARIAN_ASSAULT_DESC", ())
				self.szPopup = "art/interface/popups/Barbarian Assault.dds"
			if inputClass.getFunctionName() == "The Splintered Court":
				self.currentScen = "The Splintered Court"
				self.szDetail = localText.getText("TXT_KEY_WB_THE_SPLINTERED_COURT_DESC", ())
				self.szPopup = "art/interface/popups/The Splintered Court.dds"
			if inputClass.getFunctionName() == "Gift of Kylorin":
				self.currentScen = "Gift of Kylorin"
				self.szDetail = localText.getText("TXT_KEY_WB_GIFT_OF_KYLORIN_DESC", ())
				self.szPopup = "art/interface/popups/Gift of Kylorin.dds"
			if inputClass.getFunctionName() == "Lord of the Balors":
				self.currentScen = "Lord of the Balors"
				self.szDetail = localText.getText("TXT_KEY_WB_LORD_OF_THE_BALORS_DESC", ())
				self.szPopup = "art/interface/popups/Lord of the Balors.dds"

			if inputClass.getFunctionName() == "Against the Grey Button":
				if self.isUnlocked("Against the Grey"):
					szName = "Against the Grey Malakim.CivBeyondSwordWBSave"
					if CyGame().getTrophyValue("TROPHY_WB_CIV_DECIUS") == gc.getInfoTypeForString('CIVILIZATION_CALABIM'):
						szName = "Against the Grey Calabim.CivBeyondSwordWBSave"
					self.loadScenario(szName)
					return 0
			if inputClass.getFunctionName() == "Against the Wall Button":
				self.loadScenario("Against the Wall.CivBeyondSwordWBSave")
				return 0
			if inputClass.getFunctionName() == "Barbarian Assault Button":
				self.loadScenario("Barbarian Assault.CivBeyondSwordWBSave")
				return 0
			if inputClass.getFunctionName() == "Beneath the Heel Button":
				if self.isUnlocked("Beneath the Heel"):
					self.loadScenario("Beneath the Heel.CivBeyondSwordWBSave")
					return 0
			if inputClass.getFunctionName() == "Blood of Angels Button":
				if self.isUnlocked("Blood of Angels"):
					self.loadScenario("Blood of Angels.CivBeyondSwordWBSave")
					return 0
			if inputClass.getFunctionName() == "Fall of Cuantine Button":
				self.loadScenario("Fall of Cuantine.CivBeyondSwordWBSave")
				return 0
			if inputClass.getFunctionName() == "Gift of Kylorin Button":
				self.loadScenario("Gift of Kylorin.CivBeyondSwordWBSave")
				return 0
			if inputClass.getFunctionName() == "Grand Menagerie Button":
				self.loadScenario("Grand Menagerie.CivBeyondSwordWBSave")
				return 0
			if inputClass.getFunctionName() == "Into the Desert Button":
				if self.isUnlocked("Into the Desert"):
					szName = "Into the Desert Malakim.CivBeyondSwordWBSave"
					if CyGame().getTrophyValue("TROPHY_WB_CIV_DECIUS") == gc.getInfoTypeForString('CIVILIZATION_CALABIM'):
						szName = "Into the Desert Calabim.CivBeyondSwordWBSave"
					self.loadScenario(szName)
					return 0
			if inputClass.getFunctionName() == "Lord of the Balors Button":
				if self.isUnlocked("Lord of the Balors"):
					self.loadScenario("Lord of the Balors.CivBeyondSwordWBSave")
					return 0
			if inputClass.getFunctionName() == "Mulcarn Reborn Button":
				if self.isUnlocked("Mulcarn Reborn"):
					self.loadScenario("Mulcarn Reborn.CivBeyondSwordWBSave")
					return 0
			if inputClass.getFunctionName() == "Return of Winter Button":
				self.loadScenario("Return of Winter.CivBeyondSwordWBSave")
				return 0
			if inputClass.getFunctionName() == "The Black Tower Button":
				if self.isUnlocked("The Black Tower"):
					self.loadScenario("The Black Tower.CivBeyondSwordWBSave")
					return 0
			if inputClass.getFunctionName() == "The Cult Button":
				if self.isUnlocked("The Cult"):
					self.loadScenario("The Cult.CivBeyondSwordWBSave")
					return 0
			if inputClass.getFunctionName() == "The Momus Button":
				if self.isUnlocked("The Momus"):
					self.loadScenario("The Momus.CivBeyondSwordWBSave")
					return 0
			if inputClass.getFunctionName() == "The Radiant Guard Button":
				if self.isUnlocked("The Radiant Guard"):
					self.loadScenario("The Radiant Guard.CivBeyondSwordWBSave")
					return 0
			if inputClass.getFunctionName() == "The Splintered Court Button":
				self.loadScenario("The Splintered Court.CivBeyondSwordWBSave")
				return 0
			if inputClass.getFunctionName() == "Wages of Sin Button":
				if self.isUnlocked("Wages of Sin"):
					szName = "Wages of Sin Malakim.CivBeyondSwordWBSave"
					if CyGame().getTrophyValue("TROPHY_WB_CIV_DECIUS") == gc.getInfoTypeForString('CIVILIZATION_CALABIM'):
						szName = "Wages of Sin Calabim.CivBeyondSwordWBSave"
					self.loadScenario(szName)
					return 0

			self.drawContents()
		return 0

	def update(self, fDelta):
		if (CyInterface().isDirty(InterfaceDirtyBits.Espionage_Advisor_DIRTY_BIT) == True):
			CyInterface().setDirty(InterfaceDirtyBits.Espionage_Advisor_DIRTY_BIT, False)
			self.refreshScreen()
		return

	def isUnlocked(self, szScenarioName):
		if szScenarioName == "Against the Grey":
			if not CyGame().isHasTrophy("TROPHY_WB_WAGES_OF_SIN"):
				return False
		if szScenarioName == "Beneath the Heel":
			if not CyGame().isHasTrophy("TROPHY_WB_BLOOD_OF_ANGELS"):
				return False
		if szScenarioName == "Blood of Angels":
			if not CyGame().isHasTrophy("TROPHY_WB_RETURN_OF_WINTER"):
				return False
		if szScenarioName == "Into the Desert":
			if not CyGame().isHasTrophy("TROPHY_WB_FALL_OF_CUANTINE"):
				return False
		if szScenarioName == "Lord of the Balors":
			if not CyGame().isHasTrophy("TROPHY_WB_THE_RADIANT_GUARD"):
				return False
			if not CyGame().isHasTrophy("TROPHY_WB_WAGES_OF_SIN"):
				return False
		if szScenarioName == "Mulcarn Reborn":
			if not CyGame().isHasTrophy("TROPHY_WB_THE_CULT"):
				return False
			if not CyGame().isHasTrophy("TROPHY_WB_THE_BLACK_TOWER"):
				return False
			if not CyGame().isHasTrophy("TROPHY_WB_AGAINST_THE_GREY"):
				return False
		if szScenarioName == "The Black Tower":
			if not CyGame().isHasTrophy("TROPHY_WB_THE_RADIANT_GUARD"):
				return False
		if szScenarioName == "The Cult":
			if not CyGame().isHasTrophy("TROPHY_WB_BENEATH_THE_HEEL"):
				return False
		if szScenarioName == "The Momus":
			if not CyGame().isHasTrophy("TROPHY_WB_GRAND_MENAGERIE"):
				return False
		if szScenarioName == "The Radiant Guard":
			if not CyGame().isHasTrophy("TROPHY_WB_THE_MOMUS"):
				return False
		if szScenarioName == "Wages of Sin":
			if not CyGame().isHasTrophy("TROPHY_WB_INTO_THE_DESERT"):
				return False
		return True

	def loadScenario(self, szScenarioName):
		if not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_WB_LOAD_SCREEN):
			self.getScreen().hideScreen()
			for iPlayer in range(gc.getMAX_PLAYERS()):
				pPlayer = gc.getPlayer(iPlayer)
				if pPlayer.isAlive():
					if pPlayer.isHuman():
						cf.addPlayerPopup(CyTranslator().getText("TXT_KEY_SCENARIO_WARNING",()), iPlayer)
			return 0
		fileName = os.path.join(os.getcwd(), "Mods", "Fall from Heaven 2", "Assets", "XML", "Scenarios", szScenarioName)
		if os.path.isfile(fileName):
			if WBDesc.read(fileName) < 0:
				print "Failed to read %s" % fileName
				return 0
			CyMap().erasePlots()
			CyGame().resetGame()
			CyGame().resetPlayers()
			CyInterface().exitingToMainMenu(fileName, true)
			if WBDesc.applyMap() < 0:
				print "Failed to apply map %s" % fileName
				return 0
#			WBDesc.applyInitialItems()
