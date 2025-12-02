const SEARCH_URL = "/search";

export async function searchArticles(query) {
    const stripped = query.trim();

    if (!stripped || stripped === "") {
        return [];
    }

    const apiResponse = await fetch(`${SEARCH_URL}/article/?q=${stripped}`);
    const data = await apiResponse.json();
    const searchResults = data["results"];

    return searchResults;
}