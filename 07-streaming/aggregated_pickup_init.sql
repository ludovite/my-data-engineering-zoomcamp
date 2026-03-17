CREATE TABLE IF NOT EXISTS aggregated_pickup (
    window_start TIMESTAMP,
    PU_location_id INT,
    num_trips BIGINT,
    PRIMARY KEY (window_start, PU_location_id)
);
