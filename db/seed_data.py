"""
Fort Fantastic - Seed Data
===========================
Populates the reference database with all static game data extracted from:

  - Organization Manual v4.0          (attraction master data, system rules)
  - Activity Cards v4.4               (all ~120 activity cards)
  - Infrastructure Cards v3.0         (node maps, internal codes, upgrade table)

Usage:
    python db/seed_data.py

Requires setup_database.py to have been run first.
Safe to re-run — clears all tables before inserting.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fort_fantastic.db")


# ==============================================================================
# 1. ATTRACTIONS
# ==============================================================================
# Source: Organization Manual Ch.8 + Infrastructure Cards p.8 (internal codes)
#         + Attraction Master Data Table (p.9)
# Columns: name, internal_code, category, type, is_base, acquisition_cost,
#          appeal, max_capacity_per_hour, capacity_per_day,
#          utilization_pct, utilization_abs, length_ft,
#          year_of_construction, useful_life_years, manufacturer,
#          fixed_costs_per_day, variable_costs_per_user,
#          sum_variable_costs_day, sum_fixed_costs_day, overall_costs_day,
#          sales_breakdown_day, gross_profit_day,
#          pds_capacity, pds_norm, stm_capacity, stm_norm
# ==============================================================================

ATTRACTIONS = [
    # ── BASE ATTRACTIONS (available at game start) ────────────────────────────

    # RIDES
    (
        "Millennium Force",
        "C44557788142775", "Ride", "Roller Coaster", 1, 1_000_000,
        6, 600, 6000, 60, 3600, 2225,
        2011, 12, "People Mover Factory Inc. Utah/USA",
        4000, 0.71,
        2556, 4000, 6556, 9507, 2951,
        80, "EU52", 33, "U"
    ),
    (
        "T-Rex",
        "C44557722818556", "Ride", "Roller Coaster", 1, 750_000,
        4, 360, 3600, 40, 1440, 1427,
        2010, 20, "Kotonami Inc, Heidelberg, Germany",
        700, 2.10,
        3024, 700, 3724, 5730, 2006,
        40, "EU52", 18, "U"
    ),
    (
        "Colorado River Rafting",
        "C44557726652556", "Ride", "Water Ride", 1, 600_000,
        6, 400, 4000, 60, 2400, 1350,
        2011, 10, "Wave Maker Ltd., Singapore",
        1800, 2.00,
        4800, 1800, 6600, 7875, 1275,
        48, "US68", 38, "U"
    ),
    (
        "Terror Tower",
        "C44667782315556", "Ride", "Free Fall", 1, 1_400_000,
        5, 240, 2400, 50, 1200, 278,
        2012, 12, "Space Flyer Machines Ltd., Sussex, GB",
        2300, 2.00,
        2400, 2300, 4700, 5823, 1123,
        75, "EU52", 28, "U"
    ),
    (
        "Panic Room",
        "C44557783665456", "Ride", "Ghost Train", 1, 780_000,
        4, 225, 2250, 40, 900, 771,
        2010, 15, "Ghostbusters Corp., NY, USA",
        800, 1.80,
        1620, 800, 2420, 4996, 2576,
        14, "EU52", 37, "U"
    ),
    (
        "Black Pearl",
        "C44667789234556", "Ride", "Swing", 1, 1_294_000,
        7, 600, 6000, 70, 4200, None,
        2012, 10, "Caribian Boats Factory, Bahamas",
        1800, 1.35,
        5670, 1800, 7470, 10743, 3273,
        65, "US68", 15, "U"
    ),
    # SHOWS
    (
        "Circus Maximus",
        "C44557766234556", "Show", "Romans", 1, 370_000,
        5, 240, 2400, 50, 1200, None,
        2010, 15, "In-House Production FortFantastic",
        4800, 0.63,
        756, 4800, 5556, 5823, 267,
        22, "EU52", 25, "G"
    ),
    (
        "Wild West",
        "C44667734987556", "Show", "Western", 1, 180_000,
        4, 150, 1500, 40, 600, None,
        2010, 18, "Licenced from Lions Productions Inc. Miami, USA",
        1200, 0.50,
        300, 1200, 1500, 4587, 3087,
        18, "US68", 22, "G"
    ),
    (
        "Cinema 4D",
        "C44557782345556", "Ride", "Cinema", 1, 870_000,
        4, 400, 4000, 40, 1600, None,
        2012, 15, "Hollywood CineCenter, Chicago",
        2800, 1.30,
        2080, 2800, 4880, 5948, 1068,
        28, "EU52", 26, "G"
    ),
    # FOOD COURTS
    (
        "Fries Corner",
        "C44667782348556", "Gastronomy", "Snack", 1, 480_000,
        8, 250, 2500, 80, 2000, None,
        2010, 12, "Fritjes King, Utrecht, NL",
        2000, 1.50,
        3000, 2000, 5000, 8169, 3169,
        36, "US68", 12, "Q"
    ),
    (
        "Angus",
        "C44577558239556", "Gastronomy", "Restaurant", 1, 580_000,
        4, 60, 600, 40, 240, None,
        2011, 10, "Moradi Steakhouse AG, Buenos Aires, Argentina",
        2300, 3.50,
        840, 2300, 3140, 4098, 958,
        24, "EU52", 8, "Q"
    ),
    (
        "PizzaPastaBasta",
        "C44557764254356", "Gastronomy", "Restaurant", 1, 230_000,
        5, 120, 1200, 50, 600, None,
        2011, 8, "Andreotti SpSA, Milano, Italy",
        1200, 1.20,
        720, 1200, 1920, 5007, 3087,
        35, "US68", 10, "Q"
    ),
    (
        "Ginosa Marina",
        "C44556687523556", "Gastronomy", "Ice-Cream Parlour", 1, 180_000,
        4, 250, 2500, 40, 1000, None,
        2010, 15, "Gelati Maximo, Neapel, ITL",
        1100, 0.70,
        700, 1100, 1800, 5132, 3332,
        10, "EU52", 15, "Q"
    ),
    (
        "Wok-In-And-Find-Out",
        "C44557766325256", "Gastronomy", "Snack", 1, 460_000,
        4, 150, 1500, 40, 600, None,
        2011, 9, "Hong-Li Chengfi, HKG",
        140, 1.00,
        600, 140, 740, 4587, 3847,
        26, "EU52", 14, "Q"
    ),

    # ── ADDITIONAL ATTRACTIONS (purchasable during game) ─────────────────────

    (
        "Predator",
        "C44665533726556", "Ride", "Spin", 0, 1_250_000,
        10, 600, 6000, 100, 6000, 75,
        None, 15, "People Mover Factory Inc. Utah/USA",
        2500, 0.90,
        5400, 2500, 7900, 13898, 5998,
        96, "US68", 29, "U"
    ),
    (
        "Enroon",
        "C44775566283456", "Ride", "Free Fall", 0, 1_000_000,
        9, 280, 2800, 90, 2520, 360,
        None, 12, "People Mover Factory Inc. Utah/USA",
        1800, 1.70,
        4284, 1800, 6084, 8745, 2661,
        74, "EU52", 22, "U"
    ),
    (
        "Bone Cracker",
        "C44665577353676", "Ride", "Chair Lift", 0, 980_000,
        8, 380, 3800, 80, 3040, 1053,
        None, 10, "People Mover Factory Inc. Utah/USA",
        600, 1.70,
        5168, 600, 5768, 9033, 3265,
        68, "EU52", 26, "U"
    ),
    (
        "Mindfreak",
        "C44555673335556", "Show", "Hypnotism", 0, 450_000,
        6, 200, 2000, 60, 1200, None,
        None, 8, "Uri Geller Sensations GmbH, Vienna, Austria",
        2000, 1.80,
        2160, 2000, 4160, 5691, 1531,
        25, "EU52", 11, "G"
    ),
    (
        "Burger Queen",
        "C44655344576652", "Gastronomy", "Snack", 0, 600_000,
        7, 120, 1200, 70, 840, None,
        None, 10, "MacDoni Inc., Boston, USA",
        2500, 1.50,
        1260, 2500, 3760, 5620, 1860,
        42, "US68", 22, "Q"
    ),
]

# ==============================================================================
# 2. ACTIVITY CARDS
# ==============================================================================
# Source: Activity Cards v4.4 — all pages extracted
# Tuple columns:
#   id, title, category,
#   order_code_std, order_code_3p, order_code_4r,
#   delivery_days, implementation_days, runtime_days,
#   price, uses,
#   attraction, attractions_multi, infrastructure_module, component,
#   effect_visitors_min_pct, effect_visitors_max_pct,
#   effect_appeal, effect_fixed_costs, effect_variable_costs,
#   effect_capacity, effect_utilization_pct,
#   effect_general_expense_min, effect_general_expense_max
# ==============================================================================

ACTIVITY_CARDS = [
    # ── CAMPAIGNS / ADVERTISING ───────────────────────────────────────────────
    (1,  "Campaign", "Campaign",
     "STD-1", "3P-1", None,
     15, None, 90,
     250_000, "1",
     None, None, None, None,
     4.0, 5.0, None, None, None, None, None, None, None),

    (2,  "Campaign", "Campaign",
     "STD-2", "3P-2", None,
     None, None, 60,
     200_000, "1",
     None, None, None, None,
     3.0, 6.0, None, None, None, None, None, None, None),

    (4,  "Special Event", "Special Event",
     "STD-T", "3P-T", None,
     None, None, 120,
     400_000, "1",
     None, None, None, None,
     4.0, 6.0, None, None, None, None, None, None, None),

    (5,  "Special Event", "Special Event",
     "STD-2", "3P-2", None,
     None, None, 60,
     200_000, "1",
     "Wild West", None, None, None,
     None, None, 6.0, None, None, None, None, None, None),

    (35, "Personnel Ramp-up", "Personnel",
     "STD-2", "3P-2", None,
     30, None, None,
     80_000, "1",
     None, None, None, None,
     None, 3.0, None, None, None, None, None, 6.0, 6.0),

    (56, "Cost Reduction", "Cost Reduction",
     "STD-1", "3P-1", None,
     45, None, None,
     300_000, "1",
     None, None, None, None,
     None, None, None, None, None, None, None, -12.0, -10.0),

    (67, "Sales Promotion", "Sales Promotion",
     "STD-5", None, None,
     None, None, 150,
     100_000, "1",
     None, None, None, None,
     0.5, 1.0, None, None, None, None, None, None, None),

    (90, "Advertisement", "Advertisement",
     "STD-3", "3P-3", None,
     None, None, 180,
     250_000, "1",
     None, None, None, None,
     1.0, 2.0, None, None, None, None, None, None, None),

    (92, "Sponsoring", "Sponsoring",
     "STD-4", None, None,
     None, None, 90,
     50_000, "1",
     None, None, None, None,
     1.0, 2.0, None, None, None, None, None, None, None),

    (96, "Radio Commercials", "Advertisement",
     "STD-4", "3P-4", None,
     None, None, 100,
     350_000, "1",
     None, None, None, None,
     3.0, 3.5, None, None, None, None, None, None, None),

    (97, "Distribution of Giveaways", "Promotion",
     "STD-4", "3P-4", None,
     None, None, 30,
     100_000, "1",
     None, None, None, None,
     3.0, 3.0, None, None, None, None, None, None, None),

    (100, "Promotion", "Promotion",
     "STD-3", "3P-3", None,
     10, None, 60,
     75_000, "1",
     None, None, None, None,
     0.5, 1.0, None, None, None, None, None, None, None),

    (101, "Sponsoring", "Sponsoring",
     "STD-1", "3P-1", None,
     None, None, 180,
     50_000, "1",
     None, None, None, None,
     0.0, 0.01, None, None, None, None, None, None, None),

    (103, "Cost Savings", "Cost Reduction",
     "STD-4", "3P-4", None,
     None, None, 60,
     100_000, "1",
     None, None, None, None,
     None, None, None, None, None, None, None, -6.0, -5.0),

    (104, "Training (Kaizen)", "Cost Reduction",
     "STD-1", None, None,
     None, None, 10,
     150_000, "1",
     None, None, None, None,
     None, None, None, None, None, None, None, -1.5, -1.0),

    (105, "Quality Improvement", "Quality Improvement",
     "STD-1", "3P-1", None,
     None, None, 180,
     350_000, "1",
     None, None, None, None,
     None, None, None, None, None, None, None, -6.0, -6.0),

    (115, "Advertisement (Predator)", "Advertisement",
     "STD-1", "3P-1", None,
     None, None, 60,
     160_000, "1",
     None, None, None, None,
     1.0, 1.2, None, None, None, None, None, None, None),

    (116, "Promotion (Bone Cracker)", "Promotion",
     "STD-2", "3P-2", None,
     None, None, 30,
     60_000, "1",
     None, None, None, None,
     2.0, 4.0, None, None, None, None, None, None, None),

    (117, "Promotion (Burger Queen)", "Promotion",
     "STD-3", None, None,
     None, None, 20,
     50_000, "1",
     None, None, None, None,
     -0.3, -0.3, None, None, None, None, None, None, None),

    (118, "Promotion (Mindfreak)", "Promotion",
     "STD-1", None, None,
     None, None, 30,
     50_000, "1",
     None, None, None, None,
     4.0, 4.5, None, None, None, None, None, None, None),

    (119, "Promotion (Enroon)", "Promotion",
     "STD-1", "3P-1", None,
     None, None, 90,
     275_000, "1",
     None, None, None, None,
     4.0, 5.0, None, None, None, None, None, None, None),

    # ── CAPACITY UPGRADES ────────────────────────────────────────────────────
    (6,  "Capacity - Millennium Force", "Capacity",
     "STD-1", "3P-1", None,
     None, 3, None,
     15_000, "1",
     "Millennium Force", None, None, None,
     None, None, None, None, -0.10, 50.0, None, None, None),

    (7,  "Capacity - T-Rex", "Capacity",
     "STD-2", "3P-2", None,
     None, 3, None,
     15_000, "1",
     "T-Rex", None, None, None,
     None, None, None, None, -0.30, 50.0, None, None, None),

    (8,  "Capacity - Colorado River Rafting", "Capacity",
     "STD-3", "3P-3", None,
     None, 3, None,
     15_000, "1",
     "Colorado River Rafting", None, None, None,
     None, None, None, None, -0.30, 50.0, None, None, None),

    (9,  "Capacity - Terror Tower", "Capacity",
     "STD-4", "3P-4", None,
     None, 3, None,
     15_000, "1",
     "Terror Tower", None, None, None,
     None, None, None, None, -0.40, 50.0, None, None, None),

    (10, "Capacity - Panic Room", "Capacity",
     "STD-5", "3P-5", None,
     None, 3, None,
     15_000, "1",
     "Panic Room", None, None, None,
     None, None, None, None, -0.30, 50.0, None, None, None),

    (11, "Capacity - Black Pearl", "Capacity",
     "STD-1", None, None,
     None, 3, None,
     15_000, "1",
     "Black Pearl", None, None, None,
     None, None, None, None, -0.15, 50.0, None, None, None),

    (12, "Capacity - Circus Maximus", "Capacity",
     "STD-2", None, None,
     None, 3, None,
     15_000, "1",
     "Circus Maximus", None, None, None,
     None, None, None, None, -0.35, 50.0, None, None, None),

    (13, "Capacity - Wild West", "Capacity",
     "STD-3", "3P-3", None,
     None, 3, None,
     15_000, "1",
     "Wild West", None, None, None,
     None, None, None, None, -0.25, 50.0, None, None, None),

    (14, "Capacity - Cinema 4D", "Capacity",
     "STD-4", "3P-4", None,
     None, 3, None,
     15_000, "1",
     "Cinema 4D", None, None, None,
     None, None, None, None, -0.15, 50.0, None, None, None),

    # ── UPGRADES ─────────────────────────────────────────────────────────────
    (3,  "Upgrade - Colorado River Rafting", "Upgrade",
     "STD-2", "3P-2", None,
     None, 10, None,
     200_000, "1",
     "Colorado River Rafting", None, None, None,
     None, None, 1.0, -300.0, -0.50, None, None, None, None),

    (15, "Reinvestment - Panic Room", "Reinvestment",
     "STD-1", "3P-1", None,
     30, 50, None,
     250_000, "1",
     "Panic Room", None, None, None,
     None, None, 6.0, 2000.0, 1.80, None, None, None, None),

    (16, "Upgrade - Cinema 4D (Sony 4D)", "Upgrade",
     "STD-T", "3P-T", None,
     None, None, 60,
     72_000, "1",
     "Cinema 4D", None, None, None,
     None, None, 3.0, None, None, None, None, None, None),

    (17, "Upgrade - Angus Counter", "Upgrade",
     "STD-1", None, None,
     None, 14, None,
     12_000, "1",
     "Angus", None, None, None,
     None, None, 2.0, 100.0, None, None, None, None, None),

    (18, "Purchase - Fries Corner Supplier", "Purchase",
     "STD-T", None, None,
     35, None, None,
     6_000, "1",
     "Fries Corner", None, None, None,
     None, None, 1.0, None, 0.10, None, None, None, None),

    (19, "Purchase - Ginosa Marina Supplier", "Purchase",
     "STD-1", "3P-1", None,
     5, None, None,
     15_000, "1",
     "Ginosa Marina", None, None, None,
     None, None, 1.0, None, 0.10, None, None, None, None),

    (33, "Procurement - Angus Steaks", "Procurement",
     "STD-5", "3P-5", None,
     None, None, None,
     5_000, "1",
     "Angus", None, None, None,
     None, None, 1.0, None, 0.30, None, None, None, None),

    (42, "Upgrade - Wok-In-And-Find-Out", "Upgrade",
     "STD-4", "3P-4", None,
     None, 3, None,
     40_000, "1",
     "Wok-In-And-Find-Out", None, None, None,
     None, None, 2.0, None, None, None, None, None, None),

    (58, "Upgrade - Cutlery (Multi)", "Upgrade",
     "STD-1", None, None,
     None, 1, None,
     50_000, "1",
     None, "Burger Queen,Fries Corner,PizzaPastaBasta,Wok-In-And-Find-Out", None, None,
     None, None, 0.50, None, None, None, None, None, None),

    (59, "Upgrade - T-Rex Renovation", "Upgrade",
     "STD-1", "3P-1", None,
     None, 8, None,
     250_000, "1",
     "T-Rex", None, None, None,
     None, None, 1.0, None, -0.60, None, None, None, None),

    (60, "Upgrade - Millennium Force Control Module", "Upgrade",
     "STD-5", "3P-5", None,
     None, 2, None,
     250_000, "1",
     "Millennium Force", None, None, None,
     None, None, None, -500.0, None, None, None, None, None),

    (61, "Upgrade - Circus Maximus Features", "Upgrade",
     "STD-3", "3P-3", None,
     None, 5, None,
     60_000, "1",
     "Circus Maximus", None, None, None,
     None, None, 1.0, -800.0, 0.30, None, None, None, None),

    (62, "Upgrade - Circus Maximus New Ensemble", "Upgrade",
     "STD-T", "3P-T", None,
     None, 3, None,
     100_000, "1",
     "Circus Maximus", None, None, None,
     None, None, 2.0, 500.0, None, 110.0, None, None, None),

    (63, "Upgrade - Circus Maximus Outfit", "Upgrade",
     "STD-3", "3P-3", None,
     None, 10, None,
     100_000, "1",
     "Circus Maximus", None, None, None,
     None, None, None, -1000.0, None, None, None, None, None),

    (66, "Upgrade - Street Entertainers", "Upgrade",
     "STD-4", "3P-4", None,
     15, None, None,
     None, "1",
     None, "Circus Maximus,Wild West", None, None,
     None, None, 1.50, 750.0, None, None, None, None, None),

    (68, "Upgrade - Millennium Force Looping", "Upgrade",
     "STD-1", None, None,
     30, 30, None,
     120_000, "1",
     "Millennium Force", None, None, None,
     None, None, 2.0, None, -0.10, -1000.0, 20.0, None, None),

    (86, "Enhancement - Wild West Grandstand", "Enhancement",
     "STD-3", None, None,
     30, 45, None,
     100_000, "1",
     "Wild West", None, None, None,
     None, None, None, 100.0, None, 1000.0, None, None, None),

    (87, "Upgrade - Wild West Disney Concept", "Upgrade",
     "STD-4", None, None,
     None, None, None,
     100_000, "1",
     "Wild West", None, None, None,
     None, None, None, None, None, None, 40.0, None, None),

    (89, "Extension - Pizza Pasta Basta Terrace", "Extension",
     "STD-1", "3P-1", None,
     None, 10, None,
     20_000, "1",
     "PizzaPastaBasta", None, None, None,
     None, None, None, None, None, 500.0, None, None, None),

    (93, "Extension - Pizza Pasta Basta Food Hall", "Extension",
     "STD-2", None, None,
     None, 20, None,
     60_000, "1",
     "PizzaPastaBasta", None, None, None,
     None, None, -0.50, None, -0.20, 900.0, None, None, None),

    (102, "Outsourcing - Pizza Pasta Basta", "Outsourcing",
     "STD-3", "3P-3", None,
     30, 5, None,
     80_000, "1",
     "PizzaPastaBasta", None, None, None,
     None, None, None, -600.0, 1.00, None, None, None, None),

    (106, "Maintenance - Millennium Force Makeover", "Maintenance",
     "STD-1", None, None,
     None, 5, None,
     50_000, "1",
     "Millennium Force", None, None, None,
     None, None, 1.0, None, None, None, None, None, None),

    (107, "Maintenance - T-Rex Makeover", "Maintenance",
     "STD-1", None, None,
     None, 10, None,
     100_000, "1",
     "T-Rex", None, None, None,
     None, None, 1.0, None, None, None, None, None, None),

    (108, "Maintenance - Colorado River Rafting Makeover", "Maintenance",
     "STD-4", None, None,
     None, 5, None,
     60_000, "1",
     "Colorado River Rafting", None, None, None,
     None, None, 1.0, None, None, None, None, None, None),

    (109, "Maintenance - Terror Tower Makeover", "Maintenance",
     "STD-5", None, None,
     None, 20, None,
     150_000, "1",
     "Terror Tower", None, None, None,
     None, None, 1.0, None, None, None, None, None, None),

    (110, "Sourcing - Circus Maximus Eastern Ensemble", "Sourcing",
     "STD-2", None, None,
     None, 5, None,
     250_000, "1",
     "Circus Maximus", None, None, None,
     None, None, None, -2400.0, None, None, None, None, None),

    (111, "Investment - T-Rex New Wagons", "Investment",
     "STD-T", "3P-T", None,
     None, 10, None,
     90_000, "1",
     "T-Rex", None, None, None,
     None, None, 2.0, 300.0, None, None, None, None, None),

    (112, "Extension - Ginosa Marina Soft Ice", "Extension",
     "STD-2", None, None,
     None, None, None,
     20_000, "1",
     "Ginosa Marina", None, None, None,
     None, None, None, None, None, None, 20.0, None, None),

    (113, "Innovation - Cinema 4D Japanese Concept", "Innovation",
     "STD-4", None, None,
     None, 10, None,
     65_000, "1",
     "Cinema 4D", None, None, None,
     None, None, 2.0, None, None, -200.0, 20.0, None, None),

    (114, "Quality Improvement - Fries Corner Oil", "Quality Improvement",
     "STD-2", None, None,
     None, None, None,
     None, "1",
     "Fries Corner", None, None, None,
     None, None, 1.0, None, 0.10, None, None, None, None),

    # ── REPAIRS ──────────────────────────────────────────────────────────────
    (20, "Repair - Millennium Force Safety Loop 1", "Repair",
     "STD-2", None, None,
     None, 5, None,
     7_500, "unlimited",
     "Millennium Force", None, None, "Safety loop 1",
     None, None, None, None, None, None, None, None, None),

    (21, "Repair - Millennium Force Safety Loop 2", "Repair",
     "STD-1", None, None,
     None, 5, None,
     7_500, "unlimited",
     "Millennium Force", None, None, "Safety loop 2",
     None, None, None, None, None, None, None, None, None),

    (22, "Repair - Millennium Force Slingshot Winch", "Repair",
     "STD-2", "3P-2", None,
     None, 5, None,
     25_500, "unlimited",
     "Millennium Force", None, None, "Slingshot winch",
     None, None, None, None, None, None, None, None, None),

    (23, "Repair - Millennium Force Brake Disks", "Repair",
     "STD-1", "3P-1", None,
     None, 5, None,
     25_000, "unlimited",
     "Millennium Force", None, None, "Left brake, Right brake",
     None, None, None, None, None, None, None, None, None),

    (24, "Repair - T-Rex Chain", "Repair",
     "STD-2", "3P-2", None,
     None, 8, None,
     10_000, "unlimited",
     "T-Rex", None, None, "Chain",
     None, None, None, None, None, None, None, None, None),

    (25, "Repair - T-Rex Rear Brake", "Repair",
     "STD-1", "3P-1", None,
     None, 3, None,
     3_000, "unlimited",
     "T-Rex", None, None, "Rear brake unit",
     None, None, None, None, None, None, None, None, None),

    (26, "Repair - Colorado River Rafting Unit 2", "Repair",
     "STD-5", None, None,
     14, 6, None,
     35_000, "unlimited",
     "Colorado River Rafting", None, None, "Roller coaster unit 2",
     None, None, None, None, None, None, None, None, None),

    (27, "Repair - Colorado River Rafting Camera (OS)", "Repair",
     "STD-3", "3P-3", None,
     None, 1, None,
     500, "unlimited",
     "Colorado River Rafting", None, None, "Camera",
     None, None, None, None, None, None, None, None, None),

    (28, "Repair - Terror Tower Brake System", "Repair",
     "STD-2", "3P-3", None,
     None, 2, None,
     3_000, "unlimited",
     "Terror Tower", None, None, "Brake system",
     None, None, None, None, None, None, None, None, None),

    (30, "Repair - Panic Room Ghost Mockup 1", "Repair",
     "STD-2", "3P-3", None,
     None, 55, None,
     250_800, "unlimited",
     "Panic Room", None, None, "Ghost mockup 1",
     None, None, None, None, None, None, None, None, None),

    (31, "Repair - Panic Room Fog Machine 1", "Repair",
     "STD-2", "3P-3", None,
     None, 3, None,
     4_500, "unlimited",
     "Panic Room", None, None, "Fog machine 1",
     None, None, None, None, None, None, None, None, None),

    (32, "Update - Black Pearl Locking Software", "Update",
     "STD-1", None, None,
     None, 2, None,
     2_500, "unlimited",
     "Black Pearl", None, None, "Retainer 1, Retainer 2",
     None, None, None, None, None, None, None, None, None),

    (34, "Repair - Black Pearl Turnstile", "Repair",
     "STD-3", None, None,
     None, 3, None,
     4_500, "unlimited",
     "Black Pearl", None, None, "Turnstile 1, Turnstile 2",
     None, None, None, None, None, None, None, None, None),

    (36, "Repair - Circus Maximus Lighting", "Repair",
     "STD-1", None, None,
     None, 3, None,
     4_500, "unlimited",
     "Circus Maximus", None, None, "Lighting",
     None, None, None, None, None, None, None, None, None),

    (37, "Reinvestment - Circus Maximus Soundsystem", "Reinvestment",
     "STD-5", "3P-5", None,
     None, 3, None,
     9_500, "unlimited",
     "Circus Maximus", None, None, "Soundsystem",
     None, None, None, None, None, None, None, None, None),

    (38, "Construction - Wild West Visitor Terrace", "Construction",
     "STD-1", None, None,
     None, 5, None,
     28_500, "unlimited",
     "Wild West", None, None, "Visitor terrace",
     None, None, None, None, None, None, None, None, None),

    (39, "Repair - Wild West Curtain", "Repair",
     "STD-1", None, None,
     None, 7, None,
     10_000, "unlimited",
     "Wild West", None, None, "Curtain",
     None, None, None, None, None, None, None, None, None),

    (40, "Repair - Cinema 4D Projector", "Repair",
     "STD-3", "3P-3", None,
     None, 2, None,
     6_500, "unlimited",
     "Cinema 4D", None, None, "Projector",
     None, None, None, None, None, None, None, None, None),

    (41, "Repair - Cinema 4D Seating", "Repair",
     "STD-2", "3P-2", None,
     None, 5, None,
     13_500, "unlimited",
     "Cinema 4D", None, None, "Seating row 1 (1-49), Seating row 2 (50-99)",
     None, None, None, None, None, None, None, None, None),

    (43, "Surveillance - Cinema 4D Balcony", "Surveillance",
     "STD-2", "3P-3", None,
     None, None, None,
     450_000, "unlimited",
     "Cinema 4D", None, None, "Balcony seats",
     None, None, None, None, None, None, None, None, None),

    (44, "Repair - Fries Corner Barbecue", "Repair",
     "STD-3", None, None,
     None, 2, None,
     3_500, "unlimited",
     "Fries Corner", None, None, "Barbecue",
     None, None, None, None, None, None, None, None, None),

    (45, "Repair - Fries Corner Fridge", "Repair",
     "STD-1", None, None,
     None, 1, None,
     4_500, "unlimited",
     "Fries Corner", None, None, "Fridge",
     None, None, None, None, None, None, None, None, None),

    (46, "Maintenance - Angus Smoke Detector", "Maintenance",
     "STD-3", None, None,
     None, 3, None,
     15_000, "unlimited",
     "Angus", None, None, "Smoke detector",
     None, None, None, None, None, None, None, None, None),

    (47, "Repair - Angus Washroom", "Repair",
     "STD-2", "3P-4", None,
     None, 4, None,
     9_000, "unlimited",
     "Angus", None, None, "Washroom 1",
     None, None, None, None, None, None, None, None, None),

    (48, "Repair - Pizza Pasta Basta Card Reader", "Repair",
     "STD-3", None, None,
     None, 2, None,
     4_000, "unlimited",
     "PizzaPastaBasta", None, None, "Card reader",
     None, None, None, None, None, None, None, None, None),

    (49, "Repair - Pizza Pasta Basta Soft Ice 1", "Repair",
     "STD-2", None, None,
     None, 1, None,
     5_000, "unlimited",
     "PizzaPastaBasta", None, None, "Soft ice machine 1",
     None, None, None, None, None, None, None, None, None),

    (50, "Repair - Pizza Pasta Basta Soft Ice 2", "Repair",
     "STD-1", None, None,
     None, 3, None,
     35_000, "unlimited",
     "PizzaPastaBasta", None, None, "Soft ice machine 2",
     None, None, None, None, None, None, None, None, None),

    (51, "Repair - Ginosa Marina Cooling Counter", "Repair",
     "STD-2", "3P-2", None,
     None, 2, None,
     4_500, "unlimited",
     "Ginosa Marina", None, None, "Cooling counter exterior",
     None, None, None, None, None, None, None, None, None),

    (52, "Training - Predator Operator", "Training",
     "STD-3", "3P-4", None,
     None, 2, None,
     7_500, "unlimited",
     "Predator", None, None, "Operator",
     None, None, None, None, None, None, None, None, None),

    (53, "Repair - Wok-In-And-Find-Out Gas Stove", "Repair",
     "STD-2", "3P-3", None,
     None, 1, None,
     2_000, "unlimited",
     "Wok-In-And-Find-Out", None, None, "Gas stove 1",
     None, None, None, None, None, None, None, None, None),

    (54, "Repair - Wok-In-And-Find-Out Inventory", "Repair",
     "STD-1", None, None,
     None, 15, None,
     50_000, "unlimited",
     "Wok-In-And-Find-Out", None, None, "Inventory",
     None, None, None, None, None, None, None, None, None),

    (69, "Maintenance - Millennium Force Safety Loops", "Maintenance",
     "STD-1", None, None,
     None, 1, None,
     15_000, "unlimited",
     "Millennium Force", None, None, "Safety loop 1, Safety loop 2",
     None, None, None, None, None, None, None, None, None),

    (70, "Purchase - Ginosa Marina Ice Cream Stock", "Purchase",
     "STD-2", "3P-3", None,
     None, None, None,
     2_000, "unlimited",
     "Ginosa Marina", None, None, "Inventory, Vanilla",
     None, None, None, None, None, None, None, None, None),

    (71, "Maintenance - Millennium Force Slingshot", "Maintenance",
     "STD-1", "3P-2", None,
     None, 1, None,
     7_000, "unlimited",
     "Millennium Force", None, None, "Slingshot winch",
     None, None, None, None, None, None, None, None, None),

    (72, "Purchase - Fries Corner French Fries", "Purchase",
     "STD-T", "3P-T", None,
     None, None, None,
     15_000, "1",
     "Fries Corner", None, None, None,
     None, None, None, None, None, None, None, None, None),

    (73, "Maintenance - Millennium Force Rear Brake", "Maintenance",
     "STD-1", "3P-1", None,
     None, 5, None,
     12_000, "unlimited",
     "Millennium Force", None, None, "Rear brake",
     None, None, None, None, None, None, None, None, None),

    (74, "Maintenance - T-Rex Cars", "Maintenance",
     "STD-1", "3P-1", None,
     None, 2, None,
     25_000, "unlimited",
     "T-Rex", None, None, "Car 1, Car 2",
     None, None, None, None, None, None, None, None, None),

    (75, "Repair - Colorado River Rafting Camera", "Repair",
     "STD-2", "3P-3", None,
     None, None, None,
     2_000, "unlimited",
     "Colorado River Rafting", None, None, "Camera",
     None, None, None, None, None, None, None, None, None),

    (76, "Investment - Circus Maximus Lighting", "Investment",
     "STD-3", None, None,
     None, 5, None,
     85_000, "unlimited",
     "Circus Maximus", None, None, "Lighting",
     None, None, None, None, None, None, None, None, None),

    (77, "Investment - Circus Maximus Chariots", "Investment",
     "STD-2", "3P-2", None,
     None, 1, None,
     25_000, "unlimited",
     "Circus Maximus", None, None, "Gladiator vehicle 1",
     None, None, None, None, None, None, None, None, None),

    (78, "Maintenance - Fries Corner Fryers", "Maintenance",
     "STD-5", None, None,
     None, 1, None,
     3_500, "unlimited",
     "Fries Corner", None, None, "Fryer 1, Fryer 2",
     None, None, None, None, None, None, None, None, None),

    (79, "Special Vacation - Wild West", "Special Event",
     "STD-2", "3P-2", None,
     None, 5, None,
     15_000, "1",
     "Wild West", None, None, None,
     None, None, None, None, None, None, None, None, None),

    (80, "Personnel - Wild West Actor", "Personnel",
     "STD-1", None, None,
     None, 7, None,
     12_000, "unlimited",
     None, None, None, None,
     None, None, None, None, None, None, None, None, None),

    (81, "Maintenance - Panic Room Fog Machine", "Maintenance",
     "STD-2", "3P-2", None,
     None, 3, None,
     16_000, "unlimited",
     "Panic Room", None, None, "Fog machine 1, Fog machine 2",
     None, None, None, None, None, None, None, None, None),

    (82, "Investment - Pizza Pasta Basta Sanitary", "Investment",
     "STD-4", None, None,
     None, 7, None,
     25_000, "1",
     "PizzaPastaBasta", None, None, None,
     None, None, None, None, None, None, None, None, None),

    (83, "Investment - Cinema 4D Fridge", "Investment",
     "STD-5", None, None,
     None, 1, None,
     3_500, "unlimited",
     "Cinema 4D", None, None, "Fridge",
     None, None, None, None, None, None, None, None, None),

    (84, "Investment - Pizza Pasta Basta Display Fridge", "Investment",
     "STD-1", "3P-1", None,
     None, 3, None,
     8_500, "unlimited",
     "PizzaPastaBasta", None, None, "Cooling counter display 1, Cooling counter display 2",
     None, None, None, None, None, None, None, None, None),

    (88, "Reconfiguration - Fries Corner WSN", "Reconfiguration",
     "STD-3", None, None,
     None, 10, None,
     25_000, "1",
     "Fries Corner", None, "WSN", "Inflow south, Drain central west",
     None, None, None, None, None, None, None, None, None),

    (91, "Training - Burger Queen Kitchen Staff", "Training",
     "STD-1", None, None,
     None, 5, None,
     15_000, "unlimited",
     "Burger Queen", None, None, "Thermostat",
     None, None, None, None, None, None, None, None, None),

    (94, "Investment - Cinema 4D Signs", "Investment",
     "STD-2", "3P-2", None,
     None, None, None,
     5_000, "1",
     "Cinema 4D", None, None, None,
     None, None, None, None, None, None, None, None, None),

    (95, "Investment - Ginosa Marina Display Fridge", "Investment",
     "STD-2", "3P-2", None,
     None, 3, None,
     22_500, "unlimited",
     "Ginosa Marina", None, None, "Cooling counter exterior, Cooling counter interior",
     None, None, None, None, None, None, None, None, None),

    (98, "Maintenance - Cinema 4D Projector", "Maintenance",
     "STD-2", None, None,
     None, 1, None,
     5_000, "1",
     "Cinema 4D", None, None, None,
     None, None, None, None, None, None, None, None, None),

    (57, "Investment - Angus Sanitary Overhaul", "Investment",
     "STD-5", "3P-5", None,
     None, 5, None,
     28_000, "1",
     "Angus", None, None, None,
     None, None, None, None, None, None, None, None, None),

    # ── INFRASTRUCTURE CARDS ─────────────────────────────────────────────────
    (29, "Frame Contract - BDN Components", "Frame Contract",
     "STD-2", None, "4R-3",
     2, None, None,
     3_000, "1",
     None, None, "BDN", "As4, B4, D1",
     None, None, None, None, None, None, None, None, None),

    (55, "Frame Contract - Pizza Pasta Basta Flour", "Frame Contract",
     "STD-2", "3P-2", None,
     2, None, None,
     3_000, "1",
     "PizzaPastaBasta", None, None, "Stock",
     None, None, None, None, None, None, None, None, None),

    (64, "Construction - WSN Drain", "Construction",
     "STD-2", None, None,
     None, 60, None,
     350_000, "unlimited",
     None, None, "WSN", "Drain central west",
     None, None, None, None, None, None, None, None, None),

    (65, "Restriction - WSN Drain Capacity", "Restriction",
     "STD-2", None, None,
     None, None, None,
     None, "1",
     None, "Angus,Fries Corner,Panic Room,Ginosa Marina", "WSN", "Drain central west",
     None, None, -1.0, None, None, None, None, None, None),

    (99, "Surveillance - BDN As4", "Surveillance",
     "STD-2", None, "4R-3",
     None, 2, None,
     500, "unlimited",
     None, None, "BDN", "As4",
     None, None, None, None, None, None, None, None, None),

    (159, "Purchase - Pizza Pasta Basta Flour (Extra)", "Purchase",
     "STD-2", "3P-3", None,
     5, None, None,
     450, "unlimited",
     "PizzaPastaBasta", None, None, "Stock",
     None, None, None, None, None, None, None, None, None),

    (160, "Purchase - Pizza Pasta Basta Flour (Online)", "Purchase",
     "STD-2", "3P-3", None,
     7, None, None,
     650, "unlimited",
     "PizzaPastaBasta", None, None, "Stock",
     None, None, None, None, None, None, None, None, None),

    (161, "Purchase - Pizza Pasta Basta Flour (Supermarket)", "Purchase",
     "STD-2", "3P-3", None,
     3, None, None,
     750, "unlimited",
     "PizzaPastaBasta", None, None, "Stock",
     None, None, None, None, None, None, None, None, None),

    (163, "Health Care - Wild West Horse", "Health Care",
     "STD-5", None, None,
     3, 5, None,
     500, "unlimited",
     "Wild West", None, None, "Jolly jumper",
     None, None, None, None, None, None, None, None, None),

    (164, "Purchase - Ginosa Marina Cocoa", "Purchase",
     "STD-1", None, None,
     3, None, None,
     1_500, "unlimited",
     "Ginosa Marina", None, None, "Cocoa powder",
     None, None, None, None, None, None, None, None, None),

    (165, "Health Care - Wok Pest Control", "Health Care",
     "STD-1", None, None,
     3, 1, None,
     2_500, "unlimited",
     "Wok-In-And-Find-Out", None, None, "Inventory",
     None, None, None, None, None, None, None, None, None),

    (167, "Personnel - Black Pearl Impersonator", "Personnel",
     "STD-1", "3P-1", None,
     None, 1, None,
     500, "unlimited",
     "Black Pearl", None, None, "Impersonator",
     None, None, None, None, None, None, None, None, None),

    (170, "Purchase - VSS Component B4 (Fast)", "Purchase",
     "STD-2", None, "4R-3",
     5, None, None,
     450, "unlimited",
     None, None, "VSS", "B4",
     None, None, None, None, None, None, None, None, None),

    (171, "Purchase - VSS Component B4 (Standard)", "Purchase",
     "STD-2", None, "4R-3",
     7, None, None,
     650, "unlimited",
     None, None, "VSS", "B4",
     None, None, None, None, None, None, None, None, None),

    (172, "Purchase - VSS Component B4 (Express)", "Purchase",
     "STD-2", None, "4R-3",
     3, None, None,
     750, "unlimited",
     None, None, "VSS", "B4",
     None, None, None, None, None, None, None, None, None),
]

# ==============================================================================
# 3. INFRASTRUCTURE DOMAINS
# ==============================================================================
# Source: Organization Manual Ch.3 + Infrastructure Cards v3.0
# ==============================================================================

INFRASTRUCTURE_DOMAINS = [
    # abbreviation, full_name, description, is_reconfigurable
    ("PDS", "Power Distribution System",
     "Distributes power to all attractions. Nodes have EU52 or US68 norm connectors. "
     "Reconfigurable by the team.", 1),
    ("STM", "Systems Tracking Module",
     "Tracks operational systems across attractions. Nodes have U, G, or Q norm connectors. "
     "Reconfigurable by the team.", 1),
    ("BDN", "Business Data Network",
     "Business data infrastructure. Managed automatically by the system.", 0),
    ("VSS", "Visual Surveillance System",
     "Camera-based surveillance covering the park. Managed automatically.", 0),
    ("WSN", "Water Supply Network",
     "Water inflow and drainage grid. Components referred to by geographical position. "
     "Managed automatically.", 0),
    ("PLS", "Park Lighting System",
     "Lighting infrastructure across the park. Managed automatically.", 0),
    ("LAS", "Park Sprinkler System",
     "Fire suppression and sprinkler system. Managed automatically.", 0),
]

# ==============================================================================
# 4. INFRASTRUCTURE NODES
# ==============================================================================
# Source: Infrastructure Cards v3.0 — node IDs read from diagrams
# PDS and STM nodes have norms; others are NULL (auto-managed).
# total_capacity is the initial node capacity from the game start configuration.
# Note: Exact initial capacities for each node are not printed on the cards —
# capacity is managed dynamically. Set to NULL; update if known from game board.
# ==============================================================================

INFRASTRUCTURE_NODES = [
    # (domain_abbreviation, node_id, norm, total_capacity)
    # PDS nodes
    ("PDS", "Y1",  "EU52", None),
    ("PDS", "L2",  "EU52", None),
    ("PDS", "P0",  "US68", None),
    ("PDS", "T3",  "EU52", None),
    ("PDS", "C9",  "EU52", None),
    ("PDS", "T6",  "US68", None),
    ("PDS", "K5",  "US68", None),
    ("PDS", "J7",  "US68", None),
    # STM nodes
    ("STM", "Q5",  "Q",    None),
    ("STM", "U3",  "U",    None),
    ("STM", "U8",  "U",    None),
    ("STM", "G0",  "G",    None),
    ("STM", "Q9",  "Q",    None),
    # BDN nodes
    ("BDN", "As4", None,   None),
    ("BDN", "Ki9", None,   None),
    ("BDN", "Lx8", None,   None),
    # VSS nodes (cameras)
    ("VSS", "C1",  None,   None),
    ("VSS", "C2",  None,   None),
    ("VSS", "A2",  None,   None),
    ("VSS", "B3",  None,   None),
    ("VSS", "B4",  None,   None),
    ("VSS", "D1",  None,   None),
    ("VSS", "B1",  None,   None),
    # WSN — geographical grid nodes (inflow + drainage)
    ("WSN", "Inflow north",         None, None),
    ("WSN", "Inflow east",          None, None),
    ("WSN", "Inflow south",         None, None),
    ("WSN", "Inflow west",          None, None),
    ("WSN", "Inflow central",       None, None),
    ("WSN", "Drain north",          None, None),
    ("WSN", "Drain east",           None, None),
    ("WSN", "Drain south",          None, None),
    ("WSN", "Drain west",           None, None),
    ("WSN", "Drain central west",   None, None),
    ("WSN", "Drain central east",   None, None),
    # LAS nodes (sprinkler zones)
    ("LAS", "G1",  None,   None),
    ("LAS", "I2",  None,   None),
    ("LAS", "5A",  None,   None),
    ("LAS", "S7",  None,   None),
    ("LAS", "T3",  None,   None),
    ("LAS", "Y6",  None,   None),
    # PLS nodes (lighting zones)
    ("PLS", "YS4", None,   None),
    ("PLS", "2FK", None,   None),
    ("PLS", "KHG", None,   None),
    ("PLS", "1Z6", None,   None),
    ("PLS", "BN1", None,   None),
    ("PLS", "XXL", None,   None),
    ("PLS", "RAT", None,   None),
    ("PLS", "LJQ", None,   None),
    ("PLS", "KKU", None,   None),
    ("PLS", "AAS", None,   None),
    ("PLS", "U8P", None,   None),
]

# ==============================================================================
# 5. INFRASTRUCTURE UPGRADES
# ==============================================================================
# Source: Infrastructure Cards v3.0, page 10
# Order code format: [Module]-[Norm]-[Node]-[Type]   e.g. PDS-EU52-Y1-A
# ==============================================================================

INFRASTRUCTURE_UPGRADES = [
    # (module, norm, upgrade_type, capacity_added, cost, delivery_days, duration_days)
    # PDS upgrades
    ("PDS", "EU52", "A", 50, 80_000, 30,  None),
    ("PDS", "EU52", "B", 20, 60_000, 10,  None),
    ("PDS", "EU52", "C", 30, 50_000, None, 60),
    ("PDS", "US68", "A", 50, 80_000, 30,  None),
    ("PDS", "US68", "B", 20, 60_000, 10,  None),
    ("PDS", "US68", "C", 30, 50_000, None, 60),
    # STM upgrades
    ("STM", "U",    "A", 30, 70_000, 30,  None),
    ("STM", "U",    "B", 10, 50_000, 10,  None),
    ("STM", "U",    "C", 15, 40_000, None, 60),
    ("STM", "G",    "A", 30, 70_000, 30,  None),
    ("STM", "G",    "B", 10, 50_000, 10,  None),
    ("STM", "G",    "C", 15, 40_000, None, 60),
    ("STM", "Q",    "A", 30, 70_000, 30,  None),
    ("STM", "Q",    "B", 10, 50_000, 10,  None),
    ("STM", "Q",    "C", 15, 40_000, None, 60),
]

# ==============================================================================
# SEED FUNCTIONS
# ==============================================================================

def seed_attractions(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM attractions")
    conn.executemany("""
        INSERT INTO attractions (
            name, internal_code, category, type, is_base, acquisition_cost,
            appeal, max_capacity_per_hour, capacity_per_day,
            utilization_pct, utilization_abs, length_ft,
            year_of_construction, useful_life_years, manufacturer,
            fixed_costs_per_day, variable_costs_per_user,
            sum_variable_costs_day, sum_fixed_costs_day, overall_costs_day,
            sales_breakdown_day, gross_profit_day,
            pds_capacity, pds_norm, stm_capacity, stm_norm
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, ATTRACTIONS)
    print(f"[seed] attractions      : {len(ATTRACTIONS)} rows")


def seed_activity_cards(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM activity_cards")
    conn.executemany("""
        INSERT INTO activity_cards (
            id, title, category,
            order_code_std, order_code_3p, order_code_4r,
            delivery_days, implementation_days, runtime_days,
            price, uses,
            attraction, attractions_multi, infrastructure_module, component,
            effect_visitors_min_pct, effect_visitors_max_pct,
            effect_appeal, effect_fixed_costs, effect_variable_costs,
            effect_capacity, effect_utilization_pct,
            effect_general_expense_min, effect_general_expense_max
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, ACTIVITY_CARDS)
    print(f"[seed] activity_cards   : {len(ACTIVITY_CARDS)} rows")


def seed_infrastructure_domains(conn: sqlite3.Connection) -> dict:
    """Returns a dict mapping abbreviation -> id for use in node seeding."""
    conn.execute("DELETE FROM infrastructure_domains")
    conn.executemany("""
        INSERT INTO infrastructure_domains (abbreviation, full_name, description, is_reconfigurable)
        VALUES (?,?,?,?)
    """, INFRASTRUCTURE_DOMAINS)
    cursor = conn.execute("SELECT abbreviation, id FROM infrastructure_domains")
    domain_map = {row[0]: row[1] for row in cursor.fetchall()}
    print(f"[seed] infra_domains    : {len(INFRASTRUCTURE_DOMAINS)} rows")
    return domain_map


def seed_infrastructure_nodes(conn: sqlite3.Connection, domain_map: dict) -> None:
    conn.execute("DELETE FROM infrastructure_nodes")
    rows = [
        (domain_map[domain], node_id, norm, capacity)
        for domain, node_id, norm, capacity in INFRASTRUCTURE_NODES
    ]
    conn.executemany("""
        INSERT INTO infrastructure_nodes (domain_id, node_id, norm, total_capacity)
        VALUES (?,?,?,?)
    """, rows)
    print(f"[seed] infra_nodes      : {len(rows)} rows")


def seed_infrastructure_upgrades(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM infrastructure_upgrades")
    conn.executemany("""
        INSERT INTO infrastructure_upgrades
            (module, norm, upgrade_type, capacity_added, cost, delivery_days, duration_days)
        VALUES (?,?,?,?,?,?,?)
    """, INFRASTRUCTURE_UPGRADES)
    print(f"[seed] infra_upgrades   : {len(INFRASTRUCTURE_UPGRADES)} rows")


def run_seed() -> None:
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"Database not found at {DB_PATH}. Run setup_database.py first."
        )

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    print(f"[seed] Seeding database : {DB_PATH}")

    domain_map = seed_infrastructure_domains(conn)
    seed_infrastructure_nodes(conn, domain_map)
    seed_infrastructure_upgrades(conn)
    seed_attractions(conn)
    seed_activity_cards(conn)

    conn.commit()
    conn.close()
    print("[seed] All done.")


if __name__ == "__main__":
    run_seed()
