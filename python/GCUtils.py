"""
Module that provides convenience methods to replace getXXXInfo() and getNumXXXInfos() in most cases.

Usage examples:

>> import GCUtils
>> gcu = GCUtils.GCUtils()

>> print gcu.getUnitInfo( 313 ).getType()
UNIT_WARRIOR # As usual

>> print gcu.getUnitInfo( "UNIT_WARRIOR" ).getType()
UNIT_WARRIOR # Also Works


Invalid usage examples, showing strictness:

>> gcu.getUnitInfo( -1 )
ValueError: -1 is not a valid UnitInfo ID

>> gcu.getUnitInfo( 500 )
ValueError: 500 is not a valid UnitInfo ID

>> gcu.getUnitInfo( "BUILDING_GAMBLING_HOUSE" )
ValueError: BUILDING_GAMBLING_HOUSE is not a UnitInfo

>> gcu.getSpaceshipInfo( "SPACESHIP_ANACONDA" )
AttributeError: 'CyGlobalContext' object has no attribute 'getSpaceshipInfo'

>> for kUnit in gcu.iterUnitInfos() : print kUnit.getType()
...

>> for kSpaceship in gcu.iterSpaceshipInfos() : print kSpaceship.getType()
AttributeError: 'CyGlobalContext' object has no attribute 'getSpaceshipInfo'

"""

import re

from CvPythonExtensions import *


gc = CyGlobalContext()

RE_GETINFO = re.compile( "get([a-zA-Z]+)Info" )
RE_ITERINFOS = re.compile( "iter([a-zA-Z]+)Infos" )

TPL_GC_GET_INFO = "get%sInfo"
TPL_GC_GET_NUM_INFOS = "getNum%sInfos"


def lookup_info_getter( szInfoName ) :
	szGetFuncName = TPL_GC_GET_INFO % szInfoName
	#assert hasattr( gc, szGetFuncName )
	return getattr( gc, szGetFuncName )

def lookup_num_getter( szInfoName ) :
	szNumFuncName = TPL_GC_GET_NUM_INFOS % szInfoName
	#assert hasattr( gc, szNumFuncName )
	return getattr( gc, szNumFuncName )


class _InfoGetter( object ) :
	def __init__( self, szInfoName ) :
		self._szInfoName = szInfoName
		self._gcGetFunc = lookup_info_getter( szInfoName )
		self._gcNumFunc = lookup_num_getter( szInfoName )
	
	def __call__( self, idxOrName ) :
		if type( idxOrName ) == int :
			if not ( 0 <= idxOrName < self._gcNumFunc() ) :
				raise ValueError( "%d is not a valid %sInfo ID" % ( idxOrName, self._szInfoName ) )
			return self._gcGetFunc( idxOrName )
		elif type( idxOrName ) == str :
			idx = gc.getInfoTypeForString( idxOrName )
			if idx == -1 :
				raise ValueError( "%s not found" % idxOrName )
			info = self._gcGetFunc( idx )
			if info.getType() != idxOrName :
				raise ValueError( "%s is not a %sInfo" % ( idxOrName, self._szInfoName ) )
			return info
		else :
			raise TypeError( type( idxOrName ) )


class _InfoIterator( object ) :
	def __init__( self, szInfoName ) :
		self._szInfoName = szInfoName
		self._gcGetFunc = lookup_info_getter( szInfoName )
		self._gcNumFunc = lookup_num_getter( szInfoName )
	
	def __call__( self ) :
		for i in range( self._gcNumFunc() ) :
			yield self._gcGetFunc( i )


class GCUtils :
	def __getattr__( mod, name ) :
		# TODO: Should do some caching
		match = RE_GETINFO.match( name )
		if match and match.start() == 0 and match.end() == len( name ) :
			return _InfoGetter( match.group( 1 ) )
		
		match = RE_ITERINFOS.match( name )
		if match and match.start() == 0 and match.end() == len( name ) :
			return _InfoIterator( match.group( 1 ) )
		
		return AttributeError( name )
			

