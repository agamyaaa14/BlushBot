import streamlit as st
import random
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# Load preprocessed data
with open('data.pkl', 'rb') as file:
    data = pickle.load(file)

# Load the concern_tfidf and tfidf_concern
with open('concern_tfidf.pkl', 'rb') as file:
    tfidf_data = pickle.load(file)
    concern_tfidf = tfidf_data['concern_tfidf']  # Precomputed TF-IDF matrix
    tfidf_concern = tfidf_data['tfidf_concern']  # TfidfVectorizer object

# Helper Functions
def encode_user_inputs(user_skin_type, user_category, user_price, data):
    skin_type_mapping = {'combination': 0, 'dry': 1, 'normal': 2, 'oily': 3, 'sensitive': 4}
    category_mapping = {'cleanser': 0, 'moisturizer': 1, 'serum': 2, 'sunscreen': 3, 'toner': 4}

    skin_type_encoded = skin_type_mapping.get(user_skin_type.lower(), None)
    category_encoded = category_mapping.get(user_category.lower(), None)

    if skin_type_encoded is None or category_encoded is None:
        return None

    price_normalized = (user_price - data['price'].min()) / (data['price'].max() - data['price'].min())
    return skin_type_encoded, category_encoded, price_normalized

def recommend_filtered_products(user_skin_type, user_category, user_price, user_concern, data, tfidf_concern, concern_tfidf, top_n=5, weight1=0.5, weight2=0.3, weight3=0.2, sigma=100):
    try:
        encoded_inputs = encode_user_inputs(user_skin_type, user_category, user_price, data)
        if encoded_inputs is None:
            return "Invalid input provided."

        skin_type_encoded, category_encoded, price_normalized = encoded_inputs

        filtered_data = data[
            (data['Skin Type Encoded'] == skin_type_encoded) & 
            (data['Product Category Encoded'] == category_encoded) & 
            ((data['price'] <= user_price + 150) & (data['price'] >= user_price - 150))
        ].copy()

        if filtered_data.empty:
            return "No products match your filters."

        user_concern_vec = tfidf_concern.transform([user_concern.strip().lower()])
        filtered_indices = filtered_data.index
        product_concerns_vec = concern_tfidf[filtered_indices, :]
        similarity_scores = cosine_similarity(user_concern_vec, product_concerns_vec).flatten()

        filtered_data['price_score'] = np.exp(-((filtered_data['price'] - user_price) ** 2) / (2 * sigma ** 2))
        filtered_data['final_score'] = (
            (similarity_scores * weight1) + 
            (filtered_data['overall_rating'] * weight2) + 
            (filtered_data['price_score'] * weight3)
        )

        filtered_data = filtered_data.sort_values(by='final_score', ascending=False).head(top_n)
        return filtered_data[['product_brand', 'product_name', 'price', 'overall_rating']]
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Streamlit App Structure
st.title("Welcome to BlushBot")
st.subheader("Personalized Skincare Recommendations")
st.write("Your one-stop guide to finding skincare products tailored to your skin type, concerns, and budget!")

st.markdown(
    """<style>
    body { background-color:#e791a3; }
    .stApp { background-color:#fff7e3; }
    </style>""", 
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    .css-1l02zno.e1tzin5v3 {  /* This class is for Streamlit's dataframe styling */
        width: 80% !important; /* Adjust the width as needed (e.g., 80% or 100%) */
        margin: 0 auto;       /* Center the box */
    }
    </style>
    """, 
    unsafe_allow_html=True
)


st.image(r"C:\Users\Thrishaa J\Downloads\logo-1.png", use_container_width=True)

# Input Sections
skin_type = st.selectbox("Select your skin type", ['combination', 'dry', 'normal', 'oily', 'sensitive'])
category = st.selectbox("Select product category", ['cleanser', 'moisturizer', 'serum', 'sunscreen', 'toner'])
price = st.number_input("Enter your budget (in INR)", min_value=0, max_value=10000, value=500)
concern = st.text_input("Enter your primary skin concern", "hydration")


# Recommendations Section

st.markdown(
    """
    <style>
    .recommendation-box {
        background-color: #f7f7f7; /* Light background for the box */
        padding: 20px; /* Add padding for better spacing */
        border-radius: 10px; /* Rounded corners */
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); /* Subtle shadow for depth */
        max-width: 90%; /* Set max width for the box */
        margin: 0 auto; /* Center the box */
        overflow-x: hidden; /* Remove horizontal scrolling */
        font-family: Arial, sans-serif; /* Use clean font */
    }
    .recommendation-product {
        margin-bottom: 15px; /* Spacing between products */
        padding: 10px;
        background-color: #fff;
        border-radius: 5px;
        border: 1px solid #ddd; /* Subtle border around products */
    }
    </style>
    """,
    unsafe_allow_html=True
)

if st.button("Get Recommendations"):
    recommendations = recommend_filtered_products(
        user_skin_type=skin_type,
        user_category=category,
        user_price=price,
        user_concern=concern,
        data=data,
        tfidf_concern=tfidf_concern,
        concern_tfidf=concern_tfidf,
        top_n=5
    )

    if isinstance(recommendations, str):
        st.write(recommendations)
    else:
        st.write("Top Recommended Products:")
        st.dataframe(recommendations)


# 3. Skincare Tip Button

# List of skincare facts
skincare_facts = [
    "Sunscreen is a must, even on cloudy days!",
    "Hydration is the foundation of healthy skin.",
    "Vitamin C helps brighten skin and fight dullness.",
    "Patch-testing a product can save you from irritation.",
    "Exfoliate gently—your skin will thank you!",
    "Double cleansing removes dirt and sunscreen effectively.",
    "Niacinamide helps regulate oil and improve skin texture.",
    "Always moisturize after washing your face to lock in hydration.",
    "Retinol works best at night but remember to use sunscreen during the day!",
    "Use lukewarm water, not hot, to prevent skin dryness.",
    "Don’t skip your neck—it needs skincare too!",
    "Overwashing can strip your skin’s natural oils. Keep it to twice a day.",
    "Layer products from thinnest to thickest for maximum absorption.",
    "Avoid harsh scrubs; use chemical exfoliants for a gentler approach.",
    "Drink plenty of water for that inside-out glow.",
    "A consistent routine is key—don’t expect overnight results.",
    "Store vitamin C serums in a cool, dark place to prevent oxidation.",
    "SPF should be reapplied every 2 hours when outdoors.",
    "Silk pillowcases can reduce skin irritation and improve hydration.",
    "Diet impacts skin—eat plenty of fruits and veggies for a natural glow."
]
st.info(f"💡 Skincare Tip: {random.choice(skincare_facts)}")

# Footer
st.write("BlushBot – Skincare Simplified. Let’s glow together!")
