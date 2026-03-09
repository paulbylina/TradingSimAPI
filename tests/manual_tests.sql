-- check accounts
SELECT * FROM accounts;

-- check positions
SELECT * FROM positions;

-- check orders
SELECT * FROM orders;

-- reset one account balance
UPDATE accounts
SET cash_balance = 100000
WHERE user_id = 1;

-- remove test positions
DELETE FROM positions
WHERE account_id = 1;

-- remove test orders
DELETE FROM orders
WHERE account_id = 1;