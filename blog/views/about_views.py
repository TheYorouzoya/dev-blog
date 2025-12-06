from django.shortcuts import render

from blog.lichess_client import get_lichess_puzzle_stats

def about(request):
    puzzle_stats = get_lichess_puzzle_stats()

    context = {
        "puzzle_stats": puzzle_stats
    }
    return render(request, 'blog/about.html', context)