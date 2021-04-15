## FfHOptionsTab
##
## Tab for FfH-specific BUG options
##
## 05/2020
##
## Author: lfgr

import BugOptionsTab


class FallFromHeavenOptionsTab( BugOptionsTab.BugOptionsTab ) :
	"Fall from Heaven Options Screen Tab"
	
	def __init__( self, screen ) :
		BugOptionsTab.BugOptionsTab.__init__( self, "FfH", "FfH" )
	
	def create( self, screen ) :
		tab = self.createTab( screen )
		panel = self.createMainPanel( screen )
		column = self.addOneColumnLayout( screen, panel )
		
		self.addCheckbox( screen, column, "FfHUI__ShowLeaderDefeatPopup" )
		self.addCheckbox( screen, column, "FfHUI__AvoidAngryCitizensDefault" )
		self.addCheckbox( screen, column, "FfHUI__AvoidUnhealthyCitizensDefault" )
		self.addCheckbox( screen, column, "FfHUI__ShowKhazadVaultText" )
		self.addCheckbox( screen, column, "FfHUI__ShowSpellAddedPromotionHelp" )
		self.addCheckbox( screen, column, "FfHUI__ShowSpellCreatedUnitHelp" )
		self.addCheckbox( screen, column, "FfHUI__ShowSpellCreatedBuildingHelp" )
		self.addTextDropdown( screen, column, column, "FfHUI__PlotHelpNumUnits" )
