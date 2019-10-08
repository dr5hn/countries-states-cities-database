// check see if your browser supports service workers
if ('serviceWorker' in navigator) {
    navigator.serviceWorker
        // register the service worker script
        .register('./sw.js')
        // using promises tell us if successful or there was an error
        .then(reg => {console.info('Service Worker registration successful: ', reg)})
        .catch(err => {console.warn('Service Worker setup failed: ', err)});
}

$(function () {
    function initializeDyna(data, target) {
        var $dynaConfig = {
            inputs: {
                queryEvent: 'blur change keyup',
                processingText: 'Processing...',
                multisort: ['ctrlKey', 'shiftKey', 'metaKey']
            },
            dataset: {
                records: data,
                perPageDefault: 15,
                perPageOptions: [15, 20, 50, 100],
                sortTypes: {
                    'id': 'number'
                }
            }
        };
        $('#' + target).dynatable($dynaConfig);
    }

    $.getJSON('https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/countries.json')
        .done(function (data) {
            initializeDyna(data, 'countries');
        });

    $.getJSON('https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/states.json')
        .done(function (data) {
            initializeDyna(data, 'states');
        });

    $.getJSON('https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/cities.json')
        .done(function (data) {
            initializeDyna(data, 'cities');
        });

    $(document).on('click', '.toggle', function() {
        $('.toggle').removeClass('active');
        $('.cities, .countries, .states').fadeOut();
        $(this).addClass('active');
        $('.'+$(this).data('toggle')).fadeIn();
    });
});
