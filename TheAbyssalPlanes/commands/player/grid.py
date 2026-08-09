"""
Help entry for the movement grid system.
"""
from evennia import Command

class CmdHelpGrid(Command):
    """
    View the coordinate grid layout.

    Usage:
      help grid
    """
    key = "grid"
    help_category = "General"

    def func(self):
        self.caller.msg("""
|w/===============================================\|n
|w|||gY|G   0 1 2 3 4 5 6 7 8 910111213141516171819   |gY|w|||n
|w|||gY|G19|n # # # # # # # # # # # # # # # # # # #|G19|G19 |gY|w|||n
|w|||gY|G18|n # # # # # # # # # # # # # # # # # #|G18|n #|G18 |gY|w|||n
|w|||gY|G17|n # # # # # # # # # # # # # # # # #|G17|n # #|G17 |gY|w|||n
|w|||gY|G16|n # # # # # # # # # # # # # # # #|G16|n # # #|G16 |gY|w|||n
|w|||gY|G15|n # # # # # # # # # # # # # # #|G15|n # # # #|G15 |gY|w|||n
|w|||gY|G14|n # # # # # # # # # # # # # #|G14|n # # # # #|G14 |gY|w|||n
|w|||gY|G13|n # # # # # # # # # # # # #|G13|n # # # # # #|G13 |gY|w|||n
|w|||gY|G12|n # # # # # # # # # # # #|G12|n # # # # # # #|G12 |gY|w|||n
|w|||gY|G11|n # # # # # # # # # # #|G11|n # # # # # # # #|G11 |gY|w|||n
|w|||gY|G10|n # # # # # # # # # #|G10|n # # # # # # # # #|G10 |gY|w|||n
|w|||gY|G 9|n # # # # # # # # # |G9|n # # # # # # # # # #|G 9 |gY|w|||n
|w|||gY|G 8|n # # # # # # # # |G8|n # # # # # # # # # # #|G 8 |gY|w|||n
|w|||gY|G 7|n # # # # # # # |G7|n # # # # # # # # # # # #|G 7 |gY|w|||n
|w|||gY|G 6|n # # # # # # |G6|n # # # # # # # # # # # # #|G 6 |gY|w|||n
|w|||gY|G 5|n # # # # # |G5|n # # # # # # # # # # # # # #|G 5 |gY|w|||n
|w|||gY|G 4|n # # # # |G4|n # # # # # # # # # # # # # # #|G 4 |gY|w|||n
|w|||gY|G 3|n # # # |G3|n # # # # # # # # # # # # # # # #|G 3 |gY|w|||n
|w|||gY|G 2|n # # |G2|n # # # # # # # # # # # # # # # # #|G 2 |gY|w|||n
|w|||gY|G 1|n # |G1|n # # # # # # # # # # # # # # # # # #|G 1 |gY|w|||n
|w|||gY|G 0|G 0|n # # # # # # # # # # # # # # # # # # #|G 0 |gY|w|||n
|w|||gY|G   0 1 2 3 4 5 6 7 8 910111213141516171819   |gY|w|||n
|w|||g  X X X X X X X X X X X X X X X X X X X X X X  |w|||n
|w\===============================================/|n 
""")
