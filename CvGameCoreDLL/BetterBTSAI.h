#pragma once

#ifndef BETTERBTSAI_H
#define BETTERBTSAI_H

// AI decision making logging

// Log levels:
// 0 - None
// 1 - Important decisions only
// 2 - Many decisions
// 3 - All logging
#if defined(LOG_AI_ALL)
#ifndef LOG_AI
#define LOG_AI
#endif
#define gPlayerLogLevel 3
#define gTeamLogLevel   3
#define gCityLogLevel   3
#define gUnitLogLevel   3
#elif defined(LOG_AI)
#define gPlayerLogLevel 2
#define gTeamLogLevel   2
#define gCityLogLevel   2
#define gUnitLogLevel   2
#else
#define gPlayerLogLevel 0
#define gTeamLogLevel   0
#define gCityLogLevel   0
#define gUnitLogLevel   0
#endif

// Special logging
#ifdef LOG_AI
// Enable these manually
#define gBonusValueLogLevel 0 // >=1 logs bonus value calculation
#define gPromoteLogLevel 0 // >=1 logs promotion values when AI promotes a units
#else
#define gBonusValueLogLevel 0
#define gPromoteLogLevel 0
#endif


void logBBAI(char* format, ... );

#endif  //BETTERBTSAI_H