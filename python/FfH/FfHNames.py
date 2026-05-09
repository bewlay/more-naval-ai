# FfHNames 11/2021 by lfgr

from CvPythonExtensions import *
import Roman

# globals
gc = CyGlobalContext()


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

	# Add roman numerals in case there are duplicates
	szNewName = szName
	iCount = 1
	while szNewName in hszOtherNames :
		iCount += 1
		szNewName = szName + u" " + unicode( Roman.toRoman( iCount ) )
	pPlayer.setName( szNewName )