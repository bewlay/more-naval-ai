## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums

# globals
gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class CvPediaSpell:
	"Civilopedia Screen for Spells"

	def __init__(self, main):
		self.iSpell = -1
		self.top = main
	
		self.BUTTON_SIZE = 46
		
		self.X_UNIT_PANE = 50
		self.Y_UNIT_PANE = 80
		self.W_UNIT_PANE = 250
		self.H_UNIT_PANE = 210

		self.X_ICON = 98
		self.Y_ICON = 110
		self.W_ICON = 150
		self.H_ICON = 150
		self.ICON_SIZE = 64

		self.X_PREREQ_PANE = 330
		self.Y_PREREQ_PANE = 60
		self.W_PREREQ_PANE = 420
		self.H_PREREQ_PANE = 110

		self.X_HELP_PANE = 330
		self.Y_HELP_PANE = 180
		self.W_HELP_PANE = self.W_PREREQ_PANE
		self.H_HELP_PANE = 110
				
		self.X_SPECIAL_PANE = 50 #330
		self.Y_SPECIAL_PANE = 294
		self.W_SPECIAL_PANE = self.W_PREREQ_PANE + (330-50)
		self.H_SPECIAL_PANE = 380

		#~ self.X_UNIT_GROUP_PANE = 50
		#~ self.Y_UNIT_GROUP_PANE = 294
		#~ self.W_UNIT_GROUP_PANE = 250
		#~ self.H_UNIT_GROUP_PANE = 380
		#~ self.DY_UNIT_GROUP_PANE = 25
#		self.ITEMS_MARGIN = 18
#		self.ITEMS_SEPARATION = 2

	# Screen construction function
	def interfaceScreen(self, iSpell):	
			
		self.iSpell = iSpell
	
		self.top.deleteAllWidgets()						
							
		screen = self.top.getScreen()
		
		bNotActive = (not screen.isActive())
		if bNotActive:
			self.top.setPediaCommonWidgets()

		# Header...
		szHeader = u"<font=4b>" + gc.getSpellInfo(self.iSpell).getDescription().upper() + u"</font>"
		szHeaderId = self.top.getNextWidgetName()
		screen.setLabel(szHeaderId, "Background", szHeader, CvUtil.FONT_CENTER_JUSTIFY, self.top.X_SCREEN, self.top.Y_TITLE, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		
		# Top
		screen.setText(self.top.getNextWidgetName(), "Background", self.top.MENU_TEXT, CvUtil.FONT_LEFT_JUSTIFY, self.top.X_MENU, self.top.Y_MENU, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_PEDIA_MAIN, CivilopediaPageTypes.CIVILOPEDIA_PAGE_SPELL, -1)

		if self.top.iLastScreen	!= CvScreenEnums.PEDIA_SPELL or bNotActive:		
			self.placeLinks(true)
			self.top.iLastScreen = CvScreenEnums.PEDIA_SPELL
		else:
			self.placeLinks(false)
			
		# Icon
		screen.addPanel( self.top.getNextWidgetName(), "", "", False, False,
		    self.X_UNIT_PANE, self.Y_UNIT_PANE, self.W_UNIT_PANE, self.H_UNIT_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(self.top.getNextWidgetName(), "", "", false, false,
		    self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_MAIN)
		screen.addDDSGFC(self.top.getNextWidgetName(), gc.getSpellInfo(self.iSpell).getButton(),
		    self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1 )
#		screen.addDDSGFC(self.top.getNextWidgetName(), gc.getSpellInfo(self.iSpell).getButton(), self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, WidgetTypes.WIDGET_GENERAL, self.iSpell, -1 )

		# Place Required promotions
		self.placePrereqs()

		# Place Allowing promotions
		self.placeHelp()
				
		# Place the Special abilities block
		self.placeEffects()
		
		#self.placeUnitGroups()
			
				
	# Place prereqs...
	def placePrereqs(self):

		screen = self.top.getScreen()
		
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_REQUIRES", ()), "", false, true,
				 self.X_PREREQ_PANE, self.Y_PREREQ_PANE, self.W_PREREQ_PANE, self.H_PREREQ_PANE, PanelStyles.PANEL_STYLE_BLUE50 )
		
		screen.attachLabel(panelName, "", "  ")

		ePromo = gc.getSpellInfo(self.iSpell).getPromotionPrereq1()
		if (ePromo > -1):
			screen.attachImageButton( panelName, "", gc.getPromotionInfo(ePromo).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, ePromo, 1, False )

			ePromo = gc.getSpellInfo(self.iSpell).getPromotionPrereq2()
			if (ePromo > -1):
	        		screen.attachTextGFC(panelName, "", localText.getText("TXT_KEY_AND", ()), FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				screen.attachImageButton( panelName, "", gc.getPromotionInfo(ePromo).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, ePromo, 1, False )
								
		#eTech = gc.getSpellInfo(self.iSpell).getTechPrereq()
		#if (eTech > -1):
		#	screen.attachImageButton( panelName, "", gc.getTechInfo(eTech).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, eTech, 1, False )		

	def placeHelp(self):

		screen = self.top.getScreen()

		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_HELP", ()), "", false, true,
				 self.X_HELP_PANE, self.Y_HELP_PANE, self.W_HELP_PANE, self.H_HELP_PANE, PanelStyles.PANEL_STYLE_BLUE50 )
		
		screen.attachLabel(panelName, "", "  ")
		listName = self.top.getNextWidgetName()
		
		szSpecialText = CyGameTextMgr().getSpellHelp(self.iSpell, True)[1:]
		
		screen.addMultilineText(listName, szSpecialText, self.X_HELP_PANE+5, self.Y_HELP_PANE+30, self.W_HELP_PANE-10, self.H_HELP_PANE-35, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
						
	def placeEffects(self):

		screen = self.top.getScreen()
		
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_SPELL_EFFECTS", ()), "", true, false,
				 self.X_SPECIAL_PANE, self.Y_SPECIAL_PANE, self.W_SPECIAL_PANE, self.H_SPECIAL_PANE, PanelStyles.PANEL_STYLE_BLUE50 )
		
		listName = self.top.getNextWidgetName()
		
		
		pediaText = gc.getSpellInfo(self.iSpell).getCivilopedia()

		screen.addMultilineText(listName, pediaText, self.X_SPECIAL_PANE+5, self.Y_SPECIAL_PANE+30, self.W_SPECIAL_PANE-10, self.H_SPECIAL_PANE-35, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)	


	def placeLinks(self, bRedraw):

		screen = self.top.getScreen()

		if bRedraw:		               
			screen.clearListBoxGFC(self.top.LIST_ID)
		
		# sort techs alphabetically
		listSpells = []
		iCount = 0
		for iSpell in range(gc.getNumSpellInfos()):
			if not gc.getSpellInfo(iSpell).isGraphicalOnly():
				listSpells.append(iSpell)
				iCount += 1

		listSorted = [(0,0)] * iCount
		iI = 0
		for iSpell in listSpells:
			listSorted[iI] = (gc.getSpellInfo(iSpell).getDescription(), iSpell)
			iI += 1
		listSorted.sort()

		i = 0
		iSelected = 0
		for iI in range(len(listSorted)):
			if (not gc.getSpellInfo(iI).isGraphicalOnly()):
				if bRedraw:
					screen.appendListBoxString( self.top.LIST_ID, listSorted[iI][0], WidgetTypes.WIDGET_PEDIA_JUMP_TO_SPELL, listSorted[iI][1], 0, CvUtil.FONT_LEFT_JUSTIFY )
				if listSorted[iI][1] == self.iSpell:
					iSelected = i			
				i += 1

		screen.setSelectedListBoxStringGFC(self.top.LIST_ID, iSelected)

	# Will handle the input for this screen...
	def handleInput (self, inputClass):
		return 0

