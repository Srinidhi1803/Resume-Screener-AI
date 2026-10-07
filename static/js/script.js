// Client-side interactions & file drag-drop management

document.addEventListener("DOMContentLoaded", function () {
    // 1. File Upload Drag & Drop Preview
    const fileInput = document.getElementById("resumes");
    const dropBox = document.getElementById("fileDropBox");
    const fileListContainer = document.getElementById("fileList");

    if (fileInput && dropBox) {
        fileInput.addEventListener("change", function () {
            updateFileList(fileInput.files);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropBox.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropBox.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropBox.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropBox.classList.remove('dragover');
            }, false);
        });

        dropBox.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            fileInput.files = files;
            updateFileList(files);
        });
    }

    function updateFileList(files) {
        if (!fileListContainer) return;
        fileListContainer.innerHTML = "";

        if (files.length === 0) return;

        const heading = document.createElement("div");
        heading.style.fontWeight = "600";
        heading.style.marginBottom = "6px";
        heading.style.fontSize = "0.9rem";
        heading.style.color = "#94a3b8";
        heading.textContent = `Selected (${files.length} resumes):`;
        fileListContainer.appendChild(heading);

        Array.from(files).forEach((file) => {
            const item = document.createElement("div");
            item.className = "file-item";
            item.innerHTML = `<span>📄 ${file.name}</span><span style="color:#64748b;">${(file.size / 1024).toFixed(1)} KB</span>`;
            fileListContainer.appendChild(item);
        });
    }

    // 2. Animate progress bar widths on page load
    const progressBars = document.querySelectorAll(".progress-bar-fill");
    progressBars.forEach(bar => {
        const targetWidth = bar.getAttribute("data-width") || "0%";
        setTimeout(() => {
            bar.style.width = targetWidth;
        }, 150);
    });
});
