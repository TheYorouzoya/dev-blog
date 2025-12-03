import { getCSRFToken } from "./utils.js";

const API_BASE_URL = "/api";
const SEARCH_URL = `${API_BASE_URL}/search`;

export async function searchArticles(query) {
    const ARTICLES_ENDPOINT = `${SEARCH_URL}/articles`;
    const stripped = query.trim();

    if (!stripped || stripped === "") {
        // fail silently if search query is empty
        return [];
    }

    const apiResponse = await fetch(`${ARTICLES_ENDPOINT}?q=${stripped}`);
    const data = await apiResponse.json();
    const searchResults = data["results"];

    return searchResults;
}

export async function autoSaveArticle(article) {
    const ARTICLE_AUTOSAVE_ENDPOINT = `${API_BASE_URL}/articles/autosave/`;

    if (!article) {
        throw new Error("Article data is required!");
    }

    const apiResponse = await fetch(ARTICLE_AUTOSAVE_ENDPOINT, {
        method: 'POST',
        body: JSON.stringify(article),
        headers: {
            "X-CSRFToken": getCSRFToken(),
        }
    });

    return await apiResponse.json();
}

export async function uploadArticleImage(formData) {
    const IMAGE_UPLOAD_ENDPOINT = `${API_BASE_URL}/images/upload/`;

    if (!formData) {
        throw new Error("FormData is required!");
    }

    const apiResponse = await fetch(IMAGE_UPLOAD_ENDPOINT, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken(),
        }
    });

    if (!apiResponse.ok) {
        throw new Error(`Upload failed ${apiResponse["errors"]}`);
    }

    return  await apiResponse.json();
}