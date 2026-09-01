import { Link } from "react-router-dom";
import BrandLockup from "@/components/BrandLockup";

export default function SiteHeader() {
  return (
    <header className="site-header" data-testid="site-header">
      <Link to="/" className="site-brand" data-testid="brand-home-link"><BrandLockup /></Link>
      <nav className="site-nav" data-testid="main-navigation">
        <a href="/#events" data-testid="nav-events-link">Events</a>
        <a href="/#categories" data-testid="nav-categories-link">Categories</a>
        <Link to="/admin" data-testid="nav-admin-link">Admin</Link>
      </nav>
      <Link to="/registration" className="button button-yellow header-register" data-testid="nav-register-link">Register <span>↗</span></Link>
    </header>
  );
}