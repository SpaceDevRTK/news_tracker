import requests
import json
import pandas as pd
import streamlit as st
import ast

# Set up streamlit page and initial headers
st.set_page_config(layout="wide")
st.title("Simple news tracker 📰")
st.caption("Using sources from newsapi.org, and the Streamlit framework")

# Read the text file into a variable
with open("isocountries.txt", "r", encoding="utf-8") as file:
    data = file.read()  # Read as string

# Convert string to dictionary
iso_countries = ast.literal_eval(data)  # Safe way to evaluate dictionary


# Get user to choose country, default to US because it has the most sources..
country_list = list(iso_countries.values())
default_country_index = country_list.index("United States")
country = st.selectbox('Choose a country:', country_list, index=default_country_index)

if country:
    # Get the source id corresponding to the selected name
    country_id = [key for key, value in iso_countries.items() if value == country][0]

    # Get available news sources for chosen country
    url = f'https://newsapi.org/v2/top-headlines/sources?country={country_id}&apiKey=042f97238ff04747808ab3b44dd295f7'
    sources = requests.get(url)
    sourcedata = sources.json()

    # Debugging: Print the sourcedata dictionary to check its structure
    #st.write(sourcedata)

    # Check if 'sources' key exists in the sourcedata dictionary
    if 'sources' in sourcedata:
        # Populate sourcelist dictionary with 'id' and 'name' fields
        sourcelist = {source['id']: source['name'] for source in sourcedata['sources']}

        # Get user to choose which news source to use
        option = st.selectbox('Choose an available news source', list(sourcelist.values()))

        if option:
            # Get the source id corresponding to the selected name
            source_id = [key for key, value in sourcelist.items() if value == option][0]

            # Fetch the top headlines for the selected source
            url = f'https://newsapi.org/v2/top-headlines?sources={source_id}&apiKey=042f97238ff04747808ab3b44dd295f7'
            response = requests.get(url)

            # Check if the response is valid
            if response.status_code != 200:
                st.error("Failed to retrieve data")
            else:
                # Turn the response into a python dictionary (which is key, value pairs)
                data = response.json()

                # Create an empty DataFrame
                df = pd.DataFrame(columns=['Title', 'Description', 'Source', 'Url', 'Url to Image'])

                # Iterate over the 'articles' key and add data to the DataFrame
                for index, entry in enumerate(data['articles']):
                    title = entry.get('title', 'No Title')
                    description = entry.get('description', 'No Description')
                    source = entry.get('source', {}).get('name', 'No Source')
                    url = entry.get('url', 'No URL')
                    urlimage = entry.get('urlToImage', 'No image')
                    new_row = pd.DataFrame({'Title': [title], 'Description': [description], 'Source': [source], 'Url': [url], 'Url to Image': [urlimage]})
                    df = pd.concat([df, new_row], ignore_index=True)

                st.subheader("News headlines:")

                # Display the data in Streamlit with expandable descriptions and images
                for index, row in df.iterrows():
                    expander_label = f"**{row['Title']} - {row['Source']}**"
                    with st.expander(expander_label):
                        if row['Url to Image'] is not None:
                            st.image(row['Url to Image'], width=500)
                        st.write(f"### {row['Title']} - {row['Source']}")
                        st.write(row['Description'])
                        st.write(row['Url'])
    else:
        st.error("No sources found for the selected country.")