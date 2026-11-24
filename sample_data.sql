-- ====================================================================
-- SMART PERSONAL EXPENSE TRACKER - DATABASE CREATION & SAMPLE DATA
-- CBSE Class 12 Informatics Practices / Computer Science Project
-- Database: SQLite3 / MySQL Compatible
-- ====================================================================

-- 1. Table: INCOME
CREATE TABLE IF NOT EXISTS INCOME (
    Income_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Date DATE NOT NULL,
    Source TEXT NOT NULL,
    Amount REAL NOT NULL,
    Payment_Mode TEXT,
    Remarks TEXT
);

-- 2. Table: EXPENDITURE
CREATE TABLE IF NOT EXISTS EXPENDITURE (
    Expense_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Date DATE NOT NULL,
    Category TEXT NOT NULL,
    Item TEXT NOT NULL,
    Amount REAL NOT NULL,
    Payment_Mode TEXT,
    Shop_Name TEXT
);

-- 3. Table: BUDGET
CREATE TABLE IF NOT EXISTS BUDGET (
    Budget_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Month TEXT NOT NULL,
    Category TEXT NOT NULL UNIQUE,
    Budgeted_Amount REAL NOT NULL,
    Spent_Amount REAL DEFAULT 0
);

-- 4. Table: GOALS
CREATE TABLE IF NOT EXISTS GOALS (
    Goal_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Goal_Name TEXT NOT NULL,
    Target_Amount REAL NOT NULL,
    Saved_Amount REAL DEFAULT 0,
    Deadline DATE
);

-- 5. Table: INVESTMENT
CREATE TABLE IF NOT EXISTS INVESTMENT (
    Invest_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Type TEXT NOT NULL,
    Date DATE,
    Amount REAL NOT NULL,
    Current_Value REAL NOT NULL,
    Returns_Percent REAL
);

-- 6. Table: BILL_REMINDER
CREATE TABLE IF NOT EXISTS BILL_REMINDER (
    Bill_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Bill_Name TEXT NOT NULL,
    Due_Date DATE NOT NULL,
    Amount REAL NOT NULL,
    Status TEXT DEFAULT 'Pending'
);

-- ====================================================================
-- SAMPLE INSERT STATEMENTS (FOR PROJECT FILE & VIVA DEMO)
-- ====================================================================

-- Sample Income Records
INSERT INTO INCOME (Date, Source, Amount, Payment_Mode, Remarks) VALUES
('2026-11-01', 'Salary', 55000.0, 'Bank Transfer', 'Monthly tech company stipend'),
('2026-11-12', 'Freelancing', 12500.0, 'UPI', 'Client website UI design'),
('2026-11-20', 'Dividends', 2200.0, 'Direct Deposit', 'Quarterly mutual fund return');

-- Sample Expenditure Records
INSERT INTO EXPENDITURE (Date, Category, Item, Amount, Payment_Mode, Shop_Name) VALUES
('2026-11-02', 'Bills & Utilities', 'Electricity Bill', 2400.0, 'UPI', 'State Electricity Board'),
('2026-11-05', 'Food & Groceries', 'Monthly Supermarket Ration', 6200.0, 'Credit Card', 'DMart'),
('2026-11-08', 'Travel & Fuel', 'Petrol refill', 2100.0, 'Debit Card', 'HP Petrol Pump'),
('2026-11-10', 'Food & Groceries', 'Weekend Cafe & Dining', 1850.0, 'UPI', 'Cafe Coffee Day'),
('2026-11-14', 'Shopping', 'Programming Books & Gear', 3400.0, 'Credit Card', 'Amazon India'),
('2026-11-18', 'Entertainment', 'Movie Tickets & Snacks', 950.0, 'UPI', 'PVR Cinemas'),
('2026-11-21', 'Food & Groceries', 'Online Food Delivery', 1200.0, 'UPI', 'Zomato'),
('2026-11-23', 'Travel & Fuel', 'Metro Card Recharge', 600.0, 'UPI', 'DMRC Metro');

-- Sample Budget Records
INSERT INTO BUDGET (Month, Category, Budgeted_Amount, Spent_Amount) VALUES
('November 2026', 'Food & Groceries', 10000.0, 9250.0),
('November 2026', 'Bills & Utilities', 3000.0, 2400.0),
('November 2026', 'Travel & Fuel', 3500.0, 2700.0),
('November 2026', 'Shopping', 4000.0, 3400.0),
('November 2026', 'Entertainment', 1500.0, 950.0);

-- Sample Goals Records
INSERT INTO GOALS (Goal_Name, Target_Amount, Saved_Amount, Deadline) VALUES
('Buy Coding Laptop', 60000.0, 42000.0, '2027-03-31'),
('Emergency Fund', 30000.0, 24000.0, '2027-06-30'),
('College Trip', 15000.0, 6500.0, '2027-01-15');

-- Sample Investment Records
INSERT INTO INVESTMENT (Type, Date, Amount, Current_Value, Returns_Percent) VALUES
('SIP / Mutual Fund', '2026-08-01', 15000.0, 16800.0, 12.0),
('Fixed Deposit (FD)', '2026-06-15', 25000.0, 26750.0, 7.0),
('Sovereign Gold', '2026-05-10', 12000.0, 13800.0, 15.0);

-- Sample Bill Reminders
INSERT INTO BILL_REMINDER (Bill_Name, Due_Date, Amount, Status) VALUES
('Wi-Fi Fiber Broadband', '2026-11-28', 999.0, 'Pending'),
('Mobile Postpaid Bill', '2026-11-30', 599.0, 'Pending'),
('House Maintenance Rent', '2026-12-05', 12000.0, 'Pending'),
('Gym Subscription', '2026-11-22', 1500.0, 'Paid');

-- ====================================================================
-- KEY QUERIES FOR VIVA & REPORT FILE
-- ====================================================================
-- 1. Total Income
-- SELECT SUM(Amount) AS Total_Income FROM INCOME;

-- 2. Total Expenditure by Category
-- SELECT Category, SUM(Amount) AS Category_Total FROM EXPENDITURE GROUP BY Category ORDER BY Category_Total DESC;

-- 3. Net Savings Calculation
-- SELECT (SELECT COALESCE(SUM(Amount), 0) FROM INCOME) - (SELECT COALESCE(SUM(Amount), 0) FROM EXPENDITURE) AS Net_Savings;

-- 4. Budget Alert Check (>= 80%)
-- SELECT Category, Budgeted_Amount, Spent_Amount, (Spent_Amount/Budgeted_Amount)*100 AS Percentage FROM BUDGET WHERE Spent_Amount >= 0.8 * Budgeted_Amount;

-- 5. Goals Progress Calculation
-- SELECT Goal_Name, Target_Amount, Saved_Amount, ROUND((Saved_Amount/Target_Amount)*100, 1) AS Progress_Percent FROM GOALS;
