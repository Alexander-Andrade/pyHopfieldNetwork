from tkinter import*
import tkinter.ttk as ttk    #ovveride tkinter widgets
import numpy as np
import sys
import random

class App(Frame):

    def __init__(self, master,cmd_args,mat_size = (10,10),cell_size = (20,20),pix_active_val = 1):
        super().__init__(master)
        self.pack(fill = BOTH,expand=1)
        self.cmd_args = cmd_args
        #pixels to show one neuron
        self.cell_size = cell_size
        self.mat_size = mat_size
        self.pix_active_val = pix_active_val
        self.im_size = (self.cell_size[0] * self.mat_size[0],self.cell_size[1] * self.mat_size[1])
        self.figures = []
        self.readFiguresFromFile(cmd_args,self.mat_size)
        #set current figure accordingly to initial combobox state
        self.cur_fig = self.figures[0].copy()
        self.__createWidgets();
        #set init combobox value
        self.combo_figures.set(self.combo_figures['values'][0])
        self.showFigure(self.canvas_left,self.figures[0],self.pix_active_val,self.cell_size)
        

    def readFiguresFromFile(self,cmd_args,mat_size):
        self.figures = [ np.fromfile(fileName,dtype=np.int8,count=-1,sep=',').reshape(mat_size) for fileName in cmd_args]


    def showFigure(self,canvas,fig,pix_active_val = 1,cell_size = (10,10),cell_color = 'black',cell_reduce = 1):
        #clear canvas
        canvas.delete('all')
        mat_size = fig.shape
        x = 0
        y = 0
        for i in range(mat_size[0]):
            x = cell_size[0] * i
            for j in range(mat_size[1]):
                y = cell_size[1] * j
                if fig[j][i] == pix_active_val:
                    canvas.create_rectangle(x + cell_reduce,y + cell_reduce,x + cell_size[0] - cell_reduce,y + cell_size[1] - cell_reduce,fill=cell_color)
    
    def findFigureIndex(self):
       return list(self.combo_figures['values']).index(self.combo_figures.get())                       

    def getCopyToCurFigure(self):
        #copy figure deeeply from figure_list to current handled figure 
        fig_ind = self.findFigureIndex()
        #get current figure as copy of one of figures
        self.cur_fig = self.figures[fig_ind].copy() 

    def combo_figure_changed_event(self,event):
        pass        

    def __createWidgets(self):
       canv_backgr_color = 'ivory'
       #left canvas - spoiled figure
       self.canvas_frame = ttk.Frame(self,width = self.im_size[0] << 2,height = self.im_size[1] << 2)
       self.canvas_left = Canvas(self.canvas_frame,bg= canv_backgr_color ,width = self.im_size[0], height = self.im_size[1])
       self.canvas_left.pack(side = 'left',fill = BOTH,expand=1)
       #right canvas - recognized figure
       self.canvas_right = Canvas(self.canvas_frame,bg= canv_backgr_color ,width = self.im_size[0], height = self.im_size[1])
       self.canvas_right.pack(side = 'right',fill = BOTH,expand=1)
       self.canvas_frame.pack(side = 'top',fill = BOTH,expand=1)
       #combobox with figures to select
       self.comb_track_frame = ttk.Frame(self)
       self.combo_figures = ttk.Combobox(self.comb_track_frame,values = [cmd_arg.split('.')[0] for cmd_arg in self.cmd_args ])
       self.combo_figures.pack(side = 'top',fill = BOTH,expand=1)
       #!!!!!!!!!bind events only after there binding
       self.combo_figures.bind('<<ComboboxSelected>>',self.combo_figure_changed_event)
       #trackbar with interference values
       self.scale_interf = Scale(self.comb_track_frame, orient = HORIZONTAL,from_ = 0, to = 100,tickinterval = 20)
       self.scale_interf.pack(side = 'bottom',fill = BOTH,expand=1)
       self.comb_track_frame.pack(fill = BOTH,expand=1 )
       #buttons
       self.buttons_frame = ttk.Frame(self)
       self.button_spoil = ttk.Button(self.buttons_frame,text = 'spoil', command = self.spoil_event)
       self.button_spoil.pack(side = 'left',fill = BOTH,expand=1)
       self.button_recognize = ttk.Button(self.buttons_frame,text = 'recognize',command = self.recognize_event)
       self.button_recognize.pack(side = 'right',fill = BOTH,expand=1)
       self.buttons_frame.pack(side = 'bottom',fill = BOTH,expand=1)


    def recognize_event(self):
        pass

    def spoil_event(self):
        self.getCopyToCurFigure()
        #get spoil percent
        spoil_perc = self.scale_interf.get()
        self.spoilFigure(self.cur_fig,spoil_perc)
        #show current figure
        self.showFigure(self.canvas_left, self.cur_fig,1,self.cell_size)

    def spoilFigure(self,fig,spoil_perc,value = 1,inv_value = -1):
        #(x,y) coordinates of the figure to spoil it (invert values)
        fig_coord = set()
        while len(fig_coord) < spoil_perc:
            fig_coord.add(( random.randint(0,self.mat_size[0] - 1),random.randint(0,self.mat_size[1] - 1)))
        #then invert this pixels
        for coord in fig_coord:
            if fig[coord[0]][coord[1]] == value:
                fig[coord[0]][coord[1]] = inv_value
            else:
                fig[coord[0]][coord[1]] = value

    def __del__(self):
       self.destroy();
       self.quit();

if __name__ == '__main__':
    #initialize random generator from sys time
    random.seed()
    root = Tk()
    app = App(root,sys.argv[1:])
    app.mainloop()
   
    
    

