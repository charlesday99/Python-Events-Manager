self.addEventListener('install', function(event) {
	console.log("Worked has been installed!");
});

self.addEventListener('fetch', event => {
	//console.log("I will fetch things!");
});
/*
importScripts('https://storage.googleapis.com/workbox-cdn/releases/4.3.1/workbox-sw.js');

// Debug messages
workbox.setConfig({debug: true});

// JS
workbox.routing.registerRoute(
	/\.js$/,
	new workbox.strategies.StaleWhileRevalidate({
		cacheName: 'workbox:js',
	})
);

// CSS
workbox.routing.registerRoute(
	/\.css$/,
	new workbox.strategies.StaleWhileRevalidate({
		cacheName: 'workbox:css',
	})
);

// HTML
workbox.routing.registerRoute(
	new RegExp('[a-zA-Z0-9]{4,10}$'),
	new workbox.strategies.CacheFirst({
		cacheName: 'workbox:html',
	})
);

// Fonts
workbox.routing.registerRoute(
	/\.ttf$/,
	new workbox.strategies.CacheFirst({
		cacheName: 'workbox:fonts',
	})
);

// JSON
workbox.routing.registerRoute(
	/\.json$/,
	new workbox.strategies.CacheFirst({
		cacheName: 'workbox:json',
		plugins: [
			new workbox.expiration.Plugin({
				maxEntries: 20, // Cache only 20 files
				maxAgeSeconds: 30 * 24 * 60 * 60, // Cache for a maximum of a month
				purgeOnQuotaError: true,
			})
		],
	})
);

// Images
workbox.routing.registerRoute(
	/.*\.(?:png|jpg|jpeg|svg|gif|ico)/,
	new workbox.strategies.CacheFirst({
		cacheName: 'workbox:images',
		plugins: [
			new workbox.expiration.Plugin({
				maxEntries: 20, // Cache only 20 images
				maxAgeSeconds: 30 * 24 * 60 * 60, // Cache for a maximum of a month
				purgeOnQuotaError: true,
			})
		],
	})
);
*/