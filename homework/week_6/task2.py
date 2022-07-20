"""

TASK 2

Write a base class to represent a student. Below is a starter code.
Feel free to add any more new features to your class.
As a minimum a student has a name and age and a unique ID.

Create a new subclass from student to represent a concrete student doing a specialization, for example:
Software Student and Data Science student.

"""


class Student:

    def __init__(self, id, first_name, last_name, age, email, phone, department):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.email = email
        self.phone = phone
        self.department = department

        self.subjects = dict()

    def enrol(self, *subjects):
        for subject in subjects:
            self.subjects.update({subject: None})

    def disenrol(self, subject):
        self.subjects.pop(subject)

    def set_grade(self, subject, grade):
        if subject in self.subjects:
            self.subjects.update({subject: grade})
        else:
            print("Student " + self.id + " is not enrolled in " + subject)

    def get_subjects(self):
        return self.subjects.keys()

    def get_overall_mark(self):
        grade_sum = 0
        grade_count = 0

        for grade in self.subjects.values():
            if grade is not None:
                grade_sum += grade
                grade_count += 1

        return round(grade_sum / grade_count, 2) if grade_count > 0 else None


class SoftwareStudent(Student):

    def __init__(self, id, first_name, last_name, age, email, phone, department, coding_languages, personal_website):
        super().__init__(id, first_name, last_name, age, email, phone, department)
        self.coding_languages = coding_languages
        self.personal_website = personal_website

    def get_favourite_language(self):
        return self.coding_languages[0] if len(self.coding_languages) > 0 else None


class ArcheologyStudent(Student):
    def __init__(self, id, first_name, last_name, age, email, phone, department, sites_worked_on, dinosaurs_discovered):
        super().__init__(id, first_name, last_name, age, email, phone, department)
        self.sites_worked_on = sites_worked_on
        self.dinosaurs_discovered = dinosaurs_discovered

    def get_number_sites_worked_on(self):
        return len(self.sites_worked_on)


def find_top_student(*students):
    highest_grade = 0
    best_student = None
    for student in students:
        if student.get_overall_mark() > highest_grade:
            highest_grade = student.get_overall_mark()
            best_student = student

    return best_student


if __name__ == '__main__':
    course_data_structures = "Data Structures"
    course_algorithm_design = "Algorithm Design"
    course_web_development = "Web Development"
    course_egyptian_culture = "Egyptian Culture"
    course_sumerian_culture = "Sumerian Culture"

    student1 = SoftwareStudent(1234, "Mark", "Summerfield", 24, "mark.summerfield@yahoo.com", 555 - 555 - 555,
                               "Engineering", ["Java", "C++"], "mark.cfg.com")
    student1.enrol(course_data_structures, course_algorithm_design)
    student1.set_grade(course_data_structures, 45)
    student1.set_grade(course_algorithm_design, 55)

    student2 = SoftwareStudent(9676, "Mike", "McGrath", 23, "mike.mcgrath@yahoo.com", 123 - 123 - 123, "Engineering",
                               ["Java", "Python"], "mike.cfg.com")
    student2.enrol(course_data_structures, course_web_development, course_algorithm_design)
    student2.set_grade(course_data_structures, 75)
    student2.set_grade(course_algorithm_design, 85)

    student3 = ArcheologyStudent(9276, "Raquel", "Lopez", 25, "raquel.lopez@yahoo.com", 127 - 183 - 193, "Archeology",
                                 ["Giza Pyramids", "Valley of Kings"], 3)
    student3.enrol(course_egyptian_culture, course_sumerian_culture)
    student3.set_grade(course_egyptian_culture, 75)
    student3.set_grade(course_sumerian_culture, 85)

    student4 = SoftwareStudent(9076, "Andreea", "Gunter", 22, "andreea.gunter@yahoo.com", 327 - 183 - 193,
                               "Engineering", ["Ruby", "C++", "Go"], "andreea.cfg.com")
    student4.enrol(course_data_structures, course_web_development)
    student4.set_grade(course_data_structures, 45)
    student4.set_grade(course_web_development, 35)

    student5 = ArcheologyStudent(9676, "Suzie", "Armour", 25, "suzie.armour@yahoo.com", 120 - 783 - 113, "Archeology",
                                 ["Iran", "Syria"], 7)
    student5.enrol(course_egyptian_culture, course_sumerian_culture)
    student5.set_grade(course_egyptian_culture, 95)
    student5.set_grade(course_sumerian_culture, 45)

    top_software_student = find_top_student(student1, student2, student4)
    top_archeology_student = find_top_student(student3, student5)

    print(
        f"The top software engineering student is {top_software_student.first_name} {top_software_student.last_name} and their favourite language is {top_software_student.get_favourite_language()}.")
    print(
        f"The top archeology student is {top_archeology_student.first_name} {top_archeology_student.last_name}. They have been on {top_archeology_student.get_number_sites_worked_on()} archaeological sites and found {top_archeology_student.dinosaurs_discovered} dinosaurs.")
