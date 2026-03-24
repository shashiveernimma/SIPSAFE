import cv2
import os
import numpy as np
from sklearn.svm import SVC
import joblib

data = []
labels = []

for label in ["microplastic","clean"]:

    folder = f"dataset/{label}"

    for img_name in os.listdir(folder):

        img = cv2.imread(os.path.join(folder,img_name))

        img = cv2.resize(img,(100,100))

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        data.append(gray.flatten())

        if label == "microplastic":
            labels.append(1)
        else:
            labels.append(0)

model = SVC()

model.fit(data,labels)

joblib.dump(model,"ml_model/microplastic_model.pkl")

print("Model retrained successfully")