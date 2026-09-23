// Alterna claro/escuro e lembra a escolha em localStorage; sem storage
// disponivel (aba anonima, storage bloqueado), so' o toggle manual some da
// memoria entre visitas -- o tema ainda funciona via prefers-color-scheme.
const STORAGE_KEY = "pokedata-theme";

function currentTheme() {
  const attr = document.documentElement.getAttribute("data-theme");
  if (attr) return attr;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export function initTheme() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) document.documentElement.setAttribute("data-theme", saved);
  } catch {
    // storage indisponivel, segue so' com prefers-color-scheme
  }

  const toggle = document.getElementById("theme-toggle");
  toggle.addEventListener("click", () => {
    const next = currentTheme() === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch {
      // segue sem lembrar a escolha
    }
  });
}
