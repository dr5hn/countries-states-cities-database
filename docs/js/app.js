// check see if your browser supports service workers
// if ('serviceWorker' in navigator) {
//     navigator.serviceWorker
//         // register the service worker script
//         .register('./sw.js')
//         // using promises tell us if successful or there was an error
//         .then(reg => {console.info('Service Worker registration successful: ', reg)})
//         .catch(err => {console.warn('Service Worker setup failed: ', err)});
// }

// $(function () {
//     function initializeDyna(data, target) {
//         var $dynaConfig = {
//             inputs: {
//                 queryEvent: 'blur change keyup',
//                 processingText: 'Processing...',
//                 multisort: ['ctrlKey', 'shiftKey', 'metaKey']
//             },
//             dataset: {
//                 records: data,
//                 perPageDefault: 15,
//                 perPageOptions: [15, 20, 50, 100],
//                 sortTypes: {
//                     'id': 'number'
//                 }
//             }
//         };
//         $('#' + target).dynatable($dynaConfig);
//     }

//     $.getJSON('https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/countries.json')
//         .done(function (data) {
//             initializeDyna(data, 'countries');
//         });

//     $.getJSON('https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/states.json')
//         .done(function (data) {
//             initializeDyna(data, 'states');
//         });

//     $.getJSON('https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/cities.json')
//         .done(function (data) {
//             initializeDyna(data, 'cities');
//         });

//     $(document).on('click', '.toggle', function() {
//         $('.toggle').removeClass('active');
//         $('.cities, .countries, .states').fadeOut();
//         $(this).addClass('active');
//         $('.'+$(this).data('toggle')).fadeIn();
//     });
// });

var db = new loki('csc.db');

const countriesJSON = 'https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/countries.json';
const statesJSON = 'https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/states.json';
const citiesJSON = 'https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/cities.json';

async function initializeData() {
    var countries = db.getCollection("countries");
    if (!countries) {
      countries = db.addCollection('countries');
      await fetch(countriesJSON)
        .then(response => response.json())
        .then(async (data) => {
          await data.forEach((d) => {
            countries.insert(d);
            $('.countries-tb').append(`<tr><td class="border px-4 py-2">${d.name}</td></tr>`);
          });
        });
    }
     
	var states = db.getCollection("states");
    if (!states) {
      states = db.addCollection('states');
      await fetch(statesJSON)
        .then(response => response.json())
        .then(async (data) => {
          await data.forEach((d) => {
            states.insert(d);
          });
        });
     }
     
	var cities = db.getCollection("cities");
    if (!cities) {
      cities = db.addCollection('cities');
      await fetch(citiesJSON)
        .then(response => response.json())
        .then(async (data) => {
          await data.forEach((d) => {
            cities.insert(d);
          });
        });
     }
      
    // Find and update an existing document
    var tyrfing = await countries.find();
    console.log('tyrfing value :', tyrfing);
    console.log('odins items', states.find({ 'country_code': 'IN' }));
}

initializeData();

function filter(type) {
    // Declare variables
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById('search-'+type);
    filter = input.value.toUpperCase();
    table = document.getElementById(type);
    tr = table.getElementsByTagName("tr");
  
    // Loop through all table rows, and hide those who don't match the search query
    for (i = 0; i < tr.length; i++) {
      td = tr[i].getElementsByTagName("td")[0];
      if (td) {
        txtValue = td.textContent || td.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
          tr[i].style.display = "";
        } else {
          tr[i].style.display = "none";
        }
      }
    }
  }

// async function fillCountries() {
//     $('.countries-tb').html('');
//     let countries = await countries.find();    
// }

