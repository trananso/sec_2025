from google import genai
import ast


def convert_hourly_to_yearly(rate, hours_per_week=40, weeks_per_year=52):  # default to be fully time conversion
    return rate * hours_per_week * weeks_per_year


def parse_salary(salary: str):
    # convert to full time
    salary = salary.replace("$", "")
    salary_time = "hourly" if "hourly" in salary else "yearly"
    salary = salary.replace(salary_time, "").strip()
    salary = salary.replace("–", "-")
    if "-" in salary:  # it is a range
        original_salary_min, original_salary_max = map(float, map(lambda x: x.replace(",", ""), salary.split("-")))

        if salary_time == "hourly":
            yearly_salary_min, yearly_salary_max = convert_hourly_to_yearly(
                original_salary_min), convert_hourly_to_yearly(original_salary_max)
        else:
            yearly_salary_min, yearly_salary_max = original_salary_min, original_salary_max
        return [salary_time, original_salary_min, original_salary_max, yearly_salary_min, yearly_salary_max]

    elif salary is not False:
        original_salary = float(salary.replace(",", ""))
        if salary_time == "hourly":
            yearly_salary = convert_hourly_to_yearly(original_salary)
        else:
            yearly_salary = original_salary
        return [salary_time, original_salary, yearly_salary]


def analyze(parsed_job_specs: list):
    salary, AI_disclosure, AI_disclosure_description, not_require_canadian_experience, vacancy_disclosure, probability_of_AI = parsed_job_specs

    if salary is not False:
        salary = parse_salary(salary)
        salary_time = salary[0]
        salary = salary[1:]
        if len(salary) == 4:  # if the salary is a range
            original_min, original_max, yearly_min, yearly_max = salary
        else:
            original_min, original_max, yearly_min, yearly_max = salary[0], False, salary[1], False

        if original_max is not False:
            salary_exceeded = (yearly_max - yearly_min) > 50000
        else:
            salary_exceeded = (original_max - original_min) > 50000
        response = {
            "salary": {
                "salaryExceeded": salary_exceeded,
                "format": salary_time,
                "originalMin": original_min,
                "originalMax": original_max,
            },
            "aiDisclosure": AI_disclosure,
            "aiDisclosureDescription": AI_disclosure_description,
            "canadianExperienceNotRequired": not_require_canadian_experience,
            "vacancyDisclosure": vacancy_disclosure,
            "aiUseProbability": probability_of_AI
        }
    else:
        response = {
            "aiDisclosure": AI_disclosure,
            "aiDisclosureDescription": AI_disclosure_description,
            "canadianExperienceNotRequired": not_require_canadian_experience,
            "vacancyDisclosure": vacancy_disclosure,
            "aiUseProbability": probability_of_AI
        }
    return response


class Parse:
    def __init__(self, api_key=None):
        self.prompt = """
        Your job is to analyze the provided job posting text and extract six specific data points into a Python list format.

        Job Description:
        "JOB_POSTING"

        Instructions:
        Analyze the text and return ONLY a single Python list containing the following elements in this exact order. Do not wrap the output in markdown or code blocks. You MUST follow exactly what the instructions below. Just return the raw list string.

        1. Salary String: Extract the exact salary or salary range or hourly rate mentioned. You MUST use [yearly, hourly] to denote the salary. If no salary is present, return "False".
        2. AI Disclosure Found: Return "True" if the text explicitly mentions using Artificial Intelligence (AI) for screening, selection, or evaluation. Return "False" if not mentioned.
        3. AI Conditions: If step 2 is True, quote the specific sentence describing how AI is used. If #2 is False, return False.
        4. Does NOT Require Canadian Experience: Return "False" if the text explicitly requires "Canadian experience," "Canadian work experience," or "local experience." Return "True" if not.
        5. Vacancy Status Disclosure: Return the specific phrase indicating if this is an existing vacancy or a future pool (e.g., "Active vacancy," "Talent pool," "Future opportunity") If the description does NOT SPECIFY or NOT MENTION vacancy return "False". 
        6. The probability that the job description was written by generative AI.

        Output Format Example:
        ["$20.00 hourly", "False", "Humans are used to screen", "False", "True", "0.3"]
        ["$20.00-$25.00 hourly", "False", "Humans are used to screen", "False", "False", "0.2"]
        ["$50,000-$60,000 yearly", "True", "AI is used to screen resumes", "False", "False", "0.6"]

        Your Response:
        """
        self.client = genai.Client(api_key=api_key)

    def parse_response(self, response):
        return ast.literal_eval(response)

    def convert_types(self, parsed_job_specs):
        for i, val in enumerate(parsed_job_specs):
            if isinstance(val, str):
                if val.lower() == "false":
                    parsed_job_specs[i] = False
                elif val.lower() == "true":
                    parsed_job_specs[i] = True
        return parsed_job_specs

    def run(self, job_desc):
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=self.prompt.replace("JOB_POSTING", job_desc))
        parsed_job_specs = self.parse_response(response.text)
        parsed_job_specs = self.convert_types(parsed_job_specs)
        return analyze(parsed_job_specs)


# format = {
#     "salary": {
#         "salaryExceeded": bool,
#         "yearlyMin": float,
#         "yearlyMax": float,
#         "originalMin": float,
#         "originalMax": float,
#     },
#     "aiDisclosure": bool,
#     "aiDisclosureDescription": str,
#     "canadianExperienceNotRequired": bool,
#     "vacancyDisclosure": bool,
#     "aiUseProbability": float,
# }


if __name__ == "__main__":
    job_parser = Parse()
    x = job_parser.run("""Job Title: Senior Data Analyst
Company: DataFlow Analytics Inc.
Location: Ottawa, ON (Remote)
Employment Type: Full-time, Permanent

Overview:
DataFlow Analytics is seeking an experienced Senior Data Analyst to join our growing team. You will work with large datasets, create insightful visualizations, and help drive data-driven decision making across the organization.

Key Responsibilities:
- Analyze complex datasets using SQL, Python, and R
- Create dashboards and reports for stakeholders
- Develop predictive models and statistical analyses
- Present findings to executive leadership
- Mentor junior analysts

Requirements (Must-Have):
- Minimum 5 years of Canadian work experience in data analysis
- Bachelor's degree in Statistics, Mathematics, or related field
- Proficiency in SQL, Python, and data visualization tools
- Strong communication and presentation skills
- Experience with cloud platforms (AWS, Azure, or GCP)

Nice-to-Have:
- Master's degree in a quantitative field
- Experience with machine learning frameworks
- Previous experience in the financial services industry

Benefits:
- Comprehensive health and dental benefits
- 4 weeks paid vacation
- Professional development budget
- Flexible work arrangements

Application Process:
Please submit your resume and cover letter through our online portal. Selected candidates will be contacted for interviews.

""")
    # Job Title: Junior Software Developer
    # Company: MapleTech Solutions
    # Location: Toronto, ON (Hybrid: 3 days on-site, 2 days remote)
    # Employment Type: Full-time, Permanent
    # Compensation: $58,000–$65,000 annually, based on experience
    #
    # Overview:
    # MapleTech Solutions is seeking a Junior Software Developer to join our internal tools team. You will work closely with senior developers to maintain and enhance applications used across the company. This is a great opportunity for recent graduates or early-career developers who want structured mentorship and exposure to a modern development stack.
    #
    # Key Responsibilities:
    # - Implement features and bug fixes for internal web applications
    # - Write unit and integration tests to maintain code quality
    # - Participate in code reviews and daily stand-up meetings
    # - Collaborate with designers and product owners to refine requirements
    # - Document changes and follow our established development workflow
    #
    # Requirements (Must-Have):
    # - 0–2 years of professional experience or equivalent personal/academic projects
    # - Proficiency in at least one programming language (Python, JavaScript, or Java)
    # - Basic understanding of Git and version control workflows
    # - Strong problem-solving skills and attention to detail
    # - Ability to work in a team and communicate clearly
    #
    # Nice-to-Have:
    # - Experience with web frameworks (e.g., Django, Flask, React, or Vue)
    # - Familiarity with relational databases (e.g., PostgreSQL, MySQL)
    # - Exposure to Agile or Scrum methodologies
    #
    # Work Hours:
    # - Standard schedule: Monday to Friday, 9:00 AM–5:00 PM (flexible within core hours)
    # - Occasional paid overtime may be requested during critical releases, with notice
    #
    # Benefits:
    # - Health, dental, and vision coverage after 3 months
    # - 3 weeks paid vacation to start, plus sick days
    # - Annual learning and training budget
    # - RRSP matching program after 1 year
    # - Access to employee wellness programs
    #
    # AI Use in Hiring:
    # - We may use automated tools to assist in application screening (e.g., keyword matching).
    # - All applications are reviewed by a human recruiter before shortlisting.
    # - Automated tools do not make final hiring decisions.
    #
    # Application Process:
    # Please submit your resume, a brief cover letter, and (optionally) a link to your GitHub or portfolio. Selected candidates will be invited to a two-step interview process, which includes a short technical exercise.
    #
    # Accommodation:
    # MapleTech Solutions is committed to an inclusive and accessible recruitment process. If you require accommodation at any stage, please contact hr@mapletech.ca.
    #
    # """)
    print([x])
