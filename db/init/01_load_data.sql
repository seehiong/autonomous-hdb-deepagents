-- Load resale flat price data

-- Files with no remaining_lease column (1990-2014)
COPY hdb_combined_resale_flat_prices (month, town, flat_type, block, street_name, storey_range, floor_area_sqm, flat_model, lease_commence_date, resale_price)
FROM '/docker-entrypoint-initdb.d/data/resale_flat_price_1990_1999.csv'
CSV HEADER;

COPY hdb_combined_resale_flat_prices (month, town, flat_type, block, street_name, storey_range, floor_area_sqm, flat_model, lease_commence_date, resale_price)
FROM '/docker-entrypoint-initdb.d/data/resale_flat_price_2000_2012.csv'
CSV HEADER;

COPY hdb_combined_resale_flat_prices (month, town, flat_type, block, street_name, storey_range, floor_area_sqm, flat_model, lease_commence_date, resale_price)
FROM '/docker-entrypoint-initdb.d/data/resale_flat_price_2012_2014.csv'
CSV HEADER;

-- Files with remaining_lease column (2015+)
COPY hdb_combined_resale_flat_prices (month, town, flat_type, block, street_name, storey_range, floor_area_sqm, flat_model, lease_commence_date, remaining_lease, resale_price)
FROM '/docker-entrypoint-initdb.d/data/resale_flat_price_2015_2016.csv'
CSV HEADER;

COPY hdb_combined_resale_flat_prices (month, town, flat_type, block, street_name, storey_range, floor_area_sqm, flat_model, lease_commence_date, remaining_lease, resale_price)
FROM '/docker-entrypoint-initdb.d/data/resale_flat_price_2017.csv'
CSV HEADER;

SELECT format('Loaded %s rows into hdb_combined_resale_flat_prices', COUNT(*))
FROM hdb_combined_resale_flat_prices;


-- Load MOE General Information of schools (Derived)

COPY sg_schools
FROM '/docker-entrypoint-initdb.d/data/sg_schools.csv'
CSV HEADER;


-- Load NParks Parks (Derived)

COPY sg_parks
FROM '/docker-entrypoint-initdb.d/data/sg_parks.csv'
CSV HEADER;


-- Load HDB property information (Derived)

COPY hdb_property_info
FROM '/docker-entrypoint-initdb.d/data/hdb_property_info.csv'
CSV HEADER;


-- Load LTA MRT Station Exit (Derived)

COPY mrt_exits
FROM '/docker-entrypoint-initdb.d/data/mrt_exits.csv'
CSV HEADER;


-- Load MRT to HDB Town (Derived)

COPY mrt_to_hdb_town
FROM '/docker-entrypoint-initdb.d/data/mrt_to_hdb_town.csv'
CSV HEADER;