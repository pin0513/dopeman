# Changelog

All notable changes to DopeMAN will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v2.1.1] - 2026-02-11

### Fixed
- **Dashboard**: Add missing `rescan()` function definition that was causing "rescan is not defined" error
- **API Server**: Correct CORS headers handling in OPTIONS request - move send_cors_headers to proper position

### Changed
- Remove redundant CORS headers calls in GET and POST handlers

## [v2.1.0] - 2026-02-10

### Added
- ✨ WebSocket 任務監控系統
- ✨ 智能快取機制（6 小時）
- ✨ 任務監控頁面（task-monitor.html）
- ✨ 健康檢查功能（health-check.py）
- ✨ 自動修復功能
- ✨ Skills 重載指引（reload-skills.py）

### Changed
- 🔧 優化啟動腳本，整合雙伺服器
- 🔧 修正 WebSocket 訊息格式

### Improved
- 📊 Dashboard 整合任務監控與資訊匯流入口

## [v2.0.0] - 2026-02-09

### Added
- ✨ 完整性檢查功能
- ✨ Symlink 管理功能
- ✨ 跨 AI 平台掃描
- 📦 新增 3 個 subagents

## [v1.0.0] - 2026-02-07

### Added
- 🎉 初始版本發布
- 基礎環境管理功能
- Skills 生命週期管理
- Control Center Dashboard

[v2.1.1]: https://github.com/pin0513/dopeman/compare/v2.1.0...v2.1.1
[v2.1.0]: https://github.com/pin0513/dopeman/compare/v2.0.0...v2.1.0
[v2.0.0]: https://github.com/pin0513/dopeman/compare/v1.0.0...v2.0.0
[v1.0.0]: https://github.com/pin0513/dopeman/releases/tag/v1.0.0
