from django.shortcuts import render

from blog.api_clients.lichess_client import get_lichess_puzzle_stats
from blog.api_clients.github_profile_card_client import get_github_profile_card

def about(request):
    puzzle_stats = get_lichess_puzzle_stats()
    github_card = get_github_profile_card()

    context = {
        "puzzle_stats": puzzle_stats,
        "github_card": github_card,
    }
    
    return render(request, 'blog/about.html', context)