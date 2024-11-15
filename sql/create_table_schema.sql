CREATE TABLE tsepcfsummary (
    `etf_code` VARCHAR(50),
    `etf_name` VARCHAR(255),
    `cash_oth` DECIMAL(20, 2),
    `outstanding` DECIMAL(20, 2),
    `fund_date` DATE,
    `amount` DECIMAL(20, 2),
    `dt` INT,
    `update_source` VARCHAR(255) DEFAULT 'jpxwebetfpcfinfo',
    `update_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_idx (etf_code, dt)
);

CREATE TABLE tsepcfdetail (
    `etf_code` VARCHAR(50),
    `code` VARCHAR(100),
    `name` VARCHAR(255),
    `istn` CHAR(12),
    `exchange` VARCHAR(10),
    `currency` CHAR(3),
    `shere_amount` DECIMAL(15, 2),
    `stock_price` DECIMAL(15, 2),
    `dt` INT,
    `update_source` VARCHAR(255) DEFAULT 'jpxwebetfpcfinfo',
    `update_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_idx (etf_code, code, dt),
    FOREIGN KEY (etf_code) REFERENCES tsepcfsummary(etf_code)
);
