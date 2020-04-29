import tkinter  
def  call(event):  
    print(event.keysym)  #打印按下的键值  
  
win=tkinter.Tk()  
frame=tkinter.Frame(win,width=200,height=200)   
frame.bind("<Key>",call) #触发的函数  
frame.focus_set()  #必须获取焦点  
frame.pack()  
win.mainloop() 