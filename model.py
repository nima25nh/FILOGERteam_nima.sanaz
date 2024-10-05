import pickle

with open('breast_cancer.pkl','rb') as f:
    model = pickle.load(f)

def predict_class(features):
    predictions = model.predict([features])
    return predictions[0]
import pickle

# Load the model
with open('breast_cancer.pkl', 'rb') as f:
    model = pickle.load(f)

# Function to predict the class and return descriptive result
def predict_class(features):
    predictions = model.predict([features])
    if predictions[0] == 0:
        return "Benign (خوش‌خیم)"
    else:
        return "Malignant (بدخیم)"
