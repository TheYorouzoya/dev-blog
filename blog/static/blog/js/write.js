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
        var content = document.getElementById('id_content');
        content.value = quill.root.innerHTML;

        var excerpt = document.getElementById('id_excerpt');
        const EXCERPT_LENGTH = 196;
        excerpt.value = quill.getText().slice(0, EXCERPT_LENGTH) + '...'; 
    };
})