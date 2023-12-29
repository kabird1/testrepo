import numpy as np
import PIL
import tensorflow as tf

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential

import pandas as pd
import requests

from pathlib import Path
import io

import streamlit as st

import json

st.set_page_config(
    page_title='Use a Model',
    page_icon = 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.bv.com%2F&psig=AOvVaw3YnhxlSA0MkNfAiaVnuwVO&ust=1703970475689000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCOintOvGtYMDFQAAAAAdAAAAABAD',
    layout = 'centered',
    initial_sidebar_state = 'auto'
)

st.write('Do not use this feature - for illustrative purposes only')
st.write('Current hosting does not have enough resources and will crash')

#gets images from google static maps api based on latitude and longitude, appends them to pandas dataframe as 3d numpy array in format (pixels x pixels x layers)
def append_images(data):
    for counter in range(len(data.latitude)):
        latitude = data.latitude[counter]
        longitude = data.longitude[counter]
        params = {
        'key': 'AIzaSyA4MhqXRYSOSOkfKw5vk-YYupMuYPMFcMQ',
        'center': str(latitude)+', '+str(longitude),
        'zoom': '19',
        'size' : '1200x1200',
        "maptype": "satellite",
        'region' : 'US',
        'imageFormat' : 'png',
        'layerTypes' : 'none'
        }
        #request comes in as binary
        map = requests.get('https://maps.googleapis.com/maps/api/staticmap', params=params)
        if map.ok:
            data.at[counter,'image']=''
            data['image'].astype(object)
            #take binary, convert to bytes, open as pil image object
            image = keras.utils.img_to_array(PIL.Image.open(io.BytesIO(map.content)))
            #save in database as pil image object
            data.at[counter,'image']=image
    return (data)

#takes an input dataset with the images in numpy array format and adds the yes or no predictions
def make_prediction(prediction_dataset, model):
    #turn dataframe into tensor
    predict_tf = tf.data.Dataset.from_tensor_slices(list(prediction_dataset['image'].values)).batch(2)
    #make predictions
    predictions = model.predict(predict_tf)
    #update user csv file with yes or no predictions
    for counter in range(len(prediction_dataset.latitude)):
        if np.argmax(predictions[counter])==0:
            prediction_dataset.at[counter,'prediction']='no'
        else:
            prediction_dataset.at[counter,'prediction']='yes'
    #return the dataframe with predictions, but remove the numpy array images
    return prediction_dataset.drop(columns='image')

if 'predict_data' not in st.session_state:
    st.session_state.predict_data=None
if 'architecture' not in st.session_state:
    st.session_state.architecture=None
if 'weights_file' not in st.session_state:
    st.session_state.weights_file = None
if 'prediction_model' not in st.session_state:
    st.session_state.prediction_model = None

if st.session_state.architecture==None:
    st.session_state.architecture = st.file_uploader('Upload the model architecture', type=['.json'], help='File should be a .json file containing the model architecture')
if st.session_state.weights_file==None:
    st.session_state.weights_file = st.file_uploader('Upload the model weights:', type=['.pkl'], help='File should be a .pkl file containing the model weights.')
if st.session_state.architecture!=None and st.session_state.weights_file!=None:
    st.session_state.architecture = json.load(st.session_state.architecture)
    st.session_state.weights_file = pickle.load(st.session_state.weights_file)
    
    st.session_state.weights_file = st.session_state.weights_file
    if st.session_state.prediction_model==None:
        with st.spinner('Preparing model for predictions'):
            st.session_sate.prediction_model = keras.models.model_from_json(st.session_state.architecture)
            st.session_sate.prediction_model.set_weights_file(st.session_state.weights_file)
    if st.session_state.prediction_model!=None:
        if st.session_state.predict_data.empty:
            st.session_state.predict_data = st.file_uploader('Upload a dataset to make predictions', type=['.csv'], help='File should be a .csv file containing two columns: latitude and longitude')
        if st.session_state.predict_data.empty==False:
            with st.spinner('Reading input data and making predictions'):
                st.session_state.predict_data = pd.readcsv(st.session_state.predict_data)
                st.session_state.predict_data = make_prediction(st.session_state.predict_data,st.session_state.prediction_model)
                st.data_editor(st.session_state.predict_data)
        



