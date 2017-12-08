project(test_package)
cmake_minimum_required(VERSION 2.8.11)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

file(GLOB SOURCE_FILES *.cpp)

add_executable(${PROJECT_NAME} ${SOURCE_FILES})
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
target_compile_definitions(${PROJECT_NAME} PRIVATE ${CONAN_COMPILE_DEFINITIONS})
message(STATUS ${CONAN_COMPILE_DEFINITIONS})
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
