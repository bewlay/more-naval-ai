"""
Columns for CvCustomizableDomesticAdvisor

CDA_REFACTOR 03/2021 lfgr
"""

from CvPythonExtensions import *
import FontUtil

gc = CyGlobalContext()
localText = CyTranslator()


class CDAColumnHelper :
	""" Useful constants. """
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

		self.yieldIcons = {}
		for eYieldType in range(YieldTypes.NUM_YIELD_TYPES):
			info = gc.getYieldInfo(eYieldType)
			self.yieldIcons[eYieldType] = u"%c" % info.getChar()

		self.commerceIcons = {}
		for eCommerceType in range(CommerceTypes.NUM_COMMERCE_TYPES):
			info = gc.getCommerceInfo(eCommerceType)
			self.commerceIcons[eCommerceType] = u"%c" % info.getChar()

		self.starIcon = u"%c" % CyGame().getSymbolID(FontSymbols.STAR_CHAR)
		self.silverStarIcon = u"%c" % CyGame().getSymbolID(FontSymbols.SILVER_STAR_CHAR)
		self.bulletIcon = u"%c" % CyGame().getSymbolID(FontSymbols.BULLET_CHAR)

		self.milInstructorIcon = FontUtil.getChar(FontSymbols.MILITARY_INSTRUCTOR_CHAR)
		self.landIcon = FontUtil.getChar(FontSymbols.DOMAIN_LAND_CHAR)
		self.seaIcon = FontUtil.getChar(FontSymbols.DOMAIN_SEA_CHAR)
		self.airIcon = FontUtil.getChar(FontSymbols.DOMAIN_AIR_CHAR)
		self.cancelIcon = FontUtil.getChar(FontSymbols.CANCEL_CHAR)

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

helper = None
def _getHelper() :
	# type: () -> CDAColumnHelper
	global helper
	if helper is None :
		helper = CDAColumnHelper()
	return helper


# Helper functions
def _appendLine( szText, szLine ) :
	# type: (unicode, unicode) -> unicode
	if len( szText ) == 0 :
		return szLine
	else :
		return szText + u"\n" + szLine


class CDAColumn( object ) :
	""" Base class of CDA columns. """
	def __init__( self, szName, iDefaultWidth, szTitle ) :
		# type: (str, int, unicode) -> None
		self._szName = szName
		self._iDefaultWidth = iDefaultWidth
		self._szTitle = szTitle

		self._help = _getHelper()
	
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
		# type : (CyCity) -> Union[unicode, int]
		"""
		Compute the cell content of this column for the given city.
		This or compute_value_and_tooltip should be overridden by subclasses.
		"""
		return self.compute_value_and_tooltip( pCity )[0]

	def compute_tooltip( self, pCity ) :
		# type: (CyCity) -> Optional[unicode]
		""" Compute the cell tooltip of this column for the given city. None means no tooltip """
		return self.compute_value_and_tooltip( pCity )[1]

	def compute_value_and_tooltip( self, pCity ) :
		"""
		Returns a tuple (cellContent, tooltip). May be overridden instead of compute_value() and compute_tooltip().
		"""
		return (u"", None)

	def compute_int_color( self, pCity, iValue ) :
		# type: (CyCity, int) -> int
		"""
		Returns the color of the cell value as a ColorTypes.
		Only is called if compute_value() returns an integer; string coloring can be done manually.
		The return value of compute_value() is provided as the second argument for convenience.
		"""
		return ColorTypes.NO_COLOR

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
		""" For compatibility. """
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
	
	def compute_value( self, pCity ) : # From CvCustomizableDomesticAdvisor
		if self._eBuilding == BuildingTypes.NO_BUILDING :
			return self._help.objectNotPossible
		if pCity.getNumBuilding( self._eBuilding ) > 0:
			if pCity.getNumActiveBuilding( self._eBuilding ) > 0:
				return self._help.objectHave
			else:
				return self._help.objectHaveObsolete
		elif pCity.getFirstBuildingOrder( self._eBuilding ) != -1:
			return self._help.objectUnderConstruction
		elif pCity.canConstruct( self._eBuilding, False, False, False ):
			return self._help.objectPossible
		elif pCity.canConstruct( self._eBuilding, True, False, False ):
			return self._help.objectPossibleConcurrent
		else:
			return self._help.objectNotPossible

	def compute_tooltip( self, pCity ) :
		szName = self._info.getDescription()
		value = self.compute_value( pCity )
		if value == self._help.objectNotPossible :
			return localText.getText( "Cannot build %s1", (szName,) ) # LFGR_TODO: Translate
		elif value == self._help.objectHave :
			return localText.getText( "%s1 present", (szName,) ) # LFGR_TODO: Translate
		elif value == self._help.objectHaveObsolete :
			return localText.getText( "%s1 present, but obsolete", (szName,) ) # LFGR_TODO: Translate
		elif value == self._help.objectUnderConstruction :
			return localText.getText( "%s1 under construction", (szName,) ) # LFGR_TODO: Translate
		elif value == self._help.objectPossible :
			return localText.getText( "%s1 can be constructed", (szName,) ) # LFGR_TODO: Translate
		elif value == self._help.objectPossibleConcurrent :
			return localText.getText( "%s1 can be continued", (szName,) ) # LFGR_TODO: Translate, is this correct?

	def is_valid( self, pPlayer ) :
		eClass = self._info.getBuildingClassType()
		civInfo = gc.getCivilizationInfo( pPlayer.getCivilizationType() )
		return civInfo.getCivilizationBuildings( eClass ) == self._eBuilding


class FeaturesCDAColumn( CDAColumn ) :
	def __init__( self ) :
		super( FeaturesCDAColumn, self ).__init__( "FEATURES", 106, localText.getText( "TXT_KEY_MISC_FEATURES", () ) )

	def compute_value_and_tooltip( self, pCity ) :
		# Mostly from original CDA
		szValue = ""
		szTooltip = ""

		# First look for Government Centers
		if pCity.isGovernmentCenter():
			# And distinguish between the Capital and the others (e.g. Forbidden Palace)
			if pCity.isCapital():
				szValue += self._help.starIcon
				szTooltip = _appendLine( szTooltip, localText.getText( "[ICON_BULLET]Capital", () ) ) # TODO: Translate
			else:
				szValue += self._help.silverStarIcon
				szTooltip = _appendLine( szTooltip, localText.getText( "[ICON_BULLET]Government center", () ) ) # TODO: Translate

		# add National Wonders
		for i in range(gc.getNumBuildingInfos()):
			info = gc.getBuildingInfo(i)
			classInfo = gc.getBuildingClassInfo(info.getBuildingClassType())
			if classInfo.getMaxGlobalInstances() == -1 and classInfo.getMaxPlayerInstances() == 1 and pCity.getNumBuilding(i) > 0 and not info.isCapital():
				# Use bullets as markers for National Wonders
				szValue += self._help.bulletIcon
				szTooltip = _appendLine( szTooltip, localText.getText( "[ICON_BULLET]National wonder: %s1_building",
						( info.getTextKey(), ) ) ) # TODO: Translate

		if pCity.isDisorder():
			if pCity.isOccupation():
				szOccu = u"%c" % CyGame().getSymbolID(FontSymbols.OCCUPATION_CHAR)
				szValue += szOccu +":"+unicode(pCity.getOccupationTimer())
				szTooltip = _appendLine( szTooltip, localText.getText( "[ICON_BULLET]Occupied for %d1 more [NUM1:turn:turns]",
						() ) ) # TODO: Translate
			else:
				pCity += self._help.angryIcon
				szTooltip = _appendLine( szTooltip, localText.getText( "[ICON_BULLET]Disorder", () ) ) # TODO: Translate

		pTradeCity = pCity.getTradeCity(0)
		if (pTradeCity and pTradeCity.getOwner() >= 0):
			szValue += self._help.tradeIcon
			szTooltip = _appendLine( szTooltip, localText.getText( "[ICON_BULLET]Trade with other cities", () ) ) # TODO: Translate

		return szValue, szTooltip
