from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .forms import ContactForm
from .models import Article, Category, ContactMessage, Subscriber, Video
from django.db.models import Q


# Create your views here.


def home(request):
    articles = Article.objects.select_related('category')
    paginator = Paginator(articles, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'index.html', {
        'liste_articles': page_obj,
        'page_obj': page_obj,
    })


def detail(request, article_id):
    article = get_object_or_404(Article, id = article_id)
    category = article.category
    articles_en_relation = Article.objects.filter(category = category).exclude(id = article_id)[:3]
    context = {
        'article': article,
        'category': category,
        'articles_en_relation': articles_en_relation
    }
    return render(request, 'detail.html', context)


def videos(request):
    liste_videos = Video.objects.all()
    context = {
        'liste_videos': liste_videos
    }
    return render(request, 'videos.html', context)


from django.db.models import Q
from .models import Article, Video

def search(request):
    query = request.GET.get('q', '')
    if query:
        resultats_articles = Article.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
        resultats_videos = Video.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
        
    else:
        resultats_articles = Article.objects.none()
        resultats_videos = Video.objects.none()
    context = {
        'resultats_articles': resultats_articles,
        'resultats_videos': resultats_videos,
        'query': query
    }

    return render(request, 'search.html', context)

def about(request):
    return render(request, 'about.html')


def privacy(request):
    return render(request, 'privacy.html')


def terms(request):
    return render(request, 'terms.html')


def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    articles = Article.objects.filter(category=category)
    paginator = Paginator(articles, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'category.html', {
        'category': category,
        'liste_articles': page_obj,
        'page_obj': page_obj,
    })
    
def contact(request):
    if request.method == 'POST':
        # Champ piège invisible : seuls les robots le remplissent
        if request.POST.get('website'):
            return redirect('contact')
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Merci ! Ton message a bien été envoyé.")
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})

@require_POST
def subscribe(request):
    email = request.POST.get('email', '').strip().lower()

    try:
        validate_email(email)
    except ValidationError:
        messages.error(request, "Cette adresse email n'est pas valide.")
    else:
        subscriber, created = Subscriber.objects.get_or_create(email=email)
        if created:
            messages.success(request, "Merci ! Tu es bien inscrit à la newsletter.")
        elif not subscriber.is_active:
            subscriber.is_active = True
            subscriber.save()
            messages.success(request, "Content de te revoir ! Ton inscription est réactivée.")
        else:
            messages.info(request, "Cette adresse est déjà inscrite.")

    # Retour à la page d'où vient le visiteur (seulement si elle est sur ton site)
    next_url = request.META.get('HTTP_REFERER', '')
    if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect('home')