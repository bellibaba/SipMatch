CREATE DATABASE IF NOT EXISTS sipmatch;
USE sipmatch;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS drinks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL UNIQUE,
    type VARCHAR(60) NOT NULL,
    flavor_profile VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    sweetness ENUM('low', 'medium', 'high') NOT NULL DEFAULT 'medium',
    acidity ENUM('low', 'medium', 'high') NOT NULL DEFAULT 'medium',
    strength ENUM('low', 'medium', 'high') NOT NULL DEFAULT 'medium',
    aggregate_rating DECIMAL(3,2) NOT NULL DEFAULT 0,
    rating_count INT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS snacks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL UNIQUE,
    description VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS pairings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    drink_id INT NOT NULL,
    snack_id INT NOT NULL,
    reason VARCHAR(255) NOT NULL,
    UNIQUE KEY unique_pairing (drink_id, snack_id),
    FOREIGN KEY (drink_id) REFERENCES drinks(id) ON DELETE CASCADE,
    FOREIGN KEY (snack_id) REFERENCES snacks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ratings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    drink_id INT NOT NULL,
    rating DECIMAL(2,1) NOT NULL,
    rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT rating_range CHECK (rating >= 1 AND rating <= 5),
    UNIQUE KEY unique_user_drink_rating (user_id, drink_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (drink_id) REFERENCES drinks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    sweetness ENUM('low', 'medium', 'high') NOT NULL DEFAULT 'medium',
    acidity ENUM('low', 'medium', 'high') NOT NULL DEFAULT 'medium',
    strength ENUM('low', 'medium', 'high') NOT NULL DEFAULT 'medium',
    preferred_type VARCHAR(60) NOT NULL DEFAULT 'Any',
    past_purchases TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

INSERT IGNORE INTO drinks
    (name, type, flavor_profile, description, sweetness, acidity, strength, aggregate_rating, rating_count)
VALUES
    ('Cloudline Pinot Noir', 'Red Wine', 'Cherry, raspberry, gentle spice', 'A silky, lighter red that is friendly to beginners.', 'low', 'high', 'medium', 4.20, 18),
    ('Kim Crawford Sauvignon Blanc', 'White Wine', 'Citrus, passionfruit, fresh herbs', 'Bright and zesty with a crisp, refreshing finish.', 'low', 'high', 'medium', 4.10, 24),
    ('Chateau Ste. Michelle Riesling', 'White Wine', 'Peach, lime, honeysuckle', 'A fruit-forward white balancing gentle sweetness with freshness.', 'high', 'high', 'low', 4.30, 31),
    ('La Marca Prosecco', 'Sparkling Wine', 'Green apple, lemon, white flowers', 'Light bubbles and clean fruit make this an easy celebration pick.', 'medium', 'high', 'low', 4.00, 42),
    ('Sierra Nevada Pale Ale', 'Beer', 'Grapefruit, pine, toasted malt', 'A classic pale ale with clear hop character and a balanced finish.', 'low', 'medium', 'medium', 4.20, 35),
    ('Modelo Especial', 'Beer', 'Grain, honey, light herbs', 'A crisp lager with mild malt sweetness and easy refreshment.', 'low', 'medium', 'low', 3.90, 51),
    ('Buffalo Trace Bourbon', 'Whiskey', 'Caramel, vanilla, oak', 'A rounded bourbon with warming spice and a gently sweet finish.', 'medium', 'low', 'high', 4.50, 46),
    ('Hendrick''s Gin', 'Gin', 'Cucumber, rose, juniper', 'A floral, botanical gin with signature cooling cucumber notes.', 'low', 'medium', 'high', 4.40, 39),
    ('Baileys Original', 'Liqueur', 'Cream, cocoa, vanilla', 'A rich and sweet cream liqueur suited to dessert occasions.', 'high', 'low', 'medium', 4.10, 29),
    ('Angry Orchard Crisp Apple', 'Cider', 'Ripe apple, light citrus', 'An approachable sweet cider with lively bubbles.', 'high', 'medium', 'low', 3.80, 22);

INSERT IGNORE INTO snacks (name, description) VALUES
    ('Brie and crackers', 'Creamy soft cheese with crisp neutral crackers.'),
    ('Spiced almonds', 'Roasted almonds with smoky warming spice.'),
    ('Dark chocolate', 'Bittersweet chocolate with deep cocoa notes.'),
    ('Salt-and-vinegar chips', 'Crunchy, salty chips with a sharp tang.'),
    ('Fish tacos', 'Fresh tacos with citrus, cabbage, and mild salsa.'),
    ('Apple slices and cheddar', 'Crisp fruit with firm, savory cheese.'),
    ('Popcorn', 'Light, salty, buttery crunch.'),
    ('Prosciutto', 'Delicate cured meat with rich savory flavor.'),
    ('Spicy chicken bites', 'Crisp chicken with chile heat.'),
    ('Vanilla cookies', 'Light buttery cookies with mellow sweetness.');

INSERT IGNORE INTO pairings (drink_id, snack_id, reason) VALUES
    (1, 1, 'The creamy cheese softens the wine while its acidity refreshes the palate.'),
    (1, 8, 'Silky red fruit echoes the sweet-salty character of cured meat.'),
    (2, 4, 'Bright citrus meets vinegar tang while bubbles of acidity clear the salt.'),
    (2, 5, 'Herbal citrus notes mirror the fresh toppings on the tacos.'),
    (3, 9, 'A touch of sweetness cools chile heat without overpowering the food.'),
    (3, 6, 'Stone-fruit flavors bridge the apple while acidity balances cheddar.'),
    (4, 7, 'Bubbles lift buttery richness and turn a simple snack festive.'),
    (4, 8, 'Crisp acidity cuts through the prosciutto''s savory fat.'),
    (5, 2, 'Toasted nuts mirror the malt while spice plays with the hops.'),
    (5, 9, 'Hop bitterness and citrus stand up to fried texture and spice.'),
    (6, 5, 'A crisp lager cleanses the palate between bright, savory bites.'),
    (6, 7, 'Light malt and salt make an easy, low-intensity match.'),
    (7, 3, 'Cocoa draws out bourbon''s caramel and vanilla notes.'),
    (7, 2, 'Roasted nuts echo oak and provide a savory contrast to caramel.'),
    (8, 5, 'Botanicals and cucumber feel fresh beside citrus and herbs.'),
    (8, 4, 'Sharp vinegar contrasts the gin''s floral, cooling character.'),
    (9, 3, 'Cream and cocoa amplify the liqueur''s dessert-like richness.'),
    (9, 10, 'Mellow vanilla complements the drink without adding bitterness.'),
    (10, 6, 'Fresh apple reinforces the cider while cheddar adds savory balance.'),
    (10, 9, 'Sweet apple provides contrast and relief from chile heat.');
