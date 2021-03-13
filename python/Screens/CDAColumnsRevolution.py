"""
Columns for CvCustomizableDomesticAdvisor

CDA_REFACTOR 03/2021 lfgr
"""

from CvPythonExtensions import *
import FontUtil

from CDAColumns import CDAColumn
from RevIdxUtils import CityRevIdxHelper

gc = CyGlobalContext()
localText = CyTranslator()


def coloredRevIdxFactorStr( iRevIdx ) :
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
		sRevIdx = ("%+d" % iRevIdx)  # Show + or minus sign
	else :
		sRevIdx = str( iRevIdx )
	return sColor + sRevIdx


class RevolutionCDAColumn( CDAColumn ) :
	def is_valid( self, pPlayer ) :
		return CyGame().isOption( GameOptionTypes.GAMEOPTION_REVOLUTIONS )


class RevIdxCityHelperCombinedCDAColumn( RevolutionCDAColumn ) : # TODO: type: int
	def __init__( self, szName, iDefaultWidth, szTitle, cityHelperRevIdxAndHelpFunc ) :
		super( RevIdxCityHelperCombinedCDAColumn, self ).__init__( szName, iDefaultWidth, szTitle )
		self._cityHelperRevIdxAndHelpFunc = cityHelperRevIdxAndHelpFunc

	def compute_value_and_tooltip( self, pCity ) :
		helper = CityRevIdxHelper( pCity )
		value, tooltip = self._cityHelperRevIdxAndHelpFunc( helper )
		return coloredRevIdxFactorStr( value ), tooltip


class RevIdxCityHelperCDAColumn( RevolutionCDAColumn ) :
	def __init__( self, szName, iDefaultWidth, szTitle, cityHelperRevIdxFunc, cityHelperRevIdxHelpFunc ) :
		super( RevIdxCityHelperCDAColumn, self ).__init__( szName, iDefaultWidth, szTitle )
		self._cityHelperRevIdxFunc = cityHelperRevIdxFunc
		self._cityHelperRevIdxHelpFunc = cityHelperRevIdxHelpFunc

	def compute_value_and_tooltip( self, pCity ) :
		helper = CityRevIdxHelper( pCity )
		value = self._cityHelperRevIdxFunc( helper )
		tooltip = self._cityHelperRevIdxHelpFunc( helper )
		return coloredRevIdxFactorStr( value ), tooltip


class RevIdxPerTurnCDAColumn( RevolutionCDAColumn ) :
	def __init__( self ) :
		super( RevIdxPerTurnCDAColumn, self ).__init__( "REV_PER_TURN", 55,
				localText.getText( "Rev/T", () ) ) # TODO: Translate

	def compute_value( self, pCity ) :
		return "?" # LFGR_TODO


class RevIdxTotalCDAColumn( RevolutionCDAColumn ) :
	def __init__( self ) :
		super( RevIdxTotalCDAColumn, self ).__init__( "REV_TOTAL", 55,
				localText.getText( "Rev", () ) ) # TODO: Translate

	def compute_value( self, pCity ) :
		return unicode( pCity.getRevolutionIndex() )


def makeColumns() :
	# type: () -> Sequence[CDAColumn]
	return (
		RevIdxPerTurnCDAColumn(),
		RevIdxTotalCDAColumn(),
		RevIdxCityHelperCombinedCDAColumn( "REV_HAPPINESS", 46,
				u"<font=2>%s/%s</font>" % ( FontUtil.getChar( "happy" ), FontUtil.getChar( "unhappy" ) ),
				CityRevIdxHelper.computeHappinessRevIdxAndHelp ),

		RevIdxCityHelperCDAColumn( "REV_LOCATION", 40, u"<font=2>%s</font>" % FontUtil.getChar( "map" ),
				CityRevIdxHelper.computeLocationRevIdx, CityRevIdxHelper.computeLocationRevIdxHelp ),

		RevIdxCityHelperCDAColumn( "REV_CONNECTION", 40, u"<font=2>%s</font>" % FontUtil.getChar( "trade" ),
			CityRevIdxHelper.computeConnectionRevIdx, CityRevIdxHelper.computeConnectionRevIdxHelp ),

		RevIdxCityHelperCDAColumn( "REV_HC_OWNERSHIP", 42,
				u"<font=2>%s%s</font>" % (FontUtil.getChar( "religion" ), FontUtil.getChar( "star" ) ),
				CityRevIdxHelper.computeHolyCityOwnershipRevIdx, CityRevIdxHelper.computeHolyCityOwnershipRevIdxHelp ),

		RevIdxCityHelperCDAColumn( "REV_RELIGION", 40, u"<font=2>%s</font>" % FontUtil.getChar( "religion" ),
				CityRevIdxHelper.computeReligionRevIdx, CityRevIdxHelper.computeReligionRevIdxHelp ),

		RevIdxCityHelperCombinedCDAColumn( "REV_CULTURE", 40, u"<font=2>%s</font>" % FontUtil.getChar( "commerce culture" ),
				CityRevIdxHelper.computeCultureRevIdxAndHelp ),

		RevIdxCityHelperCombinedCDAColumn( "REV_NATIONALITY", 42,
				u"<font=2>%s%s</font>" % ( FontUtil.getChar( "commerce culture" ), FontUtil.getChar( "power" ) ),
			   CityRevIdxHelper.computeNationalityRevIdxAndHelp ),

		RevIdxCityHelperCombinedCDAColumn( "REV_HEALTH", 40, u"<font=2>%s</font>" % FontUtil.getChar( "healthy" ),
				CityRevIdxHelper.computeHealthRevIdxAndHelp ),

		RevIdxCityHelperCombinedCDAColumn( "REV_GARRISON", 40, u"<font=2>%s</font>" % FontUtil.getChar( "power" ),
				CityRevIdxHelper.computeGarrisonRevIdxAndHelp ),

		RevIdxCityHelperCombinedCDAColumn( "REV_SIZE", 40, u"<font=2>%s</font>" % FontUtil.getChar( "war" ),
				CityRevIdxHelper.computeSizeRevIdxAndHelp ),

		RevIdxCityHelperCombinedCDAColumn( "REV_STARVATION", 40, u"<font=2>%s</font>" % FontUtil.getChar( "badfood" ),
				CityRevIdxHelper.computeStarvingRevIdxAndHelp ),

		RevIdxCityHelperCombinedCDAColumn( "REV_DISORDER", 40, u"<font=2>%s</font>" % FontUtil.getChar( "occupation" ),
				CityRevIdxHelper.computeDisorderRevIdxAndHelp ),

		RevIdxCityHelperCombinedCDAColumn( "REV_CRIME", 50, u"<font=2>%s</font>" % FontUtil.getChar( "badgold" ),
				CityRevIdxHelper.computeCrimeRevIdxAndHelp )
	)



