# gl3w Single File Verions
Original gl3w.h - https://github.com/skaslev/gl3w

### You MUST

	#define GL3W_IMPLEMENTATION

in EXACLY _one_ C or C++ file that includes this header, BEFORE the include,
like this:

	#define GL3W_IMPLEMENTATION
	#include "gl3w.h"

All other files should just #include "gl3w.h" without the #define.
