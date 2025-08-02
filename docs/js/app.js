// IndexedDB setup
let db;
const DB_NAME = 'CountryStateCityDB';
const DB_VERSION = 1;
const COLLECTIONS = ['regions', 'subregions', 'countries', 'states', 'cities'];
const API_BASE = 'https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/json/';

function deleteDatabase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.deleteDatabase(DB_NAME);

    request.onsuccess = () => {
      console.log(`Database ${DB_NAME} successfully deleted`);
      resolve();
    };

    request.onerror = (event) => {
      console.error(`Error deleting database: ${event.target.error}`);
      reject(event.target.error);
    };
  });
}


function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onerror = event => reject("IndexedDB error: " + event.target.error);

    request.onsuccess = event => {
      db = event.target.result;
      resolve(db);
    };

    request.onupgradeneeded = event => {
      db = event.target.result;
      COLLECTIONS.forEach(collectionName => {
        if (!db.objectStoreNames.contains(collectionName)) {
          const store = db.createObjectStore(collectionName, { keyPath: 'id' });

          // Add indexes based on the collection
          switch(collectionName) {
            case 'subregions':
              store.createIndex('region_id', 'region_id', { unique: false });
              break;
            case 'countries':
              store.createIndex('subregion_id', 'subregion_id', { unique: false });
              break;
            case 'states':
              store.createIndex('country_id', 'country_id', { unique: false });
              break;
            case 'cities':
              store.createIndex('state_id', 'state_id', { unique: false });
              break;
          }
        }
      });
      console.log('Database upgraded');
    };
  });
}

async function initializeData() {
  console.log('Initializing data');
  // Delete existing database if requested via URL parameter
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('reset') === 'true') {
    await deleteDatabase();
    window.location.search = '';
  }

  await openDB();
  for (const collectionName of COLLECTIONS) {
    const objectStore = db.transaction(collectionName, 'readonly').objectStore(collectionName);
    const count = await new Promise(resolve => objectStore.count().onsuccess = e => resolve(e.target.result));

    if (count === 0) {
      await fetch(`${API_BASE}${collectionName}.json`)
        .then(response => response.json())
        .then(async (data) => {
          const transaction = db.transaction(collectionName, 'readwrite');
          const store = transaction.objectStore(collectionName);
          for (const item of data) {
            store.add(item);
          }
          await new Promise(resolve => transaction.oncomplete = resolve);
        });
    }

    if (collectionName === 'regions') {
      const regions = await getAllFromStore('regions');
      renderRegions(regions);
    }
  }
}

function getAllFromStore(storeName) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(storeName, 'readonly');
    const store = transaction.objectStore(storeName);
    const request = store.getAll();
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

function renderRegions(regions) {
  const regionsTb = document.querySelector('.regions-tb');
  regionsTb.innerHTML = regions.map(r => `
    <tr>
      <td class="border px-4 py-2">
        ${r.name}
        <button class="tooltip inline-block align-middle float-right" onclick="filterSubregions(${r.id})">
          <svg viewBox="0 0 20 20" fill="currentColor" class="arrow-circle-right w-6 h-6 text-pink-600">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clip-rule="evenodd"></path>
          </svg>
          <span class="tooltip-text bg-indigo-600 rounded text-white text-sm -mt-12">Show Subregions</span>
        </button>
        <button class="tooltip inline-block align-middle float-right" onclick="toggleModal(${r.id}, 'regions')">
          <svg viewBox="0 0 20 20" fill="currentColor" class="information-circle w-6 h-6 text-blue-600">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
          </svg>
          <span class="tooltip-text bg-indigo-600 rounded text-white text-sm -mt-12">More Details</span>
        </button>
      </td>
    </tr>
  `).join('');
}

async function filterSubregions(regionId) {
  if (typeof regionId === 'string') {
    window.location.search = 'reset=true';
    window.location.reload();
  }
  const subregions = await getFromIndex('subregions', 'region_id', regionId);
  renderSubregions(subregions);
  document.querySelector('.countries-tb').innerHTML = '';
  document.querySelector('.states-tb').innerHTML = '';
  document.querySelector('.cities-tb').innerHTML = '';
}

async function getFromIndex(storeName, indexName, value) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(storeName, 'readonly');
    const store = transaction.objectStore(storeName);
    const index = store.index(indexName);
    const request = index.getAll(value);
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

function renderSubregions(subregions) {
  const subregionsTb = document.querySelector('.subregions-tb');
  subregionsTb.innerHTML = subregions.length ? subregions.map(sr => `
    <tr>
      <td class="border px-4 py-2">
        ${sr.name}
        <button class="tooltip inline-block align-middle float-right" onclick="filterCountries(${sr.id})">
          <svg viewBox="0 0 20 20" fill="currentColor" class="arrow-circle-right w-6 h-6 text-pink-600">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clip-rule="evenodd"></path>
          </svg>
          <span class="tooltip-text bg-indigo-600 rounded text-white text-sm -mt-12">Show Countries</span>
        </button>
        <button class="tooltip inline-block align-middle float-right" onclick="toggleModal(${sr.id}, 'subregions')">
          <svg viewBox="0 0 20 20" fill="currentColor" class="information-circle w-6 h-6 text-blue-600">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
          </svg>
          <span class="tooltip-text bg-indigo-600 rounded text-white text-sm -mt-12">More Details</span>
        </button>
      </td>
    </tr>
  `).join('') : '<tr><td class="border px-4 py-2">No Subregions Found.</td></tr>';
}

async function filterCountries(subregionId) {
  const countries = await getFromIndex('countries', 'subregion_id', subregionId);
  renderCountries(countries);
  document.querySelector('.states-tb').innerHTML = '';
  document.querySelector('.cities-tb').innerHTML = '';
}

function renderCountries(countries) {
  const countriesTb = document.querySelector('.countries-tb');
  countriesTb.innerHTML = countries.map(c => `
    <tr>
      <td class="border px-4 py-2">
        <span class="emoji">${c.emoji}</span> ${c.name}
        <span class="inline-block bg-gray-200 rounded-full px-3 text-sm font-semibold text-gray-700">${c.iso2}</span>
        <button class="tooltip inline-block align-middle float-right" onclick="filterStates(${c.id})">
          <svg viewBox="0 0 20 20" fill="currentColor" class="arrow-circle-right w-6 h-6 text-pink-600">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clip-rule="evenodd"></path>
          </svg>
          <span class="tooltip-text bg-indigo-600 rounded text-white text-sm -mt-12">Show States</span>
        </button>
        <button class="tooltip inline-block align-middle float-right" onclick="toggleModal(${c.id}, 'countries')">
          <svg viewBox="0 0 20 20" fill="currentColor" class="information-circle w-6 h-6 text-blue-600">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
          </svg>
          <span class="tooltip-text bg-indigo-600 rounded text-white text-sm -mt-12">More Details</span>
        </button>
      </td>
    </tr>
  `).join('');
}

async function filterStates(countryId) {
  const states = await getFromIndex('states', 'country_id', countryId);
  renderStates(states);
  document.querySelector('.cities-tb').innerHTML = '';
}

function renderStates(states) {
  const statesTb = document.querySelector('.states-tb');
  statesTb.innerHTML = states.length ? states.map(s => `
    <tr>
      <td class="border px-4 py-2">
        ${s.name}
        <span class="inline-block bg-gray-200 rounded-full px-3 text-sm font-semibold text-gray-700">${s.iso2}</span>
        <button class="tooltip inline-block align-middle float-right" onclick="filterCities(${s.id})">
          <svg viewBox="0 0 20 20" fill="currentColor" class="arrow-circle-right w-6 h-6 text-pink-600">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clip-rule="evenodd"></path>
          </svg>
          <span class="tooltip-text bg-indigo-600 rounded text-white text-sm -mt-12">Show Cities</span>
        </button>
        <button class="tooltip inline-block align-middle float-right" onclick="toggleModal(${s.id}, 'states')">
          <svg viewBox="0 0 20 20" fill="currentColor" class="information-circle w-6 h-6 text-blue-600">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
          </svg>
          <span class="tooltip-text bg-indigo-600 rounded text-white text-sm -mt-12">More Details</span>
        </button>
      </td>
    </tr>
  `).join('') : '<tr><td class="border px-4 py-2">No States Found.</td></tr>';
}

async function filterCities(stateId) {
  const cities = await getFromIndex('cities', 'state_id', parseInt(stateId));
  renderCities(cities);
}

function renderCities(cities) {
  const citiesTb = document.querySelector('.cities-tb');
  citiesTb.innerHTML = cities.length ? cities.map(c => `
    <tr>
      <td class="border px-4 py-2">
        ${c.name}
        <button class="tooltip inline-block align-middle float-right" onclick="toggleModal(${c.id}, 'cities')">
          <svg viewBox="0 0 20 20" fill="currentColor" class="information-circle w-6 h-6 text-blue-600">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
          </svg>
          <span class="tooltip-text bg-indigo-600 rounded text-white text-sm -mt-12">More Details</span>
        </button>
      </td>
    </tr>
  `).join('') : '<tr><td class="border px-4 py-2">No Cities Found.</td></tr>';
}

function filter(type) {
  const input = document.getElementById('search-' + type);
  const filter = input.value.toUpperCase();
  const table = document.getElementById(type);
  const rows = table.getElementsByTagName("tr");

  for (let row of rows) {
    const cell = row.getElementsByTagName("td")[0];
    if (cell) {
      const txtValue = cell.textContent || cell.innerText;
      row.style.display = txtValue.toUpperCase().includes(filter) || filter === "" ? "" : "none";
    }
  }
}

const overlay = document.querySelector('.modal-overlay');
overlay.addEventListener('click', toggleModal);

document.querySelectorAll('.modal-close').forEach(el => el.addEventListener('click', toggleModal));

document.addEventListener('keydown', (evt) => {
  if ((evt.key === "Escape" || evt.key === "Esc") && document.body.classList.contains('modal-active')) {
    toggleModal();
  }
});

async function toggleModal(id = null, type = null) {
  const body = document.querySelector('body');
  const modal = document.querySelector('.modal');
  modal.classList.toggle('opacity-0');
  modal.classList.toggle('pointer-events-none');
  body.classList.toggle('modal-active');

  if (id && type) {
    const transaction = db.transaction(type, 'readonly');
    const store = transaction.objectStore(type);
    const request = store.get(parseInt(id));

    request.onsuccess = (event) => {
      const item = event.target.result;
      if (item) {
        document.querySelector('.modal-title').textContent = item.name;
        document.getElementById('modal-code').textContent = JSON.stringify(item, null, 2);
      }
    };

    request.onerror = (event) => {
      console.error("Error fetching item:", event.target.error);
    };
  }
}


// Optimized copy to clipboard function
const copyToClipboard = () => {
  const copyText = document.getElementById("modal-code").textContent;
  navigator.clipboard.writeText(copyText).then(() => {
    const copyBtn = document.querySelector('.copy-to-clipboard');
    copyBtn.textContent = 'Copied 🎉';
    copyBtn.classList.add('opacity-50', 'cursor-not-allowed');
    setTimeout(() => {
      copyBtn.textContent = 'Copy 📋';
      copyBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    }, 3000);
  });
}

document.querySelector('.copy-to-clipboard').addEventListener('click', copyToClipboard);

// Add this line to initialize the database when the page loads
window.addEventListener('load', initializeData);
