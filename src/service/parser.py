from google import genai

client = genai.Client(api_key="AIzaSyDUDbRyUbKbnGvung0BCN6sQdk-yu2E9f4")

prompt = """
You are a Compliance Parsing Engine for Ontario Employment Standards. Your job is to analyze the provided job posting text and extract five specific data points into a Python list format.

Job Description:
{JOB_POSTING}

Instructions:
Analyze the text and return ONLY a single Python list containing the following elements in this exact order. Do not wrap the output in markdown or code blocks. Just return the raw list string.

1. Salary String: Extract the exact salary range or hourly rate mentioned. If no salary is present, return "None".
2. AI Disclosure Found: Return "True" if the text explicitly mentions using Artificial Intelligence (AI) for screening, selection, or evaluation. Return "False" if not mentioned.
3. AI Conditions: If #2 is True, quote the specific sentence describing how AI is used. If #2 is False, return "None".
4. Does NOT Require Canadian Experience: Return "False" if the text explicitly requires "Canadian experience," "Canadian work experience," or "local experience." Return "True" if not.
5. Vacancy Status Disclosure: Return the specific phrase indicating if this is an existing vacancy or a future pool (e.g., "Active vacancy," "Talent pool," "Future opportunity"). If not specified, return "None".

Output Format Example:
["$50,000-$60,000", "True", "AI is used to screen resumes", "False", "None"]

Your Response:
"""

prompt = prompt.replace("JOB_POSTING", """Job Title: Senior Data Analyst
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

print(prompt)
# raise ValueError
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt)

format = {
    "salary": {
        "salaryExceeded": bool,
        "yearlyMin": float,
        "yearlyMax": float,
        "originalMin": float,
        "originalMax": float,
    },
    "aiDisclosure": bool,
    "aiDisclosureDescription": str,
    "canadianExperienceNotRequired": bool,
    "vacancyDisclosure": bool,
    "aiUseProbability":{
        "probability": float,
        "reasoning": str
    }
}


def analyze(job_specs: list):
    salary, AI_disclosure,
    # returns in this format:
    # {
    # salaryRangeExceeded: true,
    # aiDisclosureIncluded: true,
    # canadianExperienceNotRequired: false,
    # vacancyDisclosure: true,
    # }


print(response.text)  # output is often markdown

# format: [salary, AI/automatic screening disclosure, Canadian experience, vacancy disclosure, comments and reasoning]
# None for missing
# salary can be a range of 2 floats or 1 number
# if it is a range [100-2000]
