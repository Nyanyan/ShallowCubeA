import sys

data = ''
for file in sys.argv[1:]:
    with open('learn_data/phase1/' + file + '.txt', 'r') as f:
        data += f.read()

with open('learn_data/phase1/all_data.txt', 'w') as f:
    f.write(data)

print(len(data.splitlines()))