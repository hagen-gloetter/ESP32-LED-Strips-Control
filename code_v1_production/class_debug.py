import sys
import time

print("debug Class loaded")

"""
Usage:
# Erstelle eine Instanz der Debug-Klasse
debug = Debug()

# Füge Debug-Nachrichten hinzu
for i in range(10):
    debug.debug(1, "Test", "Debug Message")

# Liste auslesen (wird gleichzeitig geleert)
print("Ausgelesene Debug-Meldungen:", debug.get_debug_msg())

# Prüfen, ob die Liste leer ist
print("Aktuelle Debug-Liste nach dem Auslesen:", debug.get_list())

"""
def debug_init(the_max_size=100):
    """
    Initialisiert die String-Liste und setzt die maximale Größe.
    """
    global max_size
    global string_list
    global DebugLevel
    max_size = the_max_size
    string_list = []
    DebugLevel = 4

def debug(level=4, ctx=None, message=None):
    """
    Fügt einen neuen String zur Liste hinzu. Wenn die maximale Größe erreicht ist,
    wird der älteste String entfernt.
    """
    global max_size
    global string_list
    global DebugLevel
    if level <= DebugLevel:
        if len(string_list) >= max_size:
            string_list.pop(0)  # Entfernt den ältesten String
        output = ctx +" "+ message
        print(output)
        string_list.append(output)

def get_debug_msg():
    """
    Gibt die aktuelle Liste zurück und leert sie danach.
    """
    global string_list
    current_list = [item for item in string_list if item]
    string_list.clear()  # Leert die Liste
    return "\n".join(current_list) + "\n"

# def main():
#     time.sleep_ms(200)

# if __name__ == "__main__":
#     debug = Debug()
#     DebugLevel = 4 
#     debug(4, __name__, "main.py start")
#     sys.exit(main())



