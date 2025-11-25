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
        Analyze the text and return ONLY a single Python list containing the following elements in this exact order. Do not wrap the output in markdown or code blocks. Just return the raw list string.

        1. Salary String: Extract the exact salary or salary range or hourly rate mentioned. You MUST use [yearly, hourly] to denote the salary. If no salary is present, return "False".
        2. AI Disclosure Found: Return "True" if the text explicitly mentions using Artificial Intelligence (AI) for screening, selection, or evaluation. Return "False" if not mentioned.
        3. AI Conditions: If step 2 is True, quote the specific sentence describing how AI is used. If #2 is False, return False.
        4. Does NOT Require Canadian Experience: Return "False" if the text explicitly requires "Canadian experience," "Canadian work experience," or "local experience." Return "True" if not.
        5. Vacancy Status Disclosure: Return True indicating if this is an existing vacancy or a future pool (for example: "Active vacancy," "Talent pool", "Future opportunity"). If not or not specified, return "False".
        6. The probability that the job description was written by generative AI.

        Output Format Example:
        ["$20.00 hourly", False, "Humans are used to screen", "False", True, 0.3]
        ["$20.00-$25.00 hourly", False, "Humans are used to screen", "False", False, 0.2]
        ["$50,000-$60,000 yearly", "True", "AI is used to screen resumes", "False", "False", 0.6]

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
    job_parser = Parse(api_key="")
    x = job_parser.run("""Accountant Position Available

Midtown Accounting Firm is seeking an experienced Accountant to join our team. This position offers excellent growth opportunities and a supportive work environment.

Job Duties:
- Prepare financial statements and reports
- Handle tax preparation for individuals and small businesses
- Maintain general ledger and reconcile accounts
- Assist with audits and compliance
- Provide financial advice to clients

Requirements:
- CPA designation or in progress
- Minimum 3 years of accounting experience in Canada
- Proficiency with accounting software (QuickBooks, Sage)
- Strong attention to detail
- Excellent organizational skills

Compensation: $55,000 - $110,000 per year

Benefits:
- Health insurance
- 3 weeks vacation
- Professional development support
- Flexible work arrangements

Please send your resume and cover letter to careers@midtownaccounting.ca. We review applications on a rolling basis.

""")
    print([x])
