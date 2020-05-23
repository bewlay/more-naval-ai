## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
##
## Scrolling aspect by johny smith in http://forums.civfanatics.com/showthread.php?t=260697&highlight=scrolling+religion
## Inspiration from zappara to handle new religions, extended to handle new types of buildings and units

from CvPythonExtensions import *
import PyHelpers
import CvUtil
import CvScreenEnums

# BUG - start
import BugCore
import PlayerUtil
import ReligionUtil
AdvisorOpt = BugCore.game.Advisors
# BUG - end

# lfgr 05/2020: Full-screen Advisors: refactored, added full-screen support
from InterfaceUtils import GenericAdvisorScreen

PyPlayer = PyHelpers.PyPlayer

# globals
gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

#FfH: Added by Kael 12/29/2006
import CustomFunctions
cf = CustomFunctions.CustomFunctions()
#FfH: End Add

class CvReligionScreen( GenericAdvisorScreen ) :
	"Religion Advisor Screen"

	def __init__(self):
		
		self.SCREEN_NAME = "ReligionScreen"
		self.BUTTON_NAME = "ReligionScreenButton"
		self.RELIGION_NAME = "ReligionText"
		self.CONVERT_NAME = "ReligionConvertButton"
		self.CANCEL_NAME = "ReligionCancelButton"
		self.CITY_NAME = "ReligionCity"
		self.HEADER_NAME = "ReligionScreenHeader"
		self.DEBUG_DROPDOWN_ID =  "ReligionDropdownWidget"
		self.TABLE_ID =  "ReligionTableWidget"
		self.AREA1_ID =  "ReligionAreaWidget1"
		self.AREA2_ID =  "ReligionAreaWidget2"
		self.RELIGION_PANEL_ID = "ReligionPanel"
		self.RELIGION_ANARCHY_WIDGET = "ReligionAnarchyWidget"
		
		# Some size/positioning constants
		
		self.Z_SCREEN = -6.1
		self.Z_TEXT = self.Z_SCREEN - 0.2
		self.DZ = -0.2

		self.BUTTON_SIZE = 48
		
		self.LEFT_EDGE_TEXT = 10
		self.X_RELIGION_START = 180
		self.DX_RELIGION = 98
		self.Y_RELIGION = 35
		self.Y_FOUNDED = 90
		self.Y_HOLY_CITY = 115
		self.Y_INFLUENCE = 140
		self.Y_RELIGION_NAME = 58
		
		self.X_SCROLLABLE_RELIGION_AREA = 0
		self.Y_SCROLLABLE_RELIGION_AREA = 0
		self.H_SCROLL_OFFSET = 20
		
		# BUG - start
		self.NUM_RELIGIONS = -1
		self.COL_ZOOM_CITY = 0
		self.COL_CITY_NAME = 1
		self.COL_FIRST_RELIGION = 2
		self.COL_FIRST_UNIT = 9
		self.COL_FIRST_BUILDING = 10
		self.COL_EFFECTS = 14
		self.TABLE_COLUMNS = 15
		# BUG - end

		self.iReligionExamined = -1
		self.iReligionSelected = -1
		self.iReligionOriginal = -1
		self.iActivePlayer = -1
		
		self.bScreenUp = False
		
		self.ReligionScreenInputMap = {
			self.RELIGION_NAME		: self.ReligionScreenButton,
			self.BUTTON_NAME		: self.ReligionScreenButton,
			self.CONVERT_NAME		: self.ReligionConvert,
			self.CANCEL_NAME		: self.ReligionCancel,
			}

		# BUG Constants
		self.bBUGConstants = False

	def getScreen(self):
		return CyGInterfaceScreen(self.SCREEN_NAME, CvScreenEnums.RELIGION_SCREEN)

	def interfaceScreen (self):

		self.SCREEN_ART = ArtFileMgr.getInterfaceArtInfo("TECH_BG").getPath()
		self.NO_STATE_BUTTON_ART = ArtFileMgr.getInterfaceArtInfo("INTERFACE_BUTTONS_CANCEL").getPath()
		self.EXIT_TEXT = u"<font=4>" + localText.getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>"
		self.CONVERT_TEXT = u"<font=4>" + localText.getText("TXT_KEY_RELIGION_CONVERT", ()).upper() + "</font>"
		self.CANCEL_TEXT = u"<font=4>" + localText.getText("TXT_KEY_SCREEN_CANCEL", ()).upper() + "</font>"
		
		self.iActivePlayer = gc.getGame().getActivePlayer()
		
# BUG - start
		if self.NUM_RELIGIONS == -1:
			self.NUM_RELIGIONS = ReligionUtil.getNumReligions()
			self.COL_FIRST_UNIT = self.COL_FIRST_RELIGION + self.NUM_RELIGIONS
			self.COL_FIRST_BUILDING = self.COL_FIRST_UNIT + ReligionUtil.getNumUnitTypes()
			self.COL_EFFECTS = self.COL_FIRST_BUILDING + ReligionUtil.getNumBuildingTypes()
			self.TABLE_COLUMNS = self.COL_EFFECTS + 1
# BUG - end

		self.bScreenUp = True

		screen = self.getScreen()
		if screen.isActive():
			return
		screen.setRenderInterfaceOnly(True)
		screen.showScreen( PopupStates.POPUPSTATE_IMMEDIATE, False)
		
		# Setup dimensions
		self.initDimensions()
		xCancel = self.wScreen - 472
		yCancel = self.yExitButton
		self.xAnarchyText = 21
		self.yAnarchyText = self.yExitButton
		
		self.xReligionArea = 45
		self.yReligionArea = 84
		self.wReligionArea = self.wScreen - 90
		self.hReligionArea = 175
		if AdvisorOpt.isReligious():
			#self.yReligionArea -= 40
			self.hReligionArea += 75
			if AdvisorOpt.isShowAllReligions():
				self.leReligions = ReligionUtil.getAllReligions()
			elif AdvisorOpt.isShowFoundedReligions():
				self.leReligions = ReligionUtil.getFoundedReligions()
			else:
				self.leReligions = ReligionUtil.getPlayerReligions( gc.getPlayer( self.iActivePlayer ) )
		else:
			self.leReligions = ReligionUtil.getAllReligions()
		
		# One city area with BUG
		self.xCityArea = self.xReligionArea
		self.yCityArea = self.yReligionArea + self.hReligionArea + self.H_SCROLL_OFFSET + 3
		self.wCityArea = self.wReligionArea
		self.hCityArea = self.hScreen - self.yCityArea - 130 - self.H_SCROLL_OFFSET + 20
		
		# Two city areas without BUG
		self.wCityAreaSplitSeparator = 20
		self.xCityArea1 = self.xCityArea
		self.wCityAreaSplit = ( self.wScreen - 2*self.xCityArea - self.wCityAreaSplitSeparator ) // 2
		self.xCityArea2 = self.xCityArea + self.wCityAreaSplit + self.wCityAreaSplitSeparator
		
		# Background, header, and footer
		self.addBackgroundHeaderFooter( localText.getText( "TXT_KEY_RELIGION_SCREEN_TITLE", () ).upper() )
		
		# Cancel button
		screen.setText( self.CANCEL_NAME, "Background", self.CANCEL_TEXT, CvUtil.FONT_CENTER_JUSTIFY,
				xCancel, yCancel, self.Z_TEXT, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, 1, 0 )

		screen.showWindowBackground(False)
		
		# Make the scrollable areas for the city list...
		
		# ComboBox for player selection in debug mode
		if (CyGame().isDebugMode()):
			self.szDropdownName = self.DEBUG_DROPDOWN_ID
			screen.addDropDownBoxGFC(self.szDropdownName, 22, 12, 300, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
			for j in range(gc.getMAX_PLAYERS()):
				if (gc.getPlayer(j).isAlive()):
					screen.addPullDownString(self.szDropdownName, gc.getPlayer(j).getName(), j, j, False )

		# Make the scrollable area for the religions list...
		screen.addPanel( self.RELIGION_PANEL_ID, "", "", False, True, self.xReligionArea, self.yReligionArea,
				self.wReligionArea, self.hReligionArea + 5, PanelStyles.PANEL_STYLE_MAIN )
		screen.addScrollPanel( "ReligionList", u"", self.xReligionArea, self.yReligionArea, self.wReligionArea, self.hReligionArea, PanelStyles.PANEL_STYLE_EXTERNAL )
		screen.setActivation( "ReligionList", ActivationTypes.ACTIVATE_NORMAL )

		# Draw Religion info
		self.drawReligionInfo()

		self.drawHelpInfo()
		
		self.drawCityInfo(self.iReligionSelected)

	# Draws the religion buttons and information
	def drawReligionInfo(self):

		screen = self.getScreen()

		# Put everything on a scrollable area
		szArea = "ReligionList"

		# Religion buttons at the top
		xLoop = self.X_RELIGION_START
		for iRel in self.leReligions:
			szButtonName = self.getReligionButtonName(iRel)
			if gc.getGame().getReligionGameTurnFounded(iRel) >= 0:
				screen.addCheckBoxGFCAt(szArea, szButtonName, gc.getReligionInfo(iRel).getButton(), ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), self.X_SCROLLABLE_RELIGION_AREA + xLoop - 25, self.Y_SCROLLABLE_RELIGION_AREA + 5, self.BUTTON_SIZE, self.BUTTON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL, False)
			else:
				screen.setImageButtonAt(szButtonName, szArea, gc.getReligionInfo(iRel).getButtonDisabled(), self.X_SCROLLABLE_RELIGION_AREA + xLoop - 25, self.Y_SCROLLABLE_RELIGION_AREA + 5, self.BUTTON_SIZE, self.BUTTON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1)
			szName = self.getReligionTextName(iRel)
			szLabel = gc.getReligionInfo(iRel).getDescription()
#			if (self.iReligionSelected == iRel):
#				szLabel = localText.changeTextColor(szLabel, gc.getInfoTypeForString("COLOR_YELLOW"))
			screen.setLabelAt(szName, szArea, szLabel, CvUtil.FONT_CENTER_JUSTIFY, self.X_SCROLLABLE_RELIGION_AREA + xLoop, self.Y_RELIGION_NAME, self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			xLoop += self.DX_RELIGION

		szButtonName = self.getReligionButtonName(gc.getNumReligionInfos())
		screen.addCheckBoxGFCAt(szArea, szButtonName, self.NO_STATE_BUTTON_ART, ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), self.X_SCROLLABLE_RELIGION_AREA + xLoop - 25, self.Y_SCROLLABLE_RELIGION_AREA + 5, self.BUTTON_SIZE, self.BUTTON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL, False)

		szName = self.getReligionTextName(gc.getNumReligionInfos())
		szLabel = localText.getText("TXT_KEY_RELIGION_SCREEN_NO_STATE", ())
#		if (self.iReligionSelected == gc.getNumReligionInfos()):
#			szLabel = localText.changeTextColor(szLabel, gc.getInfoTypeForString("COLOR_YELLOW"))
		screen.setLabelAt(szName, szArea, szLabel, CvUtil.FONT_CENTER_JUSTIFY,  self.X_SCROLLABLE_RELIGION_AREA + xLoop, self.Y_RELIGION_NAME, self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)		

	
	def drawHelpInfo(self):
		
		screen = self.getScreen()
		szArea = "ReligionList"
		
		## johny smith
		## This attaches the text to the panel
		## This is for every line of font
		# Founded...
		screen.setLabelAt("", szArea, localText.getText("TXT_KEY_RELIGION_SCREEN_DATE_FOUNDED", ()), CvUtil.FONT_LEFT_JUSTIFY, self.LEFT_EDGE_TEXT, self.Y_FOUNDED, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		# Date Founded:
		xLoop = self.X_RELIGION_START
		for iRel in self.leReligions:
			if (gc.getGame().getReligionGameTurnFounded(iRel) >= 0):
				szFounded = CyGameTextMgr().getTimeStr(gc.getGame().getReligionGameTurnFounded(iRel), false)
				screen.setLabelAt("", szArea, szFounded, CvUtil.FONT_CENTER_JUSTIFY, xLoop, self.Y_FOUNDED, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			xLoop += self.DX_RELIGION

#		screen.setLabelAt("", szArea, "", CvUtil.FONT_CENTER_JUSTIFY, xLoop, self.Y_FOUNDED, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		# Holy City...
		screen.setLabelAt("", szArea, localText.getText("TXT_KEY_RELIGION_SCREEN_HOLY_CITY", ()), CvUtil.FONT_LEFT_JUSTIFY, self.LEFT_EDGE_TEXT, self.Y_HOLY_CITY, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		xLoop = self.X_RELIGION_START
		for iRel in self.leReligions:
			if (gc.getGame().getReligionGameTurnFounded(iRel) >= 0):
				pHolyCity = gc.getGame().getHolyCity(iRel)
				if pHolyCity.isNone():
					szFounded = localText.getText("TXT_KEY_NONE", ())
					screen.setLabelAt("", szArea, szFounded, CvUtil.FONT_CENTER_JUSTIFY, xLoop, self.Y_HOLY_CITY, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				elif not pHolyCity.isRevealed(gc.getPlayer(self.iActivePlayer).getTeam(), False):
					szFounded = localText.getText("TXT_KEY_UNKNOWN", ())
					screen.setLabelAt("", szArea, szFounded, CvUtil.FONT_CENTER_JUSTIFY, xLoop, self.Y_HOLY_CITY, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				else:
					szFounded = pHolyCity.getName()
					screen.setLabelAt("", szArea, u"(%s)" % gc.getPlayer(pHolyCity.getOwner()).getCivilizationAdjective(0), CvUtil.FONT_CENTER_JUSTIFY, xLoop, self.Y_HOLY_CITY+8, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
					screen.setLabelAt("", szArea, szFounded, CvUtil.FONT_CENTER_JUSTIFY, xLoop, self.Y_HOLY_CITY-8, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
#			else:
#				szFounded = "-"
#				screen.setLabelAt("", szArea, szFounded, CvUtil.FONT_CENTER_JUSTIFY, xLoop, self.Y_HOLY_CITY, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			xLoop += self.DX_RELIGION

		# Influence...
		screen.setLabelAt("", szArea, localText.getText("TXT_KEY_RELIGION_SCREEN_INFLUENCE", ()), CvUtil.FONT_LEFT_JUSTIFY, self.LEFT_EDGE_TEXT, self.Y_INFLUENCE, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		xLoop = self.X_RELIGION_START
		for iRel in self.leReligions:
			if (gc.getGame().getReligionGameTurnFounded(iRel) >= 0):
				szFounded = str(gc.getGame().calculateReligionPercent(iRel)) + "%"
				screen.setLabelAt("", szArea, szFounded, CvUtil.FONT_CENTER_JUSTIFY, xLoop, self.Y_INFLUENCE, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
#			else:
#				szFounded = "-"
#				screen.setLabelAt("", szArea, szFounded, CvUtil.FONT_CENTER_JUSTIFY, xLoop, self.Y_INFLUENCE, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			xLoop += self.DX_RELIGION

		if AdvisorOpt.isReligious():
			# Count the number of temples and monastery
			self.BUGConstants()
			iPlayer = PyPlayer(self.iActivePlayer)
			cityList = iPlayer.getCityList()
# BUG - start
			iCities = [0] * self.NUM_RELIGIONS
			iTemple = [0] * self.NUM_RELIGIONS
#			iMonastery = [0] * self.NUM_RELIGIONS
			iMissionaries_Active = [0] * self.NUM_RELIGIONS
			iMissionaries_Construct = [0] * self.NUM_RELIGIONS
			
			for pLoopCity in cityList:
				lHolyCity = pLoopCity.getHolyCity()
				lReligions = pLoopCity.getReligions()

				for iRel in self.leReligions:
					# count the number of cities
					if iRel in lReligions:
						iCities[iRel] += 1

					# count the number of temples
					iBldg = ReligionUtil.getBuilding(iRel, ReligionUtil.BUILDING_TEMPLE)
					if self.calculateBuilding(pLoopCity, iBldg) == self.objectHave:
						iTemple[iRel] += 1

					# count the number of monasteries
					#iBldg = ReligionUtil.getBuilding(iRel, ReligionUtil.BUILDING_MONASTERY)
					#if self.calculateBuilding(pLoopCity, iBldg) == self.objectHave:
						#iMonastery[iRel] += 1

					# count the number of missionaries under construction
					iUnit = ReligionUtil.getUnit(iRel, ReligionUtil.UNIT_MISSIONARY)
					if pLoopCity.GetCy().getFirstUnitOrder(iUnit) != -1:
						iMissionaries_Construct[iRel] += 1

			# count the number of active missionaries
			for iUnit in PlayerUtil.playerUnits(self.iActivePlayer):  
				for iRel in self.leReligions:
					if iUnit.getUnitType() == ReligionUtil.getUnit(iRel, ReligionUtil.UNIT_MISSIONARY):
						iMissionaries_Active[iRel] += 1

			# number of cities...
			iY = self.Y_INFLUENCE + 20
			sCities = "%s [%i]:" % (self.szCities, len(cityList))
			screen.setLabelAt("", szArea, sCities, CvUtil.FONT_LEFT_JUSTIFY, self.LEFT_EDGE_TEXT, iY, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

			xLoop = self.X_RELIGION_START
			for iRel in self.leReligions:
				if (gc.getGame().getReligionGameTurnFounded(iRel) >= 0):
					szFounded = "%i" % (iCities[iRel])
					screen.setLabelAt("", szArea, szFounded, CvUtil.FONT_CENTER_JUSTIFY, xLoop, iY, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				xLoop += self.DX_RELIGION

			# number of temples...
			iY = self.Y_INFLUENCE + 40
			screen.setLabelAt("", szArea, self.szTemples, CvUtil.FONT_LEFT_JUSTIFY, self.LEFT_EDGE_TEXT, iY, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

			xLoop = self.X_RELIGION_START
			for iRel in self.leReligions:
				if (gc.getGame().getReligionGameTurnFounded(iRel) >= 0):
					szFounded = "%i" % (iTemple[iRel])
					screen.setLabelAt("", szArea, szFounded, CvUtil.FONT_CENTER_JUSTIFY, xLoop, iY, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				xLoop += self.DX_RELIGION

			# number of monasteries...
#			iY = self.Y_INFLUENCE + 60
#			screen.setLabelAt("", szArea, self.szMonastaries, CvUtil.FONT_LEFT_JUSTIFY, self.LEFT_EDGE_TEXT, iY, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

#			xLoop = self.X_RELIGION_START
#			for iRel in self.RELIGIONS:
#				if (gc.getGame().getReligionGameTurnFounded(iRel) >= 0):
#					szFounded = "%i" % (iMonastery[iRel])
#					screen.setLabelAt("", szArea, szFounded, CvUtil.FONT_CENTER_JUSTIFY, xLoop, iY, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
#				xLoop += self.DX_RELIGION

			# number of missionaries...
			iY = self.Y_INFLUENCE + 80
			screen.setLabelAt("", szArea, self.szMissionaries, CvUtil.FONT_LEFT_JUSTIFY, self.LEFT_EDGE_TEXT, iY, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

			xLoop = self.X_RELIGION_START
			for iRel in self.leReligions:
				if (gc.getGame().getReligionGameTurnFounded(iRel) >= 0):
					szFounded = "%i [%i]" % (iMissionaries_Active[iRel], iMissionaries_Construct[iRel])
					screen.setLabelAt("", szArea, szFounded, CvUtil.FONT_CENTER_JUSTIFY, xLoop, iY, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				xLoop += self.DX_RELIGION

		self.iReligionSelected = gc.getPlayer(self.iActivePlayer).getStateReligion()
		if (self.iReligionSelected == -1):
			self.iReligionSelected = gc.getNumReligionInfos()
		self.iReligionExamined = self.iReligionSelected
		self.iReligionOriginal = self.iReligionSelected

	# BUG constants
	def BUGConstants(self):

		if self.bBUGConstants:
			return

		self.bBUGConstants = True

		# BUG additions
		self.hammerIcon = u"%c" %(gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar())

		# Special symbols for building, wonder and project views
		self.objectIsPresent = "x"
		self.objectIsNotPresent = "-"
		self.objectCanBeBuild = "o"
		self.objectUnderConstruction = self.hammerIcon
		
		# add the colors dependant on the statuses
		self.objectHave = localText.changeTextColor (self.objectIsPresent, gc.getInfoTypeForString("COLOR_GREEN")) #"x"
		self.objectNotPossible = localText.changeTextColor (self.objectIsNotPresent, gc.getInfoTypeForString("COLOR_RED")) #"-"
		self.objectPossible = localText.changeTextColor (self.objectCanBeBuild, gc.getInfoTypeForString("COLOR_BLUE")) #"o"
		self.objectHaveObsolete = localText.changeTextColor (self.objectIsPresent, gc.getInfoTypeForString("COLOR_WHITE")) #"x"
		self.objectNotPossibleConcurrent = localText.changeTextColor (self.objectIsNotPresent, gc.getInfoTypeForString("COLOR_YELLOW")) #"-"
		self.objectPossibleConcurrent = localText.changeTextColor (self.objectCanBeBuild, gc.getInfoTypeForString("COLOR_YELLOW")) #"o"

		self.szCities = localText.getText("TXT_KEY_BUG_RELIGIOUS_CITY", ())
		self.szTemples = localText.getText("TXT_KEY_BUG_RELIGIOUS_TEMPLE", ())
#		self.szMonastaries = localText.getText("TXT_KEY_BUG_RELIGIOUS_MONASTARY", ())
		self.szMissionaries = localText.getText("TXT_KEY_BUG_RELIGIOUS_MISSIONARY", ())

		self.zoomArt = ArtFileMgr.getInterfaceArtInfo("INTERFACE_BUTTONS_CITYSELECTION").getPath()
		self.sCity = localText.getText("TXT_KEY_WONDER_CITY", ())

		# scroll offset
		if ReligionUtil.getNumReligions() > 7:
			self.H_SCROLL_OFFSET = 20
		else:
			self.H_SCROLL_OFFSET = 0


	# Draws the city list
	def drawCityInfo(self, iReligion):

		if (not self.bScreenUp):
			return

		screen = self.getScreen()

		if (iReligion == gc.getNumReligionInfos()):
			iLinkReligion = -1
		else:
			iLinkReligion = iReligion

		if AdvisorOpt.isReligious():
			screen.addPanel( self.AREA1_ID, "", "", True, True, self.xCityArea, self.yCityArea, self.wCityArea, self.hCityArea, PanelStyles.PANEL_STYLE_MAIN )
		else:
			screen.addPanel( self.AREA1_ID, "", "", True, True, self.xCityArea1, self.yCityArea, self.wCityAreaSplit, self.hCityArea, PanelStyles.PANEL_STYLE_MAIN )
			screen.addPanel( self.AREA2_ID, "", "", True, True, self.xCityArea2, self.yCityArea, self.wCityAreaSplit, self.hCityArea, PanelStyles.PANEL_STYLE_MAIN )

		szArea = self.RELIGION_PANEL_ID
		for iRel in self.leReligions:
			if (self.iReligionSelected == iRel):
				screen.setState(self.getReligionButtonName(iRel), True)
			else:
				screen.setState(self.getReligionButtonName(iRel), False)

		if (self.iReligionSelected == gc.getNumReligionInfos()):
			screen.setState(self.getReligionButtonName(gc.getNumReligionInfos()), True)
		else:
			screen.setState(self.getReligionButtonName(gc.getNumReligionInfos()), False)

		iPlayer = PyPlayer(self.iActivePlayer)
		cityList = iPlayer.getCityList()

# start of BUG indent for new code
		if AdvisorOpt.isReligious():
			# create religion table
			wTable = self.wCityArea - 2 * 15
			screen.addTableControlGFC( self.TABLE_ID, self.TABLE_COLUMNS, self.xCityArea + 15, self.yCityArea + 15,
					wTable, self.hCityArea - self.H_SCROLL_OFFSET - 5,  True, True, 24, 24,
					TableStyles.TABLE_STYLE_STANDARD )
			screen.enableSort(self.TABLE_ID)
			
			
			screen.setTableColumnHeader(self.TABLE_ID, self.COL_ZOOM_CITY, "", 30)
			screen.setTableColumnHeader(self.TABLE_ID, self.COL_CITY_NAME, self.sCity, 115)
			
			iTotalColWidth = 30 + 115

			for iRel in range(self.NUM_RELIGIONS):   # columns for religious icons
				if (gc.getGame().getReligionGameTurnFounded(iRel) >= 0):
					szReligionIcon = u"<font=2>%c</font>" %(gc.getReligionInfo(iRel).getChar())
					screen.setTableColumnHeader(self.TABLE_ID, self.COL_FIRST_RELIGION + iRel, szReligionIcon, 25)
					iTotalColWidth += 25

			# columns for units (missionaries)
			for type in ReligionUtil.getUnitTypes():
				screen.setTableColumnHeader(self.TABLE_ID, self.COL_FIRST_UNIT + type.index, u"<font=2>%s</font>" % type.icon, 30)
				iTotalColWidth += 30

			# columns for buildings (temples, monasteries, cathedral, shrine)
			for type in ReligionUtil.getBuildingTypes():
				screen.setTableColumnHeader(self.TABLE_ID, self.COL_FIRST_BUILDING + type.index, u"<font=2>%s</font>" % type.icon, 30)
				iTotalColWidth += 30

			# column for religious impact
			screen.setTableColumnHeader(self.TABLE_ID, self.COL_EFFECTS, "", max( 400, wTable - iTotalColWidth ) )
			
			# Loop through the cities
			for iCity in range(len(cityList)):
				pLoopCity = cityList[iCity]

				screen.appendTableRow(self.TABLE_ID)
				screen.setTableText(self.TABLE_ID, self.COL_ZOOM_CITY, iCity, "" , self.zoomArt, WidgetTypes.WIDGET_ZOOM_CITY, pLoopCity.getOwner(), pLoopCity.getID(), CvUtil.FONT_LEFT_JUSTIFY)
				screen.setTableText(self.TABLE_ID, self.COL_CITY_NAME, iCity, pLoopCity.getName(), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

				lHolyCity = pLoopCity.getHolyCity()
				lReligions = pLoopCity.getReligions()

				for iRel in range(self.NUM_RELIGIONS):
					if (gc.getGame().getReligionGameTurnFounded(iRel) >= 0):
						szReligionIcon = ""
						if iRel in lHolyCity:
							szReligionIcon = u"<font=2>%c</font>" %(gc.getReligionInfo(iRel).getHolyCityChar())
						elif iRel in lReligions:
							szReligionIcon = u"<font=2>%c</font>" %(gc.getReligionInfo(iRel).getChar())

						screen.setTableText(self.TABLE_ID, self.COL_FIRST_RELIGION + iRel, iCity, szReligionIcon, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)

				if ReligionUtil.isValid(iReligion):
					# check for missionaries
					for i in range(ReligionUtil.getNumUnitTypes()):
						iUnit = ReligionUtil.getUnit(iReligion, i)
						if pLoopCity.GetCy().getFirstUnitOrder(iUnit) != -1:
							sUnit = self.objectUnderConstruction
						elif pLoopCity.GetCy().canTrain(iUnit, False, False):
							sUnit = self.objectPossible
						else:
							sUnit = self.objectNotPossible
						screen.setTableText(self.TABLE_ID, self.COL_FIRST_UNIT + i, iCity, sUnit, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)
					
					# check for temples, cathedral, monasteries, shrine
					for i in range(ReligionUtil.getNumBuildingTypes()):
						iBldg = ReligionUtil.getBuilding(iReligion, i)
						sBldg = self.calculateBuilding(pLoopCity, iBldg)
						screen.setTableText(self.TABLE_ID, self.COL_FIRST_BUILDING + i, iCity, sBldg, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)

				if (iLinkReligion == -1):
					bFirst = True
					sHelp = ""
					for iI in range(len(lReligions)):
						szTempBuffer = CyGameTextMgr().getReligionHelpCity(lReligions[iI], pLoopCity.GetCy(), False, False, False, True)
						if (szTempBuffer):
							if (not bFirst):
								sHelp += u", "
							sHelp += szTempBuffer
							bFirst = False
				else:
					sHelp = CyGameTextMgr().getReligionHelpCity(iLinkReligion, pLoopCity.GetCy(), False, False, True, False)

				screen.setTableText(self.TABLE_ID, self.COL_EFFECTS, iCity, sHelp, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

# start of BUG indent of original code
		else:
			# Loop through the cities
			szLeftCities = u""
			szRightCities = u""
			for i in range(len(cityList)):

				bFirstColumn = (i % 2 == 0)

				pLoopCity = cityList[i]

				# Constructing the City name...
				szCityName = u""
				if pLoopCity.isCapital():
					szCityName += u"%c" % CyGame().getSymbolID(FontSymbols.STAR_CHAR)

				lHolyCity = pLoopCity.getHolyCity()
				if lHolyCity:
					for iI in range(len(lHolyCity)):
						szCityName += u"%c" %(gc.getReligionInfo(lHolyCity[iI]).getHolyCityChar())

				lReligions = pLoopCity.getReligions()
				if lReligions:
					for iI in range(len(lReligions)):
						if lReligions[iI] not in lHolyCity:
							szCityName += u"%c" %(gc.getReligionInfo(lReligions[iI]).getChar())

				szCityName += pLoopCity.getName()[0:17] + "  "

				#phungus Enlightened Start
				if (iLinkReligion == -1) or (gc.getPlayer(self.iActivePlayer).isNonStateReligionCommerce()):
					bFirst = True
					for iI in range(len(lReligions)):
						if (iLinkReligion > -1):
							if (lReligions[iI] == iLinkReligion):
								szTempBuffer = CyGameTextMgr().getReligionHelpCity(iLinkReligion, pLoopCity.GetCy(), False, False, True, False)
							else:
								szTempBuffer = CyGameTextMgr().getReligionHelpCity(lReligions[iI], pLoopCity.GetCy(), False, False, False, True)
						else:
							szTempBuffer = CyGameTextMgr().getReligionHelpCity(lReligions[iI], pLoopCity.GetCy(), False, False, False, True)
							if (szTempBuffer):
								if (not bFirst):
									szCityName += u", "
								szCityName += szTempBuffer
								bFirst = False
				else:
					szCityName += CyGameTextMgr().getReligionHelpCity(iLinkReligion, pLoopCity.GetCy(), False, False, True, False)
				#phungus Enlightened End

				if bFirstColumn:
					szLeftCities += u"<font=3>" + szCityName + u"</font>\n"
				else:
					szRightCities += u"<font=3>" + szCityName + u"</font>\n"

			screen.addMultilineText("Child" + self.AREA1_ID, szLeftCities, self.xCityArea1 + 5, self.yCityArea + 5, self.wCityAreaSplit - 10, self.hCityArea - 10, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
			screen.addMultilineText("Child" + self.AREA2_ID, szRightCities, self.xCityArea2 + 5, self.yCityArea + 5, self.wCityAreaSplit - 10, self.hCityArea - 10, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
# end of BUG indent of original code

		# Convert Button....
		iLink = 0
		if (gc.getPlayer(self.iActivePlayer).canChangeReligion()):
			iLink = 1

		if (not self.canConvert(iLinkReligion) or iLinkReligion == self.iReligionOriginal):			
			screen.setText( self.CONVERT_NAME, "Background", self.EXIT_TEXT, CvUtil.FONT_RIGHT_JUSTIFY, self.xExitButton, self.yExitButton, self.Z_TEXT, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, 1, 0 )
			screen.hide(self.CANCEL_NAME)
			szAnarchyTime = CyGameTextMgr().setConvertHelp(self.iActivePlayer, iLinkReligion)
		else:
			screen.setText( self.CONVERT_NAME, "Background", self.CONVERT_TEXT, CvUtil.FONT_RIGHT_JUSTIFY, self.xExitButton, self.yExitButton, self.Z_TEXT, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CONVERT, iLinkReligion, 1 )
			screen.show(self.CANCEL_NAME)
			szAnarchyTime = localText.getText("TXT_KEY_ANARCHY_TURNS", (gc.getPlayer(self.iActivePlayer).getReligionAnarchyLength(), ))

		# Turns of Anarchy Text...
		screen.setLabel( self.RELIGION_ANARCHY_WIDGET, "Background", u"<font=3>" + szAnarchyTime + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, self.xAnarchyText, self.yAnarchyText, self.Z_TEXT, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

	def getReligionButtonName(self, iReligion):
		szName = self.BUTTON_NAME + str(iReligion)
		return szName

	def getReligionTextName(self, iReligion):
		szName = self.RELIGION_NAME + str(iReligion)
		return szName

	def canConvert(self, iReligion):
		iCurrentReligion = gc.getPlayer(self.iActivePlayer).getStateReligion()
		if (iReligion == gc.getNumReligionInfos()):
			iConvertReligion = -1
		else:
			iConvertReligion = iReligion

		return (iConvertReligion != iCurrentReligion and gc.getPlayer(self.iActivePlayer).canConvert(iConvertReligion))		

	# Will handle the input for this screen...
	def handleInput (self, inputClass):
#		BugUtil.debugInput(inputClass)

		screen = self.getScreen()

		szWidgetName = inputClass.getFunctionName()
		szFullWidgetName = szWidgetName + str(inputClass.getID())
		code = inputClass.getNotifyCode()

		if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_LISTBOX_ITEM_SELECTED
		and szWidgetName != self.TABLE_ID):
			screen = self.getScreen()
			iIndex = screen.getSelectedPullDownID(self.DEBUG_DROPDOWN_ID)
			self.iActivePlayer = screen.getPullDownData(self.DEBUG_DROPDOWN_ID, iIndex)
			self.drawReligionInfo()
			self.drawCityInfo(self.iReligionSelected)
			return 1

		# BUG Zoom to City
		elif (szWidgetName == self.TABLE_ID):
			if (inputClass.getMouseX() == 0):
				screen.hideScreen()
				pPlayer = gc.getPlayer(inputClass.getData1())
				pCity = pPlayer.getCity(inputClass.getData2())
#				CyCamera().JustLookAtPlot(pCity.plot())

				CyInterface().selectCity(pCity, true);

		elif (self.ReligionScreenInputMap.has_key(inputClass.getFunctionName())):
			'Calls function mapped in ReligionScreenInputMap'
			# only get from the map if it has the key

			# get bound function from map and call it
			self.ReligionScreenInputMap.get(inputClass.getFunctionName())(inputClass)
			return 1

		return 0

	def update(self, fDelta):
		return

	# Religion Button
	def ReligionScreenButton( self, inputClass ):	
		if ( inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED ) :
			if (inputClass.getID() == gc.getNumReligionInfos() or gc.getGame().getReligionGameTurnFounded(inputClass.getID()) >= 0) :

#FfH: Added by Kael 12/29/2006
				py = PyPlayer(self.iActivePlayer)
				for pUnit in py.getUnitList():
					if gc.getUnitInfo(pUnit.getUnitType()).isAbandon():
						if gc.getUnitInfo(pUnit.getUnitType()).getStateReligion() == self.iReligionSelected:
							cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_RELIGION_ABANDON_WARN",()), 'art/interface/popups/Abandon.dds')
#FfH: End Add

				self.iReligionSelected = inputClass.getID()
				self.iReligionExamined = self.iReligionSelected
				self.drawCityInfo(self.iReligionSelected)
		elif ( inputClass.getNotifyCode() == NotifyCode.NOTIFY_CURSOR_MOVE_ON ) :
			if ( inputClass.getID() == gc.getNumReligionInfos() or gc.getGame().getReligionGameTurnFounded(inputClass.getID()) >= 0) :
				self.iReligionExamined = inputClass.getID()
				self.drawCityInfo(self.iReligionExamined)
		elif ( inputClass.getNotifyCode() == NotifyCode.NOTIFY_CURSOR_MOVE_OFF ) :
			self.iReligionExamined = self.iReligionSelected
			self.drawCityInfo(self.iReligionSelected)
		return 0

	def ReligionConvert(self, inputClass):
		screen = self.getScreen()
		if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED) :
			screen.hideScreen()
		
	def ReligionCancel(self, inputClass):
		screen = self.getScreen()
		if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED) :
			self.iReligionSelected = self.iReligionOriginal
			if (-1 == self.iReligionSelected):
				self.iReligionSelected = gc.getNumReligionInfos()
			self.drawCityInfo(self.iReligionSelected)

	def calculateBuilding (self, city, bldg):
		if (bldg == BuildingTypes.NO_BUILDING):
			return self.objectNotPossible
			
		if city.getNumBuilding(bldg) > 0:
			return self.objectHave
#			if city.getNumActiveBuilding(bldg) > 0:
#				return self.objectHave
#			else:
#				return self.objectHaveObsolete
		elif city.GetCy().getFirstBuildingOrder(bldg) != -1:
			return self.objectUnderConstruction
		elif city.GetCy().canConstruct(bldg, False, False, False):
			return self.objectPossible
		elif city.GetCy().canConstruct(bldg, True, False, False):
			return self.objectPossibleConcurrent
		else:
			return self.objectNotPossible

