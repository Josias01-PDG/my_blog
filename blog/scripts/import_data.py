from blog.models import Article
import csv

def run():
    for i in range(20, 41 ):
        article = Article()
        article.title = f"Article {i}"
        article.content = f"Contenu de l'article {i}"
        article.image = "http://default"
        article.save()
print("Données importées avec succès !")