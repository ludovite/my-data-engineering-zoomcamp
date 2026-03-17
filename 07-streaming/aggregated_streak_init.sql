CREATE TABLE IF NOT EXISTS aggregated_streak (
    window_start TIMESTAMP(3),
    window_end TIMESTAMP(3),
    PU_location_id INT,
    num_trips BIGINT,
    PRIMARY KEY (window_start, window_end, PU_location_id)
);
