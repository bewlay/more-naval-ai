#include "CvGameCoreDLL.h"

#include "BetterBTSAI.h"

// AI decision making logging

void logBBAI(char* format, ... )
{
#ifdef LOG_AI
	static char buf[2048];
	_vsnprintf( buf, 2048-4, format, (char*)(&format+1) );
	TCHAR szFileName[1024];
	sprintf(szFileName, "BBAILog - %S.txt", GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getName());
	gDLL->logMsg(szFileName, buf, false, false);
#endif
}