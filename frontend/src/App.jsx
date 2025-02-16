import { createMemoryRouter, Navigate, RouterProvider } from "react-router-dom";

import Loading from "./pages/Loading";
import Login from "./pages/Login";

function App() {
  const router = createMemoryRouter([
    { path: "/", element: <Navigate to="/loading" /> },
    { path: "/loading", element: <Loading /> },
    { path: "/login", element: <Login /> },
  ]);

  return (
    <div className="font-mono">
      <RouterProvider router={router} />
    </div>
  );
}

export default App;
