# DynamicCivNames
#
# by jdog5000
# Version 1.0
#


from CvPythonExtensions import *
import CvUtil
import PyHelpers
import Popup as PyPopup
# --------- Revolution mod -------------
import RevDefs
import SdToolKitCustom as SDTK
import RevUtils
import LeaderCivNames
import BugCore

# globals
gc = CyGlobalContext()
PyPlayer = PyHelpers.PyPlayer
PyInfo = PyHelpers.PyInfo
game = CyGame()
localText = CyTranslator()
RevOpt = BugCore.game.Revolution

class DynamicCivNames :

	def __init__(self, customEM, RevOpt ) :

		self.RevOpt = RevOpt
		self.customEM = customEM
		
		print "Initializing DynamicCivNames Mod"

		self.LOG_DEBUG = RevOpt.isDynamicNamesDebugMode()
		
		self.bTeamNaming = RevOpt.isTeamNaming()
		self.bLeaveHumanName = RevOpt.isLeaveHumanPlayerName()

		self.customEM.addEventHandler( "BeginPlayerTurn", self.onBeginPlayerTurn )
		self.customEM.addEventHandler( "setPlayerAlive", self.onSetPlayerAlive )
		self.customEM.addEventHandler( "kbdEvent", self.onKbdEvent )
		self.customEM.addEventHandler( "cityAcquired", self.onCityAcquired )
		self.customEM.addEventHandler( 'cityBuilt', self.onCityBuilt )
		self.customEM.addEventHandler( "vassalState", self.onVassalState )
		# lfgr
		self.customEM.addEventHandler( "playerRevolution", self.onPlayerRevolution )
		# lfgr end
		
		LeaderCivNames.setup()
		
		if( not game.isFinalInitialized or game.getGameTurn() == game.getStartTurn() ) :
			for idx in range(0,gc.getMAX_CIV_PLAYERS()) :
				self.onSetPlayerAlive( [idx, gc.getPlayer(idx).isAlive()] )
		
		# lfgr
		# constants
		self.iDespotism =		gc.getInfoTypeForString( "CIVIC_DESPOTISM" )
		self.iCityStates =		gc.getInfoTypeForString( "CIVIC_CITY_STATES" )
		self.iGodKing =			gc.getInfoTypeForString( "CIVIC_GOD_KING" )
		self.iAristocracy =		gc.getInfoTypeForString( "CIVIC_ARISTOCRACY" )
		self.iTheocracy =		gc.getInfoTypeForString( "CIVIC_THEOCRACY" )
		self.iRepublic =		gc.getInfoTypeForString( "CIVIC_REPUBLIC" )
		
		self.iReligion =		gc.getInfoTypeForString( "CIVIC_RELIGION" )
		self.iPacifism =		gc.getInfoTypeForString( "CIVIC_PACIFISM" )
		self.iLiberty =			gc.getInfoTypeForString( "CIVIC_LIBERTY" )
		self.iScholarship = 	gc.getInfoTypeForString( "CIVIC_SCHOLARSHIP" )
		self.iTribalism =		gc.getInfoTypeForString( "CIVIC_TRIBALISM" )
		self.iArete =			gc.getInfoTypeForString( "CIVIC_ARETE" )
		self.iMilitaryState =	gc.getInfoTypeForString( "CIVIC_MILITARY_STATE" )
		self.iConquest =		gc.getInfoTypeForString( "CIVIC_CONQUEST" )
		self.iCrusade =			gc.getInfoTypeForString( "CIVIC_CRUSADE" )
		self.iGuilds =			gc.getInfoTypeForString( "CIVIC_GUILDS" )
		self.iSlavery =			gc.getInfoTypeForString( "CIVIC_SLAVERY" )
		self.iGuardian =		gc.getInfoTypeForString( "CIVIC_GUARDIAN_OF_NATURE" )
		self.iForeignTrade =	gc.getInfoTypeForString( "CIVIC_FOREIGN_TRADE" )
		self.iSacrifice =		gc.getInfoTypeForString( "CIVIC_SACRIFICE_THE_WEAK" )
		self.iDecentralization=	gc.getInfoTypeForString( "CIVIC_DECENTRALIZATION" )
		
		self.iOrder =			CvUtil.findInfoTypeNum( gc.getReligionInfo, gc.getNumReligionInfos(), 'RELIGION_THE_ORDER' )
		self.iVeil =			CvUtil.findInfoTypeNum( gc.getReligionInfo, gc.getNumReligionInfos(), 'RELIGION_THE_ASHEN_VEIL' )
		self.iEmpyrean =		CvUtil.findInfoTypeNum( gc.getReligionInfo, gc.getNumReligionInfos(), 'RELIGION_THE_EMPYREAN' )
		
		self.iGood = 			gc.getInfoTypeForString( "ALIGNMENT_GOOD" )
		self.iEvil = 			gc.getInfoTypeForString( "ALIGNMENT_EVIL" )
		# lfgr end

	def removeEventHandlers( self ) :
		print "Removing event handlers from DynamicCivNames"
		
		self.customEM.removeEventHandler( "BeginPlayerTurn", self.onBeginPlayerTurn )
		self.customEM.removeEventHandler( "setPlayerAlive", self.onSetPlayerAlive )
		self.customEM.removeEventHandler( "kbdEvent", self.onKbdEvent )
		self.customEM.removeEventHandler( "cityAcquired", self.onCityAcquired )
		self.customEM.removeEventHandler( 'cityBuilt', self.onCityBuilt )
		self.customEM.removeEventHandler( "vassalState", self.onVassalState )
		# lfgr
		self.customEM.removeEventHandler( "playerRevolution", self.onPlayerRevolution )
		# lfgr end
	
	def blankHandler( self, playerID, netUserData, popupReturn ) :
		# Dummy handler to take the second event for popup
		return

	def onKbdEvent(self, argsList ):
		'keypress handler'
		eventType,key,mx,my,px,py = argsList

		if ( eventType == RevDefs.EventKeyDown ):
			theKey = int(key)

			# For debug or trial only
			if( theKey == int(InputTypes.KB_U) and self.customEM.bShift and self.customEM.bCtrl ) :
				pass


	def onBeginPlayerTurn( self, argsList ) :
		iGameTurn, iPlayer = argsList

		# Stuff at end of previous players turn
		iPrevPlayer = iPlayer - 1
		while( iPrevPlayer >= 0 and not gc.getPlayer(iPrevPlayer).isAlive() ) :
				iPrevPlayer -= 1

		if( iPrevPlayer < 0 ) :
			iPrevPlayer = gc.getBARBARIAN_PLAYER()

		if( iPrevPlayer >= 0 and iPrevPlayer < gc.getBARBARIAN_PLAYER() ) :
			iPlayer = iPrevPlayer
			pPlayer = gc.getPlayer( iPlayer )

			if( pPlayer.isAlive() and SDTK.sdObjectExists( "Revolution", pPlayer ) ) :
				#CvUtil.pyPrint("  Name - Object exists %d"%(iPlayer))
				prevCivics = SDTK.sdObjectGetVal( "Revolution", pPlayer, 'CivicList' )
				if( not prevCivics == None ) :
					for i in range(0,gc.getNumCivicOptionInfos()):
						if( not prevCivics[i] == pPlayer.getCivics(i) ) :
							self.setNewNameByCivics(iPlayer)
							return
							
				revTurn = SDTK.sdObjectGetVal( "Revolution", pPlayer, 'RevolutionTurn' )
				if( not revTurn == None and game.getGameTurn() - revTurn == 30 and pPlayer.getNumCities() > 0 ) :
					# "Graduate" from rebel name
					self.setNewNameByCivics(iPlayer)
					return
					
			if( pPlayer.isAlive() and SDTK.sdObjectExists( "BarbarianCiv", pPlayer ) ) :
				barbTurn = SDTK.sdObjectGetVal( "BarbarianCiv", pPlayer, 'SpawnTurn' )
				if( not barbTurn == None and game.getGameTurn() - barbTurn == 30 ) :
					# "Graduate" from barb civ name
					self.setNewNameByCivics(iPlayer)
					return
			
			if( pPlayer.isAlive() and not SDTK.sdObjectExists( "BarbarianCiv", pPlayer )) :
				if( 'Tribe' in pPlayer.getCivilizationDescription(0) ) :
					if( pPlayer.getCurrentEra() > 0 or pPlayer.getTotalPopulation() >= 3 ) :
						# Graduate from game start name
						CvUtil.pyPrint("  Name - Graduating from game start name Player %d"%(iPlayer))
						self.setNewNameByCivics(iPlayer)
						return
		
		# lfgr: Alliances
			if( pPlayer.isAlive() and gc.getTeam( pPlayer.getTeam() ).getNumMembers() == 2 ) :
				if( not "Alliance" in pPlayer.getCivilizationDescription(0) ) :
					CvUtil.pyPrint( "  Name - Changing name from Alliance of Player %d"%( iPlayer ) )
					self.setNewNameByCivics( iPlayer )
		# lfgr end

	def onCityAcquired( self, argsList):
		'City Acquired'

		owner,playerType,city,bConquest,bTrade = argsList

		owner = gc.getPlayer( city.getOwner() )
		
	# lfgr
	# old
	#	if( owner.isAlive() and not owner.isBarbarian() and owner.getNumCities() < 5 and owner.getNumMilitaryUnits() > 0 ) :
	#		if( owner.getCapitalCity().getGameTurnAcquired() + 5 < game.getGameTurn() ) :
	#			CvUtil.pyPrint("  Name - Checking for new name by number of cities")
	#			self.setNewNameByCivics( owner.getID() )
		if( owner.isAlive() and not owner.isBarbarian() ) :
			CvUtil.pyPrint("  Name - Checking for new name by number of cities")
			self.setNewNameByCivics( owner.getID() )
	# lfgr end
	
	def onCityBuilt( self, argsList ) :
		
		city = argsList[0]

		owner = gc.getPlayer( city.getOwner() )
		
	# lfgr
	# old
	#	if( owner.isAlive() and not owner.isBarbarian() and owner.getNumCities() < 5 and owner.getNumMilitaryUnits() > 0 ) :
	#		if( owner.getCapitalCity().getGameTurnAcquired() + 5 < game.getGameTurn() ) :
	#			CvUtil.pyPrint("  Name - Checking for new name by number of cities")
	#			self.setNewNameByCivics( owner.getID() )
		if( owner.isAlive() and not owner.isBarbarian() ) :
			CvUtil.pyPrint("  Name - Checking for new name by number of cities")
			self.setNewNameByCivics( owner.getID() )
	# lfgr end
	
	def onVassalState(self, argsList):
		iMaster, iVassal, bVassal = argsList

		if (bVassal):
			#CvUtil.pyPrint("Team %d becomes a Vassal State of Team %d"%(iVassal, iMaster))
			for iPlayer in range(0,gc.getMAX_CIV_PLAYERS()) :
				if( gc.getPlayer(iPlayer).getTeam() == iVassal ) :
					self.setNewNameByCivics( iPlayer )
		else:
			#CvUtil.pyPrint("Team %d revolts and is no longer a Vassal State of Team %d"%(iVassal, iMaster))
			for iPlayer in range(0,gc.getMAX_CIV_PLAYERS()) :
				if( gc.getPlayer(iPlayer).getTeam() == iVassal ) :
					self.setNewNameByCivics( iPlayer )

# lfgr
	def onPlayerRevolution( self, argsList ) :
		ePlayer, iAnarchyTurns, leOldCivics, leNewCivics = argsList
		
		self.setNewNameByCivics( ePlayer )
# lfgr end
	
	def setNewNameByCivics( self, iPlayer ) :
		[newCivDesc, newCivShort, newCivAdj] = self.newNameByCivics( iPlayer )

		if( gc.getPlayer(iPlayer).isHuman() or game.getActivePlayer() == iPlayer ) :
			if( self.bLeaveHumanName ) :
				CvUtil.pyPrint("  Name - Leaving name for human player")
				return
			else :
				#CvUtil.pyPrint("  Name - Changing name for human player!")
				pass

		newDesc  = CvUtil.convertToStr(newCivDesc)
		newShort = CvUtil.convertToStr(newCivShort)
		newAdj   = CvUtil.convertToStr(newCivAdj)
		
		if( not newDesc == gc.getPlayer(iPlayer).getCivilizationDescription(0) ) :
			CyInterface().addMessage(iPlayer, false, gc.getDefineINT("EVENT_MESSAGE_TIME"), "Your civilization is now known as the %s"%(newDesc), None, InterfaceMessageTypes.MESSAGE_TYPE_INFO, None, gc.getInfoTypeForString("COLOR_HIGHLIGHT_TEXT"), -1, -1, False, False)
			if( self.LOG_DEBUG ) :
				CvUtil.pyPrint("  Name - Setting civ name due to civics to %s"%(newCivDesc))
		
		gc.getPlayer(iPlayer).setCivName( newDesc, newShort, newAdj )
		
		return
	
	def onSetPlayerAlive( self, argsList ) :

		iPlayerID = argsList[0]
		bNewValue = argsList[1]
		if( bNewValue == True and iPlayerID < gc.getMAX_CIV_PLAYERS() ) :
			pPlayer = gc.getPlayer( iPlayerID )

			if( pPlayer.isHuman() or game.getActivePlayer() == iPlayerID ) :
				if( self.bLeaveHumanName ) :
					CvUtil.pyPrint("  Name - Leaving name for human player")
					return
			 
			[newCivDesc, newCivShort, newCivAdj] = self.nameForNewPlayer( iPlayerID )
			
			if( self.LOG_DEBUG ) :
				CvUtil.pyPrint("  Name - Setting civ name for new civ to %s"%(newCivDesc))

			newDesc  = CvUtil.convertToStr(newCivDesc)
			newShort = CvUtil.convertToStr(newCivShort)
			newAdj   = CvUtil.convertToStr(newCivAdj)

			# Pass to pPlayer seems to require a conversion to 'ascii'
			pPlayer.setCivName( newDesc, newShort, newAdj )


	def showNewNames( self ) :

		bodStr = 'New names for all civs:\n\n'

		for i in range(0,gc.getMAX_CIV_PLAYERS()) :
			iPlayer = i

			[newName,newShort,newAdj] = self.newNameByCivics(iPlayer)

			bodStr += curDesc + '\t-> ' + newName + '\n'

		popup = PyPopup.PyPopup()
		popup.setBodyString( bodStr )
		popup.launch()


	def nameForNewPlayer( self, iPlayer ) :
		# Assigns a new name to a recently created player from either
		# BarbarianCiv or Revolution components

		pPlayer = gc.getPlayer(iPlayer)
		currentEra = 0
		for i in range(0,gc.getMAX_CIV_PLAYERS()) :
			if( gc.getPlayer(i).getCurrentEra() > currentEra ) :
				currentEra = gc.getPlayer(i).getCurrentEra()

		curDesc = pPlayer.getCivilizationDescription(0)
		curShort = pPlayer.getCivilizationShortDescription(0)
		curAdj = pPlayer.getCivilizationAdjective(0)

		civInfo = gc.getCivilizationInfo(pPlayer.getCivilizationType())
		origDesc  = civInfo.getDescription()
		
		if( not game.isOption(GameOptionTypes.GAMEOPTION_LEAD_ANY_CIV) ) :
			if( pPlayer.getLeaderType() in LeaderCivNames.LeaderCivNames.keys() ) :
				[curDesc,curShort,curAdj] = LeaderCivNames.LeaderCivNames[pPlayer.getLeaderType()]

		newName = curDesc
		if( SDTK.sdObjectExists( "Revolution", pPlayer ) ) :
			revTurn = SDTK.sdObjectGetVal( "Revolution", pPlayer, 'RevolutionTurn' )
		else :
			revTurn = None

		if( SDTK.sdObjectExists( "BarbarianCiv", pPlayer ) ) :
			barbTurn = SDTK.sdObjectGetVal( "BarbarianCiv", pPlayer, 'SpawnTurn' )
		else :
			barbTurn = None

		if( not pPlayer.isAlive() ) :
			newName = localText.getText("TXT_KEY_MOD_DCN_REFUGEES", ())%(curAdj)
		elif( pPlayer.isRebel() ) :
			# To name rebels in Revolution mod
			cityString = SDTK.sdObjectGetVal( "Revolution", pPlayer, 'CapitalName' )
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("Names - player is rebel")
			
			sLiberation = localText.getText("TXT_KEY_MOD_DCN_LIBERATION_FRONT", ()).replace('%s','').strip()
			sGuerillas = localText.getText("TXT_KEY_MOD_DCN_GUERILLAS", ()).replace('%s','').strip()
			sRebels = localText.getText("TXT_KEY_MOD_DCN_REBELS", ()).replace('%s','').strip()
			
			if( sLiberation in curDesc or sGuerillas in curDesc or sRebels in curDesc ) :
				newName = curDesc
			else :
			# lfgr
			# old
			#	if( currentEra > 5 and 30 > game.getSorenRandNum(100,'Rev: Naming')) :
			#		newName = localText.getText("TXT_KEY_MOD_DCN_LIBERATION_FRONT", ())%(curAdj)
			#	elif( currentEra > 4 and 30 > game.getSorenRandNum(100,'Rev: Naming') ) :
			#		newName = localText.getText("TXT_KEY_MOD_DCN_GUERILLAS", ())%(curAdj)
			#	else :
			#		if( not cityString == None and len(cityString) < 10 ) :
			#			try :
			#				if( cityString in curAdj or cityString in curShort ) :
			#					newName = localText.getText("TXT_KEY_MOD_DCN_THE_REBELS_OF", ())%(CvUtil.convertToStr(cityString))
			#				else :
			#					newName = localText.getText("TXT_KEY_MOD_DCN_REBELS_OF", ())%(curAdj,CvUtil.convertToStr(cityString))
			#			except :
			#				newName = localText.getText("TXT_KEY_MOD_DCN_REBELS", ())%(curAdj)
			#		else :
			#			newName = localText.getText("TXT_KEY_MOD_DCN_REBELS", ())%(curAdj)
				if( not cityString == None and len(cityString) < 10 ) :
					try :
						if( cityString in curAdj or cityString in curShort ) :
							newName = localText.getText("TXT_KEY_MOD_DCN_THE_REBELS_OF", ())%(CvUtil.convertToStr(cityString))
						else :
							newName = localText.getText("TXT_KEY_MOD_DCN_REBELS_OF", ())%(curAdj,CvUtil.convertToStr(cityString))
					except :
						newName = localText.getText("TXT_KEY_MOD_DCN_REBELS", ())%(curAdj)
				else :
					newName = localText.getText("TXT_KEY_MOD_DCN_REBELS", ())%(curAdj)
			# lfgr end
	# lfgr commented out
	#	elif( not barbTurn == None and game.getGameTurn() - barbTurn < 20 ) :
	#		# To name BarbarianCiv created civs
	#		numCities = SDTK.sdObjectGetVal( "BarbarianCiv", pPlayer, 'NumCities' )
	#		cityString = SDTK.sdObjectGetVal( "BarbarianCiv", pPlayer, 'CapitalName' )
	#		if( self.LOG_DEBUG ) : CvUtil.pyPrint("Names - player is barbciv")
	#		
	#		if( pPlayer.isMinorCiv() ) :
	#			if( currentEra < 2 ) :
	#				if( 70 - 40*currentEra > game.getSorenRandNum(100,"Naming") ) : 
	#					newName = localText.getText("TXT_KEY_MOD_DCN_TRIBE", ())%(curAdj)
	#				else :
	#					newName = localText.getText("TXT_KEY_MOD_DCN_CITY_STATE", ())%(curAdj)
	#			elif( currentEra < 3 ) :
	#				newName = localText.getText("TXT_KEY_MOD_DCN_CITY_STATE", ())%(curAdj)
	#			else :
	#				newName = localText.getText("TXT_KEY_MOD_DCN_NATION", ())%(curAdj)
	#		elif( currentEra < 4 ) :
	#			# Early era barbs
	#			if( SDTK.sdObjectGetVal( 'BarbarianCiv', pPlayer, 'BarbStyle' ) == 'Military' ) :
	#				if( pPlayer.getNumMilitaryUnits() > 7*numCities ) :
	#					newName = localText.getText("TXT_KEY_MOD_DCN_HORDE", ())%(curAdj)
	#				else :
	#					if( not cityString == None and len(cityString) < 10 ) :
	#						if( cityString in curAdj or cityString in curShort ) :
	#							newName = localText.getText("TXT_KEY_MOD_DCN_THE_WARRIORS_OF", ())%(cityString)
	#						else :
	#							newName = localText.getText("TXT_KEY_MOD_DCN_WARRIORS_OF", ())%(curAdj,cityString)
	#					else :
	#						newName = localText.getText("TXT_KEY_MOD_DCN_WARRIOR_STATE", ())%(curAdj)
	#			else :
	#				if( numCities == 1 ) :
	#					newName = localText.getText("TXT_KEY_MOD_DCN_CITY_STATE", ())%(curAdj)
	#				else :
	#					newName = localText.getText("TXT_KEY_MOD_DCN_EMPIRE", ())%(curAdj)
	#				
	#				if( numCities < 3 ) :
	#					if( not cityString == None and len(cityString) < 10) :
	#						newName += localText.getText("TXT_KEY_MOD_DCN_OF", ()) + cityString
    #
	#		else :
	#			
	#			newName = localText.getText("TXT_KEY_MOD_DCN_EMPIRE", ())%(curAdj)
	#			if( numCities < 3 and not cityString == None and len(cityString) < 10) :
	#				newName += localText.getText("TXT_KEY_MOD_DCN_OF", ()) + cityString
    #
	# lfgr end
		else :
			if( game.getGameTurn() == game.getStartTurn() and game.getCurrentEra() < 1 ) :
				# Name civs at beginning of game
				if( self.LOG_DEBUG ) : CvUtil.pyPrint("Names - Giving game start name")
				newName = localText.getText("TXT_KEY_MOD_DCN_TRIBE", ())%(curAdj)
				return [newName, curShort, curAdj]
			
			if( self.LOG_DEBUG ) : CvUtil.pyPrint("Names - player not of special type, naming by civics")
			return self.newNameByCivics( iPlayer )

		return [newName, curShort, curAdj]


	# lfgr: modified
	def newNameByCivics( self, iPlayer, bVerbose = True, bForceUpdate = False ) :
		# Assigns a new name to a player based on their civics choices
		
		# lfgr debug
		print "DCN - Player %i Picking new name by Civics" % ( iPlayer )
		# lfgr end

		pPlayer = gc.getPlayer(iPlayer)
		capital = pPlayer.getCapitalCity()
		playerEra = pPlayer.getCurrentEra()
		pTeam = gc.getTeam(pPlayer.getTeam())
		
		cityString = None
		if( not capital == None and not capital.isNone() ) :
			try :
				# Silly game to force ascii encoding now
				cityString =  pPlayer.getCivilizationDescription(0)
				cityString += "&" + CvUtil.convertToStr(capital.getName())
				cityString =  cityString.split('&',1)[-1]
			except :
				pass

		curDesc  = pPlayer.getCivilizationDescription(0)
		curShort = pPlayer.getCivilizationShortDescription(0)
		curAdj   = pPlayer.getCivilizationAdjective(0)

		civInfo = gc.getCivilizationInfo(pPlayer.getCivilizationType())
		origDesc  = civInfo.getDescription()
		
		if( not game.isOption(GameOptionTypes.GAMEOPTION_LEAD_ANY_CIV) ) :
			if( pPlayer.getLeaderType() in LeaderCivNames.LeaderCivNames.keys() ) :
				[curDesc,curShort,curAdj] = LeaderCivNames.LeaderCivNames[pPlayer.getLeaderType()]

		newName = curDesc
		if( SDTK.sdObjectExists( "Revolution", pPlayer ) ) :
			revTurn = SDTK.sdObjectGetVal( "Revolution", pPlayer, 'RevolutionTurn' )
		else :
			revTurn = None

		if( SDTK.sdObjectExists( "BarbarianCiv", pPlayer ) ) :
			barbTurn = SDTK.sdObjectGetVal( "BarbarianCiv", pPlayer, 'SpawnTurn' )
		else :
			barbTurn = None

		if( not pPlayer.isAlive() ) :
			if( self.LOG_DEBUG and bVerbose ) : CvUtil.pyPrint("Names - player is not alive")
			newName = localText.getText("TXT_KEY_MOD_DCN_REFUGEES", ())%(curAdj)
			return [newName, curShort, curAdj]

#########################################################################
#			Rebel														#
#########################################################################
		
		if( pPlayer.isRebel() ) :
			# Maintain name of rebels from Revolution Mod
			if( self.LOG_DEBUG and bVerbose ) : CvUtil.pyPrint("Names - player is rebel, keeping current name")
			if( bForceUpdate ) :
				return self.nameForNewPlayer(iPlayer)
			else :
				return [curDesc, curShort, curAdj]

#########################################################################
#			Teams/Permanent Alliances									#
#########################################################################
		
		# Special options for teams and permanent alliances
		if( self.bTeamNaming and pTeam.getNumMembers() > 1 ) : # and pTeam.getPermanentAllianceTradingCount() > 0 ) :
			if( self.LOG_DEBUG and bVerbose ) : CvUtil.pyPrint("Names - Multiple players on team")
			if( self.LOG_DEBUG and bVerbose and pTeam.getPermanentAllianceTradingCount() > 0 ) : CvUtil.pyPrint("Names - Player in Permanent Alliance")
			if( pTeam.getNumMembers() == 2 ) :
				iLeader = pTeam.getLeaderID()
				newName = gc.getPlayer(iLeader).getCivilizationAdjective(0) + "-"
				for idx in range(0,gc.getMAX_CIV_PLAYERS()):
					if( not idx == iLeader and gc.getPlayer(idx).getTeam() == pTeam.getID() ) :
						newName += gc.getPlayer(idx).getCivilizationAdjective(0)
						break
			# lfgr fix
			# old
			#	newName += localText.getText("TXT_KEY_MOD_DCN_ALLIANCE", ())
				newName += " " + localText.getText("TXT_KEY_MOD_DCN_ALLIANCE", ())
			# lfgr end
				return [newName,curShort,curAdj]
			else :
				iLeader = pTeam.getLeaderID()
				newName = gc.getPlayer(iLeader).getCivilizationAdjective(0)[0:4]
				for idx in range(0,gc.getMAX_CIV_PLAYERS()):
					if( not idx == iLeader and gc.getPlayer(idx).getTeam() == pTeam.getID() ) :
						newName += gc.getPlayer(idx).getCivilizationAdjective(0)[0:3]
				newName += localText.getText("TXT_KEY_MOD_DCN_ALLIANCE", ())
				return [newName,curShort,curAdj]

#########################################################################
#			From Civics													#
#########################################################################
		if( self.LOG_DEBUG ) : CvUtil.pyPrint("Names - Start computing name")
		iMxc = 0 # (e.g. "ADJ EMP of CAPITAL" when NumCities <= iMxc)
		sEmp = "Empire"
		sPre = "" # Prefix
		bFof = False # Force "of" (e.g. "PRE EMP of SRT", never "PRE ADJ EMP")
		
		# parameters
		sSrt = curShort
		sAdj = curAdj
		sCpt = cityString
		sLeaderName = pPlayer.getName()
		iNumCities = pPlayer.getNumCities()
		
		bGood = pPlayer.getAlignment() == self.iGood
		bEvil = pPlayer.getAlignment() == self.iEvil
		
		# Traits
		bCharismatic = pPlayer.hasTrait(gc.getInfoTypeForString('TRAIT_CHARISMATIC'))
		bInsane = pPlayer.hasTrait(gc.getInfoTypeForString('TRAIT_INSANE'))
		
		#Civics
		bDespotism = pPlayer.isCivic( self.iDespotism )
		bCityStates = pPlayer.isCivic( self.iCityStates )
		bGodKing = pPlayer.isCivic( self.iGodKing )
		bAristocracy = pPlayer.isCivic( self.iAristocracy )
		bTheocracy = pPlayer.isCivic( self.iTheocracy )
		bRepublic = pPlayer.isCivic( self.iRepublic )
		
		bReligion = pPlayer.isCivic( self.iReligion )
		bPacifism = pPlayer.isCivic( self.iPacifism )
		bLiberty = pPlayer.isCivic( self.iLiberty )
		
		bTribalism = pPlayer.isCivic( self.iTribalism )
		bMilitaryState = pPlayer.isCivic( self.iMilitaryState )
		bConquest = pPlayer.isCivic( self.iConquest )
		bCrusade = pPlayer.isCivic( self.iCrusade )
		bGuilds = pPlayer.isCivic ( self.iGuilds )
		bSlavery = pPlayer.isCivic ( self.iSlavery )
		bArete = pPlayer.isCivic ( self.iArete )
		bGuardian = pPlayer.isCivic ( self.iGuardian )
		bForeignTrade = pPlayer.isCivic ( self.iForeignTrade )
		bSacrifice = pPlayer.isCivic ( self.iSacrifice )
		bDecentralization = pPlayer.isCivic ( self.iDecentralization )
		
		# Misc
		bPuppet = pPlayer.isPuppetState()
		
		bHolyShrine = false
		if pPlayer.getStateReligion() >= 0:
			if pPlayer.hasHolyCity(pPlayer.getStateReligion()):
				bHolyShrine = true
				
		bVeil = pPlayer.getStateReligion() == self.iVeil
		bEmpyrean = pPlayer.getStateReligion() == self.iEmpyrean
		bOrder = pPlayer.getStateReligion() == self.iOrder
		
		sPost = ""
		if( iNumCities == 0 ) :
			sEmp = "Tribe"
			return ["%s %s"%( sAdj, sEmp ), curShort, curAdj]
			
		if bCharismatic:
			sPre = "Beloved"
		elif bInsane:
			sPre = "Deranged"
		
		if( bDespotism ) :
			iMxc = 2
			if( bGood ) :
				sEmp = "Autocracy"
			elif( bEvil ) :
				sEmp = "Tyranny"
			# else: Default
		elif( bCityStates ) :
			if bMilitaryState:
				return ["%s Hegemony"%( sAdj ), curShort, curAdj]
			iMxc = 1
			if( iNumCities == 1 ) :
				sEmp = "City"
			else :
				sEmp = "League"
				sPost = "City States"
			if bSlavery:
				sPost = "Slavers"
			if bForeignTrade:
				sEmp = "Confederation"
			elif bDecentralization:
				sEmp = "Independent Alliance"
		elif( bGodKing ) :
			iMxc = 4
			if bReligion:
				sEmp = "Cult"
			sEmp = "Realm"
		elif( bAristocracy ) :
			iMxc = 3
			sEmp = "Kingdom"
			sPre = "Royal"
		elif( bTheocracy ) :
			iMxc = 2
			sEmp = "Divinity"
		elif( bRepublic ) :
			iMxc = 1
			if( bEvil ) :
				sEmp = "Ochlocracy"
			else :
				sEmp = "Republic"
    
		if( bReligion ) :
			if sPre == "":
				sPre = "Sacred"
			if( bGodKing and iNumCities <= iMxc ) :
				sPre = "Holy"
				sEmp = "See"
			elif( bTheocracy):
				sEmp = "Caliphate"
				sPre = "Holy"
				if ( bVeil ) :
					if bHolyShrine:
						return ["Chosen of Agares", curShort, curAdj]
					sPre = "The Ashen"
				elif( bEmpyrean ) :
					sPre = "Illuminated"
				elif( bOrder ) :
					sPre = "Righteous"
		elif( bPacifism ) :
			if sPre == "":
				sPre = "Benevolent"
			if( bCityStates and iNumCities > iMxc ) :
				sEmp = "League of Peace"
				bFof = True
		elif( bLiberty ) :
			sPre = "Free"
			if( bAristocracy ) :
				sEmp = "Imperial Estates"
		elif( bTribalism ) :
			sPre = "Tribal"
			if( bDespotism ) :
				sEmp = "Chiefdom"
				
		if bCrusade:
			sPre = "Righteous"
		elif bGuilds:
			sPre = "Technocratic"
			
		if bMilitaryState:
			if bConquest:
				if bAristocracy:
					bEmp = "Dynasty"
				else:
					sEmp = "Junta"
					bFof = true
			elif bRepublic:
				sEmp = "Regime"
    
		if bPuppet:
			sEmp = "Satrapy"
			if bMilitaryState:
				sEmp = "Prefecture"
			if bAristocracy:
				sEmp = "Province"
			if bReligion or bTheocracy:
				sEmp = "Diocese"
			bFof = true
    
		if bArete:
			sPre = "Golden"
		elif bGuardian:
			sEmp = "Fellowship"
		elif bSacrifice:
			sPre = "Demonic"
			
		if( sPre != "" ) :
			sPre += " "

		if( sPost != "" ) :
			return ["%s %s of %s %s"%(sPre, sEmp, sAdj, sPost), curShort, curAdj]
		
		if bGodKing:
			return ["%s%s of %s"%( sPre, sEmp, sLeaderName ), curShort, curAdj]
		elif( iNumCities <= iMxc ) :
			return ["%s%s of %s"%( sPre, sEmp, sCpt ), curShort, curAdj]
		elif( bFof or 50 > game.getSorenRandNum( 100, 'Rev: Naming' ) ) :
			return ["%s%s of the %s"%( sPre, sEmp, sSrt ), curShort, curAdj]
		else :
			return ["%s%s %s"%( sPre, sAdj, sEmp ), curShort, curAdj]
# lfgr end
	
	def resetName( self, iPlayer, bVerbose = True ) :
		
		pPlayer = gc.getPlayer(iPlayer)
		
		civInfo = gc.getCivilizationInfo(pPlayer.getCivilizationType())
		origDesc  = civInfo.getDescription()
		origShort = civInfo.getShortDescription(0)
		origAdj   = civInfo.getAdjective(0)

		if( not game.isOption(GameOptionTypes.GAMEOPTION_LEAD_ANY_CIV) ) :
			if( not self.bLeaveHumanName or not (pPlayer.isHuman() or game.getActivePlayer() == iPlayer) ) :
				if( pPlayer.getLeaderType() in LeaderCivNames.LeaderCivNames.keys() ) :
					[origDesc,origShort,origAdj] = LeaderCivNames.LeaderCivNames[pPlayer.getLeaderType()]

		newDesc  = CvUtil.convertToStr(origDesc)
		newShort = CvUtil.convertToStr(origShort)
		newAdj   = CvUtil.convertToStr(origAdj)
		
		if( self.LOG_DEBUG ) :
			CvUtil.pyPrint("  Name - Re-setting civ name for player %d to %s"%(iPlayer,newDesc))
		
		gc.getPlayer(iPlayer).setCivName( newDesc, newShort, newAdj )
