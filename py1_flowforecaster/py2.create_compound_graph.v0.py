import sys
import argparse
import time
import os
import numpy as np
import networkx as nx

sys.path.append("../utils")
from py_lib_flowforecaster import EdgeType, VertexType
from py_lib_flowforecaster import show_dag


def get_task_prefix(task):
    return task.rsplit("_taskid", 1)[0]


def get_file_prefix(file):
    return file.rsplit("_fileid", 1)[0]


def get_common_suffix(strings):
    if len(strings) == 1:
        return strings[0]

    common_suffix = strings[0]
    for str_i in range(1, len(strings)):
        curr = strings[str_i]
        i = len(common_suffix) - 1
        j = len(curr) - 1
        suffix = ""
        while i >= 0 and j >= 0 and common_suffix[i] == curr[j]:
            suffix = common_suffix[i] + suffix
            i -= 1
            j -= 1
        common_suffix = suffix

    return common_suffix


def get_compound_file_name(file_vertices):
    filenames = []
    for v in file_vertices:
        basename, ext = os.path.splitext(v)
        basename = basename.split("_fileid")[0]
        filenames.append(basename + ext)

    if len(filenames) == 1:
        return filenames[0]

    common_prefix = os.path.commonprefix(filenames)
    common_suffix = get_common_suffix(filenames)
    if common_prefix == "" and common_suffix == "":
        return filenames[0]
    else:
        return common_prefix + common_suffix


def add_edge_to_graph(G,
                      src,
                      dst,
                      attr):
    G.add_edge(src, dst, **attr)
    # G.nodes[src]["type"] = src_type
    # G.nodes[dst]["type"] = dst_type


def set_vertex_attr(G,
                    vertex,
                    attr):
    for key, val in attr.items():
        G.nodes[vertex][key] = val


def compound(filename: str):
    print(f"graphml_file: {filename}")
    G = nx.read_graphml(filename)

    """
    Topological generations
    """
    generations = nx.topological_generations(G)
    vertex_levels = []
    print(f"\nGenerations(topological_generations):")
    for layer, nodes in enumerate(generations):
        vertex_levels.append(nodes)
        print(f"layer: {layer} nodes: {nodes}")

    task_set = set()

    """
    Construct the compound graph
    """
    compound_graph = nx.DiGraph()
    num_levels = len(vertex_levels)
    for level in range(1, num_levels, 2):
        # Iterate the task levels
        tasks = vertex_levels[level]

        # Classify tasks
        task_clusters = {}
        for task in tasks:
            task_prefix = get_task_prefix(task)
            if task_prefix not in task_clusters:
                task_clusters[task_prefix] = set()
            task_clusters[task_prefix].add(task)

        if task_prefix in task_set:
            # TODO
            # this is boundary
            pass

        # Add edges from files to tasks
        for task_prefix, tasks in task_clusters.items():
            if len(tasks) > 1:
                # Could be a fan-out edge
                # find out all possible sources to this cluster
                source_to_ends_info = {}
                for task in tasks:
                    for src in G.predecessors(task):
                        if src not in source_to_ends_info:
                            source_to_ends_info[src] = {"num_ends": 0, "weights": []}
                        # Get edge statistics
                        source_to_ends_info[src]["num_ends"] += 1
                        source_to_ends_info[src]["weights"].append(np.float64(G[src][task]["weight"]))
                # Add the compound edge
                for src, info in source_to_ends_info.items():
                    file_name = get_compound_file_name([src])
                    if info["num_ends"] > 1:
                        """
                        Fan-out edge
                        """
                        add_edge_to_graph(G=compound_graph,
                                          src=file_name,
                                          dst=task_prefix,
                                          attr={
                                              "type": EdgeType.FAN_OUT,
                                              "num_tasks": info["num_ends"],
                                              "weight": np.mean(info["weights"]),  # mean or sum
                                          })
                        if level == 1:
                            # Set level 0 files
                            set_vertex_attr(G=compound_graph,
                                            vertex=file_name,
                                            attr={
                                                "type": VertexType.FILE,
                                                "size": np.float64(G.nodes[src]["size"])
                                            })
                        set_vertex_attr(G=compound_graph,
                                        vertex=task_prefix,
                                        attr={
                                            "type": VertexType.TASK,
                                        })
                    elif info["num_ends"] == 1:
                        """
                        Sequential edge
                        """
                        # edge_type = EdgeType.SEQ
                        # weight = info["weights"][0]
                        # compound_graph.add_edge(src, task_prefix,
                        #                         type=edge_type, num_tasks=1, weight=weight)
                        add_edge_to_graph(G=compound_graph,
                                          src=src,
                                          dst=task_prefix,
                                          attr={
                                              "type": EdgeType.SEQ,
                                              "num_tasks": 1,
                                              "weight": info["weights"][0]
                                          })
                        if level == 1:
                            # Set level 0 files
                            set_vertex_attr(G=compound_graph,
                                            vertex=src,
                                            attr={
                                                "type": VertexType.FILE,
                                                "size": np.float64(G.nodes[src]["size"])
                                            })
                        set_vertex_attr(G=compound_graph,
                                        vertex=task_prefix,
                                        attr={
                                            "type": VertexType.TASK,
                                        })
                    else:
                        raise Exception(f"Should never happen. info={info}")
                pass  # end Could be a fan-out edge
            elif len(tasks) == 1:
                # Could be a fin-in edge
                task = next(iter(tasks))  # the only element
                if G.in_degree(task) > 1:
                    """
                    Fin-in edge
                    """
                    # Get edge statistics
                    info = {"weights": []}
                    for src in G.predecessors(task):
                        info["weights"].append(np.float64(G[src][task]["weight"]))
                    file_name = get_compound_file_name(G.predecessors(task))
                    # Add the compound edge
                    add_edge_to_graph(G=compound_graph,
                                      src=file_name,
                                      dst=task_prefix,
                                      attr={
                                          "type": EdgeType.FAN_IN,
                                          "num_tasks": 1,
                                          "weight": np.sum(info["weights"])
                                      })
                    if level == 1:
                        # Set level 0 files
                        set_vertex_attr(G=compound_graph,
                                        vertex=file_name,
                                        attr={
                                            "type": VertexType.FILE,
                                            "size": np.mean(G.predecessors(task))
                                        })
                    set_vertex_attr(G=compound_graph,
                                    vertex=task_prefix,
                                    attr={
                                        "type": VertexType.TASK,
                                    })
                elif G.in_degree(task) == 1:
                    """
                    Sequential edge
                    """
                    src = next(iter(G.predecessors(task)))  # the only predecessor
                    file_name = get_compound_file_name([src])
                    # Add the compound edge
                    add_edge_to_graph(G=compound_graph,
                                      src=file_name,
                                      dst=task_prefix,
                                      attr={
                                          "type": EdgeType.SEQ,
                                          "num_tasks": 1,
                                          "weight": np.float64(G[src][task]["weight"])
                                      })
                    if level == 1:
                        # Set level 0 files
                        set_vertex_attr(G=compound_graph,
                                        vertex=file_name,
                                        attr={
                                            "type": VertexType.FILE,
                                            "size": np.float64(G.nodes[src]["size"])
                                        })
                    set_vertex_attr(G=compound_graph,
                                    vertex=task_prefix,
                                    attr={
                                        "type": VertexType.TASK
                                    })
                else:
                    raise Exception(f"Should never happen. G.predecessors(task) = {G.predecessors(task)}")
                pass  # end Could be a fin-in edge
            else:
                raise Exception(f"Should never happen. len(tasks) = {len(tasks)}")

        """
        Add edges from tasks to sequential files. These edges are all sequential.
        """
        for task_prefix, tasks in task_clusters.items():
            # Get files statistics
            info = {"files": [], "weights": [], "sizes": []}
            for task in tasks:
                for file in G.successors(task):
                    info["files"].append(file)
                    info["weights"].append(np.float64(G[task][file]["weight"]))
                    info["sizes"].append(np.float64(G.nodes[file]["size"]))
            file_name = get_compound_file_name(info["files"])
            # Add the compound edge
            add_edge_to_graph(G=compound_graph,
                              src=task_prefix,
                              dst=file_name,
                              attr={
                                  "type": EdgeType.SEQ,
                                  "num_tasks": 1,
                                  "weight": np.mean(info["weights"])
                              })
            set_vertex_attr(G=compound_graph,
                            vertex=file_name,
                            attr={
                                "type": VertexType.FILE,
                                "size": np.mean(info["sizes"])
                            })
        pass  # end this level

    # test
    # show_dag(compound_graph)
    basename = os.path.splitext(os.path.basename(filename))[0]
    compound_filename = f"{basename}.compound.graphml"
    nx.write_graphml(G=compound_graph, path=compound_filename)
    # end test

    """
    Continue traverse, collect statistics into the compound graph.
    """
    # TODO


if __name__ == "__main__":
    parser = argparse.ArgumentParser(f"{sys.argv[0]}")
    parser.add_argument("graphml_file", type=str, help="input GraphML file")
    # parser.add_argument("-i", "--iterations", type=int, default=3, help="number of iterations to synthesize")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(-1)
    args = parser.parse_args()

    tt_time_start = time.perf_counter()

    graphml_file = args.graphml_file
    compound(graphml_file)

    tt_time_end = time.perf_counter()
    print(f"total_exe_time(s): {tt_time_end - tt_time_start}")