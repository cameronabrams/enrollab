import random
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd


class Student:
    def __init__(self, id, score, preference):
        self.id = id
        self.score = score
        self.preference = preference  # 0 = cost-driven, 1 = prestige-driven
        self.efc = random.randint(0, 60)  # Expected Family Contribution ($k)
        self.applications = []
        self.offers = []
        self.aid_offers = {}  # university.id -> aid amount
        self.enrolled_at = None

    def choose(self):
        if not self.offers:
            return
        def utility(u):
            aid = self.aid_offers.get(u.id, 0)
            net_cost = u.cost - aid
            return u.prestige * self.preference - net_cost * (1 - self.preference)
        self.offers.sort(key=utility,reverse=True)
        for idx,offer in enumerate(self.offers):
            if offer.enroll(self):
                self.enrolled_at = offer
                self.rank_of_enroll=idx
                break

class University:
    def __init__(self, id, prestige, cost, capacity):
        self.id = id
        self.prestige = prestige
        self.cost = cost
        self.capacity = capacity
        self.applicants = []
        self.num_applicants=0
        self.enrolled_students = []

    def receive_application(self, student):
        self.applicants.append(student)
        self.num_applicants+=1

    def admit(self):
        self.applicants.sort(key=lambda s: s.score, reverse=True)
        base = 1.0
        scale = 5.0
        overbook_factor = base + scale * (1 - self.prestige)
        admits = self.applicants[:int(self.capacity * overbook_factor)]
        for student in admits:
            need = max(0, self.cost - student.efc)
            merit_factor = (student.score - 800) / 400  # roughly -0.5 to +0.75
            merit_aid = self.cost * merit_factor

            # Allow above-need merit aid if low prestige
            merit_boost = self.cost * 0.25 * (1-self.prestige)  # offer up to 25% more than need
            max_aid = min(self.cost, int(need + merit_boost))

            aid = max(0, min(max_aid, int(merit_aid)))
            student.aid_offers[self.id] = aid
            student.offers.append(self)
        self.applicants.clear()


    def enroll(self, student):
        if len(self.enrolled_students) < self.capacity:
            self.enrolled_students.append(student)
            return True
        return False

# --- Setup ---
NUM_STUDENTS = 700
NUM_UNIVERSITIES = 15

students = [Student(
    id=f"S{i}",
    score=random.gauss(1000, 100),
    preference=random.uniform(0, 1)
) for i in range(NUM_STUDENTS)]

universities = [University(
    id=f"U{i}",
    prestige=random.uniform(0.5, 1.0),
    cost=random.randint(10, 60),
    capacity=random.randint(10, 100)
) for i in range(NUM_UNIVERSITIES)]

# --- Simulation Step 1: Apply ---
for student in students:
# Rank universities by individual utility
    ranked_unis = sorted(universities, key=lambda u: u.prestige * student.preference - u.cost * (1 - student.preference), reverse=True)
    # student.applications = ranked_unis[:min(10, len(ranked_unis))]
    # student.applications = random.sample(ranked_unis[:len(ranked_unis)//2], k=min(5, len(ranked_unis)//2))
    student.applications = random.sample(universities, k=min(5, len(universities)))

    for uni in student.applications:
        uni.receive_application(student)

# --- Step 2: Admit ---
for uni in universities:
    uni.admit()

# --- Step 3: Choose ---
for student in students:
    student.choose()

# --- Report Results ---
print("\nEnrollment Results (with average aid and yield):")
results=dict(capacity=[],prestige=[],num_applicants=[],avg_aid=[],offers_made=[],num_enrollments=[],yield_rate=[])
for uni in universities:
    aid_amounts = [s.aid_offers.get(uni.id, 0) for s in students if uni.id in s.aid_offers]
    results['avg_aid'].append(sum(aid_amounts) / len(aid_amounts) if aid_amounts else 0)
    results['offers_made'].append(len([s for s in students if uni in s.offers]))
    results['yield_rate'].append(100 * len(uni.enrolled_students) / results['offers_made'][-1] if results['offers_made'][-1] > 0 else 0)
    results['capacity'].append(uni.capacity)
    results['num_applicants'].append(uni.num_applicants)
    results['prestige'].append(uni.prestige)
    results['num_enrollments'].append(len(uni.enrolled_students))
rd=pd.DataFrame(results)
rd.sort_values(by='prestige',inplace=True)

print(rd.to_string())
print(f'Total capacity: {rd["capacity"].sum():d}')
unmatched = len([s for s in students if not s.enrolled_at])
print(f"\nUnmatched students: {unmatched}")

eranks=[s.rank_of_enroll for s in students if ]

cmap=matplotlib.colormaps['tab10']
uni_ids = [uni.id for uni in universities]
color_map = {uni.id: cmap(uni.prestige) for uni in universities}


# Gather data
x_need = []
y_aid = []
colors = []

for student in students:
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
plt.title("Financial Aid vs Student Need (Colored by University)")
plt.grid(True)
plt.tight_layout()

# Add legend
handles = [plt.Line2D([0], [0], marker='o', color='w', label=uid,
                      markerfacecolor=color_map[uid], markersize=8, markeredgecolor='k')
           for uid in uni_ids]
plt.legend(handles=handles, title="University", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.savefig('fig.png',bbox_inches='tight')