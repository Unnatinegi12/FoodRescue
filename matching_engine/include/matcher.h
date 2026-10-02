#pragma once

#include <string>
#include <vector>

namespace foodrescue {

struct Donation {
    int id;
    std::string food_type;
    double quantity_kg;
    std::string city;
    std::string expiry_time;
    bool is_vegetarian;
};

struct NGO {
    int id;
    std::string name;
    std::string city;
    double capacity_kg;
    bool accepts_non_veg;
};

struct Requirement {
    int id;
    int ngo_id;
    std::string food_type;
    double required_meals;
};

struct ScoreBreakdown {
    double food_type;
    double quantity;
    double location;
    double expiry;
    double capacity;

    double total() const;
};

struct Match {
    int ngo_id;
    std::string ngo_name;
    int requirement_id;
    double match_score;
    ScoreBreakdown breakdown;
};

ScoreBreakdown score_match(
    const Donation& donation,
    const NGO& ngo,
    const Requirement& requirement
);

std::vector<Match> rank_candidates(
    const Donation& donation,
    const std::vector<NGO>& ngos,
    const std::vector<Requirement>& requirements
);

}