from nodcast.util.nlp_utils import *

def new_sent(s):
    _new_sent = {"text":s,"type":"sentence", "end":'\n','eol':False, 'eob':False, 'eos':False, 'next':False, "block":"sent", "merged":False, "block_id":-1, "nod":"", "countable":False, "visible":True, "hidden":False, 'can_skip':True, "passable":False, "nods":[], "user_nods":[], "rtime":0, "tries":1, "comment":"", "notes":{}}
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

def fix_article(art, split_level=1):
    """
    Restore and normalize the article dictionary using the old schema.
    Compatible with existing init_frag_sents(), refresh_offsets(), and new_sent().
    Also cleans '@' from nods and sets default nods + meta info for each sentence.
    """
    # --- root-level defaults ---
    art.setdefault("title", "Untitled")
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
                if "nods" in sent:
                    default_nod = None
                    sent_nods = sent["nods"]

                    if isinstance(sent_nods, dict):
                        for key in ("affirmative", "reflective"):
                            if key in sent_nods:
                                cleaned = []
                                for n in sent_nods[key]:
                                    if isinstance(n, str) and n.startswith("@"):
                                        default_nod = n.lstrip("@")
                                        cleaned.append(default_nod)
                                    else:
                                        cleaned.append(n)
                                sent_nods[key] = cleaned
                    elif isinstance(sent_nods, list):
                        cleaned = []
                        for n in sent_nods:
                            if isinstance(n, str) and n.startswith("@"):
                                default_nod = n.lstrip("@")
                                cleaned.append(default_nod)
                            else:
                                cleaned.append(n)
                        sent["nods"] = cleaned

                    # If '@' was found, mark it as default nod
                    if default_nod:
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

    return art

