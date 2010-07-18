#ifndef CyMessageControl2_h
#define CyMessageControl2_h
//
// Python wrapper class for some extra net stuff
// SINGLETON
// updated 6-5

//#include "CvEnums.h"


class CyMessageControl2
{
public:
	CyMessageControl2();
	void sendDoCommand(int iUnitID, int /*CommandTypes*/ eCommand, int iData1, int iData2, bool bAlt);
};
#endif	// #ifndef CyMessageControl2_h
