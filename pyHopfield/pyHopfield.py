from tkinter import*
import tkinter.ttk as ttk    #ovveride tkinter widgets
import numpy as np
import sys
import random


class HopfieldNetwork:
    
    def __init__(self,figures,mat_size,max_idle_it = 500):
        #weighting coefficient matrix
        self.neurons_num = mat_size[0] * mat_size[1]
        self.W = np.zeros(self.neurons_num * self.neurons_num, dtype = np.int8).reshape((self.neurons_num,self.neurons_num))
        self.figures = figures
        #max number of the idle iterations
        self.max_idle_it = max_idle_it
        self.train_all()

    def train(self,figure):
        for i in range(self.neurons_num):
            for j in range(i):
                if i == j:
                    self.W[i][j] = 0
                else:
                    self.W[i][j] += figure[i] * figure[j]
                    self.W[j][i] = self.W[i][j] 

    def train_all(self):
        for fig in self.figures:
            self.train(fig)

    def isReferenceFigure(self,fig):
        for ref_fig in self.figures:
            if  np.array_equal(ref_fig,fig):
                return True
        return False

    def recognize(self,figure):
        fig = figure.copy()
        i = 0
        iddle_it = 0
        is_corrected = False
        #until it coincides with the known figure
        while not self.isReferenceFigure(fig):
            is_corrected = self.correctRandNeuron(fig)
            i += 1
            if is_corrected:
                iddle_it = 0
            else:
                iddle_it += 1
            if iddle_it == self.max_idle_it:
                return (fig,False,i)
        return (fig,True,i)


    @staticmethod
    def signum(a,b):
        return int(a > b) - int(a < b) 

    def correctRandNeuron(self,fig):
        #randomly select a neuron to update it value
        r = random.randrange(0,self.neurons_num)
        net = 0
        for i in range(self.neurons_num):
            net += fig[i] * self.W[i][r]
        s = HopfieldNetwork.signum(net,0)
        #change the current neuron
        if s != fig[r]:
            fig[r] = s
            return True
        return False

class App(Frame):

    def __init__(self, master,cmd_args,mat_size = (10,10),cell_size = (20,20),pix_active_val = 1):
        super().__init__(master)
        self.pack(fill = BOTH,expand=1)
        self.cmd_args = cmd_args
        #pixels to show one neuron
        self.cell_size = cell_size
        self.mat_size = mat_size
        #we take picture matrix as vector
        self.vect_size = self.mat_size[0] * self.mat_size[1]
        self.pix_active_val = pix_active_val
        self.im_size = (self.cell_size[0] * self.mat_size[0],self.cell_size[1] * self.mat_size[1])
        self.figures = []
        self.readFiguresFromFile(cmd_args,self.mat_size)
        self.hopfield = HopfieldNetwork(self.figures,self.mat_size)
        #set current figure accordingly to initial combobox state
        self.cur_fig = self.figures[0].copy()
        self.__createWidgets();
        #set init combobox value
        self.combo_figures.set(self.combo_figures['values'][0])
        self.showVector(self.canvas_left,self.figures[0],self.pix_active_val,self.cell_size)
        

    def readFiguresFromFile(self,cmd_args,mat_size):
        self.figures = [ np.fromfile(fileName,dtype=np.int8,count=-1,sep=',') for fileName in cmd_args]


    def showVector(self,canvas,fig,pix_active_val = 1,cell_size = (10,10),cell_color = 'black',cell_reduce = 1):
        #clear canvas
        canvas.delete('all')
        x = 0
        y = 0
        row_beg = 0
        for i in range(self.mat_size[0]):
            x = cell_size[0] * i
            for j in range(self.mat_size[1]):
                y = cell_size[1] * j
                row_beg = j * self.mat_size[1]
                if fig[row_beg + i] == pix_active_val:
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
        recogn_fig,success,n_iters = self.hopfield.recognize(self.cur_fig)
        self.showVector(self.canvas_right, recogn_fig,1,self.cell_size)

    def spoil_event(self):
        self.getCopyToCurFigure()
        #get spoil percent
        spoil_perc = self.scale_interf.get()
        self.spoilFigure(self.cur_fig,spoil_perc)
        #show current figure
        self.showVector(self.canvas_left, self.cur_fig,1,self.cell_size)

    def spoilFigure(self,fig,spoil_perc,value = 1,inv_value = -1):
        #(x,y) coordinates of the figure to spoil it (invert values)
        fig_coord = set()
        while len(fig_coord) < spoil_perc:
            fig_coord.add( random.randint(0,self.vect_size - 1))
        #then invert this pixels
        for coord in fig_coord:
            if fig[coord] == value:
                fig[coord] = inv_value
            else:
                fig[coord] = value

    def __del__(self):
       self.destroy();
       self.quit();
    
    

if __name__ == '__main__':
    #initialize random generator from sys time
    random.seed()
    root = Tk()
    app = App(root,sys.argv[1:])
    app.mainloop()
    
    
    
   
    
    

