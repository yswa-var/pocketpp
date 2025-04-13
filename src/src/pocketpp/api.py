# Serve static files from the "static" directory
app.mount("/static",
          StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")
