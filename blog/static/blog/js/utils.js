

export const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


/**
 * Convert the Base64 image encoding to a blob and upload to server.
 * Code is from: https://ourcodeworld.com/articles/read/322/how-to-convert-a-base64-image-into-a-image-file-and-upload-it-with-an-asynchronous-form-using-jquery
 */
export async function uploadBase64Img(base64Str, article_id) {
    if (typeof base64Str !== 'string' || base64Str.length < 100) {
        return base64Str;
    }
    const url = await b64ToUrl(base64Str, article_id);
    return url;
}


function b64ToBlob(b64Data, contentType, sliceSize) {
    contentType = contentType || '';
    sliceSize = sliceSize || 512;

    // decode Base64 string
    var byteCharacters = atob(b64Data);
    var byteArrays = [];

    // slice into chunks
    for (var offset = 0; offset < byteCharacters.length; offset += sliceSize) {
        var slice = byteCharacters.slice(offset, offset + sliceSize);

        var byteNumbers = new Array(slice.length);
        for (var i = 0; i < slice.length; i++) {
            byteNumbers[i] = slice.charCodeAt(i);
        }

        var byteArray = new Uint8Array(byteNumbers);

        byteArrays.push(byteArray);
    }

    var blob = new Blob(byteArrays, {type: contentType});
    return blob;
}

function b64ToUrl(base64Str, article_id) {
    return new Promise(resolve => {
        var block = base64Str.split(";");
        var extension = block[0].split("/")[1];
        var contentType = block[0].split(":")[1];
        var imageData = block[1].split(",")[1];
        var blob = b64ToBlob(imageData, contentType);
        const csrfToken = getCookie('csrftoken');

        const formData = new FormData();
        formData.append('image', blob, `article-${article_id}.${extension}`);
        formData.append('article', article_id);

        fetch('/images/upload/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => resolve(data))
    })
}

