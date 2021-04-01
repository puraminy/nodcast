# Nodcast v 0.1.2
import requests
import io
import platform
import webbrowser
import time
import string
import re
from subprocess import call
from time import sleep
from itertools import filterfalse
import datetime
import pickle
import textwrap
import json
import urllib.request
import urllib.parse
pyperclip_imported =False
try:
    import pyperclip 
    pyperclip_imported =True
except:
    pass
try:
    from nodcast.util import *
except:
    from util import *
import curses as cur
from curses import wrapper
from pathlib import Path
import shutil
from appdirs import *
import logging, sys
import traceback
import subprocess
#from gtts import gTTS

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
left_side_win = None
right_side_win = None

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

pdf2text_imported = True
#try:
from pdfminer.pdfparser import  PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LTTextBox,LTTextLine,LTChar, LTTextBoxHorizontal,LTFigure,LTImage
#except ImportError as e:
#    pdf2text_imported = False

std = None
theme_menu = {}
theme_options = {}
template_menu = {}
template_options = {"preset":{}}

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
ARROWS = [UP, DOWN, LEFT, RIGHT, SLEFT, SRIGHT, SUP, SDOWN]

nod_colors = {
    "yes": 77,
    "OK": 36,
    "OK, I get it now": 36,
    "I agree!": 22,
    "answer": 41,
    "idea": 151,
    "correct": 30,
    "incorrect": 161,
    "background": 93,
    "archive": 145,
    "okay": 36,
    "okay, okay!": 25,
    "okay, go on": 30,
    "okay?": 240,
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
    "question": 136,
    "comment": 141,
    "didn't get the article": 161,
    "didn't get, needs review": 161,
    "okay, never mind": 145,
    "what?!": 161,
    "what?! needs review": 161,
    "don't think so": 179,
    "not sure!": 179,
    "what?!": 31,
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
    "check later": 186,
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

hl_colors = [(137,52), (137,236), (137,234), (144, 234), (95,233), (95, 17), (245,17), (245,235)]

def extractPdfText(file):
    menu = {}
    menu["sections"] = ""
    menu["pages (from-to)"] = ""
    menu["convert"] = "button"
    menu["sep1"] = "Advanced Options for pdfMiner"
    menu["boxes-flow"] = "-0.5"
    menu["line-margin"] = "0.5"
    menu["word-margin"] = "0.2"
    menu["char-margin"] = "2.0"
    menu["text-size"] = "9.0"
    options = {"sections":{"range":["All except References", "All", "References", "Abstract", "Abstract+Introduction+Conclusion"]} }
    options["boxes-flow"]= {"range":[str(x/10) for x in range(-10,11)]}
    options["line-margin"]= {"range":[str(x/20) for x in range(0,11)]}
    options["word-margin"]= {"range":[str(x/20) for x in range(0,11)]}
    options["char-margin"]= {"range":[str(x/1) for x in range(1,25)]}
    options["text-size"]= {"range":[str(x/1) for x in range(5,15)]}
    ch = ''
    mi=0
    while ch != 'q':
        ch, opts, mi = show_menu(menu, options, shortkeys={"c":"convert"}, mi = mi)
        if ch == "convert":
            params={"boxes_flow":float(menu["boxes-flow"]), 
                    "char_margin":float(menu["char-margin"]),
                    "word_margin":float(menu["word-margin"]),
                    "line_margin":float(menu["line-margin"])}
            _from_to = menu["pages (from-to)"]
            pages = []
            if _from_to and not "-" in _from_to:
                show_err("Invalid input, enter two numbers separated by a dash, example 3-7")
                continue
            elif _from_to:
                _from, _to = _from_to.split("-")
                if not _from.isdigit() and _to.isdigit():
                    show_err("Invalid input, enter two numbers separated by a dash, example 3-7")
                    continue
                else:
                    _from = int(_from) - 1
                    _to = int(_to) - 1
                    pages = range(_from, _to)
            show_info("Converting ...")
            if menu["sections"] == "All except References":
                sel_sects = "all-references"
            else:
               sel_sects = menu["sections"].lower()
            return extractText(file, sel_sects, pages=pages, params= params, def_size=menu["text-size"]), _from_to, sel_sects
    return "","",""

#xxxx
from io import BytesIO
from pdfminer.converter import TextConverter

def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = BytesIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()
    with open(path, 'rb') as fp:
        for page in PDFPage.get_pages(fp, pagenos,
                                      maxpages=maxpages, password=password,
                                      caching=caching, check_extractable=True):
            interpreter.process_page(page)

    text = retstr.getvalue()

    device.close()
    retstr.close()

    return str(text)

def extractText(file, sel_sects="", pages=[], params={}, def_size = 9):
    def_size = float(def_size)
    if not pdf2text_imported:
        return ""
    text = ""
    if not params:
        params={"boxes_flow":-0.5, "char_margin":2.0, "word_margin":0.15, "line_margin":0.5}
        #params = {}
    with open(file, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        if not doc.is_extractable:
            show_err("The Pdf file doesn't allow text extraction")
            return ""
        rsrcmgr = PDFResourceManager()
        if params:
            laparams = LAParams(boxes_flow=params["boxes_flow"], 
                char_margin=params["char_margin"], line_margin=params["line_margin"],
                word_margin=params["word_margin"],
                detect_vertical=False)
        else:
            laparams = LAParams()

        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        pat = re.compile("^(\w+[.]\s)?(?:(\d{1,3}\.?(?:\d{1,3}\.?)*)?) ?([\w\s\-\t\?:]{3,50})$")
        page_numbers = re.compile("^(\d{1,4}( of \d{1,4})?)$")
        seen = {}
        sections = ["abstract","introduction","references","related work", "summary", "conclusion"]
        cur_sect = ""
        to_prev = 0
        figure = ""
        def_size_set = False
        table_pat = re.compile("Table \d{1,2}:")
        for pn, page in enumerate(PDFPage.create_pages(doc)):
            if pages and not pn in pages:
                continue
            interpreter.process_page(page)
            layout = device.get_result()
            short_line = True
            new_page = True
            for element in layout:
                # if isinstance(element, LTFigure):
                if isinstance(element, LTTextBox):
                    new_box = True
                    p = element.get_text().strip()
                    if not p:
                        continue
                    if table_pat.search(p):
                       continue
                    if "following the above" in p:
                        seen["indcate"] = True
                    if "references" in seen:
                        text += "<FRAG>"
                    if text.endswith(".") and figure != "":
                        text += figure
                        figure = ""
                    if p.startswith("Figure"):
                        figure = p
                    else:
                        for lineObj in element._objs:
                            if isinstance(lineObj, LTTextLine):
                                line = lineObj.get_text().strip()
                                if not line:
                                    continue
                                if line.strip():
                                    charObj=lineObj._objs[0]
                                    #if not def_size_set and "abstract" in seen:
                                    #    def_size = round(charObj.size,1) + 0.2
                                    #    def_size_set = True
                                    if isinstance(charObj, LTChar):
                                        if round(charObj.size,1) < def_size:
                                            break
                                sect_seen = False
                                to_prev += 1
                                for sect in sections:
                                    if len(line) < len(sect) + 5 and sect in line.lower():
                                        seen[sect] = True
                                        cur_sect = sect
                                        sect_seen = True

                                if sel_sects and cur_sect:
                                    if "-"+cur_sect in sel_sects:
                                        continue
                                    if not "all" in sel_sects and not cur_sect in sel_sects:
                                        continue
                                if sect_seen:
                                    text += "\n## " + line + "\n"
                                    continue
                                #if not "abstract" in seen:
                                #    continue
                                page_number = page_numbers.search(line)
                                if page_number:
                                    continue
                                out = pat.search(line)
                                if out and out.group(2) and to_prev > 5 and not "references" in seen: 
                                    if len(out.group(3)) >= 2 and len(out.group(3)) < 60:
                                        parts = out.group(2).split('.')
                                        to_prev = 0
                                        if len(parts) <= 1:
                                            text += "\n## " + out.group(2) + " " + out.group(3)+ "\n"
                                        else:
                                            text += "\n### " + out.group(2) + " " +  out.group(3)+ "\n"
                                        continue

                                if False: #len(line) < 10: # Remove successive short lines
                                    if short_line or not "title" in seen:
                                        continue
                                    else:
                                        short_line = True
                                else:
                                    short_line = False
                                if not "title" in seen:
                                    text += "# " + p.replace("\n"," ") + "\n"
                                    seen["title"] = True
                                    break
                                if (new_page or new_box):
                                    if line[0].isupper() or text.endswith('.'):
                                        if new_page:
                                            text += f"============= Page {pn} ==========<stop>"
                                            new_page = False
                                        text += "\n"
                                        new_box = False
                                if line.endswith("-"):
                                    line = line[:-1]
                                else:
                                    line += " "
                                text += line 
                    if "references" in seen:
                        text += "</FRAG>"
                    #text += "\n"
    return text

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
    reset_hl(theme)
    cur.init_pair(CUR_ITEM_COLOR, bg, int(theme["cur-item-color"]) % cur.COLORS)
    cur.init_pair(SEL_ITEM_COLOR, bg, int(theme["sel-item-color"]) % cur.COLORS)
    cur.init_pair(INPUT_COLOR, TEXT_COLOR, int(theme["input-color"]) % cur.COLORS)
    cur.init_pair(ERR_COLOR, cW, cR % cur.COLORS)
    cur.init_pair(MSG_COLOR, cW, clB % cur.COLORS)
    #cur.init_pair(INFO_COLOR, 235, cG % cur.COLORS)
    cur.init_pair(INFO_COLOR, 243, 235 % cur.COLORS)
    cur.init_pair(WARNING_COLOR, cW, cO % cur.COLORS)

def reset_hl(theme):
    global HL_COLOR
    if theme["inverse-highlight"] == "True":
        cur.init_pair(HL_COLOR, int(theme["hl-text-color"]) % cur.COLORS,
                      int(theme["highlight-color"]) % cur.COLORS)
    else:
        cur.init_pair(HL_COLOR, int(theme["highlight-color"]) % cur.COLORS,
                      int(theme["hl-text-color"]) % cur.COLORS)
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
    title = art["title"]
    file_name = title.replace(' ', '-')[:50]  # url.split('/')[-1]
    if "save_folder" in art:
        fname = art["save_folder"] + "/" + file_name
    else:
        folder = doc_path + "/" + profile
        if folder.endswith("/"):
            folder = folder[:-1]

        fname = folder + "/" + file_name
    pdf_file = Path(fname + ".pdf")
    art_file = Path(fname + ".art")
    if pdf_file.is_file():
        pdf_file.unlink()
        art-file.unlink()
        show_info("File was deleted")
    else:
        show_info("File wasn't found on computer")

def move_pdf(art,fname, full_path=True):
    url = art["localPdfUrl"] if "localPdfUrl" in art else art["pdfUrl"]
    src_file = Path(url[7:])
    if src_file.is_file() and not Path(fname).is_file():
        if src_file.parent == Path(fname).parent or not full_path:
            if not full_path:
                fname = str(src_file.parent) + "/" + fname
            shutil.move(src_file, Path(fname))
            art["localPdfUrl"] = "file://" + fname
        else:
            if str(src_file.parent).endswith("Files"):
                shutil.move(src_file, Path(fname))
                art["localPdfUrl"] = "file://" + fname
        return True
    return True

def download_or_open(url, art, fname, open_file =True, download_if_not_found=True):
    if not url.endswith("pdf"):
        webbrowser.open(url)
        return
    if url.startswith("file://"):
        move_pdf(art, fname)

    if "localPdfUrl" in art:
        fname = art["localPdfUrl"][7:]
    _file = Path(fname)
    if _file.is_file():
        mbeep()
        if open_file:
            openFile(_file)
    elif not url.startswith("file://") and download_if_not_found:
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


            except Exception as e:
                show_err("ERROR:" + str(e))
                return
            except KeyboardInterrupt:
                show_info("loading canceled")
                return

            _file.write_bytes(BufferAll.getvalue())
            show_info("File was written to " + str(_file))
            if open_file:
                openFile(_file)
    else:
        return False
    return True

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


def save_doc(doc, docname, folder="", root =False):
    if root:
        path = doc_path 
    else:
        path = doc_path + '/' + profile   

    path += "/" + folder  
    if not path.endswith("/"):
        path += "/"

    Path(path).mkdir(parents=True, exist_ok=True)
    fname = path + docname 
    with open(fname, 'w') as outfile:
        json.dump(doc, outfile)

def load_doc(docname, folder, default = {}, root = False):
    if root:
        path = doc_path
    else:
        path = doc_path + '/' + profile 
    if folder != "":
        path += "/" + folder + "/" 
    fname = path + docname 
    obj_file = Path(fname)
    if not obj_file.is_file():
        return default
    with open(fname, 'r') as _file:
        doc = json.load(_file)
        return doc

def load_docs(folder, ext):
    if folder == "":
        path = doc_path + '/' + profile +"/"  
    else:
        path = doc_path + '/' + profile +"/" + folder + "/" 

    return load_docs_path(path, ext)

def load_docs_path(path, ext):
    _, files = load_rec_docs(path, ext)
    docs = []
    for fname in files:
        with open(fname, 'r') as _file:
            doc = json.load(_file)
            docs.append(doc)
    return docs

def load_rec_docs(folder, ext):    # folder: str, ext: list
    subfolders, files = [], []

    for f in os.scandir(folder):
        if f.is_dir():
            subfolders.append(f.path)
        if f.is_file():
            if os.path.splitext(f.name)[1].lower() in ext:
                files.append(f.path)


    for folder in list(subfolders):
        sf, f = load_rec_docs(folder, ext)
        subfolders.extend(sf)
        files.extend(f)
    return subfolders, files

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

def remove_saved_article(artid):
    saved_articles = load_obj("saved_articles", "articles", {})
    del saved_articles[artid]
    save_obj(saved_articles, "saved_articles", "articles")

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
        if end > 100:
            end = 100
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
        for sect in sects:
            if not sect.strip(): 
                continue
            new_sect = {}
            end = sect.find("\n")
            sect_title = sect[:end]
            new_sect["title"] = sect_title if sect_title.strip() else "untitled section"
            frags = sect[end:]
            new_sect["fragments"] = get_frags(frags)
            ret.append(new_sect)
    return ret

def get_frags(text, cohesive =False, split_level = 0, word_limit=5):
    text = "\n" + text
    subs = text.split("\n### ")
    if len(subs) == 1:
        return extract_frags(text, cohesive, split_level, word_limit)
    else:
        frags = []
        for i, sub in enumerate(subs):
            sub = sub.strip()
            if not sub:
                continue
            if i > 0 or sub.startswith("### "):
                end = sub.find("\n")
                title = sub[:end]
                sub_text = sub[end:]
            else:
                title = ""
                sub_text = sub
            sub_frags = extract_frags(sub_text, cohesive, split_level, word_limit, title)
            frags.extend(sub_frags)
        return frags

def extract_frags(text, cohesive=False, split_level = 0, word_limit=5, title = ""):
    text = text.strip()
    delimits = split_levels[split_level]
    if split_level == 0:
        parts = text.split("\n")
    else:
        parts = split_into_sentences(text, limit = word_limit, split_on = delimits)

    parts = list(filter(None, parts))
    frags = []
    for t in parts:
        if t[0].isupper() and "[ edit ]" in t and title == "":
            title = t
            continue
        frag = {"text":t}
        frag["sents"] = init_frag_sents(t, cohesive)
        if len(frag["sents"]) > 0 and title != "":
            frag["title"] = title
            title = ""
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
    rows, cols = std.getmaxyx()
    size = rows - 8
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
def list_artids(id_list, fid, group):
    articles = []
    saved_articles = load_obj("saved_articles", "articles", {})
    for _id in id_list:
        if _id in saved_articles:
            articles.append(saved_articles[_id])
    arts = list_articles(articles, fid, group=group)
    artids = []
    for art in arts:
        artids.append(art["id"])
    if group != "":
        with open(group, 'w') as outfile:
            json.dump(artids, outfile)


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
    cap = rows - 8
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
        while cc < start + cap and jj < len(articles):
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
            if (len(a["sections"]) > 0 
                    and "sents" in a["sections"][0]["fragments"][0]):
                review = a["sections"][0]["fragments"][0]["sents"][0]
                if "nods" in review:
                    note_indx = min(max(0, note_index), len(review["nods"]))
                    if note_index < len(review["nods"]):
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
        _p = k // cap
        all_pages = (N // cap) + (1 if N % cap > 0 else 0)
        mprint(" total:" + str(N) + " | page " + str(_p + 1) + " of " + str(all_pages), list_win, color = DIM_COLOR)
        left = ((cols - width) // 2)
        rows, cols = std.getmaxyx()
        if hotkey == "":
            # print_sect(cur_title, cur_prog, left)
            mprint(cur_title, list_win)
            list_win.refresh(0, 0, 1, 2, rows - 2, cols - 2)
            std.refresh()
            #list_win.refresh()
            show_info("h) list commands ")
        ch = get_key(std)

        if ch == ord("r") or is_enter(ch) or ch == RIGHT:
            k = max(k, 0)
            k = min(k, N - 1)
            list_win.erase()
            list_win.refresh(0, 0, 1,2, rows - 3, cols - 2)
            #list_win.refresh()
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

        if k >= start + cap and k < N:
            ch = cur.KEY_NPAGE
        if k < start:
            ch = "prev_pg"

        if ch == cur.KEY_PPAGE or ch == 'prev_pg':
            start -= cap
            start = max(start, 0)
            k = start + cap - 1 if ch == 'prev_pg' else start
        elif ch == cur.KEY_NPAGE:
            start += cap
            if start > N - cap:
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
            start = min(start, N - cap)
            k = start
        elif ch == cur.KEY_HOME:
            k = start
        elif ch == cur.KEY_END:
            k = N - 1  # start + 14
            mod = cap if N % cap == 0 else N % cap
            start = N - mod

        if ch == ord('h'):
            show_info(('\n'
                       ' s)            select/deselect an article\n'
                       ' a)            select all articles\n'
                       ' r/Enter/Right open the selected article\n'
                       " f)            filter the articles by the title's nod \n"
                       ' t)            tag the selected items\n'
                       ' d/DEL)        delete the selected items from list\n'
                       ' w)            save the selected articles as al list\n'
                       ' x)            export the selected files\n'
                       ' T)            change the color theme\n'
                       ' HOME)         go to the first item\n'
                       ' END)          go to the last item\n'
                       ' PageDown)     next page or load more\n'
                       ' PageUp)       previous page\n'
                       ' Arrow keys)   next, previous article\n'
                       ' q/Left)       return back to the main menu\n'),
                      bottom=False)
        if ch == ord('s') or ch == ord(' '):
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
        if ch == ord('T'):
            choice = ''
            while choice != 'q':
                choice, theme_menu, _ = show_menu(theme_menu, theme_options, title="theme")
            save_obj(theme_menu, conf["theme"], "theme")
            list_win.erase()
            #list_win.refresh()
            list_win.refresh(0, 0, 1, 2, rows - 2, cols - 2)
        if ch == ord('A'):
            pyperclip.copy(articles[k]["title"])
            show_msg("Title was copied to the clipboard")
        if ch == ord('a'):
            for ss in range(start, min(N, start + cap)):
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
                        _confirm = confirm_all("Are you sure you want to remove the article " + art["title"][:20])
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
                        _confirm = confirm_all("Are you sure you want to remove the last tag of " + art["title"][:20])
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
        if ch == ord('x'):
            if not sel_arts:
                show_err("No article was selected")
            else:
                choice = ''
                mi = 0
                while choice != 'q':
                    template_menu["export"] = "button"
                    template_menu["save folder"] = doc_path + "/Files/" + template_menu["preset"] + "/"
                    choice, template_menu, mi = show_menu(template_menu, 
                            template_options, 
                            title="template", mi=mi, 
                            shortkeys={"x":"export","s": "save as"})
                    if choice == "export":
                        choice = 'q'
                        folder = template_menu["save folder"]
                        for art in sel_arts:
                            write_article(art, folder)
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

                path = doc_path + '/' + folder + "/"
                Path(path).mkdir(parents=True, exist_ok=True)
                with open(path + " [ " + str(len(sel_arts)) + " articles]" + '.list', 'w') as outfile:
                    json.dump(sel_arts, outfile)
                for a in sel_arts:
                    write_article(a, folder)
                show_msg(str(len(sel_arts)) + " articles were downloaded and saved into saved articles")
    return articles


def replace_template(template, old_val, new_val):
    ret = template.replace("{newline}", "\n")
    ret = ret.replace(old_val, new_val)
    return ret


def write_article(article, folder=""):
    ext = '.' + template_menu["preset"]
    _folder = folder
    if _folder == "":
        _folder = doc_path + "/Files/" + template_menu["preset"]
    Path(_folder).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(_folder):
        os.makedirs(_folder)
    top = replace_template(template_menu["top"], "{url}", article["pdfUrl"])
    bottom = replace_template(template_menu["bottom"], "{url}", article["pdfUrl"])
    paper_title = article['title']
    file_name = paper_title #.replace(' ', '_').lower()
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
notes_dict = {"+":"point", "&":"answer",  "-":"check later","?":"question", "\\":"comment"}
notes_list = list(notes_dict.values())
notes_keys = list(notes_dict.keys())
nods_show = ["correct", "incorrect"]
pos_nods = ["okay", "I see!"]
neg_nods = ["what?!","okay, never mind"]
nods_list = ["didn't get", continue_nod, "OK, I get it now", "okay", "I see!", "interesting!"]
art_sent_types = ["problem statement", "research question", "definition", "description", "classification","claim", "background", "proposed solution", "finding", "goal", "feature", "contribution", "comparison", "usage", "example"]
sent_types = ["main idea", "example", "support"]
art_status = ["interesting!", "novel idea!", "my favorite!", "important!", "needs review", "check later", "not bad","not of my interest","didn't get it!", "survey paper", "archive", "not reviewed", "to read later"]
feedbacks = set(pos_nods + neg_nods + notes_list + nods_list + art_status)

def find_color(sents, fsn, check_next = False, okays = False):
    if "hidden" in sents[fsn] and sents[fsn]["hidden"]:
        return back_color
    if okays and not "okays" in sents[fsn]:
        return 30
    key = "okays" if okays else "nod"
    nod = sents[fsn][key]
    if check_next and sents[fsn]["next"]:
        ii = fsn
        while sents[ii]["next"] and ii < len(sents):
            ii += 1
        nod = sents[ii][key]
    if okays:
        return 30 + nod
    else:
        return find_nod_color(nod)

def find_nod_color(nod):
    ret = int(theme_menu["text-color"])
    colors = theme_menu
    find = False
    for key, val in colors.items():
        if key == nod:
            ret = val
            find = True

    if not find:
        colors = nod_colors
        for key, val in colors.items():
            if key == nod:
                ret = val
    return int(ret)

def list_nods(win, ypos, cur_nod):
    if cur_nod == "" or cur_nod == "skipped": cur_nod = "okay"
    xpos = 2
    nods = list(reversed(neg_nods)) + pos_nods
    ni = nods.index(cur_nod) if cur_nod in nods else len(neg_nods) + 1
    for nod in reversed(nods):
        if nod == cur_nod:
            color = find_nod_color(nod)
        else:
            color = DIM_COLOR
        print_there(ypos, xpos, nod, win, color)
        win.clrtoeol()
        ypos += 1

def print_notes(win, notes, ypos, xpos):
    for note in notes:
        if note == "okay" or note in nods_list or note in art_status:
            color = find_nod_color(note)
            print_there(ypos, xpos, ' ' + note, win, color)
            ypos += 1


top_win = None


def print_sect(title, prog, left):
    l_color = TITLE_COLOR
    top_win.clear()
    if title != "":
        prog = int(prog)
        title = textwrap.shorten(title, 2*text_width - 20)
        title = textwrap.fill(title,text_width)
        title = textwrap.indent(title," "*left)
        mprint(title, top_win, l_color, attr=cur.A_BOLD, end="")
        prog_color = TEXT_COLOR  # scale_color(prog)
        #add_info = " [" + str(prog) + "%] "  # + f"({sect_fc+1}/{fnum})"
        #y, x = top_win.getyx()
        #print_there(y, x + 1, add_info, top_win, prog_color, attr=cur.A_BOLD)
    top_win.refresh()


def print_prog(text_win, prog, width):
    w = int(width * prog / 100)
    d_color = scale_color(prog)
    cur.init_pair(TEMP_COLOR2, back_color, d_color % cur.COLORS)
    addinfo = ("Progress:" + str(prog) + "%")
    mprint(addinfo, text_win, d_color)

def print_comment(text_win, comment, width):
    com_sents = split_into_sentences(comment, limit=2)
    for com in com_sents:
        com = textwrap.fill(com,
                        width=width - 4, replace_whitespace=False)
        mprint(com, text_win, TEXT_COLOR, end="\n")
        
def new_sent(s):
    _new_sent = {"text":s,"type":"sentence", "end":'\n','eol':False, 'eob':False, 'eos':False, 'next':False, "block":"sent", "merged":False, "block_id":-1, "nod":"", "countable":False, "visible":True, "hidden":False, 'can_skip':True, "passable":False, "nods":[], "rtime":0, "tries":1, "comment":"", "notes":{}}
    if len(s.split(' ')) <= 1:
        _new_sent["end"] = " "
    return _new_sent

split_levels = [['\n'],['.','?','!'], ['.','?','!',';'], ['.','?','!',';', ' ', ',', '-']]
text_width = 72
text_width = 62
text_width = 52
#iii
def init_frag_sents(text, cohesive =False, unit_sep = "", word_limit = 20, nod = "", split_level = 1, block_id=-1):
    if word_limit == 20 and split_level == 2: word_limit = 10
    all_sents = []
    if split_level == 3:
        sents = []
        lines = textwrap.wrap(text, text_width)
        for line in lines:
            words = line.split()
            for w in words:
                u = new_sent(w)
                u["next"] = False
                u["block"] = "word"
                u["block_id"] = block_id 
                sents.append(u)
            sents[-1]["eol"] = True
            sents[-1]["end"] = "\n"
        sents[-1]["end"] = "\n"
        sents[-1]["eob"] = True
        sents[-1]["eos"] = True
        all_sents = sents
    else:
        if unit_sep != "":
           units = text.split(unit_sep)
           units = list(filter(None, units))
        else:
           units = [text]
        all_sents = []
        uid = 0 if block_id < 0 else block_id
        for unit in units: 
            unit = unit.strip()
            if not unit:
                continue
            unit_sents = split_into_sentences(unit, limit = word_limit, split_on=split_levels[split_level])
            if not unit_sents:
                continue
            sents = [new_sent(s) for s in unit_sents]
            prev_s = None
            for i,s in enumerate(sents):
                s["nod"] = nod
                s["block_id"] = block_id if block_id < 0 else block_id + i
                s["eos"] = True 
                s["eob"] = block_id >= 0
                if (prev_s and not prev_s["merged"] and len(prev_s["text"]) < 160 and ( 
                    s["text"].lower().startswith(("thus","hense",
                        "so ", "so,", "therefore","thereby","this ", "they", "however", "instead"))
                    or any(x in prev_s["text"].lower() for x in ["shows "]))
                    and not prev_s["text"].startswith(("Figure","Table"))):
                    s["merged"] = True
                    prev_s["text"] = prev_s["text"] +  " " + s["text"]
                prev_s = s
            sents = [sent for sent in sents if not sent["merged"]] 
            prev_s = None
            for i,s in enumerate(sents):
                if prev_s and not prev_s["merged"] and len(s["text"]) < 150:
                    s["merged"] = True
                    prev_s["text"] = prev_s["text"] +  " " + s["text"]
                prev_s = s
            sents = [sent for sent in sents if not sent["merged"]] 
            if cohesive:
                for s in sents:
                    s["next"] = True
                    s["block_id"] = uid
                    s["eob"] = False 
                sents[-1]["next"] = False 
            sents[-1]["eob"] = True 
            all_sents.extend(sents)
            uid  += 1
    return all_sents

def refresh_offsets(art, split_level = 1):
    ii = 1
    prev_sect = None
    fn = 0
    sents = [new_sent(art["title"])]
    for sect in art["sections"]:
        sect["offset"] = ii
        if not "progs" in sect:
            sect["progs"] = 0
        if not prev_sect is None:
            prev_sect["sents_num"] = ii - prev_sect["offset"]
        prev_sect = sect
        _sect = new_sent(sect["title"])
        _sect["passable"] = True
        sents.append(_sect)
        ii += 1
        for frag in sect["fragments"]:
            frag["offset"] = ii
            ofs = 0
            if not "sents" in frag:
                frag["sents"] = init_frag_sents(frag["text"], split_level = split_level)
            for sent in frag["sents"]:
                # sent["passable"] = False
                sent["char_offset"] = ofs
                sents.append(sent)
                ofs += len(sent["text"])
                ii += 1
        sect["fragments"] = [x for x in sect["fragments"] if x["sents"]]
        fn += len(sect["fragments"])
    sect["sents_num"] = ii - prev_sect["offset"]
    return len(art["sections"]),fn, ii, sents

def locate(art, si, sel_first_sent=False):
    ii = 0
    if si < 0:
        si = 0
    for sect in art["sections"]:
        if si < sect["offset"] + sect["sents_num"]:
            break

    if not sect["fragments"]:
        return sect, {"offset": sect["offset"], "sents":[]}, new_sent(""), sect["offset"]
    for frag in sect["fragments"]:
        if sel_first_sent:
            break
        if si < frag["offset"] + len(frag["sents"]):
            break

    sent = new_sent("")
    s_start = si
    for i, sent in enumerate(frag["sents"]):
        s_start = frag["offset"] + i
        if sel_first_sent and not sent["passable"] and sent["visible"]:
            break
        elif s_start >= si:
            break
    return sect, frag, sent, min(si, s_start)

def get_sel_name(path, ext="", cat = "Folder"):
    _win = cur.newwin(10, 60, 2, 5)
    _win.bkgd(' ', cur.color_pair(HL_COLOR))  # | cur.A_REVERSE)
    _win.border()
    if ext == "":
        fs = ["Create New " + cat]+ [f.name for f in os.scandir(path) if f.is_dir()]
    else:
        fs = ["Create New " + cat ]+ [f.name for f in Path(path).glob(ext) if f.is_file()]
    sfi, _ = select_box({cat + "s":fs}, _win, 0, in_row=False, border=True, ret_index =True)
    if sfi < 0:
        return False
    if sfi == 0:
        fid, _ = minput(win_info, 0, 1, cat + " name: My articles/" + profile+"/", default="")
        if fid != "<ESC>":
            if fid.strip() == "": fid = "UC"
            return fid
        else:
            return ""
    else:
        return fs[sfi]

def get_path(art):
    file_name = art["title"][:60]  # url.split('/')[-1]
    if "save_folder" in art and art["save_folder"] != "":
        fname = art["save_folder"] + "/" + file_name 
        return fname
    else:
        folder = profile 
        _def = ""
        path = doc_path + '/' + folder 
        fid = get_sel_name(path, "", "Folder")
        if not fid:
            return False
        else:
            folder += "/" + fid
        path = doc_path + '/' + folder 
        if path.endswith("/"):
            path = path[:-1]
        Path(path).mkdir(parents=True, exist_ok=True)
        art["save_folder"] = str(path)
        fname = path + "/" + file_name
        return fname 
def unset_sent(sent, ch =0):
    conf_msg = """Select what do you want to unset: 
    a) all 
    n) all notes  
         l) last note
         :) last comment ?) last queston _) last check later 
         !) last idea  &) last answer 
         *) all points
    t) type 
    o) nods
    s) sentence
    r) reading time 
    f) external pdf file 
    q) nothing
        """
    if ch == 0:
        _c = confirm(conf_msg, acc=['a','n','t','o', 'l','q'] + notes_keys, bottom=False, list_opts=False)
    else:
       _c = ch
    if _c != 'q':
        if _c == "o" or _c == "a": 
            sent["nod"] = ""
            sent["nods"] = []
            sent["block_id"] = -1 
            sent["next"] = False 
        if _c == "t" or _c == "a": sent["type"] = ""
        if _c == "n" or _c == "a": sent["notes"] = {}
        if _c == "s":
            sent["visible"] = False
        if _c == "l":
            last_note = list(sent["notes"])[-1]
            if len(sent["notes"][last_note]) > 1:
                sent["notes"][last_note].pop()
            else:
                del sent["notes"][last_note]
        if _c in notes_keys:
            note_type = notes_dict[_c]
            if note_type in sent["notes"]:
                if len(sent["notes"][note_type]) > 1:
                    sent["notes"][note_type].pop()
                else:
                    del sents["notes"][note_type]
        if _c == "+" and "point" in sent["notes"]:
            del sent["notes"]["point"]
        if _c == "r" or _c == "a": 
            sent["rtime"] = 0
            sent["tries"] = 1
        if _c == "f":
            delete_file(art)
            art["save_folder"] = ""
    return _c

def reset_q_context(sect): #reset context text for a question
    for f in sect["fragments"]:
        for s in f["sents"]:
            if s["nod"] != "correct":
                s["nod"] = ""

def move_article(art, move_or_copy="move"):
    temp = art["save_folder"]
    fname1 = get_path(art)
    art["save_folder"] = "" # To force it to get a new path to save the article
    fname2 = get_path(art)
    mydate = datetime.datetime.now()
    move_date = mydate.strftime("%Y-%m-%d")
    art["move_date"] = move_date 
    if fname2:
        if Path(fname1 + ".artid").is_file():
            if move_or_copy == "move":
                shutil.move(fname1 + ".artid", fname2 +".artid")
            else:
                shutil.copy(fname1 + ".artid", fname2 +".artid")
        return True
    else:
        art["save_folder"] = temp
        return False

def save_article(art):
    fname = get_path(art)
    if Path(fname + ".artid").is_file():
        with open(fname + ".artid", 'w') as outfile:
            outfile.write(art["id"])

def speak(text, fname):
  tts = gTTS(text=text, lang="en")
  tts.save(fname)

# sss
word_level = False
def show_article(art, show_note="", collect_art = False, ref_sent = ""):
    global theme_menu, theme_options, query, filters, hotkey, show_instruct, word_level

    if not art["sections"]:
        show_msg("The article has no content to show")
        return
    sel_sects = {}
    fast_read = False
    start_row = 0
    rows, cols = std.getmaxyx()
    width = text_width
    needs_review = not "needs_review" in art or art["needs_review"]
    def_review = """Your summary or review of paper:
    """
    #def_inst = """Press @ anywhere in the article to edit the review, and press # to add a review tag."""
    def_inst = """For more information about how to read and review a paper using Checkideh please visit: http://checkideh.com/getting_started#review 
    To hide instructions like this go to the main menu > options > show instructions, and set it to Disabled. """
    if not collect_art and needs_review and art["sections"][0]["title"] != "Review":
        new_sect = {}
        new_sect["title"] = "Review"
        frag = {"text":def_review}
        frag["sents"] = init_frag_sents(def_review, True)
        frag["sents"][-1]["notes"]["instruct"] = [{"text":def_inst}]
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
    frags_text = ""
    art_id = -1
    si = 0
    end_y = rows
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
    if (total_sects > 2 and show_note == "" 
            and not collect_art and si == 0 and ref_sent == ""
            and not art["id"] in saved_articles):
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
    prev_si, prev_bmark = -1,-1
    auto_mode = False
#vvv
    split_level = 1
    total_sects, total_frags, total_sents, sents = refresh_offsets(art, split_level=split_level)
    pos = [0]*total_sents
    first_frag = art["sections"][0]['fragments'][0]
    if si == 0:
        bmark, si = moveon(sents, 0)
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
    nr_opts = load_obj("settings", "", common = True)
    sel_first_sent = False
    total_pr = int(art["total_prog"]) if "total_prog" in art else 0
    start_time = 0
    too_big_warn = False
    start_reading = True
    first = True
    forward = True
    visual_mode = False
    mode = "normal"
    mode_info = main_info
    begin_offset = art["sections"][0]["offset"]
    cur_sect = cur_frag = cur_sent = {}
    can_skip = True
    can_skip_sect = True
    skip_alert = False
    ref_q = si
    ref_rc_sent = -1
    rc_text = "rc_text" in art and art["rc_text"]
    instructs = {"Right":"Press Right to start reading"}
    show_instruct = rc_text
    rc_mode = False
    start_rc = False
    search = ""
    ####
    mydate = datetime.datetime.now()
    create_date = mydate.strftime("%Y-%m-%d")
    save_pdf_folder = doc_path + "/" + profile + "/Files/" + create_date
    Path(save_pdf_folder).mkdir(parents=True, exist_ok=True)
    pdf_name = save_pdf_folder + "/" + art["title"] + ".pdf"
    move_pdf(art, pdf_name)
    #bbb
    update_article(saved_articles, art)
    true_answers = []
    context = None
    prev_idea = ""
    show_sel_nod = False
    if rc_text:
        context = art["sections"][1]
    ni = -1
    hl_index = 0
    scroll_page = False
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
        do_scroll = False
        if not can_skip:
            if ch == ord('s'):
                start_rc = True
            elif ch == UP:
                if not sents[si]["type"] == "question":
                    mbeep()
                    si = prev_si
                    bmark = prev_bmark
                    show_instruct = True
                    do_scroll = False
                else:
                    reset_q_context(context)
            elif ch == ord('n'):
                can_skip = True
                cur_sent["nod"] = "skipped"
                cur_sent["hidden"] = False
                do_scroll = False
                reset_q_context(context)
            elif ch == ord('g'):
                for note, val in cur_sent["notes"].items():
                    if note == "answer":
                        for ans in val:
                            ans['visible'] = True
                can_skip = True
                cur_sent["nod"] = "give up"
                cur_sent["hidden"] = False
                cur_sent["can_skip"] = True
                do_scroll = False
                reset_q_context(context)
            elif ch == RIGHT or ch == ord('\t'):
                ref_q = prev_si
                true_answers = cur_sent["notes"]["answer"]
                si = cur_sect["offset"] + cur_sect["sents_num"] if ref_rc_sent < 0 else ref_rc_sent
                si, bmark = moveon(sents, si)
                rc_mode = rc_text 
                #sel_first_sent = True
                can_skip = False
            else:
                si = prev_si
                if not skip_alert or ch == RIGHT:
                    mbeep()
                    skip_alert = True
                    show_instruct = True 
                bmark = prev_bmark
                do_scroll = False
        if not can_skip_sect and cur_sect:
            if (ch == LEFT and not word_level) or ch == ord('\t'):
                ref_rc_sent = bmark - 1
                si = ref_q
                can_skip_sect = False
                rc_mode = False
            elif si < cur_sect['offset']:
                mbeep()
                si = cur_sect['offset'] + 1
                bmark = si
                do_scroll = False
                show_instruct = True
            elif si > cur_sect['offset'] + cur_sect['sents_num']:
                mbeep()
                si = cur_sect['offset'] + cur_sect['sents_num']
                bmark = si
                do_scroll = True
                show_instruct = True
            
        if do_scroll:
            if ch == DOWN: start_row += 10
            if ch == UP: start_row -= 10
            if ch == cur.KEY_NPAGE: start_row += 30
            if ch == cur.KEY_PPAGE: start_row -= 30
            if ch == cur.KEY_HOME: start_row = 0
            if ch == cur.KEY_END: start_row = end_y 
            scroll_page = True
        if not do_scroll and not can_skip:
            mbeep()
        if  prev_si != si:
            cur_nod = ""
            split_level  = 1
            prev_si = si
            prev_bmark = bmark
        prev_sect = cur_sect
        prev_frag = cur_frag
        prev_sent = cur_sent
        cur_sect, cur_frag, cur_sent, si = locate(art, si, sel_first_sent)

        if si - prev_si > 10: #jump detected
            first = True

        can_skip_sect = True
        can_skip = True
        if "can_skip" in cur_sent:
            can_skip = cur_sent["can_skip"]
        if not can_skip and cur_sent["type"] == "question" and start_rc:
            mode = "Questions"
            mode_info = "Check the instructions"
        if "can_skip" in cur_sect:
            can_skip_sect = cur_sect["can_skip"]
        if not can_skip_sect and cur_sect["title"] == "Context":
            mode = "Text"
            mode_info = "Check the instructions"
            

        if mode == "Questions": 
            instructs = {}
            instructs["Right/TAB"] = "Switch to text"
            instructs["Left"] = "Skip the question"
            instructs["-"] = "Mark question as 'impossible to answer' based on the given text"

        if mode == "Text" and not word_level: 
            instructs = {}
            instructs["TAB"]="Switch to question"
            instructs["Up/Down"]="Navigate between sentences"
            instructs["Right"]="Select the sentence that contains the answer"
        if rc_mode and word_level:
            instructs = {}
            instructs["Arrow keys"]="Navigate between words"
            instructs["Shift + Arrow keys"] = "start/end marking"
            instructs["q"] = "Cancel"
            instructs["Enter"]="Mark the answer and return to the question"
        if prev_sent and prev_sent["block"] == "word" and cur_sent["block_id"] != prev_sent["block_id"]:
            word_level = False
            ii = prev_sent["block_id"]
            jj = ii
            while ii < total_sents and  sents[ii]["block_id"] == jj:
                sents[ii]["next"] = True
                ii += 1
            sents[ii-1]["next"] = False

        if bmark > si:
            bmark = si

        if not scroll_page and not word_level:
            if not do_scroll:
                scroll_page = False
            top_margin = 15 if cur_sect == art["sections"][0] else 12 #rows // 3
            if len(cur_sent["text"]) > 450:
                top_margin = 20
            bmark = max(0, bmark)
            cur_pos = bmark if expand == 1 else cur_sect['offset']
            if cur_pos < len(pos) and pos[cur_pos] > top_margin:
                start_row = pos[cur_pos] - top_margin
            else:
                start_row = 0

        sel_first_sent = False
        bmark = min(bmark, si)
        start_row = max(0, start_row)
        start_row = min(end_y - 1, start_row)
        if bg != theme_menu["back-color"]:
            bg = theme_menu["back-color"]
            clear_screen(std)
            # text_win.refresh(start_row,0, 0,0, rows-1, cols-1)
            show_info(main_info)
        text_win.erase()
        left_side_win.erase()
        right_side_win.erase()
        sn = 0
        title = "\n".join(textwrap.wrap(art["title"], width))  # wrap at 60 characters
        pdfurl = "NA"
        if "pdfUrl" in art: 
            pdfurl = art["pdfUrl"] 
        elif "localPdfUrl" in art and "/" in art["localPdfUrl"]:
            pdfurl = art["localPdfUrl"].split("/")[-1]
        top = ""
        if not collect_art:
            if "save_folder" in art and Path(art["save_folder"]).is_file():
                top = "[open file] "
            else:
                if pdfurl.endswith("pdf"):
                    top = "[download] " + pdfurl
                else:
                    top = "[open link] " + pdfurl

        total_prog = int(round(si / total_sents*100, 2))
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
        type_count = {}
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
            #sents[fsn]["passable"] = True
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
            sent_count = 1
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
                    if too_big_art: 
                        break
                    if frag != cur_frag and expand == 3:
                        fsn += frag['sents_num']
                        ffn += 1
                    elif (not first and pos[fsn] > start_row + rows + rows//2):
                        break
                    else:
                        new_frag = True
                        prev_sent = None
                        lines_count = 0
                        if "title" in frag and frag["title"]:
                            mprint(frag["title"], text_win, ITEM_COLOR, attr=cur.A_BOLD)

                        if not "sents" in frag:
                            frag["sents"] = init_frag_sents(frag["text"])
                        _sents = frag["sents"]
                        hlcolor = HL_COLOR
                        color = DIM_COLOR
                        # fff
                        if not too_big_art:
                            nexts = 0
                            word_count = 0
                            frag_offset = fsn
                            frag_end = frag_offset + len(_sents) -1
                            has_sents = False
                            while fsn <= frag_end and not too_big_art:
                                sent = _sents[fsn - frag_offset] 
                                feedback = sent["nod"] if "nod" in sent else ""
                                if b == cur_sect:
                                    if sent["nod"] in pos_nods:
                                        nexts += 1
                                        pr += nexts
                                        cur_sect["progs"] = pr
                                        nexts = 0
                                    elif sent["next"]:
                                        nexts += 1
                                    else:
                                        nexts = 0
                                if show_note == "comments":
                                    if sent["comment"] != "":
                                        sent["visible"] = True
                                    else:
                                        sent["visible"] = False
                                elif (show_note != "" and not show_note in sent["notes"]) or "remove" in sent["notes"]:
                                    sent["visible"] = False
                                elif show_note != "" and not "remove" in sent["notes"]:
                                    sent["visible"] = True

                                if not sent["visible"]:
                                    pos[fsn], _ = text_win.getyx()
                                    fsn += 1
                                    continue
                                has_sents =True

                                is_word = sent["block"] == "word"
                                is_sent = sent["block"] == "sent" and sent["type"] == "sentence"
                                if is_word:
                                    word_count += 1

                                # cur.init_pair(NOD_COLOR,back_color,cG)
                                reading_time = sent["rtime"]
                                f_color = HL_COLOR
                                hline = "-" * (width)
                                if show_reading_time:
                                    f_color = scale_color((100 - reading_time * 4), 0.1)
                                    mprint(str(reading_time), text_win, f_color)

                                     
                                text = ""
                                while sent["passable"] and fsn < frag_end:
                                    text += sent["text"] + " "
                                    fsn += 1
                                    sent = _sents[fsn - frag_offset]

                                text += sent["text"]
                                lines = textwrap.wrap(text, width - 4)
                                lines = list(filter(None, lines))
                                end = ""

                                # sent += " "*(width -2) + "\n"
                                sent_text = ""
                                sent_text = " "*(width) + "\n"
                                for line in lines:
                                    sent_text += "  "+ line.ljust(width - 4) + "  \n"
                                sent_text += " "*(width) + "\n"
                                posy, posx = text_win.getyx()
                                end = ""
                                count_sents = "count_sents" in b and b["count_sents"]
                                if is_sent:
                                    lines_count += len(lines)
                                if is_word:
                                    sent_text = sent["text"]
                                    #if count_sents: # and word_level: 
                                    #sent_text = str(sent["nod"]) + "." + sent_text
                                    end = sent["end"] if "end" in sent else "\n"
                                    if sent["eol"] or sent["eob"]:
                                       end = "\n"
                                       lines_count += 1
                                       sent_text += " "*(width - posx -len(sent_text))
                                if "type" in sent:
                                    _type = sent["type"]
                                    if _type in type_count:
                                        type_count[_type] += 1
                                    else:
                                        type_count[_type] = 1
                                    if _type != "" and _type != "sentence":
                                        if not sent["countable"]:
                                            mprint(_type + ":", text_win, theme_menu["bright-color"], end="\n")
                                        else:
                                            mprint(_type + " " + str(type_count[_type]) + ":", 
                                                    text_win, theme_menu["bright-color"], end="\n")
                                #ffff
                                if fsn >= bmark and fsn <= si and not sents[fsn]["passable"]:
                                    hl_pos = text_win.getyx()
                                    hlcolor = HL_COLOR
                                    l_color = find_color(sents, fsn)
                                    b_color = int(theme_menu["highlight-color"]) % cur.COLORS
                                    cur.init_pair(TEMP_COLOR, l_color % cur.COLORS, b_color)
                                    _color = l_color
                                    _attr = True
                                    if (_color == int(theme_menu["hl-text-color"]) or sent["hidden"]
                                        or not rc_text):
                                        _color = HL_COLOR
                                    if theme_menu["bold-highlight"] == "True":
                                        mprint(sent_text, text_win, _color, attr=_attr  | cur.A_BOLD, end=end)
                                    else:
                                        mprint(sent_text, text_win, _color, attr=_attr, end=end)
                                else:
                                    if (word_level and sent["block"] == "word" and 
                                            sent["block_id"] == sents[si]["block_id"]):
                                        _color = SEL_ITEM_COLOR
                                    elif sent["passable"]:
                                        _color = TEXT_COLOR
                                    else:
                                        _color = DIM_COLOR
                                    if sent["nod"] != "" and start_reading:
                                        _color = find_color(sents, fsn)
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
                                if True: #start_reading:
                                    for note in sent["nods"]:
                                        nn.append(note)
                                    #print_notes(text_win, nn, ypos, width + 1)
                                    color = find_nod_color(sent["nod"])
                                    if (count_sents and sent["eob"]):
                                        print_there(_y - (lines_count // 2 + 1), 
                                                1, ' ' + str(sent_count), left_side_win, color, attr=cur.A_REVERSE)
                                        sent_count += 1
                                        lines_count = 0 
                                    if ("eob" in sent and sent["eob"]): # or sent["nod"] in nods_show:
                                        if  ((not fsn >= bmark and fsn <= si)): 
                                            pass
                                        else:
                                            pass
                                            #print_there(_y + (lines_count //2 + 1), 
                                            #    2, sent["nod"], right_side_win, color)
                                        if False: #not rc_text and show_sel_nod and fsn >= bmark and fsn <= si:
                                            cur_nod = sents[fsn]["nod"]
                                            list_nods(right_side_win, _y - lines_count, cur_nod)
                                        lines_count = 0 
                                prev_sent = sent
                                text_win.move(_y, _x)
                                #ccc
                                if not sents[fsn]["passable"]:
                                    if sent["comment"] != "":
                                        comment = sent["comment"]
                                        print_comment(text_win, comment, width)
                                    empty = []
                                    filled = []
                                    for _note_type, _notes in sent["notes"].items():
                                        for _note in _notes:
                                            if ("text" in _note and _note["text"] != ""
                                                    and (not "visible" in _note or _note["visible"])):
                                                filled.append((_note_type,_note["text"]))
                                            else:
                                                empty.append((_note_type,""))
                                    note_count = 0
                                    for _note, _note_text in empty:
                                        print_there(_y - (lines_count // 2 + 2), 
                                                4+note_count, notes_keys[notes_list.index(_note)],
                                                left_side_win, TEXT_COLOR)
                                        note_count += 1
                                        lines_count = 0 
                                        _note_color = find_nod_color(_note)
                                        mprint(_note + " ", text_win, _note_color, end = "")
                                    if empty:
                                        mprint("", text_win)
                                    for _note, _note_text in filled:
                                        if _note != "instruct":
                                            _note_color = find_nod_color(_note)
                                            mprint(_note + ": ", text_win, _note_color, end = "")
                                            print_comment(text_win, _note_text, width)
                                    if filled:
                                        mprint("", text_win)
                                else:
                                    pass  # mprint("", text_win, f_color)
                                pos[fsn], _ = text_win.getyx()
                                if pos[fsn] > rows*190:
                                    too_big_art = True
                                    if not too_big_warn:
                                        too_big_warn = True
                                        show_warn("The article is too big to be displayed completely!") 
                                fsn += 1
                                new_frag = False

                        #fffe
                        if has_sents:
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
        win_info = cur.newwin(1, cols, rows - 1, 0)
        win_info.bkgd(' ', cur.color_pair(INFO_COLOR))  # | cur.A_REVERSE)
        win_info.erase()
        win_info.erase()
        if mode != "normal":
            _color = WARNING_COLOR
            mprint(" " + mode, win_info, color = _color, end = " ")
        mprint(" " + mode_info, win_info, color = INFO_COLOR, end = "")
        if start_reading:
            #print_there(0, 1, "   ", win_info, color=WARNING_COLOR)
            #print_there(0, 5, "s) stop reading", win_info, color=INFO_COLOR)
            if show_instruct:
                print_there(0, cols - 25, "l) hide insturctions", win_info, color=INFO_COLOR)
            else:
                print_there(0, cols - 25, "l) list instructions", win_info, color=INFO_COLOR)
        else:
            #print_there(0, 1, "   ", win_info, color=22, attr= cur.A_REVERSE)
            #print_there(0, 5, "s) start reading", win_info, color=INFO_COLOR)
            if show_instruct:
                print_there(0, cols - 25, "l) hide instructions", win_info, color=INFO_COLOR)
            else:
                print_there(0, cols - 25, "l) list instructions", win_info, color=INFO_COLOR)
        win_info.refresh()
        end_y, curx = text_win.getyx()
        # mark get_key

        # if ch != LEFT:
        rows, cols = std.getmaxyx()
        # width = 2*cols // 3
        left = ((cols - width) // 2) - 10
        ypos = pos[bmark] - start_row
        end_row = ypos + (pos[si] - pos[bmark]) 
        limit_row = rows - 5
        if not scroll_page and not word_level and end_row > limit_row:
            start_row -= end_row - limit_row
            scroll_page = True
        elif scroll_page:
            if end_row <= limit_row:
                scroll_page = False
        if hotkey == "":
            text_win.refresh(start_row, 0, 2, left, rows - 2, left + width)
            left_side_win.refresh(start_row, 0, 2, 0, rows - 2, left - 1)
            right_side_win.refresh(start_row, 0, 2, left + width, rows - 2, cols -1)
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
        if ch == ord('A'):
            pyperclip.copy(art["title"])
            show_msg("Title was copied to the clipboard")
        if ch == ord('a'): 
            show_msg(" Total:" + art["total_prog"] + "% | Section:" +str(cur_sect["prog"]) + "% ")
        if ch == ord('l'):
            show_instruct = not show_instruct 
            nr_opts["show instructions"] = "Enabled" if show_instruct else "Disabled"
        if show_instruct:
            cur.init_pair(TEMP_COLOR, 35, int(theme_menu["input-color"]) % cur.COLORS)
            s_win = cur.newpad(rows, cols)
            s_win.bkgd(' ', cur.color_pair(INPUT_COLOR))  # | cur.A_REVERSE)
            mprint("Instructions: l) hide".ljust(35),s_win, color=INFO_COLOR)
            for key,instruct in instructs.items():
                if not key == "intro":
                    mprint(" " + key, s_win, color=TEMP_COLOR, end = ")")
                instruct = textwrap.fill(instruct, 30)    
                mprint(" " + instruct, s_win, color=INPUT_COLOR)
            _y, x = s_win.getyx()
            s_win.refresh(0, 0, 3, cols - 35, _y + 3, cols -1)
            #s_win.refresh(0, 0, rows - len(instructs) - 3, cols - 35, rows - 1, cols -1)
        # jjj
        if jump_key == 0:
            if auto_mode:
                if si + 1 < total_sents:
                    sent_len = len(sents[si]["text"])
                    _timeout = int((sent_len**1.2)*20)
                    std.timeout(_timeout)
                    show_info("remaining time:" + str(si) + ":" + str(sent_len) + ":" + str(_timeout))
                    tmp_ch = get_key(std)
                    if tmp_ch == -1:
                        ch = RIGHT
                    else:
                        auto_mode = False
                        std.timeout(-1)
                else:
                    auto_mode = False
                    std.timeout(-1)
            else:
                ch = get_key(std)
                start_time = 0
        else:
            ch = jump_key
            jump_key = 0

        if word_level and not ch in ARROWS + [ord('v'), ord('q')] and not is_enter(ch):
            mbeep()
            show_instruct = True
            continue
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
        if ch == ord("H") or ch == ord("Q"):
            hotkey = "qq" if expand == 0 else "qqq"
        if ch == ord('F') and not rc_text:
            ypos = pos[bmark] - start_row
            nod_win = cur.newwin(9, 50, ypos + 2, left)
            nod_win.bkgd(' ', cur.color_pair(INFO_COLOR))  # | cur.A_REVERSE)
            tmp, _ = select_box({"Notes":["All"] + notes_list}, nod_win, title="Show only", in_row=True)
            show_note = tmp if tmp != "NULL" and tmp != "All" else ""
            if show_note == "":
                for _sent in sents:
                    if not "remove" in _sent["notes"]:
                        _sent["visible"] = True
                bmark = si = 0
        if ch == ord('d'):
            acc = notes_keys + ['l','o','q','d']
            _ch = confirm("Delete: Press d to see the list or choose from " + ",".join(acc),
                    acc=acc)
            if _ch == 'd':
                unset_sent(cur_sent)
            elif _ch != 'q':
                unset_sent(cur_sent, _ch)
        if ch == ord("^"):
            if len(cur_sent["nods"]) > 0:
                cur_sent["nods"].pop(0)
            elif len(cur_sent["notes"]) > 0:
                top_key = list(cur_sent["notes"].keys())[0]
                _note = cur_sent["notes"].pop(top_key)
        #dcdc
        if ch == cur.KEY_SDC:
            cur_sent["notes"] = []
            if sents[si]["nod"] != "":
                sents[si]["nod"] = ""
                if si > 0:
                    si -= 1
                    while si > 0 and (not sents[si]["visible"] or sents[si]["passable"]):
                        si -= 1
                    if bmark >= si:
                        bmark = si
                        while bmark >= 0 and sents[bmark - 1]["next"]:
                            bmark -= 1
                else:
                    mbeep()
                    si = 0
        if ch == ord('y'):
            with open(art["title"] + ".txt", "w") as f:
                print(art, file=f)
        if ch == ord('r'):
            si = 1
            text_win.erase()
            text_win.refresh(0, 0, 0, 0, rows - 2, cols - 1)
            si = total_sents - 1
            while True:
                if sents[si]["nod"]:
                    break
                si -= 1
            bmark, si = moveon(sents, si)
            expand = 1
            first = True
            for _sect in art["sections"]:
                _sect["opened"] = True
            start_reading = True

        if ch == ord('v'):
            if visual_mode:
                ch = RIGHT
            visual_mode = not visual_mode 
        if ch == ord('z'):
            # show_reading_time = not show_reading_time
            auto_mode = True  # not auto_mode

        if ch == ord('h'):  # article help
            show_info(('\n'
                       '  Down)          expand the selection to the next sentence\n'
                       '  Right)         open a collapsed section\n'
                       '  Right)         nod the selected sentences and move to the next\n'
                       '  Left)          show a list of nods\n'
                       '  Enter)         open a link, article or refrence associated to the selected sentence\n'
                       '  o)             download/open the pdf file externally\n'
                       '  f)             list figures\n'
                       '  t)             add a tag to the article\n'
                       '  w)             save the article into the saved articles\n     `'
                       '  x)             save as/export the article into a file\n'
                       '  T)             change the color theme\n'
                       '  m)             merege selected sentences\n'
                       '  u)             reset comments and notes\n'
                       '  n)             filter sentences by a note\n'
                       '  DEL)           remove the sentece or the current notes \n'
                       '  d)             a shorkey for DEL \n'
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
        if ch == ord('c'):
            if not pyperclip_imported:
                show_warn("Please install pyperclip using 'pip install pyperclip' to use clipboard functonality")
            else:
                _text = ""
                for ii in range(bmark, si+1):
                    if not is_passable(sents, ii):
                        text += sents[ii]["text"] + " " 
                pyperclip.copy(text)
                show_msg("Text was copied to clipboard...", delay=500)
        if ch == ord('w'):
            if "save_folder" in art and "/Files" in art["save_folder"]:
                ch = ord('C') # Move it to articles
            else:
                #save_article(art)
                update_article(save_article, art)
                show_msg(art["save_folder"])
        if ch == ord('W') or ch == ord('C'):
            if ch == ord('C'):
                show_info("copy from " + art["save_folder"])
                move_article(art)
            else:
                show_info("move from " + art["save_folder"])
                move_article(art, "copy")
            show_msg("to " + art["save_folder"], delay=1500)
        if ch == ord('m'):
            new_sent_text = ""
            new_sent_notes = {}
            _,m_frag,_,_ = locate(art, bmark)
            m_pos = bmark - m_frag['offset']
            for ii in range(bmark, si+1):
                if is_passable(sents, ii):
                    continue
                new_sent_text += sents[ii]["text"] + " "
                for _note,_note_val in sents[ii]["notes"]:
                    new_sent_notes[_note] = _note_val
                _,_frag,_,_ = locate(art, ii)
                _pos = ii - _frag["offset"]
                _frag["sents"][_pos]["merged"] = True

            for ii in range(bmark, si+1):
                if is_passable(sents, ii):
                    continue
                _,_frag,_,_ = locate(art, ii)
                _frag["sents"] = [sent for sent in _frag["sents"] if not "merged" in sent or not sent["merged"]] 
            si = bmark
            _new_sent = new_sent(new_sent_text)
            _new_sent["notes"] = new_sent_notes
            m_frag['sents'][m_pos:m_pos] = [_new_sent]
            old_total_sents = total_sents
            total_sects, total_frags, total_sents, sents = refresh_offsets(art)
            dif = total_sents - old_total_sents
            first = True
            if dif > 0:
                pos += [0]*dif
        if ch == ord('p'):
            for ii in range(bmark, si + 1):
                sents[ii]["passable"] = True
            bmark, si = moveon(sents, si)
        #ddd
        if ch == ord('u') or ch == cur.KEY_DC:
            if ch == cur.KEY_DC and not cur_sent["notes"]: 
                for ii in range(bmark, si + 1):
                    if not sents[ii]["notes"]:
                        sents[ii]["visible"] = False
                        sents[ii]["notes"]["remove"] = ""
                bmark, si = moveon(sents, si)
            else:
                _c = unset_sent(sents[si])
                if _c != "q" and ch == ord('u'):
                    for sent in sents[si:]:
                        unset_sent(sent, _c)
            art_changed = True

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
        #~~~
        if ch == ord('~'):
            if ch == ord('~') or (cur_sect["title"] == "Review" and cur_sect == art["sections"][0]):
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
                set_nod(cur_nod, tmp_sent, sents, bmark, si, elapsed_time)
                si,bmark = moveon(sents, si)

        if ch == ord('i'):
            ypos = pos[bmark] - start_row
            tmp_sent = cur_sent
            _notes_list = []
            for k,v in notes_dict.items():
                _notes_list.append(v + " (" + k + ")")
            n_list = {"Notes":_notes_list, "Types": art_sent_types}
            #n_list = {"Types": art_sent_types}
            _win_w = 75
            # NNN
            _y_pos = ypos + 2 if ypos + 2 < rows - 2 else rows - 10
            nod_win = cur.newwin(9, _win_w, _y_pos, left)
            nod_win.bkgd(' ', cur.color_pair(INFO_COLOR))  # | cur.A_REVERSE)
            tmp_note, note_index = select_box(n_list, nod_win, 1, in_row=True)
            if tmp_note != 'NULL':
                cur_note = tmp_note.split("(")[0].strip()
                if cur_note in art_sent_types:
                    b_ind = bmark - cur_frag["offset"]
                    cur_frag["sents"][b_ind]["type"] = cur_note
                if tmp_sent == cur_sent: 
                    for ii in range(bmark, si):
                        sents[ii]["next"] = True
                if cur_note in notes_list:
                    _ind = notes_list.index(cur_note)
                    ch = ord(notes_keys[_ind])
                art_changed = True
        if False: #chr(ch).isdigit() and False:
            try:
                index = int(chr(ch))
            except:
                index = 0
            if index < len(nods_list):
                cur_nod = nods_list[index]
                set_nod(cur_nod, cur_sent, sents, bmark, si, elapsed_time)
                if cur_note in notes_list:
                    _ind = notes_list(cur_note).index()
                    ch = ord(notes_keys[_ind])

        #www
        if is_enter(ch) and word_level and expand != 0 or (ch == ord('q') and word_level):
            if word_level:
                word_level = False
                mode = "normal"
                visual_mode = False
                if bmark <= si and rc_mode and is_enter(ch):
                    answer = ""
                    for _sent in sents[bmark:si+1]:
                        answer += _sent["text"] + " "
                    answer = answer.strip()
                    true_ans = true_answers[0]["text"]
                    correct = answer == true_ans.strip() or true_ans.strip() in answer
                    if correct:
                        sents[ref_q]["notes"]["answer"][0]["visible"] = True
                    can_pass_q = correct
                    if len(true_answers) > 1:
                        for i, ans in enumerate(true_answers[1:]):
                            true_ans += " or " + ans["text"]
                            correct = (correct or 
                                    answer == ans["text"].strip() or ans["text"].strip() in answer)
                            can_pass_q = (can_pass_q and answer == ans["text"].strip() or
                                    ans["text"].strip() in answer)
                            if correct:
                                sents[ref_q]["notes"]["answer"][i]["visible"] = True
                    if can_pass_q:
                        sents[ref_q]["can_skip"] = True
                        sents[ref_q]["nod"] = "correct" 
                        reset_q_context(context)

                    for _sent in sents[bmark:si+1]:
                         _sent["nod"] = "correct" if correct else "incorrect"
                    
                si = pass_forward(sents, bmark)
                bmark = pass_backward(sents, bmark)
                ch = 0 
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
        if visual_mode:
            if ch == RIGHT: ch = SRIGHT
            if ch == LEFT: ch = SLEFT
            if ch == UP: ch = SUP
            if ch == DOWN: ch = SDOWN
        if ch == SRIGHT:
            if forward and bmark <= si:
                si = inc_si(sents, si)
            elif not forward and bmark == si:
                forward = True
                si = inc_si(sents, si)
            elif not forward:
                bmark = inc_si(sents, bmark)
            si = min(si, total_sents - 1)
        if ch == SLEFT: 
            if forward and bmark < si:
                si = dec_si(sents, si)
            elif forward and bmark == si:
                forward = False
                bmark = dec_si(sents, bmark)
            elif not forward:
                bmark = dec_si(sents, bmark)
            si = max(si, begin_offset)
            bmark = max(bmark, begin_offset)
        if ch == SUP:
            check_eol = word_level 
            if forward and bmark <= si:
                if check_eol:
                    si = pass_backward(sents, si)
                si = dec_si(sents, si)
                if si == bmark:
                    forward = False
                elif si < bmark:
                    si = bmark
                    bmark = dec_si(sents, bmark)
                    if check_eol:
                        bmark = pass_backward(sents, bmark)
                    forward = False
            elif not forward:
                if check_eol:
                    bmark = pass_backward(sents, bmark)
                bmark = dec_si(sents, bmark)
        if ch == SDOWN: 
            check_eol = word_level
            if forward and bmark <= si:
                if check_eol:
                    si = pass_forward(sents, si )
                si = inc_si(sents, si)
            elif not forward:
                if check_eol:
                    bmark = pass_forward(sents, bmark)
                bmark = inc_si(sents, bmark)
                if bmark == si:
                    forward = True
                if bmark > si:
                    bmark = si
                    if check_eol:
                        si = pass_forward(sents, si)
                    si = inc_si(sents, si)
                    forward = True
        #kkkd
        if ch == DOWN: 
            if scroll_page:
                start_row += scroll
            elif show_sel_nod: 
                cur_nod = sents[si]["nod"]
                cur_nod = next_nod(cur_nod, ch)
                set_nod(cur_nod, cur_sent, sents, bmark, si, elapsed_time)
            else:
                nf = cur_frag["offset"] + len(cur_frag["sents"])
                ii = inc_si(sents, si)
                if word_level:
                    si = pass_forward(sents, si)
                    si = inc_si(sents, si) 
                    bmark = si
                elif (sents[si]["block_id"] < 0) and ii < nf and si < bmark:
                    si = ii 
                else:
                    prev_nod = sents[si]["nod"]
                    if prev_nod == "":
                        set_nod("okay", cur_sent, sents, bmark, si, -1)
                    if False: #prev_nod == "what?!":
                        show_msg("Press either Right or Left key to move to the next sentence")
                    else:
                        si, bmark = moveon(sents, si)

        # kkku
        if ch == UP:
            scroll_page = False
            if show_sel_nod: 
                cur_nod = sents[si]["nod"]
                cur_nod = next_nod(cur_nod, ch)
                set_nod(cur_nod, cur_sent, sents, bmark, si, -1)
            else:
                bf = cur_frag["offset"]
                ii = dec_si(sents, si)
                if word_level:
                    bmark = pass_backward(sents, bmark)
                    bmark = dec_si(sents, bmark)
                    si = bmark
                elif ii >= bf and ii >= bmark and (sents[si]["block_id"] < 0):
                    si = ii 
                else:
                    si, bmark = backoff(sents,  bmark)
        #kkkr
        if ch == RIGHT and (not rc_mode or word_level): # move next
            show_sel_nod = False
            if not rc_text and (bmark != si or sents[bmark]["block"] != "word" 
                                and sents[si]["block"] != "word"):
                prev_nod = sents[si]["nod"] 
                if prev_nod == "": prev_nod = "okay"
                if prev_nod != "what?!" and prev_nod != "okay, go on":
                    _next_nod = next_nod(prev_nod, key_pos) if not auto_mode else "okay"
                else:
                    _next_nod = "okay, go on"
                set_nod(_next_nod, cur_sent, sents, bmark, si, elapsed_time)
                for ii in range(bmark, si+1):
                    if not "okays" in sents[ii]:
                        sents[ii]["okays"] = 1
                    else:
                        sents[ii]["okays"] += 1

                up_pos = (pos[si-1] + pos[si])//2 - start_row + 2
                nod_win = cur.newwin(2,10, up_pos, left + width)
                nod_win.bkgd(' ', cur.color_pair(TEXT_COLOR))  # | cur.A_REVERSE)
                print_there(0, 
                        2, "I see!", nod_win, find_nod_color("I see!"))
                nod_win.refresh()
                std.timeout(500)
                mbeep()
                t_ch = get_key(std)
                if t_ch < 0:
                    print_there(0, 
                        2, "", nod_win, find_nod_color("I see!"))
                    nod_win.refresh()
                elif t_ch == RIGHT:
                    set_nod("interesting!", cur_sent, sents, bmark, si, elapsed_time)
                    ch = 0
                    if False:
                        set_nod(_next_nod, cur_sent, sents, bmark, si, elapsed_time)
                        si, bmark = moveon(sents, si)
                        forward = True
                else:
                    jump_key = t_ch
                std.timeout(-1)
        #kkkl
        if ch == LEFT and (not rc_text or word_level): # move previous
            if not word_level:
                if True: #not show_sel_nod:
                    #show_sel_nod = True
                    prev_nod = sents[si]["nod"] 
                    if prev_nod == "": prev_nod = "okay"
                    _next_nod = next_nod(prev_nod, key_neg) 
                    set_nod(_next_nod, cur_sent, sents, bmark, si, elapsed_time)
                #else:
                    #show_sel_nod = False
                    #si, bmark = moveon(sents, si)
                    #forward = True
                for ii in range(bmark, si+1):
                    if not "whats" in sents[ii]:
                        sents[ii]["whats"] = 1
                    else:
                        sents[ii]["whats"] += 1
                print_there((pos[si-1] + pos[si])//2, 
                    2, "what?!", right_side_win, color)
                right_side_win.refresh(start_row, 0, 2, left + width, rows - 2, cols -1)
                std.timeout(500)
                t_ch = get_key(std)
                #sound_file = art["title"][:10] + "_" + str(si) + ".mp3" 
                #speak(cur_sent["text"], sound_file) 
                #call(["ffplay", sound_file])

                if t_ch < 0:
                    std.timeout(-1)
                    set_nod("", cur_sent, sents, bmark, si, elapsed_time)
                    print_there((pos[si-1] + pos[si])//2, 
                        2, cur_sent["nod"], right_side_win, color)
                    right_side_win.refresh(start_row, 0, 2, left + width, rows - 2, cols -1)
                elif t_ch == LEFT:
                    std.timeout(-1)
                    set_nod("okay, never mind", cur_sent, sents, bmark, si, elapsed_time)
                    if False:
                        set_nod(_next_nod, cur_sent, sents, bmark, si, elapsed_time)
                        si, bmark = moveon(sents, si)
                        forward = True
        #pp#p
        if ((rc_mode and ch==RIGHT) or ch == cur.KEY_IC) and not word_level and expand != 0:
            in_sent = True
            if rc_mode and not word_level:
                in_sent = False
                _sent = sents[bmark]
                for ans in true_answers:
                   ofs = _sent["char_offset"] 
                   if "answer_start" in ans: 
                       start = ans["answer_start"] 
                       _len = len(_sent["text"])
                       if _sent["block"] == "word":
                           _len = 0
                           ii = bmark
                           while not sents[ii]["eob"]:
                               _len += len(sents[ii]['text']) + 1
                               ii += 1
                       if (start >= ofs and start < ofs + _len):
                           in_sent = True
                   else:
                        in_sent = ans["text"] in _sent["text"]
                if not in_sent:
                    mbeep()
                    _sent["nod"] = "incorrect"

            split_level = 3
            if in_sent:
                for ii in range(bmark, si +1):
                    sents[ii]["next"] = False
            si = bmark        
            is_word = sents[si]["block"] == "word"
            if in_sent and not is_word:
                word_level = True
                mode = "word level"
                _pos = si - cur_frag['offset']
                new_sents = init_frag_sents(cur_frag["sents"][_pos]["text"], 
                        split_level = split_level, block_id = si)
                cur_frag['sents'].pop(_pos)
                cur_frag['sents'][_pos:_pos] = new_sents
                old_total_sents = total_sents
                total_sects, total_frags, total_sents, sents = refresh_offsets(art)
                dif = total_sents - old_total_sents
                first = True
                if dif > 0:
                    pos += [0]*dif
            elif in_sent and is_word:
                word_level = True
            elif not in_sent and is_word:
                mbeep()
                for ii in range(bmark, si +1):
                    if sents[ii]["nod"] == "":
                        sents[ii]["nod"] = "incorrect"
                

            # std.timeout(500)
            # tmp_ch = get_key(std)
            # remove_nod = False
            # if tmp_ch == cur.KEY_DC:
            #    remove_nod = True
            # std.timeout(-1)
        #+++
        if ch == ord('*'):
            if sents[si]["nod"] in neg_nods:
                cur_nod = "OK, I get it now"
            else:
                cur_nod = next_nod(cur_nod, key_pos)
            sents[si]["nod"] = cur_nod
            sents[si]["block_id"] = si
        if ch == ord('_'):
            pass
            #cur_nod = next_nod(cur_nod, key_neg)
            #sents[si]["nod"] = cur_nod
            #sents[si]["block_id"] = si
        art_changed = art_changed or nod_set
        if si > 0 and (expand == 0 and ch == UP and not cur_sect["opened"]) or ch == cur.KEY_PPAGE:
            sel_first_sent = True
            si = cur_sect["offset"] - 1
            bmark = si
        if (expand == 0 and ch == DOWN and not cur_sect["opened"]) or ch == cur.KEY_NPAGE:
            sel_first_sent = True
            first = True
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
            if start_row < end_y:
                start_row += scroll
                scroll_page = True
            else:
                mbeep()

        if ch == ord(','):
            if start_row > 0:
                start_row -= scroll
                scroll_page = True
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
            first = True
            bmark = si

        if ch == 127 and cur_sect["opened"]:
            ch = 0
            expand = 0
            pos = [0] * total_sents
            for _sect in art["sections"]:
                _sect["opened"] = False
        elif ch == 127:
            ch = ord('q')

        elif ch == ord(']'):
            hl_index +=1
            hl_index = min(len(hl_colors)-1, hl_index)
            if theme_menu["preset"] == "default":
                theme_menu["highlight-color"] = str(int(theme_menu["highlight-color"]) - 1) 
                theme_menu["hl-text-color"] = str(int(int(theme_menu["hl-text-color"]) - 1)) 
            else:
                theme_menu["hl-text-color"] = str(int(theme_menu["hl-text-color"]) + 1) 
                theme_menu["highlight-color"] = str(int(int(theme_menu["highlight-color"]) + 1)) 
            theme_menu["highlight-color"] = str(hl_colors[hl_index][0])
            theme_menu["hl-text-color"] = str(hl_colors[hl_index][1])
            reset_hl(theme_menu)
        if ch == ord('['):
            hl_index -=1
            hl_index = max(0, hl_index)
            if theme_menu["preset"] == "default":
                theme_menu["highlight-color"] = str(int(theme_menu["highlight-color"]) + 1) 
                theme_menu["hl-text-color"] = str(int(int(theme_menu["hl-text-color"]) + 1)) 
            else:
                theme_menu["hl-text-color"] = str(int(theme_menu["hl-text-color"]) - 1) 
                theme_menu["highlight-color"] = str(int(int(theme_menu["highlight-color"]) - 1)) 
            theme_menu["highlight-color"] = str(hl_colors[hl_index][0])
            theme_menu["hl-text-color"] = str(hl_colors[hl_index][1])
            reset_hl(theme_menu)
        if ch == ord('E'):
            win_input = cur.newwin(5, cols - 2*left, 5, left)
            prompt = "Paper title"
            win_input.bkgd(' ', cur.color_pair(CUR_ITEM_COLOR))  # | cur.A_REVERSE)
            new_tit, _ch = minput(win_input, 0, 0, prompt, default= cur_sent["text"],mode = MULTI_LINE)
            if new_tit != "<ESC>":
                art["title"] = new_tit.strip()
            pdf_name = art["title"] + ".pdf"
            move_pdf(art, pdf_name, full_path=False)
        if ch == ord('o') or ch == ord('/') or ch == ord('O'):
            fname = get_path(art)
            if fname:
                if "localPdfUrl" in art and art["localPdfUrl"]:
                    url = art["localPdfUrl"]
                else:
                    url = art["pdfUrl"]
                if not download_or_open(url, art, pdf_name, open_file = (ch == ord('o') or ch == ord('/'))):
                    win_input = cur.newwin(5, cols - 2*left, 5, left)
                    prompt = "File not found, new File localtion:"
                    win_input.bkgd(' ', cur.color_pair(CUR_ITEM_COLOR))  # | cur.A_REVERSE)
                    new_loc, _ch = minput(win_input, 0, 0, prompt, mode = MULTI_LINE)
                    if new_loc != "<ESC>":
                        art["localPdfUrl"] = "file://" + new_loc.strip()
                        openFile(Path(new_loc))

                art_changed = True
                if ch == ord('O'):
                    show_info("Converting pdf to text .... Please wait")
                    text_content = extractText(pdf_fname)
                    output = fname + ".txt"
                    with open(output, "w") as text_file:
                        text_file.write(text)
                        show_msg("Pdf was converted to text, and you can open the text file")
                    data = text_content 
                    title, i = get_title(data, fname)
                    url = fname
                    url = "file://" + url
                    if i > 0:
                        data = data[i:]
                    ext_art = {"id": fname, "pdfUrl": url, "save_folder":art["save_folder"], 
                            "title": title, "sections": get_sects(data)}
                    if profile in fname:
                        ext_art["save_folder"] = art["save_folder"]
                    show_article(ext_art)
            else:
                show_info(main_info)
        if type(ch) == str and chr(ch) == '"':
            win = cur.newwin(10, width, 6, left)
            win.bkgd(' ', cur.color_pair(CUR_ITEM_COLOR))  # | cur.A_REVERSE)
            new_text, _ = minput(win, 0, 0, "New text", 
                    default="", mode =MULTI_LINE)
            cur_frag["text"] += "." + new_text
            cur_frag["sents"] += init_frag_sents(new_text, word_limit=1)
            old_total_sents = total_sents
            total_sects, total_frags, total_sents, sents = refresh_offsets(art)
            dif = total_sents - old_total_sents
            if dif > 0:
                pos += [0]*dif
            update_article(saved_articles, art)

        if chr(ch) in ['1','8','9','0','5','3'] or chr(ch) in ['!','*','(',')','=',' ',':']: #@@@
            bg_color = HL_COLOR
            win_height = 8
            note_art_title = art["title"]
            fifo = False
            mydate = datetime.datetime.now()
            if ch == ord('1') or ch == ord('!'): note_file = "ideas" 
            if ch == ord('8') or ch == ord('*'): note_file = "findings" 
            if ch == ord('8') or ch == ord(':'): note_file = "notes" 
            if ch == ord('6') or ch == ord('='): note_file = "exp" 
            if ch == ord('6') or ch == ord(' '): note_file = "questions" 
            if ch == ord('0') or ch == ord('('): note_file = "nn"
            if ch == ord('9') or ch == ord(')'): 
                note_file = "jj"
                bg_color = 12
                win_height = 3
            _idea = _comment = ""
            if note_file == "nn" or note_file == "jj" or note_file == "exp":
                month = mydate.strftime("%Y-%B-%V")
                note_art_title = month
                fifo = True
            if ch == ord('3') or ch == ord('#'):
                path = doc_path + '/Notes'  
                note_file = get_sel_name(path, "*.tag.list", "Tag")
            if note_file:
                if not note_file.endswith(".tag.list"):
                    note_file += ".tag.list"
                note_title = note_file[:-4]
                win = cur.newwin(win_height, width - 1, 6, left)
                _default = prev_idea
                win.bkgd(' ', cur.color_pair(CUR_ITEM_COLOR))  # | cur.A_REVERSE)
                _comment, ret_ch = minput(win, 0, 0, note_title, 
                        default=_default, mode =MULTI_LINE, color=bg_color)
                _idea = _comment
                if ret_ch == "=":
                    prev_idea = _idea
                else:
                    prev_idea = ""
            if _idea != "":
                _frag = {}
                _idea = mydate.strftime("%Y-%m-%d-%H-%M") + ":" +  _idea
                _frag["sents"] = init_frag_sents(_idea, word_limit=1)
                _frag["ref_art"] = art["id"]
                _frag["ref_title"] = art["title"]
                _frag["ref_sent"] = si
                _frag["time"] = str(datetime.datetime.now())
                frag_id = art["id"] + "_" + _frag["time"]
                #notes_doc = load_doc(note_file, "Notes", root =True)
                if not Path(doc_path + "/Notes/" + note_file).is_file():
                    notes_arts = []
                    _f_art = {}
                else:
                    with open(doc_path + "/Notes/" + note_file) as _file:
                        notes_arts = json.load(_file)
                    _f_art = {}
                    for _art in notes_arts:
                        if _art["title"] == note_art_title:
                            _f_art = _art
                            break
                if not _f_art:
                    _f_art = {"id": note_title + art["id"], "needs_review":False, "pdfUrl": "", "title": note_art_title, "sections":[]}
                    new_sect = {"title":"all", "fragments":[]}
                    new_sect["fragments"].append(_frag)
                    _f_art["sections"].append(new_sect)
                    #save_doc(notes_doc, note_file,"Notes", root =True)
                    notes_arts.insert(0, _f_art)
                else:
                    _f_sect = _f_art["sections"][0]
                    if not ret_ch == cur.KEY_IC or not _f_sect["fragments"]:
                        if fifo:
                            _f_sect["fragments"].insert(0, _frag)
                        else:
                            _f_sect["fragments"].append(_frag)
                    else:
                        _f_frag = _f_sect["fragments"][0]
                        _f_frag["sents"].append(new_sent(_idea))
                    #save_doc(notes_doc, note_file,"Notes", root =True)
                    show_warn("The note file was added to " + note_file, delay=100)
                with open(doc_path + '/Notes/' + note_file, 'w') as outfile:
                    json.dump(notes_arts, outfile)
                if ch == ord(':'):
                    review = art["sections"][0]["fragments"][-1]
                    review["text"] += _idea
                    review["sents"] += init_frag_sents(_comment, True, word_limit = 2, nod ="okay")
                    old_total_sents = total_sents
                    total_sects, total_frags, total_sents, sents = refresh_offsets(art)
                    dif = total_sents - old_total_sents
                    si += dif
                    bmark += dif
                    art_changed = True
                    if dif > 0:
                        pos += [0]*dif
                    update_article(saved_articles, art)
        #////
        if chr(ch) == "n" or ch == ord("n"):
            if ch == ord("n"):
                search,_ = minput(win_info, 0, 1, "/")
            _found = False
            for ii in range(si+1, len(sents)):
                if search.lower() in sents[ii]["text"].lower():
                    bmark = si = ii
                    _found = True
                    first = True
                    break
            if not _found:
                show_msg("Not found", delay=500)

        #:::
        if chr(ch) in notes_keys:
            default = cur_sent["comment"]
            prompt = "Comment:"
            note_type = notes_dict[chr(ch)]
            inp_mode = SINGLE_LINE
            _lines = 5
            if note_type != "": #and note_type in cur_sent["noets"]:
                default = "" #cur_sent["notes"][note_type]["text"]
            if chr(ch) == "-":
                prompt = "Check later (you can leave it blank)"
            elif chr(ch) == "!":
                prompt = "What is your idea?"
                inp_mode = MULTI_LINE
            elif chr(ch) == "&":
                prompt = "Answer:"
                inp_mode = MULTI_LINE
            elif chr(ch) == "?":
                prompt = "What is your question?"
            elif chr(ch) == "+":
                prompt = "You can write down the point or leave it blank"
            elif chr(ch) == "\\":
                prompt = "Any comment"
                inp_mode = MULTI_LINE
            _comment = ""
            _y_pos = ypos + 2 if ypos + 2 < rows - 2 else rows - _lines - 5
            win = cur.newwin(_lines, width-1, _y_pos, left)
            win.bkgd(' ', cur.color_pair(CUR_ITEM_COLOR))  # | cur.A_REVERSE)
            if chr(ch) not in ["+","-"]:
                _comment, _ = minput(win, 0, 0, prompt, default=default, mode=inp_mode)
            #show_info(main_info)
                _comment = _comment if _comment != "<ESC>" and _comment != "q" else cur_sent["comment"]
            art_changed = True
            if note_type == "":
                cur_sent["comment"]= _comment
            else:
                if _comment or (chr(ch) in ["+", "-"]):
                    if not note_type in cur_sent["notes"]:
                        cur_sent["notes"][note_type] = [{"text":_comment}]
                    elif _comment and not _comment in cur_sent["notes"][note_type]:
                        cur_sent["notes"][note_type].append({"text":_comment})
                    elif not _comment and chr(ch) in ["+","_"]:
                        del cur_sent["notes"][note_type]
                    cur_sent["block_id"] = si
                if chr(ch) == "+" and needs_review and False:
                    _text = ""
                    for ii in range(bmark, si +1):
                        _text += sents[ii]["text"]  + " "
                    _rev = {}
                    _rev["sents"] = init_frag_sents(_text)
                    art["sections"][0]["fragments"].append(_rev)
                update_article(saved_articles, art)


        if ch == ord('t'):
            subwins = {
                "select tag": {"x": 7, "y": 5, "h": 15, "w": 68}
            }
            choice = ''
            mi = 0
            tags_menu = {"tags (one per line)": "", "select tag": ""}
            tags_options = {"select tag":{}}
            tag_path = doc_path + "/" + profile 
            cur_tags = [str(Path(f).stem) for f in Path(tag_path).glob("*.listid") if f.is_file()]
            tags_options["select tag"]["range"] = cur_tags
            tags_options["tags (one per line)"] = {"type":"input-box-mline", "rows":12, "addto":"select tag"}
            inp_ch = 0
            while choice != 'q':
                tags = ""
                if "tags" in art:
                    for tag in art["tags"]:
                        tags += tag.replace("\n","") + ", "
                tags_menu["tags (one per line)"] = tags
                choice, tags_menu, mi = show_menu(tags_menu, tags_options,
                                                  shortkeys={"s": "select tag"},
                                                  subwins=subwins, mi=mi, title="tags", ch = inp_ch)
                if choice == "select tag":
                    new_tag = tags_menu["select tag"].strip().replace("\n","")
                    if not "tags" in art:
                        art["tags"] = [new_tag]
                    elif not new_tag in art["tags"]:
                        art["tags"].append(new_tag)
                    inp_ch = cur.KEY_ENTER
                else:
                    inp_ch = 0
                    new_tags = tags_menu["tags (one per line)"].split(",")
                    art["tags"] = []
                    for tag in new_tags:
                        tag = tag.strip().replace("\n","")
                        if tag != '' and not tag in art["tags"]:
                            art["tags"].append(tag)
                    if len(art["tags"]) > 0:
                        insert_article(saved_articles, art)
                    else:
                        remove_article(saved_articles, art)

                    save_obj(saved_articles, "saved_articles", "articles")
            for tag in art["tags"]:
                tag_file = doc_path + "/" + profile + "/" + tag + ".listid"
                if not Path(tag_file).is_file():
                    new_list = [art["id"]]
                    with open(tag_file, "w") as outfile:
                        json.dump(new_list, outfile)
                else:
                    with open(tag_file, "r") as infile:
                        artids = json.load(infile)
                    if not art["id"] in artids:
                        artids.append(art["id"])
                    with open(tag_file, "w") as outfile:
                        json.dump(artids, outfile)

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
        if ch == ord('T'):
            choice = ''
            while choice != 'q':
                choice, theme_menu, _ = show_menu(theme_menu, theme_options, title="theme")
            save_obj(theme_menu, conf["theme"], "theme")
            text_win.erase()
            text_win.refresh(0, 0, 0, 0, rows - 2, cols - 1)
# eee
        if ch == ord('q'):  # before exiting artilce
            save_obj(nr_opts, "settings", "", common = True)
            art_changed = True
            if art_changed and not collect_art:
                if not "visits" in art:
                    art["visits"] = 1
                else:
                    art["visits"] += 1
                art["last_visit"] = datetime.datetime.today().strftime('%Y-%m-%d')
                ii = 1
                begin = 1
                sect_counter = 0
                article_notes = {}
                for sect in art["sections"]:
                    ii += 1
                    frag_counter = 0
                    for frag in sect["fragments"]:
                        _frag = {"sents":[]}
                        sent_counter = 0
                        begin = sent_counter
                        for sent in frag["sents"]:
                            ii += 1
                            sent["last"] = False
                            _frag["sents"].append(sent)
                            for note in sent["notes"]:
                                if note != "" and ii > 0:
                                    _frag["ref_art"] = art_id
                                    _frag["ref_title"] = art["title"]
                                    _frag["ref_url"] = art["localPdfUrl"] if "localPdfUrl" in art else art["pdfUrl"] if "pdfUrl" in art else ""
                                    _frag["ref_sent"] = str(sect_counter) + "_" + str(frag_counter) + "_" + str(begin) + "_" + str(sent_counter) 
                                    frag_id = art_id + "_" + _frag["ref_sent"]
                                    if not note in article_notes:
                                        article_notes[note] = {art_id:{frag_id:_frag}}
                                    elif not art_id in article_notes[note]:
                                        article_notes[note][art_id] = {frag_id:_frag}
                                    elif not frag_id in article_notes[note][art_id]:
                                        article_notes[note][art_id][frag_id] = _frag
                            if sent["nod"] != "" and not sent["next"]:
                                begin = sent_counter
                                _frag = {"sents":[]}
                            sent_counter += 1
                            # end for sent 
                        frag_counter += 1
                        # end for fragments
                    sect_counter += 1
                    # end for sect
                for note in article_notes:
                    if note != "instruct":
                        append_notes(note, article_notes[note])

            sents[si]["last"] = True
            if not collect_art and needs_review:
                if "save_folder" in art:
                    save_article(art)
                else:
                    _conf = confirm("You didn't add the article to your library, press w to add it and q to quit?", acc=['w','q'])
                    if _conf == "w":
                        ch = ord('w')
                insert_article(saved_articles, art)
                save_obj(saved_articles, "saved_articles", "articles")
                last_visited = load_obj("last_visited", "articles", [])
                insert_article_list(last_visited, art)
                save_obj(last_visited, "last_visited", "articles")
    return ""

key_neg = DOWN 
key_pos = UP
def get_nod(cur_nod, ni = -1):
    nods = list(reversed(neg_nods)) + pos_nods
    top = middle = bottom = ""
    if ni < 0:
        ni = nods.index(cur_nod) if cur_nod in nods else len(neg_nods) + 1
    else:
        cur_nod = nods[ni]
    if ni < len(nods) - 1:
        top = " Up) " + nods[ni+1]
    middle = "Right) " + cur_nod
    if ni > 0:
        bottom = " Down) " + nods[ni-1]
    if cur_nod in neg_nods:
        bottom = " Down) OK, I get it now"
    return top, middle, bottom, cur_nod 

def next_nod(cur_nod, ch): 
    nods = list(reversed(neg_nods)) + pos_nods
    ni = len(neg_nods) -1 if ch == key_pos else len(neg_nods) 
    if cur_nod in nods:
        ni = nods.index(cur_nod)
    ni = ni + 1 if ch == key_pos else ni - 1
    ni = max(0, min(ni, len(nods) - 1))
    cur_nod = nods[ni]
    return cur_nod

def set_nod(cur_nod, cur_sent, sents, bmark, si, elapsed_time):
    cur_sent_length = len(cur_sent["text"].split())
    if cur_sent_length == 0:
        cur_sent_length = 0.01
    reading_time = round(elapsed_time / cur_sent_length, 2)
    #if elapsed_time < 1 and sents[si]["nod"] == "":
    #    cur_nod = "skipped"
    tries = 0
    avg = cur_sent["rtime"]
    tries = cur_sent["tries"]
    reading_time = avg + 1 / tries * (reading_time - avg)

    cur_sent["tries"] += 1
    cur_sent["rtime"] = reading_time
    for ii in range(bmark, si + 1):
        if ii < si:
            sents[ii]["next"] = True
            sents[ii]["eob"] = False
            sents[ii]["block_id"] = si
            sents[ii]["nod"] = cur_nod
        if cur_nod == "remove":
            sents[ii]["visible"] = False
    sents[si]["next"] = False
    sents[si]["eob"] = True
    sents[si]["block_id"] = si
    if sents[si]["visible"]:  # and (sents[si]["nod"] == "" or nod_set):
        cur_sent["nod"] = cur_nod
        if not cur_nod in cur_sent["nods"]:
            cur_sent["nods"].insert(0, cur_nod)
        else:
            #cur_sent["nods"].remove(cur_nod)
            cur_sent["nods"].insert(0, cur_nod)

def is_passable(sents, si):
    cond = not sents[si]["visible"] or sents[si]["passable"]
    return cond

def can_pass(sents, si, cond = False):
    pass_words = not word_level
    total_sents = len(sents)
    cond1 = si < total_sents - 1 
    if not cond1:
        return False
    cond2 = sents[si]["next"] 
    cond3 = not sents[si]["visible"] or sents[si]["passable"]
    cond4 = pass_words and sents[si]["block"]=="word" and not sents[si]["eob"]
    return cond1 and (cond2 or cond3 or cond4 or cond)

def inc_si(sents, si):
    pass_words = not word_level
    total_sents = len(sents)
    if si == total_sents - 1:
        return si
    if word_level and (sents[si + 1]["block"] != "word" or sents[si +1]["block_id"] != sents[si]["block_id"]):
        mbeep()
        return si
    si += 1
    while si < total_sents - 1 and (not sents[si]["visible"] 
           or sents[si]["passable"] 
           or (pass_words and sents[si]["block"]=="word" and not sents[si]["eob"])):
        si += 1
    return si

def dec_si(sents, si):
    pass_words = not word_level
    total_sents = len(sents)
    if word_level and (sents[si - 1]["block"] != "word" or sents[si-1]["block_id"] != sents[si]["block_id"]):
        mbeep()
        return si
    si -= 1
    while si > 1 and (not sents[si]["visible"] 
           or sents[si]["passable"] 
           or (pass_words and sents[si]["block"]=="word" and not sents[si]["eob"])):
        si -= 1
    return si

def pass_forward(sents, ii):
    if word_level:
        while not sents[ii]["eol"] and sents[ii]["block"] == "word":
            jj = inc_si(sents,ii)
            if jj == ii: break
            ii = jj
    else:
        while can_pass(sents, ii):
            ii = inc_si(sents, ii)
    return ii

def pass_backward(sents,i):
    if i <= 0:
        return 0
    ii = dec_si(sents,i)
    if word_level:
        while not sents[ii]["eol"] and sents[ii]["block"] == "word":
            jj = dec_si(sents, ii)
            if jj == ii: break
            ii = jj
    else:
        while ii > 1 and can_pass(sents, ii):
            ii = dec_si(sents, ii)
    ii += 1
    while ii < len(sents) and (not sents[ii]["visible"] or sents[ii]["passable"]):
        ii += 1
    return ii 

def moveon(sents, i):
    ii = inc_si(sents, i)
    if ii > len(sents) -1:
        mbeep()
        return i, i
    elif ii == len(sents) - 1:
        if not is_passable(sents, ii):
            return ii, ii
    if not word_level:
        si = pass_forward(sents, ii)
        bmark = pass_backward(sents, si)
    else:
        bmark = si = ii
    return si, bmark

def backoff(sents, i):
    ii = dec_si(sents, i)
    if not word_level:
        bmark = pass_backward(sents, ii)
        si = pass_forward(sents, bmark)
    else:
        bmark = si = ii
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
def refresh_menu(menu, menu_win, sel, options, shortkeys, subwins, start_row=0, horiz=False, active_sel=True, pad=True, title= ""):
    global clG
    menu_win.erase()
    mprint("", menu_win)

    mprint(" " * 5 + title, menu_win, color=TEXT_COLOR)
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
        if "button-hidden" in str(v):
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
            if k.endswith(".art"):
                color = int(theme_menu["title-color"])
            if k.endswith(".artid"):
                color = int(theme_menu["I see!"])
            elif ".list" in k:
                color = int(theme_menu["text-color"])
            elif k.endswith(".txt"):
                color = int(theme_menu["interesting!"])
            elif k.endswith(".txt.pdf") or k.endswith(".art.pdf"):
                color = int(theme_menu["dim-color"])
            elif k.endswith(".pdf"):
                color = int(theme_menu["bright-color"])
        fw = cur.A_BOLD
        if "button-light" in str(v):
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
            if "color" in k or (k in options and "range" in options[k] and options[k]["range"] == colors):
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
            si = options[k]['range'].index(menu[k]) if k in menu and menu[k] in options else -1
            sub_menu_win.bkgd(' ', cur.color_pair(TEXT_COLOR))  # | cur.A_REVERSE)
            show_submenu(sub_menu_win, options[k]['range'], si, active_sel=False)


def get_sel(menu, mi):
    mi = max(mi, 0)
    mi = min(mi, len(menu) - 1)
    return list(menu)[mi], mi


win_info = None


def confirm_all(msg):
    return confirm(msg, acc=['y', 'n', 'a'])


def confirm(msg, acc=['y', 'n'], color=WARNING_COLOR, list_opts=True, bottom = True):
    mbeep()
    if list_opts:
        msg = msg + " (" + "/".join(acc) + ")"
    if not bottom:
        ch = show_info(msg, color, bottom, title="Confirm", acc=acc)
    else:
        show_info(msg, color)
        ch = 0
        while chr(ch).lower() not in acc:
            ch = std.getch()
            if not chr(ch).lower() in acc:
                mbeep()
            else:
                break
        ch = chr(ch).lower()
    show_info(old_msg)
    return ch

old_msg = ''
def show_info(msg, color=INFO_COLOR, bottom=True, title = "Info", acc =[]):
    global win_info, old_msg
    rows, cols = std.getmaxyx()
    if bottom:
        old_msg = msg
        win_info = cur.newwin(1, cols, rows - 1, 0)
        win_info.bkgd(' ', cur.color_pair(color))  # | cur.A_REVERSE)
        win_info.erase()
        msg = msg.replace("\n","")
        if len(msg) > cols - 15:
            msg = msg[:(cols - 16)] + "..."
        print_there(0, 1, " {} ".format(msg), win_info, color)
        win_info.clrtoeol()
        win_info.refresh()
    else:
        mcols = 2*cols//3 - 2
        nlines = 0
        for line in msg.splitlines():
            wrap = textwrap.wrap(line,mcols, break_long_words=False,replace_whitespace=False)
            nlines += len(wrap)
        nlines += 1
        mrows = nlines + 2
        footer =  "q: Close "
        top = (rows - 5 - nlines)//2
        if nlines > rows - 5:
            top = 2
            footer += "; Up/Down: Scroll the message"
            mrows = rows - 5
        footer = textwrap.shorten(footer, mcols)
        mwin = cur.newwin(mrows, mcols, top, cols //6)
        mwin.bkgd(' ', cur.color_pair(HL_COLOR))  # | cur.A_REVERSE)
        mwin.border()
        print_there(0, 1, title, mwin)
        print_there(mrows-1, 1, footer, mwin)
        mwin.refresh()
        win_info = cur.newpad(rows * 2, (2 * cols // 3) - 2)
        win_info.bkgd(' ', cur.color_pair(color))  # | cur.A_REVERSE)
        win_info.erase()
        left = cols // 6 + 1
        start_row = 0
        ch = 0
        while ch != ord('q'):
            win_info.erase()
            # msg = textwrap.indent(textwrap.fill(msg),'  ')
            mprint(msg, win_info, color)
            start_row = max(start_row, 0)
            start_row = min(start_row, 2 * rows)
            win_info.refresh(start_row, 0, top + 1, left, top + mrows - 2, left + mcols - 3)
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
            elif not chr(ch).lower() in acc + [ord('q')]:
                mbeep()
            else:
                return chr(ch).lower()


def show_msg(msg, color=MSG_COLOR, delay=2000):
    temp = old_msg
    mbeep()
    show_info(msg, color)
    if delay > 0:
        std.timeout(delay)
        std.getch()
        std.timeout(-1)
        show_info(temp)
    else:
        std.getch()


def show_warn(msg, color=WARNING_COLOR, bottom=True, stop=True, delay=3000):
    if bottom:
        msg += "; press any key..."
        temp = old_msg
    show_info(msg, color, bottom)
    ch = ''
    if bottom and stop:
        if delay > 0:
            std.timeout(delay)
            ch = std.getch()
            std.timeout(-1)
            show_info(temp)
        else:
            ch = std.getch()
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
        text = {"preset": "md", "top": "", "title": "# {title}", "section-title": "## {section-title}",
                "paragraph": "{paragraph}{newline}{newline}", "bottom": "{url}"}
        html = {"preset": "html", "top": "<!DOCTYPE html>{newline}<html>{newline}<body>", "title": "<h1>{title}</h1>",
                "section-title": "<h2>{section-title}</h2>", "paragraph": "<p>{paragraph}</p>",
                "bottom": "<p>source:{url}</p></body>{newline}</html>"}
        for mm in [text, html]:
            mm["save as"] = "button"
            options["paragraph"] = {"type":"input-box-mline", "rows":12}
            options["section-title"] = {"type":"input-box-mline", "rows":12}
            mm["reset"] = "button"
        save_obj(text, "txt", folder, common =True)
        save_obj(html, "html", folder, common =True)
        new_preset = "txt"

    menu = load_obj(new_preset, folder, common =True)
    menu["preset"] = new_preset
    menu_dir = user_data_dir(appname, appauthor) + "/" + folder
    saved_presets = [Path(f).stem for f in Path(menu_dir).glob('*') if f.is_file()]
    options["preset"]["range"] = saved_presets

    if folder == "theme":
        for k in menu:
            if k.endswith("-color"):
                options[k] = {'range':colors}
        for k in feedbacks:
            options[k] = {"range":colors}
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
        v = v.strip().replace("\n","")
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
def show_menu(menu, options, shortkeys={}, hotkeys={}, title="", mi=0, subwins={}, info="h) help | q) quit", ch = 0):
    global menu_win, common_subwin, hotkey

    rows, cols = std.getmaxyx()
    height = rows - 1
    width = cols
    key_set = ch != 0

    for opt in menu:
        if opt in options and "range" in options[opt] and menu[opt] == "":
            menu[opt] = options[opt]["range"][0] if options[opt]["range"] else ""

    if info.startswith("error"):
        show_err(info)
    else:
        for k, v in hotkeys.items():
            info += " | " + k + ") " + v
        info += "  (case sensitive)"
        show_info(info)

    #mprint(title.center(rows), menu_win, TITLE_COLOR)
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
    while ch != ord('q') and ch != ord('Q'):
        sel, mi = get_sel(menu, mi)
        is_hidden = "-hidden" in menu[sel] 
        if sel in options and "type" in options[sel]:
            sel_type = options[sel]["type"]
        elif str(menu[sel]).startswith("button"):
            sel_type = "button"
        elif sel.startswith("sep"):
            sel_type = "sep"
        elif sel in options and "range" in options[sel]:
            sel_type = "select"
        else:
            sel_type = "input-box"
        passable_item = sel_type == 'sep' or is_hidden
        sub_menu_win = common_subwin
        cmd = ""
        start_row = 0
        if row + start_row + mi >= 3 * rows - 2:
            start_row = 3 * (rows - 2) - 2 
        if row + start_row + mi >= 2 * rows - 2:
            start_row = 2 * (rows - 2) -2
        elif row + start_row + mi >= rows - 1:
            start_row = rows - 2
        refresh_menu(menu, menu_win, sel, options, shortkeys, subwins, start_row, active_sel = True, title=title)
        if edit_mode and sel_type.startswith("input-box"):
            cur_val = menu[sel]
            _m = max([len(x) for x in menu.keys()]) + 5
            mode = PROMPT_LINE
            if sel_type.startswith("input-box-mline"):
                win_input = cur.newwin(options[sel]["rows"], cols - 10, row + mi, col)
                mode = MULTI_LINE
                prompt = sel
                cur_values = "\n".join([x.strip() for x in menu[sel].split(',')])
            elif sel_type == "input-box-sline":
                _rows = options[sel]["rows"] if "rows" in options[sel] else 4 
                win_input = cur.newwin(_rows, cols - 10, row + mi, col)
                mode = SINGLE_LINE
                prompt = sel
                cur_values = menu[sel]
            else:
                win_input = cur.newwin(1, cols - 10, row + mi, col)
                prompt = "{:<{}}".format(sel, _m) + ": "
                cur_values = menu[sel]
            win_input.bkgd(' ', cur.color_pair(CUR_ITEM_COLOR))  # | cur.A_REVERSE)
            val, ch = minput(win_input, 0, 0, prompt,  default=cur_values, mode = mode)
            if val != "<ESC>":
                if sel in options and "addto" in options[sel] and val.strip() != "":
                    addto_list = options[sel]["addto"]
                    new_tags = val.split("\n")
                    new_tags = list(filter(None, new_tags))
                    for tag in new_tags:
                        tag = tag.strip().replace("\n","")
                        if tag != '' and not tag in options[addto_list]:
                            options[addto_list]["range"].append(tag)
                val = val.replace("\n",",")
                val = textwrap.fill(val, width=cols - 12)
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
            ret_mi = max(0, min(mi, len(menu) - 1))
            return sel, menu, ret_mi 
        if sel in subwins:
            if menu[sel] in options[sel]['range']:
                si = options[sel]['range'].index(menu[sel])
            rows, cols = std.getmaxyx()
            sub_menu_win = cur.newwin(subwins[sel]["h"],
                                      subwins[sel]["w"],
                                      subwins[sel]["y"],
                                      subwins[sel]["x"])
            sub_menu_win.bkgd(' ', cur.color_pair(TEXT_COLOR))  # | cur.A_REVERSE)
        if (not passable_item and not key_set) or hotkey != "":
            prev_ch = ch
            if title.startswith("Checkideh") and hotkey == "q":
                hotkey = ""
            ch = get_key(std)
        elif passable_item and mi == 0:
            ch = DOWN
        elif passable_item and mi == len(menu) - 1:
            ch = UP
        if ch == cur.KEY_RESIZE:
            mbeep()
            refresh_menu(menu, menu_win, sel, options, shortkeys, subwins, start_row, title=title)
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
            elif sel_type.startswith("input-box"):
                edit_mode = True
            elif sel_type == "select" or sel_type == "combo-box":
                si = 0
                if menu[sel] in options[sel]['range']:
                    si = options[sel]["range"].index(menu[sel])
                if "preset" in menu:
                    last_preset = menu["preset"]
                refresh_menu(menu, menu_win, sel, options, shortkeys, subwins, start_row, active_sel = False, title=title)
                si, canceled, st = open_submenu(sub_menu_win, options, sel, si, title)
                if not canceled:
                    is_combo = sel_type == "combo-box"
                    if is_combo:
                        if not str(options[sel]['range'][si]).lower().startswith(st.lower()):
                            options[sel]['range'].insert(0, st)
                            si = 0
                        else:
                            sep_index = options[sel]['range'].index("---")
                            cur_item = options[sel]['range'][si]
                            if si < sep_index:
                                options[sel]['range'].pop(si)
                            options[sel]['range'].insert(0, cur_item)
                            si = 0
                    menu[sel] = options[sel]['range'][si]
                    if "preset" in menu and sel != "preset":
                        if title == "theme":
                            reset_colors(menu)
                        save_obj(menu, menu["preset"], title, common =True)
                    if sel == "preset":
                        save_obj(menu, last_preset, title, common =True)
                        new_preset = menu[sel]
                        menu, options = load_preset(new_preset, options, title)
                        last_preset = new_preset
                        refresh_menu(menu, menu_win, sel, options, shortkeys, subwins, start_row, title=title)
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
            if not title.startswith("Checkideh"):
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
                if not fname in options["preset"]['range']:
                    options["preset"]['range'].append(fname)
                last_preset = fname
                refresh_menu(menu, menu_win, sel, options, shortkeys, subwins, start_row, title=title)
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
        elif ch == ord('q') and title.startswith("Checkideh"):
            pass
            #show_info("Hit q again to exit the program.")
            #_confirm = confirm("you want to exit the program")
            #if _confirm != "y":
            #    ch = 0
        key_set = False # End_While
    return chr(ch), menu, mi

def open_submenu(sub_menu_win, options, sel, si, title):
    ch = 0
    st = ""
    back_st = ""
    prev_si = si
    cancel = False
    temp_msg = old_msg
    is_combo = "type" in options[sel] and options[sel]["type"] == "combo-box"
    sel_range = options[sel]["range"]
    info = "Enter/Right: select | qq/ESC/Left: cancel "    
    if sel == "preset" or is_combo:
        info += " | Del: delete an item"

    show_info(info)
    while not is_enter(ch) and not ch == RIGHT:
        if ch == UP:
            if si == 0:
                si = prev_si
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
            si = len(sel_range) - 1
        elif ch == LEFT or ch == 27 or (back_st.lower() == "q" and chr(ch) == "q"):
            si = prev_si
            cancel = True
            break
        elif ch == cur.KEY_DC:
            can_delete = True
            if sel == "preset" and len(sel_range) == 1 or sel_range[si] == "default":
                show_warn("You can't delete the default " + title)
                can_delete = False
            elif is_combo:
                sep_index = sel_range.index("---")
                if si > sep_index:
                    show_warn("You can't remove predefined profiles which appear below separate line (---)")
                    can_delete = False
            if can_delete:
                item = sel_range[si]
                _confirm = confirm("Are you sure you want to delete '" + item)
                if _confirm == "y" or _confirm == "a":
                    del_obj(item, title, common = True)
                if item in sel_range:
                    sel_range.remove(item)
                    if si > len(sel_range):
                        si = len(sel_range) 
                    if is_combo and "list-file" in sel_range:
                        save_obj(sel_range["range"], sel_range["list-file"], "", common = True)
        elif ch != 0:
            if ch == 127 or ch == cur.KEY_BACKSPACE:
                st = st[:-1]
                back_st = back_st[:-1]
                si, st = find(sel_range, st, "", si)
            if chr(ch).lower() in string.printable:
                back_st += chr(ch)
                si, new_st = find(sel_range, st, chr(ch), si)
                if not is_combo:
                    if st == new_st:
                        mbeep()
                    else:
                        st = new_st
                else:
                    st += chr(ch)
        si = min(si, len(sel_range) - 1)
        si = max(si, 0)
        sub_menu_win.erase()
        searchable = is_combo or len(sel_range) > 8
        show_submenu(sub_menu_win, sel_range, si, search=searchable)
        if is_combo: 
            show_cursor()
            mprint("Search or Add:" + st, sub_menu_win, end ="")
        elif len(sel_range) > 8:
            show_cursor()
            mprint("Search:" + st, sub_menu_win, end ="")
        sub_menu_win.refresh()
        ch = get_key(std)

    si = min(si, len(sel_range) - 1)
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
    global colors, template_menu, template_options, theme_options, theme_menu, std, conf, query, filters, top_win, hotkey, menu_win, list_win, common_subwin, text_win, left_side_win,right_side_win, profile, cur_articles

    std = stdscr
    stdscr.refresh()
    now = datetime.datetime.now()
    logging.info(f"========================= Starting program at {now}")
    # logging.info(f"curses colors: {cur.COLORS}")

    rows, cols = std.getmaxyx()
    height = rows - 1
    width = cols
    # mouse = cur.mousemask(cur.ALL_MOUSE_EVENTS)
    list_win = cur.newpad(rows*2, cols - 1)
    list_win.bkgd(' ', cur.color_pair(TEXT_COLOR))  # | cur.A_REVERSE)
    text_win = cur.newpad(rows * 200, cols - 1)
    text_win.bkgd(' ', cur.color_pair(TEXT_COLOR))  # | cur.A_REVERSE)
    left_side_win = cur.newpad(rows * 200, (cols - text_width) //2)
    left_side_win.bkgd(' ', cur.color_pair(ITEM_COLOR))  # | cur.A_REVERSE)
    right_side_win = cur.newpad(rows * 200, text_width//2)
    right_side_win.bkgd(' ', cur.color_pair(ITEM_COLOR))  # | cur.A_REVERSE)
    menu_win = cur.newpad(rows*20 , cols*2)
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
            menu["recent articles"] = "button-hidden"
        menu["notes"] = "button"
        menu["open file"] = "button"
        menu["my articles"] = "button"
        menu["sepb1"] = ""
        menu["sep1"] = "Search AI-related papers"
        if is_obj("last_results", ""):
            menu["last results"] = "button"
        else:
            menu["last results"] = "button-hidden"
        menu["task"] = prev_menu["task"]
        menu["keywords"] = prev_menu["keywords"]
        menu["Go!"] = "button"
        menu["advanced search"] = "button"
        if newspaper_imported:
            menu["sepb2"] = ""
            menu["sep2"] = "Load website articles"
            menu["website articles"] = "button"
            menu["webpage"] = "button"
        menu["settings"] = "button"

    options = {
        # "recent articles":["None"],
        "task": {"range":["All", "Reading Comprehension", "Machine Reading Comprehension", "Sentiment Analysis",
                 "Question Answering", "Transfer Learning", "Natural Language Inference", "Computer Vision",
                 "Machine Translation", "Text Classification", "Decision Making"]},
        profile_str: {"range":["---", "Computer Vision", "Image Recognition", "Speech Recognition", "Dialog Systems", "Information Retrieval", "Reinforcement Learning", "Reading Comprehension",
                 "Question Answering", "Knowledge Graph", "Text Generation", "Transfer Learning", "Natural Language Inference","Machine Translation", "Sentiment Analysis", "Text Classification", "Decision Making"]},
    }


    menu[profile_str] = profile
    conf = load_obj("conf", "", common = True)
    options[profile_str]['type'] = 'combo-box'
    options[profile_str]['list-file'] = 'profiles'
    profiles = load_obj("profiles","", common = True)
    if not profiles is None:
       options[profile_str]['range'] = profiles
    else:
       save_obj(options[profile_str]['range'], "profiles", "", common = True)
    task_file = Path('tasks.txt')
    if task_file.is_file():
        with open('tasks.txt', 'r') as f:
            options["task"]['range'] = ["All"] +  [t.strip() for t in f.readlines()]
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
         "preset": {'range':[]},
         "inverse-highlight":{'range':["True", "False"]},
         "bold-highlight":{'range': ["True", "False"]},
         "bold-text":{'range':["True", "False"]},
    }

    for k in feedbacks:
        theme_options[k] = {'range':colors}
    theme_menu, theme_options = load_preset(conf["theme"], theme_options, "theme")
    template_menu, template_options = load_preset(conf["template"], template_options, "template")

    ver_file = Path('version.txt')
    version = ""
    if ver_file.is_file():
        with open("version.txt", 'r') as f:
            version = f.readline()

    main_title = "Checkideh " + version
    reset_colors(theme_menu)
    # os.environ.setdefault('ESCDELAY', '25')
    # ESCDELAY = 25
    std.bkgd(' ', cur.color_pair(TEXT_COLOR))  # | cur.A_REVERSE)
    clear_screen(std)
    top_win = cur.newwin(2, cols, 1, 0)
    top_win.bkgd(' ', cur.color_pair(TEXT_COLOR))  # | cur.A_REVERSE)
    ch = ''
    shortkeys = {"m": "my articles", "l": "last results", "k": "keywords", "n": "notes", "r": "recent articles", "g":"Go!", "t": "tags", "s": "settings", "p": "webpage", "a": "advanced search", "w": "website articles", 'o': "open file"}
    mi = 0
    while ch != 'q':
        info = "h) help         q) quit"
        show_info(info)
        ch, menu, mi = show_menu(menu, options, shortkeys=shortkeys, mi=mi, subwins=subwins, title=main_title,
                hotkeys={"R": "resume last article", "c": "Clear saved articles"})
        save_obj(menu, "main_menu", "")
        if ch == "R":
            hotkey = "rrr"
        if ch == 'c':
            del_obj("last_visited", "articles")
            del_obj("saved_articles", "articles")
            mi = 0
        if ch == "advanced search":
            search()
        elif ch == profile_str:
            profile = menu[profile_str]
            conf["profile"] = profile
            save_obj(conf, "conf", "", common = True)
            save_obj(options[profile_str]["range"], "profiles", "", common = True)
        elif ch == "m" or ch == "my articles":
            save_folder = doc_path + '/' + profile
            Path(save_folder).mkdir(parents=True, exist_ok=True)
            cur_articles = load_docs("", ['.art'])
            show_files(save_folder, exts=["*.list", "*.listid","*.artid", "*.pdf", "*.txt", '*.art', '*.html'])
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
                       '                                              \n'
                       f'  Checkideh  {version}                       \n'
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

        elif ch == 'n' or ch == "notes":
            save_folder = doc_path + "/Notes"
            Path(save_folder).mkdir(parents=True, exist_ok=True)
            show_files(save_folder, exts=['*.txt','*.artid','*.art',"*.listid", '*.list','*.tag.art'], extract=True)
        elif ch == 'o' or ch == "open file":
            save_folder = doc_path + "/" +  profile + '/Files'
            Path(save_folder).mkdir(parents=True, exist_ok=True)
            show_files(save_folder, exts=['*.txt', '*.artid', "*.listid", '*.art','*.pdf','*.list','*.json','*.squad','*.prc'], extract=True)
        last_visited = load_obj("last_visited", "articles", [])
        if len(last_visited) > 0:
            menu["recent articles"] = "button"
        elif len(last_visited) == 0:
            menu["recent articles"] = "button-hidden"
        if is_obj("last_results", ""):
            menu["last results"] = "button"
        else:
            menu["last results"] = "button-hidden"
        if ch in menu and menu[ch] == "button-hidden":
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
def refresh_files(save_folder, subfolders, files, depth=1):
    menu = {}
    menu[".."] = "button"
    menu["back home"] = "button"
    menu["explore"] = "button"
    menu["tags"] = "button"
    menu["new article"] = "button"
    menu["refresh"] = "button-hidden"
    _folder = save_folder
    if len(_folder) > 80 or depth > 1:
        _folder = "/".join(_folder.split("/")[-2:])
        _folder = "[<] " + _folder
        menu[_folder] = "button@parent"  
    else:
        menu["sep1"] = _folder
    menu_len = len(menu)
    mydate = datetime.datetime.today()
    today = mydate.strftime("%Y-%m-%d")
    d = mydate - datetime.timedelta(days=1)
    yesterday = d.strftime("%Y-%m-%d")
    if True: #not save_folder.endswith("Files"):
        for ind, sf in enumerate(subfolders):
            if sf.endswith(today) or sf.endswith(yesterday):
                menu["[>] " + sf] = "button@folder@" + str(ind)
    count = 1
    sk = {'q':"..", 'e':"explore", 'h':'back home', 'n':'new article', 't':'tags'}
    rows, cols = std.getmaxyx()
    for ind, f in enumerate(files):
        name = Path(f).name
        if len(name) > cols:
            name = name[:cols] + "..." + name.split(".",1)[1] 
        sk[str(count)] = name
        menu[name] = "button-light@file@" + str(ind)
        count += 1
    if True: #save_folder.endswith("Files"):
        for ind, sf in enumerate(subfolders):
            menu["[>] " + sf] = "button@folder@" + str(ind)
    return menu, sk, menu_len


# ttt
def show_files(save_folder, exts, depth = 1, title ="My Articles", extract = False):
    global hotkey
    options = {}
    menu =[]
    mi = 6
    menu_len = 0
    ch = 'refresh'
    while ch != 'q':
        if ch == "r" or ch == "refresh":
            #clear_screen(std)
            subfolders = [f.name for f in os.scandir(save_folder) if f.is_dir()]
            subfolders = sorted(subfolders)
            if save_folder.endswith("Files"):
                subfolders = reversed(subfolders)
            files = []
            for ext in exts:
                _files = [str(Path(f)) for f in Path(save_folder).glob(ext) if f.is_file()]
                files.extend(_files)
                #files = sorted(files)
                files.sort(key=os.path.getctime, reverse=True)
                #files = []
                #for str_file in _files:
                #    _file = Path(str_file)
                #    mtime = datetime.datetime.fromtimestamp(_file.stat().st_ctime)
                #    past = datetime.datetime.now() - datetime.timedelta(days=1)
                #    if mtime > past: 
                #        files.extend(_file)
            menu, sk, menu_len = refresh_files(save_folder, subfolders, files, depth)
            mi = menu_len

        ch, menu, mi = show_menu(menu, options, mi=mi, hotkeys = {'r':'refresh','c':'convert options', 'o':'open externally'}, shortkeys = sk, title=title)
        if ch.startswith("[>"):
            sfolder = save_folder + "/" + ch[4:]
            show_files(sfolder, exts, depth + 1)
        elif ch == ".." or ch.startswith("[<]"):
            ch = 'q'
        elif ch == "tags":
            list_tags(save_folder)
        elif (ch == "back home" or ch == "H" or ch == 'h'):
            if depth >= 1:
                hotkey = 'q'*(depth - 1)
            else:
                mbeep()
        elif ch == "new folder":
            filepath = save_folder + "/"+menu["new folder"] 
            ch = "refresh"
        elif ch == "new article" or ch == "explore":
            filepath = save_folder 
            if ch == "new article":
                name = "new article"
                filepath = save_folder + "/"+ name + ".txt"
                count = 1
                while Path(filepath).is_file():
                    name = "new article (" + str(count) + ")"
                    filepath = save_folder +  "/"+ name + ".txt"
                    count += 1
                with open(filepath, "w") as f:
                    print("Write your text file here, rename it and save, then refresh", file = f)
            platform_open(filepath)
            ch = "refresh"
        elif "del@" in ch:
            parts = ch.split("@")
            _confirm = ""
            if parts[2] == "file":
                index = int(parts[3]) 
                filepath = files[index]
                ext = os.path.splitext(filepath)[1]
                fname = filepath.split("/")[-1]
                _confirm = confirm("Are you sure you want to delete "+fname)
                if _confirm == "y":
                    if ext == ".artid":
                        _file = open(filepath, "r")
                        artid = _file.read().strip()
                        remove_saved_article(artid)
                        _file.close()
                    Path(filepath).unlink()
            else:
                index = int(parts[3])
                filepath = save_folder + "/" + subfolders[index]
                fname = filepath.split("/")[-1]
                is_empty = not any(Path(filepath).iterdir())
                if not is_empty:
                    show_msg("The folder " + fname + " is not empty and can't be deleted!")
                else:
                    _confirm = confirm("Are you sure you want to delete "+fname)
                if _confirm == "y":
                    Path(filepath).rmdir()

            ch = "refresh"
        elif ch != "q" and (len(ch) > 1 or ch in ["c", "o"]) and ch != "refresh":
            mval = list(menu.values())[mi]
            parts = mval.split("@")
            index = int(parts[2]) 
            filename = files[index]
            ext = os.path.splitext(filename)[1]
            name = os.path.basename(filename)
            name_without_ext = name.split('.')[0]
            _file = open(filename, "r")
            data = ""
            #sqq
            extract = ch == "c" or not Path(filename + ".txt").is_file()
            if ch == "o" or (ext == ".pdf" and not extract):
                openFile(filename)
            elif ext == ".pdf" and extract:
                show_info("Converting to text ... Please wait...(Ctrl + C to cancel)")
                mydate = datetime.datetime.now()
                create_date = mydate.strftime("%Y-%m-%d")
                save_pdf_folder = doc_path + "/" + profile + "/Files/" + create_date
                Path(save_pdf_folder).mkdir(parents=True, exist_ok=True)
                pages = "all"
                if not save_folder.endswith("Files"):
                    save_pdf_folder = save_folder
                output = save_pdf_folder + "/" + name + ".txt"
                if ch == "c":
                    text, pages, sel_sects = extractPdfText(filename)
                    if text == "":
                        continue
                    if pages != "all" and pages != "":
                        output =  save_pdf_folder + "/(partial) " + name[:25] + "..._pages_" + pages + sel_sects[:2] + ".pdf.txt"
                else:
                    try:
                        text = extractText(filename)
                    except KeyboardInterrupt:
                        show_info("convert canceled")
                        continue
                    #text = convert_pdf_to_txt(filename)
                pdf_file = filename
                if save_folder.endswith("Files"):
                    pdf_file = save_pdf_folder + "/" + name 
                    shutil.move(filename, pdf_file)
                text = pdf_file + "\n" + pages + "\n" + text
                with open(output, "w") as text_file:
                    text_file.write(text)
                show_msg("Pdf was converted to text, and you can open the text file")
                if save_folder.endswith("Files"):
                    show_files(save_pdf_folder, exts, depth + 1)
                else:
                    save_folder = save_pdf_folder
                ch = "refresh"
            elif ext == ".txt":
                data = _file.read()
                _file.close()
                url = filename
                pages = "all"
                if url.endswith("pdf.txt"):
                    _lines = data.split('\n', 2)
                    _url = _lines[0]
                    url = "file://" + _url
                    pages = _lines[1]
                    data = _lines[2]
                title, i = get_title(data, name)
                if pages != "all":
                    title = pages + title
                if i > 0:
                    data = data[i:]
                    
                mydate = datetime.datetime.now()
                create_date = mydate.strftime("%Y-%m-%d")
                art = {"id": filename,  "localPdfUrl": url, "save_folder":save_folder, 
                        "title": title, "sections": get_sects(data)}
                art["create_date"] = create_date 
                if profile in filename:
                    art["save_folder"] = save_folder
                Path(filename).unlink()
                fname = get_path(art)
                if fname:
                    saved_articles = load_obj("saved_articles", "articles", {})
                    insert_article(saved_articles, art)
                    save_obj(saved_articles, "saved_articles", "articles")
                    with open(fname + ".artid", 'w') as outfile:
                        outfile.write(art["id"])
                show_article(art)
            elif ext == ".json" or ext == ".list":
                arts = json.load(_file)
                group = filename
                if "Tags/" in filename:
                    group = "tags"
                list_articles(arts, fid = name, group=group)
            elif ext == ".listid":
                artids = json.load(_file)
                group = filename
                list_artids(artids, fid=name, group=group)

            elif ext == ".artid":
                art_id = _file.read()
                saved_articles = load_obj("saved_articles", "articles", {})
                if not art_id in saved_articles:
                    show_err("Article wasn't found")
                else:
                    show_article(saved_articles[art_id])
            elif ext == ".art":
                art = json.load(_file)
                collect_art = "Notes/" in filename
                art["save_folder"] = save_folder
                show_article(art, collect_art=collect_art)
            elif ext == ".prc":
                show_info("Openning ...  Please wait...")
                jlist = list(_file)
                data = [json.loads(jline) for jline in jlist]
                arts = []
                for i, part in enumerate(data):
                    art = {}
                    if type(part['url']) == str:
                        up = urllib.parse.unquote(part['url'])
                        title = up.split('/')[-1]
                    else:
                        title = "None " + str(i)
                    art["needs_review"] = False
                    art["rc_text"] = True
                    art["title"] = title
                    art["id"] = "parsinlu-v-1-part-" + str(i)
                    art["pdfUrl"] = "na"
                    k = 1
                    c_sect = {}
                    c_sect["title"] = "Context" 
                    c_sect["count_sents"]=True
                    c_sect["can_skip"] = False
                    c_frag = {}
                    c_frag["sents"] = init_frag_sents(part["passage"], block_id = 0)
                    c_sect["fragments"] = [c_frag] 
                    q_sect = {"fragments":[]}
                    q_sect["title"] = "Reading Comprehension"
                    instruct = "Find and highlight the answers to the following questions in the given text. Follow the instructions that appears in the instruction window."
                    first_frag = {"title":"Instruction"}
                    first_frag["sents"] = init_frag_sents(instruct, unit_sep="\n", cohesive=True)
                    for s in first_frag["sents"]:
                        s["passable"] = True
                    q_sect["fragments"].append(first_frag)
                    q_frag = {"title":"Question", "sents":[]}
                    sent = new_sent(part['question'])
                    sent['type'] = "question"
                    sent['nod'] = "okay?"
                    sent['block_id'] = i
                    sent['can_skip'] = False
                    sent['hidden'] = True
                    sent['countable'] = True
                    #sent['is_impossible'] = qa['is_impossible']
                    for ans in part["answers"]:
                        note = {"text":ans}
                        note["visible"]=False
                        if not "answer" in sent["notes"]:
                            sent["notes"]["answer"] = [note]
                        else:
                            sent["notes"]["answer"].append(note)
                    q_frag["sents"].append(sent)
                    q_sect["fragments"].append(q_frag)
                    sections = []
                    sections.append(q_sect)
                    sections.append(c_sect)
                    art["sections"] = sections
                    arts.append(art)
                with open(save_folder + '/parsinlu-rc.json', 'w') as outfile:
                    json.dump(arts, outfile)
                list_articles(arts, "ParsiNlu Reading Comprehension")
            elif ext == ".squad":
                show_info("Openning ...  Please wait...")
                squad = json.load(_file)
                version = squad['version']
                fid = "SQUAD " + version
                data = squad['data']
                arts = []
                for i, part in enumerate(data[:3]):
                    art = {}
                    art["needs_review"] = False
                    art["rc_text"] = True
                    art["title"] = part["title"]
                    art["id"] = "squad-v-" + version + '-part-' + str(i)
                    art["pdfUrl"] = "na"
                    sections = []
                    k = 1
                    for j, p in enumerate(part["paragraphs"]):
                        c_sect = {}
                        c_sect["title"] = "Context" 
                        c_sect["count_sents"]=True
                        c_sect["can_skip"] = False
                        c_frag = {}
                        c_frag["sents"] = init_frag_sents(p["context"], block_id = 0)
                        for ss in c_frag["sents"]:
                            ss["hidden"] = True
                        c_sect["fragments"] = [c_frag] 
                        q_sect = {"fragments":[]}
                        q_sect["title"] = "Reading Comprehension"
                        #q_sect["count_sents"] = True
                        #instruct = """
                        #    The answer to the following questions is a span of the given text. To find them, navigate to each question, and follow the given instructions.
                        #    Please note that some questions cannot be answered by the given text and you must specify them as 'impossible to answer'. 
                        #"""
                        instruct = "Find and highlight the answers to the following questions in the given text. Follow the instructions that appears in the instruction window."
                        first_frag = {"title":"Instruction"}
                        first_frag["sents"] = init_frag_sents(instruct, unit_sep="\n", cohesive=True)
                        for s in first_frag["sents"]:
                            s["passable"] = True
                        q_sect["fragments"].append(first_frag)
                        q_frag = {"title":"Questions (" + str(len(p['qas'])) + " questions)","sents":[]}
                        for i, qa in enumerate(p['qas']):
                            sent = new_sent(qa['question'])
                            sent['type'] = "question"
                            sent['nod'] = "okay?"
                            sent['block_id'] = i
                            sent['can_skip'] = False
                            sent['hidden'] = True
                            sent['countable'] = True
                            sent['is_impossible'] = qa['is_impossible']
                            if qa['is_impossible']:
                                sent["notes"]["answer"] = [{"text":"Impossible to answer based on the text"}]
                            else:
                                for ans in qa["answers"]:
                                    note = ans.copy()
                                    note["visible"]=False
                                    if not "answer" in sent["notes"]:
                                        sent["notes"]["answer"] = [note]
                                    else:
                                        sent["notes"]["answer"].append(note)
                            q_frag["sents"].append(sent)

                        q_sect["fragments"].append(q_frag)
                        sections.append(q_sect)
                        sections.append(c_sect)
                        if j >= 0 and (j + 1) % 1 == 0:
                            art["title"] = part["title"] + " (" + str(k) + "-" + str(j+1) + ")"
                            art["id"] = "squad-v-" + version + '-part-' + str(i) + "-" + str(j)
                            art["pdfUrl"] = "na"
                            art["needs_review"] = False
                            art["rc_text"] = True
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
            ch = "refresh"

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

cur_articles = {}
def append_notes(note, arts):
    n_art = load_doc(note + ".art","Notes",{})
    if not n_art:
        n_art = {"id":note, "title": note ,"pdfUrl":"na", "sections":[]}
        new_sect = {"title":"all", "fragments":[]}
        n_art["sections"].append(new_sect)
    else:
        new_sect = n_art["sections"][-1]
    frags = new_sect["fragments"]
    frag_ids = {}
    for frag in frags:
        if "id" in frag:
            frag_ids[frag["id"]] = frag

    old_art_id = 0
    for art_id, frags_dict in arts.items():
        if art_id in cur_articles:
            avail = " [Enter to open]"
        else:
            avail = " [Not available]"
        for frag_id, frag in frags_dict.items():
            if frag_id in frag_ids:
                continue
            title = frag["ref_title"]
            title = title if art_id != old_art_id else "Same article"
            old_art_id = art_id
            ref = new_sent("[Ref] " + title + avail)
            ref["passable"] = "True"
            frag["id"] = frag_id
            frag["sents"].append(ref)
            frags.insert(0, frag)
    frags[-1]["end_mark"] = "True"

    save_doc(n_art, note + ".art", "Notes")

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

def refresh_tags(save_folder):
    saved_articles = load_docs_path(save_folder, [".art"])
    art_num = {}
    art_list = {}
    tag_list = []
    for art in saved_articles:
        if not "tags" in art:
            continue
        for tag in art["tags"]:
            tag = tag.strip().replace("\n"," ")
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
        fname = tag.ljust(40) + "(" + str(art_num[tag]) + ")"
        opts.append(fname)

    return opts, art_list

def list_tags(save_folder):
    tag_win = cur.newwin(10, 60, 2, 5)
    tag_win.bkgd(' ', cur.color_pair(HL_COLOR))  # | cur.A_REVERSE)
    tag_win.border()
    opts, art_list = refresh_tags(save_folder)
    ti, _ = select_box({"Tags":opts}, tag_win, 0, in_row=False, border=True, ret_index =True)

    if ti >= 0:
        articles = list(art_list.values())[ti]
        if len(articles) > 0:
            ret = list_articles(articles, opts[ti], group = "tags")

def list_tags2(save_folder):
    subwins = {
            "tags":{"x":7,"y":5,"h":15,"w":68},
            }
    choice = ''
    opts = {"tags":{}}
    opts["tags"]["range"], art_list = refresh_tags(save_folder)
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
            opts["tags"]["range"], art_list = refresh_tags(save_folder)
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
                    uri = urlib.parse.urlparse(site_addr)
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
    options["address"] = {"type":"input-box-sline", "rows":5}
    recent_pages = load_obj("recent_pages", "articles",[])
    arts = []
    for art in recent_pages:
        uri = urllib.parse.urlparse(art["pdfUrl"])
        name = "(" + uri.netloc + ") " + art["title"]
        arts.append(name)
    options["recent pages"] = {"range":arts}
    subwins = {} #{"recent pages": {"x": 12, "y": 7, "h": 10, "w": 68}}

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
            if url:
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
        if ch == "recent pages":
            si = options["recent pages"]["range"].index(menu["recent pages"])
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
        options = {}
        options["year"] = {}
        options["task"] = {}
        options["conference"] = {}
        options["dataset"] = {}
        options["year"]['range'] = ["All"] + [str(y) for y in range(now.year, 2010, -1)]
        options["task"]['range'] =  ["All", "Reading Comprehension", "Machine Reading Comprehension", "Sentiment Analysis","Question Answering", "Transfer Learning", "Natural Language Inference", "Computer Vision",
                 "Machine Translation", "Text Classification", "Decision Making"]
        options["conference"]["range"] = ["All", "Arxiv", "ACL", "Workshops", "EMNLP", "IJCNLP", "NAACL", "LERC", "CL", "COLING", "BEA"]
        options["dataset"]["range"] = ["All", "SQuAD", "RACE", "Social Media", "TriviaQA", "SNLI", "GLUE", "Image Net", "MS Marco", "TREC","News QA"]

    task_file = Path('tasks.txt')
    if task_file.is_file():
        with open('tasks.txt', 'r') as f:
            options["task"]["range"] = ["All"] + [t.strip() for t in f.readlines()]
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
