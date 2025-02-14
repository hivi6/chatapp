import { useState } from "react";
import { FaBeer } from "react-icons/fa";

function App() {
  const [count, setCount] = useState(0);

  return (
    <>
      <div className="h-screen flex items-center justify-center">
        <button
          onClick={() => setCount((count) => count + 1)}
          className="text-red-900 border-red-900 border-2 text-9xl flex items-center justify-center"
        >
          <FaBeer />
          <div>count is {count}</div>
        </button>
      </div>
    </>
  );
}

export default App;
