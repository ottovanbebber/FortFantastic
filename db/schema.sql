-- =============================================================================
-- Fort Fantastic - Reference Database Schema
-- =============================================================================
-- Source: Organization Manual v4.0, Activity Cards v4.4, Infrastructure Cards v3.0
-- Purpose: Static reference data for the AI Decision Support pipeline
-- =============================================================================

-- -----------------------------------------------------------------------------
-- ATTRACTIONS
-- -----------------------------------------------------------------------------
-- All 19 attractions (14 base + 5 purchasable) with full master data,
-- internal control room codes, and infrastructure connector specs.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS attractions (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    name                    TEXT NOT NULL UNIQUE,

    -- Identity
    internal_code           TEXT,               -- Control Room identifier (e.g. C44557788142775)
    category                TEXT,               -- Ride | Show | Gastronomy
    type                    TEXT,               -- Roller Coaster | Free Fall | Cinema | Snack | etc.
    is_base                 INTEGER DEFAULT 1,  -- 1 = available at start, 0 = purchasable
    acquisition_cost        REAL,

    -- Operational specs
    appeal                  REAL NOT NULL,      -- 1–10 scale
    max_capacity_per_hour   REAL,               -- max visitors/hour
    capacity_per_day        REAL,               -- visitors capacity/day
    utilization_pct         REAL,               -- average utilization in %
    utilization_abs         REAL,               -- average utilization absolute/day
    length_ft               REAL,               -- ride length in feet (NULL for shows/food)
    year_of_construction    INTEGER,
    useful_life_years       INTEGER,
    manufacturer            TEXT,

    -- Operating costs (initial values)
    fixed_costs_per_day     REAL,
    variable_costs_per_user REAL,
    sum_variable_costs_day  REAL,               -- variable_costs_per_user * utilization_abs
    sum_fixed_costs_day     REAL,               -- same as fixed_costs_per_day
    overall_costs_day       REAL,               -- sum_variable + sum_fixed
    sales_breakdown_day     REAL,               -- approximated daily sales contribution
    gross_profit_day        REAL,               -- sales_breakdown - overall_costs

    -- Infrastructure connectors
    pds_capacity            INTEGER,            -- capacity demand on PDS node
    pds_norm                TEXT,               -- EU52 | US68
    stm_capacity            INTEGER,            -- capacity demand on STM node
    stm_norm                TEXT                -- U | G | Q
);

-- -----------------------------------------------------------------------------
-- ACTIVITY CARDS
-- -----------------------------------------------------------------------------
-- All ~120 activity cards available to the Operating Business team.
-- Effects use NULL when not applicable to a card.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS activity_cards (
    id                          INTEGER PRIMARY KEY, -- card number as printed
    title                       TEXT NOT NULL,
    category                    TEXT,               -- Campaign | Repair | Upgrade | Maintenance | etc.

    -- Order codes (entered into Control Room Purchase Panel)
    order_code_std              TEXT,               -- e.g. STD-1
    order_code_3p               TEXT,               -- e.g. 3P-1 (alternative)
    order_code_4r               TEXT,               -- e.g. 4R-3 (infrastructure variant)

    -- Timing
    delivery_days               INTEGER,            -- days until delivery
    implementation_days         INTEGER,            -- days attraction is unavailable
    runtime_days                INTEGER,            -- duration of effect

    -- Cost
    price                       REAL,

    -- Usage limit
    uses                        TEXT DEFAULT 'unlimited', -- 'unlimited' or integer as text

    -- Scope (NULL = park-wide effect)
    attraction                  TEXT,               -- specific attraction name or NULL
    attractions_multi           TEXT,               -- comma-separated if multiple attractions
    infrastructure_module       TEXT,               -- BDN | WSN | VSS | etc.
    component                   TEXT,               -- specific component(s)

    -- Effects (NULL = no effect of this type)
    effect_visitors_min_pct     REAL,               -- visitor number change min %
    effect_visitors_max_pct     REAL,               -- visitor number change max %
    effect_appeal               REAL,               -- appeal change
    effect_fixed_costs          REAL,               -- fixed cost change per day
    effect_variable_costs       REAL,               -- variable cost change per user
    effect_capacity             REAL,               -- capacity change per day
    effect_utilization_pct      REAL,               -- utilization change %
    effect_general_expense_min  REAL,               -- general overhead change min %
    effect_general_expense_max  REAL                -- general overhead change max %
);

-- -----------------------------------------------------------------------------
-- INFRASTRUCTURE DOMAINS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS infrastructure_domains (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    abbreviation    TEXT NOT NULL UNIQUE,   -- PDS | STM | BDN | VSS | WSN | PLS | LAS
    full_name       TEXT NOT NULL,
    description     TEXT,
    is_reconfigurable INTEGER DEFAULT 0     -- 1 = PDS and STM only
);

-- -----------------------------------------------------------------------------
-- INFRASTRUCTURE NODES
-- -----------------------------------------------------------------------------
-- Each node belongs to a domain. PDS and STM nodes have norms and capacities.
-- BDN/VSS/WSN/PLS/LAS nodes are managed automatically by the system.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS infrastructure_nodes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    domain_id       INTEGER NOT NULL REFERENCES infrastructure_domains(id),
    node_id         TEXT NOT NULL,          -- e.g. Y1, L2, Q5, As4, C1
    norm            TEXT,                   -- EU52 | US68 | U | G | Q (NULL for non-PDS/STM)
    total_capacity  INTEGER,                -- total capacity units (NULL for non-PDS/STM)
    UNIQUE(domain_id, node_id)
);

-- -----------------------------------------------------------------------------
-- ATTRACTION NODE CONNECTIONS
-- -----------------------------------------------------------------------------
-- Maps which attraction connects to which node in PDS and STM.
-- This is the initial configuration from the game start.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS attraction_node_connections (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    attraction_id   INTEGER NOT NULL REFERENCES attractions(id),
    domain_id       INTEGER NOT NULL REFERENCES infrastructure_domains(id),
    node_id         TEXT NOT NULL,          -- references infrastructure_nodes.node_id
    using_adapter   INTEGER DEFAULT 0,      -- 1 = adapter in use (appeal -1)
    UNIQUE(attraction_id, domain_id)
);

-- -----------------------------------------------------------------------------
-- INFRASTRUCTURE UPGRADES
-- -----------------------------------------------------------------------------
-- Available capacity upgrade options for PDS and STM nodes.
-- Order code format: [Module]-[Norm]-[Node]-[Type]  e.g. PDS-EU52-Y1-A
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS infrastructure_upgrades (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    module          TEXT NOT NULL,          -- PDS | STM
    norm            TEXT NOT NULL,          -- EU52 | US68 | U | G | Q
    upgrade_type    TEXT NOT NULL,          -- A | B | C
    capacity_added  INTEGER NOT NULL,
    cost            REAL NOT NULL,
    delivery_days   INTEGER,
    duration_days   INTEGER                 -- NULL = permanent
);

-- -----------------------------------------------------------------------------
-- INDEXES for common query patterns
-- -----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_cards_attraction   ON activity_cards(attraction);
CREATE INDEX IF NOT EXISTS idx_cards_category     ON activity_cards(category);
CREATE INDEX IF NOT EXISTS idx_cards_price        ON activity_cards(price);
CREATE INDEX IF NOT EXISTS idx_attractions_base   ON attractions(is_base);
CREATE INDEX IF NOT EXISTS idx_attractions_appeal ON attractions(appeal);
CREATE INDEX IF NOT EXISTS idx_nodes_domain       ON infrastructure_nodes(domain_id);
CREATE INDEX IF NOT EXISTS idx_connections_attr   ON attraction_node_connections(attraction_id);
