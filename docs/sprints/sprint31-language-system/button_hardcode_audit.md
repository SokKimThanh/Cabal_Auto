# Hardcoded Button Text Audit Report

This report lists all hardcoded `text` strings in UI button creations for review before migrating to `text_key`.

## P1 - User Visible

- **File**: `ui/components/demo_icon_button.py`
  - **Line**: 1
  - **Text**: `"Refresh"`
  - **Suggested**: `text_key="btn.refresh"`

## P2 - Label/Action

- **File**: `ui/components/icon_button.py`
  - **Line**: 1
  - **Text**: `"Add Item"`
  - **Suggested**: `text_key="btn.add_item"`

- **File**: `ui/components/icon_button.py`
  - **Line**: 1
  - **Text**: `"Save All"`
  - **Suggested**: `text_key="btn.save_all"`

- **File**: `ui/components/icon_button.py`
  - **Line**: 1
  - **Text**: `"?"`
  - **Suggested**: `text_key="btn.?"`

- **File**: `ui/components/icon_button.py`
  - **Line**: 1
  - **Text**: `"Monster Name:"`
  - **Suggested**: `text_key="btn.monster_name:"`

- **File**: `ui/components/demo_icon_button.py`
  - **Line**: 1
  - **Text**: `"Green Light"`
  - **Suggested**: `text_key="btn.green_light"`

- **File**: `ui/components/demo_icon_button.py`
  - **Line**: 1
  - **Text**: `"Red"`
  - **Suggested**: `text_key="btn.red"`

- **File**: `ui/components/demo_icon_button.py`
  - **Line**: 1
  - **Text**: `"Blue"`
  - **Suggested**: `text_key="btn.blue"`

- **File**: `ui/components/demo_icon_button.py`
  - **Line**: 1
  - **Text**: `"Orange"`
  - **Suggested**: `text_key="btn.orange"`

- **File**: `ui/components/demo_icon_button.py`
  - **Line**: 1
  - **Text**: `"Compact"`
  - **Suggested**: `text_key="btn.compact"`

- **File**: `ui/components/demo_icon_button.py`
  - **Line**: 1
  - **Text**: `"Small"`
  - **Suggested**: `text_key="btn.small"`

- **File**: `ui/components/demo_icon_button.py`
  - **Line**: 1
  - **Text**: `"Medium"`
  - **Suggested**: `text_key="btn.medium"`

- **File**: `ui/components/demo_icon_button.py`
  - **Line**: 1
  - **Text**: `"Large"`
  - **Suggested**: `text_key="btn.large"`

- **File**: `ui/components/demo_icon_button.py`
  - **Line**: 1
  - **Text**: `"Text Button"`
  - **Suggested**: `text_key="btn.text_button"`

- **File**: `ui/components/demo_icon_button.py`
  - **Line**: 1
  - **Text**: `"Normal"`
  - **Suggested**: `text_key="btn.normal"`

- **File**: `ui/components/demo_icon_button.py`
  - **Line**: 1
  - **Text**: `"Highlight"`
  - **Suggested**: `text_key="btn.highlight"`

- **File**: `ui/components/demo_icon_button.py`
  - **Line**: 1
  - **Text**: `"Danger"`
  - **Suggested**: `text_key="btn.danger"`

- **File**: `ui/components/demo_icon_button.py`
  - **Line**: 1
  - **Text**: `"Disabled"`
  - **Suggested**: `text_key="btn.disabled"`

- **File**: `ui/components/demo_icon_button.py`
  - **Line**: 1
  - **Text**: `"Add item"`
  - **Suggested**: `text_key="btn.add_item"`

- **File**: `ui/components/demo_icon_button.py`
  - **Line**: 1
  - **Text**: `"Delete item"`
  - **Suggested**: `text_key="btn.delete_item"`

- **File**: `ui/components/demo_icon_button.py`
  - **Line**: 1
  - **Text**: `"Edit item"`
  - **Suggested**: `text_key="btn.edit_item"`

- **File**: `ui/components/demo_icon_button.py`
  - **Line**: 1
  - **Text**: `"Refresh list"`
  - **Suggested**: `text_key="btn.refresh_list"`

- **File**: `ui/components/demo_icon_button.py`
  - **Line**: 1
  - **Text**: `"Settings"`
  - **Suggested**: `text_key="btn.settings"`

- **File**: `ui/components/demo_icon_button.py`
  - **Line**: 1
  - **Text**: `"Search"`
  - **Suggested**: `text_key="btn.search"`

- **File**: `ui/components/demo_icon_button.py`
  - **Line**: 1
  - **Text**: `"Hover Me"`
  - **Suggested**: `text_key="btn.hover_me"`

- **File**: `ui/components/demo_icon_button.py`
  - **Line**: 1
  - **Text**: `"Focus Me"`
  - **Suggested**: `text_key="btn.focus_me"`

- **File**: `ui/components/demo_icon_button.py`
  - **Line**: 1
  - **Text**: `"Custom Width"`
  - **Suggested**: `text_key="btn.custom_width"`

- **File**: `ui/components/demo_icon_button.py`
  - **Line**: 1
  - **Text**: `"Custom Padding"`
  - **Suggested**: `text_key="btn.custom_padding"`

- **File**: `ui/components/demo_icon_button.py`
  - **Line**: 1
  - **Text**: `"Custom Font"`
  - **Suggested**: `text_key="btn.custom_font"`

- **File**: `ui/components/confirmation_widget.py`
  - **Line**: 1
  - **Text**: `"✓"`
  - **Suggested**: `text_key="btn.✓"`

- **File**: `ui/windows/monster_manager_win.py`
  - **Line**: 1
  - **Text**: `"#0D47A1"`
  - **Suggested**: `text_key="btn.#0d47a1"`

- **File**: `ui/windows/monster_manager_win.py`
  - **Line**: 2
  - **Text**: `"Capture"`
  - **Suggested**: `text_key="btn.capture"`

- **File**: `ui/windows/monster_manager_win.py`
  - **Line**: 2
  - **Text**: `"Browse"`
  - **Suggested**: `text_key="btn.browse"`

- **File**: `ui/windows/monster_manager_win.py`
  - **Line**: 2
  - **Text**: `"◀"`
  - **Suggested**: `text_key="btn.◀"`

- **File**: `ui/windows/monster_manager_win.py`
  - **Line**: 2
  - **Text**: `"Go"`
  - **Suggested**: `text_key="btn.go"`

- **File**: `ui/windows/monster_manager_win.py`
  - **Line**: 2
  - **Text**: `"▶"`
  - **Suggested**: `text_key="btn.▶"`

- **File**: `ui/panels/monster_target_panel.py`
  - **Line**: 1
  - **Text**: `"➕"`
  - **Suggested**: `text_key="btn.➕"`

## P3 - Internal/Debug

- **File**: `ui/windows/monster_manager_win.py`
  - **Line**: 2
  - **Text**: `"Test"`
  - **Suggested**: `text_key="btn.test"`
