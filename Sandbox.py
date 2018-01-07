import math

for i, j in zip(range(10), range(2, 20, 2)):
    print("{} {}".format(i,j))
    if i > 6:
        break

print("Done")