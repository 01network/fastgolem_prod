import pandas as pd
import streamlit as st
import random

# Expanded tree structure with more specializations
tree_structure = {
    'Group1': {
        'Classification1': {
            'Specialization1': {'value': {'nucc_code': '001', 'nucc_definition': 'Def1'}},
            'Specialization2': {'value': {'nucc_code': '003', 'nucc_definition': 'Def3'}}
        },
        'Classification2': {
            'Specialization1': {'value': {'nucc_code': '004', 'nucc_definition': 'Def4'}},
            'Specialization2': {'value': {'nucc_code': '005', 'nucc_definition': 'Def5'}}
        }
    },
    'Group2': {
        'Classification1': {
            'Specialization1': {'value': {'nucc_code': '006', 'nucc_definition': 'Def6'}},
            'Specialization2': {'value': {'nucc_code': '007', 'nucc_definition': 'Def7'}}
        },
        'Classification2': {
            'Specialization1': {'value': {'nucc_code': '002', 'nucc_definition': 'Def2'}},
            'Specialization2': {'value': {'nucc_code': '008', 'nucc_definition': 'Def8'}}
        }
    }
}

def parse_tree(node, path=[]):
    """Parse the n-ary tree into a flat structure."""
    rows = []
    if 'value' in node:
        rows.append({
            'Group': path[0] if len(path) > 0 else None,
            'Classification': path[1] if len(path) > 1 else None,
            'Specialization': path[2] if len(path) > 2 else None,
            'NUCC Code': node['value'].get('nucc_code', None),
            'NUCC Definition': node['value'].get('nucc_definition', None)
        })
    for key, child in node.items():
        if key != 'value':
            rows.extend(parse_tree(child, path + [key]))
    return rows

# Create DataFrame from tree structure
tree_data = parse_tree(tree_structure)
df_nary_tree = pd.DataFrame(tree_data)
tree_dict = df_nary_tree.set_index(['Group', 'Classification', 'Specialization']).to_dict('index')

# Generate synthetic DataFrame of individuals
def create_synthetic_individuals(num_individuals):
    random.seed(42)
    nucc_codes = ['001', '002', '003', '004', '005', '006', '007', '008']
    data = {
        'Name': [f'Person{i}' for i in range(1, num_individuals + 1)],
        'Age': [random.randint(20, 60) for _ in range(num_individuals)],
        'Gender': [random.choice(['Male', 'Female']) for _ in range(num_individuals)],
        'NUCC Code': [random.choice(nucc_codes) for _ in range(num_individuals)]
    }
    return pd.DataFrame(data)

df_individuals = create_synthetic_individuals(100)

def get_filtered_nucc_codes(tree_dict, selections):
    nucc_codes = []
    for key, value in tree_dict.items():
        if all(sel in key for sel in selections):
            nucc_codes.append(value['NUCC Code'])
    return nucc_codes

def display_data(filtered_data):
    st.write(filtered_data)

# Main Streamlit app logic
def main():
    st.sidebar.title("Filter Options")
    groups = sorted(list(set(df_nary_tree['Group'].dropna())))
    selected_group = st.sidebar.selectbox('Select Group', [''] + groups)

    if selected_group:
        classifications = sorted(list(set(df_nary_tree[df_nary_tree['Group'] == selected_group]['Classification'].dropna())))
        selected_classification = st.sidebar.selectbox('Select Classification', [''] + classifications)

        if selected_classification:
            specializations = sorted(list(set(df_nary_tree[(df_nary_tree['Group'] == selected_group) & (df_nary_tree['Classification'] == selected_classification)]['Specialization'].dropna())))
            selected_specialization = st.sidebar.selectbox('Select Specialization', [''] + specializations)

            if selected_specialization:
                selections = [selected_group, selected_classification, selected_specialization]
            else:
                selections = [selected_group, selected_classification]
        else:
            selections = [selected_group]
    else:
        selections = []

    if selections:
        nucc_codes = get_filtered_nucc_codes(tree_dict, selections)
        filtered_data = df_individuals[df_individuals['NUCC Code'].isin(nucc_codes)].copy()
        display_data(filtered_data)

if __name__ == "__main__":
    main()
