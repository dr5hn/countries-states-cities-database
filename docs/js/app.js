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
        await data.forEach((c) => {
          countries.insert(c);
          $('.countries-tb').append(`
            <tr>
              <td class="border px-4 py-2">
                ${c.emoji} ${c.name}  <span class="inline-block bg-gray-200 rounded-full px-3 text-sm font-semibold text-gray-700">${c.iso2}</span> <button class="tooltip inline-block align-middle float-right" onclick="filterStates(${c.id})"><svg viewBox="0 0 20 20" fill="currentColor" class="arrow-circle-right w-6 h-6 text-pink-600"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clip-rule="evenodd"></path></svg><span class="tooltip-text bg-indigo-600 rounded text-white text-sm -mt-12">Show States</span></button> <button class="tooltip inline-block align-middle float-right" onclick="toggleModal(${c.id}, 'countries')"><svg viewBox="0 0 20 20" fill="currentColor" class="information-circle w-6 h-6 text-blue-600"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path></svg><span class="tooltip-text bg-indigo-600 rounded text-white text-sm -mt-12">More Details</span></button>
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
}

initializeData();

async function filterStates($cid = null) {
  let statesColl = db.getCollection("states");
  let states = await statesColl.find({ country_id: parseInt($cid) });
  let $states = $('.states-tb');
  $states.html('');
  $('.cities-tb').html('');
  if (states.length) {
    await states.forEach((s) => {
      $states.append(`
        <tr>
          <td class="border px-4 py-2">
            ${s.name}  <span class="inline-block bg-gray-200 rounded-full px-3 text-sm font-semibold text-gray-700">${s.state_code}</span> <button class="tooltip inline-block align-middle float-right" onclick="filterCities(${s.id})"><svg viewBox="0 0 20 20" fill="currentColor" class="arrow-circle-right w-6 h-6 text-pink-600"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clip-rule="evenodd"></path></svg><span class="tooltip-text bg-indigo-600 rounded text-white text-sm -mt-12">Show Cities</span></button> <button class="tooltip inline-block align-middle float-right" onclick="toggleModal(${s.id}, 'states')"><svg viewBox="0 0 20 20" fill="currentColor" class="information-circle w-6 h-6 text-blue-600"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path></svg><span class="tooltip-text bg-indigo-600 rounded text-white text-sm -mt-12">More Details</span></button>
          </td>
        </tr>
      `);
    });
  } else {
    $states.append(`
        <tr>
          <td class="border px-4 py-2">
            No States Found.
          </td>
        </tr>
      `);
  }
}

async function filterCities($sid = null) {
  let citiesColl = db.getCollection("cities");
  let cities = await citiesColl.find({ state_id: parseInt($sid) });
  let $cities = $('.cities-tb');
  $cities.html('');
  if (cities.length) {
    await cities.forEach((c) => {
      $cities.append(`
        <tr>
          <td class="border px-4 py-2">
            ${c.name} <button class="tooltip inline-block align-middle float-right" onclick="toggleModal(${c.id}, 'cities')"><svg viewBox="0 0 20 20" fill="currentColor" class="information-circle w-6 h-6 text-blue-600"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path></svg><span class="tooltip-text bg-indigo-600 rounded text-white text-sm -mt-12">More Details</span></button>
          </td>
        </tr>
      `);
    });
  } else {
    $cities.append(`
        <tr>
          <td class="border px-4 py-2">
            No Cities Found.
          </td>
        </tr>
      `);
  }
}

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

async function toggleModal($id = null, $type = null) {
  const body = document.querySelector('body')
  const modal = document.querySelector('.modal')
  modal.classList.toggle('opacity-0')
  modal.classList.toggle('pointer-events-none')
  body.classList.toggle('modal-active')

  if ($id && $type) {
    let content = { name: '' };
    if ($type == 'countries') {
      let countries = db.getCollection($type);
      let country = await countries.findOne({ id: parseInt($id) });
      delete country.$loki;
      delete country.meta;
      content = { ...country };
    } else if ($type == 'states') {
      let states = db.getCollection($type);
      let state = await states.findOne({ id: parseInt($id) });
      delete state.$loki;
      delete state.meta;
      content = { ...state };
    } else if ($type == 'cities') {
      let cities = db.getCollection($type);
      let city = await cities.findOne({ id: parseInt($id) });
      delete city.$loki;
      delete city.meta;
      content = { ...city };
    }
    $('.modal-title').html(content.name);
    $('#modal-code').html(JSON.stringify(content, undefined, 2));
  }
}

// Copy to clipboard
const textArea = document.createElement('textarea');
const copyMeOnClipboard = () => {
  const copyText = document.getElementById("modal-code").textContent;
  textArea.textContent = copyText;
  document.body.append(textArea);
  textArea.setSelectionRange(0, 99999); // used for mobile phone
  textArea.select();
  document.execCommand("copy");
  $('.copy-to-clipboard').text('Copied 🎉');
  $('.copy-to-clipboard').addClass('opacity-50 cursor-not-allowed');
  setTimeout(() => {
    $('.copy-to-clipboard').text('Copy 📋');
    $('.copy-to-clipboard').removeClass('opacity-50 cursor-not-allowed');
  }, 3000);
}


