// ---------------------------------------------------------------------------------------------------
// FProfiler - DLL wrapper to FireEngine/FProfiler.cpp
//
// Author: tomw
//---------------------------------------------------------------------------------------------------------------------

#ifndef	__PROFILE_H__
#define __PROFILE_H__
#pragma once


#include "CvDLLEntityIFaceBase.h"
#include "CvDLLUtilityIFaceBase.h"
#include "CvGlobals.h"	// for gDLL

#ifndef FINAL_RELEASE
#ifndef FP_PROFILE_ENABLE 
	#define FP_PROFILE_ENABLE 
#endif
#endif

#ifdef CUSTOM_PROFILER
namespace custom_profiler
{
	void beginSample( ProfileSample* pSample );
	void endSample( ProfileSample* pSample );
}
#endif

//NOTE: This struct must be identical ot the same struct in  FireEngine/FProfiler.h
//---------------------------------------------------------------------------------------------------------------------
struct ProfileSample
{
	ProfileSample(char *name) {
		strcpy(Name, name);
#ifdef CUSTOM_PROFILER
		bRegistered = false;
#else
		Added=false;
		Parent=-1;
#endif
	}

	char	Name[256];						// Name of sample;

	unsigned int	ProfileInstances;		// # of times ProfileBegin Called
	int				OpenProfiles;			// # of time ProfileBegin called w/o ProfileEnd
#ifdef CUSTOM_PROFILER
	LONGLONG StartTime; // The current open profile start time
	LONGLONG Accumulator; // All samples this frame added together
	bool bRegistered; // True if this sample is registered at the profiler
#else
	double			StartTime;				// The current open profile start time
	double			Accumulator;			// All samples this frame added together

	// Not used by CUSTOM_PROFILER
	double			ChildrenSampleTime;		// Time taken by all children
	unsigned int	NumParents;				// Number of profile Parents
	bool			Added;					// true when added to the list
	int				Parent;
#endif // not CUSTOM_PROFILER
};

//---------------------------------------------------------------------------------------------------------------------
// Allows us to Profile based on Scope, to limit intrusion into code.
// Simply use PROFLE("funcname") instead having to insert begin()/end() pairing
class CProfileScope
{
public:
	CProfileScope() { bValid= false;};
	CProfileScope(ProfileSample *pSample)
	{
		m_pSample = pSample;
		bValid = true;
#ifdef CUSTOM_PROFILER
		custom_profiler::beginSample( m_pSample );
#else
		gDLL->BeginSample(m_pSample);
#endif
	};
	~CProfileScope()
	{
		if(bValid )
		{
#ifdef CUSTOM_PROFILER
			custom_profiler::endSample( m_pSample );
#else
			gDLL->EndSample(m_pSample);
#endif
			bValid = false;
		}	
	};

private:
	bool bValid;
	ProfileSample *m_pSample;
};

//---------------------------------------------------------------------------------------------------------------------

// Main Interface for Profile
#ifdef FP_PROFILE_ENABLE				// Turn Profiling On or Off .. 
#define PROFILE(name)\
	static ProfileSample sample(name);\
	CProfileScope ProfileScope(&sample);		

//BEGIN & END macros:		Only needed if you don't want to use the scope macro above. 
// Macros must be in the same scope
#ifdef CUSTOM_PROFILER
#define PROFILE_BEGIN(name)\
	static ProfileSample sample__(name);\
	custom_profiler::beginSample(&sample__);

#define PROFILE_END()\
	custom_profiler::endSample(&sample__);
#else // not CUSTOM_PROFILER
#define PROFILE_BEGIN(name)\
	static ProfileSample sample__(name);\
	gDLL->BeginSample(&sample__);
#define PROFILE_END()\
	gDLL->EndSample(&sample__);
#endif

#define PROFILE_FUNC()\
	static ProfileSample sample(__FUNCTION__);\
	CProfileScope ProfileScope(&sample);	

#else
#define PROFILE(name)				// Remove profiling code
#define PROFILE_BEGIN(name)
#define PROFILE_END()
#define PROFILE_FUNC()
#endif


#endif //__PROFILE_H__


