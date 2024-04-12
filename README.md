# Spotify-CMD-Interface
A simple spotify command line interface using spotipy library

## The project is still under development.

## Requirements
* Before using it, you need to install the requirements to your env by using a
    command like:
```bash
    pip install -r requirements.txt
```
* In addition, you will need a spotify developer account to provide a
    `client-id`, `client-secret`, and a `redirect-url` in `helper_function.py`.
* The first time you try to run it, it'll open up a web page for you to log in
    and allow the program to use your info. You need to enter the url after
    redirecting to your specified url when configuring your develoer account.
### Important
After logging in, it'll create a token.txt file that stores your credential so
    that you won;t need to reauthorize it. Do not share that information with
    anyone.
## potential Issues
* One potential issue is when you try to authorize yourself, you might get a
    message like `illegal scope`. This is usually caused by the specified
    `SCOPE`.