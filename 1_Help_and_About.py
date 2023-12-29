import streamlit as st

st.set_page_config(
    page_title='Help and About',
    page_icon = 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.bv.com%2F&psig=AOvVaw3YnhxlSA0MkNfAiaVnuwVO&ust=1703970475689000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCOintOvGtYMDFQAAAAAdAAAAABAD',
    layout = 'centered',
    initial_sidebar_state = 'auto'
)

st.write('About: The goal of this app is to create a machine learning model to identify whether an object is present in a certain location using satellite images')
st.write('See below for help topics for each component of the app:')

generate_data=st.expander("Generate Data")
generate_data.write('The purpose of this section is to generate a data set to train an AI model to identify features on satellite images of maps.')
generate_data.write('1. Create .csv file with columns \"latitude\" and \"longitude\".')
generate_data.write('2. Populate .csv file with latitude and longitude of locations on the maps.')
generate_data.write('3. Upload the .csv file to the app, using the browse button, or by dragging and dropping your file.')
generate_data.write('4. The contents of the .csv file are displayed at the bottom of the screen. The user can edit the data by clicking on cells and typing, and can download the edited data at any time.')
generate_data.write('5. Satellite images of the locations are loaded by Google Maps API and displayed on the screen. Underneath the image, the user can enter their input using the three buttons: yes, No and Inconclusive. The user can also enter any addition comments.')
generate_data.write('6. Upon pressing the submit button, the yes/No/Inconclusive selection is entered under the \'features\' column appended to the user\'s .csv file. The comments entered in the textbox are entered under the \'comments\' column appended to the user\'s .csv file. To ensure comments are submitted, the user must press \'CTRL+Enter\' or click out of the textbox to pass the value to the .csv file.')
generate_data.write('5. Google Maps API does not return images for locations that contain no features (i.e. the middle of the ocean)')
generate_data.write('6. The annotated coordinates file can be downloaded using the button at the top right corner of the data table, and can then be used to train an AI model. (This feature is under development)')

train_model=st.expander("Train and save a machine learning model")
train_model.write('This purpose of this section is to upload a dataset and train and save an AI model to identify features on satellite images of maps.')
train_model.write('1. Upload .csv file created using the \"Generate Data\" function fo this app. Your file should have columns \"latitude\", longitude \"longitude\" and \"features\"')
train_model.write('2. Images of the locations are loaded using Google Maps API to be able to train the AI model.')
train_model.write('3. The provided data is split into 80% training data, 20% validation data.')
train_model.write('4. The model is trained using the training dataset.')
train_model.write('5. Once training is completed, the architecture of the model can be downloaded as a .json file, and the weights of the model can be downloaded as a .pkl file')

use_model=st.expander("Use a saved machine learning model")
use_model.write("The purpose of this section is to upload existing model architecture and weights and make predictions on whether a feature exists in certain locations")
use_model.write('1. Upload .json file containg the model architecture.')
use_model.write('2. Upload .pkl file containing model weights')
use_model.write('3. Once the model has been built based on your files, upload a .csv file containing latitude and longitude coordinates. These coordinates are the locations at which predictions are made')
use_model.write('4. Images of the the locations are loaded using Google Maps API to be able to make predictions')
use_model.write('5. The model makes predictions. Once the model has finished all predictions, the files can be download in .csv format')

