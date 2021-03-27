## TechPrefs
##
## Builds ordered lists of techs as preferred by the various Great People.
##
## Copyright (c) 2007-2008 The BUG Mod.
##
## Author: EmperorFool
##
## lfgr 03/2021: Changed to be unit-based instead of flavor based, to fix errors when a unit has multiple flavors
## Also, made it respect canEverResearch()

from CvPythonExtensions import *
import GCUtils

# BUG - Mac Support - start
import BugUtil
BugUtil.fixSets(globals())
# BUG - Mac Support - end

gc = CyGlobalContext()
gcu = GCUtils.GCUtils()


# Helper functions
def getDiscoveryValue( pUnitInfo, eTech ) :
	# type: (CvUnitInfo, int) -> int
	# Note: This must reflect changes in CvGameCoreUtils/getDiscoveryTech().
	# LFGR_TODO: Make a this a C++ helper function
	pTechInfo = gc.getTechInfo( eTech )
	iValue = 0
	for eFlavor in range( gc.getNumFlavorTypes() ) :
		iValue += pUnitInfo.getFlavorValue( eFlavor ) * pTechInfo.getFlavorValue( eFlavor )
	return iValue

def makeDiscoveryTechList( eUnit ) :
	# type: (int) -> List[int]
	""" A list of techs that a unit of the given type can research, by order of importance. """
	pUnitInfo = gc.getUnitInfo( eUnit )
	lTechsWithValue = [(-getDiscoveryValue( pUnitInfo, eTech ), eTech) for eTech in range( gc.getNumTechInfos() )]
	lTechsWithValue.sort()
	return [eTech for _, eTech in lTechsWithValue]

def iterDiscoverUnitInfos() :
	for pUnitInfo in gcu.iterUnitInfos() :
		if pUnitInfo.getBaseDiscover() > 0 :
			yield pUnitInfo


class TechPrefs:

	def __init__(self):
		self.NUM_TECHS = gc.getNumTechInfos()
		self.NUM_AND_PREREQS = gc.getDefineINT("NUM_AND_TECH_PREREQS")
		self.NUM_OR_PREREQS = gc.getDefineINT("NUM_OR_TECH_PREREQS")
		
		# The tech tree
		self.mTechs = {} # type: Dict[int, Tech]
		
		# Unit(Type)s that can discover. Best discoverers first
		self.leDiscoverUnits = [eUnit for eUnit in range( gc.getNumUnitInfos() )
				if gc.getUnitInfo( eUnit ).getBaseDiscover() > 0]
		self.leDiscoverUnits.sort( key = lambda eUnit : gc.getUnitInfo( eUnit ).getBaseDiscover(), reverse = True )
		
		# Tech pref lists by unit
		self.mTechsByUnit = {}
		for eUnit in self.leDiscoverUnits :
			self.mTechsByUnit[eUnit] = [self.getTech( eTech ) for eTech in makeDiscoveryTechList( eUnit )]
		
		# Initialize tech tree
		for iTech in range(self.NUM_TECHS):
			pTechInfo = gc.getTechInfo(iTech)
			pTech = self.getTech(iTech)
			
			# hook up prereq techs
			for i in range(self.NUM_AND_PREREQS):
				pPrereqTech = pTechInfo.getPrereqAndTechs(i)
				if (pPrereqTech != -1):
					pTech.addAndPrereq(self.getTech(pPrereqTech))
			for i in range(self.NUM_OR_PREREQS):
				pPrereqTech = pTechInfo.getPrereqOrTechs(i)
				if (pPrereqTech != -1):
					pTech.addOrPrereq(self.getTech(pPrereqTech))
	
	def getDiscoverUnits( self ) :
		return list( self.leDiscoverUnits )

	def getTech(self, iTech):
		if iTech not in self.mTechs:
			self.mTechs[iTech] = Tech(iTech)
		return self.mTechs[iTech]

	def getTechStr(self, sTech):
		iTech = gc.getInfoTypeForString(sTech)
		if iTech in self.mTechs:
			return self.mTechs[iTech]
		return None

	def removeTech(self, iTech):
		"""Removes the given tech, usually because it has been researched."""
		if (iTech in self.mTechs):
			pTech = self.mTechs[iTech]
			del self.mTechs[iTech]
			for lTechs in self.mTechsByUnit.values() :
				if pTech in lTechs :
					lTechs.remove(pTech)
			pTech.removeFromTree()

	def removeKnownTechs(self):
		"""Removes the techs known to the current team."""
		pTeam = gc.getTeam(gc.getActivePlayer().getTeam())
		for iTech in range(self.NUM_TECHS):
			if (pTeam.isHasTech(iTech)):
				self.removeTech(iTech)

	def getNextResearchableUnitTech(self, eUnit):
		"""Returns the next tech in the unit's list that is researchable now or None."""
		for pTech in self.mTechsByUnit[eUnit]:
			if pTech.canResearch() :
				return pTech
		return None

	def getNextResearchableWithUnitTech(self, eUnit, sTechs):
		"""Returns the next tech in the flavor's list that is researchable once the given techs are researched or None."""
		for pTech in self.mTechsByUnit[eUnit]:
			if pTech not in sTechs and pTech.canResearchWith(sTechs) :
				return pTech
		return None

	def getAllUnitTechs(self, eUnit):
		"""Returns a list of all techs in the unit's list."""
		return list( self.mTechsByUnit[eUnit] )

	def getCurrentUnitTechs(self, eUnit):
		"""Returns a list of techs in the unit's list that are researchable now."""
		return [tech for tech in self.mTechsByUnit[eUnit] if tech.canResearch()]

	def getCurrentWithUnitTechs(self, eUnit, sTechs):
		"""Returns a list of techs in the unit's list that are researchable once sTechs have been researched."""
		return [tech for tech in self.mTechsByUnit[eUnit] if tech.canResearchWith(sTechs)]


class Tech:
	
	def __init__(self, iTech):
		self.iTech = iTech
		self.sAndPrereqs = set()
		self.sOrPrereqs = set()
		self.iNumAndPrereqs = 0
		self.iNumOrPrereqs = 0
		self.sLeadsTo = set()

	def getID(self):
		return self.iTech

	def getInfo(self):
		return gc.getTechInfo(self.iTech)

	def getName(self):
		return self.getInfo().getDescription()
	
	def __hash__(self):
		return hash(self.iTech)
	
	def __eq__(self, other):
		return self.iTech == other.iTech
	
	def __cmp__(self, other):
		return self.iTech - other.iTech


	def addAndPrereq(self, pTech):
		if pTech not in self.sAndPrereqs:
			self.iNumAndPrereqs += 1
			self.sAndPrereqs.add(pTech)
			pTech.addLeadsTo(self)

	def addOrPrereq(self, pTech):
		if pTech not in self.sOrPrereqs:
			self.iNumOrPrereqs += 1
			self.sOrPrereqs.add(pTech)
			pTech.addLeadsTo(self)

	def removePrereq(self, pTech):
		self.sAndPrereqs.discard(pTech)
		self.sOrPrereqs.discard(pTech)


	def getNumTechsNeeded(self):
		"""Returns the minimum number of techs that must be researched to be able to research this tech."""
		return self.getNumAndTechsNeeded() + self.getNumOrTechsNeeded()

	def getNumAndTechsNeeded(self):
		return len(self.sAndPrereqs)

	def getNumOrTechsNeeded(self):
		if (len(self.sOrPrereqs) == 0 or len(self.sOrPrereqs) < self.iNumOrPrereqs):
			return 0
		return 1

	def getTechsNeeded(self):
		"""
		Returns two sets of techs that are needed to make this tech researchable.
		
		The first set are all missing And prereqs.
		The second set is all Or prereqs or an empty set if at least one has already been researched.
		"""
		andSet = self.sAndPrereqs.copy()
		if (len(self.sOrPrereqs) == 0 or len(self.sOrPrereqs) < self.iNumOrPrereqs):
			orSet = set()
		else:
			orSet = self.sOrPrereqs.copy()
		return andSet, orSet
	
	def canEverResearch( self ) :
		return gc.getActivePlayer().canEverResearch( self.iTech )

	def canResearch(self):
		"""Returns True if this tech has met all And prereqs and at least one Or prereq."""
		return self.getNumTechsNeeded() == 0 and self.canEverResearch()

	def canResearchWith(self, sTechs):
		"""Returns True if this tech can be researched once the given tech(s) have been researched."""
		if (len(sTechs) == 0):
			return self.canResearch()
		if not self.canEverResearch() :
			return False
		if self in sTechs :
			return False
		sAnds = self.sAndPrereqs.difference(sTechs)
		sOrs = self.sOrPrereqs.difference(sTechs)
		return (len(sOrs) == 0 or len(sOrs) < self.iNumOrPrereqs) and len(sAnds) == 0


	def addLeadsTo(self, pTech):
		self.sLeadsTo.add(pTech)

	def removeLeadsTo(self, pTech):
		self.sLeadsTo.discard(pTech)

	def removeFromTree(self):
		"""Removes this tech from the prereq lists of the techs it leads to and the leads to lists of its prereqs."""
		for pTech in self.sAndPrereqs:
			pTech.removeLeadsTo(self)
		for pTech in self.sOrPrereqs:
			pTech.removeLeadsTo(self)
		for pTech in self.sLeadsTo:
			pTech.removePrereq(self)


	def __str__(self):
		str = self.getName()
		bFirst = True
		if (len(self.sAndPrereqs) > 0 or len(self.sOrPrereqs) > 0):
			str += " requires "
		if (len(self.sAndPrereqs) > 0):
			for pTech in self.sAndPrereqs:
				if bFirst:
					bFirst = False
				else:
					str += " and "
				str += pTech.getName()
		if (len(self.sOrPrereqs) > 0):
			if not bFirst:
				str += " and "
				bFirst = True
			for pTech in self.sOrPrereqs:
				if bFirst:
					bFirst = False
				else:
					str += " or "
				str += pTech.getName()
		if (len(self.sLeadsTo) > 0):
			str += ", leads to "
			bFirst = True
			for pTech in self.sLeadsTo:
				if bFirst:
					bFirst = False
				else:
					str += ", "
				str += pTech.getName()
		return str
