from datetime import datetime, timedelta


def classify_node(node_id, last_heard, existing_nodes, traceroute_log_nodes, current_time, stale_after=timedelta(hours=2)):
    """Decide what to do with a node seen in the mesh's node list.

    Returns one of:
      "no_last_heard"  - no lastHeard timestamp available
      "stale"          - last heard more than `stale_after` ago
      "already_logged" - fresh, but already in the traceroute log
      "new"            - fresh, not logged, not in existing_nodes
      "known"          - fresh, not logged, but already in existing_nodes
    """
    if not last_heard:
        return "no_last_heard"

    last_heard_time = datetime.fromtimestamp(last_heard)
    time_since_last_heard = current_time - last_heard_time

    if time_since_last_heard > stale_after:
        return "stale"

    if node_id in traceroute_log_nodes:
        return "already_logged"

    if node_id not in existing_nodes:
        return "new"

    return "known"
