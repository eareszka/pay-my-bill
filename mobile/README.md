# Yearnly iOS shell

A Capacitor wrapper that opens https://yearnly.app full-screen as a native iOS app (#193). The site is the app; this folder only holds the shell.

- **App ID:** `app.yearnly.ios` (permanent). **Name:** Yearnly.
- **Config:** `capacitor.config.json` points `server.url` at the live site. `www/` is only a fallback page.
- **Links** to other sites (Cash App, Venmo, PayPal, Stripe) open outside the app, in Safari or the pay app.
- **Icon:** `ios/App/App/Assets.xcassets/AppIcon.appiconset` holds the 1024 deck icon (DESIGN.md → App Icon). The launch screen is plain void.

## Ship a TestFlight build
GitHub → Actions → **iOS TestFlight** → Run workflow. It runs on a macOS runner, signs automatically with the App Store Connect API key, and uploads. The build number is the workflow's run number.

Secrets it needs (repo Settings → Secrets and variables → Actions): `ASC_KEY_ID`, `ASC_ISSUER_ID`, `ASC_KEY_P8` (the whole `.p8` file's text), and `APPLE_TEAM_ID`.

## Change the shell
```
cd mobile
npm ci
npx cap sync ios
```
Commit what changes under `ios/`. Bump `MARKETING_VERSION` in the Xcode project for a new public version.
