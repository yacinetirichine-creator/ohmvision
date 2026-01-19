-- OhmVision Platform - Supabase Database Initialization
-- =======================================================
-- Execute this script in Supabase SQL Editor
-- Dashboard → SQL Editor → New Query → Paste & Run

-- Create ENUM types
CREATE TYPE user_role AS ENUM ('admin', 'support', 'client_admin', 'client_user');
CREATE TYPE package_type AS ENUM ('starter', 'business', 'enterprise', 'platinum');
CREATE TYPE contract_status AS ENUM ('trial', 'active', 'suspended', 'cancelled', 'expired');
CREATE TYPE alert_severity AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE alert_type AS ENUM (
    'person_detected', 'intrusion', 'fall_detected', 'man_down', 'ppe_missing',
    'fire_detected', 'smoke_detected', 'vehicle_detected', 'license_plate',
    'crowd_detected', 'suspicious_behavior', 'system_error'
);
CREATE TYPE deployment_type AS ENUM ('cloud', 'on_premise', 'hybrid');

-- =============================================================================
-- CLIENTS & CONTRACTS
-- =============================================================================

CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    address TEXT,
    city VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'France',
    siret VARCHAR(20),
    stripe_customer_id VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE contracts (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    package_type package_type NOT NULL DEFAULT 'starter',
    status contract_status NOT NULL DEFAULT 'trial',
    deployment_type deployment_type DEFAULT 'cloud',
    max_cameras INTEGER DEFAULT 10,
    price_monthly DECIMAL(10, 2),
    start_date DATE NOT NULL,
    end_date DATE,
    trial_ends_at TIMESTAMP,
    stripe_subscription_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- USERS & AUTH
-- =============================================================================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role user_role DEFAULT 'client_user',
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    client_id INTEGER REFERENCES clients(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_client_id ON users(client_id);

-- =============================================================================
-- CAMERAS
-- =============================================================================

CREATE TABLE cameras (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    rtsp_url TEXT,
    username VARCHAR(100),
    password VARCHAR(100),
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    resolution VARCHAR(50),
    fps INTEGER DEFAULT 15,
    is_active BOOLEAN DEFAULT true,
    is_recording BOOLEAN DEFAULT false,
    ptz_capable BOOLEAN DEFAULT false,
    onvif_url TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    zone_type VARCHAR(50),
    ai_features JSON,
    last_seen TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cameras_client_id ON cameras(client_id);
CREATE INDEX idx_cameras_is_active ON cameras(is_active);

-- =============================================================================
-- ALERTS
-- =============================================================================

CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    camera_id INTEGER REFERENCES cameras(id) ON DELETE SET NULL,
    type alert_type NOT NULL,
    severity alert_severity DEFAULT 'medium',
    title VARCHAR(255) NOT NULL,
    description TEXT,
    detected_at TIMESTAMP NOT NULL,
    thumbnail_url TEXT,
    video_url TEXT,
    metadata JSON,
    is_acknowledged BOOLEAN DEFAULT false,
    acknowledged_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    acknowledged_at TIMESTAMP,
    is_false_positive BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_alerts_client_id ON alerts(client_id);
CREATE INDEX idx_alerts_camera_id ON alerts(camera_id);
CREATE INDEX idx_alerts_detected_at ON alerts(detected_at);
CREATE INDEX idx_alerts_type ON alerts(type);

-- =============================================================================
-- ANALYTICS
-- =============================================================================

CREATE TABLE analytics_events (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    camera_id INTEGER REFERENCES cameras(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    event_data JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analytics_client_timestamp ON analytics_events(client_id, timestamp);
CREATE INDEX idx_analytics_camera_timestamp ON analytics_events(camera_id, timestamp);

-- =============================================================================
-- SUPPORT TICKETS
-- =============================================================================

CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium',
    category VARCHAR(50),
    status VARCHAR(20) DEFAULT 'open',
    ai_handled BOOLEAN DEFAULT false,
    ai_response TEXT,
    ai_resolved BOOLEAN DEFAULT false,
    assigned_to INTEGER REFERENCES users(id) ON DELETE SET NULL,
    resolution TEXT,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ticket_messages (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    message TEXT NOT NULL,
    is_from_ai BOOLEAN DEFAULT false,
    is_internal BOOLEAN DEFAULT false,
    attachments JSON DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- SYSTEM SETTINGS
-- =============================================================================

CREATE TABLE system_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSON NOT NULL,
    category VARCHAR(50) DEFAULT 'general',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_settings_key ON system_settings(key);

-- =============================================================================
-- INSERT DEFAULT ADMIN USER
-- =============================================================================

-- Password: admin123 (bcrypt hashed)
INSERT INTO users (email, hashed_password, first_name, last_name, role, is_active, is_verified)
VALUES (
    'admin@ohmvision.fr',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ND2JWW4LmNqW',
    'Admin',
    'OhmVision',
    'admin',
    true,
    true
);

-- =============================================================================
-- INSERT DEMO CLIENT (Ohm Tronic)
-- =============================================================================

INSERT INTO clients (name, company_name, email, phone, address, city, postal_code, siret, is_active)
VALUES (
    'Ohm Tronic',
    'OHM TRONIC',
    'contact@ohmtronic.fr',
    '+33 1 23 45 67 89',
    '64 Avenue Marinville',
    'Saint-Maur-des-Fossés',
    '94100',
    '12345678900012',
    true
);

-- =============================================================================
-- INSERT DEMO CONTRACT
-- =============================================================================

INSERT INTO contracts (client_id, package_type, status, deployment_type, max_cameras, price_monthly, start_date)
VALUES (
    1,
    'enterprise',
    'active',
    'hybrid',
    100,
    999.00,
    CURRENT_DATE
);

-- =============================================================================
-- SUCCESS MESSAGE
-- =============================================================================

SELECT '✅ OhmVision database initialized successfully!' AS message;
SELECT '👤 Admin credentials:' AS message;
SELECT '   Email: admin@ohmvision.fr' AS credentials;
SELECT '   Password: admin123' AS credentials;
