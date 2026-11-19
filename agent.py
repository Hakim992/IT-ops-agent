import os
import json
import shutil
import subprocess
import re
import platform
import string
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.environ["GEMINI_API_KEY"],
)
MODEL = "gemini-2.5-flash"


# ===== 1. TOOLS =====
def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def list_files(folder="."):
    if not os.path.isdir(folder):
        return f"Folder {folder} tak wujud"
    return ", ".join(os.listdir(folder))


def list_drives():
    ada = []
    for d in string.ascii_uppercase:
        if os.path.exists(f"{d}:\\"):
            ada.append(f"{d}:")
    if not ada:
        return "Tiada drive dijumpai"
    return ", ".join(ada)


def check_disk(drive="C:"):
    drive = drive.strip().upper()
    if len(drive) == 1:
        drive += ":"
    if drive.endswith(":"):
        drive += "\\"
    if not os.path.exists(drive):
        return f"Drive {drive} tak wujud"
    total, used, free = shutil.disk_usage(drive)
    gb = 1024 ** 3
    peratus = used / total * 100
    return (
        f"{drive} Total {total / gb:.1f}GB, "
        f"guna {used / gb:.1f}GB, "
        f"baki {free / gb:.1f}GB ({peratus:.0f}% penuh)"
    )


def ping_host(host):
    if not re.fullmatch(r"[A-Za-z0-9.\-]+", host):
        return "Nama host tak sah"
    if platform.system() == "Windows":
        flag = "-n"
    else:
        flag = "-c"
    cmd = ["ping", flag, "2", host]
    r = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=15,
    )
    return r.stdout[-400:] or r.stderr


def read_file(path):
    if not os.path.isfile(path):
        return "Fail tak wujud"
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()[:3000]


FUNCS = {
    "get_time": get_time,
    "list_files": list_files,
    "list_drives": list_drives,
    "check_disk": check_disk,
    "ping_host": ping_host,
    "read_file": read_file,
}


# ===== 2. PENERANGAN TOOLS UNTUK AI =====
def tool(name, desc, props=None, required=None):
    params = {"type": "object", "properties": props or {}}
    if required:
        params["required"] = required
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": desc,
            "parameters": params,
        },
    }


STR = {"type": "string"}

tools = [
    tool("get_time",
         "Dapatkan tarikh dan masa sekarang"),
    tool("list_files",
         "Senaraikan fail dalam satu folder",
         {"folder": STR}),
    tool("list_drives",
         "Senaraikan semua drive dalam komputer. "
         "Guna ini dulu sebelum check_disk kalau user tak sebut drive."),
    tool("check_disk",
         "Semak ruang storage satu drive, contoh C:",
         {"drive": STR}, ["drive"]),
    tool("ping_host",
         "Ping satu host/domain/IP untuk semak sambungan network",
         {"host": STR}, ["host"]),
    tool("read_file",
         "Baca isi fail teks (contoh fail log)",
         {"path": STR}, ["path"]),
]


# ===== 3. LOOP AGENT =====
SYSTEM = (
    "Kau IT assistant yang membantu. "
    "Guna tools bila perlu tanpa tanya user dulu kalau boleh cari sendiri. "
    "Jawab dalam Bahasa Melayu, ringkas dan jelas."
)
messages = [{"role": "system", "content": SYSTEM}]


def jalankan_tool(call):
    args = json.loads(call.function.arguments or "{}")
    try:
        result = FUNCS[call.function.name](**args)
    except Exception as e:
        result = f"Error: {e}"
    print(f"  [tool] {call.function.name}({args}) -> {str(result)[:100]}")
    return {
        "role": "tool",
        "tool_call_id": call.id,
        "content": str(result),
    }


def tanya_ai():
    while True:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
        )
        msg = resp.choices[0].message

        if not msg.tool_calls:
            print("AI:", msg.content)
            messages.append({"role": "assistant", "content": msg.content})
            return

        messages.append(msg.model_dump(exclude_none=True))
        for call in msg.tool_calls:
            messages.append(jalankan_tool(call))


print("IT Agent sedia. Taip 'keluar' untuk berhenti.")

while True:
    soalan = input("\nKau: ").strip()
    if not soalan:
        continue
    if soalan.lower() in ("exit", "keluar"):
        break

    sebelum = len(messages)
    messages.append({"role": "user", "content": soalan})
    try:
        tanya_ai()
    except Exception as e:
        print(f"[Ralat API] {e}")
        print("Kalau 429, tunggu seminit dan cuba lagi.")
        del messages[sebelum:]