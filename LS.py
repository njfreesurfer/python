'''
L System in Python

This program is adapted from Bernie Pope's python script and rewritten by Tony Jiang (nic.cns.ucla@gmail.com). 
It now uses a string manipulation mechanism (multiple replace in parallel model) instead of compling and defining 
dynamic functions on the fly(which is an excellent idea but would be less straightforward for others to follow).

To run the program, run
  python LS.py

Author: Tony Jiang: https://github.com/njfreesurfer/
License: Unrestricted as long as you keep this header.

#########
L-System(L for Language or Lindenmayer)
########
L-System is closely linked to creating fractals,a term coined by Benoit Mandelbrot. The core of an L-System is the 
rules which are later translated to commands to direct a "turtle" to move. For example,
Initial String: X
Rule 1: X -> F[+X][-X]FX
Rule 2: F -> FF

Each symbols encodes certain action. For example,
F = Forward; 
+ = Turn Right at an angle of XX
- = Turn Left  at an angle of xx
[ = Remember this location and orientation
] = Return to most recent remembered location and keep the same orientation
X = Do nothing
...

For each interation, each target symbol (X or F) will be replaced based on the rules parallely (we replace the symbols 
in one shot so the F symbols added when we replace X will not be replaced again by Rule 2. This is important!! 
In this implementatoin, we call this expansion of the command. After we finish all the iterations, we end up with a very
long string arrays. Then this string array will be translated to "turtle" actions defined by a dictionary. 

We defined a LS class to implement the L-System, to initiate a LS object, we need to pass some required argument
myLS= LS(rules,left_angle,right_angle,fwd_distance,init_command,init_rule,max_iteration,output)
in which
    rules: an example is rules=['X-> F-[[X]+X]+F[+FX]-X','F -> FF']
    left_angle: this defines the angle when turn left
    right_angle: this defines the angle when turn right
    fwd_distance: this defines the distance the turtle moves forward
    init_command: this gives the turtle some initial command before moving in fractal pattern
    init_rule:  we need to give a first command when n=0 . this sometimes is just a single letter X or F. 
    max_iteration: the number of maximal iteration, we usually use a number around 10. you do not want to go over 20 in most cases.
    output: a file name which saves the drawing in .eps format. 
Actions can be redefined other than the ones defiend in basic_actions after you create an instance of LS class. For example
we can change the angle when turnning right or add an action for A command
myL=LS(rules,90,90,2,init,'B',12,'output') 
myL.actions['A'] = lambda _ : forward(0.2)# move forward 0.2 
myL.actions['-'] = lambda _ : right(60)#turn 60 degree to the right
myL.actions['+'] = lambda _ : left(60)#turn 60 degree to the left
'''
import sys
# import the turtle graphics library
try:
    import turtle
    from turtle import *
except ImportError:
    print("This program requires the turtle graphics library.")
    print("Unfortunately Python cannot find that library on your computer.")
    print("See the documentation at: http://docs.python.org/library/turtle.html")
    sys.exit(-1)
from collections import deque
import re
def multiple_replace(text,dict): 
  """ Replace in 'text' all occurences of any key in the given
  dictionary by its corresponding value.  Returns the new tring.""" 
  # Create a regular expression  from the dictionary keys
  regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
  # For each match, look-up corresponding value in dictionary
  return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text)         
def expand_command(n,command,dict):
    if n==0:
        return command
    else:
        return expand_command(n-1,multiple_replace(command,dict),dict)
def makeDictionary(rules):
    mydict={}
    for rule in rules:
        splitRule = rule.split('->')
        if len(splitRule) != 2:
            raise Exception("badly formed L-System rule: " + quote(str(rule)))
        name = splitRule[0].strip()
        body = splitRule[1].strip()
        if len(name) != 1 or len(body) == 0:
            raise Exception("badly formed L-System rule: " + quote(str(rule)))
        mydict.update({name:body})
    return mydict    
# Configuration of graphics window
def initDisp124Glay(drawColour="black"):
    title ("TJ's L System")
    setup()
    reset()
    degrees()
    color(drawColour)
    # Try to make the animation of drawing reasonably fast.
    tracer(10,0) # Only draw every 50th update, set delay to zero.
    hideturtle() # don't draw the turtle; increase drawing speed.

def initPosition(mover=lambda width, height : (0, -height/2)):
    height = window_height()
    width = window_width()
    up() 
    goto (mover (width, height))
    down()
class LS(object):
    # initiator
    def __init__ (self, rules,left_angle,right_angle,fwd_distance,init_command,init_rule,max_iteration,output):
        #some constants
        #self.wn = turtle.Screen()      # Creates a playground for turtles
        self.actions=basic_actions(left_angle,right_angle,fwd_distance)
        self.init_command=init
        self.stack=deque()
        self.commands=expand_command(max_iteration,init_rule,makeDictionary(rules))
        self.output=output
    
    def push(self):
        orient=heading()
        pos=position()
        self.stack.append((orient,pos))
    def pop(self):
        if len(self.stack)==0:
            raise Exception('Attempt to pop empty stack')
        (orient,pos)=self.stack.pop()
        up()
        goto(pos)
        setheading(orient)
        down()
    def draw(self):
        #everything should be ready to go if this is called. 
        initDisplay()
        if self.init_command!=None: self.init_command()
        #intepret command strings to actions and execute
        def action_fun(token):
            return self.actions.get(token,lambda _: None)(self)
        #self.statck=deque()
        map(action_fun,self.commands)   
        #update()
        ts=turtle.getscreen()
        ts.getcanvas().postscript(file=self.output+".eps")
def basic_actions (left_angle, right_angle, fwd_distance):
   return { '-': lambda _ : left(left_angle)
          , '+': lambda _ : right(right_angle)
          , 'F': lambda _ : forward(fwd_distance)
          , '[': lambda obj : obj.push()
          , ']': lambda obj : obj.pop()
          }

def init():
    #initPosition()
    initPosition(lambda width, height : (-3*width/8, -height/4))
    left(90)
rules=  ['X -> F-[[FX]+X]+F[+FX]-X','F->FF']
rules=  ['X -> F-[[X]+X]+F[+FX]-X','F->FF']
rules = [ 'X -> XFYFX+F+YFXFY-F-XFYFX'
       , 'Y -> YFXFY-F-XFYFX+F+YFXFY'
       , 'F -> F' ]
rules=['A -> B-A-B', 'B -> A+B+A']

myL=LS(rules,90,90,2,init,'B',12,'output') 
myL.actions['A'] = lambda _ : forward(0.2)
myL.actions['B'] = lambda _ : forward(0.2)
myL.actions['-'] = lambda _ : right(60)
myL.actions['+'] = lambda _ : left(60)
myL.draw()
