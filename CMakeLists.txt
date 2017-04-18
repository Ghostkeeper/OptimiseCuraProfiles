#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

cmake_minimum_required(VERSION 2.8)
project(OptimiseCuraProfiles)
set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")

find_package(Python REQUIRED)

option(BUILD_TESTING "Generate a target for automatically testing correctness of the code." TRUE)
if(BUILD_TESTING)
    enable_testing()

    add_test(NAME optimise COMMAND ${PYTHON_EXECUTABLE} -m unittest tests.test_optimise WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
    set_tests_properties(optimise PROPERTIES ENVIRONMENT PYTHONPATH=${CMAKE_SOURCE_DIR})
endif()