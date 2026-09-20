# ArchI3D

ArchI3D reconstruit automatiquement un jumeau numerique 3D d'une maison a partir de photos
annotees, d'une image aerienne et de plans 2D, puis pose des questions progressives et
intelligentes (materiaux, isolation, vitrages, equipements) pour affiner un moteur d'analyse
thermique/energetique simplifie. L'utilisateur ne modelise jamais manuellement : l'IA construit
et enrichit le modele a partir des donnees disponibles.

Cette iteration livre le **scaffolding + une premiere tranche verticale du MVP** : un flux
complet (upload -> analyse vision -> generation 3D -> questionnaire -> rapport thermique) qui
tourne de bout en bout, avec des heuristiques volontairement simples plutot qu'une
implementation exhaustive.

## Sommaire

- [Architecture globale](#architecture-globale)
- [Stack technique et justifications](#stack-technique-et-justifications)
- [Modele de donnees hierarchique](#modele-de-donnees-hierarchique)
- [Approche de reconstruction 3D](#approche-de-reconstruction-3d)
- [Ecran camera integre (cap boussole)](#ecran-camera-integre-cap-boussole)
- [Fournisseur IA (Gemini / Claude)](#fournisseur-ia-gemini--claude)
- [Stockage des fichiers](#stockage-des-fichiers)
- [Geolocalisation, orientation et donnees climatiques](#geolocalisation-orientation-et-donnees-climatiques)
- [Bibliotheque de valeurs thermiques par defaut](#bibliotheque-de-valeurs-thermiques-par-defaut)
- [Inertie thermique](#inertie-thermique)
- [Authentification (Google OAuth)](#authentification-google-oauth)
- [Lancer le projet en local](#lancer-le-projet-en-local)
- [Deploiement](#deploiement)
- [Limitations connues et compromis V1](#limitations-connues-et-compromis-v1)
- [Roadmap V2](#roadmap-v2)
- [Outils / MCP potentiellement necessaires](#outils--mcp-potentiellement-necessaires)

## Architecture globale

Monorepo avec deux applications independantes :

```
ArchI3D/
├── frontend/   React + Vite + TypeScript (DDD), deploye sur GitHub Pages
├── backend/    Python + FastAPI (DDD par module domaine), conteneurise (Docker)
└── .github/workflows/   CI/CD (build+deploy frontend, tests backend)
```

Le frontend est un SPA statique qui ne fait **jamais** de calcul lourd : il appelle l'API du
backend pour l'upload, l'analyse vision IA, la generation 3D et le calcul thermique. Le backend
est un service dedie, conteneurise, pense pour heberger tout ce qui est CPU/IO-intensif (vision,
OpenCV, generation de mesh, calcul thermique).

### Backend - organisation par domaine (DDD adapte a FastAPI)

```
backend/app/
├── auth/                 authentification Google OAuth 2.0 + sessions JWT httpOnly
├── ingestion/            upload direct (plan, image aerienne, photos, factures)
├── vision_analysis/      analyse IA des photos (materiaux, ouvertures, isolation, equipements)
├── model_generation/     heuristique plan 2D -> pieces -> export GLB (Three.js)
├── annexes/              agregat Annex (abris, garages, dependances) - independant du Building
├── material_invoices/    OCR + extraction IA des factures/fiches techniques materiaux
├── thermal_engine/       moteur de calcul simplifie + bibliotheque de valeurs par defaut
├── questionnaire/        moteur a regles du questionnaire progressif
├── geolocation/          geocodage d'adresse + altitude (Nominatim, Open-Meteo)
├── climate/              abstraction ClimateDataProvider (Open-Meteo, point d'integration PVGIS)
├── ai_provider/          abstraction du fournisseur IA (Gemini par defaut, Claude optionnel)
├── storage/              abstraction de stockage fichiers (local par defaut, Cloudflare R2)
├── ocr/                  extraction de texte (labels de plan, factures)
├── projects/             etat persistant d'un projet (JSON sur disque, cf compromis V1) +
│                         dependance get_owned_project_state (controle d'acces, cf Authentification)
└── shared/                schemas Pydantic partages (modele hierarchique du batiment)
```

### Frontend - organisation DDD

```
frontend/src/
├── domain/          entites (Building, Room, Wall, User...), interfaces repository
├── application/     use-cases (orchestrent les repositories, aucun fetch direct ici)
├── infrastructure/  implementations HTTP des repositories (ApiClient + Http*Repository)
├── presentation/    pages (LoginPage, ProjectListPage, ProjectPage), composants React, hooks UI
└── shared/           config (import.meta.env), types communs
```

Aucun `fetch` direct dans un composant React : tout passe par
`presentation -> application/use-cases -> domain/repositories (interface) <- infrastructure/http (implementation)`.

## Stack technique et justifications

| Choix | Justification |
|---|---|
| **Frontend** : React + Vite + TypeScript strict | Stack par defaut du projet. Vite = build rapide compatible GitHub Pages (site statique). |
| **Viewer 3D** : React Three Fiber + drei | Integration React idiomatique de Three.js, chargement GLTF/GLB natif (`useGLTF`). |
| **Backend** : Python + FastAPI | Les besoins V1 (OpenCV, OCR, generation de mesh 3D avec trimesh, calcul scientifique) sont nativement couverts par l'ecosysteme Python (`opencv-python`, `pytesseract`, `trimesh`, `numpy`). FastAPI offre une DX proche de Express/Nest avec validation Pydantic integree, tres adaptee a l'upload de fichiers et au typage strict des schemas hierarchiques. |
| **Persistance V1** : JSON par projet sur disque | Pas de base de donnees en V1 pour rester simple (scaffolding, pas de multi-utilisateur reel) - cf compromis ci-dessous. |
| **Design system frontend** : shadcn/ui (Radix + Tailwind CSS) | Decide par le PO. Integration manuelle (CLI shadcn interactive non automatisable dans ce sandbox) - primitives copiees dans `frontend/src/presentation/components/ui/` (button, input, label, card, select, slider, badge), `components.json` present pour permettre `npx shadcn add <composant>` par la suite. |

## Modele de donnees hierarchique

Le batiment est modelise de facon hierarchique, coherente entre le backend (Pydantic,
`backend/app/shared/schemas.py`) et le frontend (TypeScript, `frontend/src/domain/model/Building.ts`) :

```
Building
├── latitude / longitude / altitudeM        (geolocalisation, cf app/geolocation)
├── northOffsetDeg                          (orientation Nord, widget compas frontend)
├── SolarInstallation[]                     (panneaux solaires existants, detection vision IA ou saisie)
├── thermalInertiaClass                     (leger/moyen/lourd, calcule a chaque rapport thermique)
└── Floor[]  (RDC, Etage 1, Combles, Sous-sol...)
    └── Room[]
        ├── name / suggestedName / nameConfirmed   (nom propose par l'IA, toujours editable)
        ├── boundingBox                             (position/emprise issues de l'heuristique)
        ├── Wall[]  (exterior | interior | floor | roof)
        │   ├── constructionType                    (cle vers le catalogue illustre)
        │   ├── azimuthDeg / cardinalOrientation     (orientation de facade - pret pour V2)
        │   ├── MaterialLayer[]                      (source: vision_estimate | invoice | user_input)
        │   └── Opening[]                            (fenetres/portes, type de vitrage, Uw)
        └── Equipment[]                              (chauffage, ventilation, ECS...)

Annex[]  (agregat distinct : abri de jardin, garage, dependance - cf backend/app/annexes)
├── offsetXM / offsetYM / widthM / depthM / heightM / rotationDeg   (repere local partage avec Building)
├── isConditioned                                                   (enveloppe thermique minimale si vrai)
└── Wall[]                                                          (reutilise le meme schema que Room, si conditionnee)
```

**SolarInstallation** (rattachee a `Building`) : surface approximative, inclinaison estimee et
orientation cardinale d'une installation solaire existante, detectee automatiquement depuis
l'image aerienne (`POST /projects/{id}/aerial-image/analyze`, cf `app/vision_analysis`) ou saisie
manuellement. Se relie au point d'integration PVGIS prevu en V2 (potentiel solaire).

**Annex** (agregat independant, pas un champ sur `Building`) : structure secondaire sur la
parcelle avec sa propre geometrie simplifiee, positionnee dans le **meme repere local (metres)**
que les pieces du batiment - ce qui lui permet d'apparaitre directement a cote du batiment
principal dans l'export GLB (`backend/app/model_generation/glb_export.py` regenere la scene a
chaque creation/modification/suppression d'annexe). Flux V1 **manuel** (l'utilisateur ajoute et
positionne une annexe via `AnnexPanel`) - la detection automatique depuis l'image aerienne est un
point d'integration vision IA identifie mais non implemente (V2), sur le meme principe que la
detection des panneaux solaires.

Le nom de chaque piece est **toujours suggere par l'IA** (OCR des labels lus sur le plan 2D +
analyse vision des photos associees) mais reste editable/a valider par l'utilisateur via le
questionnaire (`name_confirmed: false` tant que non valide).

> **Compromis assume** : les types TypeScript et les schemas Pydantic sont maintenus **a la
> main** en parallele (pas de generation automatique depuis l'OpenAPI). Pour eviter les divergences
> de casse JSON, tous les schemas Pydantic exposes par l'API heritent de `CamelModel`
> (`backend/app/shared/base.py`), qui serialise automatiquement en camelCase - le frontend recoit
> donc directement des cles alignees avec ses types TS. Une generation de types (ex. `openapi-typescript`)
> serait pertinente des que l'API se stabilise (V2).

## Approche de reconstruction 3D

Approche **hybride structuree**, pas de photogrammetrie brute (pas de COLMAP/NeRF en V1) :

1. **Plans 2D -> topologie** : heuristique OpenCV (`backend/app/model_generation/plan_heuristic.py`)
   qui binarise le plan, detecte les contours "trous" (pieces) a l'interieur du contour exterieur
   du batiment, et lit le label de chaque piece par OCR (`pytesseract`) pour suggerer un nom/type
   (cuisine, chambre, salon...).
2. **Image aerienne -> emprise/orientation globale** : uploadee et associee au projet en V1 ;
   l'exploitation automatique (emprise au sol precise, alignement Nord) est une amelioration V2 -
   pour l'instant l'orientation se regle manuellement via le widget compas (`northOffsetDeg`).
3. **Photos -> enrichissement vision IA** : materiaux apparents, types d'ouvertures, etat apparent
   de l'isolation, equipements visibles (`backend/app/vision_analysis`).
4. **Export 3D** : chaque piece devient une boite (`trimesh.creation.box`) positionnee selon sa
   bounding box et son etage, exportee en GLB (`backend/app/model_generation/glb_export.py`) et
   chargee dans le viewer React Three Fiber.

Ce choix donne une topologie propre et fiable pour le calcul thermique, au prix d'un rendu moins
photorealiste qu'une reconstruction photogrammetrique classique - **c'est un choix assume**.

**Simplification V1 explicite** : l'heuristique ne segmente pas les murs par facade individuelle
(mitoyennete non detectee) - chaque piece recoit une seule paroi "exterior" agregeant tout son
perimetre, ce qui **surestime** les deperditions des pieces interieures. Documente dans les
`assumptions` retournees par le moteur thermique.

## Ecran camera integre (cap boussole)

Pour les photos exterieures, `UploadPanel` propose (en plus du choix de fichier classique) un
bouton **"Prendre une photo (camera + boussole)"** qui ouvre un ecran plein ecran
(`frontend/src/presentation/components/CameraCapture/CameraCapture.tsx`) :

- Flux video live via `navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })`
  (camera arriere en priorite).
- Bouton de capture : dessine la frame video courante sur un `<canvas>` cache, puis exporte un
  blob JPEG (`canvas.toBlob`) transforme en `File` - meme flux d'upload que le reste de l'app.
- **Cap boussole en direct**, superpose a l'ecran : `event.webkitCompassHeading` sur iOS/Safari
  (deja exprime en degres 0-360 depuis le Nord), ou calcul approximatif `(360 - event.alpha) % 360`
  depuis l'evenement `deviceorientationabsolute` (`deviceorientation` avec `absolute: true` en
  repli) sur les autres navigateurs.
- **iOS 13+** : `DeviceOrientationEvent.requestPermission()` doit etre appelee depuis un geste
  utilisateur explicite (bouton "Activer la boussole" affiche a l'ecran) - sans ca, l'API ne
  renvoie aucun evenement, c'est une contrainte Apple, pas un choix d'implementation.
- Le cap releve au moment de la capture est envoye avec la photo (`compassHeadingDeg`, champ
  optionnel sur `PhotoFile` cote backend).

**Repli propre** : la camera integree est detectee au chargement (`getUserMedia` disponible ?) et
n'est proposee que si le navigateur la supporte ; le choix de fichier classique (avec
`capture="environment"` natif du navigateur comme confort supplementaire) reste **toujours**
disponible en parallele, y compris si la camera/boussole echoue en cours d'usage (permission
refusee, pas de camera...) - aucune fonctionnalite n'est bloquee par l'absence de ces API.

**Point d'integration vision IA** : si une photo exterieure porte un `compassHeadingDeg`, il est
transmis comme indice au prompt d'analyse (`backend/app/vision_analysis/service.py`), qui peut
alors suggerer `suggestedCardinalOrientation` (N/NE/E/SE/S/SW/W/NW) en le corroborant avec l'image.
**Non branche automatiquement sur une `Wall` precise** en V1 (les photos sont associees a une
piece, pas encore a une facade/paroi individuelle - meme limitation que la segmentation par
facade evoquee plus haut) - point d'integration prepare, a completer en V2.

**Limitations connues** (non testees sur device reel dans ce sandbox, cf section Limitations) :
- Precision de la boussole **approximative** : pas de calibration, pas de compensation de la
  rotation ecran (`screen.orientation.angle`), sensible aux perturbations magnetiques locales
  (structures metalliques, aimants...). A traiter comme un indice, pas une mesure fiable.
- Support navigateur variable : `deviceorientationabsolute` n'existe pas partout (notamment
  Safari desktop/iOS, qui n'expose que `webkitCompassHeading` via `deviceorientation`) ; certains
  navigateurs desktop n'exposent aucune boussole (comportement attendu : indicateur "Boussole
  indisponible", capture photo toujours fonctionnelle sans le cap).
- **Necessite HTTPS** (contexte securise) pour `getUserMedia` et les evenements d'orientation -
  deja le cas en production (GitHub Pages + backend HTTPS) ; en dev local, `localhost` beneficie
  d'une exception navigateur standard, donc pas de configuration TLS locale necessaire.

## Fournisseur IA (Gemini / Claude)

L'analyse vision des photos, la generation de questions et l'extraction des factures materiaux
passent par une abstraction `AIProvider` (`backend/app/ai_provider/base.py`) avec deux
implementations :

- **Gemini (par defaut, gratuit)** - `GeminiProvider`, via `google-generativeai`, modele
  `gemini-2.0-flash`.
- **Claude (optionnel, payant)** - `ClaudeProvider`, via `anthropic`, active en mettant
  `AI_PROVIDER=claude` et `ANTHROPIC_API_KEY` dans `.env`.

Le choix se fait via la variable d'environnement `AI_PROVIDER` (`backend/app/ai_provider/factory.py`).
Aucune cle n'est hardcodee dans le code - tout passe par `.env` (voir `backend/.env.example`).

**Cle Gemini par utilisateur** : chaque utilisateur connecte peut renseigner sa propre cle API
Gemini **gratuite** (creee sur https://ai.google.dev) dans la page **Parametres** de l'app
(`PUT/DELETE /auth/me/gemini-key`). Elle est chiffree au repos (Fernet, `SECRETS_ENCRYPTION_KEY`)
et **jamais renvoyee en clair** au frontend (seul un apercu masque type `AIza...xyz` est affiche).
`GeminiProvider` utilise en priorite la cle de l'utilisateur courant, avec repli sur la variable
d'environnement globale `GEMINI_API_KEY` si absente - pratique pour le dev local, mais en
production chaque utilisateur doit normalement creer et renseigner la sienne (voir
`app/ai_provider/factory.py` pour la logique de resolution, et sa docstring pour une limitation
connue du SDK `google-generativeai` sous forte charge concurrente multi-utilisateurs).
On a deliberement **evite d'elargir les scopes OAuth Google** pour tenter de provisionner cette
cle automatiquement : cela necessiterait une verification de l'application par Google, un mauvais
rapport effort/benefice pour un usage personnel/demo.

## Stockage des fichiers

Abstraction `StorageBackend` (`backend/app/storage/base.py`) avec deux implementations :

- **Local (par defaut)** - ecrit sur le disque du conteneur backend, servi via `/files`. Zero
  dependance externe, ideal pour le developpement local.
- **Cloudflare R2 (optionnel)** - API compatible S3, **tier gratuit jusqu'a 10 Go/mois**. Active
  via `STORAGE_BACKEND=r2` + `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`,
  `R2_BUCKET_NAME` (voir `backend/.env.example`). Choisi plutot que Supabase Storage pour rester
  sur une API S3 standard (compatible `boto3`, pas de SDK proprietaire supplementaire).

> Attention : en production, si le backend tourne sur plusieurs instances/redemarrages sans
> volume persistant, `STORAGE_BACKEND=local` perd les fichiers a chaque redeploiement - passer
> a R2 est recommande des la sortie du cadre "demo locale".

**Arborescence par projet** : toute cle de stockage suit la convention
`{ownerId}/{projectId}/{plans|photos|aerial|invoices|model}/...` (`build_project_key`,
`backend/app/storage/base.py`), garantissant une isolation physique des fichiers par utilisateur
et par projet des le stockage. Les 5 sous-dossiers sont crees automatiquement des la creation du
projet (`ProjectStore.create` appelle `StorageBackend.ensure_project_structure`) - concretement
pour `LocalDiskStorage` (creation reelle des repertoires) ; no-op pour `R2Storage` puisqu'un
stockage objet S3-compatible n'a pas de vraie notion de dossier vide, le prefixe apparait des le
premier fichier uploade dans cette "arborescence".

## Geolocalisation, orientation et donnees climatiques

- **Geocodage d'adresse** : Nominatim/OpenStreetMap (gratuit, sans cle) -
  `backend/app/geolocation/service.py`. Ajustement manuel possible (pin sur carte - a implementer
  cote UI carte en V2, l'endpoint `PATCH /projects/{id}/building/location` existe deja).
- **Altitude** : Open-Meteo Elevation API (gratuit, sans cle).
- **Orientation Nord** : widget compas frontend (`BuildingLocationPanel`) reglant
  `Building.northOffsetDeg`. Chaque paroi a des champs `azimuthDeg`/`cardinalOrientation` prets a
  etre calcules automatiquement (`backend/app/shared/geo.py`) des que la segmentation par facade
  sera disponible (V2 - cf limitations ci-dessus).
- **Donnees climatiques** : abstraction `ClimateDataProvider` (`backend/app/climate/base.py`),
  implementee via **Open-Meteo** (historique meteo gratuit, sans cle) pour calculer un DJU
  (degres-jours unifies) reel a partir de la position geographique, avec repli automatique sur une
  constante nationale si l'API est indisponible (sandbox hors-ligne, quota...). Le moteur thermique
  utilise deja ce DJU reel des que `Building.latitude/longitude` sont renseignes.
  **PVGIS** (irradiation solaire par orientation/inclinaison, JRC europeen, gratuit sans cle) n'est
  **pas encore appele** - point d'integration identifie mais non implemente (V2), utile pour les
  apports solaires bioclimatiques/passifs.

## Bibliotheque de valeurs thermiques par defaut

`backend/app/thermal_engine/reference_data/` contient des donnees structurees JSON :

- `materials.json` - conductivite thermique (lambda) indicative par materiau
- `glazing.json` - coefficients Uw indicatifs par type de vitrage
- `thermal_bridges.json` - coefficients lineiques psi indicatifs par type de jonction
- `construction_types.json` - **catalogue illustre** des typologies de construction courantes
  (ossature bois, ITE, monomur, parpaing+ITI, brique, pierre), avec description et Uw par defaut.
  Les images sont des **placeholders SVG generes** (`assets/*.svg`) - a remplacer par de vraies
  photos/schemas illustratifs en V2. Ce catalogue est affiche dans le questionnaire pour
  l'identification visuelle par l'utilisateur, et sert de reference de comparaison pour l'analyse
  vision IA.
- `thermal_inertia.json` - poids leger/moyen/lourd par typologie de construction et par materiau,
  utilise pour calculer la classe d'inertie thermique (cf section dediee ci-dessous).

**Toutes ces valeurs sont indicatives**, issues d'ordres de grandeur usuels - **ce n'est pas une
source reglementaire certifiee** (pas de connexion a une base Th-Bat/RE2020 officielle en V1).
Le rapport thermique retourne systematiquement un champ `assumptions` listant explicitement
toutes les hypotheses de calcul utilisees pour rester transparent.

## Inertie thermique

Le rapport thermique calcule automatiquement une **classe d'inertie thermique simplifiee a 3
niveaux** (leger/moyen/lourd), inspiree de l'approche RE2020 sans en reprendre la methode
complete (5 classes normees Th-I, avec un Cm en J/m2.K par zone) - cf
`backend/app/thermal_engine/inertia.py`.

**Deux facteurs, de nature tres differente :**

1. **Parois structurelles (dominant, seul facteur reellement norme)** - derive automatiquement de
   la masse surfacique approximative des materiaux/typologies des parois exposees cote interieur
   (murs exterieurs, planchers, toiture) : si une `MaterialLayer` precise est renseignee (vision,
   facture, saisie utilisateur), son materiau prime ; sinon, la typologie de construction de la
   paroi (`Wall.constructionType`, cf catalogue illustre) sert de repli (ex : ITE -> masse dense
   exposee cote interieur -> "lourd" ; ossature bois/ITI -> masse dense isolee ou absente ->
   "leger"). Score moyen pondere par surface -> classe retenue (seuils dans
   `thermal_inertia.json`).
2. **Mobilier/elements massifs (secondaire, QUALITATIF)** - une question du questionnaire
   ("elements massifs importants : cheminee en pierre, poele de masse, chape beton apparente,
   mobilier massif en bois ?") et/ou des indices detectes par l'analyse vision des photos
   (nouveau champ `heavyThermalMassElementsDetected` sur `PhotoAnalysis`) peuvent faire basculer
   la classe calculee a l'etape 1 d'un cran vers le haut (leger -> moyen, moyen -> lourd).
   **Important - distinction toujours visible dans les `assumptions` du rapport** : ce facteur est
   une **correction indicative uniquement**. Les methodes reglementaires RE2020/RT ne
   comptabilisent **pas** le mobilier dans le calcul officiel d'inertie, seulement les parois -
   ce N'EST PAS une donnee d'entree certifiee, juste un indice qualitatif optionnel.

**Integration au calcul du besoin de chauffage : volontairement NON appliquee.** L'inertie reduit
en realite la consommation via un effet de dephasage/amortissement (meilleure utilisation des
apports solaires et internes), mais le moteur actuel est un calcul **statique** (coefficient de
deperdition x DJU), sans notion de dynamique temporelle ni d'apports. Appliquer un facteur
correctif arbitraire sur le kWh/m²/an aurait ete un calcul non fonde. Le champ
`thermalInertiaClass` est donc calcule et expose dans le rapport (a titre informatif), mais
**n'influence pas** `estimatedKwhPerM2PerYear`. Le vrai point d'integration - documente ici plutot
qu'improvise - necessiterait soit une methode a facteur d'utilisation des apports dependant de
l'inertie (type Th-C-E simplifiee), soit une **simulation thermique dynamique (STD)** : cf
roadmap V2.

## Authentification (Google OAuth)

Les projets contiennent des donnees sensibles (photos interieures, factures) : l'acces est
**obligatoirement authentifie**. Flow OAuth 2.0 "Authorization Code" standard avec Google,
implemente dans `backend/app/auth/` :

- `GET /auth/google/login` - redirige vers l'ecran de consentement Google (avec un `state`
  anti-CSRF pose en cookie court-terme).
- `GET /auth/google/callback` - echange le code d'autorisation contre des tokens, **verifie
  serveur** l'ID token Google (signature, emetteur, expiration, et surtout `audience` = notre
  propre `GOOGLE_CLIENT_ID`, via la bibliotheque officielle `google-auth` - pas de confiance
  aveugle dans le contenu du token), cree ou retrouve l'utilisateur (agregat `User` : id, email,
  googleSub, displayName, createdAt - persiste dans `storage/_users/users.json`), pose une session
  applicative puis redirige vers `FRONTEND_URL`.
- `POST /auth/logout` - efface la session.
- `GET /auth/me` - utilisateur courant (401 si non authentifie).

**Session** : JWT signe (HS256, `SESSION_SECRET`) pose en cookie **httpOnly** (inaccessible en
JavaScript). Le token Google lui-meme n'est **jamais** stocke ni renvoye au frontend - uniquement
notre propre session. Le frontend appelle l'API avec `credentials: "include"` sur chaque requete
pour que ce cookie soit envoye/recu.

**Controle d'acces** : chaque `Project` porte un champ `ownerId`. Tous les endpoints qui operent
sur un projet existant passent par la dependance FastAPI partagee
`app.projects.dependencies.get_owned_project_state`, qui verifie l'authentification (401 si
absente) PUIS la propriete (`403` si le projet appartient a quelqu'un d'autre). `GET /projects`
ne retourne que les projets du proprietaire courant. Aucun endpoint de donnees de projet n'est
accessible sans session valide.

### Etape par etape : creer des identifiants OAuth Google (gratuit)

A faire toi-meme sur https://console.cloud.google.com (l'agent ne peut pas creer ces identifiants
a ta place) :

1. Cree un projet Google Cloud (ou reutilise un projet existant).
2. Menu **APIs & Services > Ecran de consentement OAuth** : type "External" (sauf si tu as un
   Google Workspace), renseigne un nom d'app + email de contact. En mode "Test", ajoute ton propre
   compte Google comme utilisateur de test (suffisant pour le developpement, pas besoin de
   validation Google pour un usage personnel/interne).
3. Menu **APIs & Services > Identifiants > Creer des identifiants > ID client OAuth**.
4. Type d'application : **Application Web**.
5. **Origines JavaScript autorisees** :
   - Dev local : `http://localhost:5173`
   - Production : `https://<ton-user>.github.io`
6. **URI de redirection autorisees** (doit correspondre EXACTEMENT a `GOOGLE_REDIRECT_URI`) :
   - Dev local : `http://localhost:8000/auth/google/callback`
   - Production : `https://<ton-backend>.onrender.com/auth/google/callback` (ou l'URL reelle de
     ton backend deploye - Render, Fly.io...)
7. Recupere le **Client ID** et le **Client Secret** generes, renseigne-les dans `backend/.env`
   (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`) - ne jamais les commiter.
8. Genere un `SESSION_SECRET` aleatoire :
   `python3 -c "import secrets; print(secrets.token_urlsafe(48))"`
9. Genere un `SECRETS_ENCRYPTION_KEY` (utilise pour chiffrer les cles Gemini personnelles) :
   `python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`

### Configuration cookie selon l'environnement

| Environnement | `SESSION_COOKIE_SAMESITE` | `SESSION_COOKIE_SECURE` | Pourquoi |
|---|---|---|---|
| Dev local (frontend/backend sur `localhost`, ports differents) | `lax` | `false` | Meme "site" au sens des cookies (le port ne compte pas) - `Lax` suffit, `Secure` impossible sans HTTPS local. |
| Production (frontend GitHub Pages, backend sur un autre domaine) | `none` | `true` | Domaines differents = cross-site : `SameSite=None` est **obligatoire** pour que le cookie parte en fetch cross-origine, et le navigateur exige `Secure` (HTTPS) des que `SameSite=None` est utilise. |

Ne jamais deployer en production avec `SESSION_COOKIE_SAMESITE=none` et `SESSION_COOKIE_SECURE=false`
: le cookie serait silencieusement rejete par le navigateur (connexion qui semble "ne pas
persister").

## Lancer le projet en local

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate   # ou l'equivalent de votre environnement
pip install -r requirements.txt
cp .env.example .env
# Editer .env : renseigner GEMINI_API_KEY (cle gratuite sur https://ai.google.dev)
# ET les identifiants Google OAuth + SESSION_SECRET (cf section Authentification ci-dessus) -
# sans ca, l'app reste bloquee sur l'ecran de connexion.
uvicorn app.main:app --reload
```

L'API est servie sur `http://localhost:8000` (docs interactives sur `/docs`).

**Dependance systeme** : l'OCR (labels de plan, factures) necessite le binaire `tesseract`
installe sur la machine (`apt install tesseract-ocr tesseract-ocr-fra` sur Debian/Ubuntu, deja
inclus dans le `Dockerfile`). En son absence, l'OCR renvoie une chaine vide et les pipelines
appelants retombent sur une alternative (nom de piece generique, extraction facture vide) au lieu
de planter.

> Note sandbox de developpement : `pip`/`venv` n'etaient pas disponibles dans l'environnement
> d'execution de cet agent au moment du scaffolding - le backend a ete valide par compilation
> (`py_compile`) et verification statique des imports, **pas par une execution reelle**. A tester
> en priorite lors de la prochaine session de dev.

### Frontend

```bash
cd frontend
cp .env.example .env   # VITE_API_BASE_URL=http://localhost:8000
npm install
npm run dev
```

L'application est servie sur `http://localhost:5173`. Verifie deja avec succes dans cette
iteration : `npm install`, `npm run build` (build de prod) et `npx eslint .` passent sans erreur.

## Deploiement

### Frontend -> GitHub Pages

`.github/workflows/frontend-deploy.yml` build et deploie automatiquement `frontend/` sur GitHub
Pages a chaque push sur `main`. Definir le secret de repo `VITE_API_BASE_URL` (URL publique du
backend deploye). Active "GitHub Pages" dans Settings > Pages avec la source "GitHub Actions".

### Backend -> conteneur Docker (Render / Fly.io / autre)

```bash
cd backend
docker build -t archi3d-backend .
docker run -p 8000:8000 --env-file .env archi3d-backend
```

Pour Render ou Fly.io : connecter le repo, pointer le service sur `backend/Dockerfile`, definir les
variables d'environnement listees dans `backend/.env.example` (au minimum `GEMINI_API_KEY`).
Prevoir un volume persistant monte sur `/app/storage` si `STORAGE_BACKEND=local`, ou configurer
Cloudflare R2 pour eviter toute perte de fichiers entre redeploiements.

`.github/workflows/backend-ci.yml` execute `ruff check` et `pytest` a chaque push touchant
`backend/` (pas de deploiement automatique configure - a brancher sur l'hebergeur choisi).

## Limitations connues et compromis V1

- **Pas de base de donnees** - etat de projet persiste en JSON sur disque
  (`backend/app/projects/store.py`). Suffisant pour un scaffold mono-utilisateur, a remplacer par
  une vraie base (Postgres/SQLite) des que le multi-utilisateur ou la concurrence devient un besoin.
- **Heuristique de vectorisation de plan simplifiee** - detection de contours basique, pas de
  reconnaissance fine des murs/portes/fenetres reels ; toute piece est traitee comme entierement
  exterieure (cf section reconstruction 3D). Fonctionne pour une demo mais sous-estime/surestime
  les deperditions reelles selon la configuration du logement.
- **Pas de detection automatique d'echelle** sur le plan - l'utilisateur renseigne manuellement
  un ratio metres/pixel (`ModelPanel`).
- **PVGIS non integre** - seul le point d'integration (`ClimateDataProvider`) existe. La
  production existante des `SolarInstallation` detectees n'est pas encore deduite du bilan
  energetique du moteur thermique (a faire en meme temps que l'integration PVGIS, V2).
- **Detection automatique des annexes non implementee** - flux manuel uniquement en V1 (ajout via
  `AnnexPanel`). Le point d'integration vision IA existe (meme principe que la detection des
  panneaux solaires) mais n'est pas appele automatiquement.
- **Environnement de dev sans pip/venv/internet verifie** - le backend n'a pas pu etre execute
  reellement pendant ce scaffolding (cf section "Lancer le projet en local").
- **UX mobile/tablette non testee sur device reel** - le layout (Tailwind, `flex-wrap`, grilles
  responsives) a ete revu pour eviter le scroll horizontal, mais aucun test manuel sur un vrai
  smartphone/tablette n'a pu etre fait dans cet environnement de scaffolding (idem pour l'ecran
  camera integre, cf section dediee ci-dessous). A verifier en priorite (tailles de cible tactile
  des boutons `shadcn/ui` par defaut - 36px, un peu sous les 44-48px recommandes - gestes tactiles
  du viewer 3D `OrbitControls`, clavier virtuel qui masque des champs de formulaire...).
- **Limitation connue du SDK Gemini sous charge concurrente multi-utilisateurs** - `genai.configure()`
  est global au process Python, pas par-requete ; deux utilisateurs avec des cles differentes
  faisant une requete simultanee peuvent en theorie interferer (cf docstring
  `backend/app/ai_provider/factory.py`). Sans consequence pour un usage personnel/demo V1.

## Roadmap V2

- Vectorisation fine des plans (murs reels, portes/fenetres individuelles, segmentation par
  facade -> calcul automatique de `azimuthDeg`/`cardinalOrientation`).
- Connexion a des bases reglementaires officielles (RE2020/RT complet, methode Th-BCE, DPE).
- Integration PVGIS (irradiation solaire par facade) pour l'analyse bioclimatique/passive.
- Detection automatique de l'emprise/orientation depuis l'image aerienne (vision IA).
- Widget carte interactif pour l'ajustement manuel du pin de geolocalisation.
- Integration Google Drive (OAuth) comme methode d'ingestion alternative a l'upload direct -
  necessiterait une integration OAuth Google Drive API cote backend, **distincte** du connecteur
  Google Drive de Claude Code (qui ne concerne que les sessions de developpement, pas
  l'application ArchI3D elle-meme).
- Generation de types partages frontend/backend depuis l'OpenAPI (reduire le risque de
  divergence des schemas maintenus a la main).
- Vraie base de donnees (Postgres/SQLite) a la place du JSON sur disque.
- Remplacement des placeholders SVG du catalogue de construction par de vraies photos/schemas.
- Integration de l'inertie thermique au calcul du besoin de chauffage (facteur d'utilisation des
  apports dependant de l'inertie type Th-C-E simplifiee, ou simulation thermique dynamique STD) -
  cf section "Inertie thermique" pour le detail de ce qui est deja calcule (la classe) vs ce qui
  reste a brancher (l'effet reel sur le kWh/m²/an).
- Rattacher automatiquement une `SolarInstallation`/le cap boussole d'une photo a une `Wall`
  precise des que la segmentation par facade (V2, ci-dessus) existera.

## Outils / MCP potentiellement necessaires

Ces besoins ont ete identifies mais **volontairement non installes/supposes disponibles** -
a demander a l'utilisateur si pertinent :

- **MCP Cloudflare R2 / S3** - pour gerer le bucket de stockage directement depuis l'agent
  (creation de bucket, verification de quotas) plutot qu'en configuration manuelle.
- **MCP cadastre / donnees geospatiales officielles** (ex. IGN, cadastre.gouv.fr) - utile en V2
  pour ameliorer la precision de l'emprise/orientation derivee de l'image aerienne.
- **MCP base de donnees thermiques reglementaires officielle** (Th-Bat, DPE ADEME) - necessaire
  quand la V2 remplacera les valeurs indicatives actuelles par des donnees certifiees.
- **Acces a un environnement Python avec pip/venv fonctionnels** - non disponible dans le sandbox
  de cette session, a verifier avant la prochaine iteration de developpement backend.
