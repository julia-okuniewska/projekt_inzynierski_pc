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


speed_700 = read_records("tse_700_0tocenter.txt")
speed_4500 = read_records("tse_4500_0tocenter.txt")


plt.plot(speed_700[:, 0], speed_700[:, 2])
plt.plot(speed_4500[:, 0], speed_4500[:, 2])
plt.show()
