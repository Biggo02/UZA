"use client";

import Link from "next/link";
import { useState } from "react";

export default function UzaHeader({ authenticated = false, name = "", avatarUrl = null }: { authenticated?: boolean; name?: string; avatarUrl?: string | null }) {
  const [open, setOpen] = useState(false);
  const initials = name ? name.split(" ").map((x) => x[0]).join("").slice(0, 2).toUpperCase() : "U";
  const links = [["Accueil", "/"], ["Annonces", "/annonces"], ["Catégories", "/categories"], ["Comment ça marche", "/comment-ca-marche"], ["À propos", "/a-propos"], ["Nos locaux", "/nos-locaux"]];
  return <header className="uza-header"><div className="uza-header-inner"><Link className="uza-logo" href="/">UZA</Link><nav className="uza-nav">{links.map(([label, href]) => <Link key={href} href={href}>{label}</Link>)}</nav><div className="uza-actions">{authenticated ? <Link className="uza-profile" href="/profil">{name && <span>{name}</span>}{avatarUrl ? <img className="uza-avatar" src={avatarUrl} alt="" /> : <span className="uza-avatar">{initials}</span>}</Link> : <><Link className="uza-btn" href="/connexion">Se connecter</Link><Link className="uza-btn uza-btn-primary" href="/inscription">S'inscrire</Link></>}<button className="uza-menu" onClick={() => setOpen(!open)} aria-label="Menu">{open ? "×" : "☰"}</button></div></div>{open && <div className="uza-mobile-panel">{links.map(([label, href]) => <Link key={href} href={href} onClick={() => setOpen(false)}>{label}</Link>)}{authenticated ? <Link className="uza-btn uza-btn-primary" href="/profil">Mon profil</Link> : <><Link className="uza-btn" href="/connexion">Se connecter</Link><Link className="uza-btn uza-btn-primary" href="/inscription">S'inscrire</Link></>}</div>}</header>;
}
