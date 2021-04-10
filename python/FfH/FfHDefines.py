from CvPythonExtensions import *

gc = CyGlobalContext()


# Required gold for the various stages of Khazad vault. First should be 0
_VAULT_MIN_GOLD = [0, 50, 100, 150, 200, 300, 500]

# Dwarven vault buildings, as strings.
_VAULT_TYPES = [
	'BUILDING_DWARVEN_VAULT_EMPTY',
	'BUILDING_DWARVEN_VAULT_LOW',
	'BUILDING_DWARVEN_VAULT',
	'BUILDING_DWARVEN_VAULT_STOCKED',
	'BUILDING_DWARVEN_VAULT_ABUNDANT',
	'BUILDING_DWARVEN_VAULT_FULL',
	'BUILDING_DWARVEN_VAULT_OVERFLOWING'
]

assert len( _VAULT_MIN_GOLD ) == len( _VAULT_TYPES )
assert _VAULT_MIN_GOLD[0] == 0, "Min gold for empty vault should be 0"


class FfHDefines :
	def __init__( self ) :
		self._vaultsWithMinGold = None
		self._vaultsWithMinGoldReverse = None

	def _loadInfoTypes( self ) :
		if self._vaultsWithMinGold is not None :
			return

		self._vaultsWithMinGold = tuple( (gc.getInfoTypeForString( sType ), iMinGold)
				for iMinGold, sType in zip( _VAULT_MIN_GOLD, _VAULT_TYPES ) )
		self._vaultsWithMinGoldReverse = tuple(reversed(self._vaultsWithMinGold))

	def getKhazadVaultsWithMinGold( self ) :
		# type: () -> Iterator[Tuple[int, int]]
		self._loadInfoTypes()
		return self._vaultsWithMinGold
	
	def getKhazadVault( self, pPlayer ) :
		# type: (CyPlayer) -> int
		self._loadInfoTypes()
		iGoldPerCity = pPlayer.getGold() // pPlayer.getNumCities()
		for eVault, iMinGold in self._vaultsWithMinGoldReverse :
			if iGoldPerCity >= iMinGold :
				return eVault
		assert False, iGoldPerCity # One of the vaults should have iMinGold == 0

	def getNextKhazadVaultWithMinGold( self, pPlayer ) :
		# type: (CyPlayer) -> Optional[Tuple[int, int]]
		self._loadInfoTypes()
		iGoldPerCity = pPlayer.getGold() // pPlayer.getNumCities()
		prevVaultWithMinGold = None # The last vault that was too expensive for us
		for eVault, iMinGold in self._vaultsWithMinGoldReverse :
			if iGoldPerCity >= iMinGold :
				return prevVaultWithMinGold
			prevVaultWithMinGold = eVault, iMinGold
		assert False, iGoldPerCity # One of the vaults should have iMinGold == 0




instance = None
def getInstance() :
	# type: () -> FfHDefines
	global instance
	if instance is None :
		instance = FfHDefines()
	return instance