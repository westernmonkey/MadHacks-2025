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
"[project]/src/app/api/analyze-video/route.ts [app-route] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "POST",
    ()=>POST
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/server.js [app-route] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$google$2f$generative$2d$ai$2f$dist$2f$index$2e$mjs__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/@google/generative-ai/dist/index.mjs [app-route] (ecmascript)");
;
;
const GEMINI_API_KEY = process.env.GEMINI_API_KEY || 'AIzaSyDjnsgbo5yc2iroteGTz5qVe0DvruZxS2M';
const genAI = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$google$2f$generative$2d$ai$2f$dist$2f$index$2e$mjs__$5b$app$2d$route$5d$__$28$ecmascript$29$__["GoogleGenerativeAI"](GEMINI_API_KEY);
async function POST(request) {
    try {
        const formData = await request.formData();
        const file = formData.get('video');
        const frameImage = formData.get('frame'); // Optional: base64 frame from client
        if (!file && !frameImage) {
            return __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json({
                error: 'No video file or frame provided'
            }, {
                status: 400
            });
        }
        // Use Gemini Vision model
        const model = genAI.getGenerativeModel({
            model: 'gemini-1.5-flash'
        });
        // For MVP, we'll analyze a frame from the video
        // If frame is provided, use it; otherwise try to use the video file (limited size)
        let imageData;
        let mimeType;
        let filename;
        if (frameImage) {
            // Use the extracted frame from client (preferred method)
            imageData = frameImage.replace(/^data:image\/\w+;base64,/, '');
            mimeType = 'image/jpeg';
            filename = (file?.name || 'video_frame') + '.jpg';
        } else if (file) {
            // Fallback: try to use video file directly (for small files only)
            // Note: Gemini 1.5 supports video, but images are more reliable
            const arrayBuffer = await file.arrayBuffer();
            const buffer = Buffer.from(arrayBuffer);
            imageData = buffer.toString('base64');
            mimeType = file.type || 'video/mp4';
            filename = file.name;
            // If video is too large, reject it
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
        // Analysis prompt
        const prompt = `Analyze this ${frameImage ? 'video frame' : 'video'} for security threats, suspicious activities, or emergency situations such as:
- Criminal activity or theft
- Physical altercations or fights
- Medical emergencies (fainting, choking, falls)
- Suspicious behavior
- Unauthorized access

Provide a detailed analysis including:
1. Any detected threats or emergencies (High/Medium/Low severity)
2. Description of what you observe
3. Recommended actions
4. Confidence level of the detection

Respond in JSON format with: {severity: "High|Medium|Low|None", description: "...", recommendations: "...", confidence: 0-100}`;
        // Prepare the content part
        const contentPart = {
            inlineData: {
                data: imageData,
                mimeType: mimeType
            }
        };
        console.log('Sending to Gemini API...', {
            mimeType,
            size: imageData.length
        });
        try {
            const result = await model.generateContent([
                prompt,
                contentPart
            ]);
            const response = await result.response;
            const text = response.text();
            console.log('Received response from Gemini');
            // Try to parse JSON from response
            let analysis;
            try {
                // Extract JSON from markdown code blocks if present
                const jsonMatch = text.match(/\{[\s\S]*\}/);
                if (jsonMatch) {
                    analysis = JSON.parse(jsonMatch[0]);
                } else {
                    // Fallback: create structured response from text
                    analysis = {
                        severity: 'None',
                        description: text,
                        recommendations: 'Continue monitoring',
                        confidence: 50
                    };
                }
            } catch (parseError) {
                console.error('Error parsing JSON response:', parseError);
                // If parsing fails, create a structured response from text
                const lowerText = text.toLowerCase();
                analysis = {
                    severity: lowerText.includes('high') || lowerText.includes('threat') || lowerText.includes('emergency') ? 'High' : lowerText.includes('medium') || lowerText.includes('suspicious') ? 'Medium' : lowerText.includes('low') ? 'Low' : 'None',
                    description: text,
                    recommendations: 'Review the footage and take appropriate action',
                    confidence: 70
                };
            }
            // Add timestamp and metadata
            const result_data = {
                ...analysis,
                timestamp: new Date().toISOString(),
                filename: file?.name || filename || 'unknown',
                fileSize: file?.size || 0,
                videoType: file?.type || mimeType
            };
            return __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json(result_data);
        } catch (geminiError) {
            console.error('Gemini API error:', geminiError);
            // Provide more detailed error message
            let errorMessage = 'Failed to analyze video';
            if (geminiError.message) {
                errorMessage += `: ${geminiError.message}`;
            }
            if (geminiError.message?.includes('API_KEY')) {
                errorMessage = 'Invalid or missing Gemini API key. Please check your GEMINI_API_KEY environment variable.';
            }
            return __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json({
                error: errorMessage,
                details: geminiError.message
            }, {
                status: 500
            });
        }
    } catch (error) {
        console.error('Error in analyze-video route:', error);
        return __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json({
            error: 'Failed to analyze video',
            details: error.message || 'Unknown error'
        }, {
            status: 500
        });
    }
}
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__0d5be605._.js.map