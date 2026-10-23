from blog.models import Article, Category


def run():
    categorie, _ = Category.objects.get_or_create(
        name="Général",
        defaults={"description": "Catégorie par défaut"},
    )

    for i in range(20, 41):
        Article.objects.get_or_create(
            title=f"Article {i}",
            defaults={
                "category": categorie,
                "content": f"Contenu de l'article {i}",
                "image": "http://default",
            },
        )

    print("Données importées avec succès !")