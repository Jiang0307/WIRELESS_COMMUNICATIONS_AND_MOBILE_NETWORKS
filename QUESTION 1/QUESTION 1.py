import pygame
import random 
import math

PROJECT_NAME = "BEST EFFORT"
FONT_NAME = pygame.font.match_font("arial")

FPS = 60
MODE = 0
RUNNING_STATE = True

P_THREASHOLD = 60 # MINIMUM
P_TRANSMIT = 160 # dB
ENTROPY = 25 # ENTROPY
LAMBDA = 1 / 1200
SPEED = 1

CLOCK = pygame.time.Clock()
BLOCK_SPRITE = pygame.sprite.Group();BASE_STATION_SPRITE = pygame.sprite.Group();CAR_SPRITE = pygame.sprite.Group()
HIDE = 0;BEST_EFFORT = 1;MINIMUM = 2;ENTROPY = 3;SELF_DESIGN = 4
BLOCKS = [];BASE_STATIONS = [];CARS = [];COORDINATE = []
TOTAL_SWITCH_BEST_EFFORT = 0 ; TOTAL_SWITCH_MINIMUM = 0 ; TOTAL_SWITCH_ENTROPY = 0 ; TOTAL_SWITCH_SELF_DESIGN = 0
BLOCK_SIZE = (50,50) ; BASE_STATION_SIZE = (40,40) ; ROAD_WIDTH = 15 ; RATIO = BLOCK_SIZE[0]/2.5
BLACK = (0, 0, 0);WHITE=(255, 255, 255) ; SILVER=(192,192,192) ; RED= (255, 0, 0) ; ORANGE=(255,165,0) ; YELLOW=(255, 204, 0) ; LIME=(50,205,50) ; GREEN=(0,128, 0) ; LIGHT_BLUE=(130,202,250) ; BLUE=(0,131,255) ; NAVY=(0,0,128) ; PURPLE=(128,0,128) ; PINK=(240,120,192)
COLORS=[RED,ORANGE,YELLOW,LIME,GREEN,LIGHT_BLUE,BLUE,NAVY,PURPLE,PINK]
WINDOW_SIZE = ( (BLOCK_SIZE[0] + ROAD_WIDTH) * 10 - ROAD_WIDTH , (BLOCK_SIZE[1] + ROAD_WIDTH) * 10 - ROAD_WIDTH )


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
    result = result / RATIO
    return result

def calculate_path_loss(frequency, distance):
    result = 32.45 + (20 * math.log10(frequency)) + (20 * math.log10(distance))
    return result

def check_in_map(left,right,top,bottom):
    if (right <= 0) or (left >= WINDOW_SIZE[0]) or (top >= WINDOW_SIZE[1]) or (bottom <= 0):
        return 0
    else:
        return 1
    
def determine_base_station_best_effort(car,BASE_STATIONS): #determine the largest power of base station to connect
    P_RECEIVE = 0
    LARGEST = float("-inf")
    index = -1
    for j in range(len(BASE_STATIONS)):
        base_station = BASE_STATIONS[j]
        frequency = base_station.frequency
        distance = calculate_distance(car.rect.centerx , car.rect.centery , base_station.rect.centerx , base_station.rect.centery)
        path_loss = calculate_path_loss(frequency,distance)
        P_RECEIVE = P_TRANSMIT - path_loss

        if P_RECEIVE > LARGEST:
            LARGEST = P_RECEIVE
            index = j

    P_RECEIVE = LARGEST
    color = BASE_STATIONS[index].color
    #car.color = color
    car.P_RECEIVE_BEST_EFFORT = P_RECEIVE
    return index , round(P_RECEIVE,2) , color

def determine_base_station_minimum(car,BASE_STATIONS,initial): #determine the largest power of base station to connect
    P_RECEIVE = 0
    LARGEST = float("-inf")
    old_index = -1
    new_index = -1
    return_index = -1
    if initial == True: # FIND LATGEST
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
        old_index = car.current_base_station_MINIMUM
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

        if CURRENT_P_RECEIVE > P_THREASHOLD:
            P_RECEIVE = CURRENT_P_RECEIVE
            return_index = old_index
        else:
            P_RECEIVE = LARGEST
            return_index = new_index

    color = BASE_STATIONS[return_index].color
    #car.color = color
    car.P_RECEIVE_MINIMUM = P_RECEIVE      
    return return_index , round(P_RECEIVE,2) , color

def determine_base_station_entropy(car,BASE_STATIONS,initial): #determine the largest power of base station to connect
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
        old_index = car.current_base_station_ENTROPY
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
    #car.color = color
    car.P_RECEIVE_ENTROPY = P_RECEIVE
    return return_index , round(P_RECEIVE,2) , color

def determine_base_station_self_design(car,BASE_STATIONS,initial): # determine the largest power of base station to connect
    index = -1
    nearest_distance = float("inf")
    for j in range(len(BASE_STATIONS)): 
        base_station = BASE_STATIONS[j]
        distance = calculate_distance(car.rect.centerx , car.rect.centery , base_station.rect.centerx , base_station.rect.centery)     
        if distance < nearest_distance:
            nearest_distance = distance
            index = j
    
    frequency = BASE_STATIONS[index].frequency
    path_loss = calculate_path_loss(frequency,nearest_distance)
    P_RECEIVE = P_TRANSMIT - path_loss
    color = BASE_STATIONS[index].color
    #car.color = color
    car.P_RECEIVE_SELF_DESIGN = P_RECEIVE
    
    return index , round(P_RECEIVE,2) , color

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

        self.rect.x = (BLOCK_SIZE[0]+ROAD_WIDTH) * i 
        self.rect.y = (BLOCK_SIZE[1]+ROAD_WIDTH) * j 
    
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
        self.rect.x = ( (BLOCK_SIZE[0]+ROAD_WIDTH) * i) + (BLOCK_SIZE[0]-BASE_STATION_SIZE[0])/2
        self.rect.y = ( (BLOCK_SIZE[1]+ROAD_WIDTH) * j) + (BLOCK_SIZE[1]-BASE_STATION_SIZE[1])/2
        prob = random.randrange(0,4)
        if prob == 0: #left
            self.rect.x = self.rect.x - (BLOCK_SIZE[0]-BASE_STATION_SIZE[0])/2
        elif prob == 1: #right
            self.rect.x = self.rect.x + (BLOCK_SIZE[0]-BASE_STATION_SIZE[0])/2
        elif prob == 2: #up
            self.rect.y = self.rect.y + (BLOCK_SIZE[1]-BASE_STATION_SIZE[1])/2
        elif prob == 3: #down
            self.rect.y = self.rect.y - (BLOCK_SIZE[1]-BASE_STATION_SIZE[1])/2
                    
    def update(self):
        return

class CAR(pygame.sprite.Sprite):           
    def __init__(self,i,j,direction):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((ROAD_WIDTH,ROAD_WIDTH))
        self.color = BLACK
        self.image.fill(self.color)
        self.rect = self.image.get_rect()  
        self.rect.x = i
        self.rect.y = j
        self.direction = direction

        self.P_RECEIVE_BEST_EFFORT = float("-inf")
        self.P_RECEIVE_MINIMUM = 0
        self.P_RECEIVE_ENTROPY = 0
        self.P_RECEIVE_SELF_DESIGN = 0

        self.current_base_station_BEST_EFFORT = -1
        self.current_base_station_MINIMUM = -1
        self.current_base_station_ENTROPY = -1
        self.current_base_station_SELF_DESIGN = -1
                
    def check_turn(self,x,y):
        for i in range(10):
            for j in range(10):
                car_x = ( (BLOCK_SIZE[0] + ROAD_WIDTH) * i) + BLOCK_SIZE[0]
                car_y = ( (BLOCK_SIZE[1] + ROAD_WIDTH) * j) + BLOCK_SIZE[1]
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
            self.rect.y += SPEED
        elif self.direction == 1:
            self.rect.y -= SPEED
        elif self.direction == 2:
            self.rect.x += SPEED
        elif self.direction == 3:
            self.rect.x -= SPEED
        
        self.image.fill(self.color)

def CREATE_BLOCK_AND_BASE_STATION():
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

def CREATE_CAR():        
    for i in range(4):
        for j in range(1,10):
            arrival_prob = arrival_probability()
            prob = random.randrange(0, 10**7)
            if(i == 0): # DOWN
                if prob < arrival_prob:
                    x = ( (BLOCK_SIZE[0] + ROAD_WIDTH) * j ) + BLOCK_SIZE[0]
                    y = 0
                    car_temp = CAR(x,y,0)
                    
                    index_BEST_EFFORT , P_RECEIVE_BEST_EFFORT , color_BEST_EFFORT = determine_base_station_best_effort(car_temp,BASE_STATIONS)
                    index_MINIMUM , P_RECEIVE_MINIMUM , color_MINIMUM = determine_base_station_minimum(car_temp,BASE_STATIONS,True)
                    index_BEST_ENTROPY , P_RECEIVE_BEST_ENTROPY , color_ENTROPY = determine_base_station_entropy(car_temp,BASE_STATIONS,True)
                    index_BEST_SELF_DESIGN , P_RECEIVE_SELF_DESIGN , color_SELF_DESIGN = determine_base_station_self_design(car_temp,BASE_STATIONS,True)
                    
                    CARS.append(car_temp)
                    CAR_SPRITE.add(car_temp)
            elif(i == 1): # UP
                if prob < arrival_prob:
                    x = ( (BLOCK_SIZE[0] + ROAD_WIDTH) * j ) + BLOCK_SIZE[0]
                    y = ( BLOCK_SIZE[1] + ROAD_WIDTH ) * 10 - BLOCK_SIZE[1]
                    car_temp = CAR(x,y,1)
                    
                    index_BEST_EFFORT , P_RECEIVE_BEST_EFFORT , color_BEST_EFFORT = determine_base_station_best_effort(car_temp,BASE_STATIONS)
                    index_MINIMUM , P_RECEIVE_MINIMUM , color_MINIMUM = determine_base_station_minimum(car_temp,BASE_STATIONS,True)
                    index_BEST_ENTROPY , P_RECEIVE_BEST_ENTROPY , color_ENTROPY = determine_base_station_entropy(car_temp,BASE_STATIONS,True)
                    index_BEST_SELF_DESIGN , P_RECEIVE_SELF_DESIGN , color_SELF_DESIGN = determine_base_station_self_design(car_temp,BASE_STATIONS,True)          
                    
                    CARS.append(car_temp)
                    CAR_SPRITE.add(car_temp)
            elif(i == 2): # RIGHT
                if prob < arrival_prob:
                    x = 0 
                    y = ( (BLOCK_SIZE[1] + ROAD_WIDTH) * j ) + BLOCK_SIZE[1]
                    car_temp = CAR(x,y,2)
                    
                    index_BEST_EFFORT , P_RECEIVE_BEST_EFFORT , color_BEST_EFFORT = determine_base_station_best_effort(car_temp,BASE_STATIONS)
                    index_MINIMUM , P_RECEIVE_MINIMUM , color_MINIMUM = determine_base_station_minimum(car_temp,BASE_STATIONS,True)
                    index_BEST_ENTROPY , P_RECEIVE_BEST_ENTROPY , color_ENTROPY = determine_base_station_entropy(car_temp,BASE_STATIONS,True)
                    index_BEST_SELF_DESIGN , P_RECEIVE_SELF_DESIGN , color_SELF_DESIGN = determine_base_station_self_design(car_temp,BASE_STATIONS,True)      
                    
                    CARS.append(car_temp)
                    CAR_SPRITE.add(car_temp)
            elif(i == 3): # LEFT
                if prob < arrival_prob:
                    x = ( BLOCK_SIZE[0] + ROAD_WIDTH ) * 10 - BLOCK_SIZE[0]
                    y = ( (BLOCK_SIZE[1] + ROAD_WIDTH) * j ) + BLOCK_SIZE[1]
                    car_temp = CAR(x,y,3)
                    
                    index_BEST_EFFORT , P_RECEIVE_BEST_EFFORT , color_BEST_EFFORT = determine_base_station_best_effort(car_temp,BASE_STATIONS)
                    index_MINIMUM , P_RECEIVE_MINIMUM , color_MINIMUM = determine_base_station_minimum(car_temp,BASE_STATIONS,True)
                    index_BEST_ENTROPY , P_RECEIVE_BEST_ENTROPY , color_ENTROPY = determine_base_station_entropy(car_temp,BASE_STATIONS,True)
                    index_BEST_SELF_DESIGN , P_RECEIVE_SELF_DESIGN , color_SELF_DESIGN = determine_base_station_self_design(car_temp,BASE_STATIONS,True)               
                    
                    CARS.append(car_temp)
                    CAR_SPRITE.add(car_temp)

def UPDATE():
    global TOTAL_SWITCH_BEST_EFFORT , TOTAL_SWITCH_MINIMUM , TOTAL_SWITCH_ENTROPY , TOTAL_SWITCH_SELF_DESIGN , MODE
    for car in CARS:
        if check_in_map(car.rect.left , car.rect.right , car.rect.top , car.rect.bottom) == 0:
            car.kill()
            CARS.remove(car)            

    for base_station in BASE_STATIONS:
        text = str(base_station.frequency) + " MHZ"
        draw_text(text , 11 , base_station.rect.centerx , base_station.rect.centery , WHITE)

    for i in range(len(CARS)):
        car = CARS[i]
        #base_station = BASE_STATIONS[0]
        
        old_index_BEST_EFFORT = car.current_base_station_BEST_EFFORT
        old_index_MINIMUM = car.current_base_station_MINIMUM
        old_index_ENTROPY = car.current_base_station_ENTROPY
        old_index_SELF_DESIGN = car.current_base_station_SELF_DESIGN
        
        new_index_BEST_EFFORT , P_RECEIVE_BEST_EFFORT , color_BEST_EFFORT = determine_base_station_best_effort(car,BASE_STATIONS)
        new_index_MINIMUM , P_RECEIVE_MINIMUM , color_MINIMUM = determine_base_station_minimum(car,BASE_STATIONS,False)
        new_index_ENTROPY , P_RECEIVE_ENTROPY , color_ENTROPY = determine_base_station_entropy(car,BASE_STATIONS,False)
        new_index_SELF_DESIGN , P_RECEIVE_SELF_DESIGN , color_SELF_DESIGN = determine_base_station_self_design(car,BASE_STATIONS,False)
        
        car.current_base_station_BEST_EFFORT = new_index_BEST_EFFORT
        car.current_base_station_MINIMUM = new_index_MINIMUM
        car.current_base_station_ENTROPY = new_index_ENTROPY
        car.current_base_station_SELF_DESIGN = new_index_SELF_DESIGN
        
        if (MODE != 0):
            if (MODE == BEST_EFFORT):
                car.color = color_BEST_EFFORT
                text = str(P_RECEIVE_BEST_EFFORT) + " dB"
                car_pos = (car.rect.centerx , car.rect.centery)
                base_station_pos = ( BASE_STATIONS[new_index_BEST_EFFORT].rect.centerx , BASE_STATIONS[new_index_BEST_EFFORT].rect.centery)  
                draw_line(car.color , car_pos , base_station_pos , 1)
                draw_text(text , 14 , car.rect.x+10 , car.rect.y-10 , car.color)
            elif (MODE == MINIMUM):
                car.color = color_MINIMUM
                text = str(P_RECEIVE_MINIMUM) + " dB"
                car_pos = (car.rect.centerx , car.rect.centery)
                base_station_pos = ( BASE_STATIONS[new_index_MINIMUM].rect.centerx , BASE_STATIONS[new_index_MINIMUM].rect.centery)  
                draw_line(car.color , car_pos , base_station_pos , 1)
                draw_text(text , 14 , car.rect.x+10 , car.rect.y-10 , car.color)
            elif (MODE == ENTROPY):
                car.color = color_ENTROPY
                text = str(P_RECEIVE_ENTROPY) + " dB"
                car_pos = (car.rect.centerx , car.rect.centery)
                base_station_pos = ( BASE_STATIONS[new_index_ENTROPY].rect.centerx , BASE_STATIONS[new_index_ENTROPY].rect.centery)  
                draw_line(car.color , car_pos , base_station_pos , 1)
                draw_text(text , 14 , car.rect.x+10 , car.rect.y-10 , car.color)
            elif (MODE == SELF_DESIGN):
                car.color = color_SELF_DESIGN
                text = str(P_RECEIVE_SELF_DESIGN) + " dB"
                car_pos = (car.rect.centerx , car.rect.centery)
                base_station_pos = ( BASE_STATIONS[new_index_SELF_DESIGN].rect.centerx , BASE_STATIONS[new_index_SELF_DESIGN].rect.centery)  
                draw_line(car.color , car_pos , base_station_pos , 1)
                draw_text(text , 14 , car.rect.x+10 , car.rect.y-10 , car.color)
        else:
            car.color = BLACK
        
        if(new_index_BEST_EFFORT != old_index_BEST_EFFORT):
            TOTAL_SWITCH_BEST_EFFORT += 1
        if(new_index_MINIMUM != old_index_MINIMUM):
            TOTAL_SWITCH_MINIMUM += 1
        if(new_index_ENTROPY != old_index_ENTROPY):
            TOTAL_SWITCH_ENTROPY += 1
        if(new_index_SELF_DESIGN != old_index_SELF_DESIGN):
            TOTAL_SWITCH_SELF_DESIGN += 1        
        if (new_index_BEST_EFFORT != old_index_BEST_EFFORT) or (new_index_MINIMUM != old_index_MINIMUM) or (new_index_ENTROPY != old_index_ENTROPY) or (new_index_SELF_DESIGN != old_index_SELF_DESIGN):
            print("TOTAL SWITCH | ","BEST EFFORT : ",TOTAL_SWITCH_BEST_EFFORT,"    MINIMUM : ",TOTAL_SWITCH_MINIMUM,"    ENTROPY : ",TOTAL_SWITCH_ENTROPY,"    SELF DESIGN : ",TOTAL_SWITCH_SELF_DESIGN)

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption(PROJECT_NAME)
    screen = pygame.display.set_mode(WINDOW_SIZE)
    CREATE_BLOCK_AND_BASE_STATION()
    # GAME LOOP
    while RUNNING_STATE == True:
        CLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUNNING_STATE = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    RUNNING_STATE = False
                elif event.key == pygame.K_0:
                    MODE = HIDE            
                elif event.key == pygame.K_1:
                    MODE = BEST_EFFORT
                elif event.key == pygame.K_2:
                    MODE = MINIMUM
                elif event.key == pygame.K_3:
                    MODE = ENTROPY
                elif event.key == pygame.K_4:
                    MODE = SELF_DESIGN
        # CAR
        CREATE_CAR()
        # 畫面顯示
        screen.fill(WHITE)
        BLOCK_SPRITE.draw(screen)
        BASE_STATION_SPRITE.draw(screen)
        CAR_SPRITE.draw(screen)
        # UPDATE
        BLOCK_SPRITE.update()
        BASE_STATION_SPRITE.update()
        CAR_SPRITE.update()
        UPDATE()
        pygame.display.update()
        
    pygame.quit()