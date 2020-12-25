import sys
import os
import curses as cur
import locale
import sys
import string
import textwrap
#locale.setlocale(locale.LC_ALL, '')
code = "utf-8" #locale.getpreferredencoding()

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


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

import nodcast as nc
def m_print(text, win, color, attr = None, end="\n", refresh = False):
    if win is None:
        print(text, end=end)
    else:
        color = int(color)
        c = cur.color_pair(color)
        if attr is not None:
            c = cur.color_pair(color) | attr
        height, width = win.getmaxyx()
        #win.addnstr(text + end, height*width-1, c)
        #text = textwrap.shorten(text, width=height*width-5)
        win.addstr((text + end).encode(code), c)
        if not refresh:
            pass #win.refresh(0,0, 0,0, height -5, width)
        else:
            #win.refresh()
            pass

def print_there(x, y, text, win = None, color=0, attr = None, pad = False):
    if win is not None:
        c = cur.color_pair(color)
        if attr is not None:
            c = cur.color_pair(color) | attr
        height, width = win.getmaxyx()
        #win.addnstr(x, y, text, height*width-1, c)
        _len = (height*width)-x
        win.addstr(x, y, text[:_len].encode(code), c)
        if pad:
            pass #win.refresh(0,0, x,y, height -5, width)
        else:
            pass # win.refresh()
    else:
        sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
        sys.stdout.flush()

def clear_screen(win = None):
    if win is not None:
        win.erase()
        win.refresh()
    else:
        os.system('clear')
def rinput(win, r, c, prompt_string, default=""):
    show_cursor()
    cur.echo() 
    win.addstr(r, c, prompt_string.encode(code))
    win.refresh()
    input = win.getstr(r, len(prompt_string), 30)
    clear_screen(win)
    hide_cursor()
    try:
        inp = input.decode(code)  
        cur.noecho()
        return inp
    except:
        hide_cursor()
        cur.noecho()
        return default

def minput(mwin, row, col, prompt_string, exit_on = [], default="", mode = 0, footer="", color=nc.HL_COLOR):
    multi_line = mode == 2
    if mode > 0:
        mrows, mcols = mwin.getmaxyx()
        mwin.border()
        print_there(row, col, prompt_string, mwin)
        if footer == "":
            footer =  "Insert: Insert | ESC: Close | Shift + Del: Clear | Shift + Left: Delete line"
            footer = textwrap.shorten(footer, mcols)
        if mode == 2:
            print_there(mrows-1, col, footer, mwin)
            win = mwin.derwin(mrows - 2, mcols-2, 1, 1)
        else:
            print_there(mrows-1, col, footer, mwin)
            win = mwin.derwin(mrows - 2, mcols-2, 1, 1)
        win.bkgd(' ', cur.color_pair(color))  # | cur.A_REVERSE)
        mwin.refresh()
    else:
        win = mwin
        attr = cur.A_BOLD
        c = cur.color_pair(color) | attr
        win.addstr(row, col, prompt_string.encode(code), c)
        win.clrtobot()
    rows, cols = win.getmaxyx()
    if not multi_line:
        exit_on = ['\n']
        next_line = "+"
    else:
        next_line = '\n'
        if not exit_on:
            exit_on = ['\t']
    show_cursor()
    cur.noecho() 
    win.keypad(True)
    out = default.split('\n')
    out = list(filter(None, out))
    #out = out[:rows]
    #inp = "\n".join(out) 
    inp = default
    pos = len(inp)
    ch = 0
    rtl = False
    start_line = 0
    max_lines = 40
    row, col = win.getyx()
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
            r = row
            if len(out) > 1:
                pass
            c = 0
            yloc = r
            xloc = pos - c
            for i, l in enumerate(out):
                enters = inp.count("\n", c, c + len(l) + 1)
                if pos >= c and pos <= c + len(l):
                    yloc = r
                    xloc = pos - c 
                r += 1
                c += len(l) + enters 
            start_line = max(0, yloc - rows + 1) 
            for ii,l in enumerate(out[start_line:]):
                if ii < rows:
                   if rtl and False:
                       start = cols - len(l)-2
                   win.addstr(ii, start, l.encode(code))
                win.clrtoeol()
            win.clrtobot()
        else:
            win.addstr(row, start, inp.encode(code))
            win.clrtoeol()
            xloc = start + pos
            yloc = row + (xloc // cols)
            xloc = xloc % cols
        if yloc < rows:
            win.move(yloc, xloc)
        else:
            win.move(rows -1 , xloc)
        ch = win.get_wch()
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
        elif ch == cur.KEY_SDC:
            inp = ""
            pos = 0
        elif ch == cur.KEY_SLEFT:
            if len(inp) > 0:
                temp = inp.split("\n")
                c = 0
                inp = ""
                for line in temp:
                    if pos >= c and pos < c + len(line):
                        pos -= min(xloc, len(line) - 1)
                    else:
                        inp += line + "\n"
                    c += len(line)
                inp = inp.strip("\n")
        elif multi_line and type(ch) == str and ch == next_line:
            enters = inp.count("\n")
            if enters < max_lines - 1:
                inp = inp[:pos] + "\n" + inp[pos:]
                pos += 1
            else:
                mbeep()
                print_there(mrows-1, col, f"You reached the maximum number of {max_lines} lines", mwin, color=nc.WARNING_COLOR)
                mwin.clrtoeol()
                mwin.get_wch()
                print_there(mrows-1, col, footer, mwin)
                mwin.refresh()
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
            if yloc < 1:
                mbeep()
            else:
                pos = 0
                for i in range(0, yloc - 1):
                    pos += len(out[i])
                enters = inp.count("\n", 0, pos + yloc - 1)
                pos += enters
                pos += min(xloc, len(out[yloc - 1]))
        elif ch == cur.KEY_DOWN:
            if not multi_line:
                break
            if yloc >= max_lines - 1 or yloc >= len(out) - 1:
                mbeep()
            else:
                pos = 0
                for i in range(0, yloc + 1):
                    pos += len(out[i])
                enters = inp.count("\n", 0, pos + yloc + 1)
                pos += enters
                pos += min(xloc, len(out[yloc + 1]))
        elif type(ch) == str and len(ch) == 1 and  ord(ch) == 27:
            hide_cursor()
            cur.noecho()
            return "<ESC>",ch
        elif ch == cur.KEY_IC:
            break
        else:
            letter = ch
            if ch in exit_on:
                break
            else:
                inp = inp[:pos] + str(letter) + inp[pos:]
                pos += 1
    cur.noecho()
    hide_cursor()
    return inp, ch

def mbeep(repeat=1):
    if os.name == "nt":
        winsound.Beep(500, 100)
    else:
        cur.beep()

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

def split_into_sentences(text, debug = False, limit = 15, split_on = ['.','?','!']):
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
    for ch in split_on:
        text = text.replace(ch, ch + "<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = list(filter(None, sentences))
    sentences = [s.strip() for s in sentences if s.strip()  and len(s) >= limit]
    return sentences
