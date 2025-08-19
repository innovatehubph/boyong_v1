// Enhanced Service Worker for Pareng Boyong PWA
// Version 2.0 - Enhanced for mobile and offline functionality

const CACHE_NAME = 'pareng-boyong-v2.0';
const OFFLINE_URL = '/offline.html';

// Core files to cache for offline functionality
const CORE_CACHE_FILES = [
    '/',
    '/index.html',
    '/index.css',
    '/css/messages.css',
    '/css/enhanced-multimedia-styles.css',
    '/css/pareng-boyong-multimedia-theme.css',
    '/css/toast.css',
    '/css/settings.css',
    '/css/file_browser.css',
    '/css/modals.css',
    '/css/modals2.css',
    '/css/speech.css',
    '/css/history.css',
    '/css/scheduler-datepicker.css',
    '/css/tunnel.css',
    '/public/innovatehub-logo.png',
    '/public/pareng-boyong-logo.svg',
    '/public/manifest.json',
    '/vendor/flatpickr/flatpickr.min.css',
    '/vendor/flatpickr/flatpickr.min.js'
];

// Assets that can be cached on first access
const CACHE_ON_ACCESS = [
    '/js/',
    '/public/',
    '/vendor/',
    '/components/'
];

// Install event - cache core files
self.addEventListener('install', (event) => {
    console.log('🇵🇭 Pareng Boyong Service Worker: Installing...');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('🇵🇭 Pareng Boyong: Caching core files for offline use');
                return cache.addAll(CORE_CACHE_FILES.concat([OFFLINE_URL]));
            })
            .then(() => {
                console.log('🇵🇭 Pareng Boyong: Service Worker installed successfully');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('🇵🇭 Pareng Boyong: Service Worker installation failed:', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('🇵🇭 Pareng Boyong Service Worker: Activating...');
    
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (cacheName !== CACHE_NAME) {
                            console.log('🇵🇭 Pareng Boyong: Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('🇵🇭 Pareng Boyong: Service Worker activated');
                return self.clients.claim();
            })
    );
});

// Fetch event - serve from cache or network with Filipino-friendly error handling
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Skip cross-origin requests that aren't assets
    if (url.origin !== location.origin) {
        return;
    }
    
    event.respondWith(
        caches.match(request)
            .then((cachedResponse) => {
                if (cachedResponse) {
                    // Serve from cache
                    return cachedResponse;
                }
                
                // Try network first
                return fetch(request)
                    .then((networkResponse) => {
                        if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
                            return networkResponse;
                        }
                        
                        // Check if we should cache this response
                        const shouldCache = CACHE_ON_ACCESS.some(pattern => 
                            request.url.includes(pattern)
                        ) || CORE_CACHE_FILES.includes(url.pathname);
                        
                        if (shouldCache) {
                            const responseToCache = networkResponse.clone();
                            caches.open(CACHE_NAME)
                                .then((cache) => {
                                    cache.put(request, responseToCache);
                                });
                        }
                        
                        return networkResponse;
                    })
                    .catch(() => {
                        // Network failed, try to serve offline page for navigation requests
                        if (request.destination === 'document') {
                            return caches.match(OFFLINE_URL);
                        }
                        
                        // For other requests, return a simple response
                        return new Response('Offline - Pareng Boyong is not available right now po. Please check your internet connection.', {
                            status: 503,
                            statusText: 'Service Unavailable - Offline',
                            headers: new Headers({
                                'Content-Type': 'text/plain; charset=utf-8'
                            })
                        });
                    });
            })
    );
});

// Background sync for when connection is restored
self.addEventListener('sync', (event) => {
    console.log('🇵🇭 Pareng Boyong: Background sync triggered');
    
    if (event.tag === 'background-sync') {
        event.waitUntil(
            // Perform background sync tasks
            syncData()
        );
    }
});

// Push notification support for Filipino context
self.addEventListener('push', (event) => {
    if (!event.data) {
        return;
    }
    
    const options = {
        body: event.data.text() || 'Kumusta! Pareng Boyong has an update for you.',
        icon: '/public/innovatehub-logo.png',
        badge: '/public/innovatehub-logo.png',
        vibrate: [200, 100, 200],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: '1'
        },
        actions: [
            {
                action: 'explore',
                title: 'Open Pareng Boyong',
                icon: '/public/innovatehub-logo.png'
            },
            {
                action: 'close',
                title: 'Dismiss',
                icon: '/public/innovatehub-logo.png'
            }
        ],
        tag: 'pareng-boyong-notification'
    };
    
    event.waitUntil(
        self.registration.showNotification('Pareng Boyong - Filipino AI Assistant', options)
    );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    
    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Helper function for background sync
async function syncData() {
    try {
        console.log('🇵🇭 Pareng Boyong: Performing background sync...');
        // Add any background sync logic here
        return Promise.resolve();
    } catch (error) {
        console.error('🇵🇭 Pareng Boyong: Background sync failed:', error);
        throw error;
    }
}

// Message handler for communication with main thread
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'GET_VERSION') {
        event.ports[0].postMessage({ version: CACHE_NAME });
    }
});

// Error handling for global errors
self.addEventListener('error', (event) => {
    console.error('🇵🇭 Pareng Boyong Service Worker Error:', event.error);
});

// Unhandled promise rejection handling
self.addEventListener('unhandledrejection', (event) => {
    console.error('🇵🇭 Pareng Boyong Service Worker Unhandled Promise Rejection:', event.reason);
    event.preventDefault();
});

console.log('🇵🇭 Pareng Boyong Service Worker: Loaded and ready to serve!');