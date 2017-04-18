#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

option(BUILD_PYTHON "Build the Python dependency from source. If you build this, the newly-built version will get used by Luna. If not, it will search for a pre-installed version on your system." FALSE)

if(BUILD_PYTHON)
	if(NOT PYTHON_FOUND)
		message(STATUS "Building Python from source.")
		if(MINGW)
			find_package(Git REQUIRED) #Both to check out the repository and to apply patches.
			include(ExternalProject)
			ExternalProject_Add(PythonMinGWPatches
				GIT_REPOSITORY https://github.com/Alexpux/MINGW-packages.git
				GIT_TAG a911df0cf055051abbdbcff9bc4e70121c2a2438
				CONFIGURE_COMMAND "" #Don't do anything with this but download it.
				BUILD_COMMAND ""
				INSTALL_COMMAND ""
				BUILD_IN_SOURCE 1
			)
			ExternalProject_Add(PythonCMakePatch
				GIT_REPOSITORY https://github.com/python-cmake-buildsystem/python-cmake-buildsystem
				GIT_TAG 39ccab04fc48d957f93d83f056e65a1dfb09d784
				CONFIGURE_COMMAND "" #Don't do anything with this but download it.
				BUILD_COMMAND ""
				INSTALL_COMMAND ""
				BUILD_IN_SOURCE 1
			)
			set(MINGW_PATCH_SOURCE ${CMAKE_CURRENT_BINARY_DIR}/PythonMinGWPatches-prefix/src/PythonMinGWPatches)
			set(CMAKE_PATCH_SOURCE ${CMAKE_CURRENT_BINARY_DIR}/PythonCMakePatch-prefix/src/PythonCMakePatch)
			set(PATCH_TARGET ${CMAKE_CURRENT_BINARY_DIR}/Python-prefix/src/Python)
			set(PATCH_PYTHON_FOR_MINGW
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0000-make-_sysconfigdata.py-relocatable.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0001-fix-_nt_quote_args-using-subprocess-list2cmdline.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0100-MINGW-BASE-use-NT-thread-model.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0110-MINGW-translate-gcc-internal-defines-to-python-platf.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0130-MINGW-configure-MACHDEP-and-platform-for-build.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0140-MINGW-preset-configure-defaults.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0150-MINGW-configure-largefile-support-for-windows-builds.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0160-MINGW-add-wincrypt.h-in-Python-random.c.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0170-MINGW-add-srcdir-PC-to-CPPFLAGS.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0180-MINGW-init-system-calls.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0190-MINGW-detect-REPARSE_DATA_BUFFER.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0200-MINGW-build-in-windows-modules-winreg.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0210-MINGW-determine-if-pwdmodule-should-be-used.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0220-MINGW-default-sys.path-calculations-for-windows-plat.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0230-MINGW-AC_LIBOBJ-replacement-of-fileblocks.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0240-MINGW-use-main-to-start-execution.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0250-MINGW-compiler-customize-mingw-cygwin-compilers.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0260-MINGW-compiler-enable-new-dtags.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0270-CYGWIN-issue13756-Python-make-fail-on-cygwin.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0290-issue6672-v2-Add-Mingw-recognition-to-pyport.h-to-al.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0300-MINGW-configure-for-shared-build.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0310-MINGW-dynamic-loading-support.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0320-MINGW-implement-exec-prefix.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0330-MINGW-ignore-main-program-for-frozen-scripts.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0340-MINGW-setup-exclude-termios-module.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0350-MINGW-setup-_multiprocessing-module.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0360-MINGW-setup-select-module.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0370-MINGW-setup-_ctypes-module-with-system-libffi.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0380-MINGW-defect-winsock2-and-setup-_socket-module.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0390-MINGW-exclude-unix-only-modules.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0400-MINGW-setup-msvcrt-and-_winapi-modules.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0410-MINGW-build-extensions-with-GCC.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0420-MINGW-use-Mingw32CCompiler-as-default-compiler-for-m.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0430-MINGW-find-import-library.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0440-MINGW-setup-_ssl-module.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0460-MINGW-generalization-of-posix-build-in-sysconfig.py.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0462-MINGW-support-stdcall-without-underscore.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0464-use-replace-instead-rename-to-avoid-failure-on-windo.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0470-MINGW-avoid-circular-dependency-from-time-module-dur.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0480-MINGW-generalization-of-posix-build-in-distutils-sys.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0490-MINGW-customize-site.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0500-add-python-config-sh.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0510-cross-darwin-feature.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0520-py3k-mingw-ntthreads-vs-pthreads.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0530-mingw-system-libffi.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0540-mingw-semicolon-DELIM.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0550-mingw-regen-use-stddef_h.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0555-msys-mingw-prefer-unix-sep-if-MSYSTEM.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0560-mingw-use-posix-getpath.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0565-mingw-add-ModuleFileName-dir-to-PATH.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0570-mingw-add-BUILDIN_WIN32_MODULEs-time-msvcrt.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0590-mingw-INSTALL_SHARED-LDLIBRARY-LIBPL.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0610-msys-cygwin-semi-native-build-sysconfig.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0620-mingw-sysconfig-like-posix.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0630-mingw-_winapi_as_builtin_for_Popen_in_cygwinccompiler.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0640-mingw-x86_64-size_t-format-specifier-pid_t.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0650-cross-dont-add-multiarch-paths-if-cross-compiling.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0660-mingw-use-backslashes-in-compileall-py.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0670-msys-convert_path-fix-and-root-hack.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0690-allow-static-tcltk.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0700-CROSS-avoid-ncursesw-include-path-hack.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0710-CROSS-properly-detect-WINDOW-_flags-for-different-nc.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0720-mingw-pdcurses_ISPAD.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0730-mingw-fix-ncurses-module.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0740-grammar-fixes.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0750-builddir-fixes.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0760-msys-monkeypatch-os-system-via-sh-exe.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0770-msys-replace-slashes-used-in-io-redirection.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0790-mingw-add-_exec_prefix-for-tcltk-dlls.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0800-mingw-install-layout-as-posix.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0810-remove_path_max.default.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0820-dont-link-with-gettext.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0830-ctypes-python-dll.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0840-gdbm-module-includes.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0850-use-gnu_printf-in-format.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0860-fix-_Py_CheckPython3-prototype.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0870-mingw-fix-ssl-dont-use-enum_certificates.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0890-mingw-build-optimized-ext.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0900-cygwinccompiler-dont-strip-modules-if-pydebug.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0910-fix-using-dllhandle-and-winver-mingw.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0920-mingw-add-LIBPL-to-library-dirs.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0930-mingw-w64-build-overlapped-module.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0940-mingw-w64-Also-define-_Py_BEGIN_END_SUPPRESS_IPH-when-Py_BUILD_CORE_MODULE.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0950-mingw-w64-XP3-compat-GetProcAddress-GetTickCount64.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0960-mingw-w64-XP3-compat-GetProcAddress-GetFinalPathNameByHandleW.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0970-Add-AMD64-to-sys-config-so-msvccompiler-get_build_version-works.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/0980-mingw-readline-features-skip.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/1010-install-msilib.patch
				COMMAND ${GIT_EXECUTABLE} apply --directory=${PATCH_TARGET} ${MINGW_PATCH_SOURCE}/mingw-w64-python3/1500-mingw-w64-dont-look-in-DLLs-folder-for-python-dll.patch
			)
			ExternalProject_Add(Python
				URL https://www.python.org/ftp/python/3.5.2/Python-3.5.2.tgz
				URL_HASH SHA512=248B3EF2DEFEE7C013E8AC7472B9F2828B1C5B07A2F091EAD46EBDF209BE11DD37911978B590367699D9FAD50F1B98B998BCEEC34FA8369BA30950D3A5FB596F
				DEPENDS PythonMinGWPatches PythonCMakePatch
				CONFIGURE_COMMAND ${CMAKE_COMMAND} -DCMAKE_INSTALL_PREFIX:PATH=${CMAKE_PATCH_SOURCE}
				PATCH_COMMAND ${PATCH_PYTHON_FOR_MINGW}
				BUILD_COMMAND "" #TODO
				INSTALL_COMMAND "" #TODO
			)
			set(PYTHON_EXECUTABLE ${CMAKE_INSTALL_PREFIX}/bin/python3)
			set(PYTHON_VERSION_STRING "3.5.2")
			set(PYTHON_VERSION_MAJOR 3)
			set(PYTHON_VERSION_MINOR 5)
			set(PYTHON_VERSION_PATCH 2)
		else()
			include(ExternalProject)
			ExternalProject_Add(Python
				URL https://www.python.org/ftp/python/3.5.2/Python-3.5.2.tgz
				URL_HASH SHA512=248B3EF2DEFEE7C013E8AC7472B9F2828B1C5B07A2F091EAD46EBDF209BE11DD37911978B590367699D9FAD50F1B98B998BCEEC34FA8369BA30950D3A5FB596F
				CONFIGURE_COMMAND ./configure --prefix=${CMAKE_INSTALL_PREFIX} --enable-shared --with-threads
				BUILD_IN_SOURCE 1
			)
			set(PYTHON_EXECUTABLE ${CMAKE_INSTALL_PREFIX}/bin/python3)
			set(PYTHON_VERSION_STRING "3.5.2")
			set(PYTHON_VERSION_MAJOR 3)
			set(PYTHON_VERSION_MINOR 5)
			set(PYTHON_VERSION_PATCH 2)
		endif()
		set(PYTHON_FOUND TRUE)
	endif()
else() #Just find it on the system.
	if(ARGC GREATER 1 AND ARGV1 STREQUAL "REQUIRED") #Pass the REQUIRED parameter on to the script. Perhaps also do other parameters?
		find_package(PythonInterp 3.4.0 REQUIRED)
	else()
		find_package(PythonInterp 3.4.0)
	endif()
	if(PYTHONINTERP_FOUND) #Rename this variable to our own conventions.
		set(PYTHON_FOUND TRUE)
	endif()
endif()