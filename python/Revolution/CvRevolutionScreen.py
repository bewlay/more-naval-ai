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

# Configuration and constants

class RevIdxColConfig :
	def __init__( self, revIdxFunc, revIdxHelpFunc, sColHeader ) :
		self._revIdxFunc = revIdxFunc
		self._revIdxHelpFunc = revIdxHelpFunc
		self.sColHeader = sColHeader

	def getIdx( self, pCityHelper ) :
		# type: (RevIdxUtils.CityRevIdxHelper) -> int
		return self._revIdxFunc( pCityHelper)

	def getHelp( self, pCityHelper ) :
		# type: (RevIdxUtils.CityRevIdxHelper) -> unicode
		if self._revIdxHelpFunc is None :
			return u""
		return self._revIdxHelpFunc( pCityHelper )

class RevIdxCombinedColConfig :
	def __init__( self, revIdxAndHelpFunc, sColHeader ) :
		self._revIdxAndHelpFunc = revIdxAndHelpFunc
		self.sColHeader = sColHeader

	def getIdx( self, pCityHelper ) :
		# type: (RevIdxUtils.CityRevIdxHelper) -> int
		return self._revIdxAndHelpFunc( pCityHelper )[0]

	def getHelp( self, pCityHelper ) :
		# type: (RevIdxUtils.CityRevIdxHelper) -> unicode
		return self._revIdxAndHelpFunc( pCityHelper )[1]

# Tuples of CityRevIdxHelper function and column header text
REV_IDX_COLUMNS_CONFIG = (
	RevIdxCombinedColConfig( RevIdxUtils.CityRevIdxHelper.computeHappinessRevIdxAndHelp,
			u"<font=2>%s/%s</font>" % (FontUtil.getChar( "happy" ), FontUtil.getChar( "unhappy" )) ),
	
	RevIdxColConfig( RevIdxUtils.CityRevIdxHelper.computeLocationRevIdx,
			RevIdxUtils.CityRevIdxHelper.computeLocationRevIdxHelp,
			u"<font=2>%s</font>" % FontUtil.getChar( "map" ) ),
	
	RevIdxColConfig( RevIdxUtils.CityRevIdxHelper.computeConnectionRevIdx,
			RevIdxUtils.CityRevIdxHelper.computeConnectionRevIdxHelp,
			u"<font=2>%s</font>" % FontUtil.getChar( "trade" ) ),
	
	RevIdxColConfig( RevIdxUtils.CityRevIdxHelper.computeHolyCityOwnershipRevIdx,
			RevIdxUtils.CityRevIdxHelper.computeHolyCityOwnershipRevIdxHelp,
			u"<font=2>%s%s</font>" % ( FontUtil.getChar( "religion" ), FontUtil.getChar( "star" ) ) ),
	
	RevIdxColConfig( RevIdxUtils.CityRevIdxHelper.computeReligionRevIdx,
			RevIdxUtils.CityRevIdxHelper.computeReligionRevIdxHelp,
			u"<font=2>%s</font>" % FontUtil.getChar( "religion" ) ),
	
	RevIdxCombinedColConfig( RevIdxUtils.CityRevIdxHelper.computeCultureRevIdxAndHelp,
			u"<font=2>%s</font>" % FontUtil.getChar( "commerce culture" ) ),
	
	RevIdxCombinedColConfig( RevIdxUtils.CityRevIdxHelper.computeNationalityRevIdxAndHelp,
			u"<font=2>%s%s</font>" % ( FontUtil.getChar( "commerce culture" ), FontUtil.getChar( "power" ) ) ),
	
	RevIdxCombinedColConfig( RevIdxUtils.CityRevIdxHelper.computeHealthRevIdxAndHelp,
			u"<font=2>%s</font>" % FontUtil.getChar( "healthy" ) ),
	
	RevIdxCombinedColConfig( RevIdxUtils.CityRevIdxHelper.computeGarrisonRevIdxAndHelp,
			u"<font=2>%s</font>" % FontUtil.getChar( "power" ) ),
	
	RevIdxCombinedColConfig( RevIdxUtils.CityRevIdxHelper.computeSizeRevIdxAndHelp,
			u"<font=2>%s</font>" % FontUtil.getChar( "war" ) ),
	
	RevIdxCombinedColConfig( RevIdxUtils.CityRevIdxHelper.computeStarvingRevIdxAndHelp,
			u"<font=2>%s</font>" % FontUtil.getChar( "badfood" ) ),
	
	RevIdxCombinedColConfig( RevIdxUtils.CityRevIdxHelper.computeDisorderRevIdxAndHelp,
			u"<font=2>%s</font>" % FontUtil.getChar( "occupation" ) ),
	
	RevIdxCombinedColConfig( RevIdxUtils.CityRevIdxHelper.computeCrimeRevIdxAndHelp,
			u"<font=2>%s</font>" % FontUtil.getChar( "badgold" ) )
)

COL_ZOOM_CITY = 0
COL_CITY_NAME = 1
REV_IDX_COL_OFFSET = 2
COL_CURRENT_REV_IDX = REV_IDX_COL_OFFSET + len( REV_IDX_COLUMNS_CONFIG )
NUM_TABLE_COLUMNS = COL_CURRENT_REV_IDX + 1



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
	
	if REV_IDX_COL_OFFSET <= iData1 < REV_IDX_COL_OFFSET + len( REV_IDX_COLUMNS_CONFIG ) :
		return REV_IDX_COLUMNS_CONFIG[iData1-REV_IDX_COL_OFFSET].getHelp( RevIdxUtils.CityRevIdxHelper( pCity ) )

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

		if iRevIdx != 0 :
			sRevIdx = ( "%+d" % iRevIdx ) # Show + or minus sign
		else :
			sRevIdx = str( iRevIdx )
		return sColor + sRevIdx
	
	
	def makeCityTable( self ) :
		screen = self.getScreen()
		
		wZoomCityCol = 30
		wCityNameCol = 115
		wRevIdxCol = 50
		wTotalRevIdxCol = 60
		
		self.wTable = wZoomCityCol + wCityNameCol + len( REV_IDX_COLUMNS_CONFIG ) * wRevIdxCol + wTotalRevIdxCol
		
		self.wLeftSpace = 200 # For the tooltip
		
		self.xCityPanel = self.wLeftSpace + self.MARGIN # TODO?
		self.yCityPanel = self.yMainArea + self.MARGIN
		self.wCityPanel = self.wTable + 2 * self.TABLE_X_MARGIN #self.wScreen - 2 * self.MARGIN - self.wLeftSpace
		self.hCityPanel = self.hMainArea - 2 * self.MARGIN
		
		screen.addPanel( self.CITY_PANEL_ID, "", "", False, True,
				self.xCityPanel, self.yCityPanel, self.wCityPanel, self.hCityPanel, PanelStyles.PANEL_STYLE_MAIN )
		
		screen.addTableControlGFC( self.CITY_TABLE_ID, NUM_TABLE_COLUMNS,
				self.xCityPanel + self.TABLE_X_MARGIN, self.yCityPanel + self.TABLE_Y_MARGIN,
				self.wTable, self.hCityPanel - 2*self.TABLE_Y_MARGIN,
				True, True, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		
		screen.setTableColumnHeader( self.CITY_TABLE_ID, COL_ZOOM_CITY, "", wZoomCityCol )
		screen.setTableColumnHeader( self.CITY_TABLE_ID, COL_CITY_NAME,
				localText.getText("TXT_KEY_WONDER_CITY", ()), wCityNameCol )
		for idx, colConfig in enumerate( REV_IDX_COLUMNS_CONFIG ) :
			iCol = idx + REV_IDX_COL_OFFSET
			screen.setTableColumnHeader( self.CITY_TABLE_ID, iCol, colConfig.sColHeader, wRevIdxCol )
		
		screen.setTableColumnHeader( self.CITY_TABLE_ID, COL_CURRENT_REV_IDX, "<font=2>Total</font>", wTotalRevIdxCol )
		
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
			screen.setTableText( self.CITY_TABLE_ID, COL_CURRENT_REV_IDX, iRow, str( pyCity.getRevolutionIndex() ), "",
					WidgetTypes.WIDGET_PYTHON, iRevScreenCode + COL_CURRENT_REV_IDX, iCityCode, CvUtil.FONT_LEFT_JUSTIFY )
			
			for idx, colConfig in enumerate( REV_IDX_COLUMNS_CONFIG ) :
				iCol = idx + REV_IDX_COL_OFFSET
				sText = self.coloredRevIdxFactorStr( colConfig.getIdx( pCityHelper ) )
				self.getScreen().setTableText( self.CITY_TABLE_ID, iCol, iRow, sText, "",
						WidgetTypes.WIDGET_PYTHON, iRevScreenCode + iCol, iCityCode, CvUtil.FONT_RIGHT_JUSTIFY )
			
	def update(self, fDelta):
		pass # Nothing to do
	
	def isVisible( self ) :
		return False # TODO
	
	def handleInput( self, inputClass ) :
		pass # TODO?
