import os
import pm4py
import xml.etree.ElementTree as ET
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
from collections import defaultdict


def calculate_alignments(bpmn_path: str, xes_path: str):
    if not os.path.exists(bpmn_path):
        raise FileNotFoundError(f"BPMN file not found: {bpmn_path}")
    if not os.path.exists(xes_path):
        raise FileNotFoundError(f"XES file not found: {xes_path}")

    bpmn_model = pm4py.read_bpmn(bpmn_path)
    net, initial_marking, final_marking = pm4py.convert.convert_to_petri_net(bpmn_model)
    log = xes_importer.apply(xes_path)
    aligned_traces = alignments.apply_log(log, net, initial_marking, final_marking)

    return aligned_traces

def get_fitness_per_trace(aligned_traces):
    fitness_data = []
    for i, alignment in enumerate(aligned_traces):
        fitness = round(alignment.get("fitness", 0), 4)
        fitness_data.append({
            "trace": f"Trace {i + 1}",
            "conformance": fitness
        })
    return fitness_data

def get_conformance_bins(fitness_data):
    bins = [ { "averageConformance": 0, "traceCount": 0 } for _ in range(10) ]

    for item in fitness_data:
        conformance = item["conformance"]
        index = min(int(conformance * 10), 9)
        bins[index]["averageConformance"] += conformance
        bins[index]["traceCount"] += 1

    for bin in bins:
        if bin["traceCount"] > 0:
            bin["averageConformance"] /= bin["traceCount"]

    return bins

def extract_desired_outcomes_from_bpmn(bpmn_path):
    tree = ET.parse(bpmn_path)
    root = tree.getroot()
    ns = {'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL'}

    end_events = root.findall(".//bpmn:endEvent", ns)
    desired_outcomes = []

    for event in end_events:
        has_error_definition = event.find("bpmn:errorEventDefinition", ns) is not None
        if not has_error_definition:
            incoming = event.find("bpmn:incoming", ns)
            if incoming is not None:
                incoming_flow = incoming.text
                seq_flows = root.findall(".//bpmn:sequenceFlow", ns)
                for flow in seq_flows:
                    if flow.get("id") == incoming_flow:
                        source_ref = flow.get("sourceRef")
                        task = root.find(f".//bpmn:task[@id='{source_ref}']", ns)
                        if task is not None and "name" in task.attrib:
                            desired_outcomes.append(task.attrib["name"])

    return list(set(desired_outcomes))

def get_outcome_distribution(bpmn_path, xes_path, aligned_traces):
    desired_outcomes = extract_desired_outcomes_from_bpmn(bpmn_path)
    log = xes_importer.apply(xes_path)

    bins = [
        {"range": [i / 10, (i + 1) / 10], "traceCount": 0, "correctCount": 0}
        for i in range(10)
    ]

    for i, alignment in enumerate(aligned_traces):
        fitness = alignment.get("fitness", 0)
        trace = log[i]

        if not trace:
            continue

        last_activity = trace[-1]['concept:name']
        bin_index = min(int(fitness * 10), 9)

        bins[bin_index]["traceCount"] += 1
        if last_activity in desired_outcomes:
            bins[bin_index]["correctCount"] += 1

    for b in bins:
        if b["traceCount"] > 0:
            b["percentageEndingCorrectly"] = round((b["correctCount"] / b["traceCount"]) * 100, 2)
        else:
            b["percentageEndingCorrectly"] = 0.0
        del b["correctCount"]

    return {
        "desiredOutcomes": desired_outcomes,
        "bins": bins
    }
def get_unique_sequences_per_bin(xes_path, aligned_traces):
    if not os.path.exists(xes_path):
        raise FileNotFoundError(f"XES file not found: {xes_path}")

    log = xes_importer.apply(xes_path)

    bins = [set() for _ in range(10)]

    for i, trace in enumerate(log):
        fitness = aligned_traces[i].get("fitness", 0)
        bin_index = min(int(fitness * 10), 9)
        sequence = tuple(event["concept:name"] for event in trace if "concept:name" in event)
        bins[bin_index].add(sequence)

    return [
        {
            "bin": i,
            "uniqueSequences": len(bins[i]),
            "sequences": [list(seq) for seq in bins[i]]  # Convert tuple to list for JSON serialization
        }
        for i in range(10)
    ]


def get_conformance_by_role(xes_path, aligned_traces):
    log = xes_importer.apply(xes_path)

    role_conformance = defaultdict(list)

    for i, trace in enumerate(log):
        fitness = aligned_traces[i].get("fitness", 0)
        roles_in_trace = {event.get("org:role") for event in trace if "org:role" in event}

        for role in roles_in_trace:
            if role:  # Avoid None
                role_conformance[role].append(fitness)

    result = []
    for role, scores in role_conformance.items():
        avg_conformance = sum(scores) / len(scores)
        result.append({
            "role": role,
            "averageConformance": round(avg_conformance, 4),
            "traceCount": len(scores)
        })

    return result

def get_requested_amount_vs_conformance(xes_path, aligned_traces):
    
    log = xes_importer.apply(xes_path)
    result = []

    for i, trace in enumerate(log):
        trace_attrs = trace.attributes

        # Try both "RequestedAmount" and "Amount" as keys
        requested_amount = (
            trace_attrs.get("RequestedAmount") or
            trace_attrs.get("Amount")
        )

        # If neither exists, skip this trace
        if requested_amount is None:
            continue

        try:
            fitness = aligned_traces[i].get("fitness", 0)
            result.append({
                "conformance": round(fitness, 4),
                "requested_amount": float(requested_amount)
            })
        except Exception as e:
            print(f"Error processing trace {i}: {e}")
            continue

    return result

def get_conformance_by_resource(xes_log, aligned_traces):
    resource_conformance = defaultdict(list)

    for i, trace in enumerate(xes_log):
        fitness = aligned_traces[i].get("fitness", 0)
        for event in trace:
            resource = event.get("org:resource")
            if resource:
                resource_conformance[resource].append(fitness)

    result = []
    for resource, fitness_values in resource_conformance.items():
        avg_fitness = sum(fitness_values) / len(fitness_values)
        result.append({
            "resource": resource,
            "avg_conformance": round(avg_fitness, 4),
            "traceCount": len(fitness_values)  # ✅ fix
        })

    return result
def get_trace_sequences(xes_path):
    if not os.path.exists(xes_path):
        raise FileNotFoundError(f"XES file not found: {xes_path}")
    
    log = xes_importer.apply(xes_path)
    result = []

    for i, trace in enumerate(log):
        sequence = [event["concept:name"] for event in trace if "concept:name" in event]
        result.append({
            "trace": f"Trace {i + 1}",
            "sequence": sequence
        })

    return result

