# Third-Party Notices and Acknowledgements

WeChat-Barcode-Scanner is released under the MIT License in the repository
`LICENSE` file.

This project relies on the open-source work listed below. Thank you to all
authors and contributors.

The server source package does not include third-party Python package binaries;
dependencies are installed separately with `pip`. When redistributing a bundle
that includes those dependencies, review and comply with the corresponding
license texts.

## Direct runtime dependencies

| Component | Version | Purpose | License | Source |
| --- | --- | --- | --- | --- |
| PyAutoGUI | 0.9.54 | Keyboard automation | BSD 3-Clause | https://github.com/asweigart/pyautogui |
| PyObjC / Quartz | Latest version compatible with macOS and Python | macOS keyboard events | MIT | https://github.com/ronaldoussoren/pyobjc |
| Segno | 1.6.6 or latest compatible version; optional | QR code generation | BSD 3-Clause | https://github.com/heuer/segno |

## Dependencies installed through PyAutoGUI

PyAutoGUI declares these packages as dependencies. The project does not
directly call most of their user-interface features, but `pip` may install them.

| Component | Purpose | Declared license | Source |
| --- | --- | --- | --- |
| PyScreeze | Screenshot support used by PyAutoGUI | BSD 3-Clause; package metadata also says MIT | https://github.com/asweigart/pyscreeze |
| PyMsgBox | Message boxes | GPLv3+ | https://github.com/asweigart/pymsgbox |
| pytweening | Mouse movement easing | BSD 3-Clause; package metadata also says MIT | https://github.com/asweigart/pytweening |
| MouseInfo | Mouse position utility | GPLv3+ | https://github.com/asweigart/mouseinfo |
| PyGetWindow | Window information | BSD 3-Clause | https://github.com/asweigart/pygetwindow |
| Pyperclip | Clipboard support used by MouseInfo | BSD 3-Clause | https://github.com/asweigart/pyperclip |
| Pillow | Image library required by PyScreeze | HPND | https://github.com/python-pillow/Pillow |

PyMsgBox metadata contains both a `GPLv3+` package declaration and a legacy
Modified BSD section. Until clarified upstream, downstream redistributors
should treat PyMsgBox as GPLv3+ and review its upstream license.

## Python and platform tooling

| Component | Purpose | License | Source |
| --- | --- | --- | --- |
| CPython and Python standard library | Runtime and standard modules | PSF License | https://github.com/python/cpython |
| GitHub Actions Checkout | Repository checkout | MIT | https://github.com/actions/checkout |
| GitHub Actions Setup Python | Python environment setup | MIT | https://github.com/actions/setup-python |
| GitHub Actions Upload Artifact | Build artifact upload | MIT | https://github.com/actions/upload-artifact |
| GitHub Actions Download Artifact | Release artifact download | MIT | https://github.com/actions/download-artifact |
| GitHub CLI | GitHub release creation | MIT | https://github.com/cli/cli |

The project uses WeChat Mini Program platform APIs provided by Tencent. Those
APIs and the WeChat client are not distributed as open-source libraries in this
repository; their use is governed by Tencent's platform terms.

## Included license texts

- [PyAutoGUI BSD license](licenses/PyAutoGUI-BSD.txt)
- [PyScreeze BSD license](licenses/PyScreeze-BSD.txt)
- [pytweening BSD license](licenses/pytweening-BSD.txt)
- [Segno BSD license](licenses/Segno-BSD.txt)
- [Python PSF license](licenses/Python-PSF.txt)

For licenses not reproduced in this directory, use the upstream source links
above and the license files installed with the corresponding Python package.

## Special thanks

Thank you to PyAutoGUI, PyObjC, Segno, PyScreeze, PyMsgBox, pytweening,
MouseInfo, PyGetWindow, Pyperclip, Pillow, CPython, GitHub Actions, GitHub CLI,
and their contributors.
