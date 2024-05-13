""" Utilities for spawning and reinforcing revolutions. """
from CvPythonExtensions import *

import BugCore
import BugUtil
import CvUtil
import RevData
import RevDefs
import RevUnits
import RevUtils

from PyHelpers import CIV_PLAYERS, PyPlayer, sorenRandChoice, getText


# 0: no logging, 1 : normal logging, 2+: verbose logging
LOG_LEVEL = 5

gc = CyGlobalContext()
game = gc.getGame()
RevOpt = BugCore.game.Revolution


### Utility

def log( s ) :
	# type: ( str ) -> None
	CvUtil.pyPrint( "  RevSpawning - %s" % s )


### Rev-utility

# lfgr: Extracted from Revolution.py
def generateRebelSpawnPlot( iX, iY, pRevPlayer, bAllowOnEnemy = False ) :
	# type: (int, int, CyPlayer, bool) -> Optional[Tuple[int, int]]

	# First look just for rebel, homeland, or unowned territory to spawn in
	spawnablePlots = RevUtils.getSpawnablePlots( iX, iY, pRevPlayer, bIncludePlot = False, iRange = 1, iSpawnPlotOwner = pRevPlayer.getID(), bAtWarPlots = False, bOpenBordersPlots = False )
	if len( spawnablePlots ) == 0 :
		# Try plots owner by other players, either with open borders or at war with rebel
		spawnablePlots = RevUtils.getSpawnablePlots( iX, iY, pRevPlayer, bIncludePlot = False, iRange = 1, iSpawnPlotOwner = pRevPlayer.getID() )
	if bAllowOnEnemy and len( spawnablePlots ) == 0 :
		# Check if plots are available if we move opposing units
		spawnablePlots = RevUtils.getSpawnablePlots( iX, iY, pRevPlayer, bIncludePlot = False, iRange = 1, iSpawnPlotOwner = pRevPlayer.getID(), bCheckForEnemy = False )
	if len( spawnablePlots ) == 0 :
		# Expand search area
		spawnablePlots = RevUtils.getSpawnablePlots( iX, iY, pRevPlayer, bIncludePlot = False, iRange = 2, iSpawnPlotOwner = pRevPlayer.getID() )
	if len( spawnablePlots ) == 0 :
		# Further expand search area
		spawnablePlots = RevUtils.getSpawnablePlots( iX, iY, pRevPlayer, bIncludePlot = False, iRange = 3, iSpawnPlotOwner = -1 )
	if bAllowOnEnemy and len( spawnablePlots ) == 0 :
		# Put them anywhere nearby, this will only fail on single plot islands
		spawnablePlots = RevUtils.getSpawnablePlots( iX, iY, pRevPlayer, bIncludePlot = False, iRange = 3, iSpawnPlotOwner = -1, bCheckForEnemy = False )

	if len( spawnablePlots ) > 0 :
		return spawnablePlots[gc.getGame().getSorenRandNum(len(spawnablePlots),'Revolution: Pick rev plot')]
	else :
		return None
	

# lfgr: Extracted from Revolution.py, simplified, incorporated the extra x2 factor from later
def getNumRevoltUnits( pCity, pRevPlayer, iCityIdx, bWeak ) :
	# type: (CyCity, CyPlayer, int, bool) -> int

	if LOG_LEVEL >= 3 : log( "Computing rebel forces size in %s" % pCity.getName() )
	
	# Compute effective population
	fEffPop = pCity.getPopulation() ** .8
	if pRevPlayer.getID() == RevData.getRevolutionPlayer( pCity ) :
		if LOG_LEVEL >= 3 : log( "  Repeat revolution, increasing enlistment" )
		fEffPop *= 2
	fEffPop += 1

	if LOG_LEVEL >= 3 : log( "  Effective population: %.2f" % fEffPop )
	
	# Modifier from rev idx. Between .2 and 1.0
	fAdjustRevIdx = pCity.getRevolutionIndex() * 1.0 / RevDefs.alwaysViolentThreshold
	fRevIdxMod = max( .2, min( 1.0, fAdjustRevIdx ) )

	if LOG_LEVEL >= 3 : log( "  RevIdx modifier: %.2f" % fRevIdxMod )
	
	# Compute basic unit number
	fUnitsFromPop = RevOpt.getStrengthModifier() * fRevIdxMod * fEffPop
	
	# if bIsBarbRev or bIsJoinWar :
	if bWeak :
		fUnitsFromPop /= 2

	iNumUnits = int( fUnitsFromPop )

	# Reduce number of rebel troops in third or higher city in large revolt;
	#   cities should be in rev index order so these should be less fervent
	return max( 0, max( 2, iNumUnits ) - iCityIdx )

# lfgr: Extracted from Revolution.py, simplified, incorporated the extra x2 factor from later
def getNumReinforceUnits( pCity, pRevPlayer, iNearbyRebels ) :
	# type: ( CyCity, CyPlayer, int ) -> int
	
	if LOG_LEVEL >= 3 : log( "Computing reinforcement size in %s" % pCity.getName() )
	
	iRevIdx = pCity.getRevolutionIndex()
	iRevIdxPerTurn = pCity.getLocalRevIndex()
	
	revStrength = 2 * RevOpt.getReinforcementModifier() * iRevIdx * 1. / RevDefs.revInstigatorThreshold
	revStrength *= min( ( pCity.getPopulation() + 1 ) / 8.0, 2.0 )
	if iRevIdxPerTurn > 0 :
		revStrength *= min( 0.5 + iRevIdxPerTurn / 10.0, 2.0 )
	else :
		revStrength /= 2 - iRevIdxPerTurn / 3.0
	
	if LOG_LEVEL >= 3 : log( "  Basic strength: %.2f" % revStrength )

	if pCity.getRevolutionCounter() == 0 :
		# Rebellion decreases in fervor after counter expires
		revStrength /= 2.0
	elif game.getGameTurn() - RevData.getCityVal( pCity, 'RevolutionTurn' ) < 3 :
		# Initial fervor
		revStrength *= 1.5
		
	if LOG_LEVEL >= 3 : log( "  Strength with time effect: %.2f" % revStrength )

	# Check for nearby enemies
	iDefIn2 = RevUtils.getNumDefendersNearPlot( pCity.getX(), pCity.getY(), pCity.getOwner(), iRange = 2 )
	if iNearbyRebels > iDefIn2 :
		# Rebels are stronger
		revStrength *= 1.3
	elif pRevPlayer.isRebel() and pRevPlayer.getNumCities() > 0 and iNearbyRebels > 3 : # LFGR_TODO: Added isRebel(), is this correct?
		# Bolster a successful revolt
		revStrength *= 1.25
	elif iNearbyRebels + 2 < iDefIn2 :
		# Odds are too steep, some doubt potential for success
		revStrength *= 0.8
		
	if LOG_LEVEL >= 3 : log( "  Strength with enemies effect: %.2f" % revStrength )

	iNumUnits = int( revStrength + .5 )
	
	# Cap number of units
	if game.getGameTurn() - RevData.getCityVal( pCity, 'RevolutionTurn' ) < 3 \
			or ( pRevPlayer.getNumCities() > 0 and iNearbyRebels >= 3 ):
		iCap = min( pCity.getPopulation() // 2, iRevIdxPerTurn )
	else :
		# Been a few turns since revolution, turn down intensity
		iCap = min( pCity.getPopulation() // 3, iRevIdxPerTurn // 2 )
	
	iNumUnits = max( 1, min( iCap, iNumUnits ) )
		
	if LOG_LEVEL >= 3 : log( "  Number of units after caps: %d" % iNumUnits )

	return iNumUnits

def createRebelUnits( pCity, pRevPlayer, iX, iY, iNumUnits, iRebelsIn3 = 0, iRebelsIn6 = 0 ) :
	# type: (CyCity, CyPlayer, int, int, int, int, int) -> List[CyUnit]
	""" Spawn rebel units to besiege a city. """

	citySpawnCache = RevUnits.CitySpawnCache( pCity, pRevPlayer, iNumUnits, iRebelsIn3, iRebelsIn6 )
	lpNewUnits = []

	# Healers
	lpNewUnits.extend( citySpawnCache.spawnUnitsByRule( min( 2, iNumUnits // 5 ), "HEALER", iX, iY, bOptional = True ) )
	
	# Support
	lpNewUnits.extend( citySpawnCache.spawnUnitsByRule( min( 1, iNumUnits // 8 ), "SUPPORT", iX, iY, bOptional = True ) )
	
	# Counter
	lpNewUnits.extend( citySpawnCache.spawnUnitsByRule( iNumUnits // 4, "COUNTER_DEFENSE", iX, iY ) )

	# Bulk of the army (always >= 50% of units)
	lpNewUnits.extend( citySpawnCache.spawnUnitsByRule( iNumUnits - len( lpNewUnits ), "ATTACK", iX, iY ) )

	return lpNewUnits

def createRebelCityUnits( pCity, pRevPlayer, iNumUnits ) :
	# type: (CyCity, CyPlayer, int) -> List[CyUnit]
	""" Spawn rebel units in a city that they took over right at the beginning of the revolt. """

	iX = pCity.getX()
	iY = pCity.getY()

	citySpawnCache = RevUnits.CitySpawnCache( pCity, pRevPlayer, iNumUnits )
	lpNewUnits = []
	
	# Defenders
	lpNewUnits.extend( citySpawnCache.spawnUnitsByRule( min( 2, iNumUnits // 3 ), "CITY_DEFENSE", iX, iY ) )

	# Healers
	lpNewUnits.extend( citySpawnCache.spawnUnitsByRule( min( 1, iNumUnits // 8 ), "HEALER", iX, iY, bOptional = True ) )

	# Support
	lpNewUnits.extend( citySpawnCache.spawnUnitsByRule( min( 1, iNumUnits // 6 ), "SUPPORT", iX, iY, bOptional = True ) )
	
	# Counter defense
	lpNewUnits.extend( citySpawnCache.spawnUnitsByRule( min( 2, iNumUnits // 4 ), "COUNTER_DEFENSE", iX, iY ) )
	
	# Attackers (remainder)
	lpNewUnits.extend( citySpawnCache.spawnUnitsByRule( iNumUnits - len( lpNewUnits ), "ATTACK", iX, iY ) )
	
	# Workers
	iNumWorkers = 1
	if pCity.getPopulation() > 5 :
		iNumWorkers += 1
	lpNewUnits.extend( citySpawnCache.spawnUnitsByRule( iNumWorkers, "WORKER", iX, iY ) )

	# Injure units, since they presumably fought to take over the city
	for newUnit in lpNewUnits :
		if newUnit.canFight():
			iDamage = 15 + game.getSorenRandNum(25,'Revolt - Injure victorious rebel unit')
			newUnit.setDamage( iDamage, pCity.getOwner() )

	return lpNewUnits

# lfgr: extracted from Revolution.py and fixed
def evacuateEnemyUnits( iX, iY, pPlayer, bInjure = False, bAllowAtWar = False, bAllowArbitraryCity = False ) :
	# type: ( int, int, CyPlayer, bool, bool, bool ) -> None
	""" Move all enemies of pPlayer out of the way"""
	
	# LFGR_TODO: What if multiple owners? -- Need to rewrite and take parts of RevUtils.moveEnemyUnits
	# pPlot = gc.getMap().plot( iX, iY )
	# pTeam = gc.getTeam( pPlayer.getTeam() )
	# depEnemyUnitsByOwner = {}
	# 
	# for i in xrange( pPlot.getNumUnits() ) :
	# 	pUnit = pPlot.getUnit( i ) # type: CyUnit
	# 	if pTeam.isAtWar( pUnit.getTeam() ) :
	# 		eOwner = pUnit.getOwner()
	# 		if eOwner not in depEnemyUnitsByOwner :
	# 			depEnemyUnitsByOwner[eOwner] = []
	# 		depEnemyUnitsByOwner[eOwner].append( pUnit )
	
	enemyUnits = RevUtils.getEnemyUnits( iX, iY, pPlayer.getID() )
	if len( enemyUnits ) > 0 :
		pOwner = gc.getPlayer( enemyUnits[0].getOwner() )
		dBaseArgs = { "bIncludePlot" : False, "bIncludeCities" : True }
		
		iInjureMax = 40
		retreatPlots = RevUtils.getSpawnablePlots( iX, iY, pOwner, bIncludeForts = True, bSameArea = True, iRange = 1, bAtWarPlots = False, bOpenBordersPlots = False, **dBaseArgs )
		if len( retreatPlots ) == 0 :
			iInjureMax = 60
			retreatPlots = RevUtils.getSpawnablePlots( iX, iY, pOwner, bIncludeForts = True, bSameArea = True, iRange = 2, bAtWarPlots = bAllowAtWar, **dBaseArgs )
		if len( retreatPlots ) == 0 :
			iInjureMax = 65
			retreatPlots = RevUtils.getSpawnablePlots( iX, iY, pOwner, bSameArea = False, iRange = 4, iSpawnPlotOwner = -1, bAtWarPlots = bAllowAtWar, **dBaseArgs )
		if bAllowArbitraryCity and len( retreatPlots ) == 0:
			iInjureMax = 70
			# Try to move to another of players cities
			if LOG_LEVEL >= 1: log( "No nearby plots, trying move to another of players cities" )
			for pOtherCity in PyPlayer( pOwner.getID() ).iterCities() :
				if pOtherCity.getX() != iX and pOtherCity.getY() != iY :
					retreatPlots.append( ( pOtherCity.getX(), pOtherCity.getY() ) )
		
		if len( retreatPlots ) == 0 :
			# Highly unlikely
			log( "WARNING: Enemy units at %d|%d are going to die cause they have no where to go ..." % ( iX, iY ) )
		else :
			if not bInjure :
				iInjureMax = 0
				
			moveToLoc = sorenRandChoice( retreatPlots, "Revolution: Pick move to plot" )
			if LOG_LEVEL >= 3 : log("Enemy units in plot %d|%d moving to %d|%d"%(iX, iY, moveToLoc[0], moveToLoc[1]))
			RevUtils.moveEnemyUnits( iX, iY, pPlayer.getID(), moveToLoc[0], moveToLoc[1], iInjureMax = iInjureMax, bDestroyNonLand = False, bLeaveSiege = False )

### Main functions

# lfgr: Extracted from Revolution.py
def announceRevolutionaries( eMotherPlayer, pRevPlayer, iX, iY, bJoinRev ) :
	# type: ( int, CyPlayer, int, int, bool ) -> None
	""" Announce revolution to all players """
	for ePlayer in xrange( gc.getMAX_CIV_PLAYERS() ) :
		if gc.getPlayer( ePlayer ) is None :
			continue
		# LFGR_TODO: Better text handling
		if gc.getPlayer( ePlayer ).canContact( eMotherPlayer ) or ePlayer == eMotherPlayer :
			eColor = 7
			if pRevPlayer.isBarbarian() :
				if ePlayer == eMotherPlayer :
					mess = "<color=255,0,0,255>" + getText( "TXT_KEY_REV_MESS_YOU_BARB" )
				else :
					mess = "<color=255,0,0,255>" + getText( "TXT_KEY_REV_MESS_VIOLENT" ) + ' ' + PyPlayer( eMotherPlayer ).getCivilizationName() + '!!!'
					mess += "  " + getText("TXT_KEY_REV_MESS_BARB" )
			else :
				if ePlayer == eMotherPlayer :
					mess = "<color=255,0,0,255>"
					if bJoinRev :
						mess += getText("TXT_KEY_REV_MESS_JOIN",pRevPlayer.getNameKey(), pRevPlayer.getCivilizationDescription(0) )
					else :
						mess += getText("TXT_KEY_REV_MESS_YOU_RISEN", pRevPlayer.getNameKey(), pRevPlayer.getCivilizationDescription(0) )
				else :
					mess = ""

					if ePlayer == pRevPlayer.getID() :
						mess += "<color=0,255,0,255>"
						eColor = 8
					else :
						mess += "<color=255,0,0,255>"
						eColor = 7

					mess += getText( "TXT_KEY_REV_MESS_VIOLENT" ) + ' ' + PyPlayer( eMotherPlayer ).getCivilizationName() + '!!!'
					if bJoinRev :
						mess += "  " + getText( "TXT_KEY_REV_MESS_JOIN",pRevPlayer.getName(), pRevPlayer.getCivilizationDescription(0) )
					else :
						mess += "  " + getText("TXT_KEY_REV_MESS_RISEN", pRevPlayer.getCivilizationDescription(0), pRevPlayer.getNameKey() )

			if ePlayer == eMotherPlayer :
				CyInterface().addMessage(ePlayer, true, gc.getDefineINT("EVENT_MESSAGE_TIME"), mess, "AS2D_CITY_REVOLT", InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT, CyArtFileMgr().getInterfaceArtInfo("INTERFACE_RESISTANCE").getPath(), ColorTypes(eColor), iX, iY, True, True)
			elif ePlayer == pRevPlayer.getID() :
				CyInterface().addMessage(ePlayer, true, gc.getDefineINT("EVENT_MESSAGE_TIME"), mess,  "AS2D_DECLAREWAR", InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT, None, ColorTypes(eColor), iX, iY, False, False)
			else :
				CyInterface().addMessage(ePlayer, false, gc.getDefineINT("EVENT_MESSAGE_TIME"), mess,  "AS2D_DECLAREWAR", InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT, None, ColorTypes(eColor), -1, -1, False, False)

# lfgr: Extracted from Revolution.py
def announceReinforcements( pCity, pRevPlayer ) :
	# type: (CyCity, CyPlayer) -> None
	pRevTeam = gc.getTeam( pRevPlayer.getTeam() )
	
	for ePlayer in CIV_PLAYERS :
		msg = None
		bImportant = True
		bPositive = False
		if pCity.getOwner() == ePlayer :
			msg = getText( "TXT_KEY_REV_MESS_REINFORCEMENTS",pRevPlayer.getNameKey(), pCity.getName() )
		elif pRevTeam.isAtWar( gc.getPlayer( ePlayer ).getTeam() ) and pRevPlayer.canContact( ePlayer ) :
			msg = getText( "TXT_KEY_REV_MESS_REINFORCEMENTS",pRevPlayer.getNameKey(), pCity.getName() )
			bImportant = False
		elif pRevPlayer.getID() == ePlayer :
			msg = getText( "TXT_KEY_REV_MESS_YOUR_REINFORCEMENTS",pRevPlayer.getCivilizationDescription(0), pCity.getName() )
			bPositive = True
		
		if msg :
			CyInterface().addMessage( ePlayer, bImportant, gc.getDefineINT("EVENT_MESSAGE_TIME"), msg,
					bImportant and "AS2D_CITY_REVOLT" or None, InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT,
					bImportant and CyArtFileMgr().getInterfaceArtInfo("INTERFACE_RESISTANCE").getPath() or None,
					bPositive and ColorTypes(8) or ColorTypes(7), pCity.getX(), pCity.getY(), bImportant, bImportant )

# lfgr: Extracted from Revolution.py
def setupRevPlayer( pMotherPlayer, pRevPlayer, lpCities, bIsJoinWar ) :
	# type: ( CyPlayer, CyPlayer, Sequence[CyCity], bool ) -> None
	""" Set up player when starting a revolution. pRevPlayer is not necessarily a new player. """
	
	pMotherTeam = gc.getTeam( pMotherPlayer.getTeam() )
	pRevTeam = gc.getTeam( pRevPlayer.getTeam() )
	
	# Declare war to mother player
	if not pRevTeam.isAtWar( pMotherPlayer.getTeam() ) :
		pRevTeam.declareWar( pMotherPlayer.getTeam(), True, WarPlanTypes.WARPLAN_TOTAL )
		if LOG_LEVEL >= 1 : log( "The %s revolutionaries declare war and start a revolution against the %s!" % (pRevPlayer.getCivilizationAdjective( 0 ), pMotherPlayer.getCivilizationDescription( 0 )) )
		pRevPlayer.setIsRebel( True )
		pRevTeam.setRebelAgainst( pMotherPlayer.getTeam(), True )
	elif pRevPlayer.isMinorCiv() and not bIsJoinWar :
		if LOG_LEVEL >= 1 : log( "The %s revolutionaries declare war and start a revolution against the %s!" % (pRevPlayer.getCivilizationAdjective( 0 ), pMotherPlayer.getCivilizationDescription( 0 )) )
		pRevPlayer.setIsRebel( True )
		pRevTeam.setRebelAgainst( pMotherPlayer.getTeam(), True )
	else :
		if LOG_LEVEL >= 1 : log( "The %s revolutionaries join in the war against the %s!" % (pRevPlayer.getCivilizationAdjective( 0 ), pMotherPlayer.getCivilizationDescription( 0 )) )
	
	# Religion
	# LFGR_TODO: Handled in chooseRevolutionCiv
	# if pRevPlayer.getStateReligion() == ReligionTypes.NO_RELIGION :
	# 	iBestRelScore = 0
	# 	eBestRel = ReligionTypes.NO_RELIGION
	# 	for eRel in xrange( gc.getNumReligionInfos() ) :
	# 		iScore = 0
	# 		for idx, pCity in enumerate( lpCities ) :
	# 			if pCity.isHasReligion( eRel ) :
	# 				if idx == 0 : # Instigator
	# 					iScore += 3
	# 				else :
	# 					iScore += 1
	# 		iScore = iScore * ( 100 + gc.getGame().getSorenRandNum( 100, "Rebel religion" ) )
	# 		if iScore >= 2 and pMotherPlayer.getStateReligion() == eRel :
	# 			iScore //= 2
	# 		if iScore > iBestRelScore : # lfgr note: Slight bias towards low religions
	# 			eBestRel = eRel
	# 			iBestRelScore = iScore
	
	# Money
	if pRevPlayer.getGold() < 200 :
		iGold = 30 + game.getSorenRandNum( 30*len( lpCities ),'Revolt: give gold' )
	else :
		iGold = 10 + game.getSorenRandNum( 20*len( lpCities ),'Revolt: give gold' )
	iGold = min( iGold, 200 )
	pRevPlayer.changeGold( iGold )
	# LFGR_TODO: Announcement if player not new (or just always...)

	pRevPlayer.setFreeUnitCountdown(20)

	# Espionage
	# if( not game.isOption(GameOptionTypes.GAMEOPTION_NO_ESPIONAGE) and not bIsJoinWar ) :
	# 	espPoints = game.getSorenRandNum(20*len( lpCities ),'Revolt: esp') + (12+len( lpCities ))*max([pMotherPlayer.getCommerceRate( CommerceTypes.COMMERCE_ESPIONAGE ), 6])
	# 	if( pRevTeam.isAlive() ) :
	# 		espPoints /= 2
	# 	pRevTeam.changeCounterespionageTurnsLeftAgainstTeam(pTeam.getID(), 10)
	# 	pRevTeam.changeEspionagePointsAgainstTeam(pTeam.getID(), espPoints)
	# 	pTeam.changeEspionagePointsAgainstTeam(pRevTeam.getID(), espPoints/(3 + pTeam.getAtWarCount(True)))
	# 	if( LOG_LEVEL >= 1 ) : log( "Giving rebels %d espionage points against motherland"%(espPoints))
	# 	if( not pRevTeam.isAlive() ) :
	# 		for k in range(0,gc.getMAX_CIV_TEAMS()) :
	# 			if(gc.getTeam(k) == None):
	# 				continue
	# 			if( pRevTeam.isAtWar(k) and not gc.getTeam(k).isMinorCiv() ) :
	# 				pRevTeam.changeEspionagePointsAgainstTeam(k, game.getSorenRandNum(espPoints/2,'Revolt: esp') )
	# 				gc.getTeam(k).changeEspionagePointsAgainstTeam(pRevTeam.getID(), game.getSorenRandNum(espPoints/5, 'Revolt: esp'))

	# Diplomacy
	if pRevTeam.isMapTrading() :
		# Give motherlands map
		gameMap = gc.getMap()
		for iX in xrange( CyMap().getGridWidth() ) :
			for iY in xrange( CyMap().getGridHeight() ) :
				pPlot = gameMap.plot( iX, iY )
				if pPlot.isRevealed( pMotherPlayer.getTeam(), False ) :
					pPlot.setRevealed( pRevTeam.getID(), True, False, pMotherPlayer.getTeam() )

		# Meet players known by motherland
		for eTeam in xrange( gc.getMAX_CIV_TEAMS() ) :
			pTeam = gc.getTeam( eTeam )
			if pTeam is None :
				continue
			if (pTeam.getLeaderID() < 0) or (pTeam.getLeaderID() > gc.getMAX_CIV_PLAYERS()) :
				continue
			pLeader = gc.getPlayer(pTeam.getLeaderID())
			if pLeader is None :
				continue
			if pMotherTeam.isHasMet( eTeam ) and eTeam != pRevPlayer.getTeam() and eTeam != pMotherPlayer.getTeam() :
				if pMotherTeam.isAtWar( eTeam ) :
					# Rev player meets a likes enemies of mother
					pRevTeam.meet( eTeam, False )
					pRevPlayer.AI_changeAttitudeExtra( pTeam.getLeaderID(), 2 )
					pLeader.AI_changeAttitudeExtra( pRevPlayer.getID(), 2 )
				else :
					# Rev player MAY meet non-enemies of mother
					if game.getSorenRandNum( 2, 'odds' ) != 0 :
						pRevTeam.meet( eTeam, False )
						if pLeader.AI_getAttitude( pMotherPlayer.getID() ) == AttitudeTypes.ATTITUDE_FRIENDLY :
							# Rev player dislikes friends of mother
							pLeader.AI_changeAttitudeExtra( pRevPlayer.getID(), -2 )

# lfgr: Extracted from Revolution.py
@BugUtil.profile( parent = "RevSpawning" )
def spawnRevolutionaries( pCity, iRevCityIdx, pRevPlayer, bJoinRev ) :
	# type: ( CyCity, int, CyPlayer, bool ) -> List[CyUnit]
	""" Spawn revolutionary units in or near the city, possibly moving other units away. Returns the spawned units. """
	
	iRevIdx = pCity.getRevolutionIndex()
	iRevIdxPerTurn = pCity.getLocalRevIndex()
	iCityX = pCity.getX()
	iCityY = pCity.getY()
	
	pCityOwner = gc.getPlayer( pCity.getOwner() )
	
	bIsBarbRev = pRevPlayer.isBarbarian()
	iTurnsBetweenRevs = RevOpt.getTurnsBetweenRevs()

	if LOG_LEVEL >= 1 : log( "In %s, with rev idx %d (%d local)" % (pCity.getName(), iRevIdx, iRevIdxPerTurn) )

	# Find best spawn plot
	pCity.setOccupationTimer(1) # LFGR_TODO: Is this intended to reduce the city borders? Seems very hacky.
	revSpawnLoc = generateRebelSpawnPlot( iCityX, iCityY, pRevPlayer )
	pCity.setOccupationTimer(0) # LFGR_TODO: ?

	# Determine number of units
	iNumUnits = getNumRevoltUnits( pCity, pRevPlayer, iRevCityIdx, bWeak = bIsBarbRev or bJoinRev )

	if LOG_LEVEL >= 1 : log( "Enlisting %d units"% iNumUnits )

	# Determine whether revolutionaries take control of the city
	bRevControl = False
	if iNumUnits == 0:
		# No actual rebels for this city, just disorder
		if revSpawnLoc is None :
			if LOG_LEVEL >= 1: log( "No where to spawn rebels, but no rebel units to spawn either ... faking spawn location" )
			revSpawnLoc = [0,0]
	elif pCity.plot().getNumDefenders( pCityOwner.getID() ) == 0:
		if LOG_LEVEL >= 1: log( "City has no defenders, revs control" )
		bRevControl = True
	elif revSpawnLoc is None:
		# If no plot on which to spawn revs, they get city and owners units flee
		if LOG_LEVEL >= 1: log( "Nowhere to spawn rebels, so they get city" )
		bRevControl = True
	else :
		bRevControl = False
		# LFGR_TODO: Refine this, might be fun. Probably should only allow this if revs are *much* stronger
		# # Compare strength of revolution and garrison
		# iRevStrength = iNumUnits
		# if( (pCity.unhappyLevel(0) - pCity.happyLevel()) > 0 ) :
		# 	iRevStrength += 2
		# if( bIsJoinWar ) :
		# 	iRevStrength -= 2
		# if( bIsBarbRev ) :
		# 	iRevStrength -= 4
		# if( pCity.isCapital() ) :
		# 	iRevStrength -= 1
		# 
		# iGarrisonStrength = pCity.plot().getNumDefenders(pCityOwner.getID()) + 1
		# iGarrisonStrength = int( iGarrisonStrength*(110 + pCity.getBuildingDefense())/100.0 )
		# 
		# if( LOG_LEVEL >= 1 ) : log( "Rev strength: %d,  Garrison strength: %d"%(iRevStrength,iGarrisonStrength))
		# 
		# if( iRevStrength > iGarrisonStrength ) :
		# 	# Revolutionaries out muscle the city garrison and take control
		# 	revControl = True
		# else :
		# 	# Spawn in countryside
		# 	revControl = False
	
	# Prepare or take over city
	if bRevControl :
		if LOG_LEVEL >= 1 : log( "Revs take control of %s (%d,%d)" % (pCity.getName(), pCity.getX(), pCity.getY()) )
		
		revSpawnLoc = (iCityX, iCityY) # Spawn on the city!

		# Some revs die when taking control of city
		iNumUnits = min( 1, iNumUnits * 9 // 10 )

		# Turn off rebellious city capture logic, all components handled here
		RevData.setRevolutionPlayer( pCity, -1 )

		# Run wounded soldiers out of Town, try to place near city
		evacuateEnemyUnits( iCityX, iCityY, pRevPlayer, bInjure = True, bAllowAtWar = True, bAllowArbitraryCity = True )
		
		# Store building types in city
		buildingClassList = list()
		for buildingType in range(0,gc.getNumBuildingInfos()) :
			if pCity.getNumRealBuilding( buildingType ) > 0:
				buildingInfo = gc.getBuildingInfo(buildingType)
				buildingClassList.append( [buildingInfo.getBuildingClassType(),pCity.getNumRealBuilding(buildingType)] )

		# Acquire city
		#pRevPlayer.acquireCity( pCity, False, False ) # LFGR_TODO: Why not like this? Because this would convert culture?
		if LOG_LEVEL >= 1 :
			log( "Population of %s before is %d" % (pCity.getName(), pCity.getPopulation()) )
			log( "Check city culture is %d, at %d, %d" % (pCity.getCulture( pCityOwner.getID() ), pCity.getX(), pCity.getY()) )
		cityPlot = pCity.plot()
		if pCity.getCulture( pCityOwner.getID() ) == 0:
			if LOG_LEVEL >= 1: log( "Forcing culture > 0" )
			pCity.setCulture( pCityOwner.getID(), 1, True )

		try :
			pCity.plot().setOwner( pRevPlayer.getID() )
		except :
			# LFGR_TODO: Can this actually happen?
			print "Error in violent takeover"
			print "ERROR:  Failed to set owner of city, %s at plot %d, %d (%d,%d)"%(pCity.getName(),cityPlot.getX(),cityPlot.getY(),iCityX,iCityY)
			#print "City culture is %d"%(pCity.getCulture(pCityOwner.getID()))

			#pCity = cityPlot.getPlotCity()
			#print "Post culture in %s is %d"%(pCity.getName(),pCity.getCulture(pCityOwner.getID()))
			#pRevPlayer.acquireCity( pCity, False, False )
			# No more revolutions for a while
			#RevData.initCity(pCity)
			# City has become invalid, will cause game to crash if left
			print "Destroying city so game can continue"
			pCity.kill()
			return []


		pCity = cityPlot.getPlotCity()
		if LOG_LEVEL >= 1: log( "Population of %s after is %d" % (pCity.getName(), pCity.getPopulation()) )

		if pCity.getPopulation() < 1:
			if LOG_LEVEL >= 1: log( "Error!  City %s is empty" % (pCity.getName()) )
		
		# Kill off auto-spawned defenders
		# LFGR_TODO: This was delayed in the original code - why? Do we need to do this at all?
		for pUnit in RevUtils.getPlayerUnits( iCityX, iCityY, pRevPlayer.getID() ) :
			pUnit.kill(False,-1)
		
		# lfgr 04/2024: Adjusted occupation timer
		pCity.setOccupationTimer( max( 2, min( 4, pCity.getPopulation() // 2 ) ) )
		
		# Culture
		newCulVal = int( RevOpt.getCultureRateModifier() * max( pCity.getCulture(pCityOwner.getID()), pCity.countTotalCultureTimes100()/200 ) )
		newPlotVal = int( RevOpt.getCultureRateModifier()*max( pCity.plot().getCulture(pCityOwner.getID()), pCity.plot().countTotalCulture()/2 ) )
		RevUtils.giveCityCulture( pCity, pRevPlayer.getID(), newCulVal, newPlotVal, overwriteHigher = False )
		
		# Should buildings stay or some destroyed?
		for [buildingClass,iNum] in buildingClassList :
			buildingType = gc.getCivilizationInfo(pRevPlayer.getCivilizationType()).getCivilizationBuildings(buildingClass)

			if buildingType != BuildingTypes.NO_BUILDING:
				if pCity.getNumRealBuilding( buildingType ) < iNum:
					buildingInfo = gc.getBuildingInfo(buildingType)
					if not buildingInfo.isGovernmentCenter():
						if LOG_LEVEL >= 1: log( "Building %s saved" % (buildingInfo.getDescription()) )
						pCity.setNumRealBuilding( buildingType, iNum )
	
	else : # not revControl
		if LOG_LEVEL >= 1 : log( "Owner keeps control of %s (%d,%d), revs spawning at %d,%d" % (pCity.getName(), iCityX, iCityY, revSpawnLoc[0], revSpawnLoc[1]) )
		
		# City in disorder
		iTurns = 1 + iRevIdx / int(0.7*RevDefs.revReadyFrac*RevDefs.revInstigatorThreshold)
		iTurns = iTurns * ( 10 + min( iRevIdxPerTurn, 5 ) ) // 10
		if iRevIdxPerTurn > 0 :
			iTurns = min( iTurns, iTurnsBetweenRevs - 1 )
		else :
			iTurns = min( iTurns, iTurnsBetweenRevs // 2 + 1 )
		pCity.setOccupationTimer( max( iTurns, 1 ) )
		if LOG_LEVEL >= 1 : log( "City occupation timer set to %d" % (pCity.getOccupationTimer()) )

		# Increase rev-related anger to 3*iTurnsBetweenRevs, but change no more than 2*iTurnsBetweenRevs
		if pCity.getRevRequestAngerTimer() < 3*iTurnsBetweenRevs :
			pCity.changeRevRequestAngerTimer( min( 2*iTurnsBetweenRevs, 3*iTurnsBetweenRevs - pCity.getRevRequestAngerTimer() ) )
		
		if iNumUnits > 0 :
			evacuateEnemyUnits( revSpawnLoc[0], revSpawnLoc[1], pRevPlayer )
		
		# Wound current owner's units?
		unitList = RevUtils.getEnemyUnits( iCityX, iCityY, pRevPlayer.getID(), bOnlyMilitary = True )
		for pUnit in unitList :
			if pUnit.canFight() :
				#if( LOG_LEVEL >= 1 ) : log( "Garrison unit %s pre damage %d"%(pUnit.getName(),pUnit.getDamage()))
				iPreDamage = pUnit.getDamage()
				if iRevIdx > RevDefs.revInstigatorThreshold :
					iDamage = iPreDamage/5 + 20 + game.getSorenRandNum(35,'Revolution: Wound units')
				else :
					iDamage = iPreDamage/5 + 15 + game.getSorenRandNum(25,'Revolution: Wound units')
				iDamage = min([iDamage,90])
				iDamage = max([iDamage,iPreDamage])
				pUnit.setDamage( iDamage, pRevPlayer.getID() )
	
	# Spawn units
	if LOG_LEVEL >= 1: log( "Spawning %d units for city of size %d" % (iNumUnits, pCity.getPopulation()) )

	if bRevControl :
		if iRevCityIdx :
			iNumUnits += 1 # Extra city defender for instigator
		lpNewUnits = createRebelCityUnits( pCity, pRevPlayer, iNumUnits )
	else :
		iSpawnX, iSpawnY = revSpawnLoc
		lpNewUnits = createRebelUnits( pCity, pRevPlayer, iSpawnX, iSpawnY, iNumUnits )

	# LFGR_TODO: Special stuff (general/hero/?) for instigator city.
	
	# Reduce population (from unit spawning)
	# LFGR_TODO: Should this also happen for reinforcements?
	if pCity.getPopulation() > 4 and len( lpNewUnits ) >= 4 :
		deltaPop = min( (len(lpNewUnits)-1) // 3, pCity.getPopulation() - 1 )
		pCity.setPopulation( min( 1, pCity.getPopulation() - deltaPop ) )
		if LOG_LEVEL >= 1 : log( "City population decreased by %d for %d rebel units spawned" % (deltaPop, len( lpNewUnits )) )
	
	# lfgr note: Spy stuff removed.

	# Increase revolutionary sentiment
	if not bRevControl :
		pCity.changeRevolutionIndex( max( 100, 200 + 15 * min( iRevIdxPerTurn, 15 ) ) )
	
	# No more revolutions for a while
	pCity.setRevolutionCounter( iTurnsBetweenRevs )
	
	# Reinforcement
	if bRevControl :
		pCity.setReinforcementCounter( 0 )
	else :
		if bIsBarbRev :
			# Only for determining if revolt has been put down
			pCity.setReinforcementCounter( 5 )
		else :
			iReinforceTurns = RevOpt.getBaseReinforcementTurns() - min( iRevIdxPerTurn, 12 ) // 4
			iReinforceTurns += min( 0, 7 - pCity.getPopulation() ) # Longer for smaller cities
			iReinforceTurns = max( iReinforceTurns, 1, RevOpt.getMinReinforcementTurns(), 4 - pCity.getPopulation() // 2 ) # Min duration
			iReinforceTurns = min( iReinforceTurns, 10 ) # Max duration
			if LOG_LEVEL >= 1 : log( "%s reinforcement in %d turns" % (pCity.getName(), iReinforceTurns) )
			pCity.setReinforcementCounter( iReinforceTurns + 1 )
	
	# Update RevData
	RevData.updateCityVal(pCity, 'RevolutionTurn', game.getGameTurn() )
	if not bIsBarbRev :
		RevData.setRevolutionPlayer( pCity, pRevPlayer.getID() )
	
	return lpNewUnits

# lfgr: Extracted from Revolution.py
@BugUtil.profile( parent = "RevSpawning" )
def spawnReinforcements( pCity, pRevPlayer, iRebelsIn3, iRebelsIn6 ) :
	# type: (CyCity, CyPlayer, int, int) -> List[CyUnit]
	
	# Find suitable location
	revSpawnLoc = generateRebelSpawnPlot( pCity.getX(), pCity.getY(), pRevPlayer, bAllowOnEnemy = False )

	if revSpawnLoc is None :
		log( "ERROR: No rev spawn location possible in %s" % (pCity.getName()) )
		return []

	iSpawnX, iSpawnY = revSpawnLoc

	# Announcements to all relevant players
	announceReinforcements( pCity, pRevPlayer )

	# Compute number of spawned units
	iNumUnits = getNumReinforceUnits( pCity, pRevPlayer, iRebelsIn3 )
	
	if len( RevUtils.getEnemyUnits( iSpawnX, iSpawnY, pRevPlayer.getID() ) ) > 0 :
		log( "WARNING: Spawning on plot with enemy units!" )

	if LOG_LEVEL >= 1 :
		log( "City at %d,%d spawning at %d,%d" % ( pCity.getX(), pCity.getY(), iSpawnX, iSpawnY ) )

	lpNewUnits = createRebelUnits( pCity, pRevPlayer, iSpawnX, iSpawnY, iNumUnits, iRebelsIn3, iRebelsIn6 )
	
	# lfgr: Spy spawning removed
	
	return lpNewUnits

# lfgr: extracted from Revolution.py
def applyEndRevoltEffect( pCity, iRevIdxFactor, iRevIdxPerTurnFactor, iMinEffect, bRealEnd = True ) :
	# type: (CyCity, int, int, int, bool) -> None
	""" RevIdx bonus for a city where a revolt just ended, or mostly ended. If bRealEnd = True, add stuff to history. """
	iRevIdxImprovement = min(
		-pCity.getRevolutionIndex() * iRevIdxFactor // 100,
		pCity.getLocalRevIndex() * iRevIdxPerTurnFactor,
		-iMinEffect )
	
	if LOG_LEVEL >= 2 : CvUtil.pyPrint( "  Local rebellion in %s ended, improving RevIdx by %d" % (pCity.getName(), iRevIdxImprovement) )
	pCity.changeRevolutionIndex( iRevIdxImprovement )
	
	if bRealEnd :
		revIdxHist = RevData.getCityVal( pCity, 'RevIdxHistory' )
		revIdxHist['RevoltEffects'][0] += iRevIdxImprovement
		RevData.updateCityVal( pCity, 'RevIdxHistory', revIdxHist )
