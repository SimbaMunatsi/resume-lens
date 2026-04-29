from app.tools.skill_normalizer import normalize_skills

test_skills = [
    "communication skills",
    "team player",
    "nursng",
    "patient-care",
    "brick laying",
    "financial reports",
    "sales",
    "teaching students",
    "fast api",
]

result = normalize_skills(test_skills)

print("INPUT:")
print(test_skills)

print("\nOUTPUT:")
print(result)