# DynamicCivNames
#
# by jdog5000
# Version 1.0
#

# lfgr 10/2019:
# * Refactored name generation out of main class
# * Removed LeaderCivNames-related code


from CvPythonExtensions import *
import CvUtil
import PyHelpers
import Popup as PyPopup
# --------- Revolution mod -------------
import SdToolKitCustom as SDTK
import BugCore
import RevInstances
import random # Only use seeded with getSorenRandNum()!

# globals
gc = CyGlobalContext()
PyPlayer = PyHelpers.PyPlayer
PyInfo = PyHelpers.PyInfo
game = CyGame()
localText = CyTranslator()
RevOpt = BugCore.game.Revolution


# Not built-in in python 2.4
def any( it ) :
	for x in it :
		if x :
			return True
	return False


# DescGenerator Helper functions
def getMainCityName( ePlayer ) :
	"""
	Get the name of the player's capital, or, if not available, of a city after which they could be named.
	"""
	pPlayer = gc.getPlayer( ePlayer )
	
	if pPlayer.isRebel() :
		return SDTK.sdObjectGetVal( "Revolution", pPlayer, 'CapitalName' )
	
	pMainCity = None
	
	if pMainCity is None :
		pMainCity = pPlayer.getCapitalCity()
	
	if pMainCity is None :
		pMainCity, _ = pPlayer.firstCity( False )
	
	if pMainCity is not None and not pMainCity.isNone() :
		# LFGR_TODO: ?
		try :
			# Silly game to force ascii encoding now
			sCpt = pPlayer.getCivilizationDescription( 0 )
			sCpt += "&" + CvUtil.convertToStr( pMainCity.getName() )
			sCpt = sCpt.split( '&', 1 )[-1]
			return sCpt
		except UnicodeDecodeError :
			pass
	return None


def setOption(option, value):
	"""
	Function called when an option is changed that requires recomputing names
	"""
	if RevInstances.DynamicCivNamesInst is not None :
		if not game.isGameMultiPlayer() : # GUI-triggered updates would cause OOS
			RevInstances.DynamicCivNamesInst.recalcAll()


class DescGenerator :
	"""
	Class responsible for generating names
	"""
	def __init__( self, LOG_DEBUG ) :
		self.LOG_DEBUG = LOG_DEBUG
		
		# Civics
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
		
		# Religions
		self.iOrder =			CvUtil.findInfoTypeNum( gc.getReligionInfo, gc.getNumReligionInfos(), 'RELIGION_THE_ORDER' )
		self.iVeil =			CvUtil.findInfoTypeNum( gc.getReligionInfo, gc.getNumReligionInfos(), 'RELIGION_THE_ASHEN_VEIL' )
		self.iEmpyrean =		CvUtil.findInfoTypeNum( gc.getReligionInfo, gc.getNumReligionInfos(), 'RELIGION_THE_EMPYREAN' )
		self.iKilmorph =		CvUtil.findInfoTypeNum( gc.getReligionInfo, gc.getNumReligionInfos(), 'RELIGION_RUNES_OF_KILMORPH' )
		
		self.iGood = 			gc.getInfoTypeForString( "ALIGNMENT_GOOD" )
		self.iEvil = 			gc.getInfoTypeForString( "ALIGNMENT_EVIL" )
		
		# Civs
		self.iAmurites = CvUtil.findCivilizationNum( 'CIVILIZATION_AMURITES' )
		self.iBannor = CvUtil.findCivilizationNum( 'CIVILIZATION_BANNOR' )
		self.iCalabim = CvUtil.findCivilizationNum( 'CIVILIZATION_CALABIM' )
		self.iClan = CvUtil.findCivilizationNum( 'CIVILIZATION_CLAN_OF_EMBERS' )
		self.iDoviello = CvUtil.findCivilizationNum( 'CIVILIZATION_DOVIELLO' )
		self.iElohim = CvUtil.findCivilizationNum( 'CIVILIZATION_ELOHIM' )
		self.iGrigori = CvUtil.findCivilizationNum( 'CIVILIZATION_GRIGORI' )
		self.iHippus = CvUtil.findCivilizationNum( 'CIVILIZATION_HIPPUS' )
		self.iIllians = CvUtil.findCivilizationNum( 'CIVILIZATION_ILLIANS' )
		self.iKhazad = CvUtil.findCivilizationNum( 'CIVILIZATION_KHAZAD' )
		self.iKuriotates = CvUtil.findCivilizationNum( 'CIVILIZATION_KURIOTATES' )
		self.iLanun = CvUtil.findCivilizationNum( 'CIVILIZATION_LANUN' )
		self.iLjosalfar = CvUtil.findCivilizationNum( 'CIVILIZATION_LJOSALFAR' )
		self.iLuchuirp = CvUtil.findCivilizationNum( 'CIVILIZATION_LUCHUIRP' )
		self.iMalakim = CvUtil.findCivilizationNum( 'CIVILIZATION_MALAKIM' )
		self.iSheaim = CvUtil.findCivilizationNum( 'CIVILIZATION_SHEAIM' )
		self.iSidar = CvUtil.findCivilizationNum( 'CIVILIZATION_SIDAR' )
		self.iSvartalfar = CvUtil.findCivilizationNum( 'CIVILIZATION_SVARTALFAR' )
	
	def getAdjKeyForNames( self, pPlayer ) :
		"""
		Returns the adjective of the player as used to generate names.
		"""
		if pPlayer.getCivilizationType() == self.iClan :
			return "TXT_KEY_DCN_ORCISH_ADJECTIVE"
		else :
			return CvUtil.convertToStr( pPlayer.getCivilizationAdjectiveKey() )
	
	def generateDescs( self, ePlayer, iCreativityLevel ) :
		"""
		Main function to generate civ descs
		@param ePlayer: Generate names for this player
		@param iCreativityLevel: How random the generated names are:
			0: Disabled - Not allowed when calling this function
			1: Minimal - Only apply for multiple players with the same civ
			2: Medium - Small selection of names, but should always feel appropriate
			3: High - Names are build from components selected by e.g. civics and religion, most interesting,
				but also most crazy names.
		@return Iterator of new desc tuples
		"""
		assert 1 <= iCreativityLevel <= 3
		
		pPlayer = gc.getPlayer( ePlayer )
		
		if self.LOG_DEBUG :
			CvUtil.pyPrint( "DCN - Generating descs for player %s with creativity level %d" % ( pPlayer.getName(), iCreativityLevel ) )
		
		tArgs = self.makeLfgrArgs( ePlayer )
		
		if not pPlayer.isAlive() :
			if self.LOG_DEBUG : CvUtil.pyPrint( "  DCN - player is dead" )
			yield localText.getText("TXT_KEY_DCN_REFUGEES", tArgs )
		elif pPlayer.isRebel() :
			if self.LOG_DEBUG : CvUtil.pyPrint( "  DCN - player is rebel" )
			
			# Try to convert city string if it is present and has reasonable size
			"""convCityStr = None
			if cityString is not None and len( cityString ) < 10 :
				try :
					convCityStr = CvUtil.convertToStr( cityString )
				except UnicodeDecodeError :
					pass"""
			sShort, sAdj, sCapital, _ = tArgs
			
			if sCapital :
				if sCapital in sAdj or sCapital in sShort :
					# Rebels of [city]
					yield localText.getText( "TXT_KEY_DCN_THE_REBELS_OF", tArgs )
				else :
					# [adj] rebels of [city]
					yield localText.getText( "TXT_KEY_DCN_REBELS_OF", tArgs )
			else :
				yield localText.getText( "TXT_KEY_DCN_REBELS", tArgs )
		elif iCreativityLevel >= 3 and pPlayer.getNumCities() == 0 :
			# Alive, not rebels, no cities -- most likely at the start of the game
			if self.LOG_DEBUG : CvUtil.pyPrint( "  DCN - Giving game start name" )
			yield localText.getText( "TXT_KEY_DCN_TRIBE", tArgs )
		else :
			if RevOpt.isTeamNaming() :
				# Team naming
				sTeamDesc = self.generateTeamDesc( ePlayer )
				if sTeamDesc is not None :
					if self.LOG_DEBUG : CvUtil.pyPrint( "  DCN - Naming by team" )
					yield sTeamDesc
					return
			
			if self.LOG_DEBUG : CvUtil.pyPrint( "  DCN - player not of special type" )
			if iCreativityLevel <= 2 :
				for sDesc in self.generateDescsLfgr( ePlayer, iCreativityLevel, tArgs ) :
					yield sDesc
			else :
				for sDesc in self.generateDescsTholal( ePlayer ) :
					yield sDesc
	
	def generateTeamDesc( self, ePlayer ) :
		"""
		Function to generate special names for players in a multi-player team
		"""
		pPlayer = gc.getPlayer( ePlayer )
		
		pTeam = gc.getTeam( pPlayer.getTeam() )
		if pTeam.getNumMembers() > 1 :  # and pTeam.getPermanentAllianceTradingCount() > 0 ) :
			if self.LOG_DEBUG : CvUtil.pyPrint( "DCN - Multiple players on team" )
			
			# LFGR_TODO: Translate, prevent too long names
			# LFGR_TODO: Remove? Different order is weird, same names are dumb
			eLeader = pTeam.getLeaderID()
			sNewName = gc.getPlayer( eLeader ).getCivilizationAdjective( 0 )
			for iLoopPlayer in range( 0, gc.getMAX_CIV_PLAYERS() ) :
				if iLoopPlayer != eLeader and gc.getPlayer( iLoopPlayer ).getTeam() == pTeam.getID() :
					sLoopAdj = gc.getPlayer( iLoopPlayer ).getCivilizationAdjective( 0 )
					if not sLoopAdj in sNewName :  # prevent Luchuirp-Luchuirp Alliance
						sNewName += "-" + sLoopAdj
			
			sNewName += " " + localText.getText( "TXT_KEY_DCN_ALLIANCE", () )
			return sNewName
		else :
			return None
	
	def makeLfgrArgs( self, ePlayer ) :
		"""
		Make standard arguments for DCN formatting strings: (short desc, adjective, capital name, leader name)
		"""
		pPlayer = gc.getPlayer( ePlayer )
		
		sShort = pPlayer.getCivilizationShortDescriptionKey()
		sAdj = self.getAdjKeyForNames( pPlayer )
		sCapital = getMainCityName( ePlayer )
		sLeaderName = pPlayer.getName()
		
		if self.LOG_DEBUG : CvUtil.pyPrint( "  DCN - Arguments: %s, %s, %s, %s" % (sShort, sAdj, sCapital, sLeaderName) )
		
		return sShort, sAdj, sCapital, sLeaderName
	
	def generateDescsLfgr( self, ePlayer, iCreativityLevel, tArgs ) :
		"""
		Generate descriptions with creativity levels 1 (minimal) and 2 (medium).
		"""
		assert iCreativityLevel in [1,2]
		pPlayer = gc.getPlayer( ePlayer )
		
		eCiv = pPlayer.getCivilizationType()
		bVassal = gc.getTeam( pPlayer.getTeam() ).isAVassal()
		
		# Is there another non-rebel (and, if iCreativityLevel == 2, non-vassal) player with the same civ?
		# TODO: We need to update names if leaders cease to be rebels
		bDuplicateCiv = False
		for eLoopPlayer in range( gc.getMAX_CIV_PLAYERS() ) :
			pLoopPlayer = gc.getPlayer( eLoopPlayer )
			if eLoopPlayer != ePlayer and pLoopPlayer.getCivilizationType() == eCiv \
					and pLoopPlayer.isAlive() and not pLoopPlayer.isRebel() : # Only consider alive non-rebels
				if iCreativityLevel == 1 or ( bVassal or not gc.getTeam( pLoopPlayer.getTeam() ).isAVassal() ) :
					# Creativity levels doesn't consider other vassals as duplicates if we are not a vassal.
					bDuplicateCiv = True
					break
		
		if bDuplicateCiv and self.LOG_DEBUG : CvUtil.pyPrint( "  DCN - Duplicate civ" )
		
		bFoundSomething = False
		
		if iCreativityLevel == 2 and tArgs[2] is not None :
			for sDescKey in self.generateDescKeysLfgr( ePlayer, bDuplicateCiv, iCreativityLevel ) :
				bFoundSomething = True
				yield localText.getText( sDescKey, tArgs )
		else :
			# Couldn't get capital name
			# Note that this is the case if there are no cities yet
			if self.LOG_DEBUG : CvUtil.pyPrint( "  DCN - Low creativity or couldn't get capital name, don't generate advanced names" )
		
		if not bFoundSomething :
			yield self.makeDefaultDescLfgr( ePlayer, bDuplicateCiv, iCreativityLevel, tArgs )
	
	def makeDefaultDescLfgr( self, ePlayer, bDuplicateCiv, iCreativityLevel, tArgs ) :
		"""
		Create default descriptions for creativity levels 1 and 2. Used if no other descriptions were generated.
		"""
		if self.LOG_DEBUG : CvUtil.pyPrint( "  DCN - No better names generated, generating default names" )
		
		# Remove possible None capital messing up localText.getText
		sShort, sAdj, sCapital, sLeaderName = tArgs
		
		pPlayer = gc.getPlayer( ePlayer )
		eCiv = pPlayer.getCivilizationType()
		if bDuplicateCiv :
			if iCreativityLevel == 2 and gc.getTeam( pPlayer.getTeam() ).isAVassal() and sCapital is not None :
				return localText.getText( "TXT_KEY_DCN_MULTI_VASSAL_DEFAULT", ( sShort, sAdj, sCapital, sLeaderName ) ) # May use capital
			else :
				return localText.getText( "TXT_KEY_DCN_MULTI_DEFAULT", ( sShort, sAdj, "INVALID", sLeaderName ) ) # May not use capital
		else :
			if RevOpt.isEmpireDefaultName() :
				return localText.getText( "TXT_KEY_DCN_DEFAULT", ( sShort, sAdj, "INVALID", sLeaderName ) ) # May not use capital
			else :
				return gc.getCivilizationInfo( eCiv ).getDescription()
	
	def generateDescKeysLfgr( self, ePlayer, bDuplicateCiv, iCreativityLevel ) :
		"""
		Generate description keys. These will be augmented with standard argument as described in makeLfgrArgs().
		"""
		pPlayer = gc.getPlayer( ePlayer )
		
		eCiv = pPlayer.getCivilizationType()
		
		# Civilizations
		bClan = eCiv == self.iClan
		bGrigori = eCiv == self.iGrigori
		bLanun = eCiv == self.iLanun
		
		# Civics
		bDespotism = pPlayer.isCivic( self.iDespotism )
		bCityStates = pPlayer.isCivic( self.iCityStates )
		bRepublic = pPlayer.isCivic( self.iRepublic )
		
		# Civic categories
		bKingdom = self.isLfgrKingdom( pPlayer )
		
		# Other stuff
		iNumCities = pPlayer.getNumCities()
		bSmall = iNumCities <= gc.getWorldInfo(gc.getMap().getWorldSize()).getTargetNumCities() / 2 / 100
		eTeam = pPlayer.getTeam()
		
		# Master stuff
		eMasterTeam = None
		for eLoopPlayer in range( gc.getMAX_CIV_PLAYERS() ) :
			pLoopPlayer = gc.getPlayer( eLoopPlayer )
			if gc.getTeam( eTeam ).isVassal( pLoopPlayer.getTeam() ) :
				eMasterTeam = pLoopPlayer.getTeam()
				break
		lpMasterPlayers = []
		for eLoopPlayer in range( gc.getMAX_CIV_PLAYERS() ) :
			pLoopPlayer = gc.getPlayer( eLoopPlayer )
			if pLoopPlayer.getTeam() == eMasterTeam :
				lpMasterPlayers.append( pLoopPlayer )
		
		if not bDuplicateCiv :
			# Implicit: iCreativityLevel == 2
			if bCityStates and (bGrigori or bLanun) :
				# Grigori and Lanun are a canonically a loose federation of city states
				yield "TXT_KEY_DCN_CITY_STATES"
		else :
			# Duplicate civ handling
			# We always assume there are non duplicate leaders # TODO: Ensure that via random naming
			if eMasterTeam is None :
				# Not a vassal
				if iCreativityLevel == 2 :
					if iNumCities == 1 and (bDespotism or bCityStates or bRepublic) :
						yield "TXT_KEY_DCN_MULTI_CITY"
						if bRepublic :
							yield "TXT_KEY_DCN_MULTI_FREE_CITY"
					elif bSmall and bKingdom :
						yield "TXT_KEY_DCN_MULTI_KINGDOM"
			else :
				# Vassal naming
				if iCreativityLevel == 2 :
					if bClan :
						yield "TXT_KEY_DCN_MULTI_VASSAL_CLAN"
					
					if any( pMasterPlayer.getCivilizationType() == self.iCalabim for pMasterPlayer in lpMasterPlayers ) :
						yield "TXT_KEY_DCN_MULTI_VASSAL_CALABIM_MASTER"
					
					# These lists each contain civs that are related enough that if one is a vassal of another, they
					#   call the vassal things like "duchy"
					lleRelatedOrganizedCivLists = [
						[self.iAmurites, self.iBannor, self.iElohim, self.iGrigori, self.iHippus, self.iKuriotates, self.iMalakim],
						[self.iKhazad, self.iLuchuirp]
					]
					
					bRelated = False
					for leCivList in lleRelatedOrganizedCivLists :
						if any( pMaster.getCivilizationType() in leCivList for pMaster in lpMasterPlayers ) and eCiv in leCivList :
							if self.LOG_DEBUG :
								CvUtil.pyPrint( "  DCN - %s vassal related to at least one master:"
										% gc.getCivilizationInfo( eCiv ).getDescription() )
							bRelated = True
							break
					
					if bRelated :
						if any( pMaster.isCivic( self.iTheocracy ) for pMaster in lpMasterPlayers ) :
							yield "TXT_KEY_DCN_MULTI_VASSAL_MASTER_RELATED_THEOCRACY"
						if any( self.isLfgrKingdom( pMaster ) for pMaster in lpMasterPlayers ) :
							if bSmall :
								yield "TXT_KEY_DCN_MULTI_VASSAL_SMALL_MASTER_RELATED_KINGDOM"
							else :
								yield "TXT_KEY_DCN_MULTI_VASSAL_MASTER_RELATED_KINGDOM"
	
	def isLfgrKingdom( self, pPlayer ) :
		return ( pPlayer.isCivic( self.iDespotism ) or pPlayer.isCivic( self.iGodKing ) or pPlayer.isCivic( self.iAristocracy ) ) and not pPlayer.getCivilizationType() == self.iGrigori
	
	def generateDescsTholal( self, ePlayer ) :
		pPlayer = gc.getPlayer( ePlayer )
		
		### Regular naming by civics
		
		if self.LOG_DEBUG : CvUtil.pyPrint("DCN - Start computing name")
		
		# Compute Parameters
		pCapital = pPlayer.getCapitalCity()
		sCpt = getMainCityName( ePlayer )
		
		eCiv = pPlayer.getCivilizationType()
		pCiv = gc.getCivilizationInfo( eCiv )
		
		sLeaderName = pPlayer.getName()
		iNumCities = pPlayer.getNumCities()
		
		# Era
		bAncient = pPlayer.getCurrentRealEra() == 0
		
		# Alignment
		bGood = pPlayer.getAlignment() == self.iGood
		bEvil = pPlayer.getAlignment() == self.iEvil
		
		# Traits
		bCharismatic = pPlayer.hasTrait( gc.getInfoTypeForString( 'TRAIT_CHARISMATIC' ) )
		bInsane = pPlayer.hasTrait( gc.getInfoTypeForString( 'TRAIT_INSANE' ) )
		
		# Civics
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
		bGuilds = pPlayer.isCivic( self.iGuilds )
		bSlavery = pPlayer.isCivic( self.iSlavery )
		bArete = pPlayer.isCivic( self.iArete )
		bGuardian = pPlayer.isCivic( self.iGuardian )
		bForeignTrade = pPlayer.isCivic( self.iForeignTrade )
		bSacrifice = pPlayer.isCivic( self.iSacrifice )
		bDecentralization = pPlayer.isCivic( self.iDecentralization )
		
		# Misc
		bPuppet = pPlayer.isPuppetState()
		
		bHolyShrine = false
		if pPlayer.getStateReligion() >= 0 :
			if pPlayer.hasHolyCity( pPlayer.getStateReligion() ) :
				bHolyShrine = true
		
		# Religion
		bVeil = pPlayer.getStateReligion() == self.iVeil
		bEmpyrean = pPlayer.getStateReligion() == self.iEmpyrean
		bOrder = pPlayer.getStateReligion() == self.iOrder
		bKilmorph = pPlayer.getStateReligion() == self.iKilmorph
		
		# Civ
		bCalabim = eCiv == self.iCalabim
		bClan = eCiv == self.iClan
		
		# Components to be set in the following
		sEmp = None
		sAltEmp = None
		sPre = ""  # Prefix
		sAltPre = ""
		sPost = ""
	
		iCityStateThreshold = 0  # (e.g. "ADJ EMP of CAPITAL" when NumCities <= iMaxCities)
		bBlockOf = False  # Block "of" (e.g. never "PRE EMP of SRT", but "PRE ADJ EMP")
		bForceOf = False  # Force "of" (e.g. never "PRE ADJ EMP", but "PRE EMP of SRT")
		
		if iNumCities == 1 :
			sEmp = "Lands"
			sAltEmp = "Stronghold"
		else :
			sEmp = "Empire"
			sAltEmp = "Territories"
		
		# Long section of setting components
		if bCharismatic :
			sPre = "Beloved"
		elif bInsane :
			sPre = "Deranged"
		
		if bDespotism :
			iCityStateThreshold = 2
			if bClan :
				sEmp = "Clan"
				sAltEmp = "Clan"
			elif bAncient :
				sEmp = "Chiefdom"
				sAltEmp = "Empire"
			else :
				sAltEmp = "Chiefdom"
				if bGood :
					sEmp = "Autocracy"
				elif bEvil :
					sEmp = "Tyranny"
				# else: Default
		elif bCityStates :
			iCityStateThreshold = 1
			if bMilitaryState :
				sEmp = "Hegemony"
				sAltEmp = "Hegemony"
			if iNumCities == 1 :
				sEmp = "City"
				sAltEmp = "City State"
			else :
				sEmp = "Federation"
				sAltEmp = "League"
				sPost = "City States"
			if bSlavery :
				sPost = "Slavers"
			if bForeignTrade :
				sPre = ""
				sEmp = "Confederation"
			elif bDecentralization :
				if iNumCities == 1 :
					sEmp = "Independent State"
				else :
					sEmp = "Independent Alliance"
		elif bGodKing :
			iCityStateThreshold = 4
			if bReligion :
				sEmp = "Cult"
				sAltEmp = "Followers"
				bForceOf = True
			elif bPacifism :
				sPre = "Benevolent"
			else :
				sEmp = "Monarchy"
				sAltEmp = "Sovereignty"
			if bClan :
				sEmp = "Clan"
				sAltEmp = "Clan"
		elif bAristocracy :
			iCityStateThreshold = 3
			if bCalabim :
				sEmp = "Principalities"
				sAltEmp = "Kingdom"
			if bGuilds :
				sEmp = "Imperium"
			elif bSlavery :
				sEmp = "Dynasty"
				bForceOf = True
			elif bMilitaryState :
				sEmp = "Monarchy"
			else :
				sEmp = "Kingdom"
				sAltEmp = "Realm"
			if bConquest :
				sPre = "Imperial"
				sAltPre = "Majestic"
			elif bArete :
				sEmp = "Plutocracy"
			else :
				sPre = "Royal"
				sAltPre = "Noble"
		elif bTheocracy :
			iCityStateThreshold = 2
			sPre = "Divine"
			sAltPre = "Chosen"
			#sEmp = "Divinity"
		elif bRepublic :
			iCityStateThreshold = 1
			sAltPre = "Democratic"
			if bEvil :
				sEmp = "Ochlocracy"
				sAltEmp = "Republic"
			else :
				sEmp = "Republic"
		
		if bReligion :
			if sPre == "" :
				sPre = "Sacred"
				sAltPre = "Holy"
			if bGodKing and iNumCities <= iCityStateThreshold :
				sPre = "Sacred"
				sEmp = "See"
			elif bTheocracy :
				sEmp = "Caliphate"
				sAltPre = "Theocratic"
				if bVeil :
					if bHolyShrine :
						yield "Chosen of Agares"
						return # That's the name
					sPre = "The Ashen"
				elif bEmpyrean :
					sPre = "Illuminated"
				elif bOrder :
					sPre = "Righteous"
		elif bPacifism :
			if bCityStates and iNumCities > iCityStateThreshold :
				sEmp = "Commune"
				bForceOf = True
		elif bLiberty :
			sPre = "Free"
			sAltPre = "Liberated"
			if bAristocracy :
				sEmp = "Imperial Estates"
				bForceOf = True
		elif bTribalism and bDespotism :
			sPre = "Tribal"
			# even if era not ancient
			sAltEmp = "Chiefdom"
		
		if bCrusade :
			sPre = "Righteous"
			sAltPre = "Righteous"
		elif bGuilds :
			sPre = "Technocratic"
		
		if bMilitaryState :
			if bConquest :
				if bAristocracy :
					sEmp = "Dynasty"
				else :
					sEmp = "Junta"
					bForceOf = true
			elif bRepublic :
				sEmp = "Regime"
		
		if bPuppet :
			iCityStateThreshold = 5  # TODO: puppet states have no capital
			sPre = ""
			sAltPre = ""
			sEmp = "Satrapy"
			sAltEmp = "Satrapy"
			if bMilitaryState :
				sEmp = "Prefecture"
				sAltEmp = "Prefecture"
			if bAristocracy :
				sEmp = "Province"
				sAltEmp = "Province"
			if bReligion or bTheocracy :
				sEmp = "Diocese"
				sAltEmp = "Diocese"
		
		if pCapital != -1 :
			pCapitalPlot = pCapital.plot()
			pCapitalLatitude = pCapitalPlot.getLatitude()
			if pCapitalLatitude > 50 :
				iMapHeight = CyMap().getGridHeight()
				if pCapitalPlot.getY() < (iMapHeight / 2) :
					sPre = "Southern"
				else :
					sPre = "Northern"
		
		if bArete and bHolyShrine :
			sPre = "Golden"
			sAltPre = "Golden"
		elif bGuardian :
			sEmp = "Fellowship"
			sAltEmp = "Fellowship"
		elif bSacrifice :
			sPre = "Demonic"
			sAltPre = "Demonic"
		
		# Now put together the names
		
		sAdj = localText.getText( self.getAdjKeyForNames( pPlayer ), () )
		if bClan :
			sTheSrt = "Embers"
		else :
			sTheSrt = "the " + pPlayer.getCivilizationShortDescription( 0 )
		
		if sPost != "" :
			yield "%s %s of %s %s" % (sPre, sEmp, sAdj, sPost)
			return
		
		# Add space to prefix, if it exsits
		if sPre != "" :
			sPre += " "
		if sAltPre != "" :
			sAltPre += " "
		
		# Some final parameters
		bCityAllowed = iNumCities <= iCityStateThreshold
		if not bGodKing :
			sLeaderName = None
		
		# Try all combindations of (sPre, sAltPre) and sEmp, sAltEmp)
		for sDesc in self.genForms( sPre, sAdj, sEmp, sTheSrt, sLeaderName, sCpt, bBlockOf, bForceOf, bCityAllowed ) :
			yield sDesc
		if sAltEmp != sEmp :
			for sDesc in self.genForms( sPre, sAdj, sAltEmp, sTheSrt, sLeaderName, sCpt, bBlockOf, bForceOf,
					bCityAllowed ) :
				yield sDesc
		if sAltPre != sPre :
			for sDesc in self.genForms( sAltPre, sAdj, sEmp, sTheSrt, sLeaderName, sCpt, bBlockOf, bForceOf,
					bCityAllowed ) :
				yield sDesc
		if sAltEmp != sEmp and sAltPre != sPre :
			for sDesc in self.genForms( sAltPre, sAdj, sAltEmp, sTheSrt, sLeaderName, sCpt, bBlockOf, bForceOf,
					bCityAllowed ) :
				yield sDesc
	
	def genForms( self, sPre, sAdj, sEmp, sTheSrt, sLeaderName, sCpt, bBlockOf, bForceOf, bCityAllowed ):
		if not bBlockOf and bCityAllowed and sEmp != "Clan" and sCpt is not None :
			yield "%s%s of %s" % (sPre, sEmp, sCpt) # Sacred Empire of Golden Lane
		
		if not bForceOf and sEmp != "Clan" :
			yield "%s%s %s" % (sPre, sAdj, sEmp)  # Sacred Malakim Empire
		
		if not bBlockOf :
			yield "%s%s of %s" % (sPre, sEmp, sTheSrt)  # Sacred Empire of the Malakim
		
		if sLeaderName is not None :
			yield "%s%s of %s" % (sPre, sEmp, sLeaderName)  # Holy Cult of Tholal


### Helper functions

def isUnusedDesc( iPlayer, sDesc ) :
	for iLoopPlayer in range( gc.getMAX_PLAYERS() ) :
		if gc.getPlayer( iLoopPlayer ).isEverAlive() :
			if iLoopPlayer != iPlayer :
				if gc.getPlayer( iLoopPlayer ).getCivilizationDescription( 0 ) == sDesc :
					return False
	return True


class DynamicCivNames :
	def __init__(self, customEM, RevOpt ) :

		self.RevOpt = RevOpt
		self.customEM = customEM
		
		CvUtil.pyPrint( "  DCN - Initializing DynamicCivNames Mod" )

		self.LOG_DEBUG = RevOpt.isDynamicNamesDebugMode()

		self.customEM.addEventHandler( "BeginPlayerTurn", self.onBeginPlayerTurn )
		self.customEM.addEventHandler( "setPlayerAlive", self.onSetPlayerAlive )
		#self.customEM.addEventHandler( "kbdEvent", self.onKbdEvent )
		self.customEM.addEventHandler( "cityAcquired", self.onCityAcquired )
		self.customEM.addEventHandler( 'cityBuilt', self.onCityBuilt )
		self.customEM.addEventHandler( "vassalState", self.onVassalState )
		self.customEM.addEventHandler( "playerRevolution", self.onPlayerRevolution ) # lfgr
		
		self.descGen = DescGenerator( self.LOG_DEBUG )
		
		if not game.isFinalInitialized or game.getGameTurn() == game.getStartTurn() :
			for idx in range(0,gc.getMAX_CIV_PLAYERS()) :
				self.onSetPlayerAlive( [idx, gc.getPlayer(idx).isAlive()] )

	def removeEventHandlers( self ) :
		CvUtil.pyPrint( "  DCN - Removing event handlers from DynamicCivNames" )
		
		self.customEM.removeEventHandler( "BeginPlayerTurn", self.onBeginPlayerTurn )
		self.customEM.removeEventHandler( "setPlayerAlive", self.onSetPlayerAlive )
		#self.customEM.removeEventHandler( "kbdEvent", self.onKbdEvent )
		self.customEM.removeEventHandler( "cityAcquired", self.onCityAcquired )
		self.customEM.removeEventHandler( 'cityBuilt', self.onCityBuilt )
		self.customEM.removeEventHandler( "vassalState", self.onVassalState )
		self.customEM.removeEventHandler( "playerRevolution", self.onPlayerRevolution ) # lfgr

	def onBeginPlayerTurn( self, argsList ) :
		iGameTurn, iPlayer = argsList

		# Stuff at end of previous players turn
		iPrevPlayer = iPlayer - 1
		while iPrevPlayer >= 0 and not gc.getPlayer(iPrevPlayer).isAlive() :
			iPrevPlayer -= 1

		if iPrevPlayer < 0 :
			iPrevPlayer = gc.getBARBARIAN_PLAYER()

		if 0 <= iPrevPlayer < gc.getBARBARIAN_PLAYER() :
			iPlayer = iPrevPlayer
			pPlayer = gc.getPlayer( iPlayer )

			if pPlayer.isAlive() and SDTK.sdObjectExists( "Revolution", pPlayer ) :
				#CvUtil.pyPrint("  DCN - Object exists %d"%(iPlayer))
				prevCivics = SDTK.sdObjectGetVal( "Revolution", pPlayer, 'CivicList' )
				if prevCivics is not None :
					for i in range(0,gc.getNumCivicOptionInfos()):
						if prevCivics[i] != pPlayer.getCivics( i ) :
							self.recalcNameWithMessage(iPlayer)
							return
							
				revTurn = SDTK.sdObjectGetVal( "Revolution", pPlayer, 'RevolutionTurn' )
				if revTurn is not None and game.getGameTurn() - revTurn == 30 and pPlayer.getNumCities() > 0 :
					# "Graduate" from rebel name
					self.recalcNameWithMessage(iPlayer)
					return
					
			if pPlayer.isAlive() and SDTK.sdObjectExists( "BarbarianCiv", pPlayer ) :
				barbTurn = SDTK.sdObjectGetVal( "BarbarianCiv", pPlayer, 'SpawnTurn' )
				if barbTurn is not None and game.getGameTurn() - barbTurn == 30 :
					# "Graduate" from barb civ name
					self.recalcNameWithMessage(iPlayer)
					return
			
			# LFGR_TODO ?
			"""if pPlayer.isAlive() and not SDTK.sdObjectExists( "BarbarianCiv", pPlayer ) :
				if 'Tribe' in pPlayer.getCivilizationDescription( 0 ) :
					if pPlayer.getCurrentRealEra() > 0 or pPlayer.getTotalPopulation() >= 3 :
						# Graduate from game start name
						CvUtil.pyPrint("  DCN - Graduating from game start name Player %d"%(iPlayer))
						self.recalcNameWithMessage(iPlayer)
						return"""
		
			# lfgr: Alliances
			if RevOpt.isTeamNaming() :
				if pPlayer.isAlive() and gc.getTeam( pPlayer.getTeam() ).getNumMembers() == 2 :
					if not "Alliance" in pPlayer.getCivilizationDescription( 0 ) :
						CvUtil.pyPrint( "  DCN - Changing name from Alliance of Player %d" % iPlayer )
						self.recalcNameWithMessage( iPlayer )

	def onCityAcquired( self, argsList):
		'City Acquired'

		owner,playerType,city,bConquest,bTrade = argsList

		owner = gc.getPlayer( city.getOwner() )
		
		if owner.isAlive() and not owner.isBarbarian() :
			CvUtil.pyPrint("  DCN - Checking for new name by number of cities")
			self.recalcNameWithMessage( owner.getID() )
	
	def onCityBuilt( self, argsList ) :
		city = argsList[0]

		pOwner = gc.getPlayer( city.getOwner() )
		
		if pOwner.isAlive() and not pOwner.isBarbarian()  :
			CvUtil.pyPrint("  DCN - Checking for new name by number of cities")
			self.recalcNameWithMessage( pOwner.getID() )
	
	def onVassalState(self, argsList):
		iMaster, iVassal, bVassal = argsList
		
		# Update name of every player with the same civ as the (former or new) vassal, as this affects the duplicate civ considerations
		
		# Find civs
		leCivs = [gc.getPlayer( iPlayer ).getCivilizationType()
				for iPlayer in range(0,gc.getMAX_CIV_PLAYERS())
				if gc.getPlayer( iPlayer ).getTeam() == iVassal]
		
		# Update player names
		for iPlayer in range(0,gc.getMAX_CIV_PLAYERS()) :
			if gc.getPlayer( iPlayer ).getCivilizationType() in leCivs :
				self.recalcNameWithMessage( iPlayer )

	def onPlayerRevolution( self, argsList ) :
		ePlayer, iAnarchyTurns, leOldCivics, leNewCivics = argsList
		self.recalcNameWithMessage( ePlayer )
	
	def onSetPlayerAlive( self, argsList ) :
		iPlayerID = argsList[0]
		bNewValue = argsList[1]
		if( bNewValue == True and iPlayerID < gc.getMAX_CIV_PLAYERS() ) :
			self.recalcName( iPlayerID, bForceUpdate = True )

	# LFGR_TODO: Currently unused
	def showNewNames( self ) :

		bodStr = 'New names for all civs:\n\n'

		for i in range( 0, gc.getMAX_CIV_PLAYERS() ) :
			iPlayer = i
			
			# lfgr bugfix
			curDesc = gc.getPlayer( iPlayer ).getCivilizationDescription( 0 )
			# lfgr end
			[newName, newShort, newAdj] = self.chooseName( iPlayer )

			bodStr += curDesc + '\t-> ' + newName + '\n'

		popup = PyPopup.PyPopup()
		popup.setBodyString( bodStr )
		popup.launch()
	
	def recalcAll( self ) :
		for iPlayer in xrange( gc.getMAX_CIV_PLAYERS() ) :
			if gc.getPlayer( iPlayer ).isAlive() :
				self.recalcNameWithMessage( iPlayer )
	
	def recalcNameWithMessage( self, iPlayer ) :
		pPlayer = gc.getPlayer( iPlayer )
		
		sCurDesc = pPlayer.getCivilizationDescription( 0 )
		
		self.recalcName( iPlayer )
		
		sNewDesc = pPlayer.getCivilizationDescription( 0 )
		
		if sCurDesc != sNewDesc :
			# LFGR_TODO: Translate
			CyInterface().addMessage( iPlayer, false, gc.getDefineINT("EVENT_MESSAGE_TIME"), "Your civilization is now known as the %s" % sNewDesc, None, InterfaceMessageTypes.MESSAGE_TYPE_INFO, None, gc.getInfoTypeForString( "COLOR_HIGHLIGHT_TEXT" ), -1, -1, False, False )
			if self.LOG_DEBUG :
				CvUtil.pyPrint("  DCN - Setting civ name due to civics to %s" % sNewDesc )
		
		return
	
	def recalcName( self, iPlayer, bForceUpdate = False ) :
		pPlayer = gc.getPlayer( iPlayer )
		if( pPlayer.isHuman() or game.getActivePlayer() == iPlayer ) :
			if RevOpt.isLeaveHumanPlayerName() :
				CvUtil.pyPrint("  DCN - Leaving name for human player")
				return
		
		# LFGR_TODO
		# When chooseName returns a unicode str that contains é (\xe9), then this works
		# Previously, CvUtil.convertToStr was used on all three strings, which messed up the é, and
		# caused pPlayer.setCivName to fail.
		pPlayer.setCivName( *self.chooseName( iPlayer, bForceUpdate ) )

	def getCreativityLevel( self ) :
		if game.isGameMultiPlayer() :
			return 0
		else :
			return RevOpt.getDNCLevel()
	
	def chooseName( self, iPlayer, bForceUpdate = False ) :
		"""
		:param iPlayer: ChooseName for this player
		:param bForceUpdate: Whether to force an update even if the civ would rather retain its name
		:return: New name tuple of the form (desc, shortDesc, adj)
		"""
		pPlayer = gc.getPlayer( iPlayer )
		sCurDesc = pPlayer.getCivilizationDescription( 0 )
		sCurShort = pPlayer.getCivilizationShortDescription( 0 )
		sCurAdj = pPlayer.getCivilizationAdjective( 0 )
		
		if pPlayer.isRebel() and not bForceUpdate :
			# Rebels keep their names for as long as possible
			return [sCurDesc, sCurShort, sCurAdj]
		
		tsOldTuple = (sCurDesc, sCurShort, sCurAdj)
		
		iCreativityLevel = self.getCreativityLevel()
		
		if iCreativityLevel == 0 :
			CvUtil.pyPrint( "  DCN - No creativity allowed here, reverting to default name" )
			return gc.getCivilizationInfo( pPlayer.getCivilizationType() ).getDescription(), sCurShort, sCurAdj
		
		# LFGR_TODO: Performance - Iterate through this and immediately return if sCurDesc is found?
		lsNewDescs = list( self.descGen.generateDescs( iPlayer, iCreativityLevel ) )
		
		if self.LOG_DEBUG : CvUtil.pyPrint( "  DCN - Generated %d names: %s" % ( len( lsNewDescs ), ", ".join( lsNewDescs ) ) )
		
		if sCurDesc in lsNewDescs :
			if self.LOG_DEBUG : CvUtil.pyPrint( "  DCN - Old name still valid, retain it" )
			return tsOldTuple
		
		rand = random.Random()
		rand.seed( CyGame().getSorenRandNum( 10000, "Shuffle seed" ) )
		rand.shuffle( lsNewDescs )

		for sNewDesc in lsNewDescs :
			if isUnusedDesc( iPlayer, sNewDesc ) :
				if self.LOG_DEBUG :
					CvUtil.pyPrint( "  DCN - Old desc: \"%s\", New desc: \"%s\"" % ( sCurDesc, sNewDesc ) )
				return [sNewDesc, sCurShort, sCurAdj]
			else :
				if self.LOG_DEBUG :
					CvUtil.pyPrint( "  DCN - Desc \"%s\" already used!" % sNewDesc )
		
		CvUtil.pyPrint( "  DCN - ERROR - No unused desc found, retaining \"%s\"!" % sCurDesc )
		return tsOldTuple

	
	def resetName( self, iPlayer ) :
		pPlayer = gc.getPlayer(iPlayer)
		
		civInfo = gc.getCivilizationInfo(pPlayer.getCivilizationType())
		origDesc  = civInfo.getDescription()
		origShort = civInfo.getShortDescription(0)
		origAdj   = civInfo.getAdjective(0)

		newDesc  = CvUtil.convertToStr(origDesc)
		newShort = CvUtil.convertToStr(origShort)
		newAdj   = CvUtil.convertToStr(origAdj)
		
		if( self.LOG_DEBUG ) :
			CvUtil.pyPrint("  DCN - Re-setting civ name for player %d to %s"%(iPlayer,newDesc))
		
		gc.getPlayer(iPlayer).setCivName( newDesc, newShort, newAdj )
