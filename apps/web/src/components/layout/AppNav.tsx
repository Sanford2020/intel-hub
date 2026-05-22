"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Menu, Moon, Sun, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { useThemeStore } from "@/stores/theme";

interface NavItem {
  href: string;
  label: string;
  group: "intel" | "analysis" | "ops";
}

const navItems: NavItem[] = [
  { href: "/briefing", label: "今日简报", group: "intel" },
  { href: "/articles", label: "资讯库", group: "intel" },
  { href: "/trends", label: "趋势分析", group: "analysis" },
  { href: "/archives", label: "归档", group: "analysis" },
  { href: "/sources", label: "来源运营", group: "ops" },
  { href: "/alerts", label: "告警规则", group: "ops" },
];

function isActive(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(href + "/");
}

export function AppNav() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const { isDark, toggle } = useThemeStore();

  return (
    <>
      <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/80 backdrop-blur-sm dark:border-slate-800 dark:bg-slate-950/80">
        <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-6">
            <Link href="/" className="flex items-center gap-2.5">
              <div className="flex h-7 w-7 items-center justify-center rounded-md bg-primary-600 text-xs font-bold text-white">
                I
              </div>
              <span className="text-base font-semibold text-slate-900 dark:text-white">
                Intel Hub
              </span>
            </Link>

            <nav className="hidden items-center gap-0.5 md:flex">
              <Link
                href="/"
                className={cn(
                  "rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
                  pathname === "/"
                    ? "bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-white"
                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-white",
                )}
              >
                工作台
              </Link>
              <NavDivider />
              {navItems
                .filter((i) => i.group === "intel")
                .map((item) => (
                  <NavLink key={item.href} item={item} pathname={pathname} />
                ))}
              <NavDivider />
              {navItems
                .filter((i) => i.group === "analysis")
                .map((item) => (
                  <NavLink key={item.href} item={item} pathname={pathname} />
                ))}
              <NavDivider />
              {navItems
                .filter((i) => i.group === "ops")
                .map((item) => (
                  <NavLink key={item.href} item={item} pathname={pathname} />
                ))}
            </nav>
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={toggle}
              className="icon-action"
              aria-label={isDark ? "切换亮色模式" : "切换暗色模式"}
            >
              {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>
            <button
              onClick={() => setMobileOpen(true)}
              className="icon-action md:hidden"
              aria-label="打开菜单"
            >
              <Menu className="h-4 w-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-[60] md:hidden">
          <div
            className="absolute inset-0 bg-slate-950/40"
            onClick={() => setMobileOpen(false)}
          />
          <aside className="absolute right-0 top-0 flex h-full w-64 flex-col bg-white dark:bg-slate-900">
            <div className="flex h-14 items-center justify-between border-b border-slate-200 px-4 dark:border-slate-800">
              <span className="text-sm font-semibold text-slate-900 dark:text-white">
                导航
              </span>
              <button
                onClick={() => setMobileOpen(false)}
                className="icon-action"
                aria-label="关闭菜单"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <nav className="flex-1 overflow-y-auto px-3 py-4">
              <MobileLink href="/" label="工作台" pathname={pathname} onClose={() => setMobileOpen(false)} />
              <MobileGroupLabel label="情报" />
              {navItems.filter((i) => i.group === "intel").map((item) => (
                <MobileLink key={item.href} href={item.href} label={item.label} pathname={pathname} onClose={() => setMobileOpen(false)} />
              ))}
              <MobileGroupLabel label="分析" />
              {navItems.filter((i) => i.group === "analysis").map((item) => (
                <MobileLink key={item.href} href={item.href} label={item.label} pathname={pathname} onClose={() => setMobileOpen(false)} />
              ))}
              <MobileGroupLabel label="运营" />
              {navItems.filter((i) => i.group === "ops").map((item) => (
                <MobileLink key={item.href} href={item.href} label={item.label} pathname={pathname} onClose={() => setMobileOpen(false)} />
              ))}
            </nav>
          </aside>
        </div>
      )}
    </>
  );
}

function NavLink({ item, pathname }: { item: NavItem; pathname: string }) {
  return (
    <Link
      href={item.href}
      className={cn(
        "rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
        isActive(pathname, item.href)
          ? "bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-white"
          : "text-slate-600 hover:bg-slate-50 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-white",
      )}
    >
      {item.label}
    </Link>
  );
}

function NavDivider() {
  return <div className="mx-1 h-4 w-px bg-slate-200 dark:bg-slate-700" />;
}

function MobileGroupLabel({ label }: { label: string }) {
  return (
    <div className="mb-1 mt-4 px-3 text-[10px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
      {label}
    </div>
  );
}

function MobileLink({
  href,
  label,
  pathname,
  onClose,
}: {
  href: string;
  label: string;
  pathname: string;
  onClose: () => void;
}) {
  return (
    <Link
      href={href}
      onClick={onClose}
      className={cn(
        "block rounded-md px-3 py-2 text-sm font-medium transition-colors",
        isActive(pathname, href)
          ? "bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-white"
          : "text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800",
      )}
    >
      {label}
    </Link>
  );
}
