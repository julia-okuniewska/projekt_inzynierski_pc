import numpy as np
import matplotlib.pyplot as plt


def read_records(path: str):
    with open(path, 'r') as f:
        lines = f.readlines()

    stripped = [str.strip(x) for x in lines]
    data = [str.split(x, " ") for x in stripped]
    data = list(map(lambda x: [int(float(y)) for y in x], data))

    data = np.asarray(data)
    one_actuator = data[np.where(data[:, 1] == 0)]

    return one_actuator


pid = read_records("with_PID.txt")
nopid = read_records("without_PID.txt")
# speed_4500 = read_records("tse_4500_0tocenter.txt")

pid[:, 0] = pid[:, 0] - pid[32, 0]
pid[0:32, :] = 0

nopid[:, 0] = nopid[:, 0] - nopid[27, 0]
nopid[0:27, :] = 0


# nopid = nopid/10
# nopid[:, 0] = nopid[:, 0] - nopid[53, 0]
# nopid[:, 0] = nopid[:, 0] - nopid[53, 0]
plt.plot(nopid[:82, 0], nopid[:82, 2], '-x', label='Bez sterownika PID')
plt.plot(pid[:87, 0], pid[:87, 2], '-x', label='Z sterownikiem PID')
plt.plot([0, 1000], [1000, 1000],  '--g')

plt.xlabel('Czas [ms]', fontsize=20)
plt.ylabel('Położenie aktuatora', fontsize=20)

plt.tick_params(labelsize=16)

plt.legend(prop={'size': 20})
plt.show()
