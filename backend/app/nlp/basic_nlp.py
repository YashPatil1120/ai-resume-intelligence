import nltk
from nltk.stem import WordNetLemmatizer

nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("stopwords")

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer


text = "I am developing web applications and I developed a React application."


# Tokenization
tokens = word_tokenize(text)

print("Original tokens:")
print(tokens)


# Stopwords
stop_words = set(stopwords.words("english"))

filtered_tokens = [
    word for word in tokens
    if word.lower() not in stop_words
]

print("\nAfter removing stopwords:")
print(filtered_tokens)


# Stemming
stemmer = PorterStemmer()

stemmed_words = [
    stemmer.stem(word)
    for word in filtered_tokens
]

print("\nAfter stemming:")
print(stemmed_words)

# Lemmatization
lemmatizer = WordNetLemmatizer()

lemmatized_words = [
    lemmatizer.lemmatize(word)
    for word in filtered_tokens
]

print("\nAfter lemmatization:")
print(lemmatized_words)