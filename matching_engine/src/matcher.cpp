#include "../include/matcher.h"

#include <algorithm>
#include <cmath>
#include <map>

namespace foodrescue {

double ScoreBreakdown::total() const {
    return food_type + quantity + location + expiry + capacity;
}

static bool same_city(const std::string& a, const std::string& b) {
    return a == b;
}

ScoreBreakdown score_match(
    const Donation& donation,
    const NGO& ngo,
    const Requirement& requirement
) {
    ScoreBreakdown score{0, 0, 0, 0, 0};

    // Food type must match.
    if (donation.food_type != requirement.food_type) {
        return score;
    }

    // Vegetarian NGO cannot receive non-vegetarian food.
    if (!donation.is_vegetarian && !ngo.accepts_non_veg) {
        return score;
    }

    // Required quantity must be positive.
    if (requirement.required_meals <= 0) {
        return score;
    }

    // NGO capacity must be sufficient.
    if (donation.quantity_kg > ngo.capacity_kg) {
        return score;
    }

    // Food type: 40 points.
    score.food_type = 40;

    // Quantity: 20 points.
    score.quantity =
        std::min(20.0,
                 (donation.quantity_kg /
                  requirement.required_meals) * 20.0);

    // Location: 20 points.
    if (same_city(donation.city, ngo.city)) {
        score.location = 20;
    }

    // Expiry: 10 points.
    // Actual expiry handling is performed by the Python service,
    // while the C++ engine receives already-valid candidates.
    score.expiry = 10;

    // Capacity: 10 points.
    double capacity_ratio =
        donation.quantity_kg / ngo.capacity_kg;

    if (capacity_ratio <= 0.5) {
        score.capacity = 10;
    } else {
        score.capacity = 5;
    }

    return score;
}

std::vector<Match> rank_candidates(
    const Donation& donation,
    const std::vector<NGO>& ngos,
    const std::vector<Requirement>& requirements
) {
    std::map<int, Match> best_per_ngo;

    for (const auto& requirement : requirements) {
        for (const auto& ngo : ngos) {

            if (ngo.id != requirement.ngo_id) {
                continue;
            }

            ScoreBreakdown breakdown =
                score_match(donation, ngo, requirement);

            double total = breakdown.total();

            if (total <= 0) {
                continue;
            }

            Match candidate{
                ngo.id,
                ngo.name,
                requirement.id,
                total,
                breakdown
            };

            auto it = best_per_ngo.find(ngo.id);

            if (it == best_per_ngo.end() ||
                candidate.match_score > it->second.match_score) {
                best_per_ngo[ngo.id] = candidate;
            }
        }
    }

    std::vector<Match> results;

    for (const auto& pair : best_per_ngo) {
        results.push_back(pair.second);
    }

    std::sort(
        results.begin(),
        results.end(),
        [](const Match& a, const Match& b) {
            if (a.match_score != b.match_score) {
                return a.match_score > b.match_score;
            }

            return a.ngo_id < b.ngo_id;
        }
    );

    return results;
}

}