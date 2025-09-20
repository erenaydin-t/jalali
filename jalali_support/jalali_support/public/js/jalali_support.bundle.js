(function () {
  if (typeof frappe === "undefined") {
    return;
  }

  frappe.provide("frappe.jalali_support");

  var bootConfig = (frappe.boot && frappe.boot.jalali_support) || {};

  var jalaliMonthDays = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29];
  var gregorianMonthDays = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  var jalaliMonthNames = [
    "Farvardin",
    "Ordibehesht",
    "Khordad",
    "Tir",
    "Mordad",
    "Shahrivar",
    "Mehr",
    "Aban",
    "Azar",
    "Dey",
    "Bahman",
    "Esfand"
  ];
  var jalaliWeekdayLong = [
    "Shanbeh",
    "Yekshanbeh",
    "Doshanbeh",
    "Seshanbeh",
    "Chaharshanbeh",
    "Panjshanbeh",
    "Jomeh"
  ];
  var jalaliWeekdayShort = ["Sh", "Ye", "Do", "Se", "Ch", "Pa", "Jo"];

  function isLeapGregorian(year) {
    return year % 400 === 0 || (year % 4 === 0 && year % 100 !== 0);
  }

  function jalaliToGregorian(jy, jm, jd) {
    var year = jy - 979;
    var month = jm - 1;
    var day = jd - 1;

    var jDayNo = 365 * year + Math.floor(year / 33) * 8 + Math.floor(((year % 33) + 3) / 4);
    for (var i = 0; i < month; i += 1) {
      jDayNo += jalaliMonthDays[i];
    }
    jDayNo += day;

    var gDayNo = jDayNo + 79;

    var gy = 1600 + 400 * Math.floor(gDayNo / 146097);
    gDayNo %= 146097;

    var leap = true;
    if (gDayNo >= 36525) {
      gDayNo -= 1;
      gy += 100 * Math.floor(gDayNo / 36524);
      gDayNo %= 36524;

      if (gDayNo >= 365) {
        gDayNo += 1;
      } else {
        leap = false;
      }
    }

    gy += 4 * Math.floor(gDayNo / 1461);
    gDayNo %= 1461;

    if (gDayNo >= 366) {
      leap = false;
      gDayNo -= 1;
      gy += Math.floor(gDayNo / 365);
      gDayNo %= 365;
    }

    var gd = gDayNo + 1;
    var months = gregorianMonthDays.slice();
    months[1] = leap || isLeapGregorian(gy) ? 29 : 28;
    var gm = 0;
    while (gm < 12 && gd > months[gm]) {
      gd -= months[gm];
      gm += 1;
    }

    return { year: gy, month: gm + 1, day: gd };
  }

  function gregorianToJalali(gy, gm, gd) {
    var year = gy - 1600;
    var month = gm - 1;
    var day = gd - 1;

    var gDayNo = 365 * year + Math.floor((year + 3) / 4) - Math.floor((year + 99) / 100) + Math.floor((year + 399) / 400);

    for (var i = 0; i < month; i += 1) {
      gDayNo += gregorianMonthDays[i];
    }
    if (month > 1 && isLeapGregorian(gy)) {
      gDayNo += 1;
    }
    gDayNo += day;

    var jDayNo = gDayNo - 79;
    var jNp = Math.floor(jDayNo / 12053);
    jDayNo %= 12053;

    var jy = 979 + 33 * jNp + 4 * Math.floor(jDayNo / 1461);
    jDayNo %= 1461;

    if (jDayNo >= 366) {
      jy += Math.floor((jDayNo - 1) / 365);
      jDayNo = (jDayNo - 1) % 365;
    }

    var jm = 0;
    var jd;
    for (; jm < 12; jm += 1) {
      var days = jalaliMonthDays[jm];
      if (jDayNo < days) {
        jd = jDayNo + 1;
        break;
      }
      jDayNo -= days;
    }
    if (typeof jd === "undefined") {
      jd = jDayNo + 1;
    }

    return { year: jy, month: jm + 1, day: jd };
  }

  function normalizeSeparators(value) {
    return value.replace(/[/.]/g, "-");
  }

  function splitDateTime(value) {
    var trimmed = value.trim();
    var parts = trimmed.split(/\s+/);
    var date = parts[0];
    var time = parts.length > 1 ? parts[1] : null;
    return { date: date, time: time };
  }

  function pad(num) {
    return String(num).padStart(2, "0");
  }

  function isJalaliString(value) {
    if (!value || typeof value !== "string") {
      return false;
    }
    var normalized = normalizeSeparators(value.trim());
    var match = normalized.match(/^(\d{3,4})-(\d{1,2})-(\d{1,2})/);
    if (!match) {
      return false;
    }
    var year = Number(match[1]);
    return year < 1700;
  }

  function parseJalaliString(value) {
    var normalized = normalizeSeparators(value.trim());
    var parts = splitDateTime(normalized);
    var numbers = parts.date.split("-").map(Number);
    var y = numbers[0];
    var m = numbers[1];
    var d = numbers[2];
    if (!(y && m && d) || y >= 1700) {
      throw new Error("Not a Jalali date string");
    }
    var hours = 0;
    var minutes = 0;
    var seconds = 0;
    if (parts.time) {
      var chunks = parts.time.split(":").map(Number);
      hours = chunks[0] || 0;
      minutes = chunks[1] || 0;
      seconds = chunks[2] || 0;
    }
    return { year: y, month: m, day: d, hours: hours, minutes: minutes, seconds: seconds, timeProvided: Boolean(parts.time) };
  }

  function toGregorianDate(value) {
    var parts = parseJalaliString(value);
    var g = jalaliToGregorian(parts.year, parts.month, parts.day);
    return new Date(g.year, g.month - 1, g.day, parts.hours, parts.minutes, parts.seconds);
  }

  function formatGregorianString(dateObj, includeTime) {
    var yy = dateObj.getFullYear();
    var mm = pad(dateObj.getMonth() + 1);
    var dd = pad(dateObj.getDate());
    var base = yy + "-" + mm + "-" + dd;
    if (includeTime) {
      base += " " + pad(dateObj.getHours()) + ":" + pad(dateObj.getMinutes()) + ":" + pad(dateObj.getSeconds());
    }
    return base;
  }

  function toGregorianString(value, includeTime) {
    var dateObj = toGregorianDate(value);
    var withTime = includeTime || value.indexOf(":") !== -1;
    return formatGregorianString(dateObj, withTime);
  }

  function fromGregorian(value, includeTime) {
    if (!value) {
      return value;
    }
    var dateObj;
    if (value instanceof Date) {
      dateObj = value;
    } else if (typeof value === "string") {
      var normalized = normalizeSeparators(value.trim());
      if (!normalized) {
        return normalized;
      }
      var dt = new Date(normalized);
      if (isNaN(dt.getTime())) {
        return value;
      }
      dateObj = dt;
    } else {
      return value;
    }

    var gYear = dateObj.getFullYear();
    var gMonth = dateObj.getMonth() + 1;
    var gDay = dateObj.getDate();
    var jalali = gregorianToJalali(gYear, gMonth, gDay);
    var result = jalali.year + "-" + pad(jalali.month) + "-" + pad(jalali.day);
    if (includeTime) {
      result += " " + pad(dateObj.getHours()) + ":" + pad(dateObj.getMinutes()) + ":" + pad(dateObj.getSeconds());
    }
    return result;
  }

  function toArray(handler) {
    if (!handler) {
      return [];
    }
    if (Array.isArray(handler)) {
      return handler.slice();
    }
    return [handler];
  }

  function decorateDayElement(dayElem) {
    if (!dayElem || !dayElem.dateObj) {
      return;
    }
    var dateObj = dayElem.dateObj;
    var jalali = gregorianToJalali(dateObj.getFullYear(), dateObj.getMonth() + 1, dateObj.getDate());
    dayElem.dataset.gregorianValue = formatGregorianString(dateObj, false);
    dayElem.textContent = jalali.day;
    dayElem.title = jalaliMonthNames[jalali.month - 1] + " " + jalali.day + ", " + jalali.year;
  }

  function updateNav(instance) {
    if (!instance || !instance.currentYearElement || !instance.monthNav) {
      return;
    }
    var jalali = gregorianToJalali(instance.currentYear, instance.currentMonth + 1, 1);
    var monthLabel = instance.monthNav.querySelector(".cur-month");
    if (monthLabel) {
      monthLabel.textContent = jalaliMonthNames[jalali.month - 1] || monthLabel.textContent;
    }
    if (instance.currentYearElement.tagName === "INPUT") {
      instance.currentYearElement.value = jalali.year;
    } else {
      instance.currentYearElement.textContent = jalali.year;
    }
  }

  var jalaliSupport = {
    isEnabled: function () {
      return Boolean(bootConfig.enabled);
    },
    isActive: function () {
      return this.isEnabled() && bootConfig.calendar === "jalali";
    },
    allowOverride: function () {
      return Boolean(bootConfig.allow_user_override);
    },
    isJalaliString: isJalaliString,
    toGregorianString: toGregorianString,
    toGregorianDate: toGregorianDate,
    fromGregorian: fromGregorian,
  };

  frappe.jalali_support = jalaliSupport;

  function patchDatetime() {
    if (!frappe.datetime) {
      return;
    }

    var dt = frappe.datetime;
    if (!dt.__jalaliPatched) {
      if (dt.user_to_str) {
        var originalUserToStr = dt.user_to_str.bind(dt);
        dt.user_to_str = function (value, df) {
          if (jalaliSupport.isActive() && typeof value === "string" && jalaliSupport.isJalaliString(value)) {
            try {
              var includeTime = (df && df.fieldtype === "Datetime") || value.indexOf(":") !== -1;
              value = jalaliSupport.toGregorianString(value, includeTime);
            } catch (error) {
              console.warn("Jalali conversion failed", error);
            }
          }
          return originalUserToStr(value, df);
        };
      }

      if (dt.str_to_user) {
        var originalStrToUser = dt.str_to_user.bind(dt);
        dt.str_to_user = function (value, only_time) {
          if (jalaliSupport.isActive() && value) {
            try {
              var includeTime = !only_time && String(value).indexOf(":") !== -1;
              return jalaliSupport.fromGregorian(value, includeTime);
            } catch (error) {
              console.warn("Jalali formatting failed", error);
            }
          }
          return originalStrToUser(value, only_time);
        };
      }

      if (dt.obj_to_user) {
        var originalObjToUser = dt.obj_to_user.bind(dt);
        dt.obj_to_user = function (value, df) {
          if (jalaliSupport.isActive() && value instanceof Date) {
            try {
              var includeTime = df && df.fieldtype === "Datetime";
              return jalaliSupport.fromGregorian(value, includeTime);
            } catch (error) {
              console.warn("Jalali obj_to_user failed", error);
            }
          }
          return originalObjToUser(value, df);
        };
      }

      dt.__jalaliPatched = true;
    }
  }

  function patchFormatters() {
    if (!frappe.formatters) {
      return;
    }

    ["Date", "Datetime", "DateTime"].forEach(function (key) {
      var original = frappe.formatters[key];
      if (!original || original.__jalaliWrapped) {
        return;
      }

      frappe.formatters[key] = function (value, df, doc) {
        if (jalaliSupport.isActive()) {
          try {
            var includeTime = key.toLowerCase() !== "date";
            var formatted = jalaliSupport.fromGregorian(value, includeTime);
            if (formatted) {
              return formatted;
            }
          } catch (error) {
            console.warn("Jalali formatter failed", error);
          }
        }
        return original(value, df, doc);
      };
      frappe.formatters[key].__jalaliWrapped = true;
    });
  }

  function patchControlDate() {
    if (!(frappe.ui && frappe.ui.form && frappe.ui.form.ControlDate)) {
      return;
    }

    var ControlDate = frappe.ui.form.ControlDate;

    if (!ControlDate.__jalaliPatched) {
      if (ControlDate.prototype.format_for_input) {
        var originalFormatForInput = ControlDate.prototype.format_for_input;
        ControlDate.prototype.format_for_input = function (value) {
          if (jalaliSupport.isActive() && value) {
            try {
              var includeTime = this.df.fieldtype === "Datetime";
              return jalaliSupport.fromGregorian(value, includeTime);
            } catch (error) {
              console.warn("Jalali format_for_input failed", error);
            }
          }
          return originalFormatForInput.call(this, value);
        };
      }

      var originalParse = null;
      if (ControlDate.prototype.parse) {
        originalParse = ControlDate.prototype.parse;
      } else if (ControlDate.prototype.get_parsed_value) {
        originalParse = ControlDate.prototype.get_parsed_value;
      }

      if (originalParse) {
        ControlDate.prototype.parse = function (value) {
          if (jalaliSupport.isActive() && typeof value === "string" && jalaliSupport.isJalaliString(value)) {
            try {
              var includeTime = this.df.fieldtype === "Datetime" || value.indexOf(":") !== -1;
              return jalaliSupport.toGregorianString(value, includeTime);
            } catch (error) {
              console.warn("Jalali parse failed", error);
            }
          }
          return originalParse.call(this, value);
        };
      }

      if (ControlDate.prototype.get_value) {
        var originalGetValue = ControlDate.prototype.get_value;
        ControlDate.prototype.get_value = function () {
          var value = originalGetValue.call(this);
          if (jalaliSupport.isActive() && typeof value === "string" && jalaliSupport.isJalaliString(value)) {
            try {
              var includeTime = this.df.fieldtype === "Datetime" || value.indexOf(":") !== -1;
              return jalaliSupport.toGregorianString(value, includeTime);
            } catch (error) {
              console.warn("Jalali get_value failed", error);
            }
          }
          return value;
        };
      }

      if (ControlDate.prototype.get_datepicker_options) {
        var originalGetOptions = ControlDate.prototype.get_datepicker_options;
        ControlDate.prototype.get_datepicker_options = function () {
          var options = originalGetOptions.call(this) || {};
          if (!jalaliSupport.isActive()) {
            return options;
          }

          options.locale = Object.assign({}, options.locale || {}, {
            firstDayOfWeek: 6,
            weekdays: {
              shorthand: jalaliWeekdayShort,
              longhand: jalaliWeekdayLong,
            },
            months: {
              shorthand: jalaliMonthNames,
              longhand: jalaliMonthNames,
            },
          });

          var readyHandlers = toArray(options.onReady);
          readyHandlers.push(function (selectedDates, dateStr, instance) {
            updateNav(instance);
          });
          options.onReady = readyHandlers;

          var monthChangeHandlers = toArray(options.onMonthChange);
          monthChangeHandlers.push(function (selectedDates, dateStr, instance) {
            updateNav(instance);
          });
          options.onMonthChange = monthChangeHandlers;

          var openHandlers = toArray(options.onOpen);
          openHandlers.push(function (selectedDates, dateStr, instance) {
            updateNav(instance);
          });
          options.onOpen = openHandlers;

          var dayCreateHandlers = toArray(options.onDayCreate);
          dayCreateHandlers.push(function (dObj, dStr, instance, dayElem) {
            decorateDayElement(dayElem);
          });
          options.onDayCreate = dayCreateHandlers;

          options.formatDate = function (dateObj, format) {
            var includeTime = /H|h|i|S/.test(format || "");
            return jalaliSupport.fromGregorian(dateObj, includeTime);
          };
          options.parseDate = function (datestr) {
            if (jalaliSupport.isJalaliString(datestr)) {
              return jalaliSupport.toGregorianDate(datestr);
            }
            var parsed = new Date(datestr);
            return isNaN(parsed.getTime()) ? new Date() : parsed;
          };
          options.disableMobile = true;
          return options;
        };
      }

      ControlDate.__jalaliPatched = true;
    }
  }

  function init() {
    if (!jalaliSupport.isActive()) {
      return;
    }
    patchDatetime();
    patchFormatters();
    patchControlDate();
  }

  if (document.readyState === "complete" || document.readyState === "interactive") {
    init();
  } else {
    document.addEventListener("DOMContentLoaded", init);
  }

  if (frappe.realtime && frappe.realtime.on) {
    frappe.realtime.on("workflow:calendar-preference-changed", function (data) {
      if (data && data.calendar && data.calendar !== bootConfig.calendar) {
        bootConfig.calendar = data.calendar;
        init();
      }
    });
  }
})();
