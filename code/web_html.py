
# html stuff
#import html
def web_page():
  # tnx to https://stackoverflow.com/questions/71111182/myobj-json-parsethis-responsetext-give-an-error-in-my-project
  html = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Sternwarte Huettenlicht</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <link rel="icon" href="data:," />
    <link rel="stylesheet" href="web.css">
    <style>
      .loading {
        display: none;
        font-size: 1.2rem;
        color: #333;
      }
    </style>
  </head>
  <body>
    <h1>ESP Web Server</h1>
    <p class="loading" id="loading">Loading...</p>
    <table>
      <tr>
        <td><p>Licht Rot</p></td>
        <td><p id="button_red"></p></td>
        <td><p><a href="/?red=on"><button class="button">ON</button></a><a href="/?red=off"><button class="button button2">OFF</button></a></p></td>
      </tr>
      <tr>
        <td><p>Licht Weiss</p></td>
        <td><p id="button_white"></p></td>
        <td><p><a href="/?white=on"><button class="button">ON</button></a><a href="/?white=off"><button class="button button2">OFF</button></a></p></td>
      </tr>
      <tr>
        <td><p>Helligkeit</p></td>
        <td><p id="LED_brightness"></p></td>
        <td><p></p></td>
      </tr>
      <tr>
        <td><p>Dach</p></td>
        <td><p id="LED_roof">&nbsp; NA &nbsp;</p></td>
        <td><p>Dach</p></td>
      </tr>
      <!-- RGB Input Section -->
      <tr>
        <td><p>RGB Werte</p></td>
        <td>
          <input type="number" id="red" placeholder="R" min="0" max="255" />
          <input type="number" id="green" placeholder="G" min="0" max="255" />
          <input type="number" id="blue" placeholder="B" min="0" max="255" />
        </td>
        <td>
          <button class="button" onclick="setColor()">Set Color</button>
        </td>
      </tr>
      <tr>
        <td><p>Aktuelle RGB Werte</p></td>
        <td colspan="2"><p id="current_rgb">R: 0, G: 0, B: 0</p></td>
      </tr>
      <tr>
        <td><p>Test LED</p></td>
        <td><p></p></td>
        <td><p><a href="/?led=on"><button class="button">ON</button></a><a href="/?led=off"><button class="button button2">OFF</button></a></p></td>
      </tr>
      <tr>
        <td><p>Network</p></td>
        <td></td>
        <td><p id="network_ip">  </p><p id="network_ssid"></p></td>
      </tr>
    </table>
    
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
              var myobj = JSON.parse(xhr.responseText);
              document.getElementById("button_red").innerText = myobj.button_red;
              document.getElementById("button_white").innerText = myobj.button_white;
              document.getElementById("LED_brightness").innerText = myobj.LED_brightness;
              document.getElementById("LED_roof").innerText = myobj.LED_roof;
              document.getElementById("network_ip").innerText = myobj.network_ip;
              document.getElementById("network_ssid").innerText = myobj.network_ssid;
              document.getElementById("current_rgb").innerText = `R: ${myobj.red}, G: ${myobj.green}, B: ${myobj.blue}`;
            } else {
              console.log("Oh no! There has been an error with the request!");
            }
            document.getElementById("loading").style.display = "none";
          }
        };
        xhr.send();
      }
      function setColor() {
        const red = document.getElementById("red").value;
        const green = document.getElementById("green").value;
        const blue = document.getElementById("blue").value;

        const xhr = new XMLHttpRequest();
        xhr.open("GET", `?r=${red}&g=${green}&b=${blue}`, true);
        xhr.send();
      }

      function toggleLoading() {
        document.getElementById("loading").style.display = "block";
        setTimeout(() => { document.getElementById("loading").style.display = "none"; }, 3000);
      }

      window.setInterval(get_HW_Infos, 1000); // Updates every 5 seconds
    </script>
  </body>
</html>
"""
  return html



def web_css():
    css = """
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

"""
    return css
