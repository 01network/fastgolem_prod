import pandas as pd
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_csv(file_path, dtype):
    """Load the CSV data with the specified dtype."""
    try:
        logger.info(f"Loading CSV file from {file_path}")
        df = pd.read_csv(file_path, dtype=dtype, low_memory=False)
        logger.info(f"CSV file loaded successfully with {len(df)} records")
        return df
    except Exception as e:
        logger.error(f"Error loading CSV file {file_path}: {e}")
        return pd.DataFrame()

def load_json(file_path):
    """Load the JSON structure."""
    try:
        logger.info(f"Loading JSON file from {file_path}")
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        logger.info(f"JSON file loaded successfully")
        return data
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {e}")
        return {}

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
            # logger.info(f"Parsed Tree Structure: {rows}")
    return rows



def generate_dataframes(csv_path, json_path):
    # Define the column data types explicitly if known
    dtype = {
        "full_name": str,
        "taxon_code": str,
        "taxon_state": str,
        "nucc_group": str,
        "nucc_classification": str,
        "nucc_specialization": str,
        "individual_place": str,
        "individual_zip5": str,
        "individual_county": str,
        "individual_state": str,
        "facility_name": str,
        "facility_place": str,
        "facility_zip5": str,
        "facility_state": str,
        "medical_school": str,
        "tenure": int,
        "enumeration_date": str,
        "graduation_year": str,
        "gender": str,
        "full_name_other": str,
        "npi": str,
        "npi_replacement": str,
        "medicare_id": str,
        "sole_proprietor": bool,
        "telehealth": bool,
        "medicare_specialty": str,
        "county_code": str,
        "geo_id": str,
        "lat": float,
        "long": float,
        "dni": str,
        "last_update_date": str
    }

    df_csv = load_csv(csv_path, dtype)
    nary_tree = load_json(json_path)

    parsed_data = []
    for group, group_data in nary_tree.items():
        parsed_data.extend(parse_tree(group_data, [group]))

    df_nary_tree = pd.DataFrame(parsed_data)
    
    return df_csv, df_nary_tree

if __name__ == "__main__":
    csv_path = 'data/hcp.csv'
    json_path = 'data/nucc_tree.json'
    logger.info("Starting data processing")
    df_csv, df_nary_tree = generate_dataframes(csv_path, json_path)
    logger.info("Data processing completed")
