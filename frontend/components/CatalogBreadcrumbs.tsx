"use client";

import Link from "next/link";

type BreadcrumbItem = {
  label: string;
  href?: string;
};

interface CatalogBreadcrumbsProps {
  items: BreadcrumbItem[];
  className?: string;
}

export default function CatalogBreadcrumbs({
  items,
  className = "",
}: CatalogBreadcrumbsProps) {
  return (
    <nav
      aria-label="Breadcrumb"
      className={`flex flex-wrap items-center gap-2 text-xs font-medium ${className}`.trim()}
    >
      {items.map((item, index) => {
        const isLast = index === items.length - 1;

        return (
          <span key={`${item.label}-${index}`} className="flex items-center gap-2">
            {item.href && !isLast ? (
              <Link
                href={item.href}
                className="transition-colors hover:text-orange-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-orange-400/60"
              >
                {item.label}
              </Link>
            ) : (
              <span className={isLast ? "text-current" : ""}>{item.label}</span>
            )}
            {!isLast && <span aria-hidden="true">/</span>}
          </span>
        );
      })}
    </nav>
  );
}
