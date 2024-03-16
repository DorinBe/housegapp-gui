ROOM_TYPES = {
    "Living Room" : 1,
    "Kitchen" : 2,
    "Bedroom" : 3,
    "Bathroom" : 4,
    "Balcony" : 5,
    "Entrance" : 6,
    "Dining Room" : 7,
    "Study Room" : 8,
    "Storage" : 10,
    "Front Door" : 15,
    "Unknown" : 16,
    "Interior Door" : 17
}

ROOM_COLORS = {
    1: '#EE4D4D', 
    2: '#C67C7B', 
    3: '#FFD274', 
    4: '#BEBEBE', 
    5: '#BFE3E8', 
    6: '#7BA779', 
    7: '#E87A90', 
    8: '#FF8C69', 
    10: '#1F849B', 
    15: '#727171', 
    16: '#785A67', 
    17: '#D3A2C7'}

def room_name_to_id(name: str) -> int:
    room_id = ROOM_TYPES[name]
    if room_id == None:
        room_id = 16 #Unknown
    
    return room_id

def room_id_to_color(id: int) -> str:
    room_color = ROOM_COLORS[id]
    if room_color == None:
        room_color = '#785A67' #Unknown
    
    return room_color