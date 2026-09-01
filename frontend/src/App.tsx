import { Routes, Route } from "react-router-dom";
import Home from "@/pages/Home";
import Registration from "@/pages/Registration";
import RegistrationSuccess from "@/pages/RegistrationSuccess";
import AdminPreview from "@/pages/AdminPreview";
import ScannerPreview from "@/pages/ScannerPreview";

// One <Route> per page in src/pages; BrowserRouter already wraps this in main.tsx.
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/registration" element={<Registration />} />
      <Route path="/registration/:eventSlug" element={<Registration />} />
      <Route path="/registration/success/:registrationId" element={<RegistrationSuccess />} />
      <Route path="/admin" element={<AdminPreview />} />
      <Route path="/scanner" element={<ScannerPreview />} />
    </Routes>
  );
}
