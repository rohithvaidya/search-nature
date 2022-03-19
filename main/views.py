from django.shortcuts import render, reverse, redirect
from django.db.models import Q
from django.contrib import messages
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist
from .models import Article, Category, Search
from user.models import Profile, Subscriber


def home(request):
    current_user = request.user
    recent_articles = Article.objects.all().order_by('-id')[:7]
    top_articles = Article.objects.all(
    ).only(
        'title', 'article_image'
    ).annotate(
        # Summing total number of clicks for each article
        Count('clicks')
    ).order_by(
        # listing last five popular articles
        '-id'
    )[:3]
    print(top_articles)

    categories = Category.objects.all()

    # get the newsletter subscriber
    if request.user.is_authenticated:
        if request.method == 'GET':
            query = request.GET.get('q')
            category = request.GET.get('category')
            random_text = request.GET.get('random_text')
            title_lookups = Q(title__icontains=query) & Q(selected_category__title__icontains=category)
            if query is not None and title_lookups:
                
                # store the search to the database
                search = Search.objects.create(title=query, user=current_user)

                lookups = Article.objects.filter(title_lookups).distinct()

                context = {
                    'lookups': lookups,
                    'title_lookups': title_lookups,
                    'recent_articles': recent_articles,
                    'top_articles': top_articles,
                    'categories': categories,
                }

                return render(request, 'results.html', context)
            else:
                try:
                    if Subscriber.objects.get(user=request.user):
                        sub = Subscriber.objects.get(user=request.user)
                        print(sub)
                        return render(request, 'base.html', {'sub': sub.email})  
                        
                except ObjectDoesNotExist:
                    messages.warning(request, 'You are not a subscriber')    
                    return render(request, 'base.html')     
        else:
            return render(request, 'base.html')
    return render(request, 'base.html')


def article_view(request, slug):
    userprofile = Profile.objects.get(user=request.user)
    article = Article.objects.get(slug=slug)

    # read txt files
    with article.text.open('r') as f:
        lines = f.read()
        print(lines)
        f.close()
  
    try:
        article = Article.objects.get(slug=slug)
        article.clicks += 1
        article.text_field = str(lines)
        article.save()
    except ObjectDoesNotExist:
        messages.warning(request, 'Article is not found! Try again')
        raise Http404

    # related articles
    category = article.selected_category
    print(category)

    related_top_articles = Article.objects.filter(
        # filtering article with the same category
        selected_category=category
    ).only(
        'title', 'article_image'
    ).annotate(
        # Summing total number of clicks for each article
        Count('clicks')
    ).order_by(
        # listing last five popular articles
        '-id'
    )[:5]
    print(related_top_articles)
    
    # saving users who clicked
    current_user = request.user
    total_clicks = article.clicked_users.all()
    print(total_clicks)

    if not current_user in total_clicks:
        article.clicked_users.add(current_user)
    else:
        messages.info(request, 'The article has been clicked by the user!')

    # saving the clicked articles to the user's history
    click_history = userprofile.clicked_articles.all()
    print(click_history)

    if not article in click_history:
        userprofile.clicked_articles.add(article)
    else:
        messages.info(request, 'The article has been clicked by the user')    

    top_articles = Article.objects.all(
    ).only(
        'title', 'article_image'
    ).annotate(
        # Summing total number of clicks for each article
        Count('clicks')
    ).order_by(
        # listing last five popular articles
        '-id'
    )[:3]
    categories = Category.objects.all()

    context = {
        'article': article,
        'top_articles': top_articles,
        'categories': categories,
        'related_top_articles': related_top_articles,
        'recent_articles': Article.objects.all().order_by('-id')[:7],
        'lines': lines
    }

    return render(request, 'article.html', context)


def contact(request):
    return render(request, 'contact.html')


def about(request):
    return render(request, 'about.html')    

def instructions(request):
    return render(request, 'instructions.html')