# Contrat d’acceptation

| ID | Fonction/parcours | Surface cible | Niveau cible | Résultat observable | Preuve constatée | Test dans la cible | Surface constatée | Niveau constaté | Effets/restauration | Statut | Limite/blocage | Mesure |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A-001 | Profil complet inspiré du modèle | github-profile | interface | Portrait ASCII, calendrier, statistiques, outils, projets et contact visibles | résultat=OK visible; référence=https://github.com/thorsenbuilds | Ouverture et défilement du profil public, six cartes observées | github-profile | interface | mutation voulue : README et six SVG publiés, anciennes cartes inutilisées | VALIDÉ | | |
| A-002 | Actualisation quotidienne | github-actions | interface | Six cartes et leurs données publiques régénérées et publiées | résultat=OK visible; référence=https://github.com/thorsenbuilds/thorsenbuilds/actions/runs/42856281049 | Workflow exécuté après publication du README, succès et cartes visibles sur le profil | github-actions | interface | mutation voulue : cartes et clés de cache mises à jour par Actions | VALIDÉ | | |
