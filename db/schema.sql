-- SmartRoute AI baseline PostgreSQL design, NOT applied migration.
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE TABLE app_user (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 email text NOT NULL UNIQUE, role text NOT NULL CHECK (role IN ('OPERATOR','DRIVER')),
 is_active boolean NOT NULL DEFAULT true,
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE driver (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), user_id uuid NOT NULL UNIQUE REFERENCES app_user(id),
 display_name text NOT NULL,
 gps_consent boolean NOT NULL DEFAULT false,
 gps_consent_updated_at timestamptz
);
CREATE TABLE delivery_order (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 created_by uuid NOT NULL REFERENCES app_user(id),
 external_reference text,
 address_label text NOT NULL,
 latitude numeric(9,6) NOT NULL CHECK (latitude BETWEEN -90 AND 90),
 longitude numeric(9,6) NOT NULL CHECK (longitude BETWEEN -180 AND 180),
 due_at timestamptz,
 status text NOT NULL DEFAULT 'PENDING'
 CHECK (status IN ('PENDING','ASSIGNED','IN_TRANSIT','DELIVERED','FAILED')),
 created_at timestamptz NOT NULL DEFAULT now(),
 updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE delivery_route (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 driver_id uuid NOT NULL REFERENCES driver(id),
 depot_latitude numeric(9,6) NOT NULL CHECK (depot_latitude BETWEEN -90 AND 90),
 depot_longitude numeric(9,6) NOT NULL CHECK (depot_longitude BETWEEN -180 AND 180),
 status text NOT NULL DEFAULT 'DRAFT'
 CHECK (status IN ('DRAFT','PLANNED','ACTIVE','COMPLETED','CANCELLED')),
 started_at timestamptz, completed_at timestamptz, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE route_stop (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 route_id uuid NOT NULL REFERENCES delivery_route(id),
 order_id uuid NOT NULL REFERENCES delivery_order(id),
 baseline_sequence integer NOT NULL CHECK (baseline_sequence > 0),
 optimized_sequence integer CHECK (optimized_sequence > 0),
 UNIQUE(route_id,order_id), UNIQUE(route_id,baseline_sequence), UNIQUE(route_id,optimized_sequence)
);
CREATE INDEX idx_route_stop_order ON route_stop(order_id);
-- Partial unique constraint across active routes requires maintaining denormalized assignment state or transaction-level checks:
-- Implement a transactional row lock on delivery_order during assignment and check route status before commit.
CREATE TABLE order_status_event (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 order_id uuid NOT NULL REFERENCES delivery_order(id),
 actor_id uuid NOT NULL REFERENCES app_user(id),
 old_status text NOT NULL, new_status text NOT NULL,
 idempotency_key text NOT NULL, occurred_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(actor_id,idempotency_key)
);
CREATE INDEX idx_order_event_order_time ON order_status_event(order_id,occurred_at DESC);
CREATE TABLE driver_location (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 driver_id uuid NOT NULL REFERENCES driver(id),
 route_id uuid NOT NULL REFERENCES delivery_route(id),
 latitude numeric(9,6) NOT NULL CHECK (latitude BETWEEN -90 AND 90),
 longitude numeric(9,6) NOT NULL CHECK (longitude BETWEEN -180 AND 180),
 accuracy_m numeric(8,2) CHECK (accuracy_m >= 0),
 captured_at timestamptz NOT NULL,
 received_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_driver_location_recent ON driver_location(driver_id,received_at DESC);
CREATE TABLE route_evaluation (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 route_id uuid NOT NULL REFERENCES delivery_route(id),
 baseline_seconds integer NOT NULL CHECK (baseline_seconds > 0),
 optimized_seconds integer NOT NULL CHECK (optimized_seconds >= 0),
 matrix_fingerprint text NOT NULL,
 matrix_source text NOT NULL CHECK (matrix_source IN ('google_routes','fixture','synthetic')),
 data_origin text NOT NULL CHECK (data_origin IN ('estimated','synthetic')),
 solver_version text NOT NULL, calculated_at timestamptz NOT NULL DEFAULT now(),
 CHECK (optimized_seconds <= baseline_seconds OR optimized_seconds > baseline_seconds)
);
CREATE TABLE incident (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 order_id uuid NOT NULL REFERENCES delivery_order(id),
 created_by uuid NOT NULL REFERENCES app_user(id),
 incident_type text NOT NULL, description text, created_at timestamptz NOT NULL DEFAULT now()
);
-- Privacy and invariants enforce in transactional application policy:
-- GPS consent + ACTIVE route + actor assignment + server timestamps; explicit deletion/retention jobs.
-- Never commit any real locations or secrets as seed data.
