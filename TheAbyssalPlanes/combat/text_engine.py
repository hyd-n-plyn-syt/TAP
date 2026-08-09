def compile_combat_text(actor, action, damage, target, next_action):
    """
    Assembles combat string.
    """
    text = f"You {action} at {target.appearance_name}, and hit them. It looks like a {damage} blow! You look like you're going to {next_action} next."
    return text
