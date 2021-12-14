        P_receive = round(P_receive,2)     
        text = str(P_receive) + " dB"
        car_pos = (car.rect.centerx , car.rect.centery)
        base_station_pos = ( BASE_STATIONS[new_index].rect.centerx , BASE_STATIONS[new_index].rect.centery)
        draw_line(car.color , car_pos , base_station_pos , 1)
        draw_text(text , 14 , car.rect.x+10 , car.rect.y-10 , car.color)
        
        if(new_index != old_index):
            TOTAL_SWITCH = TOTAL_SWITCH + 1
            print("TOTAL SWITCH : ",TOTAL_SWITCH)