import tkinter as tk

root = tk.Tk()
    # root is now a window.
root.title("Title!")
    # root's minimized name is "Title!"
root.geometry("500x500+100+100") 
    # Makes a 500x500 window, with the top left corner
    # at screen position (100,100)

screen_height = root.winfo_screenheight();
screen_width = root.winfo_screenwidth();
print("height = ",screen_height)
print("width = ",screen_width)
print(f"some text, and {screen_height}")

root.resizable(True,False)
    # root can now be resized horizontally, but not vertically
root.iconbitmap("./fun/Excl.ico")
    # root now has this picture as it's icon.

message = tk.Label(root, text="Hello World!")
    # message is now some text associated with the window root.
message.pack()
    # message is now shown on root.

root.mainloop()

#IT'S ALIVE!!!!! 
#Why did Spyder not work!?!??! 
#Why didn't I know VSCode was on here!?!??!?
#What's going to break this time!?!??!?!?
#IT"S ALIVE AGAIN!!!!!!