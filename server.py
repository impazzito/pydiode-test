#!/usr/bin/env -S uvx --with fastapi --with uvicorn --python 3.13.2 --python-preference only-managed python

from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pathlib import Path
import importlib
import zipfile
import io
import os
import sys
import py_compile

app = FastAPI()

@app.get("/")
async def root():
    """Serve index.html from the same directory as the script."""
    index_path = Path("index.html")
    if not index_path.exists():
        return {"error": "index.html not found"}
    return FileResponse(index_path)

@app.get("/{module}.zip")
async def get_module_pyc(module: str):
    """
    Generate a zip file containing compiled .pyc files for the specified module.
    Source code is compiled but not included in the zip.
    The module structure is preserved in the zip file.
    """
    try:
        # Try to import the module to get its location
        mod = importlib.import_module(module)
    except ImportError:
        raise HTTPException(status_code=404, detail=f"Module '{module}' not found")

    # Get the module path
    if hasattr(mod, '__path__'):  # Package
        module_path = mod.__path__[0]
        is_package = True
    elif hasattr(mod, '__file__'):  # Module
        module_path = os.path.dirname(mod.__file__)
        is_package = False
    else:
        raise HTTPException(status_code=404, detail=f"Cannot determine path for module '{module}'")

    # Get the parent directory to maintain correct structure
    parent_dir = os.path.dirname(module_path)

    # Create an in-memory zip file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Walk through the module directory
        for root, _, files in os.walk(module_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Process Python files
                if file.endswith('.py'):
                    try:
                        # Get the relative path from the parent directory
                        # This preserves the module name in the path
                        rel_path = os.path.relpath(file_path, parent_dir)
                        # Replace .py extension with .pyc
                        pyc_rel_path = os.path.splitext(rel_path)[0] + '.pyc'

                        # Compile the file
                        pyc_path = py_compile.compile(file_path, cfile=None, doraise=True)

                        # Add the compiled file to the zip with the correct relative path
                        if pyc_path:
                            zip_file.write(pyc_path, pyc_rel_path)
                    except Exception as e:
                        print(f"Error compiling {file_path}: {e}")
                        continue


    # Reset the buffer position
    zip_buffer.seek(0)

    # Return the zip file as a response
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={module}.zip"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)