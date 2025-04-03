## Pyodide Examples

Use the `./server.py` to serve the files. If you request "some_directory.zip" it
the server will zip the directory on the fly and serve it. This is useful for
developing Python packages for use with Pyodide.


### Minification
```
uv run --python 3.13.2 --python-preference only-managed --with python-minifier pyminify some_funcs.py --remove-literal-statements --rename-globals
```