
from TextFunction import preprocess


from tensorflow.keras.preprocessing.sequence import pad_sequences
from googletrans import Translator
import pickle
from nltk.stem import WordNetLemmatizer
from tensorflow.keras import models
from tensorflow.keras import layers




model = models.Sequential()
model.add(layers.Embedding(25000, 80, input_length=100))
model.add(layers.Flatten())
model.add(layers.Dense(64, activation='relu'))
model.add(layers.Dropout(0.5))
model.add(layers.Dense(32, activation='relu'))
model.add(layers.Dropout(0.5))
model.add(layers.Dense(16, activation='relu'))
model.add(layers.Dense(1, activation='sigmoid'))

model.load_weights('text_model.h5')

translator = Translator()


handle = open('tokenizer.pickle', 'rb')
tokenizer = pickle.load(handle)



def predict_text_sentiment(text):

    x = Translator().translate(text, src='ca', dest='en')
    x = [x.text]
    print(x)
    x = preprocess(x , WordNetLemmatizer())
    x = tokenizer.texts_to_sequences(x)
    x = pad_sequences(x, maxlen=100)
    r = model.predict(x)
    return r[0]