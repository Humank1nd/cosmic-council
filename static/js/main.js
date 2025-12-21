/**
 * Cosmic Council - Main JavaScript
 * Core functionality for the web interface
 */

// Global application state
const AppState = {
    user: null,
    websocket: null,
    notifications: [],
    currentPage: 'home',
    isLoading: false,
    theme: 'cosmic'
};

// Utility functions
const Utils = {
    // Format date
    formatDate: (date) => {
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // Format number with commas
    formatNumber: (num) => {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    },

    // Format currency
    formatCurrency: (amount) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    },

    // Generate UUID
    generateUUID: () => {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    },

    // Debounce function
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Throttle function
    throttle: (func, limit) => {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

// API client
const API = {
    baseURL: '/api/web',
    
    // Generic request method
    request: async (endpoint, options = {}) => {
        try {
            const response = await fetch(`${API.baseURL}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },

    // GET request
    get: (endpoint) => API.request(endpoint, { method: 'GET' }),

    // POST request
    post: (endpoint, data) => API.request(endpoint, {
        method: 'POST',
        body: JSON.stringify(data)
    }),

    // PUT request
    put: (endpoint, data) => API.request(endpoint, {
        method: 'PUT',
        body: JSON.stringify(data)
    }),

    // DELETE request
    delete: (endpoint) => API.request(endpoint, { method: 'DELETE' }),

    // Specific API methods
    problems: {
        create: (data) => API.post('/problems', data),
        getAll: (params = {}) => API.get(`/problems?${new URLSearchParams(params)}`),
        getById: (id) => API.get(`/problems/${id}`),
        update: (id, data) => API.put(`/problems/${id}`, data),
        delete: (id) => API.delete(`/problems/${id}`)
    },

    cycles: {
        create: (data) => API.post('/cycles', data),
        getById: (id) => API.get(`/cycles/${id}`),
        execute: (id) => API.post(`/cycles/${id}/execute`)
    },

    solutions: {
        create: (data) => API.post('/solutions', data),
        getAll: (params = {}) => API.get(`/solutions?${new URLSearchParams(params)}`),
        getById: (id) => API.get(`/solutions/${id}`)
    },

    analytics: {
        getAll: () => API.get('/analytics')
    },

    enterprises: {
        getAll: () => API.get('/supra_enterprise')
    },

    perpetual: {
        createSession: (data) => API.post('/perpetual/sessions', data),
        getSessions: () => API.get('/perpetual/sessions'),
        getSession: (id) => API.get(`/perpetual/sessions/${id}`),
        pauseSession: (id) => API.post(`/perpetual/sessions/${id}/pause`),
        stopSession: (id) => API.post(`/perpetual/sessions/${id}/stop`),
        getStatus: () => API.get('/perpetual/status'),
        getAISessions: (params = {}) => API.get(`/perpetual/ai/sessions?${new URLSearchParams(params)}`),
        getAISessionAnalytics: (id) => API.get(`/perpetual/ai/sessions/${id}/analytics`),
        getAIEnhancedCycleStatus: (id) => API.get(`/perpetual/ai/sessions/${id}/status`)
    }
};

// Notification system
const Notifications = {
    container: null,

    init: () => {
        Notifications.container = document.getElementById('toastContainer');
    },

    show: (message, type = 'info', duration = 5000) => {
        if (!Notifications.container) {
            Notifications.init();
        }

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const iconMap = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };

        toast.innerHTML = `
            <div class="toast-header">
                <div class="toast-icon ${type}">
                    <i class="${iconMap[type]}"></i>
                </div>
                <div class="toast-title">${type.charAt(0).toUpperCase() + type.slice(1)}</div>
                <button class="toast-close" onclick="Notifications.hide(this.parentElement.parentElement)">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="toast-message">${message}</div>
        `;

        Notifications.container.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Auto-hide
        if (duration > 0) {
            setTimeout(() => Notifications.hide(toast), duration);
        }

        return toast;
    },

    hide: (toast) => {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentElement) {
                toast.parentElement.removeChild(toast);
            }
        }, 300);
    },

    success: (message, duration) => Notifications.show(message, 'success', duration),
    error: (message, duration) => Notifications.show(message, 'error', duration),
    warning: (message, duration) => Notifications.show(message, 'warning', duration),
    info: (message, duration) => Notifications.show(message, 'info', duration)
};

// Modal system
const Modal = {
    container: null,

    init: () => {
        Modal.container = document.getElementById('modalContainer');
    },

    show: (content, options = {}) => {
        if (!Modal.container) {
            Modal.init();
        }

        const modal = document.createElement('div');
        modal.className = 'modal';
        
        const { title, body, footer, size = 'medium' } = options;
        
        modal.innerHTML = `
            <div class="modal-header">
                <h3 class="modal-title">${title || 'Modal'}</h3>
                <button class="modal-close" onclick="Modal.hide()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                ${body || content}
            </div>
            ${footer ? `<div class="modal-footer">${footer}</div>` : ''}
        `;

        Modal.container.innerHTML = '';
        Modal.container.appendChild(modal);
        Modal.container.classList.add('active');
        
        // Trigger animation
        setTimeout(() => modal.classList.add('active'), 100);

        return modal;
    },

    hide: () => {
        if (Modal.container) {
            Modal.container.classList.remove('active');
            setTimeout(() => {
                Modal.container.innerHTML = '';
            }, 300);
        }
    }
};

// Loading system
const Loading = {
    show: (message = 'Loading...') => {
        AppState.isLoading = true;
        // Create loading overlay
        const overlay = document.createElement('div');
        overlay.id = 'loadingOverlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="spinner"></div>
                <p>${message}</p>
            </div>
        `;
        document.body.appendChild(overlay);
    },

    hide: () => {
        AppState.isLoading = false;
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.remove();
        }
    }
};

// Form handling
const Forms = {
    // Serialize form data
    serialize: (form) => {
        const formData = new FormData(form);
        const data = {};
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        return data;
    },

    // Validate form
    validate: (form, rules) => {
        const errors = {};
        const formData = Forms.serialize(form);

        for (const [field, rule] of Object.entries(rules)) {
            const value = formData[field];
            
            if (rule.required && (!value || value.trim() === '')) {
                errors[field] = `${rule.label || field} is required`;
            } else if (rule.minLength && value && value.length < rule.minLength) {
                errors[field] = `${rule.label || field} must be at least ${rule.minLength} characters`;
            } else if (rule.maxLength && value && value.length > rule.maxLength) {
                errors[field] = `${rule.label || field} must be no more than ${rule.maxLength} characters`;
            } else if (rule.pattern && value && !rule.pattern.test(value)) {
                errors[field] = rule.message || `${rule.label || field} format is invalid`;
            }
        }

        return errors;
    },

    // Show form errors
    showErrors: (form, errors) => {
        // Clear previous errors
        form.querySelectorAll('.form-error').forEach(error => error.remove());
        form.querySelectorAll('.form-input, .form-select, .form-textarea').forEach(input => {
            input.classList.remove('error');
        });

        // Show new errors
        for (const [field, message] of Object.entries(errors)) {
            const input = form.querySelector(`[name="${field}"]`);
            if (input) {
                input.classList.add('error');
                const errorDiv = document.createElement('div');
                errorDiv.className = 'form-error';
                errorDiv.textContent = message;
                input.parentNode.appendChild(errorDiv);
            }
        }
    }
};

// Chart utilities
const Charts = {
    // Create a simple chart
    create: (canvas, config) => {
        const ctx = canvas.getContext('2d');
        return new Chart(ctx, {
            type: config.type || 'line',
            data: config.data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#cbd5e1'
                        }
                    }
                },
                scales: config.scales || {
                    x: {
                        ticks: { color: '#94a3b8' },
                        grid: { color: '#334155' }
                    },
                    y: {
                        ticks: { color: '#94a3b8' },
                        grid: { color: '#334155' }
                    }
                },
                ...config.options
            }
        });
    }
};

// Event handlers
const EventHandlers = {
    // Initialize all event handlers
    init: () => {
        // User menu toggle
        const userMenuBtn = document.getElementById('userMenuBtn');
        if (userMenuBtn) {
            userMenuBtn.addEventListener('click', EventHandlers.toggleUserMenu);
        }

        // Notification button
        const notificationBtn = document.getElementById('notificationBtn');
        if (notificationBtn) {
            notificationBtn.addEventListener('click', EventHandlers.toggleNotifications);
        }

        // Global click handler for dropdowns
        document.addEventListener('click', EventHandlers.handleGlobalClick);

        // Form submissions
        document.addEventListener('submit', EventHandlers.handleFormSubmit);

        // Keyboard shortcuts
        document.addEventListener('keydown', EventHandlers.handleKeyboard);
    },

    toggleUserMenu: (e) => {
        e.stopPropagation();
        const dropdown = document.getElementById('userDropdown');
        if (dropdown) {
            dropdown.classList.toggle('active');
        }
    },

    toggleNotifications: (e) => {
        e.stopPropagation();
        // Toggle notifications panel
        console.log('Toggle notifications');
    },

    handleGlobalClick: (e) => {
        // Close dropdowns when clicking outside
        if (!e.target.closest('.user-menu')) {
            const dropdown = document.getElementById('userDropdown');
            if (dropdown) {
                dropdown.classList.remove('active');
            }
        }
    },

    handleFormSubmit: (e) => {
        const form = e.target;
        if (form.dataset.validate) {
            e.preventDefault();
            EventHandlers.validateAndSubmit(form);
        }
    },

    validateAndSubmit: async (form) => {
        const rules = JSON.parse(form.dataset.validate);
        const errors = Forms.validate(form, rules);
        
        if (Object.keys(errors).length > 0) {
            Forms.showErrors(form, errors);
            return;
        }

        const formData = Forms.serialize(form);
        const action = form.dataset.action;
        
        if (action) {
            try {
                Loading.show('Processing...');
                const result = await API.request(action, {
                    method: 'POST',
                    body: JSON.stringify(formData)
                });
                
                if (result.success) {
                    Notifications.success(result.message || 'Operation completed successfully');
                    if (form.dataset.redirect) {
                        window.location.href = form.dataset.redirect;
                    }
                } else {
                    Notifications.error(result.message || 'Operation failed');
                }
            } catch (error) {
                Notifications.error('An error occurred while processing your request');
                console.error('Form submission error:', error);
            } finally {
                Loading.hide();
            }
        }
    },

    handleKeyboard: (e) => {
        // Global keyboard shortcuts
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case 'k':
                    e.preventDefault();
                    // Open search
                    break;
                case 'n':
                    e.preventDefault();
                    // Create new item
                    break;
            }
        }
    }
};

// Initialize application
const initializeApp = () => {
    console.log('Initializing Cosmic Council Web Interface...');
    
    // Initialize components
    Notifications.init();
    Modal.init();
    EventHandlers.init();
    
    // Initialize WebSocket connection
    if (typeof WebSocketManager !== 'undefined') {
        WebSocketManager.init();
    }
    
    // Set up page-specific functionality
    const currentPage = document.body.dataset.page || 'home';
    AppState.currentPage = currentPage;
    
    // Initialize page-specific features
    switch (currentPage) {
        case 'home':
            initializeDashboard();
            break;
        case 'problems':
            initializeProblems();
            break;
        case 'cycles':
            initializeCycles();
            break;
        case 'solutions':
            initializeSolutions();
            break;
        case 'analytics':
            initializeAnalytics();
            break;
        case 'workflow':
            initializeWorkflow();
            break;
        case 'hexagon':
            initializeHexagon();
            break;
    }
    
    console.log('Cosmic Council Web Interface initialized successfully');
};

// Page-specific initializers
const initializeDashboard = () => {
    console.log('Initializing dashboard...');
    loadDashboardData();
};

const initializeProblems = () => {
    console.log('Initializing problems page...');
    loadProblems();
};

const initializeCycles = () => {
    console.log('Initializing cycles page...');
    loadCycles();
};

const initializeSolutions = () => {
    console.log('Initializing solutions page...');
    loadSolutions();
};

const initializeAnalytics = () => {
    console.log('Initializing analytics page...');
    loadAnalytics();
};

const initializeWorkflow = () => {
    console.log('Initializing workflow page...');
    // Initialize workflow components
};

const initializeHexagon = () => {
    console.log('Initializing hexagon page...');
    // Initialize hexagon visualization
};

// Data loading functions
const loadDashboardData = async () => {
    try {
        const analytics = await API.analytics.getAll();
        if (analytics.success) {
            updateDashboard(analytics.data);
        }
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
        Notifications.error('Failed to load dashboard data');
    }
};

const loadProblems = async () => {
    try {
        const problems = await API.problems.getAll();
        if (problems.success) {
            updateProblemsList(problems.data.problems);
        }
    } catch (error) {
        console.error('Failed to load problems:', error);
        Notifications.error('Failed to load problems');
    }
};

const loadCycles = async () => {
    try {
        // Load cycles data
        console.log('Loading cycles...');
    } catch (error) {
        console.error('Failed to load cycles:', error);
        Notifications.error('Failed to load cycles');
    }
};

const loadSolutions = async () => {
    try {
        const solutions = await API.solutions.getAll();
        if (solutions.success) {
            updateSolutionsList(solutions.data.solutions);
        }
    } catch (error) {
        console.error('Failed to load solutions:', error);
        Notifications.error('Failed to load solutions');
    }
};

const loadAnalytics = async () => {
    try {
        const analytics = await API.analytics.getAll();
        if (analytics.success) {
            updateAnalyticsCharts(analytics.data);
        }
    } catch (error) {
        console.error('Failed to load analytics:', error);
        Notifications.error('Failed to load analytics');
    }
};

// Update functions
const updateDashboard = (data) => {
    console.log('Updating dashboard with data:', data);
    // Update dashboard components
};

const updateProblemsList = (problems) => {
    console.log('Updating problems list:', problems);
    // Update problems list
};

const updateSolutionsList = (solutions) => {
    console.log('Updating solutions list:', solutions);
    // Update solutions list
};

const updateAnalyticsCharts = (data) => {
    console.log('Updating analytics charts:', data);
    // Update analytics charts
};

// Export for global access
window.AppState = AppState;
window.Utils = Utils;
window.API = API;
window.Notifications = Notifications;
window.Modal = Modal;
window.Loading = Loading;
window.Forms = Forms;
window.Charts = Charts;
window.initializeApp = initializeApp;
