// OptDefines 03/2024 lfgr

#ifndef CVDEFINESCACHE_H_
#define CVDEFINESCACHE_H_

#pragma once

class CvDefinesCache {
public :
	void init(); // Called after reading defines from CvGlobalDefines.xml, etc.
	void init_delayed(); // Called after reading other info stuff

#include "CvDefines_fields.inc"
};

#endif /* CVDEFINESCACHE_H_ */
