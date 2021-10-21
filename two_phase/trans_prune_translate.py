

def data_flatten(raw_data):
    raw_data = raw_data.splitlines()
    data = []
    for line in raw_data:
        for elem in line.split(','):
            data.append(elem)
    return data

def translate(file):
    with open('normal_alg/' + file + '.csv', 'r') as f:
        raw_data = f.read()
    data = data_flatten(raw_data)
    with open('param/' + file + '.txt', 'w') as f:
        for elem in data:
            f.write(elem + '\n')


translate('trans_co')
translate('trans_cp')
translate('trans_eo')
translate('trans_ep_phase0')
translate('trans_ep_phase1_1')
translate('trans_ep_phase1_2')
translate('prun_phase0_co_ep')
translate('prun_phase0_eo_ep')
translate('prun_phase1_cp_ep')
translate('prun_phase1_ep_ep')