# WXML-Affine-Geometry
This repository contains code for working with the affine space F_3^n. The provided GUI, affineGUI.py is currently the only file that's mine. The other files were written by Jaron Wang, who was a WXML researcher at UW in Fall 2019. Running affineGUI brings up a GUI that allows the user to see a visual representation of F_3^n for any n from 1 to 6. It also allows the user to view subsets of F_3^n by either typing them in in binary or by manually editing the state by checking checkboxes corresponding to desired points.

Goals: 
1) Generate all 2-caps for F_3^4. So far we can generate 2-caps but only ones that include three specific points, which greatly limits how many we can find.
2) Find all valid affine transformations in F_3^4
3) Use results from goals 1 and 2 to determine whether or not all 2-caps in F_3^4 are equivalent.
