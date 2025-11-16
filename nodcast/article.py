from nodcast.util.nlp_utils import *
import json
import yaml
from pathlib import Path

def new_sent(s):
    _new_sent = {"text":s,"type":"sentence", "end":'\n','eol':False, 'eob':False, 'eos':False, 'next':False, "block":"sent", "merged":False, "questions":[], "q_index":0, "block_id":-1, "nod":"", "countable":False, "visible":True, "hidden":False, 'can_skip':True, "passable":False, "nods":{}, "user_nods":[], "rtime":0, "tries":1, "comment":"", "notes":{}}
    if len(s.split(' ')) <= 1:
        _new_sent["end"] = " "
    return _new_sent

split_levels = [['\n'],['.','?','!'], ['.','?','!',';'], ['.','?','!',';', ' ', ',', '-']]
text_width = 60
#iii
def init_frag_sents(text, cohesive =False, unit_sep = "", word_limit = 20, nod = "", split_level = 1, block_id=-1, merge=False):
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
            if merge:
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
            if False: #cohesive:
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
    for idx, sect in enumerate(art["sections"]):
        sect["index"] = idx
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
                sent["index"] = ii
                sents.append(sent)
                ofs += len(sent["text"])
                ii += 1
        sect["fragments"] = [x for x in sect["fragments"] if x["sents"]]
        fn += len(sect["fragments"])
    sect["sents_num"] = ii - prev_sect["offset"]
    return len(art["sections"]),fn, ii, sents

def fix_article(art, split_level=1, use_default_nod = False):
    """
    Restore and normalize the article dictionary using the old schema.
    Compatible with existing init_frag_sents(), refresh_offsets(), and new_sent().
    Also cleans '@' from nods and sets default nods + meta info for each sentence.
    """
    # --- root-level defaults ---
    art.setdefault("title", "Untitled")
    art.setdefault("id", "")
    art.setdefault("author", "")
    art.setdefault("created", "")
    art.setdefault("modified", "")
    art.setdefault("meta", {})
    art.setdefault("sections", [])
    art.setdefault("summary", "")
    art.setdefault("intro", "")
    art.setdefault("save_folder", "")
    art.setdefault("version", 1)

    # --- ensure each section is well-formed ---
    for si, sect in enumerate(art["sections"]):
        sect.setdefault("title", f"Section {si+1}")
        sect.setdefault("offset", 0)
        sect.setdefault("sents_num", 0)
        sect.setdefault("fragments", [])
        sect.setdefault("notes", {})
        sect.setdefault("progs", 0)
        sect.setdefault("visible", True)
        sect.setdefault("hidden", False)
        sect.setdefault("expanded", True)

        # --- ensure each fragment is well-formed ---
        for fi, frag in enumerate(sect["fragments"]):
            # frag.setdefault("title", f"Fragment {fi+1}")
            frag.setdefault("offset", 0)
            frag.setdefault("text", "")
            frag.setdefault("notes", {})
            frag.setdefault("visible", True)
            frag.setdefault("hidden", False)
            frag.setdefault("merged", False)
            frag.setdefault("nod", "")
            frag.setdefault("block_id", fi)
            frag.setdefault("countable", False)
            frag.setdefault("passable", False)

            # rebuild sents if missing or inconsistent
            if "sents" not in frag or not frag["sents"]:
                frag["sents"] = init_frag_sents(
                    frag["text"],
                    split_level=split_level,
                    block_id=frag["block_id"],
                )
            else:
                # ensure each sentence follows current schema
                new_sents = []
                for s in frag["sents"]:
                    if isinstance(s, str):
                        s = new_sent(s)
                    else:
                        for k, v in new_sent("").items():
                            if k not in s:
                                s[k] = v
                        if len(s.get("text", "").split(" ")) <= 1:
                            s["end"] = " "
                    new_sents.append(s)
                frag["sents"] = new_sents

            # --- NEW BLOCK: Normalize nods and add meta info ---
            for sent in frag["sents"]:
                # Detect and clean '@' from nods
                if not "questions" in sent:
                    sent["questions"] = []
                if sent["questions"]:
                    default_question = sent["questions"][0]
                    cleaned = []
                    q_index = 0
                    for i, q in enumerate(sent["questions"]):
                        if q.startswith("@"):
                            q_index = i
                            default_question = q.lstrip("@")
                            cleaned.append(default_question)
                        else:
                            cleaned.append(q)
                    sent["default_question"] = default_question
                    sent["q_index"] = q_index
                    sent["questions"] = cleaned

                if "nods" in sent:
                    default_nod = ""
                    sent_nods = sent["nods"]
                    if not sent["nods"]:
                        sent["nods"] = {
                            "affirmative":["I see!"],
                            "reflective": ["didn't get"]
                        }

                    if isinstance(sent_nods, dict):
                        for key in ("affirmative", "reflective"):
                            if key in sent_nods:
                                cleaned = []
                                for n in sent_nods[key]:
                                    if isinstance(n, str) and n.startswith("@"):
                                        default_nod = n.lstrip("@")
                                        cleaned.append(default_nod)
                                    else:
                                        n = n.lstrip("@")
                                        cleaned.append(n)
                                sent_nods[key] = cleaned
                    elif isinstance(sent_nods, list):
                        cleaned = []
                        for n in sent_nods:
                            if isinstance(n, str) and n.startswith("@"):
                                default_nod = n.lstrip("@")
                                cleaned.append(default_nod)
                            else:
                                n = n.lstrip("@")
                                cleaned.append(n)
                        sent["nods"] = cleaned

                    # If '@' was found, mark it as default nod
                    # sent["nods"]["affirmative"].insert(0,"okay")
                    # sent["nod"] = "okay"
                    sent["default_nod"] = default_nod
                    if default_nod: # and use_default_nod:
                        sent["nod"] = default_nod

                # Attach per-sentence metadata
                if "meta" not in sent:
                    sent["meta"] = {}

                sent["meta"].update({
                    "word_count": len(sent["text"].split()),
                    "char_count": len(sent["text"]),
                    "section": sect["title"],
                    "fragment": frag.get("title", f"Fragment {fi+1}"),
                })
            # --- END NEW BLOCK ---

    # --- update offsets for navigation compatibility ---
    try:
        refresh_offsets(art, split_level=split_level)
    except Exception as e:
        print("Warning: refresh_offsets failed during fix_article:", e)
    # --- ensure dummy "end" fragment exists ---
    end_sent = new_sent("end")
    end_sent["nods"] = { 
    "reflective": [
        "gave me something to think about", 
        "thought-provoking piece",
        "a bit complex but worth it",
    ],
    "affirmative": [
        "interesting article",
        "learned something new",
        "gave me something to think about",
        "clear and well explained",
        "nice conclusion",
        "makes sense overall",
        "left me curious",
        "good summary",
    ]}
    end_frag = {
        "offset": 0,
        "text": "end",
        "notes": {},
        "visible": True,
        "hidden": False,
        "merged": False,
        "nod": "",
        "block_id": 99999,
        "countable": False,
        "passable": False,
        "sents": [end_sent]
    }

    if not art["sections"] or art["sections"][-1].get("title", "").lower() != "end":
        # create a minimal dummy section if no sections exist
        art["sections"].append({
            "title": "End",
            "offset": 0,
            "sents_num": 1,
            "fragments": [end_frag],
            "notes": {},
            "progs": 0,
            "visible": True,
            "hidden": False,
            "expanded": True
        })
    else:
        last_sect = art["sections"][-1]
        # avoid duplication if a dummy end already exists
        last_texts = [f["text"].strip().lower() for f in last_sect.get("fragments", [])]
        last_title = last_sect["title"].lower()
        if "end" not in last_title:
            last_sect["fragments"].append(end_frag)
            last_sect["sents_num"] += 1

    # --- update offsets again to include the dummy end ---
    try:
        refresh_offsets(art, split_level=split_level)
    except Exception as e:
        print("Warning: refresh_offsets failed after adding end fragment:", e)

    return art


def save_article(art, artid=False, minimal=False, use_yaml=True):
    """
    Save an article file.
    Supports JSON or YAML output depending on `use_yaml` or file extension.
    If minimal=True, only essential content fields are saved.
    """
    fname = art.get("path")
    if not fname:
        raise ValueError("Article missing 'path' field")

    # Auto-switch to YAML if file extension suggests it
    ext = Path(fname).suffix.lower()
    if ext in [".yaml", ".yml"]:
        use_yaml = True
    elif ext == ".json":
        use_yaml = False

    # Optional: write ID file
    if artid and Path(fname + ".nctid").is_file():
        with open(fname + ".nctid", 'w', encoding='utf-8') as outfile:
            outfile.write(art["id"])

    # --- Minimal (compact) version ---
    if minimal:
        minimal_art = {
            "title": art.get("title", ""),
            "sections": [],
        }

        for section in art.get("sections", []):
            min_section = {"title": section.get("title", ""), "fragments": []}

            for frag in section.get("fragments", []):
                min_frag = {"id": frag.get("id", ""), "sents": []}

                for s in frag.get("sents", []):
                    text = s.get("text", "")
                    nods = s.get("nods", {}) or []
                    questions = s.get("questions", []) or []
                    q_index = s.get("q_index", 0)
                    selected_nod = s.get("nod", "")

                    # ---- encode questions with '@' marker ----
                    q_encoded = [
                        f"@{q}" if i == q_index else q
                        for i, q in enumerate(questions)
                    ]

                    # ---- encode nods with '@' marker ----
                    if isinstance(nods, dict):
                        encoded_nods = {
                            key: [
                                f"@{n}" if n == selected_nod else n
                                for n in vals if isinstance(n, str)
                            ]
                            for key, vals in nods.items()
                            if isinstance(vals, list)
                        }
                    elif isinstance(nods, list):
                        encoded_nods = [
                            f"@{n}" if n == selected_nod else n
                            for n in nods if isinstance(n, str)
                        ]
                    else:
                        encoded_nods = nods

                    min_sent = {
                        "id": s.get("id", ""),
                        "text": text,
                        "nods": encoded_nods,
                        "questions": q_encoded,
                    }

                    min_frag["sents"].append(min_sent)

                min_section["fragments"].append(min_frag)
            minimal_art["sections"].append(min_section)

        art_to_save = minimal_art
    else:
        art_to_save = art

    # --- Save to disk ---
    with open(fname, 'w', encoding='utf-8') as outfile:
        if use_yaml:
            yaml.safe_dump(art_to_save, outfile, allow_unicode=True, sort_keys=False)
        else:
            json.dump(art_to_save, outfile, indent=2, ensure_ascii=False)


def read_article(filename, ext=None):
    """
    Read an article file (JSON or YAML).
    Automatically detects format from extension if not provided.
    """
    ext = ext or Path(filename).suffix.lower()

    with open(filename, 'r', encoding='utf-8') as infile:
        if ext in [".yaml", ".yml", ".nct"]:
            art = yaml.safe_load(infile)
        else:
            art = json.load(infile)

    if art is None: return None
    art["save_folder"] = filename
    art["path"] = filename
    art = fix_article(art)
    return art


