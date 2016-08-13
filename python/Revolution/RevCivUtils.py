# RevCivUtils.py

from CvPythonExtensions import *
import CvUtil
import RevDefs
import RevData
import TerrainFlavorUtil

import random

# globals
gc = CyGlobalContext()
game = CyGame()

LOG_DEBUG = True

# must both be < 0
SCORE_NOT_AVAILABLE = -2
SCORE_NOT_ALLOWED = -1

# whether to use SCORE_NOT_ALLOWED-civs if there are no other civs available (e.g. due to lack of leaders)
USE_NOT_ALLOWED = True

# score addition if a split is forced and the civ type is the same as the old civ
SCORE_SPLIT_FORCED = 100
# score addition if a split is allowed and the civ type is the same as the old civ
SCORE_SPLIT_ALLOWED = 2
# score addition if religion matches
SCORE_RELIGION = 3
# score addition if race equal
SCORE_SAME_RACE = 2
# score addition if race is related
SCORE_GOOD_RACE = 1
# factor for terrain score.
TERRAIN_SCORE_FACTOR = 0.5

#split types
SPLIT_NOT_ALLOWED = 0
SPLIT_ALLOWED = 1 # Splinter civ is a bit more likely
SPLIT_FORCED = 2 # Tries to split civ, but does not allow duplicate leaders
SPLIT_PUPPET = 3 # Splits civ, does allow duplicate leaders


class RevCivUtils :
	def __init__( self ) :
		self.rcd = RevCivDefines()


	# Returns the chosen civilization type and a list of possible leaders. It does not perform any random number calls.
	def getNewCivAndLeaderList( self, iOldCivType, iCultureOwnerCivType, iSplitType, iReligion, iPlotX, iPlotY ) :
		if( LOG_DEBUG ) : print "RevCivUtils.getNewCivAndLeaderList( iOldCivType=%i, iCultureOwnerCivType=%i, iSplitType=%i, iReligion=%i, iPlotX=%i, iPlotY=%i )"%( iOldCivType, iCultureOwnerCivType, iSplitType, iReligion, iPlotX, iPlotY )

		# find available civs

		liNotAllowedCivs = list()
		liGoodCivs = list()
		liBestCivs = list()
		iBestScore = 0

		iRace = self.rcd.lpCivRules[iCultureOwnerCivType].iRace

		for iCiv in xrange( gc.getNumCivilizationInfos() ) :
			iScore = self.rcd.lpCivRules[iCiv].getScore( iOldCivType, iRace, iSplitType, iReligion, iPlotX, iPlotY )
			if( iScore == SCORE_NOT_ALLOWED ) :
				liNotAllowedCivs.append( iCiv )
				if( LOG_DEBUG ) : print "RevCivUtils: Civ %s has not-allowed score(%d)" % ( gc.getCivilizationInfo( iCiv ).getType(), iScore )
			else :
				if( iScore > iBestScore ) :
					iBestScore = iScore
					liGoodCivs.extend( liBestCivs )
					liBestCivs = list()
					liBestCivs.append( iCiv )
					if( LOG_DEBUG ) : print "RevCivUtils: Civ %s has best score(%d)" % ( gc.getCivilizationInfo( iCiv ).getType(), iScore )
				elif( iScore == iBestScore ) :
					liBestCivs.append( iCiv )
					if( LOG_DEBUG ) : print "RevCivUtils: Civ %s has good score(%d)" % ( gc.getCivilizationInfo( iCiv ).getType(), iScore )
				elif( iScore >= 0 ) :
					liGoodCivs.append( iCiv )
					if( LOG_DEBUG ) : print "RevCivUtils: Civ %s has okay score(%d)" % ( gc.getCivilizationInfo( iCiv ).getType(), iScore )
				else :
					if( LOG_DEBUG ) : print "RevCivUtils: Civ %s has bad score(%d)" % ( gc.getCivilizationInfo( iCiv ).getType(), iScore )

		# shuffle and put lists together
		random.shuffle( liBestCivs )
		random.shuffle( liGoodCivs )

		liCivs = liBestCivs
		liCivs.extend( liGoodCivs )

		if( USE_NOT_ALLOWED ) :
			random.shuffle( liNotAllowedCivs )
			liCivs.extend( liNotAllowedCivs )

		print "RevCivUtils: liCivs:"
		print liCivs

		for iNewCiv in liCivs :
			if( LOG_DEBUG ) : print "RevCivUtils: Trying Civ %d" % ( iNewCiv )
			liLeaders = self.rcd.lpCivRules[iNewCiv].getLeaderList( iSplitType, iReligion )

			# prefer minor leaders
			liMinorLeaders = list()
			for iLeader in liLeaders :
				if( iLeader in self.rcd.liMinorLeaders[iNewCiv] ) :
					if( LOG_DEBUG ) : print "leader %s is minor leader" % ( gc.getLeaderHeadInfo( iLeader ).getType() )
					liMinorLeaders.append( iLeader )
				else :
					if( LOG_DEBUG ) : print "leader %s is major leader" % ( gc.getLeaderHeadInfo( iLeader ).getType() )

			liNewLeaders = []
			if( len( liMinorLeaders ) > 0 ) :
				if( LOG_DEBUG ) : print "Choosing minor leader list"
				liNewLeaders = liMinorLeaders
			elif( len( liLeaders ) > 0 ) :
				if( LOG_DEBUG ) : print "Choosing major leader list"
				liNewLeaders = liLeaders

			return iNewCiv, liNewLeaders

		if( LOG_DEBUG ) : print 'RevCivUtils: No civ available, returning (-1, [])'
		return -1, []


	# Returns the chosen civilization type and a possible leader. It performs random number calls.
	def chooseNewCivAndLeader( self, iOldCivType, iCultureOwnerCivType, iSplitType, iReligion, iPlotX, iPlotY ) :
		if LOG_DEBUG: print "RevCivUtils.chooseNewCivAndLeader( iOldCivType=%i, iCultureOwnerCivType=%i, iSplitType=%i, iReligion=%i, iPlotX=%i, iPlotY=%i )"%( iOldCivType, iCultureOwnerCivType, iSplitType, iReligion, iPlotX, iPlotY )
		iNewCivIdx, liNewLeaders = self.getNewCivAndLeaderList(iOldCivType, iCultureOwnerCivType, iSplitType, iReligion, iPlotX, iPlotY)
		iNewLeader = -1
		if len(liNewLeaders) > 0:
			iNewLeader = liNewLeaders[game.getSorenRandNum(len(liNewLeaders), 'RevCivUtils: pick leader from chosen leaders list')]
		if LOG_DEBUG: print "RevCivUtils: Returning Civ %d and Leader %d" % (iNewCivIdx, iNewLeader)
		return iNewCivIdx, iNewLeader


class RevCivRule :
	def __init__( self, rcd, iCiv ) :
		self.iCiv = iCiv

		self.liLeaders = rcd.getLeaders( iCiv )

		self.bNoRevolt = False

		# TODO: add religion points
		self.liReligions = list()
		self.liBlockedReligions = list()

		self.iRace = None
		self.liGoodRaces = list()

		self.pCivTerrainPreference = TerrainFlavorUtil.CivTerrainPreference()

		# TODO check for religions present in cities

	def getScore( self, iOldCivilization, iCultureRace, iSplitType, iReligion, iPlotX, iPlotY ) :
		# check if any leaders are available
		if( len( self.getLeaderList( iSplitType, -1 ) ) == 0 and iSplitType != SPLIT_PUPPET ) :
			print "\tSCORE_NOT_AVAILABLE: No more leaders"
			return SCORE_NOT_AVAILABLE

		# check if civ is blocked as rebel
		if( self.bNoRevolt ) :
			print "\tSCORE_NOT_AVAILABLE: Civ cannot revolt"
			return SCORE_NOT_AVAILABLE

		# check if civ is same as parent and split is not allowed
		if( iSplitType == SPLIT_NOT_ALLOWED and self.iCiv == iOldCivilization ) :
			print "\tSCORE_NOT_ALLOWED: split civ not allowed"
			return SCORE_NOT_ALLOWED

		# check if civ is already alive (only if new civ would not be a splinter civ)?
		# TODO: maybe allow some civs with culture present
		if( self.iCiv != iOldCivilization ) :
			for i in range( 0, gc.getMAX_CIV_PLAYERS() ) :
				if( gc.getPlayer( i ).getCivilizationType() == self.iCiv ) :
					if( ( gc.getPlayer( i ).isAlive() ) or ( gc.getPlayer( i ).isEverAlive() ) or ( RevData.revObjectExists( gc.getPlayer( i ) ) ) ) :
						print "\tSCORE_NOT_ALLOWED civ already alive"
						return SCORE_NOT_ALLOWED

		# check if non-agnostic leaders are availble for a religious revolution
		if( iReligion != -1 and len( self.getLeaderList( iSplitType, iReligion ) ) == 0 ) :
			print "\tSCORE_NOT_ALLOWED: there are only agnostic or no leaders available"
			return SCORE_NOT_ALLOWED

		# check for blocked religions
		if( iReligion in self.liBlockedReligions ) :
			print "\tSCORE_NOT_ALLOWED: bad religion"
			return SCORE_NOT_ALLOWED

		iScore = 0
		
		if( ( iSplitType == SPLIT_FORCED or iSplitType == SPLIT_PUPPET ) and self.iCiv == iOldCivilization ) :
			print "\tScore: +%d: SPLIT_FORCED addition" % ( SCORE_SPLIT_FORCED )
			iScore += SCORE_SPLIT_FORCED
		elif( iSplitType == SPLIT_ALLOWED and self.iCiv == iOldCivilization ) :
			print "\tScore: +%d: SPLIT_ALLOWED addition" % ( SCORE_SPLIT_ALLOWED )
			iScore += SCORE_SPLIT_ALLOWED

		if( iReligion in self.liReligions ) :
			print "\tScore: +%d: Religion addition" % ( SCORE_RELIGION )
			iScore += SCORE_RELIGION

		if( self.iRace != None ) :
			if( iCultureRace == self.iRace ) :
				print "\tScore: +%d: Same race addition" % ( SCORE_SAME_RACE )
				iScore += SCORE_SAME_RACE

		if( iCultureRace in self.liGoodRaces ) :
			print "\tScore: +%d: Aligned race addition" % ( SCORE_GOOD_RACE )
			iScore += SCORE_GOOD_RACE

		iAreaRadius = 3
		fTerrainScore = TerrainFlavorUtil.getPlotScore( self.iCiv, iPlotX, iPlotY, self.pCivTerrainPreference, iAreaRadius )
		fTerrainScore *= TERRAIN_SCORE_FACTOR
		if( fTerrainScore > 0 ) :
			print "\tScore: +%d: Terrain addition" % ( int( fTerrainScore + 0.5 ) )
			iScore += int( fTerrainScore + 0.5 )
		else :
			print "\tScore: %d: Terrain subtraction" % ( int( fTerrainScore + 0.5 ) )
			iScore += int( fTerrainScore - 0.5 )

		if( iScore >= 0 ) :
			return iScore
		else :
			return 0
	
	def getLeaderList( self, iSplitType, iReligion ) :
		liResult = list()
		liResult.extend( self.liLeaders )
		
		liBadLeaders = list()
		
		for iLeader in self.liLeaders :
			# check if leader is used
			for iPlayer in xrange( gc.getMAX_CIV_PLAYERS() ) :
				if( iLeader == gc.getPlayer( iPlayer ).getLeaderType() ) :
					liResult.remove( iLeader )
					liBadLeaders.append( iLeader )
					break
			if( not iLeader in liResult ) :
				continue
			# check for agnostic leaders in a religious revolution
			iAgnostic = CvUtil.findInfoTypeNum( gc.getTraitInfo, gc.getNumTraitInfos(), 'TRAIT_AGNOSTIC' )
			if( iReligion != -1 ) :
				if( gc.getLeaderHeadInfo( iLeader ).hasTrait( iAgnostic ) ) :
					liResult.remove( iLeader )
					liBadLeaders.append( iLeader )
					continue
		
		if( iSplitType == SPLIT_PUPPET and len( liResult ) == 0 ) :
			liResult = liBadLeaders
		
		return liResult


class RevCivDefines :
	def __init__( self ) :
		# civs

		self.iAmurite		 = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'CIVILIZATION_AMURITES' )
		self.iBalseraph		 = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'CIVILIZATION_BALSERAPHS' )
		self.iBannor		 = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'CIVILIZATION_BANNOR' )
		self.iCalabim = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'CIVILIZATION_CALABIM' )
		self.iClan		 = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'CIVILIZATION_CLAN_OF_EMBERS' )
		self.iDoviello	 = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'CIVILIZATION_DOVIELLO' )
		self.iElohim	 = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'CIVILIZATION_ELOHIM' )
		self.iGrigori		 = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'CIVILIZATION_GRIGORI' )
		self.iHippus		 = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'CIVILIZATION_HIPPUS' )
		self.iIllians	 = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'CIVILIZATION_ILLIANS' )
		self.iInfernal		 = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'CIVILIZATION_INFERNAL' )
		self.iKhazad		 = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'CIVILIZATION_KHAZAD' )
		self.iKuriotates		 = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'CIVILIZATION_KURIOTATES' )
		self.iLanun		 = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'CIVILIZATION_LANUN' )
		self.iLjosalfar		 = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'CIVILIZATION_LJOSALFAR' )
		self.iLuchuirp	 = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'CIVILIZATION_LUCHUIRP' )
		self.iMalakim		 = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'CIVILIZATION_MALAKIM' )
		self.iMercurians		 = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'CIVILIZATION_MERCURIANS' )
		self.iSheaim		 = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'CIVILIZATION_SHEAIM' )
		self.iSidar		 = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'CIVILIZATION_SIDAR' )
		self.iSvartalfar		 = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'CIVILIZATION_SVARTALFAR' )

		self.iMinor = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), RevDefs.sXMLMinor )
		self.iBarbarian = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), RevDefs.sXMLBarbarian )
		self.iRandom = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'CIVILIZATION_RANDOM' )


		# minor leaders

		self.iAnaganios = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_ANAGANTIOS' )
		self.iAverax = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_AVERAX' )
		self.iBraeden = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_BRAEDEN' )
		self.iDuin = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_DUIN' )
		self.iDumannios = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_DUMANNIOS' )
		self.iFuria = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_FURIA' )
		self.iGosea = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_GOSEA' )
		self.iHafgan = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_HAFGAN' )
		self.iJudecca = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_JUDECCA' )
		self.iKane = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_KANE' )
		self.iKoun = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_KOUN' )
		self.iLethe = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_LETHE' )
		self.iMahon = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_MAHON' )
		self.iMalchavic = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_MALCHAVIC' )
		self.iMelisandre = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_MELISANDRE' )
		self.iMeresin = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_MERESIN' )
		self.iOstanes = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_OSTANES' )
		self.iOuzza = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_OUZZA' )
		self.iRiuros = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_RIUROS' )
		self.iRivanna = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_RIVANNA' )
		self.iSallos = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_SALLOS' )
		self.iShekinah = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_SHEKINAH' )
		self.iStatius = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_STATIUS' )
		self.iUldanor = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_ULDANOR' )
		self.iTethira = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_TETHIRA' )
		self.iTya = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_TYA' )
		self.iThessalonica = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_THESSALONICA' )
		self.iVolanna = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_VOLANNA' )
		self.iWeevil = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_WEEVIL' )
		
		self.liMinorLeaders = list()

		for idx in range( 0, gc.getNumCivilizationInfos() ) :
			self.liMinorLeaders.append( list() )

		self.liMinorLeaders[self.iAmurite] = [self.iTya]
		self.liMinorLeaders[self.iBannor] = [self.iTethira]
		self.liMinorLeaders[self.iBalseraph] = [self.iMelisandre, self.iFuria, self.iWeevil]
		self.liMinorLeaders[self.iClan] = [self.iHafgan]
		self.liMinorLeaders[self.iCalabim] = [self.iMahon]
		self.liMinorLeaders[self.iDoviello] = [self.iVolanna, self.iDuin]
		self.liMinorLeaders[self.iElohim] = [self.iThessalonica]
		self.liMinorLeaders[self.iGrigori] = [self.iKoun]
		self.liMinorLeaders[self.iHippus] = [self.iOstanes, self.iUldanor]
		self.liMinorLeaders[self.iIllians] = [self.iDumannios, self.iRiuros, self.iAnaganios, self.iBraeden]
		self.liMinorLeaders[self.iInfernal] = [self.iSallos, self.iJudecca, self.iOuzza, self.iMeresin, self.iStatius, self.iLethe]
		self.liMinorLeaders[self.iMalakim] = [self.iKane]
		self.liMinorLeaders[self.iSheaim] = [self.iAverax, self.iGosea, self.iMalchavic]
		self.liMinorLeaders[self.iSidar] = [self.iShekinah]
		self.liMinorLeaders[self.iSvartalfar] = [self.iVolanna, self.iRivanna]

		# religions

		self.iFellowship = CvUtil.findInfoTypeNum( gc.getReligionInfo, gc.getNumReligionInfos(), 'RELIGION_FELLOWSHIP_OF_LEAVES' )
		self.iOrder = CvUtil.findInfoTypeNum( gc.getReligionInfo, gc.getNumReligionInfos(), 'RELIGION_THE_ORDER' )
		self.iOverlords = CvUtil.findInfoTypeNum( gc.getReligionInfo, gc.getNumReligionInfos(), 'RELIGION_OCTOPUS_OVERLORDS' )
		self.iKilmorph = CvUtil.findInfoTypeNum( gc.getReligionInfo, gc.getNumReligionInfos(), 'RELIGION_RUNES_OF_KILMORPH' )
		self.iVeil = CvUtil.findInfoTypeNum( gc.getReligionInfo, gc.getNumReligionInfos(), 'RELIGION_THE_ASHEN_VEIL' )
		self.iEmpyrean = CvUtil.findInfoTypeNum( gc.getReligionInfo, gc.getNumReligionInfos(), 'RELIGION_THE_EMPYREAN' )
		self.iEsus = CvUtil.findInfoTypeNum( gc.getReligionInfo, gc.getNumReligionInfos(), 'RELIGION_COUNCIL_OF_ESUS' )

		# races
		self.iHuman = -1
		self.iNomad = CvUtil.findInfoTypeNum( gc.getPromotionInfo, gc.getNumPromotionInfos(), 'PROMOTION_NOMAD' )
		self.iWinterborn = CvUtil.findInfoTypeNum( gc.getPromotionInfo, gc.getNumPromotionInfos(), 'PROMOTION_WINTERBORN' )

		self.iDarkElf = CvUtil.findInfoTypeNum( gc.getPromotionInfo, gc.getNumPromotionInfos(), 'PROMOTION_DARK_ELF' )
		self.iElf = CvUtil.findInfoTypeNum( gc.getPromotionInfo, gc.getNumPromotionInfos(), 'PROMOTION_ELF' )

		self.iDwarf = CvUtil.findInfoTypeNum( gc.getPromotionInfo, gc.getNumPromotionInfos(), 'PROMOTION_DWARF' )

		self.iOrc = CvUtil.findInfoTypeNum( gc.getPromotionInfo, gc.getNumPromotionInfos(), 'PROMOTION_ORC' )
		#self.iDemon = CvUtil.findInfoTypeNum( gc.getPromotionInfo, gc.getNumPromotionInfos(), 'PROMOTION_DEMON' )

		# terrain

		self.iDesert = CvUtil.findInfoTypeNum( gc.getTerrainInfo, gc.getNumTerrainInfos(), 'TERRAIN_DESERT' )
		self.iTundra = CvUtil.findInfoTypeNum( gc.getTerrainInfo, gc.getNumTerrainInfos(), 'TERRAIN_TUNDRA' )
		self.iSnow = CvUtil.findInfoTypeNum( gc.getTerrainInfo, gc.getNumTerrainInfos(), 'TERRAIN_SNOW' )
		self.iGrass = CvUtil.findInfoTypeNum( gc.getTerrainInfo, gc.getNumTerrainInfos(), 'TERRAIN_GRASS' )
		self.iPlains = CvUtil.findInfoTypeNum( gc.getTerrainInfo, gc.getNumTerrainInfos(), 'TERRAIN_PLAINS' )
		
		self.iJungle = CvUtil.findInfoTypeNum( gc.getFeatureInfo, gc.getNumFeatureInfos(), 'FEATURE_JUNGLE' )
		self.iForest = CvUtil.findInfoTypeNum( gc.getFeatureInfo, gc.getNumFeatureInfos(), 'FEATURE_FOREST' )

		self.iHorse = CvUtil.findInfoTypeNum( gc.getBonusInfo, gc.getNumBonusInfos(), 'BONUS_HORSE' )

		self.iPeak = 0
		self.iHills = 1
		self.iLand = 2
		self.iOcean = 3

		############################# rules

		self.lpCivRules = list()

		for iCiv in range( 0, gc.getNumCivilizationInfos() ) :
			self.lpCivRules.append( RevCivRule( self, iCiv ) )

		self.lpCivRules[self.iAmurite].iRace = self.iHuman
		self.lpCivRules[self.iAmurite].liGoodRaces = [self.iNomad, self.iWinterborn]

		self.lpCivRules[self.iBalseraph].iRace = self.iHuman
		self.lpCivRules[self.iBalseraph].liGoodRaces = [self.iNomad, self.iWinterborn]

		self.lpCivRules[self.iBannor].liReligions = [self.iOrder]
		self.lpCivRules[self.iBannor].iRace = self.iHuman
		self.lpCivRules[self.iBannor].liGoodRaces = [self.iNomad, self.iWinterborn]

		self.lpCivRules[self.iCalabim].iRace = self.iHuman
		self.lpCivRules[self.iCalabim].liGoodRaces = [self.iNomad, self.iWinterborn]

		self.lpCivRules[self.iClan].liBlockedReligions = [self.iOrder]
		self.lpCivRules[self.iClan].iRace = self.iOrc

		self.lpCivRules[self.iDoviello].liBlockedReligions = [self.iOrder]
		self.lpCivRules[self.iDoviello].iRace = self.iWinterborn
		self.lpCivRules[self.iDoviello].liGoodRaces = [self.iHuman, self.iNomad]
		self.lpCivRules[self.iDoviello].pCivTerrainPreference.afTerrainAffinity[self.iTundra] = 1.0
		self.lpCivRules[self.iDoviello].pCivTerrainPreference.afFeatureAffinity[self.iForest] = 1.0
		self.lpCivRules[self.iDoviello].pCivTerrainPreference.afTerrainAffinity[self.iSnow] = 0.5
		self.lpCivRules[self.iDoviello].pCivTerrainPreference.afTerrainAffinity[self.iGrass] = -0.5
		self.lpCivRules[self.iDoviello].pCivTerrainPreference.afTerrainAffinity[self.iDesert] = -1.5
		
		self.lpCivRules[self.iElohim].liReligions = [self.iEmpyrean, self.iOrder]
		self.lpCivRules[self.iElohim].liBlockedReligions = [self.iVeil]
		self.lpCivRules[self.iElohim].iRace = self.iHuman
		self.lpCivRules[self.iElohim].liGoodRaces = [self.iNomad, self.iWinterborn]

		self.lpCivRules[self.iGrigori].liBlockedReligions = [self.iFellowship, self.iOrder, self.iOverlords, self.iKilmorph, self.iVeil, self.iEsus]
		self.lpCivRules[self.iGrigori].iRace = self.iHuman
		self.lpCivRules[self.iGrigori].liGoodRaces = [self.iNomad, self.iWinterborn]

		self.lpCivRules[self.iHippus].iRace = self.iHuman
		self.lpCivRules[self.iHippus].liGoodRaces = [self.iNomad, self.iWinterborn]
		self.lpCivRules[self.iHippus].pCivTerrainPreference.afPlotAffinity[self.iLand] = 2.0
		self.lpCivRules[self.iHippus].pCivTerrainPreference.afTerrainAffinity[self.iGrass] = 1.5
		self.lpCivRules[self.iHippus].pCivTerrainPreference.afBonusAffinity[self.iHorse] = 1.5
		self.lpCivRules[self.iHippus].pCivTerrainPreference.afTerrainAffinity[self.iTundra] = -0.25
		self.lpCivRules[self.iHippus].pCivTerrainPreference.afTerrainAffinity[self.iSnow] = -0.25
		self.lpCivRules[self.iHippus].pCivTerrainPreference.afPlotAffinity[self.iHills] = -0.5
		self.lpCivRules[self.iHippus].pCivTerrainPreference.afTerrainAffinity[self.iDesert] = -1.0
		self.lpCivRules[self.iHippus].pCivTerrainPreference.afPlotAffinity[self.iPeak] = -1.0
		self.lpCivRules[self.iHippus].pCivTerrainPreference.fCoastAffinity = -1.0

		self.lpCivRules[self.iIllians].liBlockedReligions = [self.iFellowship, self.iOrder, self.iOverlords, self.iKilmorph, self.iVeil, self.iEsus]
		self.lpCivRules[self.iIllians].iRace = self.iWinterborn
		self.lpCivRules[self.iIllians].liGoodRaces = [self.iHuman, self.iNomad]
		self.lpCivRules[self.iIllians].pCivTerrainPreference.afTerrainAffinity[self.iSnow] = 1.5
		self.lpCivRules[self.iIllians].pCivTerrainPreference.afTerrainAffinity[self.iTundra] = 1.0
		self.lpCivRules[self.iIllians].pCivTerrainPreference.afTerrainAffinity[self.iGrass] = -1.0
		self.lpCivRules[self.iIllians].pCivTerrainPreference.afTerrainAffinity[self.iDesert] = -1.5
		
		self.lpCivRules[self.iKhazad].liReligions = [self.iKilmorph]
		self.lpCivRules[self.iKhazad].iRace = self.iDwarf
		self.lpCivRules[self.iKhazad].pCivTerrainPreference.afPlotAffinity[self.iHills] = 2.0
		self.lpCivRules[self.iKhazad].pCivTerrainPreference.fCoastAffinity = -2.0

		self.lpCivRules[self.iKuriotates].iRace = None
		self.lpCivRules[self.iKuriotates].liGoodRaces = [self.iNomad, self.iWinterborn, self.iDarkElf, self.iElf, self.iDwarf, self.iOrc]

		self.lpCivRules[self.iLanun].liReligions = [self.iOverlords]
		self.lpCivRules[self.iLanun].iRace = self.iHuman
		self.lpCivRules[self.iLanun].liGoodRaces = [self.iNomad, self.iWinterborn]
		self.lpCivRules[self.iLanun].pCivTerrainPreference.fCoastAffinity = 2.0
		self.lpCivRules[self.iLanun].pCivTerrainPreference.afPlotAffinity[self.iLand] = 1.0
		self.lpCivRules[self.iLanun].pCivTerrainPreference.afPlotAffinity[self.iHills] = -1.0
		self.lpCivRules[self.iLanun].pCivTerrainPreference.afPlotAffinity[self.iPeak] = -2.0

		self.lpCivRules[self.iLjosalfar].liReligions = [self.iFellowship]
		self.lpCivRules[self.iLjosalfar].iRace = self.iElf
		self.lpCivRules[self.iLjosalfar].liGoodRaces = [self.iDarkElf]
		self.lpCivRules[self.iLjosalfar].pCivTerrainPreference.afFeatureAffinity[self.iForest] = 2.0
		self.lpCivRules[self.iLjosalfar].pCivTerrainPreference.afTerrainAffinity[self.iGrass] = 0.5
		self.lpCivRules[self.iLjosalfar].pCivTerrainPreference.afPlotAffinity[self.iHills] = -0.5
		self.lpCivRules[self.iLjosalfar].pCivTerrainPreference.afTerrainAffinity[self.iDesert] = -2.0

		self.lpCivRules[self.iLuchuirp].liReligions = [self.iKilmorph]
		self.lpCivRules[self.iLuchuirp].iRace = self.iDwarf
		self.lpCivRules[self.iLuchuirp].pCivTerrainPreference.afPlotAffinity[self.iHills] = 2.0
		self.lpCivRules[self.iLuchuirp].pCivTerrainPreference.fCoastAffinity = -2.0

		self.lpCivRules[self.iMalakim].liReligions = [self.iEmpyrean]
		self.lpCivRules[self.iMalakim].iRace = self.iNomad
		self.lpCivRules[self.iMalakim].liGoodRaces = [self.iHuman, self.iWinterborn]
		self.lpCivRules[self.iMalakim].pCivTerrainPreference.afTerrainAffinity[self.iDesert] = 2.0
		self.lpCivRules[self.iMalakim].pCivTerrainPreference.afFeatureAffinity[self.iJungle] = -1.0
		self.lpCivRules[self.iMalakim].pCivTerrainPreference.afFeatureAffinity[self.iForest] = -1.0

		self.lpCivRules[self.iSheaim].liReligions = [self.iVeil]
		self.lpCivRules[self.iSheaim].iRace = None

		self.lpCivRules[self.iSidar].liReligions = [self.iEsus]
		self.lpCivRules[self.iSidar].iRace = None

		self.lpCivRules[self.iSvartalfar].liReligions = [self.iEsus, self.iFellowship]
		self.lpCivRules[self.iSvartalfar].iRace = self.iDarkElf
		self.lpCivRules[self.iSvartalfar].liGoodRaces = [self.iElf]
		self.lpCivRules[self.iSvartalfar].pCivTerrainPreference.afFeatureAffinity[self.iForest] = 1.8
		self.lpCivRules[self.iSvartalfar].pCivTerrainPreference.afTerrainAffinity[self.iGrass] = 0.3
		self.lpCivRules[self.iSvartalfar].pCivTerrainPreference.afPlotAffinity[self.iHills] = -0.3
		self.lpCivRules[self.iSvartalfar].pCivTerrainPreference.afTerrainAffinity[self.iDesert] = -1.8


		self.lpCivRules[self.iInfernal].bNoRevolt = True
		self.lpCivRules[self.iMercurians].bNoRevolt = True
		self.lpCivRules[self.iMinor].bNoRevolt = True
		self.lpCivRules[self.iBarbarian].bNoRevolt = True
		self.lpCivRules[self.iRandom].bNoRevolt = True

	def getLeaders( self, iCiv ) :
		liLeaders = list()

		for leaderType in range( 0, gc.getNumLeaderHeadInfos() ) :
			if( gc.getCivilizationInfo( iCiv ).isLeaders( leaderType ) or game.isOption( GameOptionTypes.GAMEOPTION_LEAD_ANY_CIV ) or ( leaderType in self.liMinorLeaders[iCiv] ) ) :
				liLeaders.append( leaderType )

		return liLeaders
