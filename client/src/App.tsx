import { BrowserRouter, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/Index";
import ResultPage from "./pages/ResultPage";

const App = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/result" element={<ResultPage />} />
    </Routes>
  </BrowserRouter>
);

export default App;
