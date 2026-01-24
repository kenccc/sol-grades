from grades.models import Subject, Grades

def save_grades(user, parsed_grades):
    for g in parsed_grades:
        subject, _ = Subject.objects.get_or_create(name=g["subject"])

        Grades.objects.create(
            user=user,
            subject=subject,
            grade=g["grade"],
            weight=g["weight"],
            date=g["date"]
        )
