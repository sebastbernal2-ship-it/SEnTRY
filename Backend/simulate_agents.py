import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "api"))
from manipulation_scorer import ManipulationScorer

scorer = ManipulationScorer()

print("Simulating Benign Agent: AGT-BENIGN")
# 3 proposals, avg size 0.5, 100% success
for _ in range(3):
    scorer.log_proposal("AGT-BENIGN", 0.5, True)

print("Simulating Suspicious Agent: AGT-SUSPECT")
# 15 proposals, avg size 4.0, 40% success
for i in range(15):
    scorer.log_proposal("AGT-SUSPECT", 4.0 + (i%3)*0.5, i%5 < 2) 

print("Simulating Malicious Spam Agent: AGT-SPAM")
# 40 proposals, avg size 15.0, 20% success
for i in range(40):
    scorer.log_proposal("AGT-SPAM", 15.0 + (i%5)*2.0, i%10 < 2)

print("\n--- Final Agent Scores ---")
for agent in scorer.get_all_agents():
    print(agent)
