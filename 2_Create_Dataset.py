import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title='Generate Dataset',
    page_icon = 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.bv.com%2F&psig=AOvVaw3YnhxlSA0MkNfAiaVnuwVO&ust=1703970475689000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCOintOvGtYMDFQAAAAAdAAAAABAD',
    layout = 'centered',
    initial_sidebar_state = 'auto'
)
st.sidebar

if 'user_file' not in st.session_state:
    st.session_state.user_file=None
if 'data' not in st.session_state:
    st.session_state.data=None
if 'counter' not in st.session_state:
    st.session_state.counter = 0
if 'comments' not in st.session_state:
    st.session_state.comments=None
if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False

image_container = st.empty()

#function to load up images from google maps api:
def load_new_image():
    if st.session_state.counter<len(st.session_state.data.latitude):
        latitude = st.session_state.data.latitude[st.session_state.counter]
        longitude = st.session_state.data.longitude[st.session_state.counter]
        params = {
        'key': str(st.secrets["key"]),
        'center': str(latitude)+', '+str(longitude),
        'zoom': '19',
        'size' : '1200x1200',
        "maptype": "satellite",
        'region' : 'US',
        'imageFormat' : 'png',
        'layerTypes' : 'none'
        }
        map = requests.get('https://maps.googleapis.com/maps/api/staticmap', params=params)
        #checks that map has any features... google api will not return maps for the ocean, only areas with features
        if map.ok:
            display_image = map.content
            image_container.image(image=display_image, caption="Satellite image at coordinates latitude="+str(latitude)+", longitude="+str(longitude)+", Copyright Map data ©2023")
        #if google api does not return a photo (i.e. no features at that coordinate) the csv file "features" column for that set of coordinates is set to "no"
        else:
            st.session_state.data.at[st.session_state.counter, 'feature']='No'
            st.session_state.data.at[st.session_state.counter, 'comments']='The Google Maps Tiles API did not return an image for this set of coordinates. Google Maps Tiles API does not return images for coordinates that do not contain features, such as images of only blue ocean'
            print(st.session_state.data.loc[[st.session_state.counter]])
            st.session_state.counter+=1
            load_new_image()
    else:
            st.write("You've reached the end of the data set")


#yes button with function to update the csv file and then load up a new image
def yes_button_callback():
    st.session_state.data.at[st.session_state.counter, 'feature']='Yes'
    st.session_state.button_clicked=True


#no button with function to update the csv file and then load up a new image
def no_button_callback():
    st.session_state.data.at[st.session_state.counter, 'feature']='No'
    st.session_state.button_clicked=True

def inc_button_callback():
    st.session_state.data.at[st.session_state.counter, 'feature'] = 'Inconclusive'
    st.session_state.button_clicked=True

def submit_button_callback():
    if st.session_state.counter<len(st.session_state.data.latitude):
        st.session_state.counter+=1
    load_new_image()

#user uploads file here
#when user uploads new file, counter is reset, and the first image is loaded

if st.session_state.user_file==None:
    st.session_state.user_file=st.file_uploader(label="Upload CSV", type={"csv","txt"}, help="CSV File containg the following columns latitude, longitude")

if st.session_state.user_file!=None:
    if st.session_state.counter==0 and st.session_state.button_clicked==False:
        st.session_state.data=pd.read_csv(st.session_state.user_file)
        st.session_state.data.at[st.session_state.counter, 'feature']=''
        st.session_state.data.at[st.session_state.counter, 'comments']=''
    if len(st.session_state.data.latitude)>0:
        load_new_image()
        col1, col2, col3= st.columns(3)
        col1.button(label="yes", help="yes = The feature IS shown in the image", on_click=yes_button_callback, use_container_width=True)
        col2.button(label='No', help="No = The feature IS NOT shown in the image", on_click=no_button_callback, use_container_width=True)
        col3.button(label="Inconclusive", help = "Inconclusive = Unsure if feature is shown in the image", on_click=inc_button_callback, use_container_width=True)
        st.session_state.data.at[st.session_state.counter, 'comments'] = st.text_area(label="Comments", label_visibility="hidden", placeholder="Enter your comments here")
        st.button(label="Submit", help="Submit the data, update the .csv file and move to the neextt image", on_click=submit_button_callback, use_container_width=True)
        user_edited_data = st.data_editor(data=st.session_state.data, use_container_width=True)
        st.session_state.data = user_edited_data

