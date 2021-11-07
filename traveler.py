import sys
import math
from tkinter import *
import random


if __name__ == "__main__":
    problem = 5
    if len(sys.argv) > 1:
        problem = int(sys.argv[1])

    # =========================================
    root = Tk()
    root.title("Segments")
    root.geometry(str(YSIZE)+'x'+str(YSIZE)) #("800x800")

    canvas = Canvas(root, width=YSIZE, height=YSIZE, bg='#FFF', highlightbackground="#999")
    # canvas.bind("<Button-1>", find_intersections_wrapper)
    canvas.grid(row=0, column=0)

    HP = generateRandomDataset(problem)
    drawHalfPlanes(HP)
    sp = halfplane_intersect(HP)
    drawSegments(sp, 'blue')
    for ss in sp:
        print('from time', ss[0][0], 'to', ss[1][0], ' leading train:', ss[2])
    root.mainloop()