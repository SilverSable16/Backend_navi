from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

class PLNClassifier:
    def __init__(self):
        self.vectorizer = CountVectorizer()
        self.model = MultinomialNB()

    def entrenar(self, ejemplos):
        textos, etiquetas = zip(*ejemplos)
        X = self.vectorizer.fit_transform(textos)
        self.model.fit(X, etiquetas)

    def predecir(self, texto):
        X = self.vectorizer.transform([texto])
        return self.model.predict(X)[0]
