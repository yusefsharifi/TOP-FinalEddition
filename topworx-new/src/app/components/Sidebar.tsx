import React, { useState } from "react";
import { List } from 'antd';
import { Link, useLocation } from "react-router-dom";
import { modules, ModuleItem } from "../navigation/modules";
import { useUserRole } from "../../core/auth/useUserRole";
import { UpOutlined } from '@ant-design/icons';
import { DownOutlined } from '@ant-design/icons';

const SidebarItem: React.FC<{ mod: ModuleItem; level?: number }> = ({ mod, level = 0 }) => {
  const location = useLocation();
  const [open, setOpen] = useState(false);

  const Icon = MuiIcons[mod.icon as keyof typeof MuiIcons] || MuiIcons["Apps"];
  const hasChildren = !!mod.children && mod.children.length > 0;
  const isActive = location.pathname.startsWith(mod.path);

  return (
    <>
      <ListItemButton
        component={mod.path ? Link : "div"}
        to={mod.path || ""}
        selected={isActive}
        style={{  pl: 2 + level * 2  }}
        onClick={() => hasChildren && setOpen((prev) => !prev)}
      >
        <ListItemIcon>
          <Icon />
        </span>
        <ListItemText primary={mod.label} />
        {hasChildren && (open ? <ExpandLess /> : <ExpandMore />)}
      </div>
      {hasChildren && (
        <Collapse in={open} timeout="auto" unmountOnExit>
          <List component="div" disablePadding>
            {mod.children!.map((child) => (
              <SidebarItem key={child.path} mod={child} level={level + 1} />
            ))}
          </List>
        </div>
      )}
    </>
  );
};

export const Sidebar: React.FC = () => {
  const role = useUserRole();

  // فیلتر ماژول‌ها و زیرماژول‌ها بر اساس نقش کاربر
  const filterModules = (mods: ModuleItem[]): ModuleItem[] =>
    mods
      .filter((mod) => mod.roles.includes(role))
      .map((mod) =>
        mod.children
          ? { ...mod, children: filterModules(mod.children) }
          : mod
      );

  const filteredModules = filterModules(modules);

  return (
    <List>
      {filteredModules.map((mod) => (
        <SidebarItem key={mod.path} mod={mod} />
      ))}
    </List>
  );
};