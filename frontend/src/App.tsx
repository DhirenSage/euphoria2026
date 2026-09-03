import { Routes, Route } from "react-router-dom";
import Home from "@/pages/Home";
import Registration from "@/pages/Registration";
import RegistrationSuccess from "@/pages/RegistrationSuccess";
import AdminPreview from "@/pages/AdminPreview";
import ScannerPreview from "@/pages/ScannerPreview";
import Events from "@/pages/Events";
import EventDetail from "@/pages/EventDetail";
import PortalLogin from "@/pages/PortalLogin";
import EventPass from "@/pages/EventPass";
import Gallery from "@/pages/Gallery";

// One <Route> per page in src/pages; BrowserRouter already wraps this in main.tsx.
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/events" element={<Events />} />
      <Route path="/events/:eventSlug" element={<EventDetail />} />
      <Route path="/gallery" element={<Gallery />} />
      <Route path="/registration" element={<Registration />} />
      <Route path="/registration/:eventSlug" element={<Registration />} />
      <Route path="/registration/success/:registrationId" element={<RegistrationSuccess />} />
      <Route path="/pass/:registrationId" element={<EventPass />} />
      <Route path="/admin/login" element={<PortalLogin portal="admin" />} />
      <Route path="/admin" element={<AdminPreview />} />
      <Route path="/scanner/login" element={<PortalLogin portal="scanner" />} />
      <Route path="/scanner" element={<ScannerPreview />} />
    </Routes>
  );
}
