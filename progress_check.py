import pickle

import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st
from pyvis.network import Network
import pandas as pd
from config import *
import ifcopenshell
from ifcopenshell.api import run
from csv_reader import read_contractor_sequence

if "selected_items" not in st.session_state:
    st.session_state.selected_items = []
    
    st.session_state.nodes_subset = set()
    if SEQUENCE_FLAG:
        st.session_state.nodes_subset = set(["start"])
    st.session_state.ifc_model = ifcopenshell.file()

    project = run("root.create_entity", st.session_state.ifc_model, ifc_class = "IFcProject", name = "My Project")
    run("unit.assign_unit", st.session_state.ifc_model)
    context = run('context.add_context', st.session_state.ifc_model, context_type = "Model")
    body = run("context.add_context",  st.session_state.ifc_model, context_type="Model",
        context_identifier="Body", target_view="MODEL_VIEW", parent=context)

if SEQUENCE_FLAG:
    contractor_sequence = read_contractor_sequence()
    predecessor_map = {key: value for value, key in contractor_sequence}


storey_list = pickle.load(open("storeys_list.pkl", "rb"))

story_option = st.selectbox("Which Story?", [None] + storey_list)

struct_option = st.selectbox("Beam or Column?", [None, "Beam", "Column"])

struct_number = st.selectbox("Number?", [None, 1, 2, 3, 4, 5, 6, 7])

construction_graph = pickle.load(open("construction.graph", "rb"))

load_graph = None

# Button to add selected items to the session state list
if st.button("Add to List"):
    selection = f"{story_option}-{struct_option}-{struct_number}"
    
    if SEQUENCE_FLAG:
        if predecessor_map[selection] not in st.session_state.nodes_subset:
            st.write("selection not in order!")
    elif selection not in construction_graph:
        st.write("selection not in construction graph")
    else:
        
        st.session_state.selected_items.extend([selection])
        # Optionally, you can remove duplicates by converting to a set and back to a list
        st.session_state.selected_items = list(set(st.session_state.selected_items))
        
        if set(nx.ancestors(construction_graph, selection)) <= set(st.session_state.selected_items) or SEQUENCE_FLAG:
            
            st.session_state.nodes_subset = (
                set(st.session_state.selected_items)
                | nx.ancestors(construction_graph, selection)
                | st.session_state.nodes_subset
            )
            if SEQUENCE_FLAG:
                st.session_state.ifc_model.create_entity("IfcStructuralCurveMember", Name=selection)
                st.session_state.ifc_model.write("trial.ifc")
        
        else:   
            st.write("selection not in order!")
            
            load_graph = construction_graph.subgraph(set(nx.ancestors(construction_graph, selection)) | set([selection]))
            
            st.session_state.selected_items.remove(selection)
            
        
    subset_graph = construction_graph.subgraph(st.session_state.nodes_subset)

    nt = Network("500px", "500px", directed=True)
    nt.from_nx(subset_graph)

    # Save and read the HTML file created by Pyvis
    nt.save_graph("nx.html")
    HtmlFile = open("nx.html", "r", encoding="utf-8")

    # Use components.html to render the HTML file in Streamlit
    source_code = HtmlFile.read()
    
    st.components.v1.html(source_code, height=500, width=500)
    st.write(
        f"Completion Percentage: {(max(0, len(st.session_state.nodes_subset)-1))/(len(construction_graph.nodes())-1)*100}%"
    )
    
    if load_graph is not None:
        nt = Network("500px", "500px", directed=True)
        nt.from_nx(load_graph)

        # Save and read the HTML file created by Pyvis
        nt.save_graph("nx1.html")
        HtmlFile = open("nx1.html", "r", encoding="utf-8")

        # Use components.html to render the HTML file in Streamlit
        source_code = HtmlFile.read()
        
        st.components.v1.html(source_code, height=500, width=500)
