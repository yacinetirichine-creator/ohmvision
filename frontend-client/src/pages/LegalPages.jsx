/*
  OhmVision - Documentation Juridique Complète
  Conformité RGPD, Loi Informatique et Libertés, Code de la Consommation
  Mis à jour : Janvier 2026
*/

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  FiShield, FiLock, FiFileText, FiArrowLeft, FiBook, 
  FiCreditCard, FiClipboard, FiCheck, FiAlertTriangle,
  FiMail, FiPhone, FiMapPin, FiChevronDown, FiChevronUp
} from 'react-icons/fi';
import { Link } from 'react-router-dom';

// ============================================
// COMPOSANT LAYOUT COMMUN
// ============================================
const LegalLayout = ({ title, icon: Icon, lastUpdate, children }) => {
  return (
    <div className="min-h-screen bg-dark-950 text-gray-300 font-sans">
      {/* Navigation */}
      <nav className="fixed w-full z-50 glass-panel border-b border-white/5 py-4 px-6">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 text-ohm-cyan hover:text-white transition-colors">
            <FiArrowLeft /> Retour à l'accueil
          </Link>
          <div className="font-bold text-white">OHM<span className="text-ohm-cyan">VISION</span></div>
        </div>
      </nav>

      <main className="pt-28 pb-20 px-4 md:px-6 max-w-5xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-6 md:p-10 mb-6"
        >
          <div className="flex flex-col md:flex-row md:items-center gap-4 mb-6 pb-6 border-b border-white/10">
            <div className="w-16 h-16 rounded-2xl bg-ohm-cyan/10 flex items-center justify-center text-ohm-cyan flex-shrink-0">
              <Icon size={32} />
            </div>
            <div className="flex-1">
              <h1 className="text-2xl md:text-3xl font-bold text-white mb-2">{title}</h1>
              {lastUpdate && (
                <p className="text-sm text-gray-500">Dernière mise à jour : {lastUpdate}</p>
              )}
            </div>
          </div>

          {/* Contenu */}
          <div className="prose prose-invert prose-lg max-w-none 
            prose-headings:text-white prose-headings:font-semibold
            prose-h2:text-xl prose-h2:mt-8 prose-h2:mb-4 prose-h2:pb-2 prose-h2:border-b prose-h2:border-white/10
            prose-h3:text-lg prose-h3:mt-6 prose-h3:mb-3 prose-h3:text-ohm-cyan
            prose-h4:text-base prose-h4:mt-4 prose-h4:mb-2
            prose-p:text-gray-300 prose-p:leading-relaxed
            prose-li:text-gray-300
            prose-a:text-ohm-cyan prose-a:no-underline hover:prose-a:underline
            prose-strong:text-white
            prose-table:text-sm
            prose-th:bg-white/5 prose-th:px-4 prose-th:py-2 prose-th:text-left
            prose-td:px-4 prose-td:py-2 prose-td:border-t prose-td:border-white/5"
          >
            {children}
          </div>
        </motion.div>

        {/* Footer légal */}
        <div className="text-center text-sm text-gray-500 mt-8">
          <p>© 2026 OhmTronic SAS - Tous droits réservés</p>
          <div className="flex flex-wrap justify-center gap-4 mt-3">
            <Link to="/legal/mentions" className="hover:text-ohm-cyan transition-colors">Mentions Légales</Link>
            <Link to="/legal/privacy" className="hover:text-ohm-cyan transition-colors">Confidentialité</Link>
            <Link to="/legal/cgu" className="hover:text-ohm-cyan transition-colors">CGU</Link>
            <Link to="/legal/cgv" className="hover:text-ohm-cyan transition-colors">CGV</Link>
            <Link to="/legal/gdpr" className="hover:text-ohm-cyan transition-colors">RGPD</Link>
          </div>
        </div>
      </main>
    </div>
  );
};

// ============================================
// 1. MENTIONS LÉGALES
// ============================================
export const LegalMentionsPage = () => (
  <LegalLayout title="Mentions Légales" icon={FiFileText} lastUpdate="20 janvier 2026">
    
    <h2>Article 1 – Éditeur du Service</h2>
    <p>
      Le site internet <strong>ohmvision.fr</strong> et le logiciel <strong>OhmVision</strong> sont édités par :
    </p>
    <div className="bg-white/5 rounded-xl p-6 my-6">
      <p className="mb-2"><strong>OhmTronic SAS</strong></p>
      <p className="mb-1">Société par Actions Simplifiée au capital de 10 000 €</p>
      <p className="mb-1">Siège social : 15 Rue de l'Innovation, 75001 Paris, France</p>
      <p className="mb-1">RCS Paris : 912 345 678</p>
      <p className="mb-1">SIRET : 912 345 678 00012</p>
      <p className="mb-1">TVA Intracommunautaire : FR12 912345678</p>
      <p className="mb-1">Code APE : 6201Z (Programmation informatique)</p>
      <p className="mt-4 pt-4 border-t border-white/10">
        <strong>Directeur de la publication :</strong> M. Yacine Tirichine, Président
      </p>
    </div>

    <h2>Article 2 – Contact</h2>
    <div className="grid md:grid-cols-3 gap-4 my-6">
      <div className="bg-white/5 rounded-xl p-4 flex items-start gap-3">
        <FiMail className="text-ohm-cyan mt-1 flex-shrink-0" />
        <div>
          <p className="text-white font-medium">Email général</p>
          <a href="mailto:contact@ohmtronic.fr">contact@ohmtronic.fr</a>
        </div>
      </div>
      <div className="bg-white/5 rounded-xl p-4 flex items-start gap-3">
        <FiPhone className="text-ohm-cyan mt-1 flex-shrink-0" />
        <div>
          <p className="text-white font-medium">Téléphone</p>
          <p>+33 (0)1 23 45 67 89</p>
        </div>
      </div>
      <div className="bg-white/5 rounded-xl p-4 flex items-start gap-3">
        <FiMapPin className="text-ohm-cyan mt-1 flex-shrink-0" />
        <div>
          <p className="text-white font-medium">Adresse</p>
          <p>15 Rue de l'Innovation<br/>75001 Paris</p>
        </div>
      </div>
    </div>

    <h2>Article 3 – Hébergement</h2>
    <p>Le service OhmVision est hébergé par :</p>
    <div className="bg-white/5 rounded-xl p-6 my-6">
      <p className="mb-2"><strong>Hetzner Online GmbH</strong></p>
      <p className="mb-1">Industriestr. 25, 91710 Gunzenhausen, Allemagne</p>
      <p className="mb-1">Certifications : ISO 27001, SOC 2 Type II</p>
      <p className="mt-3 text-sm text-gray-400">
        Les données sont stockées exclusivement dans des datacenters situés en Union Européenne 
        (Allemagne et Finlande), conformément aux exigences du RGPD.
      </p>
    </div>

    <h2>Article 4 – Propriété Intellectuelle</h2>
    <h3>4.1 Droits d'auteur</h3>
    <p>
      L'ensemble des éléments constituant le site et le logiciel OhmVision (textes, graphismes, 
      logiciels, photographies, images, vidéos, sons, plans, noms, logos, marques, créations et œuvres 
      protégeables diverses, bases de données, etc.) ainsi que le site et le logiciel eux-mêmes, sont 
      la propriété exclusive d'OhmTronic SAS ou de ses partenaires.
    </p>

    <h3>4.2 Algorithmes et Intelligence Artificielle</h3>
    <p>
      Les modèles d'intelligence artificielle, algorithmes de détection, de reconnaissance et d'analyse 
      comportementale intégrés dans OhmVision sont protégés par le droit d'auteur et constituent des 
      secrets commerciaux d'OhmTronic SAS. Toute tentative de rétro-ingénierie, décompilation ou 
      extraction est strictement interdite.
    </p>

    <h3>4.3 Marques</h3>
    <p>
      Les marques « OhmVision », « OhmTronic » et les logos associés sont des marques déposées 
      d'OhmTronic SAS. Toute reproduction ou utilisation de ces marques sans autorisation préalable 
      écrite est prohibée.
    </p>

    <h2>Article 5 – Activité Réglementée</h2>
    <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-6 my-6">
      <div className="flex items-start gap-3">
        <FiAlertTriangle className="text-amber-500 mt-1 flex-shrink-0" size={24} />
        <div>
          <p className="text-white font-medium mb-2">Réglementation Vidéosurveillance</p>
          <p className="text-sm">
            L'installation et l'exploitation de systèmes de vidéosurveillance sont soumises à des 
            obligations légales spécifiques en France (Loi n° 95-73, Code de la sécurité intérieure) 
            et dans l'Union Européenne (RGPD). L'utilisateur est seul responsable de la conformité 
            de son installation aux réglementations applicables, notamment concernant :
          </p>
          <ul className="text-sm mt-3 space-y-1">
            <li>• L'autorisation préfectorale pour les lieux ouverts au public</li>
            <li>• La déclaration à la CNIL pour les traitements de données personnelles</li>
            <li>• L'information des personnes filmées (affichage obligatoire)</li>
            <li>• La durée de conservation des enregistrements (1 mois maximum en général)</li>
            <li>• La consultation préalable du CSE pour les entreprises</li>
          </ul>
        </div>
      </div>
    </div>

    <h2>Article 6 – Liens Hypertextes</h2>
    <p>
      Le site peut contenir des liens vers d'autres sites web. OhmTronic SAS n'exerce aucun contrôle 
      sur ces sites et décline toute responsabilité quant à leur contenu ou aux traitements de données 
      qu'ils effectuent.
    </p>

    <h2>Article 7 – Droit Applicable et Juridiction</h2>
    <p>
      Les présentes mentions légales sont régies par le droit français. En cas de litige, et après 
      tentative de résolution amiable, compétence exclusive est attribuée aux tribunaux de Paris.
    </p>

  </LegalLayout>
);

// ============================================
// 2. POLITIQUE DE CONFIDENTIALITÉ
// ============================================
export const PrivacyPage = () => (
  <LegalLayout title="Politique de Confidentialité" icon={FiLock} lastUpdate="20 janvier 2026">
    
    <div className="bg-ohm-cyan/10 border border-ohm-cyan/30 rounded-xl p-6 mb-8">
      <p className="text-white">
        <strong>Résumé :</strong> Nous collectons uniquement les données nécessaires au fonctionnement 
        du service de vidéosurveillance. Les flux vidéo restent sous votre contrôle exclusif. 
        Nous ne vendons jamais vos données.
      </p>
    </div>

    <h2>Article 1 – Responsable du Traitement</h2>
    <p>Le responsable du traitement des données personnelles est :</p>
    <div className="bg-white/5 rounded-xl p-6 my-6">
      <p><strong>OhmTronic SAS</strong></p>
      <p>15 Rue de l'Innovation, 75001 Paris, France</p>
      <p>Email : <a href="mailto:privacy@ohmtronic.fr">privacy@ohmtronic.fr</a></p>
    </div>

    <h2>Article 2 – Délégué à la Protection des Données (DPO)</h2>
    <p>
      Conformément au RGPD, nous avons désigné un Délégué à la Protection des Données que vous 
      pouvez contacter pour toute question relative à vos données personnelles :
    </p>
    <div className="bg-white/5 rounded-xl p-6 my-6">
      <p><strong>DPO OhmTronic</strong></p>
      <p>Email : <a href="mailto:dpo@ohmtronic.fr">dpo@ohmtronic.fr</a></p>
      <p>Courrier : DPO OhmTronic, 15 Rue de l'Innovation, 75001 Paris</p>
    </div>

    <h2>Article 3 – Données Collectées</h2>
    
    <h3>3.1 Données d'identification et de compte</h3>
    <table className="w-full">
      <thead>
        <tr>
          <th>Donnée</th>
          <th>Finalité</th>
          <th>Base légale</th>
          <th>Conservation</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Nom, prénom</td>
          <td>Gestion du compte</td>
          <td>Contrat</td>
          <td>Durée du contrat + 3 ans</td>
        </tr>
        <tr>
          <td>Email</td>
          <td>Communication, notifications</td>
          <td>Contrat</td>
          <td>Durée du contrat + 3 ans</td>
        </tr>
        <tr>
          <td>Téléphone</td>
          <td>Alertes SMS (optionnel)</td>
          <td>Consentement</td>
          <td>Jusqu'au retrait du consentement</td>
        </tr>
        <tr>
          <td>Adresse</td>
          <td>Facturation</td>
          <td>Obligation légale</td>
          <td>10 ans (comptabilité)</td>
        </tr>
        <tr>
          <td>Données de paiement</td>
          <td>Transactions</td>
          <td>Contrat</td>
          <td>Gérées par Stripe (PCI-DSS)</td>
        </tr>
      </tbody>
    </table>

    <h3>3.2 Données techniques et de connexion</h3>
    <table className="w-full">
      <thead>
        <tr>
          <th>Donnée</th>
          <th>Finalité</th>
          <th>Base légale</th>
          <th>Conservation</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Adresse IP</td>
          <td>Sécurité, diagnostic</td>
          <td>Intérêt légitime</td>
          <td>12 mois</td>
        </tr>
        <tr>
          <td>Logs de connexion</td>
          <td>Audit de sécurité</td>
          <td>Obligation légale</td>
          <td>12 mois</td>
        </tr>
        <tr>
          <td>Configuration caméras</td>
          <td>Fonctionnement du service</td>
          <td>Contrat</td>
          <td>Durée du contrat</td>
        </tr>
        <tr>
          <td>Métadonnées d'alertes</td>
          <td>Historique, statistiques</td>
          <td>Contrat</td>
          <td>Selon abonnement (7j à 1an)</td>
        </tr>
      </tbody>
    </table>

    <h3>3.3 Données vidéo et images</h3>
    <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-6 my-6">
      <p className="text-white font-medium mb-3">⚠️ Important concernant les flux vidéo</p>
      <ul className="space-y-2 text-sm">
        <li>
          <strong>Déploiement Cloud :</strong> Les snapshots et clips vidéo liés aux alertes sont 
          stockés temporairement sur nos serveurs sécurisés (chiffrés AES-256) pendant la durée 
          définie par votre abonnement.
        </li>
        <li>
          <strong>Déploiement On-Premise :</strong> Aucune donnée vidéo ne transite par nos serveurs. 
          Le traitement s'effectue intégralement sur votre infrastructure.
        </li>
        <li>
          <strong>Flux temps réel :</strong> Les flux vidéo en direct ne sont jamais enregistrés 
          par OhmTronic sauf déclenchement d'alerte selon vos paramètres.
        </li>
      </ul>
    </div>

    <h2>Article 4 – Finalités du Traitement</h2>
    <p>Vos données sont utilisées exclusivement pour :</p>
    <ul>
      <li><strong>Fourniture du service :</strong> Fonctionnement de la vidéosurveillance, analyse IA, alertes</li>
      <li><strong>Gestion commerciale :</strong> Facturation, support client, communication contractuelle</li>
      <li><strong>Amélioration du service :</strong> Statistiques anonymisées, correction de bugs</li>
      <li><strong>Sécurité :</strong> Prévention de la fraude, détection d'intrusions</li>
      <li><strong>Obligations légales :</strong> Conservation des données de connexion, réponse aux réquisitions</li>
    </ul>

    <h2>Article 5 – Destinataires des Données</h2>
    <p>Vos données peuvent être transmises à :</p>
    <table className="w-full">
      <thead>
        <tr>
          <th>Destinataire</th>
          <th>Finalité</th>
          <th>Localisation</th>
          <th>Garanties</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Hetzner Online GmbH</td>
          <td>Hébergement</td>
          <td>UE (Allemagne)</td>
          <td>ISO 27001</td>
        </tr>
        <tr>
          <td>Stripe Inc.</td>
          <td>Paiements</td>
          <td>UE/US</td>
          <td>PCI-DSS, SCCs</td>
        </tr>
        <tr>
          <td>Brevo (ex-Sendinblue)</td>
          <td>Emails transactionnels</td>
          <td>UE (France)</td>
          <td>ISO 27001</td>
        </tr>
        <tr>
          <td>Sentry.io</td>
          <td>Monitoring erreurs</td>
          <td>UE</td>
          <td>SCCs</td>
        </tr>
      </tbody>
    </table>
    <p className="mt-4 text-sm text-gray-400">
      <strong>Aucune vente de données :</strong> Nous ne vendons, ne louons et ne partageons jamais vos 
      données personnelles à des fins commerciales ou publicitaires.
    </p>

    <h2>Article 6 – Transferts Hors UE</h2>
    <p>
      Certains de nos sous-traitants peuvent être situés hors de l'Union Européenne. Dans ce cas, 
      nous nous assurons que des garanties appropriées sont mises en place :
    </p>
    <ul>
      <li>Clauses Contractuelles Types (CCT/SCCs) de la Commission Européenne</li>
      <li>Décision d'adéquation de la Commission Européenne le cas échéant</li>
      <li>Binding Corporate Rules (BCR) pour les groupes internationaux</li>
    </ul>

    <h2>Article 7 – Vos Droits</h2>
    <p>Conformément au RGPD, vous disposez des droits suivants :</p>
    
    <div className="grid md:grid-cols-2 gap-4 my-6">
      <div className="bg-white/5 rounded-xl p-4">
        <h4 className="text-white font-medium mb-2">Droit d'accès</h4>
        <p className="text-sm">Obtenir la confirmation que vos données sont traitées et en recevoir une copie.</p>
      </div>
      <div className="bg-white/5 rounded-xl p-4">
        <h4 className="text-white font-medium mb-2">Droit de rectification</h4>
        <p className="text-sm">Corriger des données inexactes ou compléter des données incomplètes.</p>
      </div>
      <div className="bg-white/5 rounded-xl p-4">
        <h4 className="text-white font-medium mb-2">Droit à l'effacement</h4>
        <p className="text-sm">Demander la suppression de vos données dans les conditions prévues par le RGPD.</p>
      </div>
      <div className="bg-white/5 rounded-xl p-4">
        <h4 className="text-white font-medium mb-2">Droit à la limitation</h4>
        <p className="text-sm">Demander la suspension temporaire du traitement de vos données.</p>
      </div>
      <div className="bg-white/5 rounded-xl p-4">
        <h4 className="text-white font-medium mb-2">Droit à la portabilité</h4>
        <p className="text-sm">Recevoir vos données dans un format structuré et lisible par machine.</p>
      </div>
      <div className="bg-white/5 rounded-xl p-4">
        <h4 className="text-white font-medium mb-2">Droit d'opposition</h4>
        <p className="text-sm">Vous opposer au traitement pour motifs légitimes ou à la prospection.</p>
      </div>
    </div>

    <p>
      <strong>Comment exercer vos droits :</strong> Envoyez votre demande à{' '}
      <a href="mailto:dpo@ohmtronic.fr">dpo@ohmtronic.fr</a> avec une copie de votre pièce d'identité. 
      Nous répondrons dans un délai d'un mois.
    </p>

    <p className="mt-4">
      <strong>Réclamation :</strong> Vous pouvez introduire une réclamation auprès de la CNIL :{' '}
      <a href="https://www.cnil.fr" target="_blank" rel="noopener noreferrer">www.cnil.fr</a>
    </p>

    <h2>Article 8 – Cookies</h2>
    <p>Notre site utilise des cookies. Pour plus d'informations, consultez notre politique de cookies.</p>
    
    <table className="w-full">
      <thead>
        <tr>
          <th>Cookie</th>
          <th>Finalité</th>
          <th>Durée</th>
          <th>Type</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>session_token</td>
          <td>Authentification</td>
          <td>Session</td>
          <td>Essentiel</td>
        </tr>
        <tr>
          <td>refresh_token</td>
          <td>Maintien connexion</td>
          <td>30 jours</td>
          <td>Essentiel</td>
        </tr>
        <tr>
          <td>theme_preference</td>
          <td>Préférence affichage</td>
          <td>1 an</td>
          <td>Fonctionnel</td>
        </tr>
        <tr>
          <td>analytics_consent</td>
          <td>Consentement analytics</td>
          <td>1 an</td>
          <td>Essentiel</td>
        </tr>
      </tbody>
    </table>

    <h2>Article 9 – Sécurité des Données</h2>
    <p>Nous mettons en œuvre les mesures de sécurité suivantes :</p>
    <ul>
      <li><strong>Chiffrement :</strong> TLS 1.3 pour les transferts, AES-256 pour le stockage</li>
      <li><strong>Authentification :</strong> Hachage bcrypt, support 2FA/MFA</li>
      <li><strong>Infrastructure :</strong> Pare-feu, détection d'intrusion, sauvegardes chiffrées</li>
      <li><strong>Accès :</strong> Principe du moindre privilège, journalisation des accès</li>
      <li><strong>Personnel :</strong> Formation sécurité, clauses de confidentialité</li>
    </ul>

    <h2>Article 10 – Modifications</h2>
    <p>
      Cette politique peut être mise à jour. En cas de modification substantielle, vous serez 
      informé par email et/ou notification dans l'application au moins 30 jours avant l'entrée en vigueur.
    </p>

  </LegalLayout>
);

// ============================================
// 3. CONDITIONS GÉNÉRALES D'UTILISATION (CGU)
// ============================================
export const CGUPage = () => (
  <LegalLayout title="Conditions Générales d'Utilisation" icon={FiBook} lastUpdate="20 janvier 2026">
    
    <div className="bg-white/5 rounded-xl p-6 mb-8">
      <p className="text-white font-medium mb-2">Préambule</p>
      <p className="text-sm">
        Les présentes Conditions Générales d'Utilisation (« CGU ») régissent l'accès et l'utilisation 
        du logiciel OhmVision et des services associés. En utilisant OhmVision, vous acceptez 
        intégralement ces CGU.
      </p>
    </div>

    <h2>Article 1 – Définitions</h2>
    <ul>
      <li><strong>« Service »</strong> : Le logiciel OhmVision et l'ensemble des fonctionnalités associées</li>
      <li><strong>« Utilisateur »</strong> : Toute personne physique ou morale utilisant le Service</li>
      <li><strong>« Client »</strong> : L'Utilisateur ayant souscrit un abonnement payant</li>
      <li><strong>« Compte »</strong> : L'espace personnel créé par l'Utilisateur</li>
      <li><strong>« Contenu Utilisateur »</strong> : Données, configurations et paramètres créés par l'Utilisateur</li>
      <li><strong>« IA »</strong> : Les fonctionnalités d'intelligence artificielle intégrées au Service</li>
    </ul>

    <h2>Article 2 – Objet</h2>
    <p>
      OhmVision est une plateforme de vidéosurveillance intelligente permettant l'analyse en temps réel 
      de flux vidéo par intelligence artificielle. Les présentes CGU définissent les conditions dans 
      lesquelles l'Utilisateur peut accéder et utiliser le Service.
    </p>

    <h2>Article 3 – Accès au Service</h2>
    
    <h3>3.1 Inscription</h3>
    <p>
      L'utilisation du Service nécessite la création d'un Compte. L'Utilisateur s'engage à fournir 
      des informations exactes, complètes et à les maintenir à jour.
    </p>

    <h3>3.2 Capacité juridique</h3>
    <p>
      L'Utilisateur déclare être majeur et avoir la capacité juridique de contracter. Pour les 
      personnes morales, l'utilisateur déclare avoir les pouvoirs nécessaires pour engager l'entité.
    </p>

    <h3>3.3 Sécurité du Compte</h3>
    <p>
      L'Utilisateur est responsable de la confidentialité de ses identifiants de connexion. 
      Toute activité réalisée depuis son Compte est présumée effectuée par lui-même. En cas 
      de compromission suspectée, l'Utilisateur doit immédiatement en informer OhmTronic.
    </p>

    <h2>Article 4 – Description du Service</h2>
    
    <h3>4.1 Fonctionnalités principales</h3>
    <ul>
      <li>Connexion et gestion de caméras de surveillance (ONVIF, RTSP, Cloud)</li>
      <li>Détection et analyse d'objets, personnes, véhicules par IA</li>
      <li>Comptage et statistiques de fréquentation</li>
      <li>Détection d'événements (intrusion, chute, incendie, etc.)</li>
      <li>Génération d'alertes et notifications multicanales</li>
      <li>Tableaux de bord et rapports analytiques</li>
      <li>Assistant IA conversationnel</li>
    </ul>

    <h3>4.2 Niveaux de service</h3>
    <p>
      Les fonctionnalités disponibles dépendent de l'abonnement souscrit. Le détail est disponible 
      sur la page Tarifs et dans les Conditions Générales de Vente.
    </p>

    <h3>4.3 Évolutions du Service</h3>
    <p>
      OhmTronic se réserve le droit de faire évoluer le Service (ajout, modification ou suppression 
      de fonctionnalités) sans que cela constitue une modification des présentes CGU, sous réserve 
      de ne pas dégrader substantiellement le niveau de service souscrit.
    </p>

    <h2>Article 5 – Obligations de l'Utilisateur</h2>
    
    <h3>5.1 Utilisation licite</h3>
    <p>L'Utilisateur s'engage à :</p>
    <ul>
      <li>Utiliser le Service conformément aux lois et réglementations applicables</li>
      <li>Respecter les droits des tiers, notamment le droit à l'image et à la vie privée</li>
      <li>Ne pas utiliser le Service à des fins illicites, frauduleuses ou malveillantes</li>
      <li>Ne pas tenter de compromettre la sécurité ou l'intégrité du Service</li>
    </ul>

    <h3>5.2 Conformité vidéosurveillance</h3>
    <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-6 my-6">
      <p className="text-white font-medium mb-3">Responsabilité de l'Utilisateur</p>
      <p className="text-sm mb-3">
        L'Utilisateur est <strong>seul responsable</strong> de la conformité de son système de 
        vidéosurveillance aux réglementations applicables. Il s'engage notamment à :
      </p>
      <ul className="text-sm space-y-2">
        <li>• Obtenir les autorisations nécessaires (préfectorales, CNIL, etc.)</li>
        <li>• Informer les personnes filmées de manière visible et lisible</li>
        <li>• Respecter les durées de conservation légales des enregistrements</li>
        <li>• Limiter l'accès aux images aux seules personnes habilitées</li>
        <li>• Ne pas filmer l'espace public sans autorisation (domicile privé)</li>
        <li>• Consulter les représentants du personnel si applicable</li>
      </ul>
    </div>

    <h3>5.3 Usages interdits</h3>
    <p>Sont expressément interdits :</p>
    <ul>
      <li>La surveillance discriminatoire ou le profilage illicite</li>
      <li>L'utilisation à des fins de harcèlement ou d'espionnage</li>
      <li>La revente ou redistribution du Service sans autorisation</li>
      <li>L'extraction automatisée de données (scraping)</li>
      <li>La rétro-ingénierie des algorithmes d'IA</li>
      <li>L'introduction de virus ou codes malveillants</li>
      <li>La surcharge intentionnelle de l'infrastructure</li>
    </ul>

    <h2>Article 6 – Propriété Intellectuelle</h2>
    
    <h3>6.1 Droits d'OhmTronic</h3>
    <p>
      OhmTronic conserve l'intégralité des droits de propriété intellectuelle sur le Service, 
      incluant les logiciels, algorithmes, interfaces, documentations et marques. L'Utilisateur 
      bénéficie uniquement d'un droit d'utilisation personnel, non exclusif et non cessible.
    </p>

    <h3>6.2 Contenu Utilisateur</h3>
    <p>
      L'Utilisateur conserve la propriété de son Contenu Utilisateur. Il accorde à OhmTronic une 
      licence limitée et non exclusive pour traiter ce contenu aux seules fins de fourniture du Service.
    </p>

    <h3>6.3 Retours et suggestions</h3>
    <p>
      Tout retour, suggestion ou idée d'amélioration communiqué à OhmTronic pourra être librement 
      utilisé sans obligation de compensation.
    </p>

    <h2>Article 7 – Données Personnelles</h2>
    <p>
      Le traitement des données personnelles est régi par notre{' '}
      <Link to="/legal/privacy" className="text-ohm-cyan">Politique de Confidentialité</Link>.
    </p>

    <h2>Article 8 – Disponibilité et Support</h2>
    
    <h3>8.1 Disponibilité</h3>
    <p>
      OhmTronic s'efforce d'assurer une disponibilité du Service 24h/24, 7j/7. Cependant, 
      l'accès peut être temporairement interrompu pour maintenance, mise à jour ou cas de force majeure.
    </p>

    <h3>8.2 Support technique</h3>
    <p>
      Le niveau de support dépend de l'abonnement souscrit. Le support est accessible via 
      l'interface du Service, par email ou via l'assistant IA intégré.
    </p>

    <h2>Article 9 – Responsabilité</h2>
    
    <h3>9.1 Limitation de responsabilité</h3>
    <p>
      OhmTronic ne saurait être tenu responsable des dommages indirects, pertes de profits, 
      pertes de données ou d'exploitation résultant de l'utilisation ou de l'impossibilité 
      d'utiliser le Service.
    </p>

    <h3>9.2 Force majeure</h3>
    <p>
      OhmTronic n'est pas responsable des manquements résultant d'événements de force majeure 
      (catastrophe naturelle, guerre, cyberattaque massive, défaillance fournisseur, etc.).
    </p>

    <h3>9.3 Précision de l'IA</h3>
    <div className="bg-white/5 rounded-xl p-6 my-6">
      <p>
        Les fonctionnalités d'intelligence artificielle fournissent des <strong>détections 
        probabilistes</strong>. Malgré nos efforts pour optimiser la précision, des faux positifs 
        et faux négatifs peuvent survenir. L'Utilisateur est invité à configurer les seuils de 
        sensibilité selon ses besoins et à ne pas se fier exclusivement aux détections automatiques 
        pour des décisions critiques de sécurité.
      </p>
    </div>

    <h2>Article 10 – Suspension et Résiliation</h2>
    
    <h3>10.1 Par l'Utilisateur</h3>
    <p>
      L'Utilisateur peut résilier son Compte à tout moment depuis les paramètres de l'application 
      ou en contactant le support. Les conditions financières sont précisées dans les CGV.
    </p>

    <h3>10.2 Par OhmTronic</h3>
    <p>
      OhmTronic peut suspendre ou résilier un Compte en cas de :
    </p>
    <ul>
      <li>Violation des présentes CGU</li>
      <li>Non-paiement après relances</li>
      <li>Activité frauduleuse ou illicite</li>
      <li>Demande d'une autorité compétente</li>
    </ul>

    <h3>10.3 Effets de la résiliation</h3>
    <p>
      À la résiliation, l'accès au Service est désactivé. L'Utilisateur peut demander l'export 
      de ses données dans les 30 jours suivant la résiliation.
    </p>

    <h2>Article 11 – Modifications des CGU</h2>
    <p>
      OhmTronic peut modifier les présentes CGU. Les modifications substantielles seront notifiées 
      30 jours à l'avance. La poursuite de l'utilisation après l'entrée en vigueur vaut acceptation.
    </p>

    <h2>Article 12 – Droit Applicable et Litiges</h2>
    <p>
      Les présentes CGU sont régies par le droit français. En cas de litige, les parties 
      s'engagent à rechercher une solution amiable. À défaut, les tribunaux de Paris seront 
      seuls compétents.
    </p>

    <h2>Article 13 – Dispositions Diverses</h2>
    <p>
      Si une disposition des présentes CGU est déclarée nulle, les autres dispositions restent 
      en vigueur. Le fait de ne pas exercer un droit ne constitue pas une renonciation à ce droit.
    </p>

  </LegalLayout>
);

// ============================================
// 4. CONDITIONS GÉNÉRALES DE VENTE (CGV)
// ============================================
export const CGVPage = () => (
  <LegalLayout title="Conditions Générales de Vente" icon={FiCreditCard} lastUpdate="20 janvier 2026">
    
    <div className="bg-white/5 rounded-xl p-6 mb-8">
      <p className="text-white font-medium mb-2">Champ d'application</p>
      <p className="text-sm">
        Les présentes Conditions Générales de Vente (« CGV ») s'appliquent à toute souscription 
        d'abonnement au service OhmVision. Elles complètent les CGU et prévalent en cas de contradiction.
      </p>
    </div>

    <h2>Article 1 – Offres et Tarifs</h2>
    
    <h3>1.1 Formules d'abonnement</h3>
    <table className="w-full text-sm">
      <thead>
        <tr>
          <th>Offre</th>
          <th>Tarif</th>
          <th>Engagement</th>
          <th>Caméras</th>
          <th>Utilisateurs</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>FREE</strong></td>
          <td>Gratuit</td>
          <td>Aucun</td>
          <td>1-2</td>
          <td>1</td>
        </tr>
        <tr>
          <td><strong>HOME</strong></td>
          <td>29€ unique</td>
          <td>Aucun</td>
          <td>1-4</td>
          <td>3</td>
        </tr>
        <tr>
          <td><strong>PRO</strong></td>
          <td>99€/an ou 12€/mois</td>
          <td>Aucun</td>
          <td>5-16</td>
          <td>10</td>
        </tr>
        <tr>
          <td><strong>BUSINESS</strong></td>
          <td>299€/an ou 29€/mois</td>
          <td>Aucun</td>
          <td>17-50</td>
          <td>50</td>
        </tr>
        <tr>
          <td><strong>ENTERPRISE</strong></td>
          <td>Sur devis</td>
          <td>Annuel</td>
          <td>Illimité</td>
          <td>Illimité</td>
        </tr>
      </tbody>
    </table>

    <h3>1.2 Options complémentaires</h3>
    <ul>
      <li><strong>Caméras supplémentaires :</strong> 3€/mois/caméra (au-delà du quota)</li>
      <li><strong>Stockage additionnel :</strong> 5€/mois/100GB</li>
      <li><strong>Support prioritaire :</strong> 49€/mois (SLA 4h)</li>
      <li><strong>Installation accompagnée :</strong> 199€ (session 2h)</li>
    </ul>

    <h3>1.3 Modification des tarifs</h3>
    <p>
      OhmTronic se réserve le droit de modifier ses tarifs. Les nouveaux tarifs s'appliquent 
      aux nouvelles souscriptions et aux renouvellements. Les abonnements en cours conservent 
      leur tarif jusqu'au prochain renouvellement, avec notification préalable de 30 jours.
    </p>

    <h2>Article 2 – Commande et Souscription</h2>
    
    <h3>2.1 Processus de commande</h3>
    <ol>
      <li>Création de compte ou connexion</li>
      <li>Sélection de l'offre et des options</li>
      <li>Vérification du récapitulatif</li>
      <li>Acceptation des CGU et CGV</li>
      <li>Paiement sécurisé</li>
      <li>Confirmation par email</li>
    </ol>

    <h3>2.2 Période d'essai</h3>
    <p>
      Les offres payantes bénéficient d'une <strong>période d'essai gratuite de 14 jours</strong> 
      sans engagement. Aucun prélèvement n'est effectué durant cette période. Sans action de votre 
      part, l'abonnement payant démarre automatiquement à l'issue de l'essai.
    </p>

    <h2>Article 3 – Paiement</h2>
    
    <h3>3.1 Moyens de paiement</h3>
    <p>Les moyens de paiement acceptés sont :</p>
    <ul>
      <li>Carte bancaire (Visa, Mastercard, American Express)</li>
      <li>Prélèvement SEPA (abonnements annuels)</li>
      <li>Virement bancaire (sur demande, entreprises)</li>
      <li>PayPal (selon disponibilité)</li>
    </ul>

    <h3>3.2 Sécurité des paiements</h3>
    <p>
      Les paiements sont traités par <strong>Stripe</strong>, prestataire certifié PCI-DSS niveau 1. 
      OhmTronic ne stocke aucune donnée bancaire.
    </p>

    <h3>3.3 Facturation</h3>
    <ul>
      <li><strong>Abonnement mensuel :</strong> Facturation le 1er de chaque mois</li>
      <li><strong>Abonnement annuel :</strong> Facturation à la date anniversaire</li>
      <li><strong>Achat unique (HOME) :</strong> Facturation immédiate</li>
    </ul>
    <p>
      Les factures sont disponibles dans l'espace client et envoyées par email au format PDF.
    </p>

    <h3>3.4 Défaut de paiement</h3>
    <p>
      En cas d'échec de paiement, OhmTronic adresse une notification à l'Utilisateur. 
      Sans régularisation sous 7 jours, le Service peut être suspendu. Des pénalités de 
      retard de 3 fois le taux d'intérêt légal peuvent être appliquées.
    </p>

    <h2>Article 4 – Droit de Rétractation</h2>
    
    <h3>4.1 Consommateurs</h3>
    <div className="bg-ohm-cyan/10 border border-ohm-cyan/30 rounded-xl p-6 my-6">
      <p className="text-white font-medium mb-3">Délai de rétractation de 14 jours</p>
      <p className="text-sm mb-3">
        Conformément aux articles L221-18 et suivants du Code de la consommation, vous disposez 
        d'un délai de <strong>14 jours</strong> à compter de la souscription pour exercer votre 
        droit de rétractation, sans avoir à justifier de motifs ni à payer de pénalités.
      </p>
      <p className="text-sm">
        Pour exercer ce droit, envoyez une demande claire à{' '}
        <a href="mailto:support@ohmtronic.fr">support@ohmtronic.fr</a> ou utilisez le formulaire 
        de rétractation disponible dans votre espace client.
      </p>
    </div>

    <h3>4.2 Exception</h3>
    <p>
      Si vous avez expressément demandé l'activation immédiate du Service et commencé à l'utiliser 
      avant la fin du délai de rétractation, vous reconnaissez perdre votre droit de rétractation 
      pour les services déjà consommés. Un remboursement au prorata peut être effectué.
    </p>

    <h3>4.3 Professionnels</h3>
    <p>
      Les clients professionnels (B2B) ne bénéficient pas du droit de rétractation légal, 
      mais peuvent annuler leur période d'essai sans frais.
    </p>

    <h2>Article 5 – Durée et Renouvellement</h2>
    
    <h3>5.1 Durée initiale</h3>
    <ul>
      <li><strong>Mensuel :</strong> Engagement d'un mois, renouvelé tacitement</li>
      <li><strong>Annuel :</strong> Engagement d'un an, renouvelé tacitement</li>
      <li><strong>Paiement unique (HOME) :</strong> Licence perpétuelle, mises à jour 1 an</li>
    </ul>

    <h3>5.2 Renouvellement automatique</h3>
    <p>
      Les abonnements sont renouvelés automatiquement à leur échéance. Une notification de 
      rappel est envoyée 7 jours avant le renouvellement. Vous pouvez désactiver le renouvellement 
      automatique à tout moment depuis votre espace client.
    </p>

    <h3>5.3 Résiliation</h3>
    <ul>
      <li><strong>Mensuel :</strong> Résiliation effective à la fin du mois en cours</li>
      <li><strong>Annuel :</strong> Résiliation effective à la fin de la période annuelle</li>
      <li><strong>Immédiate :</strong> Possible avec remboursement au prorata (consommateurs)</li>
    </ul>

    <h2>Article 6 – Remboursements</h2>
    
    <h3>6.1 Politique de remboursement</h3>
    <table className="w-full text-sm">
      <thead>
        <tr>
          <th>Situation</th>
          <th>Remboursement</th>
          <th>Délai</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Rétractation (14 jours)</td>
          <td>Intégral ou prorata</td>
          <td>14 jours</td>
        </tr>
        <tr>
          <td>Indisponibilité majeure (&gt;48h)</td>
          <td>Prorata temporis</td>
          <td>30 jours</td>
        </tr>
        <tr>
          <td>Double facturation</td>
          <td>Intégral</td>
          <td>7 jours</td>
        </tr>
        <tr>
          <td>Résiliation anticipée (annuel)</td>
          <td>Non applicable</td>
          <td>-</td>
        </tr>
      </tbody>
    </table>

    <h3>6.2 Procédure</h3>
    <p>
      Les demandes de remboursement doivent être adressées à{' '}
      <a href="mailto:billing@ohmtronic.fr">billing@ohmtronic.fr</a>. 
      Le remboursement s'effectue sur le moyen de paiement d'origine.
    </p>

    <h2>Article 7 – Garanties</h2>
    
    <h3>7.1 Garantie légale de conformité</h3>
    <p>
      Conformément aux articles L217-4 et suivants du Code de la consommation, le Service est 
      garanti conforme au contrat. Vous bénéficiez d'un délai de 2 ans pour agir.
    </p>

    <h3>7.2 Garantie des vices cachés</h3>
    <p>
      Conformément aux articles 1641 et suivants du Code civil, vous pouvez demander la 
      résolution du contrat ou une réduction du prix en cas de vice caché.
    </p>

    <h3>7.3 Niveau de service (SLA)</h3>
    <table className="w-full text-sm">
      <thead>
        <tr>
          <th>Offre</th>
          <th>Disponibilité garantie</th>
          <th>Support</th>
          <th>Temps de réponse</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>FREE</td>
          <td>Best effort</td>
          <td>Communauté</td>
          <td>-</td>
        </tr>
        <tr>
          <td>HOME / PRO</td>
          <td>99%</td>
          <td>Email</td>
          <td>48h</td>
        </tr>
        <tr>
          <td>BUSINESS</td>
          <td>99.5%</td>
          <td>Prioritaire</td>
          <td>24h</td>
        </tr>
        <tr>
          <td>ENTERPRISE</td>
          <td>99.9%</td>
          <td>Dédié</td>
          <td>4h</td>
        </tr>
      </tbody>
    </table>

    <h2>Article 8 – Limites de Responsabilité</h2>
    
    <h3>8.1 Plafond de responsabilité</h3>
    <p>
      La responsabilité totale d'OhmTronic est limitée au montant des sommes effectivement 
      versées par le Client au cours des 12 derniers mois.
    </p>

    <h3>8.2 Exclusions</h3>
    <p>OhmTronic n'est pas responsable :</p>
    <ul>
      <li>Des dommages indirects (perte de chiffre d'affaires, préjudice d'image, etc.)</li>
      <li>Des dysfonctionnements liés à l'environnement technique du Client</li>
      <li>Des conséquences d'une utilisation non conforme</li>
      <li>Des défaillances de services tiers (fournisseur internet, caméras, etc.)</li>
    </ul>

    <h2>Article 9 – Propriété et Portabilité des Données</h2>
    
    <h3>9.1 Propriété</h3>
    <p>
      Le Client reste propriétaire de ses données (configurations, alertes, statistiques). 
      OhmTronic n'en acquiert aucun droit de propriété.
    </p>

    <h3>9.2 Export des données</h3>
    <p>
      Le Client peut à tout moment exporter ses données dans des formats standards (JSON, CSV) 
      depuis l'interface ou via l'API. L'export reste disponible 30 jours après résiliation.
    </p>

    <h2>Article 10 – Médiation</h2>
    <p>
      En cas de litige non résolu, le consommateur peut recourir gratuitement au médiateur 
      de la consommation :
    </p>
    <div className="bg-white/5 rounded-xl p-6 my-6">
      <p><strong>Médiateur de la consommation</strong></p>
      <p>CM2C - Centre de Médiation de la Consommation de Conciliateurs de Justice</p>
      <p>14 rue Saint Jean, 75017 Paris</p>
      <p><a href="https://www.cm2c.net">www.cm2c.net</a></p>
    </div>

    <h2>Article 11 – Droit Applicable</h2>
    <p>
      Les présentes CGV sont soumises au droit français. Tout litige relève de la compétence 
      exclusive des tribunaux de Paris, sous réserve des règles de compétence territoriale 
      applicables aux consommateurs.
    </p>

  </LegalLayout>
);

// ============================================
// 5. CONFORMITÉ RGPD
// ============================================
export const GDPRPage = () => (
  <LegalLayout title="Conformité RGPD" icon={FiShield} lastUpdate="20 janvier 2026">
    
    <div className="bg-ohm-cyan/10 border border-ohm-cyan/30 rounded-xl p-6 mb-8">
      <p className="text-white font-medium mb-2">Notre engagement</p>
      <p>
        OhmVision intègre le principe de « Privacy by Design ». La protection des données personnelles 
        est au cœur de notre conception technique et organisationnelle.
      </p>
    </div>

    <h2>Article 1 – Cadre Réglementaire</h2>
    <p>OhmVision est conçu pour être conforme aux réglementations suivantes :</p>
    <ul>
      <li><strong>RGPD</strong> - Règlement Général sur la Protection des Données (UE 2016/679)</li>
      <li><strong>Loi Informatique et Libertés</strong> - Loi n° 78-17 du 6 janvier 1978 modifiée</li>
      <li><strong>Directive ePrivacy</strong> - Directive 2002/58/CE concernant les cookies</li>
      <li><strong>Code de la sécurité intérieure</strong> - Dispositions sur la vidéosurveillance</li>
    </ul>

    <h2>Article 2 – Privacy by Design</h2>
    
    <h3>2.1 Minimisation des données</h3>
    <p>
      Nous ne collectons que les données strictement nécessaires au fonctionnement du service. 
      Les flux vidéo en direct ne sont pas stockés sauf configuration explicite par l'utilisateur.
    </p>

    <h3>2.2 Anonymisation automatique</h3>
    <div className="bg-white/5 rounded-xl p-6 my-6">
      <p className="text-white font-medium mb-3">Fonctionnalités d'anonymisation intégrées</p>
      <ul className="space-y-2">
        <li>
          <strong>Floutage des visages :</strong> Option activable pour flouter automatiquement 
          les visages dans les enregistrements non critiques (détection hors alerte).
        </li>
        <li>
          <strong>Masquage des plaques :</strong> Anonymisation des plaques d'immatriculation 
          sauf activation explicite de la reconnaissance LPR.
        </li>
        <li>
          <strong>Zones de confidentialité :</strong> Définition de zones à ne jamais enregistrer 
          (fenêtres donnant chez des voisins, bureaux, etc.).
        </li>
      </ul>
    </div>

    <h3>2.3 Pseudonymisation</h3>
    <p>
      Les identifiants des alertes et événements sont pseudonymisés. Les données de comptage 
      sont agrégées et ne permettent pas d'identifier les individus.
    </p>

    <h2>Article 3 – Durées de Conservation</h2>
    
    <table className="w-full">
      <thead>
        <tr>
          <th>Type de donnée</th>
          <th>Durée par défaut</th>
          <th>Maximum légal</th>
          <th>Paramétrable</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Flux vidéo temps réel</td>
          <td>Non stocké</td>
          <td>-</td>
          <td>Non</td>
        </tr>
        <tr>
          <td>Enregistrements sur alerte</td>
          <td>Selon abonnement</td>
          <td>1 mois*</td>
          <td>Oui</td>
        </tr>
        <tr>
          <td>Snapshots</td>
          <td>Selon abonnement</td>
          <td>1 mois*</td>
          <td>Oui</td>
        </tr>
        <tr>
          <td>Métadonnées d'alertes</td>
          <td>Selon abonnement</td>
          <td>1 an</td>
          <td>Oui</td>
        </tr>
        <tr>
          <td>Statistiques agrégées</td>
          <td>Illimitée</td>
          <td>Illimitée</td>
          <td>Oui</td>
        </tr>
        <tr>
          <td>Logs de connexion</td>
          <td>12 mois</td>
          <td>12 mois</td>
          <td>Non</td>
        </tr>
      </tbody>
    </table>
    <p className="text-sm text-gray-400 mt-2">
      * Sauf exception légale (procédure judiciaire en cours, réquisition)
    </p>

    <h3>3.1 Purge automatique</h3>
    <p>
      OhmVision inclut un système de purge automatique qui supprime définitivement les données 
      à l'expiration de leur durée de conservation. Aucune intervention manuelle n'est requise.
    </p>

    <h2>Article 4 – Droits des Personnes</h2>
    
    <h3>4.1 Droit d'accès des personnes filmées</h3>
    <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-6 my-6">
      <p className="text-white font-medium mb-3">Important pour les opérateurs</p>
      <p className="text-sm mb-3">
        En tant qu'opérateur du système de vidéosurveillance, vous êtes responsable de traitement. 
        Les personnes filmées ont le droit de demander l'accès aux images les concernant.
      </p>
      <p className="text-sm">
        OhmVision facilite ce processus via la fonction « Recherche par période » permettant 
        d'extraire les séquences pertinentes à communiquer au demandeur.
      </p>
    </div>

    <h3>4.2 Exercice des droits (utilisateurs OhmVision)</h3>
    <p>
      Pour exercer vos droits concernant votre compte OhmVision, utilisez l'une des méthodes suivantes :
    </p>
    <ul>
      <li><strong>Interface :</strong> Section Paramètres → Données personnelles</li>
      <li><strong>API :</strong> Endpoints /api/gdpr/* (documentation disponible)</li>
      <li><strong>Email :</strong> <a href="mailto:dpo@ohmtronic.fr">dpo@ohmtronic.fr</a></li>
    </ul>

    <h2>Article 5 – Mesures Techniques et Organisationnelles</h2>
    
    <h3>5.1 Sécurité technique</h3>
    <div className="grid md:grid-cols-2 gap-4 my-6">
      <div className="bg-white/5 rounded-xl p-4">
        <h4 className="text-white font-medium mb-2">Chiffrement</h4>
        <ul className="text-sm space-y-1">
          <li>• TLS 1.3 pour les communications</li>
          <li>• AES-256 pour le stockage</li>
          <li>• Chiffrement de bout en bout (option)</li>
        </ul>
      </div>
      <div className="bg-white/5 rounded-xl p-4">
        <h4 className="text-white font-medium mb-2">Authentification</h4>
        <ul className="text-sm space-y-1">
          <li>• Hachage bcrypt (coût 12)</li>
          <li>• Support 2FA/MFA</li>
          <li>• Tokens JWT signés</li>
        </ul>
      </div>
      <div className="bg-white/5 rounded-xl p-4">
        <h4 className="text-white font-medium mb-2">Infrastructure</h4>
        <ul className="text-sm space-y-1">
          <li>• Isolation réseau (VPC)</li>
          <li>• Pare-feu applicatif (WAF)</li>
          <li>• Détection d'intrusion (IDS)</li>
        </ul>
      </div>
      <div className="bg-white/5 rounded-xl p-4">
        <h4 className="text-white font-medium mb-2">Sauvegarde</h4>
        <ul className="text-sm space-y-1">
          <li>• Sauvegardes quotidiennes chiffrées</li>
          <li>• Réplication géographique UE</li>
          <li>• Tests de restauration réguliers</li>
        </ul>
      </div>
    </div>

    <h3>5.2 Mesures organisationnelles</h3>
    <ul>
      <li><strong>Formation :</strong> Personnel formé à la protection des données</li>
      <li><strong>Habilitations :</strong> Principe du moindre privilège</li>
      <li><strong>Confidentialité :</strong> Clauses contractuelles avec employés et sous-traitants</li>
      <li><strong>Audit :</strong> Revue annuelle des processus</li>
    </ul>

    <h2>Article 6 – Sous-traitance</h2>
    
    <h3>6.1 Liste des sous-traitants</h3>
    <table className="w-full text-sm">
      <thead>
        <tr>
          <th>Sous-traitant</th>
          <th>Finalité</th>
          <th>Localisation</th>
          <th>Garanties</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Hetzner Online</td>
          <td>Hébergement</td>
          <td>Allemagne/Finlande</td>
          <td>ISO 27001, RGPD Art.28</td>
        </tr>
        <tr>
          <td>Stripe</td>
          <td>Paiements</td>
          <td>Irlande (UE)</td>
          <td>PCI-DSS, SCCs</td>
        </tr>
        <tr>
          <td>Brevo</td>
          <td>Emails</td>
          <td>France</td>
          <td>ISO 27001, RGPD</td>
        </tr>
        <tr>
          <td>Sentry</td>
          <td>Monitoring</td>
          <td>UE</td>
          <td>SCCs, SOC 2</td>
        </tr>
      </tbody>
    </table>

    <h3>6.2 Contrats de sous-traitance</h3>
    <p>
      Tous nos sous-traitants ont signé des accords de traitement de données (DPA) conformes 
      à l'article 28 du RGPD, incluant des clauses de confidentialité, de sécurité et d'audit.
    </p>

    <h2>Article 7 – Notification des Violations</h2>
    <p>
      En cas de violation de données personnelles, OhmTronic s'engage à :
    </p>
    <ul>
      <li>Notifier la CNIL dans les 72 heures si la violation présente un risque</li>
      <li>Informer les personnes concernées si le risque est élevé</li>
      <li>Documenter l'incident et les mesures correctives</li>
      <li>Informer les clients concernés dans les meilleurs délais</li>
    </ul>

    <h2>Article 8 – Contact DPO</h2>
    <div className="bg-white/5 rounded-xl p-6 my-6">
      <p className="text-white font-medium mb-3">Délégué à la Protection des Données</p>
      <p className="mb-1">Email : <a href="mailto:dpo@ohmtronic.fr">dpo@ohmtronic.fr</a></p>
      <p className="mb-1">Courrier : DPO OhmTronic, 15 Rue de l'Innovation, 75001 Paris</p>
      <p className="text-sm text-gray-400 mt-3">
        Délai de réponse : 30 jours maximum (conformément au RGPD)
      </p>
    </div>

  </LegalLayout>
);

// ============================================
// 6. POLITIQUE CONTRACTUELLE (ABONNEMENTS)
// ============================================
export const ContractPolicyPage = () => (
  <LegalLayout title="Politique Contractuelle" icon={FiClipboard} lastUpdate="20 janvier 2026">
    
    <div className="bg-white/5 rounded-xl p-6 mb-8">
      <p className="text-sm">
        Cette politique détaille les conditions spécifiques applicables aux contrats d'abonnement 
        OhmVision. Elle complète les CGU et CGV.
      </p>
    </div>

    <h2>Article 1 – Formation du Contrat</h2>
    
    <h3>1.1 Étapes de souscription</h3>
    <ol>
      <li><strong>Offre :</strong> Présentation des formules sur le site ohmvision.fr</li>
      <li><strong>Commande :</strong> Sélection de l'offre et saisie des informations</li>
      <li><strong>Acceptation :</strong> Validation des CGU, CGV et de la présente politique</li>
      <li><strong>Paiement :</strong> Règlement sécurisé ou démarrage de l'essai gratuit</li>
      <li><strong>Confirmation :</strong> Email récapitulatif avec numéro de contrat</li>
    </ol>

    <h3>1.2 Documents contractuels</h3>
    <p>Le contrat est constitué par ordre de prévalence :</p>
    <ol>
      <li>Les conditions particulières (devis signé pour ENTERPRISE)</li>
      <li>La présente Politique Contractuelle</li>
      <li>Les Conditions Générales de Vente</li>
      <li>Les Conditions Générales d'Utilisation</li>
    </ol>

    <h3>1.3 Preuve du contrat</h3>
    <p>
      Les registres informatisés d'OhmTronic constituent la preuve des communications, 
      commandes et paiements intervenus entre les parties.
    </p>

    <h2>Article 2 – Période d'Essai</h2>
    
    <h3>2.1 Conditions</h3>
    <div className="bg-ohm-cyan/10 border border-ohm-cyan/30 rounded-xl p-6 my-6">
      <p className="text-white font-medium mb-3">Essai gratuit de 14 jours</p>
      <ul className="space-y-2 text-sm">
        <li>• Accès complet aux fonctionnalités de l'offre sélectionnée</li>
        <li>• Aucun moyen de paiement requis pour démarrer</li>
        <li>• Annulation possible à tout moment sans frais</li>
        <li>• Notification 3 jours avant la fin de l'essai</li>
        <li>• Conversion automatique en abonnement payant sauf annulation</li>
      </ul>
    </div>

    <h3>2.2 Fin de la période d'essai</h3>
    <p>
      À l'issue des 14 jours, sans action de votre part et si un moyen de paiement a été enregistré, 
      l'abonnement payant démarre automatiquement. Vous recevrez une facture pour la première période.
    </p>

    <h2>Article 3 – Exécution du Contrat</h2>
    
    <h3>3.1 Activation du service</h3>
    <p>
      Le service est activé immédiatement après la confirmation du paiement (ou le démarrage de l'essai). 
      Les identifiants de connexion sont envoyés par email.
    </p>

    <h3>3.2 Obligations d'OhmTronic</h3>
    <ul>
      <li>Fournir le service conformément à l'offre souscrite</li>
      <li>Assurer la disponibilité selon les SLA de l'offre</li>
      <li>Maintenir la sécurité et la confidentialité des données</li>
      <li>Informer des maintenances programmées (48h à l'avance)</li>
      <li>Fournir un support selon le niveau de l'offre</li>
    </ul>

    <h3>3.3 Obligations du Client</h3>
    <ul>
      <li>Régler les factures aux échéances convenues</li>
      <li>Utiliser le service conformément aux CGU</li>
      <li>Maintenir à jour ses informations de contact et de facturation</li>
      <li>Respecter les limites de l'offre (nombre de caméras, utilisateurs)</li>
      <li>Assurer la conformité réglementaire de son installation</li>
    </ul>

    <h2>Article 4 – Modifications du Contrat</h2>
    
    <h3>4.1 Changement d'offre (upgrade)</h3>
    <p>
      Le passage à une offre supérieure est effectif immédiatement. La différence de prix est 
      calculée au prorata de la période restante.
    </p>

    <h3>4.2 Changement d'offre (downgrade)</h3>
    <p>
      Le passage à une offre inférieure prend effet au prochain renouvellement. Les fonctionnalités 
      non incluses dans la nouvelle offre seront désactivées. Les données excédant les quotas 
      seront conservées 30 jours pour permettre leur export.
    </p>

    <h3>4.3 Modification des conditions par OhmTronic</h3>
    <p>
      OhmTronic peut modifier les conditions contractuelles. Les modifications substantielles 
      sont notifiées 30 jours à l'avance. Le Client peut résilier sans frais s'il refuse les 
      nouvelles conditions.
    </p>

    <h2>Article 5 – Suspension du Service</h2>
    
    <h3>5.1 Suspension pour impayé</h3>
    <p>
      En cas de non-paiement, après une relance restée sans effet pendant 7 jours, OhmTronic 
      peut suspendre l'accès au service. La suspension n'exonère pas du paiement des sommes dues.
    </p>

    <h3>5.2 Suspension pour violation</h3>
    <p>
      En cas de violation grave des CGU (utilisation illicite, atteinte à la sécurité), OhmTronic 
      peut suspendre immédiatement l'accès, avec notification au Client.
    </p>

    <h3>5.3 Réactivation</h3>
    <p>
      La réactivation intervient après régularisation de la situation (paiement, engagement de conformité). 
      Des frais de réactivation de 50€ peuvent s'appliquer.
    </p>

    <h2>Article 6 – Résiliation</h2>
    
    <h3>6.1 Résiliation par le Client</h3>
    <table className="w-full text-sm">
      <thead>
        <tr>
          <th>Type d'abonnement</th>
          <th>Modalités</th>
          <th>Prise d'effet</th>
          <th>Remboursement</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Mensuel</td>
          <td>À tout moment</td>
          <td>Fin du mois en cours</td>
          <td>Non</td>
        </tr>
        <tr>
          <td>Annuel</td>
          <td>À tout moment</td>
          <td>Fin de l'année en cours</td>
          <td>Non (sauf consommateur)</td>
        </tr>
        <tr>
          <td>Essai gratuit</td>
          <td>À tout moment</td>
          <td>Immédiat</td>
          <td>N/A</td>
        </tr>
      </tbody>
    </table>

    <h3>6.2 Résiliation par OhmTronic</h3>
    <p>OhmTronic peut résilier le contrat dans les cas suivants :</p>
    <ul>
      <li>Non-paiement persistant (30 jours après mise en demeure)</li>
      <li>Violation grave des CGU</li>
      <li>Cessation d'activité de la société</li>
      <li>Demande d'une autorité compétente</li>
    </ul>

    <h3>6.3 Effets de la résiliation</h3>
    <ul>
      <li>Désactivation de l'accès au service</li>
      <li>Conservation des données 30 jours (export possible)</li>
      <li>Suppression définitive des données après 30 jours</li>
      <li>Envoi d'une facture de clôture si applicable</li>
    </ul>

    <h2>Article 7 – Dispositions Spécifiques aux Professionnels</h2>
    
    <h3>7.1 Contrats ENTERPRISE</h3>
    <p>
      Les contrats ENTERPRISE font l'objet de conditions particulières négociées incluant :
    </p>
    <ul>
      <li>SLA personnalisé avec pénalités</li>
      <li>Interlocuteur dédié (Account Manager)</li>
      <li>Conditions de paiement adaptées</li>
      <li>Clauses de confidentialité renforcées</li>
      <li>Audit de sécurité annuel</li>
    </ul>

    <h3>7.2 Facturation professionnelle</h3>
    <ul>
      <li>Factures conformes aux exigences légales et fiscales</li>
      <li>TVA applicable selon le lieu d'établissement</li>
      <li>Paiement sous 30 jours date de facture (sauf accord)</li>
      <li>Possibilité de règlement par virement ou prélèvement</li>
    </ul>

    <h2>Article 8 – Dispositions Spécifiques aux Consommateurs</h2>
    
    <h3>8.1 Droit de rétractation</h3>
    <p>
      Les consommateurs bénéficient d'un droit de rétractation de 14 jours conformément au 
      Code de la consommation (voir CGV Article 4).
    </p>

    <h3>8.2 Résiliation anticipée</h3>
    <p>
      Les consommateurs peuvent résilier un abonnement annuel à tout moment après les 12 premiers 
      mois, avec effet au terme du mois en cours.
    </p>

    <h3>8.3 Médiation</h3>
    <p>
      En cas de litige, les consommateurs peuvent recourir gratuitement au médiateur de la 
      consommation désigné dans les CGV.
    </p>

    <h2>Article 9 – Confidentialité</h2>
    <p>
      Les parties s'engagent à maintenir confidentielles les informations échangées dans le 
      cadre du contrat, notamment les données techniques, commerciales et financières.
    </p>

    <h2>Article 10 – Force Majeure</h2>
    <p>
      Ni OhmTronic ni le Client ne seront responsables d'un manquement à leurs obligations 
      en cas de force majeure telle que définie par l'article 1218 du Code civil.
    </p>

    <h2>Article 11 – Cession</h2>
    <p>
      Le Client ne peut céder le contrat sans l'accord écrit d'OhmTronic. OhmTronic peut céder 
      le contrat à toute société du groupe ou à un acquéreur de son activité.
    </p>

    <h2>Article 12 – Intégralité</h2>
    <p>
      Les documents contractuels constituent l'intégralité de l'accord entre les parties et 
      remplacent tout accord antérieur portant sur le même objet.
    </p>

  </LegalLayout>
);

// Export par défaut pour compatibilité
export default {
  LegalMentionsPage,
  PrivacyPage,
  CGUPage,
  CGVPage,
  GDPRPage,
  ContractPolicyPage
};
