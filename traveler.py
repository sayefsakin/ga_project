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

    root.mainloop()
