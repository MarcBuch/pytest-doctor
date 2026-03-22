# 1.0.0 (2026-03-22)


### Bug Fixes

* remove unused imports ([3d273d9](https://github.com/MarcBuch/pytest-doctor/commit/3d273d9849a14e0bcf2d94648986e6490e7b0101))
* resolve mypy type checking errors ([8de55aa](https://github.com/MarcBuch/pytest-doctor/commit/8de55aa71825ecad485729180add9edebad71ec0))


### Features

* **agent:** Add --fix flag with agent-friendly output and deeplinks ([39c2a20](https://github.com/MarcBuch/pytest-doctor/commit/39c2a200cbeba856daab7525d081a939b1d84bc5))
* **aggregation:** Implement results aggregation with deduplication and prioritization ([d5d7bef](https://github.com/MarcBuch/pytest-doctor/commit/d5d7befe315e5b45a07e01f2438ab8f8d2adef8c))
* **analyzers:** Add coverage gap analysis engine ([0aa3b52](https://github.com/MarcBuch/pytest-doctor/commit/0aa3b52731af0a894cbcea40eae6da430977fa5c))
* **analyzers:** Implement analysis pipeline skeleton with all analyzer modules ([a39d1fa](https://github.com/MarcBuch/pytest-doctor/commit/a39d1fa05f709dfdb1c459b2f6860b805d18443e))
* **analyzers:** Implement Ruff linting integration ([31c5e95](https://github.com/MarcBuch/pytest-doctor/commit/31c5e9548b6a0e98fb4ca1f33411a66ca8c4a957))
* **analyzers:** Implement test quality analysis engine ([f23bfdc](https://github.com/MarcBuch/pytest-doctor/commit/f23bfdcfd1303facc716b1e2b8f8e9450a7d45e4))
* **analyzers:** Implement Vulture dead code detection integration ([649389d](https://github.com/MarcBuch/pytest-doctor/commit/649389da8be1fc7d7104d8b286a1377485dcd5fa))
* **cli:** Auto-generate diagnostics.json with deeplinks for --fix flag ([ee03f55](https://github.com/MarcBuch/pytest-doctor/commit/ee03f557954b2960af60005420dfb95fb3a1297c))
* **cli:** Implement --diff flag for incremental scanning ([488be2c](https://github.com/MarcBuch/pytest-doctor/commit/488be2ce358d329caaad8a66318a7d708440d858))
* **cli:** Implement CLI command surface skeleton with full argument parsing ([d3e7fd5](https://github.com/MarcBuch/pytest-doctor/commit/d3e7fd5b90e778f14c821dd9a7edb6fbc6672a91))
* **cli:** Integrate analysis engines with aggregation and output formatting ([151e042](https://github.com/MarcBuch/pytest-doctor/commit/151e042023671c3c200efbe8b795f9ef8d9b7e98))
* **config:** Add configuration loading and validation skeleton ([dfeb943](https://github.com/MarcBuch/pytest-doctor/commit/dfeb943a0576e7d743a9bb33435ab6f212be5981))
* **config:** Add default ignore patterns for common directories ([ce4f04c](https://github.com/MarcBuch/pytest-doctor/commit/ce4f04c9ad9ca5d7d0c38173d23d730bc000103c))
* **config:** Implement configuration system with file and CLI flag support ([7cc99a4](https://github.com/MarcBuch/pytest-doctor/commit/7cc99a49eb933c6ee686cd86fbf05e09d958bb19))
* **git_utils:** Add git integration for diff-based filtering ([78fa5a7](https://github.com/MarcBuch/pytest-doctor/commit/78fa5a70d5e97a9c1f44ae746ce02f039af700b7))
* **models:** Define core data contracts and result models ([7fb57fd](https://github.com/MarcBuch/pytest-doctor/commit/7fb57fd81b8b54a73e53c01013c293447b15db43))
* **parallel:** Implement parallel analysis execution for performance ([424b9bf](https://github.com/MarcBuch/pytest-doctor/commit/424b9bfb768df2d74b7f06b95ec40d84d7e50b0a))
* **scoring:** Implement health score calculation system ([3808b33](https://github.com/MarcBuch/pytest-doctor/commit/3808b3338c0622a9e660de25dae1c34a47076a79))
* **T1:** Initialize uv-based Python project scaffold ([2195e63](https://github.com/MarcBuch/pytest-doctor/commit/2195e63aa797a7a115da8c18253847f2098e4c94))
* **tooling:** Initialize Python project with uv package manager ([e8182ea](https://github.com/MarcBuch/pytest-doctor/commit/e8182eaf9218ae91de7b171b140e01a652d9bcfb))
