PLAN_DASHBOARD = """
Market Dashboard – Plan des éléments (version texte)

1) En-tête & configuration
- Titre, sous-titre, date de dernière mise à jour
- Sélecteur de thème clair/sombre

2) Panneau de filtres (sidebar)
- Période (slider de dates, presets YTD/1Y/5Y/Max)
- Classes d’actifs: Equity (SPY), USD (DXY), Or, WTI, Blé, TIPS, UST 10Y, Bund 10Y, VIX
- Granularité: jour/semaine/mois
- Régime de marché: All / Growth↑↓ × Inflation↑↓
- Options: échelle log, base 100, lissage

3) Bloc “État du marché” (overview)
- Tuiles KPI: Perf YTD par actif, Vol 30j, UST10Y & Bund10Y niveaux, Breakeven TIPS, niveau VIX
- Indicateurs synthétiques: Growth proxy, Inflation proxy, Slope 2s10s

4) Vue Performance
- Courbes de performance normalisée par actif
- Heatmap des performances par actif × période
- Bar chart contributions/dispersion sur la période sélectionnée

5) Vue Volatilité & Risque
- Courbe de vol réalisée (rolling, annualisée) par actif
- VIX vs actions (lecture conjointe)
- Drawdowns maximums par actif (top 5) et drawdown courant

6) Vue Devises & USD
- USD index: niveau et performances multi-horizons
- Corrélation roulante USD avec SPY, Or, WTI

7) Vue Matières Premières
- Or, WTI, Blé: niveaux et perfs
- Momentum court/long terme (comparatif simple)

8) Vue Taux & Inflation
- Courbes de taux US & DE: points 2Y/5Y/10Y/30Y
- Pentes: 2s10s, 5s30s
- Indicateurs d’inflation: TIPS/TIP, breakeven, CPI proxy (résumé)

9) Term Structures (structures à terme)
- Courbes de futures par classe (Equity, Or, WTI, Blé, USD) – snapshot à la date sélectionnée
- Évolution de la pente/contango vs backwardation dans le temps

10) Régimes de marché
- Matrice 2×2: Growth↑↓ × Inflation↑↓ (définition courte)
- Performance moyenne par actif dans chaque régime
- Timeline colorée des régimes sur la période sélectionnée

11) Corrélations & Co-mouvements
- Matrice de corrélations (fenêtre glissante)
- Paires clés: SPY–USD, SPY–VIX, Or–USD, WTI–SPY

12) Tableau “Données & Statistiques”
- Dernier prix, perf 1W/1M/3M/YTD/1Y, vol 30j, drawdown, corrélation SPY
- Bouton de téléchargement CSV de la vue filtrée

13) Annotations & Événements
- Marqueurs sur les graphiques: publications d’inflation, décisions de banques centrales, chocs pétrole
- Légende/notes brèves par graphique

14) Qualité des données
- Alerte NAs/jours manquants par série
- Badge “source/horodatage” (Yahoo, FRED, etc.) par série

15) Paramètres & Préférences utilisateur
- Mémoire des filtres (dernier état)
- Bouton “Reset” global

16) Pied de page
- Sources de données
- Version du dashboard et changelog succinct

17) Itérations futures (parking lot)
- Modélisation avancée des régimes (HMM/Markov switching)
- Facteurs (value/growth, cycliques/défensives)
- Scénarios de risques (stress tests simples)
"""

# Pour afficher le plan dans la console si besoin :
if __name__ == "__main__":
    print(PLAN_DASHBOARD)
