# Author: Cameron F. Abrams <cfa22@drexel.edu>

class University:
    def __init__(self, id, prestige, cost, capacity):
        self.id = id
        self.prestige = prestige
        self.cost = cost
        self.capacity = capacity
        self.applicants = []
        self.enrolled_students = []
        self.num_applicants=0
    
    def reset(self):
        self.applicants = []
        self.enrolled_students = []
        self.num_applicants=0

    def admit(self): # baseline university behavior, only admit based on capacity, score, and aid is only need-based
        self.applicants.sort(key=lambda s: s.score, reverse=True)
        admits = self.applicants[:int(self.capacity)]
        for student in admits:
            # Offer merit-based aid: scaled by how strong the score is
            # merit_factor = (student.score - 800) / 400  # range roughly -0.5 to +0.75
            need = max(0, self.cost - student.efc)
            # merit_aid = self.cost * merit_factor
            aid = max(0, min(self.cost, need)) #int(min(need, merit_aid))))
            student.aid_offers[self.id] = aid
            student.offers.append(self)
        self.applicants.clear()

    def enroll(self, student):
        if len(self.enrolled_students) < self.capacity:
            self.enrolled_students.append(student)
            return True
        return False