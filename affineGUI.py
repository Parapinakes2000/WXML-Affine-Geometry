"""This is a GUI that provides a visualization of the geometric interpretation of the card
game SET as well as generalizations of the game.

Avery Milandin"""

from tkinter import *

root = Tk()
root.title("SET and Affine Geometry")
w, h = root.winfo_screenwidth(), root.winfo_screenheight()-100
root.geometry("%dx%d+0+0" % (w, h))

# Defines the frame and canvas that will hold the visualization of the affine space
C = Canvas(root)
C.grid(row=1, column=0, columnspan=99)
F = LabelFrame(C, text="Affine Space")
F.grid(row=1, column=0)


# Allows user to manually edit the state by clicking checkboxes of which points to include
# in the state. Also constructs "Done" button for the user to click to update the state
# to the edited state
def manual(dim, state):
    global editState
    global doneBtn
    if 'doneBtn' in globals():  # user may click manual edit button multiple times before clicking
                               # Done, which would construct this button multiple times
        doneBtn.destroy()
    editState = []
    buildF(dim, state, manEdit=TRUE)
    doneBtn = Button(root, text="DONE", padx=30, pady=30,
                     command=lambda: applyEdit(dim))
    doneBtn.grid(row=2, column=0)


# After the user clicks "Done", delete the "Done" button and display the state without checkboxes.
# Also update the state text displayed in the stateText box
def applyEdit(dim):
    global editState
    global doneBtn
    newState = ""
    for cbox in editState:
        newState = newState + str(cbox.check.get())
    stateText.delete(0, END)
    stateText.insert(0, newState)
    doneBtn.destroy()
    buildF(dim, newState)


# Constructs and displays the visualization of the subset of F_3 ^dim with the state
# and dimension provided by the user
def buildF(dim, state, manEdit=FALSE):
    global F, C, colors
    F.destroy()
    C.destroy()
    C = Canvas(root)
    C.grid(row=1, column=0, columnspan=999)
    F = LabelFrame(C, text="Affine Space")
    F.grid(row=0, column=0, columnspan=999)
    stateIter = stateIterator(state, dim)
    colors = ["blue", "red", "green", "cyan", "black", "orange"]
    if dim != 6:
        F0 = build(F, dim, stateIter, manEdit)
        F0.grid(row=0, column=0)
    else:
        F0 = build(F, dim, stateIter, manEdit)
        F0[0].grid(row=0, column=0, columnspan=99)
        currPage = IntVar()
        currPage.set(0)
        pageBtn1 = Button(F, text="<", command=lambda: pageNext(
            currPage, F0, next=FALSE))
        pageBtn1.grid(row=1, column=0)
        pageBtn2 = Button(F, text=">", command=lambda: pageNext(
            currPage, F0, next=TRUE))
        pageBtn2.grid(row=1, column=1)
        pageLabel = Label(F, text="Page "+str(currPage.get()+1)+" of 3")
        pageLabel.grid(row=2, column=0)


# Generates the space given by the buildF method
def build(frame, dim, stateIter, manEdit):
    global colors
    if dim == 0:
        activated = stateIter.__next__()
        if activated == "1":
            boxText = "X"
            box = Label(frame, text=boxText, padx=9, pady=6)
        else:
            boxText = ""
            box = Label(frame, text=boxText, padx=13, pady=6)
        if manEdit:
            box = Label(frame, text=boxText, padx=4, pady=6)
            frame.check = IntVar(value=int(activated))
            manEdit = Checkbutton(
                frame, variable=frame.check, foreground="blue")
            manEdit.grid(row=0, column=1)
            editState.append(frame)
        return box
    if dim != 6:
        F0 = newFrame(frame, colors[dim-1], dim, manEdit)
        F1, F2, F3 = triFrame(F0, colors[dim-1], dim-1, stateIter, manEdit)
        return F0
    else:
        F1, F2, F3 = triFrame(frame, colors[dim-1], dim-1, stateIter, manEdit)
        return [F1, F2, F3]


# Helper method for build
def triFrame(frame, color, dimension, stateIter, manEdit):
    F1 = newFrame(frame, color, dimension, manEdit)
    F2 = newFrame(frame, color, dimension, manEdit)
    F3 = newFrame(frame, color, dimension, manEdit)
    first = build(F1, dimension, stateIter, manEdit)
    second = build(F2, dimension, stateIter, manEdit)
    third = build(F3, dimension, stateIter, manEdit)
    first.grid(row=0, column=0)
    second.grid(row=0, column=0)
    third.grid(row=0, column=0)
    if dimension != 5:
        if (dimension % 2 == 0):
            F1.grid(row=0, column=0)
            F2.grid(row=0, column=1)
            F3.grid(row=0, column=2)
        else:
            F1.grid(row=0, column=0)
            F2.grid(row=1, column=0)
            F3.grid(row=2, column=0)
    return F1, F2, F3


# Used by build to construct a new fram with given color and dimension
def newFrame(frame, color, dimension, manEdit=FALSE):
    if dimension < 3:
        thickness = dimension
    else:
        thickness = 2
    new = LabelFrame(frame, highlightbackground=color,
                     highlightcolor=color, highlightthickness=thickness+1, bd=0)
    if manEdit:
        new = LabelFrame(frame, highlightbackground=color,
                         highlightcolor=color, highlightthickness=1, bd=0)
    return new


# Used by the page right and page left buttons that show up when viewing
# 6 dimensions. It updates the display based on which page the user goes to.
def pageNext(currPage, F0, next):
    if not ((currPage.get() == 2 and next) or (currPage.get() == 0 and not next)):
        F0[currPage.get()].grid_forget()
        if next:
            currPage.set(currPage.get()+1)
        else:
            currPage.set(currPage.get()-1)
        F0[currPage.get()].grid(row=0, column=0, columnspan=99)
        pageLabel = Label(F, text="Page "+str(currPage.get()+1)+" of 3")
        pageLabel.grid(row=2, column=0)


# returns an iterator to iterate over the provided state. If the state has too
# few characters, the missing characters are treated as zeroes.
def stateIterator(state, dimension):
    if len(state) < 3**dimension:
        state = state + "0" * (3**dimension - len(state))
    return state.__iter__()


# Here the user can set the number of dimensions to any integer between 1 and 6 and also
# provide a state to display.
dimension = IntVar()
dimension.set(4)
dimLabel = Label(root, text="Desired dimension: ")
chooseDim = OptionMenu(root, dimension, "1", "2", "3", "4", "5", "6")
update = Button(root, text="Update",
                command=lambda: buildF(dimension.get(), stateText.get()))
manualEdit = Button(root, text="Manually Edit State",
                    command=lambda: manual(dimension.get(), stateText.get()))
stateLabel = Label(root, text="Enter a state: ")
stateText = Entry(root, width=50)
dimLabel.grid(row=0, column=0)
chooseDim.grid(row=0, column=1)
stateLabel.grid(row=0, column=2)
stateText.grid(row=0, column=3)
update.grid(row=0, column=4)
manualEdit.grid(row=0, column=5)
exitBtn = Button(root, text="Close", command=root.quit).grid(row=10, column=0)

root.mainloop()
