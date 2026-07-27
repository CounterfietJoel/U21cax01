# Storyline Web publishing and staging

All nine Unit I modules in this repository already contain complete Storyline
Web publications.

When a module is revised:

1. Open the editable `.story` source in Storyline 360.
2. Choose **Publish > Web** and publish to a fresh local folder.
3. Confirm that the folder contains `story.html`, `html5`, `mobile`, and
   `story_content`.
4. Copy the complete publication into the matching `modules/<slug>/` folder.
   Preserve the existing `index.html` wrapper and `module.json`.
5. Run `python tools\validate_site.py`.
6. Serve the repository over local HTTP and run the Chrome smoke test described
   in `qa/README.md`.

Do not place editable `.story` files or supplied template originals in this
public repository.
