importScripts('./js/cache-polyfill.js');

self.addEventListener('install', (e) => {
    e.waitUntil(
        caches.open('countrystatecity').then((cache) => {
            // add all the following resources to the cache
            return cache.addAll([
                './',
                './css/app.css',
                './js/app.js',
                './index.html',
                './vendor/bootstrap/css/bootstrap.min.css',
                './vendor/bootstrap/js/bootstrap.bundle.min.js',
                './vendor/dynatable/css/jquery.dynatable.css',
                './vendor/dynatable/js/jquery.dynatable.js',
                './vendor/jquery/jquery.min.js',
                'https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/countries.json',
                'https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/states.json',
                'https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/cities.json'
            ]);
        })
    );
});

self.addEventListener('activate', function (event) {
    event.waitUntil(
        // Get all the cache names
        caches.keys().then(function (cacheNames) {
            return Promise.all(
                // Get all the items that are stored under a different cache name than the current one
                cacheNames.filter(function (cacheName) {
                    return cacheName == 'countrystatecity';
                }).map(function (cacheName) {
                    // Delete the items
                    return caches.delete(cacheName);
                })
            ); // end Promise.all()
        }) // end caches.keys()
    ); // end event.waitUntil()
});

// NOTE: the fetch event is triggered for every request on the page. So for every individual CSS, JS and image file.
self.addEventListener('fetch', function (event) {
    event.respondWith(
        caches.match(event.request).then(function (response) {
            return response || fetch(event.request);
        })
    );
});
