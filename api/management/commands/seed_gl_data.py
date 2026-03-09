import json
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from api.models import (
    Company, User, BudgetPool, GLAccount, GLTransaction, GLTransactionLine, 
    Claim, ReceiptFile, Approval, PolicyDoc, ReportTemplate, GeneratedReport,
    ChatSession, ChatMessage
)

class Command(BaseCommand):
    help = 'Seeds the database with comprehensive Finsight MVP dummy data including Agents, GL, and Policies.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Clearing existing data..."))
        
        # 1. Clear database idempotently (Order matters for Foreign Keys!)
        GeneratedReport.objects.all().delete()
        ReportTemplate.objects.all().delete()
        ChatMessage.objects.all().delete()
        ChatSession.objects.all().delete()
        PolicyDoc.objects.all().delete()
        Approval.objects.all().delete()
        ReceiptFile.objects.all().delete()
        GLTransactionLine.objects.all().delete()
        GLTransaction.objects.all().delete()
        GLAccount.objects.all().delete()
        Claim.objects.all().delete()
        BudgetPool.objects.all().delete()
        User.objects.all().delete()
        Company.objects.all().delete()

        # 2. Re-create Company
        company = Company.objects.create(name="Acme Corp")
        
        # 3. Create Users
        admin_user = User.objects.create(
            username="finance_admin", 
            email="admin@acme.com", 
            role="admin", 
            company=company
        )
        admin_user.set_password('admin123')
        admin_user.save()

        employee_user = User.objects.create(
            username="john_doe", 
            email="john@acme.com", 
            role="employee", 
            company=company
        )
        employee_user.set_password('emp123')
        employee_user.save()

        # 4. Create PolicyDoc (For RAG)
        PolicyDoc.objects.create(
            company=company,
            title="Q3 Travel and Expense Policy",
            version="1.2",
            content_text="Meals and Entertainment are capped at $500 HKD per day. Software licenses require pre-approval from the IT department. Travel expenses must be booked via Acme-approved vendors only. Receipts are mandatory for claims over $100 HKD."
        )

        PolicyDoc.objects.create(
            company=company,
            title="IT Hardware Procurement Guidelines",
            version="2.0",
            content_text="Any laptop purchases over $10,000 HKD require CXO approval. Cables and peripherals under $500 HKD can be expensed directly via the IT & Software ledger."
        )

        # 5. Create Budget Pool
        pool = BudgetPool.objects.create(
            company=company, 
            name="Q3 Marketing & General Budget",
            start_date=date(2026, 7, 1),
            end_date=date(2026, 9, 30),
            total_budget_hkd=Decimal('100000.00'),
            remaining_hkd=Decimal('100000.00')
        )

        # 6. Create Chart of Accounts
        accounts_data = [
            ("1000", "Cash", "asset"),
            ("2000", "Accounts Payable", "liability"),
            ("5010", "Travel Expense", "expense"),
            ("5020", "Meals & Entertainment", "expense"),
            ("5030", "Office Supplies", "expense"),
            ("5040", "IT & Software", "expense"),
            ("4000", "Services Revenue", "revenue"),
        ]

        accounts = {}
        for code, name, acc_type in accounts_data:
            accounts[code] = GLAccount.objects.create(
                company=company,
                code=code,
                name=name, 
                account_type=acc_type
            )

        # 7. Create Claims, Receipts, Approvals & GL Transactions
        dummy_claims = [
            {"merchant": "Cathay Pacific", "amount": "4500.00", "cat": "Travel Expense", "code": "5010", "date": date(2026, 8, 10), "status": "approved"},
            {"merchant": "Starbucks", "amount": "45.00", "cat": "Meals & Entertainment", "code": "5020", "date": date(2026, 8, 12), "status": "approved"},
            {"merchant": "Adobe Systems", "amount": "250.00", "cat": "IT & Software", "code": "5040", "date": date(2026, 8, 15), "status": "pending"},
            {"merchant": "IKEA", "amount": "12000.00", "cat": "Office Supplies", "code": "5030", "date": date(2026, 8, 20), "status": "rejected"},
            {"merchant": "Marriott Hotel", "amount": "3200.00", "cat": "Travel Expense", "code": "5010", "date": date(2026, 8, 25), "status": "approved"},
        ]

        for c_data in dummy_claims:
            claim = Claim.objects.create(
                user=employee_user,
                budget_pool=pool,
                status=c_data["status"],
                amount_hkd=Decimal(c_data["amount"]),
                merchant=c_data["merchant"],
                date=c_data["date"],
                category=c_data["cat"],
                note=f"Business trip/expense for {c_data['merchant']}."
            )

            # Assign Dummy OCR Receipt File
            ocr_mock = {
                "entities": {"Total": c_data["amount"], "Merchant": c_data["merchant"], "Tax": "0.00"},
                "confidence_score": 0.95
            }
            ReceiptFile.objects.create(
                claim=claim,
                ocr_json=ocr_mock,
                ocr_confidence=0.95
            )

            # Assign Approvals
            if c_data["status"] == "approved":
                Approval.objects.create(
                    claim=claim,
                    approver=admin_user,
                    decision="Approved",
                    comment="Looks good, falls within policy limits."
                )
                pool.remaining_hkd -= claim.amount_hkd
                
                # Create GL Transaction for Approved Claims
                txn = GLTransaction.objects.create(
                    company=company,
                    date=claim.date,
                    description=f"Expense Claim #{claim.id} - {claim.merchant}",
                    claim=claim
                )
                GLTransactionLine.objects.create(
                    transaction=txn,
                    account=accounts[c_data["code"]],
                    debit=claim.amount_hkd,
                    credit=Decimal('0.00')
                )
                GLTransactionLine.objects.create(
                    transaction=txn,
                    account=accounts["2000"],
                    debit=Decimal('0.00'),
                    credit=claim.amount_hkd
                )

            elif c_data["status"] == "rejected":
                Approval.objects.create(
                    claim=claim,
                    approver=admin_user,
                    decision="Rejected",
                    comment=f"Expense of ${c_data['amount']} exceeds normal limits. Please provide extra justification."
                )

        pool.save()

        # Add generic revenue transaction
        rev_txn = GLTransaction.objects.create(
            company=company,
            date=date(2026, 8, 30),
            description="August Consulting Revenue"
        )
        GLTransactionLine.objects.create(
            transaction=rev_txn, account=accounts["1000"], debit=Decimal('25000.00'), credit=Decimal('0.00')
        )
        GLTransactionLine.objects.create(
            transaction=rev_txn, account=accounts["4000"], debit=Decimal('0.00'), credit=Decimal('25000.00')
        )

        # 8. Create ReportTemplate and Dummy GeneratedReport
        template = ReportTemplate.objects.create(
            company=company,
            name="Executive Expense Summary",
            format="pdf",
            config_json={"theme": "dark", "includeChart": True},
            created_by=admin_user
        )
        
        GeneratedReport.objects.create(
            template=template,
            user=admin_user,
            file_url="https://storage.googleapis.com/finsight-dummy-bucket/report.pdf"
        )

        # 9. Create standard Chat Session and Messages
        session = ChatSession.objects.create(user=employee_user, context="employee")
        ChatMessage.objects.create(
            session=session,
            role="user",
            content="Can I expense a $12000 desk from IKEA?"
        )
        ChatMessage.objects.create(
            session=session,
            role="model",
            content="No, according to the IT Hardware Procurement Guidelines, large purchases require specific CXO pre-approvals and don't generally fall under standard employee office supplies limits."
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded full schema! All 14 models populated for Acme Corp.'))