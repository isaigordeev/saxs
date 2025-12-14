-- SAXS data storage: q, intensity, error
CREATE TABLE IF NOT EXISTS saxs_data (
    id BIGSERIAL PRIMARY KEY,
    q DOUBLE PRECISION NOT NULL,
    intensity DOUBLE PRECISION NOT NULL,
    error DOUBLE PRECISION
);

CREATE INDEX IF NOT EXISTS idx_saxs_data_q ON saxs_data(q);