# REVOLUTION_MOD
#
# by jdog5000
# Version 1.5


from CvPythonExtensions import *
import CvUtil
import PyHelpers
import Popup as PyPopup
import math
# --------- Revolution mod -------------
import RevDefs
import RevData
import RevUtils
import RevEvents
import SdToolKitCustom
#RevolutionDCM
import CvScreensInterface
# lfgr
import RevCivUtils
import RevIdxUtils
import InterfaceUtils
# lfgr end

# lfgr: removed RebelTypes stuff

import RevInstances
from TextUtils import getCityTextList
import BugCore

# globals
gc = CyGlobalContext()
PyPlayer = PyHelpers.PyPlayer
PyInfo = PyHelpers.PyInfo
game = CyGame()
localText = CyTranslator()
RevOpt = BugCore.game.Revolution
# lfgr
rcu = RevCivUtils.RevCivUtils()
# lfgr end

class Revolution :

	def __init__(self, customEM, RevOpt):

		print "Initializing Revolution Component"

		####### Revolution Variables ##########

		self.RevOpt = RevOpt
		self.customEM = customEM


		# Debug settings
		self.LOG_DEBUG = RevOpt.isRevDebugMode()
		self.DEBUG_MESS = RevOpt.isShowDebugMessages()

		self.maxCivs = RevOpt.getRevMaxCivs()
		if( self.maxCivs <= 0 ) :
			self.maxCivs = gc.getMAX_CIV_PLAYERS()

		self.offerDefectToRevs = RevOpt.isOfferDefectToRevs()

		self.bArtStyleTypes = RevOpt.isArtStyleTypes()

		self.bAllowBreakVassal = RevOpt.isAllowBreakVassal()
		self.allowSmallBarbRevs = RevOpt.isAllowSmallBarbRevs()

		self.centerPopups = RevOpt.isCenterPopups()

		# Fewer than this number of cities won't try for independence, but change leader
		#self.minCitiesForIndependence = config.getint("Revolution","MinCitiesForIndependence",4)
		# Cities considered close to revolution instigator inside this radius
		self.closeRadius = RevOpt.getCloseRadius()

		#Cities may attempt to leave and join dominant culture
		self.culturalRevolution = RevOpt.isCulturalRevolution()
		# Cities with at least this level of your nationality won't start cultural revolutions
		self.maxNationalityThreshold = RevOpt.getMaxNationality()

		# Cities may ask for religious change or independence for religious reasons
		self.religiousRevolution = RevOpt.isReligiousRevolution()
		# Cities with your state religion can join a religious revolution
		self.allowStateReligionToJoin = RevOpt.isAllowStateReligionToJoin()

		# Cities may ask for civics changes
		self.civicRevolution = RevOpt.isCivicRevolution()

		# Cities may ask/demand changes in leadership
		self.leaderRevolution = RevOpt.isLeaderRevolution()
		self.humanLeaderRevolution = RevOpt.isHumanLeaderRevolution()

		# Cities may ask/demand independence
		# This is the base kind of revolution, not really negotiable if you have this component on
		self.independenceRevolution = True

		#self.warningThreshold = config.getint("Revolution", "HumanWarningThreshold", 900)
		self.warnFrac = RevOpt.getHumanWarnFrac()
		self.warnTurns = RevOpt.getWarnTurns()
		#self.revReadyThreshold = config.getint("Revolution", "JoinRevolutionThreshold", 600)
		self.revReadyFrac = RevDefs.revReadyFrac
		self.revInstigatorThreshold = RevDefs.revInstigatorThreshold
		self.alwaysViolentThreshold = RevDefs.alwaysViolentThreshold
		self.badLocalThreshold = RevDefs.badLocalThreshold
		self.showLocalEffect = 2
		self.showTrend = 5
		self.showStabilityTrend = 2
		self.warWearinessMod = RevOpt.getWarWearinessMod()

		self.turnsBetweenRevs = RevOpt.getTurnsBetweenRevs()
		self.acceptedTurns = RevOpt.getAcceptedTurns()
		self.acquiredTurns = RevOpt.getAcquiredTurns()
		self.buyoffTurns = RevOpt.getBuyoffTurns()
		self.baseReinforcementTurns = RevOpt.getBaseReinforcementTurns()
		self.minReinforcementTurns = RevOpt.getMinReinforcementTurns()
		if( self.minReinforcementTurns < 1 ) :
			self.minReinforcementTurns = 1

		# Increase rate of accumulation of revolution index
		self.revIdxModifier = RevOpt.getIndexModifier()
		self.revIdxOffset = RevOpt.getIndexOffset()
		self.humanIdxModifier = RevOpt.getHumanIndexModifier()
		self.humanIdxOffset = RevOpt.getHumanIndexOffset()
		# Change chances a revolution occurs given conditions
		self.chanceModifier = RevOpt.getChanceModifier()
		# Change strength of revolutions that resort to violence
		self.strengthModifier = RevOpt.getStrengthModifier()
		# Change number of rebel reinforcement units
		self.reinforcementModifier = RevOpt.getReinforcementModifier()

		self.distToCapModifier = RevOpt.getDistanceToCapitalModifier()
		self.happinessModifier = RevOpt.getHappinessModifier()
		self.cultureRateModifier = RevOpt.getCultureRateModifier()
		self.garrisonModifier = RevOpt.getGarrisonModifier()
		self.nationalityModifier = RevOpt.getNationalityModifier()
		# Change strength of city area revolution factor
		self.colonyModifier = RevOpt.getColonyModifier()
		# Change strength of civ size revolution factor
		self.civSizeModifier = RevOpt.getCivSizeModifier()
		# Change strength of religion revolution factor
		self.religionModifier = RevOpt.getReligionModifier()
		# Change strength of losing a city on revolution indices
		self.cityLostModifier = RevOpt.getCityLostModifier()
		# Change strength of gaining a city on revolution indices
		self.cityAcquiredModifier = RevOpt.getCityAcquiredModifier()
		# Change the initial strength of rev culture in a captured city (1.0 = 50% nationality)
		self.revCultureModifier = RevOpt.getCultureRateModifier()

		self.iRevRoll = 20000

		# Stores human leader type when human loses control of civ
		self.humanLeaderType = None

		# RevolutionMP
		# Network protocol header
		self.netRevolutionPopupProtocol = 100
		self.netControlLostPopupProtocol = 101

		######################
		# These are initialized on first end of game turn
		self.iNationalismTech = None
		self.iLiberalismTech = None
		self.iSciMethodTech = None

		############# Register events and popups ##############
		# City and civ events

		#customEM.addEventHandler( "cityBuilt", self.onCityBuilt )
		customEM.addEventHandler( "cityAcquired", self.onCityAcquired )
##********************************
##   LEMMY 101 FIX
##********************************

		# All revolution index update and processing
		customEM.addEventHandler( "PreEndGameTurn", self.onEndGameTurn )
##********************************
##   LEMMY 101 FIX
##********************************
		customEM.addEventHandler( "BeginPlayerTurn", self.onBeginPlayerTurn )
		customEM.addEventHandler( "EndPlayerTurn", self.onEndPlayerTurn )
		customEM.addEventHandler( "ModNetMessage", self.onModNetMessage )

		# Popup launching and handling events
		customEM.addEventHandler( "kbdEvent", self.onKbdEvent )
		self.customEM.setPopupHandler( RevDefs.revolutionPopup, ["revolutionPopup",self.revolutionPopupHandler,self.blankHandler] )
		self.customEM.setPopupHandler( RevDefs.joinHumanPopup, ["joinHumanPopup",self.joinHumanHandler,self.blankHandler] )
		self.customEM.setPopupHandler( RevDefs.controlLostPopup, ["controlLostPopup",self.controlLostHandler,self.blankHandler] )

		self.customEM.setPopupHandler( RevDefs.pickCityPopup, ["pickCityPopup", self.pickCityHandler, self.blankHandler] )
		self.customEM.setPopupHandler( RevDefs.bribeCityPopup, ["bribeCityPopup", self.bribeCityHandler, self.blankHandler] )

	def removeEventHandlers( self ) :
		print "Removing event handlers from Revolution"

		self.customEM.removeEventHandler( "cityAcquired", self.onCityAcquired )

		# All revolution index update and processing
##********************************
##   LEMMY 101 FIX
##********************************
		self.customEM.removeEventHandler( "PreEndGameTurn", self.onEndGameTurn )
##********************************
##   LEMMY 101 FIX
##********************************
		self.customEM.removeEventHandler( "BeginPlayerTurn", self.onBeginPlayerTurn )
		self.customEM.removeEventHandler( "EndPlayerTurn", self.onEndPlayerTurn )
		self.customEM.removeEventHandler( "ModNetMessage", self.onModNetMessage )

		# Popup launching and handling events
		self.customEM.removeEventHandler( "kbdEvent", self.onKbdEvent )

		self.customEM.setPopupHandler( RevDefs.revolutionPopup, ["revolutionPopup",self.blankHandler,self.blankHandler] )
		self.customEM.setPopupHandler( RevDefs.joinHumanPopup, ["joinHumanPopup",self.blankHandler,self.blankHandler] )
		self.customEM.setPopupHandler( RevDefs.controlLostPopup, ["controlLostPopup",self.blankHandler,self.blankHandler] )
		self.customEM.setPopupHandler( RevDefs.revWatchPopup, ["revWatchPopup", self.blankHandler, self.blankHandler] )

		self.customEM.setPopupHandler( RevDefs.pickCityPopup, ["pickCityPopup", self.blankHandler, self.blankHandler] )
		self.customEM.setPopupHandler( RevDefs.bribeCityPopup, ["bribeCityPopup", self.blankHandler, self.blankHandler] )

	def blankHandler( self, playerID, netUserData, popupReturn ) :
		# Dummy handler to take the second event for popup
		return

	def isLocalHumanPlayer( self, playerID ) :
		# Determines whether to show popup to active player
		return (gc.getPlayer(playerID).isHuman()) and game.getActivePlayer() == playerID
#-------------------------------------------------------------------------------------------------
# Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
	def isLocalHumanPlayerOrAutoPlay( self, playerID ) :
		# Determines whether to show popup to active player
		return (gc.getPlayer(playerID).isHuman()  or gc.getPlayer(playerID).isHumanDisabled()) and game.getActivePlayer() == playerID

	def isHumanPlayerOrAutoPlay( self, playerID ) :
		# Determines whether to show popup to active player
		return (gc.getPlayer(playerID).isHuman() or gc.getPlayer(playerID).isHumanDisabled())
#-------------------------------------------------------------------------------------------------
# END Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------

	def loadInfo( self ) :
		# Function loads info required by other components
		if( self.LOG_DEBUG ) : CvUtil.pyPrint( "  Loading revolution data" )


		self.iNationalismTech = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(), RevDefs.sXMLNationalism)
		self.iLiberalismTech = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(), RevDefs.sXMLLiberalism)
		self.iSciMethodTech = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(), RevDefs.sXMLSciMethod)

		self.showLocalEffect = int( self.showLocalEffect*RevUtils.getGameSpeedMod() )


##--- Keyboard handling and Rev Watch popup -------------------------------------------

	def onKbdEvent(self, argsList ):
		'keypress handler'
		eventType,key,mx,my,px,py = argsList

		if ( eventType == RevDefs.EventKeyDown ):
			theKey=int(key)

			#RevolutionDCM
			if( theKey == int(InputTypes.KB_G) and self.customEM.bShift and self.customEM.bCtrl ) :
				# multiplayer warning, need to tell other computers about any city bribery
				CvScreensInterface.showRevolutionWatchAdvisor(self)


	def showPickCityPopup( self, iPlayer ) :
		if (self.isLocalHumanPlayer(iPlayer)):
			playerPy = PyPlayer( iPlayer )
			cityList = playerPy.getCityList()

			popup = PyPopup.PyPopup( RevDefs.pickCityPopup, contextType = EventContextTypes.EVENTCONTEXT_ALL, bDynamic = False)

			if( len(cityList) < 1 ) :
				popup = PyPopup.PyPopup()
				popup.setBodyString( localText.getText("TXT_KEY_REV_WATCH_NO_CITIES", ()) )
				popup.launch()

			popup.setBodyString( localText.getText("TXT_KEY_REV_BRIBE_CITY_WHICH",()) )
			popup.addSeparator()

			popup.createPythonPullDown( 'Cities', 1 )
			cityByRevList = list()
			for [i,city] in enumerate(cityList) :
				pCity = city.GetCy()
				if( not pCity.isNone() ) :
					cityByRevList.append( (pCity.getRevolutionIndex(),pCity.getName(), pCity.getID() ) )

			cityByRevList.sort()
			cityByRevList.reverse()

			for cityData in cityByRevList :
				popup.addPullDownString( "%s"%(cityData[1]), cityData[2], 1 )

			popup.addButton(localText.getText("TXT_KEY_REV_NONE",()))
			#popup.addButton('Bribe This City')
			popup.launch()

			print 'Launch city picker popup'

	def pickCityHandler( self, iPlayerID, netUserData, popupReturn ) :
		if (self.isLocalHumanPlayer(iPlayerID)):
			print 'picking city ...'

			if(  popupReturn.getButtonClicked() == 0 ):
				# None selected
				return

			cityID = popupReturn.getSelectedPullDownValue( 1 )
			if( cityID >= 0 ) :
				pCity = gc.getPlayer( iPlayerID ).getCity( cityID )

				self.showBribeCityPopup( pCity )

	def showBribeCityPopup( self, pCity ) :
		popup = PyPopup.PyPopup(RevDefs.bribeCityPopup,contextType = EventContextTypes.EVENTCONTEXT_ALL)

		popupData = dict()

		popupData['City'] = pCity.getID()
		popupData['Buttons'] = list()

		[bCanBribe, reason] = RevUtils.isCanBribeCity( pCity )

		if( not bCanBribe ) :
			if( reason == 'Violent' ) :
				# Can't be bought
				bodStr = localText.getText("TXT_KEY_REV_BRIBE_CITY_VIOLENT",())%(pCity.getName())
				popup.setBodyString(bodStr)
				popupData['Buttons'] = [['None',-1]]
				popup.setUserData((popupData,))
				popup.launch()
				return

			elif( reason == 'No Need' ) :
				bodStr = localText.getText("TXT_KEY_REV_BRIBE_CITY_NO_NEED",())%(pCity.getName())
				popup.setBodyString(bodStr)
				popupData['Buttons'] = [['None',-1]]
				popup.setUserData((popupData,))
				popup.launch()
				return

			else :
				print 'Error! unknown reason for inability to bribe: %s'%(reason)
				bodStr = localText.getText("TXT_KEY_REV_BRIBE_CITY_NO_NEED",())%(pCity.getName())
				popup.setBodyString(bodStr)
				popupData['Buttons'] = [['None',-1]]
				popup.setUserData((popupData,))
				popup.launch()
				return

		pPlayer = gc.getPlayer( pCity.getOwner() )
		[iSmall,iMed,iLarge] = RevUtils.computeBribeCosts( pCity )
		buttonList = list()
		lastBribeTurn = RevData.getCityVal( pCity, 'BribeTurn' )

		iGold = pPlayer.getGold()
		if( iGold < iSmall ) :
			bodStr = localText.getText("TXT_KEY_REV_BRIBE_CITY_POOR",())
			if( not lastBribeTurn == None and game.getGameTurn() - lastBribeTurn < 20 ) :
				bodStr += '  ' + localText.getText("TXT_KEY_REV_BRIBE_CITY_RECENT",())%(game.getGameTurn() - lastBribeTurn) + '  '
			popup.setBodyString(bodStr)
			popupData['Buttons'] = [['None',-1]]
			popup.setUserData((popupData,))
			popup.launch()
			return
		else :
			bodStr = ''
			if( not lastBribeTurn == None and game.getGameTurn() - lastBribeTurn < 20 ) :
				bodStr += localText.getText("TXT_KEY_REV_BRIBE_CITY_RECENT",())%(game.getGameTurn() - lastBribeTurn) + '  '

			bodStr += localText.getText("TXT_KEY_REV_BRIBE_CITY_OPTIONS",())
			bodStr += '\n\n' + localText.getText("TXT_KEY_REV_BRIBE_CITY_SMALL",())%(iSmall)
			buttonList.append( ['Small', iSmall] )

			if( iGold > iMed ) :
				bodStr += '\n' + localText.getText("TXT_KEY_REV_BRIBE_CITY_MED",())%(iMed)
				buttonList.append( ['Med', iMed] )
				#popup.addButton( localText.getText("TXT_KEY_REV_BRIBE_CITY_BUTTON",())%(iMed) )
				if( iGold > iLarge ) :
					bodStr += '\n' + localText.getText("TXT_KEY_REV_BRIBE_CITY_LARGE",())%(iLarge)
					buttonList.append( ['Large', iLarge] )
					#popup.addButton( localText.getText("TXT_KEY_REV_BRIBE_CITY_BUTTON",())%(iLarge) )

			popup.setBodyString( bodStr )

			popup.addButton( localText.getText("TXT_KEY_REV_BRIBE_CITY_NO_BRIBE",()) )
			buttonList.insert( 0, [localText.getText("TXT_KEY_REV_NONE",()), -1] )
			for [label,cost] in buttonList :
				if( cost > 0 ) :
					popup.addButton( localText.getText("TXT_KEY_REV_BRIBE_CITY_BUTTON",())%(cost) )
			popupData['Buttons'] = buttonList
			popup.setUserData( (popupData,) )

			popup.launch(bCreateOkButton = False)

	def bribeCityHandler( self, iPlayerID, netUserData, popupReturn ) :
		print 'bribing city ...'

		pPlayer = gc.getPlayer( iPlayerID )
		pCity = pPlayer.getCity( netUserData[0]['City'] )
		[buttonLabel, iCost] = netUserData[0]['Buttons'][popupReturn.getButtonClicked()]

		if( buttonLabel == 'None' ) :
			return
		elif( buttonLabel == 'Small' ) :
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Small bribe selected for city %s"%(pCity.getName()))
			RevUtils.bribeCity( pCity, 'Small' )
			pPlayer.changeGold( -iCost )
		elif( buttonLabel == 'Med' ) :
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Med bribe selected for city %s"%(pCity.getName()))
			RevUtils.bribeCity( pCity, 'Med' )
			pPlayer.changeGold( -iCost )
		elif( buttonLabel == 'Large' ) :
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Large bribe selected for city %s"%(pCity.getName()))
			RevUtils.bribeCity( pCity, 'Large' )
			pPlayer.changeGold( -iCost )
		else :
			print 'Error! Bribe city button label %s not recognized, cost is %d'%(buttonLabel,iCost)
			return

		#RevolutionDCM - post bribe popup handling
		if CvScreensInterface.isRevolutionWatchAdvisor():
			CvScreensInterface.showRevolutionWatchAdvisor(self)
		else:
			CvScreensInterface.cityScreenRedraw()

		# lfgr 04/2021: Update CDA (might be displaying revolution values)
		CyInterface().setDirty(InterfaceDirtyBits.Domestic_Advisor_DIRTY_BIT, True)


##--- Standard Event handling functions -------------------------------------------

	def onEndGameTurn( self, argsList ) :

		if( self.iNationalismTech == None ) :
			self.loadInfo()

		self.topCivAdjustments( )


	def onBeginPlayerTurn( self, argsList ) :

		iGameTurn, iPlayer = argsList

		# Stuff at end of previous players turn
		iPrevPlayer = iPlayer - 1
		while( iPrevPlayer >= 0 and not gc.getPlayer(iPrevPlayer).isAlive() ) :
			iPrevPlayer -= 1

		if( iPrevPlayer < 0 ) :
			iPrevPlayer = gc.getBARBARIAN_PLAYER()

		if( iPrevPlayer >= 0 and iPrevPlayer < gc.getBARBARIAN_PLAYER() ) :
			self.checkForRevReinforcement( iPrevPlayer )
			self.checkCivics( iPrevPlayer )

		iNextPlayer = iPlayer + 1
		while( iNextPlayer <= gc.getBARBARIAN_PLAYER() and not gc.getPlayer(iNextPlayer).isAlive() ) :
			iNextPlayer += 1

		if( iNextPlayer > gc.getBARBARIAN_PLAYER() ) :
			iNextPlayer = 0
			while( iNextPlayer < iPlayer and not gc.getPlayer(iNextPlayer).isAlive() ) :
				iNextPlayer += 1

		#if( self.LOG_DEBUG ) : CvUtil.pyPrint(" Beginning turn for player %d, %s"%(iPlayer, gc.getPlayer(iPlayer).getCivilizationDescription(0)))

		# Stuff at beginning of this players turn
		#self.updatePlayerRevolution( argsList )

	def onEndPlayerTurn( self, argsList ) :

		iGameTurn, iPlayer = argsList
		bDoLaunchRev = False

		iNextPlayer = iPlayer + 1
		while( iNextPlayer <= gc.getBARBARIAN_PLAYER() ) :
			if( RevData.revObjectExists(gc.getPlayer(iNextPlayer)) ) :
				# RevolutionMP start - general fix thanks Init
				spawnList = RevData.revObjectGetVal(gc.getPlayer(iNextPlayer), 'SpawnList' )
				if( spawnList != None and len(spawnList) > 0 ) :
				# RevolutionMP end - general fix thanks Init
					bDoLaunchRev = True
					break

			if( not gc.getPlayer(iNextPlayer).isAlive() ) :
				iNextPlayer += 1
			else :
				break

		if( iNextPlayer > gc.getBARBARIAN_PLAYER() ) :
			iGameTurn += 1
			iNextPlayer = 0
			while( iNextPlayer < iPlayer ) :
				if( RevData.revObjectExists(gc.getPlayer(iNextPlayer)) ) :
					# RevolutionMP start - general fix thanks Init
					spawnList = RevData.revObjectGetVal(gc.getPlayer(iNextPlayer), 'SpawnList' )
					if( spawnList != None and len(spawnList) > 0 ) :
					# RevolutionMP end - general fix thanks Init
						bDoLaunchRev = True
						break

				if( not gc.getPlayer(iNextPlayer).isAlive() ) :
					iNextPlayer += 1
				else :
					break

		#if( self.LOG_DEBUG ) : CvUtil.pyPrint(" Next player after %d (%s) is %d (%s) alive %d"%( iPlayer, gc.getPlayer(iPlayer).getCivilizationDescription(0), iNextPlayer, gc.getPlayer(iNextPlayer).getCivilizationDescription(0), gc.getPlayer(iNextPlayer).isAlive()))

		# Stuff at beginning of this players turn
		if( gc.getPlayer(iNextPlayer).isAlive() ) :
			#if( self.LOG_DEBUG ) : CvUtil.pyPrint(" Beginning turn %d for player %d, %s"%(iGameTurn, iNextPlayer, gc.getPlayer(iNextPlayer).getCivilizationDescription(0)))
			self.updatePlayerRevolution( [iGameTurn,iNextPlayer] )

		if( bDoLaunchRev ) :
			self.launchRevolution( iNextPlayer )

	def onCityAcquired( self, argsList):
		'City Acquired'

		owner,playerType,pCity,bConquest,bTrade = argsList

		self.updateLocalRevIndices( game.getGameTurn(), pCity.getOwner(), subCityList = [pCity], bNoApply = True )

##--- Player turn functions ---------------------------------------

	def checkForRevReinforcement( self, iPlayer ) :
		# Checks iPlayer's cities for any rebel reinforcement units that should be spawned
		# Should be called at end of player's turn

		playerPy = PyPlayer( iPlayer )
		cityList = playerPy.getCityList()

		#if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Checking player %d's cities for rebel reinforcement"%(iPlayer))

		for city in cityList :
			pCity = city.GetCy()
			if( pCity.getReinforcementCounter() == 1 ) :
				# Do something awesome
				#if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Checking player %d's city %s for rebel reinforcement spawning"%(iPlayer,pCity.getName()))
				self.doRevReinforcement( pCity )

		return

	def doRevReinforcement( self, pCity ) :
		# type: (CyCity) -> None
		""" Trigger reinforcements if the city is still rebellious. """
		if self.LOG_DEBUG : CvUtil.pyPrint( "  Revolt - Do reinforcements in %s" % pCity.getName() )

		eRevPlayer = RevData.getRevolutionPlayer( pCity )
		ownerID = pCity.getOwner()
		owner = gc.getPlayer(ownerID)

		# City must have valid rev player
		if( eRevPlayer < 0 ) :
			if self.LOG_DEBUG : CvUtil.pyPrint( "    ... aborted: no rev player" )
			return
		if( eRevPlayer == ownerID ) :
			if self.LOG_DEBUG : CvUtil.pyPrint( "    ... aborted: city already captured (?)" )
			# Already captured and got capture bonus
			return

		# FIXME: What is eRevPlayer for barb uprising?
		pRevPlayer = gc.getPlayer( eRevPlayer )
		pRevTeam = gc.getTeam( pRevPlayer.getTeam() )

		if( not pRevTeam.isAtWar(owner.getTeam()) ) :
			# Revolt has ended
			return

		# City must still be rebellious
		revIdx = pCity.getRevolutionIndex()
		localRevIdx = pCity.getLocalRevIndex()
		revIdxHist = RevData.getCityVal( pCity, 'RevIdxHistory' )
		
		if revIdx < self.revInstigatorThreshold:
			# Overall rev idx is low
			localRevEffect = min([-revIdx/10.0,6.0*localRevIdx,-25.0])
			revIdxHist['RevoltEffects'][0] += localRevEffect
			RevData.updateCityVal( pCity, 'RevIdxHistory', revIdxHist )
			pCity.changeRevolutionIndex( int(localRevEffect))
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Local rebellion in %s ends due to low rev index"%(pCity.getName()))
			# LFGR_TODO: Message
			return
		elif localRevIdx < -(self.badLocalThreshold / 2):
			localRevEffect = min([-revIdx/8.0,8.0*localRevIdx,-50.0])
			revIdxHist['RevoltEffects'][0] += localRevEffect
			RevData.updateCityVal( pCity, 'RevIdxHistory', revIdxHist )
			pCity.changeRevolutionIndex( int(localRevEffect))
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Local rebellion in %s ends due to improving situation"%(pCity.getName()))
			# LFGR_TODO: Message
			return
	
		# Possibly delay reinforcements if rebels are very strong.
		rebPower = pCity.area().getPower( pRevPlayer.getID() )
		ownerPower = pCity.area().getPower( ownerID )

		if( rebPower > 2*ownerPower ) :
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Reinforcing %s: Rebel power %d much higher than owner %d in area, No Reinforce for 3 turns"%(pCity.getName(),rebPower,ownerPower))
			pCity.setReinforcementCounter(3 + 1)
			return

		# Do reinforcement
		if( self.LOG_DEBUG and not pRevPlayer.isBarbarian() ) : CvUtil.pyPrint("  Revolt - Reinforcing rebel %s outside %s (%d, %d, owned by %s)"%(pRevPlayer.getCivilizationDescription(0),pCity.getName(),revIdx,localRevIdx,owner.getCivilizationDescription(0)))
		spawnableUnits = RevUtils.getUprisingUnitTypes( pCity, pRevPlayer, True )
		#[iWorker,iBestDefender,iCounter,iAttack] = RevUtils.getHandoverUnitTypes( pCity, pRevPlayer )

		if( len(spawnableUnits) < 1 ) :
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - ERROR!!! No rev units possible in %s"%(pCity.getName()))
			return

		ix = pCity.getX()
		iy = pCity.getY()

		bRecentSuccess = False
		for revCity in PyPlayer(pRevPlayer.getID()).getCityList() :
			pRevCity = revCity.GetCy()
			if( game.getGameTurn() - pRevCity.getGameTurnAcquired() < 6 and pRevCity.getPreviousOwner() == ownerID ) :
				bRecentSuccess = True
				break

		iRebelsIn6 = RevUtils.getNumDefendersNearPlot( ix, iy, pRevPlayer.getID(), iRange = 6 )
		iRebelsIn3 = RevUtils.getNumDefendersNearPlot( ix, iy, pRevPlayer.getID(), iRange = 3 )

		if( pRevPlayer.isBarbarian() ) :

			if( iRebelsIn6 == 0 ) :
#-------------------------------------------------------------------------------------------------
# Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
				localRevEffect = min([-revIdx/8.0,8.0*localRevIdx,-50.0])
				revIdxHist['RevoltEffects'][0] += localRevEffect
				RevData.updateCityVal( pCity, 'RevIdxHistory', revIdxHist )
				pCity.changeRevolutionIndex( int(localRevEffect))
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Barbarian local rebellion in %s put down, idx drop of %d from %d"%(pCity.getName(),localRevEffect,revIdx))

			elif( iRebelsIn3 == 0 ) :
				pCity.setReinforcementCounter(2+1)
				pCity.changeRevolutionIndex( int(min([-revIdx/20.0,4.0*localRevIdx,-25.0])) )
#-------------------------------------------------------------------------------------------------
# END Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------

			else :
				pCity.setReinforcementCounter( 3 + 1 )

			# Never actually spawn reinforcements for barb rebels, just check again for end of revolt
			return

		if( not pRevPlayer.isRebel() ) :

			if( game.getGameTurn() - RevData.getCityVal(pCity, 'RevolutionTurn') > 5 ) :
				if( iRebelsIn3 == 0 ) :
					# No rebel troops near here, effectively end active revolt
#-------------------------------------------------------------------------------------------------
# Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
					localRevEffect = min([-revIdx/6.0,10.0*localRevIdx,-100.0])
					revIdxHist['RevoltEffects'][0] += localRevEffect
					RevData.updateCityVal( pCity, 'RevIdxHistory', revIdxHist )
					pCity.changeRevolutionIndex( int(localRevEffect))
#-------------------------------------------------------------------------------------------------
# END Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Non-rebel: No nearby troops to reinforce, local rebellion in %s ends, with idx drop of %d from %d"%(pCity.getName(),localRevEffect,revIdx))
					return
				else :
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Non-rebel: Reinforcement window over, but nearby fighting continues")
					pCity.setReinforcementCounter(2+1)
					#pCity.changeRevolutionIndex( min([-revIdx/50,4*localRevIdx,-10]) )
					return

		if( bRecentSuccess ) :

			if( iRebelsIn6 == 0 ) :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - No rebel troops to reinforce, but local rebellion continues due to recent success elsewhere")
#-------------------------------------------------------------------------------------------------
# Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
				pCity.changeRevolutionIndex( int(min([-revIdx/50.0,4.0*localRevIdx,-10.0])) )
				pCity.setReinforcementCounter(3+1)
#-------------------------------------------------------------------------------------------------
# END Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------

		else :

			if( iRebelsIn6 == 0 ) :
				# No rebel troops anywhere near here, effectively end active revolt
#-------------------------------------------------------------------------------------------------
# Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
				localRevEffect = min([-revIdx/8.0,8.0*localRevIdx,-80.0])
				revIdxHist['RevoltEffects'][0] += localRevEffect
				RevData.updateCityVal( pCity, 'RevIdxHistory', revIdxHist )
				pCity.changeRevolutionIndex( int(localRevEffect))
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - No rebel troops to reinforce, local rebellion in %s ends, with idx drop of %d from %d"%(pCity.getName(),localRevEffect,revIdx))
				return

			elif( iRebelsIn3 == 0 ) :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - No nearby rebel troops to reinforce, try again later")
				pCity.setReinforcementCounter(2+1)
				pCity.changeRevolutionIndex( int(min([-revIdx/50.0,4.0*localRevIdx,-10.0])) )
#-------------------------------------------------------------------------------------------------
# END Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
				return


		spawnablePlots = RevUtils.getSpawnablePlots( ix, iy, pRevPlayer, bLand = True, bIncludePlot = False, bIncludeCities = False, bSameArea = True, iRange = 1, iSpawnPlotOwner = pRevPlayer.getID(), bCheckForEnemy = True )
		if( len(spawnablePlots) == 0 ) :
			spawnablePlots = RevUtils.getSpawnablePlots( ix, iy, pRevPlayer, bLand = True, bIncludePlot = False, bIncludeCities = False, bSameArea = True, iRange = 2, iSpawnPlotOwner = pRevPlayer.getID(), bCheckForEnemy = True )
		if( len(spawnablePlots) == 0 ) :
			spawnablePlots = RevUtils.getSpawnablePlots( ix, iy, pRevPlayer, bLand = True, bIncludePlot = False, bIncludeCities = False, bSameArea = True, iRange = 3, iSpawnPlotOwner = -1, bCheckForEnemy = True )

		if( len(spawnablePlots) == 0 ) :
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - ERROR!!! No rev spawn location possible in %s"%(pCity.getName()))
			return
		revSpawnLoc = spawnablePlots[game.getSorenRandNum(len(spawnablePlots),'Revolution: Pick rev plot')]

		revStrength = self.reinforcementModifier*(revIdx/(1.0*self.revInstigatorThreshold))
		revStrength *= min([0.13 + pCity.getPopulation()/8.0,2.0])
		if( localRevIdx > 0 ) :
			revStrength *= min([0.5+localRevIdx/10.0,2.0])
		else :
			revStrength *= 1/(2-localRevIdx/3.0)

		if( pCity.getRevolutionCounter() == 0 ) :
			# Rebellion decreases in fervor after counter expires
			revStrength /= 2.0
		elif( game.getGameTurn() - RevData.getCityVal(pCity, 'RevolutionTurn') < 3 ) :
			# Initial fervor
			revStrength *= 1.5

		iDefIn2 = RevUtils.getNumDefendersNearPlot( ix, iy, ownerID, iRange = 2 )
		if( iRebelsIn3 > iDefIn2 ) :
			revStrength *= 1.3
		elif( pRevPlayer.getNumCities() > 0 and iRebelsIn3 > 3 ) :
			# Bolster a successful revolt
			revStrength *= 1.25
		elif( iRebelsIn3 + 2 < iDefIn2 ) :
			# Odds are too steep, some doubt potential for success
			revStrength *= 0.8

		iNumUnits = int(math.floor( revStrength + .5 ))
		if( game.getGameTurn() - RevData.getCityVal(pCity, 'RevolutionTurn') < 3 ) :
			iNumUnits = min([iNumUnits,(pCity.getPopulation())/4,localRevIdx/2])
		elif( pRevPlayer.getNumCities() > 0 and iRebelsIn3 > 2 ) :
			iNumUnits = min([iNumUnits,(pCity.getPopulation())/4,localRevIdx/2])
		else :
			# Been a few turns since revolution, turn down intensity
			iNumUnits = min([iNumUnits,(pCity.getPopulation())/6,localRevIdx/4])

		iNumUnits = max([iNumUnits,1])

		for iPlayer in range(0,gc.getMAX_CIV_PLAYERS()) :

			if( ownerID == iPlayer ) :
				mess = localText.getText("TXT_KEY_REV_MESS_REINFORCEMENTS",(pRevPlayer.getNameKey(), pCity.getName()))
				CyInterface().addMessage(iPlayer, true, gc.getDefineINT("EVENT_MESSAGE_TIME"), mess, "AS2D_CITY_REVOLT", InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT, CyArtFileMgr().getInterfaceArtInfo("INTERFACE_RESISTANCE").getPath(), ColorTypes(7), ix, iy, True, True)
			elif( pRevTeam.isAtWar(gc.getPlayer(iPlayer).getTeam()) and pRevPlayer.canContact(iPlayer) ) :
				mess = localText.getText("TXT_KEY_REV_MESS_REINFORCEMENTS",(pRevPlayer.getNameKey(), pCity.getName()))
				CyInterface().addMessage(iPlayer, false, gc.getDefineINT("EVENT_MESSAGE_TIME"), mess, None, InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT, None, ColorTypes(7), -1, -1, False, False)
			elif( pRevPlayer.getID() == iPlayer ) :
#				mess = localText.getText("TXT_KEY_REV_MESS_YOUR_REINFORCEMENTS",(pRevPlayer.getNameKey(), pCity.getName()))
				mess = localText.getText("TXT_KEY_REV_MESS_YOUR_REINFORCEMENTS",(pRevPlayer.getCivilizationDescription(0), pCity.getName()))
				
				CyInterface().addMessage(iPlayer, true, gc.getDefineINT("EVENT_MESSAGE_TIME"), mess, "AS2D_CITY_REVOLT", InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT, CyArtFileMgr().getInterfaceArtInfo("INTERFACE_RESISTANCE").getPath(), ColorTypes(8), ix, iy, True, True)

		if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Reinforcement strength %.2f, spawning %d reinforcements for city of size %d"%(revStrength,iNumUnits,pCity.getPopulation()))

		if( len(RevUtils.getEnemyUnits( revSpawnLoc[0], revSpawnLoc[1], pRevPlayer.getID())) > 0 ) :
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - ERROR!  Spawning on plot with enemy units!!!")

		if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - City at %d,%d spawning at %d,%d"%(ix,iy,revSpawnLoc[0],revSpawnLoc[1]))

		# Spawn rev units outside city
		newUnitList = list()
		for i in range(0,(iNumUnits*2)) :
			newUnitID = spawnableUnits[game.getSorenRandNum( len(spawnableUnits), 'Revolution: pick unit' )]
			if newUnitID != -1:
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Outside of %s, spawning %s"%(pCity.getName(),PyInfo.UnitInfo(newUnitID).getDescription()))
				newUnit = pRevPlayer.initUnit( newUnitID, revSpawnLoc[0], revSpawnLoc[1], UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )
				newUnitList.append( newUnit )

		for [iNum,newUnit] in enumerate(newUnitList) :
#			if( newUnit.canFight() ) :
				# Injure units to simulate the lack of training in rebel troops
#				iDamage = 10 + game.getSorenRandNum(15,'Revolt - Injure unit')
#				newUnit.setDamage( iDamage, ownerID )

			# Check AI settings
			if( newUnit.isBarbarian() ) :
				if( iNumUnits > 2 and pRevPlayer.AI_unitValue(newUnit.getUnitType(),UnitAITypes.UNITAI_ATTACK_CITY_LEMMING,newUnit.area(), false) > 0 ) :
					newUnit.setUnitAIType( UnitAITypes.UNITAI_ATTACK_CITY_LEMMING )
				elif( newUnit.canFight() ) :
					newUnit.setUnitAIType( UnitAITypes.UNITAI_ATTACK )
			else :
				if( iNum < 2 and iNumUnits + iRebelsIn3 > 2 and pRevPlayer.AI_unitValue(newUnit.getUnitType(),UnitAITypes.UNITAI_ATTACK_CITY,newUnit.area(), false) > 0 ) :
					newUnit.setUnitAIType( UnitAITypes.UNITAI_ATTACK_CITY )
				elif( iNumUnits == 1 and iRebelsIn6 < 3 and pRevPlayer.AI_unitValue(newUnit.getUnitType(),UnitAITypes.UNITAI_PILLAGE,newUnit.area(), false) > 0 ) :
					newUnit.setUnitAIType( UnitAITypes.UNITAI_PILLAGE )
				else :
					iniAI = newUnit.getUnitAIType()
					if( not (iniAI == UnitAITypes.UNITAI_COUNTER or iniAI == UnitAITypes.UNITAI_ATTACK_CITY) ) :
						newUnit.setUnitAIType( UnitAITypes.UNITAI_ATTACK )
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s starting with AI type: %d (ini %d)"%(newUnit.getName(),newUnit.getUnitAIType(),iniAI))

			if( revStrength > 1.5 and pRevPlayer.isRebel() ) :
				iOdds = 10*min([revStrength,4.5]) + 5*pRevPlayer.getNumCities()
				if( iOdds > game.getSorenRandNum(100,'Revolt - Promotion') ) :
					RevUtils.giveRebelUnitFreePromotion( newUnit )

		# Occasionally spawn a spy as well
		if( not game.isOption(GameOptionTypes.GAMEOPTION_NO_ESPIONAGE) ) :
			if( (40 - 20*pRevPlayer.AI_getNumAIUnits(UnitAITypes.UNITAI_SPY) > game.getSorenRandNum(100,'Revolt - Spy')) ) :
				# phungus420 RevUnits Softcoding
				iSpy = pRevPlayer.getBestUnitType(UnitAITypes.UNITAI_SPY)
				# phungus420 end
				if(iSpy != -1):
					if( revStrength > 1.5 and pRevPlayer.canTrain(iSpy,False,False)) :
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Spy spawned in %s"%(pCity.getName()))
						pSpy = pRevPlayer.initUnit( iSpy, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )
						pSpy.setFortifyTurns(gc.getDefineINT("MAX_FORTIFY_TURNS"))

			# Give a little boost to espionage
			pRevTeam.changeEspionagePointsAgainstTeam( owner.getTeam(), game.getSorenRandNum((10+pRevPlayer.getCurrentRealEra())*iNumUnits, 'Revolt - Esp') )

		if( pRevPlayer.isRebel() ) :
			# Set reinforcement timer again
			iReinforceTurns = int(math.floor( self.baseReinforcementTurns*(2.0/(revStrength)) + .5 ))

			minReinfTurns = max([self.minReinforcementTurns, 4 - owner.getCurrentRealEra(), 9 - pCity.getPopulation()])

			iReinforceTurns = max([iReinforceTurns,minReinfTurns])
			if( pCity.getRevolutionCounter() == 0 ) :
				iReinforceTurns += 2
			elif( game.getGameTurn() - RevData.getCityVal(pCity, 'RevolutionTurn') > 3 ) :
				iReinforceTurns += 1

			iReinforceTurns = min([iReinforceTurns,10])
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s reinforcement counter set to %d (min %d)"%(pCity.getName(),iReinforceTurns, minReinfTurns))
			pCity.setReinforcementCounter( iReinforceTurns + 1 )

		else :
			pCity.setReinforcementCounter( 3 + 1 )


	def checkCivics( self, iPlayer ) :

		pPlayer = gc.getPlayer( iPlayer )

		if( pPlayer.getNumCities() == 0 or pPlayer.isBarbarian() ) :
			return

		#if( iPlayer == game.getActivePlayer() ) :
		#CvUtil.pyPrint("Revolt - Checking civics for player %d"%(iPlayer))

		curCivics = list()

		for i in range(0,gc.getNumCivicOptionInfos()):
			curCivics.append( pPlayer.getCivics(i) )

		prevCivics = RevData.revObjectGetVal( pPlayer, "CivicList" )

		if( prevCivics == None or not len(prevCivics) == len(curCivics) ) :
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Setting civics for %s"%(pPlayer.getCivilizationDescription(0)))
			RevEvents.recordCivics( iPlayer )
			return

		else :
			sumRevIdx = 0
			for [i,curCivic] in enumerate(curCivics) :
				if( not curCivic == prevCivics[i] ) :
					curInfo  = gc.getCivicInfo(curCivic)
					prevInfo = gc.getCivicInfo(prevCivics[i])
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s changing civic option %d from %s to %s"%(pPlayer.getCivilizationDescription(0),i,prevInfo.getDescription(),curInfo.getDescription()))
					iRevIdxChange = curInfo.getRevIdxSwitchTo() - prevInfo.getRevIdxSwitchTo()
					sumRevIdx += iRevIdxChange

					if( not iRevIdxChange == 0 ) :

						keyList = list()
						if( curInfo.getRevDemocracyLevel()*prevInfo.getRevDemocracyLevel() < 0 ) :
							# Democracy level changed sign
							keyList.extend( ['Location', 'Colony', 'Nationality'] )
						elif( curInfo.getRevReligiousFreedom()*prevInfo.getRevReligiousFreedom() < 0 ) :
							# Rel freedom changed sign
							keyList.append( 'Religion' )
						elif( curInfo.getRevLaborFreedom()*prevInfo.getRevLaborFreedom() < 0 ) :
							# Democracy level changed sign
							keyList.extend( ['Colony', 'Nationality'] )

						if( self.LOG_DEBUG and len(keyList) > 0 ) :
							keyStr = ''
							for key in keyList :
								keyStr += key + ', '
							CvUtil.pyPrint("  Revolt - Increasing effect for cities with high %s factors"%(keyStr))

						for city in PyPlayer( iPlayer ).getCityList() :
							pCity = city.GetCy()
							revIdxHist = RevData.getCityVal(pCity,'RevIdxHistory')

							mod = 1.0
							for key in keyList :
								if( revIdxHist[key][0] > 9 ) :
									mod *= 1.8
								elif( revIdxHist[key][0] > 3 ) :
									mod *= 1.4
								elif( revIdxHist[key][0] > 0 ) :
									mod *= 1.2

							mod = min([3.0,mod])
							iThisRevIdxChange = int( mod*iRevIdxChange + 0.5 )

							if( mod > 1.0 and self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Increasing civic effects in %s"%(pCity.getName()))

#-------------------------------------------------------------------------------------------------
# Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
							pCity.changeRevolutionIndex( int(iThisRevIdxChange) )
#-------------------------------------------------------------------------------------------------
# END Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
							revIdxHist['Events'][0] += iThisRevIdxChange
							RevData.updateCityVal(pCity,'RevIdxHistory',revIdxHist)

			if( not sumRevIdx == 0 ) :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Avg net effect for %s: %d"%(pPlayer.getCivilizationDescription(0),sumRevIdx))

			# REVOLUTION_ALERTS 03/2021 lfgr
			if sumRevIdx > 0 :
				InterfaceUtils.addMessage( iPlayer, PyHelpers.getText(
						"[COLOR_NEGATIVE_TEXT]The change of civics has increased revolutionary sentiment throughout your empire[COLOR_REVERT]"  ) ) # LFGR_TODO: Translate
			elif sumRevIdx < 0 :
				InterfaceUtils.addMessage( iPlayer, PyHelpers.getText(
						"[COLOR_POSITIVE_TEXT]The change of civics has reduced revolutionary sentiment throughout your empire[COLOR_REVERT]"  ) ) # LFGR_TODO: Translate


	def updatePlayerRevolution( self, argsList ):

		iGameTurn, iPlayer = argsList

		if( gc.getPlayer(iPlayer).isBarbarian() ) :
			return

		if( self.iNationalismTech == None ) :
			self.loadInfo()

		if( self.LOG_DEBUG and iGameTurn%25 == 0 and iPlayer == 0 ) : CvUtil.pyPrint("  Revolt - Rev index report for year %d"%(game.getGameTurnYear()))

		self.updateRevolutionCounters( iGameTurn, iPlayer )
		self.updateLocalRevIndices( iGameTurn, iPlayer )
		self.checkForBribes( iGameTurn, iPlayer )
		self.checkForRevolution( iGameTurn, iPlayer )

		self.incrementRevIdxHistory( iGameTurn, iPlayer )


		return

	def updateRevolutionCounters( self, iGameTurn, iPlayer ) :

		playerPy = PyPlayer( iPlayer )
		cityList = playerPy.getCityList()

		for city in cityList :
			pCity = city.GetCy()

			if( not RevData.revObjectExists(pCity) ) :
				RevData.initCity(pCity)
				continue

			if( pCity.getRevolutionCounter() > 0 ) :
				pCity.changeRevolutionCounter( -1 )

			if( RevData.getCityVal(pCity, 'SmallRevoltCounter') > 0 ) :
				RevData.changeCityVal(pCity, 'SmallRevoltCounter', -1 )

			if( RevData.getCityVal( pCity, 'WarningCounter' ) > 0 ) :
				RevData.changeCityVal(pCity, 'WarningCounter', -1 )

			if( pCity.getReinforcementCounter() > 0 ) :
				pCity.changeReinforcementCounter(-1)

	# lfgr 08/2023: Removed RevIdx string building, some refactoring.
	def updateLocalRevIndices( self, iGameTurn, iPlayer, subCityList = None, bNoApply = False ) :
		# type: (int, int, Optional[List[CyCity]], bool) -> None
		"""
		Updates the revolution effects local to each city.
		If subCityList is not None, only consider the cities in subCityList
		Always cities' LocalRevIdx (i.e., per turn). Adjusts RevIdx (total) if out of bounds.
		If not bNoApply, apply rev idx per current turn, and update history.
		"""
		# LFGR_TODO: if bNoApply, this only updates LocalRevIndex [per turn]. Probably can still cause OOS errors, and
		#  may not even be useful.
		# LFGR_TODO: This is currently used in updateCityScreen(). This will probably cause OOS errors

		# Includes some "Lemmy101 RevolutionMP edit"s

		pPlayer = gc.getPlayer(iPlayer)
		if pPlayer.getNumCities() == 0 :
			return

		playerPy = PyPlayer( iPlayer )

		# Gather some data on the civ that will effect every city
		capital = pPlayer.getCapitalCity()
		if capital is None or capital.isNone() :
			# LFGR_TODO: Don't return here!
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - WARNING!  %s have cities but no capital on turn %d"%(pPlayer.getCivilizationDescription(0),iGameTurn))
			return

		# Make sure cache is loaded
		if self.iNationalismTech is None :
			self.loadInfo()

		if subCityList is None :
			cityList = playerPy.getCityList()
		else :
			cityList = subCityList
		
		pPlayerCache = RevIdxUtils.PlayerRevIdxCache( iPlayer )

		for city in cityList :
			try:
				pCity = city.GetCy()
			except AttributeError :
				# already a CyCity object
				pCity = city

			# 05/2020 lfgr: REV_REFACTORING
			pCityHelper = RevIdxUtils.CityRevIdxHelper( pCity, pPlayerCache )

			# Check if city can revolt at all
			if RevIdxUtils.cityCannotRevoltStr( pCity ) is not None :
				continue

			# RevIdx history and previous revIdx
			revIdxHist = RevData.getCityVal( pCity, 'RevIdxHistory' )
			if revIdxHist is None :
				revIdxHist = RevDefs.initRevIdxHistory()

			### MAIN COMPUTATION
			# Fill history (LFGR_TODO: Not if bNotApply?)
			if not bNoApply :
				revIdxHist['Happiness'] = [pCityHelper.computeHappinessRevIdx()] + revIdxHist['Happiness'][0:RevDefs.revIdxHistLen-1]
				revIdxHist['Location'] = [pCityHelper.computeLocationRevIdx()] + revIdxHist['Location'][0:RevDefs.revIdxHistLen-1]
				revIdxHist['Colony'] = [0] + revIdxHist['Colony'][0:RevDefs.revIdxHistLen-1] # TODO: Remove
				revIdxHist['Religion'] = [pCityHelper.computeReligionRevIdx()] + revIdxHist['Religion'][0:RevDefs.revIdxHistLen-1]
				revIdxHist['Nationality'] = [pCityHelper.computeNationalityRevIdx()] + revIdxHist['Nationality'][0:RevDefs.revIdxHistLen-1]
				revIdxHist['Health'] = [0] + revIdxHist['Health'][0:RevDefs.revIdxHistLen-1] # LFGR_TODO
				revIdxHist['Garrison'] = [pCityHelper.computeGarrisonRevIdx()] + revIdxHist['Garrison'][0:RevDefs.revIdxHistLen-1]
				revIdxHist['Disorder'] = [pCityHelper.computeDisorderRevIdx()] + revIdxHist['Disorder'][0:RevDefs.revIdxHistLen-1]
				iCrimeIdx = pCityHelper.computeCrimeRevIdx() # LFGR_TODO: History?

			# lfgr note: This includes feedback. Before, feedback was left out of LocalRevIdx
			iLocalRevIdx = pCityHelper.computeRevIdx()

			# Update local RevIndex whenever called
			pCity.setLocalRevIndex( iLocalRevIdx )

			if not bNoApply :
				# Change revolution indices based on local effects
				pCity.changeRevolutionIndex( iLocalRevIdx )
				pCity.updateRevIndexAverage()
	
				RevData.updateCityVal(pCity, 'RevIdxHistory', revIdxHist )
	
				# Incase interturn stuff set out of range
				if pCity.getRevolutionIndex() < 0 :
					pCity.setRevolutionIndex( 0 )
				elif pCity.getRevolutionIndex() > 2*self.alwaysViolentThreshold :
					pCity.setRevolutionIndex( 2*self.alwaysViolentThreshold )

	# LFGR_TODO: CyPlayer.changeStabilityIndex() and CyPlayer.updateStabilityIndexAverage() are now (almost) unused

	def checkForBribes( self, iGameTurn, iPlayer ) :

		pPlayer = gc.getPlayer( iPlayer )
		if( pPlayer.isHuman() or pPlayer.isBarbarian() ) :
			return

		iGold = pPlayer.getGold()

		if( iGold < 100 or pPlayer.isAnarchy() ) :
			return

		cityList = PyPlayer( iPlayer ).getCityList()
		for city in cityList :
			pCity = city.GetCy()

			[bCanBribeCity, reason] = RevUtils.isCanBribeCity(pCity)
			if( not bCanBribeCity ) :
				continue

			bribeTurn = RevData.getCityVal( pCity, 'BribeTurn' )

			if( not bribeTurn == None ) :
				if( game.getGameTurn() - bribeTurn < 20 ) :
					# Costs will be highly elevated from recent bribe
					continue

			[iSmall,iMed,iLarge] = RevUtils.computeBribeCosts(pCity)

			if( iSmall > iGold ) :
				continue

			revIdx = pCity.getRevolutionIndex()
			localRevIdx = pCity.getLocalRevIndex()

			if( localRevIdx > 2*self.badLocalThreshold ) :
				# Consider small bribe to buy time
				iOdds = min([2*iGold/iSmall, 8])
				if( iOdds > game.getSorenRandNum(100,'Rev: bribe city') ) :
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s bribing %s with small bribe to buy time, odds %d"%(pPlayer.getCivilizationDescription(0),pCity.getName(),iOdds))
					RevUtils.bribeCity( pCity, 'Small' )
					iGold = pPlayer.getGold()
					if( iGold < 100 ) :
						return
					continue

			elif( localRevIdx < -self.badLocalThreshold/2 ) :
				# Situation should be improving on its own, perhaps a bribe could make city not want to join a revolt
				if( revIdx < self.revInstigatorThreshold and iMed < iGold - 30 ) :
					iOdds = min([2*iGold/iMed, 10])
					if( iOdds > game.getSorenRandNum(100,'Rev: bribe city') ) :
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s bribing %s with med bribe so that it won't join a revolt, odds %d"%(pPlayer.getCivilizationDescription(0),pCity.getName(),iOdds))
						RevUtils.bribeCity( pCity, 'Med' )
						iGold = pPlayer.getGold()
						if( iGold < 100 ) :
							return
						continue

			if( revIdx > 0.8*self.revInstigatorThreshold and iLarge < iGold - 45 ) :
					iOdds = min([2*iGold/iLarge - localRevIdx, 5])
					if( iOdds > game.getSorenRandNum(100,'Rev: bribe city') ) :
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s bribing %s with large bribe so that it won't join a revolt, odds %d"%(pPlayer.getCivilizationDescription(0),pCity.getName(),iOdds))
						RevUtils.bribeCity( pCity, 'Large' )
						iGold = pPlayer.getGold()
						if( iGold < 100 ) :
							return
						continue

	def checkForRevolution( self, iGameTurn, iPlayer ) :

		pPlayer = gc.getPlayer(iPlayer)
		if( pPlayer.getNumCities() == 0 ) :
			return

		if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Checking %s for revolutions"%(pPlayer.getCivilizationDescription(0)))
		playerPy = PyPlayer( iPlayer )
		cityList = playerPy.getCityList()

		# lfgr 08/2023: Check if player can revolt at all
		szCannotRevolt = RevIdxUtils.playerCannotRevoltStr( pPlayer )
		if szCannotRevolt :
			if self.LOG_DEBUG : CvUtil.pyPrint( "    " + szCannotRevolt )
			return

		revReadyCities = list()
		revInstigatorCities = list()
		warnCities = list()

		capRevIdx = 0

		for city in cityList :
			pCity = city.GetCy()

			# lfgr settlements
			if( pCity.isSettlement() and ( pCity.getOwner() == pCity.getOriginalOwner() ) ) :
				continue
			# end lfgr

			revIdx = pCity.getRevolutionIndex()
			prevRevIdx = RevData.getCityVal(pCity, 'PrevRevIndex')
			localRevIdx = pCity.getLocalRevIndex()

			numUnhappy = RevUtils.getModNumUnhappy( pCity, self.warWearinessMod )
			if( numUnhappy > 0 ) :
				cityThreshold = max([int( self.revInstigatorThreshold - 2.5*self.revInstigatorThreshold*numUnhappy/pCity.getPopulation() ),int(self.revInstigatorThreshold/6.0)])
			elif( localRevIdx > 60 and pCity.getPopulation() < pCity.getHighestPopulation() - 1 ) :
				cityThreshold = max([int( self.revInstigatorThreshold*50/(1.0*localRevIdx)), int(self.revInstigatorThreshold/2.0)])
			else :
				cityThreshold = self.revInstigatorThreshold

			if( revIdx >= int( self.warnFrac*cityThreshold ) and pCity.getRevolutionCounter() == 0 ) :
				if(  RevData.getCityVal(pCity, 'WarningCounter') == 0 ) :
					# Warn human of impending revolution (note can't instigate on warning turn)
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  REVOLT - %s (%s) is over %d warning threshold in year %d!!!!"%(pCity.getName(),pPlayer.getCivilizationDescription(0),int( self.warnFrac*cityThreshold ),game.getGameTurnYear()))
					warnCities.append(pCity)
				elif( revIdx > cityThreshold and prevRevIdx > cityThreshold ) :
					# City meets instigator criteria
					revInstigatorCities.append(pCity)

			if( revIdx > int(self.revReadyFrac*cityThreshold) and prevRevIdx > int(self.revReadyFrac*cityThreshold) and pCity.getRevolutionCounter() == 0 ) :
				# City meets revolution ready criteria
				revReadyCities.append( pCity )

			RevData.updateCityVal( pCity, 'PrevRevIndex', revIdx )

		instigator = None

		# LFGR_TODO: turn this and instigator bit above into a function, when revolt odds > 0 then is an instigator
		if( len(revInstigatorCities) > 0 ) :
			for pCity in revInstigatorCities :
				revIdx = pCity.getRevolutionIndex()
				localRevIdx = pCity.getLocalRevIndex()
				revIdxHist = RevData.getCityVal(pCity,'RevIdxHistory')

				gsm = RevUtils.getGameSpeedMod()

				odds = (1000.0*revIdx)/(self.iRevRoll)
				factors = ""

				if( localRevIdx < 0 ) :
					if( localRevIdx < -gsm*self.badLocalThreshold ) :
						odds -= 1.5*localRevIdx + 30
						if( odds > 0 ) :
							odds = odds/4
						factors += 'Quickly imp local, '
					else :
						odds -= 1.5*localRevIdx
						odds = odds/2
						factors += 'Imp local, '

				elif( localRevIdx > gsm*self.badLocalThreshold ) :

					odds *= 2.0
					factors += 'Bad local, '

					avgHappiness = 0
					for happi in revIdxHist['Happiness'] :
						avgHappiness += happi
					avgHappiness /= len(revIdxHist['Happiness'])

					if( revIdxHist['Health'][0] > 20 ) :
						odds = max([250.0,odds*2.5])
						factors += 'Starvation, '
					elif( revIdxHist['Disorder'][0] > 20 ) :
						odds = max([180.0,odds*1.8])
						factors += 'Disorder, '
					elif( avgHappiness > 12 ) :
						odds = max([120.0,odds*1.5])
						factors += 'Unhappy, '
					elif( localRevIdx > gsm*max([int(2.5*self.badLocalThreshold),12]) ) :
						odds *= 1.5
						factors += 'Quickly worsening local, '

					if( revIdxHist['Garrison'] < -5 ) :
						odds *= 0.6
						odds = min([odds,150.0])
						factors += 'Very strong gar, '
					elif( revIdxHist['Garrison'] < -3 ) :
						odds *= 0.8
						odds = min([odds,200.0])
						factors += 'Strong gar, '

				odds = int( self.chanceModifier*odds )

				eventSum = 0
				for event in revIdxHist['Events'] :
					eventSum += event

				if( eventSum < -50 ) :
					odds *= 0.75
					factors += 'Very pos events, '
				elif( eventSum < -20 ) :
					odds *= 0.9
					factors += 'Pos events, '
				elif( eventSum > 300 ) :
					if( revIdxHist['Events'][0] > 330 ) :
						odds = min([ odds*4.0, max([odds,300]) ])
						factors += 'Lost capital, '
					else :
						odds *= 2.0
						factors += 'Ext neg events, '
				elif( eventSum > 120 ) :
					odds *= 1.2
					factors += 'Very Neg events, '
				elif( eventSum > 50 ) :
					odds *= 1.1
					factors += 'Neg events, '

				# Do revolution?
				odds = min([odds, 500])

				if( odds > game.getSorenRandNum( 1000, 'Revolt - do revolution?' ) ) :
					if( self.LOG_DEBUG ) :
						CvUtil.pyPrint("  REVOLT - %s (%s) has decided to launch a revolution with index %d (%d local) and odds %.1f in year %d!!!!"%(pCity.getName(),pPlayer.getCivilizationDescription(0),revIdx,localRevIdx,odds/10.0,game.getGameTurnYear()))
						CvUtil.pyPrint("  REVOLT - Factors effecting timing: %s"%(factors))
					instigator = pCity
					break

		if( not instigator == None ) :
			self.pickRevolutionStyle( pPlayer, instigator, revReadyCities )

		elif( len(warnCities) > 0 ) : # LFGR_TODO: Update this
			for pCity in warnCities :
				RevData.updateCityVal( pCity, 'WarningCounter', self.warnTurns )

			if( self.isLocalHumanPlayer(pPlayer.getID())  ) :
				pTeam = gc.getTeam( pPlayer.getTeam() )
				# Additions by Caesium et al
				caesiumtR = CyUserProfile().getResolutionString(CyUserProfile().getResolution())
				caesiumtextResolution = caesiumtR.split('x')
				caesiumpasx = int(caesiumtextResolution[0])/10
				caesiumpasy = int(caesiumtextResolution[1])/10
				popup = PyPopup.PyPopup(bDynamic=False)
				if( self.centerPopups ) : popup.setPosition(3*caesiumpasx,3*caesiumpasy)
				# End additions by Caesium et al
				popup.setHeaderString( localText.getText("TXT_KEY_REV_WARN_TITLE",()) )
				bodStr = localText.getText("TXT_KEY_REV_WARN_NEWS",()) + ' '
				bodStr += getCityTextList(warnCities) + ' '
				bodStr += ' ' + localText.getText("TXT_KEY_REV_WARN_CONTEMPLATING",())
				# lfgr 08/2023: Removed RevIdx overview
				if( pTeam.getAtWarCount(True) > 0 ) :
					bodStr += '\n\n' + localText.getText("TXT_KEY_REV_WARN_WARS",())
				else :
					bodStr += '\n\n' + localText.getText("TXT_KEY_REV_WARN_GLORY",())
					if( pPlayer.getCitiesLost() > 0 ) :
						bodStr += "  " + localText.getText("TXT_KEY_REV_WARN_LOST",())
					bodStr += '  ' + localText.getText("TXT_KEY_REV_WARN_TEMPORARY",())
				popup.setBodyString( bodStr )

				# Center camera on city
				CyCamera().JustLookAt( warnCities[0].plot().getPoint() )

				popup.launch()


	def incrementRevIdxHistory( self, iGameTurn, iPlayer ) :
		# Increment RevIdxHistory fields that are not handled by updateLocalRevIndices

		for city in PyPlayer(iPlayer).getCityList() :
			pCity = city.GetCy()

			revIdxHist = RevData.getCityVal( pCity, 'RevIdxHistory' )

			# Bump turn for fields that are not handled by updateLocalRevIndices
			revIdxHist['RevoltEffects'] = [0] + revIdxHist['RevoltEffects'][0:RevDefs.revIdxHistLen-1]
			revIdxHist['Events'] = [0] + revIdxHist['Events'][0:RevDefs.revIdxHistLen-1]

			RevData.updateCityVal( pCity, 'RevIdxHistory', revIdxHist )


##--- Game turn functions  ---------------------------------------------------

	def topCivAdjustments( self ) :
		# Penalty on top score/power to help keep game even
		# Benefit for highest culture

		powerList = list()
		cultureList = list()
		scoreList = list()

		for iPlayer in range(0,gc.getMAX_CIV_PLAYERS()) :
			pPlayer = gc.getPlayer( iPlayer )
			if( pPlayer.isAlive() and not pPlayer.getNumCities() == 0 ) :
				powerList.append((pPlayer.getPower(),iPlayer))
				cultureList.append((pPlayer.countTotalCulture(),iPlayer))
				scoreList.append((game.getPlayerScore(iPlayer),iPlayer))


		powerList.sort()
		powerList.reverse()
		cultureList.sort()
		cultureList.reverse()
		scoreList.sort()
		scoreList.reverse()

		iNumTopPlayers = (game.countCivPlayersAlive() - 4)/3
		if( self.LOG_DEBUG and game.getGameTurn()%25 == 0 ) : CvUtil.pyPrint("  Revolt - Adjustments for top %d players"%(iNumTopPlayers))

		for [iRank,listElement] in enumerate(powerList[0:iNumTopPlayers]) :
			[iPower,iPlayer] = listElement
			if( (3*iPower)/2 > powerList[0][0] ) :
				iPowerEffect = 3 - (3*iRank)/iNumTopPlayers
				if( self.LOG_DEBUG and game.getGameTurn()%25 == 0 ) : CvUtil.pyPrint("  Revolt - %s have %dth most power, effect: %d"%(gc.getPlayer(iPlayer).getCivilizationDescription(0),iRank+1,-iPowerEffect))
				gc.getPlayer(iPlayer).changeStabilityIndex(-iPowerEffect)

		for [iRank,listElement] in enumerate(cultureList[0:iNumTopPlayers]) :
			[iCulture,iPlayer] = listElement
			if( (3*iCulture)/2 > cultureList[0][0] ) :
				iCultureEffect = 3 - (3*iRank)/iNumTopPlayers
				if( self.LOG_DEBUG and game.getGameTurn()%25 == 0 ) : CvUtil.pyPrint("  Revolt - %s have %dth most culture, effect: %d"%(gc.getPlayer(iPlayer).getCivilizationDescription(0),iRank+1,iCultureEffect))
				gc.getPlayer(iPlayer).changeStabilityIndex(iCultureEffect)

		for [iRank,listElement] in enumerate(scoreList[0:iNumTopPlayers]) :
			[iScore,iPlayer] = listElement
			if( (3*iScore)/2 > scoreList[0][0] ) :
				iScoreEffect = 3 - (3*iRank)/iNumTopPlayers
				if( self.LOG_DEBUG and game.getGameTurn()%25 == 0 ) : CvUtil.pyPrint("  Revolt - %s have %dth highest score, effect: %d"%(gc.getPlayer(iPlayer).getCivilizationDescription(0),iRank+1,-iScoreEffect))
				gc.getPlayer(iPlayer).changeStabilityIndex(-iScoreEffect)


#-------------------------------------------------------------------------------------------------
# Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
	def revIndexAdjusted( self, pCity):

		if(pCity.isCapital()):
			return pCity.getRevolutionIndex()-self.revInstigatorThreshold
		else:
			return pCity.getRevolutionIndex()

##--- Revolution setup functions ---------------------------------------------
#-------------------------------------------------------------------------------------------------
# END Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------

	# lfgr 06/2023 refactoring
	def isRevolutionPeaceful( self, pInstigatorCity, lpRevCities ) :
		# type: (CyCity, List[CyCity]) -> bool
		iInstRevIdx = pInstigatorCity.getRevolutionIndex()
		iInstLocalIdx = pInstigatorCity.getLocalRevIndex()
		
		if iInstRevIdx > self.alwaysViolentThreshold :
			# Situation really bad
			if self.LOG_DEBUG : CvUtil.pyPrint( "  Revolt - Violent, above always violent threshold" )
			return False
		elif pInstigatorCity.getNumRevolts( pInstigatorCity.getOwner() ) == 0 :
			# First revolution is always peaceful
			if self.LOG_DEBUG : CvUtil.pyPrint( "  Revolt - Peaceful, first revolution" )
			return True
		else :
			modNumUnhappy = RevUtils.getModNumUnhappy( pInstigatorCity, self.warWearinessMod ) # LFGR_TODO: Use different func
			if int( 200 * modNumUnhappy / pInstigatorCity.getPopulation() ) > game.getSorenRandNum( 100, 'Rev' ) :
				if self.LOG_DEBUG : CvUtil.pyPrint( "  Revolt - Violent due to Unhappiness" )
				return False

			if iInstLocalIdx > self.badLocalThreshold :
				# Situation deteriorating rapidly
				if self.LOG_DEBUG : CvUtil.pyPrint( "  Revolt - Violent due to rapidly deteriorating situation" )
				return False

			if len( lpRevCities ) == 1 :
				# Single city is not violent except for the above reasons
				if self.LOG_DEBUG : CvUtil.pyPrint( "  Revolt - Peaceful, single city" )
				return True

			# Compute violent modifier
			iViolentThresholdMod = 80

			for pCivic in PyPlayer( pInstigatorCity.getOwner() ).iterCivicInfos() :
				iViolentThresholdMod += pCivic.getRevViolentMod()

			if iInstLocalIdx < 0 :
				iViolentThresholdMod += 10

			iViolentThreshold = self.alwaysViolentThreshold * iViolentThresholdMod // 100

			if iInstRevIdx > iViolentThreshold :
				iOdds = 100 * (iInstRevIdx - iViolentThreshold) / (self.alwaysViolentThreshold - iViolentThreshold)
				if self.LOG_DEBUG : CvUtil.pyPrint( "  Revolt - Odds for violence are %d" % iOdds )
				if game.getSorenRandNum( 100, 'Rev' ) < iOdds :
					return False

			return True


	def pickRevolutionStyle( self, pPlayer, instigator, revReadyCities ) :
		bReinstatedOnRevolution = False
#-------------------------------------------------------------------------------------------------
# Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
	   # MOVED ELSEWHERE
#-------------------------------------------------------------------------------------------------
# END Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------

		iPlayer = pPlayer.getID()
		pTeam = gc.getTeam( pPlayer.getTeam() )

		revCities = list()
		revCities.append(instigator)
		revInCapital = instigator.isCapital()

		instRevIdx = instigator.getRevolutionIndex()

		# Who will join them?  City must be either in area with instigator, or close to instigator but not in homeland
		# City must also be able to revolt now (not recently revolted)
		for pCity in revReadyCities :
			if( pCity.getRevolutionCounter() == 0 and not pCity.getID() == instigator.getID() ) :

				if( pCity.area().getID() == instigator.area().getID() ) :
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s is in the area, joining revolution"%(pCity.getName()))
					revCities.append(pCity)
					revInCapital = (revInCapital or pCity.isCapital())

				elif( plotDistance( pCity.getX(), pCity.getY(), instigator.getX(), instigator.getY() ) <= self.closeRadius and not pCity.area().getID() == pPlayer.getCapitalCity().area().getID() ) :
					# Catch cities on small island chains ... not in same area, but close and not in homeland
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s is nearby, joining revolution"%(pCity.getName()))
					revCities.append(pCity)
					revInCapital = (revInCapital or pCity.isCapital())

		# Peaceful or violent?
		bPeaceful = self.isRevolutionPeaceful( instigator, revCities ) # lfgr 06/2023 refactoring


		if self.LOG_DEBUG and bPeaceful : CvUtil.pyPrint("  Revolt - Peaceful revolution")

#-------- Check for still existing violent revolution for instigator
		# lfgr 03/2024: Lots of Lemmy101 RevolutionMP edits not highlighted anymore.
		if( not bPeaceful and pPlayer.getNumCities() > 1 and not RevData.getCityVal(instigator, 'RevolutionTurn') == None ) :
			iRevPlayer = RevData.getRevolutionPlayer( instigator )
			if iRevPlayer >= 0 :
				pRevPlayer = gc.getPlayer( iRevPlayer )
				if pRevPlayer.isAlive() and pRevPlayer.isRebel() \
						and gc.getTeam( pRevPlayer.getTeam() ).isRebelAgainst( pTeam.getID() ) \
						and pTeam.isAtWar( pRevPlayer.getTeam() ) :
					# Found existing revolution!
					
					# LFGR_TODO: Outsource into function
					bCanJoin = True
	
					# Cannot join human rebel
					# TODO: Create popup offering peace to human rebel player in this circumstance?
					if( pRevPlayer.isHuman() ) :
						bCanJoin = False
	
					# Cannot join if host is vassal of a human
					if( bCanJoin and pTeam.isAVassal() ) :
						for teamID in range(0,gc.getMAX_CIV_TEAMS()) :
							if( pTeam.isVassal(teamID) and gc.getTeam(teamID).isHuman() ) :
								bCanJoin = False
								break
					
					# Cannot join if rebel is vassal of a human
					if( bCanJoin and gc.getTeam(pRevPlayer.getTeam()).isAVassal() ) :
						for teamID in range(0,gc.getMAX_CIV_TEAMS()) :
							if( gc.getTeam(pRevPlayer.getTeam()).isVassal(teamID) and gc.getTeam(teamID).isHuman() ) :
								bCanJoin = False
								break
	
					if( bCanJoin ) :
						# Build list of cities still actively participating in the revolt
						bJoin = False
						citiesInRevolt = list()
						for city in PyPlayer(pPlayer.getID()).getCityList() :
							pCity = city.GetCy()
							if RevData.getRevolutionPlayer( pCity ) == iRevPlayer :
								# LFGR_TODO: Check the conditions here...
								if( pCity.getReinforcementCounter() > 0 and pCity.getReinforcementCounter() < 9 - pRevPlayer.getCurrentRealEra()/2 ) :
									if( self.LOG_DEBUG ) :
										bInRev = False
										for pRevCity in revCities :
											if( pCity.getID() == pRevCity.getID() ) :
												bInRev = True
												break
										if( bInRev ) :
											CvUtil.pyPrint("  Revolt - %s actively revolting"%(pCity.getName()))
										else :
											CvUtil.pyPrint("  Revolt - Unlisted %s also actively revolting"%(pCity.getName()))
									citiesInRevolt.append(pCity)
	
						if( game.getGameTurn() - RevData.getCityVal(instigator, 'RevolutionTurn') < 3*self.turnsBetweenRevs ) :
							# Recent revolt
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Joining recent revolt")
							bJoin = True
						elif( len(citiesInRevolt) > 0 ) :
							# Continuing revolt
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Joining still active revolt")
							bJoin = True
	
						if( bJoin ) :
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Cities revolt civ type %s is fighting owner"%(pRevPlayer.getCivilizationDescription(0)))
							if( pRevPlayer.isRebel() and not (pRevPlayer.isMinorCiv() or pPlayer.isMinorCiv()) ) :
								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Joining existing revolution with %s"%(pRevPlayer.getCivilizationDescription(0)))
	
								# Filter cities for this revolt
								joinRevCities = list()
								for pCity in revCities :
									cityDist = plotDistance( pCity.getX(), pCity.getY(), instigator.getX(), instigator.getY() )
									if RevData.getRevolutionPlayer( pCity ) == iRevPlayer :
										joinRevCities.append(pCity)
										if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s has same rev type"%(pCity.getName()))
									elif( pCity.getRevolutionIndex() > self.revInstigatorThreshold and cityDist <= 0.8*self.closeRadius ) :
										joinRevCities.append(pCity)
										if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s is close and over threshold, joining"%(pCity.getName()))
	
								# Create list of cities to handover to end revolt
								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Creating list of cities to request to be handed over")
								handoverCities = list()
								toSort = list()
								for pCity in citiesInRevolt :
									revIdx = pCity.getRevolutionIndex()
									if( pCity.isCapital() ) :
										if( revIdx > self.alwaysViolentThreshold and pCity.getLocalRevIndex() > 0 ) :
											if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s (capital), %d qualifies as revolting city"%(pCity.getName(),revIdx))
											handoverCities.append( pCity )
											toSort.append(pCity)
									else :
										if( revIdx > self.alwaysViolentThreshold or (revIdx > self.revInstigatorThreshold and pCity.getLocalRevIndex() > -self.badLocalThreshold/2) ) :
											if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s, %d qualifies as revolting city"%(pCity.getName(),revIdx))
											handoverCities.append( pCity )
											toSort.append(pCity)
								for pCity in joinRevCities :
									bInList = False
									for handoverCity in handoverCities :
										if( pCity.getID() == handoverCity.getID() ) :
											bInList = True
											break
	
									if( not bInList ) :
										revIdx = pCity.getRevolutionIndex()
										if( pCity.isCapital() ) :
											if( revIdx > self.alwaysViolentThreshold and pCity.getLocalRevIndex() > 0 ) :
												if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s (capital), %d qualifies as joining city"%(pCity.getName(),revIdx))
												handoverCities.append( pCity )
												toSort.append(pCity)
										else :
											if( revIdx > self.alwaysViolentThreshold or (revIdx > self.revInstigatorThreshold and pCity.getLocalRevIndex() > -self.badLocalThreshold/2) ) :
												if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s, %d qualifies as joining city"%(pCity.getName(),revIdx))
												handoverCities.append( pCity )
												toSort.append(pCity)
	
								toSort.sort(key=lambda i: (self.revIndexAdjusted(i), i.getName()))
								toSort.reverse()
	
								# Make order list of cities to request to be handed over
								handoverCities = list()
								for pCity in toSort :
									handoverCities.append( pCity )
	
								# Limit ambitions to something player could conceivably accept ...
								maxHandoverCount = (3*pPlayer.getNumCities())/4
								handoverCities = handoverCities[0:maxHandoverCount]
	
								# If asking for capital, put it first in list
								capID = pPlayer.getCapitalCity().getID()
								for [i,pCity] in enumerate(handoverCities) :
									if( capID == pCity.getID() ) :
										handoverCities.pop(i)
										handoverCities = [pCity] + handoverCities
										break
	
								if( len(handoverCities) > 0 ) :
	
									# Enable only for debugging handover cities
									if( False ) :
										if(pPlayer.isHuman() or pPlayer.isHumanDisabled()):
											game.setForcedAIAutoPlay(pPlayer.getID(), 0, false )
										iPrevHuman = game.getActivePlayer()
										RevUtils.changeHuman( pPlayer.getID(), iPrevHuman )
	
									if( self.LOG_DEBUG ) :
										str = "  Revolt - Offering peace in exchange for handover of: "
										for pCity in handoverCities :
											str += "%s, "%pCity.getName()
										if( self.LOG_DEBUG ) : CvUtil.pyPrint(str)
	
									# Determine strength of rebellion
									bIsJoinWar = False
									bOfferPeace = True
									revArea = instigator.area()
									revPower = revArea.getPower(pRevPlayer.getID())
									pPower = revArea.getPower(pPlayer.getID())
									if( revPower > 0 ) :
										powerFrac = pPower/(1.0*revPower)
									else :
										powerFrac = 10.0
	
									if( powerFrac < 1.5 ) :
										# Rebels rival homeland power
										if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Rebels rival homeland power, limiting enlistment")
										bIsJoinWar = True
	
									handoverStr = getCityTextList(handoverCities)
									cityStr = getCityTextList(joinRevCities)
	
									bodStr = pRevPlayer.getName() + localText.getText("TXT_KEY_REV_LEADER",()) + ' ' + pRevPlayer.getCivilizationDescription(0)
									bodStr += ' ' + localText.getText("TXT_KEY_REV_JOINREV_OFFER",())
									bodStr += ' ' + handoverStr
									bodStr += localText.getText("TXT_KEY_REV_JOINREV_PEACE",())%(cityStr)
	
									joinRevCityIdxs = list()
									for pCity in joinRevCities :
										joinRevCityIdxs.append( pCity.getID() )
	
									handoverCityIdxs = list()
									for pCity in handoverCities :
										handoverCityIdxs.append( pCity.getID() )
	
									specialDataDict = { 'iRevPlayer' : pRevPlayer.getID(), 'bIsJoinWar' : bIsJoinWar, 'bOfferPeace' : bOfferPeace, 'HandoverCities' : handoverCityIdxs }
									revData = RevDefs.RevoltData( pPlayer.getID(), game.getGameTurn(), joinRevCityIdxs, 'independence', bPeaceful, specialDataDict )
	
									revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
									iRevoltIdx = len(revoltDict.keys())
									revoltDict[iRevoltIdx] = revData
									RevData.revObjectUpdateVal( pPlayer, 'RevoltDict', revoltDict )
	
									self.makeRevolutionDecision( pPlayer, iRevoltIdx, joinRevCities, 'independence', bPeaceful, bodStr )
	
									return
	
								else :
									if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - No cities qualify for handover request, try something else")

		# All of these have violent and peaceful paths
#-------- Check if instigator influence by other culture -> try to join
		if( self.culturalRevolution and instigator.plot().calculateCulturePercent(iPlayer) <= self.maxNationalityThreshold ) :
			#cultOwnerID = instigator.plot().calculateCulturalOwner()
			# calculateCulturalOwner rules out dead civs ...
			maxCulture = 30
			cultOwnerID = -1
			for idx in range(0,gc.getMAX_CIV_PLAYERS()) :
				if( instigator.plot().getCulture( idx ) > maxCulture ) :
					maxCulture = instigator.plot().getCulture( idx )
					cultOwnerID = idx

			if( cultOwnerID >= 0 and cultOwnerID < gc.getBARBARIAN_PLAYER() and not gc.getPlayer(cultOwnerID).getTeam() == pPlayer.getTeam() ) :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s has majority culture from other player %d, asking to join"%(instigator.getName(),cultOwnerID))
				cultCities = list()
				for pCity in revCities :
					maxCulture = 30
					cityCultOwnerID = -1
					for idx in range(0,gc.getMAX_CIV_PLAYERS()) :
						if( pCity.plot().getCulture( idx ) > maxCulture ) :
							maxCulture = pCity.plot().getCulture( idx )
							cityCultOwnerID = idx

					if( cityCultOwnerID == cultOwnerID ) :
						cultCities.append(pCity)
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s also wants to go to other civ"%(pCity.getName()))

				cultPlayer = gc.getPlayer( cultOwnerID )
				cultTeam = gc.getTeam( cultPlayer.getTeam() )

				bodStr = getCityTextList(cultCities, bPreCity = True, second = localText.getText("TXT_KEY_REV_ALONG_WITH",()) + ' ', bPostIs = True)

				if( bPeaceful ) :

					if( cultPlayer.isAlive() and not cultPlayer.isMinorCiv() ) :
						if( pTeam.isAtWar(cultTeam.getID()) ) :
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Owner at war with city's cultural civ")
							if( pTeam.canChangeWarPeace(cultTeam.getID()) ) :
								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Ask for end to hostilities")

						if( pPlayer.getCurrentRealEra() - cultPlayer.getCurrentRealEra() > 1 ) :
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Tech divide with cultural player, ask for charity")

					# ask to join other civ, if denied get angrier
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Peaceful, asking to join the %s"%(cultPlayer.getCivilizationDescription(0)))

					pRevPlayer = None
					bIsJoinWar  = False
					joinPlayer = None

					if( cultPlayer.isAlive() ) :
						bodStr += ' ' + localText.getText("TXT_KEY_REV_CULT_PEACE_JOIN",()) + ' ' + cultPlayer.getCivilizationDescription(0) + '.'
						# Will only form pRevPlayer if human join player rebuffs revolutionaries
						if( cultPlayer.isStateReligion() ) :
							giveRelType = cultPlayer.getStateReligion()
						else :
							if( 50 > game.getSorenRandNum(100,'Rev') ) :
								giveRelType = None
							else :
								giveRelType = -1
						# lfgr: form splinter civ of joinPlayer
						joinPlayer = cultPlayer
						# lfgr note: split allowed
						[pRevPlayer,bIsJoinWar] = self.chooseRevolutionCiv( cultCities, bJoinCultureWar = False, bReincarnate = True, bJoinRebels = False, bSpreadRebels = False, giveRelType = giveRelType, bMatchCivics = False, iSplitType = RevCivUtils.SPLIT_ALLOWED, iForcedCivilization = joinPlayer.getCivilizationType() )
						# end lfgr

					else :
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Cult player is dead, trying to reform")
						bodStr += ' ' + localText.getText("TXT_KEY_REV_CULT_PEACE_REFORM",()) + ' ' + cultPlayer.getCivilizationShortDescription(0) + '.'
						pRevPlayer = cultPlayer


					bodStr += '  ' + localText.getText("TXT_KEY_REV_CULT_PEACE",())

				else :
					# demand to join other civ, if denied, fight!
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Violent, demanding to join the %s"%(cultPlayer.getCivilizationDescription(0)))

					# lfgr note: that ist the same as above, only with joinPlayer(=cultPlayer) instead of cultPlayer
					if( cultPlayer.isAlive() ) :
						joinPlayer = cultPlayer
						if( joinPlayer.isStateReligion() ) :
							giveRelType = joinPlayer.getStateReligion()
						else :
							if( 50 > game.getSorenRandNum(100,'Rev') ) :
								giveRelType = None
							else :
								giveRelType = -1
						# lfgr: form splinter civ of joinPlayer
						# lfgr note: split allowed
						[pRevPlayer,bIsJoinWar] = self.chooseRevolutionCiv( cultCities, bJoinCultureWar = True, bReincarnate = True, bJoinRebels = True, bSpreadRebels = False, giveRelType = giveRelType, bMatchCivics = False, iSplitType = RevCivUtils.SPLIT_ALLOWED, iForcedCivilization = joinPlayer.getCivilizationType() )
						# end lfgr
						if( joinPlayer.getID() == pRevPlayer.getID() ) :
							joinPlayer = None
						else :
							if( self.allowSmallBarbRevs and len(cultCities) == 1 ) :
								if( instRevIdx < int(1.2*self.revInstigatorThreshold) ) :
									if( not instigator.area().isBorderObstacle(pPlayer.getTeam()) ) :
										pRevPlayer = gc.getPlayer( gc.getBARBARIAN_PLAYER() )
										bIsJoinWar = False
										if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Small, disorganized Revolution")
					else :
						pRevPlayer = cultPlayer
						bIsJoinWar = False
						joinPlayer = None
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Cult player is dead, trying to reform")

					if( not joinPlayer == None ) :
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Violent, demanding to join the %s"%(joinPlayer.getCivilizationDescription(0)))
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - If denied, will form/join the %s, alive: %d"%(pRevPlayer.getCivilizationDescription(0),pRevPlayer.isAlive()))
						bodStr += ' ' + localText.getText("TXT_KEY_REV_CULT_VIOLENT_JOIN",()) + ' ' + joinPlayer.getCivilizationDescription(0) + '.'
						if( bIsJoinWar ) :
							bodStr += '  ' + localText.getText("TXT_KEY_REV_CULT_VIOLENT_JOIN_DENY",()) + ' ' + pRevPlayer.getCivilizationShortDescription(0) + '.'
						else :
							if( pRevPlayer.isBarbarian() ) :
								bodStr += '  ' + localText.getText("TXT_KEY_REV_CULT_VIOLENT_JOIN_DENY_BARB",())
							elif( pRevPlayer.isAlive() ) :
								bodStr += '  ' + localText.getText("TXT_KEY_REV_CULT_VIOLENT_JOIN_DENY_ALIVE",())%(pRevPlayer.getCivilizationDescription(0))
							else :
								bodStr += '  ' + localText.getText("TXT_KEY_REV_CULT_VIOLENT_JOIN_DENY",()) + ' ' + pRevPlayer.getCivilizationShortDescription(0) + '.'
							if( gc.getTeam(pPlayer.getTeam()).canDeclareWar(joinPlayer.getTeam()) ) :
								bodStr += '  ' + localText.getText("TXT_KEY_REV_CULT_VIOLENT_JOIN_DECLARE_WAR",()) + ' ' +  joinPlayer.getCivilizationDescription(0) + '.'
					else :
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Violent, demanding to join the %s"%(pRevPlayer.getCivilizationDescription(0)))
						if( pRevPlayer.isBarbarian() ) :
							bodStr += ' ' + localText.getText("TXT_KEY_REV_CULT_VIOLENT_REFORM_BARB",())
						elif( not pRevPlayer.isAlive() ) :
							bodStr += ' ' + localText.getText("TXT_KEY_REV_CULT_VIOLENT_REFORM",()) + ' ' + pRevPlayer.getCivilizationShortDescription(0) + '.'
						else :
							bodStr += ' ' + localText.getText("TXT_KEY_REV_CULT_VIOLENT_JOIN",()) + ' ' + pRevPlayer.getCivilizationDescription(0) + '.'

					bodStr += '  ' + localText.getText("TXT_KEY_REV_CULT_VIOLENT_1",())
					if( not joinPlayer == None ) :
						bodStr += '  ' + localText.getText("TXT_KEY_REV_THE",()) + ' ' + joinPlayer.getCivilizationDescription(0) + ' ' + localText.getText("TXT_KEY_REV_CULT_VIOLENT_2",())
						if( pRevPlayer.isBarbarian() ) :
							bodStr += ' ' + localText.getText("TXT_KEY_REV_CULT_VIOLENT_BARB",())
						else :
							bodStr += ' ' + localText.getText("TXT_KEY_REV_CULT_VIOLENT_FIGHT",()) + ' ' + pRevPlayer.getCivilizationShortDescription(0) + '.'
					else :
						if( pRevPlayer.isBarbarian() ) :
							pass
						elif( pRevPlayer.isAlive() ) :
							bodStr += '  ' + localText.getText("TXT_KEY_REV_CULT_VIOLENT_ENEMY",()) + ' ' + pRevPlayer.getCivilizationDescription(0) + '.'

					bodStr += '  ' + localText.getText("TXT_KEY_REV_CULT_VIOLENT_FINAL",())

				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %d cities in revolution"%(len(cultCities)))
				assert( len(cultCities) > 0 )

				specialDataDict = {'iRevPlayer' : pRevPlayer.getID(), 'bIsJoinWar' : bIsJoinWar }
				if( not joinPlayer == None ) :
					specialDataDict['iJoinPlayer'] = joinPlayer.getID()
				cityIdxs = list()
				for pCity in cultCities :
					cityIdxs.append( pCity.getID() )
				revData = RevDefs.RevoltData( pPlayer.getID(), game.getGameTurn(), cityIdxs, 'independence', bPeaceful, specialDataDict )

				revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
				iRevoltIdx = len(revoltDict.keys())
				revoltDict[iRevoltIdx] = revData
				RevData.revObjectUpdateVal( pPlayer, 'RevoltDict', revoltDict )

				self.makeRevolutionDecision( pPlayer, iRevoltIdx, cultCities, 'independence', bPeaceful, bodStr )

				return

#-------- Check for religious revolution
		stateRel = pPlayer.getStateReligion()
		if( self.religiousRevolution and pPlayer.isStateReligion() and stateRel >= 0 ) :
			revRel = None

			# Check holy city instigating
			if( instigator.isHolyCity() ) :

				if( not instigator.isHolyCityByType(stateRel) ) :

					for relType in range(0,gc.getNumReligionInfos()) :
						if( instigator.isHolyCityByType(relType) and not stateRel == relType ) :
							if( self.allowStateReligionToJoin or not instigator.isHasReligion(stateRel) ) :
								revRel = relType
								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Instigator is rival religion (%s) holy city"%(gc.getReligionInfo( revRel ).getDescription()))
								break

			# Check for significant minority religion
			if( revRel == None  ) :
				if( self.allowStateReligionToJoin or not instigator.isHasReligion(stateRel) ) :
					if( len(revCities) >= 3 ) :
						# Must be large movement of like minded cities
						maxCount = 0
						maxCountRel = -1
						for relType in range(0,gc.getNumReligionInfos()) :
							if( instigator.isHasReligion(relType) and not stateRel == relType ) :
								relCount = 0
								for pCity in revCities :
									if( pCity.isHasReligion(relType) ) :
										if( pCity.isHasReligion(stateRel) ) :
											relCount += .5
										else :
											relCount += 1
								if( relCount > maxCount ) :
									maxCount = relCount
									maxCountRel = relType

						# Is the best good enough?
						if( maxCount >= 3 ) :
							revRel = maxCountRel
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Instigator and enough others have %s"%(gc.getReligionInfo( revRel ).getDescription()))

			# Decide how to revolt
			if( not revRel == None ) :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Religious revolution")

				relCities = list()
				for pCity in revCities :
					if( pCity.isHasReligion(revRel) ) :
						if( self.allowStateReligionToJoin or not pCity.isHasReligion(stateRel) ) :
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s has %s"%(pCity.getName(),gc.getReligionInfo( revRel ).getDescription()))
							relCities.append(pCity)

				if( bPeaceful ) :
					# Check if there are civics they would like changed
					newRelCivic = None

					[level,optionType] = RevUtils.getReligiousFreedom( iPlayer )
					[newLevel,newRelCivic] = RevUtils.getBestReligiousFreedom( iPlayer, optionType )

					if( not newRelCivic == None and newLevel > level ) :
						if( level < -5 or (newLevel > 5 and level < 0) ) :
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Asking for change from %s to %s"%(gc.getCivicInfo(pPlayer.getCivics(optionType)).getDescription(),gc.getCivicInfo(newRelCivic).getDescription()))

							bodStr = getCityTextList(relCities, bPreCity = True, bPostIs = True)

							# Can't pay them enough so they don't feel oppressed

							if( level < -5 ) :
								bodStr += ' ' + localText.getText("TXT_KEY_REV_REL_THEOCRACY1",()) + ' ' + gc.getCivicInfo(pPlayer.getCivics(optionType)).getDescription() + ".  " + localText.getText("TXT_KEY_REV_REL_THEOCRACY2",()) + ' ' + gc.getCivicInfo(newRelCivic).getDescription() + '.'
							else :
								bodStr += ' ' + localText.getText("TXT_KEY_REV_REL_FREE_REL1",()) + ' ' + gc.getCivicInfo(newRelCivic).getDescription() + '.  ' + localText.getText("TXT_KEY_REV_REL_FREE_REL2",()) + ' ' + gc.getReligionInfo(stateRel).getDescription()
								bodStr += ' ' + localText.getText("TXT_KEY_REV_REL_PRACTICE",()) + ' ' + gc.getReligionInfo(revRel).getDescription() + '.'
							bodStr += '\n\n' + localText.getText("TXT_KEY_REV_HONORING",())

							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %d cities in revolution"%(len(relCities)))
							assert( len(relCities) > 0 )

							specialDataDict = { 'iNewCivic' : newRelCivic }
							cityIdxs = list()
							for pCity in relCities :
								cityIdxs.append( pCity.getID() )
							revData = RevDefs.RevoltData( pPlayer.getID(), game.getGameTurn(), cityIdxs, 'civics', bPeaceful, specialDataDict )

							revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
							iRevoltIdx = len(revoltDict.keys())
							revoltDict[iRevoltIdx] = revData
							RevData.revObjectUpdateVal( pPlayer, 'RevoltDict', revoltDict )

							self.makeRevolutionDecision( pPlayer, iRevoltIdx, relCities, 'civics', bPeaceful, bodStr )

							return

					# Ask for switch of state religions?
					revRelCount = pPlayer.getHasReligionCount(revRel)
					stateRelCount = pPlayer.getHasReligionCount(stateRel)
					if( revRelCount > stateRelCount/4 ) :

						bodStr = getCityTextList(relCities, bPreCity = True, bPostIs = True)

						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Asking change in state religion, %d practice new, %d practice state"%(revRelCount,stateRelCount))
						totalRevIdx = 0
						for pCity in relCities :
							totalRevIdx += pCity.getRevolutionIndex()
						iBuyOffCost = totalRevIdx/(17-pPlayer.getCurrentRealEra()) + game.getSorenRandNum(50+10*pPlayer.getCurrentRealEra(),'Rev')
						#iBuyOffCost = (60 + 12*pPlayer.getCurrentRealEra())*len(relCities) + game.getSorenRandNum(50+10*pPlayer.getCurrentRealEra(),'Rev')
						if( not pPlayer.isHuman() ) : iBuyOffCost = int( iBuyOffCost*.7 )
						iBuyOffCost = max( [iBuyOffCost,pPlayer.getGold()/10 + game.getSorenRandNum(50,'Rev')] )
						bodStr += ' ' + localText.getText("TXT_KEY_REV_REL_CHANGE",()) + ' ' + gc.getReligionInfo( revRel ).getDescription() + '.'
						bodStr += '  ' + localText.getText("TXT_KEY_REV_CURRENTLY",()) + ' %d '%(revRelCount) + localText.getText("TXT_KEY_REV_REL_NEW_REL",()) + ' %d '%(stateRelCount) + localText.getText("TXT_KEY_REV_REL_STATE_REL",())
						bodStr += '\n\n' + localText.getText("TXT_KEY_REV_REL_HONORING",())

						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %d cities in revolution, buyoff cost %d"%(len(relCities),iBuyOffCost))
						assert( len(relCities) > 0 )
						specialDataDict = { 'iNewReligion' : revRel, 'iBuyOffCost' : iBuyOffCost }
						cityIdxs = list()
						for pCity in relCities :
							cityIdxs.append( pCity.getID() )
						revData = RevDefs.RevoltData( pPlayer.getID(), game.getGameTurn(), cityIdxs, 'religion', bPeaceful, specialDataDict )

						revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
						iRevoltIdx = len(revoltDict.keys())
						revoltDict[iRevoltIdx] = revData
						RevData.revObjectUpdateVal( pPlayer, 'RevoltDict', revoltDict )

						self.makeRevolutionDecision( pPlayer, iRevoltIdx, relCities, 'religion', bPeaceful, bodStr )

						return

					# Ask for independence
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Asking for independence for religious reasons")

					# Prune for only close cities since cities in area may be quite far away
					indCities = list()
					for pCity in relCities :
						# Add only cities near instigator in first pass
						cityDist = plotDistance( pCity.getX(), pCity.getY(), instigator.getX(), instigator.getY() )
						if( cityDist <= self.closeRadius ) :
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s is close enough to instigator to join in independence quest"%(pCity.getName()))
							indCities.append(pCity)

					for pCity in relCities :
						if( not pCity in indCities ) :
							# Add cities a little further away that are also near another rebelling city
							cityDist = plotDistance( pCity.getX(), pCity.getY(), instigator.getX(), instigator.getY() )
							if( cityDist <= 2.0*self.closeRadius ) :
								for iCity in indCities :
									cityDist = min([cityDist, plotDistance( pCity.getX(), pCity.getY(), iCity.getX(), iCity.getY() )])

								if( cityDist <= 0.8*self.closeRadius ) :
									if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s is close enough to another rebelling city to join in independence quest"%(pCity.getName()))
									indCities.append(pCity)

					bodStr = getCityTextList(indCities, bPreCity = True, bPostIs = True)

					#iBuyOffCost = (60 + 12*pPlayer.getCurrentRealEra())*len(indCities) + game.getSorenRandNum(50+10*pPlayer.getCurrentRealEra(),'Rev')
					totalRevIdx = 0
					for pCity in indCities :
						totalRevIdx += pCity.getRevolutionIndex()
					iBuyOffCost = totalRevIdx/(17-pPlayer.getCurrentRealEra()) + game.getSorenRandNum(50+10*pPlayer.getCurrentRealEra(),'Rev')
					if( not pPlayer.isHuman() ) : iBuyOffCost = int( iBuyOffCost*.7 )
					iBuyOffCost = max( [iBuyOffCost,pPlayer.getGold()/12 + game.getSorenRandNum(50,'Rev')] )

					# lfgr: split forced
					[pRevPlayer,bIsJoinWar] = self.chooseRevolutionCiv( indCities, bJoinCultureWar = False, bReincarnate = True, bJoinRebels = False, bSpreadRebels = False, giveRelType = revRel, bMatchCivics = True, iSplitType = RevCivUtils.SPLIT_FORCED )
					# lfgr end

					vassalStyle = None
					if( not pTeam.isAVassal() and pTeam.isVassalStateTrading() ) :
						if( totalRevIdx/len(indCities) < self.revInstigatorThreshold ) :
							if( pRevPlayer.AI_getAttitude(pPlayer.getID()) == AttitudeTypes.ATTITUDE_FRIENDLY or pRevPlayer.AI_getAttitude(pPlayer.getID()) == AttitudeTypes.ATTITUDE_PLEASED ) :
								vassalStyle = 'free'
								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Vassal style %s chosen"%(vassalStyle))

					if( not vassalStyle == None ) :
						bodStr += ' ' + localText.getText("TXT_KEY_REV_REL_PEACE_VASSAL_1",()) + ' ' + gc.getReligionInfo( revRel ).getDescription() + '.'
						bodStr += '  ' + localText.getText("TXT_KEY_REV_REL_PEACE_VASSAL_2",()) + ' ' + pRevPlayer.getCivilizationShortDescription(0) + ' ' + localText.getText("TXT_KEY_REV_REL_PEACE_VASSAL_3",())
					else :
						bodStr += ' ' + localText.getText("TXT_KEY_REV_REL_PEACE_IND_1",()) + ' ' + gc.getReligionInfo( revRel ).getDescription() + '.'
						bodStr += '  ' + localText.getText("TXT_KEY_REV_REL_PEACE_IND_2",()) + ' ' + gc.getReligionInfo(pPlayer.getStateReligion()).getDescription() + ' ' + localText.getText("TXT_KEY_REV_REL_PEACE_IND_3",()) + ' ' + pRevPlayer.getCivilizationShortDescription(0) + '.'
						bodStr += '\n\n' + localText.getText("TXT_KEY_REV_REL_PEACE",())

					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %d cities in revolution, buyoff cost %d"%(len(indCities),iBuyOffCost))
					assert( len(indCities) > 0 )
					specialDataDict = { 'iRevPlayer' : pRevPlayer.getID(), 'iBuyOffCost' : iBuyOffCost, 'vassalStyle' : vassalStyle }
					cityIdxs = list()
					for pCity in indCities :
						cityIdxs.append( pCity.getID() )
					revData = RevDefs.RevoltData( pPlayer.getID(), game.getGameTurn(), cityIdxs, 'independence', bPeaceful, specialDataDict )

					revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
					iRevoltIdx = len(revoltDict.keys())
					revoltDict[iRevoltIdx] = revData
					RevData.revObjectUpdateVal( pPlayer, 'RevoltDict', revoltDict )

					self.makeRevolutionDecision( pPlayer, iRevoltIdx, indCities, 'independence', bPeaceful, bodStr )

					return

				else :
					# Demand independence for religious reasons
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Demanding independence for religious reasons")

					# Prune for only close cities, cities in area may be quite far away
					indCities = list()
					for pCity in relCities :
						# Add only cities near instigator in first pass
						cityDist = plotDistance( pCity.getX(), pCity.getY(), instigator.getX(), instigator.getY() )
						if( cityDist <= self.closeRadius ) :
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s is close enough to instigator to join in independence quest"%(pCity.getName()))
							indCities.append(pCity)

					for pCity in relCities :
						if( not pCity in indCities ) :
							# Add cities a little further away that are also near another rebelling city
							cityDist = plotDistance( pCity.getX(), pCity.getY(), instigator.getX(), instigator.getY() )
							if( cityDist <= 2.0*self.closeRadius ) :
								for iCity in indCities :
									cityDist = min([cityDist, plotDistance( pCity.getX(), pCity.getY(), iCity.getX(), iCity.getY() )])

								if( cityDist <= 0.8*self.closeRadius ) :
									if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s is close enough to another rebellin city to join in independence quest"%(pCity.getName()))
									indCities.append(pCity)

					bodStr = getCityTextList(indCities, bPreCity = True, bPostIs = True)

					bodStr += ' ' + localText.getText("TXT_KEY_REV_REL_VIOLENT_IND_1",()) + ' %s.'%(gc.getReligionInfo( revRel ).getDescription())
					bodStr += '  ' + localText.getText("TXT_KEY_REV_REL_VIOLENT_IND_2",()) + ' %s '%(gc.getReligionInfo( pPlayer.getStateReligion() ).getDescription()) + localText.getText("TXT_KEY_REV_REL_VIOLENT_IND_3",())
					bodStr += '\n\n' + localText.getText("TXT_KEY_REV_REL_VIOLENT_IND",())

					# lfgr: split forced
					[pRevPlayer,bIsJoinWar] = self.chooseRevolutionCiv( indCities, bJoinCultureWar = False, bReincarnate = True, bJoinRebels = False, bSpreadRebels = False, giveRelType = revRel, bMatchCivics = False, iSplitType = RevCivUtils.SPLIT_FORCED )
					# lfgr end

					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %d cities in revolution"%(len(indCities)))
					assert( len(indCities) > 0 )
					specialDataDict = { 'iRevPlayer' : pRevPlayer.getID(), 'vassalStyle' : None }
					cityIdxs = list()
					for pCity in indCities :
						cityIdxs.append( pCity.getID() )
					revData = RevDefs.RevoltData( pPlayer.getID(), game.getGameTurn(), cityIdxs, 'independence', bPeaceful, specialDataDict )

					revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
					iRevoltIdx = len(revoltDict.keys())
					revoltDict[iRevoltIdx] = revData
					RevData.revObjectUpdateVal( pPlayer, 'RevoltDict', revoltDict )

					self.makeRevolutionDecision( pPlayer, iRevoltIdx, indCities, 'independence', bPeaceful, bodStr )

					return

# --------------- Special options for homeland revolutions
		if instigator != None:
			if( instigator.area().getID() == pPlayer.getCapitalCity().area().getID() ) :
				# Revolution in homeland
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Revolution in homeland")
	
				if( bPeaceful and not gc.getTeam(pPlayer.getTeam()).isHasTech(self.iNationalismTech) ) :
					[goodEffect,badEffect] = RevUtils.getCivicsHolyCityEffects( iPlayer )
					if( badEffect > 0 ) :
						stateRel = pPlayer.getStateReligion()
						if( pPlayer.isStateReligion() and stateRel >= 0 ) :
							# Check for ask for crusade
							stateHolyCity = game.getHolyCity( stateRel )
							stateHolyCityOwner = gc.getPlayer( stateHolyCity.getOwner() )
							if( not stateHolyCityOwner == None ) :
								if( instigator.isHasReligion(stateRel) and not stateHolyCityOwner.getID() == iPlayer ) :
									if( pTeam.canDeclareWar( stateHolyCityOwner.getTeam() ) and not pTeam.isAVassal() ) :
	
										if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Holy city for %s (%d) is %s, owner %s practices %d"%(gc.getReligionInfo(stateRel).getDescription(),stateRel,stateHolyCity.getName(),stateHolyCityOwner.getCivilizationDescription(0),stateHolyCityOwner.getStateReligion()))
	
										relCities = list()
										for city in revCities :
											if( city.isHasReligion(stateRel) ) :
												if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s has state religion"%(city.getName()))
												relCities.append(city)
	
										bodStr = getCityTextList(revCities, bPreCity = True, bPostIs = True)
	
										if( not stateHolyCityOwner.getStateReligion() == stateRel ) :
											if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Ask for Crusade against %s!"%(stateHolyCityOwner.getCivilizationDescription(0)))
	
											bodStr += " " + localText.getText("TXT_KEY_REV_HL_HOLY_WAR",()) + " %s."%(stateHolyCityOwner.getCivilizationDescription(0))
											bodStr += "   " + localText.getText("TXT_KEY_REV_HL_HOLY_RECLAIM",()) + " %s, "%(stateHolyCity.getName()) + localText.getText("TXT_KEY_REV_HL_HOLY_HEATHENS",())
											bodStr += "\n\n" + localText.getText("TXT_KEY_REV_HL_HOLY_REQUEST",())
	
											assert( len(relCities) > 0 )
	
											specialDataDict = { 'iRevPlayer' : stateHolyCityOwner.getID() }
											cityIdxs = list()
											for pCity in relCities :
												cityIdxs.append( pCity.getID() )
											revData = RevDefs.RevoltData( pPlayer.getID(), game.getGameTurn(), cityIdxs, 'war', bPeaceful, specialDataDict )
	
											revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
											iRevoltIdx = len(revoltDict.keys())
											revoltDict[iRevoltIdx] = revData
											RevData.revObjectUpdateVal( pPlayer, 'RevoltDict', revoltDict )
	
											self.makeRevolutionDecision( pPlayer, iRevoltIdx, relCities, 'war', bPeaceful, bodStr )
	
											return
	
										if( pPlayer.AI_getAttitude(stateHolyCityOwner.getID()) == AttitudeTypes.ATTITUDE_FURIOUS or pPlayer.AI_getAttitude(stateHolyCityOwner.getID()) == AttitudeTypes.ATTITUDE_ANNOYED ) :
											if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Ask for crusade against fellow believer, %s!"%(stateHolyCityOwner.getCivilizationDescription(0)))
	
											bodStr += " " + localText.getText("TXT_KEY_REV_HL_HOLY_WAR",()) + " %s."%(stateHolyCityOwner.getCivilizationDescription(0))
											bodStr += "   " + localText.getText("TXT_KEY_REV_HL_HOLY_WHILE",()) + ' %s '%(stateHolyCityOwner.getCivilizationDescription(0)) + localText.getText("TXT_KEY_REV_HL_HOLY_CLAIMS",()) + ' %s, '%(gc.getReligionInfo(stateRel).getDescription()) + localText.getText("TXT_KEY_REV_HL_HOLY_WORTHY",()) + " %s!"%(stateHolyCity.getName())
											bodStr += "   " + localText.getText("TXT_KEY_REV_HL_HOLY_DEVOTION",()) + " %s "%(stateHolyCity.getName()) + localText.getText("TXT_KEY_REV_HL_HOLY_UNWORTHY",())
											bodStr += "\n\n" + localText.getText("TXT_KEY_REV_HL_HOLY_REQUEST",())
	
											assert( len(relCities) > 0 )
											specialDataDict = { 'iRevPlayer' : stateHolyCityOwner.getID() }
											cityIdxs = list()
											for pCity in relCities :
												cityIdxs.append( pCity.getID() )
											revData = RevDefs.RevoltData( pPlayer.getID(), game.getGameTurn(), cityIdxs, 'war', bPeaceful, specialDataDict )
	
											revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
											iRevoltIdx = len(revoltDict.keys())
											revoltDict[iRevoltIdx] = revData
											RevData.revObjectUpdateVal( pPlayer, 'RevoltDict', revoltDict )
	
											self.makeRevolutionDecision( pPlayer, iRevoltIdx, relCities, 'war', bPeaceful, bodStr )
	
											return
	
	
				if( self.civicRevolution ) :
					[laborLevel,optionType] = RevUtils.getLaborFreedom( iPlayer )
					[newLaborLevel,newCivic] = RevUtils.getBestLaborFreedom( iPlayer, optionType )
					if( bPeaceful and laborLevel < 0 and newLaborLevel > 5 and not newCivic == None ) :
						if( (10*abs(laborLevel) > game.getSorenRandNum(100, 'Revolt - emancipation request')) ):
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Asking change to emancipation, %d"%(newCivic))
	
							bodStr = getCityTextList(revCities, bPreCity = True, bPostIs = True)
	
							#iBuyOffCost = (50 + 10*pPlayer.getCurrentRealEra())*len(revCities) + game.getSorenRandNum(50+10*pPlayer.getCurrentRealEra(),'Rev')
							totalRevIdx = 0
							for pCity in revCities :
								totalRevIdx += pCity.getRevolutionIndex()
							iBuyOffCost = totalRevIdx/(20-pPlayer.getCurrentRealEra()) + game.getSorenRandNum(50+10*pPlayer.getCurrentRealEra(),'Rev')
							if( not pPlayer.isHuman() ) : iBuyOffCost = int( iBuyOffCost*.7 )
							iBuyOffCost = max( [iBuyOffCost,pPlayer.getGold()/10 + game.getSorenRandNum(50,'Rev')] )
							bodStr += ' ' + localText.getText("TXT_KEY_REV_HL_EMAN_REJECT",()) + ' %s '%(gc.getCivicInfo(newCivic).getDescription()) + localText.getText("TXT_KEY_REV_HL_EMAN_CIVIC",())
							bodStr += '\n\n' + localText.getText("TXT_KEY_REV_PEACEFUL_CONCLUSION",())
							bodStr += '  ' + localText.getText("TXT_KEY_REV_HL_EMAN_SLAVE",())
							bodStr += '  ' + localText.getText("TXT_KEY_REV_BRIBE",())
	
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %d cities in revolution, buyoff cost %d"%(len(revCities),iBuyOffCost))
							assert( len(revCities) > 0 )
	
							specialDataDict = { 'iNewCivic' : newCivic, 'iBuyOffCost' : iBuyOffCost }
							cityIdxs = list()
							for pCity in revCities :
								cityIdxs.append( pCity.getID() )
							revData = RevDefs.RevoltData( pPlayer.getID(), game.getGameTurn(), cityIdxs, 'civics', bPeaceful, specialDataDict )
	
							revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
							iRevoltIdx = len(revoltDict.keys())
							revoltDict[iRevoltIdx] = revData
							RevData.revObjectUpdateVal( pPlayer, 'RevoltDict', revoltDict )
	
							self.makeRevolutionDecision( pPlayer, iRevoltIdx, revCities, 'civics', bPeaceful, bodStr )
	
							return
	
					if( laborLevel < -5 and newLaborLevel > (laborLevel + 2) and not newCivic == None ) :
						if( not bPeaceful and 50 > game.getSorenRandNum( 100, 'Revolt - do slave rebellion' ) ) :
							if( not instigator.area().isBorderObstacle(pPlayer.getTeam()) ) :
								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Slave rebellion!!!, %d"%(newCivic))
	
								slaveCities = list()
								for pCity in revCities :
									# Add only cities near instigator in first pass
									cityDist = plotDistance( pCity.getX(), pCity.getY(), instigator.getX(), instigator.getY() )
									if( cityDist <= self.closeRadius ) :
										if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s is close enough to instigator to join in slave revolt"%(pCity.getName()))
										slaveCities.append(pCity)
	
								for pCity in revCities :
									if( not pCity in slaveCities ) :
										# Add cities a little further away that are also near another rebelling city
										cityDist = plotDistance( pCity.getX(), pCity.getY(), instigator.getX(), instigator.getY() )
										if( cityDist <= 2.0*self.closeRadius ) :
											for iCity in slaveCities :
												cityDist = min([cityDist, plotDistance( pCity.getX(), pCity.getY(), iCity.getX(), iCity.getY() )])
	
											if( cityDist <= 0.8*self.closeRadius ) :
												if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s is close enough to another rebellin city to join in slave revolt"%(pCity.getName()))
												slaveCities.append(pCity)
	
								bodStr = localText.getText("TXT_KEY_REV_HL_SLAVE_REBELLION",())
								bodStr += getCityTextList(slaveCities) + '!'
	
								bodStr += '  ' + localText.getText("TXT_KEY_REV_HL_SLAVE_DEMAND",())
								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Asking change to %s"%(gc.getCivicInfo(newCivic).getDescription()))
								bodStr += ' %s '%(gc.getCivicInfo(newCivic).getDescription())
	
								bodStr += localText.getText("TXT_KEY_REV_HL_SLAVE_DENY",())
	
								# Slaves always rise up as barbarians
								pRevPlayer = gc.getPlayer( gc.getBARBARIAN_PLAYER() )
								assert(len(slaveCities) > 0)
								specialDataDict = { 'iNewCivic' : newCivic, 'iRevPlayer' : pRevPlayer.getID() }
								cityIdxs = list()
								for pCity in slaveCities :
									cityIdxs.append( pCity.getID() )
								revData = RevDefs.RevoltData( pPlayer.getID(), game.getGameTurn(), cityIdxs, 'civics', bPeaceful, specialDataDict )
	
								revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
								iRevoltIdx = len(revoltDict.keys())
								revoltDict[iRevoltIdx] = revData
								RevData.revObjectUpdateVal( pPlayer, 'RevoltDict', revoltDict )
	
								self.makeRevolutionDecision( pPlayer, iRevoltIdx, slaveCities, 'civics', bPeaceful, bodStr )
	
								return
	
					[enviroLevel,optionType] = RevUtils.getEnvironmentalProtection( iPlayer )
					[newEnviroLevel,newCivic] = RevUtils.getBestEnvironmentalProtection( iPlayer, optionType )
					if( bPeaceful and newEnviroLevel > enviroLevel + 2 and not newCivic == None ) :
						if( 30 > game.getSorenRandNum(100, 'Revolt - environmentalism request') ):
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Asking change to %s, %d (environment)"%(gc.getCivicInfo(newCivic).getDescription(),newCivic))
	
							bodStr = getCityTextList(revCities, bPreCity = True, bPostIs = True)
	
							#iBuyOffCost = (50 + 10*pPlayer.getCurrentRealEra())*len(revCities) + game.getSorenRandNum(50+10*pPlayer.getCurrentRealEra(),'Rev')
							totalRevIdx = 0
							for pCity in revCities :
								totalRevIdx += pCity.getRevolutionIndex()
							iBuyOffCost = totalRevIdx/(20-pPlayer.getCurrentRealEra()) + game.getSorenRandNum(50+10*pPlayer.getCurrentRealEra(),'Rev')
							if( not pPlayer.isHuman() ) : iBuyOffCost = int( iBuyOffCost*.7 )
							iBuyOffCost = max( [iBuyOffCost,pPlayer.getGold()/10 + game.getSorenRandNum(50,'Rev')] )
							bodStr += ' ' + localText.getText("TXT_KEY_REV_HL_ENV_REQUEST",()) + ' %s.'%(gc.getCivicInfo(newCivic).getDescription())
							bodStr += '  ' + localText.getText("TXT_KEY_REV_HL_ENV_GREEN",())
							bodStr += '\n\n' + localText.getText("TXT_KEY_REV_PEACEFUL_CONCLUSION",())
							bodStr += '  ' + localText.getText("TXT_KEY_REV_HL_ENV_SMOG",())
							bodStr += '  ' + localText.getText("TXT_KEY_REV_BRIBE",())
	
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %d cities in revolution, buyoff cost %d"%(len(revCities),iBuyOffCost))
							assert( len(revCities) > 0 )
							specialDataDict = { 'iNewCivic' : newCivic, 'iBuyOffCost' : iBuyOffCost }
							cityIdxs = list()
							for pCity in revCities :
								cityIdxs.append( pCity.getID() )
							revData = RevDefs.RevoltData( pPlayer.getID(), game.getGameTurn(), cityIdxs, 'civics', bPeaceful, specialDataDict )
	
							revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
							iRevoltIdx = len(revoltDict.keys())
							revoltDict[iRevoltIdx] = revData
							RevData.revObjectUpdateVal( pPlayer, 'RevoltDict', revoltDict )
	
							self.makeRevolutionDecision( pPlayer, iRevoltIdx, revCities, 'civics', bPeaceful, bodStr )
	
							return
	
	
	# -------------------- Special options for colonial revolutions
			else :
				# Revolution based in other area
				# These are special requests peaceful colonists may make
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Revolution in colony")
	
				foreignCities = list()
				capitalArea = pPlayer.getCapitalCity().area().getID()
				for pCity in revCities :
					if( not pCity.area().getID() == capitalArea ) :
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s is colony"%(pCity.getName()))
						foreignCities.append( pCity )
	
				bodStr = getCityTextList(foreignCities, bPreCity = True, bPostIs = True)
	
				if( bPeaceful and self.civicRevolution ) :
					# Sufferage or representation
					[demoLevel,optionType] = RevUtils.getDemocracyLevel( iPlayer )
					[newDemoLevel,newCivic] = RevUtils.getBestDemocracyLevel( iPlayer, optionType )
					if( demoLevel < 0 and newDemoLevel > 0 and not newCivic == None ) :
	
							bodStr += ' ' + localText.getText("TXT_KEY_REV_COL_GOVT_REQUEST",())
							if( newDemoLevel > 9 ) :
								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Asking change to universal sufferage")
								bodStr += "  " + localText.getText("TXT_KEY_REV_COL_GOVT_PROTESTING",()) + " %s!"%(gc.getCivicInfo(newCivic).getDescription())
							else :
								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Asking change to representation")
								bodStr += "  " + localText.getText("TXT_KEY_REV_COL_GOVT_CRIES",()) + " %s!' "%(gc.getCivicInfo(newCivic).getDescription()) +localText.getText("TXT_KEY_REV_COL_GOVT_MARCH",())
	
							#iBuyOffCost = (75 + 12*pPlayer.getCurrentRealEra())*len(foreignCities) + game.getSorenRandNum(100+10*pPlayer.getCurrentRealEra(),'Rev')
							totalRevIdx = 0
							for pCity in foreignCities :
								totalRevIdx += pCity.getRevolutionIndex()
							iBuyOffCost = totalRevIdx/(15-pPlayer.getCurrentRealEra()) + game.getSorenRandNum(80+10*pPlayer.getCurrentRealEra(),'Rev')
							if( not pPlayer.isHuman() ) : iBuyOffCost = int( iBuyOffCost*.7 )
							iBuyOffCost = max( [iBuyOffCost,pPlayer.getGold()/8 + game.getSorenRandNum(50,'Rev')] )
							bodStr += '\n\n' + localText.getText("TXT_KEY_REV_PEACEFUL_CONCLUSION",())
							bodStr += '  ' + localText.getText("TXT_KEY_REV_COL_GOVT_PRACTICES",())
							bodStr += '  ' + localText.getText("TXT_KEY_REV_BRIBE",())
	
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %d cities in revolution, buyoff cost %d"%(len(revCities),iBuyOffCost))
							assert( len(revCities) > 0 )
							specialDataDict = { 'iNewCivic' : newCivic, 'iBuyOffCost' : iBuyOffCost }
							cityIdxs = list()
							for pCity in foreignCities :
								cityIdxs.append( pCity.getID() )
							revData = RevDefs.RevoltData( pPlayer.getID(), game.getGameTurn(), cityIdxs, 'civics', bPeaceful, specialDataDict )
	
							revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
							iRevoltIdx = len(revoltDict.keys())
							revoltDict[iRevoltIdx] = revData
							RevData.revObjectUpdateVal( pPlayer, 'RevoltDict', revoltDict )
	
							self.makeRevolutionDecision( pPlayer, iRevoltIdx, foreignCities, 'civics', bPeaceful, bodStr )
	
							return
	
				#if( bPeaceful and self.vassalRevolution ) :
					# Ask to become vassal
					# Trim down cities to only those close to instigator


#-------- If capital or majority of cities,
		if( revInCapital or (len(revCities) >= (pPlayer.getNumCities()-1)/2 and len(revCities) > 2) ) :

			bodStr = getCityTextList(revCities, bPreCity = True, bPostIs = True)

			if( bPeaceful ) :
				# If peaceful, ask change to civics ... if no civics, ask for change of leader
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Capital or large number of cities in peaceful revolution!")

				if( self.civicRevolution ) :
					# Emancipation
					[laborLevel,optionType] = RevUtils.getLaborFreedom( iPlayer )
					[newLaborLevel,newCivic] = RevUtils.getBestLaborFreedom( iPlayer, optionType )
					if( laborLevel < 0 and newLaborLevel > 5 and not newCivic == None ):
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Asking change to %s, %d"%(gc.getCivicInfo(newCivic).getDescription(),newCivic))

						#iBuyOffCost = (50 + 12*pPlayer.getCurrentRealEra())*len(revCities) + game.getSorenRandNum(50+10*pPlayer.getCurrentRealEra(),'Rev')
						totalRevIdx = 0
						for pCity in revCities :
							totalRevIdx += pCity.getRevolutionIndex()
						iBuyOffCost = totalRevIdx/(20-pPlayer.getCurrentRealEra()) + game.getSorenRandNum(50+10*pPlayer.getCurrentRealEra(),'Rev')
						if( not pPlayer.isHuman() ) : iBuyOffCost = int( iBuyOffCost*.7 )
						iBuyOffCost = max( [iBuyOffCost,pPlayer.getGold()/10 + game.getSorenRandNum(50,'Rev')] )
						bodStr += ' ' + localText.getText("TXT_KEY_REV_HL_EMAN_REJECT",()) + ' %s '%(gc.getCivicInfo(newCivic).getDescription()) + localText.getText("TXT_KEY_REV_HL_EMAN_CIVIC",())
						bodStr += '\n\n' + localText.getText("TXT_KEY_REV_PEACEFUL_CONCLUSION",())
						bodStr += '  ' + localText.getText("TXT_KEY_REV_HL_EMAN_SLAVE",())
						bodStr += '  ' + localText.getText("TXT_KEY_REV_BRIBE",())

						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %d cities in revolution, buyoff cost %d"%(len(revCities),iBuyOffCost))
						assert( len(revCities) > 0 )
						specialDataDict = { 'iNewCivic' : newCivic, 'iBuyOffCost' : iBuyOffCost }
						cityIdxs = list()
						for pCity in revCities :
							cityIdxs.append( pCity.getID() )
						revData = RevDefs.RevoltData( pPlayer.getID(), game.getGameTurn(), cityIdxs, 'civics', bPeaceful, specialDataDict )

						revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
						iRevoltIdx = len(revoltDict.keys())
						revoltDict[iRevoltIdx] = revData
						RevData.revObjectUpdateVal( pPlayer, 'RevoltDict', revoltDict )

						self.makeRevolutionDecision( pPlayer, iRevoltIdx, revCities, 'civics', bPeaceful, bodStr )

						return

					[isCanDoCommunism,newCivic] = RevUtils.canDoCommunism( iPlayer )
					if( isCanDoCommunism and not newCivic == None ) :
						if( 35 > game.getSorenRandNum(100, 'Revolt - Communist revolution') ) :
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Communist revolution, ask change to %s, %d"%(gc.getCivicInfo(newCivic).getDescription(), newCivic))

							bodStr += ' ' + localText.getText("TXT_KEY_REV_CAP_COM_REQUEST",()) + ' %s.  '%(gc.getCivicInfo(newCivic).getDescription()) + localText.getText("TXT_KEY_REV_CAP_COM_BROTHER",())
							bodStr += ' %s '%(gc.getCivicInfo(newCivic).getDescription()) + localText.getText("TXT_KEY_REV_CAP_COM_ECON",())

							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %d cities in revolution"%(len(revCities)))
							assert( len(revCities) > 0 )
							specialDataDict = { 'iNewCivic' : newCivic }
							cityIdxs = list()
							for pCity in revCities :
								cityIdxs.append( pCity.getID() )
							revData = RevDefs.RevoltData( pPlayer.getID(), game.getGameTurn(), cityIdxs, 'civics', bPeaceful, specialDataDict )

							revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
							iRevoltIdx = len(revoltDict.keys())
							revoltDict[iRevoltIdx] = revData
							RevData.revObjectUpdateVal( pPlayer, 'RevoltDict', revoltDict )

							self.makeRevolutionDecision( pPlayer, iRevoltIdx, revCities, 'civics', bPeaceful, bodStr )

							return

					# Sufferage or representation
					[demoLevel,optionType] = RevUtils.getDemocracyLevel( iPlayer )
					[newDemoLevel,newCivic] = RevUtils.getBestDemocracyLevel( iPlayer, optionType )
					if( demoLevel < 0 and newDemoLevel > 0 and not newCivic == None ) :

							bodStr += ' ' + localText.getText("TXT_KEY_REV_CAP_VOTE_REQUEST",())
							if( newDemoLevel > 9 ) :
								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Asking change to universal sufferage, %d"%(newCivic))
								bodStr += "  " + localText.getText("TXT_KEY_REV_CAP_VOTE_US",()) + " %s!"%(gc.getCivicInfo(newCivic).getDescription())
							else :
								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Asking change to representation, %d"%(newCivic))
								bodStr += "  " + localText.getText("TXT_KEY_REV_CAP_VOTE_CRIES",()) + " %s!' "%(gc.getCivicInfo(newCivic).getDescription()) +localText.getText("TXT_KEY_REV_CAP_VOTE_MARCH",())

							#iBuyOffCost = (50 + 15*pPlayer.getCurrentRealEra())*len(revCities) + game.getSorenRandNum(150+15*pPlayer.getCurrentRealEra(),'Rev')
							totalRevIdx = 0
							for pCity in revCities :
								totalRevIdx += pCity.getRevolutionIndex()
							iBuyOffCost = totalRevIdx/(20-pPlayer.getCurrentRealEra()) + game.getSorenRandNum(100+10*pPlayer.getCurrentRealEra(),'Rev')
							if( not pPlayer.isHuman() ) : iBuyOffCost = int( iBuyOffCost*.7 )
							iBuyOffCost = max( [iBuyOffCost,pPlayer.getGold()/8 + game.getSorenRandNum(50,'Rev')] )
							bodStr += '\n\n' + localText.getText("TXT_KEY_REV_PEACEFUL_CONCLUSION",())
							bodStr += '  ' + localText.getText("TXT_KEY_REV_CAP_VOTE_POWER",())
							bodStr += "  " + localText.getText("TXT_KEY_REV_BRIBE",()) + "  " + localText.getText("TXT_KEY_REV_CAP_VOTE_STATUES",())

							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %d cities in revolution, buyoff cost %d"%(len(revCities),iBuyOffCost))
							assert( len(revCities) > 0 )
							specialDataDict = { 'iNewCivic' : newCivic, 'iBuyOffCost' : iBuyOffCost }
							cityIdxs = list()
							for pCity in revCities :
								cityIdxs.append( pCity.getID() )
							revData = RevDefs.RevoltData( pPlayer.getID(), game.getGameTurn(), cityIdxs, 'civics', bPeaceful, specialDataDict )

							revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
							iRevoltIdx = len(revoltDict.keys())
							revoltDict[iRevoltIdx] = revData
							RevData.revObjectUpdateVal( pPlayer, 'RevoltDict', revoltDict )

							self.makeRevolutionDecision( pPlayer, iRevoltIdx, revCities, 'civics', bPeaceful, bodStr )

							return

					[bCanDoFreeSpeech,newCivic] = RevUtils.canDoFreeSpeech( iPlayer )
					if( bCanDoFreeSpeech and not newCivic == None ) :
						if( 50 > game.getSorenRandNum(100, 'Revolt - free speech request') ):
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Asking change to Free Speech, %d"%(newCivic))

							bodStr = getCityTextList(revCities, bPreCity = True, bPostIs = True)

							#iBuyOffCost = (50 + 10*pPlayer.getCurrentRealEra())*len(revCities) + game.getSorenRandNum(50+10*pPlayer.getCurrentRealEra(),'Rev')
							totalRevIdx = 0
							for pCity in revCities :
								totalRevIdx += pCity.getRevolutionIndex()
							iBuyOffCost = totalRevIdx/(20-pPlayer.getCurrentRealEra()) + game.getSorenRandNum(50+12*pPlayer.getCurrentRealEra(),'Rev')
							if( not pPlayer.isHuman() ) : iBuyOffCost = int( iBuyOffCost*.7 )
							iBuyOffCost = max( [iBuyOffCost,pPlayer.getGold()/10 + game.getSorenRandNum(50,'Rev')] )
							bodStr += ' ' + localText.getText("TXT_KEY_REV_CAP_SPEECH_REQUEST",()) + ' %s.'%(gc.getCivicInfo(newCivic).getDescription())
							bodStr += '  ' + localText.getText("TXT_KEY_REV_CAP_SPEECH_DENY",())

							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %d cities in revolution, buyoff cost %d"%(len(revCities),iBuyOffCost))
							assert( len(revCities) > 0 )
							specialDataDict = { 'iNewCivic' : newCivic, 'iBuyOffCost' : iBuyOffCost }
							cityIdxs = list()
							for pCity in revCities :
								cityIdxs.append( pCity.getID() )
							revData = RevDefs.RevoltData( pPlayer.getID(), game.getGameTurn(), cityIdxs, 'civics', bPeaceful, specialDataDict )

							revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
							iRevoltIdx = len(revoltDict.keys())
							revoltDict[iRevoltIdx] = revData
							RevData.revObjectUpdateVal( pPlayer, 'RevoltDict', revoltDict )

							self.makeRevolutionDecision( pPlayer, iRevoltIdx, revCities, 'civics', bPeaceful, bodStr )

							return

				if( self.leaderRevolution and not bReinstatedOnRevolution ) : #and (len(revCities) == pPlayer.getNumCities() or len(revCities) > (pPlayer.getNumCities()+1)/3) ) :
					# All or most cities in revolt
					if( not pPlayer.isHuman() or self.humanLeaderRevolution ) :
						# Ask for change of leader

						bodStr += ' ' + localText.getText("TXT_KEY_REV_CAP_LEAD_REQUEST",())
						if( not RevUtils.isCanDoElections( iPlayer ) ) :
							if( 70 > game.getSorenRandNum(100, 'Revolt - cede power request') or len(revCities) == pPlayer.getNumCities() ):

								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Asking for change in leader from %s"%(pPlayer.getName()))
								[newLeaderType,newLeaderName] = self.chooseRevolutionLeader( revCities )

								bIsElection = False
								#iBuyOffCost = (50 + 15*pPlayer.getCurrentRealEra())*len(revCities) + game.getSorenRandNum(100+10*pPlayer.getCurrentRealEra(),'Rev')
								totalRevIdx = 0
								for pCity in revCities :
									totalRevIdx += pCity.getRevolutionIndex()
								iBuyOffCost = totalRevIdx/(20-pPlayer.getCurrentRealEra()) + game.getSorenRandNum(80+10*pPlayer.getCurrentRealEra(),'Rev')
								if( not pPlayer.isHuman() ) : iBuyOffCost = int( iBuyOffCost*.7 )
								iBuyOffCost = max( [iBuyOffCost,pPlayer.getGold()/10 + game.getSorenRandNum(50,'Rev')] )
								bodStr += '  ' + localText.getText("TXT_KEY_REV_CAP_LEAD_CEDE",()) + ' %s.'%(newLeaderName)
								bodStr += '\n\n' + localText.getText("TXT_KEY_REV_CAP_LEAD_CONCLUSION",())
								bodStr += '  %s '%(newLeaderName) + localText.getText("TXT_KEY_REV_CAP_LEAD_RULER",())

								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %d cities in revolution, buyoff cost %d"%(len(revCities),iBuyOffCost))
								assert( len(revCities) > 0 )
								specialDataDict = { 'iNewLeaderType' : newLeaderType, 'newLeaderName' : newLeaderName, 'bIsElection' : bIsElection, 'iBuyOffCost' : iBuyOffCost }
								cityIdxs = list()
								for pCity in revCities :
									cityIdxs.append( pCity.getID() )
								revData = RevDefs.RevoltData( pPlayer.getID(), game.getGameTurn(), cityIdxs, 'leader', bPeaceful, specialDataDict )

								revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
								iRevoltIdx = len(revoltDict.keys())
								revoltDict[iRevoltIdx] = revData
								RevData.revObjectUpdateVal( pPlayer, 'RevoltDict', revoltDict )

								self.makeRevolutionDecision( pPlayer, iRevoltIdx, revCities, 'leader', bPeaceful, bodStr )

								return

						else :
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Asking for %s to face election"%(pPlayer.getName()))
							[newLeaderType,newLeaderName] = self.chooseRevolutionLeader( revCities )

							bIsElection = True
							#iBuyOffCost = (30 + 10*pPlayer.getCurrentRealEra())*len(revCities) + game.getSorenRandNum(100+10*pPlayer.getCurrentRealEra(),'Rev')
							totalRevIdx = 0
							for pCity in revCities :
								totalRevIdx += pCity.getRevolutionIndex()
							iBuyOffCost = totalRevIdx/(25-pPlayer.getCurrentRealEra()) + game.getSorenRandNum(90+10*pPlayer.getCurrentRealEra(),'Rev')
							if( not pPlayer.isHuman() ) : iBuyOffCost = int( iBuyOffCost*.7 )
							iBuyOffCost = max( [iBuyOffCost,pPlayer.getGold()/12 + game.getSorenRandNum(50,'Rev')] )
							bodStr += '  ' + localText.getText("TXT_KEY_REV_CAP_LEAD_ELECTION",()) + ' %s!'%(newLeaderName)
							bodStr += '\n\n' + localText.getText("TXT_KEY_REV_PEACEFUL_CONCLUSION",())
							bodStr += '\n\n' + localText.getText("TXT_KEY_REV_CAP_LEAD_BUYOFF",())

							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %d cities in revolution, buyoff cost %d"%(len(revCities),iBuyOffCost))
							assert( len(revCities) > 0 )
							specialDataDict = { 'iNewLeaderType' : newLeaderType, 'newLeaderName' : newLeaderName, 'bIsElection' : bIsElection, 'iBuyOffCost' : iBuyOffCost }
							cityIdxs = list()
							for pCity in revCities :
								cityIdxs.append( pCity.getID() )
							revData = RevDefs.RevoltData( pPlayer.getID(), game.getGameTurn(), cityIdxs, 'leader', bPeaceful, specialDataDict )

							revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
							iRevoltIdx = len(revoltDict.keys())
							revoltDict[iRevoltIdx] = revData
							RevData.revObjectUpdateVal( pPlayer, 'RevoltDict', revoltDict )

							self.makeRevolutionDecision( pPlayer, iRevoltIdx, revCities, 'leader', bPeaceful, bodStr )

							return

			else :
				# If violent, demand change of leader!
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Capital or majority of cities in violent revolution!")

				if( self.leaderRevolution ) : #and (len(revCities) > 1 or len(revCities) == pPlayer.getNumCities()) ) :
					if( not pPlayer.isHuman() or self.humanLeaderRevolution ) :

						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Demanding change in leader from %s"%(pPlayer.getName()))

						[newLeaderType,newLeaderName] = self.chooseRevolutionLeader( revCities )

						if( pPlayer.isStateReligion() ) :
							giveRelType = pPlayer.getStateReligion()
						else :
							giveRelType = None

						# lfgr: split empire when asking for leader change
						[pRevPlayer,bIsJoinWar] = self.chooseRevolutionCiv( revCities, bJoinCultureWar = False, bReincarnate = True, bJoinRebels = True, bSpreadRebels = False, giveRelType = giveRelType, bMatchCivics = True, iSplitType = RevCivUtils.SPLIT_FORCED )
						# lfgr end

						bodStr += ' ' + localText.getText("TXT_KEY_REV_CAP_RULE_DEMAND",())
						if( not RevUtils.isCanDoElections( iPlayer ) ) :
							bIsElection = False
							iBuyOffCost = -1
							bodStr += '  ' + localText.getText("TXT_KEY_REV_CAP_RULE_CEDE",()) + ' %s.'%(newLeaderName)
							bodStr += '\n\n' + localText.getText("TXT_KEY_REV_CAP_RULE_TERRIBLE",())
							bodStr += ' %s '%(pRevPlayer.getCivilizationShortDescription(0)) + localText.getText("TXT_KEY_REV_CAP_RULE_FIGHT",())
							bodStr += '  %s '%(newLeaderName) + localText.getText("TXT_KEY_REV_CAP_LEAD_RULER",())

						else :
							bIsElection = True
							#iBuyOffCost = (50 + 12*pPlayer.getCurrentRealEra())*len(revCities) + game.getSorenRandNum(100+10*pPlayer.getCurrentRealEra(),'Rev')
							totalRevIdx = 0
							for pCity in revCities :
								totalRevIdx += pCity.getRevolutionIndex()
							iBuyOffCost = totalRevIdx/(22-pPlayer.getCurrentRealEra()) + game.getSorenRandNum(80+10*pPlayer.getCurrentRealEra(),'Rev')
							if( not pPlayer.isHuman() ) : iBuyOffCost = int( iBuyOffCost*.7 )
							iBuyOffCost = max( [iBuyOffCost,pPlayer.getGold()/8 + game.getSorenRandNum(50,'Rev')] )
							bodStr += '  ' + localText.getText("TXT_KEY_REV_CAP_RULE_ELECTION",()) + ' %s!'%(newLeaderName)
							bodStr += '\n\n' + localText.getText("TXT_KEY_REV_CAP_RULE_RISE",()) + ' %s '%(pRevPlayer.getCivilizationShortDescription(0))
							bodStr += localText.getText("TXT_KEY_REV_CAP_RULE_BUYOFF",())

						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %d cities in revolution, buyoff cost %d"%(len(revCities),iBuyOffCost))
						assert( len(revCities) > 0 )
						specialDataDict = { 'iNewLeaderType' : newLeaderType, 'newLeaderName' : newLeaderName, 'bIsElection' : bIsElection, 'iBuyOffCost' : iBuyOffCost, 'iRevPlayer' : pRevPlayer.getID(), 'bIsJoinWar' : bIsJoinWar }
						cityIdxs = list()
						for pCity in revCities :
							cityIdxs.append( pCity.getID() )
						revData = RevDefs.RevoltData( pPlayer.getID(), game.getGameTurn(), cityIdxs, 'leader', bPeaceful, specialDataDict )

						revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
						iRevoltIdx = len(revoltDict.keys())
						revoltDict[iRevoltIdx] = revData
						RevData.revObjectUpdateVal( pPlayer, 'RevoltDict', revoltDict )

						self.makeRevolutionDecision( pPlayer, iRevoltIdx, revCities, 'leader', bPeaceful, bodStr )

						return

#-------- Default to ask/demand independence
		if( not self.independenceRevolution ) :
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - WARNING: default ask for independence has been disabled!")
			return

		if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Default: ask/demand independence!")

		# Prune for only close cities, Cities in area may be quite far away
		indCities = list()
		for pCity in revCities :
			# Add only cities near instigator in first pass
			cityDist = plotDistance( pCity.getX(), pCity.getY(), instigator.getX(), instigator.getY() )
			if( cityDist <= self.closeRadius ) :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s is close enough to instigator to join in independence quest"%(pCity.getName()))
				indCities.append(pCity)

		for pCity in revCities :
			if( not pCity in indCities ) :
				# Add cities a little further away that are also near another rebelling city
				cityDist = plotDistance( pCity.getX(), pCity.getY(), instigator.getX(), instigator.getY() )
				if( cityDist <= 2.0*self.closeRadius ) :
					for iCity in indCities :
						cityDist = min([cityDist, plotDistance( pCity.getX(), pCity.getY(), iCity.getX(), iCity.getY() )])

					if( cityDist <= 0.8*self.closeRadius ) :
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s is close enough to another rebelling city to join in independence quest"%(pCity.getName()))
						indCities.append(pCity)

		bodStr = getCityTextList(indCities, bPreCity = True, bPostIs = True)

		iBuyOffCost = -1

		if( bPeaceful ) :
			if( pPlayer.isStateReligion() ) :
				if( 70 > game.getSorenRandNum(100,'Rev') ) :
					giveRelType = pPlayer.getStateReligion()
				else :
					giveRelType = -1
			else :
				if( 50 > game.getSorenRandNum(100,'Rev') ) :
					giveRelType = None
				else :
					giveRelType = -1
			# lfgr note: split allowed
			[pRevPlayer,bIsJoinWar] = self.chooseRevolutionCiv( indCities, bJoinCultureWar = False, bReincarnate = True, bJoinRebels = True, bSpreadRebels = True, giveRelType = giveRelType, bMatchCivics = True )
			#iBuyOffCost = (100 + 20*pPlayer.getCurrentRealEra())*len(indCities) + game.getSorenRandNum(100+20*pPlayer.getCurrentRealEra(),'Rev')
			totalRevIdx = 0
			totalPop = 0
			for pCity in indCities :
				totalRevIdx += pCity.getRevolutionIndex()
				totalPop += pCity.getPopulation()
			iBuyOffCost = totalRevIdx/(17-pPlayer.getCurrentRealEra()) + game.getSorenRandNum(50+10*pPlayer.getCurrentRealEra(),'Rev')
			if( not pPlayer.isHuman() ) : iBuyOffCost = int( iBuyOffCost*.7 )
			iBuyOffCost = max( [iBuyOffCost,pPlayer.getGold()/8 + game.getSorenRandNum(50,'Rev')] )

			# Determine Vassal or no
			# if annoyed or worse, ask for independence
			# if tiny or really like, ask capitulation
			# othwise ask for free vassal
			vassalStyle = None
			if( not pTeam.isAVassal() and pTeam.isVassalStateTrading() ) :
				if( pRevPlayer.AI_getAttitude(pPlayer.getID()) == AttitudeTypes.ATTITUDE_FURIOUS or pRevPlayer.AI_getAttitude(pPlayer.getID()) == AttitudeTypes.ATTITUDE_ANNOYED ) :
					vassalStyle = None
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Vassal style: No due to attitude")
				elif( totalPop < pPlayer.getTotalPopulation()/3 ) :
					if( pRevPlayer.AI_getAttitude(pPlayer.getID()) == AttitudeTypes.ATTITUDE_FRIENDLY or pRevPlayer.AI_getAttitude(pPlayer.getID()) == AttitudeTypes.ATTITUDE_PLEASED ) :
						vassalStyle = 'capitulated'
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Vassal style %s chosen from size and attitude"%(vassalStyle))
					elif( totalPop < pPlayer.getTotalPopulation()/6 ) :
						vassalStyle = 'capitulated'
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Vassal style %s chosen from size"%(vassalStyle))
					else :
						vassalStyle = 'free'
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Vassal style %s chosen from size"%(vassalStyle))
				elif( pRevPlayer.AI_getAttitude(pPlayer.getID()) == AttitudeTypes.ATTITUDE_FURIOUS or pRevPlayer.AI_getAttitude(pPlayer.getID()) == AttitudeTypes.ATTITUDE_FURIOUS ) :
					vassalStyle = 'free'
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Vassal style %s chosen from attitude"%(vassalStyle))


			if( not vassalStyle == None ) :
				bodStr += ' ' + localText.getText("TXT_KEY_REV_IND_PEACE_VASSAL",())
				bodStr += ' %s '%(pRevPlayer.getCivilizationShortDescription(0)) + localText.getText("TXT_KEY_REV_IND_PEACE_BECOME",())
				if( vassalStyle == 'free' ) :
					bodStr += ' %s '%(localText.getText("TXT_KEY_REV_VASSAL_FREE",()))
				else :
					bodStr += ' %s '%(localText.getText("TXT_KEY_REV_VASSAL_CAP",()))
				bodStr += localText.getText("TXT_KEY_REV_IND_PEACE_GRANT",())
			else :
				if( pRevPlayer.isAlive() ) :
					bodStr += ' ' + localText.getText("TXT_KEY_REV_IND_PEACE_REQUEST_ALIVE",())%(pRevPlayer.getCivilizationShortDescription(0))
				else :
					bodStr += ' ' + localText.getText("TXT_KEY_REV_IND_PEACE_REQUEST",()) + ' %s.'%(pRevPlayer.getCivilizationShortDescription(0))
			bodStr += '\n\n' + localText.getText("TXT_KEY_REV_IND_PEACE_ACTION",())
			if( pPlayer.getGold() > iBuyOffCost ) :
				bodStr += '\n\n' + localText.getText("TXT_KEY_REV_IND_PEACE_ACTION2",())

		else :
			# lfgr note: split allowed
			[pRevPlayer,bIsJoinWar] = self.chooseRevolutionCiv( indCities, bJoinCultureWar = False, bReincarnate = True, bJoinRebels = True, bSpreadRebels = False )
			vassalStyle = None
			if( self.allowSmallBarbRevs and len(indCities) == 1 ) :
				if( instRevIdx < int(1.4*self.revInstigatorThreshold) ) :
					if( not instigator.area().isBorderObstacle(pPlayer.getTeam()) ) :
						pRevPlayer = gc.getPlayer( gc.getBARBARIAN_PLAYER() )
						bIsJoinWar = False
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Small, disorganized Revolution")
			bodStr += ' ' + localText.getText("TXT_KEY_REV_IND_VIOLENT_DEMAND",())
			if( pRevPlayer.isBarbarian() ) :
				bodStr += " " + localText.getText("TXT_KEY_REV_IND_VIOLENT_BARB",())
			else :
				bodStr += ' ' + localText.getText("TXT_KEY_REV_IND_VIOLENT_FORM",()) + ' %s.'%(pRevPlayer.getCivilizationShortDescription(0))
			bodStr += '\n\n' + localText.getText("TXT_KEY_REV_IND_VIOLENT_FIGHT",())

		if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %d cities in revolution, buyoff cost %d"%(len(indCities),iBuyOffCost))
		assert( len(indCities) > 0 )
		specialDataDict = { 'iRevPlayer' : pRevPlayer.getID(), 'bIsJoinWar' : bIsJoinWar, 'iBuyOffCost' : iBuyOffCost, 'vassalStyle' : vassalStyle }
		cityIdxs = list()
		for pCity in indCities :
			cityIdxs.append( pCity.getID() )
		revData = RevDefs.RevoltData( pPlayer.getID(), game.getGameTurn(), cityIdxs, 'independence', bPeaceful, specialDataDict )

		revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
		iRevoltIdx = len(revoltDict.keys())
		revoltDict[iRevoltIdx] = revData
		RevData.revObjectUpdateVal( pPlayer, 'RevoltDict', revoltDict )

		self.makeRevolutionDecision( pPlayer, iRevoltIdx, indCities, 'independence', bPeaceful, bodStr )

		return


	# lfgr: added parameter iSplitType
	def chooseRevolutionCiv( self, cityList, bJoinCultureWar = True, bReincarnate = True, bJoinRebels = True, bSpreadRebels = False, pNotThisCiv = None, giveTechs = True, giveRelType = -1, bMatchCivics = False, iSplitType = RevCivUtils.SPLIT_ALLOWED, iForcedCivilization = -1 ) :
		# All cities should have same owner

		pRevPlayer = None
		bIsJoinWar = False

		owner = gc.getPlayer( cityList[0].getOwner() )
		ownerTeam = gc.getTeam( owner.getTeam() )

		# TODO:  Turn into a pick best option as opposed to first option
		# Attempt to find a worthy civ to reincarnate from these cities
		instigator = cityList[0]
		closeCityList = list()
		for pCity in cityList :
			if( plotDistance( pCity.getX(), pCity.getY(), instigator.getX(), instigator.getY() ) < 0.7*self.closeRadius ) :
				closeCityList.append( pCity )

		for pCity in closeCityList :

			if pRevPlayer is None:

				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Looking for revolution worthy civ in %s"%(pCity.getName()))

				cultPlayer = None
				if( pCity.countTotalCultureTimes100() > 50*100 ) :
					cultPlayer = gc.getPlayer( pCity.findHighestCulture() )
					if( cultPlayer.getID() == owner.getID() or cultPlayer.isBarbarian() or cultPlayer.isMinorCiv() ) :
						cultPlayer = None

				if( bJoinCultureWar and not cultPlayer == None ) :
					# If at war with significant culture, join them
					if( ownerTeam.getAtWarCount(True) > 0 ) :
						if( ownerTeam.isAtWar(cultPlayer.getID()) and cultPlayer.isAlive() ) :
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Owner at war with dominant culture player %s"%(cultPlayer.getCivilizationDescription(0)))
							pRevPlayer = cultPlayer
							if( cultPlayer.getNumCities() > 2 ) :
								bIsJoinWar = True

				if( bJoinRebels and pRevPlayer == None ) :
					# If at war with this cities rebel civ type, join them
					eRevPlayer = RevData.getRevolutionPlayer( pCity )
					if eRevPlayer >= 0 :
						pMaybeRevPlayer = gc.getPlayer( eRevPlayer )
						if pMaybeRevPlayer.isAlive() :
							if ownerTeam.isAtWar( pMaybeRevPlayer.getTeam() ) and ownerTeam.isHasMet( pMaybeRevPlayer.getTeam() ):
								if RevUtils.getNumDefendersNearPlot( pCity.getX(), pCity.getY(), eRevPlayer, iRange = 5, bIncludePlot = True, bIncludeCities = True ) > 0:
									pRevPlayer = pMaybeRevPlayer
									if self.LOG_DEBUG : CvUtil.pyPrint( "  Revolt - Owner at war with cities revolt civ type, player %s" % (pRevPlayer.getCivilizationDescription( 0 )) )
				
				if( bReincarnate and pRevPlayer == None ) :
					# Check for civ that can rise from the ashes
					for i in range(0,gc.getMAX_CIV_PLAYERS()) :
						if( not i == owner.getID() ) :
							playerI = gc.getPlayer( i )
							if( (not playerI.isAlive()) and (pCity.getCulture( i ) > 50) ) :
								pRevPlayer = playerI
								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Reincarnating player %s"%(pRevPlayer.getCivilizationDescription(0)))
								break

		# Search around all cities for a rebellion that wants to spill over into this territory
		if( bSpreadRebels and pRevPlayer == None ) :
			#if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Checking for rebellions that could spill over")

			rebelIDList = list()
			for i in range(0,gc.getMAX_CIV_PLAYERS()) :
				# LFGR_TODO: pCity is the last city from the loop above, is this intended?
				if( not i == owner.getID() and pCity.area().getUnitsPerPlayer(i) > 0 ) :
					playerI = gc.getPlayer(i)
					teamI = gc.getTeam( playerI.getTeam() )
					relations = playerI.AI_getAttitude(owner.getID())

					if( playerI.isRebel() and teamI.canDeclareWar(ownerTeam.getID()) ) :
						if( not playerI.isFoundedFirstCity() ) :  # Is a homeless rebel
							if i == RevData.getRevolutionPlayer( pCity ) :
								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Homeless rebel (type) %s in area"%(playerI.getCivilizationDescription(0)))
								rebelIDList.append(i)
							elif( teamI.isAtWar(ownerTeam.getID()) ) :
								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Homeless rebel (at war) %s in area"%(playerI.getCivilizationDescription(0)))
								rebelIDList.append(i)
							elif( relations == AttitudeTypes.ATTITUDE_FURIOUS or relations == AttitudeTypes.ATTITUDE_ANNOYED ) :
								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Homeless rebel (attitude) %s in area"%(playerI.getCivilizationDescription(0)))
								rebelIDList.append(i)

						if( playerI.getCitiesLost() < 3 and playerI.getNumCities() < 4 ) :
							if( game.getGameTurn() - playerI.getCapitalCity().getGameTurnAcquired() < 30 and not playerI.getCapitalCity().getPreviousOwner() == gc.getBARBARIAN_PLAYER() ) :
								if i == RevData.getRevolutionPlayer( pCity ) :
									if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Young rebel (type) %s in area"%(playerI.getCivilizationDescription(0)))
									rebelIDList.append(i)
								elif( teamI.isAtWar(ownerTeam.getID()) ) :
									if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Young rebel (at war) %s in area"%(playerI.getCivilizationDescription(0)))
									rebelIDList.append(i)
								elif( relations == AttitudeTypes.ATTITUDE_FURIOUS or relations == AttitudeTypes.ATTITUDE_ANNOYED ) :
									if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Young rebel (attitude) %s in area"%(playerI.getCivilizationDescription(0)))
									rebelIDList.append(i)

			if( len(rebelIDList) > 0 ) :
				for pCity in closeCityList :
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Checking around %s for other rebellion"%(pCity.getName()))

					for [radius,plotI] in RevUtils.plotGenerator( pCity.plot(), 6 ) :
						for rebelID in rebelIDList :
							if( plotI.getNumDefenders(rebelID) > 0 ) :
								pRevPlayer = gc.getPlayer(rebelID)
								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Found %s within %d, expanding their rebellion!"%(pRevPlayer.getCivilizationDescription(0),radius))
								break

						if( not pRevPlayer == None ) :
							break

					if( not pRevPlayer == None ) :
							break

		# Search around all cities in list for a dead player to reincarnate
		if( pRevPlayer == None and bReincarnate ) :
			if( game.countCivPlayersAlive() < game.countCivPlayersEverAlive() ) :

				deadCivs = list()
				for idx in range(0,gc.getMAX_CIV_PLAYERS()) :
					playerI = gc.getPlayer(idx)
					if( not playerI.isAlive() and playerI.isEverAlive() ) :
						# TODO: Should this also check for revData?
						deadCivs.append(idx)

				for pCity in closeCityList :
					if( pRevPlayer == None ) :
						for civIdx in deadCivs :
							playerI = gc.getPlayer(civIdx)
							if idx == RevData.getRevolutionPlayer( pCity ) :
								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Reincarnation %s's rev civ, the %s"%(pCity.getName(),playerI.getCivilizationDescription(0)))
								pRevPlayer = playerI
								break

				for pCity in closeCityList :
					if( pRevPlayer == None ) :

						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Checking around %s for dead player"%(pCity.getName()))
						maxCult = 0
						maxCultRad = 5
						for [radius,plotI] in RevUtils.plotGenerator( pCity.plot(), 4 ) :

							if( not pRevPlayer == None and radius > maxCultRad ) :
								break

							for civIdx in deadCivs :
								if( plotI.getCulture(civIdx) > maxCult ) :
									if( self.LOG_DEBUG ) : CvUtil.pyPrint("Revolt: Found plot culture from dead player %d"%(civIdx))
									maxCult = plotI.getCulture(civIdx)
									maxCultRad = radius
									pRevPlayer = gc.getPlayer(civIdx)

		# Create new civ based on culture/owner of first city in list
		if( pRevPlayer == None ) :

			pCity = cityList[0]
			owner = gc.getPlayer( pCity.getOwner() )
			ownerTeam = gc.getTeam( owner.getTeam() )

			# Search for empty slot
			newPlayerIdx = -1
			for i in range(0,gc.getMAX_CIV_PLAYERS()) :
				if( (not gc.getPlayer(i).isAlive()) and (not gc.getPlayer(i).isEverAlive()) and (not RevData.revObjectExists(gc.getPlayer(i))) ) :
					newPlayerIdx = i
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Creating new player in slot %d"%(i))
					break

#			if( newPlayerIdx < 0 ) :
#				# Overwrite a civ that never managed to found a city and hasn't lost a city (probably a previous rebel)
#				for i in range(0,gc.getMAX_CIV_PLAYERS()) :
#					if( (not gc.getPlayer(i).isAlive()) and (not gc.getPlayer(i).isFoundedFirstCity()) and gc.getPlayer(i).getCitiesLost() == 0 and (gc.getPlayer(i).getNumUnits() == 0) ) :
#						if( RevData.revObjectExists(gc.getPlayer(i)) ) :
#							if( len(RevData.revObjectGetVal( gc.getPlayer(i), 'SpawnList' )) ) :
#								# Revolution pending for this player slot already
#								continue
#						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Overwriting dead player %d, has founded city: %d Num cities lost: %d"%(i,gc.getPlayer(i).isFoundedFirstCity(),gc.getPlayer(i).getCitiesLost()))
#						RevData.initPlayer( gc.getPlayer(i) )
#						newPlayerIdx = i
#						break

			if( newPlayerIdx < 0 ) :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - No available slots, spawning as Barbarians")
				pRevPlayer = gc.getPlayer( gc.getBARBARIAN_PLAYER() )
				return [pRevPlayer, bIsJoinWar]

			# lfgr: use RevCivUtils

			# capital should not form new civs
			isCapital = False
			for pCity in cityList :
				if( pCity.isCapital() ) :
					isCapital = True
					break

			if( isCapital ) :
				iSplitType = RevCivUtils.SPLIT_FORCED
			if( ( not isCapital ) and iForcedCivilization != -1 ):#
				print "force civ %i"%( iForcedCivilization )
				iOldCivType = iForcedCivilization
			else :
				print "do not force civ %i (capital)"%( iForcedCivilization )
				iOldCivType = owner.getCivilizationType()
			# TODO: that seems not to work
			pCultureOwner = None
			if instigator != None:
				if instigator.findHighestCulture() != -1:
					pCultureOwner = gc.getPlayer( instigator.findHighestCulture() )
			if( pCultureOwner != None ) :
				iCultureOwnerCivType = pCultureOwner.getCivilizationType()
			else :
				iCultureOwnerCivType = iOldCivType

			newCivIdx, newLeaderIdx = rcu.chooseNewCivAndLeader( iOldCivType, iCultureOwnerCivType, iSplitType, giveRelType, instigator.plot().getX(), instigator.plot().getY() )

			if( newLeaderIdx < 0 ) :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - LeaderIdx < 0, spawning as Barbarians")
				pRevPlayer = gc.getPlayer( gc.getBARBARIAN_PLAYER() )
				return [pRevPlayer, bIsJoinWar]
			# end lfgr

			# lfgr: removed RebelTypes stuff

			game.addPlayer( newPlayerIdx, newLeaderIdx, newCivIdx, false )
#			gc.getPlayer(game.getActivePlayer()).initNewEmpire(newLeaderIdx, newPlayerIdx)

			if( False ) :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - New civ creation failed, spawning as Barbarians")
				pRevPlayer = gc.getPlayer( gc.getBARBARIAN_PLAYER() )
				return [pRevPlayer, bIsJoinWar]

			pRevPlayer = gc.getPlayer(newPlayerIdx)

			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Created the %s in slot %d"%(pRevPlayer.getCivilizationDescription(0),pRevPlayer.getID()))

		# Do special setup for non-living revolutionaries ...

		if( giveTechs and not pRevPlayer.isAlive() and not pRevPlayer.isBarbarian() ) :
			RevUtils.giveTechs( pRevPlayer, owner )

		if( not giveRelType == None and not pRevPlayer.isAlive() and not pRevPlayer.isBarbarian() and not pRevPlayer.isAgnostic()) :
			if( giveRelType >= 0 ) :
				# Give specified religion
				# THOLAL TODO - skip this section is leader has a -100 rating towards that religion
#				pRevPlayer.setLastStateReligion( giveRelType )
				pRevPlayer.convert( giveRelType )
				if( self.LOG_DEBUG ) :
					#CvUtil.pyPrint("  Revolt - Setting revolutionary's religion to %d"%(giveRelType))
					religionDesc = gc.getReligionInfo(giveRelType).getDescription()
					CvUtil.pyPrint("  Revolt - Revolutionary's religion set to %s"%(religionDesc))
			else :
				# Give minority religion in city
				availRels = list()
				for relType in range(0,gc.getNumReligionInfos()) :
					if( not relType == owner.getStateReligion() ) :
						if( pCity.isHolyCityByType(relType) ) :
							#if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s is holy city for non-state religion %s"%(pCity.getName(), gc.getReligionInfo( relType ).getDescription()))
							giveRelType = relType
						elif( pCity.isHasReligion(relType) ) :
							availRels.append( relType )

				if( giveRelType < 0 ) :
					if( len(availRels) > 0 ) :
						giveRelType = availRels[game.getSorenRandNum(len(availRels),'Revolution: pick religion')]

				if( giveRelType >= 0 ) :
					pRevPlayer.setLastStateReligion( giveRelType )
					if( self.LOG_DEBUG ) :
						#CvUtil.pyPrint("  Revolt - Setting revolutionary's religion to %d"%(giveRelType))
						religionDesc = gc.getReligionInfo(giveRelType).getDescription()
						CvUtil.pyPrint("  Revolt - Revolutionary's religion set to %s"%(religionDesc))

		if( bMatchCivics ) :
			pPlayer = gc.getPlayer( pCity.getOwner() )
			for civicOptionID in range(0,gc.getNumCivicOptionInfos()) :
				#civicOption = gc.getCivicOptionInfo(civicOptionID)
				civicType = pPlayer.getCivics(civicOptionID)
				if( pRevPlayer.canDoCivics( civicType ) ) :
					pRevPlayer.setCivics( civicOptionID, civicType )

		if( not pRevPlayer.isAlive() and game.countCivPlayersAlive() >= self.maxCivs ) :
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Reached max civs limit, spawning as Barbarians")
			pRevPlayer = gc.getPlayer( gc.getBARBARIAN_PLAYER() )
			return [pRevPlayer, False]

		return [pRevPlayer, bIsJoinWar]


	def chooseRevolutionLeader( self, cityList ) :
		""" Choose Leader for a "change in leadership" revolution. """
		newLeaderType = None
		newLeaderName = None

		owner = gc.getPlayer( cityList[0].getOwner() )
		ownerCivType = owner.getCivilizationType()
		ownerLeaderType = owner.getLeaderType()
		ownerCivInfo = gc.getCivilizationInfo( ownerCivType )

		# Use new leader type
		count = 0
		availLeader = list()
		for i in range(0,gc.getNumLeaderHeadInfos()) :
			if( ownerCivInfo.isLeaders(i) or game.isOption( GameOptionTypes.GAMEOPTION_LEAD_ANY_CIV ) ) :
				taken = False
				for jdx in range(0,gc.getMAX_PLAYERS()) :
					if( gc.getPlayer(jdx).getLeaderType() == i ) :
						taken = True
						break
				if( not taken ) :
					count += 1
					availLeader.append(i)

		#if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Found %d available from %d for civ"%(len(availLeader),count))

		if( len(availLeader) > 0 ) :
			newLeaderType = availLeader[game.getSorenRandNum(len(availLeader),'Revolution: pick leader')]
			newLeaderName = gc.getLeaderHeadInfo( newLeaderType ).getDescription()
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Switching from leader type %d to %d (%s)"%(ownerLeaderType,newLeaderType,newLeaderName))

		# LFGR_TODO: Use FfHNames.setNewLeaderName?
		if( newLeaderType == None ) :
			# Use same leader type, but with new name
			newLeaderType = ownerLeaderType
			newLeaderName = gc.getLeaderHeadInfo( newLeaderType ).getDescription()
			newLeaderName = CvUtil.convertToStr(newLeaderName)
			if( newLeaderName == owner.getName() ) :
				# Hack Roman numeral naming
				if( newLeaderName[-3:len(newLeaderName)] == ' II' ) :
					newLeaderName = newLeaderName + 'I'
				elif( newLeaderName[-2:len(newLeaderName)] == ' I' ) :
					newLeaderName = newLeaderName + 'I'
				else :
					newLeaderName = newLeaderName + ' II'
			else :
				newLeaderName = newLeaderName
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - No new leader available, using current type %d (%s)"%(newLeaderType,newLeaderName))

		return [newLeaderType,newLeaderName]


##--- Revolution decision functions ------------------------------------------

	def makeRevolutionDecision( self, pPlayer, iRevoltIdx, cityList, revType, bPeaceful, bodStr ) :
		revData = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )[iRevoltIdx]

#-------------------------------------------------------------------------------------------------
# Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
# Enable only for debugging different revolution styles
#		if( self.LOG_DEBUG and self.isHumanPlayerOrAutoPlay(pPlayer.getID()) and game.getAIAutoPlay(pPlayer.getID()) > 0 ) :
#			bCanCancelAuto = SdToolKitCustom.sdObjectGetVal( "AIAutoPlay", game, "bCanCancelAuto" )
#			game.setForcedAIAutoPlay(pPlayer.getID(), 0, false)
#-------------------------------------------------------------------------------------------------
# END Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------

		pTeam = gc.getTeam( pPlayer.getTeam() )
		iAggressive = CvUtil.findInfoTypeNum(gc.getTraitInfo,gc.getNumTraitInfos(),RevDefs.sXMLAggressive)
		iSpiritual = CvUtil.findInfoTypeNum(gc.getTraitInfo,gc.getNumTraitInfos(),RevDefs.sXMLSpiritual)
		numRevCities = len(revData.cityList)

		pRevPlayer = None
		bIsBarbRev = False
		if( 'iRevPlayer' in revData.dict.keys() ) :
			pRevPlayer = gc.getPlayer(revData.dict['iRevPlayer'])
			bIsBarbRev = pRevPlayer.isBarbarian()

		isRevType = True

		if( revType == 'civics' ) :

			iNewCivic = revData.dict['iNewCivic']
			iBuyOffCost = revData.dict.get( 'iBuyOffCost', -1 )

			if( bPeaceful ) :
				if( numRevCities > pPlayer.getNumCities()/2 ) :
					iOdds = 70
				elif( numRevCities < pPlayer.getNumCities()/4 ) :
					iOdds = 25
				else :
					iOdds = 40
			else :
				if( numRevCities > pPlayer.getNumCities()/2 ) :
					iOdds = 80
				elif( numRevCities < pPlayer.getNumCities()/4 ) :
					iOdds = 40
				else :
					iOdds = 60

			iOdds += self.RevOpt.getCivicsOdds()

			if( self.isLocalHumanPlayer(pPlayer.getID()) ) :
				# Offer choice
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Offering human choice on civics")

				# Additions by Caesium et al
				caesiumtR = CyUserProfile().getResolutionString(CyUserProfile().getResolution())
				caesiumtextResolution = caesiumtR.split('x')
				caesiumpasx = int(caesiumtextResolution[0])/10
				caesiumpasy = int(caesiumtextResolution[1])/10
				popup = PyPopup.PyPopup( RevDefs.revolutionPopup, contextType = EventContextTypes.EVENTCONTEXT_ALL, bDynamic = False)
				if( self.centerPopups ) : popup.setPosition(3*caesiumpasx,3*caesiumpasy)
				# End additions by Caesium et al
				if( bPeaceful ) :
					popup.setHeaderString( localText.getText("TXT_KEY_REV_TITLE_PEACEFUL",()) )
				else :
					popup.setHeaderString( localText.getText("TXT_KEY_REV_TITLE_VIOLENT",()) )
				if( iOdds >= 70 ) :
					bodStr += "\n\n" + localText.getText("TXT_KEY_REV_ADVISOR_ACCEPT",())
				elif( iOdds <= 30 ) :
					bodStr += "\n\n" + localText.getText("TXT_KEY_REV_ADVISOR_REJECT",())
				else :
					bodStr += "\n\n" + localText.getText("TXT_KEY_REV_ADVISOR_NEUTRAL",())
				popup.setBodyString( bodStr )
				popup.addButton( localText.getText("TXT_KEY_REV_BUTTON_ACCEPT",()) )
				buttons = ('accept',)
				popup.addButton( localText.getText("TXT_KEY_REV_BUTTON_REJECT",()) )
				buttons += ('reject',)
				if( iBuyOffCost > 0 and iBuyOffCost <= pPlayer.getGold() ) :
					popup.addButton( localText.getText("TXT_KEY_REV_BUTTON_BUYOFF",()) + ' %d'%(iBuyOffCost) )
					buttons += ('buyoff',)
				if( not bPeaceful and not 'iJoinPlayer' in revData.dict.keys() and not bIsBarbRev and (pRevPlayer.getNumCities() == 0) and self.offerDefectToRevs ) :
					popup.addButton( localText.getText("TXT_KEY_REV_BUTTON_DEFECT",()) )
					buttons += ('defect',)

				popup.setUserData( (buttons, pPlayer.getID(), iRevoltIdx) )
				# Center camera on city
				CyCamera().JustLookAt( cityList[0].plot().getPoint() )
				popup.launch(bCreateOkButton = False)

			elif (not pPlayer.isHuman()) :
				# Make AI decision
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Making AI choice on civics")

				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Odds are %d"%(iOdds))

				if( game.getSorenRandNum(100,'Revolt: switch civics') < iOdds ) :
					self.processRevolution( pPlayer, iRevoltIdx, cityList, revType, bPeaceful, True )

				else :
					if( iBuyOffCost > 0 and iBuyOffCost <= pPlayer.getGold() ) :
						if( bPeaceful ) :
							base = .8
						else :
							base = .7
#-------------------------------------------------------------------------------------------------
# Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
						buyOdds = int( float(iOdds)/2.0 + 75.0*(1.0 - pow(base,float(pPlayer.getGold())/float(iBuyOffCost))) )
#-------------------------------------------------------------------------------------------------
# END Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - AI buyoff iOdds are %d, with base %.1f, from cost %d and gold %d"%(buyOdds,base,iBuyOffCost,pPlayer.getGold()))
						if( buyOdds > game.getSorenRandNum( 100, 'Revolt - AI buyoff decision' ) ) :
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - AI buyingoff rebels")
							revData.dict['bDidBuyOff'] = True

							revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
							revoltDict[iRevoltIdx] = revData
							RevData.revObjectSetVal( pPlayer, 'RevoltDict', revoltDict )

							self.processRevolution( pPlayer, iRevoltIdx, cityList, revType, bPeaceful, False )
							return

					self.processRevolution( pPlayer, iRevoltIdx, cityList, revType, bPeaceful, False )

		elif( revType == 'religion' ) :

			iNewReligion = revData.dict['iNewReligion']
			iBuyOffCost = revData.dict.get( 'iBuyOffCost', -1 )

			if( not pPlayer.isStateReligion() ) :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - AI has no state religion ... this shouldn't happen")
				return

			newCount = pPlayer.getHasReligionCount( iNewReligion )
			newHoly = pPlayer.hasHolyCity( iNewReligion )

			stateCount = pPlayer.getHasReligionCount( pPlayer.getStateReligion() )
			stateHoly = pPlayer.hasHolyCity( pPlayer.getStateReligion() )

			if( stateHoly and not newHoly ) :
				iOdds = 0
			elif( newHoly and not stateHoly ) :
				if( pPlayer.hasTrait( iSpiritual ) ) :
					# Spiritual player will spread religion pretty quickly
					if( stateCount > 2*newCount ) :
						iOdds = 60
					else :
						iOdds = 100
				else :
					if( stateCount > 2*newCount ) :
						iOdds = 30
					elif( newCount > stateCount ) :
						iOdds = 100
					else :
						iOdds = 70
			else :
				if( stateCount > 2*newCount ) :
					iOdds = 0
				elif( newCount > stateCount ) :
					iOdds = 70
				else :
					iOdds = 30

			iOdds += self.RevOpt.getReligionOdds()

			if( self.isLocalHumanPlayer(pPlayer.getID()) ) :
				# Offer choice
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Offering human choice on religion change")

				# Additions by Caesium et al
				caesiumtR = CyUserProfile().getResolutionString(CyUserProfile().getResolution())
				caesiumtextResolution = caesiumtR.split('x')
				caesiumpasx = int(caesiumtextResolution[0])/10
				caesiumpasy = int(caesiumtextResolution[1])/10
				popup = PyPopup.PyPopup( RevDefs.revolutionPopup, contextType = EventContextTypes.EVENTCONTEXT_ALL, bDynamic = False)
				if( self.centerPopups ) : popup.setPosition(3*caesiumpasx,3*caesiumpasy)
				# End additions by Caesium et al
				if( bPeaceful ) :
					popup.setHeaderString( localText.getText("TXT_KEY_REV_TITLE_PEACEFUL",()) )
				else :
					popup.setHeaderString( localText.getText("TXT_KEY_REV_TITLE_VIOLENT",()) )
				if( iOdds >= 70 ) :
					bodStr += "\n\n" + localText.getText("TXT_KEY_REV_ADVISOR_ACCEPT",())
				elif( iOdds <= 30 ) :
					bodStr += "\n\n" + localText.getText("TXT_KEY_REV_ADVISOR_REJECT",())
				else :
					bodStr += "\n\n" + localText.getText("TXT_KEY_REV_ADVISOR_NEUTRAL",())
				popup.setBodyString( bodStr )
				popup.addButton( localText.getText("TXT_KEY_REV_BUTTON_ACCEPT",()) )
				buttons = ('accept',)
				popup.addButton( localText.getText("TXT_KEY_REV_BUTTON_REJECT",()) )
				buttons += ('reject',)
				if( iBuyOffCost > 0 and iBuyOffCost <= pPlayer.getGold() ) :
					popup.addButton( localText.getText("TXT_KEY_REV_BUTTON_BUYOFF",()) + ' %d'%(iBuyOffCost) )
					buttons += ('buyoff',)
				if( not bPeaceful and not 'iJoinPlayer' in revData.dict.keys() and not bIsBarbRev and (pRevPlayer.getNumCities() == 0) and self.offerDefectToRevs ) :
					popup.addButton( localText.getText("TXT_KEY_REV_BUTTON_DEFECT",()) )
					buttons += ('defect',)

				popup.setUserData( (buttons, pPlayer.getID(), iRevoltIdx) )
				# Center camera on city
				CyCamera().JustLookAt( cityList[0].plot().getPoint() )
				popup.launch(bCreateOkButton = False)

			elif (not pPlayer.isHuman()) :
				# Make AI decision
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Making AI choice on religion change")

				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Odds are %d"%(iOdds))

				if( game.getSorenRandNum(100,'Revolt: switch religion') < iOdds ) :
					self.processRevolution( pPlayer, iRevoltIdx, cityList, revType, bPeaceful, True )

				else :
					if( iBuyOffCost > 0 and iBuyOffCost <= pPlayer.getGold() ) :
						if( bPeaceful ) :
							base = .8
						else :
							base = .7
#-------------------------------------------------------------------------------------------------
# Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
						buyOdds = int( float(iOdds)/2.0 + 75.0*(1.0 - pow(base,float(pPlayer.getGold())/float(iBuyOffCost))) )
#-------------------------------------------------------------------------------------------------
# END Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - AI buyoff odds are %d, with base %.1f, from cost %d and gold %d"%(buyOdds,base,iBuyOffCost,pPlayer.getGold()))
						if( buyOdds > game.getSorenRandNum( 100, 'Revolt - AI buyoff decision' ) ) :
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - AI buyingoff rebels")
							revData.dict['bDidBuyOff'] = True

							revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
							revoltDict[iRevoltIdx] = revData
							RevData.revObjectSetVal( pPlayer, 'RevoltDict', revoltDict )

							self.processRevolution( pPlayer, iRevoltIdx, cityList, revType, bPeaceful, False )
							return

					self.processRevolution( pPlayer, iRevoltIdx, cityList, revType, bPeaceful, False )

		elif( revType == 'leader' ) :

			# Load special data for this type
			iNewLeaderType = revData.dict['iNewLeaderType']
			if( 'newLeaderName' in revData.dict.keys() ) :
				newLeaderName = revData.dict['newLeaderName']
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Potential new leader: %s"%(newLeaderName))
			bIsElection = revData.dict['bIsElection']
			iBuyOffCost = revData.dict.get( 'iBuyOffCost', -1 )

			# Compute approval rating (formula from demographics info screen)
			if (pPlayer.calculateTotalCityHappiness() > 0) :
				iHappiness = int((1.0 * pPlayer.calculateTotalCityHappiness()) / (pPlayer.calculateTotalCityHappiness() + \
									pPlayer.calculateTotalCityUnhappiness()) * 100)
			else :
				iHappiness = 100

			# Adjusted approval rating based on num cities in revolt
			if( numRevCities > pPlayer.getNumCities()/2 ) :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Approval rating (initially %d) adjusted due to %d of %d cities revolting"%(iHappiness,numRevCities,pPlayer.getNumCities()))
				iHappiness = int( iHappiness - 100*(numRevCities - pPlayer.getNumCities()/2)/(2.0*pPlayer.getNumCities()) )
				iHappiness = max([iHappiness,25])

			revData.dict['iHappiness'] = iHappiness

			revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
			revoltDict[iRevoltIdx] = revData
			RevData.revObjectSetVal( pPlayer, 'RevoltDict', revoltDict )

			# Other potential factors:
			# Player rank

			if( numRevCities > pPlayer.getNumCities()/2 ) :
				iOdds = 50
				if( bPeaceful ) :
					iOdds -= 20
				else :
					if( pTeam.getAtWarCount(True) > 1 ) :
						iOdds += 10
				if( pPlayer.hasTrait(iAggressive) ) :
					iOdds -= 30
			elif( numRevCities < pPlayer.getNumCities()/4 ) :
				iOdds = 25
				if( bPeaceful ) :
					iOdds -= 20
				else :
					if( pTeam.getAtWarCount(True) > 1 ) :
						iOdds += 10
				if( pPlayer.hasTrait(iAggressive) ) :
					iOdds -= 20
			else :
				iOdds = 35
				if( bPeaceful ) :
					iOdds -= 30
				else :
					if( pTeam.getAtWarCount(True) > 1 ) :
						iOdds += 10
				if( pPlayer.hasTrait(iAggressive) ) :
					iOdds -= 20

			if( bIsElection ) :
				if( iHappiness > 55 ) :
					iOdds += 40
				elif( iHappiness < 40 ) :
					iOdds -= 30
				elif( iHappiness < 50 ) :
					iOdds -= 15
				else :
					iOdds += 10

			iOdds += self.RevOpt.getLeaderOdds()

			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Odds are %d"%(iOdds))
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Adjusted approval rating is %d"%(iHappiness))

			if( self.isLocalHumanPlayer(pPlayer.getID()) ) :
				# Offer choice
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Offering human choice on leader change")

				# Additions by Caesium et al
				caesiumtR = CyUserProfile().getResolutionString(CyUserProfile().getResolution())
				caesiumtextResolution = caesiumtR.split('x')
				caesiumpasx = int(caesiumtextResolution[0])/10
				caesiumpasy = int(caesiumtextResolution[1])/10
				popup = PyPopup.PyPopup( RevDefs.revolutionPopup, contextType = EventContextTypes.EVENTCONTEXT_ALL, bDynamic = False)
				if( self.centerPopups ) : popup.setPosition(3*caesiumpasx,3*caesiumpasy)
				# End additions by Caesium et al
				if( bPeaceful ) :
					popup.setHeaderString( localText.getText("TXT_KEY_REV_TITLE_PEACEFUL",()) )
				else :
					popup.setHeaderString( localText.getText("TXT_KEY_REV_TITLE_VIOLENT",()) )
				if( iOdds >= 70 ) :
					bodStr += "\n\n" + localText.getText("TXT_KEY_REV_ADVISOR_ACCEPT",())
				elif( iOdds <= 30 ) :
					bodStr += "\n\n" + localText.getText("TXT_KEY_REV_ADVISOR_REJECT",())
				else :
					bodStr += "\n\n" + localText.getText("TXT_KEY_REV_ADVISOR_NEUTRAL",())
				if( bIsElection ) :
					bodStr += "  " + localText.getText("TXT_KEY_REV_ADVISOR_APPROVAL",()) + " %d."%(iHappiness)
					if( iHappiness < 40 ) :
						bodStr += "  " + localText.getText("TXT_KEY_REV_ADVISOR_ELEC_LOSE",())
				popup.setBodyString( bodStr )
				popup.addButton( localText.getText("TXT_KEY_REV_BUTTON_ACCEPT",()) )
				buttons = ('accept',)
				popup.addButton( localText.getText("TXT_KEY_REV_BUTTON_REJECT",()) )
				buttons += ('reject',)
				if( iBuyOffCost > 0 and iBuyOffCost <= pPlayer.getGold() ) :
					if( bIsElection ) :
						popup.addButton( localText.getText("TXT_KEY_REV_BUTTON_BUY_ELECTION",()) + ' %d'%(iBuyOffCost) )
						buttons += ('buyelection',)
					else :
						popup.addButton( localText.getText("TXT_KEY_REV_BUTTON_BUYOFF",()) + ' %d'%(iBuyOffCost) )
						buttons += ('buyoff',)
				if( not bPeaceful and not 'iJoinPlayer' in revData.dict.keys() and not bIsBarbRev and (pRevPlayer.getNumCities() == 0) and self.offerDefectToRevs ) :
					popup.addButton( localText.getText("TXT_KEY_REV_BUTTON_DEFECT",()) )
					buttons += ('defect',)

				popup.setUserData( (buttons, pPlayer.getID(), iRevoltIdx) )
				# Center camera on city
				CyCamera().JustLookAt( cityList[0].plot().getPoint() )
				popup.launch(bCreateOkButton = False)

			elif (not pPlayer.isHuman()) :
				# Make AI decision
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Making AI choice on leader change")

				if( game.getSorenRandNum(100,'Revolt: switch leader') < iOdds ) :
					self.processRevolution( pPlayer, iRevoltIdx, cityList, revType, bPeaceful, True )

				else:
					if( iBuyOffCost > 0 and iBuyOffCost <= pPlayer.getGold() ) :
						if( bPeaceful ) :
							base = .8
						else :
							base = .7
#-------------------------------------------------------------------------------------------------
# Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
						buyOdds = int( float(iOdds)/2.0 + 75.0*(1.0 - pow(base,float(pPlayer.getGold())/float(iBuyOffCost))) )
#-------------------------------------------------------------------------------------------------
# END Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - AI buyoff iOdds are %d, with base %.1f, from cost %d and gold %d"%(buyOdds,base,iBuyOffCost,pPlayer.getGold()))
						if( buyOdds > game.getSorenRandNum( 100, 'Revolt - AI buyoff decision' ) ) :
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - AI buyingoff rebels")
							revData.dict['bDidBuyOff'] = True

							revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
							revoltDict[iRevoltIdx] = revData
							RevData.revObjectSetVal( pPlayer, 'RevoltDict', revoltDict )

							self.processRevolution( pPlayer, iRevoltIdx, cityList, revType, bPeaceful, False )
							return

					self.processRevolution( pPlayer, iRevoltIdx, cityList, revType, bPeaceful, False )

		elif( revType == 'war' ) :
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Making decision on crusade")

			victim = gc.getPlayer( revData.dict['iRevPlayer'] )

			[iOdds,attackerTeam,victimTeam] = RevUtils.computeWarOdds( pPlayer, victim, cityList[0].area(), allowAttackerVassal = False, allowBreakVassal = self.bAllowBreakVassal )

			if( numRevCities > pPlayer.getNumCities()/2 ) :
				iOdds += 50

			elif( numRevCities < pPlayer.getNumCities()/4 ) :
				iOdds += 20

			else :
				iOdds += 30

			iOdds += self.RevOpt.getCrusadeOdds()

			if( self.isLocalHumanPlayer(pPlayer.getID()) ) :
				# Offer choice
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Offering human choice on crusade")

				# Additions by Caesium et al
				caesiumtR = CyUserProfile().getResolutionString(CyUserProfile().getResolution())
				caesiumtextResolution = caesiumtR.split('x')
				caesiumpasx = int(caesiumtextResolution[0])/10
				caesiumpasy = int(caesiumtextResolution[1])/10
				popup = PyPopup.PyPopup( RevDefs.revolutionPopup, contextType = EventContextTypes.EVENTCONTEXT_ALL, bDynamic = False)
				if( self.centerPopups ) : popup.setPosition(3*caesiumpasx,3*caesiumpasy)
				# End additions by Caesium et al
				if( bPeaceful ) :
					popup.setHeaderString( localText.getText("TXT_KEY_REV_TITLE_PEACEFUL",()) )
				else :
					popup.setHeaderString( localText.getText("TXT_KEY_REV_TITLE_VIOLENT",()) )
				if( iOdds >= 70 ) :
					bodStr += "\n\n" + localText.getText("TXT_KEY_REV_ADVISOR_ACCEPT",())
				elif( iOdds <= 30 ) :
					bodStr += "\n\n" + localText.getText("TXT_KEY_REV_ADVISOR_REJECT",())
				else :
					bodStr += "\n\n" + localText.getText("TXT_KEY_REV_ADVISOR_NEUTRAL",())

				popup.setBodyString( bodStr )
				popup.addButton( localText.getText("TXT_KEY_REV_BUTTON_ACCEPT",()) )
				buttons = ('accept',)
				popup.addButton( localText.getText("TXT_KEY_REV_BUTTON_REJECT",()) )
				buttons += ('reject',)

				popup.setUserData( (buttons, pPlayer.getID(), iRevoltIdx) )
				# Center camera on city
				CyCamera().JustLookAt( cityList[0].plot().getPoint() )
				popup.launch(bCreateOkButton = False)

			elif (not pPlayer.isHuman()) :
				# Make AI decision
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Making AI choice on crusade")
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Odds are %d"%(iOdds))

				if( game.getSorenRandNum(100,'Revolt: crusade') < iOdds ) :
					self.processRevolution( pPlayer, iRevoltIdx, cityList, revType, bPeaceful, True )
				else:
					self.processRevolution( pPlayer, iRevoltIdx, cityList, revType, bPeaceful, False )

		elif( revType == 'independence' ) :

			bOfferPeace = revData.dict.get( 'bOfferPeace', False )
			joinPlayer = None
			if( 'iJoinPlayer' in revData.dict.keys() ) :
				joinPlayer = gc.getPlayer( revData.dict['iJoinPlayer'] )
			iNumHandoverCities = len( revData.dict.get('HandoverCities', list()) )

			vassalStyle = revData.dict.get( 'vassalStyle', None )
			iBuyOffCost = revData.dict.get( 'iBuyOffCost', -1 )
			bIsJoinWar = revData.dict.get( 'bIsJoinWar', False )

			area = cityList[0].area()

			if( numRevCities > pPlayer.getNumCities()/2 ) :
				if( not pRevPlayer == None and pTeam.isAtWar(pRevPlayer.getTeam()) ) :
					if( area.getPower(pRevPlayer.getID()) > 1.5*area.getPower(pPlayer.getID()) and bOfferPeace ) :
						iOdds = 30
					elif( area.getPower(pRevPlayer.getID()) < area.getPower(pPlayer.getID())/2 ) :
						iOdds = -20
					else :
						iOdds = 0
				else :
					iOdds = 20
				if( bPeaceful ) :
					iOdds -= 20
				if( pPlayer.hasTrait(iAggressive) ) :
					iOdds -= 10
				if( pTeam.getAtWarCount(True) > 1 ) :
					iOdds += 5
				if( bOfferPeace ) :
					if( iNumHandoverCities < pPlayer.getNumCities()/4 ) :
						iOdds = max([iOdds + 25, 20])
					elif( iNumHandoverCities < pPlayer.getNumCities()/3 ) :
						iOdds += 15
					elif( iNumHandoverCities < pPlayer.getNumCities()/2 ) :
						iOdds += 10
					else :
						iOdds -= 0
				if( not joinPlayer == None ) :
					if( pTeam.isAtWar(joinPlayer.getTeam()) ) :
						if( bPeaceful ) :
							iOdds = 0
						else :
							iOdds -= 20
			elif( numRevCities < pPlayer.getNumCities()/4 ) :
				if( not pRevPlayer == None and pTeam.isAtWar(pRevPlayer.getTeam()) ) :
					if( area.getPower(pRevPlayer.getID()) > area.getPower(pPlayer.getID()) ) :
						iOdds = 10
						if( bOfferPeace ) :
							iOdds += 40
					elif( area.getPower(pRevPlayer.getID()) < area.getPower(pPlayer.getID())/2 ) :
						iOdds = -20
					else :
						iOdds = 0
				elif( numRevCities == 1 ) :
					iOdds = 20
				else :
					iOdds = 40
				if( bPeaceful ) :
					iOdds -= 20
				if( pPlayer.hasTrait(iAggressive) ) :
					iOdds -= 10
				if( not cityList[0].area().getID() == pPlayer.getCapitalCity().area().getID() ) :
					iOdds += 20
				if( pTeam.getAtWarCount(True) > 1 ) :
					iOdds += 10
				if( bOfferPeace ) :
					if( iNumHandoverCities < pPlayer.getNumCities()/4 ) :
						iOdds = max([iOdds + 20, 20])
					elif( iNumHandoverCities < pPlayer.getNumCities()/3 ) :
						iOdds += 10
					elif( iNumHandoverCities < pPlayer.getNumCities()/2 ) :
						iOdds += 0
					else :
						iOdds -= 20
				if( not joinPlayer == None ) :
					if( pTeam.isAtWar(joinPlayer.getTeam()) ) :
						if( bPeaceful ) :
							iOdds -= 40
						else :
							iOdds -= 30
				if( cityList[0].getNumRevolts(pPlayer.getID()) > 2 ) :
					iOdds += 10
					if( vassalStyle == 'capitulated' ) :
						iOdds += 15

				if( not vassalStyle == None ) :
					iOdds += 10

			else :
				if( not pRevPlayer == None and pTeam.isAtWar(pRevPlayer.getTeam()) ) :
					iOdds = -10
				else :
					iOdds = 25
				if( bPeaceful ) :
					iOdds -= 20
				if( pPlayer.hasTrait(iAggressive) ) :
					iOdds -= 10
				# lfgr fix
				#if( not cityList[0].area().getID() == pPlayer.getCapitalCity().area().getID() ) :
				if( cityList[0].area() != None and pPlayer.getCapitalCity().area() != None and cityList[0].area().getID() != pPlayer.getCapitalCity().area().getID() ) :
				# lfgr fix end
					iOdds += 20
				if( pTeam.getAtWarCount(True) > 1 ) :
					iOdds += 10
				if( bOfferPeace ) :
					if( iNumHandoverCities < pPlayer.getNumCities()/4 ) :
						iOdds = max([iOdds + 20, 20])
					elif( iNumHandoverCities < pPlayer.getNumCities()/3 ) :
						iOdds += 15
					elif( iNumHandoverCities < pPlayer.getNumCities()/2 ) :
						iOdds += 0
					else :
						iOdds -= 10
				if( not joinPlayer == None ) :
					if( pTeam.isAtWar(joinPlayer.getTeam()) ) :
						if( bPeaceful ) :
							iOdds -= 30
						else :
							iOdds -= 20
				if( cityList[0].getNumRevolts(pPlayer.getID()) > 2 ) :
					iOdds += 10
					if( vassalStyle == 'capitulated' ) :
						iOdds += 20
					elif( not vassalStyle == None ) :
						iOdds += 10

			iOdds += self.RevOpt.getIndependenceOdds()

			if( joinPlayer == None and bIsBarbRev ) :
				iOdds = 0

			if( bOfferPeace ) :
				if( iNumHandoverCities == pPlayer.getNumCities() ) :
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Will not surrender all cities")
					iOdds = 0
			else :
				if( numRevCities == pPlayer.getNumCities() ) :
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Will not surrender all cities")
					iOdds = 0

			if( self.isLocalHumanPlayer(pPlayer.getID()) ) :
				# Offer choice
				# TODO: is bOfferPeace properly supported?
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Offering human choice on independence")

				# Additions by Caesium et al
				caesiumtR = CyUserProfile().getResolutionString(CyUserProfile().getResolution())
				caesiumtextResolution = caesiumtR.split('x')
				caesiumpasx = int(caesiumtextResolution[0])/10
				caesiumpasy = int(caesiumtextResolution[1])/10
				popup = PyPopup.PyPopup( RevDefs.revolutionPopup, contextType = EventContextTypes.EVENTCONTEXT_ALL, bDynamic = False)
				if( self.centerPopups ) : popup.setPosition(3*caesiumpasx,3*caesiumpasy)
				# End additions by Caesium et al
				if( bPeaceful ) :
					popup.setHeaderString( localText.getText("TXT_KEY_REV_TITLE_PEACEFUL",()) )
				else :
					popup.setHeaderString( localText.getText("TXT_KEY_REV_TITLE_VIOLENT",()) )
				if( iOdds >= 70 ) :
					bodStr += "\n\n" + localText.getText("TXT_KEY_REV_ADVISOR_ACCEPT",())
				elif( iOdds <= 30 ) :
					bodStr += "\n\n" + localText.getText("TXT_KEY_REV_ADVISOR_REJECT",())
				else :
					bodStr += "\n\n" + localText.getText("TXT_KEY_REV_ADVISOR_NEUTRAL",())

				popup.setBodyString( bodStr )
				if( not vassalStyle == None ) :
					popup.addButton( localText.getText("TXT_KEY_REV_BUTTON_VASSAL",()) )
					buttons = ('vassal',)
					popup.addButton( localText.getText("TXT_KEY_REV_BUTTON_INDEPENDENCE",()) )
					buttons += ('accept',)
				else :
					if( not bPeaceful and not bOfferPeace and joinPlayer == None and not pRevPlayer.isAlive() ) :
						popup.addButton( localText.getText("TXT_KEY_REV_BUTTON_RECOGNIZE",()) )
						buttons = ('accept',)
					else :
						popup.addButton( localText.getText("TXT_KEY_REV_BUTTON_ACCEPT",()) )
						buttons = ('accept',)
				popup.addButton( localText.getText("TXT_KEY_REV_BUTTON_REJECT",()) )
				buttons += ('reject',)
				if( not joinPlayer == None and not bIsJoinWar and gc.getTeam(pPlayer.getTeam()).canDeclareWar(joinPlayer.getTeam()) ) :
					popup.addButton( localText.getText("TXT_KEY_REV_BUTTON_WAR",()) + ' ' + joinPlayer.getCivilizationDescription(0) )
					buttons += ('war',)
				if( iBuyOffCost > 0 and iBuyOffCost <= pPlayer.getGold() ) :
					popup.addButton( localText.getText("TXT_KEY_REV_BUTTON_BUYOFF",()) + ' %d'%(iBuyOffCost) )
					buttons += ('buyoff',)
				if( bPeaceful and joinPlayer == None and (pRevPlayer.getNumCities() == 0) ) :
					popup.addButton( localText.getText("TXT_KEY_REV_BUTTON_CONTROL",()) )
					buttons += ('control',)
				elif( not bPeaceful and joinPlayer == None and not pRevPlayer.isBarbarian() and (pRevPlayer.getNumCities() == 0) ) :
					popup.addButton( localText.getText("TXT_KEY_REV_BUTTON_CONTROL",()) )
					buttons += ('control',)
				if( not bPeaceful and joinPlayer == None and not bIsBarbRev and (pRevPlayer.getNumCities() == 0) and self.offerDefectToRevs ) :
					popup.addButton( localText.getText("TXT_KEY_REV_BUTTON_DEFECT",()) )
					buttons += ('defect',)

				popup.setUserData( (buttons, pPlayer.getID(), iRevoltIdx) )
				# Center camera on city
				CyCamera().JustLookAt( cityList[0].plot().getPoint() )
				popup.launch(bCreateOkButton = False)

			elif (not pPlayer.isHuman()) :
				# Make AI decision
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Making AI choice on independence")
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Odds are %d"%(iOdds))

				if( game.getSorenRandNum(100,'Revolt: give independence') < iOdds ) :
					self.processRevolution( pPlayer, iRevoltIdx, cityList, revType, bPeaceful, True )
				else:
					if( iBuyOffCost > 0 and iBuyOffCost <= pPlayer.getGold() ) :
						if( bPeaceful ) :
							base = .8
						else :
							base = .7
#-------------------------------------------------------------------------------------------------
# Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
						buyOdds = int( float(iOdds)/2.0 + 75.0*(1.0 - pow(base,float(pPlayer.getGold())/float(iBuyOffCost))) )
#-------------------------------------------------------------------------------------------------
# END Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - AI buyoff iOdds are %d, with base %.1f, from cost %d and gold %d"%(buyOdds,base,iBuyOffCost,pPlayer.getGold()))
						if( buyOdds > game.getSorenRandNum( 100, 'Revolt - AI buyoff decision' ) ) :
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - AI buyingoff rebels")
							revData.dict['bDidBuyOff'] = True

							revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
							revoltDict[iRevoltIdx] = revData
							RevData.revObjectSetVal( pPlayer, 'RevoltDict', revoltDict )

							self.processRevolution( pPlayer, iRevoltIdx, cityList, revType, bPeaceful, False )
							return

					self.processRevolution( pPlayer, iRevoltIdx, cityList, revType, bPeaceful, False )

		else :
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Unknown revolution type %s"%(revType))
			isRevType = False

		if (pPlayer.isHuman() and isRevType) :
			if( not pRevPlayer == None ) :
				# Claim slot so it's not taken while waiting for response to popup (local or network)
				RevData.revObjectInit( pRevPlayer )


##--- Revolution processing functions ----------------------------------------

	def revolutionNetworkPopupHandler( self, iPlayerID, iButton, iIdx) :

		if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Handling network revolution popups including local player")

		newHumanPlayer = None
		termsAccepted = False
		bSwitchToRevs = False

		iButtonCode = iButton
		iPlayer = iPlayerID
		iRevoltIdx = iIdx

		buttonLabel = ''
		if (iButtonCode == 0) : buttonLabel = 'accept'
		elif (iButtonCode == 1) : buttonLabel = 'reject'
		elif (iButtonCode == 2) : buttonLabel = 'buyoff'
		elif (iButtonCode == 3) : buttonLabel = 'vassal'
		elif (iButtonCode == 4) : buttonLabel = 'control'
		elif (iButtonCode == 5) : buttonLabel = 'buyelection'
		elif (iButtonCode == 6) : buttonLabel = 'war'
		elif (iButtonCode == 7) : buttonLabel = 'defect'
		else :
			buttonLabel = 'reject'

		pPlayer = gc.getPlayer(iPlayer)
		revData = RevData.revObjectGetVal(pPlayer, 'RevoltDict')[iRevoltIdx]

		if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Button :%s: pressed by playerID = %d"%(buttonLabel,iPlayer))

		# Clear claim on slot
		if( 'iRevPlayer' in revData.dict.keys() ) :
			pRevPlayer = gc.getPlayer(revData.dict['iRevPlayer'])
			RevData.revObjectWipe( pRevPlayer )

		cityList = list()
		for iCity in revData.cityList :
			# No game actions have been taken that could take these cities away, so all should still be owner by pPlayer
			cityList.append( pPlayer.getCity(iCity) )
		revType = revData.revType
		bPeaceful = revData.bPeaceful

		if( buttonLabel == 'accept' ) :
			termsAccepted = True
		elif( buttonLabel == 'reject' ) :
			termsAccepted = False
		elif( buttonLabel == 'buyoff' ) :
			# Pay the cities not to revolt
			termsAccepted = False
			revData.dict['bDidBuyOff'] = True
		elif( buttonLabel == 'vassal' ) :
			# pRevPlayer becomes vassal of pPlayer
			termsAccepted = True
			assert( 'vassalStyle' in revData.dict.keys() )
		elif( buttonLabel == 'control' ) :
			# Give control of new civ
			termsAccepted = True
			newHumanPlayer = revData.dict['iRevPlayer']
		elif( buttonLabel == 'buyelection' ) :
			# Attempt buyoff of election results
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Feature not fully implemented %s"%(buttonLabel))
			if self.isLocalHumanPlayer(iPlayerID):
				# Report election bought off
				# Additions by Caesium et al
				caesiumtR = CyUserProfile().getResolutionString(CyUserProfile().getResolution())
				caesiumtextResolution = caesiumtR.split('x')
				caesiumpasx = int(caesiumtextResolution[0])/10
				caesiumpasy = int(caesiumtextResolution[1])/10
				popup = PyPopup.PyPopup()
				if( self.centerPopups ) : popup.setPosition(3*caesiumpasx,3*caesiumpasy)
				# End additions by Caesium et al
				bodStr = bodStr = localText.getText("TXT_KEY_REV_HUMAN_ELEC_BUYOFF",())
				popup.setBodyString(bodStr)
				popup.launch()
			revData.dict['bDidBuyOff'] = True
			termsAccepted = False
		elif( buttonLabel == 'war' ) :
			# Declare war on cultural owner of rebelling cities
			termsAccepted = False
			revData.dict['iRevPlayer'] = revData.dict['iJoinPlayer']
			del revData.dict['iJoinPlayer']

			pRevPlayer = gc.getPlayer( revData.dict['iRevPlayer'] )
			gc.getTeam( pPlayer.getTeam()).declareWar( pRevPlayer.getTeam(), True, WarPlanTypes.NO_WARPLAN )
		elif( buttonLabel == 'defect' ) :
			termsAccepted = False
			revData.dict['bSwitchToRevs'] = True
#-------------------------------------------------------------------------------------------------
# Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
			# had to remove. is this important?
			#game.setForcedAIAutoPlay(iPlayerID, 1, true) # Releases this player turn to the AI, human player changed below so that human now will control rebels
#-------------------------------------------------------------------------------------------------
# END Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
		else :
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Error! Unrecognized button label %s"%(buttonLabel))
			termsAccepted = False

		if( not newHumanPlayer == None ) :
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Human being given control of new player %d"%(newHumanPlayer))
			RevUtils.changeHuman( newHumanPlayer, iPlayerID )

		revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
		revoltDict[iRevoltIdx] = revData
		RevData.revObjectSetVal( pPlayer, 'RevoltDict', revoltDict )

		self.processRevolution( pPlayer, iRevoltIdx, cityList, revType, bPeaceful, termsAccepted, switchToRevs = bSwitchToRevs )


	def processRevolution( self, pPlayer, iRevoltIdx, cityList, revType, bPeaceful, termsAccepted, switchToRevs = False ) :
		if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Processing revolution revolution type: %s"%(revType))
		if( self.DEBUG_MESS ) : CyInterface().addImmediateMessage('Processing revolution!!!',"")

		if( not pPlayer.isAlive() or not pPlayer.getNumCities() > 0 ) :
			return

		revData = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )[iRevoltIdx]

		pTeam = gc.getTeam( pPlayer.getTeam() )

		iAggressive = CvUtil.findInfoTypeNum(gc.getTraitInfo,gc.getNumTraitInfos(),RevDefs.sXMLAggressive)
		iSpiritual = CvUtil.findInfoTypeNum(gc.getTraitInfo,gc.getNumTraitInfos(),RevDefs.sXMLSpiritual)
		numRevCities = len(cityList)
		capital = pPlayer.getCapitalCity()
		if not capital.isNone():
			capitalArea = capital.area().getID()
		else:
			capitalArea = -1

		newCityList = list()
		for pCity in cityList :
			if( pCity.getOwner() == pPlayer.getID() ) :
				pCity.changeNumRevolts( pPlayer.getID(), 1 )
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s has now revolted %d times"%(pCity.getName(),pCity.getNumRevolts(pPlayer.getID())))
				newCityList.append(pCity)
			else :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - WARNING: %s no longer owned by revolt player!"%(pCity.getName()))

		cityList = newCityList

		#if( not len(cityList) > 0 ) :
		#	return

		if( revData.dict.get( 'bDidBuyOff', False ) ) :
			if( revType == 'leader' and revData.dict.get( 'bIsElection', False ) ) :
				# TODO something special for this
				pass
			pPlayer.changeGold( -revData.dict['iBuyOffCost'] )
			for pCity in cityList :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Buying off revolutionaries in %s"%(pCity.getName()))
				revIdx = pCity.getRevolutionIndex()
				pCity.setRevolutionIndex( min([int(self.revReadyFrac*self.revInstigatorThreshold),revIdx-200]) )
				pCity.setRevolutionCounter( self.buyoffTurns )
				pCity.setReinforcementCounter(0)
				RevData.setCityVal( pCity, 'BribeTurn', game.getGameTurn() )
				pCity.changeNumRevolts( pPlayer.getID(), -1 )

		elif( revType == 'civics' ) :

			newCivic = revData.dict['iNewCivic']

			if( termsAccepted ) :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Player opts to switch, lowering rev indices")
				# Do switch
				newCivicOption = gc.getCivicInfo( newCivic ).getCivicOptionType()
				pPlayer.setCivics( newCivicOption, newCivic )
				iSpiritual = CvUtil.findInfoTypeNum(gc.getTraitInfo,gc.getNumTraitInfos(),RevDefs.sXMLSpiritual)
				pPlayer.changeRevolutionTimer(5)
				if( not pPlayer.hasTrait(iSpiritual) ) :
					if( pPlayer.getCurrentRealEra() > gc.getNumRealEras()/2 ) :
						pPlayer.changeAnarchyTurns(2)
					else :
						pPlayer.changeAnarchyTurns(1)

				# Make those cities happier
				for pCity in cityList :
					revIdx = pCity.getRevolutionIndex()
					pCity.setRevolutionIndex( min([revIdx/2,int(.6*self.revInstigatorThreshold)]) )
					pCity.setRevolutionCounter( self.acceptedTurns )
					pCity.setReinforcementCounter(0)
					if( pCity.getNumRevolts(pPlayer.getID()) > 1 ) :
						pCity.changeNumRevolts( pPlayer.getID(), -2 )
					else :
						pCity.changeNumRevolts( pPlayer.getID(), -1 )

			else :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Player declines to switch")
				if( bPeaceful ) :

					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Peaceful, increasing rev indices")
					# Make those cities more unhappy
					for pCity in cityList :
						RevUtils.doRevRequestDeniedPenalty( pCity, capitalArea, bExtraColony = True )

				else :
					pRevPlayer = gc.getPlayer( revData.dict['iRevPlayer'] )
					self.prepareRevolution( pPlayer, iRevoltIdx, cityList, pRevPlayer, bIsJoinWar = revData.dict.get('bIsJoinWar', False), switchToRevs = switchToRevs )

		elif( revType == 'religion' ) :

			iNewReligion = revData.dict['iNewReligion']

			assert( pPlayer.isStateReligion() )

			if( termsAccepted ) :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Player opts to switch, lowering rev indices")
				# Do switch
				pPlayer.convert(iNewReligion)
				# Make those cities happier
				for pCity in cityList :
					revIdx = pCity.getRevolutionIndex()
					pCity.setRevolutionIndex( min([revIdx/2,int(.6*self.revInstigatorThreshold)]) )
					pCity.setRevolutionCounter( self.acceptedTurns )
					pCity.setReinforcementCounter(0)
					if( pCity.getNumRevolts(pPlayer.getID()) > 1 ) :
						pCity.changeNumRevolts( pPlayer.getID(), -2 )
					else :
						pCity.changeNumRevolts( pPlayer.getID(), -1 )

			else :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Player declines to switch")
				if( not bPeaceful ) :
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Error ... shouldn't have violent request for religion switch")

				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Peaceful, increasing rev indices")
				# Make those cities more unhappy
				for pCity in cityList :
					RevUtils.doRevRequestDeniedPenalty( pCity, capitalArea, revIdxInc = 150, bExtraColony = True )

		elif( revType == 'leader' ) :

			newLeaderType = revData.dict['iNewLeaderType']

			newLeaderName = revData.dict.get( 'newLeaderName', None )

			if( termsAccepted ) :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Player opts to cede power, lowering rev indices")

				# Lower indices
				for pCity in cityList :
					revIdx = pCity.getRevolutionIndex()
					pCity.setRevolutionIndex( min([revIdx/2,int(.6*self.revInstigatorThreshold)]) )
					pCity.setRevolutionCounter( self.acceptedTurns )
					pCity.setReinforcementCounter(0)
					if( pCity.getNumRevolts(pPlayer.getID()) > 1 ) :
						pCity.changeNumRevolts( pPlayer.getID(), -2 )
					else :
						pCity.changeNumRevolts( pPlayer.getID(), -1 )

				# Do switch leader
				if( revData.dict.get( 'bIsElection', False ) ) :

					iHappiness = revData.dict['iHappiness']

					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Running an election for a new leader!")
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Adjusted approval rating is %d"%(iHappiness))

					if( iHappiness < 40 ) :
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Election lost due to low approval rating")
						# Continue to change leader code below
					elif( game.getSorenRandNum(25,'Revolution: election results') + 30 > iHappiness ) :
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Election lost by probability")
					else :
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Election won!  Leader stays in power!")
						if( self.isLocalHumanPlayer(pPlayer.getID()) ) :
							# Report election victory
							# Additions by Caesium et al
							caesiumtR = CyUserProfile().getResolutionString(CyUserProfile().getResolution())
							caesiumtextResolution = caesiumtR.split('x')
							caesiumpasx = int(caesiumtextResolution[0])/10
							caesiumpasy = int(caesiumtextResolution[1])/10
							popup = PyPopup.PyPopup()
							if( self.centerPopups ) : popup.setPosition(3*caesiumpasx,3*caesiumpasy)
							# End additions by Caesium et al
							bodStr = localText.getText("TXT_KEY_REV_HUMAN_ELEC_VICTORY",())
							popup.setBodyString(bodStr)
							popup.launch()
						return

				if( self.isLocalHumanPlayer(pPlayer.getID()) ) :
					# Additions by Caesium et al
					caesiumtR = CyUserProfile().getResolutionString(CyUserProfile().getResolution())
					caesiumtextResolution = caesiumtR.split('x')
					caesiumpasx = int(caesiumtextResolution[0])/10
					caesiumpasy = int(caesiumtextResolution[1])/10
					popup = PyPopup.PyPopup(RevDefs.controlLostPopup, contextType = EventContextTypes.EVENTCONTEXT_ALL)
					if( self.centerPopups ) : popup.setPosition(3*caesiumpasx,3*caesiumpasy)
					# End additions by Caesium et al

					gameSpeedMod = RevUtils.getGameSpeedMod()

					if( revData.dict.get('bIsElection', False) ) :
						iNumTurns = int(math.floor( 15/gameSpeedMod + .5 ))
						bodStr = localText.getText("TXT_KEY_REV_HUMAN_ELEC_LOSS",())
					else :
						iNumTurns = int(math.floor( 24/gameSpeedMod + .5 ))
						bodStr = localText.getText("TXT_KEY_REV_HUMAN_CEDE",())

					bodStr += '\n\n' + localText.getText("TXT_KEY_REV_HUMAN_CONTROL_RETURNED",()) + ' %d '%(iNumTurns) + localText.getText("TXT_KEY_REV_TURNS",()) + '.'
					popup.setBodyString( bodStr )
#-------------------------------------------------------------------------------------------------
# Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
					# Hacky fix to make the controlLost net message get out. Doesn't seem to work otherwise.
					#iNewLeaderType = revData.dict['iNewLeaderType']
					popup.setUserData( (iNumTurns, newLeaderType) )
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Control player is %d"%(game.getActivePlayer()))

					#self.controlLostNetworkHandler(game.getActivePlayer(), iNumTurns, newLeaderType)
					CyMessageControl().sendModNetMessage(self.netControlLostPopupProtocol, game.getActivePlayer(), iNumTurns, newLeaderType, 0)
#-------------------------------------------------------------------------------------------------
# END Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
					popup.launch()

			#terms not accepted
			else:
				if( revData.dict.get( 'bIsElection', False ) ) :
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Player refuses election")
				else :
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Player clings to power")

				if( bPeaceful ) :
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Peaceful, increasing rev indices")
					for pCity in cityList :
						RevUtils.doRevRequestDeniedPenalty( pCity, capitalArea, revIdxInc = 150, bExtraColony = True )

				else :
					joinPlayer = None
					if( 'iJoinPlayer' in revData.dict.keys() ) :
						joinPlayer = gc.getPlayer( revData.dict['iJoinPlayer'] )
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Error!  Join player specified for leader type revolt ...")

					# if( not joinPlayer == None ) :
						# joinPlayer.AI_changeAttitudeExtra( pPlayer.getID(), -2 )
						# if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s's Extra Attitude towards %s now %d"%(joinPlayer.getCivilizationDescription(0),pPlayer.getCivilizationDescription(0),joinPlayer.AI_getAttitudeExtra(pPlayer.getID())))
						# pPlayer.AI_changeAttitudeExtra( joinPlayer.getID(), -2 )

						# self.prepareRevolution( pPlayer, iRevoltIdx, cityList, joinPlayer, bIsJoinWar = True, switchToRevs = switchToRevs )

					# else :
					pRevPlayer = gc.getPlayer( revData.dict['iRevPlayer'] )
					if( not pRevPlayer.isBarbarian() ) :
						pRevPlayer.AI_changeAttitudeExtra( pPlayer.getID(), -5 )
						if( 'iJoinPlayer' in revData.dict.keys() ) : pRevPlayer.AI_changeAttitudeExtra( revData.dict['iJoinPlayer'], 5 )
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s's Extra Attitude towards %s now %d"%(pRevPlayer.getCivilizationDescription(0),pPlayer.getCivilizationDescription(0),pRevPlayer.AI_getAttitudeExtra(pPlayer.getID())))
						pPlayer.AI_changeAttitudeExtra( pRevPlayer.getID(), -3 )
					self.prepareRevolution( pPlayer, iRevoltIdx, cityList, pRevPlayer, bIsJoinWar = revData.dict.get('bIsJoinWar', False), switchToRevs = switchToRevs )

		elif( revType == 'war' ) :

			if( termsAccepted ) :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Player opts for war!!!")

				pRevPlayer = gc.getPlayer( revData.dict['iRevPlayer'] )

				for pCity in cityList :
					revIdx = pCity.getRevolutionIndex()
					pCity.setRevolutionIndex( min([revIdx/2,int(.5*self.revInstigatorThreshold)]) )
					pCity.setRevolutionCounter( self.acceptedTurns )
					pCity.setReinforcementCounter(0)
					if( pCity.getNumRevolts(pPlayer.getID()) > 1 ) :
						pCity.changeNumRevolts( pPlayer.getID(), -2 )
					else :
						pCity.changeNumRevolts( pPlayer.getID(), -1 )

				pTeam.declareWar( pRevPlayer.getTeam(), True, WarPlanTypes.NO_WARPLAN )

				#TODO: spawn fanatic units or something for holy war?

			else :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Player declines cries for war.")

				if( bPeaceful ) :
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Peaceful, increasing rev indices")
					# Make those cities more unhappy
					for pCity in cityList :
						RevUtils.doRevRequestDeniedPenalty( pCity, capitalArea, bExtraHomeland = True )

				else :
					# Violent uprising!!!
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Error!  Unexpected violent request for war, not well supported")

					if( 'iJoinPlayer' in revData.dict.keys() ) :

						joinPlayer = gc.getPlayer( revData.dict['iJoinPlayer'] )
						joinPlayer.AI_changeAttitudeExtra( pPlayer.getID(), -3 )
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s's Extra Attitude towards %s now %d"%(joinPlayer.getCivilizationDescription(0),pPlayer.getCivilizationDescription(0),joinPlayer.AI_getAttitudeExtra(pPlayer.getID())))

						# Check if joinPlayer would like to declare war on player
						[warOdds,attackerTeam,victimTeam] = RevUtils.computeWarOdds( joinPlayer, pPlayer, cityList[0].area(), False, allowBreakVassal = self.bAllowBreakVassal )
						# TODO: Find way to support human selecting war in this case
						if( attackerTeam.isHuman() and not attackerTeam.isAtWar(victimTeam.getID()) ) :
							warOdds = 0

						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - War odds are %d"%(warOdds))

						if( warOdds > 25 and warOdds > game.getSorenRandNum(100,'Revolution: war') ) :
							# have joinPlayer's team (or vassal master) declare war on player's team
							attackerTeam.declareWar(pPlayer.getTeam(),True, WarPlanTypes.NO_WARPLAN)

							revData.dict['iRevPlayer'] = joinPlayer.getID()
							del revData.dict['iJoinPlayer']
							revData.dict['bIsJoinWar'] = True

							revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
							revoltDict[iRevoltIdx] = revData
							RevData.revObjectUpdateVal( pPlayer, 'RevoltDict', revoltDict )

							self.prepareRevolution( pPlayer, iRevoltIdx, cityList, joinPlayer, bIsJoinWar = True, switchToRevs = switchToRevs )

						else :
							pRevPlayer = gc.getPlayer( revData.dict['iRevPlayer'] )
							if( not pRevPlayer.isBarbarian() ) :
								pRevPlayer.AI_changeAttitudeExtra( pPlayer.getID(), -5 )
								pRevPlayer.AI_changeAttitudeExtra( joinPlayer.getID(), 5 )
								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s's Extra Attitude towards %s now %d"%(pRevPlayer.getCivilizationDescription(0),pPlayer.getCivilizationDescription(0),pRevPlayer.AI_getAttitudeExtra(pPlayer.getID())))
								pPlayer.AI_changeAttitudeExtra( pRevPlayer.getID(), -3 )

							self.prepareRevolution( pPlayer, iRevoltIdx, cityList, pRevPlayer, bIsJoinWar = revData.dict.get('bIsJoinWar', False), switchToRevs = switchToRevs )

					else :
						pRevPlayer = gc.getPlayer( revData.dict['iRevPlayer'] )
						if( not pRevPlayer.isBarbarian() ) :
							pRevPlayer.AI_changeAttitudeExtra( pPlayer.getID(), -5 )
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s's Extra Attitude towards %s now %d"%(pRevPlayer.getCivilizationDescription(0),pPlayer.getCivilizationDescription(0),pRevPlayer.AI_getAttitudeExtra(pPlayer.getID())))
							pPlayer.AI_changeAttitudeExtra( pRevPlayer.getID(), -3 )

						self.prepareRevolution( pPlayer, iRevoltIdx, cityList, pRevPlayer, bIsJoinWar = revData.dict.get('bIsJoinWar', False), switchToRevs = switchToRevs )

		elif( revType == 'independence' ) :

			pRevPlayer = gc.getPlayer( revData.dict['iRevPlayer'] )

			bOfferPeace = revData.dict.get('bOfferPeace', False)
			handoverCities = list()
			for iCity in revData.dict.get('HandoverCities', list()) :
				handoverCities.append(pPlayer.getCity(iCity))

			if( termsAccepted ) :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Player opts to give independence, lowering rev indices")

				# Lower indices (makes life a little easier for new civ ...)
				if( bOfferPeace ) :
					# Special case where pPlayer turns over control of handover cities instead of having cityList revolt

					for pCity in handoverCities :
						revIdx = pCity.getRevolutionIndex()
						pCity.setRevolutionIndex( min([revIdx/2,int(.8*self.revReadyFrac*self.revInstigatorThreshold)]) )
						# Other changes handled by acquired city logic
						if( pCity.getNumRevolts(pPlayer.getID()) > 1 ) :
							pCity.changeNumRevolts( pPlayer.getID(), -2 )
						else :
							pCity.changeNumRevolts( pPlayer.getID(), -1 )

					for pCity in cityList :
						if( not pCity.getID() in revData.dict.get('HandoverCities', list()) ) :
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Turning down rebelliousness in non-handed over city %s"%(pCity.getName()))
							revIdx = pCity.getRevolutionIndex()
							pCity.setRevolutionIndex( min([(3*revIdx)/4,int(self.revInstigatorThreshold)]) )
							if( pCity.getNumRevolts(pPlayer.getID()) > 2 ) :
								pCity.changeNumRevolts( pPlayer.getID(), -2 )
							else :
								pCity.changeNumRevolts( pPlayer.getID(), -1 )

					pCity = pPlayer.getCapitalCity()
					if( not pCity.getID() in revData.dict.get('HandoverCities', list()) ) :
						revIdx = pCity.getRevolutionIndex()
						if( pCity.getID() not in revData.dict.get('cityList', list()) and revIdx > self.revInstigatorThreshold
								and RevData.getRevolutionPlayer( pCity ) == pRevPlayer.getID() ) :
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Also turning down rebelliousness in capital %s"%(pCity.getName()))
							pCity.setRevolutionIndex( min([(7*revIdx)/8,int(self.revInstigatorThreshold)]) )
							# Other changes handled by acquired city logic
							if( pCity.getNumRevolts(pPlayer.getID()) > 2 ) :
								pCity.changeNumRevolts( pPlayer.getID(), -2 )
							elif( pCity.getNumRevolts(pPlayer.getID()) > 0 ) :
								pCity.changeNumRevolts( pPlayer.getID(), -1 )

					# Switch list to be given independence
					cityList = handoverCities

				else :
					for pCity in cityList :
						revIdx = pCity.getRevolutionIndex()
						pCity.setRevolutionIndex( min([revIdx/2,int(.8*self.revReadyFrac*self.revInstigatorThreshold)]) )
						# Other changes handled by acquired city logic
						if( pCity.getNumRevolts(pPlayer.getID()) > 1 ) :
							pCity.changeNumRevolts( pPlayer.getID(), -2 )
						else :
							pCity.changeNumRevolts( pPlayer.getID(), -1 )


				iGoodyMap = CvUtil.findInfoTypeNum(gc.getGoodyInfo,gc.getNumGoodyInfos(),RevDefs.sXMLGoodyMap)

				if( not 'iJoinPlayer' in revData.dict.keys() ) :
					# Grant independence
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - The %s are taking over the revolutionary cities"%(pRevPlayer.getCivilizationDescription(0)))

					bIsBarbRev = pRevPlayer.isBarbarian()

					pRevTeam = gc.getTeam( pRevPlayer.getTeam() )
					pTeam = gc.getTeam( pPlayer.getTeam() )

					bGaveMap = False

					if( not bIsBarbRev ) :
						# Diplomacy
						pRevTeam.meet(pPlayer.getTeam(),False)

						if( not pRevTeam.isAlive() ) :
							if( pRevTeam.isAtWar(pPlayer.getTeam()) ) :
								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Reincarnated %s ending war with %s"%(pRevPlayer.getCivilizationDescription(0),pPlayer.getCivilizationDescription(0)))
								pRevTeam.makePeace( pPlayer.getTeam() )

							pRevTeam.signOpenBorders(pPlayer.getTeam())

						if( pRevTeam.isAtWar(pPlayer.getTeam()) and revData.dict.get( 'bOfferPeace', False ) ) :
							pRevTeam.makePeace( pPlayer.getTeam() )

						if( pRevTeam.isAtWar(pPlayer.getTeam()) ) :
							pRevPlayer.AI_changeMemoryCount(pPlayer.getID(), MemoryTypes.MEMORY_LIBERATED_CITIES, 1)
						else :
							pRevPlayer.AI_changeAttitudeExtra( pPlayer.getID(), 6 + len(cityList)/2 )
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s's Extra Attitude towards %s now %d"%(pRevPlayer.getCivilizationDescription(0),pPlayer.getCivilizationDescription(0),pRevPlayer.AI_getAttitudeExtra(pPlayer.getID())))

						if( pRevPlayer.getGold() < 50 ) :
							pRevPlayer.changeGold( 30 + game.getSorenRandNum(25*len(cityList),'Revolt: give gold') )
						else :
							pRevPlayer.changeGold( 10 + game.getSorenRandNum(15*len(cityList),'Revolt: give gold') )

						if( pRevTeam.isMapTrading() ) :
							# Give motherlands map
							bGaveMap = True
							gameMap = gc.getMap()
							for ix in range(0,CyMap().getGridWidth()) :
								for iy in range(0,CyMap().getGridHeight()) :
									pPlot = gameMap.plot(ix,iy)
									if( pPlot.isRevealed(pTeam.getID(),False) ) :
										pPlot.setRevealed(pRevTeam.getID(),True,False,pTeam.getID())

							# Meet players known by motherland
							for k in range(0,gc.getMAX_CIV_TEAMS()) :
								if( pTeam.isHasMet(k) ) :
									# Granted independence, so just meet some fraction of players
									if( game.getSorenRandNum(100,'odds') > 50 ) :
										pRevTeam.meet(k,False)

						if( not revData.dict.get('bIsJoinWar', False) ) :
							if( not RevData.revObjectGetVal(pRevPlayer, 'MotherlandID') == None ) :
								revTurn = RevData.revObjectGetVal(pRevPlayer, 'RevolutionTurn')
								if( revTurn == None or game.getGameTurn() - revTurn > 30 ) :
									RevData.revObjectSetVal( pRevPlayer, 'MotherlandID', pPlayer.getID() )
							else :
								RevData.revObjectSetVal( pRevPlayer, 'MotherlandID', pPlayer.getID() )
							RevData.revObjectSetVal( pRevPlayer, 'RevolutionTurn', game.getGameTurn() )

						if( not pRevPlayer.isAlive() ) :
							if( len(cityList) < 3 ) :
								#try :
									cityString = CvUtil.convertToStr(cityList[0].getName())
								#except UnicodeDecodeError :
									#cityString = None
							else :
								cityString = None
							RevData.revObjectSetVal( pRevPlayer, 'CapitalName', cityString )

							# Set new player alive before giving cities so that they draw properly
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Setting new player alive")
							if( SdToolKitCustom.sdObjectExists( 'BarbarianCiv', pPlayer ) and not RevInstances.BarbarianCivInst == None ) :
								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Setting new rebel player as barb civ since motherland is")
								RevInstances.BarbarianCivInst.setupSavedData( pRevPlayer.getID(), bSetupComplete = 1 )
							if( pPlayer.isMinorCiv() ) :
								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Setting new rebel player as minor civ since motherland is")
								pRevTeam.setIsMinorCiv( True, False )
								if( SdToolKitCustom.sdObjectExists( 'BarbarianCiv', game ) ) :
									# If motherland is on always minor list, put rebel on as well
									alwaysMinorList = SdToolKitCustom.sdObjectGetVal( "BarbarianCiv", game, "AlwaysMinorList" )
									if( not alwaysMinorList == None and pPlayer.getID() in alwaysMinorList ) :
										alwaysMinorList.append(pRevPlayer.getID())
										SdToolKitCustom.sdObjectSetVal( "BarbarianCiv", game, "AlwaysMinorList", alwaysMinorList )
							else :
								if( pRevPlayer.isMinorCiv() ) :
									if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - pRevPlayer was minor civ, changing")
									pRevTeam.setIsMinorCiv( False, False )
							pRevPlayer.setNewPlayerAlive(True)

					iNumPlayerCities = pPlayer.getNumCities()

					for iPlayer in range(0,gc.getMAX_CIV_PLAYERS()) :
						# Craft revolution anouncement message for all players
						if( gc.getPlayer(iPlayer).canContact(pPlayer.getID()) or iPlayer == pPlayer.getID() ) :

							colorNum = gc.getInfoTypeForString("COLOR_HIGHLIGHT_TEXT")
							pPlayerName = str(localText.getText("TXT_KEY_REV_THE",())) + ' ' + pPlayer.getCivilizationDescription(0)
							revPlayerName = str(localText.getText("TXT_KEY_REV_THE",())) + ' ' + pRevPlayer.getCivilizationDescription(0)

							if( iPlayer == pRevPlayer.getID() ) :
								colorNum = gc.getInfoTypeForString("COLOR_HIGHLIGHT_TEXT")
								revPlayerName = localText.getText("TXT_KEY_REV_YOUR_CIV",())
							elif( iPlayer == pPlayer.getID() ) :
								pPlayerName = str(localText.getText("TXT_KEY_REV_YOU",()))

							cityString = bodStr = getCityTextList(cityList)

							mess = localText.getText("TXT_KEY_REV_MESS_CEDE",())%(pPlayerName,cityString,revPlayerName)

							if( iPlayer == pPlayer.getID() ) :
								CyInterface().addMessage(iPlayer, false, gc.getDefineINT("EVENT_MESSAGE_TIME"), mess, "AS2D_CITY_REVOLT", InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT, CyArtFileMgr().getInterfaceArtInfo("INTERFACE_RESISTANCE").getPath(), ColorTypes(colorNum), cityList[0].getX(), cityList[0].getY(), True, True)
							else :
								CyInterface().addMessage(iPlayer, false, gc.getDefineINT("EVENT_MESSAGE_TIME"), mess, None, InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT, None, ColorTypes(colorNum), -1, -1, False, False)

					if( not bIsBarbRev and (pRevPlayer.getNumCities() + pRevPlayer.getCitiesLost() < 4) and len(cityList) > 1 ) :
						# Launch golden age for rebel player (helps with stability and being competitive)
						pRevPlayer.changeGoldenAgeTurns( int(1.5*game.goldenAgeLength()) )

					# Since instigator is first in list, it will become capital if pRevPlayer has no others
					for pCity in cityList :
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Acquiring %s, pop %d"%(pCity.getName(),pCity.getPopulation()))
						# Move units out of city?  Handled by trade style

						if( pRevTeam.isAtWar(pPlayer.getTeam()) and iNumPlayerCities > len(cityList) ) :
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Moving owner's units")
							RevUtils.clearOutCity( pCity, pPlayer, pRevPlayer )

						[iWorker,iBestDefender,iCounter,iAttack] = RevUtils.getHandoverUnitTypes( pCity, pRevPlayer, pPlayer )
						
						RevData.setRevolutionPlayer( pCity, -1 )

						# Store building types in city
						buildingClassList = list()
						for buildingType in range(gc.getNumBuildingInfos()) :
							if( pCity.getNumRealBuilding(buildingType) > 0 ) :
								buildingInfo = gc.getBuildingInfo(buildingType)
								buildingClassList.append([buildingInfo.getBuildingClassType(),pCity.getNumRealBuilding(buildingType)])

#***********************************
						# Acquire city
						#joinPlayer.acquireCity( pCity, False, True )

						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Population of %s before is %d"%(pCity.getName(),pCity.getPopulation()))
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Check city culture is %d, at %d, %d"%(pCity.getCulture(pPlayer.getID()), pCity.getX(),pCity.getY()))
						cityPlot = pCity.plot()
						if( pCity.getCulture( pPlayer.getID() ) == 0 ) :
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Forcing culture > 0")
							pCity.setCulture( pPlayer.getID(), 1, True )

						try :
							pCity.plot().setOwner( pRevPlayer.getID() )
						except :
							print "ERROR in grant independence"
							print "ERROR:  Failed to set owner of city, %s at plot %d, %d"%(pCity.getName(),cityPlot.getX(),cityPlot.getY())
							#print "City culture is %d"%(pCity.getCulture(pPlayer.getID()))

							#pCity = cityPlot.getPlotCity()
							#print "Post culture in %s is %d"%(pCity.getName(),pCity.getCulture(pPlayer.getID()))
							#pRevPlayer.acquireCity( pCity, False, False )
							#RevData.initCity(pCity)
							# City has become invalid, will cause game to crash if left
							print "Destroying city so game can continue"
							pCity.kill()
							continue


						pCity = cityPlot.getPlotCity()
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Population of %s after is %d"%(pCity.getName(),pCity.getPopulation()))

						if( pCity.getPopulation() < 1 ) :
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Error!  City %s is empty"%(pCity.getName()))
#*************************************

						# Save most buildings - should some be destroyed?
						for [buildingClass,iNum] in buildingClassList :
							buildingType = gc.getCivilizationInfo(pRevPlayer.getCivilizationType()).getCivilizationBuildings(buildingClass)
							if (buildingType != BuildingTypes.NO_BUILDING):
								if( pCity.getNumRealBuilding(buildingType) < iNum ) :
									buildingInfo = gc.getBuildingInfo(buildingType)
									if( not buildingInfo.isGovernmentCenter() ) :
										if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Building %s saved"%(buildingInfo.getDescription()))
										pCity.setNumRealBuilding( buildingType, iNum )

						#if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s at %d, %d"%(pCity.getName(),pCity.getX(),pCity.getY()))

						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Culture in %s: %d, plot %d"%(pCity.getName(),pCity.getCulture(pPlayer.getID()),pCity.plot().getCulture(pPlayer.getID())))

						newCulVal = int( self.revCultureModifier*max([1.0*pCity.getCulture(pPlayer.getID()),pCity.countTotalCultureTimes100()/200]) )
						newPlotVal = int( self.revCultureModifier*max([1.2*pCity.plot().getCulture(pPlayer.getID()),pCity.plot().countTotalCulture()/2]) )
						RevUtils.giveCityCulture( pCity, pRevPlayer.getID(), newCulVal, newPlotVal, overwriteHigher = False )

						ix = pCity.getX()
						iy = pCity.getY()

						# Record pre-given units for deletion after giving other units
						defaultUnits = RevUtils.getPlayerUnits( ix, iy, pRevPlayer.getID() )

						# Give a few defenders
						newUnit = pRevPlayer.initUnit( iBestDefender, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )
						pRevPlayer.initUnit( iBestDefender, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )
						pRevPlayer.initUnit( iCounter, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )
						if(iWorker != -1):
							pRevPlayer.initUnit( iWorker, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )

						if( pRevPlayer.getNumCities() <= 2 ) :
							# Extra units for first two cities
							#pRevPlayer.initUnit( iAttack, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )
							pRevPlayer.initUnit( iAttack, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )
						elif( gc.getTeam(pPlayer.getTeam()).isAtWar(pRevPlayer.getTeam()) ) :
							pRevPlayer.initUnit( iBestDefender, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )
							#pRevPlayer.initUnit( iBestDefender, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )

						if( not bIsBarbRev and not bGaveMap ) :
							pRevPlayer.receiveGoody( gc.getMap().plot(ix,iy), iGoodyMap, newUnit )
							pRevPlayer.receiveGoody( gc.getMap().plot(ix,iy), iGoodyMap, newUnit )

						# Remove default given units
						for unit in defaultUnits :
							unit.kill( False, -1 )

						if( not bIsBarbRev ) : RevData.setRevolutionPlayer( pCity, pRevPlayer.getID() )

						# City starts in disorder
						pCity.setOccupationTimer( 2 )

					vassalStyle = revData.dict.get('vassalStyle',None)
					if( not bIsBarbRev and not vassalStyle == None ) :
						if( vassalStyle == 'capitulated' ) :
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s is forming as capitulated vassal to %s"%(pRevPlayer.getCivilizationDescription(0),pPlayer.getCivilizationDescription(0)))
							pTeam.assignVassal( pRevPlayer.getTeam(), True )
							game.updateScore(True)
						else :
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s is forming as vassal to %s"%(pRevPlayer.getCivilizationDescription(0),pPlayer.getCivilizationDescription(0)))
							pTeam.assignVassal( pRevPlayer.getTeam(), False )
							game.updateScore(True)

					if( bPeaceful ) :
						pTeam.signOpenBorders( pRevPlayer.getTeam() )

				else :
					# Join cultural owner
					joinPlayer = gc.getPlayer( revData.dict['iJoinPlayer'] )

					# Enable only for debugging join human popup
					if( False ) :
						if(pPlayer.isAlive()):
							if(pPlayer.isHuman() or pPlayer.isHumanDisabled()):
								game.setForcedAIAutoPlay(pPlayer.getID(), 0, false )
						iPrevHuman = game.getActivePlayer()
						RevUtils.changeHuman( joinPlayer.getID(), iPrevHuman )

					if( self.isLocalHumanPlayer(joinPlayer.getID()) ) :
						# Offer human the option of accepting the cities
						popup = PyPopup.PyPopup( RevDefs.joinHumanPopup, contextType = EventContextTypes.EVENTCONTEXT_ALL, bDynamic = False)

						popup.setHeaderString( localText.getText("TXT_KEY_REV_TITLE_GOOD_NEWS",()) )

						bodStr = getCityTextList(cityList, bPreCitizens = True)

						bodStr += ' ' + localText.getText("TXT_KEY_REV_HUMAN_GRANTED",()) + ' %s!'%(pPlayer.getName())
						bodStr += '  ' + localText.getText("TXT_KEY_REV_HUMAN_REGAIN",()) + ' %s.'%(pRevPlayer.getCivilizationShortDescription(0))
						bodStr += '  ' + localText.getText("TXT_KEY_REV_HUMAN_JOIN_CHOICE",())

						popup.setBodyString( bodStr )
						popup.addButton( localText.getText("TXT_KEY_REV_BUTTON_WELCOME",()) )
						buttons = ('welcome',)
						popup.addButton( localText.getText("TXT_KEY_REV_BUTTON_NOT_WANTED",()) )
						buttons += ('goaway',)
						popup.setUserData( (buttons, joinPlayer.getID(), iRevoltIdx) )
						# Center camera on city
						CyCamera().JustLookAt( cityList[0].plot().getPoint() )
						popup.launch(bCreateOkButton = False)

					else :
						joinPlayer = gc.getPlayer( revData.dict['iJoinPlayer'] )
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - The %s are claiming their cultural cities"%(joinPlayer.getCivilizationDescription(0)))

						bIsBarbRev = joinPlayer.isBarbarian()

						for iPlayer in range(0,gc.getMAX_CIV_PLAYERS()) :
							# Craft revolution anouncement message for all players
							if( gc.getPlayer(iPlayer).canContact(pPlayer.getID()) or iPlayer == pPlayer.getID() ) :

								colorNum = 7 # Red
								pPlayerName = str(localText.getText("TXT_KEY_REV_THE",())) + ' ' + pPlayer.getCivilizationDescription(0)
								joinPlayerName = str(localText.getText("TXT_KEY_REV_THE",())) + ' ' + joinPlayer.getCivilizationDescription(0)

								if( iPlayer == joinPlayer.getID() ) :
									colorNum = 8 # Green
									joinPlayerName = localText.getText("TXT_KEY_REV_YOU",())
								elif( iPlayer == pPlayer.getID() ) :
									pPlayerName = str(localText.getText("TXT_KEY_REV_YOU",()))

								cityString = getCityTextList(cityList)

								mess = localText.getText("TXT_KEY_REV_MESS_CEDE",())%(pPlayerName,cityString,joinPlayerName)

								if( iPlayer == pPlayer.getID() ) :
									CyInterface().addMessage(iPlayer, false, gc.getDefineINT("EVENT_MESSAGE_TIME"), mess, "AS2D_CITY_REVOLT", InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT, CyArtFileMgr().getInterfaceArtInfo("INTERFACE_RESISTANCE").getPath(), ColorTypes(colorNum), cityList[0].getX(), cityList[0].getY(), True, True)
								else :
									CyInterface().addMessage(iPlayer, false, gc.getDefineINT("EVENT_MESSAGE_TIME"), mess, None, InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT, None, ColorTypes(colorNum), -1, -1, False, False)

						if( not bIsBarbRev ) :
							# Improve relations
							joinPlayer.AI_changeAttitudeExtra( pPlayer.getID(), 4 )
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s's Extra Attitude towards %s now %d"%(joinPlayer.getCivilizationDescription(0),pPlayer.getCivilizationDescription(0),joinPlayer.AI_getAttitudeExtra(pPlayer.getID())))

						pRevTeam = gc.getTeam( joinPlayer.getTeam() )

						iNumPlayerCities = pPlayer.getNumCities()

						for pCity in cityList :

							# Move units out of city
							if( pRevTeam.isAtWar(pPlayer.getTeam()) and iNumPlayerCities > len(cityList) ) :
								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Moving owner's units")
								RevUtils.clearOutCity( pCity, pPlayer, pRevPlayer )

							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Acquiring %s, pop %d"%(pCity.getName(),pCity.getPopulation()))

							[iWorker,iBestDefender,iCounter,iAttack] = RevUtils.getHandoverUnitTypes( pCity, joinPlayer, joinPlayer )

							RevData.setRevolutionPlayer( pCity, -1 )

#***********************************
							# Acquire city
							#joinPlayer.acquireCity( pCity, False, True )

							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Population of %s before is %d"%(pCity.getName(),pCity.getPopulation()))
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Check city culture is %d, at %d, %d"%(pCity.getCulture(pPlayer.getID()), pCity.getX(),pCity.getY()))
							cityPlot = pCity.plot()
							if( pCity.getCulture( pPlayer.getID() ) == 0 ) :
								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Forcing culture > 0")
								pCity.setCulture( pPlayer.getID(), 1, True )

							try :
								pCity.plot().setOwner( joinPlayer.getID() )
							except :
								print "ERROR in cultural acquisition"
								print "ERROR:  Failed to set owner of city, %s at plot %d, %d "%(pCity.getName(),cityPlot.getX(),cityPlot.getY())
								#print "City culture is %d"%(pCity.getCulture(pPlayer.getID()))

								#pCity = cityPlot.getPlotCity()
								#print "Post culture in %s is %d"%(pCity.getName(),pCity.getCulture(pPlayer.getID()))
								#joinPlayer.acquireCity( pCity, False, False )
								#RevData.initCity(pCity)
								# City has become invalid, will cause game to crash if left
								print "Destroying city so game can continue"
								pCity.kill()
								continue


							pCity = cityPlot.getPlotCity()
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Population of %s after is %d"%(pCity.getName(),pCity.getPopulation()))

							if( pCity.getPopulation() < 1 ) :
								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Error!  City %s is empty"%(pCity.getName()))
#*************************************


							ix = pCity.getX()
							iy = pCity.getY()

							# Record pre-given units for deletion after giving other units
							defaultUnits = RevUtils.getPlayerUnits( ix, iy, joinPlayer.getID() )

							# Give a few defenders
							newUnit = joinPlayer.initUnit( iBestDefender, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )
							#joinPlayer.initUnit( iBestDefender, ix, iy, UnitAITypes.NO_UNITAI )
							joinPlayer.initUnit( iCounter, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )
							if( joinPlayer.getNumCities() <= 2 ) :
								# Extra units for first two cities (unlikely in this case)
								if(iWorker != -1):
									joinPlayer.initUnit( iWorker, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )
								joinPlayer.initUnit( iAttack, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )
								joinPlayer.initUnit( iAttack, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )

							elif( gc.getTeam(pPlayer.getTeam()).isAtWar(joinPlayer.getTeam()) ) :
								joinPlayer.initUnit( iBestDefender, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )
								#joinPlayer.initUnit( iBestDefender, ix, iy, UnitAITypes.NO_UNITAI )

							#joinPlayer.receiveGoody( gc.getMap().plot(ix,iy), iGoodyMap, newUnit )
							#joinPlayer.receiveGoody( gc.getMap().plot(ix,iy), iGoodyMap, newUnit )

							# Remove default units
							for unit in defaultUnits :
								unit.kill( False, -1 )

							if( not bIsBarbRev ) : RevData.setRevolutionPlayer( pCity, joinPlayer.getID() )

							# City starts in disorder
							pCity.setOccupationTimer( 2 )

				# Update score to show new agreements, especially Vassal
				CyInterface().setDirty( InterfaceDirtyBits.Score_DIRTY_BIT, True )

			else:
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Player refuses to let civ walk")

				joinPlayer = None
				if( 'iJoinPlayer' in revData.dict.keys() ) :
					joinPlayer = gc.getPlayer( revData.dict['iJoinPlayer'] )

				if( bPeaceful ) :
					# Cities get more pissed off
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Peaceful, increasing rev indices")

					# Save civ type for instigator only
					RevData.setRevolutionPlayer( cityList[0], pRevPlayer.getID() )

					for pCity in cityList :
						RevUtils.doRevRequestDeniedPenalty( pCity, capitalArea, revIdxInc = 150, bExtraColony = True )

					if( not joinPlayer == None ) :
						joinPlayer.AI_changeAttitudeExtra( pPlayer.getID(), -2 )
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s's Extra Attitude towards %s now %d"%(joinPlayer.getCivilizationDescription(0),pPlayer.getCivilizationDescription(0),joinPlayer.AI_getAttitudeExtra(pPlayer.getID())))

				else :
					# Violent uprising!!!
					if( not joinPlayer == None ) :
						joinPlayer.AI_changeAttitudeExtra( pPlayer.getID(), -3 )
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s's Extra Attitude towards %s now %d"%(joinPlayer.getCivilizationDescription(0),pPlayer.getCivilizationDescription(0),joinPlayer.AI_getAttitudeExtra(pPlayer.getID())))

						# Check if joinPlayer would like to declare war on player
						[warOdds,attackerTeam,victimTeam] = RevUtils.computeWarOdds( joinPlayer, pPlayer, cityList[0].area(), allowBreakVassal = self.bAllowBreakVassal )
						# TODO: provide support for human war selection
						if( attackerTeam.isHuman() and not attackerTeam.isAtWar(victimTeam.getID()) ) :
							warOdds = 0

						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - War odds are %d"%(warOdds))

						if( warOdds > 25 and warOdds > game.getSorenRandNum(100,'Revolution: war') ) :
							# have joinPlayer declare war on player
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - joinPlayer's team decides to declare war on pPlayer's team!")
							attackerTeam.declareWar(pPlayer.getTeam(),True, WarPlanTypes.NO_WARPLAN)

							revData.dict['iRevPlayer'] = joinPlayer.getID()
							del revData.dict['iJoinPlayer']
							revData.dict['bIsJoinWar'] = True

							revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
							revoltDict[iRevoltIdx] = revData
							RevData.revObjectUpdateVal( pPlayer, 'RevoltDict', revoltDict )

							self.prepareRevolution( pPlayer, iRevoltIdx, cityList, joinPlayer, bIsJoinWar = True, switchToRevs = switchToRevs )

						else :
							# Check if pPlayer wants to declare war on joinPlayer
							[warOdds,attackerTeam,victimTeam] = RevUtils.computeWarOdds( pPlayer, joinPlayer, cityList[0].area(), allowBreakVassal = self.bAllowBreakVassal )
							if( attackerTeam.isHuman() and not attackerTeam.isAtWar(victimTeam.getID()) ) :
								warOdds = 0

							if( warOdds > 25 and warOdds > game.getSorenRandNum(100,'Revolution: war') ) :
								# pPlayer declares war on joinPlayer!!!
								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - pPlayer's team decides to declare war on joinPlayer's team!")
								attackerTeam.declareWar(joinPlayer.getTeam(),True, WarPlanTypes.NO_WARPLAN)

								revData.dict['iRevPlayer'] = joinPlayer.getID()
								del revData.dict['iJoinPlayer']
								revData.dict['bIsJoinWar'] = False

								revoltDict = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )
								revoltDict[iRevoltIdx] = revData
								RevData.revObjectUpdateVal( pPlayer, 'RevoltDict', revoltDict )

								self.prepareRevolution( pPlayer, iRevoltIdx, cityList, joinPlayer, bIsJoinWar = False, switchToRevs = switchToRevs )

							else :
								# pRevPlayer revolts against pPlayer
								if( not pRevPlayer.isBarbarian() ) :
									pRevPlayer.AI_changeAttitudeExtra( pPlayer.getID(), -5 )
									pRevPlayer.AI_changeAttitudeExtra( joinPlayer.getID(), 5 )
									if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s's Extra Attitude towards %s now %d"%(pRevPlayer.getCivilizationDescription(0),pPlayer.getCivilizationDescription(0),pRevPlayer.AI_getAttitudeExtra(pPlayer.getID())))
									pPlayer.AI_changeAttitudeExtra( pRevPlayer.getID(), -3 )

									gc.getTeam(pRevPlayer.getTeam()).signOpenBorders(joinPlayer.getTeam())
									RevData.revObjectSetVal( pRevPlayer, 'JoinPlayerID', joinPlayer.getID() )

								self.prepareRevolution( pPlayer, iRevoltIdx, cityList, pRevPlayer, bIsJoinWar = revData.dict.get('bIsJoinWar',False), switchToRevs = switchToRevs )

					else :
						if( revData.dict.get('bOfferPeace',False) ) :
							for pCity in handoverCities :
								if( not pCity.getID() in revData.dict.get('cityList', list()) ) :
									if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Bolstering rebellious spirit in %s (handover city only)"%(pCity.getName()))

									revIdx = pCity.getRevolutionIndex()
									localRevIdx = pCity.getLocalRevIndex()
									reinfTurns = pCity.getReinforcementCounter()

									pCity.setRevolutionIndex( max([revIdx+50,revIdx+10*min([localRevIdx,15])]) )
									if( reinfTurns > 2 ) :
										RevData.setCityVal( pCity, 'ReinforcementTurns', max([reinfTurns-(2*revIdx)/self.revInstigatorThreshold,2]) )

						if( not pRevPlayer.isBarbarian() ) :
							pRevPlayer.AI_changeAttitudeExtra( pPlayer.getID(), -5 )
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s's Extra Attitude towards %s now %d"%(pRevPlayer.getCivilizationDescription(0),pPlayer.getCivilizationDescription(0),pRevPlayer.AI_getAttitudeExtra(pPlayer.getID())))
							pPlayer.AI_changeAttitudeExtra( pRevPlayer.getID(), -3 )

						self.prepareRevolution( pPlayer, iRevoltIdx, cityList, pRevPlayer, bIsJoinWar = revData.dict.get('bIsJoinWar',False), switchToRevs = switchToRevs )

		else :
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Unknown revolution type %s"%(revType))
			return

		try :
			cityStr = getCityTextList(cityList)
			cityStr2 = localText.getText("TXT_KEY_REV_CITY", ())
			if( len(cityList) > 1 ) :
				cityStr2 = localText.getText("TXT_KEY_REV_CITIES", ())
		except :
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - ERROR! with city strings")
			return


		mess = localText.getText("TXT_KEY_REV_MESS_REPORT", ())%(cityStr2,cityStr,pPlayer.getCivilizationShortDescription(0))
		if( termsAccepted ) :
			mess += " " + localText.getText("TXT_KEY_REV_MESS_REPORT_EASED", ())
		else :
			mess += " " + localText.getText("TXT_KEY_REV_MESS_REPORT_INCREASED", ())

		for iPlayer in range(0,gc.getMAX_CIV_PLAYERS()):
			if( (not iPlayer == pPlayer.getID()) and gc.getPlayer(iPlayer).isAlive() ) :
				if( not (revType == "independence" and termsAccepted) ) :
					try :
						iTeam = gc.getPlayer(iPlayer).getTeam()
						if( cityList[0].getEspionageVisibility(iTeam) ) :
							CyInterface().addMessage(iPlayer, false, gc.getDefineINT("EVENT_MESSAGE_TIME"), mess, None, InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT, None, gc.getInfoTypeForString("COLOR_HIGHLIGHT_TEXT"), -1, -1, False, False)
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Informing %s, who have espionage vis, of this revolt"%(gc.getPlayer(iPlayer).getCivilizationDescription(0)))
					except :
						print "Error!  C++ call failed, end of processRevolution, player %d"%(iPlayer)


		if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Completed processing revolution")

		return


	def controlLostNetworkHandler( self, iPlayer, iNumTurns, newLeaderType ) :
		if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Handling network lost control of civ popup")

		pPlayer = gc.getPlayer(iPlayer)
#-------------------------------------------------------------------------------------------------
# Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
		# still some issues here with the passed in newLeaderType... so setting to existing name atm
		newLeaderName = pPlayer.getName()
#-------------------------------------------------------------------------------------------------
# END Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------

		if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Changing leader to %s"%(newLeaderName))

		if( newLeaderType == pPlayer.getLeaderType() ) :
			# Just change the name of leader
			#assert( not newLeaderName == None )
			#if( pPlayer.isHuman() or pPlayer.getID() == game.getActivePlayer() ) :
				# Don't change for human, so their name remains after anarchy
			#	pass
			#else :
			#	pPlayer.setName( CvUtil.convertToStr(newLeaderName) )

			pPlayer.setName( CvUtil.convertToStr(newLeaderName) )

			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - No leader change, leader's of same type")
			for iPlayer in range(0,gc.getMAX_CIV_PLAYERS()) :
				if( pPlayer.canContact(iPlayer) ) :
					mess = '%s '%(newLeaderName) + localText.getText("TXT_KEY_REV_MESS_NEW_LEADER",()) + ' %s!'%(pPlayer.getCivilizationDescription(0))
					CyInterface().addMessage(iPlayer, false, gc.getDefineINT("EVENT_MESSAGE_TIME"), mess, None, InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT, None, ColorTypes(79), -1, -1, False, False)

			# Change personality type
			if( game.isOption( GameOptionTypes.GAMEOPTION_RANDOM_PERSONALITIES ) ) :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Giving new, random personality by game option")
				RevUtils.changePersonality( pPlayer.getID() )
			elif( newLeaderName == CvUtil.convertToStr(gc.getLeaderHeadInfo( newLeaderType ).getDescription()) ) :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Giving back original leader personality")
				RevUtils.changePersonality( pPlayer.getID(), newLeaderType )
			else :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Giving new, random personality")
				RevUtils.changePersonality( pPlayer.getID() )

		else :
			#if( pPlayer.isHuman() or pPlayer.getID() == game.getActivePlayer() ) :
				# Don't need to save this as player can't exit while in automation
			#	if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Skipping leader change for human")
				#self.humanLeaderType = pPlayer.getLeaderType()
			#else :
			#	RevUtils.changeCiv(pPlayer.getID(),pPlayer.getCivilizationType(),newLeaderType)

			RevUtils.changeCiv(pPlayer.getID(),pPlayer.getCivilizationType(),newLeaderType)
#-------------------------------------------------------------------------------------------------
# Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
			for iPlayerTest in range(0,gc.getMAX_CIV_PLAYERS()) :
				if( pPlayer.canContact(iPlayerTest) ) :
					mess = '%s '%(pPlayer.getName()) + localText.getText("TXT_KEY_REV_MESS_NEW_LEADER",()) + ' %s!'%(pPlayer.getCivilizationDescription(0))
					CyInterface().addMessage(iPlayerTest, false, gc.getDefineINT("EVENT_MESSAGE_TIME"), mess, None, InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT, None, ColorTypes(79), -1, -1, False, False)
#-------------------------------------------------------------------------------------------------
# Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------

		#if( revData.dict.get( 'bIsElection', False ) ) :
		#	pPlayer.changeAnarchyTurns(1)
		#elif( pPlayer.getCurrentRealEra() > gc.getNumRealEras()/2 ) :
		if( pPlayer.getCurrentRealEra() > gc.getNumRealEras()/2 ) :
			pPlayer.changeAnarchyTurns(3)
		else :
			pPlayer.changeAnarchyTurns(2)
#-------------------------------------------------------------------------------------------------
# Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------

		#if (self.isLocalHumanPlayer(pPlayer.getID())):
		if(pPlayer.isHuman()) :
			game.setForcedAIAutoPlay( iPlayer, iNumTurns, true )
		#	SdToolKitCustom.sdObjectSetVal( "AIAutoPlay", game, "bCanCancelAuto", False )
			SdToolKitCustom.sdObjectSetVal( "AIAutoPlay", game, "bCanCancelAuto", False )
		RevInstances.AIAutoPlayInst.abdicateMultiCheckNoMessage(iPlayer, iNumTurns, False)
#-------------------------------------------------------------------------------------------------
# Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------


	def joinHumanHandler( self, iPlayerID, netUserData, popupReturn ) :
		if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Handling join human popup")

		buttons = netUserData[0]
		buttonLabel = buttons[popupReturn.getButtonClicked()]
		iPlayer = netUserData[1]
		pPlayer = gc.getPlayer(iPlayer)
		iRevoltIdx = netUserData[2]
		revData = RevData.revObjectGetVal( pPlayer, 'RevoltDict' )[iRevoltIdx]

		cityList = list()
		for iCity in revData.cityList :
			pCity = pPlayer.getCity( iCity )
			if( pCity.isNone() ) :
				# City no longer owned by the former owner
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s no longer owned by former owner")
			else :
				cityList.append( pCity )

		if( len(cityList) == 0 ) :
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - No cities left, cancelling")
			return

		revType = revData.revType
		bPeaceful = revData.bPeaceful

		if( buttonLabel == 'welcome' ) :
			# Welcome back!
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Revolutionaries welcomed with open arms")

			joinPlayer = gc.getPlayer( revData.dict['iJoinPlayer'] )

			joinPlayer.AI_changeAttitudeExtra( pPlayer.getID(), 2 )
			#if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s's Extra Attitude towards %s now %d"%(joinPlayer.getCivilizationDescription(0),pPlayer.getCivilizationDescription(0),joinPlayer.AI_getAttitudeExtra(pPlayer.getID())))

			pJoinTeam = gc.getTeam( joinPlayer.getTeam() )

			iNumPlayerCities = pPlayer.getNumCities()
			iGoodyMap = CvUtil.findInfoTypeNum(gc.getGoodyInfo,gc.getNumGoodyInfos(),RevDefs.sXMLGoodyMap)

			for pCity in cityList :
				# Move units out of city
				if( pJoinTeam.isAtWar(pPlayer.getTeam()) and iNumPlayerCities > len(cityList) ) :
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Moving owner's units")
					RevUtils.clearOutCity( pCity, pPlayer, joinPlayer )

				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Acquiring %s"%(pCity.getName()))

				[iWorker,iBestDefender,iCounter,iAttack] = RevUtils.getHandoverUnitTypes( pCity, joinPlayer, joinPlayer )

				RevData.setRevolutionPlayer( pCity, -1 )

#***********************************
				# Acquire city
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Population of %s before is %d"%(pCity.getName(),pCity.getPopulation()))
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Check city culture is %d, at %d, %d"%(pCity.getCulture(pPlayer.getID()), pCity.getX(),pCity.getY()))
				cityPlot = pCity.plot()
				if( pCity.getCulture( pPlayer.getID() ) == 0 ) :
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Forcing culture > 0")
					pCity.setCulture( pPlayer.getID(), 1, True )

				try :

					pCity.plot().setOwner( joinPlayer.getID() )
				except :
					print "ERROR in join human"
					print "ERROR:  Failed to set owner of city, %s at plot %d, %d "%(pCity.getName(),cityPlot.getX(),cityPlot.getY())
					#print "City culture is %d"%(pCity.getCulture(pPlayer.getID()))

					#pCity = cityPlot.getPlotCity()
					#print "Post culture in %s is %d"%(pCity.getName(),pCity.getCulture(pPlayer.getID()))
					#joinPlayer.acquireCity( pCity, False, False )
					#RevData.initCity(pCity)
					# City has become invalid, will cause game to crash if left
					print "Destroying city so game can continue"
					pCity.kill()
					continue

				pCity = cityPlot.getPlotCity()
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Population of %s after is %d"%(pCity.getName(),pCity.getPopulation()))

				if( pCity.getPopulation() < 1 ) :
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Error!  City %s is empty"%(pCity.getName()))
#*************************************

				# Give a few defenders
				ix = pCity.getX()
				iy = pCity.getY()
				newUnit = joinPlayer.initUnit( iBestDefender, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )
				#joinPlayer.initUnit( iBestDefender, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )
				joinPlayer.initUnit( iCounter, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )
				if( joinPlayer.getNumCities() <= 2 ) :
					# Extra units for first two cities (unlikely in this case)
					if(iWorker != -1):
						joinPlayer.initUnit( iWorker, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )
					joinPlayer.initUnit( iAttack, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )
					joinPlayer.initUnit( iAttack, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )
				elif( gc.getTeam(pPlayer.getTeam()).isAtWar(joinPlayer.getTeam()) ) :
					joinPlayer.initUnit( iBestDefender, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )
					#joinPlayer.initUnit( iBestDefender, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )

				#joinPlayer.receiveGoody( gc.getMap().plot(ix,iy), iGoodyMap, newUnit )
				#joinPlayer.receiveGoody( gc.getMap().plot(ix,iy), iGoodyMap, newUnit )

				RevData.setRevolutionPlayer( pCity, joinPlayer.getID() )

		elif( buttonLabel == 'goaway' ) :
			# Go away!
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Revolutionaries rebuffed, striking out on their own")
			revData.dict['bIsJoinWar'] = False
			del revData.dict['iJoinPlayer']
			self.processRevolution( pPlayer, iRevoltIdx, cityList, revType, bPeaceful, True )

		else :
			# WTF?
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Unexpected button label %s"%(buttonLabel))


##--- Revolutionary spawning functions ---------------------------------------

	# lfgr: Cleanup
	def prepareRevolution( self, pPlayer, iRevoltIdx, cityList, pRevPlayer, bIsJoinWar = False, switchToRevs = False ) :
		# Store revolution data, so rev starts with new civs turn
		cityIDList = list()
		for pCity in cityList :
			#if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Storing city id #%d"%(pCity.getID()))
			cityIDList.append(pCity.getID())

		spawnList = RevData.revObjectGetVal( pRevPlayer, 'SpawnList' )
		spawnList.append([pPlayer.getID(), iRevoltIdx])
		RevData.revObjectSetVal( pRevPlayer, 'SpawnList', spawnList )

		if self.LOG_DEBUG : CvUtil.pyPrint( "  Revolt - Stored revolt spawn data for rev player %d, revolt against player %d idx %d" % (pRevPlayer.getID(), pPlayer.getID(), iRevoltIdx) )

		if self.isLocalHumanPlayer( pPlayer.getID() ) and game.getAIAutoPlay( game.getActivePlayer() ) == 0 :
			# Threatening popup to remind player what's coming

			bodStr = getCityTextList(cityList, bPreCity = True, bPostIs = True) + ' '

			if pRevPlayer.isAlive() :
				bodStr += localText.getText("TXT_KEY_REV_JOINING_WAR",())%(pRevPlayer.getCivilizationDescription(0))
			else :
				bodStr += localText.getText("TXT_KEY_REV_PREPARING_WAR",())

			popupInfo = CyPopupInfo()
			popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
			popupInfo.setText( bodStr )
			popupInfo.addPythonButton("OK",'')
			popupInfo.addPopup(pPlayer.getID())

		# Cause disorder in rebelling cities, injure units now
		for pCity in cityList :
			pCity.setOccupationTimer( 2 )
			pCity.setRevolutionCounter( 2 )

			mess = localText.getText("TXT_KEY_REV_MESS_BREWING",())%(pCity.getName())
			CyInterface().addMessage(pPlayer.getID(), true, gc.getDefineINT("EVENT_MESSAGE_TIME"), mess, "AS2D_CITY_REVOLT", InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT, CyArtFileMgr().getInterfaceArtInfo("INTERFACE_RESISTANCE").getPath(), ColorTypes(7), pCity.getX(), pCity.getY(), true, true)

			unitList = RevUtils.getPlayerUnits( pCity.getX(), pCity.getY(), pPlayer.getID() )
			for unit in unitList :
				if( unit.canFight() ) :
					iPreDamage = unit.getDamage()
					iDamage = iPreDamage/3 + 20 + game.getSorenRandNum(15,'Revolt - Injure unit')
					iDamage = min([iDamage,90])
					iDamage = max([iDamage,iPreDamage])
					unit.setDamage( iDamage, pRevPlayer.getID() )
					# LFGR_TODO: Don't injure heroes?

	# lfgr: cleanup
	def launchRevolution( self, iRevPlayer ) :

		pRevPlayer = gc.getPlayer( iRevPlayer )

		spawnList = RevData.revObjectGetVal( pRevPlayer, 'SpawnList' )
		assert spawnList is not None and len( spawnList ) > 0, "Error:  Launch revolution called for player %d with no rev data"%(iRevPlayer)

		newSpawnList = list()

		for [iPlayer,iRevoltIdx] in spawnList :
			pPlayer = gc.getPlayer(iPlayer)

			if not pPlayer.isAlive() :
				if self.LOG_DEBUG : CvUtil.pyPrint( "  Revolt - WARNING!  Player %d is dead, revolt %d canceled" % (iPlayer, iRevoltIdx) )
				continue

			try :
				revoltData = RevData.revObjectGetVal(pPlayer, 'RevoltDict')[iRevoltIdx]
			except KeyError :
				if self.LOG_DEBUG : CvUtil.pyPrint( "  Revolt - Error! Player %d does not have a revolt of index %d" % (iPlayer, iRevoltIdx) )
				continue

			if revoltData.iRevTurn <= game.getGameTurn() :
				# It's on!  Spawn revolutionaries
				if revoltData.dict.get( 'iRevPlayer', -1 ) != pRevPlayer.getID() :
					if self.LOG_DEBUG : CvUtil.pyPrint( "  Revolt - Error! pRevPlayer %d does not match revolt data iRevPlayer %d" % (pRevPlayer.getID(), revoltData.dict.get( 'iRevPlayer', -1 )) )

				cityIDList = revoltData.cityList
				bIsJoinWar = revoltData.dict.get('bIsJoinWar',False)
				switchToRevs = revoltData.dict.get('bSwitchToRevs',False)

				cityList = list()
				for iCity in cityIDList :
					try :
						cityList.append( pPlayer.getCity(iCity) )
					except :
						print "Error:  Couldn't find city #%d"%(iCity) # LFGR_TODO: This can happen sometimes, right?

				if self.LOG_DEBUG : CvUtil.pyPrint( "  Revolt - Found launchable revolt spawn data for player %d, starting spawn against player %d idx %d" % (pRevPlayer.getID(), iPlayer, iRevoltIdx) )

				self.spawnRevolutionaries( cityList, pPlayer, pRevPlayer, bIsJoinWar, switchToRevs )

			else :
				newSpawnList.append([iPlayer,iRevoltIdx])

		RevData.revObjectSetVal( pRevPlayer, 'SpawnList', newSpawnList )

	# lfgr: cleanup
	def spawnRevolutionaries( self, cityList, pPlayer, pRevPlayer, bIsJoinWar = False, switchToRevs = False ) :

		if self.LOG_DEBUG : CvUtil.pyPrint( "  Revolt - Spawning revolutionaries for %d cities in %s" % (len( cityList ), pPlayer.getCivilizationDescription( 0 )) )

		if pPlayer.isBarbarian() :
			if self.LOG_DEBUG : print "Error: attempted spawning of revs for barb player"
			return

		# Enable only for debugging revolts
		if( False ) :
			if(pPlayer.isAlive()):
				if(pPlayer.isHuman() or pPlayer.isHumanDisabled()):
					game.setForcedAIAutoPlay( pPlayer.getID(), 0, false )
			iPrevHuman = game.getActivePlayer()
			RevUtils.changeHuman( pPlayer.getID(), iPrevHuman )

		bIsBarbRev = pRevPlayer.isBarbarian()
		bGaveMap = False

		pTeam = gc.getTeam(pPlayer.getTeam())
		pRevTeam = gc.getTeam(pRevPlayer.getTeam())

		# Check which cities are still up for revolt
		newCityList = list()
		for pCity in cityList :
			if( pCity == None or pCity.isNone() ) :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - WARNING: one rebelling city is dead and gone")
			elif( not pCity.getOwner() == pPlayer.getID() ) :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s no longer controlled by %s, no revolt"%(pCity.getName(),pPlayer.getCivilizationDescription(0)))
			else :
				newCityList.append(pCity)

		cityList = newCityList

		if len( cityList ) == 0 :
			if self.LOG_DEBUG : CvUtil.pyPrint( "  Revolt - WARNING: Revolt cancelled cause no cities in updated list!" )
			return

		# Order by rev index after instigator
		if len( cityList ) > 2 :
			revIdxCityList = cityList[1:]
			revIdxCityList.sort(key=lambda i: (-i.getRevolutionIndex(), i.getName()))
			cityList = cityList[0] + revIdxCityList

		if self.LOG_DEBUG : CvUtil.pyPrint( "  Revolt - Cities in revolt: " + ", ".join( pCity.getName() for pCity in cityList ) )

		# Possibly switch human to rebels
		if not bIsBarbRev and switchToRevs == True :
#-------------------------------------------------------------------------------------------------
# Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
			iPrevHuman = pPlayer.getID()
			RevUtils.changeHuman( pRevPlayer.getID(), iPrevHuman )
#-------------------------------------------------------------------------------------------------
# END Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------

		# Some bookkeeping
		if not bIsBarbRev and not bIsJoinWar and pRevPlayer.getNumCities() < 4 :
			# Record rev turn for this player
			RevData.initPlayer( pRevPlayer )
			RevData.revObjectSetVal( pRevPlayer, 'RevolutionTurn', game.getGameTurn() )

			# LFGR_TODO: Check what exactly is happening here
			if not pRevPlayer.isAlive() :
				if len( cityList ) < 3 :
					cityString = CvUtil.convertToStr(cityList[0].getName())
				else :
					cityString = None
				RevData.revObjectSetVal( pRevPlayer, 'CapitalName', cityString )
			if RevData.revObjectGetVal( pRevPlayer, 'MotherlandID' ) is None :
				RevData.revObjectSetVal( pRevPlayer, 'MotherlandID', pPlayer.getID() )

		bJoinRev = True
		# Possibly create revolutionary player
		if not pRevPlayer.isAlive() and not bIsBarbRev :
			# Fires naming logic for new civ, so messages get the right name

			# Must call setNewPlayerAlive to avoid having DLL set this player alive with setPlayerAlive which calls its turn and the turns of all players with higher numbers
			# Instead, this way makes it alive so it takes its next turn in turn

			# Add replay message
			mess = localText.getText("TXT_KEY_REV_MESS_VIOLENT",()) + ' ' + PyPlayer(pPlayer.getID()).getCivilizationName() + '!'
			mess += "  " + localText.getText("TXT_KEY_REV_MESS_RISEN",(pRevPlayer.getCivilizationDescription(0), pRevPlayer.getNameKey()))
			game.addReplayMessage( ReplayMessageTypes.REPLAY_MESSAGE_MAJOR_EVENT, pRevPlayer.getID(), mess, cityList[0].getX(), cityList[0].getY(), gc.getInfoTypeForString("COLOR_WARNING_TEXT"))

			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Setting new rebel player alive")
			pRevPlayer.setIsRebel( True )
			if( SdToolKitCustom.sdObjectExists( 'BarbarianCiv', pPlayer ) and not RevInstances.BarbarianCivInst == None ) :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Setting new rebel player as barb civ since motherland is")
				RevInstances.BarbarianCivInst.setupSavedData( pRevPlayer.getID(), bSetupComplete = 1 )
			if( pPlayer.isMinorCiv() ) :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Setting new rebel player as minor civ since motherland is")
				pRevTeam.setIsMinorCiv( True, False )
				if( SdToolKitCustom.sdObjectExists( 'BarbarianCiv', game ) ) :
					# If motherland is on always minor list, put rebel on as well
					alwaysMinorList = SdToolKitCustom.sdObjectGetVal( "BarbarianCiv", game, "AlwaysMinorList" )
					if( not alwaysMinorList == None and pPlayer.getID() in alwaysMinorList ) :
						alwaysMinorList.append(pRevPlayer.getID())
						SdToolKitCustom.sdObjectSetVal( "BarbarianCiv", game, "AlwaysMinorList", alwaysMinorList )
			else :
				if( pRevPlayer.isMinorCiv() ) :
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - pRevPlayer was minor civ, changing")
					pRevTeam.setIsMinorCiv( False, False )
			pRevPlayer.setNewPlayerAlive(True)

			bJoinRev = False

		for iPlayer in range(0,gc.getMAX_CIV_PLAYERS()) :
			if(gc.getPlayer(iPlayer) == None):
				continue
			# Craft revolution anouncement message for all players

			if( gc.getPlayer(iPlayer).canContact(pPlayer.getID()) or iPlayer == pPlayer.getID() ) :
				colorNum = 7
				if( bIsBarbRev ) :
					if( iPlayer == pPlayer.getID() ) :
						colorNum = 7
						mess = "<color=255,0,0,255>" + localText.getText("TXT_KEY_REV_MESS_YOU_BARB",())
					else :
						colorNum = 7
						mess = "<color=255,0,0,255>" + localText.getText("TXT_KEY_REV_MESS_VIOLENT",()) + ' ' + PyPlayer(pPlayer.getID()).getCivilizationName() + '!!!'
						mess += "  " + localText.getText("TXT_KEY_REV_MESS_BARB",())
				else :
					if( iPlayer == pPlayer.getID() ) :
						colorNum = 7
						mess = "<color=255,0,0,255>"
						if( bJoinRev ) :
							mess += localText.getText("TXT_KEY_REV_MESS_JOIN",(pRevPlayer.getNameKey(), pRevPlayer.getCivilizationDescription(0)))
						else :
							mess += localText.getText("TXT_KEY_REV_MESS_YOU_RISEN",(pRevPlayer.getNameKey(), pRevPlayer.getCivilizationDescription(0)))
					else :
						mess = ""

						if( iPlayer == pRevPlayer.getID() ) :
							mess += "<color=0,255,0,255>"
							colorNum = 8
						else :
							mess += "<color=255,0,0,255>"
							colorNum = 7

						mess += localText.getText("TXT_KEY_REV_MESS_VIOLENT",()) + ' ' + PyPlayer(pPlayer.getID()).getCivilizationName() + '!!!'
						if( bJoinRev ) :
							mess += "  " + localText.getText("TXT_KEY_REV_MESS_JOIN",(pRevPlayer.getName(), pRevPlayer.getCivilizationDescription(0)))
						else :
							mess += "  " + localText.getText("TXT_KEY_REV_MESS_RISEN",(pRevPlayer.getCivilizationDescription(0), pRevPlayer.getNameKey()))

				if( iPlayer == pPlayer.getID() ) :
					CyInterface().addMessage(iPlayer, true, gc.getDefineINT("EVENT_MESSAGE_TIME"), mess, "AS2D_CITY_REVOLT", InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT, CyArtFileMgr().getInterfaceArtInfo("INTERFACE_RESISTANCE").getPath(), ColorTypes(colorNum), cityList[0].getX(), cityList[0].getY(), True, True)
				elif( iPlayer == pRevPlayer.getID() ) :
					CyInterface().addMessage(iPlayer, true, gc.getDefineINT("EVENT_MESSAGE_TIME"), mess,  "AS2D_DECLAREWAR", InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT, None, ColorTypes(colorNum), cityList[0].getX(), cityList[0].getY(), False, False)
				else :
					CyInterface().addMessage(iPlayer, false, gc.getDefineINT("EVENT_MESSAGE_TIME"), mess,  "AS2D_DECLAREWAR", InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT, None, ColorTypes(colorNum), -1, -1, False, False)

		if( not bIsBarbRev ) :

			pRevTeam = gc.getTeam( pRevPlayer.getTeam() )
			if( not pRevTeam.isAtWar(pPlayer.getTeam()) ) :
				pRevTeam.declareWar( pPlayer.getTeam(), True, WarPlanTypes.WARPLAN_TOTAL )
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - The %s revolutionaries declare war and start a revolution against the %s!"%(pRevPlayer.getCivilizationAdjective(0),pPlayer.getCivilizationDescription(0)))
				pRevPlayer.setIsRebel( True )
				pRevTeam.setRebelAgainst( pPlayer.getTeam(), True )
			elif( pRevPlayer.isMinorCiv() and not bIsJoinWar ) :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - The %s revolutionaries declare war and start a revolution against the %s!"%(pRevPlayer.getCivilizationAdjective(0),pPlayer.getCivilizationDescription(0)))
				pRevPlayer.setIsRebel( True )
				pRevTeam.setRebelAgainst( pPlayer.getTeam(), True )
			else :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - The %s revolutionaries join in the war against the %s!"%(pRevPlayer.getCivilizationAdjective(0),pPlayer.getCivilizationDescription(0)))

			# Money
			if( pRevPlayer.getGold() < 200 ) :
				iGold = 30 + game.getSorenRandNum(30*len(cityList),'Revolt: give gold')
			else :
				iGold = 10 + game.getSorenRandNum(20*len(cityList),'Revolt: give gold')
			pRevPlayer.changeGold( min([iGold,200]) )

			pRevPlayer.setFreeUnitCountdown(20)

			# Espionage
			if( not game.isOption(GameOptionTypes.GAMEOPTION_NO_ESPIONAGE) and not bIsJoinWar ) :
				espPoints = game.getSorenRandNum(20*len(cityList),'Revolt: esp') + (12+len(cityList))*max([pPlayer.getCommerceRate( CommerceTypes.COMMERCE_ESPIONAGE ), 6])
				if( pRevTeam.isAlive() ) :
					espPoints /= 2
				pRevTeam.changeCounterespionageTurnsLeftAgainstTeam(pTeam.getID(), 10)
				pRevTeam.changeEspionagePointsAgainstTeam(pTeam.getID(), espPoints)
				pTeam.changeEspionagePointsAgainstTeam(pRevTeam.getID(), espPoints/(3 + pTeam.getAtWarCount(True)))
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Giving rebels %d espionage points against motherland"%(espPoints))
				if( not pRevTeam.isAlive() ) :
					for k in range(0,gc.getMAX_CIV_TEAMS()) :
						if(gc.getTeam(k) == None):
							continue
						if( pRevTeam.isAtWar(k) and not gc.getTeam(k).isMinorCiv() ) :
							pRevTeam.changeEspionagePointsAgainstTeam(k, game.getSorenRandNum(espPoints/2,'Revolt: esp') )
							gc.getTeam(k).changeEspionagePointsAgainstTeam(pRevTeam.getID(), game.getSorenRandNum(espPoints/5, 'Revolt: esp'))

			# Diplomacy
			if( pRevTeam.isMapTrading() ) :
				# Give motherlands map
				bGaveMap = True
				gameMap = gc.getMap()
				for ix in range(0,CyMap().getGridWidth()) :
					for iy in range(0,CyMap().getGridHeight()) :
						pPlot = gameMap.plot(ix,iy)
						if( pPlot.isRevealed(pTeam.getID(),False) ) :
							pPlot.setRevealed(pRevTeam.getID(),True,False,pTeam.getID())

				# Meet players known by motherland
				for k in range(0,gc.getMAX_CIV_TEAMS()) :
					kTeam = gc.getTeam(k)
					if(kTeam == None):
						continue
					if( (kTeam.getLeaderID() < 0) or  (kTeam.getLeaderID() > gc.getMAX_CIV_PLAYERS()) ):
						continue
					kPlayer = gc.getPlayer(kTeam.getLeaderID())
					if(kPlayer == None):
						continue
					if( pTeam.isHasMet(k) and not k == pRevPlayer.getTeam() and not k == pTeam.getID() ) :
						if( pTeam.isAtWar(k) ) :
							pRevTeam.meet(k,False)
							pRevPlayer.AI_changeAttitudeExtra( kTeam.getLeaderID(), 2 )
							kPlayer.AI_changeAttitudeExtra( pRevPlayer.getID(), 2 )
						else :
							if( game.getSorenRandNum(100,'odds') > 50 ) :
								pRevTeam.meet(k,False)
								if( kPlayer.AI_getAttitude(pPlayer.getID()) == AttitudeTypes.ATTITUDE_FRIENDLY ) :
									kPlayer.AI_changeAttitudeExtra( pRevPlayer.getID(), -2 )


		if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Spawning %s revolutionaries!!!"%(pRevPlayer.getCivilizationAdjective(0)))

		iGoodyMap = CvUtil.findInfoTypeNum(gc.getGoodyInfo,gc.getNumGoodyInfos(),RevDefs.sXMLGoodyMap)
		iGeneral = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),RevDefs.sXMLGeneral)
		# phungus420 RevUnits Softcoding
		iSpy = pRevPlayer.getBestUnitType(UnitAITypes.UNITAI_SPY)
		iSettler = pRevPlayer.getBestUnitType(UnitAITypes.UNITAI_SETTLE)
		iScout = pRevPlayer.getBestUnitType(UnitAITypes.UNITAI_EXPLORE)
		# phungus420 end

		revIdxInc = 200

		for [cityIdx,pCity] in enumerate(cityList) :

			revIdx = pCity.getRevolutionIndex()
			localRevIdx = pCity.getLocalRevIndex()
			ix = pCity.getX()
			iy = pCity.getY()

			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - In %s, with rev idx %d (%d local)"%(pCity.getName(),revIdx,localRevIdx))

			spawnableUnits = RevUtils.getUprisingUnitTypes( pCity, pRevPlayer, bIsJoinWar )
			[iWorker,iBestDefender,iCounter,iAttack] = RevUtils.getHandoverUnitTypes( pCity, pRevPlayer, pPlayer )

			if( len(spawnableUnits) < 1 ) :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - ERROR!!! No rev units possible in %s"%(pCity.getName()))
				continue

			pCity.setOccupationTimer(1)

			# First look just for rebel, homeland, or unowned territory to spawn in
			spawnablePlots = RevUtils.getSpawnablePlots( ix, iy, pRevPlayer, bLand = True, bIncludePlot = False, bIncludeCities = False, bSameArea = True, iRange = 1, iSpawnPlotOwner = pRevPlayer.getID(), bCheckForEnemy = True, bAtWarPlots = False, bOpenBordersPlots = False )
			if( len(spawnablePlots) == 0 ) :
				# Try plots owner by other players, either with open borders or at war with rebel
				spawnablePlots = RevUtils.getSpawnablePlots( ix, iy, pRevPlayer, bLand = True, bIncludePlot = False, bIncludeCities = False, bSameArea = True, iRange = 1, iSpawnPlotOwner = pRevPlayer.getID(), bCheckForEnemy = True, bAtWarPlots = True )
			if( len(spawnablePlots) == 0 ) :
				# Check if plots are available if we move opposing units
				spawnablePlots = RevUtils.getSpawnablePlots( ix, iy, pRevPlayer, bLand = True, bIncludePlot = False, bIncludeCities = False, bSameArea = True, iRange = 1, iSpawnPlotOwner = pRevPlayer.getID(), bCheckForEnemy = False, bAtWarPlots = True )
			if( len(spawnablePlots) == 0 ) :
				# Expand search area
				spawnablePlots = RevUtils.getSpawnablePlots( ix, iy, pRevPlayer, bLand = True, bIncludePlot = False, bIncludeCities = False, bSameArea = True, iRange = 2, iSpawnPlotOwner = pRevPlayer.getID(), bCheckForEnemy = True )
			if( len(spawnablePlots) == 0 ) :
				# Put them anywhere nearby, this will only fail on single plot islands
				spawnablePlots = RevUtils.getSpawnablePlots( ix, iy, pRevPlayer, bLand = True, bIncludePlot = False, bIncludeCities = False, bSameArea = True, iRange = 3, iSpawnPlotOwner = -1, bCheckForEnemy = False )

			pCity.setOccupationTimer(0) # LFGR_TODO: ?

			revSpawnLoc = None
			if( len(spawnablePlots) > 0 ) :
				revSpawnLoc = spawnablePlots[game.getSorenRandNum(len(spawnablePlots),'Revolution: Pick rev plot')]

			# if( pPlayer.getID() == game.getActivePlayer() or pRevPlayer.getID() == game.getActivePlayer() ) :
				#Center camera on city
				# if( not revSpawnLoc == None ) :
					# CyCamera().LookAt( pCity.plot().getPoint(), CameraLookAtTypes.CAMERALOOKAT_CITY_ZOOM_IN, gc.getMap().plot(revSpawnLoc[0],revSpawnLoc[1]).getPoint() )
				# else :
					# CyCamera().LookAt( pCity.plot().getPoint(), CameraLookAtTypes.CAMERALOOKAT_CITY_ZOOM_IN, pCity.plot().getPoint() )

			# New unit count method
			localFactor = min([localRevIdx+2,1.5*self.badLocalThreshold])
			if pRevPlayer.getID() == RevData.getRevolutionPlayer( pCity ) :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Repeat revolution, increasing enlistment")
				effPop = 2.0*pow(pCity.getPopulation(),.8) + 1.0
			else :
				effPop = pow(pCity.getPopulation(),.8) + 1.0
			popMod = (revIdx/(1.0*self.alwaysViolentThreshold))
			if( bIsBarbRev or bIsJoinWar ) :
				popMod = max([ 0.2, pow(max([popMod-.35,0]),.5)/2.0])
			else :
				popMod = max([ 0.3, pow(max([popMod-.35,0]),.5)])
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Population modifier: %.3f on eff pop %.2f (%d)"%(popMod,effPop,pCity.getPopulation()))
			iNumUnits2a = (popMod*(effPop))/2.0

			if( bIsBarbRev or bIsJoinWar ) :
				iNumUnits2b = ((localFactor-self.badLocalThreshold)/(1.0*self.badLocalThreshold))*pow(RevUtils.getNumDefendersNearPlot(ix,iy,pPlayer.getID())/2.0,.5)/2.0
			else :
				iNumUnits2b = (localFactor/(1.0*self.badLocalThreshold))*pow(RevUtils.getNumDefendersNearPlot(ix,iy,pPlayer.getID()),.5)/2.0
			if( iNumUnits2b < 0 ) :
				iNumUnits2b = max([iNumUnits2b,-iNumUnits2a/2.0,-2.0])
			iNumUnits2 = int(math.floor( self.strengthModifier*(iNumUnits2a + iNumUnits2b) + .5 ))

			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - New method from pop: %.2f, from troops: %.2f, total: %d"%(iNumUnits2a,iNumUnits2b,iNumUnits2))

			iNumUnits = iNumUnits2
			
			iNumUnit = iNumUnits * 2 # LFGR_TODO: typo?

			iNumDefenders = RevUtils.getNumDefendersNearPlot(ix,iy,pPlayer.getID())

			if( cityIdx > 1 and iNumUnits > 2 ) :
				# Third or higher city in large revolt, cities should be in rev index order so these should be less fervent
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Reducing number of rebel troops for large revolt")
				iNumUnits = iNumUnits - cityIdx/2
				iNumUnits = max([iNumUnits, 2])

			unitAdjust = max([3, pCity.getPopulation()/4, iNumDefenders])
			if( False and bIsJoinWar ) :
				# Joining established player in war
				iNumUnits = min( [iNumUnits, max([pCity.getPopulation()/3,iNumUnits/2,1]), unitAdjust] )
				iNumUnits = max( [iNumUnits, 1 - cityIdx, 0] )
			elif( False and bIsBarbRev ) :
				# Lower max number of barb units
				iNumUnits = min( [iNumUnits - 1, max([pCity.getPopulation()/2,iNumUnits/2,1]), unitAdjust] )
				iNumUnits = max( [iNumUnits, 2 - cityIdx, 0] )
			else :
				#iNumUnits = min( [iNumUnits, pCity.getPopulation(), 2*unitAdjust] )
				iNumUnits = max( [iNumUnits, 2 - cityIdx, 0] )


			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Revised enlistment: %d, num defenders nearby: %d"%(iNumUnits,iNumDefenders))

			# Determine whether revolutionaries take control of the city
			revControl = False
			if( iNumUnits == 0 ) :
				# No actual rebels for this city, just disorder
				revControl = False
				if( revSpawnLoc == None ) :
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - No where to spawn rebels, but no rebel units to spawn either ... faking spawn location")
					revSpawnLoc = [0,0]
			elif( pCity.plot().getNumDefenders(pPlayer.getID()) == 0 ) :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - City has no defenders, revs control")
				revControl = True
			elif( revSpawnLoc == None ) :
				# If no plot on which to spawn revs, they get city and owners units flee
				# TODO: What about bIsJoinWar case?
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - No where to spawn rebels, so they get city")
				revControl = True
			elif( True ) :
				# Config option (LFGR_TODO)
				revControl = False
			else :
				# Compare strength of revolution and garrison
				iRevStrength = iNumUnits
				if( (pCity.unhappyLevel(0) - pCity.happyLevel()) > 0 ) :
					iRevStrength += 2
				if( bIsJoinWar ) :
					iRevStrength -= 2
				if( bIsBarbRev ) :
					iRevStrength -= 4
				if( pCity.isCapital() ) :
					iRevStrength -= 1

				iGarrisonStrength = pCity.plot().getNumDefenders(pPlayer.getID()) + 1
				iGarrisonStrength = int( iGarrisonStrength*(110 + pCity.getBuildingDefense())/100.0 )

				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Rev strength: %d,  Garrison strength: %d"%(iRevStrength,iGarrisonStrength))

				if( iRevStrength > iGarrisonStrength ) :
					# Revolutionaries out muscle the city garrison and take control
					revControl = True
				else :
					# Spawn in countryside
					revControl = False

			if( revControl ) :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Revs take control of %s (%d,%d)"%(pCity.getName(),pCity.getX(),pCity.getY()))

				# Turn off rebellious city capture logic, all components handled here
				RevData.setRevolutionPlayer( pCity, -1 )

				# Run wounded soldiers out of Town, try to place near city
				iInjureMax = 40
				retreatPlots = RevUtils.getSpawnablePlots( ix, iy, pPlayer, bLand = True, bIncludePlot = False, bIncludeCities = True, bSameArea = True, iRange = 2, iSpawnPlotOwner = pPlayer.getID(), bCheckForEnemy = True, bAtWarPlots = False, bOpenBordersPlots = False )
				if( len(retreatPlots) == 0 ) :
					iInjureMax = 60
					retreatPlots = RevUtils.getSpawnablePlots( ix, iy, pPlayer, bLand = True, bIncludePlot = False, bIncludeCities = True, bSameArea = False, iRange = 2, iSpawnPlotOwner = pPlayer.getID(), bCheckForEnemy = True, bAtWarPlots = True )
				if( len(retreatPlots) == 0 ) :
					iInjureMax = 65
					retreatPlots = RevUtils.getSpawnablePlots( ix, iy, pPlayer, bLand = True, bIncludePlot = False, bIncludeCities = True, bSameArea = False, iRange = 4, iSpawnPlotOwner = pPlayer.getID(), bCheckForEnemy = True, bAtWarPlots = True )
				if( len(retreatPlots) == 0 ) :
					iInjureMax = 70
					# Try to move to another of players cities
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - No nearby plots, trying move to another of players cities")
					for otherCity in PyPlayer( pPlayer.getID() ).getCityList() :
						pOtherCity = otherCity.GetCy()
						if( not pOtherCity.getID() == pCity.getID() ) :
							retreatPlots.append([pOtherCity.getX(),pOtherCity.getY()])

				if( len(retreatPlots) > 0 ) :
					retreatLoc = retreatPlots[game.getSorenRandNum(len(retreatPlots),'Revolution: Pick rev plot')]
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - City garrison retreating to %d,%d"%(retreatLoc[0], retreatLoc[1]))
				else :
					retreatLoc = None
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - City garrison massacred (had nowhere to go)")
					# pPlayer is about to die anyway

				# Defections?

				toRebelList = list()
				if( not retreatLoc == None ) :
					RevUtils.moveEnemyUnits( ix, iy, pRevPlayer.getID(), retreatLoc[0], retreatLoc[1], iInjureMax = iInjureMax, bDestroyNonLand = False, bLeaveSiege = False )
					unitList = RevUtils.getEnemyUnits( ix, iy, pRevPlayer.getID() )
					for unit in unitList :
						# TODO: if units is captureable ...
						if( 35 > game.getSorenRandNum(100,'Revolution: give rebels equipment') ) :
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Will be giving rebels %s"%(unit.getName()))
							toRebelList.append( unit.getUnitType() )
						else :
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Destroying %s"%(unit.getName()))
							unit.kill(False, pRevPlayer.getID())

				# Store building types in city
				buildingClassList = list()
				for buildingType in range(0,gc.getNumBuildingInfos()) :
					if( pCity.getNumRealBuilding(buildingType) > 0 ) :
						buildingInfo = gc.getBuildingInfo(buildingType)
						buildingClassList.append( [buildingInfo.getBuildingClassType(),pCity.getNumRealBuilding(buildingType)] )

# ***************************************************************
				# Acquire city by cultural conversion
				#pRevPlayer.acquireCity( pCity, False, False )
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Population of %s before is %d"%(pCity.getName(),pCity.getPopulation()))
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Check city culture is %d, at %d, %d"%(pCity.getCulture(pPlayer.getID()), pCity.getX(),pCity.getY()))
				cityPlot = pCity.plot()
				if( pCity.getCulture( pPlayer.getID() ) == 0 ) :
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Forcing culture > 0")
					pCity.setCulture( pPlayer.getID(), 1, True )

				try :
					pCity.plot().setOwner( pRevPlayer.getID() )
				except :
					print "Error in violent takeover"
					print "ERROR:  Failed to set owner of city, %s at plot %d, %d (%d,%d)"%(pCity.getName(),cityPlot.getX(),cityPlot.getY(),ix,iy)
					#print "City culture is %d"%(pCity.getCulture(pPlayer.getID()))

					#pCity = cityPlot.getPlotCity()
					#print "Post culture in %s is %d"%(pCity.getName(),pCity.getCulture(pPlayer.getID()))
					#pRevPlayer.acquireCity( pCity, False, False )
					# No more revolutions for a while
					#RevData.initCity(pCity)
					# City has become invalid, will cause game to crash if left
					print "Destroying city so game can continue"
					pCity.kill()
					continue


				pCity = cityPlot.getPlotCity()
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Population of %s after is %d"%(pCity.getName(),pCity.getPopulation()))

				if( pCity.getPopulation() < 1 ) :
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Error!  City %s is empty"%(pCity.getName()))

				# To kill off auto-spawned defenders after creating new defenders
				defaultUnits = RevUtils.getPlayerUnits( ix, iy, pRevPlayer.getID() )

#****************************************************************

				if( pCity.getPopulation() > 3 + pPlayer.getCurrentRealEra() ) :
					pCity.setOccupationTimer(3)
				else :
					pCity.setOccupationTimer(2)

				newCulVal = int( self.revCultureModifier*max([pCity.getCulture(pPlayer.getID()),pCity.countTotalCultureTimes100()/200]) )
				newPlotVal = int( self.revCultureModifier*max([pCity.plot().getCulture(pPlayer.getID()),pCity.plot().countTotalCulture()/2]) )
				RevUtils.giveCityCulture( pCity, pRevPlayer.getID(), newCulVal, newPlotVal, overwriteHigher = False )

				newUnitList = list()

				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s, pop. %d has %d defenders after removing defaults"%(pCity.getName(),pCity.getPopulation(),pCity.plot().getNumDefenders(pCity.getOwner())))

				# Create stolen equipment
				for unitType in toRebelList :
					newUnit = pRevPlayer.initUnit( unitType, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )
					newUnitList.append( newUnit )

				# Spawn revs in the city, plus an extra defender or two
				# Couple revs die in taking control of city:
				if( iNumUnits > 9 ) :
					iNumUnits -= 2
				elif( iNumUnits > 5 ) :
					iNumUnits -= 1

				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Spawning %d units for city of size %d"%(iNumUnits,pCity.getPopulation()))

				for i in range(0,(iNumUnits*2)) :
					newUnitID = spawnableUnits[game.getSorenRandNum( len(spawnableUnits), 'Revolution: pick unit' )]
					if newUnitID != -1:
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - In %s, spawning %s"%(pCity.getName(),PyInfo.UnitInfo(newUnitID).getDescription()))
						newUnit = pRevPlayer.initUnit( newUnitID, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )
						newUnitList.append( newUnit )
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - In %s, spawned %s   %d,%d   %d"%(pCity.getName(),PyInfo.UnitInfo(newUnitID).getDescription(),ix, iy,newUnit.getID()))


				# Give a few extra defenders and a worker
				if( cityIdx == 0 ) :
					newUnitList.append( pRevPlayer.initUnit(iBestDefender, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH) )
				if(iWorker != -1):
					pRevPlayer.initUnit( iWorker, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )
					if( pCity.getPopulation() > 5 ) :
						pRevPlayer.initUnit( iWorker, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )

				# Injure units to simulate the lack of training in rebel troops
#				for newUnit in newUnitList :
#					if( newUnit.canFight() ) :
#						iDamage = 15 + game.getSorenRandNum(25,'Revolt - Injure unit')
#						newUnit.setDamage( iDamage, pPlayer.getID() )

				# Remove the default given defenders
				for pUnit in defaultUnits :
					pUnit.kill(False,-1)

				if( pCity.getPopulation() > 4 and len(newUnitList) >= 4 ) :
					deltaPop = int( (len(newUnitList)-1)/3.0 )
					pCity.changePopulation( -deltaPop )
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - City population decreased by %d for %d rebel units spawned"%(deltaPop,len(newUnitList)))

				# Extra stuff for instigator city
				if( cityIdx == 0 and len(cityList) > 1 and not bIsBarbRev ) :
					if( 10 + 3*len(cityList) + 5*pCity.getNumRevolts(pCity.getOwner()) < game.getSorenRandNum(100,'Rev') ) :
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Great General (%d) spawned in %s"%(iGeneral,pCity.getName()))
						pRevPlayer.initUnit( iGeneral, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )

				if( not game.isOption(GameOptionTypes.GAMEOPTION_NO_ESPIONAGE) and (iSpy != -1) ):
					if( pRevPlayer.canTrain(iSpy,False,False) and pRevPlayer.AI_getNumAIUnits( UnitAITypes.UNITAI_SPY ) < 3 ) :
						if( (pCity.getNumRevolts(pCity.getOwner()) > 1 and revIdx > self.alwaysViolentThreshold) or (pCity.getNumRevolts(pCity.getOwner()) > 2 and revIdx > self.revInstigatorThreshold) ) :
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Spy spawned in %s"%(pCity.getName()))
							pRevPlayer.initUnit( iSpy, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )

				# Should buildings stay or some destroyed?
				for [buildingClass,iNum] in buildingClassList :
					buildingType = gc.getCivilizationInfo(pRevPlayer.getCivilizationType()).getCivilizationBuildings(buildingClass)

					if (buildingType != BuildingTypes.NO_BUILDING):
						if( pCity.getNumRealBuilding(buildingType) < iNum ) :
							buildingInfo = gc.getBuildingInfo(buildingType)
							if( not buildingInfo.isGovernmentCenter() ) :
								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Building %s saved"%(buildingInfo.getDescription()))
								pCity.setNumRealBuilding( buildingType, iNum )

				# Reveal surrounding countryside
				if( not bGaveMap ) :
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Giving map")
					pRevPlayer.receiveGoody( gc.getMap().plot(ix,iy), iGoodyMap, newUnitList[0] )
					pRevPlayer.receiveGoody( gc.getMap().plot(ix,iy), iGoodyMap, newUnitList[0] )

				# No more revolutions for a while
				pCity.setRevolutionCounter( self.turnsBetweenRevs )
				pCity.setReinforcementCounter( 0 )
				RevData.updateCityVal(pCity, 'RevolutionTurn', game.getGameTurn() )
				if( not bIsBarbRev ) :
					RevData.setRevolutionPlayer( pCity, pRevPlayer.getID() )

			else :
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Owner keeps control of %s (%d,%d), revs spawning at %d,%d"%(pCity.getName(),ix,iy,revSpawnLoc[0],revSpawnLoc[1]))

				# City in disorder
				iTurns = 1 + revIdx/int(0.7*self.revReadyFrac*self.revInstigatorThreshold)
				if( localRevIdx > 4 ) :
					iTurns = int(iTurns*1.5)
					iTurns = min([iTurns,self.turnsBetweenRevs - 1])
				else :
					iTurns = int(min([iTurns,1 + self.turnsBetweenRevs/2]))
				pCity.setOccupationTimer( max([iTurns,1]) )
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - City occupation timer set to %d"%(pCity.getOccupationTimer()))

				if( pCity.getRevRequestAngerTimer() < 3*self.turnsBetweenRevs ) :
					pCity.changeRevRequestAngerTimer( min([2*self.turnsBetweenRevs, 3*self.turnsBetweenRevs - pCity.getRevRequestAngerTimer()]) )

				if( iNumUnits > 0 ) :
					# Move any units that may be on the spawn plot
					enemyUnits = RevUtils.getEnemyUnits( revSpawnLoc[0], revSpawnLoc[1], pRevPlayer.getID() )
					if( len(enemyUnits) > 0 ) :
						moveToPlots = RevUtils.getSpawnablePlots( revSpawnLoc[0], revSpawnLoc[1], gc.getPlayer(enemyUnits[0].getOwner()), bLand = True, bIncludePlot = False, bIncludeCities = True, bIncludeForts = True, bSameArea = True, iRange = 1, iSpawnPlotOwner = enemyUnits[0].plot().getOwner(), bCheckForEnemy = True, bAtWarPlots = False, bOpenBordersPlots = False )
						if( len(moveToPlots) == 0 ) :
							moveToPlots = RevUtils.getSpawnablePlots( revSpawnLoc[0], revSpawnLoc[1], gc.getPlayer(enemyUnits[0].getOwner()), bLand = True, bIncludePlot = False, bIncludeCities = True, bIncludeForts = True, bSameArea = True, iRange = 2, iSpawnPlotOwner = enemyUnits[0].plot().getOwner(), bCheckForEnemy = True, bAtWarPlots = False )
						if( len(moveToPlots) == 0 ) :
							moveToPlots = RevUtils.getSpawnablePlots( revSpawnLoc[0], revSpawnLoc[1], gc.getPlayer(enemyUnits[0].getOwner()), bLand = True, bIncludePlot = False, bIncludeCities = True, bSameArea = False, iRange = 4, iSpawnPlotOwner = -1, bCheckForEnemy = True, bAtWarPlots = False )

						if( len(moveToPlots) == 0 ) :
							# Highly unlikely
							print 'WARNING: Enemy units outside city are going to die cause they have no where to go ...'
						else :
							moveToLoc = moveToPlots[game.getSorenRandNum(len(moveToPlots),'Revolution: Pick move to plot')]
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Enemy units in plot moving to %d,%d"%(moveToLoc[0], moveToLoc[1]))
							RevUtils.moveEnemyUnits( ix, iy, pRevPlayer.getID(), moveToLoc[0], moveToLoc[1], iInjureMax = 0, bDestroyNonLand = False, bLeaveSiege = False )

				# Wound player's units?
				unitList = RevUtils.getEnemyUnits( ix, iy, pRevPlayer.getID(), bOnlyMilitary = True )
				for pUnit in unitList :
					if( pUnit.canFight() ) :
						#if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Garrison unit %s pre damage %d"%(pUnit.getName(),pUnit.getDamage()))
						iPreDamage = pUnit.getDamage()
						if( revIdx > self.revInstigatorThreshold ) :
							iDamage = iPreDamage/5 + 20 + game.getSorenRandNum(35,'Revolution: Wound units')
						else :
							iDamage = iPreDamage/5 + 15 + game.getSorenRandNum(25,'Revolution: Wound units')
						iDamage = min([iDamage,90])
						iDamage = max([iDamage,iPreDamage])
						pUnit.setDamage( iDamage, pRevPlayer.getID() )

				# Defections?

				if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Spawning %d units for city of size %d"%(iNumUnits,pCity.getPopulation()))

				# Spawn rev units outside city
				newUnitList = list()
				for i in range(0,(iNumUnits*2)) :
					newUnitID = spawnableUnits[game.getSorenRandNum( len(spawnableUnits), 'Revolution: pick unit' )]
					if newUnitID != -1:
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Outside of %s, spawning %s"%(pCity.getName(),PyInfo.UnitInfo(newUnitID).getDescription()))
						newUnit = pRevPlayer.initUnit( newUnitID, revSpawnLoc[0], revSpawnLoc[1], UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )
						newUnitList.append( newUnit )
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Outside of %s, spawned %s   %d,%d   %d"%(pCity.getName(),PyInfo.UnitInfo(newUnitID).getDescription(),revSpawnLoc[0], revSpawnLoc[1],newUnit.getID()))

				iOdds = 20 + 8*(min([len(cityList)-cityIdx-1,4])) + 5*min([pCity.getNumRevolts(pPlayer.getID()),5])
				for [iNum,newUnit] in enumerate(newUnitList) :
					if( newUnit.canFight() ) :
						# Injure units to simulate the lack of training in rebel troops
#						iDamage = 10 + game.getSorenRandNum(30,'Revolt - Injure unit')
#						newUnit.setDamage( iDamage, pPlayer.getID() )

						# Check AI settings
						if( newUnit.isBarbarian() ) :
							if( pRevPlayer.AI_unitValue(newUnit.getUnitType(),UnitAITypes.UNITAI_ATTACK_CITY_LEMMING,newUnit.area(), false) > 0 ) :
								newUnit.setUnitAIType( UnitAITypes.UNITAI_ATTACK_CITY_LEMMING )
							else :
								newUnit.setUnitAIType( UnitAITypes.UNITAI_ATTACK )
						else :
							if( iNum < 2 and iNumUnits > 2 and pRevPlayer.AI_unitValue(newUnit.getUnitType(),UnitAITypes.UNITAI_ATTACK_CITY,newUnit.area(), false) > 0 ) :
								newUnit.setUnitAIType( UnitAITypes.UNITAI_ATTACK_CITY )
							elif( iNumUnits == 1 and game.getSorenRandNum(2,'Revolt - Pillage') == 0 and pRevPlayer.AI_unitValue(newUnit.getUnitType(),UnitAITypes.UNITAI_PILLAGE,newUnit.area(), false) > 0 ) :
								newUnit.setUnitAIType( UnitAITypes.UNITAI_PILLAGE )
							else :
								iniAI = newUnit.getUnitAIType()
								if( not (iniAI == UnitAITypes.UNITAI_COUNTER or iniAI == UnitAITypes.UNITAI_ATTACK_CITY) ) :
									newUnit.setUnitAIType( UnitAITypes.UNITAI_ATTACK )
								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s starting with AI type: %d (ini %d)"%(newUnit.getName(),newUnit.getUnitAIType(),iniAI))

						if( not bIsBarbRev and pRevPlayer.isRebel() and revIdx > self.revInstigatorThreshold ) :
							# Give some units a free promotion to help rebel cause
							if( iOdds > game.getSorenRandNum(100,'Revolt - Promotion odds') ) :
								RevUtils.giveRebelUnitFreePromotion(newUnit)

				if( pCity.getPopulation() > 4 and len(newUnitList) >= 4 ) :
					deltaPop = int( (len(newUnitList)-1)/2.5 )
					if( deltaPop >= pCity.getPopulation() ) :
						deltaPop = pCity.getPopulation() - 1
					pCity.changePopulation( -deltaPop )
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - City population decreased by %d for %d rebel units spawned"%(deltaPop,len(newUnitList)))

				# Extra stuff for instigator city
				if( cityIdx == 0 and len(cityList) > 1 and iNumUnits > 0 and not bIsBarbRev ) :
					if( 3*len(cityList) + 5*pCity.getNumRevolts(pCity.getOwner()) < game.getSorenRandNum(100,'Rev') ) :
						if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Great General spawned outside %s"%(pCity.getName()))
						pRevPlayer.initUnit( iGeneral, revSpawnLoc[0], revSpawnLoc[1], UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )

					if(iScout != -1):
						if( pRevPlayer.canTrain(iScout,False,False) ) :
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Scout spawned outside %s"%(pCity.getName()))
							pRevPlayer.initUnit( iScout, revSpawnLoc[0], revSpawnLoc[1], UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )

#					if( not bIsBarbRev and not bIsJoinWar ) :
#						# Settler if there is sufficient empty land available?
#						if( pCity.area().getNumTiles()/pCity.area().getNumCities() > 25 ) :
#							if(iSettler != -1):
#								if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Settler spawned outside %s"%(pCity.getName()))
#								pRevPlayer.initUnit( iSettler, revSpawnLoc[0], revSpawnLoc[1], UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )

				if(iSpy != -1):
					if( pRevPlayer.canTrain(iSpy,False,False) and pRevPlayer.AI_getNumAIUnits( UnitAITypes.UNITAI_SPY ) < 3 ) :
						if( (pCity.getNumRevolts(pCity.getOwner()) > 1 and revIdx > self.alwaysViolentThreshold) or (pCity.getNumRevolts(pCity.getOwner()) > 2 and revIdx > self.revInstigatorThreshold) ) :
							if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Spy spawned in %s"%(pCity.getName()))
							pSpy = pRevPlayer.initUnit( iSpy, ix, iy, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )
							pSpy.setFortifyTurns(gc.getDefineINT("MAX_FORTIFY_TURNS"))

				# Reveal surrounding countryside
				if( not bGaveMap and len(newUnitList) > 0 ) :
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Giving map")
					pRevPlayer.receiveGoody( gc.getMap().plot(revSpawnLoc[0], revSpawnLoc[1]), iGoodyMap, newUnitList[0] )
					pRevPlayer.receiveGoody( gc.getMap().plot(revSpawnLoc[0], revSpawnLoc[1]), iGoodyMap, newUnitList[0] )

				if( bIsBarbRev ) :
					# Only for determining if revolt has been put down
					pCity.setReinforcementCounter( 5 )
				else :
					iReinforceTurns = self.baseReinforcementTurns - revIdx/self.revInstigatorThreshold - min([localRevIdx,12])/4
					if( pCity.getPopulation() < 7 ) :
						iReinforceTurns += 7 - pCity.getPopulation()
						if( pCity.getPopulation() < 5 ) :
							iReinforceTurns = max([iReinforceTurns,4 - (pCity.getPopulation()/2)])

					minReinfTurns = self.minReinforcementTurns
					if( pPlayer.getCurrentRealEra() < 4 ) :
						minReinfTurns += 2 - pPlayer.getCurrentRealEra()/2
					iReinforceTurns = max([iReinforceTurns,self.minReinforcementTurns])
					iReinforceTurns = min([iReinforceTurns,10])
					if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - %s reinforcement counter set to %d"%(pCity.getName(),iReinforceTurns))
					pCity.setReinforcementCounter( iReinforceTurns + 1 )

#-------------------------------------------------------------------------------------------------
# Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
				pCity.changeRevolutionIndex( int(max([revIdxInc + 15.0*min([localRevIdx,15.0]), 100.0])) )
#-------------------------------------------------------------------------------------------------
# END Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
				pCity.setRevolutionCounter( self.turnsBetweenRevs )
				RevData.updateCityVal(pCity, 'RevolutionTurn', game.getGameTurn() )
				if( not bIsBarbRev ) :
					RevData.setRevolutionPlayer( pCity, pRevPlayer.getID() )


		if( pPlayer.getNumCities() == 0 ) :
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Homeland has no more cities!  Setting founded city to false to keep civil war alive")
			pPlayer.setFoundedFirstCity( False )

		# Release camera from cities
		#CyCamera().ReleaseLockedCamera()

		return

##--- Network syncing functions------------------------------------------

	def onModNetMessage( self, argsList) :
		protocol, data1, data2, data3, data4 = argsList
		if protocol == self.netRevolutionPopupProtocol :
			self.revolutionNetworkPopupHandler(data1, data2, data3)
		if protocol == self.netControlLostPopupProtocol :
			self.controlLostNetworkHandler(data1, data2, data3)

	def revolutionPopupHandler( self, iPlayerID, netUserData, popupReturn ) :
		if self.isLocalHumanPlayer(iPlayerID) :
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Handling local revolution popup")
			buttons = netUserData[0]
			iPlayer = netUserData[1]
#-------------------------------------------------------------------------------------------------
# Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
			if(not self.isLocalHumanPlayer(iPlayer)):
				return
#-------------------------------------------------------------------------------------------------
# END Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
			iRevoltIdx = netUserData[2]
			buttonLabel = buttons[popupReturn.getButtonClicked()]
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Local Button %d pressed, label: %s"%(popupReturn.getButtonClicked(),buttonLabel))
			iButton = -1
			if( buttonLabel == 'accept' )		: iButton = 0
			elif( buttonLabel == 'reject' )	  : iButton = 1
			elif( buttonLabel == 'buyoff' )	  : iButton = 2
			elif( buttonLabel == 'vassal' )	  : iButton = 3
			elif( buttonLabel == 'control' )	 : iButton = 4
			elif( buttonLabel == 'buyelection' ) : iButton = 5
			elif( buttonLabel == 'war' )		 : iButton = 6
			elif( buttonLabel == 'defect' )	  : iButton = 7
			if (iButton >= 0) :
				CyMessageControl().sendModNetMessage(self.netRevolutionPopupProtocol, iPlayer, iButton, iRevoltIdx, 0)

	def controlLostHandler( self, iPlayerID, netUserData, popupReturn ) :
		if self.isLocalHumanPlayer(iPlayerID) :
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("  Revolt - Handling local control lost popup")
			iPlayer = netUserData[0]
#-------------------------------------------------------------------------------------------------
# Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
			if(not self.isLocalHumanPlayer(iPlayer)):
				return
			iNumTurns = netUserData[1]
			iNewLeaderType = netUserData[2]
			# This is sometimes not being called. So I moved it into the pre-dialog bit.
			# This is ok tho since it now happens on NEXT turn not when dialog is okayed.
			#CyMessageControl().sendModNetMessage(self.netControlLostPopupProtocol, iPlayer, iNumTurns, iNewLeaderType, 0)
#-------------------------------------------------------------------------------------------------
# END Lemmy101 RevolutionMP edit
#-------------------------------------------------------------------------------------------------
