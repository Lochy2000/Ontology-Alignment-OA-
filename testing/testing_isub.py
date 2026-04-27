from isub import isub
from difflib import SequenceMatcher

# isub here helps improve the matches score and thus the threshold can be set to higher
# but the false posotives also go up

pairs = [
    ("chairman", "chair"),
    ("paper abstract", "abstract"),
    ("subject area", "topic"),
    ("preference", "review preference"),
    ("conference chair", "conference part"),
    ("rejection", "presentation"),
    ("author", "regular author"),
    ("co author", "contribution co author"),
    ("document", "conference document"),
    ("email", "has an email"),
]

print(f"  {'String 1':30s} {'String 2':30s} {'SequenceM':>10s} {'ISub':>10s}")
print(f"  {'-'*30} {'-'*30} {'-'*10} {'-'*10}")
for s1, s2 in pairs:
    seq = SequenceMatcher(None, s1, s2).ratio()
    isub_score = isub(s1, s2)
    print(f"  {s1:30s} {s2:30s} {seq:10.3f} {isub_score:10.3f}")