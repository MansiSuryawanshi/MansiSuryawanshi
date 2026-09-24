# Installation

1. Replace the current contents of your `MansiSuryawanshi` profile repository with this package.
2. Commit and push all files, including `.github/workflows/profile-graphics.yml`.
3. Open the **Actions** tab and run **Refresh profile graphics** once. The scheduled workflow then refreshes the two repository graphics daily.

The portrait is already generated. To regenerate it later:

```bash
python -m pip install pillow
python scripts/make_ascii_svg.py path/to/new-photo.jpg assets/ascii.svg
```

No external image service is used. GitHub supplies the workflow token automatically.
