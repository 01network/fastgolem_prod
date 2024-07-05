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
    logger.info("get_next_level_option function called")
    node = tree
    for selection in selections:
        if selection in node:
            node = node[selection]
        else:
            return []
    return [key for key in node.keys() if key != 'value']

def get_all_taxon_codes(node):
    """Recursively get all taxon codes from a node and its children"""
    taxon_codes = []
    if 'value' in node:
        taxon_codes.append(node['value'].get('nucc_code', 'null'))
    for key in node:
        if key != 'value' and isinstance(node[key], dict):
            taxon_codes.extend(get_all_taxon_codes(node[key]))
    return taxon_codes

def filter_data_by_group(tree, group, df):
    """Filter data by selected group using taxon_code of all child and grandchild nodes"""
    logger.info("filter_data_by_group function called")
    node = tree[group]
    filtered_taxon_codes = get_all_taxon_codes(node)
    if not filtered_taxon_codes:
        # If no taxon codes are found in the group, use the group's own code
        filtered_taxon_codes = [group]
    return df[df['taxon_code'].isin(filtered_taxon_codes)].copy()

# Sidebar for n-ary tree search
st.sidebar.title('FastGolem Search')
st.sidebar.write(f"You are logged in as {st.session_state.role}")

# Dropdown for group level
groups = sorted(list(tree_dict.keys()))
selected_group = st.sidebar.selectbox('Select Group', [''] + groups, help='Defines the type of practitioner by education', key='group_selectbox')

if selected_group:
    filtered_data = filter_data_by_group(tree_dict, selected_group, df)

    # Dropdown for classification level
    classifications = sorted(get_next_level_options(tree_dict, [selected_group]))
    selected_classification = st.sidebar.selectbox('Select Classification', [''] + classifications, help='Defines the primary function of the practitioner', key='classification_selectbox')

    if selected_classification:
        # Further filter the data based on the selected classification
        filtered_data = filtered_data[filtered_data['nucc_classification'] == selected_classification].copy()

        # Dropdown for specialization level
        specializations = sorted(get_next_level_options(tree_dict, [selected_group, selected_classification]))
        selected_specialization = st.sidebar.selectbox('Select Specialization', [''] + specializations, help='Defines niche roles of the practitioner', key='specialization_selectbox')

        # Determine the selected node and get the NUCC code and definition
        if selected_specialization:
            node = tree_dict[selected_group][selected_classification][selected_specialization]
            nucc_code = node['value'].get('nucc_code', 'null')
            # Filter the CSV data based on the selected taxon_code
            filtered_data = df[df['taxon_code'] == nucc_code].copy()
        else:
            node = tree_dict[selected_group][selected_classification]
            filtered_taxon_codes = get_all_taxon_codes(node)
            filtered_data = df[df['taxon_code'].isin(filtered_taxon_codes)].copy()
    
    else:
        node = tree_dict[selected_group]
        filtered_taxon_codes = get_all_taxon_codes(node)
        filtered_data = df[df['taxon_code'].isin(filtered_taxon_codes)].copy()


    # Additional dynamic filtering options
    st.sidebar.header("Additional Filters")

    # Options to select which filters to display
    filter_options = st.sidebar.multiselect(
        'Select Filters to Display',
        ['Full_name','Tenure','Gender', 'Individual Location', 'Individual State', 'Individual County', 'Individual ZIP Code', 'Sole Proprietor', 'Telehealth','Medicare']
    )

    # Filter by gender
    if 'Gender' in filter_options:
        genders = sorted(filtered_data['gender'].astype(str).unique())
        selected_gender = st.sidebar.selectbox('Select Gender', [''] + list(genders))
        if selected_gender:
            filtered_data = filtered_data[filtered_data['gender'] == selected_gender].copy()

    # Filter by individual_location
    if 'Individual Location' in filter_options:
        individual_places = sorted(filtered_data['individual_place'].astype(str).unique())
        selected_places = st.sidebar.selectbox('Select Candidate Location', [''] + list(individual_places))
        if selected_places:
            filtered_data = filtered_data[filtered_data['individual_place'] == selected_places].copy()

    # Filter by individual_state
    if 'Individual State' in filter_options:
        individual_states = sorted(filtered_data['individual_state'].astype(str).unique())
        selected_state = st.sidebar.selectbox('Select Individual State', [''] + list(individual_states))
        if selected_state:
            filtered_data = filtered_data[filtered_data['individual_state'] == selected_state].copy()

    # Filter by individual_county
    if 'Individual County' in filter_options:
        individual_counties = sorted(filtered_data['individual_county'].astype(str).unique())
        selected_county = st.sidebar.selectbox('Select Individual County', [''] + list(individual_counties))
        if selected_county:
            filtered_data = filtered_data[filtered_data['individual_county'] == selected_county].copy()

    # Filter by individual_zip5
    if 'Individual ZIP Code' in filter_options:
        individual_zip5s = sorted(filtered_data['individual_zip5'].astype(str).unique())
        selected_zip5 = st.sidebar.selectbox('Select Individual ZIP Code', [''] + list(individual_zip5s))
        if selected_zip5:
            filtered_data = filtered_data[filtered_data['individual_zip5'] == selected_zip5].copy()

    # Filter by telehealth
    if 'Telehealth' in filter_options:
        selected_telehealth = st.sidebar.checkbox('Filter by Telehealth Certification')
        if selected_telehealth:
            filtered_data = filtered_data[filtered_data['telehealth'] == True].copy()

    # Filter by sole_proprietor
    if 'Sole Proprietor' in filter_options:
        selected_sole_proprietor = st.sidebar.checkbox('Filter by Sole Proprietorship')
        if selected_sole_proprietor:
            filtered_data = filtered_data[filtered_data['sole_proprietor'] == True].copy()

    # Filter by medicare
    if 'Medicare' in filter_options:
        selected_medicare = st.sidebar.checkbox('Filter by Medicare')
        if selected_medicare:
            filtered_data = filtered_data[filtered_data['medicare_id'].notnull()].copy()

    # Tenure advanced filter
    if 'Tenure' in filter_options:
            # Drop NA values before computing min and max
            filtered_data_non_na_tenure = filtered_data['tenure'].dropna()
            if not filtered_data_non_na_tenure.empty:
                min_tenure = int(filtered_data_non_na_tenure.min())
                max_tenure = int(filtered_data_non_na_tenure.max())
                if min_tenure < max_tenure:
                    selected_tenure = st.sidebar.slider('Select Tenure', min_tenure, max_tenure, (min_tenure, max_tenure))
                    filtered_data = filtered_data[(filtered_data['tenure'] >= selected_tenure[0]) & (filtered_data['tenure'] <= selected_tenure[1])]
                else:
                    st.sidebar.write(f"Tenure: {min_tenure} years")
    
    # Filter by part of the full name
    if 'Full Name' in filter_options:
        name_part = st.sidebar.text_input('Filter by Full Name')
        if name_part:
            filtered_data = filtered_data[filtered_data['full_name'].str.contains(name_part, case=False, na=False)].copy()
    
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
        selection_mode="multi-row",
        hide_index=True)    

    logger.info(f"selected rows {event.selection}")

    selected_data =  {}

    # Save the selected data into session state
    if 'rows' in event.selection:
        selected_data = grouped_data.iloc[event.selection.rows]
        st.session_state.selected_data = selected_data


else:
    st.write("Please select a classification.")