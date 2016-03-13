import textwrap
from ControlService import Colors,getTerminalSize
class HelpEntry:
    def __init__(self,descriptors,name,desc):
        self.name = name
        self.desc =desc
        self.descriptors = descriptors
    def description(self):
        pref = self.name
        wrapper = textwrap.TextWrapper(width=getTerminalSize()[0],initial_indent=4*" ",subsequent_indent=4*" ",replace_whitespace=False)
        return Colors.UNDERLINE+pref+":\n"+Colors.ENDC+wrapper.fill(self.desc)
class Helptxt:
    def __init__(self):pass
    _approx_query_description="Approximation queries are a simplification of regular expression queries." \
                              " An Approximaiton query is preceeded by either a ~ or a =." \
                              " If it preceeded by a ~, then all values in which the whitespace-seperated strings appear in *in any order* match (see examples below)." \
                              " If it is preceeded by a =, then all values that are an exact match with the strings match (as such, threre can only be one match to this query)." \
                              " Most instances that accept an Approximation query, a regular expression can be entered instead, by not putting a ~ or = at the start of the query." \
                              " Example I: '~foo boo' match 'fooboo', 'foo boo', 'foo.boo', 'boofoo', 'bootoofoo' but not 'beetoo'." \
                              " Example II: '~foo' matches all values with foo in it." \
                              " Example III: '=foo' will match only 'foo'." \
                              " Example IV: '=foo boo' will match only 'foo boo'."
    _valid_naming_description="All key and value names cannot be blank, or be a single space." \
                              " They cannot include a tab, newline, quote (\"), return character, or other special character." \
                              " They cannot start with a '@'." \
                              " Furthermore, key names cannot begin with a '~', or include ':' or '='."
    approx_query_help_entry = HelpEntry(["approximation"],"Approximation Queries", _approx_query_description)
    valid_naming_help_entry = HelpEntry(["validation","valid naming","naming"],"Valid Naming", _valid_naming_description)
    help_enteries = [approx_query_help_entry, valid_naming_help_entry]
    c_long_desc="Create a new entry." \
                 " Requires a valid (unused) key name and a valid value."
    e_long_desc="Edit an entry's value." \
                 " Requires an in-use key name and a new, valid value." \
                 " If the new value is ommited on the decleration line, the old value is auto-completed and can be edited in-terminal." \
                 " The entry key can be approximated with an Approximation Query (see below), granted only one entry key will match it."
    d_long_desc="Delete an entry." \
                 " Requires an in-use key name." \
                 " The entry key can be approximated with an Approximation Query (see below), granted only one entry key will match it."
    md_long_desc="Delete multiple entries." \
                  " Requires a Regex or Approximation (see below) query." \
                  " Targets all entries that match the query." \
                  " Upon execution, a confirmation message will appear prompting the user to continue, abort removal, or view the entreries to be deleted." \
                  " The confirmation will be skipped if the query is preceeded with a triple exclemation mark (!!!)." \
                  " Examples: 'md .*' will delete all enetries and require a confirmation, 'md !!!~d a' will delete all entries with a d and an a in them, but will not require confirmation."
    r_long_desc="Rename an entry to a different key."\
                 " Requires an in-use key name and a new, valid key name."\
                 " If the new key is ommited on the decleration line, the old key is auto-completed and can be edited in-terminal." \
                 " The entry key can be approximated with an Approximation Query (see below), granted only one entry key will match it."
    f_long_desc="Search among the entry keys." \
                 " Requires a Regex or Approximation (see below) query." \
                 " Lists all entries that match the query." \
                 " If no enteries match the query, it returns 'no results found'." \
                 ' If the query is empty (""), returns all enteries present.' \
                 " Examples: 'f .*' will list all enteries, 'f foo' and 'f ~foo' will both list all enteries with foo in its name, 'f =foo' will list only the key foo (if it exists), 'f ~foo boo' will list all entries whose name has both foo and boo."
    q_long_desc="Exits the program." \
                 " Requires either 's' (save) or 'd' (discard) to declare whether to save the changes made to file." \
                 " If no changes were made, the parameter is not required, it can be optionally entered, and if it is 's', the dictionary will be saved."
    h_long_desc="Prints a description of the program's functionality." \
                " Prints all commands including their usage and purpose." \
                " Also prints the program's mechanics." \
                " An optional parameter is a command or alias of command, if entered, only that command's help will be printed." \
                " The optional parameter can also be a mechanic, a valid list of mechanics are: ["+",".join((map(lambda x:"|".join(x.descriptors),help_enteries)))+"]" \
                " The optional parameter can be also 'all', this results in the default behaviour."
    clear_long_desc="Clears the console window." \
                     " Does not work on some platforms." \
                     " Does not necessarily clear the buffer, means that what was on the console CAN be recovered."
    script_long_desc="Runs the commands from an exterior file." \
                     " The output from the commands are not printed." \
                     " If an error is encountered, the following lines are not executed." \
                     " All lines that begin with $ or are blank are ignored." \
                     " If a line begins with ?, it will be executed only if the last Ask or Cond command returned true or a non-zero number." \
                     " If a command is incomplete, then the following lines are used as arguments, each line meaning one argument, until the command is complete." \
                     " Some commands (clear, quit) do not work as expected"
    s_long_desc="Searches among the values of enteries." \
                 " Requires a Regex or Approximation (see below) query." \
                 " Lists all entries that match the query." \
                 " If no enteries match the query, it returns 'no results found'."
    a_long_desc="Returns a value to answer a question." \
                 " Accepts either a def,cnt,cval, or echo as the first parameter." \
                 " If the first parameter is dfn, the second is a key name, the ask returns the value of the entry with the key." \
                 " The entry key can be approximated with an Approximation Query (see below), granted only one entry key will match it." \
                 " If the first parameter is cnt, the second is a Regex or Approximation query, the ask returns how many keys match the query." \
                 " If the first parameter is val, the second is a Regex or Approximation query, the ask returns how many entry values match the query." \
                 " If the First parameter is echo, the second value is returned without processing. The value is converted to an appropriate type handleable by cond operations" \
                 " Ask stores the result in a temporary value, that can be evaluated by the cond command."
    cond_long_desc="Compares a value against the result of the last 'Ask' or 'Cond' result." \
                    " Accepts a valid comparison (==,!=,<,>,<=,>=) or a boolean operation (&,|) and a second value." \
                    " The second value must be comperable with the last Ask or Cond result, and the comparison must be valid with them."\
                    " The result of the Cond is stored as the result of the last Ask."
    x_long_desc ="Clears the encryption key from the program's memory." \
                 " If changes are to be saved, the password must hen be re-entered." \
                 " This is useful in case you want to change passwords."
    vr_long_desc= "Prints the version of the current instance of SecretService."
    v_long_desc= "Checks and returns whether a text is a valid key or value." \
                 "Does not check whether the key is in use."
