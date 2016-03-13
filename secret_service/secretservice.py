from optparse import OptionParser
from os import stat
from os.path import isfile

from secret_service.AESService import encrypt, decrypt
from secret_service.CommandService import CommandService
from secret_service.ControlService import silent_invariant_raw_input, silent_invariant_print, Control, Colors, clear
from secret_service.StorageService import from_storage, to_storage
from secret_service.packagedata import Version




optionparser = OptionParser("usage: %prog [options]", version="%prog {}".format(Version.get()),prog="secretservice")
optionparser.add_option("-x", "--xkey", "--forgetkey", action="store_true",dest="xkey",default=False,help="Whether the "
                        "program should forget the key once entered, and will not write in the buffer history")
optionparser.add_option("-f", "--file", action="store",dest="file_name",default=None,help="The file for the program to use")
optionparser.add_option("-k", "--key", "--password", action="store",dest="key",default=None,help="The key to decrypt the file with, use of this flag is "
                        "discouraged and it is recommended that you use 'history -c' after using this option")
optionparser.add_option("-s", "--silent", action="store_true",dest="silent",default=False,help="If set, the program will not print anything")
optionparser.add_option("-p", "--padding", action="store", dest="padding", type="int", default=0, help="the maximum extra padding (in 16 block chunks)"
                       "to append to the encrypted file to obscure the original file size (the actual padding will be between the maximum and the maximum/2)")
optionparser.add_option("-r", "--raw", "--noencrypt", action="store_true",dest="raw",default=False,help="If set, the file is not encrypted or decrypted")
optionparser.add_option("-e", "--file_exclusion",type="choice", action="store", choices=["a","w","c","e","t","r"],dest="exclusion",default="a",help=""\
                        "Exclusion type for the file, a-any file, w-the file must be either empty or missing, c-the file must be missing"\
                        ", e-the file must exist, t-the file must be empty,r-the file must be non-empty")
options, _ = optionparser.parse_args()

xkey = options.xkey
key = options.key
if not key is None:
    silent_invariant_print("WARNING: -k flag is discouraged as the password can be more easily recorded. Use of 'history -c' upon quitting is recommended", color=Colors.WARNING)
file_name = options.file_name
raw = options.raw
Control.silent = options.silent
allowread = 4
allowempty = 2
allowmissing = 1
exclusionstates = {"a":allowread|allowempty|allowmissing, "w":allowempty|allowmissing, "c":allowmissing,
                   "e":allowread|allowempty, "t":allowempty, "r":allowread}
exclusion = exclusionstates[options.exclusion]
outfile = None
while True:
    if file_name is None:
        try:
            file_name = silent_invariant_raw_input("Enter file:",completion="Files")
        except (KeyboardInterrupt, EOFError):
            exit(1)

    if isfile(file_name):
        filestatus = allowread if stat(file_name).st_size > 0 else allowempty
    else:
        filestatus = allowmissing
    if (filestatus & exclusion) == 0:
        silent_invariant_print("Exclusion mismatch!")
        file_name = None
        continue

    if filestatus == allowread:
        if key is None and not raw:
            try:
                key = silent_invariant_raw_input("Enter Key:",wipe=True,echo=False)
            except (KeyboardInterrupt,EOFError):
                exit(1)
        outfile = open(file_name,"r+")
        try:
            read = outfile.read()
            data = from_storage(read if raw else decrypt(key, read))
        except Exception as e:
            silent_invariant_print("Error decrypting: {}".format(str(e)))
            key = None
            continue
    else:
        outfile = open(file_name,"w+")
        data = {}
    break
silent_invariant_print("Welcome to SecretService! Version {}".format(Version.get()),color=Colors.UNDERLINE+Colors.BOLD)
if xkey:
    key = None
commdescriptions = ", ".join(map(lambda x:x.min_describe(), CommandService.simple_types))
while True:
    try:
        out = None
        command = silent_invariant_raw_input("Enter command ({})\n".format(commdescriptions),color=Colors.OKBLUE + Colors.BOLD)
    except (KeyboardInterrupt,EOFError):
        out = CommandService.exit_discard_return_code
        command = None
        res = "Quitting"
    if out is None:
        try:
            out, res = CommandService.process_command(command, data)
        except KeyboardInterrupt:
            silent_invariant_print("Aborted, press q or crtl+d to quit",color=Colors.FAIL+Colors.BOLD)
            continue
        except EOFError:
            out = CommandService.exit_discard_return_code
            res = "Quitting"
    if out < 0:
        silent_invariant_print("Error: "+res+"\n",color=Colors.FAIL+Colors.BOLD)
        continue
    if out == 0:
        silent_invariant_print("Success: "+res+"\n",color=Colors.OKGREEN+Colors.BOLD)
        continue
    if out in [CommandService.ask_return_code,CommandService.cond_true_return_code,CommandService.cond_false_return_code]:
        silent_invariant_print(res+"\n",color=Colors.UNDERLINE+Colors.BOLD)
        continue
    if out == CommandService.xkey_return_code:
        key = None
        silent_invariant_print("Key forgotten",color=Colors.WARNING+Colors.BOLD)
        continue
    if out == CommandService.version_return_code:
        silent_invariant_print("Version: {}".format(res),color=Colors.BOLD)
        continue
    if out == CommandService.clear_return_code:
        clear()
        continue
    if out == CommandService.exit_save_return_code:
        if key is None and not raw:
            key = silent_invariant_raw_input("Enter Key:",wipe=True,echo=False)
        outfile.seek(0)
        outfile.truncate(0)
        write = to_storage(data)
        outfile.write(write if raw else encrypt(key,write,options.padding))
    if out in [CommandService.exit_save_return_code,CommandService.exit_discard_return_code]:
        silent_invariant_print("Goodbye: "+res,color=Colors.WARNING+Colors.BOLD)
        break
    silent_invariant_print(res)
outfile.close()