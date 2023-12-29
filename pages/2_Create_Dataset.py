import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title='Generate Dataset',
    page_icon = 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.bv.com%2F&psig=AOvVaw3YnhxlSA0MkNfAiaVnuwVO&ust=1703970475689000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCOintOvGtYMDFQAAAAAdAAAAABAD',
    layout = 'wide',
    initial_sidebar_state = 'auto'
)

if 'user_file' not in st.session_state:
    st.session_state.user_file=None
if 'data' not in st.session_state:
    st.session_state.data=pd.DataFrame()
if 'counter' not in st.session_state:
    st.session_state.counter = 0
if 'comments' not in st.session_state:
    st.session_state.comments=None
if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False

col1, col2 =st.columns(2)
image_box = col1.empty()
col11, col12, col13, col14, col15, col16 = col1.columns(6)
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
            image_box.image(image=display_image, caption="Satellite image at coordinates latitude="+str(latitude)+", longitude="+str(longitude)+", Copyright Map data ©2023")
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
    if st.session_state.counter<len(st.session_state.data.latitude):
        st.session_state.counter+=1
    load_new_image()


#no button with function to update the csv file and then load up a new image
def no_button_callback():
    st.session_state.data.at[st.session_state.counter, 'feature']='No'
    if st.session_state.counter<len(st.session_state.data.latitude):
        st.session_state.counter+=1
    load_new_image()

def inc_button_callback():
    st.session_state.data.at[st.session_state.counter, 'feature'] = 'Inconclusive'
    if st.session_state.counter<len(st.session_state.data.latitude):
        st.session_state.counter+=1
    load_new_image()

def prev_image_callback():
    if st.session_state.counter<len(st.session_state.data.latitude):
        st.session_state.counter-=1
    load_new_image()

def next_image_callback():
    if st.session_state.counter<len(st.session_state.data.latitude):
        st.session_state.counter+=1
    load_new_image()

#user uploads file here
#when user uploads new file, counter is reset, and the first image is loaded

if st.session_state.user_file==None:
    st.session_state.user_file=st.file_uploader(label="Upload CSV", type={"csv","txt"}, help="CSV File containg the following columns latitude, longitude")

if st.session_state.user_file!=None:
    if st.session_state.counter==0 and st.session_state.button_clicked==False:
        if st.session_state.data.empty:
            st.session_state.data=pd.read_csv(st.session_state.user_file)
            st.session_state.data.at[st.session_state.counter, 'feature']=''
    if len(st.session_state.data.latitude)>0:
        load_new_image()
        col11.button(label="Yes", help="Yes = The feature IS shown in the image", on_click=yes_button_callback, use_container_width=True)
        col12.button(label='No', help="No = The feature IS NOT shown in the image", on_click=no_button_callback, use_container_width=True)
        col13.button(label="Maybe", help = "Maybe = Unsure if feature is shown in the image", on_click=inc_button_callback, use_container_width=True)
        col14.button(label='Previous', help = 'Return to the previous image', on_click=prev_image_callback, use_container_width=True)
        st.session_state.counter=col15.number_input(label='#', help= 'Enter the index of the image that should be displayed', min_value=0, max_value=len(st.session_state.data.latitude)-1, value=st.session_state.counter, label_visibility="collapsed", on_change=load_new_image)
        col16.button(label='Next', help = 'Move to the next image', on_click=next_image_callback, use_container_width=True)
        user_edited_data = col2.data_editor(data=st.session_state.data, use_container_width=True, height = 590)
        st.session_state.data = user_edited_data

