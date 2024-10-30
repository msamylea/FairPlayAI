function hideError() {
    const errorDiv = document.getElementById('error');
    if (errorDiv) {
        errorDiv.classList.add('hidden');
    }
}

function showError(message) {
    const errorMessage = document.getElementById('error-message');
    const errorDiv = document.getElementById('error');
    if (errorMessage && errorDiv) {
        errorMessage.textContent = message;
        errorDiv.classList.remove('hidden');
    }
}

async function sendForAnalysis(source) {
    const loadingElement = document.getElementById('loading-searched');
    const analysisContentElement = document.getElementById('analysis-content');
    const analysisResultsElement = document.getElementById('analysis-results');
    const analysisPdfViewer = document.getElementById('analysis-pdf-viewer');
    
    if (loadingElement) loadingElement.classList.remove('hidden');
    if (analysisContentElement) analysisContentElement.classList.add('hidden');
    if (analysisResultsElement) analysisResultsElement.classList.add('hidden');

    try {
        let formData = new FormData();

        if (source === 'pdf') {
            const billId = document.getElementById('bills').value;
            const response = await fetch('/get_bill_pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'bill_id': billId
                })
            });
            const blob = await response.blob();
            formData.append('file', blob, 'bill.pdf');
        } else if (source === 'file') {
            const fileInput = document.getElementById('file-input');
            formData.append('file', fileInput.files[0]);
        } else {
            throw new Error('Invalid analysis source');
        }

        const analysisResponse = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });

        if (!analysisResponse.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await analysisResponse.json();
        if (loadingElement) loadingElement.classList.add('hidden');

        console.log("Analysis response data:", data); // Debug log

        if (data.success) {
            if (analysisPdfViewer) {
                console.log("Setting analysis PDF URL:", data.pdf_url); // Debug log
                analysisPdfViewer.src = data.pdf_url;
            } else {
                console.error("Analysis PDF viewer element not found");
            }
            if (analysisResultsElement) {
                analysisResultsElement.classList.remove('hidden');
            } else {
                console.error("Analysis results element not found");
            }
            if (analysisContentElement) {
                analysisContentElement.classList.remove('hidden');
            } else {
                console.error("Analysis content element not found");
            }
            switchTab('analysis');
        } else {
            throw new Error(data.error || 'An error occurred');
        }
    } catch (error) {
        if (loadingElement) loadingElement.classList.add('hidden');
        console.error('Error:', error);
        showError('An error occurred while analyzing the policy: ' + error.message);
    }
}
function analyzePolicy() {
    console.log("analyzePolicy called");
    const fileInput = document.getElementById('file-input');
    const billsSelect = document.getElementById('bills');

    const uploadedFile = fileInput ? fileInput.files[0] : null;
    const selectedBill = billsSelect ? billsSelect.value : '';

    console.log("Uploaded file:", uploadedFile ? uploadedFile.name : "None");
    console.log("Selected bill:", selectedBill || "None");

    hideError();

    if (uploadedFile) {
        sendForAnalysis('file');
    } else if (selectedBill) {
        sendForAnalysis('pdf');
    } else {
        showError('Please select a bill or upload a file before analyzing.');
    }
}

function switchTab(tabName) {
    console.log("Switching to tab:", tabName); // Debug log
    const pdfTab = document.getElementById('pdf-tab');
    const analysisTab = document.getElementById('analysis-tab');
    const pdfContent = document.getElementById('pdf-content');
    const analysisContent = document.getElementById('analysis-content');

    if (tabName === 'pdf') {
        pdfTab.classList.add('bg-primary', 'text-white');
        analysisTab.classList.remove('bg-primary', 'text-white');
        pdfContent.classList.remove('hidden');
        analysisContent.classList.add('hidden');
    } else if (tabName === 'analysis') {
        analysisTab.classList.add('bg-primary', 'text-white');
        pdfTab.classList.remove('bg-primary', 'text-white');
        analysisContent.classList.remove('hidden');
        pdfContent.classList.add('hidden');
    }
}
function initializeScript() {
    async function fetchBills() {
        const topic = document.getElementById('topic').value;
        const state = document.getElementById('state').value;
        
        if (!topic || !state) {
            // Don't show an error, just return silently if either is not selected
            return;
        }

        try {
            const response = await fetch('/get_bills', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'topic': topic,
                    'state': state
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            const billsDropdown = document.getElementById('bills');
            billsDropdown.innerHTML = '<option value="">Select a bill</option>';
            
            if (data.length === 0) {
                document.getElementById('bills-dropdown').classList.add('hidden');
                document.getElementById('no-bills-message').classList.remove('hidden');
                document.getElementById('no-bills-text').textContent = `No bills found for ${topic} in ${state} for current year.`;
            } else {
                data.forEach(bill => {
                    const option = document.createElement('option');
                    option.value = bill.bill_id;
                    option.textContent = truncateText(bill.title, 100);
                    option.title = bill.title;
                    billsDropdown.appendChild(option);
                });
                document.getElementById('bills-dropdown').classList.remove('hidden');
                document.getElementById('no-bills-message').classList.add('hidden');
            }
            hideError();
        } catch (error) {
            console.error('Error fetching bills:', error);
            showError(`Error fetching bills: ${error.message}`);
        }
    }

    async function fetchBillPDF() {
        const billId = document.getElementById('bills').value;

        if (!billId) {
            showError('Please select a bill.');
            return;
        }

        try {
            const response = await fetch('/get_bill_pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'bill_id': billId
                })
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw errorData;
            }
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const iframe = document.getElementById('pdf-iframe');
            iframe.src = url;
            
            document.getElementById('pdf-viewer').classList.remove('hidden');
            switchTab('pdf');
            document.getElementById('results').classList.remove('hidden');
            document.getElementById('analysis-results').classList.add('hidden');
            
            // Clear file upload when a bill is selected
            clearFileUpload();
        } catch (error) {
            console.error('Error fetching bill PDF:', error);
            showError(error.error || 'An error occurred while fetching the PDF');
        }
    }

    function getElementSafely(id) {
        const element = document.getElementById(id);
        if (!element) {
            console.warn(`Element with id '${id}' not found`);
        }
        return element;
    }

    function truncateText(text, maxLength) {
        return text.length > maxLength ? text.substr(0, maxLength - 3) + '...' : text;
    }
    

    function handleFileSelection(event) {
        console.log("handleFileSelection called");
        const files = event.target.files;
        const fileName = getElementSafely("uploaded-file-name");
        if (files.length > 0) {
            if (fileName) {
                fileName.textContent = `Selected file: ${files[0].name}`;
            } else {
                console.warn("Element 'uploaded-file-name' not found. Unable to display file name.");
            }
            
            // Clear bill selection when a file is selected
            clearBillSelection();
        } else {
            console.log("No file selected");
            if (fileName) {
                fileName.textContent = "";
            }
        }
    }

    function uploadFile() {
        console.log("uploadFile called");
        const fileInput = getElementSafely("file-input");
        if (fileInput && fileInput.files.length > 0) {
            const file = fileInput.files[0];
            if (/\.(pdf|docx?|txt)$/i.test(file.name)) {
                loadURL(file);
            } else {
                console.log("Invalid file type");
                showError("Please upload a PDF, DOC, DOCX, or TXT file.");
            }
        } else {
            console.log("No file selected");
            showError("Please select a file to upload.");
        }
    }

    function loadURL(file) {
        console.log("loadURL called");
        const frameElement = getElementSafely("pdf-iframe");
        const pdfViewer = getElementSafely("pdf-viewer");

        const reader = new FileReader();
        reader.onload = function(e) {
            if (frameElement) {
                frameElement.src = e.target.result;
            }
            if (pdfViewer) {
                pdfViewer.classList.remove("hidden");
            }
            document.getElementById('results').classList.remove('hidden');
            switchTab('pdf');
        };
        reader.readAsDataURL(file);
    }

    function clearBillSelection() {
        const topicSelect = getElementSafely('topic');
        const stateSelect = getElementSafely('state');
        const billsSelect = getElementSafely('bills');
        const billsDropdown = getElementSafely('bills-dropdown');

        if (topicSelect) topicSelect.value = '';
        if (stateSelect) stateSelect.value = '';
        if (billsSelect) billsSelect.innerHTML = '<option value="">Select a bill</option>';
        if (billsDropdown) billsDropdown.classList.add('hidden');
    }

    function clearFileUpload() {
        const fileInput = getElementSafely('file-input');
        const uploadedFileName = getElementSafely('uploaded-file-name');
        if (fileInput) fileInput.value = '';
        if (uploadedFileName) uploadedFileName.textContent = '';
    }


    // Set up event listeners
    const fileInput = getElementSafely('file-input');
    const billsSelect = getElementSafely('bills');
    const analyzePolicyBtn = getElementSafely('analyze-policy-btn');
    const uploadFileBtn = getElementSafely('upload-file-btn');
    const topicSelect = getElementSafely('topic');
    const stateSelect = getElementSafely('state');
    const pdfTab = getElementSafely('pdf-tab');
    const analysisTab = getElementSafely('analysis-tab');

    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelection);
    } else {
        console.error("File input element not found");
    }

    if (billsSelect) {
        billsSelect.addEventListener('change', fetchBillPDF);
    } else {
        console.error("Bills select element not found");
    }

    if (analyzePolicyBtn) {
        analyzePolicyBtn.addEventListener('click', analyzePolicy);
    } else {
        console.error("Analyze policy button not found");
    }

    if (uploadFileBtn) {
        uploadFileBtn.addEventListener('click', uploadFile);
    } else {
        console.error("Upload file button not found");
    }

    if (topicSelect && stateSelect) {
        topicSelect.addEventListener('change', fetchBills);
        stateSelect.addEventListener('change', fetchBills);
    }

    if (pdfTab && analysisTab) {
        pdfTab.addEventListener('click', () => switchTab('pdf'));
        analysisTab.addEventListener('click', () => switchTab('analysis'));
    }

    console.log("Script initialized");
}

// Call our initialize function when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', initializeScript);