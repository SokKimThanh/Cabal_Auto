# Features - Vision System

Tài liệu về Vision System - hệ thống nhận diện hình ảnh và tracking.

## Quick Start
- **[QUICK_START_VISION_WIZARD.md](QUICK_START_VISION_WIZARD.md)** - Hướng dẫn nhanh sử dụng Vision Wizard

## Architecture & Framework
- **[VISION_WIZARD_FRAMEWORK.md](VISION_WIZARD_FRAMEWORK.md)** - Framework và cấu trúc Vision Wizard
- **[../../../architecture/WORKER_THREAD_ARCHITECTURE.md](../../architecture/WORKER_THREAD_ARCHITECTURE.md)** - Worker thread architecture

## Integration
- **[VISION_MENU_INTEGRATION.md](VISION_MENU_INTEGRATION.md)** - Tích hợp Vision menu vào app
- **[VISION_MENU_CHECKLIST.md](VISION_MENU_CHECKLIST.md)** - Checklist integration

## Related Documentation
- [Sprint 22 Documentation](../../sprints/sprint22/) - Implementation details
- [Architecture](../../architecture/) - System architecture
- [Examples](../../sprints/sprint22/examples/) - Code examples

## Key Concepts

### Vision Wizard
- Giao diện quản lý vision system
- Singleton pattern (1 instance duy nhất)
- Topmost window (luôn trên cùng)
- Real-time CV detection & tracking

### Worker Thread Architecture
- Non-blocking UI updates
- Queue-based communication
- FPS throttling (15 FPS max)
- Clean shutdown mechanism

### Template Management
- Multi-template support
- Per-template thresholds
- Multi-scale detection
- Region of Interest (ROI) support
