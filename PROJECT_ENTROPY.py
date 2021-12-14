import pygame
import random 
import math

FPS = 80
WINDOW_SIZE = (725,725)
BLOCK_SIZE = (50,50)
BASE_STATION_SIZE = (40,40)
ROAD_WIDTH = 25

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SILVER = (192,192,192)

RED = (255, 0, 0)
ORANGE = (255,165,0)
YELLOW = (255, 204, 0)
LIME = (50,205,50)
GREEN = (0, 128, 0)
LIGHT_BLUE = (130,202,250)
BLUE = (0,131,255)
NAVY = (0,0,128)
PURPLE = (128,0,128)
PINK = (240,120,192)

COLORS = [RED,ORANGE,YELLOW,LIME,GREEN,LIGHT_BLUE,BLUE,NAVY,PURPLE,PINK]

RUNNING_STATE = True
CLOCK = pygame.time.Clock()
PROJECT_NAME = "THREASHOLD"
FONT_NAME = pygame.font.match_font('arial')

P_TRANSMIT = 180 #dB
ENTROPY = 25 #dB
LAMBDA = 1 / 1200

pygame.init()
pygame.display.set_caption(PROJECT_NAME)
screen = pygame.display.set_mode(WINDOW_SIZE)

# BLOCK
BLOCKS = []
BLOCK_SPRITE = pygame.sprite.Group()
# BASE STATION
BASE_STATIONS = []
BASE_STATION_SPRITE = pygame.sprite.Group()
COORDINATE = []    
# CAR
CARS = []
CAR_SPRITE = pygame.sprite.Group()

def CHECK_DUPLICATE(i,j,list):
    for k in range(len(list)):
        if i == list[k][0] and j == list[k][1]:
            return 1
    return 0
        
def draw_text(text, size, x, y, color):
    font = pygame.font.Font(FONT_NAME, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.centery = y
    screen.blit(text_surface, text_rect)
    
def draw_line(color, start, end, width):
    pygame.draw.line(screen , color , start , end , width)  
    
def calculate_distance(car_x,car_y,base_station_x,base_station_y):
    delta_x_square = (car_x - base_station_x)**2
    delta_y_square = (car_y - base_station_y)**2
    result = (delta_x_square + delta_y_square)**(1/2)
    return result

def calculate_path_loss(frequency, distance):
    result = 32.45 + (20 * math.log10(frequency)) + (20 * math.log10(distance))
    return result

def check_in_map(left,right,top,bottom):
    if (right <= 0) or (left >= WINDOW_SIZE[0]) or (top >= WINDOW_SIZE[1]) or (bottom <= 0):
        return 0
    else:
        return 1
    
def determine_base_station(car,BASE_STATIONS,initial): #determine the largest power of base station to connect
    P_RECEIVE = 0
    LARGEST = float("-inf")
    old_index = -1
    new_index = -1
    return_index = -1
    if initial == True: # FIND LARGEST
        for j in range(len(BASE_STATIONS)):
            base_station = BASE_STATIONS[j]
            frequency = base_station.frequency
            distance = calculate_distance(car.rect.centerx , car.rect.centery , base_station.rect.centerx , base_station.rect.centery)
            path_loss = calculate_path_loss(frequency,distance)
            P_RECEIVE = P_TRANSMIT - path_loss
            if P_RECEIVE > LARGEST:
                LARGEST = P_RECEIVE
                new_index = j
        P_RECEIVE = LARGEST
        return_index = new_index
    elif initial == False:
        # FIND CURRENT PR
        old_index = car.current_base_station
        frequency = BASE_STATIONS[old_index].frequency
        base_station_x = BASE_STATIONS[old_index].rect.centerx
        base_station_y = BASE_STATIONS[old_index].rect.centery
        distance = calculate_distance(car.rect.centerx , car.rect.centery , base_station_x , base_station_y)
        path_loss = calculate_path_loss(frequency,distance)
        CURRENT_P_RECEIVE = P_TRANSMIT - path_loss

        # FIND LARGEST PR AND DETERMINE WHETHER SWITCH TO IT
        for j in range(len(BASE_STATIONS)): #找最大的PR
            base_station = BASE_STATIONS[j]
            frequency = base_station.frequency
            distance = calculate_distance(car.rect.centerx , car.rect.centery , base_station.rect.centerx , base_station.rect.centery)
            path_loss = calculate_path_loss(frequency,distance)
            P_RECEIVE = P_TRANSMIT - path_loss
            if P_RECEIVE > LARGEST:
                LARGEST = P_RECEIVE
                new_index = j
        if (LARGEST - CURRENT_P_RECEIVE) > ENTROPY:
            P_RECEIVE = LARGEST
            return_index = new_index
        else:
            P_RECEIVE = CURRENT_P_RECEIVE
            return_index = old_index

    color = BASE_STATIONS[return_index].color
    car.color = color
    car.P_RECEIVE = P_RECEIVE      
    return return_index , P_RECEIVE , color

def arrival_probability():
    probability = ((LAMBDA * 1) ** 1) * (math.e ** -(LAMBDA * 1))
    probability = round(probability, 7) * (10**7)
    return probability

class BLOCK(pygame.sprite.Sprite):
    def __init__(self,i,j):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface(BLOCK_SIZE)
        self.color = SILVER
        self.image.fill(SILVER)
        self.rect = self.image.get_rect()

        self.rect.x = (50+ROAD_WIDTH) * i 
        self.rect.y = (50+ROAD_WIDTH) * j 
    
    def update(self):
        return
        
class BASE_STATION(pygame.sprite.Sprite):
    def __init__(self,i,j):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface(BASE_STATION_SIZE)
        color_index = random.randrange(1,11)
        self.color = COLORS[color_index-1]
        self.frequency = color_index * 100
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.x = ( (50+ROAD_WIDTH) * i) + 5
        self.rect.y = ( (50+ROAD_WIDTH) * j) + 5
        
        prob = random.randrange(0,4)
        if prob == 0: #left
            self.rect.x = self.rect.x - 5
        elif prob == 1: #right
            self.rect.x = self.rect.x + 5
        elif prob == 2: #up
            self.rect.y = self.rect.x + 5
        elif prob == 3: #down
            self.rect.y = self.rect.y - 5
                    
    def update(self):
        return

class CAR(pygame.sprite.Sprite):           
    def __init__(self,i,j,direction):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((ROAD_WIDTH,ROAD_WIDTH))
        self.current_base_station = -1
        self.color = BLACK
        self.image.fill(self.color)
        self.rect = self.image.get_rect()  
        self.rect.x = i
        self.rect.y = j
        self.direction = direction
        self.P_RECEIVE = 0
                
    def check_turn(self,x,y):
        for i in range(10):
            for j in range(10):
                car_x = (75*i) + 50
                car_y = (75*j) + 50
                if car_x == x and car_y == y:
                    return 1
        return 0
        
    def update(self):       
        check = self.check_turn(self.rect.x,self.rect.y)
        if check == 1:
            prob = random.randint(1,32)
            if prob <= 16:
                self.direction = self.direction + 0
            elif prob >= 17 and prob <= 18:
                self.direction = self.direction + 2 
            elif prob >= 19 and prob <= 26:
                self.direction = self.direction + 1
            else:
                self.direction = self.direction - 1
            self.direction = self.direction % 4
        
        if self.direction == 0:
            self.rect.y += 2
        elif self.direction == 1:
            self.rect.y -= 2
        elif self.direction == 2:
            self.rect.x += 2
        elif self.direction == 3:
            self.rect.x -= 2       
        
        self.image.fill(self.color)

for i in range(10):
    for j in range(10):
        block_temp = BLOCK(i,j)
        BLOCKS.append(block_temp)
        BLOCK_SPRITE.add(block_temp)
        prob = random.randrange(0,10)
        if(prob == 1):
            if ( CHECK_DUPLICATE(i,j,COORDINATE) == 0 ):
                COORDINATE.append( (i,j) )
                base_station_temp = BASE_STATION(i,j)
                BASE_STATIONS.append(base_station_temp)
                BASE_STATION_SPRITE.add(base_station_temp)

#====================GAME LOOP====================
while RUNNING_STATE == True:
    CLOCK.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUNNING_STATE = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                RUNNING_STATE = False
    #====================CAR====================
    for i in range(4):
        for j in range(1,10):
            arrival_prob = arrival_probability()
            prob = random.randrange(0, 10**7)
            
            if(i == 0): # DOWN
                if prob < arrival_prob:
                    x = (75 * j) + 50
                    y = 0
                    car_temp = CAR(x,y,0)
                    index , P_RECEIVE , color = determine_base_station(car_temp,BASE_STATIONS,True)
                    car_temp.color = color
                    car_temp.current_base_station = index
                    CARS.append(car_temp)
                    CAR_SPRITE.add(car_temp)
            elif(i == 1): # UP
                if prob < arrival_prob:
                    x = (75 * j) + 50
                    y = 700
                    car_temp = CAR(x,y,1)
                    index , P_RECEIVE , color = determine_base_station(car_temp,BASE_STATIONS,True)
                    car_temp.current_base_station = index
                    CARS.append(car_temp)
                    CAR_SPRITE.add(car_temp)
            elif(i == 2): # RIGHT
                if prob < arrival_prob:
                    x = 0 
                    y = (75 * j) + 50
                    car_temp = CAR(x,y,2)
                    index , P_RECEIVE , color = determine_base_station(car_temp,BASE_STATIONS,True)
                    car_temp.current_base_station = index
                    CARS.append(car_temp)
                    CAR_SPRITE.add(car_temp)
            elif(i == 3): # LEFT
                if prob < arrival_prob:
                    x = 700
                    y = (75 * j) + 50
                    car_temp = CAR(x,y,3)
                    index , P_RECEIVE , color = determine_base_station(car_temp,BASE_STATIONS,True)
                    car_temp.current_base_station = index
                    CARS.append(car_temp)
                    CAR_SPRITE.add(car_temp)
                    
    #畫面顯示
    screen.fill(WHITE)
    BLOCK_SPRITE.draw(screen)
    BASE_STATION_SPRITE.draw(screen)
    CAR_SPRITE.draw(screen)
    
    #====================UPDATE====================
    BLOCK_SPRITE.update()
    BASE_STATION_SPRITE.update()
    CAR_SPRITE.update()
    
    for car in CARS:
        if check_in_map(car.rect.left , car.rect.right , car.rect.top , car.rect.bottom) == 0:
            car.kill()
            CARS.remove(car)            
    
    for base_station in BASE_STATIONS:
        text = str(base_station.frequency) + " MHZ"
        draw_text(text , 11 , base_station.rect.centerx , base_station.rect.centery , WHITE)

    for i in range(len(CARS)):
        car = CARS[i]
        base_station = BASE_STATIONS[0]
        index , P_RECEIVE , color = determine_base_station(car,BASE_STATIONS,False)
        car.current_base_station = index
        car.color = color
        
        P_RECEIVE = round(P_RECEIVE,2)     
        text = str(P_RECEIVE) + " dB"
        car_pos = (car.rect.centerx , car.rect.centery)
        base_station_pos = ( BASE_STATIONS[index].rect.centerx , BASE_STATIONS[index].rect.centery)
        draw_line(car.color , car_pos , base_station_pos , 1)
        draw_text(text , 14 , car.rect.x+10 , car.rect.y-10 , car.color)

    pygame.display.update()
    
pygame.quit()