from microbit import *
import neopixel
import math

N = 24 # number of neopixels
b = 1 # initial brightness level
# -- actual 8-bit brightness (0->255), non-linear conversion
B = lambda : int(255*(b/10.)**1.5)
L = 10 # initial countdown length in minutes

# -- initialise neopixel array, set to dark
np = neopixel.NeoPixel(pin0, N)
for i in range(N):
    np[i] = (0,0,0)
np.show()

# -- initial mode: set brightness
mode = 'setbri'

# -- 5x3 digits:
num53 = {0:'010101101101010',
         1:'010110010010111',
         2:'110001011100111',
         3:'110001110001110',
         4:'101101111001001',
         5:'111100110001110',
         6:'011100110101011',
         7:'111001010100100',
         8:'011101111101110',
         9:'110101011001110'}
num52 = {0:'1111111111',
         1:'1010101010',
         2:'1101111011',
         3:'1101100111',
         4:'1011110101',
         5:'1110110111',
         6:'0110111101',
         7:'1101011010',
         8:'1111001111',
         9:'1111110110'}

def int_to_55(n):
    """
    write a number in 0-99 to a 5x5 image to be displayed by the microbit LED array
    """
    res = ''
    for i in range(5):
        if n>9:
            res += num52[n//10][2*i:2*(i+1)]
        else:
            res += '0'
        if n<20:
            res += num53[n%10][3*i:3*(i+1)]
        else:
            res += '0'+num52[n%10][2*i:2*(i+1)]
        if n<10:
            res += '0'
        if i<4:
            res += ':'
    return Image(res.replace('1','9'))

# -- main loop
while True:
    if mode == 'setbri':
        # == set brightness ================
        for i in range(N):
            np[i] = (B(),B(),B())
        np.show()
        if button_a.is_pressed() and button_b.is_pressed():
            for i in range(N):
                np[i] = (0,0,0)
            np.show()
            mode = 'settim'
            sleep(500)
        elif button_b.is_pressed():
            b = min(b+1, 10)
        elif button_a.is_pressed():
            b = max(b-1, 0)
        display.show(int_to_55(b))
    elif mode=='running':
        # == count down time =================
        # -- elapsed time, in minutes
        t = (running_time() - t0)/60000.0
        remaining = L-t # in minutes
        # -- remaining time
        display.show(int_to_55(int(remaining)))
        # -- global color
        if remaining <= min(2, 0.25*L): 
            # -- little time remaining! give visual cue
            x = 0.7 + 0.3*math.sin(2*3.1415*(running_time() - t0)/3000.)
            c = (int(B()*x), int(0.5*x*B()), 0) # progress bar color
            if b==0:
                s = (int(20*x), 0, 0) # seconds' hand color
            else:
                s = (0, B(), B()) # seconds' hand color
        else:
            # -- normal progress
            c = (0,0,B()) # progress bar color
            if b==0:
                s = (0, 10, 20) # seconds' hand color
            else:
                s = (B(), int(0.8*B()), 0) # second's hand color
        # -- set neopixels array
        for i in range(N):
            if i/N*L <= t:
               np[i] = c
            else:
               np[i] = (0,0,0) 
        # -- seconds' hand
        np[int(N*(t%1))] = s   
        np.show()  
        if t>L:
            # -- finished
            j = 0
            mode = 'finished'
            t0 = running_time() # in ms
        if button_a.is_pressed() or button_b.is_pressed():
            mode = 'settim' # stop and cancel
            # -- make a little animation with neopixels
            for i in range(N):
                np[i] = (0,0,0)
            np.show()
            for i in range(N):
                np[i] = c
                sleep(1000/N)
                np.show()
            for i in range(N):
                np[i] = (0,0,0)
            np.show()
    elif mode=='finished':
        # -- finishing screen
        j = (running_time() - t0)/1000. # additional time im seconds
        # -- show blinking neopixel array
        for i in range(N):
            if (i+int(j))%2 == 0:
                np[i] = (B(),0,0)
            else:
                np[i] = (0,0,0)
        # -- show seconds' hand 
        np[int(N*((j/60.)%1))] = (0,0,B())
        if j%1>0.5:
            # -- show additional time in minutes
            display.show(int_to_55(min(int(j/60.), 99)))
        else:
            display.clear()
            if b==0:
                # -- show the seconds' hand in case there is no progress bar
                np[int(N*((j/60.)%1))] = (20,0,0)
        np.show()
        if button_a.is_pressed() or button_b.is_pressed():
            # -- cancel finishing screen go back to setup
            for i in range(N):
                np[i] = (0,0,0)
            np.show()
            mode = 'settim'
    elif mode == 'settim':
        display.show(int_to_55(L))
        # -- standby / setup
        if button_a.is_pressed() and button_b.is_pressed():
            # -- A+B starts the counter
            mode = 'running'
            t0 = running_time() # in ms
            sleep(500)
        elif button_a.is_pressed():
            # -- decrement the decount time
            L = max(1, L-1)
        elif button_b.is_pressed():
            # -- increment the decount time
            L = min(99,L+1)
    sleep(200)