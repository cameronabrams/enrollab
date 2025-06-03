from itertools import product
import random
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt 
import numpy as np
class Student:
    def __init__(self, id, score, efc, noise):
        self.id = id
        self.score = score
        self.efc = efc  # Expected Family Contribution ($k)
        self.noise = noise  # Noise factor for utility calculation
        base_apps = 7.5 + (self.efc - 30) * 0.05 - (self.score - 1000) * 0.002
        self.num_apps = int(np.clip(random.gauss(base_apps, 1), 5, 10))
        self.applications = []
        self.offers = []
        self.aid_offers = {}  # university.id -> aid amount
        self.enrolled_at = None

    def expected_net_cost(self,u):
        est_aid = min(u.cost, max(0, (self.score - 800) / 400 * u.cost))
        return u.cost - est_aid

    def app_utility(self,u):
        prestige_weight = self.score / 1600
        cost_weight = 1 / (self.efc + 1)
        noise = random.gauss(0, self.noise)
        return prestige_weight * u.prestige - cost_weight * self.expected_net_cost(u) + noise
    
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

    def receive_application(self, student):
        self.applicants.append(student)
        self.num_applicants += 1

    def admit(self):
        self.applicants.sort(key=lambda s: s.score, reverse=True)
        overbook_factor = 1.5
        admits = self.applicants[:int(self.capacity * overbook_factor)]
        for student in admits:
            # Offer merit-based aid: scaled by how strong the score is
            merit_factor = (student.score - 800) / 400  # range roughly -0.5 to +0.75
            need = max(0, self.cost - student.efc)
            merit_aid = self.cost * merit_factor
            aid = max(0, min(self.cost, int(min(need, merit_aid))))
            student.aid_offers[self.id] = aid
            student.offers.append(self)
        self.applicants.clear()

    def enroll(self, student):
        if len(self.enrolled_students) < self.capacity:
            self.enrolled_students.append(student)
            return True
        return False


class Simulation:
    def __init__(self, num_students, num_universities):
        self.students = []
        self.universities = []
        self.num_students = num_students
        self.num_universities = num_universities
        self.setup_students()
        self.setup_universities()
    def setup_students(self):
        for i in range(self.num_students):
            base_score = np.clip(random.gauss(1000, 100), 0, 1600)  # Score between 0 and 1600
            efc = np.clip(random.gauss(30, 30), 0, 100)  # Expected Family Contribution ($k)
            # Slight downward adjustment to score based on higher efc
            adjusted_score = base_score + (efc - 30) * random.uniform(0.6, 1.0)
            adjusted_score = max(600, min(1600, adjusted_score))  # clamp to reasonable range
            student = Student(id=f"S{i}", score=adjusted_score, efc=efc, noise=random.uniform(0.05, 0.15))
            self.students.append(student)
    def setup_universities(self):
        cost_references = np.linspace(10, 80, int(np.sqrt(self.num_universities)))
        prestige_references = np.linspace(0.5, 1.0, int(np.sqrt(self.num_universities)))
        for i, (c, p) in enumerate(product(cost_references, prestige_references)):
            capacity = int(np.clip(200 - 50 * (c - 40) / 40 + random.gauss(0, 30), 50, 300))
            uni = University(id=f"U{i}", prestige=p, cost=int(c), capacity=capacity)
            self.universities.append(uni)
    def apply(self):
        for student in self.students:
            ranked_unis = sorted(self.universities, key=student.app_utility, reverse=True)
            student.applications = ranked_unis[:min(student.num_apps, len(ranked_unis))]
            for uni in student.applications:
                uni.receive_application(student)
    def admit(self):
        for uni in self.universities:
            uni.admit()
    def choose(self):
        for student in self.students:
            student.choose()
    def run(self):
        self.apply()
        self.admit()
        self.choose()
    def collect(self):
        uni_data = []
        for uni in self.universities:
            utility_values = [s.app_utility(uni) for s in self.students]
            offer_amounts = [s.aid_offers.get(uni.id, 0) for s in self.students if uni.id in s.aid_offers]
            uni.avg_app_utility = sum(utility_values) / len(utility_values)
            uni_data.append({
                'university': uni.id,
                'prestige': uni.prestige,
                'cost': uni.cost,
                'capacity': uni.capacity,
                'avg_app_utility': uni.avg_app_utility,
                'avg_aid_offered': sum(offer_amounts) / len(offer_amounts) if offer_amounts else 0,
                'offers_made': len([s for s in self.students if uni in s.offers]),
                'num_applicants': uni.num_applicants,
                'num_enrollments': len(uni.enrolled_students),
                'yield_rate': 100 * len(uni.enrolled_students) / uni.num_applicants if uni.num_applicants > 0 else 0
            })
            df=pd.DataFrame(uni_data)
            df['norm_avg_app_utility'] = (df['avg_app_utility'] - df['avg_app_utility'].min()) / \
                                        (df['avg_app_utility'].max() - df['avg_app_utility'].min())
        self.uni_data=df

    def student_plots(self):
        efcs = [s.efc for s in self.students]
        scores = [s.score for s in self.students]
        num_poor= len([s for s in self.students if s.efc==0])
        print(f'Number of students with EFC=0: {num_poor} ({num_poor/self.num_students:.2%})')
        plt.figure(figsize=(8, 6))
        plt.scatter(efcs, scores, alpha=0.6, edgecolors='k')
        plt.xlabel("Expected Family Contribution (EFC) [$k]")
        plt.ylabel("Student Score")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('student_population.png')
        cmap=matplotlib.colormaps['tab10']
        self.universities.sort(key=lambda u: u.prestige, reverse=True)
        uni_ids = [uni.id for uni in self.universities]
        color_map = {uni.id: cmap(uni.prestige) for uni in self.universities}

        # Gather data
        x_need = []
        y_aid = []
        colors = []

        for student in self.students:
            if student.enrolled_at:
                uni = student.enrolled_at
                need = max(0, uni.cost - student.efc)
                aid = student.aid_offers.get(uni.id, 0)
                x_need.append(need)
                y_aid.append(aid)
                colors.append(color_map[uni.id])

        # Plot
        plt.figure(figsize=(8, 6))
        plt.scatter(x_need, y_aid, c=colors, alpha=0.7, edgecolors='k')
        plt.xlabel("Financial Need ($k, Tuition - EFC)")
        plt.ylabel("Financial Aid Awarded ($k)")
        plt.title("Financial Aid Awarded vs Student Need (Colored by University, ordered by Prestige)")
        plt.grid(True)
        plt.tight_layout()

        # Add legend
        handles = [plt.Line2D([0], [0], marker='o', color='w', label=uid,
                    markerfacecolor=color_map[uid], markersize=8, markeredgecolor='k')
                    for uid in uni_ids]
        plt.legend(handles=handles, title="University", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.savefig('aid_v_need_offers.png',bbox_inches='tight')
        plt.close('all')

    def university_plots(self):
        area_scale = 2000
        bubble_area = area_scale * (self.uni_data['capacity'] / self.uni_data['capacity'].max())
        color_norm = (self.uni_data['avg_app_utility'] - self.uni_data['avg_app_utility'].min()) / \
                        (self.uni_data['avg_app_utility'].max() - self.uni_data['avg_app_utility'].min())
        plt.figure(figsize=(10, 7))
        scatter = plt.scatter(
            self.uni_data['cost'],
            self.uni_data['prestige'],
            s=bubble_area,
            c=color_norm,
            cmap='plasma',
            alpha=0.8,
            edgecolors='k'
        )
        for _, row in self.uni_data.iterrows():
            plt.text(row['cost'], row['prestige'], row['university'], fontsize=8, ha='center', va='center')
        cbar = plt.colorbar(scatter)
        cbar.set_label("Normalized Avg Application Utility")
        plt.xlabel("Cost ($k)")
        plt.ylabel("Prestige")
        plt.title("University Prestige vs Cost\nBubble Area = Capacity, Color = Application Utility")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("bubble_prestige_cost_capacity_utility.png")
        area_scale = 2000  # Adjust to taste
        bubble_area = area_scale * (self.uni_data['num_enrollments'] / self.uni_data['num_enrollments'].max())

        # Normalize average utility for colormap
        color_norm = (self.uni_data['avg_aid_offered'] - self.uni_data['avg_aid_offered'].min()) / \
                    (self.uni_data['avg_aid_offered'].max() - self.uni_data['avg_aid_offered'].min())

        # Plot
        plt.figure(figsize=(10, 7))
        scatter = plt.scatter(
            self.uni_data['num_applicants'],
            self.uni_data['offers_made'],
            s=bubble_area,
            c=color_norm,
            cmap='plasma',
            alpha=0.8,
            edgecolors='k'
        )

        # Annotate points with university IDs
        for _, row in self.uni_data.iterrows():
            plt.text(row['num_applicants'], row['offers_made'], row['university'], fontsize=8, ha='center', va='center')

        # Add colorbar for utility
        cbar = plt.colorbar(scatter)
        cbar.set_label("Normalized Avg Aid Awarded")

        # Labels and layout
        plt.xlabel("Number of Applicants")
        plt.ylabel("Number of Offers Made")
        plt.title("Offers Made vs Applicants\nBubble Area = Enrollments, Color = Avg Aid Awarded")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("bubble_applicants_offers_enrollments_aid.png")

# --- Setup ---
NUM_STUDENTS = 4000
NUM_UNIVERSITIES = 20
simulation = Simulation(NUM_STUDENTS, NUM_UNIVERSITIES)
simulation.setup_universities()
simulation.setup_students()
simulation.run()
simulation.collect()

# --- Plotting ---
simulation.student_plots() 
simulation.university_plots()