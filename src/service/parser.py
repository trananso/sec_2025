from google import genai
import ast



def convert_hourly_to_yearly(rate, hours_per_week=40, weeks_per_year=52):  # default to be fully time conversion
    return rate * hours_per_week * weeks_per_year


def parse_salary(salary: str):
    if salary == "None":
        return None
    # convert to full time
    salary = salary.replace("$", "")
    salary_time = "hourly" if "hourly" in salary else "yearly"
    salary = salary.replace(salary_time, "").strip()

    if "-" in salary:  # it is a range
        original_salary_min, original_salary_max = map(float, salary.split("-"))

        if salary_time == "hourly":
            yearly_salary_min, yearly_salary_max = convert_hourly_to_yearly(
                original_salary_min), convert_hourly_to_yearly(original_salary_max)
        else:
            yearly_salary_min, yearly_salary_max = original_salary_min, original_salary_max
        return [salary_time, original_salary_min, original_salary_max, yearly_salary_min, yearly_salary_max]

    else:
        original_salary = float(salary)
        if salary_time == "hourly":
            yearly_salary = convert_hourly_to_yearly(original_salary)
        else:
            yearly_salary = original_salary
        return [salary_time, original_salary, yearly_salary]

def analyze(parsed_job_specs: list):
    salary, AI_disclosure, AI_disclosure_description, not_require_canadian_experience, vacancy_disclosure, probability_of_AI = parsed_job_specs

    if salary != "None":
        salary = parse_salary(salary)
        salary_time = salary[0]
        salary = salary[1:]
        if len(salary) == 4:  # if the salary is a range
            original_min, original_max, yearly_min, yearly_max = salary
        else:
            original_min, original_max, yearly_min, yearly_max = salary[0], None, salary[1], None

        if original_max is not None:
            salary_exceeded = (yearly_max - yearly_min) > 50000
        else:
            salary_exceeded = False
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

        1. Salary String: Extract the exact salary or salary range or hourly rate mentioned. You MUST use [yearly, hourly] to denote the salary. If no salary is present, return "None".
        2. AI Disclosure Found: Return "True" if the text explicitly mentions using Artificial Intelligence (AI) for screening, selection, or evaluation. Return "False" if not mentioned.
        3. AI Conditions: If step 2 is True, quote the specific sentence describing how AI is used. If #2 is False, return "None".
        4. Does NOT Require Canadian Experience: Return "False" if the text explicitly requires "Canadian experience," "Canadian work experience," or "local experience." Return "True" if not.
        5. Vacancy Status Disclosure: Return True or False indicating if this is an existing vacancy or a future pool (for example: "Active vacancy," "Talent pool", "Future opportunity"). If not specified, return "None".
        6. The probability that the job description was written by generative AI.

        Output Format Example:
        ["$20.00 hourly", False, "Humans are used to screen", "False", True, 0.3]
        ["$20.00-$25.00 hourly", False, "Humans are used to screen", "False", False, 0.2]
        ["$50,000-$60,000 yearly", "True", "AI is used to screen resumes", "False", "None", 0.6]

        Your Response:
        """
        self.client = genai.Client(api_key=api_key)

    def parse_response(self, response):
        return ast.literal_eval(response)

    # def convert_types(self, parsed_job_specs):
    #     for i in range(len(parsed_job_specs)):
    #         print(parsed_job_specs[i])
    #         if isinstance(parsed_job_specs, str) and parsed_job_specs[i].lower() == "none":
    #             parsed_job_specs[i] = None
    #     return parsed_job_specs

    def run(self, job_desc):
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=self.prompt.replace("JOB_POSTING", job_desc))
        parsed_job_specs = self.parse_response(response.text)
        # parsed_job_specs = self.convert_types(parsed_job_specs)
        # print([parsed_job_specs[0]])
        # raise ValueError
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
    x = job_parser.run("""
Job Title: Software Developer
Company: VelocityTech Solutions
Location: Toronto, ON (Hybrid: Flexible schedule)
Employment Type: Full-time, Permanent

Overview:
VelocityTech Solutions is a fast-growing technology company looking for a talented Software Developer to join our dynamic team. We work with cutting-edge technologies and the latest frameworks to deliver innovative solutions for our clients. This is an exciting opportunity to work on challenging projects and grow your career in a fast-paced environment.

Key Responsibilities:
- Develop and maintain web applications using modern JavaScript frameworks
- Write clean, efficient, and well-documented code
- Collaborate with cross-functional teams including designers, product managers, and other developers
- Participate in code reviews and contribute to technical discussions
- Debug and troubleshoot issues in production environments
- Stay current with emerging technologies and industry best practices
- Work on multiple projects simultaneously and meet tight deadlines

Requirements (Must-Have):
- Bachelor's degree in Computer Science, Software Engineering, or related field
- 2-4 years of professional software development experience
- Strong proficiency in JavaScript, HTML, and CSS
- Experience with at least one modern framework (React, Vue, or Angular)
- Knowledge of version control systems (Git)
- Strong problem-solving abilities and attention to detail
- Ability to work independently and as part of a team
- Excellent communication skills

Nice-to-Have:
- Experience with Node.js and backend development
- Familiarity with cloud platforms (AWS, Azure, or GCP)
- Understanding of database design and SQL
- Experience with Agile/Scrum methodologies
- Knowledge of testing frameworks (Jest, Mocha, etc.)

Work Environment:
- Flexible work hours with option for remote work
- Collaborative team environment
- Opportunities for professional growth and learning
- Fast-paced startup culture with exciting challenges

Benefits:
- Competitive compensation package
- Health and dental benefits after probation period
- Flexible vacation policy
- Professional development opportunities
- Stock options available for high performers

Application Process:
We are actively seeking candidates for this position. Please submit your resume and a brief cover letter outlining your relevant experience. Selected candidates will be contacted for an initial phone screening, followed by technical interviews.

Our hiring process is designed to identify the best talent efficiently. We review applications on a rolling basis and encourage early submissions.
""")
    print([x])
