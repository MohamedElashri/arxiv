let titles_area = [
    "B^+", "meson", "charm", "strange", "top", "quark", "CP violation", 
    "CKM", "lepton", "hadron", "flavor", "FCNC", "rare decay",
    "tracking", "reconstruction", "detector", "trigger",
    "transformer", "attention", "LLM", "foundation model", "large language model"
];

let titles_type = [
    "flavor", "phenomenology", "Collider", "Neural", "Machine-Learning",
    "LHCb", "RNN", "Jet", "ATLAS", "CMS", "embedding", "GPU", "FPGA",
    "real-time", "online", "offline", "distributed", "parallel",
    "inference", "fine-tuning", "few-shot", "zero-shot"
];

let titles = titles_area + titles_type;

let authors_array = [
    "LHCb", "CMS", "ATLAS", "ALICE", "Belle II", "BaBar",
    "FAIR", "FNAL", "KEK", "IHEP", "DESY"
];

let meetings = [
    // HEP
    "CHEP", "ICHEP", "Beauty", "CKM", "Flavor", "EPS-HEP", "Lepton-Photon",
    // ML/AI
    "ICLR", "ICML", "NeurIPS", "AAAI", "IJCAI",
    // Computing
    "ACAT", "Computing in High Energy Physics", "Real Time Processing",
    "IEEE NSS/MIC", "FPGA for Machine Learning"
];

let start = meetings.shift();
let meetings_rg = meetings.reduce(|sum, v| sum + "|" + v, start);
let meetings_rg = "(" + meetings_rg + ")([\\s'-]*\\d+)?";
let start = titles.shift();
let title_rg = titles.reduce(|sum, v| sum + "|" + v, start);
let start = authors_array.shift();
let authors_rg = authors_array.reduce(|sum, v| sum + "|" + v, start);
export title_rg;
export authors_rg;
export meetings_rg;
