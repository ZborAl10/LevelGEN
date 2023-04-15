# Внизу будет указано, где можно вставить
# название файла, чтобы (поиграться) протестить алгоритм.

from PIL import Image, ImageDraw, ImageColor
from random import *
import math

def lowerImage(img):
    w = img.size[0]
    h = img.size[1]
    w_ = w
    h_ = h
    div = 2
    while w_ > 512 and h_ > 512:
        w_ = w_ // 2
        h_ = h_ // 2
        div *= 2
    img = img.resize((w//div,h//div), Image.ANTIALIAS)
    return img

def getRGB(image, x, y): # очередная бесполезная функция get, пусть будет
    pix = image.load()
    r = pix[x, y][0]
    g = pix[x, y][1]
    b = pix[x, y][2]
    return r, g, b

def rgb2H(r, g, b): # преобр. RGB в параметр тона
    r, g, b = r/255, g/255, b/255
    cmax = max(r, g, b)
    cmin = min(r, g, b)
    diff = cmax-cmin
  
    if cmax == cmin:  
        h = 0
    elif cmax == r:  
        h = (60 * ((g - b) / diff) + 360) % 360
    elif cmax == g: 
        h = (60 * ((b - r) / diff) + 120) % 360
    elif cmax == b: 
        h = (60 * ((r - g) / diff) + 240) % 360
    return round(h)

def rgb2S(r, g, b): # преобр. RGB в параметр насыщенности
    r, g, b = r/255, g/255, b/255
    cmax = max(r, g, b)
    cmin = min(r, g, b)
    diff = cmax-cmin
    if cmax == 0: 
        s = 0
    else: 
        s = (diff / cmax) * 100
    return round(s)

def rgb2V(r, g, b): # преобр. RGB в параметр яркости
    r, g, b = r/255, g/255, b/255
    cmax = max(r, g, b)
    v = cmax * 100
    return round(v)

def hsv2RGB(h, s, v): # преобразование HSV -> RGB
    hi = math.floor(h/60)%6
    vm = (100 - s)*v/100
    a = (v-vm)*(h%60)/60
    vi = vm + a
    vd = v - a
    if hi==0:
        r = v
        g = vi
        b = vm
    elif hi==1:
        r = vd
        g = v
        b = vm
    elif hi==2:
        r = vm
        g = v
        b = vi
    elif hi==3:
        r = vm
        g = vd
        b = v
    elif hi==4:
        r = vi
        g = vm
        b = v
    else:
        r = v
        g = vm
        b = vd
    return round(r*255/100), round(g*255/100), round(b*255/100)

def middleColor(img):
    mid = 0
    r_ = 0
    g_ = 0
    b_ = 0
    pix = img.load()
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            r = pix[x,y][0]
            g = pix[x,y][1]
            b = pix[x,y][2]
            r_ += r
            g_ += g
            b_ += b
            mid += ((r+g+b) / 3)
    r_ /= (img.size[0]*img.size[1])
    g_ /= (img.size[0]*img.size[1])
    b_ /= (img.size[0]*img.size[1])
    mid /= (img.size[0]*img.size[1])
    return round(r_), round(g_), round(b_)
            


def createLayer(img, param): #Создать изображение на основе отдельного канала ('h', 's', 'v')
    width = img.size[0]//2
    height = img.size[1]//2
    new_image = img
    draw = ImageDraw.Draw(new_image)
    pix = new_image.load()
    for x in range(width):
        for y in range(height):
            r = pix[x,y][0]
            g = pix[x,y][1]
            b = pix[x,y][2]
            if param=='h':
                h = rgb2H(r, g, b)
                r, g, b = hsv2RGB(h, 100, 100)
            elif param=='v':
                v = rgb2V(r, g, b)
                r, g, b = hsv2RGB(180, 100, v)
            elif param=='s':
                s = rgb2S(r, g, b)
                r, g, b = hsv2RGB(180, s, 100)
            draw.point((x,y), (r, g, b))
    return new_image
    

def biomLayer(img): #ДЛЯ ПЕРВОГО УРОВНЯ ГЕНЕРАЦИИ! (деление на биомы)
    width = img.size[0]
    height = img.size[1]
    print(width, height)
    new_image = img.resize((width,height), Image.ANTIALIAS)
    draw = ImageDraw.Draw(new_image)
    pix = new_image.load()
    for x in range(width):
        for y in range(height):
            r = pix[x,y][0]
            g = pix[x,y][1]
            b = pix[x,y][2]
            h = rgb2H(r, g, b)
            r, g, b = hsv2RGB(h, 100, 100)
            draw.point((x,y), (r, g, b))
    return new_image


def landscapeLayer(img): #ДЛЯ ВТОРОГО УРОВНЯ ГЕНЕРАЦИИ! (деление на поверхность)
    width = img.size[0]
    height = img.size[1]
    new_image = img.resize((width,height), Image.ANTIALIAS)
    draw = ImageDraw.Draw(new_image)
    pix = new_image.load()
    r_, g_, b_ = middleColor(img)
    mid = rgb2V(r_, g_, b_)
    for x in range(width):
        for y in range(height):
            r = pix[x,y][0]
            g = pix[x,y][1]
            b = pix[x,y][2]
            v = rgb2V(r, g, b)
            if v<mid:
                draw.point((x,y), (255, 0, 0))
            else:
                draw.point((x,y), (0, 0, 0))
    return new_image


def eventsLayer(img): #ДЛЯ ТРЕТЬЕГО УРОВНЯ ГЕНЕРАЦИИ! (деление на события)
    width = img.size[0]
    height = img.size[1]
    new_image = Image.new('RGB', (width,height), Image.ANTIALIAS)
    draw = ImageDraw.Draw(new_image)
    pix = img.load()
    r_, g_, b_ = middleColor(img)
    mid = rgb2S(r_, g_, b_)
    print(mid)
    for x in range(0, width, 2):
        for y in range(0, height, 2):
            r = pix[x,y][0]
            g = pix[x,y][1]
            b = pix[x,y][2]
            s = rgb2S(r, g, b)
            noise = (randint(-1, 1)) * (randint(-1, 1)) * randint(round(15*(r+g+b)/255), round(15*(r+g+b)/255)+10)
            shade = round(255-round(s*256/100)-mid)
            if randint(-3, 1) < 1: noise = 0
            elif randint(-2, 1) == 1:
                if shade >= mid: noise = -abs(noise)
                else: noise = abs(noise)
            draw.point((x,y), (shade+noise, shade+noise, shade+noise))
    return new_image

# !!!!!!!!!! СЮДА ВСТАВИТЬ НАЗВАНИЕ ФАЙЛА В РАСШИРЕНИЕМ
# !!!!!!!!!! ИЗ ТОЙ ЖЕ ДИРЕКТОРИИ  !!!!!!!
a = Image.open('test.png')

a = lowerImage(a)

img1 = biomLayer(a)
img2 = landscapeLayer(a)
img3 = eventsLayer(a)

num = '3'
img1.save(num+'testBioms.png', 'PNG')
img2.save(num+'testLandscape.png', 'PNG')
img3.save(num+'testEvents.png', 'PNG')
