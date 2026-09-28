-- =========================
-- USERS
-- =========================
CREATE TYPE user_role_enum AS ENUM (
    'user',
    'admin'
);
-- STATEMENT-END

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE,
    role user_role_enum NOT NULL DEFAULT 'user',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
-- STATEMENT-END

CREATE INDEX idx_users_telegram_id ON users(telegram_id);
-- STATEMENT-END
CREATE INDEX idx_users_role ON users(role);
-- STATEMENT-END
CREATE INDEX idx_users_created_at ON users(created_at);
-- STATEMENT-END

-- =========================
-- CATEGORIES
-- =========================
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    parent_id INTEGER,
    created_at TIMESTAMPTZ DEFAULT now(),

    CONSTRAINT fk_parent_category
        FOREIGN KEY (parent_id)
        REFERENCES categories(id)
        ON DELETE SET NULL
);
-- STATEMENT-END

CREATE INDEX idx_categories_parent_id ON categories(parent_id);
-- STATEMENT-END
CREATE INDEX idx_categories_slug ON categories(slug);
-- STATEMENT-END
CREATE INDEX idx_categories_created_at ON categories(created_at);
-- STATEMENT-END

-- =========================
-- PRODUCTS
-- =========================
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,
    sku VARCHAR(50) UNIQUE,
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    compare_at_price DECIMAL(10, 2),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    category_id INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    fts tsvector,

    CONSTRAINT fk_product_category
        FOREIGN KEY (category_id)
        REFERENCES categories(id)
        ON DELETE CASCADE,

    CONSTRAINT chk_compare_price
        CHECK (compare_at_price IS NULL OR compare_at_price >= price)
);
-- STATEMENT-END

CREATE INDEX idx_products_category_id ON products(category_id);
-- STATEMENT-END
CREATE INDEX idx_products_slug ON products(slug);
-- STATEMENT-END
CREATE INDEX idx_products_sku ON products(sku);
-- STATEMENT-END
CREATE INDEX idx_products_price ON products(price);
-- STATEMENT-END
CREATE INDEX idx_products_stock ON products(stock);
-- STATEMENT-END
CREATE INDEX idx_products_is_active ON products(is_active);
-- STATEMENT-END
CREATE INDEX idx_products_created_at ON products(created_at);
-- STATEMENT-END
CREATE INDEX idx_products_category_active ON products(category_id, is_active);
-- STATEMENT-END
CREATE INDEX idx_products_sku_prefix ON products(sku varchar_pattern_ops);
-- STATEMENT-END
CREATE INDEX idx_products_name_prefix ON products(name varchar_pattern_ops);
-- STATEMENT-END

-- =========================
-- FTS HELPERS & INDEX
-- =========================
CREATE OR REPLACE FUNCTION products_tsvector_trigger()
RETURNS TRIGGER AS $BODY$
BEGIN
    NEW.fts = (
        setweight(to_tsvector('russian', coalesce(NEW.name, '')), 'A') ||
        setweight(to_tsvector('russian', coalesce(NEW.description, '')), 'B')
    );
    RETURN NEW;
END;
$BODY$ LANGUAGE plpgsql;
-- STATEMENT-END

CREATE INDEX idx_products_fts ON products USING gin(fts);
-- STATEMENT-END

CREATE TRIGGER tsvectorupdate
BEFORE INSERT OR UPDATE ON products
FOR EACH ROW EXECUTE FUNCTION products_tsvector_trigger();
-- STATEMENT-END

-- =========================
-- CART ITEMS (USER CART)
-- =========================
CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity BETWEEN 1 AND 1000),
    added_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    CONSTRAINT fk_cart_item_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_cart_item_product
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE CASCADE,
    CONSTRAINT uniq_cart_user_product
        UNIQUE (user_id, product_id)
);
-- STATEMENT-END

CREATE INDEX idx_cart_items_user_id ON cart_items(user_id);
-- STATEMENT-END
CREATE INDEX idx_cart_items_product_id ON cart_items(product_id);
-- STATEMENT-END

-- =========================
-- ORDERS
-- =========================
CREATE TYPE order_status_enum AS ENUM (
    'new',
    'processing',
    'shipped',
    'delivered',
    'cancelled'
);
-- STATEMENT-END

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    status order_status_enum NOT NULL DEFAULT 'new',
    total_price DECIMAL(12, 2) NOT NULL CHECK (total_price >= 0),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    CONSTRAINT fk_order_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE SET NULL
);
-- STATEMENT-END

CREATE INDEX idx_orders_user_id ON orders(user_id);
-- STATEMENT-END
CREATE INDEX idx_orders_status ON orders(status);
-- STATEMENT-END
CREATE INDEX idx_orders_created_at ON orders(created_at);
-- STATEMENT-END

-- =========================
-- ORDER ITEMS
-- =========================
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    quantity INTEGER NOT NULL CHECK (quantity > 0),

    CONSTRAINT fk_order_item_order
        FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_order_item_product
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE RESTRICT
);
-- STATEMENT-END

CREATE INDEX idx_order_items_order_id ON order_items(order_id);
-- STATEMENT-END
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
-- STATEMENT-END

-- =========================
-- FAVORITES (WISHLIST)
-- =========================
CREATE TABLE favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    added_at TIMESTAMPTZ DEFAULT now(),

    CONSTRAINT fk_favorite_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_favorite_product
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE CASCADE,
    CONSTRAINT uniq_user_product_favorite
        UNIQUE (user_id, product_id)
);
-- STATEMENT-END

CREATE INDEX idx_favorites_user_id ON favorites(user_id);
-- STATEMENT-END
CREATE INDEX idx_favorites_product_id ON favorites(product_id);
-- STATEMENT-END
CREATE INDEX idx_favorites_added_at ON favorites(added_at);
-- STATEMENT-END

-- =========================
-- UPDATED_AT TRIGGERS
-- =========================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $BODY$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$BODY$ LANGUAGE plpgsql;
-- STATEMENT-END

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
-- STATEMENT-END

CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
-- STATEMENT-END

CREATE TRIGGER update_cart_items_updated_at
    BEFORE UPDATE ON cart_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
-- STATEMENT-END

CREATE TRIGGER update_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
-- STATEMENT-END
