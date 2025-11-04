---
trigger: manual
---

## ⚙️ Estructura general del proyecto

1. **Usa una estructura modular y limpia:**

   ```
   src/
   ├── components/
   │   ├── board/
   │   │   ├── Board.tsx
   │   │   ├── Cell.tsx
   │   │   └── styles.css
   │   ├── ships/
   │   │   ├── Ship.tsx
   │   │   └── ShipSelector.tsx
   │   ├── ui/
   │   │   ├── Button.tsx
   │   │   ├── Modal.tsx
   │   │   └── Loader.tsx
   ├── hooks/
   ├── context/
   ├── pages/
   ├── utils/
   ├── types/
   ├── services/
   ├── App.tsx
   └── main.tsx
   ```

2. **Divide el código por dominio, no por tipo de archivo.**
   Ejemplo: `board/Board.tsx` y `board/Cell.tsx`, en vez de `components/atoms`, `components/molecules`, etc.

3. **Usa TypeScript.**
   React con TS = menos bugs, más mantenible. Declara tipos para estado, props y eventos del tablero.

---

## ⚛️ Reglas de React

1. **Usa componentes funcionales con Hooks.**
   Evita `class components`.
   Ejemplo:

   ```tsx
   function Board({ grid }: BoardProps) {
     const [selectedCell, setSelectedCell] = useState<Cell | null>(null);
     ...
   }
   ```

2. **Crea hooks personalizados** para manejar lógica compleja (turnos, disparos, posiciones, IA, etc.).
   Ejemplo:

   ```tsx
   const useBattleshipGame = () => {
     const [playerBoard, setPlayerBoard] = useState(createEmptyBoard());
     const [enemyBoard, setEnemyBoard] = useState(createEmptyBoard());
     ...
   };
   ```

3. **Nunca mezcles lógica y presentación.**

   * Lógica → hooks (`useGameLogic`, `useAI`, etc.)
   * UI → componentes (`Board`, `Ship`, `Cell`, `ScorePanel`)

4. **Evita estados innecesarios.**
   No dupliques datos que se pueden derivar (por ejemplo, el número de barcos restantes).

5. **Usa Context API o Zustand/Recoil para estado global**, no `prop drilling`.

   * Ideal para mantener el estado del juego, turnos, y puntuaciones.

---

## 🚀 Reglas de Vite y Build

1. **Configura alias en `vite.config.ts`** para imports limpios:

   ```ts
   resolve: {
     alias: {
       "@": "/src",
     },
   }
   ```

   Luego:

   ```tsx
   import { Board } from "@/components/board/Board";
   ```

2. **Usa lazy loading para vistas o componentes pesados.**

   ```tsx
   const GamePage = lazy(() => import("@/pages/GamePage"));
   ```

3. **Optimiza assets**:

   * Usa imágenes en formato `.webp` o `.svg`.
   * Importa sonidos con `?url` y precárgalos si es necesario.

4. **Configura ESLint + Prettier + TypeScript strict mode.**

---

## 🎮 Reglas específicas para el juego de Batalla Naval

1. **Mantén la lógica del tablero pura.**
   Las funciones para colocar barcos, verificar impactos y hundimientos deben ser independientes de React (en `/utils/gameLogic.ts`).

2. **Evita hardcodear posiciones.**
   Usa configuraciones dinámicas para tamaño del tablero, número de barcos, etc.

3. **Desacopla la interfaz del motor del juego.**
   Podrías exportar una API tipo:

   ```ts
   game.placeShip({ x: 2, y: 3, size: 4, orientation: "horizontal" });
   game.shoot({ x: 5, y: 2 });
   game.isGameOver();
   ```

4. **Crea una máquina de estados** para controlar fases:

   * Colocación de barcos
   * Turno del jugador
   * Turno de la IA
   * Fin del juego

   Ejemplo simple:

   ```ts
   enum GamePhase {
     Placing,
     PlayerTurn,
     EnemyTurn,
     GameOver
   }
   ```

5. **Para la IA**, usa un hook (`useAI`) con heurísticas o patrones predefinidos (por ejemplo, disparar cerca de un impacto confirmado).

---

## 🎨 Reglas de diseño y UX

1. **Usa Tailwind o CSS Modules.**
2. **Agrega animaciones pequeñas (Framer Motion o CSS transitions).**
3. **Proporciona feedback inmediato:**

   * Efecto visual al disparar o al recibir impacto.
   * Sonido distinto para agua / impacto / hundimiento.
4. **No bloquees la UI:** usa loaders o deshabilita botones mientras espera la IA.

---

## 🧪 Reglas de pruebas

1. **Prueba la lógica del juego con Jest o Vitest.**

   * `utils/gameLogic.test.ts` → colocar barcos, validar disparos, detectar fin del juego.

2. **Prueba componentes clave con React Testing Library.**

   * Simula clicks, render de tablero, mensajes de victoria, etc.

3. **Asegura el 80%+ de cobertura en lógica crítica.**

---

## 📦 Otras buenas prácticas

* Usa **.env** para configurar el backend o endpoints.
* Usa un **hook `useSound`** para controlar efectos.
* Documenta cada componente con un pequeño bloque de descripción.
* Haz **commits pequeños y significativos**, siguiendo Convenciones tipo:

  * `feat: add ship placement logic`
  * `fix: correct hit detection`
  * `refactor: extract AI logic`