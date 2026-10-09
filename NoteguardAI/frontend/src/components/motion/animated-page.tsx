"use client";

import React, { useEffect, useState } from "react";

export interface AnimatedPageProps {
  children: React.ReactNode;
  className?: string;
}

export const AnimatedPage: React.FC<AnimatedPageProps> = ({ children, className = "" }) => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div
      className={`transition-all duration-300 ease-out ${
        mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2"
      } ${className}`}
    >
      {children}
    </div>
  );
};
