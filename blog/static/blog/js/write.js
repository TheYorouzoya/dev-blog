document.addEventListener('DOMContentLoaded', () => {
    const toolbarOptions = [
        
        ['bold', 'italic', 'underline', 'strike'],        // toggled buttons
        ['blockquote', 'code-block'],
        ['link', 'image', 'video'],
        
        [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
        [{ 'list': 'ordered'}, { 'list': 'bullet' }, { 'list': 'check' }],
        [{ 'script': 'sub'}, { 'script': 'super' }],      // superscript/subscript
        [{ 'indent': '-1'}, { 'indent': '+1' }],          // outdent/indent
        [{ 'direction': 'rtl' }],                         // text direction

        [{ 'color': [] }, { 'background': [] }],          // dropdown with defaults from theme
        [{ 'align': [] }],

        ['clean']                                         // remove formatting button
    ];
    const quill = new Quill('#editor', {
        modules: {
            syntax: true,
            toolbar: toolbarOptions
        },
        theme: 'snow',
    });

    const editorContent = document.getElementById('id_content');
    if (editorContent.value) {
        quill.root.innerHTML = editorContent.value;
    }

    const articleId = document.querySelector('form#article-form').dataset.articleId;

    document.querySelector('form#article-form').onsubmit = async () => {
        await uploadImages(articleId);
        saveContent();
        saveExcerpt();
        
    };

    const saveButton = document.getElementById('save-article');
    saveButton.onclick = async () => {
        await uploadImages(articleId);
        saveContent();
        saveExcerpt();
        
        const title = document.getElementById('id_title').value;
        const content = document.getElementById('id_content').value;
        const excerpt = document.getElementById('id_excerpt').value;
        const csrfToken = getCookie('csrftoken');
        
        fetch(`/autosave/`, {
            method: 'POST',
            body: JSON.stringify(
                {
                    id: articleId,
                    title: title,
                    content: content,
                    excerpt: excerpt,
                }
            ),
            headers: {
                "X-CSRFToken": csrfToken
            }
        })
        .then(response => response.json())
        .then(data => console.log(data))
    }
    
    const saveContent = () => {
        // copy editor content
        var content = document.getElementById('id_content');
        content.value = quill.root.innerHTML;

        // process content for uploaded images
        const imgs = content.querySelectorAll("img[data-article-image-id]");
        const ids = Array.from(imgs).map(img => img.getAttribute("data-article-image-id"));
        
        document.querySelector("input[name='image_ids']").value = JSON.stringify(ids);
    }

    const saveExcerpt = () => {
        var excerpt = document.getElementById('id_excerpt');
        const EXCERPT_LENGTH = 194;
        excerpt.value = quill.getText().slice(0, EXCERPT_LENGTH) + '...'; 
    }

    const uploadImages = async (article_id) => {
        const imgs = Array.from(
            quill.container.querySelectorAll('img[src^="data:"]')
        );

        const uploadPromises = imgs.map(img =>
            uploadBase64Img(img.getAttribute("src"), article_id)
                .then(data => ({ img, data }))
        )

        const results = await Promise.all(uploadPromises);

        results.forEach(({ img, data }) => {
            img.setAttribute("src", data.url);
            img.setAttribute("data-article-image-id", data.id);
        })
    }
})


/**
 * Convert the Base64 image encoding to a blob and upload to server.
 * Code is from: https://ourcodeworld.com/articles/read/322/how-to-convert-a-base64-image-into-a-image-file-and-upload-it-with-an-asynchronous-form-using-jquery
 */
async function uploadBase64Img(base64Str, article_id) {
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

const getCookie = (name) => {
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