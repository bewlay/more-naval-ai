import CvUtil
import RevCivUtils
from CvPythonExtensions import *

# globals
gc = CyGlobalContext()
rcu = RevCivUtils.RevCivUtils()

def getPuppetCivLeader( args ) :
	( iNewOwner, iOriginalOwner, iNewCityID ) = args
	pCity = gc.getPlayer( iNewOwner ).getCity( iNewCityID )
	
	iOldCivType = gc.getPlayer( iOriginalOwner ).getCivilizationType()
	iCultureOwnerCivType = iOldCivType
	iSplitType = RevCivUtils.SPLIT_PUPPET
	iReligion = -1
	newCivIdx, newLeaderIdx = rcu.chooseNewCivAndLeader( iOldCivType, iCultureOwnerCivType, iSplitType, iReligion, pCity.plot().getX(), pCity.plot().getY() )
	return newCivIdx * gc.getNumLeaderHeadInfos() + newLeaderIdx


def canHavePuppetCivLeader(args):
	iNewOwner, iOriginalOwner, iNewCityID = args
	pCity = gc.getPlayer(iNewOwner).getCity(iNewCityID)

	iOldCivType = gc.getPlayer(iOriginalOwner).getCivilizationType()
	iCultureOwnerCivType = iOldCivType
	iSplitType = RevCivUtils.SPLIT_PUPPET
	iReligion = -1
	newCivIdx, liNewLeaders = rcu.getNewCivAndLeaderList(iOldCivType, iCultureOwnerCivType, iSplitType, iReligion, pCity.plot().getX(), pCity.plot().getY())
	return newCivIdx != -1 and len(liNewLeaders) > 0
