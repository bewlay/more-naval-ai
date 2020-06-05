"""
Definitions for WIDGET_PYTHON help
"""

WIDGET_HELP_CLASS_REVOLUTION_SCREEN = 10


def getHelp( iData1, iData2 ) :
	# type: (int, int) -> unicode
	iHelpClass = iData1 // 1000
	iData1 = iData1 % 1000

	if iHelpClass == WIDGET_HELP_CLASS_REVOLUTION_SCREEN :
		import CvRevolutionScreen # Avoid circular dependency
		return CvRevolutionScreen.getHelp( iData1, iData2 )
	else :
		return u""
