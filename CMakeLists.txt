# This cmake script is heavily based on 
# https://github.com/Microsoft/vcpkg/blob/master/ports/libflac/CMakeLists.txt
# courtesy of the vcpkg project.

cmake_minimum_required(VERSION 2.6)
cmake_policy(SET CMP0005 NEW) # do not escape preprocessor defines

project(libflac)

include(CheckSymbolExists)
include(CheckIncludeFiles)
include(conanbuildinfo.cmake)

conan_basic_setup()

set(FLAC_SRC_DIR ${PROJECT_SOURCE_DIR}/sources)

file(GLOB LIBFLAC_SOURCES
    ${FLAC_SRC_DIR}/src/libFLAC/*.c)

if(WIN32)
  list(APPEND LIBFLAC_SOURCES 
    ${FLAC_SRC_DIR}/src/share/win_utf8_io/win_utf8_io.c)
else()
  list(REMOVE_ITEM LIBFLAC_SOURCES
    ${FLAC_SRC_DIR}/src/libFLAC/windows_unicode_filenames.c)
endif()

file(GLOB LIBFLACXX_SOURCES
    ${FLAC_SRC_DIR}/src/libFLAC++/*.cpp)

include_directories(${FLAC_SRC_DIR}/include)
include_directories(${FLAC_SRC_DIR}/src/libFLAC/include)

if(NOT ${CONAN_ARCH} MATCHES arm)
    add_definitions(-DFLAC__SSE_OS)
    add_definitions(-DFLAC__HAS_X86INTRIN)
endif()

if(${CONAN_ARCH} STREQUAL "x86")
    add_definitions(-DFLAC__CPU_IA32)
    add_definitions(-DFLAC__HAS_NASM)
    file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/nasm)
    foreach(ASM_SOURCE cpu_asm fixed_asm lpc_asm)
        execute_process(COMMAND nasm "-i${FLAC_SRC_DIR}/src/libFLAC/ia32/" -f win32 -d OBJ_FORMAT_win32 -f win32 
            -o "${CMAKE_BINARY_DIR}/nasm/${ASM_SOURCE}.obj" "${FLAC_SRC_DIR}/src/libFLAC/ia32/${ASM_SOURCE}.nasm"
            WORKING_DIRECTORY ${CMAKE_BINARY_DIR})
        list(APPEND LIBFLAC_SOURCES ${CMAKE_BINARY_DIR}/nasm/${ASM_SOURCE}.obj)
    endforeach()
elseif(${CONAN_ARCH} STREQUAL "x86_64")
    add_definitions(-DFLAC__CPU_X86_64)
    add_definitions(-DENABLE_64_BIT_WORDS)
endif()

check_symbol_exists(lround math.h HAVE_LROUND)
check_include_files(sys/param.h HAVE_SYSPARAM_H)

if (HAVE_LROUND)
  add_definitions(-DHAVE_LROUND)
endif()
if(HAVE_SYSPARAM_H)
  add_definitions(-DHAVE_SYS_PARAM_H)
endif()

if(CMAKE_BUILD_TYPE MATCHES Debug)
    add_definitions(-DFLAC__OVERFLOW_DETECT)
endif()

add_definitions(-DPACKAGE_VERSION="1.3.2")
add_definitions(-DFLAC__HAS_OGG)
add_definitions(-DFLAC__ALIGN_MALLOC_DATA) # 32 byte boundary
add_definitions(-D_CRT_SECURE_NO_WARNINGS)
add_definitions(-D_CRT_NONSTDC_NO_WARNINGS)

add_library(libFLAC ${LIBFLAC_SOURCES})
add_library(libFLACXX ${LIBFLACXX_SOURCES})

set_target_properties(libFLAC PROPERTIES OUTPUT_NAME flac)
set_target_properties(libFLACXX PROPERTIES OUTPUT_NAME flac++)

include_directories(${CONAN_INCLUDE_DIRS})
target_link_libraries(libFLAC ${CONAN_LIBS})
target_link_libraries(libFLACXX libFLAC)

if(BUILD_SHARED_LIBS)
    set_target_properties(libFLACXX PROPERTIES COMPILE_FLAGS -DFLACPP_API_EXPORTS)
    set_target_properties(libFLAC PROPERTIES COMPILE_FLAGS -DFLAC_API_EXPORTS)
else()
    add_definitions(-DFLAC__NO_DLL)
endif()

install(TARGETS libFLAC libFLACXX
    RUNTIME DESTINATION bin
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib)

if(NOT DEFINED LIBFLAC_SKIP_HEADERS)
    install(DIRECTORY ${FLAC_SRC_DIR}/include/FLAC/
        DESTINATION include/FLAC
        FILES_MATCHING PATTERN "*.h")
    install(DIRECTORY ${FLAC_SRC_DIR}/include/FLAC++/
        DESTINATION include/FLAC++
        FILES_MATCHING PATTERN "*.h")
endif()
