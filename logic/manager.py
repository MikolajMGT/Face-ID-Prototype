import os
import cv2
from pathlib import Path
from tkinter import messagebox

ESC_CODE = 27
SPACE_CODE = 32


class Manager:

    def __init__(self, auth):
        self.auth = auth

    def register(self, username):
        print('Manager.register() performed')

        # load or create directory for user images
        if not os.path.exists('data/images'):
            os.makedirs('data/images')

        # create user directory of does not exist
        Path(f'data/images/{username}').mkdir(parents=True, exist_ok=True)

        # count user photos in directory
        files_num = len([filename for filename in os.listdir(f'data/images/{username}')
                         if os.path.isfile(os.path.join(f'data/images/{username}', filename))])

        # take photo and save
        save_photo(files_num, username)

        # load all the data again to consider last registration
        self.auth.reload()

    def login(self):
        print('Manager.login() performed')

        # returns username if face matched
        auth_user = self.auth.authenticate()
        if not auth_user:
            messagebox.showerror('Alert', 'Face does not match any user, please register to the service first.')
            return

        return auth_user


def save_photo(files_num, username):
    camera = cv2.VideoCapture(0)
    cv2.namedWindow('Take a photo')

    while True:
        ret, image = camera.read()
        cv2.imshow('Image', image)
        if not ret:
            break

        # wait for hitting button
        key = cv2.waitKey(1)

        if key % 256 == ESC_CODE:
            print('esc press detected, aborting')
            camera.release()
            cv2.destroyAllWindows()
            break
        elif key % 256 == SPACE_CODE:
            print('space press detected, taking photo')
            cv2.imwrite(f'data/images/{username.lower()}/{str(files_num)}.png', image)
            print(f'image has been written')

            camera.release()
            cv2.destroyAllWindows()
            break
