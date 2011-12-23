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

	except:
		print "Error!  Rebel types not found, no short lists available"
