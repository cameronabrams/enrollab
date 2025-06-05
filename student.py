# Author: Cameron F. Abrams <cfa22@drexel.edu>
import numpy as np

class Student:  # base student class
    def __init__(self, id, score, efc):
        self.id = id
        self.score = score
        self.efc = efc  # Expected Family Contribution ($k)
        self.applications = []
        self.offers = []
        self.aid_offers = {}  # university.id -> aid amount
        self.enrolled_at = None

    def expected_net_cost(self,u):
        est_aid = 0
        return u.cost - est_aid

    def app_utility(self,u):
        prestige_weight = self.score / 1600
        cost_weight = 1 / (self.efc + 1)
        return prestige_weight * u.prestige - cost_weight * self.expected_net_cost(u)
    
    def apply(self, u):
        if u not in self.applications:
            self.applications.append(u)
            u.applicants.append(self)
            u.num_applicants += 1
            return True
        return False

    def choose_utility(self, u):
        aid = self.aid_offers.get(u.id, 0)
        net_cost = np.clip(u.cost - aid,0, None)  # Ensure non-negative net cost
        prestige_weight = self.score / 1600  # normalize score to [0,1]
        cost_weight = 1 / (self.efc + 1)  # more cost sensitivity if low EFC
        return prestige_weight * u.prestige - cost_weight * net_cost
    
    def choose(self):
        if not self.offers:
            return
        best = max(self.offers, key=self.choose_utility)
        if best.enroll(self):
            self.enrolled_at = best

