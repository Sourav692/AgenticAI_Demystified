TABLE_CONFIG = { 
    "transaction_data.csv": {
        "table": "transaction_data",
        "text_fields": ["Description", "DocumentType", "Vendor"]
    },
    "general_ledger_entries.csv": {
        "table": "general_ledger_entries",
        "text_fields": ["Description", "AccountName"]
    },
    "income_statement.csv": {
        "table": "income_statement",
        "text_fields": ["AccountName", "Type"]
    },
    "balance_sheet.csv": {
        "table": "balance_sheet",
        "text_fields": ["AccountName", "Type"]
    },
    "cash_flow_statement.csv": {
        "table": "cash_flow_statement",
        "text_fields": ["Category", "Subcategory"]
    },
    "bank_statements.csv": {
        "table": "bank_statements",
        "text_fields": ["Description"]
    },
    "credit_card_statements.csv": {
        "table": "credit_card_statements",
        "text_fields": ["Description"]
    },
    "reconciliation_records.csv": {
        "table": "reconciliation_records",
        "text_fields": ["Description", "AccountType"]
    },
    "fixed_asset_register.csv": {
        "table": "fixed_asset_register",
        "text_fields": ["AssetName", "Category"]
    },
    "accounts_payable_receivable.csv": {
        "table": "accounts_payable_receivable",
        "text_fields": ["Vendor_Customer", "Type"]
    },
    "inventory_records.csv": {
        "table": "inventory_records",
        "text_fields": ["ItemName", "Category", "Supplier"]
    },
    "tax_returns.csv": {
        "table": "tax_returns",
        "text_fields": ["TaxType", "Status"]
    },
    "internal_controls.csv": {
        "table": "internal_controls",
        "text_fields": ["ControlName", "Description", "ResponsibleDept"]
    },
    "employee_records.csv": {
        "table": "employee_records",
        "text_fields": ["Name", "Position", "Department"]
    },
    "invoices.csv": {
        "table": "invoices",
        "text_fields": ["Description", "Vendor"]
    },
    "receipts.csv": {
        "table": "receipts",
        "text_fields": ["Payee", "Description"]
    },
    "purchase_orders.csv": {
        "table": "purchase_orders",
        "text_fields": ["Description", "Vendor"]
    },
    "credit_notes.csv": {
        "table": "credit_notes",
        "text_fields": ["Vendor", "Reason"]
    },
    "debit_notes.csv": {
        "table": "debit_notes",
        "text_fields": ["Vendor", "Reason"]
    },
    "bank_confirmations.csv": {
        "table": "bank_confirmations",
        "text_fields": ["BankName"]
    },
    "credit_card_confirmations.csv": {
        "table": "credit_card_confirmations",
        "text_fields": ["BankName"]
    },
    "journal_entries.csv": {
        "table": "journal_entries",
        "text_fields": ["Description", "CreatedBy"]
    },
    "bank_reconciliations.csv": {
        "table": "bank_reconciliations",
        "text_fields": ["BankAccountID"]
    },
    "account_reconciliations.csv": {
        "table": "account_reconciliations",
        "text_fields": ["AccountType"]
    },
    "vendor_confirmations.csv": {
        "table": "vendor_confirmations",
        "text_fields": ["Vendor"]
    },
    "customer_confirmations.csv": {
        "table": "customer_confirmations",
        "text_fields": ["Customer"]
    },
    "payroll_reports.csv": {
        "table": "payroll_reports",
        "text_fields": ["EmployeeID"]
    },
    "employee_files.csv": {
        "table": "employee_files",
        "text_fields": ["Name", "Position"]
    },
    "asset_purchase_invoices.csv": {
        "table": "asset_purchase_invoices",
        "text_fields": ["Vendor", "DepreciationMethod"]
    },
    "depreciation_schedules.csv": {
        "table": "depreciation_schedules",
        "text_fields": ["DepreciationMethod"]
    },
    "inventory_count_sheets.csv": {
        "table": "inventory_count_sheets",
        "text_fields": ["ItemName", "Location"]
    },
    "inventory_valuation.csv": {
        "table": "inventory_valuation",
        "text_fields": ["ItemName", "ValuationMethod"]
    },
    "tax_return_files.csv": {
        "table": "tax_return_files",
        "text_fields": ["TaxType"]
    },
    "internal_control_docs.csv": {
        "table": "internal_control_docs",
        "text_fields": ["ControlName", "ResponsibleDept"]
    },
    "management_reports.csv": {
        "table": "management_reports",
        "text_fields": ["ReportType", "Description"]
    },
    "meeting_minutes.csv": {
        "table": "meeting_minutes",
        "text_fields": ["Agenda", "DecisionsMade"]
    },
    "system_audit_trail.csv": {
        "table": "system_audit_trail",
        "text_fields": ["Action", "Description"]
    },
    "transaction_audit_trail.csv": {
        "table": "transaction_audit_trail",
        "text_fields": ["Action", "Description"]
    }
}
