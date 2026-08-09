from world.systems import stats

def get_target_state(actor, target):
    """
    Returns state: 'Masked', 'Unreachable', or 'Active'.
    """
    if not actor.can_see(target):
        return 'Masked'
    if not actor.can_touch(target):
        return 'Unreachable'
    return 'Active'

def get_status_descriptor(target):
    """
    Returns (Vigor, Vim, Mens) status descriptor tuple.
    """
    pools = target.pools_current
    max_pools = stats.derived_pools(target)
    
    descriptors = []
    for pool in stats.POOL_KEYS:
        cur = pools.get(pool, 0)
        maxv = max_pools.get(pool, 1)
        pct = (cur / maxv) * 100
        
        if pct >= 90: descriptors.append("mentally sound") # placeholder logic
        elif pct >= 70: descriptors.append("somewhat troubled")
        else: descriptors.append("distraught") # Need mapping for Vigor/Vim/Mens
    return tuple(descriptors)
