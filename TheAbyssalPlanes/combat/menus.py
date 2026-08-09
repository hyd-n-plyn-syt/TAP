from evennia.utils.evmenu import EvMenu

def collision_menu_node(caller):
    text = "That grid is occupied. How would you like to proceed?"
    options = (
        {"desc": "Sit", "goto": "action_sit"},
        {"desc": "Ram", "goto": "action_ram"},
        {"desc": "Restrain", "goto": "action_restrain"},
        {"desc": "Abort", "goto": "action_abort"},
    )
    return text, options

def action_sit(caller):
    caller.msg("You sit down.")
    return None

def action_ram(caller):
    caller.msg("You attempt to ram them.")
    return None

def action_restrain(caller):
    caller.msg("You attempt to restrain them.")
    return None

def action_abort(caller):
    caller.msg("Action aborted.")
    return None
