# FfHNames 11/2021 by lfgr

from CvPythonExtensions import *

import BugCore
import RandomNameUtils
import Roman

# globals
gc = CyGlobalContext()

ffhUIOpt = BugCore.game.FfHUI


def onSetPlayerAlive( args ) :
	ePlayer, bNewValue = args

	if bNewValue :
		setNewLeaderName( ePlayer )

# onSetPlayerAlive is not called on game start, since our BUG module isn't registered yet
def onGameStart( _argsList ) :
	for ePlayer in xrange( gc.getMAX_CIV_PLAYERS() ) :
		if gc.getPlayer( ePlayer ).isAlive() :
			# Set bPrecedence = True to rename players in order
			setNewLeaderName( ePlayer, bPrecedence = True )

def setNewLeaderName( ePlayer, bPrecedence = False ) :
	"""
	Rename the given player, if necessary due to duplicates.
	If bPrecedence=True, only check lower-index players for duplicates.
	"""
	pPlayer = gc.getPlayer( ePlayer ) # type: CyPlayer
	szName = pPlayer.getName()
	
	# Find other player's names
	if bPrecedence :
		iMaxPlayer = ePlayer
	else :
		iMaxPlayer = gc.getMAX_CIV_PLAYERS()
	hszOtherNames = set( gc.getPlayer( eLoopPlayer ).getName() for eLoopPlayer in range( iMaxPlayer )
			if eLoopPlayer != ePlayer and gc.getPlayer( eLoopPlayer ).isAlive() )
	
	if szName in hszOtherNames :
		# Replace name
		if ffhUIOpt.isRandomDuplicateLeaderNames() :
			# Try assigning random name
			for _ in range( 100 ) : # Try at most 100 times
				szNewName = RandomNameUtils.generateRandomLeaderHeadName( pPlayer )
				if szNewName is None :
					break
				if szNewName not in hszOtherNames :
					pPlayer.setName( szNewName )
					return
		
		# Add roman numerals
		szNewName = szName
		iCount = 1
		while szNewName in hszOtherNames :
			iCount += 1
			szNewName = szName + u" " + unicode( Roman.toRoman( iCount ) )
		pPlayer.setName( szNewName )