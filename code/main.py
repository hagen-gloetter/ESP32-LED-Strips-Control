import machine
import time
led = machine.Pin(2, machine.Pin.OUT)
#while True:
#    led.value(1)
#    time.sleep(1)
#    led.value(0)
#    time.sleep(1)

#PINs :
#           R   G  B 
#LED OUT 1: 17,21,22
#LED OUT 2: 32,25,27
#Taster1: 39
#Taster2: 35
print("main")

# html stuff
#import html
def web_page():
  if led.value() == 1:
    gpio_state="ON"
  else:
    gpio_state="OFF"
  # tnx to https://stackoverflow.com/questions/71111182/myobj-json-parsethis-responsetext-give-an-error-in-my-project
  html = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Sternwarte Huettenlicht</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <link rel="icon" href="data:," />
    <style>
      html {
        font-family: Helvetica;
        display: inline-block;
        margin: 0px auto;
        text-align: center;
      }

      h1 {
        color: #0f3376;
        padding: 1vh;
      }
      table {
        margin-left: auto;
        margin-right: auto;
        text-align: left;
      }
      td {
        padding: 4px;
        border: 1px solid;
      }
      p {
        font-size: 1.5rem;
      }

      .button {
        display: inline-block;
        background-color: rgb(85, 231, 59);
        border: none;
        border-radius: 4px;
        color: white;
        padding: 16px 40px;
        text-decoration: none;
        font-size: 30px;
        margin: 2px;
        cursor: pointer;
      }

      .button2 {
        background-color: #f44242;
      }
    </style>
  </head>

  <body>
    <h1>ESP Web Server</h1>
    <table>
      <tr>
        <td><p>Licht Rot</p></td>
        <td><p id="button_red"></p></td>
      </tr>
      <tr>
        <td><p>Licht Weiss</p></td>
        <td><p id="button_white"></p></td>
      </tr>
      <tr>
        <td><p>Helligkeit</p></td>
        <td><p id="LED_brightness"></p></td>
      </tr>
      <tr>
        <td><p>Dach</p></td>
        <td><p id="LED_roof"></p></td>
      </tr>
    </table>
    <p>
      <a href="/?led=on"><button class="button">ON</button></a>
    </p>
    <p>
      <a href="/?led=off"><button class="button button2">OFF</button></a>
    </p>
    <script>
      function get_HW_Infos() {
        const xhr = new XMLHttpRequest(),
          method = "GET",
          url = "data.json";
        xhr.open(method, url, true);
        xhr.onreadystatechange = function () {
          if (xhr.readyState === XMLHttpRequest.DONE) {
            var status = xhr.status;
            if (status === 0 || (status >= 200 && status < 400)) {
              // The request has been completed successfully
              // console.log(xhr.responseText);
              myobj = JSON.parse(xhr.responseText);
              document.getElementById("button_red").innerText =
                myobj.button_red;
              document.getElementById("button_white").innerText =
                myobj.button_white;
              document.getElementById("LED_brightness").innerText =
                myobj.LED_brightness;
              document.getElementById("LED_roof").innerText = myobj.LED_roof;
            } else {
              console.log("Oh no! There has been an error with the request!");
            }
          }
        };
        xhr.send();
      }
      window.setInterval(get_HW_Infos, 1000);
    </script>
  </body>
</html>
"""
  return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

# button part start =========================================================================================================
from machine import Pin, Timer
import time

light_white = 0 #white
light_red = 0 #red
button_white_pressed=False
button_red_pressed=False
button_white_status=True
button_red_pressed=False
LED_brightness=255

led = Pin(2, Pin.OUT)

def on_pressed(timer):
    print('button_white_pressed')
    global button_white_pressed
    button_white_pressed=True
    
def on_pressed2(timer):
    print('button_red_pressed')
    global button_red_pressed
    button_red_pressed=True
    
def debounce1(pin):
#    print (pin)
    # Start or replace a timer for 200ms, and trigger on_pressed.
    timer1.init(mode=Timer.ONE_SHOT, period=200, callback=on_pressed)

def debounce2(pin):
#    print (pin)
    # Start or replace a timer for 200ms, and trigger on_pressed.
    timer2.init(mode=Timer.ONE_SHOT, period=200, callback=on_pressed2)

# Register a new hardware timer.
timer1 = Timer(0)
timer2 = Timer(1)

# Setup the button input pin with a pull-up resistor.
button1 = Pin(35, Pin.IN, Pin.PULL_UP)
button2 = Pin(34, Pin.IN, Pin.PULL_UP)

# Register an interrupt on rising button input.
button1.irq(debounce1, Pin.IRQ_RISING)
button2.irq(debounce2, Pin.IRQ_RISING)


# button part end =========================================================================================================
JSONdata="""
{
    "button_red": "-x-",
    "button_white": "-x-",
    "LED_brightness": "-x-",
    "LED_roof": "-x-"
}
"""


while True:
# button part start =========================================================================================================

    time.sleep(.5)
    statechange=0
    # Drehregler abfragen
    
    if light_red == 0 and button_red_pressed == True:
        light_red = LED_brightness
        light_white = 0
        statechange+=1
        print('MAIN light_red ON  light_white OFF')
    elif light_red > 0 and button_red_pressed == True:
        print('MAIN light_red OFF ')
        light_red = 0
        statechange+=1
    elif light_red > 0 and button_red_pressed == False:
        print('MAIN light_red ON LED_brightness ')
#        statechange+=1        

    elif light_white == 0 and button_white_pressed == True and light_red == 0:
        light_white = LED_brightness
        print('MAIN light_white ON ')
        statechange+=1
    elif light_white > 0 and button_white_pressed == True:
        print('MAIN light_white OFF ')
        light_white = 0
        statechange+=1
    elif light_white > 0 and button_white_pressed == False:
        print('MAIN light_white LED_brightness')

    if statechange>0:
        print (f"light_white:{light_white} light_red:{light_red} button_white_pressed:{button_white_pressed} button_red_pressed:{button_red_pressed} LED_brightness:{LED_brightness}")
        s1='{\n"button_red":"'  +  str(light_red) + '",\n'
        s2='"button_white":"'   +  str(light_white) + '",\n'
        s3='"LED_brightness":"' +  str(LED_brightness) + '",\n'
        s4='"LED_roof":"'       +  "NA" + '"\n}\n'
        JSONdata=s1+s2+s3+s4

    button_red_pressed = False
    button_white_pressed = False


#    f = open("data.json", "w")
#    f.write('{' +s1+s2+s3+s4 '}')
#    f.write(demodata)
#    f.close()
# button part end =========================================================================================================



# print webpage =========================================================================================================

    conn, addr = s.accept()
    #print('Got a connection from %s' % str(addr)) 
    request = conn.recv(1024)
    request = str(request)
    #print('Content = %s' % request)
    led_on = request.find('/?led=on')
    led_off = request.find('/?led=off')
    if led_on == 6:
        #print('LED ON')
        led.value(1)
    if led_off == 6:
        #print('LED OFF')
        led.value(0)
    jsonrequest = request.find('data.json')
    if jsonrequest > 4: 
        response = JSONdata
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: application/json\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()
    else:
        response = web_page()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()

