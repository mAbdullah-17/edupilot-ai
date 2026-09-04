"""Seed script — populate realistic demo opportunities for EduPilot AI (Day 2).

Run from project root:
    python -m scripts.seed_data

Safe to run multiple times (uses INSERT IGNORE on title+organization uniqueness).
"""

import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import get_db

# ── Demo opportunities ──────────────────────────────────

OPPORTUNITIES = [
    # ── Lahore (city-level) ──
    {
        "title": "LUMS National Outreach Programme 2026",
        "organization": "LUMS",
        "description": (
            "The Lahore University of Management Sciences offers a fully funded "
            "undergraduate programme for talented students from underprivileged "
            "backgrounds across Pakistan. Covers tuition, hostel, and a monthly stipend."
        ),
        "category": "Scholarship",
        "opportunity_type": "Undergraduate",
        "location": "Lahore, Punjab, Pakistan",
        "city": "Lahore", "province": "Punjab", "country": "Pakistan", "region": None,
        "deadline": "2026-11-30",
        "external_url": "https://lums.edu.pk/nop",
        "eligibility_summary": "Pakistani nationals with financial need; intermediate (HSSC) with 80%+ marks.",
        "status": "active",
    },
    {
        "title": "Software Engineering Internship — Systems Ltd",
        "organization": "Systems Limited",
        "description": (
            "Three-month paid summer internship at Pakistan's largest IT company. "
            "Work on enterprise projects using Java, Spring Boot, and React. "
            "Mentorship from senior engineers included."
        ),
        "category": "Internship",
        "opportunity_type": "Internship",
        "location": "Lahore, Punjab, Pakistan",
        "city": "Lahore", "province": "Punjab", "country": "Pakistan", "region": None,
        "deadline": "2026-10-15",
        "external_url": "https://systemsltd.com/careers/internship",
        "eligibility_summary": "CS/SE undergraduates in their 3rd year or above.",
        "status": "active",
    },
    {
        "title": "Punjab Youth Festival 2026 — Startup Pitch",
        "organization": "Punjab Information Technology Board",
        "description": (
            "Annual youth innovation festival featuring a startup pitch competition "
            "with prizes up to PKR 5 million in seed funding. Workshops, hackathons, "
            "and networking with investors."
        ),
        "category": "Competition",
        "opportunity_type": "Competition",
        "location": "Lahore, Punjab, Pakistan",
        "city": "Lahore", "province": "Punjab", "country": "Pakistan", "region": None,
        "deadline": "2026-12-20",
        "external_url": "https://pitb.gop.pk/youthfestival",
        "eligibility_summary": "Open to all Pakistani youth aged 18-35 with a startup idea.",
        "status": "active",
    },
    # ── Punjab (province-level) ──
    {
        "title": "Punjab Merit Scholarship 2026",
        "organization": "Government of Punjab",
        "description": (
            "Merit-based scholarships for students enrolled in public-sector "
            "universities across Punjab. Annual award of PKR 100,000 for top "
            "performers in STEM disciplines."
        ),
        "category": "Scholarship",
        "opportunity_type": "Undergraduate",
        "location": "Punjab, Pakistan",
        "city": None, "province": "Punjab", "country": "Pakistan", "region": None,
        "deadline": "2026-09-30",
        "external_url": None,
        "eligibility_summary": "Enrolled in a public-sector university in Punjab; CGPA 3.5+.",
        "status": "active",
    },
    # ── Pakistan (country-level) ──
    {
        "title": "HEC Overseas Scholarship Phase II",
        "organization": "Higher Education Commission",
        "description": (
            "Fully funded PhD scholarships for Pakistani nationals to study at "
            "top-100 world universities. Covers tuition, living expenses, travel, "
            "and health insurance for up to 5 years."
        ),
        "category": "Scholarship",
        "opportunity_type": "PhD",
        "location": "Pakistan",
        "city": None, "province": None, "country": "Pakistan", "region": None,
        "deadline": "2026-12-31",
        "external_url": "https://hec.gov.pk/english/scholarships/Pages/OS-II.aspx",
        "eligibility_summary": "Pakistani nationals with MPhil/MS; age under 35.",
        "status": "active",
    },
    {
        "title": "Junior Data Analyst — Jazz",
        "organization": "Jazz (VEON)",
        "description": (
            "Full-time entry-level position in the Data & Analytics division. "
            "Work with Python, SQL, and Tableau to drive business insights for "
            "Pakistan's largest telecom operator."
        ),
        "category": "Job",
        "opportunity_type": "Full-time",
        "location": "Islamabad, Pakistan",
        "city": "Islamabad", "province": None, "country": "Pakistan", "region": None,
        "deadline": "2026-10-01",
        "external_url": "https://jazz.com.pk/careers",
        "eligibility_summary": "Bachelor's in CS, Stats, or related field; 0-2 years experience.",
        "status": "active",
    },
    {
        "title": "Pakistan Climate Fellowship 2026",
        "organization": "WWF Pakistan",
        "description": (
            "Six-month research fellowship focused on climate adaptation strategies "
            "in the Indus River basin. Field work combined with policy research. "
            "Monthly stipend of PKR 80,000."
        ),
        "category": "Fellowship",
        "opportunity_type": "Fellowship",
        "location": "Pakistan",
        "city": None, "province": None, "country": "Pakistan", "region": None,
        "deadline": "2026-11-15",
        "external_url": "https://wwf.org.pk/fellowships",
        "eligibility_summary": "Master's in Environmental Science, Geography, or related field.",
        "status": "active",
    },
    {
        "title": "National Science & Engineering Fair 2026",
        "organization": "Pakistan Science Foundation",
        "description": (
            "National-level science fair for university students. Present research "
            "projects in engineering, biotech, AI, and energy. Winners receive cash "
            "prizes and international conference sponsorship."
        ),
        "category": "Competition",
        "opportunity_type": "Competition",
        "location": "Islamabad, Pakistan",
        "city": "Islamabad", "province": None, "country": "Pakistan", "region": None,
        "deadline": "2027-01-15",
        "external_url": "https://psf.org.pk/nsf",
        "eligibility_summary": "Open to all Pakistani university students.",
        "status": "active",
    },
    # ── International ──
    {
        "title": "Erasmus Mundus — European Master in AI",
        "organization": "European Commission",
        "description": (
            "Two-year joint master's programme in Artificial Intelligence across "
            "three European universities. Full scholarship including tuition, travel, "
            "and a monthly allowance of EUR 1,400."
        ),
        "category": "Scholarship",
        "opportunity_type": "Master's",
        "location": "Europe (Multiple Countries)",
        "city": None, "province": None, "country": None, "region": "Europe",
        "deadline": "2027-01-16",
        "external_url": "https://www.eacea.ec.europa.eu/scholarships/emjmd-catalogue_en",
        "eligibility_summary": "Bachelor's in CS or related field; IELTS 6.5+; programming experience.",
        "status": "active",
    },
    {
        "title": "Fulbright Master's Scholarship 2027",
        "organization": "USEFP Pakistan",
        "description": (
            "Fully funded master's degree at a US university. Covers tuition, "
            "textbooks, airfare, and a living stipend. GRE required."
        ),
        "category": "Scholarship",
        "opportunity_type": "Master's",
        "location": "United States",
        "city": None, "province": None, "country": None, "region": "North America",
        "deadline": "2027-02-28",
        "external_url": "https://www.usefp.org/scholarships/fulbright-degree",
        "eligibility_summary": "Pakistani citizens; 16 years of education; GRE General.",
        "status": "active",
    },
    {
        "title": "Google STEP Internship 2026",
        "organization": "Google",
        "description": (
            "Student Training in Engineering Program — 12-week internship at "
            "Google offices worldwide. Mentorship, training, and real project work. "
            "Targeted at first and second year CS students."
        ),
        "category": "Internship",
        "opportunity_type": "Internship",
        "location": "Multiple Locations",
        "city": None, "province": None, "country": None, "region": "International",
        "deadline": "2026-10-30",
        "external_url": "https://careers.google.com/students",
        "eligibility_summary": "Currently enrolled in a CS or related bachelor's programme (1st/2nd year).",
        "status": "active",
    },
    {
        "title": "Chevening Scholarship 2027",
        "organization": "UK Foreign, Commonwealth & Development Office",
        "description": (
            "One-year fully funded master's degree at any UK university. "
            "Leadership development, networking opportunities, and full financial support."
        ),
        "category": "Scholarship",
        "opportunity_type": "Master's",
        "location": "United Kingdom",
        "city": None, "province": None, "country": None, "region": "Europe",
        "deadline": "2026-11-05",
        "external_url": "https://www.chevening.org/apply",
        "eligibility_summary": "Two years of work experience; return to home country for 2 years.",
        "status": "active",
    },
    # ── Remote ──
    {
        "title": "Google Developer Student Clubs — Lead 2026",
        "organization": "Google Developers",
        "description": (
            "Become a GDSC Lead at your university. Organise workshops, build "
            "community, and receive training from Google. One-year leadership programme."
        ),
        "category": "Programme",
        "opportunity_type": "Programme",
        "location": "Remote",
        "city": None, "province": None, "country": None, "region": None,
        "deadline": "2026-10-31",
        "external_url": "https://developers.google.com/community/gdsc",
        "eligibility_summary": "University students with leadership and technical skills.",
        "status": "active",
    },
    {
        "title": "Meta University — Remote Software Engineering",
        "organization": "Meta",
        "description": (
            "Eight-week remote programme for students from underrepresented "
            "backgrounds. Work on real Meta products with dedicated mentors. "
            "Stipend included."
        ),
        "category": "Internship",
        "opportunity_type": "Internship",
        "location": "Remote",
        "city": None, "province": None, "country": None, "region": None,
        "deadline": "2026-11-01",
        "external_url": "https://www.metacareers.com/jobs",
        "eligibility_summary": "Pursuing a bachelor's or master's in a technical field.",
        "status": "active",
    },
    {
        "title": "Khan Academy Content Fellow",
        "organization": "Khan Academy",
        "description": (
            "Part-time remote fellowship creating educational content in Urdu "
            "and English for mathematics and science courses. Flexible hours. "
            "Monthly honorarium of USD 800."
        ),
        "category": "Fellowship",
        "opportunity_type": "Part-time",
        "location": "Remote",
        "city": None, "province": None, "country": None, "region": None,
        "deadline": None,
        "external_url": "https://www.khanacademy.org/careers",
        "eligibility_summary": "Strong subject knowledge in Math or Science; teaching experience preferred.",
        "status": "active",
    },
]

# ── Requirements per opportunity ────────────────────────
# Keyed by opportunity title (matched after insert).

REQUIREMENTS = {
    "LUMS National Outreach Programme 2026": [
        ("academic", "Intermediate (HSSC) with at least 80% marks"),
        ("financial", "Demonstrated financial need — family income below PKR 600,000/year"),
        ("nationality", "Pakistani national or AJK domicile holder"),
    ],
    "Software Engineering Internship — Systems Ltd": [
        ("academic", "Enrolled in CS, SE, or IT programme — 3rd year or above"),
        ("technical", "Proficiency in at least one programming language (Java, Python, or C#)"),
    ],
    "HEC Overseas Scholarship Phase II": [
        ("academic", "MPhil or MS degree from an HEC-recognised institution"),
        ("age", "Maximum 35 years at the time of application"),
        ("nationality", "Pakistani national with valid CNIC"),
    ],
    "Erasmus Mundus — European Master in AI": [
        ("academic", "Bachelor's degree in CS, Maths, or related field with GPA 3.0+"),
        ("language", "IELTS 6.5 or equivalent (TOEFL iBT 90+)"),
        ("technical", "Demonstrated programming experience in Python or C++"),
    ],
    "Fulbright Master's Scholarship 2027": [
        ("academic", "Minimum 16 years of education (4-year bachelor's or equivalent)"),
        ("test", "GRE General test — competitive score required"),
        ("nationality", "Pakistani citizen residing in Pakistan at the time of application"),
    ],
    "Google STEP Internship 2026": [
        ("academic", "Currently in 1st or 2nd year of a bachelor's in CS or related field"),
        ("technical", "Coding experience in at least one language (Python, Java, C++)"),
    ],
    "Chevening Scholarship 2027": [
        ("experience", "Minimum two years of work experience (2,800 hours)"),
        ("commitment", "Commit to return to home country for at least two years after study"),
        ("academic", "Undergraduate degree equivalent to UK upper second-class honours"),
    ],
}


def seed():
    """Insert demo opportunities and requirements. Safe to re-run."""
    db = get_db()

    inserted = 0
    skipped = 0

    for opp in OPPORTUNITIES:
        # Check if already exists by title + organization
        existing = db.execute(
            "SELECT id FROM opportunities WHERE title = %s AND organization = %s",
            (opp["title"], opp["organization"]),
            fetch=True,
        )
        if existing:
            skipped += 1
            opp_id = existing[0]["id"]
        else:
            opp_id = db.execute(
                "INSERT INTO opportunities "
                "(title, organization, description, category, opportunity_type, "
                " location, city, province, country, region, deadline, "
                " external_url, eligibility_summary, status) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    opp["title"], opp["organization"], opp["description"],
                    opp["category"], opp["opportunity_type"], opp["location"],
                    opp["city"], opp["province"], opp["country"], opp["region"],
                    opp["deadline"], opp["external_url"],
                    opp["eligibility_summary"], opp["status"],
                ),
            )
            inserted += 1

        # Insert requirements (if any)
        reqs = REQUIREMENTS.get(opp["title"], [])
        for req_type, req_desc in reqs:
            # Avoid duplicate requirements
            existing_req = db.execute(
                "SELECT id FROM opportunity_requirements "
                "WHERE opportunity_id = %s AND requirement_type = %s AND description = %s",
                (opp_id, req_type, req_desc),
                fetch=True,
            )
            if not existing_req:
                db.execute(
                    "INSERT INTO opportunity_requirements "
                    "(opportunity_id, requirement_type, description) "
                    "VALUES (%s, %s, %s)",
                    (opp_id, req_type, req_desc),
                )

    total = len(OPPORTUNITIES)
    print(f"[seed_data] Done. {total} opportunities total: "
          f"{inserted} inserted, {skipped} already existed.")


if __name__ == "__main__":
    seed()
