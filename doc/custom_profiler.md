# CUSTOM_PROFILER by lfgr #


CUSTOM_PROFILER is a replacement of the CIV4 profiler, because I couldn't get the latter
working reliably.


### USAGE ###

You need to compile with the /DCUSTOM_PROFILER as well as /DFP_PROFILE_ENABLE.
The "Profile" configuration of the included Makefile does this. Its output, found in
custom_profile.log in the Logs folder is slightly simpler than that of Firaxis' profiler.
The first column shows the total time spent in the profiled function/block in ms. The
second column shows the number of calls to the profiled function/block. The third column
shows the number of unclosed calls, i.e. the number of calls where the profiling wasn't
ended for that particular sample. The fourth column is the name of the profiled
function/block. The functions/blocks are sorted by total time. The special "Turn" sample
measures the whole time (between starting and stopping profiling in this turn).


### MERGING ###

All code is inside CUSTOM_PROFILER-#ifdefs. Make sure to also merge the #ifndef and #else
which disable the Firaxis profiler.

### CREDITS ###

CUSTOM_PROFILER was inspired by Koshling's custom C2C profiler. I also used some of
Koshing's code.
