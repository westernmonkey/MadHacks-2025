module.exports = [
"[externals]/next/dist/compiled/next-server/app-route-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-route-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-route-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-route-turbo.runtime.dev.js"));

module.exports = mod;
}),
"[externals]/next/dist/compiled/@opentelemetry/api [external] (next/dist/compiled/@opentelemetry/api, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/@opentelemetry/api", () => require("next/dist/compiled/@opentelemetry/api"));

module.exports = mod;
}),
"[externals]/next/dist/compiled/next-server/app-page-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-page-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-unit-async-storage.external.js [external] (next/dist/server/app-render/work-unit-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-unit-async-storage.external.js", () => require("next/dist/server/app-render/work-unit-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-async-storage.external.js [external] (next/dist/server/app-render/work-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-async-storage.external.js", () => require("next/dist/server/app-render/work-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/shared/lib/no-fallback-error.external.js [external] (next/dist/shared/lib/no-fallback-error.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/shared/lib/no-fallback-error.external.js", () => require("next/dist/shared/lib/no-fallback-error.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/after-task-async-storage.external.js [external] (next/dist/server/app-render/after-task-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/after-task-async-storage.external.js", () => require("next/dist/server/app-render/after-task-async-storage.external.js"));

module.exports = mod;
}),
"[project]/src/lib/site-guardian.ts [app-route] (ecmascript)", ((__turbopack_context__) => {
"use strict";

// Site Guardian Core System Types and Utilities
__turbopack_context__.s([
    "INTERVENTION_SCRIPTS",
    ()=>INTERVENTION_SCRIPTS,
    "getAudioLevel",
    ()=>getAudioLevel
]);
const INTERVENTION_SCRIPTS = {
    ppeHat: "ATTENTION {WORKER}. YOU ARE IN A HARD HAT ZONE. STOP IMMEDIATELY AND PUT ON YOUR HELMET.",
    ppeVest: "SAFETY VIOLATION DETECTED. HIGH-VISIBILITY VEST REQUIRED IN THIS SECTOR. RETURN TO SAFETY ZONE IMMEDIATELY.",
    dangerZone: "WARNING! WARNING! YOU HAVE ENTERED THE EXCAVATOR SWING RADIUS. MOVE BACK. MOVE BACK NOW.",
    fallRisk: "ALERT. YOU ARE WORKING AT HEIGHT WITHOUT A CLIPPED HARNESS. ANCHOR YOUR LINE NOW.",
    distraction: "EYES UP. PHONE DOWN. PAY ATTENTION TO THE FORKLIFT CROSSING.",
    manDown: "MEDICAL EMERGENCY IN {ZONE}. CLEAR THE AREA. DISPATCH SITE_MEDIC."
};
function getAudioLevel(zone, violationType) {
    if (violationType === 'MAN_DOWN') return 'EMERGENCY_ALARM';
    if (zone === 'ZONE_RED') return 'AUDIO_LEVEL_3';
    if (zone === 'ZONE_BLACK') return 'AUDIO_LEVEL_3';
    if (zone === 'ZONE_YELLOW') return 'AUDIO_LEVEL_2';
    return 'AUDIO_LEVEL_1';
}
}),
"[project]/src/app/api/analyze-safety/route.ts [app-route] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "POST",
    ()=>POST
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/server.js [app-route] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$google$2f$generative$2d$ai$2f$dist$2f$index$2e$mjs__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/@google/generative-ai/dist/index.mjs [app-route] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$site$2d$guardian$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/lib/site-guardian.ts [app-route] (ecmascript)");
;
;
;
const GEMINI_API_KEY = process.env.GEMINI_API_KEY || 'AIzaSyDjnsgbo5yc2iroteGTz5qVe0DvruZxS2M';
const genAI = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$google$2f$generative$2d$ai$2f$dist$2f$index$2e$mjs__$5b$app$2d$route$5d$__$28$ecmascript$29$__["GoogleGenerativeAI"](GEMINI_API_KEY);
// MODEL CONFIGURATION - Update this based on your API key's available models
// Try: 'gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-1.5-pro', or 'gemini-pro'
// Visit /api/test-models to see which models work with your API key
const MODEL_NAME = 'gemini-2.5-flash';
async function POST(request) {
    try {
        const formData = await request.formData();
        const file = formData.get('video');
        const frameImage = formData.get('frame');
        const zoneMap = formData.get('zoneMap'); // Optional zone configuration
        if (!file && !frameImage) {
            return __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json({
                error: 'No video file or frame provided'
            }, {
                status: 400
            });
        }
        // Use the configured model name (defined at top of file)
        const model = genAI.getGenerativeModel({
            model: MODEL_NAME
        });
        let imageData;
        let mimeType;
        if (frameImage) {
            imageData = frameImage.replace(/^data:image\/\w+;base64,/, '');
            mimeType = 'image/jpeg';
        } else if (file) {
            const arrayBuffer = await file.arrayBuffer();
            const buffer = Buffer.from(arrayBuffer);
            imageData = buffer.toString('base64');
            mimeType = file.type || 'video/mp4';
            if (file.size > 20 * 1024 * 1024) {
                return __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json({
                    error: 'Video file too large. Please extract a frame on the client side or use a smaller video.'
                }, {
                    status: 400
                });
            }
        } else {
            return __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json({
                error: 'No valid file or frame provided'
            }, {
                status: 400
            });
        }
        // Site Guardian Analysis Prompt
        const prompt = `You are SITE GUARDIAN, an autonomous Computer Vision Safety System for construction sites.

Analyze this video frame with MAXIMUM SAFETY FOCUS. Identify ALL safety violations and potential hazards.

LAYER A - PPE COMPLIANCE:
For each person detected, check HEAD COVERINGS CAREFULLY:

CRITICAL: You must differentiate between:
1. HARD_HAT (safety helmet - compliant) - Usually white, yellow, or bright colors, smooth hard surface, often has a brim
2. TURBAN (head wrap - NOT compliant as hard hat replacement) - Cloth wrapped around head, various colors (often white, blue, black, orange), fabric texture visible, cylindrical or rounded shape, may show wrapped layers
3. MUSLIM_TAQIYAH (skullcap - NOT compliant) - Small rounded cap, covers top of head only, usually white or colored fabric, sits on top of head, does not cover sides/front/back fully
4. BARE_HEAD (NO head covering - VIOLATION) - Visible hair, scalp, or exposed head with no covering at all

IMPORTANT RULES:
- Only HARD_HAT counts as proper safety head protection
- TURBAN and MUSLIM_TAQIYAH are religious head coverings but NOT safety equipment
- Workers wearing turbans or taqiyah WITHOUT a hard hat over them are NON-COMPLIANT
- For BARE_HEAD, TURBAN, or MUSLIM_TAQIYAH (without hard hat), provide precise face/head coordinates

For face detection:
- Look for the entire head/face area (from hairline/forehead to chin)
- Include enough area to cover the face for privacy blurring
- Use percentages: x (left position), y (top position), width, height (all 0-100)
- For bare heads, the head area is typically in the upper-middle region of a person
- Face is usually 10-15% of image width and 12-18% of image height, positioned around 40-60% x and 10-25% y for standing person

Also check:
- SAFETY_VEST: High-visibility Yellow/Orange vest
- PROTECTIVE_BOOTS: Steel-toe boots
- SAFETY_GLASSES: If in grinding/cutting zones
- EAR_PROTECTION: If near loud machinery
- HARNESS: If working at height (>6ft)

LAYER B - ZONAL AWARENESS:
- ZONE_GREEN: Safe walkways, break areas
- ZONE_YELLOW: Active work areas (PPE Mandatory)
- ZONE_RED: High Danger (excavator swing radius, open pits, electrical panels)
- ZONE_BLACK: No-Go Zones (blast radius, chemical storage)

LAYER C - BEHAVIORAL ANALYSIS:
- RUSHING: Moving too fast near hazards (>2.5m/s)
- DISTRACTED: Head down + phone while walking
- MAN_DOWN: Horizontal posture for >5 seconds (MEDICAL EMERGENCY)
- ILLEGAL_RIDE: Riding on unauthorized machinery parts

For each violation detected, identify:
1. Worker description (clothing color, position)
2. Missing PPE items
3. Current zone location
4. Behavioral risks
5. Severity (CRITICAL/WARNING/CLEAR)
6. Face location coordinates (x, y, width, height as percentages 0-100)

IMPORTANT: For workers without hard hats, provide face coordinates so we can draw boxes to protect their privacy.

Respond in JSON format ONLY:
{
  "status": "🔴 CRITICAL DANGER" | "🟡 WARNING" | "🟢 CLEAR",
  "workers": [
    {
      "description": "Worker in blue shirt near excavator",
      "ppe": {
        "hardHat": true/false,
        "headCovering": "HARD_HAT" | "TURBAN" | "MUSLIM_TAQIYAH" | "BARE_HEAD" | "UNKNOWN",
        "safetyVest": true/false,
        "protectiveBoots": true/false,
        "safetyGlasses": true/false,
        "earProtection": true/false,
        "harness": true/false
      },
      "zone": "ZONE_GREEN" | "ZONE_YELLOW" | "ZONE_RED" | "ZONE_BLACK",
      "behavior": {
        "rushing": true/false,
        "distracted": true/false,
        "manDown": true/false,
        "illegalRide": true/false
      },
      "violations": ["MISSING_HARD_HAT", "IN_DANGER_ZONE", etc.],
      "faceCoordinates": {
        "x": 25.5,
        "y": 30.2,
        "width": 8.3,
        "height": 10.1
      }
    }
  ],
  "analysis": ["Bullet point 1", "Bullet point 2", "Bullet point 3"],
  "primaryViolation": "MISSING_HARD_HAT" | "DANGER_ZONE_ENTRY" | "MAN_DOWN" | etc.,
  "urgency": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
}

Format the analysis as an array of bullet points. Face coordinates are percentages (0-100) of image dimensions.`;
        const contentPart = {
            inlineData: {
                data: imageData,
                mimeType: mimeType
            }
        };
        console.log('SITE GUARDIAN: Analyzing frame for safety violations...');
        try {
            const result = await model.generateContent([
                prompt,
                contentPart
            ]);
            const response = await result.response;
            const text = response.text();
            console.log('SITE GUARDIAN: Analysis received');
            // Parse JSON response
            let analysisData;
            try {
                const jsonMatch = text.match(/\{[\s\S]*\}/);
                if (jsonMatch) {
                    analysisData = JSON.parse(jsonMatch[0]);
                } else {
                    throw new Error('No JSON found in response');
                }
            } catch (parseError) {
                console.error('Error parsing analysis:', parseError);
                // Fallback analysis
                // Convert text to bullet points if not already an array
                const bulletPoints = text.split('\n').filter((line)=>line.trim().length > 0);
                analysisData = {
                    status: '🟢 CLEAR',
                    workers: [],
                    analysis: bulletPoints.length > 0 ? bulletPoints : [
                        text
                    ],
                    primaryViolation: null,
                    urgency: 'LOW'
                };
            }
            // Generate intervention script
            const workers = (analysisData.workers || []).map((w)=>{
                const headCovering = w.ppe?.headCovering || (w.ppe?.hardHat === true ? 'HARD_HAT' : 'BARE_HEAD');
                const hasHardHat = headCovering === 'HARD_HAT';
                const needsPrivacyBlur = !hasHardHat && (headCovering === 'BARE_HEAD' || headCovering === 'TURBAN' || headCovering === 'MUSLIM_TAQIYAH');
                return {
                    description: w.description || 'Unknown worker',
                    ppe: {
                        hardHat: hasHardHat,
                        headCovering: headCovering,
                        safetyVest: w.ppe?.safetyVest || false,
                        protectiveBoots: w.ppe?.protectiveBoots || false,
                        safetyGlasses: w.ppe?.safetyGlasses || false,
                        earProtection: w.ppe?.earProtection || false,
                        harness: w.ppe?.harness || false
                    },
                    zone: w.zone || 'ZONE_YELLOW',
                    compliance: !w.violations || w.violations.length === 0,
                    behavior: w.behavior || {
                        rushing: false,
                        distracted: false,
                        manDown: false,
                        illegalRide: false
                    },
                    faceCoordinates: w.faceCoordinates || (needsPrivacyBlur ? {
                        // Default face area for privacy blur if head is uncovered
                        x: 45,
                        y: 10,
                        width: 10,
                        height: 12
                    } : undefined)
                };
            });
            // Determine action and voice output
            let action = 'MONITOR';
            let voiceOutput = '';
            let audioLevel;
            const violations = analysisData.primaryViolation || '';
            const urgency = analysisData.urgency || 'LOW';
            const worker = workers[0]; // Primary worker of concern
            if (analysisData.primaryViolation || urgency === 'CRITICAL' || urgency === 'HIGH') {
                if (violations.includes('MAN_DOWN') || worker?.behavior?.manDown) {
                    action = 'TRIGGER EMERGENCY_ALARM';
                    audioLevel = 'EMERGENCY_ALARM';
                    voiceOutput = __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$site$2d$guardian$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["INTERVENTION_SCRIPTS"].manDown.replace('{ZONE}', worker?.zone || 'SECTOR');
                } else if (violations.includes('MISSING_HARD_HAT') || !worker?.ppe.hardHat || worker?.ppe.headCovering === 'BARE_HEAD' || worker?.ppe.headCovering === 'TURBAN' || worker?.ppe.headCovering === 'MUSLIM_TAQIYAH') {
                    action = 'TRIGGER SCRIPT_PPE_HAT';
                    audioLevel = (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$site$2d$guardian$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["getAudioLevel"])(worker?.zone || 'ZONE_YELLOW', 'MISSING_HARD_HAT');
                    voiceOutput = __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$site$2d$guardian$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["INTERVENTION_SCRIPTS"].ppeHat.replace('{WORKER}', worker?.description || 'WORKER');
                } else if (violations.includes('MISSING_VEST') || !worker?.ppe.safetyVest) {
                    action = 'TRIGGER SCRIPT_PPE_VEST';
                    audioLevel = (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$site$2d$guardian$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["getAudioLevel"])(worker?.zone || 'ZONE_YELLOW', 'MISSING_VEST');
                    voiceOutput = __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$site$2d$guardian$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["INTERVENTION_SCRIPTS"].ppeVest;
                } else if (violations.includes('DANGER_ZONE') || worker?.zone === 'ZONE_RED') {
                    action = 'TRIGGER SCRIPT_DANGER_ZONE';
                    audioLevel = 'AUDIO_LEVEL_3';
                    voiceOutput = __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$site$2d$guardian$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["INTERVENTION_SCRIPTS"].dangerZone;
                } else if (violations.includes('FALL_RISK') || !worker?.ppe.harness && worker?.zone === 'ZONE_YELLOW') {
                    action = 'TRIGGER SCRIPT_FALL_RISK';
                    audioLevel = (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$site$2d$guardian$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["getAudioLevel"])(worker?.zone || 'ZONE_YELLOW', 'FALL_RISK');
                    voiceOutput = __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$site$2d$guardian$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["INTERVENTION_SCRIPTS"].fallRisk;
                } else if (worker?.behavior?.distracted) {
                    action = 'TRIGGER SCRIPT_DISTRACTION';
                    audioLevel = 'AUDIO_LEVEL_2';
                    voiceOutput = __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$site$2d$guardian$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["INTERVENTION_SCRIPTS"].distraction;
                } else {
                    action = 'TRIGGER AUDIO_LEVEL_1';
                    const analysisText = Array.isArray(analysisData.analysis) ? analysisData.analysis.join('. ') : analysisData.analysis || 'Safety violation detected';
                    voiceOutput = `SAFETY VIOLATION DETECTED. ${analysisText}`;
                }
            }
            // Convert analysis to array format (bullet points)
            let analysisBullets = [];
            if (Array.isArray(analysisData.analysis)) {
                analysisBullets = analysisData.analysis;
            } else if (typeof analysisData.analysis === 'string') {
                // Split by newlines or periods to create bullet points
                analysisBullets = analysisData.analysis.split(/\n|\. /).filter((point)=>point.trim().length > 0).map((point)=>point.trim().replace(/^[-•]\s*/, ''));
            } else {
                analysisBullets = [
                    'No issues detected'
                ];
            }
            const safetyAnalysis = {
                status: analysisData.status || '🟢 CLEAR',
                detected: workers,
                analysis: analysisBullets.length > 0 ? analysisBullets : [
                    'No issues detected'
                ],
                action: action,
                voiceOutput: voiceOutput || 'Area clear. Continue monitoring.',
                audioLevel: audioLevel,
                timestamp: new Date().toISOString()
            };
            return __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json(safetyAnalysis);
        } catch (geminiError) {
            console.error('SITE GUARDIAN API error:', geminiError);
            let errorMessage = 'Failed to analyze safety frame';
            if (geminiError.message) {
                errorMessage += `: ${geminiError.message}`;
            }
            if (geminiError.message?.includes('API_KEY')) {
                errorMessage = 'Invalid or missing Gemini API key. Please check your GEMINI_API_KEY environment variable.';
            } else if (geminiError.message?.includes('not found') || geminiError.message?.includes('404')) {
                // Model not found - provide clear instructions
                errorMessage = `Model "${MODEL_NAME}" not available with your API key. `;
                errorMessage += `Please update MODEL_NAME in src/app/api/analyze-safety/route.ts (line ~23) to one of: `;
                errorMessage += `gemini-1.5-flash, gemini-1.5-pro, or gemini-pro. `;
                errorMessage += `Visit /api/test-models to see which models are available. `;
                errorMessage += `Error: ${geminiError.message}`;
            }
            return __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json({
                error: errorMessage,
                details: geminiError.message,
                suggestion: 'Try using a different model name in the API route. Available models vary by API key access level.'
            }, {
                status: 500
            });
        }
    } catch (error) {
        console.error('SITE GUARDIAN route error:', error);
        return __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json({
            error: 'Failed to analyze safety frame',
            details: error.message || 'Unknown error'
        }, {
            status: 500
        });
    }
}
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__6de24387._.js.map