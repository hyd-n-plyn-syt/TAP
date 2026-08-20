# EVENNIA SETUP IN 10 STEPS FOR POWERSHELL

## 1. Create environment within the TAP(project) folder.
```powershell
py -3.14 -m venv evenv
```

## 2. Activate the environment in Powershell.
```powershell
.\evenv\Scripts\Activate.ps1
```

## 3. Upgrade pip setup tools fully, so it throws no errors.
```powershell
pip install --upgrade pip setuptools wheel
```

## 4. Install Evennia
```powershell
pip install evennia
```

## 5. Register the installation location with POWERSHELL
```powershell
py -m evennia
```

## 6. Set up the actual Evennia game directory.
```powershell
evennia --init TheAbyssalPlanes
```

## 7. Move to the new game directory.
```powershell
cd TheAbyssalPlanes
```

## 8. Build the database architecture.
```powershell
evennia migrate
```

## 9. Launch the server. (Make a SuperUser account. Username/email/password) Runs in the background. You can close POWERSHELL.
```powershell
evennia start
```

## 10. Login from the client of your choice with localhost:4000, or in the browser with localhost:4001

---

# RESTART THE SERVER AFTER SHUTDOWN OR STOPPING THE SERVER

```powershell
cd D:\TAP
.\evenv\Scripts\Activate.ps1
cd TheAbyssalPlanes
evennia start
```

---

# RUNNING EVENNIA COMMANDS

**Important:** Always use the `&` call operator with the full path to evennia.exe from PowerShell:

```powershell
& ..\evenv\Scripts\evennia.exe <command>
```

Bare `evennia` does NOT work from PowerShell without this.

## Server Management
- `evennia start` — start server (background)
- `evennia stop` — stop server entirely
- `evennia reload` — restart without kicking players (code changes)
- `evennia reboot` — hard restart, disconnects all sessions
- `evennia status` — check if Portal/Server are running
- `evennia info` — port config, DB connections, stats
- `evennia --log` — tail server logs in real time
- `evennia istart` — interactive mode (locks terminal, debugger attach)

## Development
- `evennia makemigrations` — scan code for DB schema changes
- `evennia migrate` — apply pending DB migrations
- `evennia shell` — interactive Python prompt linked to live DB

## Testing
```powershell
# Run the full game test suite
& ..\evenv\Scripts\evennia.exe test --settings settings.py .

# Run one group (e.g. data/systems tests)
& ..\evenv\Scripts\evennia.exe test --settings settings.py world.tests

# Run command integration tests
& ..\evenv\Scripts\evennia.exe test --settings settings.py commands.tests
```

The test runner builds a throwaway `test_evennia.db3` — it never touches the live dev DB.

---

# RUNNING OPENCODE INSIDE THE ENVIRONMENT

```powershell
cd D:\TAP
.\evenv\Scripts\Activate.ps1
cd TheAbyssalPlanes
opencode
```

---

# PUBLIC ACCESS (DUCKDNS)

- The MUD is reachable externally via telnet at theabyssalplane.duckdns.org:4000.
- The website/webclient is served on port 80 (Evennia WEBSERVER_PORTS = [(80, 4005)]):
  http://theabyssalplane.duckdns.org
- The router only supports opening port ranges (no external→internal remap), so
  Evennia must own port 80 directly. The IIS "Default Web Site" had claimed :80
  and was unbinding it (Remove-WebBinding) to free the port for Evennia.
- SERVER_HOSTNAME is set to theabyssalplane.duckdns.org so the webclient websocket
  resolves through the domain.
- Windows Firewall inbound rules: "Evennia Telnet 4000", "Evennia Web 80",
  "Evennia Web 4001", "Evennia 4002"-"Evennia 4005" (all TCP, Allow).
- The GitHub repo is private: https://github.com/hyd-n-plyn-syt/TAP

---

# ADDITIONAL NOTES

## PowerShell Gotchas
- **PowerShell 5.1 does NOT support `&&`.** Use `cmd1; if ($?) { cmd2 }` for dependent commands. Use `cmd1; cmd2` (semicolon) for sequential independent commands.
- **Paths starting with `..\` need the `&` call operator.** Without it, PowerShell tries to interpret the path as a native command name.

## Shell Scripts
For complex DB queries, write a script to `D:\TAP\scr_<topic>.py` and run:
```powershell
$cmd = "exec(open(r'D:\TAP\scr_<topic>.py').read())"
$cmd | ..\evenv\Scripts\evennia.exe shell
```
The script should write results to `D:\TAP\scr_<topic>_result.txt`.

## secret_settings.py
Sensitive settings (webhook tokens, bot tokens) live in `server/conf/secret_settings.py`
which is gitignored and imported at the end of `settings.py`.
