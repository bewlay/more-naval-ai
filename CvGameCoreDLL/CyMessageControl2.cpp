#include "CvGameCoreDLL.h"
#include "CyMessageControl2.h"
#include "CvGlobals.h"


CyMessageControl2::CyMessageControl2()
{
}
void CyMessageControl2::sendDoCommand(int iUnitID, int eCommand, int iData1, int iData2, bool bAlt)
{
	//gDLL->sendDoCommand(iUnitID, (CommandTypes)eCommand, iData1, iData2, bAlt);
}//could do sendPushMission
