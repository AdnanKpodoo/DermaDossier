import json
import streamlit as st
import pandas as pd
from streamlit_lottie import st_lottie
import gspread
from google.oauth2.service_account import Credentials
from oauth2client.service_account import ServiceAccountCredentials

# Load the Lottie animation file
def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

lottie_skincare = load_lottiefile(".streamlit/skincare.json")

# Function to connect to Google Sheets
# Establish a connection to Google Sheets and return all sheets
def connect_to_gsheets(creds_json, sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scope)
    client = gspread.authorize(credentials)
    workbook = client.open(sheet_name)
    sheets = workbook.worksheets()  # Get all worksheets
    return workbook, sheets

SPREADSHEET_NAME = 'skin_caree'
CREDENTIALS_FILE = './newcredkey.json'

# Connect to the workbook
workbook, sheets = connect_to_gsheets(CREDENTIALS_FILE, SPREADSHEET_NAME)

# Get the 'products' and 'brands' worksheets by name
products_sheet = workbook.worksheet('products')
brands_sheet = workbook.worksheet('brands')

# Function to fetch products based on skin type from the 'products' and 'brands' worksheets
def get_products_from_sheets(products_sheet, brands_sheet, skin_type):
    products_data = products_sheet.get_all_records()
    brands_data = brands_sheet.get_all_records()
    products = []

    # Map brand IDs to names from the 'brands' table
    brand_map = {brand['brand_id']: brand['brand_name'] for brand in brands_data}

    # Filter products by skin type
    for product in products_data:
        if product['skin_type'] == skin_type or (product['skin_type_two'] == skin_type and product['skin_type'] != skin_type):
            brand_name = brand_map.get(product['brand_id'], "Unknown Brand")
            products.append({
                "product_name": product['product_name'],
                "brand_name": brand_name,
                "category": product['category'],
                "description": product['description'],
                "price": product['price'],
                "skin_type": product['skin_type'],
                "skin_type_two": product['skin_type_two']
            })
    return products

# Streamlit Application
st.title('DermaDossier')
st.subheader('Start Your Search for a Basic Effective Routine!')

# Display the Lottie animation
st_lottie(
    lottie_skincare,
    speed=1,
    reverse=False,
    loop=True,
    quality="low",
    height=500,
    width=300
)

# Google Sheets Setup
#products_sheet, brands_sheet = connect_to_gsheets()
#sheets = connect_to_gsheets('./credkey.json', 'skin_caree')

# Sidebar for selecting a skin type
st.subheader("Select Skin Type")
skin_type = st.selectbox("Options", ("Oily", "Dry", "Normal", "Combination", "Acne-Prone", "Sensitive", "All"))

# Display products based on selected skin type
if skin_type:
    st.subheader(f"Products For {skin_type} Skin")

    products = get_products_from_sheets(products_sheet, brands_sheet, skin_type)

    if products:
        for product in products:
            st.write(f"**Product Name**: {product['product_name']}")
            st.write(f"**Brand**: {product['brand_name']}")
            st.write(f"**Category**: {product['category']}")
            st.write(f"**Description**: {product['description']}")
            st.write(f"**Price**: ${product['price']:.2f}")
            st.write(f"**Skin Type**: {product['skin_type']}, {product['skin_type_two']}")
            st.write("---")
    else:
        st.write("No products found for the selected skin type.")
