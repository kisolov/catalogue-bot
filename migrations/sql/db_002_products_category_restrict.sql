-- Потерю товаров при удалении категории теперь запрещает и сама БД, а не только код.
ALTER TABLE products DROP CONSTRAINT fk_product_category;
-- STATEMENT-END
ALTER TABLE products
    ADD CONSTRAINT fk_product_category
    FOREIGN KEY (category_id)
    REFERENCES categories(id)
    ON DELETE RESTRICT;
-- STATEMENT-END
