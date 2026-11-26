import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Solo cambia la presentación; el título almacenado conserva su valor original.
export function tituloVisible(titulo: string): string {
  return titulo.replace(/^\[demo\]\s*/i, "");
}
