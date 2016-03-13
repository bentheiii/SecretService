import re
from ControlService import Control,silent_invariant_raw_input, silent_invariant_print
from HelpSource import *
from packagedata import Version
from itertools import chain
import textwrap
class CommandType:
    code = 0
    def __init__(self,prefixes,description,usage=None,mindescription=None, delegate=lambda (c,p,d):(CommandService.notimplerr_return_code,"implementation not inserted"),long_description=None):
        usage = [] if usage is None else usage
        self.code = CommandType.code
        CommandType.code += 1
        self.prefixes = prefixes
        self.description = description
        self.usage = usage
        self.delegate = delegate
        descind = self.description.find(" ")
        descind = len(self.description) if descind  <= 0 else descind
        self.mindescription = self.description[:descind] if mindescription is None else mindescription
        self.longdescription = self.short_describe() if long_description is None else long_description
    def short_describe(self):
        if len(self.usage) == 0:
            return self.min_describe()
        return "{} {}- {}".format(self.prefixes[0]," ".join(self.usage),self.description)
    def use_describe(self):
        if len(self.usage) == 0:
            return "{{{}}}- {}".format("|".join(self.prefixes),self.description)
        return "{{{}}} {}- {}".format("|".join(self.prefixes)," ".join(self.usage),self.description)
    def long_describe(self):
        pref = self.use_describe()
        wrapper = textwrap.TextWrapper(width=getTerminalSize()[0],initial_indent=4*" ",subsequent_indent=4*" ")
        return Colors.UNDERLINE+pref+":\n"+Colors.ENDC+wrapper.fill(self.longdescription)
    def min_describe(self):
        return "{}- {}".format(self.prefixes[0],self.mindescription)
def comm_batch(params,dictionary):
    try:
        bfile = open(params.get_first_or_ask("Batch Script File"),"r")
    except Exception as e:
        return CommandService.ioerr_return_code,"can't open file, {}".format(str(e))
    tempsilent = Control.silent
    Control.silent = True
    r = LineReader(bfile.readlines())
    bfile.close()
    no, line = r.get_line()
    code,response = -1,""
    while not (line is None):
        code, response = CommandService.process_command(line,dictionary,lambda x,c,t:r.get_line()[1])
        if code < 0:
            code, response = CommandService.batcherr_return_code, "error on line {}: {}".format(no,response)
            break
        no, line = r.get_line()
    Control.silent = tempsilent
    if line is None:
        return CommandService.success_return_code,"script completed without errors"
    return code,response
def comm_insert(params,dictionary):
    key = params.get_first_or_ask("Key")
    if CommandService.is_invalid_key(key):
        return CommandService.error_return_code, "key invalid"
    if key in dictionary:
        return CommandService.error_return_code, "key already exists"
    value = params.get_first_or_ask("Value")
    if CommandService.is_invalid_value(value):
        return CommandService.error_return_code, "value invalid"
    dictionary[key] = value
    Control.changed = True
    return CommandService.success_return_code, "value of '{}' set to be '{}'".format(key,value)
def comm_edit(params,dictionary):
    key = params.get_first_or_ask("Key",tab=dictionary.keys())
    key = CommandService.get_approximate_key(key, dictionary)
    if key is None:
        return CommandService.error_return_code, "key not found"
    oldval = dictionary[key]
    value = params.get_first_or_ask("Value",comp=oldval)
    if CommandService.is_invalid_value(value):
        return CommandService.error_return_code, "new value invalid"
    dictionary[key] = value
    Control.changed = True
    return CommandService.success_return_code, "value of '{}' changed from '{}' to '{}'".format(key,oldval,value)
def comm_delete(params,dictionary):
    key = params.get_first_or_ask("Key",tab=dictionary.keys())
    key = CommandService.get_approximate_key(key, dictionary)
    if key is None:
        return CommandService.error_return_code, "key not found"
    dictionary.pop(key)
    Control.changed = True
    return CommandService.success_return_code, "entry '{}' deleted".format(key)
def comm_batchdel(params,dictionary):
    confirm = True
    query = params.get_first_or_ask("Regex or Approximation Query")
    if query.startswith("!!!"):
        confirm = False
        query = query[3:]
    res,todelete = CommandService.query(query,dictionary)
    if not res == 0:
        return res, todelete
    if len(todelete) == 0:
        return CommandService.success_return_code, "no results found"
    while confirm:
        response = silent_invariant_raw_input("About to delete {} eneries, (c)ontinue, (a)bort, (d)isplay\n".format(len(todelete)),color=Colors.BOLD+Colors.UNDERLINE)
        if response == "c":
            confirm = False
        elif response == "a":
            return CommandService.success_return_code, "deletion aborted"
        elif response == "d":
            silent_invariant_print("\n".join(map(lambda  a: Colors.BOLD+Colors.WARNING+a+": "+Colors.OKGREEN+dictionary[a], todelete)))
        else:
            return CommandService.unclear_return_code, "unclear response"
    Control.changed = True
    for k in todelete:
        dictionary.pop(k)
    return CommandService.success_return_code, "{} entries deleted".format(len(todelete))
def comm_rename(params,dictionary):
    oldkey = params.get_first_or_ask("Old Key",tab=dictionary.keys())
    oldkey = CommandService.get_approximate_key(oldkey, dictionary)
    if oldkey is None:
        return CommandService.error_return_code, "key not found"
    newkey = params.get_first_or_ask("New Key",comp=oldkey)
    if CommandService.is_invalid_key(newkey):
        return CommandService.error_return_code, "key invalid"
    if newkey in dictionary:
        return CommandService.error_return_code, "key already exists"
    dictionary[newkey] = dictionary[oldkey]
    dictionary.pop(oldkey)
    Control.changed = True
    return CommandService.success_return_code, "'{}' renamed to '{}'".format(oldkey,newkey)
def comm_find(params,dictionary):
    query = params.get_first_or_ask("Regex or Approximation Query")
    res, toprint = CommandService.query(query,dictionary)
    if not res == 0:
        return res, toprint
    return CommandService.success_return_code, (str(len(toprint))+" Results:\n"+"\n".join(map(lambda  a: Colors.BOLD+Colors.WARNING+a+": "+Colors.OKGREEN+dictionary[a], toprint)) if len(toprint) > 0 else "no results")
def comm_exit(params,dictionary):
    mode = params.get_first_or_ask("'Save (s) or Discard (d) changes?\n",default=(None if Control.changed else "d"))
    if mode.lower() in ["d","no","discard","wipe","forget"]:
        return CommandService.exit_discard_return_code, "your changes will not be saved"
    if mode.lower() in ["s","yes","save","remember"]:
        return CommandService.exit_save_return_code, "your changes will be saved"
    return CommandService.unclear_return_code, "response unclear"
def comm_help(params,dictionary):
    comname = params.get_first_or_ask("Command name, alias or entry (or 'all' for all)",default="all",tab= \
        chain(chain(map(lambda x:x.prefixes,CommandService.implemented_types)),chain(map(lambda x:x.descriptors,Helptxt.help_enteries))))
    if comname == "all":
        return CommandService.help_return_code, "\n" + "\n".join(map(lambda x:x.long_describe(), CommandService.implemented_types)) \
            +("\n"*3) + "\n".join(map(lambda x:x.description(), Helptxt.help_enteries))
    t = CommandService.get_type(comname)
    if not t is None:
        return CommandService.help_return_code, t.long_describe()
    t = filter(lambda x:comname in x.descriptors,Helptxt.help_enteries)
    if len(t) > 0:
        return CommandService.help_return_code, t[0].description()
    return CommandService.unclear_return_code, "'{}' is not a command name, alias or entry".format(comname)
def comm_clear(params,dictionary):
    return CommandService.clear_return_code, ""
def comm_search(params,dictionary):
    query = params.get_first_or_ask("Regex or Approximation Query")
    res, toprint = CommandService.valuequery(query,dictionary)
    if not res == 0:
        return res, toprint
    return CommandService.success_return_code, (str(len(toprint))+" Results:\n"+"\n".join(map(lambda  a: Colors.BOLD+Colors.WARNING+a+": "+Colors.OKGREEN+dictionary[a], toprint)) if len(toprint) > 0 else "no results")
def comm_ask(params,dictionary):
    t = params.get_first_or_ask("'get definition (dfn), count key matches (cnt), count value matches (val), or echo (ech)?")
    cntm = ["count","cnt","c"]
    cvalm = list(map(lambda x:x+"val",cntm))+list(map(lambda x:x+"v",cntm))+["v","val"]
    ret = None
    if t in ["def","dfn","define","definition","d"]:
        key = params.get_first_or_ask("Key",tab=dictionary.keys())
        key = CommandService.get_approximate_key(key,dictionary)
        if key is None:
            return CommandService.error_return_code, "key not found"
        ret = dictionary[key]
    elif t in cntm+cvalm:
        query = params.get_first_or_ask("Regex or Approximation query")
        out, ret = CommandService.query(query,dictionary) if t in cntm else CommandService.valuequery(query,dictionary)
        if not out == 0:
            return out, ret
        ret = len(ret)
    elif t in ["Echo","echo","ech","e","const"]:
        val = params.get_first_or_ask("Enter Value to Echo")
        if val in ["True"]:
            val = True
        elif val in ["False"]:
            val = False
        else:
            try:
                val = int(val)
            except ValueError:
                pass
        ret = val
    else:
        return CommandService.unclear_return_code, "ask type unclear"
    Control.ask = ret
    return CommandService.ask_return_code,str(ret)
def comm_cond(params,dictionary):
    if Control.ask is None:
        return CommandService.error_return_code, "No previous ask."
    validcomps = ["==","!="]
    if type(Control.ask) is int:
        validcomps+=[">","<",">=","<="]
    if type(Control.ask) is bool:
        validcomps+=["|","&"]
    comp = params.get_first_or_ask("Enter comparison ({})".format("|".join(validcomps)))
    if not comp in validcomps:
        return CommandService.error_return_code, "Invalid comparison for type"
    val = params.get_first_or_ask("Enter compared value")
    try:
        if type(Control.ask) is int:
            val = int(val)
        elif type(Control.ask) is bool:
            if val in ["true","True","t","T"]:
                val = True
            elif val in ["false","False","f","F"]:
                val = False
            else:
                raise ValueError
    except ValueError:
        return CommandService.error_return_code,"cannot evaluate compared value {}".format(val)
    if comp == "==":
        ret = (Control.ask == val)
    elif comp == "!=":
        ret = (Control.ask != val)
    elif comp == ">":
        ret = (Control.ask > val)
    elif comp == "<":
        ret = (Control.ask < val)
    elif comp == ">=":
        ret = (Control.ask >= val)
    elif comp == "<=":
        ret = (Control.ask <= val)
    elif comp == "|":
        ret = (Control.ask | val)
    elif comp == "&":
        ret = (Control.ask & val)
    else:
        ret = None
    Control.ask = ret
    if ret:
        return CommandService.cond_true_return_code,"True"
    return CommandService.cond_false_return_code, "False"
def comm_xkey(params,dictionary):
    return CommandService.xkey_return_code,""
def comm_version(params,dictionary):
    return CommandService.version_return_code, Version.get()
def comm_validate(params,dictionary):
    candidate = params.get_first_or_ask("Candidate Name")
    valk = not CommandService.is_invalid_key(candidate)
    valv = not CommandService.is_invalid_value(candidate)
    ret = "is not a valid key or value"
    if valk and valv:
        ret = "is a valid key and value"
    elif valk:
        ret = "is a valid key, but not a valid value"
    elif valv:
        ret = "is a valid value, but not a valid key"
    return CommandService.success_return_code,"'{}' ".format(candidate)+ret
class ParamReader:
    def __init__(self, originalstring,asker = lambda x,c,t:silent_invariant_raw_input(x,comp=c,color=Colors.WARNING+Colors.BOLD+Colors.UNDERLINE,completion=t)):
        quotesep = originalstring.split("\"")
        self.params = []
        ind = -1
        for q in quotesep:
            ind+=1
            last = (ind+1) == len(quotesep)
            if ind%2 == 0:
                first = True
                for p in q.split(" "):
                    if len(p) <= 0 and (first or not last):
                        continue
                    first = False
                    self.params.append(p)
            else:
                self.params.append(q)
        self.asker = asker
    def get_first_or_ask(self,asklabel,comp=None,default=None,tab=None):
        asklabel = ("Enter "+asklabel+":\n") if not asklabel.startswith("'") else asklabel[1:]
        if len(self.params) > 0:
            ret = self.params[0]
            self.params = self.params[1:]
            return ret
        else:
            if not default is None:
                return default
            return self.asker(asklabel,comp,tab)
class LineReader:
    def __init__(self,lines):
        self.lineno = -1
        self.lines = lines[:]
        self.lines.reverse()
    def get_line(self):
        self.lineno+=1
        if len(self.lines) == 0:
            return self.lineno, None
        ret = self.lines.pop()[:-1]
        skip,ret = self.skip_line(ret)
        if skip:
            return self.get_line()
        return self.lineno, ret
    @staticmethod
    def skip_line(string):
        if string.startswith("$") or string == "":
            return True,""
        if string.startswith("?"):
            string = string[1:]
            skip = True
            if type(Control.ask) is bool:
                skip = not Control.ask
            elif type(Control.ask) is int:
                skip = Control.ask==0
            return skip,string
        return False,string
class CommandService:
    def __init__(self):
        pass
    create_com_type = CommandType(["c", "create", "new", "define"], "Create Entry", ["<entry key>", "<entry value>"],delegate=comm_insert,long_description=Helptxt.c_long_desc)
    edit_com_type = CommandType(["e", "edit"], "Edit Entry", ["<entry key>", "<new entry value>"],delegate=comm_edit,long_description=Helptxt.e_long_desc)
    delete_com_type = CommandType(["d", "delete", "remove"], "Delete Entry", ["<entry key>"],delegate=comm_delete,long_description=Helptxt.d_long_desc)
    multidelete_com_type = CommandType(["md", "multiremove", "batchremove"], "Remove Multiple", ["<Approximation or Regular expression query>"], mindescription="Batch Remove", delegate=comm_batchdel,long_description=Helptxt.md_long_desc)
    rename_com_type = CommandType(["r", "rename"], "Rename Entry", ["<entry key>", "<new entry key>"],delegate=comm_rename,long_description=Helptxt.r_long_desc)
    find_regex_com_type = CommandType(["f", "find", "filter"], "Find enteries", ["<Regex or Approximation query>"],delegate=comm_find,long_description=Helptxt.f_long_desc)
    exit_com_type = CommandType(["q", "quit", "exit", "done"], "Quit", ["[save|discard]"],delegate=comm_exit, long_description=Helptxt.q_long_desc)
    help_com_type = CommandType(["h", "help"], "Help", usage=["[Command name or alias]"],delegate=comm_help,long_description=Helptxt.h_long_desc)
    clear_com_type = CommandType(["clr", "cls", "clear"], "Clear Console",delegate=comm_clear,long_description=Helptxt.clear_long_desc)
    script_com_type = CommandType(["b", "batch", "script", "use"], "Run Script",["<bash file>"],mindescription="Run Script",delegate=comm_batch,long_description=Helptxt.script_long_desc)
    search_com_type = CommandType(["s", "search", "search-values","locate"],"Search by values",["<Regex or Approximation query>"],mindescription="Search by values",delegate=comm_search,long_description=Helptxt.s_long_desc)
    ask_com_type = CommandType(["a","ask","query"],"Ask",["<ask type (dfn|cnt|val|echo)>","<key or query>"],delegate=comm_ask,long_description=Helptxt.a_long_desc)
    cond_com_type = CommandType(["cond","if","comp", "is"],"Condition",["<comparer>","<constant value>"],delegate=comm_cond,long_description=Helptxt.cond_long_desc)
    xkey_com_type = CommandType(["x","xkey"],"Forget Key",mindescription="Forget Key",delegate=comm_xkey,long_description=Helptxt.x_long_desc)
    version_com_type = CommandType(["vr","version"], "Get Version", mindescription="Get Version", delegate=comm_version, long_description=Helptxt.vr_long_desc)
    valid_com_type = CommandType(["v","validate","valid"], "Validate Entry Name/Value",mindescription="Validate Name",delegate=comm_validate,long_description=Helptxt.v_long_desc)
    simple_types = [create_com_type,edit_com_type,delete_com_type,rename_com_type,find_regex_com_type,exit_com_type,help_com_type,clear_com_type]
    implemented_types = simple_types+[multidelete_com_type, script_com_type, search_com_type,ask_com_type,cond_com_type,xkey_com_type,version_com_type,valid_com_type]
    #zero means success
    success_return_code = 0
    #one means unclear
    unclear_return_code = 1
    #neg means error
    error_return_code = -1
    regexerr_return_code = -2
    notimplerr_return_code = -3
    ioerr_return_code = -4
    batcherr_return_code = -5
    #pow of 2 means exit
    exit_save_return_code = 2
    exit_discard_return_code = 4
    #pow of 7 means cond output
    cond_true_return_code = 7
    cond_false_return_code = 49
    #pow of 17 means clear
    clear_return_code = 17
    #pow of 19 means ask output
    ask_return_code = 19
    #pow of 23 means help
    help_return_code = 23
    #pow of 29 means xkey
    xkey_return_code = 29
    #pow of 31 means version
    version_return_code = 31
    @classmethod
    def apply_command(cls,c_type,params,dictionary):
        return c_type.delegate(params,dictionary)
    @classmethod
    def valuequery(cls, query, dictionary):
        if query.startswith("="):
                ret = filter(lambda x:query[1:] == dictionary[x],dictionary.keys())
        elif query.startswith("~"):
            ret = cls.approx_vals(query[1:].split(" "), dictionary)
        else:
            if query == "":
                query = ".*"
            try:
                prog = re.compile(query)
            except re.error as r:
                return cls.regexerr_return_code, "can't parse regex, {}".format(str(r))
            ret = filter(lambda a: bool(prog.search(dictionary[a])),dictionary.keys())
        ret = sorted(ret)
        return 0,ret
    @classmethod
    def query(cls, query, dictionary):
        if query.startswith("="):
                ret = [query[1:]] if query[1:] in dictionary else []
        elif query.startswith("~"):
            ret = cls.approx_keys(query[1:].split(" "), dictionary)
        else:
            if query == "":
                query = ".*"
            try:
                prog = re.compile(query)
            except re.error as r:
                return cls.regexerr_return_code, "can't parse regex, {}".format(str(r))
            ret = filter(lambda a: bool(prog.search(a)),dictionary.keys())
        ret = sorted(ret)
        return 0,ret
    @classmethod
    def process_command(cls,command, dictionary,asker = lambda x,c,t:silent_invariant_raw_input(x,comp=c,color=Colors.WARNING+Colors.BOLD+Colors.UNDERLINE,completion=t)):
        command = command
        reader = ParamReader(command,asker=asker)
        t = cls.get_type(reader.get_first_or_ask("Command").lower())
        if t is None:
            return cls.unclear_return_code, "command unclear"
        return cls.apply_command(t,reader,dictionary)

    @classmethod
    def get_approximate_key(cls, key, definitions):
        if not key.startswith("~"):
            return key if key in definitions else None
        key = key[1:]
        if key in definitions:
            return key
        parts = key.split(" ")
        approx = cls.approx_keys(parts, definitions)
        if len(approx) != 1:
            return None
        silent_invariant_print("Key approximated to be '{}'".format(approx[0]))
        return approx[0]

    @classmethod
    def approx_keys(cls, parts, definitions):
        return filter(lambda x: all(map(lambda y: x.find(y) >= 0, parts)),definitions.keys())

    @classmethod
    def approx_vals(cls, parts, definitions):
        return filter(lambda x: all(map(lambda y: definitions[x].find(y) >= 0, parts)),definitions.keys())

    @classmethod
    def is_invalid_key(cls, key):
        return key in [""," "] or any(map(lambda a:key.find(a) > -1, ['"',":","\n","\t","\r","\b","\0","="])) or any(map(lambda a:key.startswith(a), ["!","~","@"]))

    @classmethod
    def is_invalid_value(cls, val):
        return val in [""," "] or any(map(lambda a:val.find(a) > -1, ['"',"\n","\t","\r","\b","\0"])) or any(map(lambda a:val.startswith(a), ["@"]))

    @classmethod
    def get_type(cls, command):
        for t in cls.implemented_types:
            if cls._is_of_type(command,t):
                return t
        return None

    @classmethod
    def _is_of_type(cls, command, c_type):
        for p in c_type.prefixes:
            if command == p:
                return  True
        return False