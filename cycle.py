# Author: Cameron F. Abrams <cfa22@drexel.edu>

class Cycle:
    def __init__(self, num):
        self.simulation = simulation
        self.students = simulation.students
        self.universities = simulation.universities

    def run(self):
        # Reset universities for a new cycle
        for u in self.universities:
            u.next_cycle()

        # Students apply to universities
        for student in self.students:
            for university in self.universities:
                student.apply(university)

        # Universities admit students based on their criteria
        for university in self.universities:
            university.admit()

        # Students choose the best offer they received
        for student in self.students:
            student.choose()