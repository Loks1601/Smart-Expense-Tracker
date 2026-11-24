"""
================================================================================
PROJECT TITLE: SMART PERSONAL EXPENSE TRACKER
CBSE Class 12 Informatics Practices / Computer Science Project
Theme: Formal Obsidian Dark / Black Mode
Typography: Highly Legible Formal Typography (Segoe UI / Calibri)
Technology: Python 3, Tkinter (ttk), SQLite3, Canvas & Matplotlib Analytics
================================================================================
"""

import sqlite3
import datetime
import math
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

# Optional Matplotlib import with graceful fallback to Native Tkinter Canvas
MATPLOTLIB_AVAILABLE = False
try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

DB_NAME = "expense_tracker.db"

# ------------------------------------------------------------------------------
# 1. DATABASE MANAGER
# ------------------------------------------------------------------------------
class DatabaseManager:
    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Table 1: INCOME
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS INCOME (
                Income_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Date DATE NOT NULL,
                Source TEXT NOT NULL,
                Amount REAL NOT NULL,
                Payment_Mode TEXT,
                Remarks TEXT
            );
            """)

            # Table 2: EXPENDITURE
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS EXPENDITURE (
                Expense_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Date DATE NOT NULL,
                Category TEXT NOT NULL,
                Item TEXT NOT NULL,
                Amount REAL NOT NULL,
                Payment_Mode TEXT,
                Shop_Name TEXT
            );
            """)

            # Table 3: BUDGET
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS BUDGET (
                Budget_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Month TEXT NOT NULL,
                Category TEXT NOT NULL UNIQUE,
                Budgeted_Amount REAL NOT NULL,
                Spent_Amount REAL DEFAULT 0
            );
            """)

            # Table 4: GOALS
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS GOALS (
                Goal_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Goal_Name TEXT NOT NULL,
                Target_Amount REAL NOT NULL,
                Saved_Amount REAL DEFAULT 0,
                Deadline DATE
            );
            """)

            # Table 5: INVESTMENT
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS INVESTMENT (
                Invest_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Type TEXT NOT NULL,
                Date DATE,
                Amount REAL NOT NULL,
                Current_Value REAL NOT NULL,
                Returns_Percent REAL
            );
            """)

            # Table 6: BILL_REMINDER
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS BILL_REMINDER (
                Bill_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Bill_Name TEXT NOT NULL,
                Due_Date DATE NOT NULL,
                Amount REAL NOT NULL,
                Status TEXT DEFAULT 'Pending'
            );
            """)
            conn.commit()

    # --- Income Operations ---
    def add_income(self, date, source, amount, mode, remarks):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO INCOME (Date, Source, Amount, Payment_Mode, Remarks) VALUES (?, ?, ?, ?, ?)",
                           (date, source, float(amount), mode, remarks))
            conn.commit()

    def get_all_income(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Income_ID, Date, Source, Amount, Payment_Mode, Remarks FROM INCOME ORDER BY Date DESC")
            return cursor.fetchall()

    def delete_income(self, income_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM INCOME WHERE Income_ID = ?", (income_id,))
            conn.commit()

    # --- Expenditure Operations ---
    def add_expense(self, date, category, item, amount, mode, shop):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO EXPENDITURE (Date, Category, Item, Amount, Payment_Mode, Shop_Name) VALUES (?, ?, ?, ?, ?, ?)",
                           (date, category, item, float(amount), mode, shop))
            conn.commit()
            self.sync_budget_spent()

    def get_all_expenses(self, category_filter=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if category_filter and category_filter != "All":
                cursor.execute("SELECT Expense_ID, Date, Category, Item, Amount, Payment_Mode, Shop_Name FROM EXPENDITURE WHERE Category = ? ORDER BY Date DESC", (category_filter,))
            else:
                cursor.execute("SELECT Expense_ID, Date, Category, Item, Amount, Payment_Mode, Shop_Name FROM EXPENDITURE ORDER BY Date DESC")
            return cursor.fetchall()

    def delete_expense(self, expense_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM EXPENDITURE WHERE Expense_ID = ?", (expense_id,))
            conn.commit()
            self.sync_budget_spent()

    # --- Budget Operations & 80% Alert Calculation ---
    def set_budget(self, month, category, amount):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO BUDGET (Month, Category, Budgeted_Amount, Spent_Amount) 
                VALUES (?, ?, ?, 0)
                ON CONFLICT(Category) DO UPDATE SET Month = excluded.Month, Budgeted_Amount = excluded.Budgeted_Amount
            """, (month, category, float(amount)))
            conn.commit()
            self.sync_budget_spent()

    def sync_budget_spent(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Category, SUM(Amount) FROM EXPENDITURE GROUP BY Category")
            expenses = cursor.fetchall()
            cursor.execute("UPDATE BUDGET SET Spent_Amount = 0")
            for cat, total in expenses:
                cursor.execute("UPDATE BUDGET SET Spent_Amount = ? WHERE Category = ?", (total or 0, cat))
            conn.commit()

    def get_budgets(self):
        self.sync_budget_spent()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Budget_ID, Month, Category, Budgeted_Amount, Spent_Amount FROM BUDGET")
            return cursor.fetchall()

    def get_budget_alerts(self):
        self.sync_budget_spent()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Category, Budgeted_Amount, Spent_Amount,
                       ROUND((Spent_Amount / Budgeted_Amount) * 100, 1) as Percentage
                FROM BUDGET 
                WHERE Spent_Amount >= 0.8 * Budgeted_Amount AND Budgeted_Amount > 0
            """)
            return cursor.fetchall()

    # --- Goals Operations ---
    def add_goal(self, name, target, saved, deadline):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO GOALS (Goal_Name, Target_Amount, Saved_Amount, Deadline) VALUES (?, ?, ?, ?)",
                           (name, float(target), float(saved), deadline))
            conn.commit()

    def update_goal_savings(self, goal_id, added_amount):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE GOALS SET Saved_Amount = Saved_Amount + ? WHERE Goal_ID = ?", (float(added_amount), goal_id))
            conn.commit()

    def get_goals(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Goal_ID, Goal_Name, Target_Amount, Saved_Amount, Deadline,
                       ROUND((Saved_Amount / Target_Amount) * 100, 1) as Progress
                FROM GOALS
            """)
            return cursor.fetchall()

    def delete_goal(self, goal_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM GOALS WHERE Goal_ID = ?", (goal_id,))
            conn.commit()

    # --- Investment Operations ---
    def add_investment(self, itype, date, amount, current_val):
        invested = float(amount)
        current = float(current_val)
        returns_pct = round(((current - invested) / invested) * 100, 2) if invested > 0 else 0
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO INVESTMENT (Type, Date, Amount, Current_Value, Returns_Percent) VALUES (?, ?, ?, ?, ?)",
                           (itype, date, invested, current, returns_pct))
            conn.commit()

    def get_investments(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Invest_ID, Type, Date, Amount, Current_Value, Returns_Percent FROM INVESTMENT ORDER BY Date DESC")
            return cursor.fetchall()

    def delete_investment(self, invest_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM INVESTMENT WHERE Invest_ID = ?", (invest_id,))
            conn.commit()

    # --- Bill Reminders ---
    def add_bill(self, name, due_date, amount):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO BILL_REMINDER (Bill_Name, Due_Date, Amount, Status) VALUES (?, ?, ?, 'Pending')",
                           (name, due_date, float(amount)))
            conn.commit()

    def mark_bill_paid(self, bill_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE BILL_REMINDER SET Status = 'Paid' WHERE Bill_ID = ?", (bill_id,))
            conn.commit()

    def get_bills(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Bill_ID, Bill_Name, Due_Date, Amount, Status FROM BILL_REMINDER ORDER BY Due_Date ASC")
            return cursor.fetchall()

    def delete_bill(self, bill_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM BILL_REMINDER WHERE Bill_ID = ?", (bill_id,))
            conn.commit()

    # --- Metrics & Totals ---
    def get_totals(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COALESCE(SUM(Amount), 0), COUNT(*) FROM INCOME")
            inc_row = cursor.fetchone()
            total_income, count_inc = inc_row[0], inc_row[1]

            cursor.execute("SELECT COALESCE(SUM(Amount), 0), COUNT(*) FROM EXPENDITURE")
            exp_row = cursor.fetchone()
            total_expense, count_exp = exp_row[0], exp_row[1]

            cursor.execute("SELECT COALESCE(SUM(Current_Value), 0), COALESCE(SUM(Amount), 0), COUNT(*) FROM INVESTMENT")
            inv_row = cursor.fetchone()
            total_investment, total_invested_cost, count_inv = inv_row[0], inv_row[1], inv_row[2]

            savings = total_income - total_expense
            return total_income, total_expense, savings, total_investment, count_inc, count_exp, count_inv, total_invested_cost

    def get_category_expenses(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Category, SUM(Amount), COUNT(*) FROM EXPENDITURE GROUP BY Category ORDER BY SUM(Amount) DESC")
            return cursor.fetchall()

    def seed_sample_data(self):
        """Populates realistic demo data for viva demonstrations"""
        today = datetime.date.today()
        d_format = "%Y-%m-%d"
        m_format = "%B %Y"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM INCOME")
            cursor.execute("DELETE FROM EXPENDITURE")
            cursor.execute("DELETE FROM BUDGET")
            cursor.execute("DELETE FROM GOALS")
            cursor.execute("DELETE FROM INVESTMENT")
            cursor.execute("DELETE FROM BILL_REMINDER")

            # Incomes
            incomes = [
                ((today - datetime.timedelta(days=25)).strftime(d_format), "Salary", 58000.0, "Bank Transfer", "Monthly tech stipend"),
                ((today - datetime.timedelta(days=12)).strftime(d_format), "Freelancing", 14500.0, "UPI", "Full-stack UI design contract"),
                ((today - datetime.timedelta(days=5)).strftime(d_format), "Dividends", 2500.0, "Direct Deposit", "Quarterly mutual fund dividend"),
            ]
            cursor.executemany("INSERT INTO INCOME (Date, Source, Amount, Payment_Mode, Remarks) VALUES (?, ?, ?, ?, ?)", incomes)

            # Expenses
            expenses = [
                ((today - datetime.timedelta(days=22)).strftime(d_format), "Bills & Utilities", "Electricity Bill", 2400.0, "UPI", "State Electricity Board"),
                ((today - datetime.timedelta(days=20)).strftime(d_format), "Food & Groceries", "Supermarket Monthly Ration", 6800.0, "Credit Card", "DMart"),
                ((today - datetime.timedelta(days=18)).strftime(d_format), "Travel & Fuel", "Petrol refill", 2200.0, "Debit Card", "HP Petrol Pump"),
                ((today - datetime.timedelta(days=15)).strftime(d_format), "Food & Groceries", "Weekend Dining", 1850.0, "UPI", "Cafe Coffee Day"),
                ((today - datetime.timedelta(days=10)).strftime(d_format), "Shopping", "Programming Reference Books", 3200.0, "Credit Card", "Amazon India"),
                ((today - datetime.timedelta(days=7)).strftime(d_format), "Entertainment", "IMAX Movie & Popcorn", 950.0, "UPI", "PVR Cinemas"),
                ((today - datetime.timedelta(days=4)).strftime(d_format), "Food & Groceries", "Online Dinner Delivery", 1250.0, "UPI", "Zomato"),
                ((today - datetime.timedelta(days=2)).strftime(d_format), "Travel & Fuel", "Metro Card Smart Recharge", 600.0, "UPI", "DMRC Metro"),
            ]
            cursor.executemany("INSERT INTO EXPENDITURE (Date, Category, Item, Amount, Payment_Mode, Shop_Name) VALUES (?, ?, ?, ?, ?, ?)", expenses)

            # Budgets
            current_month_str = today.strftime(m_format)
            budgets = [
                (current_month_str, "Food & Groceries", 11000.0),
                (current_month_str, "Bills & Utilities", 3000.0),
                (current_month_str, "Travel & Fuel", 3500.0),
                (current_month_str, "Shopping", 4000.0),
                (current_month_str, "Entertainment", 1500.0),
            ]
            cursor.executemany("INSERT INTO BUDGET (Month, Category, Budgeted_Amount) VALUES (?, ?, ?)", budgets)

            # Goals
            goals = [
                ("High-Performance Laptop", 65000.0, 48000.0, (today + datetime.timedelta(days=90)).strftime(d_format)),
                ("Emergency Reserve Fund", 35000.0, 28000.0, (today + datetime.timedelta(days=180)).strftime(d_format)),
                ("Educational Conference Trip", 16000.0, 9500.0, (today + datetime.timedelta(days=45)).strftime(d_format)),
            ]
            cursor.executemany("INSERT INTO GOALS (Goal_Name, Target_Amount, Saved_Amount, Deadline) VALUES (?, ?, ?, ?)", goals)

            # Investments
            investments = [
                ("Nifty 50 Index Fund SIP", (today - datetime.timedelta(days=60)).strftime(d_format), 18000.0, 20400.0, 13.33),
                ("Fixed Deposit (FD)", (today - datetime.timedelta(days=120)).strftime(d_format), 25000.0, 26850.0, 7.4),
                ("Sovereign Gold Bond", (today - datetime.timedelta(days=180)).strftime(d_format), 14000.0, 16200.0, 15.71),
            ]
            cursor.executemany("INSERT INTO INVESTMENT (Type, Date, Amount, Current_Value, Returns_Percent) VALUES (?, ?, ?, ?, ?)", investments)

            # Bills
            bills = [
                ("Fiber Broadband Internet", (today + datetime.timedelta(days=3)).strftime(d_format), 999.0, "Pending"),
                ("Mobile Postpaid Plan", (today + datetime.timedelta(days=7)).strftime(d_format), 599.0, "Pending"),
                ("Apartment Maintenance Fee", (today + datetime.timedelta(days=10)).strftime(d_format), 12500.0, "Pending"),
                ("Gym Membership", (today - datetime.timedelta(days=2)).strftime(d_format), 1500.0, "Paid"),
            ]
            cursor.executemany("INSERT INTO BILL_REMINDER (Bill_Name, Due_Date, Amount, Status) VALUES (?, ?, ?, ?)", bills)
            conn.commit()

        self.sync_budget_spent()


# ------------------------------------------------------------------------------
# 2. OBSIDIAN DARK THEMED TKINTER APPLICATION
# ------------------------------------------------------------------------------
class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SMART PERSONAL EXPENSE TRACKER • EXECUTIVE EDITION")
        self.root.geometry("1140x740")
        self.root.minsize(1020, 680)

        # ----------------------------------------------------------------------
        # FORMAL OBSIDIAN BLACK PALETTE
        # ----------------------------------------------------------------------
        self.COLOR_BG = "#090D16"         # Deep black-slate canvas
        self.COLOR_HEADER = "#05080E"     # Obsidian header
        self.COLOR_CARD = "#111827"       # Elevated dark surface
        self.COLOR_CARD_ALT = "#162032"   # Secondary elevated surface
        self.COLOR_INPUT = "#1F2937"      # High-contrast input background
        self.COLOR_BORDER = "#374151"     # Subtle boundary border

        self.COLOR_TEXT_PRIMARY = "#F9FAFB"    # Crisp pure white
        self.COLOR_TEXT_SECONDARY = "#9CA3AF"  # Formal subtle gray
        self.COLOR_TEXT_MUTED = "#6B7280"      # Muted footnote

        self.ACCENT_CYAN = "#06B6D4"      # Bright high-tech cyan
        self.ACCENT_BLUE = "#3B82F6"      # Royal formal blue
        self.COLOR_SUCCESS = "#10B981"    # Emerald green
        self.COLOR_WARNING = "#F59E0B"    # Amber gold
        self.COLOR_DANGER = "#EF4444"     # Ruby red
        self.COLOR_PURPLE = "#8B5CF6"     # Violet purple

        # Formal Legible Fonts
        self.FONT_FAMILY = "Segoe UI"
        self.FONT_TITLE = (self.FONT_FAMILY, 15, "bold")
        self.FONT_SUBTITLE = (self.FONT_FAMILY, 9)
        self.FONT_CARD_TITLE = (self.FONT_FAMILY, 9, "bold")
        self.FONT_CARD_VAL = (self.FONT_FAMILY, 17, "bold")
        self.FONT_BODY = (self.FONT_FAMILY, 10)
        self.FONT_BOLD = (self.FONT_FAMILY, 10, "bold")
        self.FONT_SMALL = (self.FONT_FAMILY, 9)

        self.root.configure(bg=self.COLOR_BG)
        self.db = DatabaseManager()

        self.setup_styles()
        self.build_ui()
        self.refresh_all_views()

    def setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except:
            pass

        # Global Widget Baseline
        style.configure(".", font=self.FONT_BODY, background=self.COLOR_BG, foreground=self.COLOR_TEXT_PRIMARY)

        # Tabbed Notebook
        style.configure("TNotebook", background=self.COLOR_BG, borderwidth=0)
        style.configure("TNotebook.Tab", padding=[18, 9], font=self.FONT_BOLD,
                        background=self.COLOR_CARD, foreground=self.COLOR_TEXT_SECONDARY, borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", self.COLOR_CARD_ALT), ("active", "#1E293B")],
                  foreground=[("selected", self.ACCENT_CYAN), ("active", self.COLOR_TEXT_PRIMARY)])

        # Data Tables (Treeview)
        style.configure("Treeview", rowheight=30, font=self.FONT_SMALL,
                        background=self.COLOR_CARD, fieldbackground=self.COLOR_CARD,
                        foreground=self.COLOR_TEXT_PRIMARY, borderwidth=0)
        style.configure("Treeview.Heading", font=(self.FONT_FAMILY, 9, "bold"),
                        background=self.COLOR_INPUT, foreground=self.COLOR_TEXT_PRIMARY,
                        relief="flat", borderwidth=0, padding=[6, 6])
        style.map("Treeview",
                  background=[("selected", "#1E3A8A")],
                  foreground=[("selected", "#FFFFFF")])

        # Buttons
        style.configure("Accent.TButton", font=self.FONT_BOLD, background=self.ACCENT_BLUE, foreground="#FFFFFF", borderwidth=0)
        style.map("Accent.TButton", background=[("active", "#2563EB")])

        style.configure("Success.TButton", font=self.FONT_BOLD, background=self.COLOR_SUCCESS, foreground="#FFFFFF", borderwidth=0)
        style.map("Success.TButton", background=[("active", "#059669")])

        style.configure("Danger.TButton", font=self.FONT_BOLD, background=self.COLOR_DANGER, foreground="#FFFFFF", borderwidth=0)
        style.map("Danger.TButton", background=[("active", "#DC2626")])

        # Entry and Combobox
        style.configure("TCombobox", fieldbackground=self.COLOR_INPUT, background=self.COLOR_INPUT,
                        foreground=self.COLOR_TEXT_PRIMARY, selectbackground=self.COLOR_INPUT,
                        selectforeground=self.COLOR_TEXT_PRIMARY)
        style.map("TCombobox", fieldbackground=[("readonly", self.COLOR_INPUT)], foreground=[("readonly", self.COLOR_TEXT_PRIMARY)])

        style.configure("TProgressbar", troughcolor=self.COLOR_INPUT, background=self.ACCENT_CYAN, borderwidth=0)

    def build_ui(self):
        # 1. Top Executive Header Bar
        header_frame = tk.Frame(self.root, bg=self.COLOR_HEADER, height=72, highlightbackground=self.COLOR_BORDER, highlightthickness=1)
        header_frame.pack(fill="x", side="top")

        # Left branding
        brand_icon = tk.Label(header_frame, text="🏛️", font=(self.FONT_FAMILY, 20), fg=self.ACCENT_CYAN, bg=self.COLOR_HEADER)
        brand_icon.pack(side="left", padx=(20, 10), pady=12)

        title_container = tk.Frame(header_frame, bg=self.COLOR_HEADER)
        title_container.pack(side="left", pady=12)

        lbl_app_title = tk.Label(title_container, text="SMART PERSONAL EXPENSE TRACKER",
                                 font=self.FONT_TITLE, fg=self.COLOR_TEXT_PRIMARY, bg=self.COLOR_HEADER)
        lbl_app_title.pack(anchor="w")

        lbl_app_sub = tk.Label(title_container, text="CBSE Class 12 IP • Executive Financial Intelligence & Audit System",
                               font=self.FONT_SUBTITLE, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_HEADER)
        lbl_app_sub.pack(anchor="w")

        # Right Header Quick Action Buttons
        btn_export = tk.Button(header_frame, text="📄 Export Audit Report", font=(self.FONT_FAMILY, 9, "bold"),
                               bg=self.COLOR_CARD_ALT, fg=self.ACCENT_CYAN, activebackground=self.COLOR_INPUT,
                               activeforeground="#FFFFFF", relief="flat", padx=12, pady=6, cursor="hand2",
                               highlightbackground=self.COLOR_BORDER, highlightthickness=1, command=self.export_audit_report)
        btn_export.pack(side="right", padx=(10, 20), pady=16)

        btn_seed = tk.Button(header_frame, text="⚡ Seed Mock Data", font=(self.FONT_FAMILY, 9, "bold"),
                             bg="#2563EB", fg="#FFFFFF", activebackground="#1D4ED8",
                             activeforeground="#FFFFFF", relief="flat", padx=12, pady=6, cursor="hand2",
                             command=self.seed_demo_data)
        btn_seed.pack(side="right", padx=5, pady=16)

        # 2. Main Tabbed Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=12)

        # Tabs
        self.tab_dashboard = tk.Frame(self.notebook, bg=self.COLOR_BG)
        self.tab_income = tk.Frame(self.notebook, bg=self.COLOR_BG)
        self.tab_expense = tk.Frame(self.notebook, bg=self.COLOR_BG)
        self.tab_budget = tk.Frame(self.notebook, bg=self.COLOR_BG)
        self.tab_goals = tk.Frame(self.notebook, bg=self.COLOR_BG)
        self.tab_invest = tk.Frame(self.notebook, bg=self.COLOR_BG)
        self.tab_bills = tk.Frame(self.notebook, bg=self.COLOR_BG)
        self.tab_reports = tk.Frame(self.notebook, bg=self.COLOR_BG)

        self.notebook.add(self.tab_dashboard, text="  📊 Executive Dashboard  ")
        self.notebook.add(self.tab_income, text="  💵 Income Ledger  ")
        self.notebook.add(self.tab_expense, text="  🛒 Expenditure Ledger  ")
        self.notebook.add(self.tab_budget, text="  🎯 Budgets & Thresholds  ")
        self.notebook.add(self.tab_goals, text="  🏆 Savings Goals  ")
        self.notebook.add(self.tab_invest, text="  📈 Investment Portfolio  ")
        self.notebook.add(self.tab_bills, text="  🔔 Bill Obligations  ")
        self.notebook.add(self.tab_reports, text="  📉 Visual Analytics  ")

        self.build_dashboard_tab()
        self.build_income_tab()
        self.build_expense_tab()
        self.build_budget_tab()
        self.build_goals_tab()
        self.build_invest_tab()
        self.build_bills_tab()
        self.build_reports_tab()

    # ==========================================================================
    # TAB 1: EXECUTIVE DASHBOARD
    # ==========================================================================
    def build_dashboard_tab(self):
        container = tk.Frame(self.tab_dashboard, bg=self.COLOR_BG)
        container.pack(fill="both", expand=True, padx=15, pady=15)

        # Top 4 Primary Metric Cards
        cards_frame = tk.Frame(container, bg=self.COLOR_BG)
        cards_frame.pack(fill="x", pady=(0, 10))
        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1, uniform="dash_metric")

        self.card_income_val, self.card_income_sub = self.create_metric_card(cards_frame, 0, "TOTAL INFLOW", "₹0.00", "0 transactions", self.COLOR_SUCCESS)
        self.card_expense_val, self.card_expense_sub = self.create_metric_card(cards_frame, 1, "TOTAL OUTFLOW", "₹0.00", "0 transactions", self.COLOR_DANGER)
        self.card_savings_val, self.card_savings_sub = self.create_metric_card(cards_frame, 2, "NET SURPLUS (SAVINGS)", "₹0.00", "Savings Rate: 0.0%", self.ACCENT_CYAN)
        self.card_invest_val, self.card_invest_sub = self.create_metric_card(cards_frame, 3, "PORTFOLIO VALUATION", "₹0.00", "ROI: +0.0%", self.COLOR_PURPLE)

        # Middle Section: Health Score + AI Insights + Alert Center
        middle_frame = tk.Frame(container, bg=self.COLOR_BG)
        middle_frame.pack(fill="both", expand=True, pady=10)
        middle_frame.columnconfigure(0, weight=3)
        middle_frame.columnconfigure(1, weight=2)

        # Left Column: Financial Health & AI Insights Card
        ai_box = tk.Frame(middle_frame, bg=self.COLOR_CARD, highlightbackground=self.COLOR_BORDER, highlightthickness=1, padx=18, pady=16)
        ai_box.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(ai_box, text="💡 AI Spending Intelligence & Health Audit", font=self.FONT_BOLD,
                 fg=self.ACCENT_CYAN, bg=self.COLOR_CARD).pack(anchor="w", pady=(0, 10))

        # Financial Health Score & Gamification Badge Container
        badges_container = tk.Frame(ai_box, bg=self.COLOR_CARD)
        badges_container.pack(fill="x", pady=(0, 10))

        self.lbl_health_score = tk.Label(badges_container, text="🛡️ Health Score: 100/100 (Optimal)", font=self.FONT_BOLD,
                                         fg=self.COLOR_SUCCESS, bg="#064E3B", padx=10, pady=5, relief="flat")
        self.lbl_health_score.pack(side="left", padx=(0, 10))

        self.lbl_saver_badge = tk.Label(badges_container, text="🏆 Saver Badge: Calculating...", font=self.FONT_BOLD,
                                        fg="#FDE68A", bg="#78350F", padx=10, pady=5, relief="flat")
        self.lbl_saver_badge.pack(side="left")

        # Detailed Bullet Points
        self.lbl_insight_1 = tk.Label(ai_box, text="• Analyzing spending patterns across all categories...",
                                      font=self.FONT_BODY, fg=self.COLOR_TEXT_PRIMARY, bg=self.COLOR_CARD, justify="left", wraplength=520)
        self.lbl_insight_1.pack(anchor="w", pady=5)

        self.lbl_insight_2 = tk.Label(ai_box, text="• Calculating prospective month expenditure forecast...",
                                      font=self.FONT_BODY, fg=self.COLOR_TEXT_PRIMARY, bg=self.COLOR_CARD, justify="left", wraplength=520)
        self.lbl_insight_2.pack(anchor="w", pady=5)

        self.lbl_insight_3 = tk.Label(ai_box, text="• Burn Rate Metric: ...",
                                      font=self.FONT_BODY, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD, justify="left", wraplength=520)
        self.lbl_insight_3.pack(anchor="w", pady=5)

        self.lbl_insight_4 = tk.Label(ai_box, text="• Strategic Advisory: Maintain 20%+ savings buffer for emergencies.",
                                      font=self.FONT_SMALL, fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_CARD, justify="left", wraplength=520)
        self.lbl_insight_4.pack(anchor="w", pady=5)

        # Right Column: Active Alerts & Overdue Obligations
        alert_box = tk.Frame(middle_frame, bg=self.COLOR_CARD, highlightbackground=self.COLOR_BORDER, highlightthickness=1, padx=18, pady=16)
        alert_box.grid(row=0, column=1, sticky="nsew")

        tk.Label(alert_box, text="⚠️ Critical Thresholds & Due Obligations", font=self.FONT_BOLD,
                 fg=self.COLOR_DANGER, bg=self.COLOR_CARD).pack(anchor="w", pady=(0, 10))

        self.txt_alerts = tk.Text(alert_box, height=8, font=(self.FONT_FAMILY, 9), relief="flat",
                                  bg=self.COLOR_INPUT, fg="#FCA5A5", insertbackground="#FFFFFF", padx=10, pady=10)
        self.txt_alerts.pack(fill="both", expand=True)

    def create_metric_card(self, parent, col, title, initial_val, initial_sub, color):
        card = tk.Frame(parent, bg=self.COLOR_CARD, highlightbackground=self.COLOR_BORDER, highlightthickness=1, padx=16, pady=14)
        card.grid(row=0, column=col, sticky="nsew", padx=6)

        lbl_title = tk.Label(card, text=title, font=self.FONT_CARD_TITLE, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD)
        lbl_title.pack(anchor="w")

        lbl_val = tk.Label(card, text=initial_val, font=self.FONT_CARD_VAL, fg=color, bg=self.COLOR_CARD)
        lbl_val.pack(anchor="w", pady=(3, 2))

        lbl_sub = tk.Label(card, text=initial_sub, font=self.FONT_SMALL, fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_CARD)
        lbl_sub.pack(anchor="w")
        return lbl_val, lbl_sub

    # ==========================================================================
    # TAB 2: INCOME MODULE
    # ==========================================================================
    def build_income_tab(self):
        container = tk.Frame(self.tab_income, bg=self.COLOR_BG)
        container.pack(fill="both", expand=True, padx=15, pady=15)

        # Left Form
        form_frame = tk.LabelFrame(container, text=" Log Inflow Transaction ", font=self.FONT_BOLD,
                                   bg=self.COLOR_CARD, fg=self.ACCENT_CYAN, padx=15, pady=15,
                                   highlightbackground=self.COLOR_BORDER, highlightthickness=1, relief="flat")
        form_frame.pack(side="left", fill="y", padx=(0, 15))

        tk.Label(form_frame, text="Date (YYYY-MM-DD):", font=self.FONT_SMALL, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD).grid(row=0, column=0, sticky="w", pady=6)
        self.ent_inc_date = tk.Entry(form_frame, font=self.FONT_BODY, bg=self.COLOR_INPUT, fg=self.COLOR_TEXT_PRIMARY,
                                     insertbackground="#FFFFFF", relief="flat", highlightbackground=self.COLOR_BORDER, highlightthickness=1, width=22)
        self.ent_inc_date.grid(row=0, column=1, pady=6, padx=(10, 0))
        self.ent_inc_date.insert(0, datetime.date.today().strftime("%Y-%m-%d"))

        tk.Label(form_frame, text="Source:", font=self.FONT_SMALL, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD).grid(row=1, column=0, sticky="w", pady=6)
        self.cmb_inc_source = ttk.Combobox(form_frame, width=20, values=["Salary", "Pocket Money", "Freelance", "Investment", "Bonus", "Gift", "Other"])
        self.cmb_inc_source.grid(row=1, column=1, pady=6, padx=(10, 0))
        self.cmb_inc_source.set("Salary")

        tk.Label(form_frame, text="Amount (₹):", font=self.FONT_SMALL, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD).grid(row=2, column=0, sticky="w", pady=6)
        self.ent_inc_amount = tk.Entry(form_frame, font=self.FONT_BODY, bg=self.COLOR_INPUT, fg=self.COLOR_TEXT_PRIMARY,
                                       insertbackground="#FFFFFF", relief="flat", highlightbackground=self.COLOR_BORDER, highlightthickness=1, width=22)
        self.ent_inc_amount.grid(row=2, column=1, pady=6, padx=(10, 0))

        tk.Label(form_frame, text="Payment Channel:", font=self.FONT_SMALL, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD).grid(row=3, column=0, sticky="w", pady=6)
        self.cmb_inc_mode = ttk.Combobox(form_frame, width=20, values=["Bank Transfer", "UPI / GPay", "Cash", "Cheque"])
        self.cmb_inc_mode.grid(row=3, column=1, pady=6, padx=(10, 0))
        self.cmb_inc_mode.set("Bank Transfer")

        tk.Label(form_frame, text="Remarks:", font=self.FONT_SMALL, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD).grid(row=4, column=0, sticky="w", pady=6)
        self.ent_inc_remarks = tk.Entry(form_frame, font=self.FONT_BODY, bg=self.COLOR_INPUT, fg=self.COLOR_TEXT_PRIMARY,
                                        insertbackground="#FFFFFF", relief="flat", highlightbackground=self.COLOR_BORDER, highlightthickness=1, width=22)
        self.ent_inc_remarks.grid(row=4, column=1, pady=6, padx=(10, 0))

        btn_add = ttk.Button(form_frame, text="➕ Commit Income Entry", style="Success.TButton", command=self.action_add_income)
        btn_add.grid(row=5, column=0, columnspan=2, pady=(20, 5), sticky="ew")

        # Right Table
        table_frame = tk.Frame(container, bg=self.COLOR_BG)
        table_frame.pack(side="right", fill="both", expand=True)

        self.lbl_inc_counter = tk.Label(table_frame, text="Total Records: 0 | Inflow Sum: ₹0.00", font=self.FONT_BOLD,
                                        fg=self.ACCENT_CYAN, bg=self.COLOR_BG)
        self.lbl_inc_counter.pack(anchor="w", pady=(0, 8))

        cols = ("ID", "Date", "Source", "Amount", "Mode", "Remarks")
        self.tree_income = ttk.Treeview(table_frame, columns=cols, show="headings")
        for col in cols:
            self.tree_income.heading(col, text=col)
            self.tree_income.column(col, anchor="center", width=95)
        self.tree_income.column("Remarks", width=160)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_income.yview)
        self.tree_income.configure(yscrollcommand=scrollbar.set)
        self.tree_income.pack(side="top", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        act_frame = tk.Frame(table_frame, bg=self.COLOR_BG)
        act_frame.pack(fill="x", pady=8)

        btn_del = ttk.Button(act_frame, text="🗑️ Delete Entry", style="Danger.TButton", command=self.action_delete_income)
        btn_del.pack(side="left")

    def action_add_income(self):
        date = self.ent_inc_date.get().strip()
        source = self.cmb_inc_source.get().strip()
        amount = self.ent_inc_amount.get().strip()
        mode = self.cmb_inc_mode.get().strip()
        remarks = self.ent_inc_remarks.get().strip()

        if not date or not source or not amount:
            messagebox.showerror("Validation Error", "Please provide Date, Source, and Amount.")
            return

        try:
            val = float(amount)
            if val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Amount must be a positive numeric value.")
            return

        self.db.add_income(date, source, val, mode, remarks)
        self.ent_inc_amount.delete(0, tk.END)
        self.ent_inc_remarks.delete(0, tk.END)
        self.refresh_all_views()
        messagebox.showinfo("Success", f"Inflow ₹{val:,.2f} recorded from '{source}'.")

    def action_delete_income(self):
        selected = self.tree_income.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an entry to delete.")
            return
        item_id = self.tree_income.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm Deletion", f"Remove Income record ID #{item_id}?"):
            self.db.delete_income(item_id)
            self.refresh_all_views()

    # ==========================================================================
    # TAB 3: EXPENDITURE MODULE
    # ==========================================================================
    def build_expense_tab(self):
        container = tk.Frame(self.tab_expense, bg=self.COLOR_BG)
        container.pack(fill="both", expand=True, padx=15, pady=15)

        # Left Form
        form_frame = tk.LabelFrame(container, text=" Log Outflow Transaction ", font=self.FONT_BOLD,
                                   bg=self.COLOR_CARD, fg=self.ACCENT_CYAN, padx=15, pady=15,
                                   highlightbackground=self.COLOR_BORDER, highlightthickness=1, relief="flat")
        form_frame.pack(side="left", fill="y", padx=(0, 15))

        tk.Label(form_frame, text="Date (YYYY-MM-DD):", font=self.FONT_SMALL, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD).grid(row=0, column=0, sticky="w", pady=6)
        self.ent_exp_date = tk.Entry(form_frame, font=self.FONT_BODY, bg=self.COLOR_INPUT, fg=self.COLOR_TEXT_PRIMARY,
                                     insertbackground="#FFFFFF", relief="flat", highlightbackground=self.COLOR_BORDER, highlightthickness=1, width=22)
        self.ent_exp_date.grid(row=0, column=1, pady=6, padx=(10, 0))
        self.ent_exp_date.insert(0, datetime.date.today().strftime("%Y-%m-%d"))

        tk.Label(form_frame, text="Category:", font=self.FONT_SMALL, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD).grid(row=1, column=0, sticky="w", pady=6)
        self.categories_list = ["Food & Groceries", "Travel & Fuel", "Bills & Utilities", "Shopping", "Entertainment", "Health & Medical", "Education", "Other"]
        self.cmb_exp_cat = ttk.Combobox(form_frame, width=20, values=self.categories_list)
        self.cmb_exp_cat.grid(row=1, column=1, pady=6, padx=(10, 0))
        self.cmb_exp_cat.set("Food & Groceries")

        tk.Label(form_frame, text="Item Description:", font=self.FONT_SMALL, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD).grid(row=2, column=0, sticky="w", pady=6)
        self.ent_exp_item = tk.Entry(form_frame, font=self.FONT_BODY, bg=self.COLOR_INPUT, fg=self.COLOR_TEXT_PRIMARY,
                                     insertbackground="#FFFFFF", relief="flat", highlightbackground=self.COLOR_BORDER, highlightthickness=1, width=22)
        self.ent_exp_item.grid(row=2, column=1, pady=6, padx=(10, 0))

        tk.Label(form_frame, text="Amount (₹):", font=self.FONT_SMALL, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD).grid(row=3, column=0, sticky="w", pady=6)
        self.ent_exp_amount = tk.Entry(form_frame, font=self.FONT_BODY, bg=self.COLOR_INPUT, fg=self.COLOR_TEXT_PRIMARY,
                                       insertbackground="#FFFFFF", relief="flat", highlightbackground=self.COLOR_BORDER, highlightthickness=1, width=22)
        self.ent_exp_amount.grid(row=3, column=1, pady=6, padx=(10, 0))

        tk.Label(form_frame, text="Payment Channel:", font=self.FONT_SMALL, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD).grid(row=4, column=0, sticky="w", pady=6)
        self.cmb_exp_mode = ttk.Combobox(form_frame, width=20, values=["UPI", "Credit Card", "Debit Card", "Cash", "Net Banking"])
        self.cmb_exp_mode.grid(row=4, column=1, pady=6, padx=(10, 0))
        self.cmb_exp_mode.set("UPI")

        tk.Label(form_frame, text="Merchant / Shop:", font=self.FONT_SMALL, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD).grid(row=5, column=0, sticky="w", pady=6)
        self.ent_exp_shop = tk.Entry(form_frame, font=self.FONT_BODY, bg=self.COLOR_INPUT, fg=self.COLOR_TEXT_PRIMARY,
                                     insertbackground="#FFFFFF", relief="flat", highlightbackground=self.COLOR_BORDER, highlightthickness=1, width=22)
        self.ent_exp_shop.grid(row=5, column=1, pady=6, padx=(10, 0))

        btn_add = ttk.Button(form_frame, text="➕ Commit Outflow Entry", style="Accent.TButton", command=self.action_add_expense)
        btn_add.grid(row=6, column=0, columnspan=2, pady=(20, 5), sticky="ew")

        # Right Table
        table_frame = tk.Frame(container, bg=self.COLOR_BG)
        table_frame.pack(side="right", fill="both", expand=True)

        filter_bar = tk.Frame(table_frame, bg=self.COLOR_BG)
        filter_bar.pack(fill="x", pady=(0, 8))

        tk.Label(filter_bar, text="Filter by Category:", font=self.FONT_BOLD, fg=self.COLOR_TEXT_PRIMARY, bg=self.COLOR_BG).pack(side="left", padx=(0, 8))
        self.cmb_filter_cat = ttk.Combobox(filter_bar, values=["All"] + self.categories_list, state="readonly", width=18)
        self.cmb_filter_cat.set("All")
        self.cmb_filter_cat.pack(side="left")
        self.cmb_filter_cat.bind("<<ComboboxSelected>>", lambda e: self.refresh_expense_table())

        self.lbl_exp_counter = tk.Label(filter_bar, text="Total: ₹0.00", font=self.FONT_BOLD, fg=self.COLOR_DANGER, bg=self.COLOR_BG)
        self.lbl_exp_counter.pack(side="right")

        cols = ("ID", "Date", "Category", "Item", "Amount", "Mode", "Merchant")
        self.tree_expense = ttk.Treeview(table_frame, columns=cols, show="headings")
        for col in cols:
            self.tree_expense.heading(col, text=col)
            self.tree_expense.column(col, anchor="center", width=95)
        self.tree_expense.column("Item", width=130)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_expense.yview)
        self.tree_expense.configure(yscrollcommand=scrollbar.set)
        self.tree_expense.pack(side="top", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        act_frame = tk.Frame(table_frame, bg=self.COLOR_BG)
        act_frame.pack(fill="x", pady=8)

        btn_del = ttk.Button(act_frame, text="🗑️ Delete Entry", style="Danger.TButton", command=self.action_delete_expense)
        btn_del.pack(side="left")

    def action_add_expense(self):
        date = self.ent_exp_date.get().strip()
        cat = self.cmb_exp_cat.get().strip()
        item = self.ent_exp_item.get().strip()
        amount = self.ent_exp_amount.get().strip()
        mode = self.cmb_exp_mode.get().strip()
        shop = self.ent_exp_shop.get().strip()

        if not date or not cat or not item or not amount:
            messagebox.showerror("Validation Error", "Please provide Date, Category, Item, and Amount.")
            return

        try:
            val = float(amount)
            if val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Amount must be a positive numeric value.")
            return

        self.db.add_expense(date, cat, item, val, mode, shop)
        self.ent_exp_item.delete(0, tk.END)
        self.ent_exp_amount.delete(0, tk.END)
        self.ent_exp_shop.delete(0, tk.END)

        self.refresh_all_views()
        self.check_category_budget_alert(cat)

    def check_category_budget_alert(self, category):
        alerts = self.db.get_budget_alerts()
        for cat, budgeted, spent, pct in alerts:
            if cat == category:
                if spent >= budgeted:
                    messagebox.showwarning("⚠️ Budget Exceeded", f"Critical Alert: You have EXCEEDED the monthly allocation for '{cat}'!\nBudget: ₹{budgeted:,.2f}\nSpent: ₹{spent:,.2f} ({pct}%)")
                else:
                    messagebox.showwarning("⚠️ 80% Threshold Reached", f"Threshold Warning: '{cat}' spending has reached {pct}% of monthly allocation.\nBudget: ₹{budgeted:,.2f}\nSpent: ₹{spent:,.2f}")
                break

    def action_delete_expense(self):
        selected = self.tree_expense.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an entry to delete.")
            return
        item_id = self.tree_expense.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm Deletion", f"Remove Outflow record ID #{item_id}?"):
            self.db.delete_expense(item_id)
            self.refresh_all_views()

    # ==========================================================================
    # TAB 4: BUDGET & THRESHOLDS MODULE
    # ==========================================================================
    def build_budget_tab(self):
        container = tk.Frame(self.tab_budget, bg=self.COLOR_BG)
        container.pack(fill="both", expand=True, padx=15, pady=15)

        form_frame = tk.LabelFrame(container, text=" Configure Category Ceiling ", font=self.FONT_BOLD,
                                   bg=self.COLOR_CARD, fg=self.ACCENT_CYAN, padx=15, pady=15,
                                   highlightbackground=self.COLOR_BORDER, highlightthickness=1, relief="flat")
        form_frame.pack(side="left", fill="y", padx=(0, 15))

        tk.Label(form_frame, text="Month / Period:", font=self.FONT_SMALL, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD).grid(row=0, column=0, sticky="w", pady=6)
        self.ent_bud_month = tk.Entry(form_frame, font=self.FONT_BODY, bg=self.COLOR_INPUT, fg=self.COLOR_TEXT_PRIMARY,
                                      insertbackground="#FFFFFF", relief="flat", highlightbackground=self.COLOR_BORDER, highlightthickness=1, width=22)
        self.ent_bud_month.grid(row=0, column=1, pady=6, padx=(10, 0))
        self.ent_bud_month.insert(0, datetime.date.today().strftime("%B %Y"))

        tk.Label(form_frame, text="Category:", font=self.FONT_SMALL, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD).grid(row=1, column=0, sticky="w", pady=6)
        self.cmb_bud_cat = ttk.Combobox(form_frame, width=20, values=self.categories_list)
        self.cmb_bud_cat.grid(row=1, column=1, pady=6, padx=(10, 0))
        self.cmb_bud_cat.set("Food & Groceries")

        tk.Label(form_frame, text="Budget Limit (₹):", font=self.FONT_SMALL, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD).grid(row=2, column=0, sticky="w", pady=6)
        self.ent_bud_amount = tk.Entry(form_frame, font=self.FONT_BODY, bg=self.COLOR_INPUT, fg=self.COLOR_TEXT_PRIMARY,
                                       insertbackground="#FFFFFF", relief="flat", highlightbackground=self.COLOR_BORDER, highlightthickness=1, width=22)
        self.ent_bud_amount.grid(row=2, column=1, pady=6, padx=(10, 0))

        btn_set = ttk.Button(form_frame, text="💾 Establish Budget Limit", style="Accent.TButton", command=self.action_set_budget)
        btn_set.grid(row=3, column=0, columnspan=2, pady=(20, 5), sticky="ew")

        info_lbl = tk.Label(form_frame, text="• 80% Early Warning Rule:\n  When actual expenses cross 80%\n  of planned allocation, system\n  triggers auditory & visual\n  high-priority notifications.",
                            font=self.FONT_SMALL, fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_CARD, justify="left")
        info_lbl.grid(row=4, column=0, columnspan=2, pady=(20, 0), sticky="w")

        table_frame = tk.Frame(container, bg=self.COLOR_BG)
        table_frame.pack(side="right", fill="both", expand=True)

        cols = ("ID", "Month", "Category", "Budgeted", "Spent", "% Used", "Status")
        self.tree_budget = ttk.Treeview(table_frame, columns=cols, show="headings")
        for col in cols:
            self.tree_budget.heading(col, text=col)
            self.tree_budget.column(col, anchor="center", width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_budget.yview)
        self.tree_budget.configure(yscrollcommand=scrollbar.set)
        self.tree_budget.pack(fill="both", expand=True)

    def action_set_budget(self):
        month = self.ent_bud_month.get().strip()
        cat = self.cmb_bud_cat.get().strip()
        amount = self.ent_bud_amount.get().strip()

        if not month or not cat or not amount:
            messagebox.showerror("Validation Error", "All fields are required.")
            return

        try:
            val = float(amount)
            if val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Budget limit must be greater than zero.")
            return

        self.db.set_budget(month, cat, val)
        self.ent_bud_amount.delete(0, tk.END)
        self.refresh_all_views()
        messagebox.showinfo("Budget Established", f"Monthly ceiling for {cat} set at ₹{val:,.2f}")

    # ==========================================================================
    # TAB 5: SAVINGS GOALS TRACKER
    # ==========================================================================
    def build_goals_tab(self):
        container = tk.Frame(self.tab_goals, bg=self.COLOR_BG)
        container.pack(fill="both", expand=True, padx=15, pady=15)

        form_frame = tk.LabelFrame(container, text=" Define Financial Objective ", font=self.FONT_BOLD,
                                   bg=self.COLOR_CARD, fg=self.ACCENT_CYAN, padx=15, pady=15,
                                   highlightbackground=self.COLOR_BORDER, highlightthickness=1, relief="flat")
        form_frame.pack(side="left", fill="y", padx=(0, 15))

        tk.Label(form_frame, text="Target Goal Title:", font=self.FONT_SMALL, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD).grid(row=0, column=0, sticky="w", pady=6)
        self.ent_goal_name = tk.Entry(form_frame, font=self.FONT_BODY, bg=self.COLOR_INPUT, fg=self.COLOR_TEXT_PRIMARY,
                                      insertbackground="#FFFFFF", relief="flat", highlightbackground=self.COLOR_BORDER, highlightthickness=1, width=22)
        self.ent_goal_name.grid(row=0, column=1, pady=6, padx=(10, 0))

        tk.Label(form_frame, text="Target Capital (₹):", font=self.FONT_SMALL, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD).grid(row=1, column=0, sticky="w", pady=6)
        self.ent_goal_target = tk.Entry(form_frame, font=self.FONT_BODY, bg=self.COLOR_INPUT, fg=self.COLOR_TEXT_PRIMARY,
                                        insertbackground="#FFFFFF", relief="flat", highlightbackground=self.COLOR_BORDER, highlightthickness=1, width=22)
        self.ent_goal_target.grid(row=1, column=1, pady=6, padx=(10, 0))

        tk.Label(form_frame, text="Initial Capital (₹):", font=self.FONT_SMALL, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD).grid(row=2, column=0, sticky="w", pady=6)
        self.ent_goal_saved = tk.Entry(form_frame, font=self.FONT_BODY, bg=self.COLOR_INPUT, fg=self.COLOR_TEXT_PRIMARY,
                                       insertbackground="#FFFFFF", relief="flat", highlightbackground=self.COLOR_BORDER, highlightthickness=1, width=22)
        self.ent_goal_saved.grid(row=2, column=1, pady=6, padx=(10, 0))
        self.ent_goal_saved.insert(0, "0")

        tk.Label(form_frame, text="Target Maturity Date:", font=self.FONT_SMALL, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD).grid(row=3, column=0, sticky="w", pady=6)
        self.ent_goal_date = tk.Entry(form_frame, font=self.FONT_BODY, bg=self.COLOR_INPUT, fg=self.COLOR_TEXT_PRIMARY,
                                      insertbackground="#FFFFFF", relief="flat", highlightbackground=self.COLOR_BORDER, highlightthickness=1, width=22)
        self.ent_goal_date.grid(row=3, column=1, pady=6, padx=(10, 0))
        next_quarter = (datetime.date.today() + datetime.timedelta(days=120)).strftime("%Y-%m-%d")
        self.ent_goal_date.insert(0, next_quarter)

        btn_add = ttk.Button(form_frame, text="🎯 Establish Goal", style="Success.TButton", command=self.action_add_goal)
        btn_add.grid(row=4, column=0, columnspan=2, pady=(20, 5), sticky="ew")

        # Right: Cards Container
        self.goals_cards_container = tk.Frame(container, bg=self.COLOR_BG)
        self.goals_cards_container.pack(side="right", fill="both", expand=True)

    def action_add_goal(self):
        name = self.ent_goal_name.get().strip()
        target = self.ent_goal_target.get().strip()
        saved = self.ent_goal_saved.get().strip()
        deadline = self.ent_goal_date.get().strip()

        if not name or not target or not deadline:
            messagebox.showerror("Error", "Please provide Title, Target Capital, and Deadline.")
            return

        try:
            t_val = float(target)
            s_val = float(saved) if saved else 0.0
            if t_val <= 0 or s_val < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Amounts must be valid numeric values.")
            return

        self.db.add_goal(name, t_val, s_val, deadline)
        self.ent_goal_name.delete(0, tk.END)
        self.ent_goal_target.delete(0, tk.END)
        self.ent_goal_saved.delete(0, tk.END)
        self.ent_goal_saved.insert(0, "0")
        self.refresh_all_views()
        messagebox.showinfo("Success", f"Financial Goal '{name}' initiated.")

    def action_deposit_to_goal(self, goal_id, goal_name):
        amt_str = simpledialog.askstring("Allocate Funds", f"Specify allocation amount towards '{goal_name}' (₹):")
        if amt_str:
            try:
                amt = float(amt_str)
                if amt <= 0:
                    raise ValueError
                self.db.update_goal_savings(goal_id, amt)
                self.refresh_all_views()
                messagebox.showinfo("Capital Allocated", f"Successfully allocated ₹{amt:,.2f} towards {goal_name}.")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid positive numerical amount.")

    def action_delete_goal(self, goal_id):
        if messagebox.askyesno("Confirm Deletion", "Decommission this financial goal?"):
            self.db.delete_goal(goal_id)
            self.refresh_all_views()

    # ==========================================================================
    # TAB 6: INVESTMENT TRACKER
    # ==========================================================================
    def build_invest_tab(self):
        container = tk.Frame(self.tab_invest, bg=self.COLOR_BG)
        container.pack(fill="both", expand=True, padx=15, pady=15)

        form_frame = tk.LabelFrame(container, text=" Register Portfolio Asset ", font=self.FONT_BOLD,
                                   bg=self.COLOR_CARD, fg=self.ACCENT_CYAN, padx=15, pady=15,
                                   highlightbackground=self.COLOR_BORDER, highlightthickness=1, relief="flat")
        form_frame.pack(side="left", fill="y", padx=(0, 15))

        tk.Label(form_frame, text="Asset Instrument:", font=self.FONT_SMALL, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD).grid(row=0, column=0, sticky="w", pady=6)
        self.cmb_inv_type = ttk.Combobox(form_frame, width=20, values=["SIP / Mutual Fund", "Fixed Deposit (FD)", "Stock Equity", "Sovereign Gold", "Crypto / Other"])
        self.cmb_inv_type.grid(row=0, column=1, pady=6, padx=(10, 0))
        self.cmb_inv_type.set("SIP / Mutual Fund")

        tk.Label(form_frame, text="Purchase Date:", font=self.FONT_SMALL, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD).grid(row=1, column=0, sticky="w", pady=6)
        self.ent_inv_date = tk.Entry(form_frame, font=self.FONT_BODY, bg=self.COLOR_INPUT, fg=self.COLOR_TEXT_PRIMARY,
                                     insertbackground="#FFFFFF", relief="flat", highlightbackground=self.COLOR_BORDER, highlightthickness=1, width=22)
        self.ent_inv_date.grid(row=1, column=1, pady=6, padx=(10, 0))
        self.ent_inv_date.insert(0, datetime.date.today().strftime("%Y-%m-%d"))

        tk.Label(form_frame, text="Invested Cost (₹):", font=self.FONT_SMALL, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD).grid(row=2, column=0, sticky="w", pady=6)
        self.ent_inv_amt = tk.Entry(form_frame, font=self.FONT_BODY, bg=self.COLOR_INPUT, fg=self.COLOR_TEXT_PRIMARY,
                                    insertbackground="#FFFFFF", relief="flat", highlightbackground=self.COLOR_BORDER, highlightthickness=1, width=22)
        self.ent_inv_amt.grid(row=2, column=1, pady=6, padx=(10, 0))

        tk.Label(form_frame, text="Current Value (₹):", font=self.FONT_SMALL, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD).grid(row=3, column=0, sticky="w", pady=6)
        self.ent_inv_curr = tk.Entry(form_frame, font=self.FONT_BODY, bg=self.COLOR_INPUT, fg=self.COLOR_TEXT_PRIMARY,
                                     insertbackground="#FFFFFF", relief="flat", highlightbackground=self.COLOR_BORDER, highlightthickness=1, width=22)
        self.ent_inv_curr.grid(row=3, column=1, pady=6, padx=(10, 0))

        btn_add = ttk.Button(form_frame, text="📈 Commit Asset to Portfolio", style="Success.TButton", command=self.action_add_investment)
        btn_add.grid(row=4, column=0, columnspan=2, pady=(20, 5), sticky="ew")

        table_frame = tk.Frame(container, bg=self.COLOR_BG)
        table_frame.pack(side="right", fill="both", expand=True)

        self.lbl_inv_counter = tk.Label(table_frame, text="Portfolio Summary: Cost ₹0.00 | Market ₹0.00", font=self.FONT_BOLD,
                                        fg=self.COLOR_PURPLE, bg=self.COLOR_BG)
        self.lbl_inv_counter.pack(anchor="w", pady=(0, 8))

        cols = ("ID", "Asset Type", "Date", "Invested (₹)", "Current Value (₹)", "ROI (%)")
        self.tree_invest = ttk.Treeview(table_frame, columns=cols, show="headings")
        for col in cols:
            self.tree_invest.heading(col, text=col)
            self.tree_invest.column(col, anchor="center", width=110)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_invest.yview)
        self.tree_invest.configure(yscrollcommand=scrollbar.set)
        self.tree_invest.pack(fill="both", expand=True)

        act_frame = tk.Frame(table_frame, bg=self.COLOR_BG)
        act_frame.pack(fill="x", pady=8)

        btn_del = ttk.Button(act_frame, text="🗑️ Liquidate / Delete Asset", style="Danger.TButton", command=self.action_delete_investment)
        btn_del.pack(side="left")

    def action_add_investment(self):
        itype = self.cmb_inv_type.get().strip()
        date = self.ent_inv_date.get().strip()
        amt = self.ent_inv_amt.get().strip()
        curr = self.ent_inv_curr.get().strip()

        if not itype or not amt or not curr:
            messagebox.showerror("Error", "Please provide Asset Instrument, Cost, and Current Value.")
            return

        try:
            a_val = float(amt)
            c_val = float(curr)
            if a_val <= 0 or c_val < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Financial values must be positive numbers.")
            return

        self.db.add_investment(itype, date, a_val, c_val)
        self.ent_inv_amt.delete(0, tk.END)
        self.ent_inv_curr.delete(0, tk.END)
        self.refresh_all_views()
        messagebox.showinfo("Asset Registered", f"Asset '{itype}' recorded in portfolio.")

    def action_delete_investment(self):
        selected = self.tree_invest.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an asset to delete.")
            return
        item_id = self.tree_invest.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm Liquidate", f"Remove asset record ID #{item_id}?"):
            self.db.delete_investment(item_id)
            self.refresh_all_views()

    # ==========================================================================
    # TAB 7: BILL OBLIGATIONS MODULE
    # ==========================================================================
    def build_bills_tab(self):
        container = tk.Frame(self.tab_bills, bg=self.COLOR_BG)
        container.pack(fill="both", expand=True, padx=15, pady=15)

        form_frame = tk.LabelFrame(container, text=" Schedule Bill Obligation ", font=self.FONT_BOLD,
                                   bg=self.COLOR_CARD, fg=self.ACCENT_CYAN, padx=15, pady=15,
                                   highlightbackground=self.COLOR_BORDER, highlightthickness=1, relief="flat")
        form_frame.pack(side="left", fill="y", padx=(0, 15))

        tk.Label(form_frame, text="Bill Description:", font=self.FONT_SMALL, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD).grid(row=0, column=0, sticky="w", pady=6)
        self.ent_bill_name = tk.Entry(form_frame, font=self.FONT_BODY, bg=self.COLOR_INPUT, fg=self.COLOR_TEXT_PRIMARY,
                                      insertbackground="#FFFFFF", relief="flat", highlightbackground=self.COLOR_BORDER, highlightthickness=1, width=22)
        self.ent_bill_name.grid(row=0, column=1, pady=6, padx=(10, 0))

        tk.Label(form_frame, text="Due Maturity Date:", font=self.FONT_SMALL, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD).grid(row=1, column=0, sticky="w", pady=6)
        self.ent_bill_date = tk.Entry(form_frame, font=self.FONT_BODY, bg=self.COLOR_INPUT, fg=self.COLOR_TEXT_PRIMARY,
                                      insertbackground="#FFFFFF", relief="flat", highlightbackground=self.COLOR_BORDER, highlightthickness=1, width=22)
        self.ent_bill_date.grid(row=1, column=1, pady=6, padx=(10, 0))
        self.ent_bill_date.insert(0, (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d"))

        tk.Label(form_frame, text="Bill Amount (₹):", font=self.FONT_SMALL, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD).grid(row=2, column=0, sticky="w", pady=6)
        self.ent_bill_amt = tk.Entry(form_frame, font=self.FONT_BODY, bg=self.COLOR_INPUT, fg=self.COLOR_TEXT_PRIMARY,
                                     insertbackground="#FFFFFF", relief="flat", highlightbackground=self.COLOR_BORDER, highlightthickness=1, width=22)
        self.ent_bill_amt.grid(row=2, column=1, pady=6, padx=(10, 0))

        btn_add = ttk.Button(form_frame, text="🔔 Register Obligation", style="Accent.TButton", command=self.action_add_bill)
        btn_add.grid(row=3, column=0, columnspan=2, pady=(20, 5), sticky="ew")

        table_frame = tk.Frame(container, bg=self.COLOR_BG)
        table_frame.pack(side="right", fill="both", expand=True)

        cols = ("ID", "Bill Description", "Due Date", "Amount (₹)", "Settlement Status")
        self.tree_bills = ttk.Treeview(table_frame, columns=cols, show="headings")
        for col in cols:
            self.tree_bills.heading(col, text=col)
            self.tree_bills.column(col, anchor="center", width=120)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_bills.yview)
        self.tree_bills.configure(yscrollcommand=scrollbar.set)
        self.tree_bills.pack(fill="both", expand=True)

        act_frame = tk.Frame(table_frame, bg=self.COLOR_BG)
        act_frame.pack(fill="x", pady=8)

        btn_pay = ttk.Button(act_frame, text="✅ Mark as Settled (Paid)", style="Success.TButton", command=self.action_mark_bill_paid)
        btn_pay.pack(side="left", padx=(0, 10))

        btn_del = ttk.Button(act_frame, text="🗑️ Delete Obligation", style="Danger.TButton", command=self.action_delete_bill)
        btn_del.pack(side="left")

    def action_add_bill(self):
        name = self.ent_bill_name.get().strip()
        date = self.ent_bill_date.get().strip()
        amt = self.ent_bill_amt.get().strip()

        if not name or not date or not amt:
            messagebox.showerror("Error", "Please provide Bill Description, Due Date, and Amount.")
            return

        try:
            val = float(amt)
            if val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Bill amount must be a positive number.")
            return

        self.db.add_bill(name, date, val)
        self.ent_bill_name.delete(0, tk.END)
        self.ent_bill_amt.delete(0, tk.END)
        self.refresh_all_views()
        messagebox.showinfo("Success", f"Reminder for '{name}' scheduled.")

    def action_mark_bill_paid(self):
        selected = self.tree_bills.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a bill to settle.")
            return
        item_id = self.tree_bills.item(selected[0])['values'][0]
        self.db.mark_bill_paid(item_id)
        self.refresh_all_views()
        messagebox.showinfo("Settled", "Bill obligation marked as Paid.")

    def action_delete_bill(self):
        selected = self.tree_bills.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a bill to remove.")
            return
        item_id = self.tree_bills.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm Deletion", f"Remove bill obligation ID #{item_id}?"):
            self.db.delete_bill(item_id)
            self.refresh_all_views()

    # ==========================================================================
    # TAB 8: CHARTS & REPORTS MODULE
    # ==========================================================================
    def build_reports_tab(self):
        self.reports_container = tk.Frame(self.tab_reports, bg=self.COLOR_BG)
        self.reports_container.pack(fill="both", expand=True, padx=15, pady=15)

    def render_visual_charts(self):
        for widget in self.reports_container.winfo_children():
            widget.destroy()

        categories = self.db.get_category_expenses()
        total_income, total_expense, savings, _, _, _, _, _ = self.db.get_totals()

        if not categories and total_income == 0:
            lbl = tk.Label(self.reports_container, text="No analytical transactions recorded.\nClick '⚡ Seed Mock Data' in the header to visualize analytics immediately.",
                           font=self.FONT_BOLD, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_BG)
            lbl.pack(expand=True)
            return

        self.reports_container.columnconfigure(0, weight=1, uniform="dark_charts")
        self.reports_container.columnconfigure(1, weight=1, uniform="dark_charts")

        # Frame 1: Category Allocation
        frame_pie = tk.Frame(self.reports_container, bg=self.COLOR_CARD, highlightbackground=self.COLOR_BORDER, highlightthickness=1, padx=14, pady=14)
        frame_pie.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(frame_pie, text="🥧 Expenditure Distribution by Category", font=self.FONT_BOLD,
                 fg=self.ACCENT_CYAN, bg=self.COLOR_CARD).pack(anchor="w", pady=(0, 6))

        # Frame 2: Cash Flow Metrics
        frame_bar = tk.Frame(self.reports_container, bg=self.COLOR_CARD, highlightbackground=self.COLOR_BORDER, highlightthickness=1, padx=14, pady=14)
        frame_bar.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        tk.Label(frame_bar, text="📊 Cash Flow Ratio (Inflow vs Outflow vs Reserve)", font=self.FONT_BOLD,
                 fg=self.ACCENT_CYAN, bg=self.COLOR_CARD).pack(anchor="w", pady=(0, 6))

        if MATPLOTLIB_AVAILABLE:
            self.render_matplotlib_charts(frame_pie, frame_bar, categories, total_income, total_expense, savings)
        else:
            self.render_native_canvas_charts(frame_pie, frame_bar, categories, total_income, total_expense, savings)

    def render_matplotlib_charts(self, f_pie, f_bar, categories, total_inc, total_exp, savings):
        # 1. Dark Pie Chart
        fig_pie = Figure(figsize=(4.6, 3.8), dpi=100, facecolor=self.COLOR_CARD)
        ax_pie = fig_pie.add_subplot(111, facecolor=self.COLOR_CARD)
        if categories:
            labels = [c[0] for c in categories]
            values = [c[1] for c in categories]
            colors = ["#38BDF8", "#F87171", "#34D399", "#FBBF24", "#A78BFA", "#F472B6", "#2DD4BF", "#94A3B8"]
            wedges, texts, autotexts = ax_pie.pie(
                values, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors[:len(labels)],
                textprops={'fontsize': 8, 'color': self.COLOR_TEXT_PRIMARY}
            )
            for autotext in autotexts:
                autotext.set_color('#0F172A')
                autotext.set_weight('bold')
        fig_pie.tight_layout()

        canvas_pie = FigureCanvasTkAgg(fig_pie, master=f_pie)
        canvas_pie.draw()
        canvas_pie.get_tk_widget().pack(fill="both", expand=True)

        # 2. Dark Bar Chart
        fig_bar = Figure(figsize=(4.6, 3.8), dpi=100, facecolor=self.COLOR_CARD)
        ax_bar = fig_bar.add_subplot(111, facecolor=self.COLOR_CARD)
        labels = ["Total Inflow", "Total Outflow", "Net Surplus"]
        values = [total_inc, total_exp, max(0, savings)]
        bar_colors = [self.COLOR_SUCCESS, self.COLOR_DANGER, self.ACCENT_CYAN]
        bars = ax_bar.bar(labels, values, color=bar_colors, width=0.48)
        
        ax_bar.tick_params(colors=self.COLOR_TEXT_SECONDARY, labelsize=8)
        ax_bar.spines['bottom'].set_color(self.COLOR_BORDER)
        ax_bar.spines['top'].set_visible(False)
        ax_bar.spines['right'].set_visible(False)
        ax_bar.spines['left'].set_color(self.COLOR_BORDER)

        for bar in bars:
            yval = bar.get_height()
            ax_bar.text(bar.get_x() + bar.get_width()/2.0, yval + (total_inc*0.01 + 200),
                        f"₹{yval:,.0f}", ha='center', va='bottom', fontsize=8, fontweight='bold', color=self.COLOR_TEXT_PRIMARY)
        fig_bar.tight_layout()

        canvas_bar = FigureCanvasTkAgg(fig_bar, master=f_bar)
        canvas_bar.draw()
        canvas_bar.get_tk_widget().pack(fill="both", expand=True)

    def render_native_canvas_charts(self, f_pie, f_bar, categories, total_inc, total_exp, savings):
        """Native Dark Vector Canvas Engine - Guarantees High-Contrast Rendering Without Dependencies"""
        # Canvas 1: Pie Chart
        c_pie = tk.Canvas(f_pie, bg=self.COLOR_CARD, highlightthickness=0)
        c_pie.pack(fill="both", expand=True)

        if categories:
            total_cat_amt = sum(c[1] for c in categories)
            colors = ["#38BDF8", "#F87171", "#34D399", "#FBBF24", "#A78BFA", "#F472B6", "#2DD4BF", "#94A3B8"]
            cx, cy, r = 150, 160, 105
            start_angle = 0
            legend_y = 25

            for i, (cat, amt, count) in enumerate(categories):
                pct = (amt / total_cat_amt) * 100
                extent = (amt / total_cat_amt) * 360
                color = colors[i % len(colors)]

                c_pie.create_arc(cx - r, cy - r, cx + r, cy + r, start=start_angle, extent=extent,
                                 fill=color, outline=self.COLOR_CARD, width=2)
                start_angle += extent

                # Draw Legend on the right
                c_pie.create_rectangle(285, legend_y, 298, legend_y + 13, fill=color, outline="")
                c_pie.create_text(308, legend_y + 6, text=f"{cat} ({pct:.1f}%)", anchor="w",
                                  font=self.FONT_SMALL, fill=self.COLOR_TEXT_PRIMARY)
                legend_y += 24
        else:
            c_pie.create_text(200, 150, text="No expense data available", font=self.FONT_BODY, fill=self.COLOR_TEXT_SECONDARY)

        # Canvas 2: Bar Chart
        c_bar = tk.Canvas(f_bar, bg=self.COLOR_CARD, highlightthickness=0)
        c_bar.pack(fill="both", expand=True)

        items = [
            ("Total Inflow", total_inc, self.COLOR_SUCCESS),
            ("Total Outflow", total_exp, self.COLOR_DANGER),
            ("Net Surplus", max(0, savings), self.ACCENT_CYAN)
        ]
        max_val = max(total_inc, total_exp, max(0, savings), 1)

        base_y = 280
        chart_height = 200
        bar_width = 75
        spacing = 45
        start_x = 65

        # Horizontal Axis
        c_bar.create_line(40, base_y, 450, base_y, fill=self.COLOR_BORDER, width=2)

        for i, (label, val, color) in enumerate(items):
            x1 = start_x + i * (bar_width + spacing)
            x2 = x1 + bar_width
            h = (val / max_val) * chart_height if max_val > 0 else 0
            y1 = base_y - h
            y2 = base_y

            c_bar.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
            c_bar.create_text((x1 + x2)/2, base_y + 20, text=label, font=self.FONT_SMALL, fill=self.COLOR_TEXT_SECONDARY)
            c_bar.create_text((x1 + x2)/2, y1 - 12, text=f"₹{val:,.0f}", font=self.FONT_BOLD, fill=self.COLOR_TEXT_PRIMARY)

    # ==========================================================================
    # DATA REFRESHING, ADVANCED AUDIT & AI LOGIC
    # ==========================================================================
    def refresh_all_views(self):
        self.refresh_dashboard()
        self.refresh_income_table()
        self.refresh_expense_table()
        self.refresh_budget_table()
        self.refresh_goals_cards()
        self.refresh_investments_table()
        self.refresh_bills_table()
        self.render_visual_charts()

    def refresh_dashboard(self):
        total_income, total_expense, savings, total_invest, count_inc, count_exp, count_inv, cost_inv = self.db.get_totals()

        # Update Top Metric Cards
        self.card_income_val.config(text=f"₹{total_income:,.2f}")
        self.card_income_sub.config(text=f"{count_inc} logged transactions")

        self.card_expense_val.config(text=f"₹{total_expense:,.2f}")
        burn_rate_daily = total_expense / 30.0
        self.card_expense_sub.config(text=f"Avg burn: ₹{burn_rate_daily:,.0f}/day")

        self.card_savings_val.config(text=f"₹{savings:,.2f}")
        savings_rate = (savings / total_income * 100) if total_income > 0 else 0.0
        self.card_savings_sub.config(text=f"Savings Ratio: {savings_rate:.1f}%")

        self.card_invest_val.config(text=f"₹{total_invest:,.2f}")
        overall_roi = ((total_invest - cost_inv) / cost_inv * 100) if cost_inv > 0 else 0.0
        self.card_invest_sub.config(text=f"Portfolio ROI: {overall_roi:+.1f}%")

        # 1. Financial Health Score Calculation (Out of 100)
        health_score = 100
        # Savings deduction if under 20%
        if savings_rate < 20:
            health_score -= int(max(0, 20 - savings_rate) * 1.5)
        
        # Budget breach deduction
        alerts = self.db.get_budget_alerts()
        for cat, budgeted, spent, pct in alerts:
            if spent >= budgeted:
                health_score -= 15
            elif pct >= 80:
                health_score -= 5

        # Overdue bills deduction
        bills = self.db.get_bills()
        today = datetime.date.today()
        overdue_count = 0
        for bid, name, due, amt, status in bills:
            if status == "Pending":
                try:
                    due_date_obj = datetime.datetime.strptime(due, "%Y-%m-%d").date()
                    if (due_date_obj - today).days < 0:
                        overdue_count += 1
                        health_score -= 10
                except:
                    pass

        health_score = max(0, min(100, health_score))
        if health_score >= 85:
            self.lbl_health_score.config(text=f"🛡️ Health Score: {health_score}/100 (Grade A • Disciplined)", bg="#064E3B", fg="#A7F3D0")
        elif health_score >= 65:
            self.lbl_health_score.config(text=f"🛡️ Health Score: {health_score}/100 (Grade B • Moderate)", bg="#78350F", fg="#FDE68A")
        else:
            self.lbl_health_score.config(text=f"🛡️ Health Score: {health_score}/100 (Grade C • High Risk)", bg="#7F1D1D", fg="#FECACA")

        # 2. Saver of the Month Gamification Badge
        if savings_rate >= 30:
            self.lbl_saver_badge.config(text=f"🌟 Elite Saver: Saving {savings_rate:.1f}% of income", bg="#78350F", fg="#FDE68A")
        elif savings_rate >= 20:
            self.lbl_saver_badge.config(text=f"🏆 Saver of the Month: Healthy {savings_rate:.1f}% Rate", bg="#064E3B", fg="#6EE7B7")
        elif savings_rate >= 0:
            self.lbl_saver_badge.config(text=f"🌱 Conservative Saver: {savings_rate:.1f}% buffer", bg="#1E3A8A", fg="#BFDBFE")
        else:
            self.lbl_saver_badge.config(text="⚠️ Capital Deficit: Outflow exceeds Inflow", bg="#7F1D1D", fg="#FECACA")

        # 3. AI Insights
        categories = self.db.get_category_expenses()
        if categories and total_expense > 0:
            top_cat, top_amt, _ = categories[0]
            top_pct = (top_amt / total_expense) * 100
            self.lbl_insight_1.config(text=f"• AI Pattern: Dominant outflow is '{top_cat}' at ₹{top_amt:,.2f} ({top_pct:.1f}% of total outflow).")
        else:
            self.lbl_insight_1.config(text="• AI Pattern: Awaiting outflow records to identify dominant categories.")

        # 4. Prospective Month Forecast
        forecast_val = total_expense * 1.065
        if total_expense > 0:
            self.lbl_insight_2.config(text=f"• Predictive Forecast: Prospective month expenditure projected at ₹{forecast_val:,.2f} (based on current velocity).")
            self.lbl_insight_3.config(text=f"• Burn Rate Detail: ₹{burn_rate_daily:,.2f}/day. At this rate, 30-day requirement is ₹{burn_rate_daily*30:,.2f}.")
        else:
            self.lbl_insight_2.config(text="• Predictive Forecast: Sufficient records required for time-series projection.")
            self.lbl_insight_3.config(text="• Burn Rate Detail: Baseline burn rate will calibrate as entries are logged.")

        # 5. Alert Center Box
        self.txt_alerts.delete("1.0", tk.END)
        has_alerts = False
        if alerts:
            has_alerts = True
            for cat, budgeted, spent, pct in alerts:
                if spent >= budgeted:
                    self.txt_alerts.insert(tk.END, f"🚨 CEILING BREACHED: '{cat}' spent ₹{spent:,.0f} / ₹{budgeted:,.0f} ({pct}%)\n")
                else:
                    self.txt_alerts.insert(tk.END, f"⚠️ 80% THRESHOLD: '{cat}' reached {pct}% (₹{spent:,.0f} / ₹{budgeted:,.0f})\n")

        for bid, name, due, amt, status in bills:
            if status == "Pending":
                try:
                    due_date_obj = datetime.datetime.strptime(due, "%Y-%m-%d").date()
                    days_left = (due_date_obj - today).days
                    if days_left < 0:
                        has_alerts = True
                        self.txt_alerts.insert(tk.END, f"❌ OVERDUE OBLIGATION: '{name}' ₹{amt:,.0f} was due {abs(days_left)} days ago!\n")
                    elif days_left <= 5:
                        has_alerts = True
                        self.txt_alerts.insert(tk.END, f"🔔 IMMINENT BILL: '{name}' ₹{amt:,.0f} due in {days_left} days ({due})\n")
                except:
                    pass

        if not has_alerts:
            self.txt_alerts.insert(tk.END, "✅ Compliance Clear: All categories within budget ceiling and zero overdue bills.")

    def refresh_income_table(self):
        for item in self.tree_income.get_children():
            self.tree_income.delete(item)
        records = self.db.get_all_income()
        total_sum = sum(r[3] for r in records)
        self.lbl_inc_counter.config(text=f"Total Records: {len(records)} | Total Inflow: ₹{total_sum:,.2f}")
        for r in records:
            formatted_r = (r[0], r[1], r[2], f"₹{r[3]:,.2f}", r[4], r[5])
            self.tree_income.insert("", "end", values=formatted_r)

    def refresh_expense_table(self):
        for item in self.tree_expense.get_children():
            self.tree_expense.delete(item)
        cat_filter = self.cmb_filter_cat.get()
        records = self.db.get_all_expenses(cat_filter)
        total_sum = sum(r[4] for r in records)
        self.lbl_exp_counter.config(text=f"Showing: {len(records)} entries | Filter Total: ₹{total_sum:,.2f}")
        for r in records:
            formatted_r = (r[0], r[1], r[2], r[3], f"₹{r[4]:,.2f}", r[5], r[6])
            self.tree_expense.insert("", "end", values=formatted_r)

    def refresh_budget_table(self):
        for item in self.tree_budget.get_children():
            self.tree_budget.delete(item)
        records = self.db.get_budgets()
        for r in records:
            bid, month, cat, budgeted, spent = r
            pct = round((spent / budgeted) * 100, 1) if budgeted > 0 else 0
            if spent >= budgeted:
                status = "🚨 EXCEEDED"
            elif pct >= 80:
                status = "⚠️ 80% ALERT"
            else:
                status = "✅ Normal"
            row_vals = (bid, month, cat, f"₹{budgeted:,.2f}", f"₹{spent:,.2f}", f"{pct}%", status)
            self.tree_budget.insert("", "end", values=row_vals)

    def refresh_goals_cards(self):
        for widget in self.goals_cards_container.winfo_children():
            widget.destroy()

        goals = self.db.get_goals()
        if not goals:
            lbl = tk.Label(self.goals_cards_container, text="No financial goals defined yet. Use the left panel to establish one.",
                           font=self.FONT_BOLD, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_BG)
            lbl.pack(pady=50)
            return

        for gid, name, target, saved, deadline, pct in goals:
            card = tk.Frame(self.goals_cards_container, bg=self.COLOR_CARD, highlightbackground=self.COLOR_BORDER, highlightthickness=1, padx=16, pady=12)
            card.pack(fill="x", pady=6)

            top_row = tk.Frame(card, bg=self.COLOR_CARD)
            top_row.pack(fill="x")

            lbl_name = tk.Label(top_row, text=f"🎯 {name}", font=self.FONT_BOLD, fg=self.COLOR_TEXT_PRIMARY, bg=self.COLOR_CARD)
            lbl_name.pack(side="left")

            lbl_deadline = tk.Label(top_row, text=f"Target Date: {deadline}", font=self.FONT_SMALL, fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD)
            lbl_deadline.pack(side="right")

            p_bar = ttk.Progressbar(card, orient="horizontal", mode="determinate", maximum=100)
            p_bar.pack(fill="x", pady=8)
            p_bar["value"] = min(pct, 100)

            btm_row = tk.Frame(card, bg=self.COLOR_CARD)
            btm_row.pack(fill="x")

            lbl_progress = tk.Label(btm_row, text=f"Accumulated: ₹{saved:,.0f} / ₹{target:,.0f} ({pct}% complete)",
                                    font=self.FONT_SMALL, fg=self.COLOR_SUCCESS if pct >= 100 else self.ACCENT_CYAN, bg=self.COLOR_CARD)
            lbl_progress.pack(side="left")

            btn_del = tk.Button(btm_row, text="🗑️ Remove", font=(self.FONT_FAMILY, 8), fg="#F87171", bg="#450A0A", relief="flat",
                                command=lambda g_id=gid: self.action_delete_goal(g_id))
            btn_del.pack(side="right", padx=(6, 0))

            btn_add_money = tk.Button(btm_row, text="➕ Allocate Capital", font=(self.FONT_FAMILY, 8, "bold"), fg="#FFFFFF", bg="#065F46", relief="flat",
                                      command=lambda g_id=gid, g_name=name: self.action_deposit_to_goal(g_id, g_name))
            btn_add_money.pack(side="right")

    def refresh_investments_table(self):
        for item in self.tree_invest.get_children():
            self.tree_invest.delete(item)
        records = self.db.get_investments()
        cost_sum = sum(r[3] for r in records)
        market_sum = sum(r[4] for r in records)
        self.lbl_inv_counter.config(text=f"Total Cost: ₹{cost_sum:,.2f} | Current Valuation: ₹{market_sum:,.2f}")
        for r in records:
            ret_str = f"{r[5]:+.2f}%"
            formatted_r = (r[0], r[1], r[2], f"₹{r[3]:,.2f}", f"₹{r[4]:,.2f}", ret_str)
            self.tree_invest.insert("", "end", values=formatted_r)

    def refresh_bills_table(self):
        for item in self.tree_bills.get_children():
            self.tree_bills.delete(item)
        records = self.db.get_bills()
        for r in records:
            status_display = "✅ Settled" if r[4] == "Paid" else "⏳ Pending"
            formatted_r = (r[0], r[1], r[2], f"₹{r[3]:,.2f}", status_display)
            self.tree_bills.insert("", "end", values=formatted_r)

    def seed_demo_data(self):
        if messagebox.askyesno("Seed Mock Data", "This will generate full-scale mock records for viva presentation.\nProceed?"):
            self.db.seed_sample_data()
            self.refresh_all_views()
            messagebox.showinfo("Success", "Mock data successfully integrated across all tables!")

    def export_audit_report(self):
        """Generates a formal, printable audit text report"""
        total_income, total_expense, savings, total_invest, count_inc, count_exp, count_inv, cost_inv = self.db.get_totals()
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = []
        report.append("================================================================================")
        report.append("          SMART PERSONAL EXPENSE TRACKER • EXECUTIVE AUDIT REPORT               ")
        report.append("================================================================================")
        report.append(f"Generated On  : {now_str}")
        report.append(f"Audit Horizon : Financial Period to Date")
        report.append("--------------------------------------------------------------------------------")
        report.append("1. EXECUTIVE FINANCIAL SUMMARY")
        report.append(f"   • Total Capital Inflow   : ₹{total_income:,.2f} ({count_inc} entries)")
        report.append(f"   • Total Capital Outflow  : ₹{total_expense:,.2f} ({count_exp} entries)")
        report.append(f"   • Net Reserve Surplus    : ₹{savings:,.2f}")
        savings_ratio = (savings / total_income * 100) if total_income > 0 else 0
        report.append(f"   • Net Savings Ratio      : {savings_ratio:.2f}%")
        report.append(f"   • Investment Valuation   : ₹{total_invest:,.2f} (Principal Cost: ₹{cost_inv:,.2f})")
        report.append("--------------------------------------------------------------------------------")
        report.append("2. OUTFLOW BREAKDOWN BY CATEGORY")
        categories = self.db.get_category_expenses()
        for cat, amt, cnt in categories:
            pct = (amt / total_expense * 100) if total_expense > 0 else 0
            report.append(f"   • {cat:<24}: ₹{amt:>10,.2f} ({pct:>5.1f}%) | {cnt} transactions")
        report.append("--------------------------------------------------------------------------------")
        report.append("3. BUDGET THRESHOLD STATUS (80% MONITOR)")
        budgets = self.db.get_budgets()
        for b in budgets:
            pct = (b[4] / b[3] * 100) if b[3] > 0 else 0
            flag = "EXCEEDED" if b[4] >= b[3] else ("80% WARNING" if pct >= 80 else "NORMAL")
            report.append(f"   • {b[2]:<24}: Limit ₹{b[3]:>9,.2f} | Spent ₹{b[4]:>9,.2f} ({pct:>5.1f}%) [{flag}]")
        report.append("--------------------------------------------------------------------------------")
        report.append("4. STRATEGIC SAVINGS GOALS")
        goals = self.db.get_goals()
        for g in goals:
            report.append(f"   • {g[1]:<24}: Saved ₹{g[3]:>9,.2f} / ₹{g[2]:>9,.2f} ({g[5]}%) Due: {g[4]}")
        report.append("================================================================================")
        report.append("                         END OF AUDIT REPORT                                    ")
        report.append("================================================================================")

        report_content = "\n".join(report)

        # Allow user to save as a text file
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text File", "*.txt"), ("All Files", "*.*")],
            initialfile=f"Financial_Audit_Report_{datetime.date.today().strftime('%Y_%m_%d')}.txt"
        )
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(report_content)
                messagebox.showinfo("Export Successful", f"Audit report successfully exported to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Export Failed", f"Could not write file: {e}")


# ------------------------------------------------------------------------------
# 3. ENTRY POINT
# ------------------------------------------------------------------------------
def main():
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
