"""Independent checks based on printed values and frequency conservation."""
import math
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent
def check(exe, args, size, bound, bins):
    output = subprocess.check_output([str(exe), *args], text=True)
    lines = output.splitlines()
    values = [float(s) for s in lines[0].split()]
    assert len(values) == size and all(0 <= x <= bound for x in values)
    mean, low, high = [float(lines[i].split(':')[1]) for i in (1, 2, 3)]
    assert math.isclose(mean, math.fsum(values)/size, rel_tol=2e-5, abs_tol=2e-6)
    assert low == min(values) and high == max(values)
    rows = lines[5:]
    counts = [sum(row[4*i:4*i+3] == '***' for row in rows) for i in range(bins)]
    assert sum(counts) == size, (counts, size)
    expected = [0]*bins
    for x in values:
        index = 0 if high == low else min(int((x-low)/(high-low)*bins), bins-1)
        expected[index] += 1
    assert counts == expected, (counts, expected)
    return counts

rv = root/'RandomVector'
counts = check(rv/'random_vector', [], 20, 1, 5)
print('Default data / statistics / histogram PASS:', counts)
for mode, size, bound, bins in [('constant',8,0,5),('single',1,1,5),('scaled',8,7.5,5),('many',100,1,200)]:
    check(rv/'edge_cases', [mode], size, bound, bins)
    print(mode, 'PASS')
print(subprocess.check_output([str(rv/'edge_cases'), 'invalid'], text=True).strip())
warmup = subprocess.check_output([str(root/'warmup_verify')], text=True)
for expected in ['Operators1: 2 1', 'Operators2: b', 'Reference1: 10 10', 'Pointer2: 1764', 'Pointer3: 0', 'Reference4: 0', 'FloatToInt: 3', 'UnsignedChar: 255', 'Condition: 0']:
    assert expected in warmup, expected
print('Warm-up executable checks PASS')
print('ALL_CHECKS_PASSED')
