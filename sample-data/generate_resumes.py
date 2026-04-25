"""Generate sample PDF resumes for testing TalentScout AI.

Usage:
    cd sample-data
    pip install fpdf2   (or:  uv pip install fpdf2)
    python generate_resumes.py

Creates PDF resumes in the resumes/ folder from profiles defined in resume_data.py.
Edit resume_data.py to add/modify candidate profiles.
"""

import os
from fpdf import FPDF
from resume_data import RESUMES


def sanitize(text: str) -> str:
    """Replace unicode characters that Helvetica can't handle."""
    return text.replace("\u2013", "-").replace("\u2014", "-").replace("\u2018", "'").replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')


def create_pdf(resume: dict, output_dir: str):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Sanitize all string values
    name = sanitize(resume["name"])
    email = sanitize(resume["email"])
    phone = sanitize(resume["phone"])
    summary = sanitize(resume["summary"])
    skills = [sanitize(s) for s in resume["skills"]]

    # Name
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, name, new_x="LMARGIN", new_y="NEXT")

    # Contact
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    contact = f"{email}  |  {phone}"
    pdf.cell(0, 6, contact, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Summary
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "PROFESSIONAL SUMMARY", new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(70, 70, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, summary)
    pdf.ln(3)

    # Skills
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "SKILLS", new_x="LMARGIN", new_y="NEXT")
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 10)
    skills_text = "  |  ".join(skills)
    pdf.multi_cell(0, 5, skills_text)
    pdf.ln(3)

    # Experience
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "WORK EXPERIENCE", new_x="LMARGIN", new_y="NEXT")
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)

    for job in resume["experience"]:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 6, sanitize(f"{job['role']}  -  {job['company']}"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, sanitize(job["duration"]), new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 10)
        for h in job["highlights"]:
            pdf.set_x(10)
            pdf.multi_cell(0, 5, sanitize("- " + h))
        pdf.ln(2)

    # Education
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "EDUCATION", new_x="LMARGIN", new_y="NEXT")
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)
    for edu in resume["education"]:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, sanitize(edu['degree']), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 5, sanitize(f"{edu['institution']}  ({edu['year']})"), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

    # Achievements
    if resume.get("achievements"):
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "ACHIEVEMENTS", new_x="LMARGIN", new_y="NEXT")
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 10)
        for a in resume["achievements"]:
            pdf.set_x(10)
            pdf.multi_cell(0, 5, sanitize("- " + a))

    path = os.path.join(output_dir, resume["filename"])
    pdf.output(path)
    print(f"  Created: {path}")


def main():
    output_dir = os.path.join(os.path.dirname(__file__), "resumes")
    os.makedirs(output_dir, exist_ok=True)

    print(f"Generating {len(RESUMES)} sample resumes...\n")
    for resume in RESUMES:
        create_pdf(resume, output_dir)

    print(f"\nDone! {len(RESUMES)} resumes saved to {output_dir}/")
    print("\nResume profiles:")
    print("  Strong Full-Stack match:  Arjun Mehta, Priya Sharma")
    print("  Partial Full-Stack match: Rahul Verma (backend-only), Sneha Iyer (frontend-only)")
    print("  Weak / wrong domain:      Vikram Joshi (marketing), Neha Kapoor (mechanical)")
    print("  Strong Data Science match: Ananya Reddy, Karthik Nair")
    print("  Strong DevOps match:      Deepak Srinivasan, Meera Krishnan")
    print("  Partial DevOps match:     Rohan Gupta (sysadmin)")
    print("  Junior Full-Stack:        Aisha Khan (1.5y exp)")


if __name__ == "__main__":
    main()
