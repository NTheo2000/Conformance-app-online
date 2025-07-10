import pm4py

def parse_xes(xes_path):
    """Parses XES event log file into a process model."""
    try:
        # Load the XES log
        log = pm4py.read_xes(xes_path)

        # Discover a Petri net from the event log (you can use alpha, inductive, etc.)
        net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(log)

        return {
            "transitions": len(net.transitions),
            "places": len(net.places),
            "description": "XES event log processed successfully"
        }

    except Exception as e:
        return {"error": str(e)}

