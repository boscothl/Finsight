from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from api.models import (
    Approval,
    BudgetPool,
    Claim,
    Company,
    GLAccount,
    GLTransaction,
    GLTransactionLine,
    PolicyDoc,
    ReceiptFile,
    User,
)


POLICY_CONTEXT_TEXT = """1
The Financial Regulation of
The Hong Kong University Students' Union Cultural Association
(Amended to 2017-2018 - CM4)
2
Enactment and Amendment History
Amended in June 2009 CM4
Amended in April 2012 CM3
Amended in January 2015 CM10
Amended in October 2015 ECM2
Amended in December 2017 CM4
3
In this Context, unless otherwise requires, the following terms shall have the following
meanings:
"the Association" shall mean the Hong Kong University Students' Union
Cultural Association;
"Cultural Club(s)" shall mean the student sub-organizations affiliated or
partially affiliated to the Union through the Association;
"the Cultural Council" shall mean the Hong Kong University Students' Union
Cultural Association Council;
"Finance Committee" shall mean Finance Committee of the Association;
"the Executive Committee" shall mean the executive committee of the Association;
"the Regulations" shall mean the Financial Regulations of the Association;
"CA Fund" shall mean Cultural Association Fund;
"CI Fund" shall mean Capital Investment Fund;
"the Union" shall mean the Hong Kong University Students' Union;
"the Union Council" shall mean the Hong Kong University Students' Union
Council;
"the Union Finance Committee" shall mean the Finance Committee, The Hong Kong
University Students' Union Council;
"the University" shall mean the University of Hong Kong;
Section I Terminology
4
Article 1 Aim
1. The Financial Regulation governs financial matters of the Association.
2. Any financial matters concerned not stated in the regulations which are not controversial and
not violating the principles in Article 2 of Section II shall be decided by the Finance
Committee.
Article 2 Principles
1. The primary function of the Financial Budget is to better serve the aims of the Association
in financial term.
2. The budget of the Association is distributed among Cultural Clubs and the Executive
Committee based on a 'need-to-give' basis.
3. Pro-rata cut on budget in case of shortage of funds is not recommended, unless the Cultural
Council acts contrary.
Article 1 Function
1. To advise the Cultural Council on all matters of finance;
2. To investigate and take action into the financial matters of the Association;
3. To scrutinize Financial Budgets and Annual Financial Reports of Cultural Clubs and the
Executive Committee;
4. To recommend the budget for CA Fund to the Cultural Council;
5. To advise Cultural Clubs on all matters related to external cultural subsidies;
6. To make regular reports to the Cultural Council;
Section II General
Section III Finance Committee
5
Article 1 Application Procedure of CA Fund
The application procedure of CA Fund shall be as follows:
1. Cultural Clubs shall submit their Annual Financial Report of the previous session, Year Plan
and Financial Budget before the commencement of the first Cultural Council Meeting;
2. The Finance Committee shall scrutinize Annual Financial Report of every Cultural Clubs
and the Executive Committee, and recommend the Cultural Council to receive and adopt the
Reports before the commencement of the first Cultural Council Meeting;
3. The Finance Committee shall scrutinize Financial Budget and Year Plan of every Cultural
Clubs and the Executive Committee, and recommend a budget for CA Fund to the Cultural
Council;
4. The Cultural Council shall receive and adopt the budget for CA Fund and the Financial
Budget of every Cultural Clubs in the same Cultural Council Meeting;
5. The adopted budget for CA Fund shall be submitted to Union Finance Committee for
scrutiny.
Article 2 Criteria of CA Fund
1. The Finance Committee shall evaluate the applications based on the following criteria:
a. maximum subsidy per function shall not exceed its expected net loss;
b. quantity and scale of functions;
c. utilization rate of CA Fund of the previous year;
d. size of the Cultural Club (if applicable);
e. any other factors which the Finance Committee or the Cultural Council deems fit.
2. The Cultural Club which violates the procedure in Article 1 of this section shall not be
eligible for subsidy from CA fund, unless the Cultural Council acts contrary.
Section IV Budget System
6
Article 3 Criteria of Membership Fee Amendment
1. Finance Committee shall evaluate the amendment in membership fee based on the following
criteria:
a. net general income of the previous session;
b. expected net general income of the current session;
c. any other factors which Finance Committee or Cultural Council deems fit.
Article 4 Procedure of Financial Budget Amendment
1. The procedure of any amendment in adopted Financial Budget shall be as follows:
a. Cultural Clubs shall convene a General Meeting to receive and adopt the proposed
amendment in the adopted Financial Budget;
b. Cultural Clubs or the Executive Committee shall submit a written request for the
proposed amendment to the Finance Committee;
c. Finance Committee shall convene a meeting within 14 days after the receipt of the
request and decide whether the application shall be recommended to the Cultural
Council;
d. Cultural Council reserves the right of the final approval on the amendment.
2. The amendment in the adopted Financial Budget shall not affect the adopted CA Fund
budget.
7
Article 1 General
1. The Financial Budget submitted to Finance Committee shall be prepared using the template
provided by the Finance Committee;
2. The items listed in the Article 2 to Article 8 of this Section shall be included in the Financial
Budget;
3. The Finance Budget is to subsidize functions organized in the fiscal year, counting from
January 1 to December 31 of the year only.
Article 2 Size of the Cultural Club
1. The size of a Cultural Club shall depend on the number of members of the Cultural Club at
the commencement of its AGM of the previous session;
Size of a Cultural Club Number of Members
Large 300 or more
Medium 150 to 299
Small Less than 150
2. The Cultural Clubs which apply for CA Fund shall submit a membership list updated at the
commencement of its AGM of the previous session to the Programme Committee upon
request;
3. Number of members and the Cultural Club's size shall be specified in the Financial Budget;
4. Finance Committee shall take Programme Committee's recommendation on size of Cultural
Clubs as reference.
Article 3 General Incomes & General Expenses
1. 'General Incomes' shall mean any income(s) not generated from functions;
2. Items under 'General Incomes' shall include the following:
a. membership fee
b. interest on bank deposit
Section V Financial Budget
8
c. sponsorship
d. expected grant from CA Fund
e. expected grant from subsidy (ies) other than CA Fund
3. 'General Expenses' shall mean any expense(s) not incurred from functions;
4. Items under 'General Expenses' shall include the following:
a. Stationery and Postage;
b. Reference Material;
c. Publicity and Publication;
d. Annual Journal;
e. Maintenance and Replacement;
f. Documentation;
g. Special Items.
Article 4 Functional Incomes & Functional Expenses
1. 'Functional Incomes' shall mean any incomes generated from functions;
2. Items under 'General Incomes' shall include the following:
a. participation fee (or equivalent);
b. sponsorship (specified for function);
c. expected grant from CA Fund (specified for function);
d. expected grant from subsidy(ies) other than CA Fund (specified for function).
3. 'Functional Expenses' shall mean any expense(s) incurred from functions;
4. Items under 'Functional Expenses' shall include the following:
a. Publicity & Publication;
b. Souvenir;
c. Prizes;
9
d. Refreshment;
e. Transportation;
f. Exhibition & Demonstration;
g. Tuition Fee/ Coach Fee/ Conductor Fee;
h. Affiliation Fee/ Registration Fee;
i. Course Materials;
j. Competition Cost;
k. Rental of Venue;
l. Practice Cost;
m. Special Items;
5. 'Functional Incomes' and 'Functional Expenses' shall be specified for each function;
6. Expected date(s) of all functions shall be specified in the Financial Budget.
Article 5 Capital Investment
1. 'Capital Investment' shall mean purchase of new equipment(s);
2. Items under 'Capital Investment' shall include the following:
a. expected price for the asset(s)
b. expected grant from CI Fund
c. expected grant from subsidy other than CI Fund
3. The regulation of application for CI Fund shall be based on the Union Financial Regulation.
Article 6 Other Incomes & Other Expenses
1. 'Other Incomes' shall mean any incomes not listed above;
2. 'Other Expenses' shall mean any expenses not listed above.
10
Article 7 Cash and Bank Balance
1. The following shall be specified in the Cultural Clubs' Financial Budget:
a. cash and bank balance updated at the commencement of AGM of the previous
session;
b. expected net income in the current session;
2. The following shall be specified in the Executive Committee's Financial Budget:
a. cash and bank balance updated at the commencement of the first Cultural Council
Meeting;
b. expected net income in the current session;
Article 8 Signatures and Official Chop
1. The Financial Budget shall be prepared by Financial Secretary (or equivalent) of the Cultural
Club or the Executive Committee and approved by the Chairperson (or equivalent) of that
session;
2. The signatures of the Financial Secretary (or equivalent) and the Chairperson (or equivalent)
and official chop of the Cultural Club or the Association shall be included in the Financial
Budget.
11
Article 1 General
1. The Annual Functional Report submitted for scrutiny shall be prepared with reference to the
template provided by the Finance Committee;
2. The items listed in Article 2 to Article 8 shall be included in the Annual Financial Report.
3. The Annual Financial Report is to report functions organized in the relative calendar year,
counting from January 1 to December 31 of the year only.
Article 2 Size of the Cultural Club
1. The size of a Cultural Club shall depend on the number of members of the Cultural Club at
the commencement of its AGM;
Size of a Cultural Club Number of Members
Large 300 or more
Medium 150 to 299
Small Less than 150
2. Number of members and Cultural Club's size shall be specified in the Annual Financial
Report.
Article 3 Budgeted Incomes & Budgeted Expenses
1. 'Budgeted Incomes' shall mean the expected incomes listed in the Financial Budget;
2. 'Budgeted Incomes' shall include:
a. budgeted General Incomes
b. budgeted Functional Incomes
c. budgeted Other Incomes
3. 'Budgeted Expenses' shall mean the expected expenses listed in the Financial Budget;
4. 'Budgeted Expenses' shall include:
a. budgeted General Expenses
Section VI Annual Financial Report
12
b. budgeted Functional Expenses
c. budgeted Other Expenses
5. The expected date(s) of all functions shall be specified in the Annual Financial Report.
Article 4 Actual Incomes & Actual Expenses
1. 'Actual Incomes' shall mean the realized incomes updated at the commencement of AGM;
2. 'Actual Incomes' shall include:
a. actual General Incomes
b. actual Functional Incomes
c. actual Other Incomes
3. 'Actual Expenses' shall mean the realized expenses updated at the commencement of AGM;
4. 'Actual Expenses' shall include:
a. actual General Expenses;
b. actual Functional Expenses;
c. actual Other Expenses.
5. The actual date(s) of all functions shall be specified in the Annual Financial Report.
Article 5 Capital Investment
1. 'Capital Investment' shall mean purchase of new equipment(s);
2. Items under 'Capital Investment' shall include the following:
a. actual price for the asset(s);
b. actual grant from CI Fund;
c. actual grant from subsidy other than CI Fund.
13
Article 6 Cash and Bank Balance
1. The following shall be specified in the Cultural Clubs' Annual Financial Report:
a. cash and bank balance updated at the commencement of AGM of the previous
session;
b. expected and actual net income in the current session;
c. actual cash and bank balance updated at the commencement of AGM
2. The following shall be specified in the Executive Committee's Annual Financial Report:
a. cash and bank balance updated at the commencement of the first Cultural Council
Meeting;
b. expected and actual net income in the current session;
c. actual cash and bank balance at the commencement of the first Cultural Council
Meeting of the next session.
Article 7 Subsidiary Documents
1. The following documents, the templates of which shall be provided by the Finance
Committee, shall be attached and submitted with the Annual Financial Report:
a. Sponsorship List;
b. Stock List;
c. verification for Cash and Bank Balance updated at the commencement of AGM.
Article 8 Signatures and Official Chop
1. The Annual Financial Report shall be prepared by Financial Secretary (or equivalent) of the
Cultural Club or the Executive Committee and approved by the Chairperson (or equivalent)
of that session;
2. The signatures of the Financial Secretary (or equivalent) and the Chairperson (or equivalent)
and official chop of each Cultural Club or the Association shall be included in the Annual
Financial Report.
14
Article 1 General
1. CA Fund shall be a subsidy distributed among Cultural Clubs and the Executive Committee;
2. The ownership of all assets purchased with the grant from CA Fund shall rest with the Union,
but the control shall rest with the respective Cultural Clubs or the Executive Committee;
3. The Cultural Club shall hand over all assets purchased with the grant from CA Fund to the
Union once disaffiliated;
4. The final approval of the budget for CA Fund shall rest with the Union Budget received and
adopted in the Union Council.
Article 2 General Expenses
Items listed below are subsidiary items in the General Expenses of CA Fund. There shall be
no maximum subsidy for each item listed below unless otherwise specified;
1. Stationery and Postage
a. The item shall include:
i) stationery for general use and activities or functions organized;
ii) all postage
b. Maximum subsidy depends on the size of the Cultural Club:
Size of a Club Maximum subsidy
Large $800
Medium $700
Small $600
Section VII Cultural Association Fund
15
2. Reference Material
a. The item shall include:
i) photocopy of material;
ii) cost of material that are vital to the functioning of the Cultural Club and cannot
be borrowed or photocopied or its usefulness and availability is related to time.
b. Maximum subsidy is $700, including photocopying costs not exceeding $400.
3. Publication
a. The subsidy includes
i) publication of the periodicals distributed to members of the Union for
promotion of the Cultural Club;
ii) publication of data.
b. Maximum subsidy is $600 per publication.
4. Annual Journal
a. The subsidy includes the publication distributed to members of the Cultural Club on
an annual basis;
b. Maximum subsidy is $2400 or two-thirds of the amounted needed, whichever is the
more.
5. Maintenance and Replacement
a. The subsidy includes:
i) equipment repaired;
ii) annual equipment check-out fee;
iii) expenses for maximizing the life-span of property;
iv) replacement of worn-out equipment and short-term materials for proper
running of the Cultural Club.
b. Maximum subsidy is $800.
16
6. Documentation
a. The subsidy is for recording activities or functions in the current session;
b. The subsidy includes:
i) multi-media storage for recording activities or functions;
ii) photographs for recording activities or functions;
iii) working paper of executive committee or group meetings
c. Maximum subsidy is $250.
7. Special Items
a. The subsidy includes any item(s) not listed above;
Article 3 Functional Expenses
Items listed below are subsidiary items in the Functional Expenses of CA Fund. There shall
be no maximum subsidy for each item listed below unless otherwise specified;
1. Publicity and Publication
a. The subsidy shall include:
i) any form(s) of advertisement of functions;
ii) publication of information for participants;
iii) publication of reports of functions.
b. The maximum basic subsidy is $200 per function;
c. There is a special subsidy for each Cultural Clubs for one of their functions. The
amount of the subsidy is $1000.
2. Souvenir
a. The subsidy shall include gift(s) to the following:
i) guest speakers for talks;
ii) external organizations or groups visited;
iii) winners of open competition;
17
iv) judges of open competition;
v) guest performers of large functions or annual performance.
b. Maximum subsidy for each souvenir is $30;
c. Maximum subsidy for souvenir is $450 per fiscal year.
3. Prizes
a. The subsidy shall include:
i) awards (or equivalent) to winners of open competitions
ii) certificates to participants of courses
b. Maximum subsidy for each prize is $30;
c. Maximum subsidy for one competition is $150.
4. Refreshment
a. The subsidy shall include food or drinks to the following:
i) guest speakers or moderators for talks;
ii) judges of open competition;
iii) guest performers of large functions or annual performance.
b. Maximum subsidy is $10 per person or $100 per function, whichever is the less;
c. No subsidy will be given for meetings;
d. No subsidy on refreshment for the purpose of members' welfare or executive
committees' personal enjoyment.
5. Transportation
a. The subsidy shall include:
i) transportation of materials or equipment;
ii) transportation of cost for pre-trip for organization of trips
b. For transportation of materials or equipment, the maximum subsidy is $500 per
function;
18
c. For pre-trip purpose inside Hong Kong, the maximum subsidy is:
i) $24 per person; or
ii) $96 per function.
iii) The amount of subsidy will be calculated per person or per function, whichever
the less.
d. For pre-trip purpose outside Hong Kong, the maximum subsidy is:
i) $150 per person; or
ii) $600 per function.
iii) The amount of subsidy will be calculated per person or per function, whichever
the less.
e. Any function that generates expected net income has no subsidy on transportation.
6. Exhibition & Demonstration
a. The subsidy shall include materials used in exhibition and demonstration related to
the nature of club;
b. Maximum subsidy is $200 per function;
c. Maximum subsidy is $800 per fiscal year;
d. No subsidy will be given to commercial display.
7. Tuition Fee/ Coach Fee/ Conductor Fee
a. The subsidy is for courses or practices that require certain expertise;
b. The maximum subsidy is one-thirds of the amounts needed;
c. The information (e.g. experience, certificate, cost, etc) of three candidates of tutors/
coaches/ conductors shall be submitted to the Finance Committee for reference unless
upon the approval of the Finance Committee or any other higher authority.
d. The following supporting documents are required for reimbursement of this item
i) letter to certify the fee had been received by the coach;
ii) HKID card and contact of the coach;
iii) written proposal on the course or practice;
19
iv) deposit slip showing the amount paid.
8. Affiliation Fee/ Registration Fee
a. The subsidy shall only include those fees that affiliated to functions held by external
organization;
b. Maximum subsidy is $1100 per function;
c. Maximum subsidy is $2200 per fiscal year.
9. Course Material
a. The subsidy shall include materials used in courses;
b. Subsidy for course materials is $20 per person;
c. Maximum subsidy for a course is $300
d. Maximum subsidy is $1500 per fiscal year.
10.Competition Cost
a. The subsidy shall include only application fee of open competition;
b. Maximum subsidy is $1100 per function;
c. Maximum subsidy is $4000 per fiscal year.
11.Rental of Venue
a. The subsidy shall include rental of venue for the function or practice;
b. Maximum subsidy is $ 2500 or one-fourths of the amount needed per function,
whichever the higher.
12.Practice Cost
a. The subsidy shall include materials used in practice or rehearsal;
b. The maximum subsidy is $2000 per fiscal year.
13.Special Items
a. The subsidy includes any item(s) not listed above;
20
Article 4 Special Items
1. The special items in General Expenses and Functional Expenses shall be considered as an
additional subsidy, and its application for subsidy shall be considered individually by the
Finance Committee;
2. All special items shall only be considered and discussed by the Finance Committee after all
basic subsidies in General Expenses are approved;
3. The final approval of special items subsidy shall rest with the Finance Committee, unless the
Cultural Council acts contrary with simple majority.
21
1. The Chairperson and the Financial Secretary of every Cultural Clubs shall be the co-holders
of its all bank accounts for the current session;
2. Cultural Clubs shall disclose information of their bank accounts to the Finance Committee
and its members;
3. Cultural Clubs shall change the authorized signatures of their bank accounts and submit
proof of the change in authorized signatures within 90 days after the date when AGM ends.
1. The interpretation of the Regulations shall rest with the Finance Committee;
2. Cultural Council reserves the right of final approval on any decision made by Finance
Committee.
1. The Regulation shall be amended or rescinded at corresponding Cultural Council Meeting
with the recommendation of the Finance Committee and the consent of a two-thirds
majority of voting members present.
2. A notice intimating the proposed amendment or recession shall be released five clear days
before the corresponding Cultural Council Meeting.
Section VIII Banking Issue
Section IX Interpretation
Section X Amendment"""


class Command(BaseCommand):
    help = "Seed company id=3 (fyp), users, demo GL data, claims data, and compliance policy context."

    @transaction.atomic
    def handle(self, *args, **options):
        company = Company.objects.filter(id=3).first()
        if company is None:
            company = Company.objects.create(id=3, name="fyp")
            self.stdout.write(self.style.SUCCESS("Created company id=3 (fyp)."))
        else:
            if company.name != "fyp":
                company.name = "fyp"
                company.save(update_fields=["name"])
            self.stdout.write("Company id=3 already exists. Ensured name is 'fyp'.")

        admin_user, _ = User.objects.update_or_create(
            username="fyp_admin",
            defaults={
                "email": "fyp_admin@fyp.local",
                "role": "admin",
                "company": company,
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )
        admin_user.set_password("fyp_admin123")
        admin_user.save()

        employee_user, _ = User.objects.update_or_create(
            username="fyp_user",
            defaults={
                "email": "fyp_user@fyp.local",
                "role": "employee",
                "company": company,
                "is_staff": False,
                "is_superuser": False,
                "is_active": True,
            },
        )
        employee_user.set_password("fyp_user123")
        employee_user.save()

        pool_definitions = [
            {"group": "Finance", "name": "Compliance Operations", "amount": Decimal("120000.00")},
            {"group": "Student Affairs", "name": "Cultural Events Budget", "amount": Decimal("180000.00")},
            {"group": "Administration", "name": "General Office Budget", "amount": Decimal("90000.00")},
        ]

        pools = []
        for pool_data in pool_definitions:
            pool, _ = BudgetPool.objects.get_or_create(
                company=company,
                name=pool_data["name"],
                defaults={
                    "group": pool_data["group"],
                    "start_date": date(2026, 1, 1),
                    "end_date": date(2026, 12, 31),
                    "total_budget_hkd": pool_data["amount"],
                    "remaining_hkd": pool_data["amount"],
                },
            )
            pools.append(pool)

        gl_account_data = [
            ("1000", "Bank - Main", "asset"),
            ("2100", "Accounts Payable", "liability"),
            ("4000", "Subsidy Income", "revenue"),
            ("5100", "Cultural Activity Expense", "expense"),
            ("5200", "Travel Expense", "expense"),
            ("5300", "Office & Administration Expense", "expense"),
        ]

        accounts_by_code = {}
        for code, name, account_type in gl_account_data:
            account, _ = GLAccount.objects.get_or_create(
                company=company,
                code=code,
                defaults={"name": name, "account_type": account_type},
            )
            accounts_by_code[code] = account

        base_date = timezone.now().date()

        if not Claim.objects.filter(user=employee_user, merchant="HKU Cultural Hall", amount_hkd=Decimal("3200.00")).exists():
            pending_claim = Claim.objects.create(
                user=employee_user,
                budget_pool=pools[1],
                status="pending",
                amount_hkd=Decimal("3200.00"),
                merchant="HKU Cultural Hall",
                date=base_date - timedelta(days=2),
                category="Venue Rental",
                note="Pending review for rehearsal venue rental.",
            )
            ReceiptFile.objects.create(
                claim=pending_claim,
                ocr_json={"entities": {"Merchant": "HKU Cultural Hall", "Total": "3200.00"}},
                ocr_confidence=0.97,
            )

        approved_samples = [
            {
                "amount": Decimal("1850.00"),
                "merchant": "Jetso Printing",
                "category": "Publicity & Publication",
                "note": "Printing for annual cultural showcase materials.",
                "pool": pools[1],
                "days_ago": 20,
                "expense_code": "5100",
            },
            {
                "amount": Decimal("420.00"),
                "merchant": "MTR Corporation",
                "category": "Transportation",
                "note": "Transportation for event setup logistics.",
                "pool": pools[0],
                "days_ago": 14,
                "expense_code": "5200",
            },
            {
                "amount": Decimal("1280.00"),
                "merchant": "OfficePlus HK",
                "category": "Stationery and Postage",
                "note": "Administrative stationery and postage supplies.",
                "pool": pools[2],
                "days_ago": 8,
                "expense_code": "5300",
            },
        ]

        for sample in approved_samples:
            existing = Claim.objects.filter(
                user=employee_user,
                merchant=sample["merchant"],
                amount_hkd=sample["amount"],
                status="approved",
            ).first()
            if existing:
                continue

            claim_date = base_date - timedelta(days=sample["days_ago"])
            claim = Claim.objects.create(
                user=employee_user,
                budget_pool=sample["pool"],
                status="approved",
                amount_hkd=sample["amount"],
                merchant=sample["merchant"],
                date=claim_date,
                category=sample["category"],
                note=sample["note"],
            )

            sample["pool"].remaining_hkd -= sample["amount"]
            sample["pool"].save(update_fields=["remaining_hkd"])

            Approval.objects.create(
                claim=claim,
                approver=admin_user,
                decision="approve",
                comment="Approved under CA fund and budget policy.",
            )

            txn = GLTransaction.objects.create(
                company=company,
                date=claim_date,
                description=f"Claim #{claim.id} - {sample['merchant']}",
                claim=claim,
            )
            GLTransactionLine.objects.create(
                transaction=txn,
                account=accounts_by_code[sample["expense_code"]],
                debit=sample["amount"],
                credit=Decimal("0.00"),
            )
            GLTransactionLine.objects.create(
                transaction=txn,
                account=accounts_by_code["1000"],
                debit=Decimal("0.00"),
                credit=sample["amount"],
            )

        rejected_exists = Claim.objects.filter(
            user=employee_user,
            merchant="Premium Catering Co.",
            amount_hkd=Decimal("5800.00"),
            status="rejected",
        ).exists()
        if not rejected_exists:
            rejected_claim = Claim.objects.create(
                user=employee_user,
                budget_pool=pools[0],
                status="rejected",
                amount_hkd=Decimal("5800.00"),
                merchant="Premium Catering Co.",
                date=base_date - timedelta(days=6),
                category="Refreshment",
                note="Refreshment claim exceeded policy subsidy cap.",
            )
            Approval.objects.create(
                claim=rejected_claim,
                approver=admin_user,
                decision="reject",
                comment="Rejected: refreshment subsidy exceeds Article 3 limits.",
            )

        PolicyDoc.objects.update_or_create(
            company=company,
            title="HKUSU Cultural Association Financial Regulation",
            version="2017-2018-CM4",
            defaults={
                "url": "",
                "content_text": POLICY_CONTEXT_TEXT,
            },
        )

        self.stdout.write(self.style.SUCCESS("FYP seed complete: company, users, budgets, claims, GL, and policy context are ready."))
