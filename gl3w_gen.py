#!/usr/bin/env python

#   This file is part of gl3w, hosted at https://github.com/skaslev/gl3w
#
#   This is free and unencumbered software released into the public domain.
#
#   Anyone is free to copy, modify, publish, use, compile, sell, or
#   distribute this software, either in source code form or as a compiled
#   binary, for any purpose, commercial or non-commercial, and by any
#   means.
#
#   In jurisdictions that recognize copyright laws, the author or authors
#   of this software dedicate any and all copyright interest in the
#   software to the public domain. We make this dedication for the benefit
#   of the public at large and to the detriment of our heirs and
#   successors. We intend this dedication to be an overt act of
#   relinquishment in perpetuity of all present and future rights to this
#   software under copyright law.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#   MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#   IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
#   OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#   ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#   OTHER DEALINGS IN THE SOFTWARE.

# Allow Python 2.6+ to use the print() function
from __future__ import print_function

import re
import os

# Try to import Python 3 library urllib.request
# and if it fails, fall back to Python 2 urllib2
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

# UNLICENSE copyright header
UNLICENSE = br'''/*

    This file is a modified version of gl3w_gen.py, part of gl3w
    (hosted at https://github.com/skaslev/gl3w)

    This is free and unencumbered software released into the public domain.

    Anyone is free to copy, modify, publish, use, compile, sell, or
    distribute this software, either in source code form or as a compiled
    binary, for any purpose, commercial or non-commercial, and by any
    means.

    In jurisdictions that recognize copyright laws, the author or authors
    of this software dedicate any and all copyright interest in the
    software to the public domain. We make this dedication for the benefit
    of the public at large and to the detriment of our heirs and
    successors. We intend this dedication to be an overt act of
    relinquishment in perpetuity of all present and future rights to this
    software under copyright law.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
    IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
    OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
    OTHER DEALINGS IN THE SOFTWARE.

============================================================================
    You MUST

        #define GL3W_IMPLEMENTATION

    in EXACLY _one_ C or C++ file that includes this header, BEFORE the include,
    like this:

        #define GL3W_IMPLEMENTATION
        #include "gl3w.h"

    All other files should just #include "gl3w.h" without the #define.

*/

'''


# Download glcorearb.h
if not os.path.exists('glcorearb.h'):
    print('Downloading glcorearb.h...')
    web = urllib2.urlopen('https://www.opengl.org/registry/api/GL/glcorearb.h')
    with open('glcorearb.h', 'wb') as f:
        f.writelines(web.readlines())
else:
    print('Reusing glcorearb.h...')

# Parse function names from glcorearb.h
print('Parsing glcorearb.h header...')
procs = []
p = re.compile(r'GLAPI.*APIENTRY\s+(\w+)')
with open('glcorearb.h', 'r') as f:
    for line in f:
        m = p.match(line)
        if m:
            procs.append(m.group(1))
procs.sort()

def proc_t(proc):
    return { 'p': proc,
             'p_s': 'gl3w' + proc[2:],
             'p_t': 'PFN' + proc.upper() + 'PROC' }

# Generate gl3w.h
print('Generating gl3w.h...')
with open('gl3w.h', 'wb') as f:
    f.write(UNLICENSE)
    f.write(br'''#ifndef __gl3w_h_
#define __gl3w_h_

#include "glcorearb.h"

#ifndef __gl_h_
#define __gl_h_
#endif

#ifdef __cplusplus
extern "C" {
#endif

typedef void (*GL3WglProc)(void);

/* gl3w api */
int gl3w_init(void);
int gl3w_is_supported(int major, int minor);
GL3WglProc gl3w_get_proc_address(char const *proc);

/* OpenGL functions */
''')
    for proc in procs:
        f.write('extern {0[p_t]: <52} {0[p_s]};\n'.format(proc_t(proc)).encode("utf-8"))
    f.write(b'\n')
    for proc in procs:
        f.write('#define {0[p]: <45} {0[p_s]}\n'.format(proc_t(proc)).encode("utf-8"))
    f.write(br'''
#ifdef __cplusplus
}
#endif

#endif

#if defined(GL3W_IMPLEMENTATION) && !defined(GL3W_IMPLEMENTATION_DONE)
#define GL3W_IMPLEMENTATION_DONE

#ifdef _WIN32

#define WIN32_LEAN_AND_MEAN 1
#define WIN32_MEAN_AND_LEAN 1
#include <windows.h>

static HMODULE gl3w__libgl;

static void gl3w__open_libgl (void) { gl3w__libgl = LoadLibraryA("opengl32.dll"); }
static void gl3w__close_libgl(void) { FreeLibrary(gl3w__libgl); }

static GL3WglProc gl3w__get_proc(char const *proc)
{
	GL3WglProc res;

	res = (GL3WglProc) wglGetProcAddress(proc);
	if (!res)
		res = (GL3WglProc) GetProcAddress(gl3w__libgl, proc);
	return res;
}

#elif defined(__APPLE__) || defined(__APPLE_CC__)

#include <Carbon/Carbon.h>

CFBundleRef gl3w__bundle;
CFURLRef gl3w__bundleURL;

static void gl3w__open_libgl(void)
{
	gl3w__bundleURL = CFURLCreateWithFileSystemPath(kCFAllocatorDefault,
		CFSTR("/System/Library/Frameworks/OpenGL.framework"),
		kCFURLPOSIXPathStyle, true);

	gl3w__bundle = CFBundleCreate(kCFAllocatorDefault, gl3w__bundleURL);
	assert(gl3w__bundle != NULL);
}

static void gl3w__close_libgl(void)
{
	CFRelease(gl3w__bundle);
	CFRelease(gl3w__bundleURL);
}

static GL3WglProc gl3w__get_proc(char const *proc)
{
	GL3WglProc res;

	CFStringRef procname = CFStringCreateWithCString(kCFAllocatorDefault, proc,
		kCFStringEncodingASCII);
	res = (GL3WglProc) CFBundleGetFunctionPointerForName(gl3w__bundle, procname);
	CFRelease(procname);
	return res;
}

#else

#include <dlfcn.h>
#include <GL/glx.h>

static void *gl3w__libgl;
static PFNGLXGETPROCADDRESSPROC gl3w__glx_get_proc_address;

static void gl3w__open_libgl(void)
{
	gl3w__libgl = dlopen("libGL.so.1", RTLD_LAZY | RTLD_GLOBAL);
	gl3w__glx_get_proc_address = (PFNGLXGETPROCADDRESSPROC) dlsym(gl3w__libgl, "glXGetProcAddressARB");
}

static void gl3w__close_libgl(void) { dlclose(gl3w__libgl); }

static GL3WglProc gl3w__get_proc(char const *proc)
{
	GL3WglProc res;

	res = (GL3WglProc) gl3w__glx_get_proc_address((const GLubyte *) proc);
	if (!res)
		res = (GL3WglProc) dlsym(gl3w__libgl, proc);
	return res;
}

#endif

static struct {
	int major, minor;
} gl3w__version;

static int gl3w__parse_version(void)
{
	if (!glGetIntegerv)
		return -1;

	glGetIntegerv(GL_MAJOR_VERSION, &gl3w__version.major);
	glGetIntegerv(GL_MINOR_VERSION, &gl3w__version.minor);

	if (gl3w__version.major < 3)
		return -1;
	return 0;
}

static void gl3w__load_procs(void);

int gl3w_init(void)
{
	gl3w__open_libgl();
	gl3w__load_procs();
	gl3w__close_libgl();
	return gl3w__parse_version();
}

int gl3w_is_supported(int major, int minor)
{
	if (major < 3)
		return 0;
	if (gl3w__version.major == major)
		return gl3w__version.minor >= minor;
	return gl3w__version.major >= major;
}

GL3WglProc gl3w_get_proc_address(char const *proc)
{
	return gl3w__get_proc(proc);
}

''')
    for proc in procs:
        f.write('{0[p_t]: <52} {0[p_s]};\n'.format(proc_t(proc)).encode("utf-8"))
    f.write(br'''
static void gl3w__load_procs(void)
{
''')
    for proc in procs:
        f.write('\t{0[p_s]} = ({0[p_t]}) gl3w__get_proc("{0[p]}");\n'.format(proc_t(proc)).encode("utf-8"))
    f.write(b'''}


#endif /* GL3W_IMPLEMENTATION */
''')
