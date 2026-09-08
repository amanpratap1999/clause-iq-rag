"""
Generates 6 synthetic, realistic multi-page policy and contract documents as PDFs.
Uses reportlab for proper multi-page PDF rendering.
"""
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

DOCS_DATA = [
    {
        "filename": "Remote_Work_and_Equipment_Policy.pdf",
        "title": "Remote Work and Home Office Equipment Policy",
        "pages": [
            [
                ("Section 1.0: Eligibility and Core Working Hours",
                 "All full-time employees are eligible for remote or hybrid work upon approval from their direct manager. Employees must be available during core business hours from 10:00 AM to 4:00 PM EST for scheduled team meetings, sprint standups, and customer escalations. Flexibility outside these core hours must be arranged directly with team leadership."),
                ("Section 2.0: Home Office Equipment Stipend",
                 "New employees receive a one-time home office setup stipend of $1,000 to purchase ergonomic desks, monitors, and peripherals. Employees are also entitled to an annual equipment maintenance and refresh allowance of $250, claimable through the corporate expense portal during Q1 of each calendar year.")
            ],
            [
                ("Section 3.0: Equipment Return Upon Separation",
                 "Company-owned hardware including laptops, security keys, and encrypted storage devices must be returned via prepaid corporate shipping box within 14 calendar days of separation. Failure to return hardware within this window may result in payroll deduction or legal recovery procedures."),
                ("Section 4.0: Information Security and Public Wi-Fi",
                 "Remote employees are strictly prohibited from conducting corporate business over unencrypted public Wi-Fi networks without activating the corporate WireGuard VPN. Multi-factor authentication (MFA) via hardware security key or corporate authenticator app is mandatory on all enrolled devices.")
            ]
        ]
    },
    {
        "filename": "Master_SaaS_Vendor_Agreement.pdf",
        "title": "Master Cloud SaaS Services Agreement",
        "pages": [
            [
                ("Section 1.0: Scope of Licensed Cloud Services",
                 "Vendor grants Customer a non-exclusive, worldwide, revocable license to access the Enterprise Analytics Platform during the Subscription Term. Customer user seats are capped at the contracted tier specified in Order Form Schedule A."),
                ("Section 2.0: Service Level Agreement and Uptime Guarantees",
                 "Vendor commits to a monthly service availability of 99.9% uptime, excluding scheduled maintenance windows announced at least 72 hours in advance. If monthly uptime drops below 99.5%, Customer is entitled to a 10% service credit; if uptime drops below 99.0%, Customer receives a 25% service credit on the subsequent billing cycle.")
            ],
            [
                ("Section 3.0: Limitation of Direct and Consequential Liability",
                 "Except for breaches of confidentiality or gross negligence, each party's aggregate liability arising under this Agreement is strictly capped at the total amount of fees paid by Customer during the twelve (12) months preceding the incident. Neither party shall be liable for indirect, punitive, or consequential damages."),
                ("Section 4.0: Termination for Cause and Notice Period",
                 "Either party may terminate this Agreement immediately upon written notice if the other party materially breaches any provision and fails to cure such breach within thirty (30) calendar days of receiving detailed written notice.")
            ]
        ]
    },
    {
        "filename": "Data_Privacy_and_Security_Policy.pdf",
        "title": "Data Privacy and Information Security Standards",
        "pages": [
            [
                ("Section 1.0: Data Classification and Handling",
                 "Data handled by corporate systems is classified into three tiers: Tier 1 (Public Marketing Materials), Tier 2 (Internal Business Operations), and Tier 3 (Restricted Customer PII and Financial Records). Tier 3 records must be encrypted at rest using AES-256 and in transit using TLS 1.3."),
                ("Section 2.0: Password Complexity and Session Timeouts",
                 "All corporate user accounts require passwords of at least 16 characters including uppercase, lowercase, numbers, and special symbols. Passwords must be rotated every 90 days. Unattended workstation sessions must automatically lock after 10 minutes of inactivity.")
            ],
            [
                ("Section 3.0: Incident Response and Breach Notification",
                 "Any suspected security breach, unauthorized credential access, or ransomware event must be escalated to the Security Operations Center (SOC) within 4 hours of detection. If customer Personally Identifiable Information (PII) is compromised, external regulatory and customer notifications must be issued within 72 hours."),
                ("Section 4.0: SOC 2 Access Auditing and Third-Party Reviews",
                 "Annual SOC 2 Type II audits are conducted by an independent certified CPA firm. User access privileges across all production environments are audited and certified on a quarterly basis by department heads.")
            ]
        ]
    },
    {
        "filename": "Employee_Travel_and_Expense_Policy.pdf",
        "title": "Corporate Travel and Business Expense Policy",
        "pages": [
            [
                ("Section 1.0: Commercial Air Travel Booking Guidelines",
                 "Employees must book airfare via the corporate travel portal at least 14 days in advance. Economy class is required for all domestic and short-haul flights under 6 hours in total duration. Premium Economy or Business Class is permitted solely for continuous international flights exceeding 6 hours."),
                ("Section 2.0: Daily Meals and Incidentals Per Diem",
                 "The company reimburses business meals up to a maximum per diem of $75 per day for domestic travel and $100 per day for international travel. Itemized item-level receipts showing date, merchant, and purchased items are required for all individual expenses exceeding $25.")
            ],
            [
                ("Section 3.0: Expense Claim Submission Window",
                 "All expense reports with attached digital receipts must be submitted via the finance portal within 30 calendar days following the completion of travel. Expenses submitted beyond 60 calendar days will be automatically rejected and ineligible for corporate reimbursement."),
                ("Section 4.0: Non-Reimbursable Personal Expenses",
                 "Personal entertainment, hotel pay-per-view movies, flight cancellation penalties incurred for non-business reasons, traffic fines, and alcoholic beverages not part of a pre-approved client dinner are strictly non-reimbursable.")
            ]
        ]
    },
    {
        "filename": "Code_of_Conduct_and_Ethics.pdf",
        "title": "Corporate Code of Business Conduct and Ethics",
        "pages": [
            [
                ("Section 1.0: Anti-Bribery and Gift Acceptance Limits",
                 "Employees must never offer, solicit, or accept any bribe, kickback, or improper advantage. Nominal business gifts, promotional items, or event tickets valued under $50 may be accepted. Any gift valued above $25 must be formally logged in the compliance registry within 5 business days."),
                ("Section 2.0: Outside Business Activities and Conflicts",
                 "Employees must disclose any external commercial engagements, advisory roles, or board memberships to Legal before commencement. Outside employment that competes directly with the company's product line is strictly prohibited.")
            ],
            [
                ("Section 3.0: Whistleblower Protections and Anonymous Hotline",
                 "The company maintains a 24/7 confidential, third-party managed whistleblower hotline. Reports may be filed anonymously via web form or toll-free telephone. Retaliation of any kind against an employee who reports suspected misconduct in good faith is grounds for immediate termination."),
                ("Section 4.0: Disciplinary Actions and Enforcement",
                 "Violations of this Code will result in disciplinary action up to and including formal reprimand, suspension, termination of employment, and referral to law enforcement authorities where civil or criminal laws have been breached.")
            ]
        ]
    },
    {
        "filename": "API_Licensing_and_Terms_of_Service.pdf",
        "title": "Developer API Licensing and Usage Agreement",
        "pages": [
            [
                ("Section 1.0: API Access Grant and Developer Credentials",
                 "Company grants Developer a non-exclusive, revocable license to access the Developer API strictly for integrating approved third-party applications. API secret keys must be stored securely in server-side environments and never exposed in public repositories or client-side web bundles."),
                ("Section 2.0: Rate Limiting and Quota Enforcement",
                 "API requests are rate-limited per API key based on subscription tier: Standard Tier keys are limited to 100 requests per minute; Enterprise Tier keys are entitled to 1,000 requests per minute with a burst allowance of up to 1,500 requests per minute. Exceeding limits will return HTTP 429 Too Many Requests.")
            ],
            [
                ("Section 3.0: Intellectual Property and Data Ownership",
                 "Developer retains all proprietary rights and ownership over application data submitted through the API. The Company retains all intellectual property rights, patents, copyrights, and trade secrets in the API platform and underlying model endpoints."),
                ("Section 4.0: Prohibited Reverse Engineering and Scraping",
                 "Developers are strictly prohibited from decompiling, reverse engineering, scraping bulk dataset payloads, or using API outputs to train competing machine learning or artificial intelligence models.")
            ]
        ]
    }
]

def generate_pdf(doc_info: dict, output_dir: Path):
    filepath = output_dir / doc_info["filename"]
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=14
    )
    heading_style = ParagraphStyle(
        'ClauseHeading',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#2563EB'),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'ClauseBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=12
    )

    story = []
    
    for page_idx, page_clauses in enumerate(doc_info["pages"]):
        if page_idx == 0:
            story.append(Paragraph(doc_info["title"], title_style))
            story.append(Spacer(1, 10))
            
        for clause_title, clause_text in page_clauses:
            story.append(Paragraph(clause_title, heading_style))
            story.append(Paragraph(clause_text, body_style))
            story.append(Spacer(1, 8))
            
        if page_idx < len(doc_info["pages"]) - 1:
            story.append(PageBreak())
            
    doc.build(story)
    print(f"Generated PDF: {filepath}")

def main():
    output_dir = Path(__file__).resolve().parent / "pdf_files"
    output_dir.mkdir(parents=True, exist_ok=True)
    for doc in DOCS_DATA:
        generate_pdf(doc, output_dir)

if __name__ == "__main__":
    main()
