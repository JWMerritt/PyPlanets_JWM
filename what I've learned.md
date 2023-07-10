So, here are some things:

To change labels: ChangeableText = tkinter.StringVar(value = "Text"); Label(textvariable = ChangeableText). 
Labels &c don't have some "Label.change()" function.

StringVar() *requires* a master, and if you've started a root Tk() window, it defaults to that Tk() object as it's master.

Button's "command" option should have the name of the function, without the () afterwards.

Object.__dict__ will list the sub-objects under Object

Using "self." a bunch inside of class methods is a fun way to declutter the code, since you don't need to include a bunch of arguments into a method that updates something about the object.... but it's also a great way to lose track of what arguments need what. Do I need to update A before updating B, or does B not even use A? Having the arguments makes it clear what the function actually uses, and what it changes. 

~~def function(self, args) Should not have an argument "self" unless you're actually using self.attr inside of the method. "self" should not necessarily be the first argument in a method.~~
Actually, make sure to initialize an instance of the class. That's what was wrong: in tkinter_ball, I was using classes as functions, and passing PhysEngine=Phys_Linear instead of PhysEngine=Phys_Linear(), so there was no 'self'.