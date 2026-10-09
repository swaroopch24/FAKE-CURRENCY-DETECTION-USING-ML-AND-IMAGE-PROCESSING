/**
 * Utility helper to join class names safely.
 * Simulates standard tailwind-merge and clsx combinations.
 */
export function cn(...inputs: any[]) {
  return inputs
    .flat()
    .filter(item => typeof item === "string" && item.trim() !== "")
    .join(" ");
}
