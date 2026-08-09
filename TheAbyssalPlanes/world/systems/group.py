from evennia import AttributeProperty

class GroupManager:
    @staticmethod
    def invite(sender, target):
        sender.db.group_invite = target
        sender.msg(f"You invited {target.name} to your group.")
        target.msg(f"{sender.name} has invited you to a group.")

    @staticmethod
    def join(target, sender):
        if target.db.group_invite == sender:
            target.db.group = sender.db.group or sender
            sender.db.group = target.db.group
            target.msg("You joined the group.")
        else:
            target.msg("No group invite found.")

def toggle_autoassist(char):
    char.db.autoassist = not char.db.autoassist
    status = "on" if char.db.autoassist else "off"
    char.msg(f"Autoassist is now {status}.")
