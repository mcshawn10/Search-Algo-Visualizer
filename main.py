     
import pygame
import time
import os
import sys
from queue import PriorityQueue
import random
import math
pygame.init()

WHITE = (255,255,255)
GRAY = (192,192,192)
BLACK = (0,0,0)
YELLOW = (255,255,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,255,255)
DARK_BLUE = (0,0,128)
FPS = 60
pygame.display.set_caption("Algorithm Visualizer")
main_font = pygame.font.SysFont("cambria", 50)
small_font = pygame.font.SysFont("cambria", 25)


class Cell:
    counter = 0
    def __init__(self, color, row, col):
        self.size = 20
        self.color = color
        self.row = row 
        self.col = col
        self.g = 0
        self.h = 0
        self.f = self.g + self.h
        Cell.counter += 1

    def __lt__(self, other):
        return self.counter < other.counter

    def set_color(self, color):
        self.color = color

    def display_cell(self, screen):
        
        pygame.draw.rect(screen, self.color, (self.col * self.size + 2, self.row * self.size +202, 18, 18))
        pygame.display.flip()


class Button:
    def __init__(self, ip, x_pos, y_pos, width, height, screen):
        self.x_pos = x_pos
        self.y_pos = y_pos 
        self.width = width
        self.height = height
        self.screen = screen
        self.input = ip
        self.text = main_font.render(self.input, True, DARK_BLUE)

        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))
        
        
        self.box = pygame.draw.rect(self.screen, WHITE, (self.x_pos, self.y_pos, self.width, self.height))
    
    def update(self):
        self.screen.blit(self.text, self.box)
        
        pygame.display.flip()

    def click(self, x, y, func):
        if x in range(self.box.left, self.box.right) and y in range(self.box.top, self.box.bottom):
            func()
    
    def change_color(self, x, y):
        if x in range(self.box.left, self.box.right) and y in range(self.box.top, self.box.bottom):
            self.text = main_font.render(self.input, True, GREEN)
        else:
            self.text = main_font.render(self.input, True, DARK_BLUE)


class Board:

    def __init__(self):
        self.width = 1200
        self.height = 700
        self.rows = 25
        self.cols = 60
        self.cell_size = 20
        self.window = pygame.display.set_mode((self.width, self.height))
        self.blocks = [[Cell(WHITE, i, j) for j in range(self.cols)] for i in range(self.rows)]

        self.parent = [[Cell(WHITE, i, j) for j in range(self.cols)] for i in range(self.rows)]
        self.start = None
        self.goal = None
        self.found = False
        self.path = []


    def draw_board(self): # draws lines to the window
       
        self.window.fill(GRAY)
        for i in range(self.rows):
            for j in range(self.cols):                
                self.blocks[i][j].display_cell(self.window)

        for i in range(self.rows+1):
            thick = 2
            pygame.draw.line(self.window, BLACK, (0, 200 + i*self.cell_size), (1200, 200+i*self.cell_size), thick)

        for i in range(self.cols+1):
            thick = 2
            pygame.draw.line(self.window, BLACK, (i * self.cell_size, 200), (i * self.cell_size, 700), thick)

    def get_pos(self,pos):
        col, row = pos
        row = (row-200)//self.cell_size
        col = col//self.cell_size
        
        return row, col
    
    def set_start(self):
        r = random.randint(0, 24)
        c = random.randint(0, 59)
        self.blocks[r][c].set_color(RED)
        self.blocks[r][c].display_cell(self.window)

        self.start = self.blocks[r][c]
        pygame.display.flip()
    
    def set_goal(self):
        r = random.randint(0, 24)
        c = random.randint(0, 59)

        self.blocks[r][c].set_color(GREEN)
        self.blocks[r][c].display_cell(self.window)

        self.goal = self.blocks[r][c]
        pygame.display.flip()
    
    def draw_obstacles(self, r, c): #will change the cell color from white to black

        self.blocks[r][c].set_color(BLACK)
        self.blocks[r][c].display_cell(self.window)
        pygame.display.flip()

    def clear_board(self):
        for i in self.blocks:
            for j in i:
                j.color = WHITE
                j.display_cell(self.window)
        self.path.clear()
        pygame.display.update()


    def clear_search(self):

        for i in self.blocks:
            for j in i:
                if j.color == BLUE or j.color == YELLOW:
                    j.color = WHITE
                j.display_cell(self.window)

        self.path.clear()
        self.found = False
        self.parent = [[Cell(WHITE, i, j) for j in range(self.cols)] for i in range(self.rows)]
        pygame.display.update()

    def find_path(self):

        if self.found:
            p = self.goal

            while p != self.start:

                self.path.append(p)
                

                p = self.parent[p.row][p.col]
              
            self.path.reverse()
            

            for p in self.path:
                if p.color != RED and p.color != GREEN:
                    p.set_color(YELLOW)
                    p.display_cell(self.window)
            
        else:
            print("Path Not Found")

    def A_star(self): # will do the search and change the color of the searched cells
        
        def m_dist(current, end): # node to self.goal
            return abs(current.row - end.row) + abs(current.col - end.col)

        def e_dist(current, end):
            return math.sqrt(abs(current.row-end.row)**2 + abs(current.col-end.col)**2)

        found = False
        cells = self.blocks
        CLSD = []
        self.start.g = 0
        self.start.h = float('inf')
        self.start.f = self.start.h
        self.goal.h = 0

        OPEN = PriorityQueue()
        OPEN.put((m_dist(self.start,self.goal), 0, self.start))

        O_ls = []

        while not OPEN.empty():
            

            curr = OPEN.get()[2]  #  get the current node
            CLSD.append(curr)     #  add the current to the closed list so not to revisit it
            O_ls.append(curr)
            if curr == self.goal:   
                self.found = True     
                break
            
            else:

                children = []
                if 0 <= curr.row+1 <= 24:
                    children.append(cells[curr.row+1][curr.col])
                if 0 <= curr.row-1 <= 24:
                    children.append(cells[curr.row-1][curr.col])
                if 0 <= curr.col+1 <= 59:
                    children.append(cells[curr.row][curr.col+1])
                if 0 <= curr.col-1 <= 59:
                    children.append(cells[curr.row][curr.col-1])

                for child in children:  #  iterate through the neighboring nodes

                    if child.color == BLACK:
                        continue
                    

                    child.g = m_dist(child, self.goal)  #  calc the scores
                    child.h = m_dist(child, self.goal)
                    child.f = child.g + child.h
                    cost = curr.g + 1


                    if child in O_ls and cost < child.g:
                        
                        for item in OPEN.queue:

                            if item[2] == child:
                                
                                OPEN.queue.remove(item)
                        for child in O_ls:
                            O_ls.remove(child)
                        

                    elif child in CLSD and child.g < cost:  # determine if you should add to the queue
                        CLSD.remove(child)
                        
                    elif child not in CLSD and child not in O_ls:
                        child.g = cost
                        child.f = child.g + child.h
                        O_ls.append(child)
                        OPEN.put((child.h, child.g, child))

                        self.parent[child.row][child.col] = curr

                        if child.color != RED and child.color!= GREEN:
                            child.set_color(BLUE)
                            child.display_cell(self.window)
                 
        self.find_path()

    def Dijkstra(self):

        def m_dist(current, end): # node to self.goal
            return abs(current.row - end.row) + abs(current.col - end.col)

        OPEN = PriorityQueue()
        self.start.h = 0
        cells = self.blocks

        for i in cells:
            for j in i:
                if j != self.start:
                    j.h = float('inf')
                    

        OPEN.put((self.start.h, self.start))
        CLSD = []
        
        while not OPEN.empty():
            dist_curr, curr = OPEN.get()
            CLSD.append(curr)

            if curr == self.goal:
                self.found = True
                break

            children = []
            if 0 <= curr.row+1 <= 24:
                children.append(cells[curr.row+1][curr.col])
            if 0 <= curr.row-1 <= 24:
                children.append(cells[curr.row-1][curr.col])
            if 0 <= curr.col+1 <= 59:
                children.append(cells[curr.row][curr.col+1])
            if 0 <= curr.col-1 <= 59:
                children.append(cells[curr.row][curr.col-1])

            for child in children:
                if child.color == BLACK:
                    continue
                
                alt = dist_curr + m_dist(curr, child)

                if alt < child.h and child not in CLSD:
                    
                    child.h = alt
                    OPEN.put((child.h, child))
                    self.parent[child.row][child.col] = curr
                    if child == self.goal:
                        self.found = True
                        break
                    if child.color != RED and child.color != GREEN:
                        child.color = BLUE
                        child.display_cell(self.window)
        self.find_path()

    def BFS(self):
        cells = self.blocks
        Q = [self.start]
        visited = [] # dont check these ones again
        
        while Q:
            curr = Q.pop(0)
            if curr == self.goal:
                self.found = True
                break

            elif curr not in visited:
                visited.append(curr)
                children = [] # neighbors of the current nodes
                if 0 <= curr.row+1 <= 24:
                    children.append(cells[curr.row+1][curr.col])
                if 0 <= curr.row-1 <= 24:
                    children.append(cells[curr.row-1][curr.col])
                if 0 <= curr.col+1 <= 59:
                    children.append(cells[curr.row][curr.col+1])
                if 0 <= curr.col-1 <= 59:
                    children.append(cells[curr.row][curr.col-1])

                for child in children:

                    if child.color == BLACK or child in visited:
                        continue

                    elif child == self.goal:
                        
                        self.parent[child.row][child.col] = curr
                        
                        Q.clear()
                        
                   
                    elif child.color != RED and child.color != GREEN:
                        self.parent[child.row][child.col] = curr
                        Q.append(child)
                        child.set_color(BLUE)
                        child.display_cell(self.window)

            else: continue
               
            
        self.find_path() 

    def GBFS(self):
        def m_dist(current, end): # node to self.goal
            return abs(current.row - end.row) + abs(current.col - end.col)

        def e_dist(current, end):
            return math.sqrt(abs(current.row-end.row)**2 + abs(current.col-end.col)**2)

        found = False
        cells = self.blocks
        CLSD = []
       
        self.start.h = e_dist(self.start,self.goal)
        
        self.goal.h = 0

        OPEN = PriorityQueue()
        OPEN.put((self.start.h, self.start))

        O_ls = []

        while not OPEN.empty():
            

            curr = OPEN.get()[1]  #  get the current node
            CLSD.append(curr)     #  add the current to the closed list so not to revisit it
            O_ls.append(curr)
            if curr == self.goal:   
                self.found = True     
                break
            
            else:

                children = []
                if 0 <= curr.row+1 <= 24:
                    children.append(cells[curr.row+1][curr.col])
                if 0 <= curr.row-1 <= 24:
                    children.append(cells[curr.row-1][curr.col])
                if 0 <= curr.col+1 <= 59:
                    children.append(cells[curr.row][curr.col+1])
                if 0 <= curr.col-1 <= 59:
                    children.append(cells[curr.row][curr.col-1])

                for child in children:  #  iterate through the neighboring nodes

                    if child.color == BLACK:
                        continue
                    

                  
                    elif child not in CLSD and child not in O_ls:
                        child.h = e_dist(child, self.goal)
                        O_ls.append(child)
                        OPEN.put((child.h, child))

                        self.parent[child.row][child.col] = curr

                        if child.color == WHITE:
                            child.set_color(BLUE)
                            child.display_cell(self.window)
                 
        self.find_path()


    def RUN(self):

        clock = pygame.time.Clock()
        run = True
        self.draw_board()

        ################ blocks for buttons #############
        start_button = Button(" Start Node ", 20, 50, 250, 50, self.window)
        goal_button = Button(" Goal Node ", 300, 50, 250, 50, self.window)

        A_button = Button(" A* Search ", 20, 150, 250, 50, self.window)
        D_button = Button(" Dijkstra ", 300, 150, 200, 50, self.window)
        BFS_button = Button(" BFS Search ", 600, 150, 250, 50, self.window)

        GBFS_button = Button(" GBFS Search ", 875, 150, 250, 50, self.window)


        CLEAR_button = Button(" CLEAR BOARD ", 800, 50, 350, 50, self.window)
        CLEAR_search_button = Button(" CLEAR SEARCH ", 800, 100, 350, 50, self.window)

        ################ blocks for buttons #############
        
        while run:
            for event in pygame.event.get():
                
                if event.type == pygame.QUIT:
                    run = False
                
                
                    
                if pygame.mouse.get_pressed()[0]:
                    mouse_pos = pygame.mouse.get_pos()
                    ROW, COL = self.get_pos(mouse_pos)

                    if mouse_pos[1] <= 200:
                        start_button.click(mouse_pos[0], mouse_pos[1], self.set_start)
                        goal_button.click(mouse_pos[0], mouse_pos[1], self.set_goal)

                        A_button.click(mouse_pos[0], mouse_pos[1], self.A_star)
                        D_button.click(mouse_pos[0], mouse_pos[1], self.Dijkstra)
                        BFS_button.click(mouse_pos[0], mouse_pos[1], self.BFS)
                        GBFS_button.click(mouse_pos[0], mouse_pos[1], self.GBFS)

                        CLEAR_button.click(mouse_pos[0], mouse_pos[1], self.clear_board)
                        CLEAR_search_button.click(mouse_pos[0], mouse_pos[1], self.clear_search)
                        
                    else:
                        
                        try:
                            
                            self.draw_obstacles(ROW, COL)
                        except AttributeError:
                            pass

            x, y = pygame.mouse.get_pos()

            start_button.update()
            start_button.change_color(x,y)

            goal_button.update()
            goal_button.change_color(x,y)

            A_button.update()
            A_button.change_color(x,y)

            D_button.update()
            D_button.change_color(x,y)

            BFS_button.update()
            BFS_button.change_color(x,y)

            GBFS_button.update()
            GBFS_button.change_color(x,y)

            
            CLEAR_button.update()
            CLEAR_button.change_color(x,y)

            CLEAR_search_button.update()
            CLEAR_search_button.change_color(x,y)


            clock.tick(FPS)
            pygame.display.update()





        
test = Board()
test.RUN()
