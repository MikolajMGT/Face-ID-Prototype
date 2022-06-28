import os
import cv2
import uuid
import pickle
import numpy as np
from PIL import Image
from copy import copy
import face_recognition
from pathlib import Path

ESC_CODE = 27
SPACE_CODE = 32


class Auth:

    def __init__(self):
        print('Auth.init() performed')
        self.__load()

    def __load(self):
        print('Auth.load() performed')

        # load encoded user objects from database
        try:
            with open(r'data/db/users.pickle', 'rb') as f:
                og_labels = pickle.load(f)
                print(og_labels)
        except FileNotFoundError:
            print('file users.pickle cannot be found, creating a new one')

        # map user directories into ids
        user_ids = collect_user_ids()
        # if something has changed (i.e. new images appeared) db is updated
        self.known_faces = update_db_if_necessary(user_ids)

    def reload(self):
        print('Auth.reload() performed')
        self.__load()

    def authenticate(self):
        image = take_photo(self.known_faces)

        if image is None:
            return []

        small_frame = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]
        save_features_image(rgb_small_frame)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        face_names = []
        for face_encoding in face_encodings:
            for user_id, face in self.known_faces.items():
                matches = face_recognition.compare_faces([face], face_encoding)
                face_distances = face_recognition.face_distance([face], face_encoding)
                best_match = np.argmin(face_distances)
                print(f'This is the match in best match {matches[best_match]}')
                if matches[best_match]:
                    face_names.append(user_id)
                    break
        print(f'The best match(es) is {str(face_names)}')

        return face_names

    def recognition(self):
        take_photo(self.known_faces, True)


def collect_user_ids():
    user_ids = []

    for root, dirs, files in os.walk('data/images'):
        for file in files:

            if not file.endswith('png') and not file.endswith('jpg'):
                continue

            path = os.path.join(root, file)
            user_id = os.path.basename(os.path.dirname(path)).replace(' ', '-').lower()

            if user_id in user_ids:
                continue

            user_ids.append(user_id)

    return user_ids


def update_db_if_necessary(user_ids):
    known_faces = {}
    Path(f'data/db').mkdir(parents=True, exist_ok=True)

    if len(user_ids) == 0:
        with open('data/db/faces.pickle', 'wb') as known_faces_file:
            pickle.dump(known_faces, known_faces_file)
            return known_faces

    with open('data/db/users.pickle', 'wb') as file:
        pickle.dump(user_ids, file)

    for user_id in user_ids:
        images_num = len([filename for filename in os.listdir(f'data/images/{user_id}')
                          if os.path.isfile(os.path.join(f'data/images/{user_id}', filename))])

        for image_num in range(0, images_num):
            if user_id not in known_faces:
                directory = os.path.join('data/images', user_id, f'{str(image_num)}.png')
                img = face_recognition.load_image_file(directory)
                img_encoding = face_recognition.face_encodings(img)[0]
                known_faces[user_id] = img_encoding

    print(f'number of images in db: {str(len(known_faces))}')
    with open('data/db/faces.pickle', 'wb') as known_faces_file:
        pickle.dump(known_faces, known_faces_file)
    return known_faces


def take_photo(known_faces, diagnostics=False):
    cap = cv2.VideoCapture(0)

    while True:
        ret, image = cap.read()
        cv2.imshow('Take Photo', image)
        if not ret:
            break

        if diagnostics:
            realtime_diagnostics(copy(image), known_faces)

        key = cv2.waitKey(1)

        if key % 256 == ESC_CODE:
            print('esc press detected, aborting')
            cap.release()
            cv2.destroyAllWindows()
            return None
        elif key % 256 == SPACE_CODE:
            print('space press detected, taking photo')
            cap.release()
            cv2.destroyAllWindows()
            break

    return image


# this function enable realtime recognition of registered users (diagnostic purposes only)
def realtime_diagnostics(image, known_faces):
    small_frame = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = small_frame[:, :, ::-1]

    # find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    face_names = []
    for face_encoding in face_encodings:
        # see if the face is a match for the known face(s)
        faces = []
        name_mapping = {}

        idx = 0
        for user_id, face in known_faces.items():
            faces.append(face)
            name_mapping[idx] = user_id
            idx += 1

        matches = face_recognition.compare_faces(faces, face_encoding)
        name = "Unknown"

        face_distances = face_recognition.face_distance(faces, face_encoding)

        if len(face_distances) != 0:
            best_match = np.argmin(face_distances)
            if matches[best_match]:
                name = name_mapping[int(best_match)]

        face_names.append(name)

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # draw a box around the face
        cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)

        # draw a label with a name below the face
        cv2.rectangle(image, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(image, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # display the resulting image
    cv2.imshow('Video', image)


# this function save image with pointed features (diagnostic purposes only)
def save_features_image(image):
    face_landmarks_list = face_recognition.face_landmarks(image)
    feature_image = copy(image)
    picture = Image.fromarray(feature_image)

    for elem in face_landmarks_list:
        for name, coords in elem.items():
            for x, y in coords:
                picture.putpixel((x, y), (255, 255, 255))
    picture.save(f'data/features/{str(uuid.uuid4())}.png')
