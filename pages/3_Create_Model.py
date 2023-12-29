import numpy as np
import PIL
import tensorflow as tf
import pickle

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential

import pandas as pd
import requests

from pathlib import Path
import io

import streamlit as st

st.set_page_config(
    page_title='Train a Model',
    page_icon = 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.bv.com%2F&psig=AOvVaw3YnhxlSA0MkNfAiaVnuwVO&ust=1703970475689000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCOintOvGtYMDFQAAAAAdAAAAABAD',
    layout = 'centered',
    initial_sidebar_state = 'auto'
)

st.write('Do not use this feature - for illustrative purposes only')
st.write('Current hosting does not have enough resources and will crash upon model training')
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

#split into training and validation datasets
def training_validation(dataset_with_images):
    #80% is used for training dataset, 20% for validation
    no_training = round(0.8*(dataset_with_images['feature'].value_counts()['No']-1),0)
    yes_training = round(0.8*(dataset_with_images['feature'].value_counts()['Yes']-1),0)
    yes_counter=0
    no_counter=0
    training_counter=0
    validation_counter=0

    #training and validation sets have two columns
    #image = 3d numpy array representation of the image
    #label = yes or no label
    training_set=pd.DataFrame(columns=['image', 'label'])
    training_set['image'].astype(object)
    training_set['label'].astype(object)
    validation_set=pd.DataFrame(columns=['image','label'])
    validation_set['image'].astype(object)
    validation_set['label'].astype(object)

    #80% of yes and 80% of no is placed in training dataset
    #rest is placed in validation dataset
    for counter in range(len(dataset_with_images.latitude)):
        if dataset_with_images.at[counter,'feature']=='Yes':
            if yes_counter<yes_training:
                training_set.at[training_counter, 'image']=dataset_with_images.at[counter, 'image']
                training_set.at[training_counter, 'label']=np.array([1])
                training_counter+=1
            else:
                validation_set.at[validation_counter,'image']=dataset_with_images.at[counter, 'image']
                validation_set.at[validation_counter, 'label']=np.array([1])
                validation_counter+=1
            yes_counter+=1   
        else:
            if no_counter<no_training:
                training_set.at[training_counter, 'image']=dataset_with_images.at[counter, 'image']
                training_set.at[training_counter, 'label']=np.array([0])
                training_counter+=1
            else:
                validation_set.at[validation_counter,'image']=dataset_with_images.at[counter, 'image']
                validation_set.at[validation_counter, 'label']=np.array([0])
                validation_counter+=1
            no_counter+=1 
    
    #convert to and return dataset objects
    training_set=tf.data.Dataset.from_tensor_slices((list(training_set['image'].values), list(training_set['label'].values))).batch(2)
    validation_set=tf.data.Dataset.from_tensor_slices((list(validation_set['image'].values), list(validation_set['label'].values))).batch(2)
    return(training_set,validation_set)

#session state variables
if 'input_data' not in st.session_state:
    st.session_state.input_data=None
if 'model' not in st.session_state:
    st.session_state.model=None
if 'json_config' not in st.session_state:
    st.session_state.json_config=None
if 'weights' not in st.session_state:
    st.session_state.weights = None
if 'input_file' not in st.session_state:
    st.session_state.input_file=None

#user uploads csv with their labelled data
if st.session_state.input_file==None:
    st.session_state.input_file=st.file_uploader('Upload your training data', type=['.csv'], help='Upload the training dataset. It must include the following 3 columns: latitude, longitude and features')

if st.session_state.input_file!=None and st.session_state.model==None:
    #once user uploaded csv, load into pandas dataframe, append images from google maps api, split into training and validation set
    st.session_state.input_data=pd.read_csv(st.session_state.input_file)
    with st.spinner('Preprocessing data for model training'):
        st.session_state.input_data = append_images(st.session_state.input_data)

        st.session_state.training_set, st.session_state.validation_set = training_validation(st.session_state.input_data)
    
        #configure dataset for performance
        AUTOTUNE = tf.data.AUTOTUNE
        st.session_state.training_set = st.session_state.training_set.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
        st.session_state.validation_set = st.session_state.validation_set.cache().prefetch(buffer_size=AUTOTUNE)

    with st.spinner ('Creating, compiling and training model'):
        #create model
        #data augmentation layers
        #improves model performance by rotating, zooming on images to create bigger training dataset
        data_augmentation = keras.Sequential(
        [
        layers.RandomFlip("horizontal",
                            input_shape=(640,
                                        640,
                                        1)),
        layers.RandomRotation(0.1),
        layers.RandomZoom(0.1),
        ]
        )

        #make model with data augmentation layer and rescaling layer to normalize the values of each pixel
        st.session_state.model = Sequential([
        data_augmentation,
        layers.Rescaling(1./255, input_shape=(640, 640, 1)),
        layers.Conv2D(16, 1, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(32, 1, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(64, 1, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Dropout(0.2),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dense(2)
        ])

        #compile and fit model to training data
        st.session_state.model.compile(optimizer='adam',
                loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                metrics=['accuracy'])

        st.session_state.model.fit(
        st.session_state.training_set,
        validation_data=st.session_state.validation_set,
        epochs=10
        )

        st.session_state.json_config = st.session_state.model.to_json()
        st.session_state.weights = st.session_state.model.get_weights()
        st.session_state.weights = pickle.dumps(st.session_state.weights)
if st.session_state.input_file!=None and st.session_state.model!=None:
    col1, col2 = st.columns(2)
    col1.download_button('Download model architecture', data=str(st.session_state.json_config), file_name='architecture.txt', use_container_width=True)
    col2.download_button('Download model weights', data=st.session_state.weights, file_name='weights.pkl', use_container_width=True)


    
