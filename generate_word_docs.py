"""
Script to generate professional Microsoft Word (.docx) documents for
CBSE Class 12 IP Project: Smart Personal Expense Tracker
Generates:
  1. Smart_Expense_Tracker_Source_Code.docx
  2. Smart_Expense_Tracker_Database_Design.docx
"""

import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

BASE_DIR = r"C:\Users\Lokesh\.gemini\antigravity\scratch\smart_expense_tracker"
MAIN_PY_PATH = os.path.join(BASE_DIR, "main.py")
SQL_PATH = os.path.join(BASE_DIR, "sample_data.sql")

DOCX_CODE_PATH = os.path.join(BASE_DIR, "Smart_Expense_Tracker_Source_Code.docx")
DOCX_DB_PATH = os.path.join(BASE_DIR, "Smart_Expense_Tracker_Database_Design.docx")

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def add_styled_heading(doc, text, level):
    h = doc.add_heading(text, level=level)
    run = h.runs[0]
    run.font.name = "Segoe UI"
    if level == 1:
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = RGBColor(15, 23, 42)
    elif level == 2:
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = RGBColor(37, 99, 235)
    return h

def generate_code_docx():
    print("Generating Source Code Word Document...")
    doc = Document()

    # Page Margins
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # Document Header / Cover Banner
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("SMART PERSONAL EXPENSE TRACKER")
    r_title.font.name = "Segoe UI"
    r_title.font.size = Pt(22)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(15, 23, 42)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("CBSE Class 12 Informatics Practices / Computer Science Project\nComplete Python Source Code Listing (main.py)")
    r_sub.font.name = "Segoe UI"
    r_sub.font.size = Pt(12)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_paragraph()

    # Meta Info Table
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Programming Language", "Python 3.x (with Standard Library sqlite3, tkinter, ttk)"),
        ("GUI Architecture", "Tkinter ttk Notebook (Obsidian Dark Executive Theme)"),
        ("Analytics Engine", "Dual Matplotlib FigureCanvasTkAgg & Native Vector Canvas Engine"),
        ("Key Innovative Features", "80% Budget Alerts, AI Spending Insights, Progress Bars, Audit Export")
    ]
    for row_idx, (k, v) in enumerate(meta_data):
        row = meta_table.rows[row_idx]
        cell_k, cell_v = row.cells[0], row.cells[1]
        cell_k.text = k
        cell_v.text = v
        set_cell_background(cell_k, "F1F5F9")
        set_cell_background(cell_v, "FFFFFF")
        set_cell_margins(cell_k)
        set_cell_margins(cell_v)
        cell_k.paragraphs[0].runs[0].font.bold = True
        cell_k.paragraphs[0].runs[0].font.name = "Segoe UI"
        cell_k.paragraphs[0].runs[0].font.size = Pt(9.5)
        cell_v.paragraphs[0].runs[0].font.name = "Segoe UI"
        cell_v.paragraphs[0].runs[0].font.size = Pt(9.5)

    doc.add_paragraph()
    doc.add_page_break()

    # Code Content
    add_styled_heading(doc, "Complete Source Code Listing", level=1)
    p_note = doc.add_paragraph("The complete, runnable implementation of the application is provided below:")
    p_note.runs[0].font.name = "Segoe UI"
    p_note.runs[0].font.size = Pt(10)
    p_note.runs[0].font.italic = True

    with open(MAIN_PY_PATH, "r", encoding="utf-8") as f:
        code_lines = f.readlines()

    # Add code inside formatted table cell for border and background effect
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.rows[0].cells[0]
    set_cell_background(cell, "0F172A") # Dark background
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)

    p_code = cell.paragraphs[0]
    p_code.paragraph_format.space_before = Pt(0)
    p_code.paragraph_format.space_after = Pt(2)
    p_code.paragraph_format.line_spacing = 1.05

    for line in code_lines:
        run = p_code.add_run(line)
        run.font.name = "Consolas"
        run.font.size = Pt(8.5)
        # Simple syntax coloring logic
        trimmed = line.strip()
        if trimmed.startswith("#") or trimmed.startswith('"""') or trimmed.startswith("'''"):
            run.font.color.rgb = RGBColor(148, 163, 184) # Light slate gray for comments
        elif trimmed.startswith("class ") or trimmed.startswith("def ") or trimmed.startswith("import ") or trimmed.startswith("from "):
            run.font.color.rgb = RGBColor(56, 189, 248) # Cyan/Blue for definitions
        elif "CREATE TABLE" in line or "SELECT " in line or "INSERT INTO" in line or "UPDATE " in line:
            run.font.color.rgb = RGBColor(52, 211, 153) # Mint green for SQL
        else:
            run.font.color.rgb = RGBColor(241, 245, 249) # Crisp white for code

    doc.save(DOCX_CODE_PATH)
    print(f"Saved: {DOCX_CODE_PATH}")

def generate_db_docx():
    print("Generating Database Design Word Document...")
    doc = Document()

    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("SMART PERSONAL EXPENSE TRACKER")
    r_title.font.name = "Segoe UI"
    r_title.font.size = Pt(22)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(15, 23, 42)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("CBSE Class 12 Informatics Practices / Computer Science Project\nDatabase Architecture & SQL Scripts (sample_data.sql)")
    r_sub.font.name = "Segoe UI"
    r_sub.font.size = Pt(12)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_paragraph()

    # Section 1: Database Tables Structure
    add_styled_heading(doc, "1. Database Schema Specifications", level=1)
    
    tables_spec = [
        ("Table 1: INCOME (Revenue / Inflow Tracking)", [
            ("Column Name", "Data Type", "Constraints", "Description"),
            ("Income_ID", "INTEGER", "PRIMARY KEY AUTOINCREMENT", "Unique identifier for each income transaction"),
            ("Date", "DATE", "NOT NULL", "Date of receipt (YYYY-MM-DD)"),
            ("Source", "TEXT", "NOT NULL", "Income category: Salary, Freelancing, Dividends, etc."),
            ("Amount", "REAL", "NOT NULL", "Numerical amount in INR (₹)"),
            ("Payment_Mode", "TEXT", "-", "Bank Transfer, UPI, Cash, Cheque"),
            ("Remarks", "TEXT", "-", "Optional notes or memorandum")
        ]),
        ("Table 2: EXPENDITURE (Outflow / Expense Tracking)", [
            ("Column Name", "Data Type", "Constraints", "Description"),
            ("Expense_ID", "INTEGER", "PRIMARY KEY AUTOINCREMENT", "Unique identifier for each expense transaction"),
            ("Date", "DATE", "NOT NULL", "Date of expenditure (YYYY-MM-DD)"),
            ("Category", "TEXT", "NOT NULL", "Food & Groceries, Travel & Fuel, Bills, etc."),
            ("Item", "TEXT", "NOT NULL", "Description of item/service purchased"),
            ("Amount", "REAL", "NOT NULL", "Expenditure amount in INR (₹)"),
            ("Payment_Mode", "TEXT", "-", "UPI, Credit Card, Debit Card, Cash"),
            ("Shop_Name", "TEXT", "-", "Merchant name (e.g. DMart, Amazon, Zomato)")
        ]),
        ("Table 3: BUDGET (Monthly Category Ceilings & Alerts)", [
            ("Column Name", "Data Type", "Constraints", "Description"),
            ("Budget_ID", "INTEGER", "PRIMARY KEY AUTOINCREMENT", "Unique budget record identifier"),
            ("Month", "TEXT", "NOT NULL", "Month and year (e.g. November 2026)"),
            ("Category", "TEXT", "NOT NULL UNIQUE", "Target category being budgeted"),
            ("Budgeted_Amount", "REAL", "NOT NULL", "Assigned spending ceiling"),
            ("Spent_Amount", "REAL", "DEFAULT 0", "Auto-calculated sum of actual expenditures")
        ]),
        ("Table 4: GOALS (Financial Target Monitoring)", [
            ("Column Name", "Data Type", "Constraints", "Description"),
            ("Goal_ID", "INTEGER", "PRIMARY KEY AUTOINCREMENT", "Unique goal identifier"),
            ("Goal_Name", "TEXT", "NOT NULL", "Target item (e.g. Laptop, Trip, Fund)"),
            ("Target_Amount", "REAL", "NOT NULL", "Total capital required"),
            ("Saved_Amount", "REAL", "DEFAULT 0", "Current capital accumulated"),
            ("Deadline", "DATE", "-", "Target completion date")
        ]),
        ("Table 5: INVESTMENT (Wealth Portfolio & ROI)", [
            ("Column Name", "Data Type", "Constraints", "Description"),
            ("Invest_ID", "INTEGER", "PRIMARY KEY AUTOINCREMENT", "Unique asset identifier"),
            ("Type", "TEXT", "NOT NULL", "SIP, Mutual Fund, FD, Sovereign Gold"),
            ("Date", "DATE", "-", "Acquisition date"),
            ("Amount", "REAL", "NOT NULL", "Principal invested capital"),
            ("Current_Value", "REAL", "NOT NULL", "Current market valuation"),
            ("Returns_Percent", "REAL", "-", "Auto-computed ROI percentage (%)")
        ]),
        ("Table 6: BILL_REMINDER (Recurring Due Obligations)", [
            ("Column Name", "Data Type", "Constraints", "Description"),
            ("Bill_ID", "INTEGER", "PRIMARY KEY AUTOINCREMENT", "Unique bill identifier"),
            ("Bill_Name", "TEXT", "NOT NULL", "Utility/Bill name (e.g. Wi-Fi, Rent)"),
            ("Due_Date", "DATE", "NOT NULL", "Maturity due date"),
            ("Amount", "REAL", "NOT NULL", "Billed amount in INR"),
            ("Status", "TEXT", "DEFAULT 'Pending'", "Pending or Paid")
        ])
    ]

    for title, rows in tables_spec:
        add_styled_heading(doc, title, level=2)
        table = doc.add_table(rows=len(rows), cols=4)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        for r_idx, row_data in enumerate(rows):
            for c_idx, val in enumerate(row_data):
                cell = table.rows[r_idx].cells[c_idx]
                cell.text = val
                set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                run = p.runs[0]
                run.font.name = "Segoe UI"
                if r_idx == 0:
                    set_cell_background(cell, "1E293B")
                    run.font.bold = True
                    run.font.color.rgb = RGBColor(255, 255, 255)
                    run.font.size = Pt(9.5)
                else:
                    bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
                    set_cell_background(cell, bg)
                    run.font.size = Pt(9)
                    if c_idx == 0:
                        run.font.bold = True
        doc.add_paragraph()

    doc.add_page_break()

    # Section 2: Complete SQL Scripts (DDL + DML)
    add_styled_heading(doc, "2. SQL Script File (sample_data.sql)", level=1)
    p_note = doc.add_paragraph("Executable SQL script for table creation, sample records insertion, and analytics queries:")
    p_note.runs[0].font.name = "Segoe UI"
    p_note.runs[0].font.size = Pt(10)
    p_note.runs[0].font.italic = True

    with open(SQL_PATH, "r", encoding="utf-8") as f:
        sql_lines = f.readlines()

    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.rows[0].cells[0]
    set_cell_background(cell, "0F172A")
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)

    p_sql = cell.paragraphs[0]
    p_sql.paragraph_format.space_before = Pt(0)
    p_sql.paragraph_format.space_after = Pt(2)
    p_sql.paragraph_format.line_spacing = 1.05

    for line in sql_lines:
        run = p_sql.add_run(line)
        run.font.name = "Consolas"
        run.font.size = Pt(9)
        trimmed = line.strip()
        if trimmed.startswith("--"):
            run.font.color.rgb = RGBColor(148, 163, 184)
        elif trimmed.startswith("CREATE TABLE") or trimmed.startswith("INSERT INTO") or trimmed.startswith("SELECT "):
            run.font.color.rgb = RGBColor(56, 189, 248)
        else:
            run.font.color.rgb = RGBColor(241, 245, 249)

    doc.save(DOCX_DB_PATH)
    print(f"Saved: {DOCX_DB_PATH}")

if __name__ == "__main__":
    generate_code_docx()
    generate_db_docx()
    print("All Word documents generated successfully!")
