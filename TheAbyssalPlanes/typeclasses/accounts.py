"""
Account

The Account represents the game "account" and each login has only one
Account object. An Account is what chats on default channels but has no
other in-game-world existence. Rather the Account puppets Objects (such
as Characters) in order to actually participate in the game world.


Guest

Guest accounts are simple low-level accounts that are created/deleted
on the fly and allows users to test the game without the commitment
of a full registration. Guest accounts are deactivated by default; to
activate them, add the following line to your settings file:

    GUEST_ENABLED = True

You will also need to modify the connection screen to reflect the
possibility to connect with a Guest account. The setting file accepts
a lot more options for customizing the Guest account system.

"""

from evennia import AttributeProperty
from evennia.accounts.accounts import DefaultAccount, DefaultGuest
from world.data import changes


def _perm_color(account):
    """Return a Truecolor hex string for *account* based on permission level."""
    if account.is_superuser:
        return "e67e22"
    perms = account.permissions.all()
    if "developer" in perms:
        return "e67e22"
    if "builder" in perms:
        return "a84300"
    return "1abc9c"


class Account(DefaultAccount):
    """
    An Account is the actual OOC player entity. It doesn't exist in the game,
    but puppets characters.

    This is the base Typeclass for all Accounts. Accounts represent
    the person playing the game and tracks account info, password
    etc. They are OOC entities without presence in-game. An Account
    can connect to a Character Object in order to "enter" the
    game.

    Account Typeclass API:

    * Available properties (only available on initiated typeclass objects)

     - key (string) - name of account
     - name (string)- wrapper for user.username
     - aliases (list of strings) - aliases to the object. Will be saved to
            database as AliasDB entries but returned as strings.
     - dbref (int, read-only) - unique #id-number. Also "id" can be used.
     - date_created (string) - time stamp of object creation
     - permissions (list of strings) - list of permission strings
     - user (User, read-only) - django User authorization object
     - obj (Object) - game object controlled by account. 'character' can also
                     be used.
     - is_superuser (bool, read-only) - if the connected user is a superuser

    * Handlers

     - locks - lock-handler: use locks.add() to add new lock strings
     - db - attribute-handler: store/retrieve database attributes on this
                              self.db.myattr=val, val=self.db.myattr
     - ndb - non-persistent attribute handler: same as db but does not
                                  create a database entry when storing data
     - scripts - script-handler. Add new scripts to object with scripts.add()
     - cmdset - cmdset-handler. Use cmdset.add() to add new cmdsets to object
     - nicks - nick-handler. New nicks with nicks.add().
     - sessions - session-handler. Use session.get() to see all sessions connected, if any
     - options - option-handler. Defaults are taken from settings.OPTIONS_ACCOUNT_DEFAULT
     - characters - handler for listing the account's playable characters

    * Helper methods (check autodocs for full updated listing)

     - msg(text=None, from_obj=None, session=None, options=None, **kwargs)
     - execute_cmd(raw_string)
     - search(searchdata, return_puppet=False, search_object=False, typeclass=None,
                      nofound_string=None, multimatch_string=None, use_nicks=True,
                      quiet=False, **kwargs)
     - is_typeclass(typeclass, exact=False)
     - swap_typeclass(new_typeclass, clean_attributes=False, no_default=True)
     - access(accessing_obj, access_type='read', default=False, no_superuser_bypass=False, **kwargs)
     - check_permstring(permstring)
     - get_cmdsets(caller, current, **kwargs)
     - get_cmdset_providers()
     - uses_screenreader(session=None)
     - get_display_name(looker, **kwargs)
     - get_extra_display_name_info(looker, **kwargs)
     - disconnect_session_from_account()
     - puppet_object(session, obj)
     - unpuppet_object(session)
     - unpuppet_all()
     - get_puppet(session)
     - get_all_puppets()
     - is_banned(**kwargs)
     - get_username_validators(validator_config=settings.AUTH_USERNAME_VALIDATORS)
     - authenticate(username, password, ip="", **kwargs)
     - normalize_username(username)
     - validate_username(username)
     - validate_password(password, account=None)
     - set_password(password, **kwargs)
     - get_character_slots()
     - get_available_character_slots()
     - create_character(*args, **kwargs)
     - create(*args, **kwargs)
     - delete(*args, **kwargs)
     - channel_msg(message, channel, senders=None, **kwargs)
     - idle_time()
     - connection_time()

    * Hook methods

     basetype_setup()
     at_account_creation()

     > note that the following hooks are also found on Objects and are
       usually handled on the character level:

     - at_init()
     - at_first_save()
     - at_access()
     - at_cmdset_get(**kwargs)
     - at_password_change(**kwargs)
     - at_first_login()
     - at_pre_login()
     - at_post_login(session=None)
     - at_failed_login(session, **kwargs)
     - at_disconnect(reason=None, **kwargs)
     - at_post_disconnect(**kwargs)
     - at_message_receive()
     - at_message_send()
     - at_server_reload()
     - at_server_shutdown()
     - at_look(target=None, session=None, **kwargs)
     - at_post_create_character(character, **kwargs)
     - at_post_add_character(char)
     - at_post_remove_character(char)
     - at_pre_channel_msg(message, channel, senders=None, **kwargs)
     - at_post_chnnel_msg(message, channel, senders=None, **kwargs)

    """

    changes_seen = AttributeProperty(default=0)

    # Override Evennia's default OOC screen — we use the EvMenu main menu instead.
    # This prevents the old "ic / ooc / charcreate" template from showing.
    ooc_appearance_template = (
        "|wYou are out-of-character.|n\n"
        "The main menu should be visible above. If not, type |wmenu|n to reopen it.\n"
        "Use |w0|n to exit, |w1|n to choose a character, |w2|n to create, |w4|n for the lounge."
    )

    def _ensure_ooc_room(self):
        try:
            from evennia.objects.models import ObjectDB
            limbo = ObjectDB.objects.get_id(2)
            if limbo:
                if not getattr(limbo.db, "is_ooc_room", False):
                    limbo.db.is_ooc_room = True
                if not limbo.tags.get("ooc_room", category="room_flag"):
                    limbo.tags.add("ooc_room", category="room_flag")
        except Exception:
            pass

    def _migrate_legacy_wisp(self):
        # If there is a character with the same name as the account that is not already a wisp,
        # convert it to the wisp (swap typeclass, move to #2).
        try:
            from evennia.objects.models import ObjectDB
            from world.systems.wisp import is_wisp
            # Use characters handler — db_account is often None for legacy chars
            candidates = [c for c in list(self.characters.all()) if c.db_key.lower() == self.key.lower()]
            for obj in candidates:
                if is_wisp(obj):
                    return  # already has wisp
            if not candidates:
                return
            obj = candidates[0]
            # Swap typeclass to Wisp
            try:
                obj.swap_typeclass("typeclasses.wisp.Wisp", clean_attributes=False)
            except Exception:
                pass
            try:
                obj.species_key = "wisp"
            except Exception:
                try:
                    obj.attributes.add("species_key", "wisp")
                except Exception:
                    pass
            try:
                obj.tags.add("wisp", category="account")
                obj.tags.add("ooc_wisp", category="account")
            except Exception:
                pass
            # Move to limbo
            try:
                from evennia.objects.models import ObjectDB as ODB2
                limbo = ODB2.objects.get_id(2)
                if limbo and obj.location != limbo:
                    obj.location = limbo
                    obj.home = limbo
            except Exception:
                pass
            # Clear _last_puppet if it pointed at this object (it was IC before)
            try:
                if getattr(self.db, "_last_puppet", None) and getattr(self.db._last_puppet, "id", None) == obj.id:
                    self.db._last_puppet = None
            except Exception:
                pass
        except Exception:
            pass

    def show_main_menu(self, session=None):
        """Launch the account main menu."""
        if not session:
            try:
                sess_list = self.sessions.all()
                if sess_list:
                    session = sess_list[0]
            except Exception:
                pass
        if not session:
            return
        # If already puppeting, don't show menu (quit should unpuppet first)
        try:
            if self.get_puppet(session):
                return
        except Exception:
            pass
        try:
            from evennia.utils.evmenu import EvMenu
            EvMenu(self, "commands.account.main_menu", startnode="node_main", session=session, cmd_on_exit=None, auto_quit=False, auto_look=False, auto_help=False)
        except Exception as e:
            try:
                self.msg(f"|rCould not open main menu: {e}|n", session=session)
            except Exception:
                pass

    def at_post_login(self, session=None, **kwargs):
        """Announce changes, ensure OOC room/wisp, then show main menu."""
        # Evennia's default at_post_login would try to auto-puppet; with
        # AUTO_PUPPET_ON_LOGIN=False it just does at_look — we skip super's
        # puppet logic and do our own flow. Still need its protocol-flag
        # replay; replicate minimal part without puppeting.
        try:
            # Replicate DefaultAccount.at_post_login protocol flag handling without puppet
            protocol_flags = self.attributes.get("_saved_protocol_flags", default={})
            if session and protocol_flags:
                session.update_flags(**protocol_flags)
            if session:
                session.msg(logged_in={})
        except Exception:
            pass
        # Send GUI install + alerts + MudInfo
        try:
            from world.systems.gmcp import send_gui_install
            send_gui_install(self)
        except Exception:
            pass
        alert = changes.alert_text(self.changes_seen)
        if alert:
            try:
                self.msg(alert, session=session)
            except Exception:
                self.msg(alert)
        try:
            from evennia import ChannelDB
            from world.discord_integration import send_to_mudinfo
            mudinfo = ChannelDB.objects.get_channel("MudInfo") or ChannelDB.objects.get_channel("mudinfo")
            if mudinfo and not mudinfo.has_connection(self):
                mudinfo.connect(self)
            send_to_mudinfo(f"|#{_perm_color(self)}{self.key}|n |ghas entered |cThe Abyssal Planes|n|g!|n")
        except Exception:
            pass

        # Ensure OOC room flagged and migrate legacy same-name char → wisp
        self._ensure_ooc_room()
        self._migrate_legacy_wisp()

        # If already puppeting (e.g., after reload), don't override — just return
        try:
            if session and self.get_puppet(session):
                return
        except Exception:
            pass

        # Show main menu (delay slightly to beat any connection screen)
        try:
            from evennia.utils.utils import delay
            delay(0.4, lambda sess=session: self.show_main_menu(session=sess))
        except Exception:
            self.show_main_menu(session=session)

    def at_disconnect(self, reason=None, **kwargs):
        super().at_disconnect(reason=reason, **kwargs)
        try:
            from world.discord_integration import send_to_mudinfo
            send_to_mudinfo(f"|#{_perm_color(self)}{self.key}|n |rhas left |cThe Abyssal Planes|n|r.|n")
        except Exception:
            pass

    def get_character_slots(self):
        if self.is_superuser or "developer" in self.permissions.all():
            return 4
        if "builder" in self.permissions.all():
            return 4
        return 3

    def at_pre_channel_msg(self, message, channel, senders=None, **kwargs):
        if senders:
            parts = []
            for sender in senders:
                colour = _perm_color(sender)
                parts.append(f"|#{colour}{sender.key}|n")
            sender_string = ", ".join(parts)
            message_lstrip = message.lstrip()
            if message_lstrip.startswith((":", ";")):
                spacing = "" if message_lstrip[1:].startswith((":", "'", ",")) else " "
                message = f"{sender_string}{spacing}{message_lstrip[1:]}"
            else:
                message = f"{sender_string}: {message}"

        if not kwargs.get("no_prefix") and not kwargs.get("emit"):
            message = channel.channel_prefix() + message
        return message


class Guest(DefaultGuest):
    """
    This class is used for guest logins. Unlike Accounts, Guests and their
    characters are deleted after disconnection.
    """

    pass
