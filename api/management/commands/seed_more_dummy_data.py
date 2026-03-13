import sys
from datetime import date, timedelta
from decimal import Decimal
import random
from django.core.management.base import BaseCommand
from api.models import (
    Company, User, BudgetPool, Claim, ReceiptFile, Approval, GLAccount, GLTransaction, GLTransactionLine
)
from django.utils import timezone

class Command(BaseCommand):
    help = 'Seeds MORE comprehensive dummy data for claims and budget pools without wiping previous data.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Generating more dummy data...")

        # Ensure we have a company and users
        company = Company.objects.first()
        if not company:
            company = Company.objects.create(name="Acme Corp")
            self.stdout.write("Created new Company")

        admin_user = User.objects.filter(role="admin").first()
        if not admin_user:
            admin_user = User.objects.create(username="finance_admin2", email="admin2@acme.com", role="admin", company=company)
            admin_user.set_password('admin123')
            admin_user.save()

        employee_user = User.objects.filter(role="employee").first()
        employee_user2, _ = User.objects.get_or_create(username="jane_smith", email="jane@acme.com", role="employee", company=company)
        employee_user2.set_password('emp123')
        employee_user2.save()

        # Generate New Budget Pools with Groups
        groups = [
            {"group": "Marketing", "name": "Q4 Event Budget", "amount": 250000.00},
            {"group": "Engineering", "name": "Cloud Infrastructure", "amount": 500000.00},
            {"group": "Sales", "name": "Client Entertainment", "amount": 80000.00},
            {"group": "Operations", "name": "Office Supplies", "amount": 20000.00},
        ]

        pools = []
        for g in groups:
            pool, created = BudgetPool.objects.get_or_create(
                company=company,
                name=g["name"],
                group=g["group"],
                defaults={
                    "start_date": date(2026, 1, 1),
                    "end_date": date(2026, 12, 31),
                    "total_budget_hkd": Decimal(str(g["amount"])),
                    "remaining_hkd": Decimal(str(g["amount"]))
                }
            )
            pools.append(pool)
            
        base_date = timezone.now().date()
        merchants = ["Uber", "AWS", "Google Cloud", "AirBnb", "Deliveroo", "Cathay Pacific", "Apple Store", "Slack", "Microsoft", "KFC", "Pacific Coffee"]
        categories = ["Travel", "Meals", "Hotel", "IT & Software", "Office Supplies"]

        # Add Pending claims
        for i in range(7):
            user = random.choice([employee_user, employee_user2])
            pool = random.choice(pools)
            amount = round(random.uniform(50.0, 4500.0), 2)
            merchant = random.choice(merchants)
            
            c = Claim.objects.create(
                user=user,
                budget_pool=pool,
                status='pending',
                amount_hkd=Decimal(str(amount)),
                merchant=merchant,
                date=base_date - timedelta(days=random.randint(1, 15)),
                category=random.choice(categories),
                note=f"Expense for {merchant} (Pending review)"
            )
            ReceiptFile.objects.create(
                claim=c,
                ocr_json={"entities": {"Total": str(amount), "Merchant": merchant}},
                ocr_confidence=round(random.uniform(0.85, 0.99), 2)
            )

        # Add Approved claims & Decrement Pools
        accounts = list(GLAccount.objects.filter(company=company))
        if not accounts: 
            accounts.append(GLAccount.objects.create(company=company, code="9999", name="General Expense", account_type="expense"))

        for i in range(15):
            user = random.choice([employee_user, employee_user2])
            pool = random.choice(pools)
            amount = round(random.uniform(100.0, 9000.0), 2)
            merchant = random.choice(merchants)
            claim_date = base_date - timedelta(days=random.randint(5, 60))
            
            c = Claim.objects.create(
                user=user,
                budget_pool=pool,
                status='approved',
                amount_hkd=Decimal(str(amount)),
                merchant=merchant,
                date=claim_date,
                category=random.choice(categories),
                note=f"Approved expense for {merchant}"
            )
            
            # Reduce pool budget
            pool.remaining_hkd -= Decimal(str(amount))
            pool.save()

            Approval.objects.create(
                claim=c,
                approver=admin_user,
                decision='approve',
                comment='Approved as per policy.'
            )
            
            # Add Transaction
            txn = GLTransaction.objects.create(
                company=company,
                date=claim_date,
                description=f"Expense #{c.id} - {c.merchant}",
                claim=c
            )
            GLTransactionLine.objects.create(
                transaction=txn,
                account=random.choice(accounts),
                debit=Decimal(str(amount)),
                credit=0
            )

        # Add Rejected claims
        for i in range(5):
            user = random.choice([employee_user, employee_user2])
            pool = random.choice(pools)
            amount = round(random.uniform(3000.0, 15000.0), 2)
            merchant = random.choice(merchants)
            
            c = Claim.objects.create(
                user=user,
                budget_pool=pool,
                status='rejected',
                amount_hkd=Decimal(str(amount)),
                merchant=merchant,
                date=base_date - timedelta(days=random.randint(2, 30)),
                category=random.choice(categories),
                note=f"Requested {merchant} expense."
            )
            Approval.objects.create(
                claim=c,
                approver=admin_user,
                decision='reject',
                comment=random.choice([
                    'Exceeds daily allowable limit.',
                    'Missing detailed receipt.',
                    'This vendor is not on the approved list.',
                    'Please bill this to a different department.'
                ])
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded Database with additional dummy claims, pools, and approvals!"))
