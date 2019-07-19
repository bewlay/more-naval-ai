#include "CvGameCoreDLL.h"

#include "CvGameCoreDLLUndefNew.h"

#include <algorithm>
#include <new>

#include "CvGlobals.h"
#include "FProfiler.h"
#include "CvDLLInterfaceIFaceBase.h"

//
// operator global new and delete override for gamecore DLL 
//
void *__cdecl operator new(size_t size)
{
	if (gDLL)
	{
		return gDLL->newMem(size, __FILE__, __LINE__);
	}
	return malloc(size);
}

void __cdecl operator delete (void *p)
{
	if (gDLL)
	{
		gDLL->delMem(p, __FILE__, __LINE__);
	}
	else
	{
		free(p);
	}
}

void* operator new[](size_t size)
{
	if (gDLL)
		return gDLL->newMemArray(size, __FILE__, __LINE__);
	return malloc(size);
}

void operator delete[](void* pvMem)
{
	if (gDLL)
	{
		gDLL->delMemArray(pvMem, __FILE__, __LINE__);
	}
	else
	{
		free(pvMem);
	}
}

void *__cdecl operator new(size_t size, char* pcFile, int iLine)
{
	return gDLL->newMem(size, pcFile, iLine);
}

void *__cdecl operator new[](size_t size, char* pcFile, int iLine)
{
	return gDLL->newMem(size, pcFile, iLine);
}

void __cdecl operator delete(void* pvMem, char* pcFile, int iLine)
{
	gDLL->delMem(pvMem, pcFile, iLine);
}

void __cdecl operator delete[](void* pvMem, char* pcFile, int iLine)
{
	gDLL->delMem(pvMem, pcFile, iLine);
}


void* reallocMem(void* a, unsigned int uiBytes, const char* pcFile, int iLine)
{
	return gDLL->reallocMem(a, uiBytes, pcFile, iLine);
}

unsigned int memSize(void* a)
{
	return gDLL->memSize(a);
}

// BUG - EXE/DLL Paths - start
HANDLE dllModule = NULL;
// BUG - EXE/DLL Paths - end

BOOL APIENTRY DllMain(HANDLE hModule, 
					  DWORD  ul_reason_for_call, 
					  LPVOID lpReserved)
{
	switch( ul_reason_for_call ) {
	case DLL_PROCESS_ATTACH:
		{

// BUG - EXE/DLL Paths - start
		dllModule = hModule;

#ifdef _DEBUG
/************************************************************************************************/
/* Afforess	                  Start		 07/30/10                                               */
/*                                                                                              */
/*                                                                                              */
/************************************************************************************************/
//Irritating, and meaningless.
//	MessageBox(0, "DLL attached", "Message", 0);
/************************************************************************************************/
/* Afforess	                     END                                                            */
/************************************************************************************************/
#endif
// BUG - EXE/DLL Paths - end

		// The DLL is being loaded into the virtual address space of the current process as a result of the process starting up 
		OutputDebugString("DLL_PROCESS_ATTACH\n");

		// set timer precision
		MMRESULT iTimeSet = timeBeginPeriod(1);		// set timeGetTime and sleep resolution to 1 ms, otherwise it's 10-16ms
		FAssertMsg(iTimeSet==TIMERR_NOERROR, "failed setting timer resolution to 1 ms");
		}
		break;
	case DLL_THREAD_ATTACH:
		// OutputDebugString("DLL_THREAD_ATTACH\n");
		break;
	case DLL_THREAD_DETACH:
		// OutputDebugString("DLL_THREAD_DETACH\n");
		break;
	case DLL_PROCESS_DETACH:

// BUG - EXE/DLL Paths - start
		dllModule = NULL;
// BUG - EXE/DLL Paths - end

		OutputDebugString("DLL_PROCESS_DETACH\n");
		timeEndPeriod(1);
		GC.setDLLIFace(NULL);
		break;
	}
	
	return TRUE;	// success
}

#ifdef CUSTOM_PROFILER
namespace custom_profiler
{
	std::map<std::string, ProfileSample*> samples;
	LARGE_INTEGER measurementFreq;

	// Called when a sample is created
	void registerSample( ProfileSample* pSample )
	{
		samples[std::string( pSample->Name )] = pSample;
	}

	// Start measurement for with the sample
	void beginSample( ProfileSample* pSample )
	{
		// TODO: performance hit to large?
		if( samples.find( std::string( pSample->Name ) ) == samples.end() )
		{
			registerSample( pSample );
		}

		pSample->ProfileInstances++;
		pSample->OpenProfiles++;
	
		LARGE_INTEGER time;
		QueryPerformanceCounter( &time );
		pSample->StartTime = time.QuadPart;
	}

	void endSample( ProfileSample* pSample )
	{
		pSample->OpenProfiles--;
	
		LARGE_INTEGER time;
		QueryPerformanceCounter( &time );
		pSample->Accumulator += time.QuadPart - pSample->StartTime;
	}

	void startProfiling()
	{
		for( std::map<std::string, ProfileSample*>::iterator it = samples.begin();
			it != samples.end(); it++ )
		{
			it->second->ProfileInstances = 0;
			it->second->OpenProfiles = 0;
			it->second->Accumulator = 0;
		}
	}

	void stopProfiling()
	{
		CvString buffer; // For formatting strings
		
		// Get tick frequency.
		QueryPerformanceFrequency( &measurementFreq );
		if( measurementFreq.QuadPart == 0 )
		{
			measurementFreq.QuadPart = 1;
			gDLL->logMsg( "custom_profile.log", "Unknown frequency!", false, false );
		}
		
		std::vector<ProfileSample*> vpSamples;
		for( std::map<std::string, ProfileSample*>::iterator it = samples.begin();
			it != samples.end(); it++ )
		{
			vpSamples.push_back( it->second );
		}
		
		// Sort vpSamples by time (descending) with insertionsort
		for( size_t i = 1; i < vpSamples.size(); i++ )
		{
			for( size_t j = i; j > 0; j-- )
			{
				if( vpSamples.at( j-1 )->Accumulator < vpSamples.at( j )->Accumulator )
				{
					std::swap( vpSamples.at(j-1), vpSamples.at(j) );
				}
				else
				{
					break;
				}
			}		
		}

		gDLL->logMsg( "custom_profile.log", "-----------------------------------", false, false );
		gDLL->logMsg( "custom_profile.log", "total time - # called - # unclosed calls - name", false, false );
		buffer.Format( "%d samples", samples.size() );
		gDLL->logMsg( "custom_profile.log", buffer.c_str() );
		for( size_t i = 0; i < vpSamples.size(); i++ )
		{
			buffer.Format( "%7ld\t%7u\t%3d\t%s",
				(long) (vpSamples.at(i)->Accumulator * 1000 / measurementFreq.QuadPart), // ms
				vpSamples.at(i)->ProfileInstances,
				vpSamples.at(i)->OpenProfiles,
				vpSamples.at(i)->Name );
			gDLL->logMsg( "custom_profile.log", buffer.c_str(), false, false );
		}
	}
	
	// Special "total turn time" sample
	ProfileSample turnSample( "Turn" );
	
} // end namespace custom_profiler
#endif // CUSTOM_PROFILER

//
// enable dll profiler if necessary, clear history
//
void startProfilingDLL()
{
#ifdef CUSTOM_PROFILER
	if( GC.isDLLProfilerEnabled() || GC.getDefineINT( "FORCE_ENABLE_CUSTOM_PROFILER", 1 ) )
	{
		custom_profiler::startProfiling();
		custom_profiler::beginSample( &custom_profiler::turnSample );
	}
#else
	if (GC.isDLLProfilerEnabled())
	{
		gDLL->ProfilerBegin();
	}
#endif
}

//
// dump profile stats on-screen
// CUSTOM_PROFILER logs profile stats to custom_profile.log
//
void stopProfilingDLL()
{
#ifdef CUSTOM_PROFILER
	if( GC.isDLLProfilerEnabled() || GC.getDefineINT( "FORCE_ENABLE_CUSTOM_PROFILER", 1 ) )
	{
		custom_profiler::endSample( &custom_profiler::turnSample );
		custom_profiler::stopProfiling();
	}
#else
	if (GC.isDLLProfilerEnabled())
	{
		gDLL->ProfilerEnd();
	}
#endif
}
