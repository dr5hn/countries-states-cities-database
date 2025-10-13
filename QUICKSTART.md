# 🚀 Quick Start Guide for Contributors

This guide will help you make your first contribution to the Countries States Cities Database in just 5 minutes!

## 🎯 What You'll Need

- A GitHub account
- Basic text editing skills
- 5 minutes of your time

**That's it!** No SQL knowledge, no local setup, no build tools required.

## 📝 Contributing Data

### Step 1: Find the Right File

All contribution files are in the `contributions/` directory:

```
contributions/
├── cities/
│   ├── US.json    ← United States cities
│   ├── IN.json    ← India cities
│   ├── FR.json    ← France cities
│   └── ...        ← 209+ country files
├── countries/
│   └── countries.json
├── states/
│   └── states.json
├── regions/
│   └── regions.json
└── subregions/
    └── subregions.json
```

### Step 2: Make Your Edit

#### Adding a New City

1. **Open** the country file (e.g., `contributions/cities/US.json`)
2. **Add** your city at the end of the array:

```json
{
    "name": "New City Name",
    "state_id": 1416,
    "state_code": "CA",
    "country_id": 233,
    "country_code": "US",
    "latitude": "37.77490000",
    "longitude": "-122.41940000",
    "timezone": "America/Los_Angeles"
}
```

**⚠️ Important:** Do NOT include an `id` field for new cities! The system will assign it automatically.

#### Editing an Existing City

1. **Find** the city in the country file
2. **Keep** the `id` field unchanged
3. **Edit** the data you want to change:

```json
{
    "id": 1234,                     ← Keep this!
    "name": "Updated City Name",    ← Edit as needed
    "state_id": 1416,
    "state_code": "CA",
    ...
}
```

#### Adding a New Country

Edit `contributions/countries/countries.json`:

```json
{
    "name": "New Country",
    "iso2": "NC",
    "iso3": "NCO",
    "capital": "Capital City",
    "currency": "NCU",
    "currency_name": "New Currency",
    "phonecode": "1",
    "region": "Region Name",
    "subregion": "Subregion Name"
}
```

**Note:** Omit the `id` field - it will be auto-assigned.

#### Adding a New State/Province

Edit `contributions/states/states.json`:

```json
{
    "name": "New State",
    "country_id": 233,
    "country_code": "US",
    "state_code": "NS",
    "latitude": "40.00000000",
    "longitude": "-75.00000000"
}
```

**Note:** Omit the `id` field - it will be auto-assigned.

### Step 3: Submit Your Pull Request

1. **Fork** the repository (click "Fork" button on GitHub)
2. **Edit** the file directly on GitHub (click the pencil icon)
3. **Commit** your changes with a clear message like:
   - "Add Springfield to US cities"
   - "Update coordinates for Paris, France"
   - "Add New Country to database"
4. **Create** a pull request with a description of your changes

### Step 4: Let GitHub Actions Do the Work

After you submit your PR:

1. ✅ Maintainers review your JSON changes
2. ✅ GitHub Actions imports to MySQL (assigns IDs automatically)
3. ✅ All formats regenerated (JSON, CSV, SQL, XML, YAML, MongoDB, SQLite, PostgreSQL, SQL Server)
4. ✅ Your PR is updated with all export files

**You don't need to do anything else!** Just wait for review.

## 🔍 Finding IDs

### Finding State IDs

1. Open `contributions/states/states.json`
2. Search for your state (Ctrl+F or Cmd+F)
3. Use the `id` field value

Example:
```json
{
  "id": 1416,              ← This is the state_id
  "name": "California",
  "state_code": "CA",
  "country_id": 233,
  "country_code": "US"
}
```

### Finding Country IDs

1. Open `contributions/countries/countries.json`
2. Search for your country
3. Use the `id` field value

Example:
```json
{
  "id": 233,               ← This is the country_id
  "name": "United States",
  "iso2": "US",            ← This is the country_code
  "iso3": "USA"
}
```

## 📋 Field Reference

### City Fields

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `id` | Auto | **Omit for new cities** | `1234` |
| `name` | ✅ Yes | Official city name | `"San Francisco"` |
| `state_id` | ✅ Yes | ID from states.json | `1416` |
| `state_code` | ✅ Yes | State ISO code | `"CA"` |
| `country_id` | ✅ Yes | ID from countries.json | `233` |
| `country_code` | ✅ Yes | Country ISO2 code | `"US"` |
| `latitude` | ✅ Yes | Latitude coordinate | `"37.77490000"` |
| `longitude` | ✅ Yes | Longitude coordinate | `"-122.41940000"` |
| `timezone` | No | IANA timezone | `"America/Los_Angeles"` |
| `translations` | No | Translations object | `{"es": "San Francisco"}` |
| `wikiDataId` | No | WikiData ID | `"Q62"` |

### Adding Translations (Optional)

You can add translations for any city, state, or country:

```json
{
  "name": "Tokyo",
  "translations": {
    "es": "Tokio",
    "fr": "Tokyo",
    "de": "Tokio",
    "zh-CN": "东京",
    "ar": "طوكيو",
    "hi": "टोक्यो"
  }
}
```

**Supported languages:** Arabic (`ar`), Chinese (`zh-CN`), Croatian (`hr`), Dutch (`nl`), French (`fr`), German (`de`), Hindi (`hi`), Italian (`it`), Japanese (`ja`), Korean (`ko`), Persian (`fa`), Polish (`pl`), Portuguese (`pt`), Brazilian Portuguese (`pt-BR`), Russian (`ru`), Spanish (`es`), Turkish (`tr`), Ukrainian (`uk`), and more.

## ✅ Best Practices

1. **Validate your JSON** - Use [JSONLint](https://jsonlint.com/) or your editor's JSON validator
2. **One change at a time** - Makes reviews easier
3. **Use official sources** - Reference WikiData, Wikipedia, or government sources
4. **Clear commit messages** - Describe what you changed
5. **Check for duplicates** - Search before adding new entries

## 🚫 What NOT to Do

- ❌ **Don't edit** SQL, CSV, XML, YAML files (they're auto-generated)
- ❌ **Don't run** build scripts locally (GitHub Actions handles this)
- ❌ **Don't add** `id` field for new records (auto-assigned)
- ❌ **Don't remove** `id` field from existing records
- ❌ **Don't commit** build artifacts or dependencies

## 🆘 Need Help?

- 📖 **Detailed guide:** [contributions/README.md](contributions/README.md)
- 📝 **Contributing guidelines:** [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md)
- 🌐 **Web tool:** [CSC Update Tool](https://manager.countrystatecity.in/) - GUI alternative
- 💬 **Questions:** Open an issue with the "question" label

## 🎉 Your First Contribution

**Example: Adding a city**

1. Fork the repo
2. Edit `contributions/cities/US.json`
3. Add at the end (before the closing `]`):
   ```json
   ,
   {
       "name": "Springfield",
       "state_id": 1440,
       "state_code": "IL",
       "country_id": 233,
       "country_code": "US",
       "latitude": "39.78172000",
       "longitude": "-89.65037000",
       "timezone": "America/Chicago"
   }
   ```
4. Commit: "Add Springfield, Illinois to US cities"
5. Create PR with description: "Adding Springfield, IL (capital of Illinois)"
6. Wait for review ✅

That's it! Welcome to the community! 🌍

## 📊 Impact

With your contributions, you're helping:
- Thousands of developers worldwide
- Applications used by millions of users
- Open source geographical data ecosystem
- Making the world's location data more accessible

Thank you! 🙏

---

**Ready to contribute?** [Start here](https://github.com/dr5hn/countries-states-cities-database/fork) → Fork the repo and make your first edit!
