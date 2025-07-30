document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing app...');
    
    // Get elements only if they exist
    const uploadForm = document.getElementById('uploadForm');
    const generateBtn = document.getElementById('generateBtn');
    const loadingState = document.getElementById('loadingState');
    const fileInput = document.getElementById('file');

    // Handle upload form submission (index page) - minimal interference
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {        
            console.log('Form submit triggered');
            
            // Show loading state if available, but don't block submission
            if (generateBtn && loadingState) {
                try {
                    showLoadingState();
                } catch (error) {
                    console.log('Error showing loading state:', error);
                }
            }
            
            console.log('Allowing form to submit normally');
            // Don't prevent default - let the form submit naturally
        });
    }

    // Handle file input changes
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            console.log('File input:', fileInput);
            console.log('Selected file:', file);
            if (file) {
                console.log('File selected:', file.name, file.size);
                // Just log validation, don't prevent submission
                const isValid = validateFile(file);
                console.log('File validation result:', isValid);
            }
        });
    }

    // Handle mapping form submission (mapping page)
    const mappingForm = document.querySelector('form[action="/generate_emails"]');
    if (mappingForm) {
        mappingForm.addEventListener('submit', function(e) {
            console.log('Form submitting...');
            
            // Show loading state
            const submitBtn = document.getElementById('generateEmailsBtn');
            const loadingDiv = document.getElementById('emailLoadingState');
            
            if (submitBtn && loadingDiv) {
                submitBtn.style.display = 'none';
                loadingDiv.style.display = 'block';
                
                // Disable all form inputs to prevent changes during processing
                const formInputs = mappingForm.querySelectorAll('input, select, button');
                formInputs.forEach(input => {
                    input.disabled = true;
                });
            }
        });
    }

    function validateFile(file) {
        console.log('Validating file:', file.name, 'Size:', file.size, 'Type:', file.type);
        
        const maxSize = 16 * 1024 * 1024; // 16MB
        
        if (file.size > maxSize) {
            alert('File too large. Maximum size is 16MB.');
            return false;
        }
        
        const extension = file.name.toLowerCase().split('.').pop();
        console.log('File extension:', extension);
        
        if (!['csv', 'xlsx', 'xls'].includes(extension)) {
            alert('Invalid file type. Please upload Excel (.xlsx, .xls) or CSV files only.');
            return false;
        }
        
        console.log('File validation passed');
        return true;
    }

    function getFileIcon(fileName) {
        if (fileName.toLowerCase().endsWith('.csv')) {
            return 'csv';
        } else if (fileName.toLowerCase().endsWith('.xlsx') || fileName.toLowerCase().endsWith('.xls')) {
            return 'excel';
        }
        return 'alt';
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function showLoadingState() {
        if (generateBtn && loadingState) {
            generateBtn.style.display = 'none';
            loadingState.style.display = 'block';
        }
        
        // Disable form inputs
        if (uploadForm) {
            const formInputs = uploadForm.querySelectorAll('input, button');
            formInputs.forEach(input => {
                input.disabled = true;
            });
        }
    }

    // Drag and drop disabled for now to fix file upload issue
    /*
    // Handle drag and drop
    const fileInputArea = fileInput.parentNode;
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        fileInputArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        fileInputArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        fileInputArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        fileInputArea.classList.add('border-primary');
    }

    function unhighlight(e) {
        fileInputArea.classList.remove('border-primary');
    }

    fileInputArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            fileInput.files = files;
            validateFile(files[0]);
        }
    }
    */
});
