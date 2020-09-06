// check see if your browser supports service workers
// if ('serviceWorker' in navigator) {
//     navigator.serviceWorker
//         // register the service worker script
//         .register('./sw.js')
//         // using promises tell us if successful or there was an error
//         .then(reg => {console.info('Service Worker registration successful: ', reg)})
//         .catch(err => {console.warn('Service Worker setup failed: ', err)});
// }

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
          $('.countries-tb').append(`
            <tr>
              <td class="border px-4 py-2">
                ${d.emoji} ${d.name}  <span class="inline-block bg-gray-200 rounded-full px-3 text-sm font-semibold text-gray-700">${d.iso2}</span> <button class="inline-block align-middle float-right"><svg viewBox="0 0 20 20" fill="currentColor" class="arrow-circle-right w-6 h-6 text-pink-600"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clip-rule="evenodd"></path></svg></button> <a href="#" class="inline-block align-middle float-right" onclick="toggleModal('${d.id}')"><svg viewBox="0 0 20 20" fill="currentColor" class="information-circle w-6 h-6 text-blue-600"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path></svg></a>
              </td>
            </tr>
          `);
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
  input = document.getElementById('search-' + type);
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

// Modal
const overlay = document.querySelector('.modal-overlay')
overlay.addEventListener('click', toggleModal)

var closemodal = document.querySelectorAll('.modal-close')
for (var i = 0; i < closemodal.length; i++) {
    closemodal[i].addEventListener('click', toggleModal)
}

document.onkeydown = function (evt) {
    evt = evt || window.event
    var isEscape = false
    if ("key" in evt) {
        isEscape = (evt.key === "Escape" || evt.key === "Esc")
    } else {
        isEscape = (evt.keyCode === 27)
    }
    if (isEscape && document.body.classList.contains('modal-active')) {
        toggleModal()
    }
};

async function toggleModal($id = null) {
    const body = document.querySelector('body')
    const modal = document.querySelector('.modal')
    modal.classList.toggle('opacity-0')
    modal.classList.toggle('pointer-events-none')
    body.classList.toggle('modal-active')

    if ($id) {
        var countries = db.getCollection("countries");
        let country = await countries.findOne({ id: parseInt($id) });
        delete country.$loki;
        delete country.meta;
        console.log(country);
        const $title = $('.modal-title');
        console.log($title);
        $title.html(country.name);
        const $code = $('.modal-code');
        console.log($code);
        $code.html(JSON.stringify(country, undefined, 2));
    }
}


