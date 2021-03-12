"""
Columns for CvCustomizableDomesticAdvisor
"""

from CvPythonExtensions import *
import CvUtil

gc = CyGlobalContext()
localText = CyTranslator()


class CDAColumnHelper :
	def __init__( self ) :
		self.angryIcon = u"%c" % CyGame().getSymbolID(FontSymbols.ANGRY_POP_CHAR)
		self.commerceIcon = u"%c" %(gc.getYieldInfo(YieldTypes.YIELD_COMMERCE).getChar())
		self.cultureIcon = u"%c" %(gc.getCommerceInfo(CommerceTypes.COMMERCE_CULTURE).getChar())
		self.defenseIcon = u"%c" % CyGame().getSymbolID(FontSymbols.DEFENSE_CHAR)
		self.espionageIcon = u"%c" %(gc.getCommerceInfo(CommerceTypes.COMMERCE_ESPIONAGE).getChar())
		self.fistIcon = u"%c" % CyGame().getSymbolID(FontSymbols.OCCUPATION_CHAR)
		self.foodIcon = u"%c" %(gc.getYieldInfo(YieldTypes.YIELD_FOOD).getChar())
		self.footIcon = u"%c" % CyGame().getSymbolID(FontSymbols.MOVES_CHAR)
		self.goldIcon = u"%c" %(gc.getCommerceInfo(CommerceTypes.COMMERCE_GOLD).getChar())
		self.redGoldIcon = u"%c" % CyGame().getSymbolID(FontSymbols.BAD_GOLD_CHAR)
		self.figureheadIcon = u"%c" % CyGame().getSymbolID(FontSymbols.GREAT_PEOPLE_CHAR)
		self.hammerIcon = u"%c" %(gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar())
		self.happyIcon = u"%c" % CyGame().getSymbolID(FontSymbols.HAPPY_CHAR)
		self.healthIcon = u"%c" % CyGame().getSymbolID(FontSymbols.HEALTHY_CHAR)
		self.lawIcon = u"%c" % CyGame().getSymbolID(FontSymbols.DEFENSIVE_PACT_CHAR)
		self.militaryIcon = u"%c" % CyGame().getSymbolID(FontSymbols.STRENGTH_CHAR)
		self.powerIcon = u"%c" % CyGame().getSymbolID(FontSymbols.POWER_CHAR)
		self.redfoodIcon = u"%c" % CyGame().getSymbolID(FontSymbols.BAD_FOOD_CHAR)
		self.religionIcon = u"%c" % CyGame().getSymbolID(FontSymbols.RELIGION_CHAR)
		self.researchIcon = u"%c" %(gc.getCommerceInfo(CommerceTypes.COMMERCE_RESEARCH).getChar())
		self.sickIcon = u"%c" % CyGame().getSymbolID(FontSymbols.UNHEALTHY_CHAR)
		self.tradeIcon = u"%c" % CyGame().getSymbolID(FontSymbols.TRADE_CHAR)
		self.unhappyIcon = u"%c" % CyGame().getSymbolID(FontSymbols.UNHAPPY_CHAR)
		self.objectIsPresent = "x"
		self.objectIsNotPresent = "-"
		self.objectCanBeBuild = "o"
		self.objectUnderConstruction = self.hammerIcon
		self.objectHave = localText.changeTextColor( self.objectIsPresent, gc.getInfoTypeForString( "COLOR_GREEN" ) )  # "x"
		self.objectNotPossible = localText.changeTextColor( self.objectIsNotPresent, gc.getInfoTypeForString( "COLOR_RED" ) )  # "-"
		self.objectPossible = localText.changeTextColor( self.objectCanBeBuild, gc.getInfoTypeForString( "COLOR_BLUE" ) )  # "o"
		self.objectHaveObsolete = localText.changeTextColor( self.objectIsPresent, gc.getInfoTypeForString( "COLOR_WHITE" ) )  # "x"
		self.objectNotPossibleConcurrent = localText.changeTextColor( self.objectIsNotPresent, gc.getInfoTypeForString( "COLOR_YELLOW" ) )  # "-"
		self.objectPossibleConcurrent = localText.changeTextColor( self.objectCanBeBuild, gc.getInfoTypeForString( "COLOR_YELLOW" ) )  # "o"

helper = None
def _getHelper() :
	# type: () -> CDAColumnHelper
	global helper
	if helper is None :
		helper = CDAColumnHelper()
	return helper


class CDAColumn( object ) :
	""" Base class of CDA columns. """
	def __init__( self, szName, iDefaultWidth, szTitle ) :
		# type: (str, int, unicode) -> None
		self._szName = szName
		self._iDefaultWidth = iDefaultWidth
		self._szTitle = szTitle
	
	@property
	def name( self ) :
		# type: () -> str
		""" The Columns unique identifier. """
		return self._szName
	
	@property
	def default_width( self ) :
		# type: () -> int
		""" The default width of the column. """
		return self._iDefaultWidth
	
	@property
	def title( self ) :
		# type: () -> unicode
		""" The title of the column, shown in the column selection table and in the column header, if no button is defined. """
		return self._szTitle
	
	@property
	def button( self ) :
		# type: () -> Optional[Tuple[str, WidgetTypes, int, int]]
		"""
		Button to replace the title as the column heading. Should return None or a 4-tupel of the form
		 	( szButton, eWidgetType, iData1, iData2 )
		where the last three parameters are for creating the button widget.
		"""
		return None
	
	def compute_value( self, pCity ) :
		# type : (CyCity) -> Union[str, int]
		""" Compute the cell content of the column for the given city. Should be overridden by subclasses """
		return ""
	
	@property
	def is_date_cell( self ) :
		# type: () -> bool
		""" Whether the cell content string should be written with CyGInterface.setTableDate """
		return False
	
	def is_valid( self, pPlayer ) :
		# type: (CyPlayer) -> bool
		""" Whether the given player should see this column. """
		return True
	
	@property
	def type( self ) : # LFGR_TODO: Remove
		# type: () -> str
		""" For compatability. """
		return "text"


class BuildingIconCDAColumn( CDAColumn ) :
	def __init__( self, eBuilding ) :
		self._eBuilding = eBuilding
		self._info = gc.getBuildingInfo( eBuilding )
		super( BuildingIconCDAColumn, self ).__init__( "I_" + self._info.getType(), 22,
			self._info.getDescription() + " (icon)" ) # LFGR_TODO: translate
		
	@property
	def button( self ) :
		return ( WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, self._info.getButton(), self._eBuilding, -1 )
	
	def compute_value( self, pCity ) :
		helper = _getHelper()
		if self._eBuilding == BuildingTypes.NO_BUILDING :
			return helper.objectNotPossible
		if pCity.getNumBuilding( self._eBuilding ) > 0:
			if pCity.getNumActiveBuilding( self._eBuilding ) > 0:
				return helper.objectHave
			else:
				return helper.objectHaveObsolete
		elif pCity.getFirstBuildingOrder( self._eBuilding ) != -1:
			return helper.objectUnderConstruction
		elif pCity.canConstruct( self._eBuilding, False, False, False ):
			return helper.objectPossible
		elif pCity.canConstruct( self._eBuilding, True, False, False ):
			return helper.objectPossibleConcurrent
		else:
			return helper.objectNotPossible
	
	def is_valid( self, pPlayer ) :
		eClass = self._info.getBuildingClassType()
		civInfo = gc.getCivilizationInfo( pPlayer.getCivilizationType() )
		return civInfo.getCivilizationBuildings( eClass ) == self._eBuilding
