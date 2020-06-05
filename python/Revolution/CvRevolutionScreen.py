# CvRevolutionScreen
# lfgr 05/2020

from CvPythonExtensions import *
import PyHelpers
import CvUtil
import CvScreenEnums
import PythonWidgetHelp

import BugCore
import FontUtil
AdvisorOpt = BugCore.game.Advisors

import RevIdxUtils

# lfgr 05/2020: Full-screen Advisors: refactored, added full-screen support
from InterfaceUtils import GenericAdvisorScreen

PyPlayer = PyHelpers.PyPlayer

# globals
gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

# Constants
NUM_TABLE_COLUMNS = 3
COL_ZOOM_CITY, \
COL_CITY_NAME, \
COL_HAPPINESS = range( NUM_TABLE_COLUMNS )



# Widget help text functions

def encodeCity( pCity ) :
	return pCity.getID() * gc.getMAX_PLAYERS() + pCity.getOwner()

def decodeCity( iData ) :
	eOwner = iData % gc.getMAX_PLAYERS()
	eCity = iData // gc.getMAX_PLAYERS()
	return gc.getPlayer( eOwner ).getCity( eCity )


# Help text
def getHelp( iData1, iData2 ) :
	# type: (int, int) -> unicode
	pCity = decodeCity( iData2 )
	if iData1 == COL_CITY_NAME :
		return u"" # TODO
	elif iData1 == COL_HAPPINESS :
		return RevIdxUtils.CityRevIdxHelper( pCity ).computeHappinessRevIdxHelp()

	return u""


class CvRevolutionScreen( GenericAdvisorScreen ) :
	def __init__( self ) :
		self.SCREEN_NAME = "RevolutionScreen"
		self.CITY_PANEL_ID = "CityPanel"
		self.CITY_TABLE_ID = "CityTable"
		
		self.MARGIN = 20
		self.TABLE_X_MARGIN = 15
		self.TABLE_Y_MARGIN = 15
		
		self.ZOOM_ART = ArtFileMgr.getInterfaceArtInfo( "INTERFACE_BUTTONS_CITYSELECTION" ).getPath()
	
	def getScreen( self ) :
		return CyGInterfaceScreen( self.SCREEN_NAME, CvScreenEnums.REVOLUTION_WATCH_ADVISOR )
	
	def interfaceScreen( self ) :
		self.eActivePlayer = gc.getGame().getActivePlayer() # TODO?
		
		screen = self.getScreen()
		if screen.isActive():
			return
		#screen.setRenderInterfaceOnly(True) # TODO: What does this mean?
		screen.showScreen( PopupStates.POPUPSTATE_IMMEDIATE, False)
		
		# Setup dimensions
		self.initDimensions()
		
		# Standard stuff
		self.addBackgroundHeaderFooter( localText.getText( "TXT_KEY_REVOLUTION_SCREEN", () ).upper() )
		self.addExitButton()
		
		self.makeCityTable()
	
	
	def coloredRevIdxFactorStr( self, iRevIdx ) :
		""" Color a single factor with green to red """
		if iRevIdx < -10 :
			sColor = "<color=20,230,20,255>"
		elif iRevIdx < -5 :
			sColor = "<color=50,230,50,255>"
		elif iRevIdx < -2 :
			sColor = "<color=100,230,100,255>"
		elif iRevIdx < 0 :
			sColor = "<color=150,230,150,255>"
		elif iRevIdx == 0 :
			sColor = ""
		elif iRevIdx <= 2 :
			sColor = "<color=225,150,150,255>"
		elif iRevIdx <= 5 :
			sColor = "<color=225,100,100,255>"
		elif iRevIdx <= 10 :
			sColor = "<color=225,75,75,255>"
		elif iRevIdx <= 20 :
			sColor = "<color=225,50,50,255>"
		else :
			sColor = "<color=255,10,10,255>"
			
		return sColor + ( "%+d" % iRevIdx ) # Show + or minus sign
	
	
	def makeCityTable( self ) :
		screen = self.getScreen()
		
		self.xCityPanel = self.MARGIN + 400
		self.yCityPanel = self.yMainArea + self.MARGIN
		self.wCityPanel = self.wScreen - 2 * self.MARGIN - 400
		self.hCityPanel = self.hMainArea - 2 * self.MARGIN
		
		screen.addPanel( self.CITY_PANEL_ID, "", "", False, True,
				self.xCityPanel, self.yCityPanel, self.wCityPanel, self.hCityPanel, PanelStyles.PANEL_STYLE_MAIN )
		
		screen.addTableControlGFC( self.CITY_TABLE_ID, NUM_TABLE_COLUMNS,
				self.xCityPanel + self.TABLE_X_MARGIN, self.yCityPanel + self.TABLE_Y_MARGIN,
				self.wCityPanel - 2*self.TABLE_X_MARGIN, self.hCityPanel - 2*self.TABLE_Y_MARGIN,
				True, True, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		
		screen.setTableColumnHeader( self.CITY_TABLE_ID, COL_ZOOM_CITY, "", 30 )
		screen.setTableColumnHeader( self.CITY_TABLE_ID, COL_CITY_NAME,
				localText.getText("TXT_KEY_WONDER_CITY", ()), 115 )
		screen.setTableColumnHeader( self.CITY_TABLE_ID, COL_HAPPINESS,
				u"<font=2>%s/%s</font>" % (FontUtil.getChar( "happy" ), FontUtil.getChar( "unhappy" )), 50 )
		
		#screen.setToolTipAlignment( self.CITY_PANEL_ID, ToolTipAlignTypes.TOOLTIP_BOTTOM_LEFT )
		
		for pyCity in PyPlayer( self.eActivePlayer ).iterCities() :
			pCityHelper = RevIdxUtils.CityRevIdxHelper( pyCity.GetCy() )

			# For widget help data
			iCityCode = encodeCity( pyCity )
			iRevScreenCode = PythonWidgetHelp.WIDGET_HELP_CLASS_REVOLUTION_SCREEN * 1000

			iRow = screen.appendTableRow( self.CITY_TABLE_ID )

			# Zoom, city name
			screen.setTableText( self.CITY_TABLE_ID, COL_ZOOM_CITY, iRow, "", self.ZOOM_ART,
					WidgetTypes.WIDGET_ZOOM_CITY, pyCity.getOwner(), pyCity.getID(), CvUtil.FONT_LEFT_JUSTIFY )
			screen.setTableText( self.CITY_TABLE_ID, COL_CITY_NAME, iRow, pyCity.getName(), "",
					WidgetTypes.WIDGET_PYTHON, iRevScreenCode + COL_CITY_NAME, iCityCode, CvUtil.FONT_LEFT_JUSTIFY )

			# Happiness
			sHappiness = self.coloredRevIdxFactorStr( pCityHelper.computeHappinessRevIdx() )
			screen.setTableText( self.CITY_TABLE_ID, COL_HAPPINESS, iRow, sHappiness, "",
					WidgetTypes.WIDGET_PYTHON, iRevScreenCode + COL_HAPPINESS, iCityCode, CvUtil.FONT_LEFT_JUSTIFY )
	
	def update(self, fDelta):
		pass # Nothing to do
	
	def isVisible( self ) :
		return False # TODO
	
	def handleInput( self, inputClass ) :
		pass # TODO?
