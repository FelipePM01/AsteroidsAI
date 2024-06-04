import numpy as np

def threatDistance(player, threat, display_dims):
        display_width, display_height = display_dims
        p_x = player.x
        p_y = player.y
        a_x = threat.x
        a_y = threat.y

        switch_y = p_y > a_y
        if switch_y:
            p_y = display_height - p_y
            a_y = display_height - a_y
        
        switch_x = p_x > a_x
        if switch_x:
            p_x = display_width - p_x
            a_x = display_width - a_x
        
        if a_y - p_y <= (p_y + display_height - a_y):
            vec_y = a_y - p_y
        else:
            vec_y = (a_y - display_height) - p_y

        if a_x - p_x <= (p_x + display_width - a_x):
            vec_x = a_x - p_x
        else:
            vec_x = (a_x - display_width) - p_x

        if switch_x:
            vec_x*=-1

        if switch_y:
            vec_y*=-1
        
        return (vec_x, vec_y)

def recToPolar(x,y = None):
  if y == None:
    return recToPolar(x[0],x[1])
  angle = np.arctan2(x, y)*180/np.pi
  magnitude = np.sqrt(x**2+y**2)
  return (magnitude, angle)

def limitTo180(angle):
  angle = angle%360
  if angle > 180:
    return angle - 360 
  if angle <= -180:
    return angle + 360
  return angle

def within_margin(number, target, margin=5):
    return abs(number - target) <= margin