# Nodcast v 0.1.2 
import requests
import io
import platform
import webbrowser
import time
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

appname = "NodCast"
appauthor = "App"
user = 'na'

hotkey = ""

doc_path = os.path.expanduser('~/Documents/Nodcast')
app_path = user_data_dir(appname, appauthor)
logFilename = app_path + '/log_file.log'
Path(app_path).mkdir(parents=True, exist_ok=True)
logging.basicConfig(filename=logFilename, level=logging.DEBUG)

def handle_exception(exc_type, exc_value, exc_traceback):
    import sys
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    exc_info=(exc_type, exc_value, exc_traceback)
    logging.critical("\nDate:" + str(datetime.datetime.now()), exc_info=(exc_type, exc_value, exc_traceback))
    print("An error occured, check log file at ",app_path," to see the error details.")
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

TEXT_COLOR = 100
ITEM_COLOR = 101
CUR_ITEM_COLOR = 102
SEL_ITEM_COLOR = 103
TITLE_COLOR = 104
INFO_COLOR = 105
ERR_COLOR = 106
HL_COLOR = 107
DIM_COLOR = 108
MSG_COLOR = 109
TEMP_COLOR = 110
TEMP_COLOR2 = 111
COMMENT_COLOR = 39

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

color_map = {
        "text-color":TEXT_COLOR, 
        "back-color":TEXT_COLOR, 
        "item-color":ITEM_COLOR, 
        "cur-item-color":CUR_ITEM_COLOR,
        "sel-item-color":SEL_ITEM_COLOR,
        "title-color":TITLE_COLOR,
        "highlight-color":HL_COLOR,
        "hl-text-color":HL_COLOR,
        "dim-color":DIM_COLOR,
        }

nod_color_light = {
        "yes":77,
        "OK":36,
        "agree":22,
        "background":93,
        "archive":145,
        "okay":36,
        "okay, okay!":25,
        "okay?":180,
        "not reviewed":143,
        "goal":22,
        "skipped":245,
        "skip":245,
        "I see!":71,
        "interesting!":76,
        "favorite!":219,
        "interesting, so?":76,
        "proposed solution":32,
        "contribution":77,
        "feature":77,
        "constraint":97,
        "important!":141,
        "point!":142,
        "main idea!":142,
        "has an idea!":115,
        "didn't get!":161,
        "didn't get the article":161,
        "didn't get, needs review":161,
        "what?!":161,
        "what?! needs review":161,
        #"didn't get, but okay":199,
        "didn't get, but okay":179,
        "didn't get, so?":196,
        "so?":39,
        "okay, so?":39,
        "almost got the idea?":32,
        "explain more":178,
        "why?":59,
        "needs review": 177,
        "review later": 177,
        "to read later": 177,
        "needs research":186,
        "problem":179,
        "definition":250,
        "got it!":69,
        "got the idea!":69,
        }
cW = 7
cR = 1
cG = 29
cY = 5
cB = 27  
cPink = 15
cC = 9 
clC = 16
clY = 13
cGray = 10
clGray = 250
clG = 12
cllC = 83
cO =  209
back_color = None

def is_enter(ch):
    return ch == cur.KEY_ENTER or ch == 10 or ch == 13 

def reset_colors(theme, bg = None):
    global back_color
    if bg is None:
        bg = int(theme["back-color"])
    back_color = bg
    for each in range(1,min(256, cur.COLORS)):
        cur.init_pair(each, each, bg)
    cur.init_pair(TEXT_COLOR, int(theme["text-color"]) % cur.COLORS, bg)
    cur.init_pair(ITEM_COLOR, int(theme["item-color"]) % cur.COLORS, bg)
    cur.init_pair(CUR_ITEM_COLOR, bg, int(theme["cur-item-color"]) % cur.COLORS)
    cur.init_pair(SEL_ITEM_COLOR, int(theme["sel-item-color"]) % cur.COLORS, bg)
    cur.init_pair(TITLE_COLOR, int(theme["title-color"]) % cur.COLORS, bg)
    if theme["inverse-highlight"] == "True":
        cur.init_pair(HL_COLOR, int(theme["hl-text-color"]) % cur.COLORS,
                int(theme["highlight-color"]) % cur.COLORS)
    else:
        cur.init_pair(HL_COLOR, int(theme["highlight-color"]) % cur.COLORS,
                int(theme["hl-text-color"]) % cur.COLORS)
    cur.init_pair(DIM_COLOR, int(theme["dim-color"]) % cur.COLORS, bg)
    cur.init_pair(ERR_COLOR, cW, cR % cur.COLORS)
    cur.init_pair(MSG_COLOR, cW, cB % cur.COLORS)
    cur.init_pair(INFO_COLOR, cW, cG % cur.COLORS)
    # for key,val in nod_color.items():
       # cur.init_pair(val[0], bg, val[0])


def scale_color(value, factor = 1):
    value = float(value)
    if value == 0:
        return int(theme_menu["text-color"])
    elif value < 10:
        return int(theme_menu["didn't get!"])
    elif value < 20:
        return int(theme_menu["didn't get, but okay"])
    elif value < 30:
        return int(theme_menu["needs research"])
    elif value < 40:
        return int(theme_menu["needs review"])
    elif value < 50:
        return int(theme_menu["needs review"])
    elif value < 60:
        return int(theme_menu["okay"])
    elif value < 70:
        return int(theme_menu["okay"])
    elif value < 80:
        return int(theme_menu["interesting!"])
    else:
        return int(theme_menu["interesting!"])

    
def openFile(filepath):
    _file = Path(filepath)
    if _file.is_file(): 
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', filepath))
        elif platform.system() == 'Windows':    # Windows
            os.startfile(filepath)
        else:                                   # linux variants
            subprocess.call(('xdg-open', filepath))
        show_info("File was opened externally")
    else:
        show_err(str(filepath) + " doesn't exist, you can download it by hitting d key")

def delete_file(art):
    if "save_folder" in art:
        fname = art["save_folder"]
    else:
        title = art["title"]
        file_name = title.replace(' ','-')[:50] + ".pdf"#url.split('/')[-1]
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
    file_name = title.replace(' ','-')[:50] + ".pdf"#url.split('/')[-1]

    # Streaming, so we can iterate over the response.
    folder = doc_path + "/" + folder

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
                        Percent = int((Size / Length)*100)
                        show_info(f"download: {Percent}% {url}")

                _file.write_bytes(BufferAll.getvalue())
                show_info("File was written to " + str(_file))
                art["save_folder"] = str(_file)
                openFile(_file)

            except Exception as e:
                show_err("ERROR:"+ str(e))


def save_obj(obj, name, directory, data_dir=True):
    if obj is None or name.strip() == "":
        logging.info("Empty object to save")
        return
    if not data_dir or name.startswith("chk_def_"):
        folder = directory
    else:
        if directory != "":
            folder = user_data_dir(appname, appauthor) + "/" + directory
        else:
            folder = user_data_dir(appname, appauthor)
    Path(folder).mkdir(parents=True, exist_ok=True)
    with open(folder + '/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name, directory, default=None, data_dir=True):
    if not data_dir:
        folder = directory
    else:
        if directory != "":
            folder = user_data_dir(appname, appauthor) + "/" + directory
        else:
            folder = user_data_dir(appname, appauthor)
    fname = folder + '/' + name + '.pkl'
    obj_file = Path(fname) 
    if not obj_file.is_file():
        return default 
    with open(fname, 'rb') as f:
        return pickle.load(f)

def is_obj(name, directory):
    if directory != "":
        folder = user_data_dir(appname, appauthor) + "/" + directory
    else:
        folder = user_data_dir(appname, appauthor)
    if not name.endswith('.pkl'):
        name = name + '.pkl'
    fname = folder + '/' + name 
    obj_file = Path(fname) 
    if not obj_file.is_file():
        return False 
    else:
        return True

def del_obj(name, directory):
    if directory != "":
        folder = user_data_dir(appname, appauthor) + "/" + directory
    else:
        folder = user_data_dir(appname, appauthor)
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

def remove_article(articles, art):
    i = get_index(articles, art) 
    if i >= 0:
       articles.pop(i)

def insert_article(articles, art):
    i = get_index(articles, art) 
    if i < 0:
        articles.insert(0, art)
    else:
        articles.pop(i)
        articles.insert(0, art)

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

def get_frags(text):
    text = text.strip()
    parts = text.split("\n")
    parts = list(filter(None, parts)) 
    frags = []
    for t in parts:
        frag = {"text":t}
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

def request(p = 0):
     
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

    item  = 'https://dimsum.eu-gb.containers.appdomain.cloud/api/scholar/search'
    #item = ''
    #try:
    #    response = requests.post('http://checkideh.com/search.php', headers=headers, data=data)
    #    item = response.json()["a"]
    #    show_msg(str(item))
    #except:
    #    pass
    try:
        response = requests.post(item, headers=headers, data=data)
    except requests.exceptions.HTTPError as errh:
        return [],("Http Error:" + str(errh))
    except requests.exceptions.ConnectionError as errc:
        return [],("Error Connecting:" + str(errc))
    except requests.exceptions.Timeout as errt:
        return [],("Timeout Error:" + str(errt))
    except requests.exceptions.RequestException as err:
        return [],("OOps: Something Else" + str(err))

    try:
        rsp = response.json()['searchResults']['results'],""
    except:
        return [], "Corrupt or no response...."
    return rsp,""

def list_articles(in_articles, fid, show_note = False, group="", filter_nod ="", sel_art = None):
    global template_menu, theme_menu, hotkey

    if sel_art != None:
        show_article(sel_art)
    
    if len(in_articles) <= 0:
        return "There is no article to list!"

    articles = in_articles
    if filter_nod != "":
        articles = []
        for art in in_articles:
            if "nods" in art and art["nods"][0] == filter_nod:
                articles.append(art)
    rows, cols = std.getmaxyx()
    main_win = cur.newpad(rows*50, cols)
    width = cols - 10
    main_win.bkgd(' ', cur.color_pair(TEXT_COLOR)) # | cur.A_REVERSE)
    sel_arts = []
    saved_articles = load_obj("saved_articles", "articles", [])
    tags = load_obj("tags","")
    ch = 0
    start = 0
    k = 0
    ni = 0
    while ch != ord('q'):
        main_win.erase()
        mprint("", main_win)
        mprint((fid + " " + query).ljust(width-36) + "     progess  " + "status", main_win, int(theme_menu["text-color"]))
        #mprint("-"*width, main_win)
        N = len(articles)
        cc = start
        jj = start
        cur_title = ""
        while cc < start + 15 and jj < len(articles): 
            a = articles[jj]
            saved_index = get_index(saved_articles, a)
            if saved_index >= 0:
                a = articles[cc] = saved_articles[saved_index]
            h = a['year'] if "year" in a else cc
            prog = a['total_prog'] if "total_prog" in a else 0
            art_nod = " [" + "not viewed".ljust(12) + "]"
            art_nod_color = TEXT_COLOR
            if "nods" in a and a["nods"][0] != "":
                nod = a["nods"][0]
                art_nod_color = find_color(a["nods"], 0) 
                art_nod = " [" + nod.ljust(12) + "]"

            color = art_nod_color
            p = int(prog)
            prog_color = scale_color(p)
            if a in sel_arts:
                color = SEL_ITEM_COLOR
            if cc == k:
                color = CUR_ITEM_COLOR
                prog_color = color
                art_nod_color = color
                cur_title = a["title"]
                cur_prog = prog


            paper_title =  a['title']
            dots = ""
            if len(paper_title + art_nod) > width - 40:
               dots = "..." 
            h = "[{:04}]".format(h)
            prog_str = "{:02d}%".format(int(prog))
            prog_str = "[" + prog_str.rjust(4) + "]"
            art_title = (" " + paper_title[:width - 40] + dots).ljust(width - 36)               
            mprint(h, main_win, color, end = "")
            if theme_menu["bold-text"]== "True":
                att = cur.A_BOLD
            else:
                att = None
            mprint(art_title, main_win, color, end = "", attr=att)
            mprint(prog_str, main_win, prog_color, end = "", attr=att)
            mprint(art_nod, main_win, art_nod_color, end = "\n", attr=att)
            _list = "nods"
            if show_note and fid == "comments":
                _list = "comments"
            if show_note and _list in a and "sents" in a:
                for i,note in enumerate(a[_list]):
                    if (fid == "comments" and note != "") or note == fid:
                        sent = textwrap.indent(textwrap.fill(str(i) + ") " + a["sents"][i]),'  ')
                        mprint(sent, main_win, TEXT_COLOR)
                        if fid == "comments":
                            mprint(note, main_win, COMMENT_COLOR)
                        mprint("", main_win)

            cc += 1
            jj += 1
            # Endf while
        mprint("", main_win)
        left = ((cols - width)//2) 
        rows, cols = std.getmaxyx()
        if hotkey == "":
            #print_sect(cur_title, cur_prog, left)
            mprint(cur_title, main_win)
            main_win.refresh(0,0, 2, 5, rows - 2, cols - 6)
            _p = k // 15
            all_pages = (N // 15) + (1 if N % 15 > 0 else 0) 
            show_info("Enter) view article       PageDown) next page (load more...)     h) other commands ")
            print_there(0, cols - 15, "|" + str(N) + "|" + str(_p + 1) +  " of " + str(all_pages), win_info, INFO_COLOR)

        if hotkey == "":
            ch = get_key(std)
        else:
            ch, hotkey = ord(hotkey[0]), hotkey[1:]

        if ch == ord("r") or is_enter(ch):
            k = max(k, 0)
            k = min(k, N-1)
            main_win.erase()
            main_win.refresh(0,0, 2, 5, rows - 3, cols - 6)
            if show_note:
                show_article(articles[k], fid)
            else:
                show_article(articles[k])

        if ch == cur.KEY_UP or ch == ord('P'):
            if k > 0:
                k -= 1
            else:
                mbeep()
        if ch == cur.KEY_DOWN or ch == ord('N'):
            if k < N -1:
                k +=1
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
                show_info("Getting articles for "+ query)
                new_articles, ret = request(page + 1)
                if len(new_articles) > 0 and ret == "":
                    if isinstance(new_articles, tuple):
                        new_articles = new_articles[0]
                    articles = articles + new_articles
                    save_obj(articles, "last_results", "")
                    N = len(articles)
                else:
                    #ret = textwrap.fill(ret[:200], initial_indent='', subsequent_indent='    ')
                    show_err(ret[:200]+ "...", bottom = False)
            start = min(start, N - 15)
            k = start
        elif ch == cur.KEY_HOME:
            k = start
        elif ch == cur.KEY_END:
            k = N -1 #start + 14
            mod = 15 if N % 15 == 0 else N % 15
            start = N - mod 

        if ch == ord('h'):
            show_info(('\n'
                       ' s)          select/deselect an article\n'
                       ' a)          select all articles\n'
                       ' r/Enter)    open the selected article\n'
                       " f/Left)     filter the articles by the title's nod \n"
                       ' t)          tag the selected items\n'
                       ' d/DEL)      delete the selected items from list\n'
                       ' w)          write the selected items into files\n'
                       ' p)          select the output file format\n'
                       ' m)          change the color theme\n'
                       ' HOME)       go to the first item\n'
                       ' END)        go to the last item\n'
                       ' PageUp)     previous page\n'
                       ' Arrow keys) next, previous article\n'
                       ' q)          return back to the search menu\n'),
                       bottom=False)
        if  ch == ord('s'):
            if not articles[k] in sel_arts:
                sel_arts.append(articles[k])
            else:
                sel_arts.remove(articles[k])
        if ch == 127 or ch == cur.KEY_LEFT:
                ch = ord('q')
        if ch == ord('f') or ch == cur.KEY_IC:
                tmp,_ = sel_nod(art_nods, 5, 10,  ni, 0)
                _nod = tmp if tmp != "NULL" else ""
                if _nod != "":
                    list_articles(articles, fid, show_note, group, _nod)
        if ch == ord('m'):
            choice = '' 
            while choice != 'q':
                choice, theme_menu,_ = show_menu(theme_menu, theme_options, title="theme")
            save_obj(theme_menu, conf["theme"], "theme")
            main_win.erase()
            main_win.refresh(0,0, 0,0, rows -2, cols-1)
        if ch == ord('a'):
            for ss in range(start,min(N, start+15)):
                  art = articles[ss]
                  if not art in sel_arts:
                      sel_arts.append(art)
                  else:
                      sel_arts.remove(art)
        if (ch == ord('d') or ch == cur.KEY_DC) and group !="tags":
            art = articles[k]
            articles.remove(art)
            if group != "":
                _confirm = confirm(win_info, "remove the article " + art["title"][:20])
                if _confirm == "y":
                    if art in saved_articles:
                        saved_articles.remove(art)
                        save_obj(saved_articles, "saved_articles", "articles")
                    if group != "saved_articles":
                        group_articles = load_obj(group, "articles", [])
                        if art in group_articles:
                            group_articles.remove(art)
                            save_obj(group_articles, group, "articles")

        if (ch == ord('d') or ch == cur.KEY_DC) and group =="tags":
            if not sel_arts:
                art = articles[k]
                if len(art["tags"]) == 1:
                    _confirm = confirm_all(win_info, "remove the last tag of " + art["title"][:20])
                    if _confirm == "y" or _confirm == "a":
                        remove_tag(art, fid, saved_articles)
                        articles.remove(art)
                else:
                    remove_tag(art, fid, saved_articles)
                    articles.remove(art)
            else:
                _confirm = ""
                for art in sel_arts:
                    if len(art["tags"]) == 1:
                        if _confirm != "a":
                            _confirm = confirm_all(win_info, "remove the last tag of " + art["title"][:20])
                        if _confirm == "y" or _confirm == "a":
                            remove_tag(art, fid, saved_articles)
                            articles.remove(art)
                    else:
                        remove_tag(art, fid, saved_articles)
                        articles.remove(art)
                sel_arts = []
            N = len(articles)
            k = 0

        if ch == ord('p'):
            choice = ''
            mi = 0
            while choice != 'q':
                choice, template_menu, mi = show_menu(template_menu, template_options, title="template", mi = mi, shortkeys = {"s":"save as"})
            save_obj(template_menu, conf["template"], "tempate")

        if ch == ord('t'):
            if not sel_arts:
                show_err("No article was selected")
            else:
                tag,_ = minput(win_info, 0, 1, "Please enter a tag for selected articles:", default = query) 
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
                fid,_ = minput(win_info, 0, 1," Folder name (relative to documents root):", default = fid)
                if fid != "<ESC>":
                    for a in sel_arts:
                        write_article(a, fid)
                    show_msg(str(len(sel_arts))+ " articles were downloaded and saved into:" + fid)

def replace_template(template, old_val, new_val):
    ret = template.replace("{newline}","\n")
    ret = ret.replace(old_val,new_val)
    return ret

def write_article(article, folder=""):
    ext = '.' + template_menu["preset"]
    _folder = doc_path + "/" +  template_menu["preset"] + "/" + folder 
    if not os.path.exists(_folder):
        os.makedirs(_folder)
    top = replace_template(template_menu["top"],"{url}", article["pdfUrl"])
    bottom = replace_template(template_menu["bottom"],"{url}", article["pdfUrl"])
    paper_title = article['title']
    file_name = paper_title.replace(' ','_').lower()
    fpath = _folder + '/' + file_name + ext
    f = open(fpath, "w")
    print(top, file=f)
    title = replace_template(template_menu["title"],"{title}",paper_title)
    print(title, file=f)
    for b in article['sections']:
        sect_title =  b['title']
        sect_title = replace_template(template_menu["section-title"],"{section-title}",sect_title)
        print(sect_title, file=f)
        for c in b['fragments']:
            text = c['text']
            text = replace_template(template_menu["paragraph"],"{paragraph}", text)
            f.write(text)
    print(bottom, file=f)
    f.close()
    show_info("Artice was writen to " + fpath + '...')

right_nods = ["okay", "okay"]
left_nods = ["needs review"]
notes_list = ["interesting!","point!","definition", "background", "problem", "proposed solution", "needs research"]
nods_list = ["okay","didn't get, but okay", "didn't get!"]
sent_types = ["problem", "definition", "solution", "goal", "contribution", "feature", "constraint", "example"]
art_nods = ["interesting!", "favorite!", "important!", "needs review", "needs research", "got the idea!", "didn't get the article", "archive", "not reviewed", "to read later", "skipped"]
feedbacks = set(right_nods + left_nods + notes_list + nods_list + art_nods)
def sel_nod(opts, ypos, left, ni, si, no_win = False, in_row = False):
    if no_win:
       _nod = opts[ni]
       return _nod, 0

    w = 30 if not in_row else 70
    nod_win = cur.newwin(8, w, ypos + 2, left)
    nod_win.bkgd(' ', cur.color_pair(INFO_COLOR)) # | cur.A_REVERSE)
    stack = []
    ni, stack_index = select_box(nod_win, opts, ni, stack_index = 0, in_row = in_row, stack = stack)
    if ni >= 0:
        _nod = opts[ni]
        if _nod == "custom":
            custom_nod,_ = minput(win_info, 0, 1, "Enter a note or a nod (<Esc> to cancel):") 
            _nod = custom_nod if custom_nod != "<ESC>" else ""
            if _nod != "":
                opts.append(_nod)
                save_obj(opts, "nod_opts", "")
        nod_win.erase()
        return _nod, stack_index
    else:
        nod_win.erase()
        return 'NULL', -1

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
   for key,val in colors.items():
       if key == nod:
          ret = val
   return int(ret)

def print_notes(win, notes, ypos, xpos):
    for note in notes:
        if note != "":
            color = find_nod_color(note)
            print_there(ypos, xpos , ' ' + note, win, color)
            ypos += 1

top_win = None
def print_sect(title, prog, left):
    l_color = SEL_ITEM_COLOR
    top_win.clear()
    if title != "":
        prog = int(prog)
        print_there(0, left, title[:90], top_win, l_color, attr = cur.A_BOLD) 
        prog_color = TEXT_COLOR #scale_color(prog)
        add_info = " [" + str(prog) + "%] " # + f"({sect_fc+1}/{fnum})" 
        y,x = top_win.getyx()
        print_there(y, x+1, add_info, top_win, prog_color, attr = cur.A_BOLD)
    top_win.refresh()

def print_prog(text_win, prog, width):
   w = int(width*prog/100)   
   d_color = scale_color(prog) 
   cur.init_pair(TEMP_COLOR2, back_color, d_color % cur.COLORS)
   addinfo = (" Progress:" + str(prog) + "%")
   mprint(addinfo, text_win, d_color) 
# sss
def show_article(art, show_note=""):
    global theme_menu, theme_options, query, filters, hotkey

    sel_sects = {}
    k,sc  = 0,0
    fast_read = False
    start_row = 0
    rows, cols = std.getmaxyx()
    width = 2*cols // 3 
    text_win = cur.newpad(rows*50, cols -1)
    text_win.bkgd(' ', cur.color_pair(TEXT_COLOR)) # | cur.A_REVERSE)

    figures = []
    fig_file = ""
    if "figures" in art:
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
            frag = {"text":"[instruct] Press <Enter> on each figure to open it in a browser!", "nod":"okay?", "can_pass":"False"}
            frags.append(frag)
            for fig in figures:
                fig_num +=1
                caption = fig["caption"]
                url = "file://" + fig_file + "#fig" + str(fig_num - 1)
                if not caption.startswith("Figure") and not caption.startswith("Table"):
                   caption = "Figure " + str(fig_num) + ":" + caption
                frag = {"text":caption, "url":url}
                frags.append(frag)
            new_sect["fragments"] = frags 
            art["sections"].append(new_sect)

    # text_win = std
    bg = ""
    saved_articles = load_obj("saved_articles", "articles", [])
    frags_text = ""
    art_id = -1
    fc = 1
    cury = 0
    page_height = rows - 4
    scroll = 1
    show_reading_time = False
    start_reading = True
    cur_sent = "1"
    is_section = False
    art_id = art['id']
    
    if False:
        with open("art.txt", "w") as f:
            print(str(art), file = f)
    sc = 0
    fc = 1
    si = 0
    bmark = 0
    frags_sents = {}
    frags_sents[0] = (0, art["title"])
    fsn = 1
    ffn = 1
    nods = []
    has_nods = False
    if "nods" in art:
       nods = art["nods"]
       has_nods = True
    comments = []   
    if "comments" in art:
        comments = art["comments"]
    visible = {}
    art["sents"] = {}
    visible[0] = True
    art["sents"][0] = art["title"]
    last_sect = -1
    sn = 0
    total_pr = 0
    progs = [0]*len(art["sections"])

    for b in art["sections"]:
        frags_text = ""
        b['frags_offset'] = ffn
        b["sents_offset"] = fsn
        frags_sents[ffn] = (fsn, b["title"])
        art["sents"][fsn] = b["title"]
        last_sect = fsn
        visible[fsn] = True if show_note == '' else False
        ffn += 1
        fsn += 1
        pr = 0
        for c in b['fragments']:
            text = c['text']
            sents = split_into_sentences(text)
            frags_sents[ffn] = (fsn, sents)
            c['sents_offset'] = fsn 
            c['sents_num'] = len(sents)
            nexts = 0
            for sent in sents:
                art["sents"][fsn] = sent
                visible[fsn] = True
                if show_note == "comments" and comments:
                    if comments[fsn] != "":
                        visible[last_sect] = True
                    else:
                        visible[fsn] = False
                elif has_nods and fsn < len(nods):
                    if nods[fsn] in right_nods:
                        nexts += 1
                        pr += nexts 
                        nexts = 0
                    elif nods[fsn] == "next":
                        nexts += 1
                    else:
                        nexts = 0
                    if show_note == nods[fsn]:
                        visible[last_sect] = True
                    elif show_note != '':
                        visible[fsn] = False
                elif not has_nods or fsn >= len(nods):
                    if fsn % 3 == 0:
                        nods.append("")
                    else:
                        nods.append("")
                fsn += 1
            if not has_nods:
                nods.append("")
            ffn += 1
        if not has_nods:
            nods.append("")
        sents_num = fsn - b["sents_offset"]
        b["sents_num"] = sents_num 
        prog = int(round(pr/(sents_num - 1), 2)*100)
        total_pr += prog
        progs[sn] = pr
        b["prog"] = prog 
        sn += 1
        b['frags_num'] = len(b["fragments"])
    total_sents = fsn 
    total_frags = ffn
    total_sects = len(art["sections"])
    if total_sects > 1 and show_note == "": 
        expand = 0 
        sect_opened = [False]*total_sects
    else:
        expand = 1 
        sect_opened = [True]*total_sects
    si = 2
    fc = 2
    if si >= total_sents -1:
        si = 0

    if bmark < si:
        bmark = si

    ch = 0
    main_info = "r) resume reading      h) list commands "
    show_info(main_info)
    if len(nods) < total_sents:
        nods += [""]*(total_sents - len(nods))
    ni,fi = 0,0
    passable = [False]*total_sents
    if not "comments" in art:
       comments = [""]*total_sents
    if len(comments) < total_sents:
        comments += [""]*(total_sents - len(comments))

    notes = []
    if not "notes" in art:
       notes = [[""] for _ in range(total_sents)]
       notes[0] = ["not reviewed"]
    else:
       notes = art["notes"] 
    if len(notes) < total_sents:
        notes += [[""] for _ in (total_sents - len(notes))]
    if "times" in art:
       rtime = art["times"]
    else:
       rtime = {} 
    pos = [0]*total_sents
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

    logging.info("Article:" + art["title"]) 
    logging.info("Total Sents:" + str(total_sents)) 
    # bbb
    while ch != ord('q'):
        # clear_screen(text_win)
        if si != old_si:
            cur_nod = ""
            old_si = si
        text_win.erase()
        start_row = max(0, start_row)
        start_row = min(cury - 1, start_row)
        if bg != theme_menu["back-color"]:
            bg = theme_menu["back-color"]
            clear_screen(std)
            #text_win.refresh(start_row,0, 0,0, rows-1, cols-1)
            show_info(main_info)
            text_win.erase()
        start_time = time.time()
        sn = 0
        sc = max(sc, 0)
        sc = min(sc, total_sects)
        title = "\n".join(textwrap.wrap(art["title"], width)) # wrap at 60 characters
        pdfurl = art["pdfUrl"]
        if "save_folder" in art and Path(art["save_folder"]).is_file():
            top =  "[open file] "  
        else:
            if pdfurl.endswith("pdf"):
                top =  "[download] " + pdfurl 
            else:
                top =  "[open link] " + pdfurl 

        total_prog = int(round(total_pr/total_sects, 2))
        art["total_prog"] = str(total_prog)
        mprint("", text_win)
        if si == 0:
            mprint(top,  text_win, HL_COLOR, attr = cur.A_BOLD) 
            cur_sent = top
            if expand == 0:
                for ii in range(len(sect_opened)):
                    sect_opened[ii] = False
        else:
            mprint(top,  text_win, TITLE_COLOR, attr = cur.A_BOLD) 
        if nods[0] == "":
            nods[0] = "not reviewed"
        if nods[0] == "not reviewed":
            inst= "Select the title (press <Home>) and then press <Left> arrow key to check the idea!"
            mprint(inst, text_win, DIM_COLOR)
        d_color = find_color(nods, 0)
        mprint(nods[0], text_win, d_color, end = "")
        print_prog(text_win, total_prog, width)
        #mprint(pdfurl,  text_win, TITLE_COLOR, attr = cur.A_BOLD) 
        if comments[0] == "":
            comments[0] = "My review:"
        if  comments[0] == "My review:":
            inst= "Select the title and then press : to add your review"
            mprint(inst, text_win, DIM_COLOR)
        if comments[0] != "":
            com = textwrap.wrap(comments[0], width=width-5, replace_whitespace=False)
            com = "\n".join(com)
            mprint(com, text_win, COMMENT_COLOR)
        pos[0],_ = text_win.getyx()
        passable[0] = False
        mprint("", text_win)
        fsn = 1
        ffn = 1
        is_section = False
        pr = 0
        total_pr = 0
        #mark sections
        for b in art["sections"]:
            fragments = b["fragments"]
            fnum = len(fragments)
            title_color = ITEM_COLOR
            if fsn == si:
                cur_sent = b["title"]
                is_section = True
                title_color = HL_COLOR
                #si = si + 1
                #fc = art["sections"][sc]["frags_offset"] + 1
            if (sn == sc and si > 0 and 
                        (expand == 0 and sect_opened[sc])): # and si == b["sents_offset"]))):
                text_win.erase()
                #text_win.refresh(start_row,0, 0,0, rows-1, cols-1)
            sents_num = b["sents_num"] - 1
            prog = int(round(progs[sn]/sents_num, 2)*100)
            b["prog"] = prog
            prog_color = scale_color(prog)
            total_pr += prog
            prog = str(prog) + "%" #+ " (" + str(progs[sn]) +  "/" + str(sents_num) + ")"
            
            if sn == sc and si > 0:
                if b["title"] == "Figures":
                    add_info = " (" + str(len(figures)) + ") "
                else:
                    add_info = " [" + str(prog) + "] " # + f"({sect_fc+1}/{fnum})" 
                if True: #fsn != si:
                    #if art_id in sel_sects and b["title"].lower() in sel_sects[art_id]:
                    if sect_opened[sc]:
                        title_color = SEL_ITEM_COLOR #HL_COLOR
                    else:
                        title_color = CUR_ITEM_COLOR
                        prog_color = title_color
                        
            else:
                if b["title"] == "Figures":
                    add_info = " (" + str(len(figures)) + ") "
                else:
                    add_info = " [" + str(prog) + "] "
 
            if b["title"] != "all" or expand == 0:
                mprint(b["title"], text_win, title_color, end = "", attr = cur.A_BOLD)
                mprint(add_info, text_win, prog_color, attr = cur.A_BOLD)

            pos[fsn],_ = text_win.getyx()
            passable[fsn] = True
            ffn += 1
            fsn += 1
            if (expand == 0 and sn != sc):
                fsn += b["sents_num"] - 1 
                ffn += len(b["fragments"])
            elif (expand == 0 and not sect_opened[sc]):
                fsn += b["sents_num"] - 1 
                ffn += len(b["fragments"])
            else:
                # mprint("", text_win)
                for frag in fragments:
                    if ffn != fc and expand == 3:
                        fsn += frag['sents_num']
                        ffn += 1
                    else:
                       new_frag = True
                       if not ffn in frags_sents:
                           frag_sents = split_into_sentences(frag['text'])
                           frags_sents[ffn] = (fsn, frag_sents)
                       else:
                           frag_sents = frags_sents[ffn][1]
 
                       # if "level" in frag:
                          # color = frag["level"] % 250
                       hlcolor = HL_COLOR
                       color = DIM_COLOR
                       if True:
                           nexts = 0
                           for sent in frag_sents:
                               feedback = nods[fsn] + " " + comments[fsn]
                               if sn == sc: 
                                   if nods[fsn] in right_nods:
                                       nexts += 1
                                       pr += nexts
                                       progs[sc] = pr
                                       nexts = 0
                                   elif nods[fsn] == "next":
                                       nexts += 1
                                   else:
                                        nexts = 0
                               if show_note == "comments":
                                   if comments[fsn] != "":
                                       visible[fsn] = True
                                       tfsn = fsn - 1
                                       while tfsn > 0 and nods[tfsn] == "next":
                                           visible[tfsn] = True
                                           tfsn -= 1
                                   else:
                                       visible[fsn] = False
                               elif (show_note != "" and not show_note in notes[fsn]) or "remove" in notes[fsn]:
                                   visible[fsn] = False
                               elif show_note != "" and not "remove" in notes[fsn]:
                                   visible[fsn] = True
                                   tfsn = fsn - 1
                                   while tfsn > 0 and nods[tfsn] == "next":
                                       visible[tfsn] = True
                                       tfsn -= 1

                               if not visible[fsn]: 
                                   pos[fsn],_ = text_win.getyx()
                                   fsn +=1 
                                   continue

                               #cur.init_pair(NOD_COLOR,back_color,cG)
                               reading_time = rtime[fsn][1] if fsn in rtime else 0 
                               f_color = HL_COLOR
                               hline = "-"*(width)
                               if show_reading_time:
                                   f_color = scale_color((100 - reading_time*4), 0.1)
                                   mprint(str(reading_time), text_win, f_color)
                               lines = textwrap.wrap(sent, width-4) 
                               lines = filter(None, lines)
                               end = ""
                               sent = ""
                               # sent += " "*(width -2) + "\n"
                               for line in lines:
                                   sent += "  " + line.ljust(width-4)+"\n" 
                               #sent += " "*(width - 2) + "\n"
                               if nods[fsn] == "" or nods[fsn] == "next":
                                   pass
                               #if nods[fsn] == "interesting!":
                               #    interestings += 1
                               #if interestings > 5 and (nods[0] == "" or nods[0] == "not reviewed"):
                               #    nods[0] = "interesting!"
                                   #sent += " "*(width -2) + "\n"

                               # fff
                               if fsn >= bmark and fsn <= si and not passable[fsn]:
                                   hl_pos = text_win.getyx() 
                                   cur_sent = sent
                                   hlcolor = HL_COLOR
                                   l_color = find_color(nods, fsn)
                                   if True: #nods[fsn] == "":
                                       b_color = int(theme_menu["highlight-color"]) % cur.COLORS
                                   else:
                                       b_color = 238
                                   cur.init_pair(TEMP_COLOR, l_color % cur.COLORS, b_color) 
                                   _color = HL_COLOR
                                   if theme_menu["bold-highlight"]== "True":
                                       mprint(sent, text_win, _color, attr=cur.A_BOLD, end=end)
                                   else:
                                       mprint(sent, text_win, _color, end=end)
                               else:
                                   _color = DIM_COLOR
                                   if nods[fsn] != "":
                                       _color = find_color(nods, fsn)
                                   if theme_menu["bold-text"]== "True":
                                       mprint(sent, text_win, _color, attr=cur.A_BOLD, end=end)
                                   else:
                                       mprint(sent, text_win, _color, end=end)
                               mark = ""
                               if "url" in frag and new_frag:
                                   mark = "f"
                               left = (cols - width)//2
                               ypos = pos[fsn-1]
                               _y,_x = text_win.getyx()
                               nn = [mark]
                               if notes[fsn] != [""]:
                                   nn += notes[fsn]
                               if nods[fsn] in notes_list:
                                   nn.append(nods[fsn])
                               print_notes(text_win,  nn, ypos, width + 1)
                               text_win.move(_y,_x)

                               if feedback != '' and passable[fsn] == False:
                                   if comments[fsn] != "":
                                       if False: #fsn >= bmark and fsn <= si:
                                           tmp = comments[fsn].ljust(width-2) 
                                           cur.init_pair(TEMP_COLOR2, back_color, COMMENT_COLOR % cur.COLORS)
                                           mprint(tmp, text_win, TEMP_COLOR2, end = "\n")
                                       else:
                                           com = textwrap.wrap(comments[fsn], 
                                                   width=width-5, replace_whitespace=False)
                                           com = "\n".join(com)
                                           mprint(com, text_win, SEL_ITEM_COLOR, end = "\n")
                                       #mprint(" "*(width-3), text_win, HL_COLOR)
                               else:
                                   pass # mprint("", text_win, f_color)
                               pos[fsn],_ = text_win.getyx()
                               fsn += 1
                               new_frag = False
                       if False: #fsn >= bmark and fsn <= si:
                           w = 4 # width - 5
                           mprint(" "*(w), text_win, TEMP_COLOR)
                       else:
                           w1 = 4 # width - 5
                           w2 = 6
                           mprint("-"*w1 + ' '*(width - w1 - w2 + 3) + "-"*w2, text_win, DIM_COLOR)
                       ffn += 1
                     # end for fragments
            sn += 1
         # end for sections
 
        #print(":", end="", flush=True)
        cury, curx = text_win.getyx()
        sc = min(sc, total_sects)
        f_offset = art['sections'][sc]['frags_offset'] 
        offset = art["sections"][sc]["sents_offset"] 
        #show_info("frags:"+ str(total_frags) + " start row:" + str(start_row) + " frag offset:"+ str(f_offset)  + " fc:" + str(fc) + " si:" + str(si) + " bmark:" + str(bmark))
        # mark get_key
        if not (ch == ord('.') or ch == ord(',')): 
            top_margin = 10 #rows // 4
            if pos[bmark] > top_margin:    
                start_row = pos[bmark] - top_margin
            else:
                start_row = 0

        #if ch != cur.KEY_LEFT:
        rows, cols = std.getmaxyx()
        #width = 2*cols // 3 
        left = ((cols - width)//2) 
        ypos = pos[bmark]-start_row
        if hotkey == "":
            text_win.refresh(start_row,0, 2,left, rows -2, cols - 1)
            show_info(main_info)
        if sc > 0 and expand != 0:
            if pos[offset] <= start_row:
                print_sect(art["sections"][sc]["title"], art["sections"][sc]["prog"], left)
            else:
                print_sect("", "", left)
        else:
            print_sect(art["title"], art["total_prog"], left)

        # jjj
        if jump_key == 0:
            if reading_mode:
                if si + 1 < total_sents:
                    sent_len = len(art["sents"][si])
                    std.timeout(sent_len*100)
                    show_info("remaining time:" + str(sent_len*100))
                    tmp_ch = get_key(std)
                    if tmp_ch == -1:
                        ch = cur.KEY_DOWN 
                    else:
                        reading_mode = False
                        std.timeout(-1)
                else:
                    reading_mode = False
                    std.timeout(-1)
            else:
                if hotkey == "":
                    ch = get_key(std)
                else:
                    ch, hotkey = ord(hotkey[0]), hotkey[1:]
        else:
            ch = jump_key
            jump_key = 0
        if ch == ord('>'):
            if width < 2*cols // 3: 
                text_win.erase()
                text_win.refresh(0,0, 2,0, rows -2, cols-1)
                width +=2
            else:
                mbeep()
        if ch == ord('<'):
            if width > cols // 3:
                text_win.erase()
                text_win.refresh(0,0, 2,0, rows -2, cols-1)
                width -= 2
            else:
               mbeep()
        if ch == ord("N"):
            hotkey = "qNr" if expand == 0 else "qqNr"
        if ch == ord('n'):
            if show_note != '':
                show_note = ''
                visible = [True]*total_sents
            else:
                ypos = pos[bmark]-start_row
                tmp, _ = sel_nod(notes_list, ypos, left, ni, 0, in_row = True)
                show_note = tmp if tmp != "NULL" else ""
        if ch == ord('d'):
            _confirm = confirm(win_info, "delete the pdf file from your computer")
            if _confirm == "y" or _confirm == "a":
                delete_file(art)
                art["save_folder"] = ""
        if ch == cur.KEY_DC:
            if len(notes[si]) > 1:
                notes[si].pop()
            #std.timeout(500)
            #tmp_ch = get_key(std)
            #remove_nod = False
            #if tmp_ch == cur.KEY_DC:
            #    remove_nod = True
            #std.timeout(-1)
        if ch == cur.KEY_SDC:
            notes[si] = [""]
            if nods[si] != "":
                nods[si] = ""
                if si > 0: 
                    si -= 1
                    while si > 0 and (not visible[si] or passable[si]):
                        si -= 1
                    if bmark >= si:
                        bmark = si
                        while bmark >=0 and nods[bmark - 1] == "next":
                            bmark -= 1
                else:
                    mbeep()
                    si = 0
        if ch == ord('y'):
            with open(art["title"]  + ".txt","w") as f:
                print(art, file = f)
        if ch == ord('r'):
           si = total_sents - 1 
           text_win.erase()
           text_win.refresh(0,0, 0,0, rows -2, cols-1)
           while (nods[si] == "" or nods[si] == "skipped" or nods[si] == "next" or not visible[si]) and si > 2:
               si -= 1
           si = max(si, 1)
           bmark = si 
           expand = 1
           for ii in range(len(sect_opened)):
               sect_opened[ii] = True
           update_si = True

        if ch == ord('v'):
            _confirm = confirm(win_info, "restore the removed parts")
            if _confirm == "y" or _confirm == "a":
                visible = [True]*total_sents
            for i,nod in enumerate(nods):
                if nod == "remove":
                    nods[i] = ""
            art_changed = True
        if ch == ord('z'):
            #show_reading_time = not show_reading_time
            reading_mode = True #not reading_mode 

        if ch == ord('h'): # article help
            show_info(('\n'
                       '  Down)          expand the selection to next sentence\n'
                       '  Right)         expaned a collapsed section\n'
                       '  Right)         nod the selected sentences with positive feedback\n'
                       '  Left)          nod the selected sentences with negative feedback\n'
                       '  Enter)         nod the selected sentences with okay and move to the next sentence\n'
                       '  +/-)           show the list of positive and negative nods\n'
                       '  o)             download/open the pdf file externally\n'
                       '  f)             list figures\n'
                       '  t)             tag the article\n'
                       '  d)             delete the external pdf file \n'
                       '  w)             write the article into a file\n'
                       '  p)             select the output file format\n'
                       '  m)             change the color theme\n'
                       '  u)             reset comments and nods\n'
                       '  n)             filter sentences by a nod\n'
                       '  DEL)           remove current nod and expand to the next sentence\n'
                       '  TAB)           skip current fragment\n'
                       '  e)             expand/collapse sections\n'
                       '  BackSpace)     collapse the current section\n'
                       '  >/<)           increase/decrease the width of text\n'
                       '  :)             add a comment \n'
                       '  k/j)           previous/next section\n'
                       '  l/;)           previous/next fragment\n'
                       '  PgUp/PgDown)   previous/next page\n'
                       '  h)             show this list\n'
                       '  q)             close \n'
                       ''),
                       bottom=False)
            text_win.erase()
            text_win.refresh(0,0, 0,0, rows-1, cols-1)
        if ch == ord('x'):
            fast_read = not fast_read
        if ch == ord('w'):
            fid,_ = minput(win_info, 0, 1," Folder name (relative to documents root, you can leave it blank):", default = "") 
            if fid != "<ESC>":
                write_article(art, fid)
                show_msg("The article was written in " + fid)
        if ch == ord('u'):
            _confirm = confirm(win_info, "reset the article")
            if _confirm == "y" or _confirm == "a":
                nods = [""]*total_sents
                comments = [""]*total_sents
                rtime = {} 
                visible = [True]*total_sents
                passable = [False]*total_sents
                si = 2
                art_changed = True
                update_si = True

        if ch == ord('s'):
            cur_sect = art["sections"][sc]["title"].lower()
            if art_id in sel_sects:
                if cur_sect in sel_sects[art_id]:
                    sel_sects[art_id].remove(cur_sect)
                else:
                    sel_sects[art_id].append(cur_sect)
            else:
                sel_sects[art_id] = [cur_sect]
        if ch == cur.KEY_SLEFT:
            ch = cur.KEY_IC
        if ch == cur.KEY_NPAGE:
            std.timeout(100)
            tmp_ch = get_key(std)
            if tmp_ch == cur.KEY_NPAGE:
                ch = cur.KEY_END
            std.timeout(-1)
        if ch == ord('i') or ch == cur.KEY_IC or ch == ord(' ') or ch == ord('\t'):
            ypos = pos[bmark]-start_row
            cur_note = notes[si][-1]
            index = 0
            if cur_note != "":
                index = notes_list.index(cur_note) if cur_note in notes_list else 0 
            tmp_note, note_index = sel_nod(notes_list, ypos, left, index, si, in_row = True)
            if tmp_note != 'NULL' and not tmp_note in notes[si]:
                cur_note = tmp_note
                notes[si].append(cur_note)
                art_changed = True
                
        elif chr(ch).isdigit():
            try:
                index = int(chr(ch))
            except:
                index = 0
            if index < len(notes_list):
                cur_note = notes_list[index]
                if not cur_note in notes[si]:
                    notes[si].append(cur_note)

        if is_enter(ch) and expand != 0:
            sect_fc = fc - art["sections"][sc]["frags_offset"] - 1
            if si > 0:
                if "url" in art["sections"][sc]["fragments"][sect_fc]:
                    _url = art["sections"][sc]["fragments"][sect_fc]["url"]
                    webbrowser.open(_url)
            else:
                ch = ord('o')

        ## kkk (bookmark)
        if ((si == 0 and not ch == cur.KEY_DOWN) or sect_opened[sc]) and (
                ch == cur.KEY_LEFT or 
                ch == cur.KEY_RIGHT or 
                ch == cur.KEY_DOWN or 
                ch == ord(']') or 
                ch == ord('+') or 
                ch == ord('-') or 
                ch == ord('?')): 
            #if cur_nod == "":
            #    cur_nod = "okay" #nods[si] 
            if ch == ord(']') or is_enter(ch) or (ch == cur.KEY_DOWN and needs_nod and not nod_set):
               for ii in range(bmark, si + 1):
                   if ii < si:
                       nods[ii] = "next"
               if is_enter(ch):
                   cur_nod = "okay"
                   nods[si] = "okay"
                   ch = cur.KEY_DOWN
                   nod_set = True
               else:
                   cur_nod = "skipped"
                   nods[si] = "skipped"
                   ch = cur.KEY_DOWN
                   nod_set = True
            else:
                nod_set = False

            if ch == cur.KEY_RIGHT or ch == cur.KEY_LEFT:
                if si == 0:
                    ypos = pos[bmark] - start_row
                    ni = art_nods.index(cur_nod) if cur_nod in art_nods else 0 
                    tmp_nod, nod_index = sel_nod(art_nods, ypos, left, abs(ni), si)
                    if tmp_nod != "NULL" and tmp_nod != "":
                        cur_nod = tmp_nod
                    ch = cur.KEY_RIGHT
                else:
                    if (cur_nod == "" or cur_nod == "skipped") and ch == cur.KEY_LEFT:
                        ni = 1 
                    elif cur_nod == "" and ch == cur.KEY_RIGHT:
                        ni = 0
                    elif cur_nod in right_nods:
                        ni = right_nods.index(cur_nod) 
                    elif cur_nod in left_nods:
                        ni = -1*left_nods.index(cur_nod)  
                    ni = ni + 1 if ch == cur.KEY_RIGHT else ni - 1
                    if ni > 0:
                        #ni = nod_opts[0].index(cur_nod) if cur_nod in nod_opts[0] else 0
                        ni = min(ni, len(right_nods) - 1)
                        cur_nod = right_nods[ni]
                    elif ni <= 0:
                        #ni = nod_opts[1].index(cur_nod) if cur_nod in nod_opts[1] else 0 
                        ni = max(ni,-1*(len(left_nods) - 1))
                        cur_nod = left_nods[abs(ni)]
                nod_set = True
                #if cur_nod == "" or cur_nod == "next":
                #elif not "so?" in cur_nod:
                #    cur_nod = cur_nod + ", so?"
                #    nod_set = True
                #    ch = cur.KEY_DOWN
                #else:
                #    ch = cur.KEY_DOWN
            elif ch == ord('+') or ch == ord('-'):
                ypos = pos[bmark]-start_row
                if ch == ord('+'):
                    ni = right_nods.index(cur_nod) if cur_nod in right_nods else 0 
                    tmp_nod, nod_index = sel_nod(right_nods, ypos, left, ni, si)
                else:
                    ni = left_nods.index(cur_nod) if cur_nod in left_nods else 0 
                    tmp_nod, nod_index = sel_nod(left_nods, ypos, left, abs(ni), si)
                if tmp_nod == "skip":
                    cur_nod = "skipped"
                    ch = cur.KEY_RIGHT
                    nod_set = True
                elif tmp_nod != 'NULL':
                    cur_nod = tmp_nod
                    ch = cur.KEY_RIGHT
                    nod_set = True
            elif chr(ch).isdigit():
                try:
                    ni = int(chr(ch))
                except:
                    ni = 0
                if ni < len(right_nods):
                    cur_nod = right_nods[ni]
                nod_set = True
                ch = cur.KEY_LEFT
                if cur_nod == "skip":
                    cur_nod = "skipped"
                    ch = cur.KEY_RIGHT
            elif ch == ord(']'):
                cur_nod = "skipped"
                nod_set = True
                ch = cur.KEY_RIGHT
            elif ch == ord('?'):
                if not "so?" in cur_nod:
                    cur_nod = cur_nod +  ", so?" if cur_nod != "" else "so?"
                nod_set = True
                ch = cur.KEY_RIGHT

            if ch == cur.KEY_LEFT or ch == cur.KEY_RIGHT or ch == cur.KEY_DOWN:  

                cur_sent_length = len(cur_sent.split()) 
                if cur_sent_length == 0:
                    cur_sent_length = 0.01
                end_time = time.time()
                elapsed_time = end_time - start_time
                reading_time = round(elapsed_time/cur_sent_length,2)
                if elapsed_time < 0.3: # prevent fast stroke by mouse
                    ch = 1
                elif reading_mode or elapsed_time < 1 and cur_nod == "" and nods[si] in ["", "okay?"]:
                    cur_nod = "skipped"
                    #mbeep()
                    nod_set = True
                    pass
                tries = 0
                if si in rtime:
                    avg = rtime[si][1]
                    tries = rtime[si][0] + 1
                    reading_time = avg + 1/tries*(reading_time - avg)

                rtime[si] = (tries, reading_time)
                if nod_set:
                    for ii in range(bmark, si + 1):
                        if ii < si:
                            nods[ii] = "next"
                        if cur_nod == "remove":
                            visible[ii] = False
               #nnn
                    if visible[si]: # and (nods[si] == "" or nod_set):
                        nods[si] = cur_nod 
                        if ch == cur.KEY_RIGHT or ch == cur.KEY_LEFT:
                            ch = cur.KEY_DOWN
                        if cur_nod in notes_list and not cur_nod in notes[si]:
                            notes[si].append(cur_nod)
            can_inc = True
            next_frag_start = frags_sents[fc + 1][0] if fc+1 < total_frags else total_sents 
            if ch == cur.KEY_DOWN and not nod_set and ((si - bmark) >= 2 or si + 1 >= next_frag_start):
                can_inc = False
            if si < total_sents:
                if si <= 1 or (not nods[si] in ["", "okay?", "skipped", "next"]):
                    can_inc = True
                    nod_set = True
            if (si  < total_sents and can_inc) or ch == cur.KEY_RIGHT:
                if ch == cur.KEY_DOWN: # or ch == cur.KEY_RIGHT: # or nod_set:
                    tmp_si = si
                    si += 1
                    ni = 0
                    while si < total_sents and (not visible[si] or passable[si] or nods[si]=="next"):
                        si += 1
                    if si == total_sents:
                        si = tmp_si
                        mbeep()
                    
                if (ch == cur.KEY_DOWN or ch == cur.KEY_RIGHT) and nod_set:
                    bmark = si
                    while bmark >=0 and nods[bmark - 1] == "next":
                        bmark -= 1
                needs_nod = False
            else:
                needs_nod = True 
                nod_set = False
                jump_key = cur.KEY_DOWN
                mbeep()
                show_info("Please use the <Left> or <Right> arrow keys to nod the sentence, or press <Down> twice to skip.")
                if si > total_sents - 1:
                    si = total_sents - 1

        art_changed  = art_changed or nod_set
        if ch == cur.KEY_UP:
            end_time = time.time()
            elapsed_time = end_time - start_time
            if elapsed_time > 0.3: # prevent fast stroke by mouse
                if si > 0: 
                    si -= 1
                    while si > 0 and (not visible[si] or passable[si] or nods[si]=="next"):
                        si -= 1
                    if bmark >= si:
                        bmark = si
                        while bmark >=0 and nods[bmark - 1] == "next":
                            bmark -= 1
                else:
                    mbeep()
                    si = 0

        update_si = False
        if si > 0 and (expand == 0 and ch == cur.KEY_UP and not sect_opened[sc]) or ch == ord('j'):
            if sc > 0:
                sc -= 1
                fc = art["sections"][sc]["frags_offset"] + 1 
                update_si = True
            else:
                sc = 0
        if  (expand == 0 and ch == cur.KEY_DOWN and not sect_opened[sc]) or ch == ord('k'):
            if sc < total_sects - 1:
                if si > 0:
                    sc += 1
                fc = art["sections"][sc]["frags_offset"] + 1
                update_si = True
            else:
                mbeep()
                sc = total_sects -1
                fc = art["sections"][sc]["frags_offset"] + 1
                update_si = True
        if ch == ord(';'):
            if fc < total_frags - 1:
                fc += 1
                _tmp = frags_sents[fc][0]
                if passable[_tmp]:
                    fc += 1
                update_si = True
            else:
                mbeep()
                fc = total_frags -1
        if ch == ord('l'):
            if fc > 0 :
                fc -= 1
                _tmp = frags_sents[fc][0]
                if passable[_tmp]:
                    fc -= 1
                update_si = True
            else:
                mbeep()
                fc = 0
        if  ((expand == 0 and is_enter(ch))
            or si > 0 and (expand == 0 and ch == cur.KEY_RIGHT and not sect_opened[sc])):
            if si > 0:
                expand = 1
                for ii in range(len(sect_opened)):
                    sect_opened[ii] = True
            else:
                ch = ord('o')


        if ch == ord('e'):
            if expand == 1:
                expand = 0
                pos = [0]*total_sents
                for ii in range(len(sect_opened)):
                    sect_opened[ii] = False
                #sect_opened[sc] = True
            else:
                expand = 1
                for ii in range(len(sect_opened)):
                    sect_opened[ii] = True

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

        if ch == cur.KEY_PPAGE:
            si = max(si - 10, 0)
            bmark = si
        elif ch == cur.KEY_NPAGE:
            si = min(si + 10, total_sents -1)
            bmark = si
        elif ch == cur.KEY_HOME:
            si = 0
            bmark = si
        elif ch == cur.KEY_END:
            si = total_sents -1 
            bmark = si

        if si < bmark:
            bmark = si

        if update_si:
            fc = max(fc, 0)
            fc = min(fc, total_frags-1)
            bmark = frags_sents[fc][0]
            #si = frags_sents[fc+1][0]-1 if fc+1 < total_frags else total_sents - 1
            si = frags_sents[fc][0]
        c = 0 
        while c < total_sects  and si >= art["sections"][c]["sents_offset"]:
            c += 1
        _sc = max(c - 1,0)
        if _sc != sc:
            sc = _sc
            if expand == 0:
                for ii in range(len(sect_opened)):
                    sect_opened[ii] = False
        f = 0
        while f < total_frags and si >= frags_sents[f][0]:
            f += 1
        fc = max(f - 1,0)

        art['sections'][sc]['fc'] = fc 
        if ch == 127:
            ch = ord('q')
            
        if ch == ord('q') and sect_opened[sc]:
            ch = 0
            expand = 0
            pos = [0]*total_sents
            for ii in range(len(sect_opened)):
                sect_opened[ii] = False

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
                fid,_ = minput(win_info, 0, 1," Folder name (relative to documents root, you can leave it blank):", default = "") 
                if fid != "<ESC>":
                    download(art["pdfUrl"], art, fid)
                    art_changed = True
                else:
                    show_info(main_info)
        if ch == ord('c'):
            win = cur.newwin(5, width, 6, left)
            win.bkgd(' ', cur.color_pair(INFO_COLOR)) # | cur.A_REVERSE)
            win.refresh()
            _comment,_ = minput(win, 1, 1, "My review of article:", default = comments[si], multi_line = True) 
        if ch == ord(':'):
            win = cur.newwin(5, width, 6, left)
            win.bkgd(' ', cur.color_pair(INFO_COLOR)) # | cur.A_REVERSE)
            win.refresh()
            _comment,_ = minput(win, 0, 1, "", default = comments[si], multi_line = True) 
            show_info(main_info)
            _comment = _comment if _comment != "<ESC>" and _comment != "q" else comments[si]
            art_changed = True
            if nods[si] == "" or nods[si] == "next":
                nods[si] = "okay"
                bmark = si
            comments[si] = _comment

        if ch == ord('t'):
            subwins = {
                    "select tag":{"x":7,"y":5,"h":15,"w":68}
                    }
            choice = ''
            mi = 0
            tags_menu = {"tags (comma separated)":"", "select tag":""} 
            tags_options = {}
            cur_tags = load_obj("tags","", [""])
            tags_options["select tag"] = cur_tags
            while choice != 'q':
                tags = ""
                if "tags" in art:
                    for tag in art["tags"]:
                        tags += tag + ", "
                tags_menu["tags (comma separated)"] = tags
                choice, tags_menu,mi = show_menu(tags_menu, tags_options,
                        shortkeys={"s":"select tag"},
                        subwins=subwins, mi=mi, title="tags")
                if choice == "select tag":
                    new_tag = tags_menu["select tag"].strip()
                    if not "tags" in art:
                        art["tags"] = [new_tag]
                    elif not new_tag in art["tags"]:
                        art["tags"].append(new_tag)
                else:
                    new_tags = tags_menu["tags (comma separated)"].split(",")
                    art["tags"]=[]
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
            text_win.refresh(0,0, 2,0, rows -2, cols -1)
        if ch == ord('f'): # show figures
            ypos = 5
            fig_win = cur.newwin(8, width, ypos + 2, left)
            fig_win.bkgd(' ', cur.color_pair(TEXT_COLOR)) # | cur.A_REVERSE)
            fig_win.border()
            opts = []
            fig_num =1
            if not figures:
                show_msg("No figure to show")
            else:
                for fig in figures:
                    fig_num +=1
                    caption = fig["caption"]
                    if not caption.startswith("Figure"):
                       caption = "Figure " + str(fig_num) + ":" + caption
                    opts.append(caption)

                fi,_ = select_box(fig_win, opts, fi, in_row = False)
                if fi >= 0:
                    fname = app_path + "/nodcast_temp.html" 
                    if not figures_created:
                        create_figures_file(figures, fname)
                        figures_created = True
                    webbrowser.open("file://" + fname + "#fig" + str(fi))
        if ch == ord('m'):
            choice = '' 
            while choice != 'q':
                choice, theme_menu,_ = show_menu(theme_menu, theme_options, title="theme")
            save_obj(theme_menu, conf["theme"], "theme")
            text_win.erase()
            text_win.refresh(0,0, 0,0, rows -2, cols-1)
        if ch == ord('q'): # before exiting artilce
            art["nods"] = nods
            art["notes"] = notes 
            art["times"] = rtime
            art["passable"] = passable
            art["comments"] = comments
            if show_note == "":
                art["visible"] = visible
            if art_changed:
                insert_article(saved_articles, art)
                save_obj(saved_articles, "saved_articles", "articles")
            last_visited = load_obj("last_visited", "articles", [])
            insert_article(last_visited, art)
            save_obj(last_visited, "last_visited", "articles")
    return "" 

def create_figures_file(figures, fname):
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
            <div class="imgbox" id='fig""" + str(fnum) +  """'>
                <img class="center-fit" src='""" + url + """'>
            </div>
            <div class="caption">""" + caption + """</div>
       """
    html += "</body></html>"    
    with open(fname, "w", encoding="utf-8") as f:
         f.write(html)


def refresh_menu(menu, menu_win, sel, options, shortkeys, subwins, horiz= False, start_row = 0):
    global clG
    menu_win.erase()
    mprint("", menu_win)
    mprint(" "*5 + "Checkideh v 1.0", menu_win)
    row = 3 
    col = 5
    rows, cols = menu_win.getmaxyx() 
    _m = max([len(x) for x in menu.keys()]) + 5  
    gap = col + _m
    prev_length = 0
    for k, v in menu.items():
       colon = ":" # if not k in options else ">"
       key = k
       if k in shortkeys.values():
           sk = list(shortkeys.keys())[list(shortkeys.values()).index(k)]
           key = sk + ") " + k
       if k == sel and not sel in subwins:
           color = CUR_ITEM_COLOR
       else:
           color = ITEM_COLOR
       fw = cur.A_BOLD
       if str(v) == "button_light":
           fw = None

       if k.startswith("sep"):
           col = 5
           if horiz:
               row += 1
           if v:
             print_there(row, col,  str(v) + colon, menu_win, TEXT_COLOR)
       else:
           if str(v).startswith("button") and horiz:
               col += prev_length + 2
               prev_length = len(key)
           print_there(row, col, "{:<{}}".format(key, _m), menu_win, color, attr = fw)
           if not str(v).startswith("button") and not k in subwins:
             print_there(row, gap, colon, menu_win, color, attr = cur.A_BOLD)

       if not str(v).startswith("button") and not k in subwins:
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
    start_row = min(start_row, 2*rows)
    if hotkey == "":
        menu_win.refresh(start_row,0, 0,0, rows-2, cols-1)
        for k, item in subwins.items():
           sub_menu_win = cur.newwin(item["h"],
                    item["w"],
                    item["y"],
                    item["x"])
           sub_menu_win.bkgd(' ', cur.color_pair(TEXT_COLOR)) # | cur.A_REVERSE)
           show_submenu(sub_menu_win, options[k],-1, "color" in k or (k in options and options[k] == colors))

def get_sel(menu, mi):
    mi = max(mi, 0)
    mi = min(mi, len(menu)-1)
    return list(menu)[mi], mi

win_info = None
def confirm_all(win, msg):
    return confirm(win, msg, acc = ['y','n','a']) 

def confirm(win, msg, acc= ['y','n'], color = MSG_COLOR):
    win.bkgd(' ', cur.color_pair(color)) # | cur.A_REVERSE)
    mbeep()
    msg = "Are you sure you want to " + msg + "? (" + "/".join(acc)  + ")"  
    return get_confirm(win, msg)

def show_info(msg, color=INFO_COLOR, bottom = True):
    global win_info
    rows, cols = std.getmaxyx()
    if bottom:
        win_info = cur.newwin(1, cols, rows-1,0) 
    else:
        win_info = cur.newpad(rows*2, 2*cols // 3)
    win_info.bkgd(' ', cur.color_pair(color)) # | cur.A_REVERSE)
    win_info.erase()
    if bottom:
        if len(msg) > cols - 15:
            msg = msg[:(cols - 16)] + "..."
        print_there(0,1," {} ".format(msg), win_info, color)
        win_info.clrtoeol()
        win_info.refresh()
    else:
        left = cols//6
        start_row = 0
        ch = 0
        guide = "\n  Press q to return"
        nlines = msg.count('\n')
        if nlines > rows - 5:
            guide += "; Press down and up keys to see the complete message"
        msg = guide + "\n" + msg
        while ch != ord('q'):
            win_info.erase()
            # msg = textwrap.indent(textwrap.fill(msg),'  ')
            mprint(msg, win_info, color)
            start_row = max(start_row, 0)
            start_row = min(start_row, 2*rows)
            win_info.refresh(start_row,0, 2,left, rows -3, cols-1)
            ch = get_key(std)
            if ch == cur.KEY_UP:
                if start_row > 0:
                    start_row -= 10
                else:
                    mbeep()
            elif ch == cur.KEY_DOWN:
                if start_row < nlines - rows + 5:
                    start_row += 10
                else:
                    mbeep()
            elif ch != ord('q'):
                mbeep()

def show_msg(msg, color=MSG_COLOR):
   mbeep()
   show_info(msg + " press any key", color)
   std.getch()

def show_err(msg, color=ERR_COLOR, bottom = True):
    if bottom:
        msg += " press any key..."
    show_info(msg, color, bottom)
    if bottom:
        std.getch()

def load_preset(new_preset, options, folder=""):
    menu = load_obj(new_preset, folder)
    if menu == None and folder == "theme":
        dark = load_obj("chk_def_dark", folder, data_dir = False)
        light = load_obj("chk_def_light", folder, data_dir = False)
        neon = load_obj("chk_def_neon", folder, data_dir = False)
        dark = save_obj(dark, "dark", folder, data_dir = True)
        light = save_obj(light, "light", folder, data_dir = True)
        neon = save_obj(neon, "neon", folder, data_dir = True)
        if dark is None:
            dark ={'preset': 'dark',"sep1":"colors", 'text-color': '247', 'back-color': '233', 'item-color': '71', 'cur-item-color': '236', 'sel-item-color': '33', 'title-color': '28', "sep2":"reading mode","dim-color":'241' ,"highlight-color":'238', "hl-text-color":"244", "inverse-highlight":"True", "bold-highlight":"True","bold-text":"False", "sep5":"Feedback Colors"}
        for k,v in nod_color_light.items():
            dark[k] = v

        dark["save as"] = "button"
        dark["reset"] = "button"
        dark["delete"] = "button"
        dark["save and quit"] = "button"
        save_obj(dark, "dark", "theme")
        new_preset = "dark"

    if menu == None and folder == "template":
       text  = {"preset":"txt", "top":"", "title":"# {title}", "section-title":"## {section-title}","paragraph": "{paragraph}{newline}{newline}", "bottom":"{url}"}
       html  = {"preset":"html", "top":"<!DOCTYPE html>{newline}<html>{newline}<body>","title":"<h1>{title}</h1>", "section-title":"<h2>{section-title}</h2>","paragraph": "<p>{paragraph}</p>", "bottom":"<p>source:{url}</p></body>{newline}</html>"}
       for mm in [text, html]:
           mm["save as"] = "button"
           mm["reset"] = "button"
           mm["delete"] = "button"
           mm["save and quit"] = "button"
       save_obj(text, "txt", folder)
       save_obj(html, "html", folder)
       new_preset = "txt"

    menu = load_obj(new_preset, folder)
    menu["preset"] = new_preset
    menu_dir = user_data_dir(appname, appauthor) + "/"+ folder
    saved_presets =  [Path(f).stem for f in Path(menu_dir).glob('*') if f.is_file()]
    options["preset"] = saved_presets

    if folder == "theme":
        reset_colors(menu)
    conf[folder] = new_preset
    save_obj(conf, "conf", "")
    return menu, options

def select_box(win, in_opts, ni, in_row = False, stack_index = 0, stack = []):
    ch = 0
    win.border()
    if not in_opts:
        show_err("No item to list")
        return ni, stack_index
    while ch != 27 and ch != ord('q'):
        opts = []
        for i,k in enumerate(in_opts):
            opts.append(str(i) + ") " + k)
        row_cap = 3 if in_row else 1
        _size = max([len(s) for s in opts]) + 2
        ni = max(ni, 0)
        ni = min(ni, len(opts)-1)
        win.erase()
        cc = 1
        for i, st in enumerate(stack):
            st = st.ljust(5)
            if i == stack_index:
                print_there(0, cc, st, win, MSG_COLOR)
            else:
                print_there(0, cc, st, win, INFO_COLOR)
            cc = len(st) + 7
        if not in_row:
            show_submenu(win, opts, ni, color = INFO_COLOR)
        else:
            for i,k in enumerate(opts):
                row = (i // row_cap) + 2
                col = (i % row_cap)*_size + 1
                if i == ni:
                    print_there(row, col, k, win, CUR_ITEM_COLOR)
                else:
                   print_there(row, col, k, win, INFO_COLOR)
            mprint("\n\n", win)
            win.refresh()
        ch = get_key(std)
        if is_enter(ch) or (not in_row and ch == cur.KEY_RIGHT):
           return ni, stack_index
        if chr(ch).isdigit():
            ni = int(chr(ch))
            return ni, stack_index
        elif ch == ord('d'):
            opts.pop(ni)
        elif ch == cur.KEY_DOWN:
            ni += row_cap
        elif ch == cur.KEY_UP:
            if ni < row_cap:
                return -1, stack_index
            ni -= row_cap
        elif ch == cur.KEY_RIGHT:
            ni += 1
        elif ch == ord('\t'):
           if stack_index < len(in_opts) - 1:
               stack_index +=1
           else:
               stack_index = 0
        elif ch == cur.KEY_LEFT:
            if not in_row:
               return -1, stack_index
            if ni > 0:
               ni -= 1
            else:
               if not stack:
                   return -1, stack_index
               if stack_index < len(in_opts) - 1:
                   stack_index +=1
               else:
                   stack_index = 0
        elif ch != 27 and ch != ord('q'):
            mbeep()
            show_info("Use left arrow key to select the item, the right key or q to cancel!")

    return -1, stack_index
    

def show_submenu(sub_menu_win, opts, si, is_color = False, color = ITEM_COLOR):
   win_rows, win_cols = sub_menu_win.getmaxyx()
   win_rows = min(win_rows-3, 10)
   start = si - win_rows // 2
   start = max(start, 0)
   if len(opts) > win_rows:
 	  start = min(start, len(opts)-win_rows)
   if start > 0:
 	  mprint("...", sub_menu_win, color)
   footer = ""
   for vi, v in enumerate(opts[start:start + win_rows]):
     if start + vi == si:
        sel_v = v
        if len(v) > win_cols:
           footer = v
           v = v[:win_cols - 5] + "..."
        if is_color:
           mprint(" {:^8}".format(">" + str(v)), sub_menu_win, int(v), attr = cur.A_REVERSE) 
        else:
           mprint(" {:<8}".format(str(v)),sub_menu_win, CUR_ITEM_COLOR)
     else:
        if len(v) > win_cols:
           v = v[:win_cols - 5] + "..."
        if is_color:
           mprint(" {:^8}".format(v), sub_menu_win, int(v), attr = cur.A_REVERSE) 
        else:
           mprint(" {:<8}".format(str(v)), sub_menu_win, color)
   if start + win_rows < len(opts):
 	  mprint("...", sub_menu_win, color)
   # if footer != "":
   #   mprint(footer, sub_menu_win, cW)
   sub_menu_win.refresh()

menu_win = None
common_subwin = None
def show_menu(menu, options, shortkeys={}, hotkeys={}, title = "", mi = 0, subwins={}, info = "h) help | q) quit"):
    global menu_win, common_subwin, hotkey, hotkey

    si = 0 #submenu index
    ch = 0 #user choice
    mode = 'm' # 'm' means we are in menu, 's' means we are in submenu

    rows, cols = std.getmaxyx()
    height = rows - 1  
    width = cols  

    menu_win = cur.newpad(rows*2, cols)
    common_subwin = cur.newwin(rows - 6, width//2 + 5, 5, width//2 - 5)

    menu_win.bkgd(' ', cur.color_pair(TEXT_COLOR)) # | cur.A_REVERSE)
    common_subwin.bkgd(' ', cur.color_pair(TEXT_COLOR)) # | cur.A_REVERSE)

    if info.startswith("error"):
        show_err(info)
    else:
        for k,v in hotkeys.items():
            info += " | " + k + ") " + v
        show_info(info)

    mprint(title.center(rows), menu_win)
    hide_cursor()
    last_preset = ""
    if "preset" in menu:
        last_preset = menu["preset"]
        shortkeys["r"] = "reset"
        shortkeys["s"] = "save as"
        shortkeys["d"] = "delete"
        shortkeys["q"] = "save and quit"

    row = 3 
    col = 5
    mt, st = "", ""
    old_val = ""
    prev_ch = 0
    start_row = 0
    while ch != ord('q'):
        sel,mi = get_sel(menu, mi)
        sub_menu_win = common_subwin
        key_set = False
        cmd = ""
        if row + start_row + mi > 2*rows:
            start_row += 10 
        elif row + start_row + mi > rows:
            start_row += 10 
        if not sel.startswith("sep"):
            sub_menu_win.erase()
            if mode == 'm':
                refresh_menu(menu, menu_win, sel, options, shortkeys, subwins, start_row)
        if sel not in options and not str(menu[sel]).startswith("button") and not sel.startswith("sep"): 
             # menu[sel]=""
            cur_val = menu[sel]
            #refresh_menu(menu, menu_win, sel, options, shortkeys, subwins)
            _m = max([len(x) for x in menu.keys()]) + 5  
            win_input = cur.newwin(1, cols-10, row + mi, col)
            win_input.bkgd(' ', cur.color_pair(CUR_ITEM_COLOR)) # | cur.A_REVERSE)
            val, ch = minput(win_input,0, 0, "{:<{}}".format(sel,_m) + ": ", default=menu[sel]) 
            if val != "<ESC>":
                 val = textwrap.fill(val, width = cols - 12 - _m)
                 menu[sel] = val
                 if "tags" in sel and val.strip() != "":
                     new_tags = val.split(",")
                     new_tags = filter(None, new_tags)
                     for tag in new_tags:
                         tag = tag.strip()
                         if tag != '' and not tag in options["select tag"]:
                             options["select tag"].append(tag)
                     save_obj(options["select tag"],"tags","")
            else:
                 menu[sel] = cur_val
                 ch = ord('q')


            key_set = True
            if ch != cur.KEY_UP and ch != 27:
                 ch = cur.KEY_DOWN
            
            mode = 'm'
            mt = ""
        if sel in subwins:
            if mode == 'm' and menu[sel] in options[sel]:
               si = options[sel].index(menu[sel])
            mode = 's'
            rows, cols = std.getmaxyx() 
            sub_menu_win = cur.newwin(subwins[sel]["h"],
                subwins[sel]["w"],
                subwins[sel]["y"],
                subwins[sel]["x"])
            sub_menu_win.bkgd(' ', cur.color_pair(TEXT_COLOR)) # | cur.A_REVERSE)
        if mode == 's' and not str(menu[sel]).startswith("button"):
            if sel in options:
              si = min(si, len(options[sel]) - 1)
              si = max(si, 0)
              show_submenu(sub_menu_win, options[sel], si, "color" in sel)

        if not sel.startswith('sep') and not key_set:
            prev_ch = ch
            if hotkey == "":
                ch = get_key(std)
            else:
                ch, hotkey = ord(hotkey[0]), hotkey[1:]
        elif sel.startswith('sep') and mi == 0:
            ch = cur.KEY_DOWN
        elif sel.startswith('sep') and mi == len(menu) -1:
            ch = cur.KEY_UP
            
        if ch == cur.KEY_RESIZE:
            mbeep()
            refresh_menu(menu, menu_win, sel, options, shortkeys, subwins, start_row)

        if ch == cur.KEY_DOWN:
            if mode == "m":
                mi += 1
            elif sel in options:
                si += 1
        elif ch == cur.KEY_UP:
            if sel in subwins and si == 0:
                mode = "m"
            if mode == "m":
                mi -= 1
            elif sel in options:
                si -= 1
        elif ch == cur.KEY_NPAGE:
            if mode == "m":
                mi += 10
            elif sel in options:
                si += 10
        elif ch == cur.KEY_PPAGE:
            if mode == "m":
                mi -= 10
            elif sel in options:
                si -= 10
        elif is_enter(ch) or (chr(ch) in shortkeys and ch == prev_ch):
            is_button = str(menu[sel]).startswith("button")
            if is_button: 
              if sel == "save as" or sel == "reset" or sel == "delete" or sel == "save and quit":
                  cmd = sel
              else:
                  return sel, menu, mi 
            elif sel in options:
                si = min(si, len(options[sel]) - 1)
                si = max(si, 0)
            elif sel.startswith("sep"):
                mi += 1
            if mode == 'm' and not is_button:
                old_val = menu[sel]
                mode = 's'
                st = ""
                if sel in options and menu[sel] in options[sel]:
                    si = options[sel].index(menu[sel])
            elif mode == 's' and not is_button:
                if last_preset.strip() != "":
                    save_obj(menu, last_preset, title)
                menu[sel] = options[sel][si]
                #if "preset" in menu and title == "theme":
                #    reset_colors(menu)
                if sel == "preset":
                    new_preset = menu[sel]
                    menu,options = load_preset(new_preset, options, title)
                    last_preset = new_preset
                    refresh_menu(menu, menu_win, sel, options, shortkeys, subwins, start_row)
                    show_info(new_preset +  " was loaded")
                if sel in shortkeys.values():
                    return sel, menu, mi
                mode = 'm'    
                mt = ""
                si = 0
                old_val = ""
        elif ch == cur.KEY_RIGHT:
            if not str(menu[sel]).startswith("button"):
                old_val = menu[sel]
                if sel in options and menu[sel] in options[sel]:
                    si = options[sel].index(menu[sel]) 
                mode = 's'
                st = ""
        elif ch == cur.KEY_LEFT or ch == 27:
            if old_val != "":
                menu[sel] = old_val
                #refresh_menu(menu, menu_win, sel, options, shortkeys, subwins)
                #if "color" in sel:
                #    reset_colors(menu)
            old_val = ""
            mode = 'm'
            mt = ""
        if cmd == "save and quit":
            ch = ord('q')
        elif ch == ord('d') or cmd == "delete":
            if mode == 'm':
                item = menu[sel]
            else:
                item = options[sel][si]
            if not is_obj(item, title) and not sel == "preset":
                return "del@" + sel+"@" + str(si), menu, mi

            _confirm = confirm(win_info,  
                    "delete '" + item)

            if _confirm == "y" or _confirm == "a":
                show_info("Deleting '"+ item + "'")
                del_obj(item, title)
                if item in options[sel]:
                    options[sel].remove(item)
                if len(options[sel]) > 0:
                    new_item = options[sel][si] if si < len(options[sel]) else options[sel][0] 
                else:
                    new_item = "None"
                if sel == "preset":
                    menu,options = load_preset(new_item, options, title)
                    last_preset = menu["preset"]
                    si = options["preset"].index(menu["preset"]) 
                    refresh_menu(menu, menu_win, sel, options, shortkeys, subwins, horiz, start_row)
                    show_info(new_item +  " was loaded")
                else:
                    menu[sel] = new_item
                    show_info(item +  " was deleted")
                    return "del@" + sel+"@" + str(si), menu, mi

        elif (ch == ord('r') or cmd == "reset") and "preset" in menu:
            menu, options = load_preset("resett", options, title)
            last_preset = menu["preset"]
            #refresh_menu(menu, menu_win, sel, options, shortkeys, subwins, horiz, start_row)
            show_info("Values were reset to defaults")
        elif (ch == ord('s') or ch == ord('z') or cmd == "save as") and "preset" in menu:
            if ch == ord('z'):
                fname = "chk_def_" + menu["preset"]
            else:
                fname,_ = minput(win_info, 0, 1, "Save as:") 
            if fname == "<ESC>":
                show_info("")
            else:
                if fname.startswith("chk_def_"):
                    save_obj(menu, fname, title, data_dir=False)
                    fname = menu["preset"]

                menu["preset"] = fname

                if title == "theme":
                    reset_colors(menu)
                show_info(menu["preset"] +  " was saved as " + fname)
                if not fname in options["preset"]:
                    options["preset"].append(fname)
                last_preset = fname
                refresh_menu(menu, menu_win, sel, options, shortkeys, subwins, horiz, start_row)
                mode = 'm'
        elif ch == ord('h'):
            return "h",menu, mi
        elif chr(ch) in hotkeys:
            return chr(ch), menu, mi
        elif ch != ord('q') and chr(ch) in shortkeys:
            if not shortkeys[chr(ch)] in menu: # then it's a hotkey
                return chr(ch), menu, mi
            else:
                mi = list(menu.keys()).index(shortkeys[chr(ch)])
                sel,mi = get_sel(menu, mi)
                #refresh_menu(menu, menu_win, sel, options, shortkeys, subwins, horiz, start_row)
                if str(menu[sel]).startswith("button"):
                    return sel, menu, mi
                old_val = menu[sel]
                mode = 's'
                st = ""
        elif ch == ord('q') and title == "main":
            pass
            #mbeep()
            #_confirm = confirm(win_info, "you want to exit the program")
            #if _confirm != "y":
            #    ch = 0
        else:
            if mode == 's' and chr(ch).isdigit() and sel in options:
                si,st = find(options[sel], st, chr(ch), si)
    return chr(ch), menu, mi

def find(list, st, ch, default):
    str = st + ch
    for i, item in enumerate(list):
        if item.startswith(str):
            return i,str
    for i, item in enumerate(list):
        if item.startswith(ch):
            return i,ch
    return default,""



colors = []
def start(stdscr):
    global colors, template_menu, template_options, theme_options, theme_menu, std, conf, query, filters, top_win, hotkey

    std = stdscr
    logging.info(f"curses colors: {cur.COLORS}")

    rows, cols = std.getmaxyx()
    # mouse = cur.mousemask(cur.ALL_MOUSE_EVENTS)
    cur.start_color()
    cur.curs_set(0) 
    # std.keypad(1)
    cur.use_default_colors()
    # sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=24, cols=112))
    rows, cols = std.getmaxyx()
    filters = {}
    now = datetime.datetime.now()
    filter_items = ["year", "conference", "dataset", "task"]
    last_visited = load_obj("last_visited", "articles", [])
    menu =  None #load_obj("main_menu", "")
    isFirst = False
    if menu is None or (newspaper_imported and not "webpage" in menu):
        isFirst = True
        menu = {}
        if last_visited:
            menu["recent articles"] = "button"
        menu["reviewed articles"]="button"
        menu["sepb1"] =""
        menu["sep1"] ="Search AI-related papers"
        if is_obj("last_results", ""):
            menu["last results"]="button"
        menu["keywords"]=""
        menu["Go!"]="button"
        menu["advanced search"]="button"
        menu["sepb2"] =""
        if newspaper_imported:
            menu["sep2"] = "Load website articles"
            menu["website articles"]="button"
            menu["webpage"]="button"
        menu["saved items"]= "button"
        menu["options"]="button"
        menu["text files"]="button"

    options = {
            "saved articles":["None"],
            #"recent articles":["None"],
            }

    recent_arts = []
    width = 2*cols//3
    y_start = len(menu) + 5
    hh = rows - y_start - 1
    for art in last_visited[:10]:
        recent_arts.append(art["title"][:60]+ "...")
    subwins = {}
        #options["recent articles"] =recent_arts 
        #subwins = {"recent articles":{"x":7,"y":y_start,"h":hh,"w":width}}

    if isFirst:
        for opt in menu:
           if opt in options:
               menu[opt] = options[opt][0] if options[opt] else ""

    conf = load_obj("conf", "")
    if conf is None:
        conf = {"theme":"default", "template":"txt"}

    colors = [str(y) for y in range(-1, cur.COLORS)]
    if cur.COLORS > 100:
        colors = [str(y) for y in range(-1, 100)] + [str(y) for y in range(112, cur.COLORS)]

    theme_options = {
            "preset":[],
            "text-color":colors,
            "back-color":colors,
            "item-color":colors,
            "cur-item-color":colors,
            "sel-item-color":colors,
            "title-color":colors,
            "highlight-color":colors,
            "hl-text-color":colors,
            "dim-color":colors,
            "inverse-highlight":["True", "False"],
            "bold-highlight":["True", "False"],
            "bold-text":["True", "False"],
            }

    for k in feedbacks:
        theme_options[k] = colors
    theme_menu, theme_options = load_preset(conf["theme"], theme_options, "theme") 
    template_menu, template_options = load_preset(conf["template"], template_options, "template") 

    reset_colors(theme_menu)
    #os.environ.setdefault('ESCDELAY', '25')
    #ESCDELAY = 25
    std.bkgd(' ', cur.color_pair(TEXT_COLOR)) # | cur.A_REVERSE)
    clear_screen(std)
    top_win = cur.newwin(2, cols, 1, 0) 
    top_win.bkgd(' ', cur.color_pair(TEXT_COLOR)) # | cur.A_REVERSE)
    ch = ''
    shortkeys = {"v":"reviewed articles", "l":"last results", "k":"keywords", "n":"nods", "r":"recent articles","t":"tagged articles","o":"options", "p":"webpage", "a":"advanced search","s":"saved items", "w":"website articles",'t':"text files"} 
    mi = 0
    while ch != 'q':
        info = "h) help         q) quit"
        show_info(info)
        ch, menu, mi = show_menu(menu, options, shortkeys = shortkeys, mi = mi, subwins = subwins, title = "main", hotkeys = {"R":"resume last article"})
        save_obj(menu, "main_menu", "")
        if ch == "R":
            hotkey = "rrr"
        if ch == "advanced search":
            search()
        elif ch == "last results":
            show_last_results()
        elif ch == 'v' or ch == "reviewed articles":
            rev_articles()
        elif ch == 's' or ch == "saved items":
            saved_items()
        elif ch == "Go!":
            query = menu["keywords"]
            fid = menu["keywords"]
            articles,ret = request(0)
            if len(articles) > 0 and ret == "":
                if isinstance(articles, tuple):
                    articles = articles[0]
                save_obj(articles, "last_results", "")
                ret = list_articles(articles, fid)
            if ret:
                show_err(ret[:200]+ "...", bottom = False)
        elif ch == "webpage":
            webpage()
        elif ch == 'o' or ch == "options":
            settings()
        if ch == 'h' or ch == "help":
            #webbrowser.open("https://github.com/puraminy/nodcast")
            show_info(('\n'
                       '        _   __          ________           __ \n'
                       '       / | / /___  ____/ / ____/___ ______/ /_\n'
                       '      /  |/ / __ \/ __  / /   / __ `/ ___/ __/\n'
                       '     / /|  / /_/ / /_/ / /___/ /_/ (__  ) /_  \n'
                       '    /_/ |_/\____/\__,_/\____/\__,_/____/\__/  \n'
                       '  Please visit the following link to get an overview of Nodcast:\n'
                       '\thttps://github.com/puraminy/nodcast\n\n'
                       '\tArrow keys)   Next, previous item\n'
                       '\tEnter)        Open/Run the selected item\n'
                       '\tPageUp/Down)  First/Last item\n'
                       '\trrr           Resume reading from last article\n'
                       '\n  Further help was provided in each section.\n'),
                       bottom=False)
            #name = '../README.md'
            #with open(name, "r") as f:
            #    data = f.read()
            #title, i = get_title(data, name)
            #if i > 0:
            #    data = data[i:]
            #art = {"id":"help", "pdfUrl":name, "title":title, "sections":get_sects(data)}
            #show_article(art)
        elif ch == 'w' or ch == "website articles":
             website()
        elif ch == "r" or ch == "recent articles":
            list_articles(last_visited, "Recent Articles", group = "last_visited")
        elif ch == 'text files':
            save_folder = doc_path + '/txt'
            Path(save_folder).mkdir(parents=True, exist_ok=True)
            show_texts(save_folder)
        elif ch.startswith("del@recent articles"):
            parts = ch.split("@")
            last_visited.pop(int(parts[2]))
            save_obj(last_visited, "last_visited", "articles") 
        elif ch == 'o' or ch == "saved articles":
             selected = menu["saved articles"]
             if selected == None:
                 show_err("Please select articles to load")
             else:
                 articles = load_obj(selected, "articles")
                 if articles != None:
                     ret = list_articles(articles, "sel articles")
                 else:
                     show_err("Unable to load the file....")

def rev_articles(sel_art = None):
    saved_articles = load_obj("saved_articles","articles", [])
    rev_articles = []
    for art in saved_articles:
        if "nods" in art and art["nods"][0] != "" and art["nods"][0] != "not reviewed":
            rev_articles.append(art)
    if len(rev_articles) == 0:
        show_msg("There is no article reviewed yet, to review an article enter a nod for its title.")
    else:
        list_articles(rev_articles, "Reviewed Articles", group = "saved_articles", sel_art = sel_art)

def show_texts(save_folder):
    subfolders = [ f.name for f in os.scandir(save_folder) if f.is_dir() ]
    menu = {}
    for sf in subfolders:
        menu["[>] "+sf]="button"
    text_files =  [str(Path(f)) for f in Path(save_folder).glob('*.txt') if f.is_file()]
    if not text_files and not subfolders:
        menu[".."] = "button"
    count = 1
    for text in text_files:
        name = Path(text).name
        if len(name) > 60:
            name = name[:60] + "..."
        name = "[" + str(count) + "] " + name
        menu[name] = "button_light"
        count += 1
    options = {}
    mi = 0
    ch = ''
    while ch != 'q':
        ch, menu, mi = show_menu(menu, options, mi = mi)
        if ch.startswith("[>"):
            sfolder = save_folder + "/" + ch[4:]
            show_texts(sfolder)
        elif ch == "..":
            ch = 'q'
        elif ch != "q":
            index = mi - len(subfolders)
            text = text_files[index]
            with open(text, "r") as f:
                data = f.read()
            title, i = get_title(data, name)
            if i > 0:
                data = data[i:]
            art = {"id":text, "pdfUrl":name, "title":title, "sections":get_sects(data)}
            show_article(art) 

def saved_items():
    menu = {}
    #menu["reviewed articles"]="button"
    menu["tagged articles"]="button"
    menu["notes"]="button"
    menu["comments"]="button"
    shortkeys = {"s":"saved articles", "c":"comments", "n":"notes", "t":"tagged articles", 'x':"text files"}
    options = {}
    mi = 0
    ch = ''
    while ch != 'q':
        info = "h) help         q) quit"
        show_info(info)
        ch, menu, mi = show_menu(menu, options, shortkeys = shortkeys, mi = mi)
        if ch == "n" or ch == "notes":
             list_notes("notes")
        elif ch == "c" or ch == "comments":
             list_comments()
        elif ch == 't' or ch == "tagged articles":
            list_tags()
        elif ch == 's' or ch == "saved articles":
            saved_articles = load_obj("saved_articles","articles")
            list_articles(saved_articles, "Saved Articles")
def settings():
    global theme_menu, doc_path
    choice = '' 
    menu = load_obj("options", "")
    font_size = 24
    path = '~/Documents/Nodcast'
    path.replace('/', os.sep)
    doc_path = os.path.expanduser(path)
    if menu is None:
        menu = {"theme":"button","documents folder":""}
        menu["documents folder"] = doc_path
    else:
        if os.name == 'nt':
            font_size = menu["font size"]
        doc_path = menu["documents folder"]

    if doc_path.endswith("/"):
        doc_path = doc_path[:-1]
    options = {}
    if os.name == 'nt':
        menu["font size"]=font_size
        options["font size"] = [str(fs) for fs in range(18, 26)]

    menu["save and quit"] = "button"
    mi = 0
    while choice != 'q':
        choice, menu, mi = show_menu(menu, options, title="options", shortkeys={"f": "font size","q":"save and quit"})  
        if choice == "theme":
            _, theme_menu,_ = show_menu(theme_menu, theme_options, title="theme")
            save_obj(theme_menu, conf["theme"], "theme")
        if choice == "font size":
            resize_font_on_windows(int(menu["font size"])) # std)
            show_msg("The font size will changes in the next run of the application")

    doc_path = menu["documents folder"]
    Path(doc_path).mkdir(parents=True, exist_ok=True)
    save_obj(menu, "options", "")
    

def list_notes(notes = "notes"):
    subwins = {
            notes:{"x":7,"y":5,"h":15,"w":68},
            }
    choice = ''
    opts, art_list = refresh_notes(notes)
    if not art_list:
        show_msg("There is no article with nods!")
        return
    clear_screen(std)
    mi = 0
    while choice != 'q':
        nods = ""
        menu = {notes:""} 
        choice, menu,mi = show_menu(menu, opts,
                shortkeys={"n":"notes", "c":"comments"},
                subwins=subwins, mi=mi, title=notes)
        if choice == notes:
            sel_nod = menu[notes][:-5]
            sel_nod = sel_nod.strip()
            articles = art_list[sel_nod]
            if len(articles) > 0:
                ret = list_articles(articles, sel_nod, True)
            opts, art_list = refresh_notes()

def list_comments():
    saved_articles = load_obj("saved_articles","articles", [])
    N = len(saved_articles)
    art_list = []
    for art in saved_articles:
        if "comments" in art:
            art_list.append(art)
    if len(art_list) > 0:
        ret = list_articles(art_list, "comments", True)
    else:
        show_msg("There is no article with comments!")
        return

def refresh_notes(in_note = "notes"):
    saved_articles = load_obj("saved_articles","articles", [])
    N = len(saved_articles)
    art_num = {}
    art_list = {}
    note_list = []
    for art in saved_articles:
        if not in_note in art:
            continue
        art_notes = art[in_note]
        for notes in art_notes:
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
    opts = {in_note:[]}
    for note in note_list:
        opts[in_note].append(note.ljust(40) + str(art_num[note]))
    return opts, art_list

def refresh_tags():
    saved_articles = load_obj("saved_articles","articles", [])
    N = len(saved_articles)
    art_num = {}
    art_list = {}
    tag_list = []
    for art in saved_articles:
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
    opts = {"tags":[]}
    for tag in tag_list:
        opts["tags"].append(tag.ljust(40) + str(art_num[tag]))
    save_obj(tag_list, "tags", "")
    return opts, art_list

def list_tags():
    subwins = {
            "tags":{"x":7,"y":5,"h":15,"w":68},
            }
    choice = ''
    opts, art_list = refresh_tags()
    if not art_list:
        show_msg("There is no tagged article!")
        return
    clear_screen(std)
    mi = 0
    while choice != 'q':
        tags = ""
        menu = {"tags":""} 
        choice, menu,mi = show_menu(menu, opts,
                shortkeys={"t":"tags"},
                subwins=subwins, mi=mi, title="tags")
        if choice == "tags":
            sel_tag = menu["tags"][:-5]
            sel_tag = sel_tag.strip()
            articles = art_list[sel_tag]
            if len(articles) > 0:
                ret = list_articles(articles, sel_tag, group = "tags")
            opts, art_list = refresh_tags()
        elif choice.startswith("del@tags"):
            save_obj(menu["tags"], "tags", "")

def website():

    menu = load_obj("website_menu", "")
    isFirst = False
    if menu is None:
        menu = {"address":"", "load":"button", "popular websites":"", "saved websites":""}
        isFirst = True

    shortkeys = {"l":"load", "p":"popular websites", 's':"saved websites"}
    ws_dir = user_data_dir(appname, appauthor) + "/websites"
    saved_websites =  [Path(f).stem for f in Path(ws_dir).glob('*') if f.is_file()]
#    if saved_websites:
#        menu["sep1"] = "saved websites"
#    c = 1 
#    for ws in reversed(saved_websites):
#        menu[ws] = "button"
#        shortkeys[str(c)] = ws
#        c += 1
    options = {"history":["None"], "bookmarks":["None"]}
    options["popular websites"] = newspaper.popular_urls()
    options["saved websites"] = saved_websites
    history = load_obj("history", "")
    if history is None:
        history = ["None"]
    elif "None" in history:
        history.remove("None")
    options["history"] = history
    if isFirst:
        for opt in menu:
           if opt in options:
               menu[opt] = options[opt][0] if options[opt] else ""
    clear_screen(std)
    ch = ''
    mi = 0
    subwins = {"saved websites":{"x":16,"y":7,"h":10,"w":48}}
    info = "h) help | q) quit"
    while ch != 'q':
        ch, menu, mi = show_menu(menu, options, shortkeys = shortkeys, mi = mi, subwins= subwins, info = info)
        if (ch == "load" or ch == "l" or ch == "popular websites"):
            site_addr = ""
            if ch == 'l' or ch == "load":
                site_addr = menu["address"]
            if ch == "popular websites":
                site_addr = menu["popular websites"]
            if not site_addr:
                info = "error: the site address can't be empty!"
            else:
                 show_info("Gettign articles from " + site_addr  + "... | Hit Ctrl+C to cancel")
                 config = newspaper.Config()
                 config.memoize_articles = False
                 try:
                     site = newspaper.build(site_addr, memoize_articles = False) # config)
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
                 stored_exception=None
                 for a in site.articles:
                     try:
                         a.download()
                         a.parse()
                         sleep(0.01)
                         show_info("loading "+ a.title[:60] + "...")
                         if stored_exception:
                            break
                     except KeyboardInterrupt:
                         stored_exception=sys.exc_info()
                     except Exception as e:
                         show_info("Error:" + str(e))
                         continue

                     #a.nlp()
                     figures = []
                     count = 0
                     for img in list(a.imgs):
                         count += 1
                         figures.append({"id":img, "caption": "Figure " + str(count)})
                     art = {"id":a.title,"pdfUrl":a.url, "title":a.title, "figures":figures, "sections":get_sects(a.text)}
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

    menu =  None #load_obj("webpage_menu", "")
    isFirst = False
    if menu is None:
        menu = {"address":"","sep1":"", "load":"button", "recent pages":""}
        isFirst = True

    shortkeys = {"l":"load", "r":"recent pages"}
    options = {}

    recent_pages = load_obj("recent_pages", "articles")
    if recent_pages is None:
        recent_pages = []
    arts = []
    for art in recent_pages:
        uri = urlparse(art["pdfUrl"])
        name = "(" + uri.netloc + ") " + art["title"]
        arts.append(name)
    options["recent pages"] = arts
    subwins = {"recent pages":{"x":12,"y":7,"h":10,"w":68}}
    if isFirst:
        for opt in menu:
           if opt in options:
               menu[opt] = options[opt][0] if options[opt] else ""

    menu["address"]=""
    clear_screen(std)
    ch = ''
    mi = 0
    history = load_obj("history", "", [])
    info = ""
    while ch != 'q':
        ch, menu, mi = show_menu(menu, options, shortkeys = shortkeys, mi = mi, subwins= subwins, info = info)
        url = ""
        if ch == 'l' or ch == "load":
            url = menu["address"]
        if url != "":
             show_info("Gettign article from " + url)
             config = newspaper.Config()
             config.memoize_articles = False
             config.fetch_images = False
             config.follow_meta_refresh = True
             try:
                 a  = newspaper.Article(url)
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
             art = {"id":a.title,"pdfUrl":a.url, "title":a.title, "sections":get_sects(a.text)}
             insert_article(recent_pages, art)
             del recent_pages[100:]
             save_obj(recent_pages, "recent_pages","articles")
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
    menu = load_obj("query_menu", "")
    isFirst = False
    if menu is None:
        isFirst = True 
        menu = {}
        if is_obj("last_results",""):
            menu["last results"]="button"
        menu["keywords"] = ""
        menu["year"] = ""
        menu["task"] =""
        menu["conference"] = ""
        menu["dataset"] = ""
        menu["sep1"] = ""
        menu["search"] = "button"
    options = {
            "year":["All"] + [str(y) for y in range(now.year,2010,-1)], 
            "task": ["All", "Reading Comprehension", "Machine Reading Comprehension","Sentiment Analysis", "Question Answering", "Transfer Learning","Natural Language Inference", "Computer Vision", "Machine Translation", "Text Classification", "Decision Making"],
            "conference": ["All", "Arxiv", "ACL", "Workshops", "EMNLP", "IJCNLP", "NAACL", "LERC", "CL", "COLING", "BEA"],
            "dataset": ["All","SQuAD", "RACE", "Social Media", "TriviaQA", "SNLI", "GLUE", "Image Net", "MS Marco", "TREC", "News QA" ],
            }
    if isFirst:
        for opt in menu:
           if opt in options:
               menu[opt] = options[opt][0] if options[opt] else ""
    clear_screen(std)
    ch = ''
    shortkeys = {"s":"search", "l":"last results"}
    mi = 0
    while ch != 'q':
        ch, menu, mi = show_menu(menu, options, shortkeys = shortkeys, mi = mi)
        if ch != 'q':
            for k,v in menu.items():
                if k in filter_items and v and v != "All":
                    filters[k] = str(v)
            try:
                ret = ""
                if ch == 's' or  ch == 'search':
                    show_info("Getting articles...")
                    query = menu["keywords"]
                    fid = menu["keywords"] + '_' + menu["year"] + '_1_' + menu["conference"] + '_' + menu["task"] + '_' + menu["dataset"]
                    fid = fid.replace('All','')
                    fid = fid.replace('__','_')
                    fid = fid.replace('__','_')
                    fid = fid.replace('__','_')
                    articles,ret = request(0)
                    if len(articles) > 0 and ret == "":
                        if isinstance(articles, tuple):
                            articles = articles[0]
                        save_obj(articles, "last_results", "")
                        ret = list_articles(articles, fid)
                    if ret:
                        show_err(ret[:200]+ "...", bottom = False)

                elif ch == 'l' or ch == "last results":
                    show_last_results()

            except KeyboardInterrupt:
                choice = ord('q')
                show_cursor()
    save_obj(menu, "query_menu", "")

def show_last_results():
     menu = load_obj("query_menu", "", {"keywords":""})
     last_query = menu["keywords"]
     query = last_query
     last_results_file = user_data_dir(appname, appauthor) + "/last_results.pkl"
     obj_file = Path(last_results_file) 
     if  obj_file.is_file():
        cr_time = time.ctime(os.path.getmtime(last_results_file))
        cr_date = str(cr_time)
     articles = load_obj("last_results", "", [])
     if articles:
         ret = list_articles(articles, "results at " + str(cr_date) + " for " + last_query)
     else:
         show_msg("Last results is missing....")

def main():
    global doc_path
    nr_options = load_obj("options", "")
    if nr_options != None:
        doc_path = nr_options["documents folder"]
        Path(doc_path).mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        maximize_console(29)       
        orig_size = resize_font_on_windows(20, True)
        orig_size = int(orig_size) if str(orig_size).isdigit() else 20
        if nr_options != None:
            fsize =int(nr_options["font size"]) if "font size" in nr_options else 24 
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
