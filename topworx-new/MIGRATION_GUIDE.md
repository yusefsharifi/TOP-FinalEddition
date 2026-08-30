# MUI → Ant Design Migration Guide

## Current Status
- **MUI imports remaining:** ~219 across ~100+ files
- **Ant Design:** Already used in MainLayout, LoginPage, and new components
- **Goal:** Complete migration to Ant Design only

## Priority Files to Migrate

### High Priority (Core Layout & Navigation)
| File | MUI Components Used |
|------|---------------------|
| `app/components/layout/Sidebar.tsx` | Drawer, List |
| `app/components/common/*.tsx` | Various |

### Medium Priority (Dashboard & Forms)
| File | MUI Components Used |
|------|---------------------|
| `app/components/dashboard/*.tsx` | Grid, Card, Typography |
| `app/components/inventory/*.tsx` | Table, Button, TextField |
| `app/components/hr/*.tsx` | Table, Select, DatePicker |
| `app/components/finance/*.tsx` | Table, Dialog, Snackbar |

### Low Priority (Utility Components)
| File | MUI Components Used |
|------|---------------------|
| `app/components/common/LoadingSpinner.tsx` | CircularProgress |
| `app/components/common/ErrorBoundary.tsx` | Alert |

## Component Mapping (MUI → Ant Design)

| MUI Component | Ant Design Equivalent |
|---------------|----------------------|
| `Button` | `Button` |
| `TextField` | `Input` or `Input.TextArea` |
| `Select` | `Select` |
| `Autocomplete` | `AutoComplete` or `Select` with `showSearch` |
| `Table` | `Table` |
| `Dialog` | `Modal` |
| `Snackbar` | `message` or `notification` |
| `Alert` | `Alert` |
| `Card` | `Card` |
| `Grid` | `Row` + `Col` |
| `Typography` | `Typography.Title`, `Typography.Paragraph` |
| `CircularProgress` | `Spin` |
| `Drawer` | `Drawer` |
| `List` | `List` |
| `Chip` | `Tag` |
| `Badge` | `Badge` |
| `Avatar` | `Avatar` |
| `Tooltip` | `Tooltip` |
| `Tabs` | `Tabs` |
| `Switch` | `Switch` |
| `Checkbox` | `Checkbox` |
| `Radio` | `Radio` |
| `DatePicker` | `DatePicker` |
| `TimePicker` | `TimePicker` |
| `Slider` | `Slider` |
| `LinearProgress` | `Progress` |
| `Accordion` | `Collapse` |
| `Breadcrumbs` | `Breadcrumb` |
| `Menu` | `Menu` |
| `Paper` | `Card` (with no padding) |
| `Box` | `div` with styles |
| `Container` | `div` with max-width |

## Migration Steps

1. **Create a branch** for the migration
2. **Start with low-priority files** (utility components)
3. **Test each component** after migration
4. **Remove MUI imports** from package.json when all files are migrated
5. **Run build** to verify no errors

## Example Migration

### Before (MUI)
```tsx
import { Button, TextField, Alert } from "@mui/material";

const MyComponent = () => (
  <div>
    <Alert severity="info">Info message</Alert>
    <TextField label="Name" variant="outlined" />
    <Button variant="contained" color="primary">Submit</Button>
  </div>
);
```

### After (Ant Design)
```tsx
import { Button, Input, Alert } from "antd";

const MyComponent = () => (
  <div>
    <Alert type="info" message="Info message" />
    <Input placeholder="Name" />
    <Button type="primary">Submit</Button>
  </div>
);
```

## Notes
- Ant Design uses `type` instead of `variant` for button styles
- Ant Design uses `message` prop instead of `children` for Alert
- Ant Design uses `placeholder` instead of `label` for Input
- Ant Design uses `onClick` handler directly on Button (no `onClick` prop needed for basic usage)
