# RebelTypes.py
#
# by jdog5000
# Version 1.1

# This file sets up the most likely rebel civ types to appear when a revolution occurs in a particular civ.

from CvPythonExtensions import *
import CvUtil

gc = CyGlobalContext()

# Initialize list to empty
RebelTypeList = list()

# This function actually sets up the lists of most preferable rebel types for each motherland civ type
# All rebel types in this list are equally likely
# If none of these are available, defaults to a similar art style civ
def setup( ) :

	#print "Setting up rebel type list"

	global RebelTypeList

	RebelTypeList = list()

	for idx in range(0,gc.getNumCivilizationInfos()) :
		RebelTypeList.append( list() )

	try :
		iAmurite		= CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'CIVILIZATION_AMURITES')
		iBalseraph		 = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'CIVILIZATION_BALSERAPHS')
		iBannor		  = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'CIVILIZATION_BANNOR')
		iClan		= CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'CIVILIZATION_CLAN_OF_EMBERS')
		iDoviello	  = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'CIVILIZATION_DOVIELLO')
		iElohim	   = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'CIVILIZATION_ELOHIM')
		iGrigori		   = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'CIVILIZATION_GRIGORI')
		iHippus		  = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'CIVILIZATION_HIPPUS')
		iIllians	  = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'CIVILIZATION_ILLIANS')
		iInfernal		= CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'CIVILIZATION_INFERNAL')
		iKhazad		= CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'CIVILIZATION_KHAZAD')
		iKuriotates		 = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'CIVILIZATION_KURIOTATES')
		iLanun		= CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'CIVILIZATION_LANUN')
		iLjosalfar		 = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'CIVILIZATION_LJOSALFAR')
		iLuchuirp	  = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'CIVILIZATION_LUCHUIRP')
		iMalakim		   = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'CIVILIZATION_MALAKIM')
		iMercurians		  = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'CIVILIZATION_MERCURIANS')
		iSheaim		  = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'CIVILIZATION_SHEAIM')
		iSidar		  = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'CIVILIZATION_SIDAR')
		iSvartalfar		  = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'CIVILIZATION_SVARTALFAR')
		iCalabim = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'CIVILIZATION_CALABIM')


		# Format is:
		# RebelTypeList[iHomeland] = [iRebel1, iRebel2, iRebel3]
		# No limit on length of rebel list, can be zero

		RebelTypeList[iAmurite]	 = [iAmurite]
		RebelTypeList[iBalseraph]	  = [iBalseraph]
		RebelTypeList[iBannor]	   = [iBannor]
		RebelTypeList[iClan]	 = [iClan]
		RebelTypeList[iDoviello]   = [iDoviello]
		RebelTypeList[iElohim]	= [iElohim]
		RebelTypeList[iGrigori]		= [iGrigori]
		RebelTypeList[iHippus]	   = [iHippus]
		RebelTypeList[iIllians]	   = [iIllians]
		RebelTypeList[iInfernal]	 = [iInfernal]
		RebelTypeList[iKhazad]	= [iKhazad]
		RebelTypeList[iKuriotates]	  = [iKuriotates]
		RebelTypeList[iLanun]	 = [iLanun]
		RebelTypeList[iLjosalfar]	  = [iLjosalfar]
		RebelTypeList[iLuchuirp]   = [iLuchuirp]
		RebelTypeList[iMalakim]		= [iMalakim]
		RebelTypeList[iMercurians]	   = [iMercurians]
		RebelTypeList[iSheaim]	   = [iSheaim]
		RebelTypeList[iSidar]	   = [iSidar]
		RebelTypeList[iSvartalfar]	   = [iSvartalfar]
		
		#print "Completed rebel type list"
		
		# lfgr
		# minor rebel leaders
		global MinorLeaders
	
		MinorLeaders = list()
		
		for idx in range(0,gc.getNumCivilizationInfos()) :
			MinorLeaders.append( list() )
		
		try :
			iAnaganios = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'LEADER_ANAGANTIOS')
			iAverax = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'LEADER_AVERAX')
			iBraeden = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'LEADER_BRAEDEN')
			iDumannios = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'LEADER_DUMANNIOS')
			iGosea = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'LEADER_GOSEA')
			iHafgan = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'LEADER_HAFGAN')
			iKane = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'LEADER_KANE')
			iKoun = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'LEADER_KOUN')
			iMahon = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'LEADER_MAHON')
			iMalchavic = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'LEADER_MALCHAVIC')
			iOstanes = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'LEADER_OSTANES')
			iRiuros = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'LEADER_RIUROS')
			iShekinah = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'LEADER_SHEKINAH')
			iUldanor = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'LEADER_ULDANOR')
			iTethira = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'LEADER_TETHIRA')
			iThessalonica = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'LEADER_THESSALONICA')
			iVolanna = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'LEADER_VOLANNA')
			iMelisandre = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'LEADER_MELISANDRE')
			iFuria = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'LEADER_FURIA')
			iWeevil = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'LEADER_WEEVIL')
			iTya = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'LEADER_TYA')
			iSallos = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'LEADER_SALLOS')
			iVolanna = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'LEADER_VOLANNA')
			iRivanna = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'LEADER_RIVANNA')
			iDuin = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'LEADER_DUIN')
			
			MinorLeaders[iAmurite] = [iTya]
			MinorLeaders[iBannor] = [iTethira]
			MinorLeaders[iBalseraph] = [iMelisandre, iFuria, iWeevil]
			MinorLeaders[iClan] = [iHafgan]
			MinorLeaders[iCalabim] = [iMahon]
			MinorLeaders[iDoviello] = [iVolanna, iDuin]
			MinorLeaders[iElohim] = [iThessalonica]
			MinorLeaders[iGrigori] = [iKoun]
			MinorLeaders[iHippus] = [iOstanes, iUldanor]
			MinorLeaders[iIllians] = [iDumannios, iRiuros, iAnaganios, iBraeden]
			MinorLeaders[iInfernal] = [iSallos]
			MinorLeaders[iMalakim] = [iKane]
			MinorLeaders[iSheaim] = [iAverax, iGosea, iMalchavic]
			MinorLeaders[iSidar] = [iShekinah]
			MinorLeaders[iSvartalfar] = [iVolanna, iRivanna]

		except:
			print "Error!  Minor leaders not found, no short lists available"

		# religious rebels
		global ReligiousRebels

		ReligiousRebels = list()

		for idx in range(0,gc.getNumReligionInfos()) :
			ReligiousRebels.append( list() )

		global BlockedReligiousRebels

		BlockedReligiousRebels = list()

		for idx in range(0,gc.getNumReligionInfos()) :
			BlockedReligiousRebels.append( list() )

		try :
			iFellowship = CvUtil.findInfoTypeNum(gc.getReligionInfo,gc.getNumReligionInfos(),'RELIGION_FELLOWSHIP_OF_LEAVES')
			iOrder = CvUtil.findInfoTypeNum(gc.getReligionInfo,gc.getNumReligionInfos(),'RELIGION_THE_ORDER')
			iOverlords = CvUtil.findInfoTypeNum(gc.getReligionInfo,gc.getNumReligionInfos(),'RELIGION_OCTOPUS_OVERLORDS')
			iKilmorph = CvUtil.findInfoTypeNum(gc.getReligionInfo,gc.getNumReligionInfos(),'RELIGION_RUNES_OF_KILMORPH')
			iVeil = CvUtil.findInfoTypeNum(gc.getReligionInfo,gc.getNumReligionInfos(),'RELIGION_THE_ASHEN_VEIL')
			iEmpyrean = CvUtil.findInfoTypeNum(gc.getReligionInfo,gc.getNumReligionInfos(),'RELIGION_THE_EMPYREAN')
			iEsus = CvUtil.findInfoTypeNum(gc.getReligionInfo,gc.getNumReligionInfos(),'RELIGION_COUNCIL_OF_ESUS')
			
			ReligiousRebels[iFellowship] = [iLjosalfar, iSvartalfar]
			ReligiousRebels[iOrder] = [iBannor, iElohim]
			ReligiousRebels[iOverlords] = [iLanun]
			ReligiousRebels[iKilmorph] = [iKhazad, iLuchuirp]
			ReligiousRebels[iVeil] = [iSheaim]
			ReligiousRebels[iEmpyrean] = [iMalakim, iElohim]
			ReligiousRebels[iEsus] = [iSidar, iSvartalfar]
			
			BlockedReligiousRebels[iFellowship] = [iGrigori, iIllians]
			BlockedReligiousRebels[iOrder] = [iGrigori, iIllians]
			BlockedReligiousRebels[iOverlords] = [iGrigori, iIllians]
			BlockedReligiousRebels[iKilmorph] = [iGrigori, iIllians]
			BlockedReligiousRebels[iVeil] = [iGrigori, iIllians]
			BlockedReligiousRebels[iEmpyrean] = [iGrigori, iIllians]
			BlockedReligiousRebels[iEsus] = [iGrigori, iIllians]
		
		except:
			print "Error!  Religions not found, no short lists available"
		# end lfgr

	except:
		print "Error!  Rebel types not found, no short lists available"
