EVENNIA SETUP IN 10 STEPS FOR POWERSHELL

# 1. Create environment within the TAP(project) folder.
py -3.14 -m venv evenv

# 2. Activate the environment in Powershell.
.\evenv\Scripts\Activate.ps1

# 3. Upgrade pip setup tools fully, so it throws no errors.
pip install --upgrade pip setuptools wheel

# 4. Install Evennia
pip install evennia

# 5. Register the installation location with POWERSHELL
py -m evennia

# 6. Set up the actual Evennia game directory.
evennia --init TheAbyssalPlanes(OrWhateverYouWantToCallIt)

# 7. Move to the new game directory.
cd TheAbyssalPlanes

# 8. Build the database architecture.
evennia migrate

# 9. Launch the server. (Make a SuperUser account. Username/email/password) Runs in the background. You can close POWERSHELL.
evennia start

# 10. Login from the client of your choice with localhost:4000, or in the browser with localhost:4001



RESTART THE SERVER AFTER SHUTDOWN OR STOPPING THE SERVER

# 1. Navigate back into your root project directory
cd D:\TAP

# 2. Re-activate your Python 3.14 virtual environment
.\evenv\Scripts\Activate.ps1

# 3. Move into your actual game code directory
cd TheAbyssalPlanes

# 4. Turn the server back on
evennia start


MORE

evennia info 
  * Displays your active port configuration, database connections, and operational statistics.

evennia status 
  * Checks if the Server and Portal are currently running or stopped.

evennia reload 
  * Performs a restart without kicking the players off the MUD. Useful after code changes and the like.

evennia reboot 
  * Performs a hard restart. This shuts down both components, completely forcing all active player sessions to disconnect.

evennia stop 
  * Stops the server entirely.

evennia --log 
  * Continuously streams (tails) your active server logs directly into your PowerShell window.
  
evennia istart
  * Launches the server in Interactive Mode. This locks your PowerShell window to the engine process. It allows you to catch explicit error tracking or attach an active debugger directly if your code crashes.

evennia makemigrations 
  * Scans your custom Python code inside typeclasses or commands for data changes. It prepares structural updates for your database schema.

evennia shell 
  * Drops your PowerShell window directly into an interactive Python prompt linked into your live game database.



RUN OPENCODE INSIDE THE ENVIRONMENT TO HELP MANAGE

# 1. Go to your main project directory
cd D:\TAP

# 2. ACTIVATE THE ENVIRONMENT FIRST
.\evenv\Scripts\Activate.ps1

# 3. Step into your game files folder
cd TheAbyssalPlanes

# 4. Launch OpenCode from INSIDE the active environment
opencode