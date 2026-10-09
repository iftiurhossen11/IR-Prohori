// ============ USER MEMORY SYSTEM ============

const MEMORY_KEY = "ir_prohori_memory";

function getMemory() {
    const data = localStorage.getItem(MEMORY_KEY);
    return data ? JSON.parse(data) : {};
}

function saveMemory(memory) {
    localStorage.setItem(MEMORY_KEY, JSON.stringify(memory));
}

// ============ BAD VALUES TO REJECT ============
const BAD_VALUES = [
    "ki", "কি", "কে", "ke", "what", "who", "where", "when",
    "how", "which", "is", "are", "the", "a", "an",
    "নাম", "name", "আমি", "ami", "my", "your", "আমার", "amar"
];

function isBadValue(value) {
    const cleaned = value.trim().toLowerCase();
    if (!cleaned) return true;
    if (BAD_VALUES.includes(cleaned)) return true;
    if (cleaned.length < 2) return true;
    return false;
}

// ============ MEMORY PATTERNS ============
// Each pattern must capture a real name/value, not question words.

const MEMORY_PATTERNS = [
    {
        key: "name",
        patterns: [
            // "আমার নাম X" (explicit statement)
            /আমার\s*নাম\s+(?:হলো|হল|is|:)?\s*([A-Za-z\u0980-\u09FF][A-Za-z\u0980-\u09FF\s\.]{1,40}?)(?:\s*[।\.\?]|$)/i,
            // "my name is X"
            /my\s+name\s+is\s+([A-Za-z][A-Za-z\s\.]{1,40}?)(?:\s*[\.\?]|$)/i,
            // "amar nam X"
            /amar\s+nam\s+(?:holo|hol|is|:)?\s*([A-Za-z][A-Za-z\s\.]{1,40}?)(?:\s*[\.\?]|$)/i
        ],
        label: "name"
    },
    {
        key: "favorite_color",
        patterns: [
            /আমার\s*প্রিয়\s*রঙ\s+(?:হলো|হল|is|:)?\s*([A-Za-z\u0980-\u09FF\s]{2,20}?)(?:\s*[।\.\?]|$)/i,
            /my\s+favorite\s+color\s+is\s+([A-Za-z\s]{2,20}?)(?:\s*[\.\?]|$)/i,
            /amar\s+priyo\s+color\s+(?:holo|hol|is|:)?\s*([A-Za-z\s]{2,20}?)(?:\s*[\.\?]|$)/i
        ],
        label: "favorite color"
    },
    {
        key: "favorite_food",
        patterns: [
            /আমার\s*প্রিয়\s*খাবার\s+(?:হলো|হল|is|:)?\s*([A-Za-z\u0980-\u09FF\s]{2,30}?)(?:\s*[।\.\?]|$)/i,
            /my\s+favorite\s+food\s+is\s+([A-Za-z\s]{2,30}?)(?:\s*[\.\?]|$)/i
        ],
        label: "favorite food"
    },
    {
        key: "city",
        patterns: [
            /আমি\s+থাকি\s+([A-Za-z\u0980-\u09FF\s]{2,30}?)(?:\s*[।\.\?]|$)/i,
            /i\s+live\s+in\s+([A-Za-z\s]{2,30}?)(?:\s*[\.\?]|$)/i,
            /ami\s+thaki\s+([A-Za-z\s]{2,30}?)(?:\s*[\.\?]|$)/i
        ],
        label: "city"
    },
    {
        key: "study",
        patterns: [
            /আমি\s+পড়ি\s+([A-Za-z\u0980-\u09FF\s]{2,40}?)(?:\s*[।\.\?]|$)/i,
            /i\s+study\s+([A-Za-z\s]{2,40}?)(?:\s*[\.\?]|$)/i
        ],
        label: "study"
    },
    {
        key: "age",
        patterns: [
            /আমার\s*বয়স\s+(\d{1,2})/i,
            /my\s+age\s+is\s+(\d{1,2})/i,
            /amar\s+boyosh\s+(\d{1,2})/i
        ],
        label: "age"
    }
];

function detectAndSaveMemory(message) {
    const memory = getMemory();
    let changed = false;

    MEMORY_PATTERNS.forEach(pattern => {
        pattern.patterns.forEach(regex => {
            const match = message.match(regex);
            if (match && match[1]) {
                let value = match[1].trim();
                // Clean up trailing words
                value = value.replace(/\s+(আমি|ami|i|the|a|an|is|are|কি|ki|কে|ke)$/i, "").trim();

                if (!isBadValue(value)) {
                    memory[pattern.key] = {
                        value: value,
                        label: pattern.label,
                        savedAt: new Date().toISOString()
                    };
                    changed = true;
                }
            }
        });
    });

    if (changed) saveMemory(memory);
    return changed;
}

function getMemoryContext() {
    const memory = getMemory();
    const keys = Object.keys(memory);
    if (keys.length === 0) return "";

    let lines = ["Known facts about the user:"];
    keys.forEach(k => {
        lines.push(`- ${memory[k].label}: ${memory[k].value}`);
    });
    return lines.join("\n");
}

function clearMemory() {
    localStorage.removeItem(MEMORY_KEY);
}