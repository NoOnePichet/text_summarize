from attention import AttentionLayer
import numpy as np  
import pandas as pd 
import re           
from bs4 import BeautifulSoup 
from keras.preprocessing.text import Tokenizer 
from keras.preprocessing.sequence import pad_sequences
from nltk.corpus import stopwords   
from tensorflow.keras.layers import Input, LSTM, Embedding, Dense, Concatenate, TimeDistributed, Bidirectional
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping
import warnings
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from keras import backend as K 
#nltk.download('popular')

#contraction to full words
contraction_mapping = {"ain't": "is not", "aren't": "are not","can't": "cannot", "'cause": "because", "could've": "could have", "couldn't": "could not",

                           "didn't": "did not", "doesn't": "does not", "don't": "do not", "hadn't": "had not", "hasn't": "has not", "haven't": "have not",

                           "he'd": "he would","he'll": "he will", "he's": "he is", "how'd": "how did", "how'd'y": "how do you", "how'll": "how will", "how's": "how is",

                           "I'd": "I would", "I'd've": "I would have", "I'll": "I will", "I'll've": "I will have","I'm": "I am", "I've": "I have", "i'd": "i would",

                           "i'd've": "i would have", "i'll": "i will",  "i'll've": "i will have","i'm": "i am", "i've": "i have", "isn't": "is not", "it'd": "it would",

                           "it'd've": "it would have", "it'll": "it will", "it'll've": "it will have","it's": "it is", "let's": "let us", "ma'am": "madam",

                           "mayn't": "may not", "might've": "might have","mightn't": "might not","mightn't've": "might not have", "must've": "must have",

                           "mustn't": "must not", "mustn't've": "must not have", "needn't": "need not", "needn't've": "need not have","o'clock": "of the clock",

                           "oughtn't": "ought not", "oughtn't've": "ought not have", "shan't": "shall not", "sha'n't": "shall not", "shan't've": "shall not have",

                           "she'd": "she would", "she'd've": "she would have", "she'll": "she will", "she'll've": "she will have", "she's": "she is",

                           "should've": "should have", "shouldn't": "should not", "shouldn't've": "should not have", "so've": "so have","so's": "so as",

                           "this's": "this is","that'd": "that would", "that'd've": "that would have", "that's": "that is", "there'd": "there would",

                           "there'd've": "there would have", "there's": "there is", "here's": "here is","they'd": "they would", "they'd've": "they would have",

                           "they'll": "they will", "they'll've": "they will have", "they're": "they are", "they've": "they have", "to've": "to have",

                           "wasn't": "was not", "we'd": "we would", "we'd've": "we would have", "we'll": "we will", "we'll've": "we will have", "we're": "we are",

                           "we've": "we have", "weren't": "were not", "what'll": "what will", "what'll've": "what will have", "what're": "what are",

                           "what's": "what is", "what've": "what have", "when's": "when is", "when've": "when have", "where'd": "where did", "where's": "where is",

                           "where've": "where have", "who'll": "who will", "who'll've": "who will have", "who's": "who is", "who've": "who have",

                           "why's": "why is", "why've": "why have", "will've": "will have", "won't": "will not", "won't've": "will not have",

                           "would've": "would have", "wouldn't": "would not", "wouldn't've": "would not have", "y'all": "you all",

                           "y'all'd": "you all would","y'all'd've": "you all would have","y'all're": "you all are","y'all've": "you all have",

                           "you'd": "you would", "you'd've": "you would have", "you'll": "you will", "you'll've": "you will have",

                           "you're": "you are", "you've": "you have"}

stop_words = set(stopwords.words('english'))

#text cleaning
'''
Convert everything to lowercase
Remove HTML tags
Contraction mapping
Remove (‘s)
Remove any text inside the parenthesis ( )
Eliminate punctuations and special characters
Remove stopwords
Remove short words 
'''
def text_cleaning(text):
    newString = text.lower()
    newString = BeautifulSoup(newString, "lxml").text
    newString = re.sub(r'\([^)]*\)', '', newString)
    newString = re.sub('"','', newString)
    newString = ' '.join([contraction_mapping[t] if t in contraction_mapping else t for t in newString.split(" ")])    
    newString = re.sub(r"'s\b","",newString)
    newString = re.sub("[^a-zA-Z]", " ", newString) 
    tokens = [w for w in newString.split() if not w in stop_words]
    long_words=[]
    for i in tokens:
        if len(i)>=3:                  #removing short word
            long_words.append(i)   
    return (" ".join(long_words)).strip()



def summary_cleaning(text):
    newString = re.sub('"','', text)
    newString = ' '.join([contraction_mapping[t] if t in contraction_mapping else t for t in newString.split(" ")])    
    newString = re.sub(r"'s\b","",newString)
    newString = re.sub("[^a-zA-Z]", " ", newString)
    newString = newString.lower()
    tokens=newString.split()
    newString=''
    for i in tokens:
        if len(i)>1:                                 
            newString=newString+i+' '  
    return newString

def visualization_of_cleaned_text_and_summary(data):
    print("Start visualization")
    text_word_count = []
    summary_word_count = []

    # populate the lists with sentence lengths
    print("iterate over cleaned_text")

    for i in data['cleaned_text']:
        text_word_count.append(len(i.split()))
        
    print("iterate over cleaned_summary")    

    for i in data['cleaned_summary']:
            summary_word_count.append(len(i.split()))
            
    length_df = pd.DataFrame({'text':text_word_count, 'summary':summary_word_count})
    length_df.hist(bins = 30)
    plt.show()

def main():
    
    pd.set_option("display.max_colwidth", 200)
    warnings.filterwarnings("ignore")

    #data=pd.read_csv("./input/amazon-fine-food-reviews/Reviews.csv",nrows=100000)
    #floydhub data used
    data = pd.read_csv("/floyd/input/amazon_fine_food_reviews",nrows=100000)

    data.drop_duplicates(subset=['Text'],inplace=True)  #dropping duplicates
    data.dropna(axis=0,inplace=True)   #dropping na

    
    cleaned_text = []
    idx_cleaned_text = 1
    print("Start cleaning text")
    for t in data['Text']:
        cleaned_text.append(text_cleaning(t))
        if idx_cleaned_text % 10000 == 0:
            print(f"Cleaned text: {idx_cleaned_text}/{len(data['Text'])}")
        idx_cleaned_text += 1

    cleaned_summary = []
    idx_cleaned_summary = 1
    print("Start cleaning summary")
    for t in data['Summary']:
        cleaned_summary.append(summary_cleaning(t))
        if idx_cleaned_summary % 10000 == 0:
            print(f"Cleaned summary: {idx_cleaned_summary}/{len(data['Summary'])}")
        idx_cleaned_summary += 1

    data['cleaned_text']=cleaned_text
    data['cleaned_summary']=cleaned_summary
    data['cleaned_summary'].replace('', np.nan, inplace=True)
   
    data.dropna(axis=0,inplace=True)
    data['cleaned_summary'] = data['cleaned_summary'].apply(lambda x : '_START_ '+ x + ' _END_')

    # Visualization to understand things
    #visualization_of_cleaned_text_and_summary(data)

    max_len_text=80 
    max_len_summary=10

    # split data for training
    x_tr,x_val,y_tr,y_val=train_test_split(data['cleaned_text'],data['cleaned_summary'],test_size=0.1,random_state=0,shuffle=True)

    # prepare a tokenizer for reviews on training data
    x_tokenizer = Tokenizer()
    x_tokenizer.fit_on_texts(list(x_tr))
    
    # convert text sequences into integer sequences
    x_tr    =   x_tokenizer.texts_to_sequences(x_tr) 
    x_val   =   x_tokenizer.texts_to_sequences(x_val)
    
    # padding zero upto maximum length
    x_tr    =   pad_sequences(x_tr,  maxlen=max_len_text, padding='post') 
    x_val   =   pad_sequences(x_val, maxlen=max_len_text, padding='post')
    
    x_voc_size   =  len(x_tokenizer.word_index) +1
    
    # preparing a tokenizer for summary on training data 
    y_tokenizer = Tokenizer()
    y_tokenizer.fit_on_texts(list(y_tr))
    
    # convert summary sequences into integer sequences
    y_tr    =   y_tokenizer.texts_to_sequences(y_tr) 
    y_val   =   y_tokenizer.texts_to_sequences(y_val) 
    
    # padding zero upto maximum length
    y_tr    =   pad_sequences(y_tr, maxlen=max_len_summary, padding='post')
    y_val   =   pad_sequences(y_val, maxlen=max_len_summary, padding='post')
    
    y_voc_size  =   len(y_tokenizer.word_index) +1
    
    
    
    '''
    Return Sequences = True: When the return sequences parameter is set to True, LSTM produces the hidden state and cell state for every timestep
    Return State = True: When return state = True, LSTM produces the hidden state and cell state of the last timestep only
    Initial State: This is used to initialize the internal states of the LSTM for the first timestep
    Stacked LSTM: Stacked LSTM has multiple layers of LSTM stacked on top of each other. This leads to a better representation of the sequence. I encourage you to experiment with the multiple layers of the LSTM stacked on top of each other (it’s a great way to learn this)
    '''
    
    print("start creating LSTM and Encoder / Decoder")
    K.clear_session()
    latent_dim = 500 
    
    # Encoder 
    encoder_inputs = Input(shape=(max_len_text,)) 
    enc_emb = Embedding(x_voc_size, latent_dim,trainable=True)(encoder_inputs) 
    
    # LSTM 1 
    encoder_lstm1 = LSTM(latent_dim,return_sequences=True,return_state=True) 
    encoder_output1, state_h1, state_c1 = encoder_lstm1(enc_emb) 
    
    # LSTM 2 
    encoder_lstm2 = LSTM(latent_dim,return_sequences=True,return_state=True) 
    encoder_output2, state_h2, state_c2 = encoder_lstm2(encoder_output1) 
    
    # LSTM 3 
    encoder_lstm3=LSTM(latent_dim, return_state=True, return_sequences=True) 
    encoder_outputs, state_h, state_c= encoder_lstm3(encoder_output2) 
    
    # Set up the decoder. 
    decoder_inputs = Input(shape=(None,)) 
    dec_emb_layer = Embedding(y_voc_size, latent_dim,trainable=True) 
    dec_emb = dec_emb_layer(decoder_inputs) 
    
    # LSTM using encoder_states as initial state
    decoder_lstm = LSTM(latent_dim, return_sequences=True, return_state=True) 
    decoder_outputs,decoder_fwd_state, decoder_back_state = decoder_lstm(dec_emb,initial_state=[state_h, state_c]) 
    
    # Attention Layer
    attn_layer = AttentionLayer(name='attention_layer') 
    attn_out, attn_states = attn_layer([encoder_outputs, decoder_outputs]) 
    
    # Concat attention output and decoder LSTM output 
    decoder_concat_input = Concatenate(axis=-1, name='concat_layer')([decoder_outputs, attn_out])
    
    # Dense layer
    decoder_dense = TimeDistributed(Dense(y_voc_size, activation='softmax')) 
    decoder_outputs = decoder_dense(decoder_concat_input) 
    
    # Define the model
    model = Model([encoder_inputs, decoder_inputs], decoder_outputs) 
    #model.summary()
    model.compile(optimizer='rmsprop', loss='sparse_categorical_crossentropy')
    
    # Model will stop training once the validation loss increases
    es = EarlyStopping(monitor='val_loss', mode='min', verbose=1)

    # training model in batch of 512 in 10% of our dataset
    history=model.fit([x_tr,y_tr[:,:-1]], y_tr.reshape(y_tr.shape[0],y_tr.shape[1], 1)[:,1:] ,epochs=50,callbacks=[es],batch_size=512, validation_data=([x_val,y_val[:,:-1]], y_val.reshape(y_val.shape[0],y_val.shape[1], 1)[:,1:]))
    
    #save model
    model.save('en_1.model')

    plt.plot(history.history['loss'], label='train') 
    plt.plot(history.history['val_loss'], label='test') 
    plt.legend()
    plt.show()
   
    #load model
    #new_model = tensorflow.keras.models.load_model('en_1.model')
    
    
    
    
main()
    
