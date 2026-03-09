from django.core.management.base import BaseCommand
from api.models import Company, User, GLAccount, GLTransaction, GLTransactionLine, Claim, BudgetPool
from datetime import date, timedelta
from decimal import Decimal

class Command(BaseCommand):
    help = 'Seeds the database with dummy General Ledger (GL) data and Claims for report generation testing'

    def handle(self, *args, **kwargs):
        # 1. Create a Company
        company, _ = Company.objects.get_or_create(name="Acme Corp")
        
        # 2. Create a User
        user, _ = User.objects.get_or_create(username="finance_admin", defaults={
            "email": "admin@acme.com",
            "role": "admin",
            "company": company
        })
        user.set_password('admin123')
        user.save()

        employee, _ = User.objects.get_or_create(username="john_doe", defaults={
            "email": "john@acme.com",
            "role": "employee",
            "company": company
        })
        employee.set_password('emp123')
        employee.save()

        # 3. Create Budget Pool
        pool, _ = BudgetPool.objects.get_or_create(
            company=company, 
            name="Q3 Marketing Budget",
            defaults={
                "start_date": date(2026, 7, 1),
                "end_date": date(2026, 9, 30),
                "total_budget_hkd": Decimal('50000.00'),
                "remaining_hkd": Decimal('50000.00')
            }
        )

        # 4. Create Standard GL Accounts (Chart of Accounts)
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
            acc, _ = GLAccount.objects.get_or_create(
                company=company,
                code=code,
                defaults={"name": name, "account_type": acc_type}
            )
            accounts[code] = acc

        # Clear existing transactions and claims (optional, for idempotency)
        GLTransaction.objects.filter(company=company).delete()
        Claim.objects.filter(user=employee).delete()

        # 5. Create some dummy claims mapped to GL Transactions
        dummy_claims = [
            {"merchant": "Cathay Pacific", "amount": "4500.00", "cat": "Travel Expense", "code": "5010", "date": date(2026, 8, 10)},
            {"merchant": "Starbucks", "amount": "45.00", "cat": "Meals & Entertainment", "code": "5020", "date": date(2026, 8, 12)},
            {"merchant": "Adobe Systems", "amount": "250.00", "cat": "IT & Software", "code": "5040", "date": date(2026, 8, 15)},
            {"merchant": "IKEA", "amount": "1200.00", "cat": "Office Supplies", "code": "5030", "date": date(2026, 8, 20)},
            {"merchant": "Marriott Hotel", "amount": "3200.00", "cat": "Travel Expense", "code": "5010", "date": date(2026, 8, 25)},
        ]

        for c_data in dummy_claims:
            # Create the Claim
            claim = Claim.objects.create(
                user=employee,
                budget_pool=pool,
                status='approved',
                amount_hkd=Decimal(c_data["amount"]),
                merchant=c_data["merchant"],
                date=c_data["date"],
                category=c_data["cat"]
            )

            # Deduct from pool (simplified for dummy data)
            pool.remaining_hkd -= claim.amount_hkd
            pool.save()

            # Create the corresponding GL Transaction
            txn = GLTransaction.objects.create(
                company=company,
                date=claim.date,
                description=f"Expense Claim #{claim.id} - {claim.merchant}",
                claim=claim
            )

            # Debit the specific expense account
            GLTransactionLine.objects.create(
                transaction=txn,
                account=accounts[c_data["code"]],
                debit=claim.amount_hkd,
                credit=Decimal('0.00')
            )

            # Credit Accounts Payable (liability to reimburse employee)
            GLTransactionLine.objects.create(
                transaction=txn,
                account=accounts["2000"],
                debit=Decimal('0.00'),
                credit=claim.amount_hkd
            )

        # Add a dummy revenue transaction just to make an Income Statement look complete
        rev_txn = GLTransaction.objects.create(
            company=company,
            date=date(2026, 8, 30),
            description="August Consulting Revenue"
        )
        # Debit Cash
        GLTransactionLine.objects.create(
            transaction=rev_txn,
            account=accounts["1000"],
            debit=Decimal('25000.00'),
            credit=Decimal('0.00')
        )
        # Credit Revenue
        GLTransactionLine.objects.create(
            transaction=rev_txn,
            account=accounts["4000"],
            debit=Decimal('0.00'),
            credit=Decimal('25000.00')
        )

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {len(dummy_claims)} claims and GL transactions for Acme Corp!'))
