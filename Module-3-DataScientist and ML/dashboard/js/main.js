// Trade Settlement Prediction Dashboard - Tab Management
// IBM Carbon Design System Implementation

document.addEventListener('DOMContentLoaded', function() {
    console.log('Trade Settlement Prediction Dashboard loaded');
    
    // Initialize tabs
    initializeTabs();
    
    // Load data if available
    loadDashboardData();
    
    // Smooth scroll for anchor links
    initializeSmoothScroll();
});

/**
 * Initialize tab functionality
 */
function initializeTabs() {
    const tabs = document.querySelectorAll('.tab');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetId = this.getAttribute('data-tab');
            
            // Remove active class from all tabs and content
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked tab and corresponding content
            this.classList.add('active');
            const targetContent = document.getElementById(targetId);
            if (targetContent) {
                targetContent.classList.add('active');
            }
            
            // Update URL hash without scrolling
            if (history.pushState) {
                history.pushState(null, null, '#' + targetId);
            }
        });
    });
    
    // Activate tab from URL hash on load
    const hash = window.location.hash.substring(1);
    if (hash) {
        const targetTab = document.querySelector(`[data-tab="${hash}"]`);
        if (targetTab) {
            targetTab.click();
        }
    } else {
        // Activate first tab by default
        const firstTab = document.querySelector('.tab');
        if (firstTab) {
            firstTab.click();
        }
    }
}

/**
 * Load dashboard data from JSON file
 */
async function loadDashboardData() {
    try {
        const response = await fetch('data/results.json');
        if (response.ok) {
            const data = await response.json();
            console.log('Dashboard data loaded:', data);
            
            // Update dynamic content if data is available
            if (data.pipeline_status === 'completed') {
                updateDashboardWithData(data);
            }
        }
    } catch (error) {
        console.log('No dashboard data available yet. Run pipeline to generate data.');
    }
}

/**
 * Update dashboard with loaded data
 */
function updateDashboardWithData(data) {
    // This function can be extended to populate dynamic content
    console.log('Updating dashboard with data:', data);
    
    // Example: Update stat cards if they exist
    if (data.stats) {
        Object.keys(data.stats).forEach(key => {
            const element = document.getElementById(`stat-${key}`);
            if (element) {
                element.textContent = data.stats[key];
            }
        });
    }
}

/**
 * Initialize smooth scrolling for anchor links
 */
function initializeSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href.length > 1) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
}

/**
 * Format numbers with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Format percentage
 */
function formatPercentage(num, decimals = 2) {
    return (num * 100).toFixed(decimals) + '%';
}

/**
 * Create a simple bar chart (text-based)
 */
function createTextBarChart(data, maxWidth = 200) {
    const max = Math.max(...data.map(d => d.value));
    return data.map(item => {
        const width = (item.value / max) * maxWidth;
        return `
            <div class="chart-row" style="margin: 8px 0;">
                <div style="display: flex; align-items: center;">
                    <span style="width: 120px; font-size: 12px;">${item.label}</span>
                    <div style="flex: 1; background: #e0e0e0; height: 20px; border-radius: 4px; overflow: hidden;">
                        <div style="width: ${width}px; height: 100%; background: #0f62fe;"></div>
                    </div>
                    <span style="margin-left: 8px; font-size: 12px; font-weight: 600;">${item.value}</span>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    notification.style.animation = 'slideIn 0.3s ease';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Export functions for use in HTML
window.dashboardUtils = {
    formatNumber,
    formatPercentage,
    createTextBarChart,
    showNotification
};

// Made with Bob
