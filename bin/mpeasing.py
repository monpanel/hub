import math

linearTween = lambda t, b, c, d : c*t/d + b

def easeInQuad(t, b, c, d):
	t /= d
	return c*t*t + b


def easeOutQuad(t, b, c, d):
	t /= d
	return -c * t*(t-2) + b

def easeInQuad(t, b, c, d):
    t /= d
    return c * t * t + b
 
def easeOutQuad(t, b, c, d):
    t /= d
    return -c * t * (t - 2) + b
 
def easeInOutQuad(t, b, c, d):
    t /= (d / 2)
    if t < 1:
	    return c / 2 * t * t + b
 
    t -= 1
    return -c / 2 * (t * (t - 2) - 1) + b
 
def easeInQuart(t, b, c, d):
    t /= d
    return c * t * t * t * t + b
 
def easeOutQuart(t, b, c, d):
    t = t / d - 1
    return -c * (t * t * t * t - 1) + b
 
def easeInOutQuart(t, b, c, d):
    t /= (d / 2)
    if t < 1:
        return c / 2 * t * t * t * t + b
	
    t -= 2
    return -c / 2 * (t * t * t * t - 2) + b
 
def easeInQuint(t, b, c, d):
    t /= d
    return c * t * t * t * t * t + b
 
def easeOutQuint(t, b, c, d):
    t = t / d - 1
    return c * (t * t * t * t * t + 1) + b
 
def easeInOutQuint(t, b, c, d):
    t /= (d / 2)
    if t < 1:
        return c / 2 * t * t * t * t * t + b
    t -= 2
    return c / 2 * (t * t * t * t * t + 2) + b
 
def easeInCubic(t, b, c, d):
    t /= d
    return c * t * t * t + b
 
def easeInOutCubic(t, b, c, d):
    t /= (d / 2)
    if t < 1:
        return c / 2 * t * t * t + b
	
    t -= 2
    return c / 2 * (t * t * t + 2) + b
 
def easeInSine(t, b, c, d):
    return -c * cos(t / d * (math.pi / 2)) + c + b
 
def easeOutSine(t, b, c, d):
    return c * sin(t / d * (math.pi / 2)) + b
 
def easeInOutSine(t, b, c, d):
    return -c / 2 * (cos(math.pi * t / d) - 1) + b
 
def easeInExpo(t, b, c, d):
    if t == 0:
        return b
    return c * pow(2, 10 * (t / d - 1)) + b
 
def easeOutExpo(t, b, c, d):
    if t == d:
        return b + c
    return c * (-pow(2, -10 * t / d) + 1) + b
 
def easeInOutExpo(t, b, c, d):
    if t == 0:
        return b
    if t == d:
        return b + c
 
    t /= (d / 2)
    if t < 1:
        return c / 2 * pow(2, 10 * (t - 1)) + b
 
    t -= 1
    return c / 2 * (-pow(2, -10 * t) + 2) + b
 
def easeInCirc(t, b, c, d):
    t /= d
    return -c * (sqrt(1 - t * t) - 1) + b
 
def easeOutCirc(t, b, c, d):
    t = t / d - 1
    return c * sqrt(1 - t * t) + b
 
def easeInOutCirc(t, b, c, d):
    t /= (d / 2)
    if t < 1:
        return -c / 2 * (sqrt(1 - t * t) - 1) + b
 
    t -= 2
    return c / 2 * (sqrt(1 - t * t) + 1) + b
 
def easeInElastic(t, b, c, d):
    s = 1.70158
    a = c
    
    if t == 0: return b
    t /= d
    if t == 1: return b + c
 
    p = d * 0.3
    if a < abs(c):
        a = c
        s = p / 4
    else:
        s = p / (2 * math.pi) * math.asin(c / a)
 
    t -= 1
    return -(a * pow(2, 10 * t) * math.sin((t * d - s) * (2 * math.pi) / p)) + b
 
def easeOutElastic(t, b, c, d):
    s, a = 1.70158, c
    
    if t == 0: return b
    t /= d
    if t == 1: return b + c
 
    p = d * 0.3
    if a < abs(c):
        a, s = c, p / 4
    else:
        s = p / (2 * math.pi) * math.asin(c / a)
 
    return a * pow(2, -10 * t) * math.sin((t * d - s) * (2 * math.pi) / p) + c + b
 
def easeInOutElastic(t, b, c, d):
    s, a = 1.70158, c
    
    if t == 0: return b
    t /= (d / 2)
    if t == 2: return b + c
    
    p = d * (0.3 * 1.5)
    if a < abs(c):
        a, s = c, p / 4
    else:
        s = p / (2 * math.pi) * math.asin(c / a)
 
    if t < 1:
        t -= 1
        return -0.5 * (a * pow(2, 10 * t) * math.sin((t * d - s) * (2 * math.pi) / p)) + b
 
    t -= 1
    return a * pow(2, -10 * t) * math.sin((t * d - s) * (2 * math.pi) / p ) * 0.5 + c + b


