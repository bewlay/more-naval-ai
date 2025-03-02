## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums
import string
import CvScreensInterface

from InterfaceUtils import GenericAdvisorScreen

# globals
gc = CyGlobalContext()
game = gc.getGame()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

#FfH: Added by Kael 12/29/2006
import PyHelpers
import CustomFunctions
cf = CustomFunctions.CustomFunctions()
PyPlayer = PyHelpers.PyPlayer
#FfH: End Add

class CvCivicsScreen( GenericAdvisorScreen ) : # lfgr 09/2019: Full-screen Advisors
	"Civics Screen"

	def __init__(self):
		self.SCREEN_NAME = "CivicsScreen"
		self.CANCEL_NAME = "CivicsCancel"
		self.EXIT_NAME = "CivicsExit"
		self.TITLE_NAME = "CivicsTitleHeader"
		self.BUTTON_NAME = "CivicsScreenButton"
		self.TEXT_NAME = "CivicsScreenText"
		self.AREA_NAME = "CivicsScreenArea"
		self.HELP_AREA_NAME = "CivicsScreenHelpArea"
		self.HELP_IMAGE_NAME = "CivicsScreenCivicOptionImage"
		self.DEBUG_DROPDOWN_ID =  "CivicsDropdownWidget"
		self.BACKGROUND_ID = "CivicsBackground"
		self.HELP_HEADER_NAME = "CivicsScreenHeaderName"

#		self.HEADINGS_TOP = 70
		self.HEADINGS_TOP = 50
#		self.HEADINGS_SPACING = 5
		self.HEADINGS_SPACING = 4
#		self.HEADINGS_BOTTOM = 280
		self.HEADINGS_BOTTOM = 307
#		self.HELP_TOP = 350
		self.HELP_TOP = 375
#		self.TEXT_MARGIN = 15
		self.TEXT_MARGIN = 12
		self.BUTTON_SIZE = 24
		self.BIG_BUTTON_SIZE = 64
		self.BOTTOM_LINE_HEIGHT = 60

		self.X_SCREEN = 600
		self.Y_SCREEN = 396
		self.Z_SCREEN = -6.1
		self.Y_TITLE = 8		
		self.Z_TEXT = self.Z_SCREEN - 0.2

		#RevolutionDCM start - revolutions screen adjustment
		if (game.isOption(GameOptionTypes.GAMEOPTION_REVOLUTIONS)):
			for l in range(gc.getNumCivicInfos()):
				self.HEADINGS_HEIGHT = (((40 + self.BUTTON_SIZE + self.TEXT_MARGIN) * l/self.CIVICCATEGORIES)/5 * 2) + 260
		else:
			for l in range(gc.getNumCivicInfos()):
				self.HEADINGS_HEIGHT = (((40 + self.BUTTON_SIZE + self.TEXT_MARGIN) * l/self.CIVICCATEGORIES)/5 * 2) + 160
		#RevolutionDCM end
		
		self.CivicsScreenInputMap = {
			self.BUTTON_NAME		: self.CivicsButton,
			self.TEXT_NAME			: self.CivicsButton,
			self.EXIT_NAME			: self.Revolution,
			self.CANCEL_NAME		: self.Cancel,
			}

		self.iActivePlayer = -1

		self.m_paeCurrentCivics = []
		self.m_paeDisplayCivics = []
		self.m_paeOriginalCivics = []

	def getScreen(self):
		return CyGInterfaceScreen(self.SCREEN_NAME, CvScreenEnums.CIVICS_SCREEN)

	def setActivePlayer(self, iPlayer):

		self.iActivePlayer = iPlayer
		activePlayer = gc.getPlayer(iPlayer)

		self.m_paeCurrentCivics = []
		self.m_paeDisplayCivics = []
		self.m_paeOriginalCivics = []
		for i in range (gc.getNumCivicOptionInfos()):
			self.m_paeCurrentCivics.append(activePlayer.getCivics(i));
			self.m_paeDisplayCivics.append(activePlayer.getCivics(i));
			self.m_paeOriginalCivics.append(activePlayer.getCivics(i));

	# lfgr 09/2019: Cleaned up, updated to allow for full-screen
	def interfaceScreen (self):
		screen = self.getScreen()
		if screen.isActive():
			return
		screen.setRenderInterfaceOnly(True)
		screen.showScreen( PopupStates.POPUPSTATE_IMMEDIATE, False)

		screen.showWindowBackground(False)
		
		# Init dimensions and button positions
		xPanelWidth, yPanelHeight = self.initDimensions()
		self.xHeadingsWidth = ( xPanelWidth - 5 - self.HEADINGS_SPACING * (gc.getNumCivicOptionInfos() - 1) ) \
				/ gc.getNumCivicOptionInfos() # Orig: 199
		self.xBottomLineWidth = xPanelWidth - 10 # Orig: 1014
		self.yHelpBottom = yPanelHeight - 130 # Orig: 638
		self.yBottomLineTop = self.yHelpBottom + 12 # Orig: 650
		self.xCancel = xPanelWidth - 472 # Orig: 552
		self.yCancel = yPanelHeight - 42 # Orig: 726
		self.xExit = xPanelWidth - 30 # Orig: 994
		self.yExit = yPanelHeight - 42 # Orig: 726
		
		# Background, header and footer
		self.addBackgroundHeaderFooter( localText.getText("TXT_KEY_CIVICS_SCREEN_TITLE", ()).upper() )
		
		# Cancel button
		screen.setText(self.CANCEL_NAME, "Background",
				u"<font=4>" + localText.getText("TXT_KEY_SCREEN_CANCEL", ()).upper() + u"</font>",
				CvUtil.FONT_CENTER_JUSTIFY, self.xCancel, self.yCancel, self.Z_TEXT,
				FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, 1, 0)
		
		self.setActivePlayer(gc.getGame().getActivePlayer())						

		if (CyGame().isDebugMode()):
			self.szDropdownName = self.DEBUG_DROPDOWN_ID
			screen.addDropDownBoxGFC(self.szDropdownName, 22, 12, 300, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
			for j in range(gc.getMAX_PLAYERS()):
				if (gc.getPlayer(j).isAlive()):
					screen.addPullDownString(self.szDropdownName, gc.getPlayer(j).getName(), j, j, False )

		screen.addPanel("CivicsBottomLine", "", "", True, True, self.HEADINGS_SPACING, self.yBottomLineTop, self.xBottomLineWidth, self.BOTTOM_LINE_HEIGHT, PanelStyles.PANEL_STYLE_MAIN )

		# Draw Contents
		self.drawContents()

		return 0

	# Draw the contents...
	def drawContents(self):
	
		# Draw the radio buttons
		self.drawAllButtons()
				
		# Draw Help Text
		self.drawAllHelpText()
		
		# Update Maintenance/anarchy/etc.
		self.updateAnarchy()

	def drawCivicOptionButtons(self, iCivicOption):

		activePlayer = gc.getPlayer(self.iActivePlayer)
		screen = self.getScreen()
		
		for j in range(gc.getNumCivicInfos()):

			if (gc.getCivicInfo(j).getCivicOptionType() == iCivicOption):										
				screen.setState(self.getCivicsButtonName(j), self.m_paeCurrentCivics[iCivicOption] == j)
							
				if (self.m_paeDisplayCivics[iCivicOption] == j):
					#screen.setState(self.getCivicsButtonName(j), True)
					screen.show(self.getCivicsButtonName(j))
				elif (activePlayer.canDoCivics(j)):
					#screen.setState(self.getCivicsButtonName(j), False)
					screen.show(self.getCivicsButtonName(j))
				else:
					screen.hide(self.getCivicsButtonName(j))
								
	# Will draw the radio buttons (and revolution)
	def drawAllButtons(self):				

		for i in range(gc.getNumCivicOptionInfos()):
		
			fX = self.HEADINGS_SPACING + (self.xHeadingsWidth + self.HEADINGS_SPACING) * i
			fY = self.HEADINGS_TOP
			szAreaID = self.AREA_NAME + str(i)
			screen = self.getScreen()
			screen.addPanel( szAreaID, "", "", True, True, fX, fY, self.xHeadingsWidth, self.HEADINGS_BOTTOM - self.HEADINGS_TOP, PanelStyles.PANEL_STYLE_MAIN )
#			screen.setLabel("", "Background",  u"<font=3>" + gc.getCivicOptionInfo(i).getDescription().upper() + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, fX + self.HEADINGS_WIDTH/2, self.HEADINGS_TOP + self.TEXT_MARGIN, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
			screen.setLabel("", "Background",  u"<font=3>" + gc.getCivicOptionInfo(i).getDescription() + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, fX + self.xHeadingsWidth / 2, self.HEADINGS_TOP + self.TEXT_MARGIN, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

			fY += self.TEXT_MARGIN
			
			for j in range(gc.getNumCivicInfos()):
				if (gc.getCivicInfo(j).getCivicOptionType() == i):										
					fY += 2 * self.TEXT_MARGIN
					screen.addCheckBoxGFC(self.getCivicsButtonName(j), gc.getCivicInfo(j).getButton(), ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), fX + self.BUTTON_SIZE/2, fY, self.BUTTON_SIZE, self.BUTTON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)
					screen.setText(self.getCivicsTextName(j), "", u"<font=2>" +gc.getCivicInfo(j).getDescription() + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, fX + self.BUTTON_SIZE + self.TEXT_MARGIN, fY, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

			self.drawCivicOptionButtons(i)
					
							
	def highlight(self, iCivic):
		iCivicOption = gc.getCivicInfo(iCivic).getCivicOptionType()
		if self.m_paeDisplayCivics[iCivicOption] != iCivic:
			self.m_paeDisplayCivics[iCivicOption] = iCivic
			self.drawCivicOptionButtons(iCivicOption)
			return True
		return False
		
	def unHighlight(self, iCivic):		
		iCivicOption = gc.getCivicInfo(iCivic).getCivicOptionType()
		if self.m_paeDisplayCivics[iCivicOption] != self.m_paeCurrentCivics[iCivicOption]:
			self.m_paeDisplayCivics[iCivicOption] = self.m_paeCurrentCivics[iCivicOption]
			self.drawCivicOptionButtons(iCivicOption)
			return True
		return False
		
	def select(self, iCivic):
		activePlayer = gc.getPlayer(self.iActivePlayer)
		if (not activePlayer.canDoCivics(iCivic)):
			# If you can't even do this, get out....
			return 0
		
		iCivicOption = gc.getCivicInfo(iCivic).getCivicOptionType()
		
		# Set the previous widget
		iCivicPrev = self.m_paeCurrentCivics[iCivicOption]

#FfH: Added by Kael 12/25/2007
		bWarn = False
		py = PyPlayer(self.iActivePlayer)
		for pUnit in py.getUnitList():
			if gc.getUnitInfo(pUnit.getUnitType()).isAbandon():
				if gc.getUnitInfo(pUnit.getUnitType()).getPrereqCivic() == iCivicPrev:
					bWarn = True
		if bWarn:
			cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_CIVIC_ABANDON_WARN",()), 'art/interface/popups/Abandon.dds')
#FfH: End Add
		
		# Switch the widgets
		self.m_paeCurrentCivics[iCivicOption] = iCivic
		
		# Unighlight the previous widget
		self.unHighlight(iCivicPrev)
		self.getScreen().setState(self.getCivicsButtonName(iCivicPrev), False)

		# highlight the new widget
		self.highlight(iCivic)		
		self.getScreen().setState(self.getCivicsButtonName(iCivic), True)
		
		return 0

	def CivicsButton(self, inputClass):
	
		if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED) :
			if (inputClass.getFlags() & MouseFlags.MOUSE_RBUTTONUP):
				CvScreensInterface.pediaJumpToCivic((inputClass.getID(), ))
			else:
				# Select button
				self.select(inputClass.getID())
				self.drawHelpText(gc.getCivicInfo(inputClass.getID()).getCivicOptionType())
				self.updateAnarchy()
		elif (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CURSOR_MOVE_ON) :
			# Highlight this button
			if self.highlight(inputClass.getID()):
				self.drawHelpText(gc.getCivicInfo(inputClass.getID()).getCivicOptionType())
				self.updateAnarchy()
		elif (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CURSOR_MOVE_OFF) :
			if self.unHighlight(inputClass.getID()):
				self.drawHelpText(gc.getCivicInfo(inputClass.getID()).getCivicOptionType())
				self.updateAnarchy()

		return 0

		
	def drawHelpText(self, iCivicOption):
		
		activePlayer = gc.getPlayer(self.iActivePlayer)
		iCivic = self.m_paeDisplayCivics[iCivicOption]

		szPaneID = "CivicsHelpTextBackground" + str(iCivicOption)
		screen = self.getScreen()

		szHelpText = u""

		# Upkeep string
		if ((gc.getCivicInfo(iCivic).getUpkeep() != -1) and not activePlayer.isNoCivicUpkeep(iCivicOption)):
			szHelpText = gc.getUpkeepInfo(gc.getCivicInfo(iCivic).getUpkeep()).getDescription()
		else:
			szHelpText = localText.getText("TXT_KEY_CIVICS_SCREEN_NO_UPKEEP", ())

		szHelpText += CyGameTextMgr().parseCivicInfo(iCivic, False, True, True)

		fX = self.HEADINGS_SPACING + (self.xHeadingsWidth + self.HEADINGS_SPACING) * iCivicOption

		screen.setLabel( self.HELP_HEADER_NAME + str(iCivicOption), "Background",  u"<font=3>" + gc.getCivicInfo(self.m_paeDisplayCivics[iCivicOption]).getDescription() + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, fX + self.xHeadingsWidth / 2, self.HELP_TOP + self.TEXT_MARGIN, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

		fY = self.HELP_TOP - self.BIG_BUTTON_SIZE
		szHelpImageID = self.HELP_IMAGE_NAME + str(iCivicOption)		
		screen.setImageButton( szHelpImageID, gc.getCivicInfo(iCivic).getButton(), fX + self.xHeadingsWidth / 2 - self.BIG_BUTTON_SIZE / 2, fY, self.BIG_BUTTON_SIZE, self.BIG_BUTTON_SIZE, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC, iCivic, 1 )

		fY = self.HELP_TOP + 3 * self.TEXT_MARGIN
		szHelpAreaID = self.HELP_AREA_NAME + str(iCivicOption)		
		screen.addMultilineText( szHelpAreaID, u"<font=2>" + szHelpText + u"</font>", fX + 5, fY, self.xHeadingsWidth - 7, self.yHelpBottom - fY - 2, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
		
		
	# Will draw the help text
	def drawAllHelpText(self):
		for i in range (gc.getNumCivicOptionInfos()):		

			fX = self.HEADINGS_SPACING + (self.xHeadingsWidth + self.HEADINGS_SPACING) * i

			szPaneID = "CivicsHelpTextBackground" + str(i)
			screen = self.getScreen()
			screen.addPanel( szPaneID, "", "", True, True, fX, self.HELP_TOP, self.xHeadingsWidth, self.yHelpBottom - self.HELP_TOP, PanelStyles.PANEL_STYLE_MAIN )

			self.drawHelpText(i)


	# Will Update the maintenance/anarchy/etc
	def updateAnarchy(self):

		screen = self.getScreen()

		activePlayer = gc.getPlayer(self.iActivePlayer)

		bChange = False
		i = 0
		while (i  < gc.getNumCivicOptionInfos() and not bChange):
			if (self.m_paeCurrentCivics[i] != self.m_paeOriginalCivics[i]):
				bChange = True
			i += 1		
		
		# Make the revolution button
		screen.deleteWidget(self.EXIT_NAME)
		if (activePlayer.canRevolution(0) and bChange):			
			screen.setText( self.EXIT_NAME, "Background", u"<font=4>" + localText.getText("TXT_KEY_CONCEPT_REVOLUTION", ( )).upper() + u"</font>", CvUtil.FONT_RIGHT_JUSTIFY, self.xExit, self.yExit, self.Z_TEXT, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_REVOLUTION, 1, 0 )
			screen.show(self.CANCEL_NAME)
		else:
			screen.setText( self.EXIT_NAME, "Background", u"<font=4>" + localText.getText("TXT_KEY_PEDIA_SCREEN_EXIT", ( )).upper() + u"</font>", CvUtil.FONT_RIGHT_JUSTIFY, self.xExit, self.yExit, self.Z_TEXT, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, 1, -1 )
			screen.hide(self.CANCEL_NAME)

		# Anarchy
		iTurns = activePlayer.getCivicAnarchyLength(self.m_paeDisplayCivics);
		
		if (activePlayer.canRevolution(0)):
			szText = localText.getText("TXT_KEY_ANARCHY_TURNS", (iTurns, ))
		else:
			szText = CyGameTextMgr().setRevolutionHelp(self.iActivePlayer)

		screen.setLabel("CivicsRevText", "Background", u"<font=3>" + szText + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, self.X_SCREEN, self.yBottomLineTop + self.TEXT_MARGIN // 2, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

		# Maintenance		
		szText = localText.getText("TXT_KEY_CIVIC_SCREEN_UPKEEP", (activePlayer.getCivicUpkeep(self.m_paeDisplayCivics, True), ))
		screen.setLabel("CivicsUpkeepText", "Background", u"<font=3>" + szText + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, self.X_SCREEN, self.yBottomLineTop + self.BOTTOM_LINE_HEIGHT - 2 * self.TEXT_MARGIN, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		
	# Revolution!!!
	def Revolution(self, inputClass):

		activePlayer = gc.getPlayer(self.iActivePlayer)

		if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED) :
			if (activePlayer.canRevolution(0)):
				messageControl = CyMessageControl()
				messageControl.sendUpdateCivics(self.m_paeDisplayCivics)			
			screen = self.getScreen()
			screen.hideScreen()


	def Cancel(self, inputClass):
		screen = self.getScreen()
		if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED) :
			for i in range (gc.getNumCivicOptionInfos()):
				self.m_paeCurrentCivics[i] = self.m_paeOriginalCivics[i]
				self.m_paeDisplayCivics[i] = self.m_paeOriginalCivics[i]
			
			self.drawContents()
			
	def getCivicsButtonName(self, iCivic):
		szName = self.BUTTON_NAME + str(iCivic)
		return szName

	def getCivicsTextName(self, iCivic):
		szName = self.TEXT_NAME + str(iCivic)
		return szName

	# Will handle the input for this screen...
	def handleInput(self, inputClass):
		if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_LISTBOX_ITEM_SELECTED):
			screen = self.getScreen()
			iIndex = screen.getSelectedPullDownID(self.DEBUG_DROPDOWN_ID)
			self.setActivePlayer(screen.getPullDownData(self.DEBUG_DROPDOWN_ID, iIndex))
			self.drawContents()
			return 1
		elif (self.CivicsScreenInputMap.has_key(inputClass.getFunctionName())):	
			'Calls function mapped in CvCivicsScreen'
			# only get from the map if it has the key		

			# get bound function from map and call it
			self.CivicsScreenInputMap.get(inputClass.getFunctionName())(inputClass)
			return 1
		return 0
		
	def update(self, fDelta):
		return




