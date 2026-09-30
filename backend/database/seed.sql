-- =====================================================================
-- FoodRescue seed data (fictional). Run AFTER schema.sql.
-- Assumes freshly created tables so the explicit IDs below line up.
-- =====================================================================

USE foodrescue;

-- Users: 1-3 are donors, 4-8 are NGOs.
-- password_hash values are placeholders, NOT real hashes.
INSERT INTO users (user_id, email, password_hash, role) VALUES
(1, 'spiceroute@example.com',   'PLACEHOLDER_NOT_A_REAL_HASH', 'donor'),
(2, 'greenfield@example.com',   'PLACEHOLDER_NOT_A_REAL_HASH', 'donor'),
(3, 'shubhevents@example.com',  'PLACEHOLDER_NOT_A_REAL_HASH', 'donor'),
(4, 'asha@example.com',         'PLACEHOLDER_NOT_A_REAL_HASH', 'ngo'),
(5, 'annapurna@example.com',    'PLACEHOLDER_NOT_A_REAL_HASH', 'ngo'),
(6, 'hopeshelter@example.com',  'PLACEHOLDER_NOT_A_REAL_HASH', 'ngo'),
(7, 'balvikas@example.com',     'PLACEHOLDER_NOT_A_REAL_HASH', 'ngo'),
(8, 'sunrise@example.com',      'PLACEHOLDER_NOT_A_REAL_HASH', 'ngo');

INSERT INTO donors
  (donor_id, user_id, name, donor_type, contact_phone, address, city, latitude, longitude) VALUES
(1, 1, 'Spice Route Restaurant',     'restaurant',      '9000000001', '12 Example Marg, C-Scheme',       'Jaipur', 26.912400, 75.787300),
(2, 2, 'Greenfield College Canteen', 'canteen',         '9000000002', 'Greenfield Campus, Example Road', 'Jaipur', 26.845700, 75.815200),
(3, 3, 'Shubh Events & Catering',    'event_organizer', '9000000003', '45 Sample Nagar, Vaishali Nagar', 'Jaipur', 26.912800, 75.741900);

INSERT INTO ngos
  (ngo_id, user_id, name, contact_phone, address, city, latitude, longitude, capacity_meals, accepts_non_veg) VALUES
(1, 4, 'Asha Meals Foundation',   '9100000001', '7 Demo Street, Bani Park',         'Jaipur', 26.920000, 75.800000, 300, TRUE),
(2, 5, 'Annapurna Seva Trust',    '9100000002', '21 Sample Lane, Sanganer',         'Jaipur', 26.890000, 75.830000, 500, FALSE),
(3, 6, 'Hope Shelter Home',       '9100000003', '3 Example Colony, Civil Lines',  'Jaipur', 26.950000, 75.770000,  80, TRUE),
(4, 7, 'Bal Vikas Children Home', '9100000004', '18 Test Road, Mansarovar',         'Jaipur', 26.860000, 75.790000, 120, FALSE),
(5, 8, 'Sunrise Elder Care',      '9100000005', '9 Placeholder Path, Malviya Nagar','Jaipur', 26.900000, 75.750000, 60, TRUE);

INSERT INTO food_donations
  (donation_id, donor_id, food_type, description, dietary_type, quantity_meals, quantity_kg,
   pickup_address, city, latitude, longitude, prepared_at, expiry_time, status) VALUES

(1, 1, 'cooked_meals',
 'Dal, jeera rice and mixed vegetable curry',
 'veg', 60, 30.00,
 '12 Example Marg, C-Scheme', 'Jaipur', 26.912400, 75.787300,
 DATE_SUB(NOW(), INTERVAL 2 HOUR),
 DATE_ADD(NOW(), INTERVAL 4 HOUR),
 'available'),

(2, 1, 'cooked_meals',
 'Chicken biryani',
 'non_veg', 40, 20.00,
 '12 Example Marg, C-Scheme', 'Jaipur', 26.912400, 75.787300,
 DATE_SUB(NOW(), INTERVAL 1 HOUR),
 DATE_ADD(NOW(), INTERVAL 3 HOUR),
 'available'),

(3, 1, 'bakery',
 'Bread loaves and buns from the day''s baking',
 'veg', 50, 10.00,
 '12 Example Marg, C-Scheme', 'Jaipur', 26.912400, 75.787300,
 DATE_SUB(NOW(), INTERVAL 10 HOUR),
 DATE_ADD(NOW(), INTERVAL 14 HOUR),
 'available'),

(4, 2, 'cooked_meals',
 'Rajma chawal and roti',
 'veg', 120, 55.00,
 'Greenfield Campus, Example Road', 'Jaipur', 26.845700, 75.815200,
 DATE_SUB(NOW(), INTERVAL 1 HOUR),
 DATE_ADD(NOW(), INTERVAL 5 HOUR),
 'available'),

(5, 2, 'fruits_vegetables',
 'Seasonal fruits and cut vegetables',
 'veg', 80, 40.00,
 'Greenfield Campus, Example Road', 'Jaipur', 26.845700, 75.815200,
 DATE_SUB(NOW(), INTERVAL 6 HOUR),
 DATE_ADD(NOW(), INTERVAL 18 HOUR),
 'available'),

(6, 2, 'dairy',
 'Sealed curd cups',
 'veg', 100, 20.00,
 'Greenfield Campus, Example Road', 'Jaipur', 26.845700, 75.815200,
 DATE_SUB(NOW(), INTERVAL 12 HOUR),
 DATE_ADD(NOW(), INTERVAL 36 HOUR),
 'matched'),

(7, 3, 'cooked_meals',
 'Wedding buffet: paneer, dal, naan and rice',
 'veg', 300, 150.00,
 'Royal Garden Banquet, Example Bypass', 'Jaipur', 26.905500, 75.760200,
 DATE_SUB(NOW(), INTERVAL 3 HOUR),
 DATE_ADD(NOW(), INTERVAL 3 HOUR),
 'available'),

(8, 3, 'cooked_meals',
 'Mixed non-veg buffet leftovers',
 'non_veg', 150, 70.00,
 'Royal Garden Banquet, Example Bypass', 'Jaipur', 26.905500, 75.760200,
 DATE_SUB(NOW(), INTERVAL 5 HOUR),
 DATE_ADD(NOW(), INTERVAL 2 HOUR),
 'available'),

(9, 3, 'packaged',
 'Sealed snack boxes and juice cartons',
 'veg', 200, 60.00,
 'Royal Garden Banquet, Example Bypass', 'Jaipur', 26.905500, 75.760200,
 DATE_SUB(NOW(), INTERVAL 48 HOUR),
 DATE_ADD(NOW(), INTERVAL 120 HOUR),
 'picked_up'),

(10, 1, 'cooked_meals',
 'Pasta and garlic bread from yesterday',
 'veg', 30, 12.00,
 '12 Example Marg, C-Scheme', 'Jaipur', 26.912400, 75.787300,
 DATE_SUB(NOW(), INTERVAL 20 HOUR),
 DATE_SUB(NOW(), INTERVAL 4 HOUR),
 'expired');

INSERT INTO ngo_requirements
  (requirement_id, ngo_id, food_type, required_meals, priority, status) VALUES
(1,  1, 'cooked_meals',      100, 'high',   'open'),
(2,  1, 'bakery',             40, 'medium', 'open'),
(3,  2, 'cooked_meals',      200, 'high',   'open'),
(4,  2, 'fruits_vegetables',  60, 'medium', 'open'),
(5,  3, 'cooked_meals',       50, 'high',   'open'),
(6,  3, 'dairy',              40, 'low',    'fulfilled'),
(7,  4, 'dairy',              80, 'high',   'open'),
(8,  4, 'fruits_vegetables',  50, 'medium', 'open'),
(9,  4, 'packaged',          100, 'low',    'open'),
(10, 5, 'cooked_meals',       40, 'medium', 'open'),
(11, 5, 'bakery',             30, 'low',    'open');

-- Hand-written sample scores (NOT produced by the matching engine yet)
INSERT INTO matches
  (match_id, donation_id, ngo_id, match_score, status) VALUES
(1,  1, 1, 87.50, 'suggested'),
(2,  1, 2, 92.10, 'suggested'),
(3,  1, 3, 74.30, 'suggested'),
(4,  2, 1, 81.00, 'suggested'),
(5,  2, 3, 88.40, 'suggested'),
(6,  4, 2, 90.00, 'suggested'),
(7,  6, 4, 91.75, 'accepted'),
(8,  6, 3, 70.00, 'rejected'),
(9,  7, 2, 95.20, 'suggested'),
(10, 7, 1, 78.60, 'suggested'),
(11, 9, 4, 89.90, 'completed');