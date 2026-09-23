// Mesmas faixas de National Dex -> geracao do pokedata/generations.py, so'
// que em JS pra filtrar no navegador sem precisar de um backend.
const RANGES = [
  [1, 151, 1], [152, 251, 2], [252, 386, 3], [387, 493, 4], [494, 649, 5],
  [650, 721, 6], [722, 809, 7], [810, 905, 8], [906, 1025, 9],
];

export function generationForId(id) {
  const range = RANGES.find(([start, end]) => id >= start && id <= end);
  return range ? range[2] : null;
}
