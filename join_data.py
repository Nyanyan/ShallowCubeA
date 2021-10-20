import sys

phase = '1'

data = ''
for file in sys.argv[1:]:
    with open('learn_data/phase' + phase + '/' + file + '.txt', 'r') as f:
        data += f.read()

with open('learn_data/phase' + phase + '/all_data.txt', 'w') as f:
    f.write(data)

print(len(data.splitlines()))