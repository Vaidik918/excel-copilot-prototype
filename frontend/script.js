

const API_BASE = 'http://localhost:5000';

// On page load, test API connection
document.addEventListener('DOMContentLoaded', () => {
    testConnection();
});

async function testConnection() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        
        document.getElementById('statusContainer').innerHTML = 
            `<span class="success">✅ API Connected</span><br>` +
            JSON.stringify(data, null, 2);
    } catch (error) {
        document.getElementById('statusContainer').innerHTML = 
            `<span class="error">❌ API Not Connected: ${error.message}</span>`;
    }
}

function testHealthEndpoint() {
    fetch(`${API_BASE}/health`)
        .then(res => res.json())
        .then(data => {
            document.getElementById('apiResponse').textContent = 
                JSON.stringify(data, null, 2);
        })
        .catch(err => {
            document.getElementById('apiResponse').textContent = 
                `Error: ${err.message}`;
        });
}

function testFileInput() {
    const file = document.getElementById('fileInput').files;
    if (!file) {
        document.getElementById('uploadStatus').innerHTML = 
            '<span class="error">❌ No file selected</span>';
        return;
    }
    
    document.getElementById('uploadStatus').innerHTML = 
        `<span class="success">✅ File selected: ${file.name}</span><br>` +
        `Size: ${(file.size / 1024).toFixed(2)} KB<br>` +
        `Type: ${file.type}`;
}
