import streamlit as st
import json
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

st.header("Health Care Practitioner Database", divider='orange')

# Caching the loading of the JSON structure
@st.cache_data
def load_json(file_path):
    logger.info(f"Initiating load_json function")
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            logger.info(f"JSON file {file_path} loaded successfully")
        return data
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {e}")
        st.error(f"Error loading JSON file {file_path}: {e}")
        return {}

# Caching the loading of the CSV data
@st.cache_data
def load_csv(file_path):
    logger.info(f"Initiating load_csv function")
    try:    
        # Specify the data types for problematic columns
        dtype = {
            'full_name': str,
            'taxon_code': str,
            'taxon_state': str,
            'nucc_group':str,
            'nucc_classification':str,
            'nucc_specialization':str,
            'individual_state': str,
            'individual_place': str,
            'individual_zip5': str,  # Ensure individual_zip5 is treated as string
            'individual_county':str,
            'individual_state':str,
            'facility_name':str,
            'facility_place':str,
            'facility_zip5': str,    # Ensure facility_zip5 is treated as string
            'facility_state':str,
            'medical_school':str,
            # 'tenure':float,
            # 'graduation_year':float,
            'gender':str,
            'full_name_other':str,
            'sole_proprietor': bool,
            'npi': str,
            'npi_replacement': str,
            'medicare_id':str,
            'telehealth':bool,
            'medicare_specialty':str,
            'county_code':str,
            'geo_id':str,
            'lat':float,
            'long':float,
            'dni':str
        }
        date_cols = ['enumeration_date', 'last_update_date']
        logger.info(f"Ingesting HCP data from {file_path}.")
        df = pd.read_csv(
            file_path,
            dtype=dtype, 
            low_memory=False
            )
        logger.info(f"CSV file {file_path} successfully loaded")
        # df[date_cols] = pd.to_datetime(df[date_cols], format='%Y/%m/%d')
        # logger.info(f"Conversion of {str(date_cols)} to datetime format complete")
        # df['tenure'] = df['tenure'].fillna(0).astype(int)
        # logger.info(f"Conversion of tenure column to integer format complete")
        # df['graduation_year'] = df['graduation_year'].fillna(0).astype(int)
        # logger.info(f"Conversion of graduation_year column to integer format complete")
        return df
    except Exception as e:
        logger.error(f"Error loading CSV file {file_path}: {e}")
        st.error(f"Error loading CSV file {file_path}")
        return pd.DataFrame()         

# Load the JSON structure
json_file_path = '.data/nucc_tree.json'
tree_dict = load_json(json_file_path)

# Load the CSV data
csv_file_path = '.data/hcp_data.csv'
df = load_csv(csv_file_path)

def get_next_level_options(tree, selections):
    """Get options for the next level based on current selection"""
    logger.info(f"get_next_level_option function called")
    node = tree
    for selection in selections:
        if selection in node:
            node = node[selection]
        else:
            return []
    return [key for key in node.keys() if key != 'value']

def filter_data_by_classification(tree, group, classification, df):
    """Filter data by selected classification"""
    logger.info(f"filter_data_by_classification function called")
    node = tree[group][classification]
    filtered_taxon_codes = [node[specialization]['value'].get('nucc_code', 'null')
                            for specialization in node 
                            if specialization != 'value' and 'value' in node[specialization]
                            ]
    return df[df['taxon_code'].isin(filtered_taxon_codes)].copy()

def filter_data_by_group(tree, group, df):
    """Filter data by selected group"""
    logger.info(f"filter_data_by_group function called")
    node = tree[group]
    filtered_taxon_codes = []
    for classification in node:
        class_node = node[classification]
        for specialization in class_node:
            if specialization != 'value' and 'value' in class_node[specialization]:
                filtered_taxon_codes.append(class_node[specialization]['value'].get('nucc_code', 'null'))
    return df[df['taxon_code'].isin(filtered_taxon_codes)].copy()

# Sidebar for n-ary tree search
st.sidebar.title('FastGolem Search')
st.sidebar.write(f"You are logged in as {st.session_state.role}")

# Dropdown for group level
groups = sorted(list(tree_dict.keys()))
selected_group = st.sidebar.selectbox('Select Group', [''] + groups, help='Defines the type of practitioner by education')

if selected_group:
    filtered_data = df[df['taxon_code'] == selected_group].copy()

    # Dropdown for classification level
    classifications = sorted(get_next_level_options(tree_dict, [selected_group]))
    selected_classification = st.sidebar.selectbox('Select Classification', [''] + classifications, help='Defines the primary function of the practitioner')

    if selected_classification:
        # Further filter the data based on the selected classification
        filtered_data = filtered_data[filtered_data['nucc_classification'] == selected_classification].copy()

        # Dropdown for specialization level
        specializations = sorted(get_next_level_options(tree_dict, [selected_group, selected_classification]))
        selected_specialization = st.sidebar.selectbox('Select Specialization', [''] + specializations, help='Defines niche roles of the practitioner')

        # Determine the selected node and get the NUCC code and definition
        if selected_specialization:
            node = tree_dict[selected_group][selected_classification][selected_specialization]
            nucc_code = node['value'].get('nucc_code', 'null')
            # Filter the CSV data based on the selected taxon_code
            filtered_data = df[df['taxon_code'] == nucc_code].copy()
        else:
            node = tree_dict[selected_group][selected_classification]
            filtered_taxon_codes = []
            for specialization in node:
                if specialization != 'value' and 'value' in node[specialization]:
                    filtered_taxon_codes.append(node[specialization]['value'].get('nucc_code', 'null'))
            filtered_data = df[df['taxon_code'].isin(filtered_taxon_codes)].copy()


        # Rename columns for better display
        filtered_data = filtered_data.rename(columns={
                    'full_name':'Full Name',
                    'taxon_code':'Taxon Code',
                    'taxon_state':'License State',
                    'nucc_group':'NUCC Group',
                    'nucc_classification':'NUCC Classification',
                    'nucc_specialization':'NUCC Specialization',
                    'individual_state': 'Individual State',
                    'individual_place': 'Individual Place',
                    'individual_zip5': 'Individual Post Code', 
                    'individual_county':'Individual County',
                    'individual_state':'Individual State',
                    'facility_name':'Facility Name',
                    'facility_place':'Facility Place',
                    'facility_zip5': 'Facility Postcode',
                    'facility_state':'Facility State',
                    'medical_school':'Medical School',
                    'tenure':'Tenure',
                    'graduation_year':'Graduation Year',
                    'gender':'Gender',
                    'full_name_other':'Full Name, other',
                    'sole_proprietor': 'Sole Proprietor',
                    'npi': 'NPI',
                    'npi_replacement': 'NPI, other',
                    'medicare_id':'Medicare ID',
                    'telehealth':'Telehealth',
                    'medicare_specialty':'Medicare Specialty',
                    'county_code':'County Code',
                    'geo_id':'Geo ID',
                    'lat':'Latitude',
                    'long':'Longitude',
                    'dni':'DNI'
        })

        # Set default columns to display
        default_columns = ['Full Name', 'License State', 'NUCC Group', 'NUCC Classification', 'NUCC Specialization']

        # Allow the user to select which additional fields to display
        st.sidebar.header("Additional Display Options")
        columns = [col for col in filtered_data.columns if col not in default_columns]
        additional_columns = st.sidebar.multiselect('Select Additional Columns to Display', columns)

        # Combine default and additional columns
        displayed_columns = default_columns + additional_columns

        # Grouping the data should be done on the filtered_data DataFrame
        grouped_data = filtered_data.groupby(displayed_columns, as_index=False).first()

        st.write(f"Number of possible candidates: {len(grouped_data)}")

        st.markdown(
        """
        <style>
        .dataframe { width: 100% !important; }
        </style>
        """, unsafe_allow_html=True
        )

        # Display the combined table
        st.write("Displayed Data:")
        event = st.dataframe(
            grouped_data[displayed_columns], 
            key='combined_editor',
            on_select="rerun",
            selection_mode="multi-row")    

        logger.info(f"selected rows {event.selection}")

else:
    st.write("Please select a classification.")