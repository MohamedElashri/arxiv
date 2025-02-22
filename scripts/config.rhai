// Physics-related terms (flavor physics, hadrons, experiments)
let titles_physics = [
    // B physics and flavor
    "B^+", "B^0", "B_s", "\\bB\\b", "meson", "hadron", "flavor", "CP violation",
    "charm", "strange", "beauty", "bottom", "rare decay", "mixing", "oscillation",
    "CKM", "Unitarity", "penguin", "box diagram", "form factor",
    
    // Experimental signatures
    "pv", "primary-vertex", "secondary-vertex", "track", "reconstruction",
    "trigger", "efficiency", "acceptance", "resolution", "luminosity",
    "cross-section", "branching ratio", "BR", "yield", "significance",
    "four-body", "three-body", "monopole", "resonance",
    
    // Detectors and experiments
    "detector", "calorimeter", "RICH", "muon system", "tracking"
];

// ML/Software terms
let titles_ml_sw = [
    // Machine Learning
    "neural network", "deep learning", "transformer", "attention mechanism",
    "RNN", "LSTM", "GNN", "graph neural", "autoencoder", "classification",
    "regression", "optimization", "hyperparameter", "training", "inference",
    "Machine-Learning", "Neural", "artificial intelligence", "reinforcement",
    "supervised", "unsupervised", "transfer learning", "few-shot", "zero-shot",
    
    // Software/Computing
    "GPU", "FPGA", "parallel", "distributed", "pipeline", "framework",
    "real-time", "online", "offline", "simulation", "Monte Carlo",
    "data acquisition", "DAQ", "storage", "database", "containerization",
    "workflow", "CI/CD", "deployment"
];

// Combine all title keywords using array concatenation
let titles = [];
for (item in titles_physics) { titles.push(item); }
for (item in titles_ml_sw) { titles.push(item); }

// Expanded list of relevant experiments and collaborations
let authors_array = [
    // Major experiments
    "LHCb", "CMS", "ATLAS", "ALICE", "Belle II", "BaBar", "BESIII",
    // Collaborations and institutes
    "CERN", "DESY", "SLAC", "KEK", "IHEP", "Fermilab",
    // Add your specific authors of interest
    "Elashri"
];

// Expanded list of relevant conferences
let meetings = [
    // Physics conferences
    "ICHEP", "Lepton Photon", "Beauty", "CKM", "Flavor Physics",
    "EPS-HEP", "PANIC", "LHCP", "HCP",
    
    // ML/Computing conferences
    "ICLR", "ICML", "NeurIPS", "AAAI", "IJCAI", "MLSys",
    "CHEP", "ACAT", "ROOTCom", "vCHEP",
    
    // Software/Computing
    "SC", "HPDC", "CCGrid", "IPDPS", "Euro-Par"
];

// Generate regex patterns
let start = meetings.shift();
let meetings_rg = meetings.reduce(|sum, v| sum + "|" + v, start);
let meetings_rg = "(" + meetings_rg + ")([\\s'-]*\\d+)?";

start = titles.shift();
let title_rg = titles.reduce(|sum, v| sum + "|" + v, start);

start = authors_array.shift();
let authors_rg = authors_array.reduce(|sum, v| sum + "|" + v, start);

export title_rg;
export authors_rg;
export meetings_rg;
