PLAN_ETAPES_DASHBOARD = """
Projet : Cross-Asset Market Regime Monitor – Plan détaillé étape par étape (version texte à conserver)

0) Cadrage & objectifs
- Clarifier l’objectif : visualiser la performance par classe d’actifs à travers des régimes de marché, avec term structures (equity, or, pétrole, blé, dollar) et courbes de taux US/DE. :contentReference[oaicite:0]{index=0}
- Définir la cible : traders / PMs. :contentReference[oaicite:1]{index=1}
- Choisir le périmètre initial de données et la fréquence d’update quotidienne. :contentReference[oaicite:2]{index=2}

1) Sidebar (panneau de filtres)
- Contrôle période : slider de dates + presets (YTD/1Y/5Y/Max).
- Sélection classes d’actifs : Equity (SPY), USD (DXY), Or, WTI (CL=F), Blé (ZW=F), TIPS, UST 10Y (^TNX), Bund 10Y, VIX.
- Granularité : jour / semaine / mois.
- Sélecteur de régime : All / Growth↑↓ × Inflation↑↓ (choix exclusif).
- Options d’affichage : échelle lin/log, base 100, lissage (moyenne mobile).

2) Chargement & préparation des données
- Télécharger / charger localement les séries (yfinance + éventuelles sources macro).
- Harmoniser les index (dates), gérer jours fériés, forward-fill puis drop NA.
- Construire rendements, perf cumulée base 1/base 100, derniers prix.
- Stocker la date/heure de dernière mise à jour (pour affichage en en-tête).
- Mettre en cache (cache données) avec invalidation quotidienne. :contentReference[oaicite:3]{index=3}

3) Indicateurs clés (features)
- Growth proxy (ex. indicateur synthétique ou série macro simple).
- Inflation proxy (ex. CPI/TIPS breakeven simplifié si dispo).
- Volatilité : vol réalisée (rolling stdev annualisée) + VIX (niveau).
- Taux & courbes : niveaux UST (2Y/5Y/10Y/30Y) et Bund 10Y + pentes 2s10s/5s30s. :contentReference[oaicite:4]{index=4}
- Table des KPI (perf YTD/1M/1W, vol 30j, drawdown courant).

4) Détection et attribution des régimes de marché
- Définir une matrice 2×2 Growth↑↓ × Inflation↑↓ (seuils via quantiles ou moyennes mobiles).
- Calculer un label de régime pour chaque date (et éventuellement une proba).
- Préparer une timeline colorée des régimes à superposer aux graphiques. :contentReference[oaicite:5]{index=5}

5) Vue Performance (main panel 1)
- Courbes de performance normalisée par actif sur la fenêtre sélectionnée.
- Heatmap des performances par actif × périodes (1W/1M/3M/YTD/1Y).
- Bar chart des contributions/dispersion sur la période courante.

6) Vue Volatilité & Risque (main panel 2)
- Courbes de vol réalisée (rolling) par actif.
- Lecture conjointe SPY vs VIX (graphes superposés ou axes secondaires).
- Tableau des drawdowns (max DD historique + DD courant) par actif.

7) Vue Devises & USD (main panel 3)
- USD index : niveau, perf multi-horizons.
- Corrélations roulantes USD avec SPY, Or, WTI (fenêtre glissante configurable).

8) Vue Matières Premières (main panel 4)
- Or, WTI, Blé : niveaux, perfs, momentum court/long terme simple.
- Comparatif inter-commodities sur la même période.

9) Vue Taux & Inflation (main panel 5)
- Courbes de taux (US & DE) : 2Y/5Y/10Y/30Y (snapshots + time series). :contentReference[oaicite:6]{index=6}
- Pentes (2s10s, 5s30s) vs performance des classes d’actifs.
- Indicateurs d’inflation : proxy (CPI/Tip breakeven) résumé et tendance.

10) Term Structures (structures à terme) (main panel 6)
- Courbes de futures par classe (Equity, Or, WTI, Blé, USD) à la date sélectionnée.
- Suivi de la pente (contango/backwardation) dans le temps (ex. métrique simple).
- Comparaison de snapshots de term structure à différentes dates. :contentReference[oaicite:7]{index=7}

11) Vue Régimes
- Matrice 2×2 Growth↑↓ × Inflation↑↓ avec brève définition des seuils.
- Performance moyenne par actif dans chaque régime (bar chart/heatmap).
- Timeline des régimes avec couleurs sur l’axe du temps pour repérer les transitions. :contentReference[oaicite:8]{index=8}

12) Corrélations & co-mouvements
- Matrice de corrélations (fenêtre glissante) pour les actifs sélectionnés.
- Séries de corrélations clés (SPY–USD, SPY–VIX, Or–USD, WTI–SPY).
- Indication des changements de signe/points de rupture.

13) Tableau “Données & Statistiques”
- Tableau récapitulatif : dernier prix, perfs (1W/1M/3M/YTD/1Y), vol 30j, max DD, corrélation SPY.
- Bouton de téléchargement CSV/Parquet de la vue filtrée.

14) Annotations & événements
- Marqueurs d’événements majeurs (prints d’inflation, décisions de banques centrales, chocs pétrole).
- Légendes/notes brèves par graphique (sources, méthodo courte).

15) Qualité & monitoring des données
- Avertissements si NAs / trous détectés sur la période visible.
- Badge “source + horodatage” par série (ex. Yahoo/FRED + timestamp). :contentReference[oaicite:9]{index=9}
- Journalisation minimale des erreurs de chargement.

16) Expérience utilisateur (UX)
- Mémorisation des filtres (session state).
- Bouton “Reset” global.
- Tabs pour organiser les vues (Performance / Vol / Devises / Commodities / Taux & Inflation / Term Structures / Régimes / Corrélations).
- Mode clair/sombre cohérent et responsive desktop. :contentReference[oaicite:10]{index=10}

17) Tests fonctionnels & qualité
- Vérifier chaque graphique et filtre (période, actifs, régimes). :contentReference[oaicite:11]{index=11}
- Contrôler cohérence data vs source (échantillons).
- Tester performance (cache, downsampling si très longue période).
- Gérer symboles capricieux (fallback propre).

18) Déploiement & intégration
- Héberger l’app Streamlit sur serveur/plateforme compatible.
- Intégrer sur la homepage via iframe/lien (public, sans login). :contentReference[oaicite:12]{index=12}
- Configurer la mise à jour automatique toutes les 24h (cron/Action + cache). :contentReference[oaicite:13]{index=13}

19) Documentation & maintenance
- README : objectif, dépendances, lancement, sources, limites.
- Changelog succinct (version du dashboard en pied de page).
- Roadmap : HMM/Markov switching, facteurs (value/growth; cy/def), scénarios de stress. :contentReference[oaicite:14]{index=14}

Fin du plan.
"""

if __name__ == "__main__":
    print(PLAN_ETAPES_DASHBOARD)
