#include "../include/matcher.h"
#include "../include/nlohmann/json.hpp"

#include <iostream>
#include <string>
#include <vector>

using json = nlohmann::json;
using namespace foodrescue;

static Donation parse_donation(const json& j) {
    return {
        j.at("id").get<int>(),
        j.at("food_type").get<std::string>(),
        j.at("quantity_kg").get<double>(),
        j.at("city").get<std::string>(),
        j.at("expiry_time").get<std::string>(),
        j.at("is_vegetarian").get<bool>()
    };
}

static NGO parse_ngo(const json& j) {
    return {
        j.at("id").get<int>(),
        j.at("name").get<std::string>(),
        j.at("city").get<std::string>(),
        j.at("capacity_kg").get<double>(),
        j.at("accepts_non_veg").get<bool>()
    };
}

static Requirement parse_requirement(const json& j) {
    return {
        j.at("id").get<int>(),
        j.at("ngo_id").get<int>(),
        j.at("food_type").get<std::string>(),
        j.at("required_meals").get<double>()
    };
}

int main() {
    try {
        json input;
        std::cin >> input;

        Donation donation = parse_donation(input.at("donation"));

        std::vector<NGO> ngos;
        for (const auto& item : input.at("ngos")) {
            ngos.push_back(parse_ngo(item));
        }

        std::vector<Requirement> requirements;
        for (const auto& item : input.at("requirements")) {
            requirements.push_back(parse_requirement(item));
        }

        auto matches =
            rank_candidates(donation, ngos, requirements);

        json output;
        output["matches"] = json::array();

        for (const auto& match : matches) {
            output["matches"].push_back({
                {"ngo_id", match.ngo_id},
                {"ngo_name", match.ngo_name},
                {"requirement_id", match.requirement_id},
                {"match_score", match.match_score},
                {"breakdown", {
                    {"food_type", match.breakdown.food_type},
                    {"quantity", match.breakdown.quantity},
                    {"location", match.breakdown.location},
                    {"expiry", match.breakdown.expiry},
                    {"capacity", match.breakdown.capacity}
                }}
            });
        }

        std::cout << output.dump() << std::endl;

    } catch (const std::exception& e) {
        std::cerr << "Matcher error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}