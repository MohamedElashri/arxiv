let titles_area = ["B^+", "B meson", "meson", "neural-network", "pv", "primary-vertex", "monopole", "four-body"];
let titles_type = ["flavor", "phenomenology", "Collider", "Neural", "Machine-Learning", "LHCb"];
let titles = titles_area + titles_type;
let authors_array = ["CMS", "ATLAS", "Alice", "Bell II", "Elashri"];

let meetings = [
    // AI
    "AAAI", "AAMAS", "ACM MM", "AISTATS", "ALT", "CEC", "ECAI", "FUZZ IEEE", "GECCO", "ICANN", "ICAPS", "ICCBR", "ICONIP", "ICRA", "ICTAI", "IJCAI", "IJCNN", "IROS", "KR", "KSEM", "SIGGRAPH", "STOC", "UAI", "PPSN", "PRICAI", "TAAI",
    // ML
    "ACML", "AISTATS", "ECML", "ICLR", "ICML", "ML4H", "NeurIPS", "NIPS", "UAI"
    // HEP
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
