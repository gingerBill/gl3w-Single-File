# gl3w Single File Verions
Original gl3w.h - https://github.com/skaslev/gl3w
This version is modified so that the generated files are in the same directory as the `gl3w_gen.py`, merges the `gl3w.h` and `gl3w.c` files into one, and adds better namespacing for global variables and procedures.

# API Reference

	#define GL3W_IMPLEMENTATION

in EXACLY _one_ C or C++ file that includes this header, BEFORE the include,
like this:

	#define GL3W_IMPLEMENTATION
	#include "gl3w.h"

All other files should just `#include "gl3w.h"` without the `#define`.

The API consists of three procedures:

	int gl3w_init(void);
> Initalizes the library. Should be called once after an OpenGL context has been created. Returns `0` when gl3w was initialized successfully, `-1` is there was an error.

	int gl3w_is_supported(int major, int minor);
	
> Return `1` when OpenGL core profile version _major.minor_ is available and `0` otherwise.

	GL3WglProc gl3w_get_proc_address(char const *proc);
> Returns the address of an OpenGL extensions procedure.

## License
[gl3w](https://github.com/skaslev/gl3w/blob/master/UNLICENSE) is in the public domain.
