import type { NavigateOptions } from "react-router-dom";

import { HeroUIProvider } from "@heroui/system";
import { useHref, useNavigate } from "react-router-dom";
import { useTheme } from "./context/ThemeContext";

declare module "@react-types/shared" {
  interface RouterConfig {
    routerOptions: NavigateOptions;
  }
}

export function Provider({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();

  const { isDarkMode } = useTheme();

  return (
    <HeroUIProvider navigate={navigate} useHref={useHref} className={`${isDarkMode ? 'dark' : ''}`}>
      {children}
    </HeroUIProvider>
  );
}
