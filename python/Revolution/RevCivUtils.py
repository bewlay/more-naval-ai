# RevCivUtils.py

from CvPythonExtensions import *
import CvUtil
import RevDefs
import RevData

# globals
gc = CyGlobalContext()
game = CyGame()

# must both be < 0
SCORE_NOT_AVAILABLE = -2
SCORE_NOT_ALLOWED = -1

# score addition if a split is forced and the civ type is the same as the old civ
SCORE_SPLIT_CIV = 10
# score addition if religion matches
SCORE_RELIGION = 3
# score addition if race equal
SCORE_SAME_RACE = 2
# score addition if race is good
SCORE_GOOD_RACE = 1


class RevCivUtils :
	def __init__( self ) :
		self.rcd = RevCivDefines()
	
	def chooseNewCivAndLeader( self, iOldCivType, iCultureOwnerCivType, bSplit, iReligion ) :
		liNotAllowedCivs = list()
		liGoodCivs = list()
		liBestCivs = list()
		iBestScore = 0
		
		iRace = self.rcd.lpCivRules[iCultureOwnerCivType].iRace
		
		for iCiv in xrange( gc.getNumCivilizationInfos() ) :
			iScore = self.rcd.lpCivRules[iCiv].getScore( iOldCivType, iRace, bSplit, iReligion )
			if( iScore == SCORE_NOT_ALLOWED ) :
				liNotAllowedCivs.append( iCiv )
				print "RevCivUtils: Civ %d has not-allowed score(%d)" % ( iCiv, iScore )
			else :
				if( iScore > iBestScore ) :
					iBestScore = iScore
					liGoodCivs.extend( liBestCivs )
					liBestCivs = list()
					liBestCivs.append( iCiv )
					print "RevCivUtils: Civ %d has best score(%d)" % ( iCiv, iScore )
				elif( iScore == iBestScore ) :
					liBestCivs.append( iCiv )
					print "RevCivUtils: Civ %d has good score(%d)" % ( iCiv, iScore )
				elif( iScore >= 0 ) :
					liGoodCivs.append( iCiv )
					print "RevCivUtils: Civ %d has okay score(%d)" % ( iCiv, iScore )
				else :
					print "RevCivUtils: Civ %d has bad score(%d)" % ( iCiv, iScore )
		
		if( len( liBestCivs ) > 0 ) :
			iNewCiv = liBestCivs[game.getSorenRandNum( len( liBestCivs ), 'RevCivUtils: pick civ from best civs list' )]
			print "RevCivUtils: Civ %i chosen" % ( iNewCiv )
		elif( len( liGoodCivs ) > 0 ) :
			iNewCiv = liGoodCivs[game.getSorenRandNum( len( liGoodCivs ), 'RevCivUtils: pick civ from good civs list' )]
			print "RevCivUtils: Civ %i chosen" % ( iNewCiv )
		elif( len( liNotAllowedCivs ) > 0 ) :
			iNewCiv = liNotAllowedCivs[game.getSorenRandNum( len( liNotAllowedCivs ), 'RevCivUtils: pick civ from not allowed civs list' )]
			print "RevCivUtils: Civ %i chosen" % ( iNewCiv )
		else :
			print 'RevCivUtils: No civ available, returning (-1, -1)'
			return ( -1, -1 )
		
		liLeaders = self.rcd.lpCivRules[iNewCiv].getLeaderList( iReligion )
		if( len( liLeaders ) == 0 ) :
			# try without religion
			liLeaders = self.rcd.lpCivRules[iNewCiv].getLeaderList( -1 )
			if( len( liLeaders ) == 0 ) :
				raise Exception( "RevCivUtils: No Available leaders for chosen civ. That should have been checked before..." )
		
		print "available leaders: %s"%( str( liLeaders ) )
		
		# prefer minor leaders
		liMinorLeaders = list()
		for iLeader in liLeaders :
			if( iLeader in self.rcd.liMinorLeaders[iNewCiv] ) :
				print "leader %i is minor leader"%( iLeader )
				liMinorLeaders.append( iLeader )
			else :
				print "leader %i is major leader"%( iLeader )
		
		if( len( liMinorLeaders ) > 0 ) :
			print "Choosing minor leader"
			iNewLeader = liMinorLeaders[game.getSorenRandNum( len( liMinorLeaders ), 'RevCivUtils: pick leader from minor leaders list' )]
		else :
			print "Choosing major leader"
			iNewLeader = liLeaders[game.getSorenRandNum( len( liLeaders ), 'RevCivUtils: pick leader from leaders list' )]
		print "RevCivUtils: Leader %i chosen" % ( iNewLeader )
		
		return ( iNewCiv, iNewLeader )

class RevCivRule :
	def __init__( self, rcd, iCiv ) :
		self.iCiv = iCiv
		
		self.liLeaders = rcd.getLeaders( iCiv )
		
		self.bNoRevolt = False
		
		self.liReligions = list()
		self.liBlockedReligions = list()
		
		self.iRace = None
		self.liGoodRaces = list()
		
		# TODO terrain
		# TODO check for religions present in cities
	
	def getScore( self, iOldCivilization, iCultureRace, bSplit, iReligion ) :
		# check if any leaders are available
		if( len( self.getLeaderList( -1 ) ) == 0 ) :
			return SCORE_NOT_AVAILABLE
		
		# check if civ is blocked as rebel
		if( self.bNoRevolt ) :
			return SCORE_NOT_AVAILABLE
		
		# check if civ is already alive (only if it isn't a split empire revolution)
		if( not bSplit ) :
			for i in range(0,gc.getMAX_CIV_PLAYERS()) :
				if( gc.getPlayer(i).getCivilizationType() == self.iCiv ) :
					if( (gc.getPlayer(i).isAlive()) or (gc.getPlayer(i).isEverAlive()) or (RevData.revObjectExists(gc.getPlayer(i))) ) :
						return SCORE_NOT_ALLOWED
		
		# check if non-agnostic leaders are availble for a religious revolution
		if( iReligion != -1 and len( self.getLeaderList( iReligion ) ) == 0 ) :
			return SCORE_NOT_ALLOWED
		
		# check for blocked religions
		if( iReligion in self.liBlockedReligions ) :
			return SCORE_NOT_ALLOWED
		
		iScore = 0
		
		if( bSplit and self.iCiv == iOldCivilization ) :
			iScore += SCORE_SPLIT_CIV
		
		if( iReligion in self.liReligions ) :
			iScore += SCORE_RELIGION
		
		if( self.iRace != None ) :
			if( iCultureRace == self.iRace ) :
				iScore += SCORE_SAME_RACE
			
		if( iCultureRace in self.liGoodRaces ) :
			iScore += SCORE_GOOD_RACE
		
		if( iScore >= 0 ) :
			return iScore
		else :
			return 0
	
	def getLeaderList( self, iReligion ) :
		liResult = list()
		liResult.extend( self.liLeaders )
		
		for iLeader in self.liLeaders :
			# check if leader is used
			for iPlayer in xrange( gc.getMAX_CIV_PLAYERS() ) :
				if( iLeader == gc.getPlayer( iPlayer ).getLeaderType() ) :
					liResult.remove( iLeader )
					break
			if( not iLeader in liResult ) :
				continue
			# check for agnostic leaders in a religious revolution
			iAgnostic = CvUtil.findInfoTypeNum( gc.getTraitInfo, gc.getNumTraitInfos(), 'TRAIT_AGNOSTIC' )
			if( iReligion != -1 ) :
				if( gc.getLeaderHeadInfo( iLeader ).hasTrait( iAgnostic ) ) :
					liResult.remove( iLeader )
					continue
		
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
		self.iDumannios = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_DUMANNIOS' )
		self.iGosea = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_GOSEA' )
		self.iHafgan = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_HAFGAN' )
		self.iKane = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_KANE' )
		self.iKoun = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_KOUN' )
		self.iMahon = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_MAHON' )
		self.iMalchavic = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_MALCHAVIC' )
		self.iOstanes = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_OSTANES' )
		self.iRiuros = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_RIUROS' )
		self.iShekinah = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_SHEKINAH' )
		self.iUldanor = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_ULDANOR' )
		self.iTethira = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_TETHIRA' )
		self.iThessalonica = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_THESSALONICA' )
		self.iVolanna = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_VOLANNA' )
		self.iMelisandre = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_MELISANDRE' )
		self.iFuria = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_FURIA' )
		self.iWeevil = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_WEEVIL' )
		self.iTya = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_TYA' )
		self.iSallos = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_SALLOS' )
		self.iVolanna = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_VOLANNA' )
		self.iRivanna = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_RIVANNA' )
		self.iDuin = CvUtil.findInfoTypeNum( gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'LEADER_DUIN' )
		
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
		self.liMinorLeaders[self.iInfernal] = [self.iSallos]
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
		
		self.lpCivRules[self.iElohim].liReligions = [self.iEmpyrean, self.iOrder]
		self.lpCivRules[self.iElohim].liBlockedReligions = [self.iVeil]
		self.lpCivRules[self.iElohim].iRace = self.iHuman
		self.lpCivRules[self.iElohim].liGoodRaces = [self.iNomad, self.iWinterborn]
		
		self.lpCivRules[self.iGrigori].liBlockedReligions = [self.iFellowship, self.iOrder, self.iOverlords, self.iKilmorph, self.iVeil, self.iEsus]
		self.lpCivRules[self.iGrigori].iRace = self.iHuman
		self.lpCivRules[self.iGrigori].liGoodRaces = [self.iNomad, self.iWinterborn]
		
		self.lpCivRules[self.iHippus].iRace = self.iHuman
		self.lpCivRules[self.iHippus].liGoodRaces = [self.iNomad, self.iWinterborn]
		
		self.lpCivRules[self.iIllians].liBlockedReligions = [self.iFellowship, self.iOrder, self.iOverlords, self.iKilmorph, self.iVeil, self.iEsus]
		self.lpCivRules[self.iIllians].iRace = self.iWinterborn
		self.lpCivRules[self.iIllians].liGoodRaces = [self.iHuman, self.iNomad]
		
		self.lpCivRules[self.iKhazad].liReligions = [self.iKilmorph]
		self.lpCivRules[self.iKhazad].iRace = self.iDwarf
		
		self.lpCivRules[self.iKuriotates].iRace = None
		self.lpCivRules[self.iKuriotates].liGoodRaces = [self.iNomad, self.iWinterborn, self.iDarkElf, self.iElf, self.iDwarf, self.iOrc]
		
		self.lpCivRules[self.iLanun].liReligions = [self.iOverlords]
		self.lpCivRules[self.iLanun].iRace = self.iHuman
		self.lpCivRules[self.iLanun].liGoodRaces = [self.iNomad, self.iWinterborn]
		
		self.lpCivRules[self.iLjosalfar].liReligions = [self.iFellowship]
		self.lpCivRules[self.iLjosalfar].iRace = self.iElf
		self.lpCivRules[self.iLjosalfar].liGoodRaces = [self.iDarkElf]
		
		self.lpCivRules[self.iLuchuirp].liReligions = [self.iKilmorph]
		self.lpCivRules[self.iLuchuirp].iRace = self.iDwarf
		
		self.lpCivRules[self.iMalakim].liReligions = [self.iEmpyrean]
		self.lpCivRules[self.iMalakim].iRace = self.iNomad
		self.lpCivRules[self.iMalakim].liGoodRaces = [self.iHuman, self.iWinterborn]
		
		self.lpCivRules[self.iSheaim].liReligions = [self.iVeil]
		self.lpCivRules[self.iSheaim].iRace = None
		
		self.lpCivRules[self.iSidar].liReligions = [self.iEsus]
		self.lpCivRules[self.iSidar].iRace = None
		
		self.lpCivRules[self.iSvartalfar].liReligions = [self.iEsus, self.iFellowship]
		self.lpCivRules[self.iSvartalfar].iRace = self.iDarkElf
		self.lpCivRules[self.iSvartalfar].liGoodRaces = [self.iElf]
		
		
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