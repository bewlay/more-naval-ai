#Blizzards v1.21 by TC01

"""Blizzards Modcomp by TC01
	initConstants() contains all the constant values used in this file, for ease of access
	isDeepening() checks if the Deepening ritual has been created yet
	doBlizzardTurn() is called every game turn and moves, kills, or spawns blizzards randomly
	moveBlizzard(pPlot, iDirection) moves a blizzard to pPlot depending on iDirection
	canBlizzard(pPlot, bNew) checks if pPlot can have a blizzard move onto it or (if bNew = true) if a blizzard can be spawned there 
	doBlizzard() applies the effects of a blizzard

	All of these functions can be modified to add your own effects. I suggest not modifying doBlizzardTurn or moveBlizzard, but instead modifying the constants defined at in initConstants, as
they affect the behavior of the movement, creation, and killing of blizzards. canBlizzard can be altered to change whether a blizzard can move onto or spawn on a plot. doBlizzard can be 
modified to cause different features or terrains to appear in different conditions.

	 You can use this modcomp with any mod. Follow the instructions in Merging Guide.txt or in the forum thread to merge it. Be aware that it has been included in my Frozen civilization and
in Rise of Erebus by Valkrionn (formerly FF+)."""

from CvPythonExtensions import *
import CvUtil
import Popup as PyPopup
import PyHelpers
import CvScreenEnums
import CvCameraControls

#Globals
gc = CyGlobalContext()
PyPlayer = PyHelpers.PyPlayer

class Blizzards:

	def initConstants(self):
		self.iBlizzardDriftChanceEast = 30		#Chance a blizzard drifts east
		self.iBlizzardDriftChanceWest = 30		#Chance a blizzard drifts west
		self.iBlizzardDriftChanceNorth = 30		#Chance a blizzard drifts north
		self.iBlizzardDriftChanceSouth = 30		#Chance a blizzard drifts south
		self.iBlizzardKillChance = 25			#Chance a blizzard expires
		self.iBlizzardKillChancePlus = 45		#Chance a blizzard expires outside of Illian territory
#		self.iBlizzardIceChance = 10			#Chance a blizzard turns an adjacent water plot into ice
#		self.iPermanentSnowChance = 30			#Chance a blizzard turns land plots into permanent snow

		self.iBlizzardChance = 3				#Chance a blizzard spawns
		if (self.isDeepening()):
			self.iBlizzardChance = 10			#If the Deepening has been completed, activate more blizzards.

		self.iMaxBlizzardsInRange = 2			#Maximum number of blizzards that can be around a newly created blizzard

	def isDeepening(self):
		iDeepening = gc.getInfoTypeForString('PROJECT_THE_DEEPENING')
		for i in range(CyGame().countCivTeamsAlive()-1):
			pTeam = gc.getTeam(i)
			if pTeam.getProjectCount(iDeepening) > 0:
				return true

		return false

	def doBlizzardTurn(self):
		
		self.initConstants()
		
		iBlizzard = gc.getInfoTypeForString('FEATURE_BLIZZARD')
		iIllians = gc.getInfoTypeForString('CIVILIZATION_ILLIANS')
		iSnow = gc.getInfoTypeForString('TERRAIN_SNOW')
		
		for i in range(CyMap().numPlots()):
			pPlot = CyMap().plotByIndex(i)
			if pPlot.getFeatureType() == iBlizzard:
				iBlizzardDirectionRand = CyGame().getSorenRandNum(100, "Blizzard")
				iBlizzardKillRand = CyGame().getSorenRandNum(100, "Kill Blizzard")

				#Moves a blizzard
				if iBlizzardDirectionRand <= 25:
					self.moveBlizzard(pPlot, 0)
				if 26 <= iBlizzardDirectionRand <= 50:
					self.moveBlizzard(pPlot, 1)
				if 51 <= iBlizzardDirectionRand <= 75:
					self.moveBlizzard(pPlot, 2)
				if 76 <= iBlizzardDirectionRand:
					self.moveBlizzard(pPlot, 3)
				
				#Kills a blizzard
				if (pPlot.getOwner() == iIllians):
					if iBlizzardKillRand <= self.iBlizzardKillChance:
						pPlot.setFeatureType(-1,-1)
				else:
					if iBlizzardKillRand <= self.iBlizzardKillChancePlus:
						pPlot.setFeatureType(-1, -1)

			#Creates a blizzard
			if pPlot.getTerrainType() == iSnow:
				if self.canBlizzard(pPlot, true):
					if CyGame().getSorenRandNum(100, "Blizzard") < self.iBlizzardChance:
						pPlot.setFeatureType(iBlizzard,0)
						self.doBlizzard(pPlot)

	def moveBlizzard(self, pPlot, iDirection):
		iBlizzard = gc.getInfoTypeForString('FEATURE_BLIZZARD')
		iRnd = CyGame().getSorenRandNum(100, "Blizzards")
		if iDirection == 0:
			if iRnd <= self.iBlizzardDriftChanceEast:
				newPlot = CyMap().plot(pPlot.getX() + 1, pPlot.getY() + 1)
			elif (iRnd > self.iBlizzardDriftChanceEast and iRnd < (100 - self.iBlizzardDriftChanceEast)):
				newPlot = CyMap().plot(pPlot.getX() + 1, pPlot.getY())
			elif iRnd >= 100 - self.iBlizzardDriftChanceEast:
				newPlot = CyMap().plot(pPlot.getX() + 1, pPlot.getY() - 1)
		elif iDirection == 1:
			if iRnd <= self.iBlizzardDriftChanceWest:
				newPlot = CyMap().plot(pPlot.getX() - 1, pPlot.getY() + 1)
			elif (iRnd > self.iBlizzardDriftChanceWest and iRnd < (100 - self.iBlizzardDriftChanceWest)):
				newPlot = CyMap().plot(pPlot.getX() - 1, pPlot.getY())
			elif iRnd >= 100 - self.iBlizzardDriftChanceWest:
				newPlot = CyMap().plot(pPlot.getX() - 1, pPlot.getY() - 1)
		elif iDirection == 2:
			if iRnd <= self.iBlizzardDriftChanceNorth:
				newPlot = CyMap().plot(pPlot.getX() - 1, pPlot.getY() + 1)
			elif (iRnd > self.iBlizzardDriftChanceNorth and iRnd < (100 - self.iBlizzardDriftChanceNorth)):
				newPlot = CyMap().plot(pPlot.getX(), pPlot.getY() + 1)
			elif iRnd >= 100 - self.iBlizzardDriftChanceNorth:
				newPlot = CyMap().plot(pPlot.getX() + 1, pPlot.getY() + 1)
		elif iDirection == 3:
			if iRnd <= self.iBlizzardDriftChanceSouth:
				newPlot = CyMap().plot(pPlot.getX() - 1, pPlot.getY() - 1)
			elif (iRnd > self.iBlizzardDriftChanceSouth and iRnd < (100 - self.iBlizzardDriftChanceSouth)):
				newPlot = CyMap().plot(pPlot.getX(), pPlot.getY() - 1)
			elif iRnd >= 100 - self.iBlizzardDriftChanceSouth:
				newPlot = CyMap().plot(pPlot.getX() + 1, pPlot.getY() - 1)
		
		if self.canBlizzard(newPlot, false):
			newPlot.setFeatureType(iBlizzard,0)
			self.doBlizzard(newPlot)
			pPlot.setFeatureType(-1,-1)

	def canBlizzard(self, pPlot, bNew):
		iIllians = gc.getInfoTypeForString('CIVILIZATION_ILLIANS')
		iBlizzard = gc.getInfoTypeForString('FEATURE_BLIZZARD')
		if pPlot.isNone() == False:
		
			#General rules, always followed for both movement and creation
#			if pPlot.isPeak():
#				return False
			if pPlot.getFeatureType() != -1:
				return False
			if pPlot.isHasTempFeature():
				return False
#			if pPlot.isWater():
#				return False

			#If we're creating a new blizzard, apply extra restrictions:
			if bNew == true:
				if pPlot.isOwned():
					if (gc.getPlayer(pPlot.getOwner()).getCivilizationType() != iIllians):
						return False
				if pPlot.getOwner() == -1:
					return False
				if pPlot.isCity():
					return False

				iNumBlizzards = 0
				for iX in range(pPlot.getX()-1, pPlot.getX()+2, 1):
					for iY in range(pPlot.getY()-1, pPlot.getY()+2, 1):
						pRange = CyMap().plot(iX, iY)
						if pRange.getFeatureType() == iBlizzard:
							iNumBlizzards += 1
				if iNumBlizzards > self.iMaxBlizzardsInRange:
					return false
				
			return True

		return False

	def doBlizzard(self, pPlot):
		self.initConstants()
		
		iIllians = gc.getInfoTypeForString('CIVILIZATION_ILLIANS')
		iSnow = gc.getInfoTypeForString('TERRAIN_SNOW')
		iTundra = gc.getInfoTypeForString('TERRAIN_TUNDRA')
		iIce = gc.getInfoTypeForString('FEATURE_ICE')
		iFlames = gc.getInfoTypeForString('FEATURE_FLAMES')
		iFloodPlains = gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS')
		iForest = gc.getInfoTypeForString('FEATURE_FOREST')
		iJungle = gc.getInfoTypeForString('FEATURE_JUNGLE')
		iScrub = gc.getInfoTypeForString('FEATURE_SCRUB')
		iSmoke = gc.getInfoTypeForString('IMPROVEMENT_SMOKE')

		if not pPlot.isNone():
			iTurns = CyGame().getSorenRandNum(15, "Temp Terrain") + 10
			iTurns = (iTurns * gc.getGameSpeedInfo(CyGame().getGameSpeedType()).getVictoryDelayPercent()) / 100
			if (self.isDeepening()):
				iTurns *= 2
	
			#Temporary terrain conversions
			if not pPlot.isWater():
				if pPlot.getTempTerrainTimer() < iTurns: #Only convert existing temporary terrain if our timer will be longer than current timer
					if not pPlot.getTerrainType() == iSnow:
						if (pPlot.getTerrainType() == iTundra) or pPlot.isHills():
							pPlot.setTempTerrainType(iSnow, iTurns)
						else:
							pPlot.setTempTerrainType(iTundra, iTurns)
					
			#Put out fire and smoke
			if pPlot.getImprovementType() == iSmoke:
				pPlot.setImprovementType(-1)
			if pPlot.getFeatureType() == iFlames:
				pPlot.setFeatureType(-1, -1)