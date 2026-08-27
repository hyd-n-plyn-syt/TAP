"""
Helpers for the OOC wisp / lounge.
"""

from evennia.objects.models import ObjectDB


def is_wisp(obj):
    """Return True if obj is a wisp."""
    if not obj:
        return False
    if getattr(obj, "is_wisp", False):
        return True
    try:
        tc = getattr(obj, "typeclass_path", "") or ""
        if "wisp" in tc.lower():
            return True
    except Exception:
        pass
    try:
        if getattr(obj.db, "species_key", None) == "wisp":
            return True
    except Exception:
        pass
    return False


def is_ooc_room(room):
    """Return True if room is the OOC lounge (#2)."""
    if not room:
        return False
    try:
        if getattr(room.db, "is_ooc_room", False):
            return True
        if room.tags.get("ooc_room", category="room_flag"):
            return True
        if getattr(room, "id", None) == 2:
            return True
    except Exception:
        pass
    return False


def _resolve_char_ref(ref):
    """Resolve a possible int/dbref/str to an ObjectDB instance."""
    if ref is None:
        return None
    if isinstance(ref, int):
        try:
            return ObjectDB.objects.get_id(ref)
        except Exception:
            return None
    if isinstance(ref, str):
        s = ref.strip()
        if s.startswith("#") and s[1:].isdigit():
            try:
                return ObjectDB.objects.get_id(int(s[1:]))
            except Exception:
                return None
        return None
    # Already an object
    return ref


def non_wisp_characters(account):
    """Return list of account's playable characters excluding the wisp."""
    try:
        raw = list(account.characters.all())
    except Exception:
        raw = []
    chars = []
    for ref in raw:
        obj = _resolve_char_ref(ref)
        if obj:
            chars.append(obj)
        else:
            # ref might already be an object that failed resolve as int/str; keep it if it looks like an object
            if hasattr(ref, "db_key") or hasattr(ref, "key"):
                chars.append(ref)
    # Fallback to ObjectDB if handler not yet populated
    if not chars:
        try:
            chars = list(ObjectDB.objects.filter(db_account=account, db_typeclass_path__contains="characters"))
            wisp_objs = list(ObjectDB.objects.filter(db_account=account, db_typeclass_path__contains="wisp"))
            chars = chars + wisp_objs
        except Exception:
            pass
    # Also ensure any int/str in fallback are resolved
    resolved = []
    for c in chars:
        obj = _resolve_char_ref(c) if isinstance(c, (int, str)) else c
        if obj and not is_wisp(obj):
            resolved.append(obj)
        elif obj and is_wisp(obj):
            continue
        elif not isinstance(c, (int, str)) and not is_wisp(c):
            resolved.append(c)
    return resolved


def get_wisp(account):
    """Return the wisp for an account, or None."""
    try:
        # Prefer characters handler (db_account is often None for existing chars)
        try:
            for ref in list(account.characters.all()):
                obj = _resolve_char_ref(ref)
                if obj and is_wisp(obj):
                    return obj
        except Exception:
            pass
        from evennia.objects.models import ObjectDB
        for ref in list(account.characters.all()):
            obj = _resolve_char_ref(ref)
            if not obj:
                continue
            try:
                if obj.db_key.lower() == account.key.lower() and is_wisp(obj):
                    return obj
            except Exception:
                continue
        # Fallback DB search
        qs = ObjectDB.objects.filter(db_typeclass_path__icontains="wisp")
        for obj in qs:
            try:
                # Check ownership via characters handler (resolve)
                for ref2 in list(account.characters.all()):
                    obj2 = _resolve_char_ref(ref2)
                    if obj2 and obj2.id == obj.id and is_wisp(obj):
                        return obj
            except Exception:
                pass
        for ref in list(account.characters.all()):
            obj = _resolve_char_ref(ref)
            if not obj:
                continue
            try:
                if obj.tags.get("wisp", category="account") or obj.tags.get("ooc_wisp", category="account"):
                    return obj
            except Exception:
                pass
    except Exception:
        pass
    return None


def get_or_create_wisp(account, session=None):
    """Find or create the wisp for an account. Ensures location is #2."""
    wisp = get_wisp(account)
    if wisp:
        try:
            limbo = ObjectDB.objects.get_id(2)
            if limbo and wisp.location != limbo:
                wisp.location = limbo
            if getattr(wisp.db, "species_key", None) != "wisp":
                wisp.db.species_key = "wisp"
            try:
                if wisp.locks:
                    wisp.locks.add(f"puppet:id({account.id}) or perm(Developer)")
                    wisp.locks.add("delete:false()")
            except Exception:
                pass
        except Exception:
            pass
        return wisp

    # No wisp found — check for legacy same-name character to convert (via characters handler)
    try:
        legacy = None
        for obj in list(account.characters.all()):
            if obj.db_key.lower() == account.key.lower() and not is_wisp(obj):
                legacy = obj
                break
        if not legacy:
            # Fallback DB raw check (in case handler empty)
            for obj in ObjectDB.objects.filter(db_key__iexact=account.key):
                # Must belong to this account via handler membership
                try:
                    if obj in list(account.characters.all()) and not is_wisp(obj):
                        legacy = obj
                        break
                except Exception:
                    continue
        if legacy:
            try:
                legacy.swap_typeclass("typeclasses.wisp.Wisp", clean_attributes=False)
            except Exception as e:
                # If swap fails, try manual fallback
                try:
                    legacy.db.species_key = "wisp"
                except Exception:
                    pass
            try:
                legacy.db.species_key = "wisp"
            except Exception:
                pass
            try:
                legacy.tags.add("wisp", category="account")
                legacy.tags.add("ooc_wisp", category="account")
            except Exception:
                pass
            try:
                legacy.locks.add(f"puppet:id({account.id}) or perm(Developer)")
                legacy.locks.add("delete:false()")
            except Exception:
                pass
            try:
                limbo = ObjectDB.objects.get_id(2)
                if limbo:
                    legacy.location = limbo
                    legacy.home = limbo
                    if not getattr(limbo.db, "is_ooc_room", False):
                        limbo.db.is_ooc_room = True
                    if not limbo.tags.get("ooc_room", category="room_flag"):
                        limbo.tags.add("ooc_room", category="room_flag")
            except Exception:
                pass
            # Clear _last_puppet if it pointed at legacy
            try:
                if getattr(account.db, "_last_puppet", None) and account.db._last_puppet.id == legacy.id:
                    account.db._last_puppet = None
            except Exception:
                pass
            return legacy
    except Exception:
        pass

    # Create new wisp
    from evennia.utils import create
    limbo = None
    try:
        limbo = ObjectDB.objects.get_id(2)
    except Exception:
        pass
    if limbo:
        try:
            if not getattr(limbo.db, "is_ooc_room", False):
                limbo.db.is_ooc_room = True
            if not limbo.tags.get("ooc_room", category="room_flag"):
                limbo.tags.add("ooc_room", category="room_flag")
        except Exception:
            pass

    try:
        wisp = create.create_object(
            "typeclasses.wisp.Wisp",
            key=account.key,
            location=limbo,
            home=limbo,
        )
        # Manually attach account (create_object with account kwarg may not work for all versions)
        try:
            if wisp and account:
                # Ensure characters handler linkage
                if wisp not in list(account.characters.all()):
                    account.characters.add(wisp)
                # Set account linkage for puppet locks
                wisp.locks.add(f"puppet:id({account.id}) or perm(Developer)")
        except Exception:
            pass
    except Exception as e:
        try:
            import evennia
            evennia.logger.log_trace(f"get_or_create_wisp create_object failed for {account.key}: {e}")
        except Exception:
            pass
        wisp = None
    if not wisp:
        try:
            char, errs = account.create_character(key=account.key, location=limbo)
            if char:
                try:
                    char.swap_typeclass("typeclasses.wisp.Wisp", clean_attributes=False)
                except Exception:
                    pass
                wisp = char
                if limbo:
                    wisp.location = limbo
                    wisp.home = limbo
            else:
                try:
                    import evennia
                    evennia.logger.log_trace(f"get_or_create_wisp create_character failed for {account.key}: {errs}")
                except Exception:
                    pass
                return None
        except Exception as e:
            try:
                import evennia
                evennia.logger.log_trace(f"get_or_create_wisp fallback failed for {account.key}: {e}")
            except Exception:
                pass
            return None

    # Ensure wisp attrs
    try:
        wisp.species_key = "wisp"
        # Purge any non-wisp appearance that may have leaked from fallback
        # Leave gender/size/adjective/color for wisp_menu to fill
        wisp.locks.add(f"puppet:id({account.id}) or perm(Developer)")
        wisp.locks.add("delete:false()")
        wisp.tags.add("wisp", category="account")
        wisp.tags.add("ooc_wisp", category="account")
        if limbo:
            wisp.location = limbo
            wisp.home = limbo
    except Exception:
        pass
    return wisp


def wisp_needs_setup(wisp):
    """Return True if wisp has not yet been customized (or has invalid wisp data)."""
    if not wisp:
        return True
    try:
        from world.data import appearance as appearance_data
        skin = wisp.attributes.get("appearance_skin")
        if not skin:
            skin = getattr(wisp.db, "appearance_skin", None)
        adj = wisp.attributes.get("appearance_adjective")
        if not adj:
            adj = getattr(wisp.db, "appearance_adjective", None)
        size = wisp.attributes.get("appearance_size")
        if not size:
            size = getattr(wisp.db, "appearance_size", None)
        # Validate against wisp-specific palettes, not just existence.
        # Legacy converts (e.g., Ohm) may have Visarii ghost-violet / refracting which are invalid for wisp.
        has_color = bool(skin and appearance_data.valid_skin("wisp", skin))
        has_adj = bool(adj and appearance_data.valid_adjective("wisp", adj))
        has_size = bool(size and appearance_data.valid_wisp_size(size))
        return not (has_color and has_adj and has_size)
    except Exception:
        return True
