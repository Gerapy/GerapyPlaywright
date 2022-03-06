# Gerapy Playwright Changelog

## 0.2.4 (2022-03-06)

- Fix bug: https://github.com/Gerapy/GerapyPlaywright/pull/8

## 0.2.3 (2022-01-12)

- Fix bug: https://github.com/Gerapy/GerapyPlaywright/issues/3

## 0.2.2 (2021-12-29)

- Change default to disable Check of Playwright Installation

## 0.2.1 (2021-12-29)

- Add switch for disabling Check of Playwright Installation

## 0.2.0 (2021-12-28)

- New Feature: Add support for:
  - Specifying `channel` for launching
  - Specifying `executablePath` for launching
  - Specifying `slowMo` for launching
  - Specifying `devtools` for launching
  - Specifying `--disable-extensions` in args for launching
  - Specifying `--hide-scrollbars` in args for launching
  - Specifying `--no-sandbox` in args for launching
  - Specifying `--disable-setuid-sandbox` in args for launching
  - Specifying `--disable-gpu` in args for launching
- Update: change `GERAPY_PLAYWRIGHT_SLEEP` default to 0

## 0.1.2 (2021-12-28)

- Fix: Add retrying logic for PlaywrightError

## 0.1.1 (2021-12-27)

- First version of Playwright, add basic support for:
  - Proxy
  - Auto Installation
  - Setting Cookies
  - Screenshot
  - Evaluating Script
  - Wait for Elements
  - Wait loading control
  - Setting Timeout
  - Pretending Webdriver
