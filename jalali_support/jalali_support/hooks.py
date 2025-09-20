app_name = "jalali_support"
app_title = "Jalali Support"
app_publisher = "Custom"
app_description = "Persian (Jalali) calendar support for ERPNext."
app_version = "0.1.0"
app_license = "MIT"

app_include_js = [
    "public/js/jalali_support.bundle.js",
]

before_request = [
    "jalali_support.utils.patches.ensure_runtime_patches",
]

boot_session = "jalali_support.utils.boot.boot_session"

doc_events = {
    "*": {
        "before_validate": "jalali_support.utils.doc_events.convert_dates_to_gregorian",
    }
}
