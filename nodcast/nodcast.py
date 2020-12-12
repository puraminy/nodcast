# Nodcast v 0.1.2
import requests
import io
import platform
import webbrowser
import time
import string
from time import sleep
import datetime
import pickle
import textwrap
import json
import urllib.request
try:
    from nodcast.util import *
except:
    from util import *
import curses as cur
from curses import wrapper
from curses import textpad
from pathlib import Path
from urllib.parse import urlparse
from appdirs import *
import logging, sys
import traceback
import subprocess

appname = "Checkideh"
appauthor = "App"
user = 'na'
profile = "---"

hotkey = ""
old_hotkey = "non-blank"
def get_key(win = None):
    global hotkey, old_hotkey
    if hotkey == old_hotkey:
       hotkey = ""
       old_hotkey = "non-blank"
    if hotkey == "":
        ch = win.getch()
    else:
        old_hotkey = hotkey
        ch, hotkey = ord(hotkey[0]), hotkey[1:]
    return ch

show_instruct = True
#Windows 
menu_win = None
common_subwin = None
list_win = None
text_win = None

doc_path = os.path.expanduser('~/Documents/Checkideh')
app_path = user_data_dir(appname, appauthor)
logFilename = "log_file.log" #app_path + '/log_file.log'
Path(app_path).mkdir(parents=True, exist_ok=True)
logging.basicConfig(filename=logFilename, level=logging.DEBUG)


def handle_exception(exc_type, exc_value, exc_traceback):
    import sys
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    exc_info = (exc_type, exc_value, exc_traceback)
    logging.critical("\nDate:" + str(datetime.datetime.now()), exc_info=(exc_type, exc_value, exc_traceback))
    print("An error occured, check log file at ", app_path, " to see the error details.")
    traceback.print_exception(*exc_info)


sys.excepthook = handle_exception

newspaper_imported = True
try:
    import newspaper
except ImportError as e:
    newspaper_imported = False

std = None
theme_menu = {}
theme_options = {}
template_menu = {}
template_options = {}

conf = {}
page = 0
query = ""
filters = {}

DOWN = cur.KEY_DOWN
UP = cur.KEY_UP
LEFT = cur.KEY_LEFT
RIGHT = cur.KEY_RIGHT
SLEFT = cur.KEY_SLEFT
SRIGHT = cur.KEY_SRIGHT
SUP = 337
SDOWN = 336

nod_colors = {
    "yes": 77,
    "OK": 36,
    "OK, I get it now": 36,
    "I agree!": 22,
    "background": 93,
    "archive": 145,
    "okay": 36,
    "okay, okay!": 25,
    "okay?": 180,
    "not reviewed": 143,
    "goal": 22,
    "got an idea!": 32,
    "skipped": 245,
    "skip": 245,
    "I see!": 71,
    "interesting!": 76,
    "favorite!": 219,
    "interesting, so?": 76,
    "proposed solution": 32,
    "contribution": 77,
    "feature": 77,
    "constraint": 97,
    "important!": 141,
    "point!": 142,
    "main idea!": 142,
    "has an idea!": 115,
    "didn't get!": 161,
    "didn't get": 161,
    "unclear": 161,
    "question": 161,
    "didn't get the article": 161,
    "didn't get, needs review": 161,
    "what?!": 161,
    "what?! needs review": 161,
    # "didn't get, but okay":199,
    "don't think so": 179,
    "not sure!": 179,
    "didn't get, but okay": 179,
    "didn't get, so?": 196,
    "so?": 39,
    "Let's continue": 39,
    "continue": 39,
    "okay, continue": 39,
    "okay, so?": 39,
    "almost got the idea?": 32,
    "explain more": 178,
    "why?": 59,
    "needs review": 177,
    "review later": 177,
    "to read later": 177,
    "needs research": 186,
    "problem": 179,
    "definition": 250,
    "got it!": 69,
    "got the idea!": 69,
}

cW = 7
cR = 1
cG = 30
cY = 5
cB = 27
clB = 33
cPink = 15
cC = 9
clC = 16
clY = 13
cGray = 10
clGray = 250
clG = 12
cllC = 83
cO = 94
back_color = None

TEXT_COLOR = 35 
ITEM_COLOR = 32 
TITLE_COLOR = 30
DIM_COLOR = 233
COMMENT_COLOR = 39

CUR_ITEM_COLOR = 100
HL_COLOR = 101
INPUT_COLOR = 102
INFO_COLOR = 103
ERR_COLOR = 104
MSG_COLOR = 105
WARNING_COLOR = 106
TEMP_COLOR = 107
TEMP_COLOR2 = 108
SEL_ITEM_COLOR = 109

color_map = {
    "cur-item-color": CUR_ITEM_COLOR,
    "sel-item-color": SEL_ITEM_COLOR,
    "highlight-color": HL_COLOR,
    "hl-text-color": HL_COLOR,
    "back-color": TEXT_COLOR,
    "input-color": INPUT_COLOR,
}

def reset_colors(theme, bg=None):
    global back_color, TEXT_COLOR, ITEM_COLOR, SEL_ITEM_COLOR, TITLE_COLOR, DIM_COLOR, color_map
    if bg is None:
        bg = int(theme["back-color"])
    back_color = bg
    for each in range(1, min(256, cur.COLORS)):
        cur.init_pair(each, each, bg)
    TEXT_COLOR = int(theme["text-color"])
    ITEM_COLOR = int(theme["item-color"]) 
    TITLE_COLOR = int(theme["title-color"])
    DIM_COLOR =  int(theme["dim-color"]) 

    cur.init_pair(CUR_ITEM_COLOR, bg, int(theme["cur-item-color"]) % cur.COLORS)
    cur.init_pair(SEL_ITEM_COLOR, bg, int(theme["sel-item-color"]) % cur.COLORS)
    cur.init_pair(INPUT_COLOR, TEXT_COLOR, int(theme["input-color"]) % cur.COLORS)
    if theme["inverse-highlight"] == "True":
        cur.init_pair(HL_COLOR, int(theme["hl-text-color"]) % cur.COLORS,
                      int(theme["highlight-color"]) % cur.COLORS)
    else:
        cur.init_pair(HL_COLOR, int(theme["highlight-color"]) % cur.COLORS,
                      int(theme["hl-text-color"]) % cur.COLORS)
    cur.init_pair(ERR_COLOR, cW, cR % cur.COLORS)
    cur.init_pair(MSG_COLOR, cW, clB % cur.COLORS)
    cur.init_pair(INFO_COLOR, 235, cG % cur.COLORS)
    cur.init_pair(WARNING_COLOR, cW, cO % cur.COLORS)

def is_enter(ch):
    return ch == cur.KEY_ENTER or ch == 10 or ch == 13

def scale_color(value, factor=1):
    value = float(value)
    if value == 0:
        return int(theme_menu["text-color"])
    elif value < 10:
        return int(theme_menu["didn't get"])
    elif value < 20:
        return int(theme_menu["didn't get"])
    elif value < 30:
        return int(theme_menu[continue_nod])
    elif value < 40:
        return int(theme_menu[continue_nod])
    elif value < 50:
        return int(theme_menu["OK, I get it now"])
    elif value < 60:
        return int(theme_menu["okay"])
    elif value < 70:
        return int(theme_menu["okay"])
    elif value < 80:
        return int(theme_menu["interesting!"])
    else:
        return int(theme_menu["interesting!"])


def platform_open(filepath):
    if platform.system() == 'Darwin':  # macOS
        subprocess.call(('open', filepath),stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif platform.system() == 'Windows':  # Windows
        os.startfile(filepath)
    else:  # linux variants
        subprocess.call(('xdg-open', filepath),stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def openFile(filepath):
    _file = Path(filepath)
    if _file.is_file():
        platform_open(filepath)
        show_msg("File was opened externally")
    else:
        show_err(str(filepath) + " doesn't exist, you can download it by hitting d key")


def delete_file(art):
    if "save_folder" in art:
        fname = art["save_folder"]
    else:
        title = art["title"]
        file_name = title.replace(' ', '-')[:50] + ".pdf"  # url.split('/')[-1]
        folder = doc_path
        if folder.endswith("/"):
            folder = folder[:-1]

        fname = folder + "/" + file_name
    _file = Path(fname)
    if _file.is_file():
        _file.unlink()
        show_info("File was deleted")
    else:
        show_info("File wasn't found on computer")


def download(url, art, folder):
    if not url.endswith("pdf"):
        webbrowser.open(url)
        return

    title = art["title"]
    file_name = title.replace(' ', '-')[:50] + ".pdf"  # url.split('/')[-1]

    folder = doc_path + '/Articles/' + folder    
    # Streaming, so we can iterate over the response.

    if folder.endswith("/"):
        folder = folder[:-1]

    Path(folder).mkdir(parents=True, exist_ok=True)

    fname = folder + "/" + file_name
    _file = Path(fname)
    if _file.is_file():
        openFile(_file)
        art["save_folder"] = str(_file)
    else:
        show_info("Starting download ... please wait")
        sleep(0.1)
        with urllib.request.urlopen(url) as Response:
            Length = Response.getheader('content-length')
            BlockSize = 1000000  # default value

            if not Length:
                show_err("ERROR, zero file size,  something went wrong")
                return
            else:
                Length = int(Length)
                BlockSize = max(4096, Length // 20)

            show_info("UrlLib len, blocksize: " + str(Length) + " " + str(BlockSize))

            BufferAll = io.BytesIO()
            Size = 0
            try:
                while True:
                    BufferNow = Response.read(BlockSize)
                    if not BufferNow:
                        break
                    BufferAll.write(BufferNow)
                    Size += len(BufferNow)
                    if Length:
                        Percent = int((Size / Length) * 100)
                        show_info(f"download: {Percent}% {url} | Ctrl + C to cancel")

                _file.write_bytes(BufferAll.getvalue())
                show_info("File was written to " + str(_file))
                art["save_folder"] = str(_file)
                openFile(_file)

            except Exception as e:
                show_err("ERROR:" + str(e))
            except KeyboardInterrupt:
                show_info("loading canceled")


def save_obj(obj, name, directory, data_dir=True, common=False):
    if obj is None or name.strip() == "":
        logging.info(f"Empty object to save: {name}")
        return
    if not data_dir or name.startswith("chk_def_"):
        folder = directory
    elif common:
        folder = user_data_dir(appname, appauthor) + "/" + directory  
    else:
        folder = user_data_dir(appname, appauthor) + "/profiles/" + profile + "/" + directory
    if folder.endswith("/"):
        folder = folder[:-1]
    Path(folder).mkdir(parents=True, exist_ok=True)
    with open(folder + '/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name, directory, default=None, data_dir=True, common =False):
    if not data_dir:
        folder = directory
    elif common:
        folder = user_data_dir(appname, appauthor) + "/" + directory  
    else:
        folder = user_data_dir(appname, appauthor) + "/profiles/" + profile + "/" + directory

    if folder.endswith("/"):
        folder = folder[:-1]
    fname = folder + '/' + name + '.pkl'
    obj_file = Path(fname)
    if not obj_file.is_file():
        return default
    with open(fname, 'rb') as f:
        return pickle.load(f)


def is_obj(name, directory, common = False):
    if common:
        folder = user_data_dir(appname, appauthor) + "/" + directory  
    else:
        folder = user_data_dir(appname, appauthor) + "/profiles/" + profile + "/" + directory
    if folder.endswith("/"):
        folder = folder[:-1]
    if not name.endswith('.pkl'):
        name = name + '.pkl'
    fname = folder + '/' + name
    obj_file = Path(fname)
    if not obj_file.is_file():
        return False
    else:
        return True


def del_obj(name, directory, common = False):
    if common:
        folder = user_data_dir(appname, appauthor) + "/" + directory  
    else:
        folder = user_data_dir(appname, appauthor) + "/profiles/" + profile + "/" + directory
    if folder.endswith("/"):
        folder = folder[:-1]
    if not name.endswith('.pkl'):
        name = name + '.pkl'
    fname = folder + '/' + name
    obj_file = Path(fname)
    if not obj_file.is_file():
        return None
    else:
        obj_file.unlink()


def get_index(articles, art):
    i = 0
    for a in articles:
        if a["id"] == art["id"]:
            return i
        i += 1
    return -1

def get_article(articles, art_id):
    for a in articles:
        if a["id"] == art_id:
            return a
    return None


def remove_article_list(articles, art):
    i = get_index(articles, art)
    if i >= 0:
        articles.pop(i)

def remove_article(articles, art):
    del articles[art["id"]]

def insert_article_list(articles, art):
    i = get_index(articles, art)
    if i < 0:
        articles.insert(0, art)
    else:
        articles.pop(i)
        articles.insert(0, art)

def insert_article(articles, art):
    articles[art["id"]] = art

def update_article(articles, art):
    insert_article(articles, art)


def get_title(text, default="No title"):
    text = text.strip()
    text = "\n" + text
    parts = text.split("\n# ")
    if len(parts) > 1:
        part = parts[1]
        end = part.find("\n")
        return part[:end], end + 2
    else:
        return default, -1


def get_sects(text):
    text = text.strip()
    text = "\n" + text
    sects = text.split("\n## ")
    ret = []
    if len(sects) == 1:
        new_sect = {}
        new_sect["title"] = "all"
        new_sect["fragments"] = get_frags(sects[0])
        ret.append(new_sect)
    else:
        for sect in sects[1:]:
            new_sect = {}
            end = sect.find("\n")
            new_sect["title"] = sect[:end]
            frags = sect[end:]
            new_sect["fragments"] = get_frags(frags)
            ret.append(new_sect)
    return ret


def get_frags(text, single_unit =False):
    text = text.strip()
    parts = text.split("\n")
    parts = list(filter(None, parts))
    frags = []
    for t in parts:
        frag = {"text":t}
        frag["sents"] = init_frag_sents(t, single_unit)
        frags.append(frag)
    return frags


def remove_tag(art, fid, saved_articles):
    if "tags" in art:
        for i, tag in enumerate(art["tags"]):
            if tag == fid:
                art["tags"].pop(i)
                update_article(saved_articles, art)
                save_obj(saved_articles, "saved_articles", "articles")
                break


def request(p=0):
    global page
    show_info("Searching ... please wait...")
    page = int(p)
    size = 15
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Mobile Safari/537.36',
        'Content-Type': 'application/json',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    size = int(size)
    filters_str = json.dumps(filters)
    data = f'{{"query":"{query}","filters":{filters_str},"page":{page},"size":{size},"sort":null,"sessionInfo":""}}'
    data2 = f'{{"user":"{user}","query":"{query}","filters":{filters_str},"page":{page},"size":{size},"sort":null,"sessionInfo":""}}'

    item = 'https://dimsum.eu-gb.containers.appdomain.cloud/api/scholar/search'
    # item = ''
    # try:
    #    response = requests.post('http://checkideh.com/search.php', headers=headers, data=data)
    #    item = response.json()["a"]
    #    show_msg(str(item))
    # except:
    #    pass
    try:
        response = requests.post(item, headers=headers, data=data)
    except requests.exceptions.HTTPError as errh:
        return [], ("Http Error:" + str(errh))
    except requests.exceptions.ConnectionError as errc:
        return [], ("Error Connecting:" + str(errc))
    except requests.exceptions.Timeout as errt:
        return [], ("Timeout Error:" + str(errt))
    except requests.exceptions.RequestException as err:
        return [], ("OOps: Something Else" + str(err))

    try:
        rsp = response.json()['searchResults']['results'], ""
    except:
        return [], "Corrupt or no response...."
    return rsp, ""

# lll
def list_articles(in_articles, fid, show_note=False, group="", filter_note="", note_index=0, sel_art=None, search_results = False):
    global template_menu, theme_menu, hotkey
    clear_screen(std)

    if sel_art != None:
        show_article(sel_art)

    rows, cols = std.getmaxyx()
    if len(in_articles) <= 0:
        return "There is no article to list!"

    articles = in_articles
    if filter_note != "":
        articles = []
        for art in in_articles:
            review = art["sections"][0]["fragments"][0]["sents"][-1]
            if "nods" in review and  filter_note in review["nods"]:
                articles.append(art)
    width = cols - 10
    sel_arts = []
    saved_articles = load_obj("saved_articles", "articles", {})
    tags = load_obj("tags", "")
    ch = 0
    start = 0
    k = 0
    ni = 0
    while ch != ord('q'):
        list_win.erase()
        mprint("", list_win)
        head = textwrap.shorten(fid, width=width - 30)
        mprint((head).ljust(width - 30) + "progess  " + "status", list_win,
               DIM_COLOR)
        # mprint("-"*width, list_win)
        N = len(articles)
        cc = start
        jj = start
        cur_title = ""
        loaded=[False]*N
        while cc < start + 15 and jj < len(articles):
            a = articles[jj]
            if  not loaded[cc] and a["id"] in saved_articles:
                loaded[cc] = True
                a = articles[cc] = saved_articles[a["id"]]
            year = a['year'] if "year" in a else 0
            h = year if year > 0 else cc
            prog = a['total_prog'] if "total_prog" in a else 0
            art_note = " [" + "not viewed".ljust(12) + "]"
            art_note_color = TEXT_COLOR
            note = "not checked"
            if len(a["sections"]) > 0 and "sents" in a["sections"][0]["fragments"][0]:
                review = a["sections"][0]["fragments"][0]["sents"][0]
                note_indx = min(max(0, note_index), len(review["nods"]))
                if "nods" in review and note_index < len(review["nods"]):
                    note = review["nods"][note_index]
            art_note_color = find_nod_color(note)
            art_note = " [" + note.ljust(12) + "]"

            color = art_note_color
            p = int(prog)
            prog_color = scale_color(p)
            yp = int(((int(year) - 2015)/5)*100) if year > 0 else 0
            year_color = scale_color(yp)
            if cc == k:
                color = CUR_ITEM_COLOR
                year_color = color
            if a in sel_arts:
                color = SEL_ITEM_COLOR
                prog_color = color
                art_note_color = color
                year_color = color
                cur_title = a["title"]
                cur_prog = prog
            if cc == k:
                color = CUR_ITEM_COLOR
                prog_color = color
                art_note_color = color
                cur_title = a["title"]
                cur_prog = prog

            paper_title = a['title']
            dots = ""
            if len(paper_title + art_note) > width - 40:
                dots = "..."
            h = "[{:04}]".format(h)
            prog_str = "{:02d}%".format(int(prog))
            prog_str = "[" + prog_str.rjust(4) + "]"
            art_title = (" " + paper_title[:width - 40] + dots).ljust(width - 36)
            mprint(h, list_win, year_color, end="")
            if theme_menu["bold-text"] == "True":
                att = cur.A_BOLD
            else:
                att = None
            mprint(art_title, list_win, color, end="", attr=att)
            mprint(prog_str, list_win, prog_color, end="", attr=att)
            mprint(art_note, list_win, art_note_color, end="\n", attr=att)

            cc += 1
            jj += 1
            # Endf while
        if search_results:
            inf = "PageDown) Load more ...".ljust(width - 32)
        else:
            inf = head.ljust(width - 30) 
            if filter_note:
               inf = "Filtered by " + filter_note
        mprint(inf, list_win, end = "", color = DIM_COLOR)
        _p = k // 15
        all_pages = (N // 15) + (1 if N % 15 > 0 else 0)
        mprint(" total:" + str(N) + " | page " + str(_p + 1) + " of " + str(all_pages), list_win, color = DIM_COLOR)
        left = ((cols - width) // 2)
        rows, cols = std.getmaxyx()
        if hotkey == "":
            # print_sect(cur_title, cur_prog, left)
            mprint(cur_title, list_win)
            #list_win.refresh(0, 0, 2, 5, rows - 2, cols - 6)
            std.refresh()
            list_win.refresh()
            show_info("h) list commands ")
        ch = get_key(std)

        if ch == ord("r") or is_enter(ch) or ch == RIGHT:
            k = max(k, 0)
            k = min(k, N - 1)
            list_win.erase()
            # list_win.refresh(0, 0, 2, 5, rows - 3, cols - 6)
            list_win.refresh()
            if k < len(articles):
                if show_note:
                    show_article(articles[k], fid)
                else:
                    show_article(articles[k])

        if ch == UP or ch == ord('P'):
            if k > 0:
                k -= 1
            else:
                mbeep()
        if ch == DOWN or ch == ord('N'):
            if k < N - 1:
                k += 1
            else:
                mbeep()

        if k >= start + 15 and k < N:
            ch = cur.KEY_NPAGE
        if k < start:
            ch = "prev_pg"

        if ch == cur.KEY_PPAGE or ch == 'prev_pg':
            start -= 15
            start = max(start, 0)
            k = start + 14 if ch == 'prev_pg' else start
        elif ch == cur.KEY_NPAGE:
            start += 15
            if start > N - 15:
                show_info("Getting articles for " + query)
                new_articles, ret = request(page + 1)
                if len(new_articles) > 0 and ret == "":
                    if isinstance(new_articles, tuple):
                        new_articles = new_articles[0]
                    articles = articles + new_articles
                    save_obj(articles, "last_results", "")
                    N = len(articles)
                else:
                    # ret = textwrap.fill(ret[:200], initial_indent='', subsequent_indent='    ')
                    show_err(ret[:200] + "...", bottom=False)
            start = min(start, N - 15)
            k = start
        elif ch == cur.KEY_HOME:
            k = start
        elif ch == cur.KEY_END:
            k = N - 1  # start + 14
            mod = 15 if N % 15 == 0 else N % 15
            start = N - mod

        if ch == ord('h'):
            show_info(('\n'
                       ' s)            select/deselect an article\n'
                       ' a)            select all articles\n'
                       ' r/Enter/Right open the selected article\n'
                       " f)            filter the articles by the title's nod \n"
                       ' t)            tag the selected items\n'
                       ' d/DEL)        delete the selected items from list\n'
                       ' w)            write the selected items into files\n'
                       ' p)            select the output file format\n'
                       ' m)            change the color theme\n'
                       ' HOME)         go to the first item\n'
                       ' END)          go to the last item\n'
                       ' PageDown)     next page or load more\n'
                       ' PageUp)       previous page\n'
                       ' Arrow keys)   next, previous article\n'
                       ' q/Left)       return back to the main menu\n'),
                      bottom=False)
        if ch == ord('s'):
            if not articles[k] in sel_arts:
                sel_arts.append(articles[k])
            else:
                sel_arts.remove(articles[k])
        if ch == 127 or ch == LEFT:
            ch = ord('q')
        if ch == ord('f'):
            n_list = art_status
            if filter_note != "":
                n_list = ["remove filter"] + art_status
            nod_win = cur.newwin(9, 55, 7, 10)
            nod_win.bkgd(' ', cur.color_pair(INFO_COLOR))  # | cur.A_REVERSE)
            tmp, _ = select_box({"Notes":n_list}, nod_win, title = "Filter articles by:")
            _note = tmp if tmp != "NULL" else ""
            if _note != "" and _note != "remove filter":
                list_articles(articles, fid, show_note, group, _note, note_index = note_index + 1)
            elif _note == "remove filter":
                ch = ord('q')
        if ch == ord('m'):
            choice = ''
            while choice != 'q':
                choice, theme_menu, _ = show_menu(theme_menu, theme_options, title="theme")
            save_obj(theme_menu, conf["theme"], "theme")
            list_win.erase()
            list_win.refresh()
            #list_win.refresh(0, 0, 0, 0, rows - 2, cols - 1)
        if ch == ord('a'):
            for ss in range(start, min(N, start + 15)):
                art = articles[ss]
                if not art in sel_arts:
                    sel_arts.append(art)
                else:
                    sel_arts.remove(art)
        if (ch == ord('d') or ch == cur.KEY_DC) and group != "tags":
            if not sel_arts:
                sel_arts = [articles[k]]
            _confirm = ""
            for art in sel_arts:
                if group != "":
                    if not _confirm == "a":
                        _confirm = confirm_all("remove the article " + art["title"][:20])
                    if _confirm == "y" or _confirm == "a":
                        articles.remove(art)
                        if k > len(articles) - 1:
                            k = len(articles) - 1
                        if art["id"] in saved_articles:
                            del saved_articles[art["id"]]
                            save_obj(saved_articles, "saved_articles", "articles")
                        if group != "saved_articles":
                            group_articles = load_obj(group, "articles", [])
                            if art in group_articles:
                                group_articles.remove(art)
                                save_obj(group_articles, group, "articles")
            if len(articles) == 0:
                break
            sel_arts = []

        if (ch == ord('d') or ch == cur.KEY_DC) and group == "tags":
            if not sel_arts:
                sel_arts = [articles[k]]
            _confirm = ""
            for art in sel_arts:
                if len(art["tags"]) == 1:
                    if _confirm != "a":
                        _confirm = confirm_all("remove the last tag of " + art["title"][:20])
                    if _confirm == "y" or _confirm == "a":
                        remove_tag(art, fid, saved_articles)
                        articles.remove(art)
                else:
                    remove_tag(art, fid, saved_articles)
                    articles.remove(art)
            sel_arts = []
            N = len(articles)
            k = 0
            if len(articles) == 0:
                break
        if ch == ord('p'):
            choice = ''
            mi = 0
            while choice != 'q':
                choice, template_menu, mi = show_menu(template_menu, template_options, title="template", mi=mi,
                                                      shortkeys={"s": "save as"})
            save_obj(template_menu, conf["template"], "tempate")

        if ch == ord('t'):
            if not sel_arts:
                show_err("No article was selected")
            else:
                tag, _ = minput(win_info, 0, 1, "Please enter a tag for selected articles:", default=query)
                tag = tag.strip()
                if tag != "<ESC>" and tag != "":
                    if not tag in tags:
                        tags.append(tag)
                        save_obj(tags, "tags", "")
                    for a in sel_arts:
                        if not "tags" in a:
                            a["tags"] = [tag]
                        elif not tag in a["tags"]:
                            a["tags"].append(tag)
                        insert_article(saved_articles, a)
                        save_obj(saved_articles, "saved_articles", "articles")
                        show_info("Selected articles were added to tagged articles ")
                    sel_arts = []
        if ch == ord('w'):
            if not sel_arts:
                show_err("No article was selected!! Select an article using s")
            else:
                folder = profile 
                _def =""
                if filters['task']:
                    _def = filters['task']
                fid, _ = minput(win_info, 0, 1, " Folder name (relative to profile root):", default=_def)
                if fid != "<ESC>":
                    folder += "/" + fid

                path = doc_path + '/Articles/' + folder + "/"
                Path(path).mkdir(parents=True, exist_ok=True)
                with open(path + fid + "[ " + len(sel_arts) + " articles]" + '.list', 'w') as outfile:
                    json.dump(sel_arts, outfile)
                for a in sel_arts:
                    write_article(a, folder)
                show_msg(str(len(sel_arts)) + " articles were downloaded and saved into saved articles")


def replace_template(template, old_val, new_val):
    ret = template.replace("{newline}", "\n")
    ret = ret.replace(old_val, new_val)
    return ret


def write_article(article, folder=""):
    ext = '.' + template_menu["preset"]
    _folder = doc_path + "/Articles/" + folder + "/" + template_menu["preset"]
    if not os.path.exists(_folder):
        os.makedirs(_folder)
    top = replace_template(template_menu["top"], "{url}", article["pdfUrl"])
    bottom = replace_template(template_menu["bottom"], "{url}", article["pdfUrl"])
    paper_title = article['title']
    file_name = paper_title.replace(' ', '_').lower()
    fpath = _folder + '/' + file_name + ext
    f = open(fpath, "w")
    print(top, file=f)
    title = replace_template(template_menu["title"], "{title}", paper_title)
    print(title, file=f)
    for b in article['sections']:
        sect_title = b['title']
        sect_title = replace_template(template_menu["section-title"], "{section-title}", sect_title)
        print(sect_title, file=f)
        for c in b['fragments']:
            text = c['text']
            text = replace_template(template_menu["paragraph"], "{paragraph}", text)
            f.write(text)
    print(bottom, file=f)
    f.close()
    show_info("Artice was writen to " + fpath + '...')

continue_nod = "continue"
okay_nod = "I see!"
notes_dict = {"*":"point", "!":"got an idea", "_":"needs research","?":"question", ":":"comment"}
notes_list = list(notes_dict.values())
notes_keys = list(notes_dict.keys())
right_nods = ["I see!", "I see!"]
left_nods = ["didn't get"]
nods_list = ["didn't get", continue_nod, "OK, I get it now", "okay", "I see!", "interesting!"]
art_sent_types = ["problem statement", "definition", "claim", "background", "proposed solution", "goal", "feature", "comparison", "usage"]
sent_types = ["main idea", "example", "support"]
art_status = ["interesting!", "novel idea!", "my favorite!", "important!", "needs review", "needs research", "not bad","not of my interest","didn't get it!", "survey paper", "archive", "not reviewed", "to read later"]
feedbacks = set(right_nods + left_nods + notes_list + nods_list + art_status)

def find_color(nods, fsn):
    nod = nods[fsn]
    if nod == "next":
        ii = fsn
        while nods[ii] == "next" and ii < len(nods):
            ii += 1
        nod = nods[ii]
    return find_nod_color(nod)


def find_nod_color(nod):
    ret = int(theme_menu["text-color"])
    colors = theme_menu
    for key, val in colors.items():
        if key == nod:
            ret = val
    return int(ret)


def print_notes(win, notes, ypos, xpos):
    for note in notes:
        if note == "okay" or note in nods_list or note in art_status:
            color = find_nod_color(note)
            print_there(ypos, xpos, ' ' + note, win, color)
            ypos += 1


top_win = None


def print_sect(title, prog, left):
    l_color = SEL_ITEM_COLOR
    top_win.clear()
    if title != "":
        prog = int(prog)
        print_there(0, left, title[:90], top_win, l_color, attr=cur.A_BOLD)
        prog_color = TEXT_COLOR  # scale_color(prog)
        add_info = " [" + str(prog) + "%] "  # + f"({sect_fc+1}/{fnum})"
        y, x = top_win.getyx()
        print_there(y, x + 1, add_info, top_win, prog_color, attr=cur.A_BOLD)
    top_win.refresh()


def print_prog(text_win, prog, width):
    w = int(width * prog / 100)
    d_color = scale_color(prog)
    cur.init_pair(TEMP_COLOR2, back_color, d_color % cur.COLORS)
    addinfo = (" Progress:" + str(prog) + "%")
    mprint(addinfo, text_win, d_color)

def print_comment(text_win, comment, width):
    com_sents = split_into_sentences(comment)
    for com in com_sents:
        com = textwrap.fill(com,
                        width=width - 4, replace_whitespace=False)
        mprint(com, text_win, SEL_ITEM_COLOR, end="\n")
        
def new_sent(s):
    _new_sent = {"text":s,"type":"", "end":'\n', "nod":"", "nods":[],"passable":"False", "rtime":0, "tries":1, "comment":"", "notes":{}}
    if len(s.split(' ')) <= 1:
        _new_sent["end"] = " "
    return _new_sent

split_levels = [['\n'],['.','?','!'], ['.','?','!',';'], ['.','?','!',';', ' ', ',', '-']]
text_width = 72
#iii
def init_frag_sents(text, single_unit = False, word_limit = 20, nod = "", split_level = 1):
    if word_limit == 20 and split_level == 2: word_limit = 10
    sents = []
    if split_level == 3:
        sents = []
        lines = textwrap.wrap(text, text_width)
        for line in lines:
            words = line.split()
            for w in words:
                u = new_sent(w)
                u["nod"] = "next"
                sents.append(u)
            sents[-1]["nod"] = nod
        sents[-1]["end"] = "\n"
    else:
        f_sents = split_into_sentences(text, limit = word_limit, split_on=split_levels[split_level])
        sents = [new_sent(s) for s in f_sents]
        if single_unit and sents:
            for s in sents:
                s["nod"] = "next"
            sents[-1]["nod"] = nod 
    return sents

def refresh_offsets(art, split_level = 1):
    ii = 1
    prev_sect = None
    fn = 0
    nods = [""]
    for sect in art["sections"]:
        sect["offset"] = ii
        if not "progs" in sect:
            sect["progs"] = 0
        if not prev_sect is None:
            prev_sect["sents_num"] = ii - prev_sect["offset"]
        prev_sect = sect
        nods.append("")
        ii += 1
        for frag in sect["fragments"]:
            fn += 1
            frag["offset"] = ii
            if not "sents" in frag:
                frag["sents"] = init_frag_sents(frag["text"], split_level = split_level)
            for sent in frag["sents"]:
                nods.append(sent["nod"])
                ii += 1
    sect["sents_num"] = ii - prev_sect["offset"]
    return len(art["sections"]),fn, ii, nods

def locate(art, si, sel_first_sent=False):
    ii = 0
    if si < 0:
        si = 0
    for sect in art["sections"]:
        if si < sect["offset"] + sect["sents_num"]:
            break

    for frag in sect["fragments"]:
        if sel_first_sent:
            break
        if si < frag["offset"] + len(frag["sents"]):
            break

    for i, sent in enumerate(frag["sents"]):
        s_start = frag["offset"] + i
        if sel_first_sent:
            break
        elif s_start >= si:
            break
    return sect, frag, sent, min(si, s_start)
# sss
def show_article(art, show_note="", collect_art = False, ref_sent = ""):
    global theme_menu, theme_options, query, filters, hotkey, show_instruct

    if not art["sections"]:
        show_msg("The article has no content to show")
        return
    sel_sects = {}
    fast_read = False
    start_row = 0
    rows, cols = std.getmaxyx()
    width = text_width
    def_review = """Your summary or review of paper:
    """
    #def_inst = """Press @ anywhere in the article to edit the review, and press # to add a review tag."""
    def_inst = """For more information about how to read and review a paper using Checkideh please visit: http://checkideh.com/getting_started#review 
    To hide instructions like this go to the main menu > options > show instructions, and set it to Disabled. """
    if not collect_art and art["sections"][0]["title"] != "Review":
        new_sect = {}
        new_sect["title"] = "Review"
        frag = {"text":def_review}
        frag["sents"] = init_frag_sents(def_review, True)
        frag["sents"][-1]["notes"]["instruct"] = def_inst
        new_sect["fragments"] = [frag]
        art["sections"].insert(0, new_sect)

    figures = []
    fig_file = ""
    if "figures" in art and not art["figures"] is None:
        figures = art["figures"]
        figures_created = False
        fig_file = app_path + "/nodcast_temp.html"
        if not figures_created:
            create_figures_file(figures, fig_file)
            figures_created = True
        fig_num = 0
        has_figure = False
        for i, sect in enumerate(art["sections"]):
            if sect["title"] == "Figures":
                has_figure = False
                art["sections"].remove(sect)

        if not has_figure:
            new_sect = {}
            new_sect["title"] = "Figures"
            frags = []
            for fig in figures:
                fig_num += 1
                caption = fig["caption"]
                url = "file://" + fig_file + "#fig" + str(fig_num - 1)
                if not caption.startswith("Figure") and not caption.startswith("Table"):
                    caption = "Figure " + str(fig_num) + ":" + caption
                frag = {"text": caption, "url": url}
                frags.append(frag)
            new_sect["fragments"] = frags
            art["sections"].append(new_sect)

    # text_win = std
    if "tasks" in art:
        tags = load_obj("tags", "", [""])
        if not "tags" in art:
            art["tags"] = []
        for task in art["tasks"]:
            if not task in art["tags"]:
                art["tags"].append(task)
            if not task in tags:
                tags.append(task)
        save_obj(tags, "tags", "")

    bg = ""
    saved_articles = load_obj("saved_articles", "articles", {})
    articles_notes = load_obj("articles_notes", "articles", {})
    frags_text = ""
    art_id = -1
    si = 0
    cury = 0
    page_height = rows - 4
    scroll = 1
    show_reading_time = False
    start_reading = True
    is_section = False
    art_id = art['id']

    if False:
        with open("art.txt", "w") as f:
            print(str(art), file=f)
    bmark = 0
    total_sects = len(art["sections"])
    if total_sects > 2 and show_note == "" and not collect_art and si == 0 and ref_sent == "":
        expand = 0
        for _sect in art["sections"]:
            _sect["opened"] = False
    else:
        expand = 1
        for _sect in art["sections"]:
            _sect["opened"] = True
    ch = 0
    main_info = "r) resume reading      h) list commands "
    show_info(main_info)
    ni, fi = 0, 0
    last_pos = 0
    art_changed = False
    art_changed = False
    show_info("r) resume from last position")
    nod_set = False
    needs_nod = False
    interestings = 0
    jump_key = 0
    cur_nod = ""
    old_si = -1
    reading_mode = False
#vvv
    split_level = 1
    total_sects, total_frags, total_sents, nods = refresh_offsets(art, split_level=split_level)
    pos = [0]*total_sents
    visible = [True]*total_sents
    passable = [False]*total_sents
    first_frag = art["sections"][0]['fragments'][0]
    if si == 0:
        ii = 0
        while ii < len(first_frag['sents']) and first_frag['sents'][ii]['nod'] == "next":
            ii += 1

        bmark = first_frag["offset"]
        si = bmark + ii
    else:
        bmrak = si
    if ref_sent != "":
        refs = ref_sent.split("_")
        _sect = int(refs[0])
        _frag = int(refs[1])
        _begin = int(refs[2])
        _end = int(refs[3])
        bmark = art["sections"][_sect]["fragments"][_frag]["offset"] + _begin
        si = art["sections"][_sect]["fragments"][_frag]["offset"] + _end 

    logging.info("Article:" + art["title"])
    #abstract = art["sections"][1]
    #def_inst2 = """Press <Down> to expand the selection, or press <Right> to adimit the selected part and move to the next part. Press <Left> to add a note to the selected part and press : to add a comment. 
    #""" + inst_footer
    #abstract["fragments"][0]["sents"][0]["notes"]["instruct"] = def_inst2
# bbb
    nr_opts = load_obj("settings", "", common = True)
    sel_first_sent = False
    total_pr = int(art["total_prog"])*total_sects if "total_prog" in art else 0
    start_time = 0
    too_big_warn = False
    start_reading = True
    first = True
    forward = True
    begin_offset = art["sections"][0]["offset"]
    while ch != ord('q'):
        # clear_screen(text_win)
        too_big_art = False
        cur_note = ""
        end_time = time.time()
        elapsed_time = end_time - start_time if start_time != 0 else 2
        if elapsed_time < 0.05:  # prevent fast scroll by mouse
            ch = get_key(std)
            continue
        start_time = time.time()
        cur_sect, cur_frag, cur_sent, si = locate(art, si, sel_first_sent)
        if bmark > si:
            bmark = si

        if not (ch == ord('.') or ch == ord(',')):
            top_margin = 15 if cur_sect == art["sections"][0] else 10 # rows // 4
            bmark = max(0, bmark)
            cur_pos = bmark if expand == 1 else cur_sect['offset']
            if cur_pos < len(pos) and pos[cur_pos] > top_margin:
                start_row = pos[cur_pos] - top_margin
            else:
                start_row = 0

        sel_first_sent = False
        bmark = min(bmark, si)
        if si != old_si:
            cur_nod = ""
            split_level  = 1
            old_si = si
        start_row = max(0, start_row)
        #start_row = min(cury - 1, start_row)
        if bg != theme_menu["back-color"]:
            bg = theme_menu["back-color"]
            clear_screen(std)
            # text_win.refresh(start_row,0, 0,0, rows-1, cols-1)
            show_info(main_info)
        text_win.erase()
        sn = 0
        title = "\n".join(textwrap.wrap(art["title"], width))  # wrap at 60 characters
        pdfurl = art["pdfUrl"]
        if "save_folder" in art and Path(art["save_folder"]).is_file():
            top = "[open file] "
        else:
            if pdfurl.endswith("pdf"):
                top = "[download] " + pdfurl
            else:
                top = "[open link] " + pdfurl

        total_prog = int(round(total_pr / total_sects, 2))
        art["total_prog"] = str(total_prog)
        mprint("", text_win)
        if si == 0:
            mprint(top, text_win, HL_COLOR, attr=cur.A_BOLD)
            if expand == 0:
               for _sect in art["sections"]:
                    _sect["opened"] = False
        else:
            mprint(top, text_win, TITLE_COLOR, attr=cur.A_BOLD)
        print_prog(text_win, total_prog, width)
        # mprint(pdfurl,  text_win, TITLE_COLOR, attr = cur.A_BOLD)
        pos[0], _ = text_win.getyx()
        mprint("", text_win)
        fsn = 1
        ffn = 1
        is_section = False
        pr = 0
        total_pr = 0
        # mark sections
        for b in art["sections"]:
            fragments = b["fragments"]
            fnum = len(fragments)
            title_color = ITEM_COLOR
            if fsn == si:
                is_section = True
                title_color = HL_COLOR
                # si = si + 1
            if (b == cur_sect and expand == 0 and cur_sect["opened"]): 
                text_win.erase()
            sents_num = b["sents_num"] - 1
            prog = 0
            if sents_num > 0:
                prog = int(round(b["progs"] / sents_num, 2) * 100) if "prog" in b else 0
            b["prog"] = prog
            prog_color = scale_color(prog)
            total_pr += prog
            prog = str(prog) + "%"  # + " (" + str(progs[sn]) +  "/" + str(sents_num) + ")"
            passable[fsn] = True

            if b == cur_sect and si > 0:
                if b["title"] == "Figures":
                    add_info = " (" + str(len(figures)) + ") "
                else:
                    add_info = " [" + str(prog) + "] "  # + f"({sect_fc+1}/{fnum})"
                if cur_sect["opened"]:
                    title_color = SEL_ITEM_COLOR  # HL_COLOR
                else:
                    title_color = CUR_ITEM_COLOR
                    prog_color = title_color
            else:
                if b["title"] == "Figures":
                    add_info = " (" + str(len(figures)) + ") "
                else:
                    add_info = " [" + str(prog) + "] "

            if b["title"] != "all" or expand == 0:
                mprint(b["title"], text_win, title_color, end="", attr=cur.A_BOLD)
                mprint(add_info, text_win, prog_color, attr=cur.A_BOLD)

            pos[fsn], _ = text_win.getyx()
            if pos[fsn] > start_row + rows + rows//2 and not first:
                break
            ffn += 1
            fsn += 1
            if too_big_art or (expand == 0 and b != cur_sect):
                fsn += b["sents_num"] - 1
                ffn += len(b["fragments"])
            elif (expand == 0 and not cur_sect["opened"]):
                fsn += b["sents_num"] - 1
                ffn += len(b["fragments"])
            else:
                for frag in fragments:
                    if pos[fsn] > start_row + rows + rows//2 and not first:
                        break
                    if frag != cur_frag and expand == 3:
                        fsn += frag['sents_num']
                        ffn += 1
                    else:
                        new_frag = True
                        if not "sents" in frag:
                            frag["sents"] = init_frag_sents(frag["text"])
                        _sents = frag["sents"]
                        hlcolor = HL_COLOR
                        color = DIM_COLOR
                        # fff
                        if not too_big_art:
                            nexts = 0
                            for sent in _sents:
                                if too_big_art:
                                    break
                                sent["nod"] = nods[fsn]
                                feedback = sent["nod"] if "nod" in sent else ""
                                passable[fsn] = sent["passable"] == "True" if "passable" in sent else False
                                if b == cur_sect:
                                    if sent["nod"] in right_nods:
                                        nexts += 1
                                        pr += nexts
                                        cur_sect["progs"] = pr
                                        nexts = 0
                                    elif sent["nod"] == "next":
                                        nexts += 1
                                    else:
                                        nexts = 0
                                if show_note == "comments":
                                    if sent["comment"] != "":
                                        visible[fsn] = True
                                    else:
                                        visible[fsn] = False
                                elif (show_note != "" and not show_note in sent["notes"]) or "remove" in sent["notes"]:
                                    visible[fsn] = False
                                elif show_note != "" and not "remove" in sent["notes"]:
                                    visible[fsn] = True

                                if not visible[fsn]:
                                    pos[fsn], _ = text_win.getyx()
                                    fsn += 1
                                    continue

                                # cur.init_pair(NOD_COLOR,back_color,cG)
                                reading_time = sent["rtime"]
                                f_color = HL_COLOR
                                hline = "-" * (width)
                                if show_reading_time:
                                    f_color = scale_color((100 - reading_time * 4), 0.1)
                                    mprint(str(reading_time), text_win, f_color)

                                text = sent["text"]
                                lines = textwrap.wrap(text, width)
                                lines = list(filter(None, lines))
                                end = ""

                                # sent += " "*(width -2) + "\n"
                                sent_text = ""
                                if len(lines) > 1:
                                    for line in lines:
                                        sent_text += line + "\n"
                                elif lines:
                                    sent_text = lines[0]
                                    # sent += " "*(width - 2) + "\n"
                                posy, posx = text_win.getyx()
                                end = ""
                                if len(lines) <= 1:
                                    end = sent["end"] if "end" in sent else "\n"
                                    if posx + len(sent_text) > width:
                                       mprint("", text_win)
                                if fsn >= bmark and fsn <= si and not passable[fsn]:
                                    hl_pos = text_win.getyx()
                                    hlcolor = HL_COLOR
                                    l_color = find_color(nods, fsn)
                                    b_color = int(theme_menu["highlight-color"]) % cur.COLORS
                                    cur.init_pair(TEMP_COLOR, l_color % cur.COLORS, b_color)
                                    _color = HL_COLOR
                                    if "type" in sent and sent["type"] != "":
                                        mprint(sent["type"] + ":" + " "*(width - 3 - len(sent["type"])), text_win, cW, end=end)
                                    if theme_menu["bold-highlight"] == "True":
                                        mprint(sent_text, text_win, _color, attr=cur.A_BOLD, end=end)
                                    else:
                                        mprint(sent_text, text_win, _color, end=end)
                                else:
                                    _color = DIM_COLOR
                                    if nods[fsn] != "" and start_reading:
                                        _color = find_color(nods, fsn)
                                    if "type" in sent and sent["type"] != "":
                                        mprint(sent["type"] + ":", text_win, cW, end="\n")
                                    if theme_menu["bold-text"] == "True":
                                        mprint(sent_text, text_win, _color, attr=cur.A_BOLD, end=end)
                                    else:
                                        mprint(sent_text, text_win, _color, end=end)
                                mark = ""
                                if "url" in frag and new_frag:
                                    mark = "f"
                                left = (cols - width) // 2
                                ypos = pos[fsn - 1]
                                _y, _x = text_win.getyx()
                                nn = [mark]
                                if start_reading:
                                    for note in sent["nods"]:
                                        nn.append(note)
                                    #print_notes(text_win, nn, ypos, width + 1)
                                    color = find_nod_color(sent["nod"])
                                    print_there(ypos, width + 1, ' ' + sent["nod"], text_win, color)
                                text_win.move(_y, _x)
                                #ccc
                                if not passable[fsn]:
                                    if sent["comment"] != "":
                                        comment = sent["comment"]
                                        print_comment(text_win, comment, width)
                                    empty = []
                                    filled = []
                                    for _note, _note_val in sent["notes"].items():
                                        if _note_val != "":
                                            filled.append((_note,_note_val))
                                        else:
                                            empty.append((_note,_note_val))
                                    for _note, _note_val in filled:
                                        if _note != "instruct":
                                            _note_color = find_nod_color(_note)
                                            mprint(_note + ": ", text_win, _note_color, end = "")
                                            print_comment(text_win, _note_val, width)
                                    for _note, _note_val in empty:
                                        _note_color = find_nod_color(_note)
                                        mprint(_note + " ", text_win, _note_color, end = "")
                                else:
                                    pass  # mprint("", text_win, f_color)
                                pos[fsn], _ = text_win.getyx()
                                if pos[fsn] > rows*40:
                                    too_big_art = True
                                    if not too_big_warn:
                                        too_big_warn = True
                                        show_warn("The article is too big to be displayed completely!") 
                                fsn += 1
                                new_frag = False

                        #fffe
                        if "end_mark" in frag:  # fsn >= bmark and fsn <= si:
                            w =  width - 5
                            mprint("-" * (w), text_win, DIM_COLOR)
                        else:
                            w1 = 4  # width - 5
                            w2 = 6
                            mprint("-" * w1 + ' ' * (width - w1 - w2) + "-" * w2, text_win, DIM_COLOR)
                        ffn += 1
                    # end for fragments
            sn += 1
        # end for sections
#bbe

        first = False
        win_info.erase()
        if start_reading:
            print_there(0, 1, "   ", win_info, color=WARNING_COLOR)
            print_there(0, 5, "s) stop reading", win_info, color=INFO_COLOR)
            if show_instruct:
                print_there(0, cols - 25, "l) hide insturctions", win_info, color=INFO_COLOR)
            else:
                print_there(0, cols - 25, "l) list instructions", win_info, color=INFO_COLOR)
        else:
            print_there(0, 1, "   ", win_info, color=22, attr= A_REVERSE)
            print_there(0, 5, "s) start reading", win_info, color=INFO_COLOR)
            if show_instruct:
                print_there(0, cols - 25, "l) hide instructions", win_info, color=INFO_COLOR)
            else:
                print_there(0, cols - 25, "l) list instructions", win_info, color=INFO_COLOR)
        win_info.refresh()
        cury, curx = text_win.getyx()
        # mark get_key

        # if ch != LEFT:
        rows, cols = std.getmaxyx()
        # width = 2*cols // 3
        left = ((cols - width) // 2) - 10
        ypos = pos[bmark] - start_row
        end_row = ypos + (pos[si] - pos[bmark]) 
        limit_row = rows - 5
        if end_row > limit_row:
            start_row -= limit_row - end_row
        if hotkey == "":
            text_win.refresh(start_row, 0, 2, left, rows - 2, cols - 1)
            #cur.doupdate()
            #show_info(main_info)
        if art["sections"].index(cur_sect) > 1 and expand != 0:
            if pos[cur_sect["offset"]] <= start_row:
                print_sect(cur_sect["title"], cur_sect["prog"], left)
            else:
                print_sect("", "", left)
        else:
            print_sect(art["title"], art["total_prog"], left)
#III
        if start_reading and show_instruct:
            s_win = cur.newwin(10, 32, rows - 11, cols - 27)
            s_win.bkgd(' ', cur.color_pair(INPUT_COLOR))  # | cur.A_REVERSE)
            _list = ["Down) move next", "Left) interesting!", "Right) okay", "-) Didn't get", "", "+) OK, I get it now", "*) bookmark", "Insert) Add a note or tag"]
            mprint(" ", s_win, color=232, attr = cur.A_REVERSE, end = "")
            mprint("Instructions: l) hide".ljust(30),s_win, color=INFO_COLOR)
            for _word in _list:
                mprint(" ", s_win, color=232, attr = cur.A_REVERSE, end = "")
                mprint(" " + _word, s_win, color=INPUT_COLOR)
            mprint(" ", s_win, color=232, attr = cur.A_REVERSE, end = "")
            s_win.refresh()
        # jjj
        if jump_key == 0:
            if reading_mode:
                if si + 1 < total_sents:
                    sent_len = len(art["sents"][si])
                    std.timeout(sent_len * 100)
                    show_info("remaining time:" + str(sent_len * 100))
                    tmp_ch = get_key(std)
                    if tmp_ch == -1:
                        ch = DOWN
                    else:
                        reading_mode = False
                        std.timeout(-1)
                else:
                    reading_mode = False
                    std.timeout(-1)
            else:
                ch = get_key(std)
                start_time = 0
        else:
            ch = jump_key
            jump_key = 0
        if ch == ord('>'):
            if width < 2 * cols // 3:
                text_win.erase()
                text_win.refresh(0, 0, 2, 0, rows - 2, cols - 1)
                width += 2
            else:
                mbeep()
        if ch == ord('<'):
            if width > cols // 3:
                text_win.erase()
                text_win.refresh(0, 0, 2, 0, rows - 2, cols - 1)
                width -= 2
            else:
                mbeep()
                


        if ch == ord("N"):
            hotkey = "qNr" if expand == 0 else "qqNr"
        if ch == ord("H"):
            hotkey = "qq" if expand == 0 else "qqq"
        if ch == ord("Q"):
            hotkey = "qqq" if expand == 0 else "qqqq"
        if ch == ord('n'):
            if show_note != '':
                show_note = ''
                visible = [True] * total_sents
            else:
                ypos = pos[bmark] - start_row
                nod_win = cur.newwin(9, w, ypos + 2, left)
                nod_win.bkgd(' ', cur.color_pair(INFO_COLOR))  # | cur.A_REVERSE)
                tmp, _ = select_box({"Notes":notes_list}, nod_win, in_row=True)
                show_note = tmp if tmp != "NULL" else ""
        if ch == ord('d'):
            _confirm = confirm("delete the pdf file from your computer")
            if _confirm == "y" or _confirm == "a":
                delete_file(art)
                art["save_folder"] = ""
        if ch == ord("^"):
            if len(cur_sent["nods"]) > 0:
                cur_sent["nods"].pop(0)
            elif len(cur_sent["notes"]) > 0:
                top_key = list(cur_sent["notes"].keys())[0]
                _note = cur_sent["notes"].pop(top_key)
        #ppp
        if ch == cur.KEY_DC:
            if split_level == len(split_levels) - 1:
                show_warn("too split")
            else:
                split_level = 3
                _pos = si - cur_frag['offset']
                new_sents = init_frag_sents(cur_frag["sents"][_pos]["text"], single_unit = True, split_level = split_level)
                cur_frag['sents'].pop(_pos)
                cur_frag['sents'][_pos:_pos] = new_sents
                old_total_sents = total_sents
                total_sects, total_frags, total_sents, nods = refresh_offsets(art)
                dif = total_sents - old_total_sents
                si = bmark
                if dif > 0:
                    pos += [0]*dif
                    visible += [True]*dif
                    passable += [False]*dif

            # std.timeout(500)
            # tmp_ch = get_key(std)
            # remove_nod = False
            # if tmp_ch == cur.KEY_DC:
            #    remove_nod = True
            # std.timeout(-1)
        if ch == cur.KEY_SDC:
            cur_sent["notes"] = []
            if nods[si] != "":
                nods[si] = ""
                if si > 0:
                    si -= 1
                    while si > 0 and (not visible[si] or passable[si]):
                        si -= 1
                    if bmark >= si:
                        bmark = si
                        while bmark >= 0 and nods[bmark - 1] == "next":
                            bmark -= 1
                else:
                    mbeep()
                    si = 0
        if ch == ord('y'):
            with open(art["title"] + ".txt", "w") as f:
                print(art, file=f)
        if ch == ord('r'):
            si = total_sents - 1
            text_win.erase()
            text_win.refresh(0, 0, 0, 0, rows - 2, cols - 1)
            while (nods[si] == "" or nods[si] == "skipped" or nods[si] == "next" or not visible[si]) and si > 2:
                si -= 1
            si = max(si, 1)
            bmark = si
            expand = 1
            first = True
            for _sect in art["sections"]:
                _sect["opened"] = True
            start_reading = True

        if ch == ord('v'):
            _confirm = confirm("restore the removed parts")
            if _confirm == "y" or _confirm == "a":
                visible = [True] * total_sents
            for i, nod in enumerate(nods):
                if nod == "remove":
                    nods[i] = ""
            art_changed = True
        if ch == ord('z'):
            # show_reading_time = not show_reading_time
            reading_mode = True  # not reading_mode

        if ch == ord('h'):  # article help
            show_info(('\n'
                       '  Down)          expand the selection to next sentence\n'
                       '  Right)         expaned a collapsed section\n'
                       '  Right)         nod the selected sentences with a positive feedback\n'
                       '  Left)          nod the selected sentences with a negative feedback\n'
                       '  Enter)         open a link, article or refrence associated to the selected sentence\n'
                       '  +/-)           show the list of positive and negative nods\n'
                       '  o)             download/open the pdf file externally\n'
                       '  f)             list figures\n'
                       '  t)             add a tag to the article\n'
                       '  d)             delete the external pdf file \n'
                       '  w)             write the article into a file\n'
                       '  p)             select the output file format\n'
                       '  m)             change the color theme\n'
                       '  u)             reset comments and notes\n'
                       '  n)             filter sentences by a note\n'
                       '  DEL)           remove current notes in order\n'
                       '  TAB)           skip current fragment\n'
                       '  e)             expand/collapse sections\n'
                       '  BackSpace)     collapse the current section\n'
                       '  >/<)           increase/decrease the width of text\n'
                       '  :)             add a single line comment \n'
                       '  {)             add a multi line comment \n'
                       '  PgUp/PgDown)   previous/next section\n'
                       '  j/k)           previous/next page\n'
                       '  l/;)           previous/next fragment\n'
                       '  ,/.)           scroll up down\n'
                       '  H)             go to the home menu\n'
                       '  P/N)           open the previous/next article\n'
                       '  h)             show this list\n'
                       '  q)             close \n'
                       ''),
                      bottom=False)
        if ch == ord('x'):
            fast_read = not fast_read
        if ch == ord('w'):
            folder = profile 
            _def =""
            if filters['task']:
                _def = filters['task']
            fid, _ = minput(win_info, 0, 1, " Folder name (relative to profile root):", default=_def)
            if fid != "<ESC>":
                folder += "/" + fid

            path = doc_path + '/Articles/' + folder + "/"
            Path(path).mkdir(parents=True, exist_ok=True)
            write_article(art, folder)
            show_msg("The article was written in " + folder)
        if ch == ord('u'):
            _confirm = confirm("reset the article")
            if _confirm == "y" or _confirm == "a":
                nods = [""] * total_sents
                for sect in art["sections"]:
                    for frag in sect["fragments"]:
                        for sent in frag["sents"]:
                            sent["nods"] = []
                visible = [True] * total_sents
                passable = [False] * total_sents
                si = 2
                art_changed = True
                update_si = True

        if ch == ord('s'):
            start_reading = not start_reading
        if ch == ord('l'):
            show_instruct = not show_instruct 
            nr_opts["show instructions"] = "Enabled" if show_instruct else "Disabled"
        if ch == ord('g'):
            cur_sect_title = cur_sect["title"].lower()
            if art_id in sel_sects:
                if cur_sect in sel_sects[art_id]:
                    sel_sects[art_id].remove(cur_sect_title)
                else:
                    sel_sects[art_id].append(cur_sect_title)
            else:
                sel_sects[art_id] = [cur_sect_title]
        if ch == cur.KEY_NPAGE:
            std.timeout(100)
            tmp_ch = get_key(std)
            if tmp_ch == cur.KEY_NPAGE:
                ch = cur.KEY_END
            std.timeout(-1)
        ####
        if ch == ord('#'):
            if ch == ord('#') or (cur_sect["title"] == "Review" and cur_sect == art["sections"][0]):
                tmp_sent = art["sections"][0]["fragments"][0]["sents"][-1]
                win_title = "Review tag on the article:"
                n_list = {"Article Notes:":art_status}
                _win_w = 70
            else:
                tmp_sent = cur_sent
                win_title = "Note:"
                n_list = {"Nods":nods_list}
                _win_w = 35 
            nod_win = cur.newwin(12, _win_w, ypos - 2, width - 10) 
            nod_win.bkgd(' ', cur.color_pair(TEXT_COLOR))  # | cur.A_REVERSE)
            tmp_note, note_index = select_box(n_list, nod_win, 0, ni = 4, in_row=False, border=False, in_colors = theme_menu, color = TEXT_COLOR)
            if tmp_note != 'NULL':
                cur_nod = tmp_note
                set_nod(cur_nod, tmp_sent, nods, visible, bmark, si, elapsed_time)
                si,bmark = moveon(si, visible, passable, nods)

        if ch == ord('i') or ch == cur.KEY_IC or ch == ord(' '):
            ypos = pos[bmark] - start_row
            tmp_sent = cur_sent
            _notes_list = []
            for k,v in notes_dict.items():
                _notes_list.append(v + " (" + k + ")")
            n_list = {"Notes":_notes_list, "Types": art_sent_types}
            _win_w = 55
            # NNN
            nod_win = cur.newwin(9, _win_w, ypos + 2, left)
            nod_win.bkgd(' ', cur.color_pair(INFO_COLOR))  # | cur.A_REVERSE)
            tmp_note, note_index = select_box(n_list, nod_win, 0, in_row=True)
            if tmp_note != 'NULL':
                cur_note = tmp_note.split("(")[0].strip()
                if cur_note in art_sent_types:
                    b_ind = bmark - cur_frag["offset"]
                    cur_frag["sents"][b_ind]["type"] = cur_note
                if tmp_sent == cur_sent: 
                    for ii in range(bmark, si):
                        nods[ii] = "next"
                    nods[si] = "noted" if cur_note not in nods_list else cur_note
                if cur_note in notes_list:
                    _ind = notes_list.index(cur_note)
                    ch = ord(notes_keys[_ind])
                art_changed = True
        if chr(ch).isdigit():
            try:
                index = int(chr(ch))
            except:
                index = 0
            if index < len(nods_list):
                cur_nod = nods_list[index]
                set_nod(cur_nod, cur_sent, nods, visible, bmark, si, elapsed_time)
                if cur_note in notes_list:
                    _ind = notes_list(cur_note).index()
                    ch = ord(notes_keys[_ind])

        if is_enter(ch) and expand != 0:
            if si > 0:
                if "url" in cur_frag:
                    _url = cur_frag["url"]
                    webbrowser.open(_url)
                elif "ref_art" in cur_frag:
                    ref_id = cur_frag["ref_art"]
                    ref_sent = cur_frag["ref_sent"]
                    if ref_id in saved_articles:
                        show_article(saved_articles[ref_id], ref_sent = ref_sent)

            else:
                ch = ord('o')

        ## kkk (bookmark)
        if ch == SRIGHT:
            if forward and bmark <= si:
                si += 1
            elif not forward and bmark == si:
                forward = True
                si += 1
            elif not forward:
                bmark += 1
            si = min(si, total_sents - 1)
        if ch == SLEFT: 
            if forward and bmark < si:
                si -= 1 
            elif forward and bmark == si:
                forward = False
                bmark -= 1
            elif not forward:
                bmark -= 1
            si = max(si, begin_offset)
            bmark = max(bmark, begin_offset)
        if ch == SUP:
            if forward and bmark <= si:
                si = contract_sel(si, visible, passable, nods)
                if si <= bmark:
                    si = bmark
                    forward = False
            elif not forward:
                bmark = contract_sel(bmark, visible, passable, nods)
        if ch == SDOWN: 
            if forward and bmark <= si:
                si = expand_sel(si, visible, passable, nods, block_id="line")
            elif not forward:
                bmark = expand_sel(bmark, visible, passable, nods, block_id="line")
                if bmark >= si:
                    bmark = si
                    forward = True

        if ch == DOWN: 
            next_frag_start = cur_frag["offset"] + len(cur_frag["sents"]) 
            if si + 1 < next_frag_start and (nods[si + 1] == "next" or nods[si + 1] == ""):
                si += 1
            else:
                mbeep()
        if ch == UP: 
            if si > bmark:
                si -= 1
            else:
                mbeep()
        if ch == RIGHT: # move next
            si, bmark = moveon(si, visible, passable, nods)
            forward = True
        if ch == LEFT: # move previous
            while not visible[bmark -1] or passable[bmark -1]:
                bmark -= 1
            bmark = move_bmark(bmark - 1, nods)
            si = bmark 
            forward = True
        if ch == ord('-'):
            if nods[si] == "okay":
                cur_nod = "I don't get it now"
            else:
                cur_nod = "didn't get"
            set_nod(cur_nod, cur_sent, nods, visible, bmark, si, elapsed_time)
            si, bmark = moveon(si, visible, passable, nods)
        if ch == ord('+'):
            if nods[si] == "didn't get":
                show_wart("You didn't get it before, first admit it with okay (Right) then you can add it to the interesting points")
            else:
                cur_nod = "interesting!"
            set_nod(cur_nod, cur_sent, nods, visible, bmark, si, elapsed_time)

        art_changed = art_changed or nod_set
        if si > 0 and (expand == 0 and ch == UP and not cur_sect["opened"]) or ch == cur.KEY_PPAGE:
            sel_first_sent = True
            si = cur_sect["offset"] - 1
            bmark = si
        if (expand == 0 and ch == DOWN and not cur_sect["opened"]) or ch == cur.KEY_NPAGE:
            sel_first_sent = True
            si = cur_sect["offset"] + cur_sect["sents_num"] + 1 
            bmark = si
        if ch == ord('j'):
            si = cur_frag["offset"] + len(cur_frag["sents"]) 
            bmark = si
        if ch == ord('k'):
            si = cur_frag["offset"] - 1
            bmark = si
        if ((expand == 0 and is_enter(ch))
                or si > 0 and (expand == 0 and ch == RIGHT and not cur_sect["opened"])):
            first = True
            if si > 0:
                expand = 1
                for _sect in art["sections"]:
                    _sect["opened"] = True
            else:
                ch = ord('o')

        if ch == ord('e'):
            if expand == 1:
                expand = 0
                pos = [0] * total_sents
                for _sect in art["sections"]:
                    _sect["opened"] = False
            else:
                expand = 1
                for _sect in art["sections"]:
                    _sect["opened"] = True

        if ch == ord('.'):
            if start_row < cury:
                start_row += scroll
            else:
                mbeep()

        if ch == ord(','):
            if start_row > 0:
                start_row -= scroll
            else:
                mbeep()

        if ch == ord('k'):
            si = max(si - 10, 0)
            bmark = si
        elif ch == ord('j'):
            si = min(si + 10, total_sents - 1)
            bmark = si
        elif ch == cur.KEY_HOME:
            si = 0
            bmark = si
        elif ch == cur.KEY_END:
            si = total_sents - 1
            bmark = si

        if ch == 127 and cur_sect["opened"]:
            ch = 0
            expand = 0
            pos = [0] * total_sents
            for _sect in art["sections"]:
                _sect["opened"] = False
        elif ch == 127:
            ch = ord('q')

        if ch == ord('o'):
            if "save_folder" in art and art["save_folder"] != "":
                fname = art["save_folder"]
                _file = Path(fname)
                if _file.is_file():
                    openFile(_file)
                else:
                    show_msg(str(_file) + " was not found")
                    art["save_folder"] = ""
            else:
                folder = profile 
                _def =""
                if filters['task']:
                    _def = filters['task']
                fid, _ = minput(win_info, 0, 1, " Folder name (relative to profile root):", default=_def)
                if fid != "<ESC>":
                    folder += "/" + fid

                path = doc_path + '/Articles/' + folder + "/"
                Path(path).mkdir(parents=True, exist_ok=True)
                if fid != "<ESC>":
                    download(art["pdfUrl"], art, folder)
                    art_changed = True
                else:
                    show_info(main_info)
        if ch == ord('@'): #@@@
            win = cur.newwin(10, width, 6, left)
            win.bkgd(' ', cur.color_pair(CUR_ITEM_COLOR))  # | cur.A_REVERSE)
            win.refresh()
            review = art["sections"][0]["fragments"][-1]
            default = ""
            if review["text"] != def_review:
                for sent in review["sents"]:
                    default += sent["text"]
            _review, _ = minput(win, 0, 0, "Article notes and review:", default=default, mode =2)
            show_info(main_info)
            _review = _review if _review != "<ESC>" and _review != "q" else default
            art_changed = True
            if _review != "" and _review != def_review:
                review["text"] = _review
                review["sents"] = init_frag_sents(_review, True, word_limit = 2, nod ="okay")
                if not "reviewed" in review["sents"][-1]["notes"]:
                    review["sents"][-1]["nods"].append("reviewed")
            old_total_sents = total_sents
            total_sects, total_frags, total_sents, nods = refresh_offsets(art)
            dif = total_sents - old_total_sents
            si += dif
            bmark += dif
            if dif > 0:
                pos += [0]*dif
                visible += [True]*dif
                passable += [False]*dif

        #:::
        if chr(ch) in notes_keys:
            win = cur.newwin(4, width, ypos + 2, left)
            win.bkgd(' ', cur.color_pair(INFO_COLOR))  # | cur.A_REVERSE)
            win.refresh()
            default = cur_sent["comment"]
            prompt = "Comment:"
            cur_note = notes_dict[chr(ch)]
            _note = cur_note != ""
            if cur_note != "":
                default = ""
                if cur_note in cur_sent["notes"]:
                    default = cur_sent["notes"][cur_note]
            if chr(ch) == "_":
                prompt = "What do you want to research on? (you can leave it blank)"
            elif chr(ch) == "!":
                prompt = "What is your idea?"
            elif chr(ch) == "?":
                prompt = "What is your question?"
            elif chr(ch) == "*":
                prompt = "You can write down the point or leave it blank"
            elif chr(ch) == ":":
                prompt = "Any comment"
            _comment, _ = minput(win, 0, 0, prompt, default=default, mode=1, color = INPUT_COLOR)
            #show_info(main_info)
            _comment = _comment if _comment != "<ESC>" and _comment != "q" else cur_sent["comment"]
            art_changed = True
            if not _note:
                cur_sent["notes"]["comment"]=_comment
            elif _note:
                if _comment or (chr(ch) in ["*","_"]):
                    cur_sent["notes"][cur_note] = _comment
                    if chr(ch) in ["*"]:
                        cur_nod = "I see!" 
                        set_nod(cur_nod, cur_sent, nods, visible, bmark, si, elapsed_time)
                        si,bmark = moveon(si, visible, passable, nods)

        if ch == ord('t'):
            subwins = {
                "select tag": {"x": 7, "y": 5, "h": 15, "w": 68}
            }
            choice = ''
            mi = 0
            tags_menu = {"tags (one per line)": "", "select tag": ""}
            tags_options = {}
            cur_tags = load_obj("tags", "", [""])
            tags_options["select tag"] = cur_tags
            extra = {}
            extra["tags (one per line)"] = {"type":"mline_input", "rows":12, "addto":"select tag"}
            while choice != 'q':
                tags = ""
                if "tags" in art:
                    for tag in art["tags"]:
                        tags += tag + ", "
                tags_menu["tags (one per line)"] = tags
                choice, tags_menu, mi = show_menu(tags_menu, tags_options,
                                                  shortkeys={"s": "select tag"},
                                                  subwins=subwins, extra=extra, mi=mi, title="tags")
                if choice == "select tag":
                    new_tag = tags_menu["select tag"].strip()
                    if not "tags" in art:
                        art["tags"] = [new_tag]
                    elif not new_tag in art["tags"]:
                        art["tags"].append(new_tag)
                else:
                    new_tags = tags_menu["tags (one per line)"].split(",")
                    art["tags"] = []
                    for tag in new_tags:
                        tag = tag.strip()
                        if tag != '' and not tag in art["tags"]:
                            art["tags"].append(tag)
                    if len(art["tags"]) > 0:
                        insert_article(saved_articles, art)
                    else:
                        remove_article(saved_articles, art)

                    save_obj(saved_articles, "saved_articles", "articles")
            text_win.erase()
            text_win.refresh(0, 0, 2, 0, rows - 2, cols - 1)
        if ch == ord('f'):  # show figures
            ypos = 5
            fig_win = cur.newwin(10, width, ypos + 2, left)
            fig_win.bkgd(' ', cur.color_pair(HL_COLOR))  # | cur.A_REVERSE)
            fig_win.border()
            opts = []
            fig_num = 1
            if not figures or figures is None:
                show_msg("No figure to show")
            else:
                for fig in figures:
                    fig_num += 1
                    caption = fig["caption"]
                    if not caption.startswith("Figure"):
                        caption = "Figure " + str(fig_num) + ":" + caption
                    opts.append(caption)

                fi, _ = select_box({"Figures":opts}, fig_win, 0, in_row=False, border=True, ret_index =True)
                if fi >= 0:
                    fname = app_path + "/nodcast_temp.html"
                    if not figures_created:
                        create_figures_file(figures, fname)
                        figures_created = True
                    webbrowser.open("file://" + fname + "#fig" + str(fi))
        if ch == ord('m'):
            choice = ''
            while choice != 'q':
                choice, theme_menu, _ = show_menu(theme_menu, theme_options, title="theme")
            save_obj(theme_menu, conf["theme"], "theme")
            text_win.erase()
            text_win.refresh(0, 0, 0, 0, rows - 2, cols - 1)
# eee
        if ch == ord('q'):  # before exiting artilce
            save_obj(nr_opts, "settings", "", common = True)
            if art_changed and not collect_art:
                if not "visits" in art:
                    art["visits"] = 1
                else:
                    art["visits"] += 1
                art["last_visit"] = datetime.datetime.today().strftime('%Y-%m-%d')
                ii = 1
                begin = 1
                sect_counter = 0
                for sect in art["sections"]:
                    ii += 1
                    frag_counter = 0
                    for frag in sect["fragments"]:
                        _frag = {"sents":[]}
                        sent_counter = 0
                        begin = sent_counter
                        for sent in frag["sents"]:
                            ii += 1
                            _frag["sents"].append(sent)
                            for note in sent["notes"]:
                                if note != "" and ii > 0:
                                    _frag["ref_art"] = art_id
                                    _frag["ref_title"] = art["title"]
                                    _frag["ref_url"] = art["pdfUrl"]
                                    _frag["ref_sent"] = str(sect_counter) + "_" + str(frag_counter) + "_" + str(begin) + "_" + str(sent_counter) 
                                    frag_id = art_id + "_" + _frag["ref_sent"]
                                    if not note in articles_notes:
                                        articles_notes[note] = {art_id:{frag_id:_frag}}
                                    elif not art_id in articles_notes[note]:
                                        articles_notes[note][art_id] = {frag_id:_frag}
                                    elif not frag_id in articles_notes[note][art_id]:
                                        articles_notes[note][art_id][frag_id] = _frag
                            if sent["nod"] != "" and sent["nod"] != "next":
                                begin = sent_counter
                                _frag = {"sents":[]}
                            sent_counter += 1
                            # end for sent 
                        frag_counter += 1
                        # end for fragments
                    sect_counter += 1
                    # end for sect
                save_obj(articles_notes, "articles_notes", "articles")
            if not collect_art:
                insert_article(saved_articles, art)
                save_obj(saved_articles, "saved_articles", "articles")
                last_visited = load_obj("last_visited", "articles", [])
                insert_article_list(last_visited, art)
                save_obj(last_visited, "last_visited", "articles")
    return ""

key_neg = ord('-')
key_okay = RIGHT
def sel_nod(cur_nod, ch, ni): 
    if (cur_nod == "" or cur_nod == "skipped") and ch == key_neg:
        ni = 1
    elif cur_nod == "" and ch == key_okay:
        ni = 0
    elif cur_nod in right_nods:
        ni = right_nods.index(cur_nod)
    elif cur_nod in left_nods:
        ni = -1 * left_nods.index(cur_nod)
    ni = ni + 1 if ch == key_okay else ni - 1
    if ni > 0:
        ni = min(ni, len(right_nods) - 1)
        cur_nod = right_nods[ni]
    elif ni <= 0:
        ni = max(ni, -1 * (len(left_nods) - 1))
        cur_nod = left_nods[abs(ni)]
    return cur_nod

def contract_sel(si, visible, passable, nods):
    if si == 0:
        return 0
    si -= 1
    while si > 0 and (not visible[si] or passable[si] or nods[si] == "next"):
        si -= 1
    return si

def move_bmark(si, nods):
    if si <= 0:
        return 0
    bmark = si
    while bmark > 1 and nods[bmark - 1] == "next":
        bmark -= 1
    return bmark

def expand_sel(si, visible, passable, nods, block_id="next"):
    total_sents = len(nods)
    while si < total_sents - 1 and (not visible[si] or passable[si] or nods[si] == block_id):
        si += 1
    if si < total_sents - 1:
        si += 1
        while (si < total_sents - 1 and not visible[si] or passable[si]):
            si += 1 
    return si

def set_nod(cur_nod, cur_sent, nods, visible, bmark, si, elapsed_time):
    cur_sent_length = len(cur_sent["text"].split())
    if cur_sent_length == 0:
        cur_sent_length = 0.01
    reading_time = round(elapsed_time / cur_sent_length, 2)
    if elapsed_time < 1 and nods[si] == "":
        cur_nod = "skipped"
    tries = 0
    avg = cur_sent["rtime"]
    tries = cur_sent["tries"]
    reading_time = avg + 1 / tries * (reading_time - avg)

    cur_sent["tries"] += 1
    cur_sent["rtime"] = reading_time
    for ii in range(bmark, si + 1):
        if ii < si:
            nods[ii] = "next"
        if cur_nod == "remove":
            visible[ii] = False
    if visible[si]:  # and (nods[si] == "" or nod_set):
        nods[si] = cur_nod
        cur_sent["nod"] = cur_nod
        if not cur_nod in cur_sent["nods"]:
            cur_sent["nods"].insert(0, cur_nod)
        else:
            #cur_sent["nods"].remove(cur_nod)
            cur_sent["nods"].insert(0, cur_nod)

def moveon(si, visible, passable, nods):
    si = expand_sel(si, visible, passable, nods)
    bmark = move_bmark(si, nods)
    return si, bmark

def create_figures_file(figures, fname):
    if figures is None:
        return
    html = """
        <html>
        <head>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                }
                .caption {
                    font-size:24px;
                    font-weight:400;
                    line-height:28px;
                    padding:2% 10% 10% 10%;
                }
                .imgbox {
                    display: grid;
                    margin:2% 10% 2% 10%;
                }
                .center-fit {
                    max-width: 100%;
                    max-height: 100vh;
                    margin: auto;
                }
            </style>
        </head>
        <body>
    """
    for fnum, fig in enumerate(figures):
        url = fig["id"]
        if not url.startswith("http"):
            url = "https://dimsum.eu-gb.containers.appdomain.cloud/api/media/" + url
        caption = fig["caption"]
        html += """
            <div class="imgbox" id='fig""" + str(fnum) + """'>
                <img class="center-fit" src='""" + url + """'>
            </div>
            <div class="caption">""" + caption + """</div>
       """
    html += "</body></html>"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(html)

def mprint(text, win, color=None, attr = None, end="\n", refresh = False):
    if color is None:
        color = TEXT_COLOR
    m_print(text, win, color, attr, end, refresh)

# rrr
def refresh_menu(menu, menu_win, sel, options, shortkeys, subwins, start_row=0, horiz=False, active_sel=True, pad=True):
    global clG
    menu_win.erase()
    mprint("", menu_win)

    ver_file = Path('version.txt')
    if ver_file.is_file():
        with open("version.txt", 'r') as f:
            version = f.readline()
    mprint(" " * 5 + "Checkideh " + version, menu_win, color=TEXT_COLOR)
    row = 3
    col = 5
    rows, cols = menu_win.getmaxyx()
    _m = max([len(x) for x in menu.keys()]) + 5
    gap = col + _m
    prev_length = 0
    for k, v in menu.items():
        colon = ":"  # if not k in options else ">"
        key = k
        v = v.replace("\n", ",").strip() 
        if "button_hidden" in str(v):
            continue
        if k in shortkeys.values():
            sk = list(shortkeys.keys())[list(shortkeys.values()).index(k)]
            key = sk + ") " + k
        if k == sel:  # and not sel in subwins:
            if active_sel:
                color = CUR_ITEM_COLOR
            else:
                color = SEL_ITEM_COLOR
        else:
            color = ITEM_COLOR
        fw = cur.A_BOLD
        if "button_light" in str(v):
            fw = None

        if k.startswith("sep"):
            col = 5
            if horiz:
                row += 1
            if v:
                print_there(row, col, str(v) + colon, menu_win, TEXT_COLOR)
        else:
            if str(v).startswith("button") and horiz:
                col += prev_length + 2
                prev_length = len(key)
            print_there(row, col, "{:<{}}".format(key, _m), menu_win, color, attr=fw)
            if not str(v).startswith("button"):  # and not k in subwins:
                print_there(row, gap, colon, menu_win, color, attr=cur.A_BOLD)

        if not str(v).startswith("button"):  # and not k in subwins:
            if "color" in k or (k in options and options[k] == colors):
                if k in color_map:
                    _color = color_map[k]
                else:
                    _color = int(menu[k])
                print_there(row, col + _m + 2, "{:^5}".format(str(v)), menu_win, _color)
            elif not k.startswith("sep"):
                tv = v
                lim = cols - (col + _m) - 10
                if len(str(v)) > lim:
                    tv = str(v)[: lim] + "..."
                print_there(row, col + _m + 2, "{}".format(tv), menu_win, TEXT_COLOR)
        if not horiz or not str(v).startswith("button"):
            col = 5
            row += 1

    rows, cols = std.getmaxyx()
    start_row = max(start_row, 0)
    start_row = min(start_row, 2 * rows)
    if hotkey == "":
        logging.info(f"Refreshing ...", menu)
        if pad:
            menu_win.refresh(start_row, 0, 0, 0, rows - 2, cols - 1)
        else:
            std.refresh()
            menu_win.refresh()
        for k, item in subwins.items():
            sub_menu_win = cur.newwin(item["h"],
                                      item["w"],
                                      item["y"],
                                      item["x"])
            si = options[k].index(menu[k]) if k in menu and menu[k] in options else -1
            sub_menu_win.bkgd(' ', cur.color_pair(TEXT_COLOR))  # | cur.A_REVERSE)
            show_submenu(sub_menu_win, options[k], si, active_sel=False)


def get_sel(menu, mi):
    mi = max(mi, 0)
    mi = min(mi, len(menu) - 1)
    return list(menu)[mi], mi


win_info = None


def confirm_all(msg):
    return confirm(msg, acc=['y', 'n', 'a'])


def confirm(msg, acc=['y', 'n'], color=WARNING_COLOR):
    win_info.bkgd(' ', cur.color_pair(color))  # | cur.A_REVERSE)
    mbeep()
    temp = old_msg
    msg = "Are you sure you want to " + msg + "? (" + "/".join(acc) + ")"
    _confirm = get_confirm(win_info, msg, acc)
    show_info(old_msg)
    return _confirm

old_msg = ''
def show_info(msg, color=INFO_COLOR, bottom=True, title = "Info"):
    global win_info, old_msg
    rows, cols = std.getmaxyx()
    if bottom:
        old_msg = msg
        win_info = cur.newwin(1, cols, rows - 1, 0)
    else:
        mwin = cur.newwin(rows -4, 2* cols //3, 2, cols //6)
        mwin.bkgd(' ', cur.color_pair(HL_COLOR))  # | cur.A_REVERSE)
        mrows, mcols = mwin.getmaxyx() 
        mwin.border()
        print_there(0, 1, title, mwin)
        footer =  "q: Close "
        nlines = msg.count('\n')
        if nlines > rows - 5:
            footer += "; Up/Down: Scroll the message"
        footer = textwrap.shorten(footer, mcols)
        print_there(mrows-1, 1, footer, mwin)
        mwin.refresh()
        win_info = cur.newpad(rows * 2, (2 * cols // 3) - 2)
    win_info.bkgd(' ', cur.color_pair(color))  # | cur.A_REVERSE)
    win_info.erase()
    if bottom:
        if len(msg) > cols - 15:
            msg = msg[:(cols - 16)] + "..."
        print_there(0, 1, " {} ".format(msg), win_info, color)
        win_info.clrtoeol()
        win_info.refresh()
    else:
        left = cols // 6 + 1
        start_row = 0
        ch = 0
        while ch != ord('q'):
            win_info.erase()
            # msg = textwrap.indent(textwrap.fill(msg),'  ')
            mprint(msg, win_info, color)
            start_row = max(start_row, 0)
            start_row = min(start_row, 2 * rows)
            win_info.refresh(start_row, 0, 3, left, rows - 4, cols - 1)
            ch = get_key(std)
            if ch == UP:
                if start_row > 0:
                    start_row -= 10
                else:
                    mbeep()
            elif ch == DOWN:
                if start_row < nlines - rows + 5:
                    start_row += 10
                else:
                    mbeep()
            elif ch != ord('q'):
                mbeep()


def show_msg(msg, color=MSG_COLOR):
    temp = old_msg
    mbeep()
    show_info(msg + "; press any key", color)
    std.getch()
    show_info(temp)


def show_warn(msg, color=WARNING_COLOR, bottom=True, stop=True):
    if bottom:
        msg += "; press any key..."
        temp = old_msg
    show_info(msg, color, bottom)
    ch = ''
    if bottom and stop:
        ch = std.getch()
        show_info(temp)
    return ch

def show_err(msg, color=ERR_COLOR, bottom=True):
    if bottom:
        msg += "; press any key..."
        temp = old_msg
    show_info(msg, color, bottom)
    if bottom:
        std.getch()
        show_info(temp)

def load_preset(new_preset, options, folder=""):
    global TEXT_COLOR
    menu = load_obj(new_preset, folder, common =True)
    if menu == None and folder == "theme":
        menu = load_obj("chk_def_" + new_preset, folder, data_dir=False)
        save_obj(menu, new_preset, folder, common=True)
    if menu == None and folder == "theme":
        init = {'preset': 'default', "sep1": "colors", 'text-color': '247', 'back-color': '233', 'item-color': '71','cur-item-color': '251', 'sel-item-color': '33', 'title-color': '28', "sep2": "reading mode",           "dim-color": '241', 'bright-color':"251", "highlight-color": '236', "hl-text-color": "250", "inverse-highlight": "True", "bold-highlight": "True", "bold-text": "False", "input-color":"234", "sep5": "Feedback Colors"}
        default = load_obj("chk_def_default", folder, data_dir=False)
        light = load_obj("chk_def_light", folder, data_dir=False)
        neon = load_obj("chk_def_neon", folder, data_dir=False)
        save_obj(default, "default", folder, common=True)
        save_obj(light, "light", folder, common=True)
        save_obj(neon, "neon", folder, common=True)
        if default is None:
            default = init 
        pp = {}
        for name, mm in {"default":default,"light":light, "neon": neon}.items():
            if mm is None:
                continue
            nn = {}
            for k in init:
                if not k in mm:
                    nn[k] = init[k]
                else:
                    nn[k] = mm[k]
            for k in nods_list:
                v = 250 if not k in nod_colors else nod_colors[k]
                if not k in mm:
                    nn[k] = str(v)
                else:
                    nn[k] = mm[k]
            save_obj(nn, name, "theme", common = True)
        new_preset = "default"

    if menu == None and folder == "template":
        text = {"preset": "txt", "top": "", "title": "# {title}", "section-title": "## {section-title}",
                "paragraph": "{paragraph}{newline}{newline}", "bottom": "{url}"}
        html = {"preset": "html", "top": "<!DOCTYPE html>{newline}<html>{newline}<body>", "title": "<h1>{title}</h1>",
                "section-title": "<h2>{section-title}</h2>", "paragraph": "<p>{paragraph}</p>",
                "bottom": "<p>source:{url}</p></body>{newline}</html>"}
        for mm in [text, html]:
            mm["save as"] = "button"
            mm["reset"] = "button"
            mm["delete"] = "button"
            mm["save and quit"] = "button"
        save_obj(text, "txt", folder, common =True)
        save_obj(html, "html", folder, common =True)
        new_preset = "txt"

    menu = load_obj(new_preset, folder, common =True)
    menu["preset"] = new_preset
    menu_dir = user_data_dir(appname, appauthor) + "/" + folder
    saved_presets = [Path(f).stem for f in Path(menu_dir).glob('*') if f.is_file()]
    options["preset"] = saved_presets

    if folder == "theme":
        for k in feedbacks:
            options[k] = colors
        reset_colors(menu)
    conf[folder] = new_preset
    save_obj(conf, "conf", "", common =True)
    return menu, options


def select_box(in_opts, mwin, list_index = 0, ni=0, in_row=False, title="", border = False, in_colors=[], color = INPUT_COLOR, ret_index = False):
    ch = 0
    list_names = in_opts.keys()
    mrows, mcols = mwin.getmaxyx() 
    if in_row:
        footer =  "Enter/number: Insert | q/ESC: Close "
    else:
        footer = "Right: Select, Left:Cancel"
    okay = RIGHT
    cancel = LEFT
    footer = textwrap.shorten(footer, mcols)
    print_there(mrows-1, 1, footer, mwin)
    mwin.refresh()
    if not border:
        win = mwin.derwin(mrows - 2, mcols, 1, 0)
    else:
        win = mwin.derwin(mrows - 2, mcols - 2, 1, 1)
    win.bkgd(' ', cur.color_pair(color))  # | cur.A_REVERSE)
    if not in_opts:
        show_err("No item to list")
        return ni, list_index
    horiz = False
    row_cap = 3 if in_row else 1
    col_cap = 5 
    opt_colors = {}
    if not horiz:
       _cap = col_cap
    while ch != 27 and ch != ord('q'):
        opts = []
        list_index = min(max(0, list_index), len(in_opts) -1)
        for i, k in enumerate(list(in_opts.values())[list_index]):
            new_k = str(i) + ") " + k
            opts.append(new_k)
            if in_colors:
                opt_colors[new_k] = in_colors[k] if k in in_colors else TEXT_COLOR 

        _size = max([len(s) for s in opts]) + 2
        ni = max(ni, 0)
        if ni > len(opts) - 1:
            ni = 0
        win.erase()
        cc = len(in_opts)*8 
        if len(in_opts) > 1:
            for i, st in enumerate(list_names):
                st = " " + st.ljust(8)
                if i == list_index:
                    print_there(0, cc, st, mwin, color)
                else:
                    print_there(0, cc, st, mwin, INFO_COLOR)
                cc -= len(st) + 2
        mwin.refresh()
        if not in_row:
            show_submenu(win, opts, ni, in_colors=opt_colors, color=color)
            win.refresh()
        else:
            for i, k in enumerate(opts):
                if horiz:
                    row = (i // row_cap) + 2
                    col = (i % row_cap) * _size + 1
                else:
                    row = (i % col_cap) + 1 
                    col = (i // col_cap) * _size + 1
                if i == ni:
                    print_there(row, col, k, win, INFO_COLOR)
                else:
                    print_there(row, col, k, win, color)
            win.refresh()
        ch = get_key(std)
        if is_enter(ch) or (ch == cur.KEY_IC):
            break
        if chr(ch).isdigit():
            ni = int(chr(ch))
            break
        elif ch == DOWN:
            ni += _cap if horiz else 1
        elif ch == ord('q'):
            ni = -1
            break
        elif ch == UP:
            if ni <= 0 or (horiz and ni < _cap):
                ni = -1
                break
            ni -= _cap if horiz else 1
        elif ch == RIGHT:
            if not in_row and len(in_opts) == 1:
                if RIGHT == cancel:
                    ni = -1
                break
            elif ni + _cap >= len(opts) and list_names:
                if list_index > 0:
                    list_index -= 1
                else:
                    list_index = len(opts) - 1
            else:
                ni += 1 if horiz else _cap
        elif ch == ord('\t'):
            if list_names:
                if list_index < len(in_opts) - 1:
                    list_index += 1
                else:
                    list_index = 0
            else:
                ni = -1
                break
        elif ch == LEFT:
            if not in_row and len(in_opts) == 1:
                if LEFT == cancel:
                    ni = -1
                break
            elif ni - _cap >= 0:
                ni -= 1 if horiz else _cap
            else:
                if not list_names:
                    ni = -1
                    break
                elif list_index < len(in_opts) - 1:
                    list_index += 1
                else:
                    list_index = 0
        elif ch != 27 and ch != ord('q'):
            mbeep()
            show_info("Use left arrow key to select the item, the right key or q to cancel!")

    if ret_index:
        return ni, list_index
    opts = list(in_opts.values())[list_index]
    if ni >= 0:
        _nod = opts[ni]
        if _nod == "custom":
            custom_nod, _ = minput(win_info, 0, 1, "Enter a note or a nod (<Esc> to cancel):")
            _nod = custom_nod if custom_nod != "<ESC>" else ""
            if _nod != "":
                opts.append(_nod)
                save_obj(opts, "nod_opts", "")
        win.erase()
        return _nod, list_index
    else:
        win.erase()
        return 'NULL', -1

def show_submenu(sub_menu_win, opts, si, in_colors={}, color=None, active_sel=True, search=False):
    if color is None:
        color = ITEM_COLOR
    win_rows, win_cols = sub_menu_win.getmaxyx()
    blank = 3 if search else 2
    if len(opts) > win_rows - 1:
        win_rows = min(win_rows - blank, 10)
    start = si - win_rows // 2
    start = max(start, 0)
    if len(opts) > win_rows:
        start = min(start, len(opts) - win_rows)
    if search and start > 0:
        mprint("...", sub_menu_win, color)
    footer = ""
    is_color = in_colors or opts == colors
    c_attr = None
    for vi, v in enumerate(opts[start:start + win_rows]):
        if is_color:
            if opts == colors:
                cc = v
                c_attr = cur.A_REVERSE
                item_w = 8
            else:
                cc = in_colors[v] if in_colors and v in in_colors else TEXT_COLOR
                c_attr = cur.A_REVERSE
                item_w = win_cols - 6
        if start + vi == si:
            sel_v = v
            if len(v) > win_cols:
                footer = v
                v = v[:win_cols - 5] + "..."
            if is_color:
                mprint(" {:<{}}".format(str(v),item_w + 4), sub_menu_win, int(cc), attr=c_attr)
            elif active_sel:
                mprint(" {:<8}".format(str(v)), sub_menu_win, CUR_ITEM_COLOR)
            else:
                mprint(" {:<8}".format(str(v)), sub_menu_win, SEL_ITEM_COLOR)
        else:
            if len(v) > win_cols:
                v = v[:win_cols - 5] + "..."
            if is_color:
                mprint(" {:<{}}".format(v, item_w), sub_menu_win, int(cc), attr=c_attr)
            else:
                #logging.info(f"submenu: {v}")
                mprint(" {:<8}".format(str(v)), sub_menu_win, color)
    if start + win_rows < len(opts):
        mprint("...", sub_menu_win, color)
    # if footer != "":
    #   mprint(footer, sub_menu_win, cW)
    sub_menu_win.refresh()
# mmm
def show_menu(menu, options, shortkeys={}, hotkeys={}, title="", mi=0, subwins={}, info="h) help | q) quit", extra={}):
    global menu_win, common_subwin 

    ch = 0  # user choice
    rows, cols = std.getmaxyx()
    height = rows - 1
    width = cols

    for opt in menu:
        if opt in options and menu[opt] == "":
            menu[opt] = options[opt][0] if options[opt] else ""

    if info.startswith("error"):
        show_err(info)
    else:
        for k, v in hotkeys.items():
            info += " | " + k + ") " + v
        info += "  (case sensitive)"
        show_info(info)

    mprint(title.center(rows), menu_win, TITLE_COLOR)
    hide_cursor()
    last_preset = ""
    if "preset" in menu:
        last_preset = menu["preset"]
        shortkeys["r"] = "reset"
        shortkeys["s"] = "save as"
        shortkeys["q"] = "save and quit"

    row = 3
    col = 5
    mt, st, old_st  = "", "", ""
    old_val = ""
    prev_ch = 0
    edit_mode = False
    while ch != ord('q'):
        sel, mi = get_sel(menu, mi)
        is_hidden = menu[sel].startswith("button_hidden")
        passable_item = sel.startswith('sep') or is_hidden
        sub_menu_win = common_subwin
        key_set = False
        cmd = ""
        start_row = 0
        if row + start_row + mi >= 3 * rows - 2:
            start_row = 3 * (rows - 2) - 2 
        if row + start_row + mi >= 2 * rows - 2:
            start_row = 2 * (rows - 2) -2
        elif row + start_row + mi >= rows - 1:
            start_row = rows - 2
        refresh_menu(menu, menu_win, sel, options, shortkeys, subwins, start_row, active_sel = True)
        if edit_mode and sel not in options and not str(menu[sel]).startswith("button") and not sel.startswith("sep"):
            cur_val = menu[sel]
            _m = max([len(x) for x in menu.keys()]) + 5
            mode = 0
            if extra and sel in extra and "type" in extra[sel] and extra[sel]["type"] == "mline_input":
                win_input = cur.newwin(extra[sel]["rows"], cols - 10, row + mi, col)
                mode = 2
                prompt = sel
                cur_values = "\n".join([x.strip() for x in menu[sel].split(',')])
            else:
                win_input = cur.newwin(1, cols - 10, row + mi, col)
                prompt = "{:<{}}".format(sel, _m) + ": "
                cur_values = menu[sel]
            win_input.bkgd(' ', cur.color_pair(CUR_ITEM_COLOR))  # | cur.A_REVERSE)
            val, ch = minput(win_input, 0, 0, prompt,  default=cur_values, mode = mode)
            if val != "<ESC>":
                if extra and sel in extra and "addto" in extra[sel] and val.strip() != "":
                    addto_list = extra[sel]["addto"]
                    new_tags = val.split("\n")
                    new_tags = list(filter(None, new_tags))
                    for tag in new_tags:
                        tag = tag.strip()
                        if tag != '' and not tag in options[addto_list]:
                            options[addto_list].append(tag)
                val = val.replace("\n",",")
                val = textwrap.fill(val, width=cols - 12 - _m)
                menu[sel] = val
            else:
                menu[sel] = cur_val
                ch = ord('q')

            edit_mode = False
            key_set = True
            ret_mi = mi - 1
            if ch != UP and ch != 27:
                ch = DOWN
                ret_mi = mi + 1
            return sel, menu, ret_mi 
        if sel in subwins:
            if menu[sel] in options[sel]:
                si = options[sel].index(menu[sel])
            rows, cols = std.getmaxyx()
            sub_menu_win = cur.newwin(subwins[sel]["h"],
                                      subwins[sel]["w"],
                                      subwins[sel]["y"],
                                      subwins[sel]["x"])
            sub_menu_win.bkgd(' ', cur.color_pair(TEXT_COLOR))  # | cur.A_REVERSE)
        if (not passable_item and not key_set) or hotkey != "":
            prev_ch = ch
            ch = get_key(std)
        elif passable_item and mi == 0:
            ch = DOWN
        elif passable_item and mi == len(menu) - 1:
            ch = UP
        if ch == cur.KEY_RESIZE:
            mbeep()
            refresh_menu(menu, menu_win, sel, options, shortkeys, subwins, start_row)
        elif (is_enter(ch) or 
                ch == RIGHT or 
                (chr(ch) in shortkeys and ch == prev_ch) or
                (ch == DOWN and mi == len(menu) - 1 and sel in subwins)):
            is_button = str(menu[sel]).startswith("button")
            if is_button:
                if sel == "save as" or sel == "reset" or sel == "delete" or sel == "save and quit":
                    cmd = sel
                else:
                    return sel, menu, mi
            elif sel.startswith("sep"):
                mi += 1
            elif not sel in options:
                edit_mode = True
            else:
                si = 0
                if sel in options and menu[sel] in options[sel]:
                    si = options[sel].index(menu[sel])
                if "preset" in menu:
                    last_preset = menu["preset"]
                refresh_menu(menu, menu_win, sel, options, shortkeys, subwins, start_row, active_sel = False)
                si, canceled, st = open_submenu(sub_menu_win, options, sel, si, title, extra)
                if not canceled:
                    is_combo = extra and sel in extra and "type" in extra[sel] and extra[sel]["type"] == "combo-box"
                    if is_combo:
                        if not str(options[sel][si]).lower().startswith(st.lower()):
                            options[sel].insert(0, st)
                            si = 0
                        else:
                            sep_index = options[sel].index("---")
                            cur_item = options[sel][si]
                            if si < sep_index:
                                options[sel].pop(si)
                            options[sel].insert(0, cur_item)
                            si = 0
                    menu[sel] = options[sel][si]
                    if "preset" in menu and sel != "preset":
                        if title == "theme":
                            reset_colors(menu)
                        save_obj(menu, menu["preset"], title, common =True)
                    if sel == "preset":
                        save_obj(menu, last_preset, title, common =True)
                        new_preset = menu[sel]
                        menu, options = load_preset(new_preset, options, title)
                        last_preset = new_preset
                        refresh_menu(menu, menu_win, sel, options, shortkeys, subwins, start_row)
                        show_info(new_preset + " was loaded")
                    if is_combo or sel in shortkeys.values():
                        return sel, menu, mi
        elif ch == DOWN:
            mi += 1
        elif ch == UP:
            mi -= 1
        elif ch == cur.KEY_NPAGE:
            mi += 10
        elif ch == cur.KEY_PPAGE:
            mi -= 10
        elif ch == LEFT or ch == 27 or ch == 127 or ch == cur.KEY_BACKSPACE:
            if title != "main":
                ch = ord('q')
        if cmd == "save and quit":
            ch = ord('q')
        elif ch == cur.KEY_DC or cmd == "delete":
            return "del@" + menu[sel] + "@" + sel, menu, mi
        elif (ch == ord('r') or cmd == "reset") and "preset" in menu:
            menu, options = load_preset("resett", options, title)
            last_preset = menu["preset"]
            # refresh_menu(menu, menu_win, sel, options, shortkeys, subwins, horiz, start_row)
            show_info("Values were reset to defaults")
        elif ((ch == ord('s') or ch == ord('z') or cmd == "save as") and "preset" in menu):
            if ch == ord('z'):
                fname = "chk_def_" + menu["preset"]
            else:
                fname, _ = minput(win_info, 0, 1, "Save as:")
            if fname == "<ESC>":
                show_info("")
            else:
                if fname.startswith("chk_def_"):
                    save_obj(menu, fname, title, data_dir=False)
                    fname = menu["preset"]
                else:
                    save_obj(menu, fname, title, common= True)

                menu["preset"] = fname

                if title == "theme":
                    reset_colors(menu)
                show_info(menu["preset"] + " was saved as " + fname)
                if not fname in options["preset"]:
                    options["preset"].append(fname)
                last_preset = fname
                refresh_menu(menu, menu_win, sel, options, shortkeys, subwins, start_row)
        elif ch == ord('h'):
            return "h", menu, mi
        elif chr(ch) in hotkeys:
            return chr(ch), menu, mi
        elif ch != ord('q') and chr(ch) in shortkeys:
            if not shortkeys[chr(ch)] in menu:  # then it's a hotkey
                return chr(ch), menu, mi
            else:
                mi = list(menu.keys()).index(shortkeys[chr(ch)])
                sel, mi = get_sel(menu, mi)
                if str(menu[sel]).startswith("button"):
                    return sel, menu, mi
        elif ch == ord('q') and title == "main":
            pass
            # mbeep()
            # _confirm = confirm(win_info, "you want to exit the program")
            # if _confirm != "y":
            #    ch = 0
    return chr(ch), menu, mi

def open_submenu(sub_menu_win, options, sel, si, title, extra):
    ch = 0
    st = ""
    back_st = ""
    old_si = si
    cancel = False
    temp_msg = old_msg
    is_combo = extra and sel in extra and "type" in extra[sel] and extra[sel]["type"] == "combo-box"
    info = "Enter/Right: select | qq/ESC/Left: cancel "    
    if sel == "preset" or is_combo:
        info += " | Del: delete an item"

    show_info(info)
    while not is_enter(ch) and not ch == RIGHT:
        if ch == UP:
            if si == 0:
                si = old_si
                cancel = True
                break
            else:
                si -= 1
        elif ch == DOWN:
            si += 1
        elif ch == cur.KEY_NPAGE:
            si += 10
        elif ch == cur.KEY_PPAGE:
            si -= 10
        elif ch == cur.KEY_HOME:
            si = 0
        elif ch == cur.KEY_END:
            si = len(options) - 1
        elif ch == LEFT or ch == 27 or (back_st.lower() == "q" and chr(ch) == "q"):
            si = old_si
            cancel = True
            break
        elif ch == cur.KEY_DC:
            can_delete = True
            if sel == "preset" and len(options[sel]) == 1 or options[sel][si] == "default":
                show_warn("You can't delete the default " + title)
                can_delete = False
            elif is_combo:
                sep_index = options[sel].index("---")
                if si > sep_index:
                    show_warn("You can't remove predefined profiles which appear below separate line (---)")
                    can_delete = False
            if can_delete:
                item = options[sel][si]
                _confirm = confirm("delete '" + item)
                if _confirm == "y" or _confirm == "a":
                    del_obj(item, title, common = True)
                if item in options[sel]:
                    options[sel].remove(item)
                    if si > len(options[sel]):
                        si = len(options[sel]) 
                    if is_combo and "list_file" in extra[sel]:
                        save_obj(options[sel], extra[sel]["list_file"], "", common = True)
        elif ch != 0:
            if ch == 127 or ch == cur.KEY_BACKSPACE:
                st = st[:-1]
                back_st = back_st[:-1]
                si, st = find(options[sel], st, "", si)
            if chr(ch).lower() in string.printable:
                back_st += chr(ch)
                si, new_st = find(options[sel], st, chr(ch), si)
                if not is_combo:
                    if st == new_st:
                        mbeep()
                    else:
                        st = new_st
                else:
                    st += chr(ch)
        si = min(si, len(options[sel]) - 1)
        si = max(si, 0)
        sub_menu_win.erase()
        searchable = is_combo or len(options[sel]) > 8
        show_submenu(sub_menu_win, options[sel], si, search=searchable)
        if is_combo: 
            show_cursor()
            mprint("Search or Add:" + st, sub_menu_win, end ="")
        elif len(options[sel]) > 8:
            show_cursor()
            mprint("Search:" + st, sub_menu_win, end ="")
        sub_menu_win.refresh()
        ch = get_key(std)

    si = min(si, len(options[sel]) - 1)
    si = max(si, 0)
    hide_cursor()
    sub_menu_win.erase()
    show_info(temp_msg)
    return si, cancel, st

def find(list, st, ch, default):
    _find = st + ch
    _find = _find.lower().strip()
    for i, item in enumerate(list):
        if item.lower().startswith(_find): #or _find in item.lower() or item.lower() in _find: 
            return i, _find
    for i, item in enumerate(list):
        if _find in item.lower(): 
            return i, _find
    return default, st


colors = []


def start(stdscr):
    global colors, template_menu, template_options, theme_options, theme_menu, std, conf, query, filters, top_win, hotkey, menu_win, list_win, common_subwin, text_win, profile

    std = stdscr
    stdscr.refresh()
    now = datetime.datetime.now()
    logging.info(f"========================= Starting program at {now}")
    # logging.info(f"curses colors: {cur.COLORS}")

    rows, cols = std.getmaxyx()
    height = rows - 1
    width = cols
    # mouse = cur.mousemask(cur.ALL_MOUSE_EVENTS)
    list_win = cur.newwin(rows-1, cols-14, 1, 7)
    list_win.bkgd(' ', cur.color_pair(TEXT_COLOR))  # | cur.A_REVERSE)
    text_win = cur.newpad(rows * 50, cols - 1)
    text_win.bkgd(' ', cur.color_pair(TEXT_COLOR))  # | cur.A_REVERSE)
    menu_win = cur.newpad(rows*3 , cols)
    menu_win.bkgd(' ', cur.color_pair(TEXT_COLOR))  # | cur.A_REVERSE)
    common_subwin = cur.newwin(rows - 6, width // 2 + 5, 5, width // 2 - 5)
    common_subwin.bkgd(' ', cur.color_pair(TEXT_COLOR))  # | cur.A_REVERSE)

    cur.start_color()
    cur.curs_set(0)
    # std.keypad(1)
    cur.use_default_colors()
    # sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=24, cols=112))
    filters = {}
    filter_items = ["year", "conference", "dataset", "task"]
    last_visited = load_obj("last_visited", "articles", [])
    prev_menu =  load_obj("main_menu", "")
    profile_str = "profile (research area)"
    if True: #menu is None or (newspaper_imported and not "webpage" in menu):
        menu = {}
        menu[profile_str] = ""
        if last_visited:
            menu["recent articles"] = "button"
        else:
            menu["recent articles"] = "button_hidden"
        menu["notes, reviews and comments"] = "button"
        menu["saved articles"] = "button"
        menu["sepb1"] = ""
        menu["sep1"] = "Search AI-related papers"
        if is_obj("last_results", ""):
            menu["last results"] = "button"
        else:
            menu["last results"] = "button_hidden"
        menu["task"] = prev_menu["task"]
        menu["keywords"] = prev_menu["keywords"]
        menu["Go!"] = "button"
        menu["advanced search"] = "button"
        if newspaper_imported:
            menu["sepb2"] = ""
            menu["sep2"] = "Load website articles"
            menu["website articles"] = "button"
            menu["webpage"] = "button"
        menu["open file"] = "button"
        menu["settings"] = "button"

    options = {
        "saved articles": ["None"],
        # "recent articles":["None"],
        "task": ["All", "Reading Comprehension", "Machine Reading Comprehension", "Sentiment Analysis",
                 "Question Answering", "Transfer Learning", "Natural Language Inference", "Computer Vision",
                 "Machine Translation", "Text Classification", "Decision Making"],
        profile_str: ["---", "Computer Vision", "Image Recognition", "Speech Recognition", "Dialog Systems", "Information Retrieval", "Reinforcement Learning", "Reading Comprehension",
                 "Question Answering", "Knowledge Graph", "Text Generation", "Transfer Learning", "Natural Language Inference", 
                 "Machine Translation", "Sentiment Analysis", "Text Classification", "Decision Making"],
    }

    extra = {}

    menu[profile_str] = profile
    conf = load_obj("conf", "", common = True)
    extra[profile_str] = {'type':'combo-box', 'list_file':'profiles'}
    profiles = load_obj("profiles","", common = True)
    if not profiles is None:
       options[profile_str] = profiles
    else:
       save_obj(options[profile_str], "profiles", "", common = True)
    task_file = Path('tasks.txt')
    if task_file.is_file():
        with open('tasks.txt', 'r') as f:
            options["task"] = ["All"] +  [t.strip() for t in f.readlines()]
    recent_arts = []
    width = 2 * cols // 3
    y_start = 6  # 5len(menu) + 5
    x_start = 60
    hh = rows - y_start - 1
    for art in last_visited[:10]:
        recent_arts.append(art["title"][:60] + "...")
    subwins = {}
    # options["recent articles"] =recent_arts
    # subwins = {"task":{"x":x_start,"y":y_start,"h":hh,"w":width}}


    if conf is None:
        conf = {"theme": "default", "template": "txt"}

    colors = [str(y) for y in range(-1, cur.COLORS)]
    if cur.COLORS > 100:
        colors = [str(y) for y in range(-1, 100)] + [str(y) for y in range(107, cur.COLORS)]

    theme_options = {
        "preset": [],
        "text-color": colors,
        "back-color": colors,
        "item-color": colors,
        "cur-item-color": colors,
        "sel-item-color": colors,
        "title-color": colors,
        "highlight-color": colors,
        "hl-text-color": colors,
        "dim-color": colors,
        "bright-color": colors,
        "input-color": colors,
        "inverse-highlight": ["True", "False"],
        "bold-highlight": ["True", "False"],
        "bold-text": ["True", "False"],
    }

    for k in feedbacks:
        theme_options[k] = colors
    theme_menu, theme_options = load_preset(conf["theme"], theme_options, "theme")
    template_menu, template_options = load_preset(conf["template"], template_options, "template")

    reset_colors(theme_menu)
    # os.environ.setdefault('ESCDELAY', '25')
    # ESCDELAY = 25
    std.bkgd(' ', cur.color_pair(TEXT_COLOR))  # | cur.A_REVERSE)
    clear_screen(std)
    top_win = cur.newwin(2, cols, 1, 0)
    top_win.bkgd(' ', cur.color_pair(TEXT_COLOR))  # | cur.A_REVERSE)
    ch = ''
    shortkeys = {"v": "saved articles", "l": "last results", "k": "keywords", "n": "nods", "r": "recent articles", "g":"Go!", "t": "tags", "s": "settings", "p": "webpage", "a": "advanced search", "n": "notes, reviews and comments", "w": "website articles", 'o': "open file"}
    mi = 0
    while ch != 'q':
        info = "h) help         q) quit"
        show_info(info)
        ch, menu, mi = show_menu(menu, options, extra= extra, shortkeys=shortkeys, mi=mi, subwins=subwins, title="main",
                                 hotkeys={"R": "resume last article"})
        save_obj(menu, "main_menu", "")
        if ch == "R":
            hotkey = "rrr"
        if ch == "advanced search":
            search()
        elif ch == profile_str:
            profile = menu[profile_str]
            conf["profile"] = profile
            save_obj(conf, "conf", "", common = True)
            save_obj(options[profile_str], "profiles", "", common = True)
        elif ch == "saved articles":
            save_folder = doc_path + '/Articles'
            Path(save_folder).mkdir(parents=True, exist_ok=True)
            show_files(save_folder, exts=["*.json", "*.pdf", "*.txt"])
        elif ch == "last results":
            show_last_results()
        elif ch == 'v' or ch == "reviewed articles":
            rev_articles()
        elif ch == 's' or ch == "notes, reviews and comments":
            saved_items()
        elif ch == "Go!":
            query = menu["keywords"] if "keywords" in menu else ""
            if menu["task"] != "All":
                filters = {"task": menu["task"]}
            fid = menu["task"] + "|" + menu["keywords"]
            conf = load_obj("conf","", common = True)
            conf["keywords"] = menu["keywords"]
            conf["fid"] = fid
            conf["filters"] = filters
            save_obj(conf, "conf", "", common = True)
            articles, ret = request(0)
            if len(articles) > 0 and ret == "":
                if isinstance(articles, tuple):
                    articles = articles[0]
                save_obj(articles, "last_results", "")
                ret = list_articles(articles, fid)
            if ret:
                show_err(ret[:200] + "...", bottom=False)
        elif ch == "webpage":
            webpage()
        elif ch == 's' or ch == "settings":
            settings()
        if ch == 'h' or ch == "help":
            # webbrowser.open("https://github.com/puraminy/nodcast")
            show_info(('\n'
                       '        _   __          ________           __ \n'
                       '       / | / /___  ____/ / ____/___ ______/ /_\n'
                       '      /  |/ / __ \/ __  / /   / __ `/ ___/ __/\n'
                       '     / /|  / /_/ / /_/ / /___/ /_/ (__  ) /_  \n'
                       '    /_/ |_/\____/\__,_/\____/\__,_/____/\__/  \n'
                       '  Please visit the following link to get an overview of Checkideh:\n'
                       '\thttps://checkideh.com\n\n'
                       '\tArrow keys)   Next, previous item\n'
                       '\tEnter)        Open/Run the selected item\n'
                       '\tPageUp/Down)  First/Last item\n'
                       '\n  Further help was provided in each section.\n'),
                      bottom=False)
            # name = '../README.md'
            # with open(name, "r") as f:
            #    data = f.read()
            # title, i = get_title(data, name)
            # if i > 0:
            #    data = data[i:]
            # art = {"id":"help", "pdfUrl":name, "title":title, "sections":get_sects(data)}
            # show_article(art)
        elif ch == 'w' or ch == "website articles":
            website()
        elif ch == "r" or ch == "recent articles":
            last_visited = load_obj("last_visited", "articles", [])
            if len(last_visited) > 0:
                list_articles(last_visited, "Recent Articles", group="last_visited")
            else:
                show_msg("There is no article in the list.")

        elif ch == 'o' or ch == 'open file':
            save_folder = doc_path + '/Files'
            Path(save_folder).mkdir(parents=True, exist_ok=True)
            show_files(save_folder, exts=['*.txt','*.json','*.squad'])
        last_visited = load_obj("last_visited", "articles", [])
        if len(last_visited) > 0:
            menu["recent articles"] = "button"
        elif len(last_visited) == 0:
            menu["recent articles"] = "button_hidden"
        if is_obj("last_results", ""):
            menu["last results"] = "button"
        else:
            menu["last results"] = "button_hidden"
        if ch in menu and menu[ch] == "button_hidden":
            mi = 0



def rev_articles(sel_art=None):
    saved_articles = load_obj("saved_articles", "articles", {})
    rev_articles = []
    for art_id, art in saved_articles.items():
        if "nods" in art and art["nods"][0] != "" and art["nods"][0] != "not reviewed":
            rev_articles.append(art)
    if len(rev_articles) == 0:
        show_msg("There is no article reviewed yet, to review an article enter a nod for its title.")
    else:
        list_articles(rev_articles, "Reviewed Articles", group="saved_articles", sel_art=sel_art)

#ttt
def refresh_files(save_folder, subfolders, files):
    menu = {}
    menu[".."] = "button"
    menu["back home"] = "button"
    menu["explore"] = "button"
    menu["new document"] = ""
    menu["new folder"] = ""
    menu["refresh"] = "button_hidden"
    _folder = save_folder
    if len(_folder) > 80:
        _folder = "[...]" + _folder[-80:]
    menu["sep1"] = _folder  
    for sf in subfolders:
        menu["[>] " + sf] = "button@folder"
    count = 1
    sk = {'q':"..", 'e':"explore", 'h':'back home'}
    for f in files:
        name = Path(f).name
        if len(name) > 60:
            name = name[:60] + "..."
        sk[str(count)] = name
        menu[name] = "button_light@file"
        count += 1
    return menu, sk 


# ttt
def show_files(save_folder, exts, depth = 1):
    global hotkey
    options = {}
    menu =[]
    mi = 7
    ch = 'refresh'
    while ch != 'q':
        if ch == "r" or ch == "refresh":
            clear_screen(std)
            subfolders = [f.name for f in os.scandir(save_folder) if f.is_dir()]
            files = []
            for ext in exts:
                _files = [str(Path(f)) for f in Path(save_folder).glob(ext) if f.is_file()]
                files.extend(_files)
            menu, sk = refresh_files(save_folder, subfolders, files)

        ch, menu, mi = show_menu(menu, options, mi=mi, hotkeys = {'r':'refresh'}, shortkeys = sk)
        if ch.startswith("[>"):
            sfolder = save_folder + "/" + ch[4:]
            show_files(sfolder, exts, depth + 1)
        elif ch == "..":
            ch = 'q'
        elif (ch == "back home" or ch == "H" or ch == 'h') and depth > 1:
            hotkey = 'q'*(depth -1)
        elif ch == "new folder":
            filepath = save_folder + "/"+menu["new folder"] 
            ch = "refresh"
        elif ch == "new document" or ch == "explore":
            filepath = save_folder 
            if ch == "new document":
                filepath += "/"+menu["new document"] + ".txt"
                with open(filepath, "w") as f:
                    print("Write your text file here, rename it and save, then refresh", file = f)
                openFile(filepath)
            else:
                platform_open(filepath)
            ch = "refresh"
        elif "del@" in ch:
            parts = ch.split("@")
            fname = parts[3].strip()
            filepath = save_folder + "/" + fname
            _confirm = ""
            if parts[2] == "folder":
                is_empty = not any(Path(filepath).iterdir())
                if not is_empty:
                    show_msg("The folder " + fname + " is not empty and can't be deleted!")
                else:
                    _confirm = confirm("to delete "+fname)
            else:
                    _confirm = confirm("to delete "+fname)
            if _confirm == "y":
                if parts[2] == "file":
                    Path(filepath).unlink()
                elif parts[2] == "folder":
                    Path(filepath).rmdir()
            ch = "refresh"
        elif ch != "q" and ch != "r" and ch != "refresh":
            index = mi - len(subfolders) - 7
            filename = files[index]
            ext = os.path.splitext(filename)[1]
            name = filename.split("/")[-1]
            _file = open(filename, "r")
            show_info("Openning ...  Please wait...")
            if ext == ".txt":
                data = _file.read()
                _file.close()
                title, i = get_title(data, name)
                if i > 0:
                    data = data[i:]
                art = {"id": filename, "pdfUrl": filename, "title": title, "sections": get_sects(data)}
                show_article(art)
            elif ext == ".json":
                arts = json.load(_file)
                list_articles(arts, fid = name)
            elif ext == ".squad":
                squad = json.load(_file)
                version = squad['version']
                fid = "SQUAD " + version
                data = squad['data']
                arts = []
                for i, part in enumerate(data[:3]):
                    art = {}
                    art["title"] = part["title"]
                    art["id"] = "squad-v-" + version + '-part-' + str(i)
                    art["pdfUrl"] = "na"
                    sections = []
                    k = 1
                    for j, p in enumerate(part["paragraphs"]):
                        sect = {}
                        sect["title"] = "Section " + str(j+1)
                        sect["fragments"] = get_frags(p["context"])
                        sections.append(sect)
                        if j > 0 and (j + 1) % 20 == 0:
                            art["title"] = part["title"] + " (" + str(k) + "-" + str(j+1) + ")"
                            art["id"] = "squad-v-" + version + '-part-' + str(i) + "-" + str(j)
                            art["pdfUrl"] = "na"
                            art["sections"] = sections
                            arts.append(art)
                            k = j + 2
                            art = {}
                            sections = []

                    if k > 1:
                        art["title"] = part["title"] + " (" + str(k) + "-" + str(j+1) + ")"
                        art["id"] = "squad-v-" + version + '-part-' + str(i) + "-" + str(j)
                        art["pdfUrl"] = "na"

                    art["sections"] = sections
                    arts.append(art)
                with open(save_folder + '/squad-' + version + '.json', 'w') as outfile:
                    json.dump(arts, outfile)
                list_articles(arts, fid)
            else:
                filepath = filename 
                openFile(filepath)

def saved_items():
    menu = {}
    menu["reviewes"]="button"
    menu["comments"] = "button"
    menu["tags"] = "button"
    shortkeys = {"s": "saved articles", "c": "comments", "n": "notes", "t": "tags", 'x': "open file"}
    options = {}
    tag_opts, tagged_art_list = refresh_tags()
    if tag_opts:
        options["tags"] = tag_opts
    notes, art_list = refresh_notes()
    if not art_list:
        menu["sep1"] = "Article Notes (No Note)"
    else:
        menu["sep1"] = "Article Notes"
        for k in notes:
            menu[k] = "button"
    mi = 0
    ch = ''
    while ch != 'q':
        info = "h) help         q) quit"
        show_info(info)
        ch, menu, mi = show_menu(menu, options, shortkeys=shortkeys, mi=mi)
        if ch == "c" or ch == "comments":
            list_notes("commented")
        elif ch == 't' or ch == "tagged articles":
            list_tags()
        elif ch == 's' or ch == "saved articles":
            saved_articles = load_obj("saved_articles", "articles", [])
            list_articles(saved_articles.values(), "Saved Articles")
        elif ch == "tags":
            list_tags()
        elif ch.startswith("del@tags"):
            save_obj(menu["tags"], "tags", "")
        elif ch == "reviewes":
            list_notes("reviewed")
        elif ch != 'q':
            sel_note = ch[:20]
            sel_note = sel_note.strip()
            articles = art_list[sel_note]
            list_notes(sel_note)

def settings():
    global theme_menu, doc_path, show_instruct
    choice = ''
    menu = load_obj("settings", "")
    font_size = 24
    path = '~/Documents/Checkideh'
    path.replace('/', os.sep)
    doc_path = os.path.expanduser(path)
    if menu is None:
        menu = {"theme": "button", "documents folder": "", "show instructions":""}
        menu["documents folder"] = doc_path
    else:
        if os.name == 'nt':
            font_size = menu["font size"]
        doc_path = menu["documents folder"]

    if doc_path.endswith("/"):
        doc_path = doc_path[:-1]
    options = {}
    menu["show instructions"] = "Enabled" if show_instruct else "Disabled"
    options["show instructions"] = ["Enabled", "Disabled"]
    if os.name == 'nt':
        menu["font size"] = font_size
        options["font size"] = [str(fs) for fs in range(18, 26)]

    menu["save and quit"] = "button"
    mi1 = 0
    while choice != 'q':
        choice, menu, mi1 = show_menu(menu, options, mi=mi1, title="settings", shortkeys={"f": "font size", "q": "save and quit", "t":"theme"})
        if choice == "theme":
            ch = ''
            mi = 0
            while ch != 'q':
                ch, theme_menu, mi = show_menu(theme_menu, theme_options, title="theme", mi = mi)
            save_obj(theme_menu, conf["theme"], "theme", common = True)
        if choice == "font size":
            resize_font_on_windows(int(menu["font size"]))  # std)
            show_msg("The font size will changes in the next run of the application")

    show_instruct = menu["show instructions"] == "Enabled"
    doc_path = menu["documents folder"]
    Path(doc_path).mkdir(parents=True, exist_ok=True)
    save_obj(menu, "settings", "", common = True)

def list_notes(note):
    saved_articles = load_obj("saved_articles", "articles", {})
    art_status = load_obj("articles_notes", "articles", {})
    if not note in art_status:
        return
    arts = art_status[note]
    n_art = {"id":note, "title": "Sentences for " + note ,"pdfUrl":"na", "sections":[]}
    new_sect = {"title":"all"}
    frags = []
    old_art_id = 0
    for art_id, frags_dict in arts.items():
        if art_id in saved_articles:
            avail = " [Enter to open]"
        else:
            avail = " [Not available]"
        for frag in frags_dict.values():
            title = frag["ref_title"]
            title = title if art_id != old_art_id else "Same article"
            old_art_id = art_id
            ref = new_sent("[Ref] " + title + avail)
            ref["passable"] = "True"
            frag["sents"].append(ref)
            frags.append(frag)
    frags[-1]["end_mark"] = "True"
    new_sect["fragments"] = frags
    n_art["sections"].append(new_sect)

    show_article(n_art, collect_art = True)

def list_comments():
    saved_articles = load_obj("saved_articles", "articles", [])
    n_art = {"id":"comments", "title": "Comments" ,"pdfUrl":"na", "sections":[], "comments":{}}
    for art_id, art in saved_articles.items():
        if "comments" in art:
            title = art["title"]
            if title == "Comments":
                continue
            new_sect = {"title":title}
            ii = 2
            frags = []
            for si, comment in art["comments"].items():
                if si <= 0:
                    continue
                frag = {"text":str(si) + ") " + art["sents"][si]}
                n_art["comments"][ii] = comment
                frags.append(frag)
                ii += 1
            new_sect["fragments"] = frags
            n_art["sections"].append(new_sect)
    if n_art['sections']:
        show_article(n_art, collect_art = True)
    else:
        show_msg("There is no comment in the saved articles.")

def refresh_notes(in_note="notes"):
    saved_articles = load_obj("saved_articles", "articles", {})
    art_status = load_obj("articles_" + in_note, "articles", {})
    N = len(saved_articles)
    art_num = {}
    art_list = {}
    note_list = []
    for note, arts in art_status.items():
        if note != "" and not note in note_list:
            note_list.append(note)
        art_num[note] = (0, 0)
        art_list[note] = []
        for art_id in arts.keys():
            if art_id in saved_articles:
                art = saved_articles[art_id]
                art_num[note] = (art_num[note][0] + 1, art_num[note][1] + len(arts[art_id]))
                if not art in art_list[note]:
                    art_list[note].append(art)
    ret = []
    for note in note_list:
        if art_num[note][0] == 0:
            del art_status[note]
        else:
            ret.append(note.ljust(20) + str(art_num[note][1]) + " cases in " +  str(art_num[note][0]) + " articles!")
    save_obj(art_status, "articles_" + in_note, "articles")
    return ret, art_list

def refresh_notes_2(in_note="notes"):
    saved_articles = load_obj("saved_articles", "articles", {})
    N = len(saved_articles)
    art_num = {}
    art_list = {}
    note_list = []
    for art in saved_articles.values():
        if not in_note in art:
            continue
        art_status = art[in_note]
        for notes in art_status:
            for note in notes:
                if note != "" and not note in note_list:
                    note_list.append(note)
                if note in art_num:
                    art_num[note] += 1
                    if not art in art_list[note]:
                        art_list[note].append(art)
                else:
                    art_num[note] = 1
                    art_list[note] = [art]
    opts = {in_note: []}
    for note in note_list:
        opts[in_note].append(note.ljust(40) + str(art_num[note]))
    return opts, art_list


def refresh_tags():
    saved_articles = load_obj("saved_articles", "articles", {})
    N = len(saved_articles)
    art_num = {}
    art_list = {}
    tag_list = []
    for art in saved_articles.values():
        if not "tags" in art:
            continue
        for tag in art["tags"]:
            tag = tag.strip()
            if not tag in tag_list:
                tag_list.append(tag)
            if tag in art_num:
                art_num[tag] += 1
                if not art in art_list[tag]:
                    art_list[tag].append(art)
            else:
                art_num[tag] = 1
                art_list[tag] = [art]
    opts = []
    for tag in tag_list:
        opts.append(tag.ljust(40) + str(art_num[tag]))
    save_obj(tag_list, "tags", "")
    return opts, art_list

def list_tags():
    subwins = {
            "tags":{"x":7,"y":5,"h":15,"w":68},
            }
    choice = ''
    opts = {}
    opts["tags"], art_list = refresh_tags()
    if not art_list:
        show_msg("There is no tagged article!")
        return
    clear_screen(std)
    mi = 0
    while choice != 'q':
        tags = ""
        menu = {"tags":""}
        choice, menu,mi = show_menu(menu, opts,
                shortkeys={"t":"tags"}, subwins = subwins)
        if choice == "tags":
            sel_tag = menu["tags"][:-5]
            sel_tag = sel_tag.strip()
            articles = art_list[sel_tag]
            if len(articles) > 0:
                ret = list_articles(articles, sel_tag, group = "tags")
            opts["tags"], art_list = refresh_tags()
        elif choice.startswith("del@tags"):
            save_obj(menu["tags"], "tags", "")

def website():
    menu = load_obj("website_menu", "")
    if menu is None:
        menu = {"address": "", "load": "button", "popular websites": "", "saved websites": ""}

    shortkeys = {"l": "load", "p": "popular websites", 's': "saved websites"}
    ws_dir = user_data_dir(appname, appauthor) + "/websites"
    saved_websites = [Path(f).stem for f in Path(ws_dir).glob('*') if f.is_file()]
    #    if saved_websites:
    #        menu["sep1"] = "saved websites"
    #    c = 1
    #    for ws in reversed(saved_websites):
    #        menu[ws] = "button"
    #        shortkeys[str(c)] = ws
    #        c += 1
    options = {"history": ["None"], "bookmarks": ["None"]}
    options["popular websites"] = newspaper.popular_urls()
    options["saved websites"] = saved_websites
    history = load_obj("history", "")
    if history is None:
        history = ["None"]
    elif "None" in history:
        history.remove("None")
    options["history"] = history
    clear_screen(std)
    ch = ''
    mi = 0
    subwins = {"saved websites": {"x": 16, "y": 7, "h": 10, "w": 48}}
    info = "h) help | q) quit"
    while ch != 'q':
        ch, menu, mi = show_menu(menu, options, shortkeys=shortkeys, mi=mi, subwins=subwins, info=info)
        if (ch == "load" or ch == "l" or ch == "popular websites"):
            site_addr = ""
            if ch == 'l' or ch == "load":
                site_addr = menu["address"]
            if ch == "popular websites":
                site_addr = menu["popular websites"]
            if not site_addr:
                info = "error: the site address can't be empty!"
            else:
                show_info("Gettign articles from " + site_addr + "... | Hit Ctrl+C to cancel")
                config = newspaper.Config()
                config.memoize_articles = False
                try:
                    site = newspaper.build(site_addr, memoize_articles=False)  # config)
                    # logger.info(site.article_urls())
                    # site.download()
                    # site.generate_articles()
                except Exception as e:
                    info = "error: " + str(e)
                    if ch == 'l' or ch == "load":
                        mi = 0
                    continue
                except KeyboardInterrupt:
                    show_info("loading canceled")
                    continue
                if not site_addr in history:
                    history.append(site_addr)
                    save_obj(history, "history", "")
                articles = []
                stored_exception = None
                for a in site.articles:
                    try:
                        a.download()
                        a.parse()
                        sleep(0.01)
                        show_info("loading " + a.title[:60] + "...")
                        if stored_exception:
                            break
                    except KeyboardInterrupt:
                        stored_exception = sys.exc_info()
                    except Exception as e:
                        show_info("Error:" + str(e))
                        continue

                    # a.nlp()
                    figures = []
                    count = 0
                    for img in list(a.imgs):
                        count += 1
                        figures.append({"id": img, "caption": "Figure " + str(count)})
                    art = {"id": a.title, "pdfUrl": a.url, "title": a.title, "figures": figures,
                           "sections": get_sects(a.text)}
                    articles.append(art)
                if articles != []:
                    uri = urlparse(site_addr)
                    save_obj(articles, uri.netloc, "websites")
                    ret = list_articles(articles, site_addr)
                else:
                    info = "error: No article was found or an error occured during getting articles..."

        if ch == "saved websites":
            selected = menu["saved websites"]
            if selected == "":
                show_err("Please select articles to load")
            else:
                articles = load_obj(selected, "websites")
                if articles != None:
                    ret = list_articles(articles, "sel articles")
                else:
                    show_err("Unable to load the file....")
    save_obj(menu, "website_menu", "")


def webpage():
    menu = None  # load_obj("webpage_menu", "")
    if menu is None:
        menu = {"address": "", "sep1": "", "load": "button", "recent pages": ""}

    shortkeys = {"l": "load", "r": "recent pages"}
    options = {}

    recent_pages = load_obj("recent_pages", "articles",[])
    arts = []
    for art in recent_pages:
        uri = urlparse(art["pdfUrl"])
        name = "(" + uri.netloc + ") " + art["title"]
        arts.append(name)
    options["recent pages"] = arts
    subwins = {"recent pages": {"x": 12, "y": 7, "h": 10, "w": 68}}

    menu["address"] = ""
    clear_screen(std)
    ch = ''
    mi = 0
    history = load_obj("history", "", [])
    info = ""
    while ch != 'q':
        ch, menu, mi = show_menu(menu, options, shortkeys=shortkeys, mi=mi, subwins=subwins, info=info)
        url = ""
        if ch == 'l' or ch == "load" or ch == "address":
            url = menu["address"]
        if url != "":
            show_info("Gettign article from " + url)
            config = newspaper.Config()
            config.memoize_articles = False
            config.fetch_images = False
            config.follow_meta_refresh = True
            try:
                a = newspaper.Article(url)
                a.download()
                a.parse()
                # site.generate_articles()
            except Exception as e:
                info = "error: " + str(e)
                if ch == 'l' or ch == "load":
                    mi = 0
                continue
            except KeyboardInterrupt:
                continue
            if not url in history:
                history.append(url)
                save_obj(history, "history", "")
            art = {"id": a.url, "pdfUrl": a.url, "title": a.title, "sections": get_sects(a.text)}
            insert_article_list(recent_pages, art)
            del recent_pages[100:]
            save_obj(recent_pages, "recent_pages", "articles")
            show_article(art)
        elif ch == "recent pages":
            si = options["recent pages"].index(menu["recent pages"])
            show_article(recent_pages[si])
    save_obj(menu, "webpage_menu", "")


def search():
    global query, filters
    filters = {}
    now = datetime.datetime.now()
    filter_items = ["year", "conference", "dataset", "task"]
    menu = None #load_obj("query_menu", "")
    if menu is None:
        menu = {}
        if is_obj("last_results", ""):
            menu["last results"] = "button"
        menu["task"] = ""
        menu["keywords"] = ""
        menu["year"] = ""
        menu["conference"] = ""
        menu["dataset"] = ""
        menu["sep1"] = ""
        menu["search"] = "button"
    options = {
        "year": ["All"] + [str(y) for y in range(now.year, 2010, -1)],
        "task": ["All", "Reading Comprehension", "Machine Reading Comprehension", "Sentiment Analysis",
                 "Question Answering", "Transfer Learning", "Natural Language Inference", "Computer Vision",
                 "Machine Translation", "Text Classification", "Decision Making"],
        "conference": ["All", "Arxiv", "ACL", "Workshops", "EMNLP", "IJCNLP", "NAACL", "LERC", "CL", "COLING", "BEA"],
        "dataset": ["All", "SQuAD", "RACE", "Social Media", "TriviaQA", "SNLI", "GLUE", "Image Net", "MS Marco", "TREC",
                    "News QA"],
    }

    task_file = Path('tasks.txt')
    if task_file.is_file():
        with open('tasks.txt', 'r') as f:
            options["task"] = ["All"] + [t.strip() for t in f.readlines()]
    clear_screen(std)
    ch = ''
    shortkeys = {"s": "search", "l": "last results"}
    mi = 0
    while ch != 'q':
        ch, menu, mi = show_menu(menu, options, shortkeys=shortkeys, mi=mi)
        if ch != 'q':
            for k, v in menu.items():
                if k in filter_items and v and v != "All":
                    filters[k] = str(v)
            try:
                ret = ""
                if ch == 's' or ch == 'search':
                    show_info("Getting articles...")
                    query = menu["keywords"]
                    fid = menu["keywords"] + '|' + menu["task"] + '|' + menu[
                        "conference"] + '|' + menu["dataset"]
                    fid = fid.replace('All', '')
                    while "||" in fid:
                        fid = fid.replace('||', '|')
                    articles, ret = request(0)
                    conf["keywords"] = menu["keywords"]
                    conf["fid"] = fid
                    conf["filters"] = filters
                    save_obj(conf, "conf", "", common = True)
                    if len(articles) > 0 and ret == "":
                        if isinstance(articles, tuple):
                            articles = articles[0]
                        save_obj(articles, "last_results", "")
                        ret = list_articles(articles, fid)
                    if ret:
                        show_err(ret[:200] + "...", bottom=False)
                    else:
                        show_msg(ret[:200] + "...")

                elif ch == 'l' or ch == "last results":
                    show_last_results()

            except KeyboardInterrupt:
                choice = ord('q')
                show_cursor()
    save_obj(menu, "query_menu", "")


def show_last_results():
    global query, filters
    last_results_file = user_data_dir(appname, appauthor)+ "/profiles/" + profile + "/last_results.pkl"
    obj_file = Path(last_results_file)
    if obj_file.is_file():
        conf = load_obj("conf", "", common = True)
        query = last_query = conf["keywords"]
        filters = conf["filters"]
        fid = conf["fid"]
        cr_time = time.ctime(os.path.getmtime(last_results_file))
        cr_date = str(cr_time)
        articles = load_obj("last_results", "", [])
        if articles:
            ret = list_articles(articles, "Results at " + str(cr_date) + " for " + fid)
    else:
        show_msg("Last results is missing....")


def main():
    global doc_path, conf, profile, show_instruct
    conf = load_obj("conf", "", common=True)
    if not conf is None and "profile" in conf:
        profile = conf["profile"]
    nc_settings = load_obj("settings", "", common=True)
    if nc_settings != None:
        doc_path = nc_settings["documents folder"]
        if "show instructions" in nc_settings:
            show_instruct = nc_settings["show instructions"] == "Enabled"
        Path(doc_path).mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        maximize_console(29)
        orig_size = resize_font_on_windows(20, True)
        orig_size = int(orig_size) if str(orig_size).isdigit() else 20
        if nc_settings != None:
            fsize = int(nc_settings["font size"]) if "font size" in nc_settings else 24
            if fsize > 24:
                fsize = 24
            ret = resize_font_on_windows(fsize)
            if ret != "":
                logging.info(ret)
    wrapper(start)
    if os.name == "nt":
        ret = resize_font_on_windows(orig_size)
        if ret != "":
            logging.info(ret)


if __name__ == "__main__":
    main()
