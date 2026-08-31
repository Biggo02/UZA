"use client";
import Link from "next/link";
import { useState } from "react";

const items = [["Accueil","/"],["Annonces","/annonces"],["Catégories","/categories"],["Comment ça marche","/comment-ca-marche"],["À propos","/a-propos"],["Nos locaux","/nos-locaux"]];
export default function MobileNav({ authenticated=false }: { authenticated?: boolean }) {
 const [open,setOpen]=useState(false);
 return <>
  <button className="uza-menu" onClick={()=>setOpen(v=>!v)} aria-label="Ouvrir le menu">{open?"×":"☰"}</button>
  {open && <div className="uza-mobile-panel">{items.map(([label,href])=><Link key={href} href={href} onClick={()=>setOpen(false)}>{label}</Link>)}{authenticated?<Link className="uza-btn uza-btn-primary" href="/profil">Mon profil</Link>:<><Link className="uza-btn" href="/connexion">Se connecter</Link><Link className="uza-btn uza-btn-primary" href="/inscription">S'inscrire</Link></>}</div>}
 </>;
}
