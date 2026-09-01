const SAGE_LOGO = "https://customer-assets-gfyr7b9c.emergentagent.net/job_sage-mega-fest/artifacts/0yfnekpb_logotechweek.png";
const EUPHORIA_LOGO = "https://customer-assets-gfyr7b9c.emergentagent.net/job_sage-mega-fest/artifacts/vevgaaxu_euphorialogo.png";

interface BrandLockupProps {
  variant?: "header" | "hero" | "footer" | "compact";
}

export default function BrandLockup({ variant = "header" }: BrandLockupProps) {
  return (
    <span className={`brand-lockup brand-lockup--${variant}`} data-testid={`brand-lockup-${variant}`}>
      <img src={SAGE_LOGO} alt="SAGE University Indore" className="brand-sage" />
      <span className="brand-divider" aria-hidden="true" />
      <img src={EUPHORIA_LOGO} alt="EUPHORIA — Joy of Colours" className="brand-euphoria" />
    </span>
  );
}