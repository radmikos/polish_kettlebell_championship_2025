import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { useEffect } from "react";
import Layout from "./components/Layout";
import HomePage from "./pages/HomePage";
import Results2025Page from "./pages/Results2025Page";
import CategoryPage from "./pages/CategoryPage";
import LivePage from "./pages/LivePage";
import StartListsPage from "./pages/StartListsPage";
import StartListCategoryPage from "./pages/StartListCategoryPage";
import ContactPage from "./pages/ContactPage";

const APP_TITLE = "Mistrzostwa Polski Kettlebell 2026 · Wyniki Live";

function App() {
  useEffect(() => {
    document.title = APP_TITLE;
  }, []);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="results-2025" element={<Results2025Page />} />  
          <Route path="category/:categoryId" element={<CategoryPage />} />
          <Route path="live" element={<LivePage />} />
          <Route path="start-lists" element={<StartListsPage />}>
            <Route path=":slug" element={<StartListCategoryPage />} />
          </Route>
          <Route path="contact" element={<ContactPage />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;