// Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyAmM07BoXBZ5OD6MUrZ2dw8b_eimgog5FA",
    authDomain: "d4p-e00a9.firebaseapp.com",
    projectId: "d4p-e00a9",
    storageBucket: "d4p-e00a9.firebasestorage.app",
    messagingSenderId: "336361717139",
    appId: "1:336361717139:web:366399bb27aab6eb577c66",
    measurementId: "G-SXB9VR42GY"
};

// Firebase service wrapper
class FirebaseService {
    constructor() {
        this.app = null;
        this.analytics = null;
        this.auth = null;
        this.db = null;
        this.storage = null;
    }

    async initialize() {
        try {
            // Initialize Firebase app
            this.app = firebase.initializeApp(firebaseConfig);
            
            // Initialize Analytics if available
            if (typeof firebase.analytics !== 'undefined') {
                this.analytics = firebase.analytics();
                console.log('Firebase Analytics initialized');
            }
            
            // Initialize other services as needed
            if (typeof firebase.auth !== 'undefined') {
                this.auth = firebase.auth();
                console.log('Firebase Auth initialized');
            }
            
            if (typeof firebase.firestore !== 'undefined') {
                this.db = firebase.firestore();
                console.log('Firebase Firestore initialized');
            }
            
            if (typeof firebase.storage !== 'undefined') {
                this.storage = firebase.storage();
                console.log('Firebase Storage initialized');
            }
            
            console.log('Firebase initialized successfully');
            return true;
        } catch (error) {
            console.error('Error initializing Firebase:', error);
            return false;
        }
    }

    // Analytics tracking methods
    logEvent(eventName, parameters = {}) {
        if (this.analytics) {
            this.analytics.logEvent(eventName, parameters);
        }
    }

    // Track page views
    trackPageView(pageName) {
        this.logEvent('page_view', {
            page_title: pageName,
            page_location: window.location.href,
            page_path: window.location.pathname
        });
    }

    // Track user interactions
    trackButtonClick(buttonName, category = 'engagement') {
        this.logEvent('button_click', {
            button_name: buttonName,
            category: category
        });
    }

    // Track donation events
    trackDonation(amount, donationType, recipientId) {
        this.logEvent('donation_made', {
            value: amount,
            currency: 'USD',
            donation_type: donationType,
            recipient_id: recipientId
        });
    }

    // Track post creation
    trackPostCreation(postType, postId) {
        this.logEvent('post_created', {
            post_type: postType,
            post_id: postId
        });
    }

    // Track user registration
    trackUserRegistration(method = 'email') {
        this.logEvent('sign_up', {
            method: method
        });
    }

    // Track user login
    trackUserLogin(method = 'email') {
        this.logEvent('login', {
            method: method
        });
    }

    // Track search
    trackSearch(searchTerm, searchCategory = 'posts') {
        this.logEvent('search', {
            search_term: searchTerm,
            category: searchCategory
        });
    }

    // Track share events
    trackShare(contentType, contentId, method) {
        this.logEvent('share', {
            content_type: contentType,
            item_id: contentId,
            method: method
        });
    }
}

// Create global Firebase service instance
window.firebaseService = new FirebaseService();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit for Firebase SDK to load
    setTimeout(() => {
        window.firebaseService.initialize().then(success => {
            if (success) {
                // Track initial page view
                window.firebaseService.trackPageView(document.title);
                
                // Set up automatic tracking for common events
                setupAutomaticTracking();
            }
        });
    }, 1000);
});

// Set up automatic event tracking
function setupAutomaticTracking() {
    // Track all button clicks with data-track attribute
    document.querySelectorAll('[data-track]').forEach(element => {
        element.addEventListener('click', function() {
            const trackName = this.getAttribute('data-track');
            const trackCategory = this.getAttribute('data-track-category') || 'engagement';
            window.firebaseService.trackButtonClick(trackName, trackCategory);
        });
    });
    
    // Track form submissions
    document.querySelectorAll('form[data-track-form]').forEach(form => {
        form.addEventListener('submit', function() {
            const formName = this.getAttribute('data-track-form');
            window.firebaseService.logEvent('form_submit', {
                form_name: formName
            });
        });
    });
    
    // Track external link clicks
    document.querySelectorAll('a[href^="http"]:not([href*="' + window.location.hostname + '"])').forEach(link => {
        link.addEventListener('click', function() {
            window.firebaseService.logEvent('external_link_click', {
                link_url: this.href,
                link_text: this.textContent.trim()
            });
        });
    });
}