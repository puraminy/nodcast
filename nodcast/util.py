import sys
import os
import curses as cur
import locale
import sys
import textwrap
#locale.setlocale(locale.LC_ALL, '')
code = "utf-8" #locale.getpreferredencoding()

if os.name == 'nt':
    import ctypes
    from ctypes import POINTER, WinDLL, Structure, sizeof, byref
    from ctypes.wintypes import BOOL, SHORT, WCHAR, UINT, ULONG, DWORD, HANDLE

    import subprocess
    import msvcrt
    import winsound

    from ctypes import wintypes

def fix_borders():
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    hWnd = kernel32.GetConsoleWindow()
    win32gui.SetWindowLong(hWnd, win32con.GWL_STYLE, 
            win32gui.GetWindowLong(hWnd, win32com.GWL_STYLE) & win32con.WS_MAXIMIZEBOX & win32con.WS_SIZEBOX)


def maximize_console(lines=None):
    if os.name == "nt":
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        hWnd = kernel32.GetConsoleWindow()
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        user32.ShowWindow(hWnd, 1)
        subprocess.check_call('mode.com con cols=124 lines=29')

    #kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    #user32 = ctypes.WinDLL('user32', use_last_error=True)

    #SW_MAXIMIZE = 3

    #kernel32.GetConsoleWindow.restype = wintypes.HWND
    #kernel32.GetLargestConsoleWindowSize.restype = wintypes._COORD
    #kernel32.GetLargestConsoleWindowSize.argtypes = (wintypes.HANDLE,)
    #user32.ShowWindow.argtypes = (wintypes.HWND, ctypes.c_int)
    #fd = os.open('CONOUT$', os.O_RDWR)
    #try:
    #    hCon = msvcrt.get_osfhandle(fd)
    #    max_size = kernel32.GetLargestConsoleWindowSize(hCon)
    #    if max_size.X == 0 and max_size.Y == 0:
    #        raise ctypes.WinError(ctypes.get_last_error())
    #finally:
    #    os.close(fd)
    #cols = max_size.X
    #hWnd = kernel32.GetConsoleWindow()
    #if cols and hWnd:
    #    if lines is None:
    #        lines = max_size.Y
    #    else:
    #        lines = max(min(lines, 9999), max_size.Y)

def resize_font_on_windows(height, get_size = False):
    LF_FACESIZE = 32
    STD_OUTPUT_HANDLE = -11

    class COORD(Structure):
        _fields_ = [
            ("X", SHORT),
            ("Y", SHORT),
        ]


    class CONSOLE_FONT_INFOEX(Structure):
        _fields_ = [
            ("cbSize", ULONG),
            ("nFont", DWORD),
            ("dwFontSize", COORD),
            ("FontFamily", UINT),
            ("FontWeight", UINT),
            ("FaceName", WCHAR * LF_FACESIZE)
        ]


    kernel32_dll = WinDLL("kernel32.dll")

    get_last_error_func = kernel32_dll.GetLastError
    get_last_error_func.argtypes = []
    get_last_error_func.restype = DWORD

    get_std_handle_func = kernel32_dll.GetStdHandle
    get_std_handle_func.argtypes = [DWORD]
    get_std_handle_func.restype = HANDLE

    get_current_console_font_ex_func = kernel32_dll.GetCurrentConsoleFontEx
    get_current_console_font_ex_func.argtypes = [HANDLE, BOOL, POINTER(CONSOLE_FONT_INFOEX)]
    get_current_console_font_ex_func.restype = BOOL

    set_current_console_font_ex_func = kernel32_dll.SetCurrentConsoleFontEx
    set_current_console_font_ex_func.argtypes = [HANDLE, BOOL, POINTER(CONSOLE_FONT_INFOEX)]
    set_current_console_font_ex_func.restype = BOOL

    # Get stdout handle
    stdout = get_std_handle_func(STD_OUTPUT_HANDLE)
    if not stdout:
        return ("{:s} error: {:d}".format(get_std_handle_func.__name__, get_last_error_func()))
    # Get current font characteristics
    font = CONSOLE_FONT_INFOEX()
    font.cbSize = sizeof(CONSOLE_FONT_INFOEX)
    res = get_current_console_font_ex_func(stdout, False, byref(font))
    if not res:
        return ("{:s} error: {:d}".format(get_current_console_font_ex_func.__name__, get_last_error_func()))
    # Display font information
    for field_name, _ in font._fields_:
        field_data = getattr(font, field_name)
        if field_name == "dwFontSize" and get_size:
            return field_data.Y
    # Alter font height
    font.dwFontSize.X = 10  # Changing X has no effect (at least on my machine)
    font.dwFontSize.Y = height
    # Apply changes
    res = set_current_console_font_ex_func(stdout, False, byref(font))
    if not res:
        return("{:s} error: {:d}".format(set_current_console_font_ex_func.__name__, get_last_error_func()))
    # Get current font characteristics again and display font size
    res = get_current_console_font_ex_func(stdout, False, byref(font))
    if not res:
        return("{:s} error: {:d}".format(get_current_console_font_ex_func.__name__, get_last_error_func()))
    return ""

if os.name == 'nt':
    import msvcrt

    class _CursorInfo(ctypes.Structure):
        _fields_ = [("size", ctypes.c_int),
                    ("visible", ctypes.c_byte)]

def hide_cursor(useCur = True):
    if useCur:
        cur.curs_set(0)
    elif os.name == 'nt':
        ci = _CursorInfo()
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
        ci.visible = False
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
    elif os.name == 'posix':
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

def show_cursor(useCur = True):
    if useCur:
        cur.curs_set(1)
    elif os.name == 'nt':
        ci = _CursorInfo()
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
        ci.visible = True
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
    elif os.name == 'posix':
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

def mprint(text, stdscr =None, color=0, attr = None, end="\n", refresh = False):
    if stdscr is None:
        print(text, end=end)
    else:
        c = cur.color_pair(color)
        if attr is not None:
            c = cur.color_pair(color) | attr
        height, width = stdscr.getmaxyx()
        #stdscr.addnstr(text + end, height*width-1, c)
        #text = textwrap.shorten(text, width=height*width-5)
        stdscr.addstr((text + end).encode(code), c)
        if not refresh:
            pass #stdscr.refresh(0,0, 0,0, height -5, width)
        else:
            #stdscr.refresh()
            pass

def print_there(x, y, text, stdscr = None, color=0, attr = None, pad = False):
    if stdscr is not None:
        c = cur.color_pair(color)
        if attr is not None:
            c = cur.color_pair(color) | attr
        height, width = stdscr.getmaxyx()
        #stdscr.addnstr(x, y, text, height*width-1, c)
        _len = (height*width)-x
        stdscr.addstr(x, y, text[:_len].encode(code), c)
        if pad:
            pass #stdscr.refresh(0,0, x,y, height -5, width)
        else:
            pass # stdscr.refresh()
    else:
        sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
        sys.stdout.flush()

def clear_screen(stdscr = None):
    if stdscr is not None:
        stdscr.erase()
        stdscr.refresh()
    else:
        os.system('clear')
def rinput(stdscr, r, c, prompt_string, default=""):
    show_cursor()
    cur.echo() 
    stdscr.addstr(r, c, prompt_string.encode(code))
    stdscr.refresh()
    input = stdscr.getstr(r, len(prompt_string), 30)
    clear_screen(stdscr)
    hide_cursor()
    try:
        inp = input.decode(code)  
        cur.noecho()
        return inp
    except:
        hide_cursor()
        cur.noecho()
        return default


def get_confirm(win, msg, acc = ['y','n']):
    win.erase()
    print_there(0,1, msg, win) 
    ch = 0
    while chr(ch) not in acc:
        ch = win.getch()
        if not ch in acc:
            mbeep()
        else:
            break
    win.clear()
    win.refresh()
    return chr(ch).lower()

def minput(stdscr, row, col, prompt_string, exit_on = [], default="", multi_line = False):
    rows, cols = stdscr.getmaxyx()
    caps = rows*(cols -2) - col - len(prompt_string) - 2
    if not multi_line:
        exit_on = ['\n']
        next_line = ">"
    else:
        next_line = '\n'
        if not exit_on:
            exit_on = ['\t']
    show_cursor()
    cur.noecho() 
    stdscr.keypad(True)
    stdscr.addstr(row, col, prompt_string.encode(code))
    stdscr.clrtoeol()
    stdscr.refresh()
    out = default.split('\n')
    out = list(filter(None, out))
    line = 0
    if out:
        inp = str(out[0])
    else:
        inp = default
        out.append(inp)
    pos = len(inp)
    ch = 0
    rtl = False
    if not multi_line:
        start = col + len(prompt_string)
    else:
        start = col
    while ch not in exit_on:
        if rtl:
            cur.curs_set(0)
        pos = max(pos, 0)
        pos = min(pos, len(inp))
        if multi_line:
            text = inp
            out = []
            temp = text.split("\n")
            for line in temp:
                if  len(line) < cols - 2:
                    out += [line]
                else:
                    out += textwrap.wrap(line, width = cols -2, break_long_words=False, replace_whitespace=False, drop_whitespace=False)
            #out = filter(None, out)
            if not out:
                out = [""]
            r = row + 1
            if len(out) > 1:
                pass
            c = 0
            yloc = r
            xloc = pos - c + 1
            for i, l in enumerate(out):
                enters = inp.count("\n", c, c + len(l) + 1)
                if pos >= c and pos <= c + len(l):
                    yloc = r
                    xloc = pos - c + 1
                if r < rows and start + len(l) < cols:
                   if rtl and False:
                       start = cols - len(l)-2
                   stdscr.addstr(r, start, l.encode(code))
                stdscr.clrtoeol()
                r += 1
                c += len(l) + enters 
            stdscr.clrtobot()
        else:
            stdscr.addstr(row, start, inp.encode(code))
            stdscr.clrtoeol()
            xloc = start + pos
            yloc = row + (xloc // cols)
            xloc = xloc % cols
        if yloc < rows and xloc < cols:
            stdscr.move(yloc, xloc)
        ch = stdscr.get_wch()
        if type(ch) == str and ord(ch) == 127: # ch == 8 or ch == 127 or ch == cur.KEY_BACKSPACE:
            if pos > 0:
                inp = inp[:pos-1] + inp[pos:]
                pos -= 1
            else:
                mbeep()
        elif ch == cur.KEY_DC:
            if pos < len(inp):
                inp = inp[:pos] + inp[pos+1:]
            else:
                mbeep()
        elif ch == cur.KEY_IC:
            #rtl = not rtl
            pass
        elif ch == cur.KEY_SDC:
            if not multi_line:
                inp = ""
                pos = 0
            elif len(inp) > 0:
                temp = inp.split("\n")
                c = 0
                inp = ""
                for line in temp:
                    if pos >= c and pos < c + len(line):
                        pos -= len(line)
                    else:
                        inp += line + "\n"
                    c += len(line)
        elif multi_line and type(ch) == str and ch == next_line:
            inp = inp[:pos] + "\n" + inp[pos:]
            pos += 1
        elif ch == cur.KEY_HOME:
            pos = 0
        elif ch == cur.KEY_END:
            pos = len(inp)
        elif ch == cur.KEY_LEFT:
            if pos > 0:
                pos -= 1 
            else:
                mbeep()
        elif ch == cur.KEY_RIGHT:
            pos += 1
        elif ch == cur.KEY_UP: 
            if not multi_line:
                break
            if yloc <= 2:
                mbeep()
            else:
                pos = 0
                for i in range(0, yloc - 3):
                    pos += len(out[i])
                enters = inp.count("\n", 0, pos + yloc - 3)
                pos += enters
                pos += min(xloc, len(out[yloc -3])) - 1
        elif ch == cur.KEY_DOWN:
            if not multi_line:
                break
            if yloc >= rows or yloc - 1 >= len(out):
                mbeep()
            else:
                pos = 0
                for i in range(0, yloc - 1):
                    pos += len(out[i])
                enters = inp.count("\n", 0, pos + yloc - 1)
                pos += enters
                pos += min(xloc, len(out[yloc -1])) - 1
        elif ch == 27:
            hide_cursor()
            cur.noecho()
            return "<ESC>",ch
        else:
            letter = ch
            if len(inp) >= caps:
                mbeep()
            elif ch in exit_on:
                break
            else:
                inp = inp[:pos] + letter + inp[pos:]
                pos += 1
    cur.noecho()
    hide_cursor()
    return inp, ch

def mbeep(repeat=1):
    if os.name == "nt":
        winsound.Beep(500, 100)
    else:
        cur.beep()

def get_key(stdscr = None):
    ch1 = stdscr.getch()
    return ch1

# -*- coding: utf-8 -*-
import re
alphabets= "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"
digits = "([0-9]+)"

def rplit_into_sentences(text):
    sents = nltk.sent_tokenize(text)
    return sents

def qplit_into_sentences(text):
    try:
        import nltk
        try:
            sents = nltk.sent_tokenize(text)
            return sents
        except LookupError:
            nltk.download('punkt')
            sents = nltk.sent_tokenize(text)
            return sents
    except ImportError as e:
        return rplit_into_sentences(text)

def split_into_sentences(text, debug = False, limit = 2):
    text = " " + text + "  "
    text = text.replace("\n","<stop>")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    text = text.replace("[FRAG]","<stop>")
    text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = text.replace("et al.","et al<prd>")
    text = text.replace("e.g.","e<prd>g<prd>")
    text = text.replace("vs.","vs<prd>")
    text = text.replace("etc.","etc<prd>")
    text = text.replace("i.e.","i<prd>e<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" (\d+)[.](\d+) "," \\1<prd>\\2 ",text)
    text = text.replace("...","<prd><prd><prd>")
    text = re.sub(digits + "[.]" + digits,"\\1<prd>\\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    if len(sentences) > 1:
        sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences if len(s) > limit]
    return sentences
