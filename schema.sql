DROP TABLE IF NOT EXISTS books;

CREATE TABLE books (
id INT PRIMARY KEY,
isbn VARCHAR(255),
title VARCHAR(255),
author VARCHAR(255),
pagecount VARCHAR(255),
averagerating DOUBLE PRECISION,
thumbnail VARCHAR(255));



