# lfgr TerrainRebels
import math
from CvPythonExtensions import *

#globals
gc = CyGlobalContext()

LOG_DEBUG = False

#PLOT_PEAK = 0
#PLOT_HILLS = 1
#PLOT_LAND = 2
PLOT_OCEAN = 3
NUM_PLOT_TYPES = 4

class CivTerrainPreference :
	def __init__( self ) :
		self.afPlotAffinity = list()
		for idx in range( 0, NUM_PLOT_TYPES ) :
			self.afPlotAffinity.append( 0.0 )
			
		self.afTerrainAffinity = list()
		for idx in range( 0, gc.getNumTerrainInfos() ) :
			self.afTerrainAffinity.append( 0.0 )
			
		self.afFeatureAffinity = list()
		for idx in range( 0, gc.getNumFeatureInfos() ) :
			self.afFeatureAffinity.append( 0.0 )
			
		self.afBonusAffinity = list()
		for idx in range( 0, gc.getNumBonusInfos() ) :
			self.afBonusAffinity.append( 0.0 )
		
		self.fRiverAffinity = 0.0
		self.fCoastAffinity = 0.0

leIgnoredPlotTypes = [PLOT_OCEAN]
leIgnoredTerrainTypes = []
leIgnoredFeatureTypes = []
leIgnoredBonusTypes = []

def getPlotScore( iCiv, iPlotX, iPlotY, pCivTerrainPreference, iAreaRadius ) :
	#TODO float?
	fScore = 0
	defPlotTypePercent = getPlotTypePercent( iPlotX, iPlotY, iAreaRadius )
	defTerrainTypePercent = getTerrainTypePercent( iPlotX, iPlotY, iAreaRadius )
	defFeatureTypePercent = getFeatureTypePercent( iPlotX, iPlotY, iAreaRadius )
	defBonusTypePercent = getBonusTypePercent( iPlotX, iPlotY, iAreaRadius )
	
	for ePlotType in xrange( NUM_PLOT_TYPES ) :
		fAffinity = float( pCivTerrainPreference.afPlotAffinity[ ePlotType ] )
		if( fAffinity > 0 ) :
			if( ePlotType in defPlotTypePercent ) :
				fScore += defPlotTypePercent[ePlotType] * fAffinity
				if( LOG_DEBUG ) : print "Additional score for plot type %i: %f*%f"%( ePlotType, defPlotTypePercent[ePlotType], fAffinity )
	
	for eTerrainType in xrange( gc.getNumTerrainInfos() ) :
		fAffinity = float( pCivTerrainPreference.afTerrainAffinity[ eTerrainType ] )
		if( fAffinity > 0 ) :
			if( eTerrainType in defTerrainTypePercent ) :
				fScore += defTerrainTypePercent[eTerrainType] * fAffinity
				if( LOG_DEBUG ) : print "Additional score for terrain type %i: %f*%f"%( eTerrainType, defTerrainTypePercent[eTerrainType], fAffinity )
	
	for eFeatureType in xrange( gc.getNumFeatureInfos() ) :
		fAffinity = float( pCivTerrainPreference.afFeatureAffinity[ eFeatureType ] )
		if( fAffinity > 0 ) :
			if( eFeatureType in defFeatureTypePercent ) :
				fScore += defFeatureTypePercent[eFeatureType] * fAffinity
				if( LOG_DEBUG ) : print "Additional score for feature type %i: %f*%f"%( eFeatureType, defFeatureTypePercent[eFeatureType], fAffinity )
	
	for eBonusType in xrange( gc.getNumBonusInfos() ) :
		fAffinity = float( pCivTerrainPreference.afBonusAffinity[ eBonusType ] )
		if( fAffinity > 0 ) :
			if( eBonusType in defBonusTypePercent ) :
				fScore += defBonusTypePercent[eBonusType] * fAffinity
				if( LOG_DEBUG ) : print "Additional score for bonus type %i: %f*%f"%( eBonusType, defBonusTypePercent[eBonusType], fAffinity )
	
	fRiverAffinity = float( pCivTerrainPreference.fRiverAffinity )
	if( fRiverAffinity > 0 ) :
		fScore += getRiverPercent( iPlotX, iPlotY, iAreaRadius ) * fRiverAffinity
		if( LOG_DEBUG ) : print "Additional score for river: %f*%f"%( getRiverPercent( iPlotX, iPlotY, iAreaRadius ), fRiverAffinity )
	
	fCoastAffinity = float( pCivTerrainPreference.fCoastAffinity )
	if( fCoastAffinity > 0 ) :
		fScore += getCoastPercent( iPlotX, iPlotY, iAreaRadius ) * fCoastAffinity
		if( LOG_DEBUG ) : print "Additional score for coast: %f*%f"%( getCoastPercent( iPlotX, iPlotY, iAreaRadius ), fCoastAffinity )
	
	if( LOG_DEBUG ) : print "Calculated PlotScore for %i in %i|%i: %f"%( iCiv, iPlotX, iPlotY, fScore )
	
	return fScore

def getPlotTypePercent( iPlotX, iPlotY, iAreaRadius ):
	pMap = CyMap()
	
	iCount = 0
	defResult = {}
	
	for iX in xrange( iPlotX - iAreaRadius, iPlotX + iAreaRadius ) :
		for iY in xrange( iPlotY - iAreaRadius, iPlotY + iAreaRadius ) :
			ePlotType = pMap.plot( iX, iY ).getPlotType()
			if( not ePlotType in leIgnoredPlotTypes ) :
				iDistance = int( calcDistance( iPlotX, iPlotY, iX, iY ) )
				if( iDistance < iAreaRadius ) :
					if( not ePlotType in defResult ) :
						defResult[ePlotType] = 0
					defResult[ePlotType] += iAreaRadius - iDistance
					iCount += 1
	
	#if( LOG_DEBUG ) : print "defResult vorher: %s"%( str( defResult ) )
	
	for ePlotType in defResult.keys() :
		if( iCount > 0 ) :
			defResult[ePlotType] /= float( iCount )
		else :
			defResult[ePlotType] = 0
	
	#if( LOG_DEBUG ) : print "defResult nachher: %s"%( str( defResult ) )
	
	return defResult

def getTerrainTypePercent( iPlotX, iPlotY, iAreaRadius ):
	pMap = CyMap()
	
	iCount = 0
	defResult = {}
	
	for iX in xrange( iPlotX - iAreaRadius, iPlotX + iAreaRadius ) :
		for iY in xrange( iPlotY - iAreaRadius, iPlotY + iAreaRadius ) :
			eTerrainType = pMap.plot( iX, iY ).getTerrainType()
			if( not ( eTerrainType in leIgnoredTerrainTypes or pMap.plot( iX, iY ).getPlotType() in leIgnoredPlotTypes ) ) :
				iDistance = int( calcDistance( iPlotX, iPlotY, iX, iY ) )
				if( iDistance < iAreaRadius ) :
					if( not eTerrainType in defResult ) :
						defResult[eTerrainType] = 0
					defResult[eTerrainType] += iAreaRadius - iDistance
					iCount += 1
	
	for eTerrainType in defResult.keys() :
		if( iCount > 0 ) :
			defResult[eTerrainType] /= float( iCount )
		else :
			defResult[eTerrainType] = 0
	
	return defResult

def getFeatureTypePercent( iPlotX, iPlotY, iAreaRadius ):
	pMap = CyMap()
	
	iCount = 0
	defResult = {}
	
	for iX in xrange( iPlotX - iAreaRadius, iPlotX + iAreaRadius ) :
		for iY in xrange( iPlotY - iAreaRadius, iPlotY + iAreaRadius ) :
			eFeatureType = pMap.plot( iX, iY ).getFeatureType()
			if( not ( eFeatureType in leIgnoredFeatureTypes or pMap.plot( iX, iY ).getPlotType() in leIgnoredPlotTypes ) ) :
				iDistance = int( calcDistance( iPlotX, iPlotY, iX, iY ) )
				if( iDistance < iAreaRadius ) :
					if( not eFeatureType in defResult ) :
						defResult[eFeatureType] = 0
					defResult[eFeatureType] += iAreaRadius - iDistance
					iCount += 1
	
	for eFeatureType in defResult.keys() :
		if( iCount > 0 ) :
			defResult[eFeatureType] /= float( iCount )
		else :
			defResult[eFeatureType] = 0
	
	return defResult

def getBonusTypePercent( iPlotX, iPlotY, iAreaRadius ):
	pMap = CyMap()
	
	iCount = 0
	defResult = {}
	
	for iX in xrange( iPlotX - iAreaRadius, iPlotX + iAreaRadius ) :
		for iY in xrange( iPlotY - iAreaRadius, iPlotY + iAreaRadius ) :
			eBonusType = pMap.plot( iX, iY ).getBonusType( -1 )
			if( not ( eBonusType in leIgnoredBonusTypes or pMap.plot( iX, iY ).getPlotType() in leIgnoredPlotTypes ) ) :
				iDistance = int( calcDistance( iPlotX, iPlotY, iX, iY ) )
				if( iDistance < iAreaRadius ) :
					if( not eBonusType in defResult ) :
						defResult[eBonusType] = 0
					defResult[eBonusType] += iAreaRadius - iDistance
					iCount += 1
	
	for eBonusType in defResult.keys() :
		if( iCount > 0 ) :
			defResult[eBonusType] /= float( iCount )
		else :
			defResult[eBonusType] = 0
	
	return defResult

def getRiverPercent( iPlotX, iPlotY, iAreaRadius ):
	pMap = CyMap()
	
	iCount = 0
	iRiverScore = 0
	
	for iX in xrange( iPlotX - iAreaRadius, iPlotX + iAreaRadius ) :
		for iY in xrange( iPlotY - iAreaRadius, iPlotY + iAreaRadius ) :
			if( not pMap.plot( iX, iY ).getPlotType() in leIgnoredPlotTypes ) :
				iDistance = int( calcDistance( iPlotX, iPlotY, iX, iY ) )
				if( iDistance < iAreaRadius ) :
					if( pMap.plot( iX, iY ).isRiver() ) :
						iRiverScore += iAreaRadius - iDistance
					iCount += 1
	
	if( iCount > 0 ) :
		return iRiverScore / iCount
	else :
		return 0

def getCoastPercent( iPlotX, iPlotY, iAreaRadius ):
	pMap = CyMap()
	
	iCount = 0
	iCoastScore = 0
	
	for iX in xrange( iPlotX - iAreaRadius, iPlotX + iAreaRadius ) :
		for iY in xrange( iPlotY - iAreaRadius, iPlotY + iAreaRadius ) :
			if( not pMap.plot( iX, iY ).getPlotType() in leIgnoredPlotTypes ) :
				iDistance = int( calcDistance( iPlotX, iPlotY, iX, iY ) )
				if( iDistance < iAreaRadius ) :
					if( isCoast( pMap.plot( iX, iY ) ) ) :
						iCoastScore += iAreaRadius - iDistance
					iCount += 1
	
	if( iCount > 0 ) :
		return iCoastScore / iCount
	else :
		return 0

# from erebus.py
def calcDistance( x, y, dx, dy ):
	distance = math.sqrt( abs( ( float( x - dx ) * float( x - dx ) ) + ( float( y - dy ) * float( y - dy ) ) ) )
	return distance

# from erebus.py
def isCoast( plot ):
	WaterArea = plot.waterArea()
	if not ( WaterArea == None or WaterArea.isNone() ):
		if not WaterArea.isLake():
			return True
	return False
