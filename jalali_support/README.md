# Jalali Support for ERPNext

This custom Frappe app keeps ERPNext data in Gregorian while presenting Jalali (Persian) dates to users.

## Features
- Stores all DocType Date/Datetime values in Gregorian, converts Jalali user input before save.
- Formats server-side and client-side date outputs as Jalali when enabled.
- Adds a **Jalali Settings** singleton DocType to enable/disable globally and choose default calendar.
- Lets users opt into Jalali or Gregorian (if permitted) via the `jalali_support.api.set_user_calendar` endpoint.
- Replaces the desk date picker locale/formatting so the calendar grid shows Jalali months/days.

## Installation
1. Copy the `jalali_support` directory into your bench apps folder (e.g. `apps/jalali_support`).
2. Ensure Python path is available:
   ```bash
   bench --site your-site-name pip install -e apps/jalali_support
   ```
3. Install the app on your site and migrate:
   ```bash
   bench --site your-site-name install-app jalali_support
   bench --site your-site-name migrate
   bench --site your-site-name clear-cache
   ```
4. Build assets so the bundled JS ships to the desk:
   ```bash
   bench build --app jalali_support
   bench restart
   ```

## Configuration
- Open **Jalali Settings** (search from Awesome Bar) and enable Jalali calendar.
- Choose the default calendar (`Jalali` or `Gregorian`).
- Decide if users may override the global choice. When enabled, call the API from client code:
  ```javascript
  frappe.call('jalali_support.api.set_user_calendar', { calendar: 'jalali' });
  ```
  Passing `'gregorian'` reverts the user back to the global default.
- You can also control defaults without the DocType via `site_config.json`:
  ```json
  {
    "enable_jalali_calendar": 1,
    "default_calendar": "jalali",
    "jalali_allow_user_override": 1
  }
  ```

## Notes & Testing
- The conversion utilities live in `jalali_support/utils/calendar.py`; add unit tests under `jalali_support/tests` if you maintain a test suite.
- After enabling Jalali, verify:
  - Creating and saving documents with Date/Datetime fields works via desk and REST.
  - List views, reports, and notifications display Jalali dates.
  - Switching back to Gregorian (globally or per user) restores original behaviour.
- If you extend ERPNext with custom scripts, call `frappe.jalali_support.toGregorianString(value)` on client input when you manually post date payloads.

## Limitations
- Background jobs run with Gregorian defaults unless a user session is associated; set `frappe.defaults.set_user_default("calendar_preference", "jalali", user)` for automated users if required.
- Ensure other apps that monkey patch date formatting run before/after this app as needed to avoid conflicts.
