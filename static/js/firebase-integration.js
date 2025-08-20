// Firebase Integration for 3D4P Django Application
// This module provides Django-specific Firebase integrations

document.addEventListener('DOMContentLoaded', function() {
    // Wait for Firebase to be initialized
    setTimeout(() => {
        if (window.firebaseService && window.firebaseService.analytics) {
            setupDjangoIntegration();
        }
    }, 1500);
});

function setupDjangoIntegration() {
    // Track Django-specific events
    
    // 1. Track donation form views
    if (window.location.pathname.includes('/donate/')) {
        window.firebaseService.logEvent('view_donation_form', {
            page_path: window.location.pathname
        });
    }
    
    // 2. Track post views
    if (window.location.pathname.includes('/posts/') && window.location.pathname.includes('/detail/')) {
        const postId = window.location.pathname.split('/').filter(Boolean).pop();
        window.firebaseService.logEvent('view_post', {
            post_id: postId,
            page_path: window.location.pathname
        });
    }
    
    // 3. Track user profile views
    if (window.location.pathname.includes('/users/profile/')) {
        const username = window.location.pathname.split('/').filter(Boolean).pop();
        window.firebaseService.logEvent('view_profile', {
            username: username,
            page_path: window.location.pathname
        });
    }
    
    // 4. Enhanced donation tracking
    const donationForms = document.querySelectorAll('form[action*="/donate/"]');
    donationForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Get donation amount if available
            const amountInput = form.querySelector('input[name="amount"]');
            const typeInput = form.querySelector('select[name="donation_type"]');
            const requestIdInput = form.querySelector('input[name="donation_request_id"]');
            
            if (amountInput) {
                window.firebaseService.trackDonation(
                    parseFloat(amountInput.value) || 0,
                    typeInput ? typeInput.value : 'one-time',
                    requestIdInput ? requestIdInput.value : 'unknown'
                );
            }
        });
    });
    
    // 5. Track authentication events
    const loginForm = document.querySelector('form[action*="/login/"]');
    if (loginForm) {
        loginForm.addEventListener('submit', function() {
            window.firebaseService.trackUserLogin('django');
        });
    }
    
    const signupForm = document.querySelector('form[action*="/signup/"]');
    if (signupForm) {
        signupForm.addEventListener('submit', function() {
            window.firebaseService.trackUserRegistration('django');
        });
    }
    
    // 6. Track post creation
    const postForm = document.querySelector('form[action*="/posts/create"]');
    if (postForm) {
        postForm.addEventListener('submit', function() {
            const postTypeInput = form.querySelector('input[name="post_type"]');
            window.firebaseService.trackPostCreation(
                postTypeInput ? postTypeInput.value : 'regular',
                'new'
            );
        });
    }
    
    // 7. Track search functionality
    const searchForm = document.querySelector('form[action*="/search"]');
    if (searchForm) {
        searchForm.addEventListener('submit', function() {
            const searchInput = searchForm.querySelector('input[type="search"], input[name="q"]');
            if (searchInput) {
                window.firebaseService.trackSearch(searchInput.value);
            }
        });
    }
    
    // 8. Track navigation clicks
    trackNavigationClicks();
    
    // 9. Track scroll depth
    trackScrollDepth();
    
    // 10. Track time on page
    trackTimeOnPage();
}

function trackNavigationClicks() {
    // Track main navigation clicks
    document.querySelectorAll('.navbar a').forEach(link => {
        link.addEventListener('click', function() {
            window.firebaseService.logEvent('navigation_click', {
                link_text: this.textContent.trim(),
                link_url: this.href,
                section: 'main_nav'
            });
        });
    });
    
    // Track footer navigation clicks
    document.querySelectorAll('.footer a').forEach(link => {
        link.addEventListener('click', function() {
            window.firebaseService.logEvent('navigation_click', {
                link_text: this.textContent.trim(),
                link_url: this.href,
                section: 'footer'
            });
        });
    });
    
    // Track CTA button clicks
    document.querySelectorAll('.btn-donate').forEach(button => {
        button.addEventListener('click', function() {
            window.firebaseService.logEvent('cta_click', {
                button_text: this.textContent.trim(),
                button_location: this.closest('nav') ? 'navbar' : 'page'
            });
        });
    });
}

function trackScrollDepth() {
    let maxScroll = 0;
    let scrollPoints = [25, 50, 75, 90, 100];
    let triggeredPoints = new Set();
    
    function calculateScrollPercentage() {
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight;
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const trackableHeight = documentHeight - windowHeight;
        const scrollPercentage = Math.round((scrollTop / trackableHeight) * 100);
        return Math.min(scrollPercentage, 100);
    }
    
    window.addEventListener('scroll', function() {
        const currentScroll = calculateScrollPercentage();
        maxScroll = Math.max(maxScroll, currentScroll);
        
        scrollPoints.forEach(point => {
            if (currentScroll >= point && !triggeredPoints.has(point)) {
                triggeredPoints.add(point);
                window.firebaseService.logEvent('scroll_depth', {
                    depth_percentage: point,
                    page_path: window.location.pathname
                });
            }
        });
    });
    
    // Track max scroll depth when user leaves page
    window.addEventListener('beforeunload', function() {
        if (maxScroll > 0) {
            window.firebaseService.logEvent('max_scroll_depth', {
                depth_percentage: maxScroll,
                page_path: window.location.pathname
            });
        }
    });
}

function trackTimeOnPage() {
    const startTime = Date.now();
    let isActive = true;
    let activeTime = 0;
    let lastActiveTime = startTime;
    
    // Track when user is active/inactive
    function handleActivity() {
        if (!isActive) {
            isActive = true;
            lastActiveTime = Date.now();
        }
    }
    
    function handleInactivity() {
        if (isActive) {
            isActive = false;
            activeTime += Date.now() - lastActiveTime;
        }
    }
    
    // Activity events
    ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
        document.addEventListener(event, handleActivity, true);
    });
    
    // Inactivity events
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            handleInactivity();
        } else {
            handleActivity();
        }
    });
    
    // Track time when user leaves
    window.addEventListener('beforeunload', function() {
        if (isActive) {
            activeTime += Date.now() - lastActiveTime;
        }
        
        const totalTime = Date.now() - startTime;
        
        window.firebaseService.logEvent('time_on_page', {
            total_time_seconds: Math.round(totalTime / 1000),
            active_time_seconds: Math.round(activeTime / 1000),
            page_path: window.location.pathname,
            page_title: document.title
        });
    });
}

// Utility function to get CSRF token for Django
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return null;
}

// Export for use in other scripts
window.djangoFirebase = {
    getCSRFToken: getCSRFToken,
    trackCustomEvent: function(eventName, parameters) {
        if (window.firebaseService) {
            window.firebaseService.logEvent(eventName, parameters);
        }
    }
};