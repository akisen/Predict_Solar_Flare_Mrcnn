import matplotlib.pyplot as plt
import matplotlib.patches as pat
def show_map(map):
    plt.figure(1)
    ax = plt.subplot(1,1,1)
    # ax.set_ylim([0,len(padded_map)])
    ax.imshow(map)
    plt.show()
def compare_map(map1,map2):
    plt.figure(1)
    ax = plt.subplot(1,2,1)
    ay = plt.subplot(1,2,2)
    ax.imshow(map1)
    ay.imshow(map2)
    plt.show()
def show_polygon(polygon):
    plt.figure(1)
    ax = plt.subplot(1,1,1)
    plt.xlim(0,4000)
    plt.ylim(0,4000)
    p = pat.Polygon(polygon)
    ax.add_patch(p)
    plt.show()