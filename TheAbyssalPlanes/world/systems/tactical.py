def opposed_test(attacker, defender, atk_skill, def_skill):
    # Logic to roll and compare skills
    # Placeholder for roll logic
    return True

def perform_ram(attacker, defender):
    if opposed_test(attacker, defender, "ram", "resist"):
        attacker.msg("You bash into them successfully.")
        return True
    return False

def perform_restrain(attacker, defender):
    if opposed_test(attacker, defender, "restrain", "resist"):
        attacker.msg("You have restrained them.")
        return True
    return False

def perform_subdue(attacker, defender):
    if opposed_test(attacker, defender, "subdue", "resist"):
        attacker.msg("You subdue them.")
        return True
    return False
