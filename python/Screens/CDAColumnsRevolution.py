"""
Columns for CvCustomizableDomesticAdvisor

CDA_REFACTOR 03/2021 lfgr
"""

from CvPythonExtensions import *
from PyHelpers import getText
import FontUtil

from CDAColumns import CDAColumn
from RevIdxUtils import CityRevIdxHelper, coloredRevIdxFactorStr

artFileMgr = CyArtFileMgr()
gc = CyGlobalContext()
localText = CyTranslator()


class RevolutionCDAColumn( CDAColumn ) :
	def is_valid( self, pPlayer ) :
		return CyGame().isOption( GameOptionTypes.GAMEOPTION_REVOLUTIONS )


class RevIdxCityHelperCombinedCDAColumn( RevolutionCDAColumn ) :
	def __init__( self, szName, iDefaultWidth, szTitle, cityHelperRevIdxAndHelpFunc ) :
		# type: (str, int, unicode, Callable[[CityRevIdxHelper], Tuple[int, unicode]]) -> None
		super( RevIdxCityHelperCombinedCDAColumn, self ).__init__( szName, iDefaultWidth, szTitle )
		self._cityHelperRevIdxAndHelpFunc = cityHelperRevIdxAndHelpFunc

	def compute_value_and_tooltip( self, pCity, pCityHelper = None, **kwargs ) :
		assert pCityHelper is not None
		value, tooltip = self._cityHelperRevIdxAndHelpFunc( pCityHelper )
		return coloredRevIdxFactorStr( value ), tooltip

	@property
	def type( self ) :
		return "int"


class RevIdxCityHelperCDAColumn( RevolutionCDAColumn ) :
	def __init__( self, szName, iDefaultWidth, szTitle, cityHelperRevIdxFunc, cityHelperRevIdxHelpFunc ) :
		# type: (str, int, unicode, Callable[[CityRevIdxHelper], int], Callable[[CityRevIdxHelper], unicode]) -> None
		super( RevIdxCityHelperCDAColumn, self ).__init__( szName, iDefaultWidth, szTitle )
		self._cityHelperRevIdxFunc = cityHelperRevIdxFunc
		self._cityHelperRevIdxHelpFunc = cityHelperRevIdxHelpFunc

	def compute_value_and_tooltip( self, pCity, pCityHelper = None, **kwargs ) :
		assert pCityHelper is not None
		value = self._cityHelperRevIdxFunc( pCityHelper )
		tooltip = self._cityHelperRevIdxHelpFunc( pCityHelper )
		return coloredRevIdxFactorStr( value ), tooltip

	@property
	def type( self ) :
		return "int"


class RevIdxTotalCDAColumn( RevolutionCDAColumn ) :
	def __init__( self ) :
		super( RevIdxTotalCDAColumn, self ).__init__( "REV_TOTAL", 55, getText( "TXT_KEY_CDA_COLUMN_REV_IDX" ) )

	def compute_value_and_tooltip( self, pCity, **kwargs ) :
		return unicode( pCity.getRevolutionIndex() ), u""

	@property
	def type( self ) :
		return "int"


def makeColumns() :
	# type: () -> Sequence[CDAColumn]
	return (
		RevIdxTotalCDAColumn(),
		RevIdxCityHelperCombinedCDAColumn( "REV_HAPPINESS", 46,
				u"<font=2>%s/%s</font>" % ( FontUtil.getChar( "happy" ), FontUtil.getChar( "unhappy" ) ),
				CityRevIdxHelper.computeHappinessRevIdxAndHelp ),

		RevIdxCityHelperCombinedCDAColumn( "REV_LOCATION", 44, u"<font=2>%s</font>" % FontUtil.getChar( "map" ),
				CityRevIdxHelper.computeLocationRevIdxAndHelp ),

		RevIdxCityHelperCDAColumn( "REV_RELIGION", 40, u"<font=2>%s</font>" % FontUtil.getChar( "religion" ),
				CityRevIdxHelper.computeReligionRevIdx, CityRevIdxHelper.computeReligionRevIdxHelp ),

		RevIdxCityHelperCombinedCDAColumn( "REV_NATIONALITY", 42,
				u"<font=2>%s%s</font>" % ( FontUtil.getChar( "commerce culture" ), FontUtil.getChar( "power" ) ),
			   CityRevIdxHelper.computeNationalityRevIdxAndHelp ),

		RevIdxCityHelperCombinedCDAColumn( "REV_GARRISON", 40, u"<font=2>%s</font>" % FontUtil.getChar( "power" ),
				CityRevIdxHelper.computeGarrisonRevIdxAndHelp ),

		RevIdxCityHelperCombinedCDAColumn( "REV_DISORDER", 40, u"<font=2>%s</font>" % FontUtil.getChar( "occupation" ),
				CityRevIdxHelper.computeDisorderRevIdxAndHelp ),

		RevIdxCityHelperCombinedCDAColumn( "REV_CRIME", 50, u"<font=2>%s</font>" % FontUtil.getChar( "badgold" ),
				CityRevIdxHelper.computeCrimeRevIdxAndHelp ),

		RevIdxCityHelperCombinedCDAColumn( "REV_VARIOUS", 50,
				u"<img=%s size=16></img>" % artFileMgr.getInterfaceArtInfo( "INTERFACE_BTN_CIVICS" ).getPath(),
				CityRevIdxHelper.computeVariousRevIdxAndHelp ),

		RevIdxCityHelperCombinedCDAColumn( "REV_PER_TURN", 55, getText( "TXT_KEY_CDA_COLUMN_REV_LOCAL_PER_TURN" ),
				CityRevIdxHelper.computeRevIdxAndFinalModifierHelp )
	)



