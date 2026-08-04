"""
Player command to browse the in-game changelog.
"""
from commands.command import Command
from world.data import changes


class CmdChanges(Command):
    """
    Browse the in-game changelog.

    Usage:
      changes
      changes all
      changes <number>
      changes latest

    With no argument, lists every change you have not read yet. 'changes
    all' lists the entire history since the first entry. To read one in
    full, give its number (or use 'latest'); doing so marks it and
    everything before it as read.
    """
    key = "changes"
    aliases = ["changelog", "news"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        account = caller.account
        seen = account.changes_seen if account else 0

        arg = self.args.strip().lower()

        if arg == "all":
            self._list_changes(caller, changes.all_changes())
            self._mark_read(account, changes.latest_number())
            return

        if arg == "latest":
            entry = changes.get_change(changes.latest_number())
            if entry:
                self._show_entry(caller, entry)
                self._mark_read(account, entry["number"])
            else:
                caller.msg("There are no recorded changes yet.")
            return

        if arg:
            try:
                number = int(arg.lstrip("#"))
            except ValueError:
                caller.msg(
                    "Usage: changes [all | <number> | latest]. "
                    "Use 'changes' with no argument to list what's new."
                )
                return
            entry = changes.get_change(number)
            if not entry:
                caller.msg(f"There is no change #{number}.")
                return
            self._show_entry(caller, entry)
            self._mark_read(account, entry["number"])
            return

        pending = changes.unread(seen)
        if not pending:
            caller.msg("You are all caught up. |wchanges all|n shows the full history.")
            return
        self._list_changes(caller, pending)

    def _list_changes(self, caller, entries):
        lines = ["|w=== Changes ===|n"]
        for entry in entries:
            lines.append(
                f"|w#{entry['number']:<3}|n {changes.short_date(entry['date']):>6}  "
                f"{entry['title']}"
            )
        lines.append("")
        lines.append("Use |wchanges <number>|n (or |wchanges latest|n) to read one in full.")
        caller.msg("\n".join(lines))

    def _show_entry(self, caller, entry):
        lines = [
            f"|wChange #{entry['number']}|n  ({changes.full_date(entry['date'])})",
            f"|w{entry['title']}|n",
            "",
            entry["body"],
        ]
        caller.msg("\n".join(lines))

    def _mark_read(self, account, number):
        if account is None:
            return
        account.changes_seen = max(account.changes_seen, number)