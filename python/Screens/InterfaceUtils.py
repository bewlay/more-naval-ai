# lfgr 09/2019
from CvPythonExtensions import *

import BugCore
import CvUtil


BugOpt = BugCore.game.Advisors
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()


def updateMinimap( *args ) :
	"""
	Re-draws the minimap
	"""
	CyMap().updateMinimapColor()


def font( font, text ) :
	return u"<font=%s>%s</font>" % ( font, text )


def makeTableColWidths( wTotal, lfWeights ) :
	wTotal -= 5 * ( len( lfWeights ) - 1 ) # Column separators (?)
	fTotalWeight = sum( lfWeights )
	
	wUsed = 0
	for fWeight in lfWeights[:-1] :
		wCol = int( wTotal * fWeight / fTotalWeight )
		wUsed += wCol
		yield wCol
	
	yield wTotal - wUsed # Last column

def setTableColHeaders( screen, szTable, wTable, lfWeights, lszHeaders = None ) :
	if lszHeaders is None :
		lszHeaders = [""] * len( lfWeights )
	for i, wCol in enumerate( makeTableColWidths( wTable, lfWeights ) ) :
		screen.setTableColumnHeader( szTable, i, lszHeaders[i], wCol )
	


def addTableRow( screen, szTable, lszCellText, leCellAlignments = None ) :
	iRow = screen.appendTableRow( szTable )
	
	if isinstance( lszCellText, str ) or isinstance( lszCellText, unicode ) : # Allow lszCellText to be a single string
		lszCellText = [lszCellText]
	
	if leCellAlignments is None : # Everything left-aligned by default
		leCellAlignments = [CvUtil.FONT_LEFT_JUSTIFY] * len( lszCellText )
	
	for iCol, szText in enumerate( lszCellText ) :
		screen.setTableText( szTable, iCol, iRow, szText, "", WidgetTypes.WIDGET_GENERAL, -1, -1,
				leCellAlignments[iCol] )

# lfgr 09/2019: Full-screen Advisors
class GenericAdvisorScreen( object ) :
	"""
	Generic Advisor screen class with with helper functions, in particular for full-screen advisors.
	"""
	
	EXIT_ID = "Exit"
	
	def getScreen( self ) :
		raise NotImplementedError( "Subclasses of GenericAdvisor must implement getScreen()" )
	
	def initDimensions( self ) :
		screen = self.getScreen()
		
		if (BugOpt.isFullScreenAdvisors() and screen.getXResolution() > 1024):
			self.xPanelWidth = max( 1024, screen.getXResolution() )
			self.yPanelHeight = max( 768, screen.getYResolution() )
			screen.setDimensions(0, 0, self.xPanelWidth, self.yPanelHeight)
		else:
			self.xPanelWidth = 1024
			self.yPanelHeight = 768
			screen.setDimensions( screen.centerX(0), screen.centerY(0),
					self.xPanelWidth, self.yPanelHeight)
		
		return self.xPanelWidth, self.yPanelHeight # For convenience
	
	def addBackgroundHeaderFooter( self, szHeaderText ) :
		xPanelWidth, yPanelHeight = self.xPanelWidth, self.yPanelHeight
		screen = self.getScreen()
		
		# Background
		screen.addDDSGFC("BackgroundPicture",
				ArtFileMgr.getInterfaceArtInfo("SCREEN_BG_OPAQUE").getPath(),
				0, 0, xPanelWidth, yPanelHeight, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		
		# Header
		screen.addPanel( "TopPanel", u"", u"", True, False, 0, 0, xPanelWidth, 55,
				PanelStyles.PANEL_STYLE_TOPBAR )
		screen.setLabel( "TitleHeader", "Background", u"<font=4>" + szHeaderText + u"</font>",
				CvUtil.FONT_CENTER_JUSTIFY, xPanelWidth / 2, 8, 0, FontTypes.TITLE_FONT,
				WidgetTypes.WIDGET_GENERAL, -1, -1 )
		
		# Footer
		screen.addPanel( "BottomPanel", u"", u"", True, False, 0, yPanelHeight - 55,
				xPanelWidth, 55, PanelStyles.PANEL_STYLE_BOTTOMBAR )
	
	def addExitButton( self ) :
		xPanelWidth, yPanelHeight = self.xPanelWidth, self.yPanelHeight
		screen = self.getScreen()
		
		szExitText = CyTranslator().getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper()
		screen.setText( self.EXIT_ID, "Background", u"<font=4>" + szExitText + "</font>",
				CvUtil.FONT_RIGHT_JUSTIFY, xPanelWidth - 30, yPanelHeight - 42, 0,
				FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )
		screen.setActivation( self.EXIT_ID, ActivationTypes.ACTIVATE_MIMICPARENTFOCUS )

