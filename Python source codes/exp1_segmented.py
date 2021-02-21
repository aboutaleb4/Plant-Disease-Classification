# -*- coding: utf-8 -*-
"""exp1_segmented.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dpK1GbdTvF7AbtldXRHyn2SaewK6XxSh
"""

from google.colab import drive

drive.mount('/content/drive')

#! git clone https://github.com/MichaelGerhard/PlantDiseaseData
! git clone https://github.com/spMohanty/PlantVillage-Dataset

#importing necessary libraries and APIs

import warnings
warnings.filterwarnings("ignore")
import os
import glob
import matplotlib.pyplot as plt
import keras

from keras.models import Sequential
from keras.layers import Dense,Dropout,Flatten
from keras.layers import Conv2D,MaxPooling2D,Activation,AveragePooling2D,BatchNormalization
from keras.preprocessing.image import ImageDataGenerator
import tensorflow as tf

import os
import numpy as np
import matplotlib.pyplot as plt

#data path

data_dir = "/content/PlantVillage-Dataset/raw/segmented"

#function that counts the number of files in a dierctory
def get_files(dir):
  if not os.path.exists(dir):
    return 0
  c=0 #initialize count with zero
  for curr_path,dirs,files in os.walk(dir):
    for d in dirs:
      c+= len(glob.glob(os.path.join(curr_path,d+"/*")))

  return c

segmented_data=get_files(data_dir)
num_classes=len(glob.glob(data_dir+"/*"))
print(num_classes,"Classes")

pip install split-folders

import splitfolders 
splitfolders.ratio("/content/PlantVillage-Dataset/raw/segmented", output="train_test", seed=1337, ratio=(.8, .2), group_prefix=None) # default values

train_dir ="/content/train_test/train"
test_dir="/content/train_test/val"

#data generator to generate images 

train_datagen=ImageDataGenerator(rescale=1./255, shear_range=0.2, zoom_range=0.2, validation_split=0.2, horizontal_flip=True)
test_datagen=ImageDataGenerator(rescale=1./255)

img_width,img_height =224,224 #sizes are compatible with MobileNet
input_shape=(img_width,img_height,3)
batch_size =64
train_generator =train_datagen.flow_from_directory(train_dir,shuffle=True, #added shuffle here
                                                   target_size=(img_width,img_height),
                                                   batch_size=batch_size,
                                                   subset='training'
                                                   )
validation_generator =train_datagen.flow_from_directory(train_dir,shuffle=True, #added shuffle here
                                                   target_size=(img_width,img_height),
                                                   batch_size=batch_size,
                                                   subset='validation')

test_generator=test_datagen.flow_from_directory(test_dir,shuffle=True,
                                                   target_size=(img_width,img_height),
                                                   batch_size=batch_size)

print(len(validation_generator))

for image_batch, label_batch in train_generator:
  break
image_batch.shape, label_batch.shape

print (train_generator.class_indices)
labels = '\n'.join(sorted(train_generator.class_indices.keys()))
with open('labels.txt', 'w') as f:
  f.write(labels)

IMG_SHAPE = (img_width, img_height, 3)

# base model is the pre-trained model MobileNet V2 (from keras library)
base_model = tf.keras.applications.MobileNetV2(input_shape=IMG_SHAPE, include_top=False, weights='imagenet')

base_model.trainable=False

#Adding the layers (model 1)
model = tf.keras.Sequential([
  base_model,
  tf.keras.layers.Conv2D(32, 3, activation='elu'),
  tf.keras.layers.Dropout(0.5),  #increase dropout
  tf.keras.layers.GlobalAveragePooling2D(),
  tf.keras.layers.Dense(38, activation='softmax')
])

model.compile(optimizer=tf.keras.optimizers.Adam(), 
              loss='categorical_crossentropy', 
              metrics=['accuracy'])

model.summary()

print('Number of trainable variables = {}'.format(len(model.trainable_variables)))

epochs = 10

history = model.fit(train_generator, 
                    epochs=epochs, 
                    validation_data=validation_generator)

score = model.evaluate(test_generator)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

plt.figure(figsize=(8, 8))
plt.subplot(2, 1, 1)
plt.plot(acc, label='Training Accuracy')
plt.plot(val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.ylabel('Accuracy')
plt.ylim([min(plt.ylim()),1])
plt.title('Training and Validation Accuracy')

plt.subplot(2, 1, 2)
plt.plot(loss, label='Training Loss')
plt.plot(val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.ylabel('Cross Entropy')
plt.ylim([0,1.0])
plt.title('Training and Validation Loss')
plt.xlabel('epoch')
plt.show()