import { searchArticles } from './api.js';

document.addEventListener('DOMContentLoaded', () => {
    const navSearchInput = document.getElementById('nav-search-bar');
    const navSearchResults = document.getElementById('nav-search-results');

    // fetch articles when user types in search bar
    navSearchInput.addEventListener('keyup', async (event) => {
        const releasedKey = event.key;
        if (releasedKey === 'Escape') {
            navSearchResults.classList.remove("visible");
            navSearchResults.innerHTML = "";
            return;
        }
        
        const searchResults = await searchArticles(navSearchInput.value);
        navSearchResults.innerHTML = "";

        searchResults.forEach(result => {
            const article = document.createElement('li');
            article.textContent = result["title"];
            article.addEventListener('click', () => {
                window.location.assign(`/articles/${result["slug"]}/`);
            });
            navSearchResults.append(article);
        });

        if (searchResults.length <= 0) {
            navSearchResults.classList.remove("visible");
        } else {
            navSearchResults.classList.add("visible");
        }

    });

    // hide search results if user clicks away from search bar
    navSearchInput.addEventListener('focusout', () => {
        if (!navSearchResults.matches(":hover")) {
            navSearchResults.classList.remove("visible");
        }
    });

    // show search results if user is focused on search bar
    navSearchInput.addEventListener('focusin', () => {
        if (navSearchResults.childNodes.length > 0) {
            navSearchResults.classList.add("visible");
        }
    });
});