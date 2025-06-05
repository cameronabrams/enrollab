# Author: Cameron F. Abrams <cfa22@drexel.edu>

class Simulation:
    def __init__(self, num_students=1000, num_publics=20, num_privates=5, num_states=1):
        self.students = []
        self.universities = []
        self.num_students = num_students
        self.num_universities = num_publics + num_privates
        self.frac_privates = num_privates / self.num_universities
        self.num_states = num_states

    def setup_students(self):
        for i in range(self.num_students):
            base_score = np.clip(random.gauss(1000, 100), 0, 1600)  # Score between 0 and 1600
            efc = np.clip(random.gauss(30, 30), 0, 100)  # Expected Family Contribution ($k)
            # Slight downward adjustment to score based on higher efc
            adjusted_score = base_score + (efc - 30) * random.uniform(0.6, 1.0)
            adjusted_score = int(max(600, min(1600, adjusted_score)))  # clamp to reasonable range
            student = Student(id=f"S{i}", score=adjusted_score, efc=efc, noise=random.uniform(0.05, 0.15))
            self.students.append(student)
        print(f"Created {len(self.students)} students with scores ranging from "
              f"{min(s.score for s in self.students)} to {max(s.score for s in self.students)} and EFCs from "
              f"{min(s.efc for s in self.students)} to {max(s.efc for s in self.students)}")

    def setup_universities(self):
        for i in range(self.num_universities):
            prestige = random.uniform(0.5, 1.0) 
            x=random.uniform(0,1)
            pop='public'
            cost = np.clip(int(random.gauss(80, 10),60,100))
            if x<self.frac_privates:
                cost = np.clip(int(random.gauss(80, 10),60,100))
                pop='private'
