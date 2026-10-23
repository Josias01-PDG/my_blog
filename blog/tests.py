from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Article, Category, ContactMessage, Subscriber, Video

# Stockage statique simple : pas besoin d'avoir lancé collectstatic pour tester
TEST_STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}


@override_settings(STORAGES=TEST_STORAGES)
class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Technologie", description="Articles tech")
        cls.article = Article.objects.create(
            title="Mon premier article",
            category=cls.category,
            content="Contenu de test",
            image="http://default",
        )
        cls.video = Video.objects.create(
            title="Ma première vidéo",
            description="Description de test",
            file="videos/test.mp4",
        )


class PagesTests(BaseTestCase):
    def test_pages_publiques_repondent(self):
        for name in ("home", "videos", "about", "privacy", "terms", "contact"):
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

    def test_accueil_affiche_article(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Mon premier article")

    def test_detail_article(self):
        response = self.client.get(reverse("detail", args=[self.article.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mon premier article")

    def test_detail_article_inexistant_renvoie_404(self):
        response = self.client.get(reverse("detail", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_page_categorie(self):
        response = self.client.get(reverse("category", args=[self.category.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mon premier article")

    def test_categorie_inexistante_renvoie_404(self):
        response = self.client.get(reverse("category", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_footer_liste_les_categories(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Technologie")


class SearchTests(BaseTestCase):
    def test_recherche_trouve_article_et_video(self):
        response = self.client.get(reverse("search"), {"q": "premi"})
        self.assertContains(response, "Mon premier article")
        self.assertContains(response, "Ma première vidéo")

    def test_recherche_sans_resultat(self):
        response = self.client.get(reverse("search"), {"q": "zzzzzz"})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Mon premier article")

    def test_recherche_vide(self):
        response = self.client.get(reverse("search"))
        self.assertEqual(response.status_code, 200)


class ContactTests(BaseTestCase):
    def test_message_valide_est_enregistre(self):
        response = self.client.post(reverse("contact"), {
            "name": "Jo",
            "email": "jo@example.com",
            "subject": "Bonjour",
            "message": "Un message de test",
        })
        self.assertRedirects(response, reverse("contact"))
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_formulaire_vide_est_refuse(self):
        response = self.client.post(reverse("contact"), {})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_robot_avec_champ_piege_est_ignore(self):
        self.client.post(reverse("contact"), {
            "name": "Robot",
            "email": "robot@example.com",
            "subject": "Spam",
            "message": "Spam",
            "website": "http://spam.example",
        })
        self.assertEqual(ContactMessage.objects.count(), 0)


class NewsletterTests(BaseTestCase):
    def test_inscription_valide(self):
        response = self.client.post(reverse("subscribe"), {"email": "Test@Example.com"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Subscriber.objects.filter(email="test@example.com").exists())

    def test_pas_de_doublon(self):
        self.client.post(reverse("subscribe"), {"email": "a@example.com"})
        self.client.post(reverse("subscribe"), {"email": "a@example.com"})
        self.assertEqual(Subscriber.objects.count(), 1)

    def test_email_invalide_refuse(self):
        self.client.post(reverse("subscribe"), {"email": "abc"})
        self.assertEqual(Subscriber.objects.count(), 0)

    def test_reactivation_d_un_inscrit(self):
        Subscriber.objects.create(email="b@example.com", is_active=False)
        self.client.post(reverse("subscribe"), {"email": "b@example.com"})
        self.assertTrue(Subscriber.objects.get(email="b@example.com").is_active)

    def test_acces_direct_en_get_interdit(self):
        response = self.client.get(reverse("subscribe"))
        self.assertEqual(response.status_code, 405)


class NavbarTests(BaseTestCase):
    def test_bouton_admin_cache_aux_visiteurs(self):
        response = self.client.get(reverse("home"))
        self.assertNotContains(response, "btn-admin")

    def test_bouton_admin_visible_pour_le_staff(self):
        user = get_user_model().objects.create_user("staff", password="x", is_staff=True)
        self.client.force_login(user)
        response = self.client.get(reverse("home"))
        self.assertContains(response, "btn-admin")


class PaginationTests(BaseTestCase):
    def test_douze_articles_par_page(self):
        Article.objects.bulk_create([
            Article(title=f"Extra {i}", category=self.category, content="x", image="http://default")
            for i in range(14)
        ])  # 14 + l'article de base = 15 articles
        page1 = self.client.get(reverse("home"))
        page2 = self.client.get(reverse("home"), {"page": 2})
        self.assertEqual(len(page1.context["liste_articles"]), 12)
        self.assertEqual(len(page2.context["liste_articles"]), 3)

    def test_page_trop_grande_ne_plante_pas(self):
        response = self.client.get(reverse("home"), {"page": 999})
        self.assertEqual(response.status_code, 200)


class ModelTests(TestCase):
    def test_embed_youtube(self):
        a = Article(video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertEqual(a.embed_url, "https://www.youtube.com/embed/dQw4w9WgXcQ")
        self.assertFalse(a.embed_vertical)

    def test_embed_youtube_lien_court(self):
        a = Article(video_url="https://youtu.be/dQw4w9WgXcQ")
        self.assertEqual(a.embed_url, "https://www.youtube.com/embed/dQw4w9WgXcQ")

    def test_embed_vimeo(self):
        a = Article(video_url="https://vimeo.com/123456789")
        self.assertEqual(a.embed_url, "https://player.vimeo.com/video/123456789")

    def test_embed_tiktok_est_vertical(self):
        a = Article(video_url="https://www.tiktok.com/@compte/video/1234567890123456789")
        self.assertEqual(a.embed_url, "https://www.tiktok.com/embed/v2/1234567890123456789")
        self.assertTrue(a.embed_vertical)

    def test_lien_non_reconnu(self):
        a = Article(video_url="https://x.com/user/status/1")
        self.assertIsNone(a.embed_url)

    def test_sans_lien(self):
        self.assertIsNone(Article().embed_url)

    def test_image_par_defaut(self):
        a = Article(image="http://default")
        self.assertEqual(a.image_url, "https://picsum.photos/400/300")
        
        
class ErrorPagesTests(BaseTestCase):
    def test_page_404_personnalisee(self):
        response = self.client.get("/cette-page-n-existe-pas/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Page introuvable", status_code=404)
        self.assertContains(response, "Retour à l'accueil", status_code=404)