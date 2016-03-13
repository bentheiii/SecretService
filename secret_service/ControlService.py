import readline
import getpass
import os
import glob
class Control:
    def __init__(self):
        pass
    silent = False
    changed = False
    bufferwidth = 110
    ask = None

class Colors:
    def __init__(self):
        pass
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    NONE=''

def silent_invariant_print(prompt, newline=True,color = Colors.NONE):
    prompt = color+prompt+Colors.ENDC
    if Control.silent:
        return
    if newline:
        print prompt
    else:
        print prompt,

def fileCompleter(text, state):
    return (glob.glob(text+'*')+[None])[state]

def listCompleter(text,state,options):
    ret = []
    for o in options:
        if o.startswith(text):
            ret.append(o)
    return (ret+[None])[state]

def silent_invariant_raw_input(prompt,comp=None,wipe=False, echo = True,color = Colors.NONE,completion=None):
    prompt = color+prompt+Colors.ENDC
    if not Control.silent:
        readline.set_startup_hook(lambda: readline.insert_text(comp))
    if completion=="Files":
        readline.set_completer_delims(' \t\n;')
        readline.parse_and_bind("tab: complete")
        readline.set_completer(fileCompleter)
    elif not completion is None:
        readline.set_completer_delims(' \t\n;')
        readline.parse_and_bind("tab: complete")
        readline.set_completer(lambda a,b:listCompleter(a,b,completion))
    try:
        if Control.silent:
            prompt = ""
        if echo:
            ret = raw_input(prompt)
        else:
            ret = getpass.getpass(prompt)
            wipe = False
        if wipe:
            l = readline.get_current_history_length()
            if l > 0:
                readline.remove_history_item(l-1)
        return ret
    finally:
        if not Control.silent:
            readline.set_startup_hook()
        if not completion is None:
            readline.parse_and_bind("set disable-completion On")
            readline.set_completer(None)
            #readline.parse_and_bind("tab: \t")
            readline.set_completer_delims("")

def clear():
    readline.clear_history()
    os.system('cls' if os.name == 'nt' else 'tput reset')

def getTerminalSize():
    import os
    env = os.environ
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
        except:
            return
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))
    return int(cr[1]), int(cr[0])