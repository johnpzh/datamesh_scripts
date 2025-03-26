import sys
import os
import argparse
import time
import copy
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint
import pandas as pd
from sortedcontainers import SortedSet

sys.path.append("../utils")
from py_lib import check_is_data


def rename_task(old_name: str, taskid_dict: dict):
    basename = old_name.rsplit("_", 1)[0]
    if basename in taskid_dict:
        taskid_dict[basename] += 1
    else:
        taskid_dict[basename] = 0
    taskid = taskid_dict[basename]
    new_name = basename + "_taskid" + str(taskid)
    return new_name


def rename_file(old_name: str, fileid_dict: dict):
    basename, ext = os.path.splitext(old_name)
    if basename in fileid_dict:
        fileid_dict[basename] += 1
    else:
        fileid_dict[basename] = 0
    fileid = fileid_dict[basename]
    new_name = basename + "_fileid" + str(fileid) + ext
    return new_name


def rename_task_plus_one(old_name: str, taskid_dict: dict):
    basename = old_name.rsplit("_taskid", 1)[0]
    taskid_dict[basename] += 1
    taskid = taskid_dict[basename]
    new_name = basename + "_taskid" + str(int(taskid))
    return new_name


def rename_file_plus_one(old_name: str, fileid_dict: dict):
    basename, ext = os.path.splitext(old_name)
    basename, id = basename.rsplit("_fileid", 1)
    fileid_dict[basename] += 1
    fileid = fileid_dict[basename]
    new_name = basename + "_fileid" + str(int(fileid)) + ext
    return new_name


def get_root_tasks(G):
    root_files = [node for node in G.nodes if G.in_degree(node) == 0]
    root_tasks = set()
    for file in root_files:
        for task in G.successors(file):
            root_tasks.add(task)
    return list(root_tasks)


def get_leafs(G):
    leafs = [node for node in G.nodes if G.out_degree(node) == 0]
    return leafs


def get_new_roots(origin_roots: list, map_nodes_old_to_new: dict):
    new_roots = [map_nodes_old_to_new[node] for node in origin_roots]
    return new_roots


def get_new_leafs(origin_leafs: list, map_nodes_old_to_new: dict):
    new_leafs = [map_nodes_old_to_new[node] for node in origin_leafs]
    return new_leafs


def get_bridge_edges(src_list: list, end_list: list):
    """
    In round-robin order, each src connects to each end
    """
    src_length = len(src_list)
    end_length = len(end_list)
    max_length = max(src_length, end_length)
    bridge_edges = [(src_list[ind % src_length], end_list[ind % end_length], {'weight': 0})
                    for ind in range(max_length)]
    return bridge_edges


def synthesize(filename: str, iterations: int):
    """
    data:
    * attr['ntype'] == 'file' and 'abspath' in attr
    * id has extension [".vcf", ".gz", ".txt"]

    task name patterns: xxx_taskid000
    file name patterns: xxx_fileid000
    """
    print(f"graphml_file: {filename}")
    print(f"iterations: {iterations}")
    if iterations < 2:
        print(f"Only {iterations} iterations. Return.")
        return
    G = nx.read_graphml(filename)

    """
    Determine vertex type
    """
    new_attr_set = {}
    for node, attr in G.nodes(data=True):
        # print(f"node: {node} attr: {attr}")
        if check_is_data(node, attr):
            attr['ntype'] = 'file'
            new_attr_set[node] = attr
        else:
            attr['ntype'] = 'task'
    nx.set_node_attributes(G, values=new_attr_set)

    # # test
    # for node, attr in G.nodes(data=True):
    #     if attr['ntype'] == 'task':
    #         print(node)
    # # end test

    """
    Rename Task IDs
    """
    taskid_dict = {}
    fileid_dict = {}
    node_mapping = {}
    for node, attr in G.nodes(data=True):
        if attr['ntype'] == 'file':
            new_name = rename_file(node, fileid_dict)
            node_mapping[node] = new_name
        else:
            new_name = rename_task(node, taskid_dict)
            node_mapping[node] = new_name
    nx.relabel_nodes(G, mapping=node_mapping, copy=False)
    # test
    print("\nRenamed graph:")
    pprint(list(G.nodes))
    print(f"num_nodes: {G.number_of_nodes()} num_edges: {G.number_of_edges()}")
    # end test

    """
    Get roots and leafs
    """
    # origin_roots = get_roots(G)
    oritin_root_tasks = get_root_tasks(G)
    origin_leafs = get_leafs(G)
    old_leafs = copy.deepcopy(origin_leafs)

    """
    Synthesize the new Graph
    """
    new_G = nx.DiGraph(G)
    for iteration in range(iterations - 1):
        # Create new nodes
        map_nodes_old_to_new = {}
        new_nodes_list = []
        for node, attr in G.nodes(data=True):
            if G.in_degree(node) == 0:
                # Skip the first level of files
                continue
            if attr['ntype'] == 'file':
                new_name = rename_file_plus_one(node, fileid_dict)
            else:
                new_name = rename_task_plus_one(node, taskid_dict)
            new_nodes_list.append((new_name, attr))
            map_nodes_old_to_new[node] = new_name

        # Create new edges
        new_edges_list = []
        for src, end, attr in G.edges(data=True):
            if G.in_degree(src) == 0:
                # Skip the first level of files
                continue
            new_src = map_nodes_old_to_new[src]
            new_end = map_nodes_old_to_new[end]
            new_edges_list.append((new_src, new_end, attr))

        # Add new nodes and edges
        # # test
        # print("\nnew_nodes_list")
        # pprint(new_nodes_list)
        # # end test
        new_G.add_nodes_from(new_nodes_list)
        new_G.add_edges_from(new_edges_list)
        # print(f"\n183 num_nodes: {new_G.number_of_nodes()} num_edges: {new_G.number_of_edges()}")

        # Connect old leaf nodes to new roots
        new_root_tasks = get_new_roots(oritin_root_tasks, map_nodes_old_to_new)
        new_leafs = get_new_leafs(origin_leafs, map_nodes_old_to_new)
        bridge_edges = get_bridge_edges(src_list=old_leafs, end_list=new_root_tasks) # old_leafs -> new_roots
        new_G.add_edges_from(bridge_edges)
        # # test
        # print("\nnew_roots")
        # pprint(new_roots)
        # print("\nnew_leafs")
        # pprint(new_leafs)
        # print("\nbridge_edges")
        # pprint(bridge_edges)
        # # end test
        old_leafs = new_leafs

        # print(f"\ni:{iteration} num_nodes: {new_G.number_of_nodes()} num_edges: {new_G.number_of_edges()}")

    print(f"\nNew graph:")
    pprint(list(new_G.nodes))
    print(f"num_nodes: {new_G.number_of_nodes()} num_edges: {new_G.number_of_edges()}")

    # Save the new Graph
    basename = os.path.splitext(os.path.basename(filename))[0]
    new_filename = basename + ".iter-" + str(iterations) + ".graphml"
    nx.write_graphml(new_G, new_filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(f"{sys.argv[0]}")
    parser.add_argument("graphml_file", type=str, help="input GraphML file")
    parser.add_argument("-i", "--iterations", type=int, default=3, help="number of iterations to synthesize")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(-1)
    args = parser.parse_args()

    tt_time_start = time.perf_counter()

    graphml_file = args.graphml_file
    iterations = args.iterations
    # print_graphml(graphml_file)
    synthesize(graphml_file, iterations)

    tt_time_end = time.perf_counter()
    print(f"total_exe_time(s): {tt_time_end - tt_time_start}")

