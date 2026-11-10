# Tartarus Spellboard · WoW Forever

A self-contained skill and keybind reference for the Razer Tartarus Pro and a standard US ANSI 104-key keyboard. Drag spell icons onto controls and keep separate layouts for each character and modifier layer.

**[Open the live app](https://rstolle.github.io/tartarus-pro-wow-key-mapper/)**

Source: [rstolle/tartarus-pro-wow-key-mapper](https://github.com/rstolle/tartarus-pro-wow-key-mapper)

## Visual themes

Use **Choose your world** above the profile toolbar to switch between **WoW Retail** (violet and gold), **WoW Classic** (bronze and parchment), and **WoW Forever** (forest green and gold). The selected appearance persists in this browser and is embedded in **Save HTML** downloads. Themes apply to both device layouts, editors, and dialogs. They change appearance only; the embedded spell library remains the WoW Forever snapshot.

## Features

- 502 spell entries across nine classes, with embedded icons
- Tartarus Pro and full keyboard layouts
- Base, Shift, Ctrl, and Alt layers
- Editable keybind labels, shortcut recording, and notes
- Custom skill icons, profiles, undo, and print/reference views
- Browser autosave, JSON import/export, and portable HTML backups

## Use the app

Open the published GitHub Pages URL, or double-click `tartarus-wow.html` to run the complete app locally. All app code, styles, spell data, and icons are embedded in that file. No package installation, backend, or API key is required.

Choose a device and class, then drag a spell onto a control. You can also click a spell, then click a control. Select a control to edit its keybind or use **Record** to capture a key combination.

Assignments are a visual reference. Configure the actual device and in-game keybinds in Razer Synapse and WoW.

## Deploy to GitHub Pages

This repository uses **Settings → Pages → Source: GitHub Actions**. The workflow in `.github/workflows/pages.yml` publishes the app whenever you push to `main`. It uploads only the app's static files and serves the complete app at the site's root URL.

Pages is already configured for this repository. The steps below apply if you deploy a separate copy:

1. Push this project to a GitHub repository with a `main` branch.
2. In the repository, open **Settings → Pages**.
3. Under **Build and deployment → Source**, select **GitHub Actions**.
4. Open **Actions → Deploy to GitHub Pages → Run workflow**, or push a commit to `main`.
5. Open the published URL shown by the deployment, normally `https://YOUR-USERNAME.github.io/YOUR-REPOSITORY/`.

The workflow uses GitHub's automatic `GITHUB_TOKEN`; no personal access token needs to be added as a repository secret. GitHub Free supports Pages for public repositories. For private repositories, check your GitHub plan.

If you prefer publishing from a branch, choose **Deploy from a branch**, `main`, and `/ (root)` in Pages settings. The small `index.html` launcher opens `tartarus-wow.html` using a relative link, so it also works under a project URL.

See [GitHub's Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## Move existing layouts to the website

Browser saves belong to the site and browser where they were created. Opening the hosted app will not automatically find layouts saved in a local HTML file or another website.

1. Open the old app in the browser where your layouts are saved.
2. Click **Export** to save a JSON backup.
3. Open the hosted app and click **Import**, then choose that backup.

The app keeps your profiles and custom icons in local browser storage. They are not uploaded to GitHub or synchronized between devices. Keep a JSON backup or use **Save HTML** to download the entire app with your current layouts embedded. Do not commit a personalized HTML backup to a public repository unless you intend to share those layouts.

## Local preview

Double-click `index.html` or `tartarus-wow.html`, or serve this directory with Python:

```sh
python -m http.server 8080 --bind 127.0.0.1
```

Then open `http://127.0.0.1:8080/`.

## Editing

Edit `tartarus-wow.html` and push to `main` to update the hosted app. The workflow copies it to the deployed `index.html`; the source `index.html` is only a launcher for local use and branch-based Pages hosting. The deployed site also retains the `tartarus-wow.html` URL.

## Credits

The embedded spellbook snapshot comes from [WCLBox's WoW Forever spellbook](https://wowforever.wclbox.com/en), collected November 10, 2026. The app includes source and device-layout credits in **Sources & credits**.

World of Warcraft, spell icons, and related names belong to Blizzard Entertainment. Razer and Tartarus are trademarks of Razer. This fan tool is unaffiliated with either company.
