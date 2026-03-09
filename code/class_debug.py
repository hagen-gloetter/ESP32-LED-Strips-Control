"""
Lightweight ring-buffer debug logger for MicroPython.

Provides three module-level functions that can be used without
instantiating a class:

- ``debug_init()``  — initialise the buffer
- ``debug()``       — append a message
- ``get_debug_msg()`` — drain the buffer as a newline-separated string

Usage::

    from class_debug import debug_init, debug, get_debug_msg
    debug_init(max_size=100)
    debug(3, __name__, "sensor ready")
    print(get_debug_msg())
"""
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
    Initialise the ring buffer.

    Args:
        the_max_size (int): Maximum number of messages to retain before
            the oldest entry is dropped. Defaults to 100.
    """
    global max_size
    global string_list
    global DebugLevel
    max_size = the_max_size
    string_list = []
    DebugLevel = 4

def debug(level=4, ctx=None, message=None):
    """
    Append a message to the ring buffer if *level* ≤ current DebugLevel.

    Also prints to stdout. If the buffer is full the oldest entry is evicted.
    ``ctx`` and ``message`` are coerced to ``str`` so passing ``None`` is safe.

    Args:
        level (int): Severity (1=error … 4=verbose). Lower is more critical.
        ctx (any): Context label, typically ``__name__``.
        message (any): Message text.
    """
    global max_size
    global string_list
    global DebugLevel
    if level <= DebugLevel:
        if len(string_list) >= max_size:
            string_list.pop(0)  # Entfernt den ältesten String
        output = str(ctx) + " " + str(message)
        print(output)
        string_list.append(output)

def get_debug_msg():
    """
    Drain the buffer and return all messages as a newline-separated string.

    Returns:
        str: All buffered messages concatenated with newlines. The buffer
            is emptied after this call.
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



