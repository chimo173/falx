
import json
from pprint import pprint

#meta = json.load(open('leetcode_data/metadata.json', 'r'))
#task_res = 'falx-new.json'
task_res = 'falx-original.json'

results = json.load(open(task_res, 'r'))
#pprint(results)
i = 1
for res in sorted(results):
  #print(i, res, round(results[res]["time"],2) if results[res]["prog"] not in ["[]", "RE"] else -1, results[res]["prog"])
  print(round(results[res]["time"], 2) if results[res]["prog"] not in ["[]", "RE"] else "NA")

  i = i + 1

  #pass
# res = json.load(open('bruteforce_results.json', 'r'))
#
# for name in res:
#   result = res[name]
#   print(result["id"], result["result"]["status_msg"])