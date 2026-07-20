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

// Search form submit - use form submit event, NOT button click
// (disabling button in click handler prevents form submission in most browsers)
const searchForm = document.getElementById('searchForm');
if (searchForm) {
    searchForm.addEventListener('submit', function() {
        const btn = document.getElementById('searchBtn');
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<span class="jf-spinner" style="width:18px;height:18px;border-width:2px;display:inline-block;vertical-align:middle;margin-left:8px;"></span> در حال جستجو...';
        }
        // Show overlay after a short delay (gives form time to actually submit)
        setTimeout(function() {
            if (btn && btn.disabled) {
                let overlay = document.getElementById('searchOverlay');
                if (!overlay) {
                    overlay = document.createElement('div');
                    overlay.id = 'searchOverlay';
                    overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.6);z-index:9999;display:flex;align-items:center;justify-content:center;flex-direction:column;backdrop-filter:blur(4px);';
                    overlay.innerHTML = '<div style="background:white;border-radius:16px;padding:48px 56px;text-align:center;box-shadow:0 25px 50px rgba(0,0,0,0.25);max-width:400px;"><div class="jf-spinner" style="width:48px;height:48px;border-width:3px;margin:0 auto 24px;"></div><h3 style="color:#1e293b;margin:0 0 8px;font-family:Vazirmatn,sans-serif;">در حال جستجوی آگهی‌ها...</h3><p style="color:#64748b;margin:0;font-size:14px;font-family:Vazirmatn,sans-serif;">لطفاً صبر کنید. این فرآیند ممکن است تا ۶۰ ثانیه طول بکشد.</p></div>';
                    document.body.appendChild(overlay);
                }
                overlay.style.display = 'flex';
            }
        }, 500);
    });
}