# web_html.py

def web_page():
    html = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Sternwarte Huettenlicht</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
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
        <td><p><a href="/?white=on"><button class="button">ON</button></a><a href="/?white=off"><button class="button button2">OFF"></button></a></p></td>
      </tr>
      <tr>
        <td><p>RGB Werte</p></td>
        <td>
          <input type="number" id="red" placeholder="R" min="1" max="1024" />
          <input type="number" id="green" placeholder="G" min="1" max="1024" />
          <input type="number" id="blue" placeholder="B" min="1" max="1024" />
        </td>
        <td>
          <button class="button" onclick="setColor()">Set Color</button>
        </td>
      </tr>
      <tr>
        <td><p>Aktuelle RGB Werte</p></td>
        <td colspan="2"><p id="current_rgb">R: 0, G: 0, B: 0</p></td>
      </tr>
    </table>

    <script>
      function get_HW_Infos() {
        const xhr = new XMLHttpRequest();
        xhr.open("GET", "data.json", true);
        xhr.onreadystatechange = function () {
          if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            var data = JSON.parse(xhr.responseText);
            document.getElementById("button_red").innerText = data.button_red;
            document.getElementById("button_white").innerText = data.button_white;
            document.getElementById("LED_brightness").innerText = data.LED_brightness;
            document.getElementById("current_rgb").innerText = `R: ${data.red}, G: ${data.green}, B: ${data.blue}`;
          }
        };
        xhr.send();
      }

      function setColor() {
        const red = document.getElementById("red").value;
        const green = document.getElementById("green").value;
        const blue = document.getElementById("blue").value;
        const xhr = new XMLHttpRequest();
        xhr.open("GET", `/?r=${red}&g=${green}&b=${blue}`, true);
        xhr.send();
      }

      setInterval(get_HW_Infos, 5000);
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
