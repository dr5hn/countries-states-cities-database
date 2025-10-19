# Wikipedia API docs

Wikipedia API examples. For advanced usage see [Official Mediawiki API documentation](https://www.mediawiki.org/wiki/API:Main_page)

Quick intro: 

- All client requests should contain `&origin=*` because of CORS. 
- Search term should be capitalize (`Tori Amos` not `tori amos`) if multiple words.
- You could request any wiki language you like (for example: `sh.wikipedia.org` or `de.wikipedia.org`)

## Table of content
* [Articles](#articles)
  + [Get an article](#get-an-article)
  + [Search articles](#search-articles)
* [Images](#images)
  + [GET the main image](#get-the-main-image)
  + [GET all images from the article](#get-all-images-from-the-article)
  + [Search free images](#search-free-images)
* [Quotes](#quotes)

## Articles

### Get an article

GET full article for the requested title (`titles=belgrade`), with images (`pageimages`) and article URL (`inprop=url`). Also, follows redirection (`redirects`) if necessary:

[`en.wikipedia.org/w/api.php?action=query&titles=belgrade&prop=extracts|pageimages|info&pithumbsize=400&inprop=url&redirects=&format=json&origin=*`](https://en.wikipedia.org/w/api.php?action=query&titles=belgrade&prop=extracts|pageimages|info&pithumbsize=400&inprop=url&redirects=&format=json&origin=*)

Previous request with minimal params:

[`en.wikipedia.org/w/api.php?action=query&titles=belgrade&prop=extracts&format=json`](https://en.wikipedia.org/w/api.php?action=query&titles=belgrade&prop=extracts&format=json)

GET first paragraph of an article:

[`en.wikipedia.org/w/api.php?action=query&titles=Belgrade&prop=extracts&format=json&exintro=1`](https://en.wikipedia.org/w/api.php?action=query&titles=Belgrade&prop=extracts&format=json&exintro=1)

### Search articles

To GET first 10 search results with extract and thumbnail image (`prop=extracts|pageimages`). Results is HTML by default, but we want `json` format:

[`en.wikipedia.org/w/api.php?action=query&generator=search&gsrsearch=belgrade&exintro=&prop=extracts|pageimages&format=json`](https://en.wikipedia.org/w/api.php?action=query&generator=search&gsrsearch=belgrade&exintro=&prop=extracts|pageimages&format=json)

GET first 20 search results (`srlimit`) with short info (`prop=info`):

[`en.wikipedia.org/w/api.php?action=query&list=search&prop=info&inprop=url&utf8=&format=json&srlimit=20&srsearch=belgrade`](https://en.wikipedia.org/w/api.php?action=query&list=search&prop=info&inprop=url&utf8=&format=json&srlimit=20&srsearch=belgrade)

GET first 20 search results (`gsrlimit`) with extract and thumbnail image (`prop=extracts|pageimages`). This time, article extract is set to plain text (`explaintext`):

[`en.wikipedia.org/w/api.php?action=query&generator=search&gsrlimit=20&prop=pageimages|extracts&exintro&explaintext&exlimit=max&format=json&gsrsearch=belgrade`](https://en.wikipedia.org/w/api.php?action=query&generator=search&gsrlimit=20&prop=pageimages|extracts&exintro&explaintext&exlimit=max&format=json&gsrsearch=belgrade)

**Advanced search params:**

- `gsrsearch=intitle:belgrade` (word "belgrade" is in title)
- `gsrsearch=prefix:belgrade` (article's title starts with the word "belgrade")

If you have problems, append `&origin=*` at the end of the route.

## Images

### GET the main image

Get source of the main image of the article:

[`en.wikipedia.org/w/api.php?action=query&titles=Belgrade&prop=pageimages&format=json&pithumbsize=250`](https://en.wikipedia.org/w/api.php?action=query&generator=search&gsrlimit=20&prop=pageimages|extracts&exintro&explaintext&exlimit=max&format=json&gsrsearch=belgrade)

### GET all images from the article

Get all images from the article:

[`en.wikipedia.org/w/api.php?action=query&titles=belgrade&prop=images&format=json`](https://en.wikipedia.org/w/api.php?action=query&titles=belgrade&prop=images&format=json)

### Search free images

GET first 20 image files (`gsrnamespace=6`) from Wikimedia Commons with the term "Belgrade" in the filename (`gsrsearch=intitle:Belgrade`). Requested thumbnail size is 250px (`pithumbsize=250`):

[`commons.wikimedia.org/w/api.php?prop=pageimages|imageinfo|info|redirects&gsrnamespace=6&pilimit=max&pithumbsize=250&iiprop=extmetadata&iiextmetadatafilter=ImageDescription&action=query&inprop=url&redirects=&format=json&generator=search&gsrsearch=intitle:Belgrade&gsrlimit=20`](https://commons.wikimedia.org/w/api.php?prop=pageimages|imageinfo|info|redirects&gsrnamespace=6&pilimit=max&pithumbsize=250&iiprop=extmetadata&iiextmetadatafilter=ImageDescription&action=query&inprop=url&redirects=&format=json&generator=search&gsrsearch=intitle:Belgrade&gsrlimit=20)

Previous request without some params:

[`commons.wikimedia.org/w/api.php?prop=pageimages|info|redirects&gsrnamespace=6&pithumbsize=250&action=query&inprop=url&redirects=&format=json&generator=search&gsrsearch=intitle:Belgrade&gsrlimit=20`](https://commons.wikimedia.org/w/api.php?prop=pageimages|info|redirects&gsrnamespace=6&pithumbsize=250&action=query&inprop=url&redirects=&format=json&generator=search&gsrsearch=intitle:Belgrade&gsrlimit=20)

Remember, if you have problems, append `&origin=*` at the end of the route.

## Quotes

GET wiki quotes for requested term (`titles=Zen`). The API is the same, just the domain is different (`wikiquote.org`):

[`en.wikiquote.org/w/api.php?action=query&titles=Zen&prop=extracts|info&inprop=url&redirects=&format=json`](https://en.wikiquote.org/w/api.php?action=query&titles=Zen&prop=extracts|info&inprop=url&redirects=&format=json)
