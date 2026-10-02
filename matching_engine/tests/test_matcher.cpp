#include "../include/matcher.h"

#include <cassert>
#include <cmath>
#include <iostream>
#include <vector>

using namespace foodrescue;

bool almost_equal(double a, double b) {
    return std::abs(a - b) < 0.01;
}

int main() {

    Donation donation{
        1,
        "rice",
        50.0,
        "Jaipur",
        "2026-10-03T18:00:00",
        true
    };

    NGO ngo{
        1,
        "Food NGO",
        "Jaipur",
        100.0,
        false
    };

    Requirement requirement{
        1,
        1,
        "rice",
        50.0
    };

    // Test ideal match
    auto score = score_match(
        donation,
        ngo,
        requirement
    );

    assert(almost_equal(score.food_type, 40));
    assert(almost_equal(score.quantity, 20));
    assert(almost_equal(score.location, 20));
    assert(almost_equal(score.expiry, 10));
    assert(almost_equal(score.capacity, 10));
    assert(almost_equal(score.total(), 100));

    std::cout << "Ideal match test passed\n";

    // Test food type mismatch
    Requirement wrong_food{
        2,
        1,
        "bread",
        50.0
    };

    auto mismatch = score_match(
        donation,
        ngo,
        wrong_food
    );

    assert(almost_equal(mismatch.total(), 0));

    std::cout << "Food type mismatch test passed\n";

    // Test capacity rejection
    NGO small_ngo{
        2,
        "Small NGO",
        "Jaipur",
        20.0,
        false
    };

    Requirement small_requirement{
        3,
        2,
        "rice",
        50.0
    };

    auto capacity_result = score_match(
        donation,
        small_ngo,
        small_requirement
    );

    assert(almost_equal(capacity_result.total(), 0));

    std::cout << "Capacity rejection test passed\n";

    // Test ranking
    NGO ngo2{
        2,
        "Other NGO",
        "Delhi",
        100.0,
        false
    };

    Requirement requirement2{
        2,
        2,
        "rice",
        50.0
    };

    std::vector<NGO> ngos = {ngo, ngo2};

    std::vector<Requirement> requirements = {
        requirement,
        requirement2
    };

    auto matches = rank_candidates(
        donation,
        ngos,
        requirements
    );

    assert(matches.size() == 2);
    assert(matches[0].ngo_id == 1);
    assert(matches[0].match_score > matches[1].match_score);

    std::cout << "Ranking test passed\n";

    std::cout << "All C++ matcher tests passed!\n";

    return 0;
}