-- Create PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;


-- public.hdb_combined_resale_flat_prices definition

CREATE TABLE public.hdb_combined_resale_flat_prices (
	month text NULL,
	town text NULL,
	flat_type text NULL,
	block text NULL,
	street_name text NULL,
	storey_range text NULL,
	floor_area_sqm float8 NULL,
	flat_model text NULL,
	lease_commence_date int4 NULL,
	remaining_lease text NULL,  -- Text format: "61 years 04 months" (2017) or integer (2015-2016)
	resale_price numeric NULL
);


-- public.hdb_property_info definition

CREATE TABLE public.hdb_property_info (
	blk_no text NULL,
	street text NULL,
	max_floor_lvl int4 NULL,
	year_completed int4 NULL,
	residential text NULL,
	commercial text NULL,
	market_hawker text NULL,
	miscellaneous text NULL,
	multistorey_carpark text NULL,
	precinct_pavilion text NULL,
	bldg_contract_town text NULL,
	total_dwelling_units int4 NULL,
	room1_sold int4 NULL,
	room2_sold int4 NULL,
	room3_sold int4 NULL,
	room4_sold int4 NULL,
	room5_sold int4 NULL,
	exec_sold int4 NULL,
	multigen_sold int4 NULL,
	studio_apartment_sold int4 NULL,
	room1_rental int4 NULL,
	room2_rental int4 NULL,
	room3_rental int4 NULL,
	other_room_rental int4 NULL,
	postal text NULL,
	full_address text NULL,
	lon float8 NULL,
	lat float8 NULL,
	x float8 NULL,
	y float8 NULL,
	geom_4326 public.geometry(point, 4326) NULL,
	geom_3414 public.geometry(point, 3414) NULL,
	updated_at timestamptz DEFAULT now() NULL,
	canonical_street text NULL
);
CREATE INDEX hdb_property_geom_idx ON public.hdb_property_info USING gist (geom_3414);
CREATE INDEX hdb_property_info_block_idx ON public.hdb_property_info USING btree (blk_no, street);
CREATE INDEX hdb_property_postal_idx ON public.hdb_property_info USING btree (postal);
CREATE INDEX idx_hdb_canonical_street ON public.hdb_property_info USING btree (canonical_street);
CREATE INDEX idx_hdb_geom ON public.hdb_property_info USING gist (geom_4326);
CREATE INDEX idx_hdb_geom_3414 ON public.hdb_property_info USING gist (geom_3414);
CREATE INDEX idx_hdb_geom_geog ON public.hdb_property_info USING gist (geography(geom_4326));
CREATE INDEX idx_hdb_town ON public.hdb_property_info USING btree (bldg_contract_town);


-- public.sg_parks definition

CREATE TABLE public.sg_parks (
	objectid int4 NULL,
	"name" text NULL,
	inc_crc text NULL,
	updated_at text NULL,
	geom_4326 public.geometry(point, 4326) NULL,
	geom_3414 public.geometry(point, 3414) NULL,
	x numeric NULL,
	y numeric NULL
);


-- public.sg_schools definition

CREATE TABLE public.sg_schools (
	school_name text NULL,
	url_address text NULL,
	address text NULL,
	postal_code text NULL,
	telephone_no text NULL,
	telephone_no_2 text NULL,
	fax_no text NULL,
	fax_no_2 text NULL,
	email_address text NULL,
	mrt_desc text NULL,
	bus_desc text NULL,
	principal_name text NULL,
	first_vp_name text NULL,
	second_vp_name text NULL,
	third_vp_name text NULL,
	fourth_vp_name text NULL,
	fifth_vp_name text NULL,
	sixth_vp_name text NULL,
	dgp_code text NULL,
	zone_code text NULL,
	type_code text NULL,
	nature_code text NULL,
	session_code text NULL,
	mainlevel_code text NULL,
	sap_ind text NULL,
	autonomous_ind text NULL,
	gifted_ind text NULL,
	ip_ind text NULL,
	mothertongue1_code text NULL,
	mothertongue2_code text NULL,
	mothertongue3_code text NULL,
	geom_4326 public.geometry(point, 4326) NULL,
	geom_3414 public.geometry(point, 3414) NULL
);


-- public.mrt_exits definition

CREATE TABLE public.mrt_exits (
	objectid int4 NULL,
	station_name text NULL,
	exit_code text NULL,
	inc_crc text NULL,
	updated_at text NULL,
	lon float8 NULL,
	lat float8 NULL,
	geom_4326 public.geometry(point, 4326) NULL,
	geom_3414 public.geometry(point, 3414) NULL
);
CREATE INDEX idx_mrt_geom ON public.mrt_exits USING gist (geom_4326);
CREATE INDEX idx_mrt_geom_3414 ON public.mrt_exits USING gist (geom_3414);
CREATE INDEX idx_mrt_geom_geog ON public.mrt_exits USING gist (geography(geom_4326));
CREATE INDEX idx_mrt_station_name ON public.mrt_exits USING btree (station_name);


-- public.mrt_to_hdb_town definition

CREATE TABLE public.mrt_to_hdb_town (
	station_name text NULL,
	town text NULL,
	num_blocks int8 NULL,
	min_dist_m numeric NULL
);