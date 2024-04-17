import pickle

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import sys
import ifcopenshell
import ifcopenshell.geom
from csv_reader import read_contractor_sequence
from config import *

model = ifcopenshell.open("DIM_000690200_ZGF_Redesign Conformed DIM STRUCTURAL_20240315.ifc")
construction_graph = nx.DiGraph()
sequence = {}
member_name_map = {}

try:
    # Finding out what story, and iterating for every
    for storey in model.by_type("IFCBUILDINGSTOREY"):

        print(storey.get_info()["Name"])
        sequence[storey.get_info()["Name"]] = {}

        
        for curve_member in storey.ContainsElements[0].RelatedElements:

            product_definition = curve_member.Representation
            topology_representation = product_definition.Representations[0]
            edge = topology_representation.Items[0]
            start = edge.EdgeStart
            end = edge.EdgeEnd
            start_coordinates = start.VertexGeometry.Coordinates
            end_coordinates = end.VertexGeometry.Coordinates
            type_of_struct = None
            if (start_coordinates[0], start_coordinates[1]) == (
                end_coordinates[0],
                end_coordinates[1],
            ):
                type_of_struct = "Column"

            else:
                type_of_struct = "Beam"

            if type_of_struct not in sequence[storey.get_info()["Name"]]:
                sequence[storey.get_info()["Name"]][type_of_struct] = 1
            else:
                sequence[storey.get_info()["Name"]][type_of_struct] += 1

            if (start_coordinates[0], start_coordinates[1]) == (
                end_coordinates[0],
                end_coordinates[1],
            ):
                print(
                    "Column",
                    start_coordinates,
                    end_coordinates,
                    f"{storey.get_info()['Name']}-{type_of_struct}-{sequence[storey.get_info()['Name']][type_of_struct]}",
                )

            else:
                print(
                    "Beam",
                    start_coordinates,
                    end_coordinates,
                    f"{storey.get_info()['Name']}-{type_of_struct}-{sequence[storey.get_info()['Name']][type_of_struct]}",
                )

            construction_graph.add_node(
                f"{storey.get_info()['Name']}-{type_of_struct}-{sequence[storey.get_info()['Name']][type_of_struct]}",
                start_coordinates=start_coordinates,
                end_coordinates=end_coordinates,
                type_of_struct=type_of_struct,
                built = False
            )

            member_name_map[curve_member] = (
                f"{storey.get_info()['Name']}-{type_of_struct}-{sequence[storey.get_info()['Name']][type_of_struct]}"
            )

            if storey.get_info()["Name"] == "Base" and type_of_struct == "Column":
                continue

            if type_of_struct == "Column":
                nodes = construction_graph.nodes(data=True)
                for node in nodes:
                    # print(node[1])
                    if (
                        node[1]["end_coordinates"][:2] == start_coordinates[:2]
                        and abs(node[1]["end_coordinates"][2] - start_coordinates[2])
                        < 3
                    ):
                        construction_graph.add_edge(
                            node[0],
                            f"{storey.get_info()['Name']}-{type_of_struct}-{sequence[storey.get_info()['Name']][type_of_struct]}",
                        )

            if type_of_struct == "Beam":
                nodes = construction_graph.nodes(data=True)
                for node in nodes:
                    if node[1]["type_of_struct"] != "Column":
                        continue

                    if abs(
                        node[1]["end_coordinates"][2] - start_coordinates[2]
                    ) < 3 or (
                        node[1]["start_coordinates"][2]
                        < start_coordinates[2]
                        < node[1]["end_coordinates"][2]
                    ):
                        if (
                            abs(node[1]["end_coordinates"][0] - start_coordinates[0])
                            < 3
                            and abs(
                                node[1]["end_coordinates"][1] - start_coordinates[1]
                            )
                            < 3
                        ):

                            construction_graph.add_edge(
                                node[0],
                                f"{storey.get_info()['Name']}-{type_of_struct}-{sequence[storey.get_info()['Name']][type_of_struct]}",
                            )

                    if abs(node[1]["end_coordinates"][2] - end_coordinates[2]) < 3 or (
                        node[1]["start_coordinates"][2]
                        < start_coordinates[2]
                        < node[1]["end_coordinates"][2]
                    ):
                        if (
                            abs(node[1]["end_coordinates"][0] - end_coordinates[0]) < 3
                            and abs(node[1]["end_coordinates"][1] - end_coordinates[1])
                            < 3
                        ):

                            construction_graph.add_edge(
                                node[0],
                                f"{storey.get_info()['Name']}-{type_of_struct}-{sequence[storey.get_info()['Name']][type_of_struct]}",
                            )

                    if abs(
                        node[1]["start_coordinates"][2] - start_coordinates[2]
                    ) < 3 or (
                        node[1]["start_coordinates"][2]
                        < start_coordinates[2]
                        < node[1]["end_coordinates"][2]
                    ):
                        if (
                            abs(node[1]["start_coordinates"][0] - start_coordinates[0])
                            < 3
                            and abs(
                                node[1]["start_coordinates"][1] - start_coordinates[1]
                            )
                            < 3
                        ):
                            construction_graph.add_edge(
                                node[0],
                                f"{storey.get_info()['Name']}-{type_of_struct}-{sequence[storey.get_info()['Name']][type_of_struct]}",
                            )

                    if abs(
                        node[1]["start_coordinates"][2] - end_coordinates[2]
                    ) < 3 or (
                        node[1]["start_coordinates"][2]
                        < start_coordinates[2]
                        < node[1]["end_coordinates"][2]
                    ):
                        if (
                            abs(node[1]["start_coordinates"][0] - end_coordinates[0])
                            < 3
                            and abs(
                                node[1]["start_coordinates"][1] - end_coordinates[1]
                            )
                            < 3
                        ):
                            construction_graph.add_edge(
                                node[0],
                                f"{storey.get_info()['Name']}-{type_of_struct}-{sequence[storey.get_info()['Name']][type_of_struct]}",
                            )

        print()
except Exception as e:
    print(e)
    print("No more structures")

relconnect_list = model.by_type("IFCRELCONNECTSSTRUCTURALMEMBER")
point_connection_idx = 1
point_connection_map = {}
for edge in relconnect_list:
    curve_member = edge.RelatingStructuralMember
    point_connection = edge.RelatedStructuralConnection

    if point_connection not in point_connection_map:
        # construction_graph.add_node(f"pc{point_connection_idx}")
        point_connection_map[point_connection] = [f"pc{point_connection_idx}", []]
        point_connection_idx += 1

    point_connection_map[point_connection][1].append(member_name_map[curve_member])
    # construction_graph.add_edge(u_of_edge= member_name_map[parent_node], v_of_edge=point_connection_map[child_node])

# print(point_connection_map)

edge_labels = []
construction_edges = construction_graph.edges()
for edge in construction_edges:
    parent, child = edge
    for key in point_connection_map:
        if (
            parent in point_connection_map[key][1]
            and child in point_connection_map[key][1]
        ):
            edge_labels.append(((parent, child), point_connection_map[key][0]))
            nx.set_edge_attributes(
                construction_graph,
                {(parent, child): {"label": point_connection_map[key][0]}},
            )
            break

if SEQUENCE_FLAG:
    
    construction_graph.add_node(
            "start",
            start_coordinates=None,
            end_coordinates=None,
            type_of_struct=None,
            built = False
        )
    
    built_nodes = set(["start"])
    contractor_sequence = read_contractor_sequence()
    
    # if len(nx.ancestors(construction_graph, first_node)) == 0:
    #     built_nodes.add(first_node)
    # else:
    #     print(f"Construction sequence does not follow load path, first node out of order")
    #     sys.exit(0)
    
    for edge in contractor_sequence:
        
        parent = edge[0]
        child = edge[1]
        
        
        if parent not in built_nodes:
            print(f"Construction sequence does not follow load path, {parent} not built for {child}")
            sys.exit(0)
        
        parents = list(set(nx.ancestors(construction_graph, child)))
        list_of_parents = []
        for par in parents:
            list_of_parents.append(par not in built_nodes)

        if any(list_of_parents):
            not_present = [parents[idx] for idx, val in enumerate(list_of_parents) if val]
            print(f"Construction sequence does not follow load path, {not_present} not built for {child}")
            sys.exit(0)
        
        if edge not in construction_edges:
            construction_graph.add_edge(
                u_of_edge=edge[0], v_of_edge=edge[1], label="conseq"
            )
            edge_labels.append((edge, "conseq"))

        built_nodes.add(child)

edge_labels = dict(edge_labels)
pos = nx.shell_layout(construction_graph)
nx.draw(
    construction_graph,
    pos,
    with_labels=True,
    node_size=100,
    node_color="pink",
    font_size=6,
)
nx.draw_networkx_edge_labels(construction_graph, pos, edge_labels=edge_labels)


plt.show()

pickle.dump(construction_graph, open("construction.graph", "wb"))
pickle.dump(list(sequence.keys()), open("storeys_list.pkl", "wb"))
