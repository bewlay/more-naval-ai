# lfgr 07/2023: Revolutions concept screen

from CvPythonExtensions import *

import GCUtils
from PyHelpers import getText

import RevUtils


gc = CyGlobalContext()
gcu = GCUtils.GCUtils()


NL = getText( "[NEWLINE]" )
NL2 = NL + NL


def makeInfoLink( pInfo ) :
	# type: ( Union[CvInfoBase] ) -> unicode
	return getText( "[LINK=" + pInfo.getType() + "]%s1[\LINK]", pInfo.getDescription() )
	
def makeBuildingLink( eInfo ) :
	# type: ( Union[int, str] ) -> unicode
	pInfo = gc.getBuildingInfo( eInfo )
	return getText( "[LINK=" + pInfo.getType() + "]%s1[\LINK]", pInfo.getDescription() )

def makeOrList( lsz ) :
	# type: ( Sequence[unicode] ) -> unicode
	if len( lsz ) >= 2 and gc.getGame().getCurrentLanguage() == 0 :
		return ", ".join( lsz[:-1] ) + ", or " + lsz[-1]
	else :
		return ", ".join( lsz )

class RevConcept :
	def __init__( self ) :
		# Create helper lists
		self.leSortedUnits = sorted( range( gc.getNumUnitInfos() ), key = lambda e : gc.getUnitInfo( e ).getDescription() )
	
	def makeRevConceptText( self ) :
		# type: () -> unicode
		szResult = u""

		szRevAdvisorShortcut = "Ctrl+Shift+G"

		# Mechanics
		szResult += getText( "TXT_KEY_REVOLUTIONS_CONCEPT_MECHANICS", szRevAdvisorShortcut, RevUtils.revInstigatorThreshold )

		# FfH integration
		szResult += NL + getText( "TXT_KEY_REVOLUTIONS_CONCEPT_FFH_INTEGRATION" )

		# Factors
		szResult += NL + getText( "TXT_KEY_REVOLUTIONS_CONCEPT_FACTORS" )

		szResult += NL2 + getText( "TXT_KEY_REVOLUTIONS_CONCEPT_HAPPINESS" )

		szGovCenters = makeOrList( [makeBuildingLink( eBuilding ) for eBuilding in range( gc.getNumBuildingInfos() )
									if gc.getBuildingInfo( eBuilding ).isGovernmentCenter() and not gc.getBuildingInfo( eBuilding ).isCapital()] )
		szTeleportBuildings = makeOrList( [makeBuildingLink( eBuilding ) for eBuilding in range( gc.getNumBuildingInfos() ) if gc.getBuildingInfo( eBuilding ).getAirlift() > 0] )
		szResult += NL2 + getText( "TXT_KEY_REVOLUTIONS_CONCEPT_LOCATION" , szGovCenters, szTeleportBuildings )

		szResult += NL2 + getText( "TXT_KEY_REVOLUTIONS_CONCEPT_RELIGION",
				makeInfoLink( gcu.getReligionInfo( "RELIGION_THE_ORDER" ) ),
				makeInfoLink( gcu.getReligionInfo( "RELIGION_THE_ASHEN_VEIL" ) ) )

		szResult += NL2 + getText( "TXT_KEY_REVOLUTIONS_CONCEPT_NATIONALITY" )

		szResult += NL2 + getText( "TXT_KEY_REVOLUTIONS_CONCEPT_GARRISON" )

		szGreatWorkUnits = u", ".join( makeInfoLink( gc.getUnitInfo( eUnit ) ) for eUnit in self.leSortedUnits if gc.getUnitInfo( eUnit ).getGreatWorkCulture() > 0 )
		szResult += NL2 + getText( "TXT_KEY_REVOLUTIONS_CONCEPT_DISORDER", szGreatWorkUnits )

		szResult += NL2 + getText( "TXT_KEY_REVOLUTIONS_CONCEPT_MISC" )

		szResult += NL + getText( r"TXT_KEY_REVOLUTIONS_CONCEPT_STRATEGY" )

		return szResult

def makeRevConceptText() :
	return RevConcept().makeRevConceptText()