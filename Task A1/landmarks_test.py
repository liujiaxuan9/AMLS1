import os
import numpy as np
from keras.preprocessing import image
import cv2
import dlib
import pandas as pd
import pathlib 


# setting path to image folders
global basedir, image_paths, target_size
basedir = 'D:/ELEC0134 Applied Machine Learning Systems/assignment/dataset_AMLS_20-21_test/'
#images_dir = os.path.join(basedir,'img')
#images_dir = images_dir.replace('\\', '/')
images_dir = pathlib.Path('/').joinpath(basedir,'celeba_test')
labels_filename = 'labels.csv'



detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

def shape_to_np(shape, dtype="int"):
    # initialize the list of (x, y)-coordinates
    coords = np.zeros((shape.num_parts, 2), dtype=dtype)

    # loop over all facial landmarks and convert them
    # to a 2-tuple of (x, y)-coordinates
    for i in range(0, shape.num_parts):
        coords[i] = (shape.part(i).x, shape.part(i).y)

    # return the list of (x, y)-coordinates
    return coords

def rect_to_bb(rect):
    x = rect.left()
    y = rect.top()
    w = rect.right() - x
    h = rect.bottom() - y

    # return a tuple of (x, y, w, h)
    return (x, y, w, h)


def run_dlib_shape(image):
    resized_image = image.astype('uint8')

    gray = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
    gray = gray.astype('uint8')

    # detect faces in the grayscale image
    rects = detector(gray, 1)
    num_faces = len(rects)

    if num_faces == 0:
        return None, resized_image

    face_areas = np.zeros((1, num_faces))
    face_shapes = np.zeros((136, num_faces), dtype=np.int64)

    # loop over the face detections
    for (i, rect) in enumerate(rects):
        temp_shape = predictor(gray, rect)
        temp_shape = shape_to_np(temp_shape)

        (x, y, w, h) = rect_to_bb(rect)
        face_shapes[:, i] = np.reshape(temp_shape, [136])
        face_areas[0, i] = w * h
    dlibout = np.reshape(np.transpose(face_shapes[:, np.argmax(face_areas)]), [68, 2])

    return dlibout, resized_image

def extract_features_labels():
    """
    This function extracts the landmarks features for all images in the folder 'dataset/celeba'.
    It also extracts the gender label for each image.
    :return:
        landmark_features:  an array containing 68 landmark points for each image in which a face was detected
        gender_labels:      an array containing the gender label (female=0 and male=1) for each image in
                            which a face was detected
    """
    image_paths = [os.path.join(images_dir, l) for l in os.listdir(images_dir)]
    target_size = None
    labels_file = open(os.path.join(images_dir, labels_filename), 'r')
    lines = labels_file.readlines()

    if os.path.isdir(images_dir):
        all_features = []
        all_labels = []

        for i in range(len(lines)):
            if i == 0: continue

            row = lines[i].split('\t')[1:]
            row[-1] = row[-1].replace('\n','').replace('.','')

            # load image
            img = image.img_to_array(
                image.load_img(image_paths[0] + '/' + row[0],
                               target_size=target_size,
                               interpolation='bicubic'))
            features, _ = run_dlib_shape(img)
            if features is not None:
                all_features.append(features)
                all_labels.append(int(row[1]))


                        
                        
    landmark_features = np.array(all_features)
    
    # converts -1 values into 0, so female=0 and male=1
    new_gender_labels = (np.array(all_labels) + 1)/2 
    
    return landmark_features, new_gender_labels

