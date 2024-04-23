CREATE TABLE potions (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    price DECIMAL(10, 2),
);

CREATE TABLE barrels (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(255) UNIQUE,
    ml_per_barrel INTEGER,
    price DECIMAL(10, 2),
);

CREATE TABLE carts (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
);

CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER,
    potion_id INTEGER,
    quantity INTEGER,
    FOREIGN KEY (cart_id) REFERENCES carts(id),
    FOREIGN KEY (potion_id) REFERENCES potions(id)
);

INSERT INTO potions (sku, name, price)
VALUES 
    ('red_potion', 'Red Potion', 50.00),
    ('green_potion', 'Green Potion', 50.00),
    ('blue_potion', 'Blue Potion', 70.00);
    ('dark_potion', 'Dark Potion', 70.00);

INSERT INTO barrels (sku, ml_per_barrel, price)
VALUES 
    ('small_red_barrel', 100, 100.00),
    ('small_green_barrel', 100, 100.00),
    ('small_blue_barrel', 100, 150.00);
    ('small_dark_barrel', 100, 150.00);

CREATE INDEX idx_potion_sku ON potions (sku);
CREATE INDEX idx_cart_id ON cart_items (cart_id);

