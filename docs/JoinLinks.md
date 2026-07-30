# Info

Join links can be used either as **QR codes** or as **URLs**. They contain the URL of the server, allowing users to connect to a server without manually entering the server address.

When a join link is scanned or clicked, it will first attempt to open the server in the app. If the app is not installed, it will open the server in the web app instead.

If the server cannot be reached, an error message will be displayed.

# Format

The format of a join link is as follows:

```
https://skapersok.no/join?url=<url_encoded_server_url>
```

Where `<url_encoded_server_url>` is the URL of the server, URL-encoded so it can safely be used as a query parameter.

For example, if the server is running on:

```
http://10.0.2.2:5000
```

The join link will be:

```
https://skapersok.no/join?url=http%3A%2F%2F10.0.2.2%3A5000
```

# URL Encoding

The server URL must be URL-encoded before it can be used in a join link. This can be done using various online tools or programming libraries.

For example, in Python, you can use the `urllib.parse` module:

```python
import urllib.parse

server_url = "http://10.0.2.2:5000"

encoded_url = urllib.parse.quote(server_url, safe="")

print(encoded_url)
# Output: http%3A%2F%2F10.0.2.2%3A5000
```

Alternatively, when constructing the full join link, `urlencode()` can be used to automatically encode the query parameter:

```python
import urllib.parse

server_url = "http://10.0.2.2:5000"

join_link = "https://skapersok.no/join?" + urllib.parse.urlencode({
    "url": server_url
})

print(join_link)
# Output: https://skapersok.no/join?url=http%3A%2F%2F10.0.2.2%3A5000
```