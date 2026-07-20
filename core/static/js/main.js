// JobFinder - Main JS

// File Upload Handlers
const fileInput = document.getElementById('fileInput');
const dropZone = document.getElementById('dropZone');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const uploadBtn = document.getElementById('uploadBtn');

if (fileInput) {
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            showFileInfo(this.files[0].name);
        }
    });
}

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('drag-over');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        showFileInfo(files[0].name);
    }
}

function showFileInfo(name) {
    fileName.textContent = name;
    fileInfo.classList.remove('d-none');
    uploadBtn.disabled = false;
}

// Upload form submission
const uploadForm = document.getElementById('uploadForm');
if (uploadForm) {
    uploadForm.addEventListener('submit', function() {
        document.getElementById('loadingCard').classList.remove('d-none');
        this.closest('.jf-grid-center').style.display = 'none';
    });
}

// Search button loading
const searchBtn = document.getElementById('searchBtn');
if (searchBtn) {
    searchBtn.addEventListener('click', function() {
        if (!this.disabled) {
            this.disabled = true;
            this.innerHTML = '<span class="jf-spinner" style="width:18px;height:18px;border-width:2px;display:inline-block;vertical-align:middle;margin-left:8px;"></span> در حال جستجو...';
        }
    });
}