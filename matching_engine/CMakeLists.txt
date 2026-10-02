cmake_minimum_required(VERSION 3.15)

project(foodrescue_matcher)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include_directories(include)

add_executable(matcher
    src/main.cpp
    src/matcher.cpp
)

add_executable(matcher_tests
    tests/test_matcher.cpp
    src/matcher.cpp
)