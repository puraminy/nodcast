import curses
import curses.textpad

def validate(ch):
    curses.beep()
    win.addstr(chr(ch).encode("utf-8"))
    return '' 
stdscr = curses.initscr()
# don't echo key strokes on the screen
curses.noecho()
# read keystrokes instantly, without waiting for enter to ne pressed
curses.cbreak()
# enable keypad mode
stdscr.keypad(1)
stdscr.clear()
stdscr.refresh()
win = curses.newwin(3, 60, 5, 10)
tb = curses.textpad.Textbox(win)
text = tb.edit()
curses.beep()
win.addstr(text.encode('utf_8'))
