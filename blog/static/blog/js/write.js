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

    document.querySelector('form#article-form').onsubmit = () => {
        saveContent();
        saveExcerpt();
    };

    const saveButton = document.getElementById('save-article');
    saveButton.onclick = () => {
        const form = document.querySelector('form#article-form');
        
        saveContent();
        saveExcerpt();
        
        const articleId = form.dataset.articleId;
        const title = document.getElementById('id_title').value;
        const content = document.getElementById('id_content').value;
        const excerpt = document.getElementById('id_excerpt').value;
        const csrfToken = getCookie('csrftoken');
        
        fetch(`autosave/`, {
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
        var content = document.getElementById('id_content');
        content.value = quill.root.innerHTML;
    }

    const saveExcerpt = () => {
        var excerpt = document.getElementById('id_excerpt');
        const EXCERPT_LENGTH = 194;
        excerpt.value = quill.getText().slice(0, EXCERPT_LENGTH) + '...'; 
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
})