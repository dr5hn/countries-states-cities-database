importScripts('js/cache-polyfill.js');

CACHE_VERSION = 1;
var CURRENT_CACHES = {
    offline: 'offline-v' + CACHE_VERSION
};
OFFLINE_URL = 'offline.html';
FOUR_OH_FOUR_URL = 'four-o-four.html';

self.addEventListener('install', (e) => {
    e.waitUntil(
        caches.open('countrystatecity').then((cache) => {
            // add all the following resources to the cache
            return cache.addAll([
                'https://dr5hn.github.io/countries-states-cities-database/',
                'css/app.css',
                'js/app.js',
                'index.html',
                'vendor/bootstrap/css/bootstrap.min.css',
                'vendor/bootstrap/js/bootstrap.bundle.min.js',
                'vendor/dynatable/css/jquery.dynatable.css',
                'vendor/dynatable/js/jquery.dynatable.js',
                'vendor/jquery/jquery.min.js',
                'https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/countries.json',
                'https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/states.json',
                'https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/cities.json',
                '.'
            ]);
        })
    );
});

// NOTE: the fetch event is triggered for every request on the page. So for every individual CSS, JS and image file.
self.addEventListener('fetch', function (event) {
    event.respondWith(
        caches.match(event.request).then(function (response) {
            return response || fetch(event.request);
        })
    );
});
