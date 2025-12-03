import { getCookie, uploadBase64Img } from "./utils.js";

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

    // pre-populate editor with saved data (if any)
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

    let autoSaveTimeout = null;
    const TIMEOUT_DURATION_MS = 2000;

    quill.on('text-change', function (delta, oldDelta, source) {
        if (source === 'user') {
            clearTimeout(autoSaveTimeout);
            autoSaveTimeout = setTimeout(saveAndUploadEditorContent, TIMEOUT_DURATION_MS);
        }
    });

    const saveButton = document.getElementById('save-article');
    saveButton.onclick = saveAndUploadEditorContent;
    
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
        );

        const results = await Promise.all(uploadPromises);

        results.forEach(({ img, data }) => {
            img.setAttribute("src", data.url);
            img.setAttribute("data-article-image-id", data.id);
        });
    }

    async function saveAndUploadEditorContent () {
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
        .then(data => updateAutoSaveStatus(data))
    }

    const updateAutoSaveStatus = (data) => {
        const status = document.getElementById('article-save-status');
        status.textContent = "";
        if (data["error"]) {
            status.textContent = `Auto-save failed: ${data["error"]}`;
        } else {
            const now = new Date();
            const formattedTime = now.toLocaleTimeString(
                'en-US', 
                { hour: '2-digit', minute: '2-digit', hour12: true }
            );
            status.textContent = `Last Saved: ${formattedTime}`;
        }
    }
})